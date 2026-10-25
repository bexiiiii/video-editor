#!/usr/bin/env python3
"""Convert word timings returned by the ElevenLabs connector (creative_transcribe_audio) into
the contracts.md transcript format.

  connector_words.py audio/connector_words.json --lang uz --out audio/transcript.json
                     [--text input/script.txt] [--audio audio/voice.wav]

Accepts the shapes the connector may return: {"transcripts":[{"words":[...]}]}, {"words":[...]},
or a bare list. Each word may use text|word and start|s / end|e; non-word entries
(type "spacing"/"audio_event") are dropped. With --text, timings are transferred onto the known
script (exact spelling), like asr.py --text. --audio sets the total duration (else last word end).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
from common import (align_script, build_transcript, die, duration, record_used,  # noqa: E402
                    validate_transcript, write_json)


def extract_words(data) -> list[dict]:
    if isinstance(data, dict):
        if "transcripts" in data:
            data = [w for t in data["transcripts"] for w in t.get("words", [])]
        else:
            data = data.get("words", [])
    out = []
    for w in data or []:
        if w.get("type", "word") not in ("word", None):
            continue
        text = (w.get("text") if "text" in w else w.get("word", "")) or ""
        s = w.get("start", w.get("s"))
        e = w.get("end", w.get("e", s))
        if text.strip() and s is not None:
            out.append({"w": text.strip(), "s": float(s), "e": float(e)})
    return sorted(out, key=lambda x: x["s"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words_json")
    ap.add_argument("--lang", required=True, choices=["ru", "uz", "kk"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", help="known script to align onto (exact spelling)")
    ap.add_argument("--audio", help="audio file for the total duration")
    a = ap.parse_args()

    words = extract_words(json.loads(Path(a.words_json).read_text(encoding="utf-8")))
    if not words:
        die("no words found in the connector output")
    if a.text:
        words = align_script(words, Path(a.text).read_text(encoding="utf-8"))
    total = duration(Path(a.audio)) if a.audio else words[-1]["e"]
    t = build_transcript(words, a.lang, "elevenlabs-connector", total)
    problems = validate_transcript(t)
    if problems:
        die("invalid transcript: " + "; ".join(problems[:5]))
    out = Path(a.out)
    write_json(out, t)
    record_used(out, "asr", "elevenlabs-connector")
    print(f"{out}: {len(t['words'])} words, {len(t['sentences'])} sentences, {t['duration']}s")


if __name__ == "__main__":
    main()
