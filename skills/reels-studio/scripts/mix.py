#!/usr/bin/env python3
"""Mix & master: voice + ducked music + SFX -> audio/mix.wav (48 kHz stereo, -14 LUFS, -1 dBTP).

Reads work/<slug>/:
  plan/scenes.json   audio.music {enabled, mood, bpm, duck_db, start, gain_db?}, audio.sfx_enabled,
                     audio.sfx_gain_db?, scenes[].sfx [{name, t, gain_db?}]   (t = final timeline)
  audio/voice.wav    required
  audio/music.wav    required only when music is enabled
  SFX files          work/<slug>/assets/sfx/<name>.wav first (custom one-offs), then $SKILL/assets/sfx

Pipeline:
  1. stems are gain-staged by loudness: voice -> -16 LUFS, music bed -> -24 LUFS (+gain_db)
  2. music is placed at `start` and ducked by `duck_db` while the voice is active. The sidechain
     envelope is computed here (RMS -> gate -> attack/release with 60 ms look-ahead) rather than
     with ffmpeg's sidechaincompress so the attenuation equals duck_db exactly, independent of
     the voice level, and is deterministic.
  3. SFX are summed onto a bus (also written to audio/sfx.wav for inspection)
  4. gain + -2 dBFS limiter, then two-pass ffmpeg loudnorm I=-14 TP=-1 LRA=7 in linear mode
     (LRA target relaxed to the measured LRA so loudnorm never switches to dynamic) -> audio/mix.wav
Style A (voice only: music disabled, no SFX) is the degenerate case of the same path.

Usage: mix.py --work work/<slug> [--out audio/mix.wav] [--voice-lufs -16] [--music-lufs -24]
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

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
from common import SFX_DIR, die, ffmpeg, log, loudness, record_used, tmpdir  # noqa: E402

SR = 48000
TARGET = {"I": -14.0, "TP": -1.0, "LRA": 7.0}


# --------------------------------------------------------------------------- io
def decode(path: Path, channels: int) -> np.ndarray:
    """Any audio file -> float32 array shaped (channels, n) at 48 kHz."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", str(channels),
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, channels).T.copy()


def encode(stereo: np.ndarray, path: Path, codec: str = "pcm_f32le") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2",
                           "-i", "-", "-c:a", codec, str(path)],
                          input=stereo.T.astype("<f4").tobytes(), capture_output=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode()[-800:])


def gain_to_lufs(path: Path, target: float) -> float:
    """Linear gain that brings `path` to `target` integrated LUFS (1.0 if silent)."""
    measured = float(loudness(path)["input_i"])
    if not math.isfinite(measured) or measured < -70:
        log(f"warning: {path.name} is (near) silent; leaving gain at 0 dB")
        return 1.0
    return 10 ** ((target - measured) / 20)


# --------------------------------------------------------------------------- ducking
def duck_envelope(voice: np.ndarray, duck_db: float, lookahead: float = 0.06,
                  attack: float = 0.04, release: float = 0.35) -> np.ndarray:
    """Per-sample gain (linear) for the music: 1.0 in silence, 10^(duck_db/20) under speech."""
    hop = int(0.01 * SR)
    mono = np.abs(voice).mean(axis=0) if voice.ndim == 2 else np.abs(voice)
    n_hops = int(math.ceil(len(mono) / hop))
    padded = np.pad(mono ** 2, (0, n_hops * hop - len(mono)))
    rms_db = 10 * np.log10(padded.reshape(n_hops, hop).mean(axis=1) + 1e-12)
    # Voice is normalised to ~-16 LUFS, so speech RMS sits around -25..-15 dBFS.
    activity = np.clip((rms_db + 45) / 10, 0, 1)          # -45 dB -> 0, -35 dB -> 1
    shift = int(lookahead / 0.01)                          # start ducking slightly early
    activity = np.r_[activity[shift:], np.zeros(shift)]
    a_up, a_dn = math.exp(-0.01 / attack), math.exp(-0.01 / release)
    smooth, level = np.empty_like(activity), 0.0
    for i, target in enumerate(activity):                  # one-pole attack/release
        coef = a_up if target > level else a_dn
        level = coef * level + (1 - coef) * target
        smooth[i] = level
    gain_db = duck_db * smooth
    per_sample = np.repeat(10 ** (gain_db / 20), hop)[: len(mono)]
    return per_sample.astype(np.float32)


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


def build_sfx(work: Path, scenes: dict, n: int, bus_gain_db: float) -> tuple[np.ndarray, int]:
    bus, cache, placed = np.zeros((2, n), np.float32), {}, 0
    for scene in scenes.get("scenes", []):
        for cue in scene.get("sfx", []) or []:
            path = find_sfx(work, cue)
            if not path or not path.is_file():
                log(f"warning: sfx '{cue.get('name')}' not found (scene {scene.get('id')}); skipped")
                continue
            if path not in cache:
                cache[path] = decode(path, 2)
            place(bus, cache[path], float(cue["t"]), 10 ** ((bus_gain_db + cue.get("gain_db", 0)) / 20))
            placed += 1
    return bus, placed


