#!/usr/bin/env python3
"""Music bed -> music.wav (48 kHz stereo, exact length, faded).

Chain (first available wins):
  1. ElevenLabs Music      (ELEVENLABS_API_KEY; POST /v1/music, force_instrumental, exact length)
  2. Google Lyria (Gemini) (GEMINI_API_KEY *and* GEMINI_MUSIC_MODEL set — opt-in, endpoint UNVERIFIED)
  3. music_local.py        (procedural, free, deterministic)

Whatever the provider returns is conformed to exactly --dur seconds with a short fade-in and
a 1.5 s fade-out, so mix.py can rely on the length.

Usage: music.py --dur 41.2 --mood "soft-subbass, calm tech" --bpm 108 --out audio/music.wav
                [--provider auto|elevenlabs|lyria|local] [--seed 7]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ProviderError, die, duration, ffmpeg, has_keys, has_module, http,  # noqa: E402
                    http_json, key, load_dotenv, log, record_used, tmpdir)

PROVIDERS = ("elevenlabs", "lyria", "local")


def prompt_for(mood: str, bpm: float | None, dur: float) -> str:
    tempo = f" Tempo around {int(bpm)} BPM." if bpm else ""
    return (f"Instrumental background music bed for a {int(round(dur))}-second vertical short-form "
            f"video with voice-over. Mood: {mood}.{tempo} No vocals. Sparse, steady groove that "
            "leaves space for speech in the 1-4 kHz range; consistent energy from start to end.")


def available(name: str) -> bool:
    if name == "elevenlabs":
        return has_keys("ELEVENLABS_API_KEY")
    if name == "lyria":
        return has_keys("GEMINI_API_KEY", "GEMINI_MUSIC_MODEL")
    return has_module("numpy") and has_module("scipy")


def _elevenlabs(dur: float, mood: str, bpm: float | None, seed: int, raw: Path) -> None:
    ms = int(min(max(dur, 3.0), 600.0) * 1000)          # API range: 3 s .. 10 min
    audio = http("POST", "https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",
                 {"xi-api-key": key("ELEVENLABS_API_KEY"), "Content-Type": "application/json"},
                 json.dumps({"prompt": prompt_for(mood, bpm, dur), "music_length_ms": ms,
                             "force_instrumental": True,
                             "model_id": os.environ.get("ELEVENLABS_MUSIC_MODEL", "music_v1")}).encode(),
                 timeout=600)
    raw.write_bytes(audio)


def _lyria(dur: float, mood: str, bpm: float | None, seed: int, raw: Path) -> None:
    # UNVERIFIED: assumes the Lyria model answers generateContent with inline audio, like
    # Gemini TTS does. Only runs when the operator sets GEMINI_MUSIC_MODEL explicitly.
    model = key("GEMINI_MUSIC_MODEL")
    data = http_json("POST", f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                     {"contents": [{"parts": [{"text": prompt_for(mood, bpm, dur)}]}],
                      "generationConfig": {"responseModalities": ["AUDIO"]}},
                     headers={"x-goog-api-key": key("GEMINI_API_KEY")}, timeout=600)
    for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            raw.write_bytes(base64.b64decode(part["inlineData"]["data"]))
            return
    raise ProviderError("Lyria returned no audio")


def _local(dur: float, mood: str, bpm: float | None, seed: int, raw: Path) -> None:
    from music_local import mood_preset, render, write_wav
    write_wav(raw, render(dur, mood_preset(mood), bpm, seed))


IMPL = {"elevenlabs": _elevenlabs, "lyria": _lyria, "local": _local}


def conform(src: Path, dst: Path, dur: float) -> None:
    """Exact length (pad with silence / trim), 48 kHz stereo, fade in 0.2 s, fade out 1.5 s."""
    fo = min(1.5, dur / 4)
    ffmpeg("-i", str(src), "-af",
           f"apad,atrim=0:{dur:.3f},afade=t=in:d={min(0.2, dur / 4):.3f},"
           f"afade=t=out:st={dur - fo:.3f}:d={fo:.3f}",
           "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(dst))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--mood", default="soft-subbass")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--seed", type=int, default=7, help="local generator seed")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--provider", default="auto", choices=("auto", *PROVIDERS))
    args = ap.parse_args(argv)
    load_dotenv()
    if args.dur <= 0:
        die("--dur must be > 0")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    chain = PROVIDERS if args.provider == "auto" else (args.provider,)
    with tmpdir() as td:
        for name in chain:
            if not available(name):
                continue
            raw = Path(td) / f"{name}.bin"
            try:
                IMPL[name](args.dur, args.mood, args.bpm, args.seed, raw)
                conform(raw, args.out, args.dur)
            except (ProviderError, RuntimeError, ValueError) as e:
                log(f"[music] {name} failed: {e}")
                continue
            note = "procedural bed — set ELEVENLABS_API_KEY for generated music" if name == "local" else None
            record_used(args.out, "music", name, note)
            print(f"{args.out}: {duration(args.out)}s via {name}")
            return
    die("no music provider succeeded (local generator needs numpy + scipy)")


if __name__ == "__main__":
    main()
