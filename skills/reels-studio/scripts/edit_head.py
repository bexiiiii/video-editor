#!/usr/bin/env python3
"""reels-studio talking-head editor (step 1a, footage modes).

  edit_head.py --work work/<slug> [--max-silence 0.35] [--pad 0.12] [--fillers "э,ну"] [--no-retakes]
               [--crop-x 0.5] [--xfade-ms 42.7] [--force] [--keep-tmp] [--dry-run]

Pipeline
  1. Probe every `brief.footage` take (rotation metadata is applied by ffmpeg autorotate), normalise to
     1080×1920 / 30 fps CFR (scale-to-cover + crop, `--crop-x` picks the horizontal centre for landscape
     footage), 48 kHz mono audio, and concatenate the takes → edit/tmp/source.mp4.
     The SOURCE TIMELINE is this concatenation (take 1, then take 2, …). `audio/transcript.json` (from
     asr.py) and, if present, `audio/voice.wav` (from cleanup.py) must be on that timeline.
  2. Plan cuts from word timings: drop filler words (per-language list, elongations like "эээ" match
     "э"), drop retakes (a sentence repeated/restarted by one of the next two sentences → keep the last),
     remove silences longer than --max-silence keeping --pad on each side. Without a transcript the
     plan falls back to an energy-based silence detector.
  3. Snap kept ranges to the 30 fps frame grid; render edit/head.mp4 frame-accurately (select by frame
     index) with audio spliced in numpy using short linear crossfades at every cut (no clicks, exact
     length = video length).
  4. Remap word times to the final timeline: audio/transcript.source.json keeps the original,
     audio/transcript.json becomes the final-timeline transcript (words, sentences, pauses). Likewise
     audio/voice.source.wav keeps the source voice and audio/voice.wav becomes the cut voice.
  5. Write edit/cuts.json: segments (source→final), removed ranges with reasons, and punch-in suggestions
     (alternating scale 1.0 / 1.12 on cut points every ~3–5 s) for assemble.py.
     Style F ("Kinetic Talking Head", `--framing auto` with brief.style "F", or `--framing two-cam`): the
     "two camera" look from ONE camera — wide 1.0 ↔ tight `--tight` (default 1.4, ref 1.25–1.55) switched on
     EVERY cut (tight segments ≤ 3.2 s; a long segment gets an extra switch on a word onset), anchored on the
     face/eye line: OpenCV Haar face detection on the first seconds of the source when cv2 is installed, else
     `--anchor-x/--anchor-y` (default 0.5 / 0.30). `--drift 0.03` adds a slow zoom inside segments ≥ 2.5 s.

Resumable: skips when edit/head.mp4 and edit/cuts.json are newer than their inputs (use --force).
Requires ffmpeg/ffprobe and numpy.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

FPS = 30
W, H = 1080, 1920
SR = 48000
DEFAULT_FILLERS = {  # compared after lower-casing, stripping punctuation and collapsing repeated letters
    "ru": ["э", "ээ", "ну", "типа", "эм", "мм"],
    "uz": ["ээ", "мм", "ee", "mm"],
    "kk": ["ээ", "мм"],
}


def log(msg: str) -> None:
    print(f"[edit_head] {msg}", file=sys.stderr)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise SystemExit(f"command failed ({p.returncode}): {' '.join(cmd[:6])} …\n{p.stderr[-2000:]}")
    return p


def probe(path: Path) -> dict:
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    info = json.loads(p.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    if v is None:
        raise SystemExit(f"no video stream in {path}")
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(round(float(sd["rotation"])))
    if "rotate" in (v.get("tags") or {}):
        rot = int(v["tags"]["rotate"])
    w, h = int(v["width"]), int(v["height"])
    if abs(rot) % 180 == 90:
        w, h = h, w
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    return {"path": str(path), "width": w, "height": h, "rotation": rot,
            "fps": float(num) / float(den or 1) if float(den or 1) else 30.0,
            "duration": float(info["format"].get("duration") or v.get("duration") or 0),
            "has_audio": any(s["codec_type"] == "audio" for s in info["streams"])}


def media_duration(path: Path) -> float:
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(p.stdout.strip() or 0)


def read_audio(path: Path):
    import numpy as np
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(SR),
                        "-f", "f32le", "-"], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"cannot decode audio from {path}: {p.stderr.decode()[-500:]}")
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


def write_wav(path: Path, x) -> None:
    import numpy as np
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    import wave
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)  # noqa: E702


# ----------------------------------------------------------------------------- normalise

def normalise(takes: list[dict], out: Path, crop_x: float) -> None:
    """Scale-to-cover + crop each take to 1080×1920 30 fps (48 kHz mono PCM), then concatenate.

    Each take is normalised in its own single-input ffmpeg run: with several inputs in one
    filter_complex, ffmpeg 7.x copies input 0's display-matrix (rotation) side data onto the output,
    so players would rotate the already-rotated picture again.
    """
    parts = []
    for i, t in enumerate(takes):
        part = out.parent / f"take_{i:02d}.mkv"
        cx = f"(iw-{W})*{crop_x:.4f}"
        fl = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
              f"crop={W}:{H}:{cx}:(ih-{H})/2,setsar=1,fps={FPS},format=yuv420p[v]"]
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", t["path"]]
        if t["has_audio"]:
            fl.append(f"[0:a]aresample={SR},aformat=sample_fmts=s16:channel_layouts=mono,"
                      f"apad,atrim=0:{t['duration']:.3f}[a]")
        else:
            fl.append(f"anullsrc=r={SR}:cl=mono,atrim=0:{t['duration']:.3f}[a]")
        cmd += ["-filter_complex", ";".join(fl), "-map", "[v]", "-map", "[a]", "-t", f"{t['duration']:.3f}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-g", "30",
                "-c:a", "pcm_s16le", "-ar", str(SR), str(part)]
        run(cmd)
        parts.append(part)
    if len(parts) == 1:
        parts[0].replace(out)
        return
    lst = out.parent / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    for p in parts:
        p.unlink(missing_ok=True)


# ----------------------------------------------------------------------------- planning

def norm_word(w: str) -> str:
    w = re.sub(r"[^\w'-]+", "", w.lower()).replace("ё", "е")
    return re.sub(r"(.)\1+", r"\1", w)


def build_sentences(words: list[dict]) -> list[dict]:
    out, start = [], 0
    for i, w in enumerate(words):
        if re.search(r"[.!?…]$", w["w"].strip()) or i == len(words) - 1:
            out.append({"text": " ".join(x["w"] for x in words[start:i + 1]),
                        "s": words[start]["s"], "e": w["e"], "w0": start, "w1": i})
            start = i + 1
    return out


def detect_retakes(words: list[dict], sentences: list[dict], thresh: float) -> set[int]:
    """Indices of words in sentences that are repeated/restarted by one of the next two sentences."""
    drop: set[int] = set()
    toks = [[norm_word(words[k]["w"]) for k in range(s["w0"], s["w1"] + 1)] for s in sentences]
    for i in range(len(sentences)):
        a = " ".join(toks[i])
        if len(toks[i]) < 2:
            continue
        for j in (i + 1, i + 2):
            if j >= len(sentences):
                break
            b = " ".join(toks[j])
            prefix = b.startswith(a) or (len(toks[i]) >= 3 and " ".join(toks[j][:len(toks[i])]) == a)
            ratio = difflib.SequenceMatcher(None, a, b).ratio()
            # false start: sentence i is (nearly) a prefix of j; full retake: similar text
            head = " ".join(toks[j][:len(toks[i])])
            if prefix or ratio >= thresh or difflib.SequenceMatcher(None, a, head).ratio() >= max(thresh, 0.85):
                drop.update(range(sentences[i]["w0"], sentences[i]["w1"] + 1))
                break
    return drop


def energy_speech(audio, min_sil: float) -> list[tuple[float, float]]:
    """Fallback speech regions from RMS energy (10 ms hop, adaptive threshold)."""
    import numpy as np
    hop = SR // 100
    n = len(audio) // hop
    if n == 0:
        return []
    rms = np.sqrt((audio[:n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    floor, peak = np.percentile(db, 10), np.percentile(db, 95)
    th = floor + 0.35 * (peak - floor)
    on = db > th
    regs, i = [], 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            regs.append([i / 100, j / 100])
            i = j
        else:
            i += 1
    merged = []
    for r in regs:
        if merged and r[0] - merged[-1][1] <= min_sil:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [(a, b) for a, b in merged if b - a >= 0.08]


def plan_cuts(words, dur, fillers, retakes, max_sil, pad, retake_thresh):
    """Return (kept ranges [(s,e)] in source seconds, removed [{type,s,e,text}], kept word indices)."""
    removed, drop = [], {}
    fl = {norm_word(f) for f in fillers}
    for i, w in enumerate(words):
        if norm_word(w["w"]) in fl:
            drop[i] = "filler"
    if retakes:
        sents = build_sentences(words)
        for i in detect_retakes(words, sents, retake_thresh):
            drop.setdefault(i, "retake")
    keep = [i for i in range(len(words)) if i not in drop]
    groups: list[list[int]] = []
    for i in keep:
        if groups:
            prev = groups[-1][-1]
            gap = words[i]["s"] - words[prev]["e"]
            if gap <= max_sil and not any(k in drop for k in range(prev + 1, i)):
                groups[-1].append(i)
                continue
        groups.append([i])
    ranges = []
    for g in groups:
        s = words[g[0]]["s"] - pad
        e = words[g[-1]]["e"] + pad
        # never pad into a dropped neighbour word
        if g[0] - 1 >= 0 and (g[0] - 1) in drop:
            s = max(s, words[g[0] - 1]["e"])
        if g[-1] + 1 < len(words) and (g[-1] + 1) in drop:
            e = min(e, words[g[-1] + 1]["s"])
        ranges.append([max(0.0, s), min(dur, e)])
    for i, why in sorted(drop.items()):
        removed.append({"type": why, "s": words[i]["s"], "e": words[i]["e"], "text": words[i]["w"]})
    return ranges, removed, keep


def snap(ranges, dur) -> list[tuple[int, int]]:
    """Snap to frame indices [f0, f1) and merge overlaps; drop segments < 2 frames."""
    import math
    nmax = int(math.floor(dur * FPS + 1e-6))
    fr = []
    for s, e in ranges:
        f0, f1 = int(math.floor(s * FPS + 1e-6)), min(nmax, int(math.ceil(e * FPS - 1e-6)))
        if f1 - f0 < 2:
            continue
        if fr and f0 <= fr[-1][1]:
            fr[-1][1] = max(fr[-1][1], f1)
        else:
            fr.append([f0, f1])
    return [tuple(x) for x in fr]


def splice_audio(audio, frames, xfade_s: float):
    """Concatenate source audio for frame ranges with linear crossfades (length = video length)."""
    import numpy as np
    spf = SR / FPS
    total = int(round(sum(f1 - f0 for f0, f1 in frames) * spf))
    out = np.zeros(total, np.float32)
    h = int(round(xfade_s * SR / 2))
    o = 0.0
    for k, (f0, f1) in enumerate(frames):
        s, e = int(round(f0 * spf)), int(round(f1 * spf))
        hs = h if k > 0 else 0
        he = h if k < len(frames) - 1 else 0
        a0, a1 = max(0, s - hs), min(len(audio), e + he)
        seg = audio[a0:a1].copy()
        if len(seg) == 0:
            o += (f1 - f0) * spf
            continue
        lead = s - a0
        if hs and lead > 0:
            seg[:2 * lead] *= np.linspace(0, 1, min(2 * lead, len(seg)), dtype=np.float32)
        tail = a1 - e
        if he and tail > 0:
            n = min(2 * tail, len(seg))
            seg[-n:] *= np.linspace(1, 0, n, dtype=np.float32)
        dst = int(round(o)) - lead
        d0, s0 = max(0, dst), max(0, -dst)
        n = min(len(seg) - s0, total - d0)
        if n > 0:
            out[d0:d0 + n] += seg[s0:s0 + n]
        o += (f1 - f0) * spf
    return out


def remap_transcript(tr: dict, words, keep, frames, removed_total: float) -> dict:
    segs, o = [], 0.0
    for f0, f1 in frames:
        s, e = f0 / FPS, f1 / FPS
        segs.append((s, e, o))
        o += e - s
    dur = o

    def m(t):
        for s, e, off in segs:
            if s - 1e-6 <= t <= e + 1e-6:
                return round(off + min(max(t, s), e) - s, 3)
        return None

    nw, kept_src = [], {}
    for i in keep:
        w = words[i]
        s, e = m(w["s"]), m(w["e"])
        if s is None and e is None:
            continue
        if s is None:
            s = max(0.0, e - (w["e"] - w["s"]))
        if e is None or e < s:
            e = s + min(w["e"] - w["s"], 0.05)
        kept_src[i] = len(nw)
        nw.append({**w, "s": round(s, 3), "e": round(min(e, dur), 3)})
    sents = []
    src_sents = tr.get("sentences") or []
    if src_sents:
        # keep original sentence boundaries (text = kept words only)
        for st in src_sents:
            idx = [kept_src[k] for k in range(st["w0"], st["w1"] + 1) if k in kept_src]
            if idx:
                sents.append({"text": " ".join(nw[k]["w"] for k in idx), "s": nw[idx[0]]["s"],
                              "e": nw[idx[-1]]["e"], "w0": idx[0], "w1": idx[-1]})
    else:
        sents = build_sentences(nw)
    pauses = []
    for a, b in zip(nw, nw[1:]):
        if b["s"] - a["e"] >= 0.15:
            pauses.append({"s": a["e"], "e": b["s"]})
    out = {k: v for k, v in tr.items() if k not in ("words", "sentences", "pauses", "duration")}
    out.update({"duration": round(dur, 3), "timeline": "final", "words": nw, "sentences": sents,
                "pauses": pauses, "edit": {"removed_sec": round(removed_total, 3), "by": "edit_head.py"}})
    return out


def punch_ins(frames, words_final, dur, lo=3.0, hi=5.0, zoom=1.12) -> list[dict]:
    """Alternate scale 1.0/zoom, switching on cut points spaced lo..hi s (pauses/words as backup)."""
    cuts, o = [], 0.0
    for f0, f1 in frames[:-1]:
        o += (f1 - f0) / FPS
        cuts.append(round(o, 3))
    backups = sorted({round(w["s"], 3) for w in words_final})
    t, scale, out = 0.0, 1.0, []
    while True:
        cand = [c for c in cuts if lo <= c - t <= hi]
        if cand:
            nxt = cand[0]
        else:
            b = [x for x in backups if lo + 0.5 <= x - t <= hi]
            nxt = b[0] if b else t + 4.0
        if dur - nxt < 1.5:
            out.append({"start": round(t, 3), "end": round(dur, 3), "scale": scale})
            break
        out.append({"start": round(t, 3), "end": round(nxt, 3), "scale": scale,
                    "on": "cut" if nxt in cuts else "word"})
        t, scale = nxt, (zoom if scale == 1.0 else 1.0)
    return out


def face_anchor(source: Path, start: float = 0.5, n: int = 5, step: float = 0.6) -> dict | None:
    """Face / eye-line anchor (0..1) from the first seconds of the CFR source via OpenCV's Haar cascade.
    Returns None when cv2 is missing or no face is found (callers fall back to the configured anchor)."""
    try:
        import cv2  # type: ignore
    except Exception:
        return None
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if casc.empty():
        return None
    cap = cv2.VideoCapture(str(source))
    pts = []
    for i in range(n):
        cap.set(cv2.CAP_PROP_POS_MSEC, (start + i * step) * 1000)
        ok, fr = cap.read()
        if not ok:
            continue
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        h, w = g.shape[:2]
        faces = casc.detectMultiScale(g, scaleFactor=1.1, minNeighbors=5, minSize=(w // 10, w // 10))
        if len(faces):
            x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            pts.append(((x + fw / 2) / w, (y + 0.42 * fh) / h))   # eye line ≈ 42 % down the face box
    cap.release()
    if not pts:
        return None
    pts.sort()
    mx = pts[len(pts) // 2][0]
    my = sorted(p[1] for p in pts)[len(pts) // 2]
    return {"x": round(min(0.85, max(0.15, mx)), 3), "y": round(min(0.6, max(0.12, my)), 3), "source": "haar"}


def two_camera(frames, words_final, dur, tight=1.4, drift=0.0, min_seg=1.2, max_tight=3.2, max_wide=4.0) -> list[dict]:
    """Style F framing plan: wide 1.0 ↔ tight on EVERY cut point (kept-range joints ≥ min_seg apart); a segment longer
    than max_tight (tight) / max_wide (wide) gets an extra switch on a word onset ~2–2.6 s in. Optional drift."""
    cuts, o = [], 0.0
    for f0, f1 in frames[:-1]:
        o += (f1 - f0) / FPS
        cuts.append(round(o, 3))
    onsets = sorted({round(float(w["s"]), 3) for w in words_final})
    pts, last = [], 0.0
    for c in cuts:
        if c - last >= min_seg and dur - c >= min_seg:
            pts.append(c)
            last = c
    # fill long stretches with word-onset switches, alternating from wide at 0
    out, t, scale, i = [], 0.0, 1.0, 0
    bounds = pts + [dur]
    while t < dur - 1e-3:
        nxt = bounds[i] if i < len(bounds) else dur
        lim = max_tight if scale > 1.0 else max_wide
        on = "cut"
        if nxt - t > lim:
            cand = [x for x in onsets if t + 2.0 <= x <= t + 2.6 and dur - x >= min_seg]
            if cand:
                nxt, on = cand[0], "word"
        else:
            i += 1
        if dur - nxt < min_seg:
            nxt, on = dur, "end"
        seg = {"start": round(t, 3), "end": round(nxt, 3), "scale": scale, "on": on, "framing": "tight" if scale > 1.0 else "wide"}
        if drift and nxt - t >= 2.5:
            seg["drift"] = drift
        out.append(seg)
        t, scale = nxt, (tight if scale == 1.0 else 1.0)
        while i < len(bounds) and bounds[i] <= t + 1e-3:
            i += 1
    return out


# ----------------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True, help="work/<slug> directory")
    ap.add_argument("--max-silence", type=float, default=0.35, help="cut pauses longer than this (s)")
    ap.add_argument("--pad", type=float, default=0.12, help="keep this much air around speech at cuts (s)")
    ap.add_argument("--fillers", help="comma-separated filler words (default per brief.lang)")
    ap.add_argument("--no-retakes", action="store_true", help="disable repeated-sentence (retake) removal")
    ap.add_argument("--retake-threshold", type=float, default=0.78, help="similarity to treat as retake")
    ap.add_argument("--crop-x", type=float, default=0.5, help="horizontal crop centre 0..1 for wide footage")
    ap.add_argument("--xfade-ms", type=float, default=2 * 1024 / SR * 1000,
                    help="audio crossfade at cuts (default 2 AAC frames ≈ 42.7 ms)")
    ap.add_argument("--punch-zoom", type=float, default=1.12)
    ap.add_argument("--framing", choices=["auto", "punch", "two-cam"], default="auto",
                    help="punch = alternating 1.0/--punch-zoom every 3–5 s; two-cam = style F wide↔tight on every cut; "
                         "auto = two-cam for brief.style F, else punch")
    ap.add_argument("--tight", type=float, default=1.4, help="two-cam tight framing scale (ref 1.25–1.55)")
    ap.add_argument("--drift", type=float, default=0.0, help="two-cam: slow zoom inside segments ≥ 2.5 s (e.g. 0.03)")
    ap.add_argument("--anchor-x", type=float, default=0.5, help="framing anchor x (0..1) when no face is detected")
    ap.add_argument("--anchor-y", type=float, default=None, help="framing anchor y (0..1); default 0.38 (punch) / 0.30 (two-cam)")
    ap.add_argument("--force", action="store_true", help="redo even if outputs are up to date")
    ap.add_argument("--keep-tmp", action="store_true", help="keep edit/tmp/source.mp4")
    ap.add_argument("--dry-run", action="store_true", help="plan and write cuts.json only, no render")
    a = ap.parse_args()

    work = Path(a.work).resolve()
    brief_p = work / "brief.json"
    if not brief_p.is_file():
        sys.exit(f"missing {brief_p}")
    brief = json.loads(brief_p.read_text())
    footage = brief.get("footage") or []
    if not footage:
        sys.exit("brief.footage is empty — edit_head.py is only for footage modes")
    lang = brief.get("lang", "ru")
    takes_p = [(work / f) if not Path(f).is_absolute() else Path(f) for f in footage]
    for p in takes_p:
        if not p.is_file():
            sys.exit(f"footage not found: {p}")
    edit, audio_d = work / "edit", work / "audio"
    tmp = edit / "tmp"
    head, cuts_p = edit / "head.mp4", edit / "cuts.json"
    tr_p, tr_src_p = audio_d / "transcript.json", audio_d / "transcript.source.json"
    voice_p, voice_src_p = audio_d / "voice.wav", audio_d / "voice.source.wav"

    inputs = [brief_p, *takes_p] + [p for p in (tr_src_p if tr_src_p.exists() else tr_p,) if p.exists()]
    if not a.force and head.is_file() and cuts_p.is_file():
        newest = max(p.stat().st_mtime for p in inputs if p.exists() and p != tr_p)
        if head.stat().st_mtime >= newest:
            log("edit/head.mp4 is up to date — skipping (use --force to redo)")
            print(cuts_p.read_text()[:400])
            return
    tmp.mkdir(parents=True, exist_ok=True)

    takes = [probe(p) for p in takes_p]
    offsets, o = [], 0.0
    for t in takes:
        offsets.append(round(o, 3))
        o += t["duration"]
    log(f"{len(takes)} take(s), {o:.2f}s total — normalising to {W}x{H}@{FPS}")
    source = tmp / "source.mkv"
    normalise(takes, source, a.crop_x)
    src_dur = media_duration(source)

    # transcript (source timeline)
    if tr_src_p.is_file():
        tr = json.loads(tr_src_p.read_text())
    elif tr_p.is_file():
        tr = json.loads(tr_p.read_text())
        if tr.get("timeline") == "final":
            sys.exit("audio/transcript.json is already on the final timeline but transcript.source.json is missing")
        shutil.copy2(tr_p, tr_src_p)
    else:
        tr = None
        log("no audio/transcript.json — falling back to energy-based silence detection (no filler/retake cuts)")

    # audio source: cleaned voice if it matches the source length, else the footage audio
    audio_src = None
    for cand in (voice_src_p, audio_d / "voice_src.wav", voice_p):     # voice_src.wav: legacy name
        if cand.is_file() and abs(media_duration(cand) - src_dur) < 0.5:
            audio_src = cand
            break
    if audio_src is None:
        log("WARNING: using RAW footage audio — the voice is NOT cleaned. Run "
            "providers/cleanup.py <take> --out audio/voice.source.wav first.")
        audio_src = source
    elif audio_src == voice_p:
        shutil.copy2(voice_p, voice_src_p)
        audio_src = voice_src_p
    audio = read_audio(audio_src)

    fillers = [f.strip() for f in a.fillers.split(",")] if a.fillers else DEFAULT_FILLERS.get(lang, DEFAULT_FILLERS["ru"])
    if tr and tr.get("words"):
        words = [{**w, "s": float(w["s"]), "e": float(w["e"])} for w in tr["words"]]
        ranges, removed, keep = plan_cuts(words, src_dur, fillers, not a.no_retakes,
                                          a.max_silence, a.pad, a.retake_threshold)
    else:
        words, keep, removed = [], [], []
        ranges = [[max(0, s - a.pad), min(src_dur, e + a.pad)] for s, e in energy_speech(audio, a.max_silence)]
    frames = snap(ranges, src_dur)
    if not frames:
        sys.exit("nothing left after cutting — check transcript/footage")
    kept = sum(f1 - f0 for f0, f1 in frames) / FPS
    # silence ranges for the report
    prev = 0.0
    for f0, f1 in frames:
        if f0 / FPS - prev > 0.04:
            removed.append({"type": "silence/cut", "s": round(prev, 3), "e": round(f0 / FPS, 3)})
        prev = f1 / FPS
    if src_dur - prev > 0.04:
        removed.append({"type": "silence/cut", "s": round(prev, 3), "e": round(src_dur, 3)})

    segments, o = [], 0.0
    for f0, f1 in frames:
        d = (f1 - f0) / FPS
        segments.append({"src_s": round(f0 / FPS, 3), "src_e": round(f1 / FPS, 3),
                         "out_s": round(o, 3), "out_e": round(o + d, 3), "f0": f0, "f1": f1})
        o += d
    tr_final = remap_transcript(tr, words, keep, frames, src_dur - kept) if tr else None
    style = str(brief.get("style") or "").lower()
    framing = a.framing if a.framing != "auto" else ("two-cam" if style == "f" else "punch")
    wf = tr_final["words"] if tr_final else []
    if framing == "two-cam":
        pis = two_camera(frames, wf, kept, tight=a.tight, drift=a.drift)
        anchor = {"x": a.anchor_x, "y": a.anchor_y if a.anchor_y is not None else 0.30, "source": "config"}
        fa = face_anchor(source)
        if fa and a.anchor_y is None:
            anchor = fa
        log(f"two-camera framing: {len(pis)} segments, tight {a.tight}, anchor {anchor}")
    else:
        pis = punch_ins(frames, wf, kept, zoom=a.punch_zoom)
        anchor = {"x": a.anchor_x, "y": a.anchor_y if a.anchor_y is not None else 0.38}
    cuts = {"fps": FPS, "width": W, "height": H, "duration": round(kept, 3), "source_duration": round(src_dur, 3),
            "takes": [{"path": str(Path(footage[i])), "offset": offsets[i], "duration": round(t["duration"], 3),
                       "rotation": t["rotation"], "size": f"{t['width']}x{t['height']}", "fps": round(t["fps"], 3)}
                      for i, t in enumerate(takes)],
            "audio_source": str(audio_src.relative_to(work)) if audio_src.is_relative_to(work) else str(audio_src),
            "segments": segments, "removed": sorted(removed, key=lambda r: r["s"]),
            "punch_ins": pis, "punch_anchor": anchor, "framing": framing,
            "params": {"max_silence": a.max_silence, "pad": a.pad, "fillers": fillers,
                       "retakes": not a.no_retakes, "xfade_ms": round(a.xfade_ms, 2), "crop_x": a.crop_x,
                       "framing": framing, "tight": a.tight, "drift": a.drift}}
    edit.mkdir(exist_ok=True)
    if a.dry_run:
        cuts_p.write_text(json.dumps(cuts, ensure_ascii=False, indent=1))
        log(f"dry run: {len(frames)} segments, {src_dur:.2f}s → {kept:.2f}s")
        return

    # video: frame-accurate select on the CFR source
    expr = "+".join(f"between(n,{f0},{f1 - 1})" for f0, f1 in frames)
    (tmp / "select.txt").write_text(f"select='{expr}',setpts=N/{FPS}/TB")
    cut_audio = splice_audio(audio, frames, a.xfade_ms / 1000)
    wav_tmp = tmp / "cut.wav"
    write_wav(wav_tmp, cut_audio)
    run(["ffmpeg", "-y", "-v", "error", "-i", str(source), "-i", str(wav_tmp),
         "-filter_script:v", str(tmp / "select.txt"), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-frames:v", str(sum(f1 - f0 for f0, f1 in frames)),
         "-movflags", "+faststart", str(head)])
    shutil.copy2(wav_tmp, voice_p)  # final-timeline voice for mix.py
    if tr_final:
        tr_p.write_text(json.dumps(tr_final, ensure_ascii=False, indent=1))
    cuts_p.write_text(json.dumps(cuts, ensure_ascii=False, indent=1))
    if not a.keep_tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    hd = media_duration(head)
    log(f"{len(frames)} segments · {src_dur:.2f}s → {kept:.2f}s (head.mp4 {hd:.3f}s) · "
        f"{sum(1 for r in removed if r['type'] == 'filler')} fillers, "
        f"{sum(1 for r in removed if r['type'] == 'retake')} retake words removed")
    print(json.dumps({"ok": True, "head": str(head), "duration": round(kept, 3), "segments": len(frames),
                      "punch_ins": len(pis)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
