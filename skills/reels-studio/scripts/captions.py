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
    get no captions in auto mode. A scene's "caption_mute": [[s, e], …] (scene-local seconds) removes those
    windows — style F mutes the small captions while a kinetic stack is on screen;
  * style F: phrases of 1–3 words / ≤ 22 chars shown WHOLE on the first word (hard swap, no per-word reveal) and a
    highlight flag on words with digits or listed in brief.captions_highlight (rendered yellow by assemble.py).
  * style G (editorial stacks): director-marked emphasis words (scenes[].emphasis / brief.emphasis, contracts.md →
    "Style G emphasis") are matched in the transcript (multi-word marks are merged into one token); an emphasis word
    ENDS its phrase (≤ 3 lead words before it, + its `tuck` words after it) and the phrase gets
    `emph: {i, treat, tuck, leadAlign}`; phrases inside scenes[].statements windows (or a scene with
    "statement": true) get kind "statement" (white M two-line); the rest kind "small". assemble.py renders them with
    RSG.captionTrack (one stack per phrase, per-word reveal on the onset, hard swaps).
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
EMPH_HOLD = 0.8       # s — style G: an emphasis stack stays ≥ this long after its emphasis word lands
STYLE_Y = {"d": 1470, "f": 1328, "g": 1335}  # caption centre y (px) by style; others 1440 (lower third, face-safe band 1250–1500)
STYLE_LIMITS = {"f": (3, 22), "g": (4, 24)}      # (max words, max chars) per phrase by style; default (MAX_WORDS, MAX_CHARS)
FOOTAGE_STYLES = ("d", "f", "g")        # styles that always sit on talking-head footage
DEFAULT_Y = 1440
SENT_END = re.compile(r"[.!?…:;]$")
COMMA = re.compile(r"[,—–]$")


