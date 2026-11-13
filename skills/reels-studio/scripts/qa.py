#!/usr/bin/env python3
"""reels-studio automatic QA (step 5): renders/final.mp4 → qa/report.json + qa/sheet.jpg + qa/frames/.

  qa.py --work work/<slug> [--video renders/final.mp4] [--lufs -14] [--lufs-tol 1] [--tp-max -1]
        [--dur-tol 0.1] [--reveal-early 0.10] [--reveal-late 0.30] [--freeze-max 3.0]

Checks (severity "fail" makes the report ok=false and exits 1; "warn" is for the QA agent to judge):
  duration      render duration = plan/scenes.json duration ± --dur-tol                       fail
  resolution    1080×1920 (and ~30 fps)                                                         fail
  loudness      integrated −14 ± 1 LUFS, true peak ≤ −1 dBTP (ffmpeg loudnorm analysis)         fail
  black         blackdetect segments ≥ 0.25 s, except scenes marked intentional                  fail
  freeze        freezedetect segments > --freeze-max s outside the last scene / intentional      warn
  tiling        scenes tile the timeline with no gaps/overlaps                                   fail
  reveal_sync   headline.words[].t, kicker.at, caption.at vs transcript word onsets
                (allowed window: −reveal-early … +reveal-late s around the spoken word)          warn
  centering     per centred-layout motion scene, final frame: content bbox (pixels != background colour)
                centre x within +-centre-tol (24) px of 540                                       warn
  caption_coverage  composition/captions.json: >= 98 % of spoken words in caption ranges captioned fail
  caption_sync  planned word appear - onset within -cap-early...+cap-late (-0.10...+0.05 s) and the
                rendered reveal (largest rise of caption-white pixels per word) in the same window fail
  caption_centering caption line bbox centre within +-centre-tol px                                warn
  audio_*       scripts/qa_audio.py checks(work, video) merged when importable (warn if missing)
Also: one snapshot per scene midpoint (qa/frames/<id>.jpg) and a labelled contact sheet (qa/sheet.jpg)
for the QA agent to eyeball, plus the style's pitfalls checklist from references/style-guide.md.
A scene is "intentional" for black/freeze when it has `"qa": {"allow_black": true}` /
`{"allow_freeze": true}` or its notes mention hold/freeze/black.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent


def log(msg: str) -> None:
    print(f"[qa] {msg}", file=sys.stderr)


def sh(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def norm(w: str) -> str:
    return re.sub(r"[^\w]+", "", w.lower()).replace("ё", "е")


def probe(path: Path) -> dict:
    p = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if p.returncode != 0:
        raise SystemExit(f"ffprobe failed on {path}: {p.stderr[-400:]}")
    info = json.loads(p.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    n, d = (v.get("avg_frame_rate") or "0/1").split("/")
    return {"duration": float(info["format"].get("duration", 0)), "width": v.get("width"), "height": v.get("height"),
            "fps": float(n) / float(d) if float(d) else 0.0,
            "has_audio": any(s["codec_type"] == "audio" for s in info["streams"])}


def loudness(path: Path) -> dict:
    p = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
            "-af", "loudnorm=I=-14:TP=-1:LRA=7:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    if not m:
        return {}
    j = json.loads(m.group(0))
    return {"I": float(j["input_i"]), "TP": float(j["input_tp"]), "LRA": float(j["input_lra"])}


def black_freeze(path: Path, freeze_min: float) -> tuple[list, list]:
    p = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-an", "-vf",
            f"scale=270:-2,blackdetect=d=0.25:pic_th=0.97:pix_th=0.06,freezedetect=n=0.002:d={freeze_min}",
            "-f", "null", "-"])
    blacks = [{"s": float(a), "e": float(b)} for a, b in
              re.findall(r"black_start:([\d.]+)\s+black_end:([\d.]+)", p.stderr)]
    fs = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", p.stderr)]
    fe = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", p.stderr)]
    dur = probe(path)["duration"]
    freezes = [{"s": s, "e": fe[i] if i < len(fe) else dur} for i, s in enumerate(fs)]
    return blacks, freezes


def intentional(scene: dict, what: str) -> bool:
    q = scene.get("qa") or {}
    if q.get(f"allow_{what}"):
        return True
    notes = (scene.get("notes") or "").lower()
    keys = {"black": ("black", "чёрн", "черн"), "freeze": ("hold", "freeze", "static", "статич")}[what]
    return any(k in notes for k in keys)


def scenes_at(scenes, s, e):
    return [sc for sc in scenes if float(sc["start"]) < e and float(sc["end"]) > s]


def reveal_checks(scenes, words, early, late) -> list[dict]:
    """Compare planned reveal times with transcript word onsets (global, final timeline)."""
    issues = []
    nw = [(norm(w["w"]), float(w["s"])) for w in words]

    def nearest(token, t):
        cands = [s for w, s in nw if w == token and abs(s - t) < 3.0]
        return min(cands, key=lambda s: abs(s - t)) if cands else None

    for sc in scenes:
        st, en = float(sc["start"]), float(sc["end"])
        hl = sc.get("headline") or {}
        for w in hl.get("words") or []:
            t = float(w["t"])
            if not (st - 0.05 <= t <= en + 0.05):
                issues.append({"scene": sc["id"], "what": f"headline word {w['w']!r}", "t": t,
                               "problem": f"outside scene range {st:.2f}–{en:.2f}"})
                continue
            ref = nearest(norm(w["w"]), t)
            if ref is None:
                continue  # paraphrased keyword (style A) — no literal match to check against
            d = t - ref
            if not (-early <= d <= late):
                issues.append({"scene": sc["id"], "what": f"headline word {w['w']!r}", "t": t, "spoken": ref,
                               "delta": round(d, 3), "problem": "reveal not synced to speech"})
        for key in ("kicker", "caption"):
            obj = sc.get(key) or {}
            if obj.get("at") is None or not obj.get("text"):
                continue
            t = float(obj["at"])
            first = next((norm(x) for x in str(obj["text"]).split() if norm(x)), "")
            if not (st - 0.05 <= t <= en + 0.05):
                issues.append({"scene": sc["id"], "what": key, "t": t, "problem": "outside scene range"})
                continue
            ref = nearest(first, t) if first else None
            if ref is not None and not (-early - 0.25 <= t - ref <= late):
                issues.append({"scene": sc["id"], "what": key, "t": t, "spoken": ref, "delta": round(t - ref, 3),
                               "problem": "reveal not synced to speech"})
    return issues


def pitfalls(style: str) -> dict:
    """Shared truths + the style's pitfalls list from references/style-guide.md."""
    p = SKILL / "references" / "style-guide.md"
    if not p.is_file():
        return {}
    text = p.read_text()
    shared = re.search(r"## Shared truths.*?\n(.*?)\n---", text, re.S)
    shared_items = [re.sub(r"^\d+\.\s*", "", ln).strip() for ln in (shared.group(1) if shared else "").splitlines()
                    if re.match(r"^\d+\.", ln.strip())]
    sec = re.search(rf"## System {style.upper()} .*?(?=\n## |\Z)", text, re.S)
    pit = re.search(r"\*\*Pitfalls:\*\*\s*(.*)", sec.group(0)) if sec else None
    items = [x.strip().rstrip(".") for x in pit.group(1).split(",")] if pit else []
    audio = re.search(r"\*\*Audio:\*\*\s*(.*)", sec.group(0)) if sec else None
    return {"shared_truths": shared_items, "style_pitfalls": items,
            "audio_policy": audio.group(1).strip() if audio else None}


