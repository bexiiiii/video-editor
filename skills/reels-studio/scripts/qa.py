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
    a = ap.parse_args()

    work = Path(a.work).resolve()
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
    (qa / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    for c in checks:
        mark = "OK  " if c["ok"] else ("FAIL" if c["severity"] == "fail" else "WARN")
        log(f"{mark} {c['name']}: {c['value'] if not isinstance(c['value'], list) else str(c['value'])[:120]}"
            f"{'  (expected ' + str(c['expected']) + ')' if c['expected'] else ''}")
    print(json.dumps({"ok": report["ok"], "failed": report["failed"], "warnings": report["warnings"],
                      "report": str(qa / "report.json"), "sheet": sheet}, ensure_ascii=False))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
