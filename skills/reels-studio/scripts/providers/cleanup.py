#!/usr/bin/env python3
"""Voice cleanup that never kills the voice: footage/audio -> clean 48 kHz mono voice wav,
normalised to a speech-gated target (default −16 LUFS).

Stages
  0. measure the original: speech-gated loudness, 2–4 kHz presence, noise floor (non-speech)
  1. denoise (first available, strength ladder):
       --isolator  ElevenLabs Voice Isolator (only when asked AND ELEVENLABS_API_KEY present)
       DeepFilterNet 3  `deepFilter --atten-lim <15|10|6>`   (never full attenuation)
       ffmpeg            highpass 80 -> afftdn nr/nf ladder (12/−30, 9/−35, 6/−40)
  2. guard: compare the denoised voice with the original over speech blocks. If it lost
     > 1.5 dB speech level or > 3 dB of 2–4 kHz presence (relative to its own speech level),
     back off one rung and retry; the last rung is "highpass only".
  3. polish: de-esser, light compression (2.5:1 above −24 dBFS, slow enough not to pump)
  4. normalise speech-gated loudness to --target with a −1 dBFS peak limiter

Everything that was done is logged and written to <out>.cleanup.json (and env.json -> used).

Usage: cleanup.py IN.(mov|mp4|wav|...) --out audio/voice.source.wav [--isolator]
                  [--provider auto|deepfilter|ffmpeg] [--target -16]
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ProviderError, die, duration, has_keys, http, key, load_dotenv, log,  # noqa: E402
                    multipart, record_used, tmpdir, to_wav, ffmpeg)
import audio_meter as am  # noqa: E402

HP = "highpass=f=80:poles=2"
# (nr dB, noise floor dB) — moderate first, then gentler. nf −25 (the old default) treated
# every quiet syllable as noise; never go above −30.
AFFTDN_LADDER = [(12, -30), (9, -35), (6, -40)]
DF_LADDER = [15, 10, 6]           # DeepFilterNet attenuation limit, dB
POLISH = ("deesser=i=0.3:m=0.5:f=0.5:s=o,"
          "acompressor=threshold=-24dB:ratio=2.5:attack=12:release=180:knee=4:makeup=1")
MAX_LEVEL_LOSS = 1.5
MAX_PRESENCE_LOSS = 3.0


# --------------------------------------------------------------------------- measurement
def measure(path: Path, mask: "am.np.ndarray | None" = None) -> dict:
    x = am.decode(path, 1)
    if mask is None:
        mask = am.vad_mask(x)
    n10 = int(math.ceil(x.shape[1] / am.SR / 0.01))
    mask = am.fit_mask(mask, n10)
    speech = am.masked(x, mask)
    return {"speech_lufs": speech,
            "presence_db": am.band_level(x, 2000, 4000, mask),
            "noise_lufs": am.masked(x, ~mask, gate=False) if (~mask).any() else float("-inf"),
            "mask": mask}


def guard(orig: dict, cand: dict) -> tuple[bool, float, float]:
    """(ok, level_loss_dB, presence_loss_dB). Presence is compared relative to speech level so
    a uniform gain change does not count as tonal loss."""
    level_loss = orig["speech_lufs"] - cand["speech_lufs"]
    pres_loss = (orig["presence_db"] - orig["speech_lufs"]) - (cand["presence_db"] - cand["speech_lufs"])
    return level_loss <= MAX_LEVEL_LOSS and pres_loss <= MAX_PRESENCE_LOSS, level_loss, pres_loss


# --------------------------------------------------------------------------- denoisers
def _isolator(wav: Path, dst: Path, td: Path, _strength) -> str:
    src = to_wav(wav, td / "iso_in.wav", sr=44100)
    body, ctype = multipart({}, {"audio": src})
    audio = http("POST", "https://api.elevenlabs.io/v1/audio-isolation",
                 {"xi-api-key": key("ELEVENLABS_API_KEY"), "Content-Type": ctype}, body, timeout=600)
    raw = td / "iso_out.bin"
    raw.write_bytes(audio)
    to_wav(raw, dst, afilter=HP)
    return "elevenlabs-isolator"


def _deepfilter(wav: Path, dst: Path, td: Path, atten: float) -> str:
    outdir = td / f"df_out_{atten}"
    proc = subprocess.run(["deepFilter", "--atten-lim", str(atten), str(wav), "-o", str(outdir)],
                          capture_output=True, text=True)
    produced = sorted(outdir.glob("*.wav")) if outdir.exists() else []
    if proc.returncode != 0 or not produced:
        raise ProviderError(f"deepFilter failed: {proc.stderr[-400:]}")
    to_wav(produced[0], dst, afilter=HP)
    return f"deepfilternet3 atten-lim {atten:g} dB"


def _afftdn(wav: Path, dst: Path, td: Path, rung) -> str:
    if rung is None:
        to_wav(wav, dst, afilter=HP)
        return "highpass 80 Hz only (denoise backed off completely)"
    nr, nf = rung
    to_wav(wav, dst, afilter=f"{HP},afftdn=nr={nr}:nf={nf}:tn=1")
    return f"ffmpeg afftdn nr={nr} nf={nf}"


def normalise(src: Path, dst: Path, target: float, mask) -> float:
    m = measure(src, mask)
    if not math.isfinite(m["speech_lufs"]):
        raise ProviderError("cleaned voice is silent")
    gain = target - m["speech_lufs"]
    ffmpeg("-i", str(src), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.891:attack=2:release=60:level=0",
           "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(dst))
    return gain


def finite(o):
    """JSON-safe copy: non-finite floats -> None."""
    if isinstance(o, dict):
        return {k: finite(v) for k, v in o.items()}
    if isinstance(o, list):
        return [finite(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--isolator", action="store_true", help="use ElevenLabs Voice Isolator (paid) if key present")
    ap.add_argument("--provider", default="auto", choices=("auto", "deepfilter", "ffmpeg"))
    ap.add_argument("--target", type=float, default=-16.0, help="speech-gated LUFS of the output")
    args = ap.parse_args(argv)
    load_dotenv()
    if not args.input.is_file():
        die(f"input not found: {args.input}")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    ladders: list[tuple[str, object, list]] = []
    if args.isolator:
        if has_keys("ELEVENLABS_API_KEY"):
            ladders.append(("isolator", _isolator, [None]))
        else:
            log("warning: --isolator needs ELEVENLABS_API_KEY; falling back to local cleanup")
    if args.provider in ("auto", "deepfilter") and shutil.which("deepFilter"):
        ladders.append(("deepfilter", _deepfilter, DF_LADDER))
    if args.provider in ("auto", "ffmpeg") or not ladders:
        ladders.append(("ffmpeg", _afftdn, [*AFFTDN_LADDER, None]))

    report: dict = {"input": str(args.input), "target_lufs": args.target, "attempts": []}
    with tmpdir() as td:
        td = Path(td)
        orig_wav = to_wav(args.input, td / "orig.wav")
        orig = measure(orig_wav)
        mask = orig["mask"]
        if not math.isfinite(orig["speech_lufs"]):
            die("no speech found in the input (silent track?)")
        report["original"] = {k: round(v, 2) for k, v in orig.items() if k != "mask"}
        log(f"[cleanup] original: speech {orig['speech_lufs']:.1f} LUFS, presence(2-4k) "
            f"{orig['presence_db']:.1f} dB, noise floor {am.fmt(orig['noise_lufs'])} LUFS")

        chosen = None
        for family, fn, rungs in ladders:
            for i, rung in enumerate(rungs):
                den = td / f"den_{family}_{i}.wav"
                try:
                    what = fn(orig_wav, den, td, rung)
                except (ProviderError, RuntimeError) as e:
                    log(f"[cleanup] {family} failed: {e}")
                    break
                cand = measure(den, mask)
                ok, lvl, pres = guard(orig, cand)
                nr_red = orig["noise_lufs"] - cand["noise_lufs"]
                att = {"what": what, "level_loss_db": round(lvl, 2), "presence_loss_db": round(pres, 2),
                       "noise_reduction_db": round(nr_red, 1) if math.isfinite(nr_red) else None, "ok": ok}
                report["attempts"].append(att)
                log(f"[cleanup] {what}: speech −{lvl:.2f} dB, presence −{pres:.2f} dB, "
                    f"noise −{am.fmt(nr_red)} dB -> {'OK' if ok else 'too strong, backing off'}")
                last = i == len(rungs) - 1
                if ok or (family == "ffmpeg" and rung is None):
                    chosen = (family, what, den)
                    break
                if last:
                    log(f"[cleanup] {family}: every strength failed the guard; trying next provider")
            if chosen:
                break
        if not chosen:
            die("voice cleanup failed with every provider")

        family, what, den = chosen
        polished = td / "polished.wav"
        ffmpeg("-i", str(den), "-af", POLISH, "-ac", "1", "-ar", "48000", "-c:a", "pcm_f32le", str(polished))
        gain = normalise(polished, args.out, args.target, mask)
        final = measure(args.out, mask)
        report.update(denoise=what, polish=POLISH, normalise_gain_db=round(gain, 2),
                      final={k: round(v, 2) for k, v in final.items() if k != "mask"})
    log(f"[cleanup] final: speech {final['speech_lufs']:.1f} LUFS (target {args.target}), presence "
        f"{final['presence_db']:.1f} dB, noise floor {am.fmt(final['noise_lufs'])} LUFS")
    rep_p = args.out.with_suffix(".cleanup.json")
    rep_p.write_text(json.dumps(finite(report), indent=1) + "\n")
    note = f"{what}; deesser + 2.5:1 comp; speech-gated {final['speech_lufs']:.1f} LUFS"
    if family == "ffmpeg":
        note += " (pip install deepfilternet for better denoising)"
    record_used(args.out, "cleanup", family if family != "ffmpeg" else "ffmpeg-chain", note)
    print(f"{args.out}: {duration(args.out)}s via {what}; speech {final['speech_lufs']:.1f} LUFS")


if __name__ == "__main__":
    main()