def snapshots(video: Path, scenes, out_dir: Path) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for sc in scenes:
        t = (float(sc["start"]) + float(sc["end"])) / 2
        f = out_dir / f"{sc['id']}.jpg"
        p = sh(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                "-vf", "scale=540:-2", "-q:v", "3", str(f)])
        if p.returncode == 0 and f.is_file():
            frames.append({"scene": sc["id"], "t": round(t, 3), "file": str(f.relative_to(out_dir.parent.parent))})
    return frames


def contact_sheet(frames, work: Path, out: Path, scenes) -> str | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        log("Pillow missing — using ffmpeg tile for the contact sheet")
        if not frames:
            return None
        lst = work / "qa" / "frames" / "_list.txt"
        lst.write_text("".join(f"file '{(work / f['file']).as_posix()}'\n" for f in frames))
        cols = min(5, len(frames))
        rows = (len(frames) + cols - 1) // cols
        p = sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf",
                f"scale=270:-2,tile={cols}x{rows}:padding=6:color=0x202020", "-frames:v", "1", str(out)])
        lst.unlink(missing_ok=True)
        return str(out) if p.returncode == 0 else None
    if not frames:
        return None
    tw, th = 270, 480
    cols = min(5, len(frames))
    rows = (len(frames) + cols - 1) // cols
    lab = 34
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + lab + 8) + 8), (24, 24, 26))
    d = ImageDraw.Draw(sheet)
    font = None
    for fp in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/Helvetica.ttc",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            font = ImageFont.truetype(fp, 16)
            break
        except Exception:
            continue
    font = font or ImageFont.load_default()
    byid = {s["id"]: s for s in scenes}
    for i, fr in enumerate(frames):
        im = Image.open(work / fr["file"]).convert("RGB").resize((tw, th))
        x, y = 8 + (i % cols) * (tw + 8), 8 + (i // cols) * (th + lab + 8)
        sheet.paste(im, (x, y))
        sc = byid.get(fr["scene"], {})
        txt = (sc.get("headline") or {}).get("text") or sc.get("kind", "")
        d.text((x, y + th + 3), f"{fr['scene']} · {fr['t']:.2f}s · {sc.get('kind', '')}", fill=(230, 230, 230), font=font)
        d.text((x, y + th + 19), str(txt)[:30], fill=(150, 150, 155), font=font)
    sheet.save(out, quality=88)
    return str(out)


def variety_issues(scenes: list[dict]) -> list[str]:
    """Plan-level anti-template rules from references/layouts.md §3."""
    issues, motion = [], [s for s in scenes if s.get("kind", "motion") != "head"]
    layouts = [s.get("layout") for s in motion]
    for s, lay in zip(motion, layouts):
        if not lay:
            issues.append(f"{s['id']}: no layout")
    for a, b in zip(motion, motion[1:]):
        if a.get("layout") and a.get("layout") == b.get("layout"):
            issues.append(f"{a['id']}→{b['id']}: same layout '{a['layout']}' twice in a row")
    if len(motion) >= 4:
        for lay in set(filter(None, layouts)):
            share = layouts.count(lay) / len(motion)
            if share > 0.30 + 1e-9:
                issues.append(f"layout '{lay}' used in {share:.0%} of scenes (max 30%)")
        if len(set(filter(None, layouts))) < min(4, len(motion)):
            issues.append(f"only {len(set(filter(None, layouts)))} distinct layouts (need ≥ {min(4, len(motion))})")
    types = [[c.get("type") for c in s.get("components", [])] for s in motion]
    for i, ts in enumerate(types):
        for t in ts:
            if t and any(t in prev for prev in types[max(0, i - 3):i]):
                issues.append(f"{motion[i]['id']}: component '{t}' reused within 3 scenes")
    return issues


# ---------------------------------------------------------------- geometry + captions (visual pipeline checks)
CENTRED_LAYOUTS = {"stack", "number", "statement", "list", "hero", "insert-hero", "insert-number", "cta"}


def grab(video: Path, t: float, crop: str | None = None, scale: str = "540:960"):
    """One frame as an RGB numpy array (optionally cropped first: 'w:h:x:y' in source px)."""
    import numpy as np
    vf = (f"crop={crop}," if crop else "") + f"scale={scale}"
    w, h = (int(x) for x in scale.split(":"))
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", str(video), "-frames:v", "1",
                        "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    if p.returncode != 0 or len(p.stdout) < w * h * 3:
        return None
    return np.frombuffer(p.stdout[: w * h * 3], dtype=np.uint8).reshape(h, w, 3).astype(int)


def _box(a, r, ax):
    import numpy as np
    c = np.cumsum(np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(a.ndim)], mode="edge"), axis=ax)
    n = a.shape[ax]
    return (np.take(c, range(2 * r + 1, 2 * r + 1 + n), axis=ax) - np.take(c, range(0, n), axis=ax)) / (2 * r + 1)


