#!/usr/bin/env python3
"""reels-studio caption track (talking-head modes): audio/transcript.json → literal subtitle phrases.

Used by assemble.py, which renders the result as ONE root-level caption layer on the main timeline (independent
of the scene builders, so it is always present and exactly synced), and by qa.py (coverage / sync checks).

  captions.py --work work/<slug> [--json]        # print the phrase plan (debug)

Rules (references/contracts.md → "Caption track"):
  * phrases of 1–4 words and ≤ 26 characters; a new phrase starts on a pause ≥ PAUSE s, after sentence
    punctuation, at a caption-range boundary, or when the limits would be exceeded;
  * every word becomes visible at its onset − LEAD s (the reveal tween ends there — never late);
  * a phrase is shown from its first word's reveal start until the next phrase starts (swap) or
    last word end + HOLD s, whichever is first, and never past its caption range;
  * ranges: brief.captions "off" → none; "all" → whole reel; "auto" (default) → every kind head|head_overlay
    scene (+ scenes with "captions": true, − scenes with "captions": false); faceless reels without head scenes
    get no captions in auto mode.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_WORDS, MAX_CHARS = 4, 26
PAUSE = 0.28          # s — a gap this long between two words swaps the phrase
LEAD = 0.03           # s — word fully visible at onset − LEAD
REVEAL = 0.08         # s — word reveal tween length (starts at onset − LEAD − REVEAL)
HOLD = 0.55           # s — keep the last phrase of a run this long after its last word
STYLE_Y = {"d": 1470}  # caption centre y (px) by style; others 1440 (lower third, face-safe band 1250–1500)
DEFAULT_Y = 1440
SENT_END = re.compile(r"[.!?…:;]$")
COMMA = re.compile(r"[,—–]$")


def head_modes(brief: dict, plan: dict) -> bool:
    style = str(plan.get("style") or brief.get("style") or "a").lower()
    scenes = plan.get("scenes", [])
    return (brief.get("mode") in ("hook_cta", "head_overlay") or style == "d"
            or any(s.get("kind") in ("head", "head_overlay") for s in scenes))


def caption_ranges(brief: dict, plan: dict) -> list[list[float]]:
    mode = str(brief.get("captions") or plan.get("captions") or "auto").lower()
    scenes = sorted(plan.get("scenes", []), key=lambda s: float(s["start"]))
    dur = float(plan.get("duration") or (scenes[-1]["end"] if scenes else 0))
    if mode == "off" or not scenes:
        return []
    if mode == "all":
        rs = [[0.0, dur]]
        for s in scenes:  # explicit opt-outs still apply
            if s.get("captions") is False:
                rs = _subtract(rs, float(s["start"]), float(s["end"]))
        return rs
    if not head_modes(brief, plan):
        return []
    rs: list[list[float]] = []
    for s in scenes:
        on = s.get("captions")
        if on is None:
            on = s.get("kind") in ("head", "head_overlay")
        if on:
            st, en = float(s["start"]), float(s["end"])
            if rs and abs(rs[-1][1] - st) < 0.02:
                rs[-1][1] = en
            else:
                rs.append([st, en])
    return rs


def _subtract(rs, a, b):
    out = []
    for s, e in rs:
        if e <= a or s >= b:
            out.append([s, e])
            continue
        if s < a:
            out.append([s, a])
        if e > b:
            out.append([b, e])
    return out


def in_range(t: float, rs) -> int:
    for i, (s, e) in enumerate(rs):
        if s - 1e-3 <= t < e:
            return i
    return -1


def build(words: list[dict], ranges: list[list[float]]) -> list[dict]:
    """Group transcript words (final timeline) into caption phrases."""
    phrases: list[dict] = []
    cur: list[dict] = []
    cur_r = -1

    def flush():
        nonlocal cur
        if cur:
            phrases.append({"range": cur_r, "words": cur})
        cur = []

    prev = None
    for w in words:
        txt = str(w.get("w", "")).strip()
        if not txt:
            continue
        s, e = float(w["s"]), float(w.get("e", w["s"]))
        r = in_range(s, ranges)
        if r < 0:
            flush()
            prev = None
            continue
        if cur:
            chars = len(" ".join(x["w"] for x in cur)) + 1 + len(txt)
            gap = s - float(prev["e"])
            brk = (r != cur_r or len(cur) >= MAX_WORDS or chars > MAX_CHARS or gap >= PAUSE
                   or SENT_END.search(prev["w"]) or (COMMA.search(prev["w"]) and len(cur) >= 2))
            if brk:
                flush()
        cur_r = r
        cur.append({"w": txt, "s": round(s, 3), "e": round(max(e, s + 0.05), 3)})
        prev = cur[-1]
    flush()
    # timing: reveal starts at onset − LEAD − REVEAL; phrase shown from its first reveal start to the next swap
    for p in phrases:
        for w in p["words"]:
            w["appear"] = round(w["s"] - LEAD, 3)              # fully visible here
            w["t0"] = round(max(0.0, w["s"] - LEAD - REVEAL), 3)  # reveal tween start (never before the reel starts)
            w["dur"] = round(max(0.01, min(REVEAL, w["appear"] - w["t0"])), 3)
    for i, p in enumerate(phrases):
        p["show"] = p["words"][0]["t0"]
        rs, re_ = ranges[p["range"]]
        hide = min(p["words"][-1]["e"] + HOLD, re_ + 0.12)
        p["swap"] = False                      # False → run end: fade out (0.2 s) instead of a one-frame swap
        if i + 1 < len(phrases) and phrases[i + 1]["words"][0]["t0"] <= hide:
            hide = phrases[i + 1]["words"][0]["t0"]
            p["swap"] = True
        p["show"] = max(p["show"], rs - 0.12, 0.0)
        # a swap is exact (never overlap the next phrase); a run end keeps the last word ≥ 0.15 s on screen
        p["hide"] = round(hide if p["swap"] else max(hide, p["words"][-1]["appear"] + 0.15), 3)
        p["text"] = " ".join(w["w"] for w in p["words"])
    return phrases


def coverage(words: list[dict], ranges, phrases) -> dict:
    spoken = [w for w in words if str(w.get("w", "")).strip() and in_range(float(w["s"]), ranges) >= 0]
    shown = sum(len(p["words"]) for p in phrases)
    total = len([w for w in words if str(w.get("w", "")).strip()])
    return {"words_total": total, "words_in_ranges": len(spoken), "captioned": shown,
            "pct_in_ranges": round(100.0 * shown / len(spoken), 1) if spoken else None,
            "pct_total": round(100.0 * shown / total, 1) if total else None,
            "ranges_sec": round(sum(e - s for s, e in ranges), 3)}


def plan_captions(work: Path, plan: dict | None = None, brief: dict | None = None) -> dict | None:
    plan = plan or json.loads((work / "plan" / "scenes.json").read_text())
    brief = brief if brief is not None else (json.loads((work / "brief.json").read_text())
                                             if (work / "brief.json").is_file() else {})
    tr_p = work / "audio" / "transcript.json"
    ranges = caption_ranges(brief, plan)
    if not ranges:
        return None
    if not tr_p.is_file():
        return {"error": "audio/transcript.json missing", "ranges": ranges, "phrases": []}
    tr = json.loads(tr_p.read_text())
    words = tr.get("words", [])
    phrases = build(words, ranges)
    style = str(plan.get("style") or brief.get("style") or "a").lower()
    y = int(brief.get("captions_y") or STYLE_Y.get(style, DEFAULT_Y))
    return {"style": style, "y": y, "ranges": ranges, "phrases": phrases, "lead": LEAD, "reveal": REVEAL,
            "source": tr.get("source"), "coverage": coverage(words, ranges, phrases)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    res = plan_captions(Path(a.work).resolve())
    print(json.dumps(res, ensure_ascii=False, indent=1) if res else '{"captions": "off"}')


if __name__ == "__main__":
    sys.exit(main())
