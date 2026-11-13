#!/usr/bin/env python3
"""Mix & master for phone speakers: voice is king, music audible and dynamic, SFX on cues.
-> audio/mix.wav (48 kHz stereo, −14 LUFS integrated, ≤ −1 dBTP) + audio/mix_report.json

Reads work/<slug>/:
  brief.json         audio_profile: "energetic" (default — music + SFX) | "reference" (purist)
  plan/scenes.json   audio.music {enabled?, start?, gap_speech_db?, gap_pause_db?, gain_db?},
                     audio.sfx_enabled, audio.sfx_gain_db?, scenes[].sfx [{name, t, gain_db?}]
  audio/voice.wav    required (cleanup.py / tts.py output on the final timeline)
  audio/transcript.json  word timings -> speech mask (energy VAD when missing)
  audio/music.wav    used when present (and not disabled in scenes.json)
  SFX files          work/<slug>/assets/sfx/<name>.wav first, then $SKILL/assets/sfx

Levels are set relative to the voice, measured with a BS.1770 meter gated on speech:
  1. voice stem -> −16 LUFS speech-gated (--voice-lufs); the music never attenuates it
  2. music: high-pass 60 Hz, +2 dB @ 1.2 kHz and +1.5 dB shelf @ 5 kHz so it reads on phone
     speakers; level closed-loop so that music under speech sits gap_speech_db (default 10,
     allowed 9–12) below the voice and rises in pauses to gap_pause_db (default 5) below it;
     ducking envelope 150 ms attack / 400 ms release with 200 ms look-ahead
  3. SFX at their cue times, peak-levelled 6–10 dB below the voice peaks (−10 dB when the cue
     lands on a word, −6 dB in a pause) — audible, never masking words
  4. gain + limiter + two-pass loudnorm (linear) -> −14 LUFS / −1 dBTP
Measured and printed: voice LUFS, music LUFS under speech / in pauses, gap, SFX count, final
I/TP and the voice level in the final mix. Exit code 3 (after writing the files) when the
voice-to-music gap is outside 7–16 dB or the voice in the final mix is > 2 dB off −14 LUFS
(--warn-only downgrades to warnings).

Usage: mix.py --work work/<slug> [--out audio/mix.wav] [--voice-lufs -16] [--gap-speech 10]
              [--gap-pause 5] [--warn-only]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
from common import SFX_DIR, die, ffmpeg, log, loudness, record_used, tmpdir, write_json  # noqa: E402
import audio_meter as am  # noqa: E402

SR = 48000
TARGET = {"I": -14.0, "TP": -1.0, "LRA": 7.0}
VOICE_FINAL_TARGET = -14.0          # speech-gated voice level expected in the master
GAP_LIMITS = (7.0, 16.0)


# --------------------------------------------------------------------------- io
def decode(path: Path, channels: int) -> np.ndarray:
    return am.decode(path, channels)


def encode(stereo: np.ndarray, path: Path, codec: str = "pcm_f32le") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2",
                           "-i", "-", "-c:a", codec, str(path)],
                          input=stereo.T.astype("<f4").tobytes(), capture_output=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode()[-800:])


def db(x: float) -> float:
    return 20 * math.log10(max(x, 1e-12))


# --------------------------------------------------------------------------- EQ (RBJ biquads)
def _peaking(f0: float, gain_db: float, q: float):
    A, w = 10 ** (gain_db / 40), 2 * math.pi * f0 / SR
    alpha = math.sin(w) / (2 * q)
    b = [1 + alpha * A, -2 * math.cos(w), 1 - alpha * A]
    a = [1 + alpha / A, -2 * math.cos(w), 1 - alpha / A]
    return np.array(b) / a[0], np.array(a) / a[0]


def _highshelf(f0: float, gain_db: float, s: float = 0.8):
    A, w = 10 ** (gain_db / 40), 2 * math.pi * f0 / SR
    alpha = math.sin(w) / 2 * math.sqrt((A + 1 / A) * (1 / s - 1) + 2)
    cw, sa = math.cos(w), 2 * math.sqrt(A) * alpha
    b = [A * ((A + 1) + (A - 1) * cw + sa), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sa)]
    a = [(A + 1) - (A - 1) * cw + sa, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sa]
    return np.array(b) / a[0], np.array(a) / a[0]


def phone_eq(x: np.ndarray) -> np.ndarray:
    """High-pass 60 Hz (rumble/sub that phones can't play and that eats headroom) + mild presence."""
    sos = signal.butter(2, 60 / (SR / 2), "high", output="sos")
    y = signal.sosfilt(sos, x, axis=1)
    y = signal.lfilter(*_peaking(1200, 2.0, 0.8), y, axis=1)
    y = signal.lfilter(*_highshelf(5000, 1.5), y, axis=1)
    return y.astype(np.float32)


# --------------------------------------------------------------------------- ducking
def duck_envelope(active10: np.ndarray, duck_db: float, n: int, lookahead: float = 0.2,
                  attack: float = 0.15, release: float = 0.4) -> np.ndarray:
    """Per-sample linear gain: 0 dB where no speech, duck_db under speech (one-pole in dB)."""
    shift = int(round(lookahead / 0.01))
    act = np.r_[active10[shift:], np.zeros(shift, bool)].astype(float) if shift else active10.astype(float)
    target = duck_db * act
    a_dn, a_up = math.exp(-0.01 / attack), math.exp(-0.01 / release)
    out, level = np.empty_like(target), 0.0
    for i, tgt in enumerate(target):
        coef = a_dn if tgt < level else a_up
        level = coef * level + (1 - coef) * tgt
        out[i] = level
    hop = int(0.01 * SR)
    g = np.repeat(10 ** (out / 20), hop)
    return np.pad(g, (0, max(0, n - len(g))), constant_values=1.0)[:n].astype(np.float32)


# --------------------------------------------------------------------------- stems
def place(bus: np.ndarray, x: np.ndarray, t: float, gain: float = 1.0) -> None:
    s = int(round(t * SR))
    if s >= bus.shape[1] or s < 0:
        return
    e = min(bus.shape[1], s + x.shape[1])
    bus[:, s:e] += x[:, : e - s] * gain


def find_sfx(work: Path, cue: dict) -> Path | None:
    if cue.get("file"):
        p = Path(cue["file"])
        return p if p.is_absolute() else work / p
    for base in (work / "assets" / "sfx", SFX_DIR):
        cand = base / f"{cue['name']}.wav"
        if cand.is_file():
            return cand
    return None


def build_sfx(work: Path, scenes: dict, n: int, voice_peak_db: float, speech10: np.ndarray,
              bus_gain_db: float) -> tuple[np.ndarray, list[dict]]:
    bus, cache, placed = np.zeros((2, n), np.float32), {}, []
    for scene in scenes.get("scenes", []):
        for cue in scene.get("sfx", []) or []:
            path = find_sfx(work, cue)
            if not path or not path.is_file():
                log(f"warning: sfx '{cue.get('name')}' not found (scene {scene.get('id')}); skipped")
                continue
            if path not in cache:
                cache[path] = decode(path, 2)
            x = cache[path]
            t = float(cue["t"])
            i0, i1 = int(max(0, t) / 0.01), int((max(0, t) + min(0.3, x.shape[1] / SR)) / 0.01)
            on_word = bool(speech10[i0:max(i1, i0 + 1)].any()) if i0 < len(speech10) else False
            offset = -10.0 if on_word else -6.0
            peak = db(float(np.max(np.abs(x))) or 1e-6)
            g_db = voice_peak_db + offset - peak + bus_gain_db + float(cue.get("gain_db", 0))
            place(bus, x, t, 10 ** (g_db / 20))
            placed.append({"name": cue.get("name"), "t": round(t, 3), "rel_voice_peak_db": round(
                offset + bus_gain_db + float(cue.get("gain_db", 0)), 1), "on_word": on_word})
    return bus, placed


# --------------------------------------------------------------------------- master
def pre_limit(src: Path, dst: Path) -> None:
    """Gain to target loudness + brick-wall limit at −2 dBFS so loudnorm stays linear."""
    measured = float(loudness(src)["input_i"])
    if not math.isfinite(measured) or measured < -70:
        raise RuntimeError("premix is silent — nothing to normalise")
    ffmpeg("-i", str(src), "-af",
           f"volume={TARGET['I'] - measured:.2f}dB,alimiter=limit=0.79:attack=3:release=80:level=0:latency=1",
           "-ar", str(SR), "-c:a", "pcm_f32le", str(dst))


def loudnorm_two_pass(src: Path, dst: Path) -> dict:
    t = TARGET
    first = loudness(src)
    if not math.isfinite(float(first["input_i"])):
        raise RuntimeError("premix is silent — nothing to normalise")
    lra = min(20.0, max(t["LRA"], math.ceil(float(first["input_lra"]) * 10 + 1) / 10))
    flt = (f"loudnorm=I={t['I']}:TP={t['TP']}:LRA={lra}"
           f":measured_I={first['input_i']}:measured_TP={first['input_tp']}"
           f":measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}"
           f":offset={first['target_offset']}:linear=true:print_format=json")
    proc = ffmpeg("-i", str(src), "-af", flt, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(dst))
    match = re.search(r"\{[^{}]*\"normalization_type\"[^{}]*\}", proc.stderr, re.S)
    return json.loads(match.group(0)) if match else {}


def r1(v: float) -> float | None:
    return round(v, 1) if math.isfinite(v) else None


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="default: <work>/audio/mix.wav")
    ap.add_argument("--voice-lufs", type=float, default=-16.0, help="voice stem, speech-gated")
    ap.add_argument("--gap-speech", type=float, help="music below voice under speech, dB (9–12, default 10)")
    ap.add_argument("--gap-pause", type=float, help="music below voice in pauses, dB (4–6, default 5)")
    ap.add_argument("--warn-only", action="store_true", help="never exit non-zero on level checks")
    args = ap.parse_args(argv)
    work = args.work
    out = args.out or work / "audio" / "mix.wav"
    voice_path = work / "audio" / "voice.wav"
    if not voice_path.is_file():
        die(f"missing {voice_path} (run tts.py or cleanup.py first)")
    scenes_path = work / "plan" / "scenes.json"
    scenes = json.loads(scenes_path.read_text(encoding="utf-8")) if scenes_path.is_file() else {}
    brief_p = work / "brief.json"
    brief = json.loads(brief_p.read_text(encoding="utf-8")) if brief_p.is_file() else {}
    profile = brief.get("audio_profile", "energetic")
    audio_cfg = scenes.get("audio", {})
    music_cfg = audio_cfg.get("music") or {}
    music_path = work / "audio" / "music.wav"
    music_on = bool(music_cfg.get("enabled", music_path.is_file()))
    sfx_on = audio_cfg.get("sfx_enabled", True)
    gap_s = float(args.gap_speech or music_cfg.get("gap_speech_db") or 10.0)
    gap_p = float(args.gap_pause or music_cfg.get("gap_pause_db") or 5.0)
    gap_s, gap_p = min(max(gap_s, 9.0), 12.0), min(max(gap_p, 3.0), gap_s - 2)

    # ---- voice (never attenuated by anything below)
    voice = decode(voice_path, 1)
    total = max(float(scenes.get("duration", 0)), voice.shape[1] / SR)
    n = int(round(total * SR))
    n10 = int(math.ceil(total / 0.01))
    speech10, mask_src = am.speech_mask(work, voice, total)
    speech10 = am.fit_mask(speech10, n10)
    v_raw = am.masked(np.vstack([voice, voice]), speech10)   # measured as it plays: dual-mono in a stereo mix
    if not math.isfinite(v_raw):
        die("voice.wav has no measurable speech")
    voice = voice * 10 ** ((args.voice_lufs - v_raw) / 20)
    vbus = np.zeros((2, n), np.float32)
    vbus[:, : min(n, voice.shape[1])] = voice[0, :n]
    v_lufs = am.masked(vbus, speech10)
    frame_peaks = np.abs(vbus[0][: (n // 480) * 480]).reshape(-1, 480).max(axis=1)
    sp = am.fit_mask(speech10, len(frame_peaks))
    voice_peak_db = db(float(np.percentile(frame_peaks[sp] if sp.any() else frame_peaks, 99)))
    report: dict = {"profile": profile, "speech_mask": mask_src, "voice_lufs_speech": r1(v_lufs),
                    "voice_peak_db": r1(voice_peak_db), "voice_gain_db": r1(args.voice_lufs - v_raw)}
    mix = vbus.copy()
    parts = ["voice"]
    problems: list[str] = []

    # ---- music
    mbus = np.zeros((2, n), np.float32)
    if music_on:
        if not music_path.is_file():
            die(f"music enabled but {music_path} is missing (run music.py / music_search.py)")
        start = float(music_cfg.get("start", 0.0) or 0.0)
        raw = np.zeros((2, n), np.float32)
        place(raw, phone_eq(decode(music_path, 2)), start)
        # music present (not silent, not in the last 1.5 s fade) -> where levels are measured
        e10 = np.abs(raw[:, : (n // 480) * 480]).max(axis=0).reshape(-1, 480).max(axis=1)
        present = am.fit_mask(e10 > 10 ** (-50 / 20), n10)
        present[max(0, n10 - 150):] = False
        present[: int((start + 0.6) / 0.01)] = False
        sp_m, pa_m = speech10 & present, (~speech10) & present
        m_s_target, m_p_target = v_lufs - gap_s, v_lufs - gap_p
        base = am.masked(raw, present, gate=False)
        g0 = (m_p_target - base) if math.isfinite(base) else 0.0
        duck = -(gap_s - gap_p)
        for _ in range(4):                       # closed loop on the measured stem levels
            mbus = raw * 10 ** (g0 / 20) * duck_envelope(speech10, duck, n)
            ls, lp = am.masked(mbus, sp_m, gate=False), am.masked(mbus, pa_m, gate=False)
            if not math.isfinite(ls):
                break
            if math.isfinite(lp) and pa_m.sum() >= 40:
                g0 += m_p_target - lp
                duck = min(-2.0, max(-14.0, duck + (m_s_target - ls) - (m_p_target - lp)))
            else:
                g0 += m_s_target - ls
            if abs(ls - m_s_target) < 0.3 and (not math.isfinite(lp) or abs(lp - m_p_target) < 0.6):
                break
        mbus = raw * 10 ** ((g0 + float(music_cfg.get("gain_db", 0))) / 20) * duck_envelope(speech10, duck, n)
        ls, lp = am.masked(mbus, sp_m, gate=False), am.masked(mbus, pa_m, gate=False)
        gap = v_lufs - ls
        report.update(music_lufs_under_speech=r1(ls), music_lufs_in_pauses=r1(lp), gap_speech_db=r1(gap),
                      gap_pause_db=r1(v_lufs - lp), duck_db=r1(duck), music_start=start,
                      pause_sec=round(float(pa_m.sum()) * 0.01, 2))
        if not (GAP_LIMITS[0] <= gap <= GAP_LIMITS[1]):
            problems.append(f"voice-to-music gap {gap:.1f} dB outside {GAP_LIMITS[0]:g}–{GAP_LIMITS[1]:g} dB")
        mix += mbus
        parts.append(f"music(gap {gap:.1f} dB speech / {v_lufs - lp:.1f} dB pauses, duck {duck:.1f} dB)"
                     if math.isfinite(lp) else f"music(gap {gap:.1f} dB, duck {duck:.1f} dB)")
    else:
        report.update(music_lufs_under_speech=None, music_lufs_in_pauses=None, gap_speech_db=None)
        if profile == "energetic":
            log("warning: profile 'energetic' but no music — run music.py (internet search) first")

    # ---- SFX
    sbus, placed = np.zeros((2, n), np.float32), []
    if sfx_on:
        sbus, placed = build_sfx(work, scenes, n, voice_peak_db, speech10, float(audio_cfg.get("sfx_gain_db", 0)))
        if placed:
            mix += sbus
            parts.append(f"sfx x{len(placed)}")
    report["sfx_count"] = len(placed)
    report["sfx"] = placed
    if profile == "energetic" and not placed:
        log("warning: profile 'energetic' but no SFX cues — run sfx_plan.py first")

    # ---- master
    with tmpdir() as td:
        premix, limited = Path(td) / "premix.wav", Path(td) / "limited.wav"
        encode(mix, premix)
        try:
            pre_limit(premix, limited)
            stats = loudnorm_two_pass(limited, out)
        except RuntimeError as e:
            die(str(e))
    final_x = decode(out, 2)
    pre_i, fin_i = am.integrated(mix), am.integrated(final_x)
    master_gain = fin_i - pre_i
    voice_final = v_lufs + master_gain
    final = loudness(out)
    sg = 10 ** (master_gain / 20)
    if music_on:
        encode(mbus * sg, work / "audio" / "music_bed.wav", "pcm_s16le")   # stems at final level (qa_audio)
    if placed:
        encode(sbus * sg, work / "audio" / "sfx.wav", "pcm_s16le")
    report.update(final_lufs=float(final["input_i"]), final_tp=float(final["input_tp"]),
                  final_lra=float(final["input_lra"]), master_gain_db=r1(master_gain),
                  voice_lufs_final=r1(voice_final), loudnorm_mode=stats.get("normalization_type"),
                  stems_at_final_level=True)
    if abs(voice_final - VOICE_FINAL_TARGET) > 2:
        problems.append(f"voice in final mix {voice_final:.1f} LUFS, > 2 dB off {VOICE_FINAL_TARGET:g}")
    if float(final["input_tp"]) > TARGET["TP"] + 0.1:
        problems.append(f"true peak {final['input_tp']} dBTP > {TARGET['TP']}")
    report["problems"] = problems
    report["ok"] = not problems
    write_json(work / "audio" / "mix_report.json", report)
    record_used(out, "mix", "mix.py-phone-v2", " + ".join(parts))

    print(f"{out}: {total:.2f}s  {' + '.join(parts)}  [profile {profile}, speech mask: {mask_src}]")
    print(f"voice: {am.fmt(v_lufs)} LUFS speech-gated (stem) -> {am.fmt(voice_final)} LUFS in the master")
    if music_on:
        print(f"music: {am.fmt(report['music_lufs_under_speech'] or -math.inf)} LUFS under speech, "
              f"{am.fmt(report['music_lufs_in_pauses'] or -math.inf)} LUFS in pauses "
              f"({report['pause_sec']} s of pauses); gap {report['gap_speech_db']} dB")
    print(f"sfx: {len(placed)} cues")
    print(f"master: I={final['input_i']} LUFS  TP={final['input_tp']} dBTP  LRA={final['input_lra']} LU"
          f"  (loudnorm {stats.get('normalization_type', '?')})")
    if problems:
        msg = "; ".join(problems)
        if args.warn_only:
            log(f"warning: {msg}")
        else:
            print(f"error: mix level check failed: {msg}", file=sys.stderr)
            sys.exit(3)


if __name__ == "__main__":
    main()