def content_bbox_x(img) -> tuple[int, int] | None:
    """Horizontal extent (1080-px units) of CONTENT: pixels that differ from the local background (41-px box blur
    high-pass, so gradients / glows / light rays don't count), eroded 3×2 so dot grids and hairlines drop out."""
    import numpy as np
    h, w, _ = img.shape
    f = img.astype(float)
    m = np.abs(f - _box(_box(f, 20, 1), 20, 0)).max(2) > 18
    m = m & np.roll(m, 1, 1) & np.roll(m, -1, 1) & np.roll(m, 1, 0)
    m[: int(h * 0.12)] = False           # reels top UI / chrome breadcrumbs
    m[int(h * 0.82):] = False            # reels bottom UI
    m[:, :3] = False
    m[:, -3:] = False
    cols = np.where(m.sum(0) >= 2)[0]
    if len(cols) < 2:
        return None
    k = 1080 / w
    return int(cols[0] * k), int((cols[-1] + 1) * k)


def centering_checks(video: Path, scenes: list[dict], bounds: list[dict], tol: float) -> list[dict]:
    out = []
    starts = {b["from"]: b["start"] for b in bounds if b.get("mode") in ("xfade", "continuous")}
    for sc in scenes:
        if sc.get("kind", "motion") != "motion" or sc.get("layout") not in CENTRED_LAYOUTS:
            continue
        t = min(float(sc["end"]) - 0.12, starts.get(sc["id"], 1e9) - 0.05)
        img = grab(video, t)
        if img is None:
            continue
        bb = content_bbox_x(img)
        if not bb:
            continue
        cx = (bb[0] + bb[1]) / 2
        out.append({"scene": sc["id"], "layout": sc.get("layout"), "t": round(t, 3), "bbox_x": bb,
                    "centre_x": round(cx, 1), "delta": round(cx - 540, 1), "ok": abs(cx - 540) <= tol})
    return out


