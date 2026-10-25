#!/usr/bin/env python3
"""Voice cleanup: footage/audio -> clean 48 kHz mono voice.wav (not loudness-normalised).

Chain:
  --isolator  ElevenLabs Voice Isolator (only when asked AND ELEVENLABS_API_KEY present; bad footage)
  1. DeepFilterNet 3  (`deepFilter` CLI from pip `deepfilternet`)
  2. ffmpeg chain     highpass 80 Hz -> afftdn -> deesser -> light compand
Both 1 and the isolator are followed by a gentle highpass so rumble never reaches the mix.

Usage: cleanup.py IN.(mov|mp4|wav|...) --out audio/voice.wav [--isolator] [--provider auto|deepfilter|ffmpeg]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ProviderError, die, duration, has_keys, http, key, load_dotenv, log,  # noqa: E402
                    multipart, record_used, tmpdir, to_wav)

# Noise floor -25 dB with tracking; de-esser at moderate intensity; compand is a soft ~1.6:1
# above -30 dB with fast attack — enough to even out phone mics without pumping.
FFMPEG_CHAIN = ("highpass=f=80,afftdn=nf=-25:tn=1,deesser=i=0.4:m=0.5:f=0.5,"
                "compand=attacks=0.01:decays=0.25:points=-80/-80|-30/-30|-15/-21|0/-14:gain=3")
POST_CHAIN = "highpass=f=70"


def _isolator(src: Path, dst: Path, td: Path) -> None:
    wav = to_wav(src, td / "iso_in.wav", sr=44100)
    body, ctype = multipart({}, {"audio": wav})
    audio = http("POST", "https://api.elevenlabs.io/v1/audio-isolation",
                 {"xi-api-key": key("ELEVENLABS_API_KEY"), "Content-Type": ctype}, body, timeout=600)
    raw = td / "iso_out.bin"
    raw.write_bytes(audio)
    to_wav(raw, dst, afilter=POST_CHAIN)


def _deepfilter(src: Path, dst: Path, td: Path) -> None:
    wav = to_wav(src, td / "df_in.wav")          # DeepFilterNet expects 48 kHz
    outdir = td / "df_out"
    proc = subprocess.run(["deepFilter", str(wav), "-o", str(outdir)], capture_output=True, text=True)
    produced = sorted(outdir.glob("*.wav")) if outdir.exists() else []
    if proc.returncode != 0 or not produced:
        raise ProviderError(f"deepFilter failed: {proc.stderr[-400:]}")
    to_wav(produced[0], dst, afilter=POST_CHAIN)


def _ffmpeg(src: Path, dst: Path, td: Path) -> None:
    to_wav(src, dst, afilter=FFMPEG_CHAIN)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--isolator", action="store_true", help="use ElevenLabs Voice Isolator (paid) if key present")
    ap.add_argument("--provider", default="auto", choices=("auto", "deepfilter", "ffmpeg"))
    args = ap.parse_args(argv)
    load_dotenv()
    if not args.input.is_file():
        die(f"input not found: {args.input}")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    chain = []
    if args.isolator:
        if has_keys("ELEVENLABS_API_KEY"):
            chain.append(("elevenlabs-isolator", _isolator))
        else:
            log("warning: --isolator needs ELEVENLABS_API_KEY; falling back to local cleanup")
    if args.provider in ("auto", "deepfilter") and shutil.which("deepFilter"):
        chain.append(("deepfilternet3", _deepfilter))
    if args.provider in ("auto", "ffmpeg"):
        chain.append(("ffmpeg-chain", _ffmpeg))

    with tmpdir() as td:
        for name, fn in chain:
            try:
                fn(args.input, args.out, Path(td))
            except (ProviderError, RuntimeError) as e:
                log(f"[cleanup] {name} failed: {e}")
                continue
            note = None if name != "ffmpeg-chain" else "pip install deepfilternet for better denoising"
            record_used(args.out, "cleanup", name, note)
            print(f"{args.out}: {duration(args.out)}s via {name}")
            return
    die("voice cleanup failed with every provider")


if __name__ == "__main__":
    main()