def head_modes(brief: dict, plan: dict) -> bool:
    style = str(plan.get("style") or brief.get("style") or "a").lower()
    scenes = plan.get("scenes", [])
    return (brief.get("mode") in ("hook_cta", "head_overlay") or style in FOOTAGE_STYLES
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
        return _mute(rs, scenes)
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
    return _mute(rs, scenes)


def _mute(rs, scenes):
    """Subtract every scene's caption_mute windows (scene-local seconds) — e.g. style F kinetic-stack windows."""
    for s in scenes:
        st = float(s["start"])
        for w in s.get("caption_mute") or []:
            a, b = float(w[0]) + st, float(w[1]) + st
            if b > a:
                rs = _subtract(rs, a, b)
    return [r for r in rs if r[1] - r[0] > 0.05]


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


def build(words: list[dict], ranges: list[list[float]], max_words: int = MAX_WORDS,
          max_chars: int = MAX_CHARS, emph: dict | None = None) -> list[dict]:
    """Group transcript words (final timeline) into caption phrases.
    emph (style G): {word index → mark}; an emphasis word ends its phrase after its `tuck` words."""
    emph = emph or {}
    tuck_left = 0
    phrases: list[dict] = []
    cur: list[dict] = []
    cur_r = -1

    def flush():
        nonlocal cur
        if cur:
            phrases.append({"range": cur_r, "words": cur})
        cur = []

    prev = None
    for wi, w in enumerate(words):
        txt = str(w.get("w", "")).strip()
        if not txt:
            continue
        s, e = float(w["s"]), float(w.get("e", w["s"]))
        r = in_range(s, ranges)
        if r < 0:
            flush()
            prev = None
            continue
        if cur and tuck_left > 0:
            if r == cur_r and s - float(prev["e"]) < 0.6:   # tucked words stay with their emphasis
                cur.append({"w": txt, "s": round(s, 3), "e": round(max(e, s + 0.05), 3)})
                prev = cur[-1]
                tuck_left -= 1
                if tuck_left == 0:
                    flush()
                continue
            tuck_left = 0
            flush()
        if cur:
            chars = len(" ".join(x["w"] for x in cur)) + 1 + len(txt)
            gap = s - float(prev["e"])
            if wi in emph:   # emphasis: may follow up to 3 lead words; the lead's own length limit applies
                brk = r != cur_r or len(cur) >= 4 or gap >= PAUSE * 2 or SENT_END.search(prev["w"])
            else:
                brk = (r != cur_r or len(cur) >= max_words or chars > max_chars or gap >= PAUSE
                       or SENT_END.search(prev["w"]) or (COMMA.search(prev["w"]) and len(cur) >= 2))
            if brk:
                flush()
        cur_r = r
        cur.append({"w": txt, "s": round(s, 3), "e": round(max(e, s + 0.05), 3)})
        prev = cur[-1]
        if wi in emph:
            m = emph[wi]
            phr_emph = {"i": len(cur) - 1, "treat": m.get("treat") or "bold-white", "tuck": int(m.get("tuck") or 0)}
            if m.get("lead_align"):
                phr_emph["leadAlign"] = m["lead_align"]
            if m.get("join"):
                phr_emph["join"] = True
            cur[-1]["_emph"] = phr_emph
            tuck_left = phr_emph["tuck"]
            if tuck_left == 0:
                flush()
    flush()
    for p in phrases:   # lift the emphasis mark from its word onto the phrase
        for w in p["words"]:
            if "_emph" in w:
                p["emph"] = w.pop("_emph")
    # "join": an emphasis that opens its phrase is appended to the previous stack as its 2nd emphasis line
    # (ref "слово / даже · важнее / жизни")
    merged: list[dict] = []
    for p in phrases:
        e = p.get("emph") or {}
        if e.get("join") and e.get("i") == 0 and len(p["words"]) == 1 and merged and merged[-1].get("emph") \
                and "emph2" not in merged[-1] and merged[-1]["range"] == p["range"]:
            q = merged[-1]
            q["emph2"] = {"i": len(q["words"]), "treat": e.get("treat", "bold-white")}
            q["words"] += p["words"]
            continue
        merged.append(p)
    phrases = merged
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


_PUNCT = re.compile(r"[.,!?…:;«»\"()]")


def _norm(t: str) -> str:
    return _PUNCT.sub("", str(t)).lower().replace("ё", "е").strip()


def emphasis_marks(plan: dict, brief: dict) -> list[dict]:
    """Style G: absolute emphasis marks [{word, treat, tuck, lead_align, at|None, win:[s,e]}] from scenes[].emphasis
    (scene-local `at`) and brief.emphasis (absolute `at`)."""
    out = []
    for sc in plan.get("scenes", []):
        st, en = float(sc["start"]), float(sc["end"])
        for m in sc.get("emphasis") or []:
            m = {"word": m} if isinstance(m, str) else dict(m)
            if m.get("at") is not None:
                m["at"] = float(m["at"]) + st
            m["win"] = [st, en]
            out.append(m)
    for m in brief.get("emphasis") or []:
        m = {"word": m} if isinstance(m, str) else dict(m)
        m["win"] = [0.0, 1e9]
        out.append(m)
    return out


def apply_emphasis(words: list[dict], marks: list[dict]) -> tuple[list[dict], dict, list[str]]:
    """Merge multi-word marks into one token and return (words, {index → mark}, warnings)."""
    words = [dict(w) for w in words if str(w.get("w", "")).strip()]
    found: dict[int, dict] = {}
    warns = []
    for m in marks:
        toks = [_norm(t) for t in str(m.get("word", "")).split()]
        if not toks:
            continue
        best, bd = None, 1e9
        for i in range(len(words) - len(toks) + 1):
            s = float(words[i]["s"])
            if not (m["win"][0] - 0.05 <= s < m["win"][1]):
                continue
            seg = [_norm(words[i + k]["w"]) for k in range(len(toks))]
            ok = all(a == b or (len(b) >= 4 and a.startswith(b[:-1])) for a, b in zip(seg, toks))
            if ok:
                d = abs(s - m["at"]) if m.get("at") is not None else s
                if d < bd and i not in found:
                    best, bd = i, d
        if best is None:
            warns.append(f"emphasis word not found in transcript: {m.get('word')!r}")
            continue
        if len(toks) > 1:   # merge into one token (keeps the first onset, the last end)
            j = best + len(toks)
            words[best] = {"w": " ".join(w["w"] for w in words[best:j]), "s": words[best]["s"], "e": words[j - 1].get("e", words[j - 1]["s"])}
            del words[best + 1:j]
            found = {(k if k <= best else k - (len(toks) - 1)): v for k, v in found.items()}
        found[best] = m
    return words, found, warns


def statement_windows(plan: dict) -> list[list[float]]:
    out = []
    for sc in plan.get("scenes", []):
        st, en = float(sc["start"]), float(sc["end"])
        if sc.get("statement") is True:
            out.append([st, en])
        for w in sc.get("statements") or []:
            out.append([float(w[0]) + st, float(w[1]) + st])
    return out


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
    style = str(plan.get("style") or brief.get("style") or "a").lower()
    mw, mc = STYLE_LIMITS.get(style, (MAX_WORDS, MAX_CHARS))
    warns: list[str] = []
    if style == "g":
        words, emarks, warns = apply_emphasis(words, emphasis_marks(plan, brief))
        phrases = build(words, ranges, mw, mc, emarks)
        sw = statement_windows(plan)
        for p in phrases:
            if "emph" not in p:
                t0 = p["words"][0]["s"]
                p["kind"] = "statement" if any(a <= t0 < b for a, b in sw) else "small"
            else:
                p["kind"] = "stack"
        # an emphasis stack must be readable: hold it ≥ EMPH_HOLD after the emphasis onset; the next phrase starts
        # later and its early words reveal on its show time (late, never early)
        for i, p in enumerate(phrases[:-1]):
            if "emph" not in p:
                continue
            t_e = p["words"][p["emph"]["i"]]["s"]
            q = phrases[i + 1]
            if p.get("swap") and p["hide"] - t_e < EMPH_HOLD:
                new = round(t_e + EMPH_HOLD, 3)
                if q["range"] == p["range"] and new < q["words"][-1]["s"] + 0.3:
                    p["hide"] = new
                    q["show"] = new
    else:
        phrases = build(words, ranges, mw, mc)
    if style == "f":  # highlight words: digits + brief.captions_highlight (yellow in the assembled track)
        hl = {str(x).lower() for x in (brief.get("captions_highlight") or [])}
        for p in phrases:
            for w in p["words"]:
                clean = re.sub(r"[.,!?…:;«»\"]", "", w["w"]).lower()
                if re.search(r"\d", clean) or clean in hl:
                    w["hl"] = True
    y = int(brief.get("captions_y") or STYLE_Y.get(style, DEFAULT_Y))
    return {"style": style, "y": y, "ranges": ranges, "phrases": phrases, "lead": LEAD, "reveal": REVEAL,
            "source": tr.get("source"), "coverage": coverage(words, ranges, phrases),
            **({"warnings": warns} if warns else {})}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    res = plan_captions(Path(a.work).resolve())
    print(json.dumps(res, ensure_ascii=False, indent=1) if res else '{"captions": "off"}')


if __name__ == "__main__":
    sys.exit(main())