def caption_band_series(video: Path, cap: dict, fps: float):
    """Per-frame count of caption-white pixels (pure white/grey text over the scrim) inside the caption band."""
    import numpy as np
    y = int(cap["y"])
    w, h = 480, 70                         # band 960×140 at x 60, half scale
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf",
                        f"crop=960:140:60:{y - 70},scale={w}:{h},fps={fps}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    if p.returncode != 0:
        return None, None
    a = np.frombuffer(p.stdout, dtype=np.uint8)
    n = len(a) // (w * h * 3)
    a = a[: n * w * h * 3].reshape(n, h, w, 3).astype(int)
    lum = a.mean(3)
    sat = a.max(3) - a.min(3)
    thr = 195 if cap.get("style") == "e" else 238
    mask = (lum > thr) & (sat < 14)
    return mask.sum((1, 2)), mask


def caption_checks(video: Path, cap: dict, fps: float, early: float, late: float, tol: float) -> dict:
    """Coverage + planned sync (composition/captions.json) + rendered sync (rise of caption-white pixels per word)."""
    import numpy as np
    words = [w for p in cap.get("phrases", []) for w in p["words"]]
    planned = [round(w["appear"] - w["s"], 3) for w in words]
    res = {"coverage": cap.get("coverage"), "words": len(words),
           "planned_delta": {"min": min(planned, default=None), "max": max(planned, default=None)},
           "planned_out_of_tol": len([d for d in planned if not (-early <= d <= late)])}
    series, mask = caption_band_series(video, cap, fps)
    if series is None or not len(series):
        res["rendered"] = None
        return res
    # rendered appearance events: runs of frames where the caption-white pixel count rises; an event's time is its
    # last rising frame (= first frame at the new level; frame f shows timeline time f/fps). Each word is matched to the
    # nearest unused event within ±0.30 s of its onset.
    dif = np.diff(series.astype(int), prepend=int(series[0]))
    events, k = [], 1
    while k < len(dif):
        if dif[k] >= 6:
            j = k
            while j + 1 < len(dif) and dif[j + 1] >= 3:
                j += 1
            events.append(j / fps)
            k = j + 1
        else:
            k += 1
    used, deltas, misses = set(), [], 0
    for w in words:
        cands = [(abs(e - (w["s"] - 0.03)), i, e) for i, e in enumerate(events) if i not in used and abs(e - w["s"]) <= 0.30]
        if not cands:
            misses += 1
            continue
        _, i, e = min(cands)
        used.add(i)
        deltas.append(round(e - w["s"], 3))
    if deltas:
        d = np.array(deltas)
        res["rendered"] = {"measured": len(deltas), "missed": misses, "median": round(float(np.median(d)), 3),
                           "min": round(float(d.min()), 3), "max": round(float(d.max()), 3),
                           "late_gt_tol": int((d > late + 1 / fps).sum()), "early_lt_tol": int((d < -early - 1 / fps).sum())}
    cents = []
    for p in cap.get("phrases", [])[:80]:
        f = int(((p["words"][-1]["appear"] + p["hide"]) / 2) * fps)
        if 0 <= f < len(mask):
            cols = np.where(mask[f].sum(0) >= 1)[0]
            if len(cols) > 3:
                cents.append(round(60 + (cols[0] + cols[-1] + 1) - 540, 1))   # half-scale cols → 1080-px units
    if cents:
        res["centre_delta"] = {"max_abs": max(abs(c) for c in cents), "n": len(cents),
                               "off": sum(1 for c in cents if abs(c) > tol)}
    return res