def build_music(path: Path, cfg: dict, n: int, gain: float) -> np.ndarray:
    music = decode(path, 2) * gain
    bus = np.zeros((2, n), np.float32)
    place(bus, music, float(cfg.get("start", 0.0)))
    end = min(n, int(round(float(cfg.get("start", 0.0)) * SR)) + music.shape[1])
    fade = min(int(1.0 * SR), end)
    if end >= n and fade:                                   # music outlives the video: fade it out
        bus[:, n - fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return bus


# --------------------------------------------------------------------------- master
def pre_limit(src: Path, dst: Path) -> None:
    """Gain the premix to the target loudness and brick-wall limit peaks at -2 dBFS.

    Without this, loudnorm cannot stay in linear mode whenever reaching -14 LUFS would push a
    peak (boom, plosive) above -1 dBTP; it then falls back to dynamic mode, which pumps and
    misses the target. Limiting first leaves loudnorm a ~0 dB linear trim."""
    first = loudness(src)
    measured = float(first["input_i"])
    if not math.isfinite(measured) or measured < -70:
        raise RuntimeError("premix is silent — nothing to normalise")
    gain = TARGET["I"] - measured
    ffmpeg("-i", str(src), "-af",
           f"volume={gain:.2f}dB,alimiter=limit=0.79:attack=3:release=80:level=0:latency=1",
           "-ar", str(SR), "-c:a", "pcm_f32le", str(dst))


def loudnorm_two_pass(src: Path, dst: Path) -> dict:
    t = TARGET
    first = loudness(src)
    if not math.isfinite(float(first["input_i"])):
        raise RuntimeError("premix is silent — nothing to normalise")
    # loudnorm only stays linear when input LRA <= target LRA. Short reels with pauses
    # routinely measure LRA 8-12 (gating barely engages on 30-60 s), and dynamic mode both
    # pumps and misses I by ~1 LU, so the LRA target is relaxed to the measured value.
    lra = min(20.0, max(t["LRA"], math.ceil(float(first["input_lra"]) * 10 + 1) / 10))
    flt = (f"loudnorm=I={t['I']}:TP={t['TP']}:LRA={lra}"
           f":measured_I={first['input_i']}:measured_TP={first['input_tp']}"
           f":measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}"
           f":offset={first['target_offset']}:linear=true:print_format=json")
    proc = ffmpeg("-i", str(src), "-af", flt, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(dst))
    match = re.search(r"\{[^{}]*\"normalization_type\"[^{}]*\}", proc.stderr, re.S)
    return json.loads(match.group(0)) if match else {}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="default: <work>/audio/mix.wav")
    ap.add_argument("--voice-lufs", type=float, default=-16.0)
    ap.add_argument("--music-lufs", type=float, default=-24.0, help="music bed level before ducking")
    args = ap.parse_args(argv)
    work = args.work
    out = args.out or work / "audio" / "mix.wav"
    voice_path = work / "audio" / "voice.wav"
    if not voice_path.is_file():
        die(f"missing {voice_path} (run tts.py or cleanup.py first)")
    scenes_path = work / "plan" / "scenes.json"
    scenes = json.loads(scenes_path.read_text(encoding="utf-8")) if scenes_path.is_file() else {}
    if not scenes:
        log(f"warning: {scenes_path} not found — voice-only master")
    audio_cfg = scenes.get("audio", {})
    music_cfg = audio_cfg.get("music") or {}
    music_on = bool(music_cfg.get("enabled"))
    sfx_on = audio_cfg.get("sfx_enabled", True)

    voice = decode(voice_path, 1) * gain_to_lufs(voice_path, args.voice_lufs)
    total = max(float(scenes.get("duration", 0)), voice.shape[1] / SR)
    n = int(round(total * SR))
    mix = np.zeros((2, n), np.float32)
    mix[:, : voice.shape[1]] += voice[0, :n]

    parts = ["voice"]
    if music_on:
        music_path = work / "audio" / "music.wav"
        if not music_path.is_file():
            die(f"music enabled in scenes.json but {music_path} is missing (run music.py)")
        gain = gain_to_lufs(music_path, args.music_lufs + float(music_cfg.get("gain_db", 0)))
        music = build_music(music_path, music_cfg, n, gain)
        duck_db = float(music_cfg.get("duck_db", -11))
        voice_full = np.zeros(n, np.float32)
        voice_full[: min(n, voice.shape[1])] = voice[0, :n]
        music *= duck_envelope(voice_full, duck_db)
        mix += music
        parts.append(f"music(duck {duck_db:g} dB, start {float(music_cfg.get('start', 0)):g}s)")

    if sfx_on:
        sfx, placed = build_sfx(work, scenes, n, float(audio_cfg.get("sfx_gain_db", -6)))
        if placed:
            mix += sfx
            encode(sfx, work / "audio" / "sfx.wav", "pcm_s16le")
            parts.append(f"sfx x{placed}")

    with tmpdir() as td:
        premix = Path(td) / "premix.wav"
        limited = Path(td) / "limited.wav"
        encode(mix, premix)                                  # float WAV: no clipping before loudnorm
        try:
            pre_limit(premix, limited)
            stats = loudnorm_two_pass(limited, out)
        except RuntimeError as e:
            die(str(e))
    final = loudness(out)
    record_used(out, "mix", "ffmpeg-loudnorm-2pass", " + ".join(parts))
    print(f"{out}: {total:.2f}s  {' + '.join(parts)}")
    print(f"measured: I={final['input_i']} LUFS  TP={final['input_tp']} dBTP  LRA={final['input_lra']} LU"
          f"  (loudnorm mode: {stats.get('normalization_type', '?')})")


if __name__ == "__main__":
    main()
