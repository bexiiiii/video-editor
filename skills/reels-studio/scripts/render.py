#!/usr/bin/env python3
"""reels-studio renderer (step 5): composition/ → renders/final.mp4 with a disk guard.

  render.py --work work/<slug> [--quality draft|looks|delivery] [--min-start-mb 1000] [--abort-mb 400]
            [--out renders/final.mp4] [--workers auto] [--timeout 3600]

- Refuses to start when free disk on the work volume is below --min-start-mb.
- Warms the browser first (`npx hyperframes browser ensure`).
- Runs `npx -y hyperframes@0.8.154 render` in its own process group with the extracted-frame cache
  disabled (`--frames-cache-dir off`, saves GBs on small disks); a watchdog polls free space every
  second and kills the whole render (and deletes the partial output) if it drops below --abort-mb.
- Retries once when Chrome fails to launch ("Chrome cannot start" / "Failed to launch the browser").
- Prints duration / size / resolution of the result and writes renders/render.json; log in renders/render.log.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assemble import HF, find_npx, node_env  # noqa: E402

CHROME_ERRORS = ("chrome cannot start", "failed to launch the browser", "chrome failed to start")


def log(msg: str) -> None:
    print(f"[render] {msg}", file=sys.stderr, flush=True)


def free_mb(path: Path) -> float:
    return shutil.disk_usage(path).free / 1e6


def kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        time.sleep(2)
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, AttributeError):
        try:
            proc.kill()
        except Exception:
            pass


def run_render(cmd, cwd, env, logf: Path, watch: Path, abort_mb: float, timeout: float):
    """Run cmd in its own session with the disk watchdog. Returns (exit, output, reason)."""
    with open(logf, "a") as lf:
        lf.write(f"\n$ {' '.join(cmd)}\n")
        lf.flush()
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=lf, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, start_new_session=True)
        reason = {"v": None}

        def watchdog():
            t0 = time.time()
            while proc.poll() is None:
                fm = free_mb(watch)
                if fm < abort_mb:
                    reason["v"] = f"free disk {fm:.0f} MB < {abort_mb:.0f} MB"
                    kill_group(proc)
                    return
                if time.time() - t0 > timeout:
                    reason["v"] = f"timeout after {timeout:.0f}s"
                    kill_group(proc)
                    return
                time.sleep(1)

        th = threading.Thread(target=watchdog, daemon=True)
        th.start()
        try:
            code = proc.wait()
        except KeyboardInterrupt:
            kill_group(proc)
            raise
        th.join(timeout=5)
    out = logf.read_text(errors="ignore").split(f"$ {' '.join(cmd)}\n")[-1]
    return code, out, reason["v"]


def probe(path: Path) -> dict:
    p = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams",
                        str(path)], capture_output=True, text=True)
    if p.returncode != 0:
        return {}
    info = json.loads(p.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    return {"duration": round(float(info["format"].get("duration", 0)), 3),
            "size_mb": round(int(info["format"].get("size", 0)) / 1e6, 2),
            "width": v.get("width"), "height": v.get("height"), "fps": v.get("avg_frame_rate"),
            "audio": any(s["codec_type"] == "audio" for s in info["streams"])}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--quality", default="looks", choices=["draft", "looks", "delivery", "standard", "high"])
    ap.add_argument("--out", default=None, help="output path (default work/<slug>/renders/final.mp4)")
    ap.add_argument("--min-start-mb", type=float, default=1000)
    ap.add_argument("--abort-mb", type=float, default=400)
    ap.add_argument("--workers", default=None, help="hyperframes --workers (default auto)")
    ap.add_argument("--timeout", type=float, default=3600)
    a = ap.parse_args()

    work = Path(a.work).resolve()
    comp = work / "composition"
    if not (comp / "index.html").is_file():
        sys.exit("composition/index.html missing — run assemble.py first")
    out = Path(a.out).resolve() if a.out else work / "renders" / "final.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    logf = out.parent / "render.log"
    logf.write_text("")
    fm = free_mb(work)
    if fm < a.min_start_mb:
        sys.exit(f"render.py: only {fm:.0f} MB free on the work volume (< {a.min_start_mb:.0f} MB) — free space first "
                 f"(`npx {HF} clean`, delete old renders)")
    npx = find_npx()
    env = node_env(npx)
    env.setdefault("HYPERFRAMES_EXTRACT_CACHE_DIR", "off")
    # we start the render in its own process group (so the watchdog can kill Chrome too); without this
    # flag the CLI treats the new group as "parent went away" and cancels itself with SIGTERM.
    env["HYPERFRAMES_RENDER_DETACHED"] = "1"

    log("ensuring headless Chrome …")
    p = subprocess.run([npx, "-y", HF, "browser", "ensure"], cwd=comp, env=env, capture_output=True, text=True)
    if p.returncode != 0:
        log("browser ensure failed: " + (p.stdout + p.stderr)[-600:])

    cmd = [npx, "-y", HF, "render", "--quality", a.quality, "--output", str(out), "--frames-cache-dir", "off"]
    if a.workers:
        cmd += ["--workers", str(a.workers)]
    t0 = time.time()
    for attempt in (1, 2):
        if out.exists():
            out.unlink()
        log(f"rendering (attempt {attempt}, free {free_mb(work):.0f} MB) → {out}")
        code, text, reason = run_render(cmd, comp, env, logf, work, a.abort_mb, a.timeout)
        if reason:
            if out.exists():
                out.unlink()
            sys.exit(f"render.py: aborted — {reason}. Log: {logf}")
        if code == 0 and out.is_file() and out.stat().st_size > 0:
            break
        low = text.lower()
        if attempt == 1 and any(e in low for e in CHROME_ERRORS):
            log("Chrome failed to start — re-ensuring browser and retrying once")
            # plain ensure (never --force: that purges the shared Chrome cache other renders may be using)
            subprocess.run([npx, "-y", HF, "browser", "ensure"], cwd=comp, env=env, capture_output=True)
            continue
        print(text[-3000:], file=sys.stderr)
        sys.exit(f"render.py: render failed (exit {code}). Log: {logf}")
    info = probe(out)
    info.update({"ok": True, "out": str(out), "seconds": round(time.time() - t0, 1), "quality": a.quality})
    summary = [ln for ln in text.splitlines() if ln.strip()][-6:]
    info["summary"] = summary
    (out.parent / "render.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    log(f"done: {info.get('duration')}s · {info.get('size_mb')} MB · {info.get('width')}x{info.get('height')} "
        f"· {info['seconds']}s wall")
    print(json.dumps({k: info.get(k) for k in ("ok", "out", "duration", "size_mb", "width", "height", "seconds")}))


if __name__ == "__main__":
    main()
