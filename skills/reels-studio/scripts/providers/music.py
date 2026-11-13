#!/usr/bin/env python3
"""Music bed -> music.wav (48 kHz stereo, exact length, faded).

Chain (first available wins):
  1. client track          work/<slug>/input/music.* (the client's own / licensed track) — fitted
                           on a downbeat like a search result; licence is the client's responsibility
  2. internet search       providers/music_search.py: Openverse (no key) + Jamendo (JAMENDO_CLIENT_ID);
                           CC0/CC BY only, analysed + ranked, writes audio/music_candidates.json and CREDITS.txt
  3. ElevenLabs Music      (ELEVENLABS_API_KEY; POST /v1/music, force_instrumental, exact length)
  4. Google Lyria (Gemini) (GEMINI_API_KEY *and* GEMINI_MUSIC_MODEL set — opt-in, endpoint UNVERIFIED)
  5. music_local.py        (procedural, free, deterministic; energetic profile never uses the
                           sub-bass-only preset — it is inaudible on phone speakers)

Network errors in 1–4 fall through to the next provider. Generated results are conformed to
exactly --dur seconds (fade-in 0.2 s, fade-out 1.5 s); client/search tracks are trimmed on a
downbeat with 0.5 s fade-in / 1.2 s fade-out (or looped with crossfades).

Usage: music.py --dur 41.2 --mood "driving, punchy groove" --bpm 108 --out audio/music.wav
                [--work work/<slug>] [--provider auto|client|search|elevenlabs|lyria|local] [--seed 7]
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

PROVIDERS = ("client", "search", "elevenlabs", "lyria", "local")


def prompt_for(mood: str, bpm: float | None, dur: float) -> str:
    tempo = f" Tempo around {int(bpm)} BPM." if bpm else ""
    return (f"Instrumental background music bed for a {int(round(dur))}-second vertical short-form "
            f"video with voice-over. Mood: {mood}.{tempo} No vocals. Sparse, steady groove that "
            "leaves space for speech in the 1-4 kHz range; consistent energy from start to end.")


def client_track(work: Path | None) -> Path | None:
    if not work:
        return None
    for p in sorted((work / "input").glob("music.*")):
        if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"):
            return p
    return None


def available(name: str, work: Path | None = None) -> bool:
    if name == "client":
        return client_track(work) is not None
    if name == "search":
        return has_module("numpy") and has_module("librosa") and os.environ.get("REELS_NO_NETWORK") != "1"
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
    preset = mood_preset(mood)
    if preset == "soft-subbass" and os.environ.get("REELS_AUDIO_PROFILE", "energetic") == "energetic":
        preset = "upbeat"          # a sub-bass-only bed disappears on phone speakers
    write_wav(raw, render(dur, preset, bpm, seed))


IMPL = {"elevenlabs": _elevenlabs, "lyria": _lyria, "local": _local}


def conform(src: Path, dst: Path, dur: float) -> None:
    """Exact length (pad with silence / trim), 48 kHz stereo, fade in 0.2 s, fade out 1.5 s."""
    fo = min(1.5, dur / 4)
    ffmpeg("-i", str(src), "-af",
           f"apad,atrim=0:{dur:.3f},afade=t=in:d={min(0.2, dur / 4):.3f},"
           f"afade=t=out:st={dur - fo:.3f}:d={fo:.3f}",
           "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(dst))


def _client(work: Path, dur: float, out: Path) -> str:
    import music_search as ms
    src = client_track(work)
    a = ms.analyse(src)
    how = ms.conform(src, a, dur, out)
    ms.write_credits(work, "music", [f"track: client-supplied {src.name} (licence: client's responsibility)",
                                     "CAPTION: (as agreed with the client)"])
    return how


def _search(work: Path | None, dur: float, mood: str, bpm: float | None, out: Path) -> str:
    import music_search as ms
    intent = ms.load_intent(work, mood if mood != "soft-subbass" else None,
                            f"{bpm - 6:g}-{bpm + 6:g}" if bpm else None, None, None, dur)
    c = ms.search(intent, out, work)
    return f"\"{c['title']}\" by {c['artist']} [{c['licence']}]"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--mood", default="soft-subbass")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--seed", type=int, default=7, help="local generator seed")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--provider", default="auto", choices=("auto", *PROVIDERS))
    ap.add_argument("--work", type=Path, help="work/<slug> (default: inferred from --out)")
    args = ap.parse_args(argv)
    load_dotenv()
    work = args.work
    if work is None and args.out.resolve().parent.name == "audio":
        work = args.out.resolve().parent.parent
    if work and (work / "brief.json").is_file():
        try:
            prof = json.loads((work / "brief.json").read_text(encoding="utf-8")).get("audio_profile")
        except json.JSONDecodeError:
            prof = None
        if prof:
            os.environ.setdefault("REELS_AUDIO_PROFILE", prof)
    if args.dur <= 0:
        die("--dur must be > 0")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    chain = PROVIDERS if args.provider == "auto" else (args.provider,)
    with tmpdir() as td:
        for name in chain:
            if not available(name, work):
                continue
            raw = Path(td) / f"{name}.bin"
            try:
                if name == "client":
                    how = _client(work, args.dur, args.out)
                    record_used(args.out, "music", "client", how)
                    print(f"{args.out}: {duration(args.out)}s via client track ({how})")
                    return
                if name == "search":
                    how = _search(work, args.dur, args.mood, args.bpm, args.out)   # records env/CREDITS itself
                    print(f"{args.out}: {duration(args.out)}s via internet search {how}")
                    return
                IMPL[name](args.dur, args.mood, args.bpm, args.seed, raw)
                conform(raw, args.out, args.dur)
            except (ProviderError, RuntimeError, ValueError, OSError, ImportError) as e:
                log(f"[music] {name} failed: {e}")
                continue
            note = "procedural bed — set ELEVENLABS_API_KEY for generated music" if name == "local" else None
            record_used(args.out, "music", name, note)
            if work:
                try:
                    import music_search as ms
                    ms.write_credits(work, "music", [f"track: generated by {name} (no attribution required)",
                                                     "CAPTION: (not required)"])
                except ImportError:
                    pass
            print(f"{args.out}: {duration(args.out)}s via {name}")
            return
    die("no music provider succeeded (local generator needs numpy + scipy)")


if __name__ == "__main__":
    main()