def audio_checks(work: Path, video: Path):
    """scripts/qa_audio.py (owned by the audio pipeline) — merged into the report when importable."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import qa_audio  # noqa
    except Exception as e:
        return None, f"qa_audio not importable ({e.__class__.__name__}: {e})"
    try:
        return list(qa_audio.checks(work, video)), None
    except Exception as e:
        return None, f"qa_audio.checks failed: {e}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--video", default=None)
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--lufs-tol", type=float, default=1.0)
    ap.add_argument("--tp-max", type=float, default=-1.0)
    ap.add_argument("--dur-tol", type=float, default=0.1)
    ap.add_argument("--reveal-early", type=float, default=0.10)
    ap.add_argument("--reveal-late", type=float, default=0.30)
    ap.add_argument("--freeze-max", type=float, default=3.0)
    ap.add_argument("--centre-tol", type=float, default=24.0, help="max |content centre x - 540| px for centred layouts")
    ap.add_argument("--cap-early", type=float, default=0.10, help="caption word may appear this early (s)")
    ap.add_argument("--cap-late", type=float, default=0.05, help="caption word may appear this late (s)")
    ap.add_argument("--plan-only", action="store_true", help="only check plan/scenes.json variety rules (before fan-out)")
    a = ap.parse_args()

    work = Path(a.work).resolve()
    if a.plan_only:
        plan = json.loads((work / "plan" / "scenes.json").read_text())
        issues = variety_issues(sorted(plan.get("scenes", []), key=lambda s: float(s["start"])))
        for i in issues:
            log(f"FAIL variety: {i}")
        print(json.dumps({"ok": not issues, "variety": issues}, ensure_ascii=False))
        sys.exit(0 if not issues else 1)
    video = Path(a.video).resolve() if a.video else work / "renders" / "final.mp4"
    if not video.is_file():
        sys.exit(f"missing {video} — run render.py first")
    plan = json.loads((work / "plan" / "scenes.json").read_text())
    scenes = sorted(plan.get("scenes", []), key=lambda s: float(s["start"]))
    style = str(plan.get("style", "A"))
    tr_p = work / "audio" / "transcript.json"
    words = json.loads(tr_p.read_text()).get("words", []) if tr_p.is_file() else []
    qa = work / "qa"
    qa.mkdir(exist_ok=True)
    checks = []

    def add(name, ok, severity, value=None, expected=None, detail=None):
        checks.append({"name": name, "ok": bool(ok), "severity": "info" if ok else severity,
                       "value": value, "expected": expected, "detail": detail})

    info = probe(video)
    exp_dur = float(plan.get("duration") or (scenes[-1]["end"] if scenes else 0))
    add("duration", abs(info["duration"] - exp_dur) <= a.dur_tol, "fail", round(info["duration"], 3),
        f"{exp_dur:.3f} ± {a.dur_tol}")
    add("resolution", (info["width"], info["height"]) == (int(plan.get("width", 1080)), int(plan.get("height", 1920)))
        and abs(info["fps"] - float(plan.get("fps", 30))) < 0.5, "fail",
        f"{info['width']}x{info['height']}@{info['fps']:.2f}", f"{plan.get('width', 1080)}x{plan.get('height', 1920)}@{plan.get('fps', 30)}")

    if info["has_audio"]:
        ld = loudness(video)
        if ld:
            add("loudness_integrated", abs(ld["I"] - a.lufs) <= a.lufs_tol, "fail", ld["I"], f"{a.lufs} ± {a.lufs_tol} LUFS")
            add("true_peak", ld["TP"] <= a.tp_max + 0.05, "fail", ld["TP"], f"≤ {a.tp_max} dBTP")
            add("loudness_range", True, "info", ld["LRA"], "LU (A ≈ 2, B ≈ 4–7)")
        else:
            add("loudness_integrated", False, "fail", None, None, "loudnorm analysis failed")
    else:
        add("audio_present", False, "fail", None, "audio stream", "render has no audio track")

    t = 0.0
    gaps = []
    for sc in scenes:
        if abs(float(sc["start"]) - t) > 0.02:
            gaps.append(f"{sc['id']}: starts {sc['start']} vs prev end {t:.3f}")
        t = float(sc["end"])
    add("tiling", not gaps, "fail", gaps or "ok", "scenes tile with no gaps")

    v_issues = variety_issues(scenes)
    add("variety", not v_issues, "warn", v_issues or "ok", "layouts.md §3 variety rules")

    blacks, freezes = black_freeze(video, a.freeze_max)
    bad_black = [b for b in blacks if not all(intentional(s, "black") for s in scenes_at(scenes, b["s"], b["e"]))
                 or not scenes_at(scenes, b["s"], b["e"])]
    add("black_frames", not bad_black, "fail", bad_black or blacks, "no unintended black ≥ 0.25 s")
    last_start = float(scenes[-1]["start"]) if scenes else 1e9
    bad_freeze = [f for f in freezes if f["s"] < last_start - 0.05 and
                  not all(intentional(s, "freeze") for s in scenes_at(scenes, f["s"], f["e"]))]
    add("frozen_segments", not bad_freeze, "warn", bad_freeze or freezes, f"no static picture > {a.freeze_max}s "
        "(except final hold)")

    if words:
        issues = reveal_checks(scenes, words, a.reveal_early, a.reveal_late)
        add("reveal_sync", not issues, "warn", issues[:40], f"reveal within −{a.reveal_early}…+{a.reveal_late}s of the spoken word",
            f"{len(issues)} issue(s)" if issues else None)
    else:
        add("reveal_sync", False, "warn", None, None, "audio/transcript.json missing — not checked")

    # ---- visual pipeline: centring of centred layouts, caption coverage + sync
    asm_p = work / "composition" / "assemble.json"
    bounds = json.loads(asm_p.read_text()).get("transitions", []) if asm_p.is_file() else []
    try:
        cen = centering_checks(video, scenes, bounds, a.centre_tol)
        off = [c for c in cen if not c["ok"]]
        add("centering", not off, "warn", off or [f"{c['scene']} {c['delta']:+.0f}px" for c in cen],
            f"|content centre x - 540| <= {a.centre_tol:.0f} px (layouts {', '.join(sorted(CENTRED_LAYOUTS))})")
    except ImportError:
        add("centering", False, "warn", None, None, "numpy missing - not checked")
    cap_p = work / "composition" / "captions.json"
    if cap_p.is_file():
        cap = json.loads(cap_p.read_text())
        cr = caption_checks(video, cap, float(plan.get("fps", 30)), a.cap_early, a.cap_late, a.centre_tol)
        cov = (cr.get("coverage") or {}).get("pct_in_ranges")
        add("caption_coverage", cov is not None and cov >= 98, "fail", cov, ">= 98 % of spoken words in caption ranges",
            cr.get("coverage"))
        rend = cr.get("rendered") or {}
        bad = rend.get("late_gt_tol", 0) + rend.get("early_lt_tol", 0)
        sync_ok = cr["planned_out_of_tol"] == 0 and bad <= max(1, int(0.02 * cr["words"]))
        add("caption_sync", sync_ok, "fail", {"planned": cr["planned_delta"], "rendered": rend or None},
            f"word appears {-a.cap_early:+.2f}...{a.cap_late:+.2f} s around its onset")
        if cr.get("centre_delta"):
            add("caption_centering", cr["centre_delta"]["off"] == 0, "warn", cr["centre_delta"],
                f"caption line centre within +-{a.centre_tol:.0f} px")
    else:
        brief = json.loads((work / "brief.json").read_text()) if (work / "brief.json").is_file() else {}
        needs = brief.get("mode") in ("hook_cta", "head_overlay") or style.lower() == "d" or any(
            s.get("kind") in ("head", "head_overlay") for s in scenes)
        if needs and str(brief.get("captions", "auto")).lower() != "off":
            add("caption_coverage", False, "fail", None, "caption track for talking-head modes",
                "composition/captions.json missing - re-run assemble.py (needs audio/transcript.json)")
    # ---- audio QA (scripts/qa_audio.py, audio pipeline) merged when available
    ac, why = audio_checks(work, video)
    if ac is None:
        log(f"WARN audio QA skipped: {why}")
        add("audio_qa_module", False, "warn", None, "scripts/qa_audio.py", why)
    else:
        for c in ac:
            ok = bool(c.get("ok"))
            checks.append({"name": c.get("name", "audio"), "ok": ok, "severity": "info" if ok else c.get("severity", "warn"),
                           "value": c.get("value"), "expected": c.get("expected"), "detail": c.get("detail")})

    frames = snapshots(video, scenes, qa / "frames")
    sheet = contact_sheet(frames, work, qa / "sheet.jpg", scenes)
    fails = [c for c in checks if not c["ok"] and c["severity"] == "fail"]
    report = {"ok": not fails, "video": str(video), "probe": info, "checks": checks,
              "failed": [c["name"] for c in fails],
              "warnings": [c["name"] for c in checks if not c["ok"] and c["severity"] == "warn"],
              "frames": frames, "sheet": sheet,
              "manual_review": {"style": style.upper(), **pitfalls(style),
                                "instructions": "Open qa/sheet.jpg and each qa/frames/<id>.jpg; tick every pitfall; "
                                                "see references/qa-checklist.md."}}
    (qa / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    for c in checks:
        mark = "OK  " if c["ok"] else ("FAIL" if c["severity"] == "fail" else "WARN")
        log(f"{mark} {c['name']}: {c['value'] if not isinstance(c['value'], list) else str(c['value'])[:120]}"
            f"{'  (expected ' + str(c['expected']) + ')' if c['expected'] else ''}")
    print(json.dumps({"ok": report["ok"], "failed": report["failed"], "warnings": report["warnings"],
                      "report": str(qa / "report.json"), "sheet": sheet}, ensure_ascii=False))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
