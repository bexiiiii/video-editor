#!/usr/bin/env python3
"""Automatic topic B-roll: one muted 1080×1920 H.264 30 fps clip per scene that asks for it.

The director marks scenes in plan/scenes.json:
    "broll": {"kind": "screen"|"stock"|"generated", "url": "https://…"?, "query": "…"?, "seconds": 6}
  screen    = a public web page the script names (kolesa.kz listing, kaspi.kz product, krisha.kz search, the
              client's own site) → smooth slow scroll recording of exactly that URL
  stock     = a generic action / place ("car dealership", "office team", "city traffic") → stock video
  generated = only via the ElevenLabs connector, run by the orchestrator after the client approves the credit
              spend (connector-elevenlabs.md) — this script never generates; it reports "needs_connector"

Chain per item (first success wins; references/broll.md):
  1. client material   input/<scene>_broll*.{mp4,mov,webm} or plan/materials.json item {scene, kind broll|
                       screen_recording, status received, path}
  2. screen capture    kind screen + url: https only, public host only (every redirect hop checked), the URL the
                       director/client gave — never a URL found in page content. Headless Chrome that HyperFrames
                       installed (`npx hyperframes browser path`) driven by providers/screen_capture.mjs (Node ≥ 22,
                       no npm deps): mobile viewport 432×768 @2.5 = 1080×1920, sine-eased scroll, trivial cookie
                       banner dismissed, phone numbers / e-mails blurred, no logins, no typing.
  3. stock video       Pexels (PEXELS_API_KEY) → Pixabay (PIXABAY_API_KEY) → Wikimedia Commons (no key; CC0 /
                       CC BY / CC BY-SA only, attribution recorded). Portrait preferred, else centre-cropped to 9:16.
  4. generated         status "needs_connector" (orchestrator decides, after approval)
  5. labelled slot     status "slot" — the scene uses RSF.broll's labelled slot / the style's placeholder
Every clip: trimmed (or looped) to `seconds`, H.264 yuv420p 30 fps, no audio (the mix carries audio).
Writes broll/<scene>.mp4 + broll/<scene>.json {status, source, provider, url, title, author, licence,
licence_url, attribution, seconds}, broll/index.json, env.json → used.broll_<scene>, CREDITS.txt [broll].

Usage
  broll.py --work work/<slug> [--scene s05] [--force]                # every scene with "broll" in plan/scenes.json
  broll.py --url https://kolesa.kz --seconds 8 --out clip.mp4         # one screen capture
  broll.py --query "car traffic" --seconds 6 --out clip.mp4 [--provider wikimedia|pexels|pixabay]
Exit 0 when every item got a clip (or a documented slot / needs_connector status), 2 on usage errors.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ProviderError, load_dotenv, log, record_used, write_json  # noqa: E402
from music_search import _SAFE_OPENER, check_public_https, write_credits  # noqa: E402  (same URL-safety rules)

HERE = Path(__file__).resolve().parent
HF = "hyperframes@0.8.154"
UA = {"User-Agent": "reels-studio/1.0 (b-roll search)"}
VIDEO_EXTS = {"mp4", "webm", "ogv", "mov", "m4v"}
OK_LICENCE = re.compile(r"^(cc0|cc-zero|cc-by(-sa)?(-\d(\.\d)?)?)$", re.I)
W, H, FPS = 1080, 1920, 30


# --------------------------------------------------------------------------- http (untrusted URLs)
def get_json(url: str, headers: dict | None = None, timeout: float = 25) -> dict:
    check_public_https(url)
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    try:
        with _SAFE_OPENER.open(req, timeout=timeout) as r:
            return json.loads(r.read(4_000_000))
    except urllib.error.HTTPError as e:
        raise ProviderError(f"HTTP {e.code} from {url.split('?')[0]}") from None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
        raise ProviderError(f"network error for {url.split('?')[0]}: {e}") from None


def download_video(url: str, dst: Path, cap_mb: float = 120, timeout: float = 120) -> Path:
    """https + public host on every hop, size cap, video extension only."""
    check_public_https(url)
    ext = urllib.parse.urlsplit(url).path.rsplit(".", 1)[-1].lower()
    if ext not in VIDEO_EXTS:
        ext = "mp4"
    dst = dst.with_suffix("." + ext)
    req = urllib.request.Request(url, headers=UA)
    got = 0
    try:
        with _SAFE_OPENER.open(req, timeout=timeout) as r, open(dst, "wb") as f:
            ln = int(r.headers.get("Content-Length") or 0)
            if ln > cap_mb * 1e6:
                raise ProviderError(f"video larger than {cap_mb} MB — skipped")
            while chunk := r.read(1 << 16):
                got += len(chunk)
                if got > cap_mb * 1e6:
                    raise ProviderError(f"video larger than {cap_mb} MB — skipped")
                f.write(chunk)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        dst.unlink(missing_ok=True)
        raise ProviderError(f"download failed: {e}") from None
    except ProviderError:
        dst.unlink(missing_ok=True)
        raise
    if got < 50_000:
        dst.unlink(missing_ok=True)
        raise ProviderError("download too small (not a video?)")
    return dst


def resolve_page_url(url: str) -> str:
    """Follow server redirects of the director/client URL with the safe opener; return the final https URL."""
    u = urllib.parse.urlsplit(url)
    if u.scheme != "https":
        raise ProviderError("screen capture: https URLs only")
    check_public_https(url)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (reels-studio screen capture)"})
    try:
        with _SAFE_OPENER.open(req, timeout=25) as r:
            final = r.geturl()
            r.read(1024)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429, 503):        # bot walls answer 403 to urllib but often render fine in Chrome
            return url
        raise ProviderError(f"page answered HTTP {e.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise ProviderError(f"page unreachable: {e}") from None
    check_public_https(final)
    return final


# --------------------------------------------------------------------------- ffmpeg
def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise ProviderError(f"{Path(cmd[0]).name} failed: {p.stderr.strip()[-400:]}")


def probe(path: Path) -> dict:
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", str(path)], capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
        s = d["streams"][0]
        return {"w": int(s["width"]), "h": int(s["height"]), "dur": float(d["format"].get("duration") or 0)}
    except (KeyError, IndexError, ValueError, json.JSONDecodeError):
        raise ProviderError(f"not a readable video: {path.name}") from None


def conform(src: Path, dst: Path, seconds: float, start: float = 0.0) -> Path:
    """Crop/scale to 1080×1920 (centre crop), 30 fps, trim or loop to `seconds`, H.264 yuv420p, no audio."""
    info = probe(src)
    loop = info["dur"] and info["dur"] - start < seconds - 0.05
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if loop:
        cmd += ["-stream_loop", "-1"]
    if start > 0 and not loop:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", str(src), "-t", f"{seconds:.3f}", "-an",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart", str(dst)]
    dst.parent.mkdir(parents=True, exist_ok=True)
    run(cmd)
    return dst


# --------------------------------------------------------------------------- 1. client material
def client_material(work: Path | None, scene: str | None) -> Path | None:
    if not work or not scene:
        return None
    mats = work / "plan" / "materials.json"
    if mats.is_file():
        try:
            for it in json.loads(mats.read_text(encoding="utf-8")).get("items", []):
                if it.get("scene") == scene and it.get("kind") in ("broll", "screen_recording") \
                        and it.get("status") == "received" and it.get("path") and (work / it["path"]).is_file():
                    return work / it["path"]
        except (OSError, json.JSONDecodeError):
            pass
    for ext in ("mp4", "mov", "webm", "m4v"):
        hits = sorted(glob.glob(str(work / "input" / f"{scene}_broll*.{ext}")))
        if hits:
            return Path(hits[0])
    return None


# --------------------------------------------------------------------------- 2. screen capture
def chrome_path() -> str:
    if os.environ.get("HYPERFRAMES_CHROME") and Path(os.environ["HYPERFRAMES_CHROME"]).is_file():
        return os.environ["HYPERFRAMES_CHROME"]
    npx = shutil.which("npx")
    if not npx:
        raise ProviderError("npx not found (Node ≥ 22 is required for screen capture)")
    p = subprocess.run([npx, "-y", HF, "browser", "path"], capture_output=True, text=True, timeout=180)
    lines = [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]
    if p.returncode != 0 or not lines or not Path(lines[-1]).is_file():
        raise ProviderError("HyperFrames Chrome not found — run `npx -y hyperframes@0.8.154 browser ensure`")
    return lines[-1]


def _static(frames: Path) -> bool:
    """True when the first and last frame are (nearly) identical — an app-install interstitial or a fixed overlay."""
    fs = sorted(frames.glob("f_*.jpg"))
    if len(fs) < 2:
        return True
    try:
        import numpy as np
        from PIL import Image
        a, b = (np.asarray(Image.open(f).convert("L").resize((108, 192)), dtype=np.float32) for f in (fs[0], fs[-1]))
        return float(np.abs(a - b).mean()) < 2.0
    except ImportError:
        return fs[0].read_bytes() == fs[-1].read_bytes()


def screen_capture(url: str, dst: Path, seconds: float, speed: float = 90, desktop: bool | None = None) -> dict:
    """desktop None = mobile layout first, desktop layout when the mobile page does not move (app interstitial)."""
    node = shutil.which("node")
    if not node:
        raise ProviderError("node not found (Node ≥ 22 is required for screen capture)")
    final = resolve_page_url(url)
    chrome = chrome_path()
    with tempfile.TemporaryDirectory(prefix="rs-broll-") as td:
        for mode in (["desktop"] if desktop else ["mobile"] if desktop is False else ["mobile", "desktop"]):
            frames = Path(td) / mode
            cmd = [node, str(HERE / "screen_capture.mjs"), "--chrome", chrome, "--url", final, "--out", str(frames),
                   "--seconds", f"{seconds:g}", "--fps", str(FPS), "--speed", f"{speed:g}"]
            if mode == "desktop":
                cmd += ["--desktop"]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=int(120 + seconds * FPS * 2))
            if p.returncode != 0:
                raise ProviderError(f"screen capture failed: {p.stderr.strip()[-300:]}")
            meta = json.loads((frames / "meta.json").read_text(encoding="utf-8"))
            check_public_https(meta["final_url"])        # the page may have redirected itself in the browser
            meta["layout"] = mode
            if not _static(frames):
                break
            log(f"[broll] {mode} capture is static (scroll {meta.get('scroll_px')} px, interstitial/overlay?)")
        dst.parent.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(frames / "f_%05d.jpg"), "-an",
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},format=yuv420p",
             "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-movflags", "+faststart", str(dst)])
    host = urllib.parse.urlsplit(meta["final_url"]).hostname or ""
    return {"provider": "screen-capture", "url": meta["final_url"], "title": meta.get("title", "")[:140],
            "author": host, "licence": "screen recording of a public page (editorial use; brand/UI belongs to " + host + ")",
            "licence_url": None, "attribution": f"Screen: {host}", "caption": False,
            "notes": {"layout": meta.get("layout"), "scroll_px": meta.get("scroll_px"), "cookie_banner": meta.get("dismissed"),
                      "blurred": meta.get("blurred")}}


# --------------------------------------------------------------------------- 3. stock
def _score(w: int, h: int, dur: float, seconds: float) -> float:
    portrait = 1.0 if h > w else 0.0
    res = min(min(w, h) / 1080, 1.0)
    fit = 1.0 if dur >= seconds else -1.5   # a looped stock clip reads as a glitch
    return portrait + res + fit


def pexels(query: str, seconds: float, tmp: Path) -> tuple[Path, dict]:
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        raise ProviderError("PEXELS_API_KEY not set")
    q = urllib.parse.urlencode({"query": query, "orientation": "portrait", "per_page": 15, "size": "medium"})
    d = get_json(f"https://api.pexels.com/videos/search?{q}", {"Authorization": key})
    best = None
    for v in d.get("videos", []):
        files = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("width") and f.get("height")]
        files = [f for f in files if min(f["width"], f["height"]) >= 720] or files
        if not files:
            continue
        f = min(files, key=lambda f: abs(min(f["width"], f["height"]) - 1080))
        s = _score(f["width"], f["height"], float(v.get("duration") or 0), seconds)
        if not best or s > best[0]:
            best = (s, v, f)
    if not best:
        raise ProviderError(f"Pexels: nothing for {query!r}")
    _, v, f = best
    src = download_video(f["link"], tmp / "pexels")
    user = (v.get("user") or {}).get("name", "Pexels")
    return src, {"provider": "pexels", "url": v.get("url"), "title": query, "author": user, "licence": "Pexels License",
                 "licence_url": "https://www.pexels.com/license/", "attribution": f"Video by {user} on Pexels", "caption": False}


def pixabay(query: str, seconds: float, tmp: Path) -> tuple[Path, dict]:
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        raise ProviderError("PIXABAY_API_KEY not set")
    q = urllib.parse.urlencode({"key": key, "q": query[:100], "per_page": 20, "safesearch": "true", "video_type": "film"})
    d = get_json(f"https://pixabay.com/api/videos/?{q}")
    best = None
    for hit in d.get("hits", []):
        for size in ("large", "medium"):
            f = (hit.get("videos") or {}).get(size) or {}
            if f.get("url") and f.get("width"):
                s = _score(f["width"], f["height"], float(hit.get("duration") or 0), seconds)
                if not best or s > best[0]:
                    best = (s, hit, f)
                break
    if not best:
        raise ProviderError(f"Pixabay: nothing for {query!r}")
    _, hit, f = best
    src = download_video(f["url"], tmp / "pixabay")
    user = hit.get("user", "Pixabay")
    return src, {"provider": "pixabay", "url": hit.get("pageURL"), "title": query, "author": user,
                 "licence": "Pixabay Content License", "licence_url": "https://pixabay.com/service/license-summary/",
                 "attribution": f"Video by {user} on Pixabay", "caption": False}


def _strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


BAD_WORDS = ("model", "simulation", "diagram", "animation", "chart", "map", "graph", "lecture", "logo", "interview",
             "arduino", "tutorial", "screencast", "toy", "game")


def wikimedia(query: str, seconds: float, tmp: Path) -> tuple[Path, dict]:
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrsearch": f"{query} filetype:video",
        "gsrnamespace": 6, "gsrlimit": 30, "prop": "videoinfo",
        "viprop": "url|size|mime|extmetadata|derivatives|dimensions",
        "viextmetadatafilter": "LicenseShortName|License|Artist|LicenseUrl|ObjectName|ImageDescription|Categories"})
    d = get_json(f"https://commons.wikimedia.org/w/api.php?{q}")
    words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
    cands = []
    for p in (d.get("query") or {}).get("pages", {}).values():
        vi = (p.get("videoinfo") or [{}])[0]
        em = vi.get("extmetadata") or {}
        lic = (em.get("License") or {}).get("value", "")
        if not OK_LICENCE.match(lic):
            continue                                      # CC0 / CC BY / CC BY-SA only
        w, h, dur = int(vi.get("width") or 0), int(vi.get("height") or 0), float(vi.get("duration") or 0)
        title = p.get("title", "")
        tl = title.lower()
        if min(w, h) < 480 or dur < 3 or dur > 900 or any(b in tl for b in BAD_WORDS):
            continue
        ders = [x for x in vi.get("derivatives", []) if "webm" in x.get("type", "") or "mp4" in x.get("type", "")]
        ders = sorted(ders, key=lambda x: int(x.get("height") or 0))
        pick = next((x for x in ders if int(x.get("height") or 0) >= 1080), ders[-1] if ders else None)
        if not pick and int(vi.get("size") or 0) < 120e6:
            pick = {"src": vi.get("url")}
        if not pick:
            continue
        text = " ".join([tl, _strip_html((em.get("ImageDescription") or {}).get("value", "")).lower(),
                         (em.get("Categories") or {}).get("value", "").lower()])
        rel = sum(w_ in text for w_ in words) / max(1, len(words))   # title + description + categories
        if rel < 0.5:
            continue
        cands.append((_score(w, h, dur, seconds) + 2 * rel, title, vi, em, pick["src"]))
    if not cands:
        raise ProviderError(f"Wikimedia Commons: no CC0/CC BY/CC BY-SA video for {query!r}")
    errors = []
    for _, title, vi, em, src_url in sorted(cands, key=lambda c: -c[0])[:3]:
        try:
            src = download_video(src_url, tmp / "commons")
        except ProviderError as e:
            errors.append(str(e))
            continue
        lic = (em.get("LicenseShortName") or {}).get("value", "")
        author = _strip_html((em.get("Artist") or {}).get("value", "")) or "Wikimedia Commons contributor"
        page = vi.get("descriptionurl") or "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        attribution = f"\"{title.removeprefix('File:')}\" by {author}, {lic}, via Wikimedia Commons {page}"
        return src, {"provider": "wikimedia-commons", "url": page, "title": title.removeprefix("File:"), "author": author,
                     "licence": lic, "licence_url": (em.get("LicenseUrl") or {}).get("value"),
                     "attribution": attribution, "caption": not lic.upper().startswith("CC0")}
    raise ProviderError("Wikimedia Commons: downloads failed: " + "; ".join(errors))


STOCK = {"pexels": pexels, "pixabay": pixabay, "wikimedia": wikimedia}


def stock(query: str, seconds: float, dst: Path, only: str | None = None) -> dict:
    errors = []
    with tempfile.TemporaryDirectory(prefix="rs-stock-") as td:
        for name in ([only] if only else ["pexels", "pixabay", "wikimedia"]):
            try:
                src, meta = STOCK[name](query, seconds, Path(td))
                info = probe(src)
                start = max(0.0, min(2.0, (info["dur"] - seconds) / 3)) if info["dur"] > seconds + 1 else 0.0
                conform(src, dst, seconds, start)
                meta["notes"] = {"source_size": [info["w"], info["h"]], "source_dur": round(info["dur"], 2),
                                 "cropped_to_9x16": info["w"] >= info["h"]}
                return meta
            except ProviderError as e:
                log(f"[broll] {name}: {e}")
                errors.append(f"{name}: {e}")
    raise ProviderError("; ".join(errors))


# --------------------------------------------------------------------------- one item
def produce(item: dict, dst: Path, work: Path | None = None, scene: str | None = None, only: str | None = None) -> dict:
    kind = item.get("kind") or ("screen" if item.get("url") else "stock")
    seconds = float(item.get("seconds") or 6)
    seconds = max(1.0, min(seconds, 20.0))
    base = {"scene": scene, "kind": kind, "seconds": seconds, "file": None}
    tried = []
    mat = client_material(work, scene)
    if mat:
        conform(mat, dst, seconds)
        return {**base, "status": "ok", "source": "client", "provider": "client-material", "url": None,
                "title": mat.name, "author": "client", "licence": "client material", "attribution": None,
                "caption": False, "file": str(dst)}
    if kind == "screen" and item.get("url"):
        try:
            meta = screen_capture(item["url"], dst, max(seconds, 5.0) if seconds < 5 else seconds,
                                  speed=float(item.get("speed") or 90), desktop=item.get("desktop"))
            if seconds < 5:
                conform(dst, dst.with_name(dst.stem + ".tmp.mp4"), seconds)
                dst.with_name(dst.stem + ".tmp.mp4").replace(dst)
            return {**base, "status": "ok", "source": "screen", **meta, "file": str(dst)}
        except ProviderError as e:
            log(f"[broll] screen capture: {e}")
            tried.append(f"screen: {e}")
    if kind == "generated":
        return {**base, "status": "needs_connector", "source": None, "tried": tried,
                "note": "generated B-roll only through the ElevenLabs connector, run by the orchestrator after the "
                        "client approves the credit spend (connector-elevenlabs.md) — or give a query for stock"}
    query = item.get("query")
    if query:
        try:
            meta = stock(query, seconds, dst, only)
            return {**base, "status": "ok", "source": "stock", **meta, "file": str(dst)}
        except ProviderError as e:
            tried.append(f"stock: {e}")
    return {**base, "status": "slot", "source": None, "tried": tried,
            "note": "no clip — the scene keeps the labelled B-roll slot; list it in the final report"}


def credits_lines(results: list[dict]) -> list[str]:
    out = []
    for r in results:
        if r.get("status") != "ok" or r.get("source") == "client":
            continue
        tag = "CAPTION " if r.get("caption") else ""
        out.append(f"{tag}{r.get('scene') or '-'}: {r.get('attribution')} · {r.get('licence')} · {r.get('url') or ''}".strip())
    return out


# --------------------------------------------------------------------------- CLI
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work")
    ap.add_argument("--scene")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--url")
    ap.add_argument("--query")
    ap.add_argument("--kind", choices=["screen", "stock", "generated"])
    ap.add_argument("--seconds", type=float, default=6)
    ap.add_argument("--speed", type=float, default=90, help="screen capture scroll speed, CSS px/s (×2.5 on screen)")
    ap.add_argument("--desktop", action="store_true", help="capture the desktop layout (1080 px wide) instead of mobile")
    ap.add_argument("--provider", choices=list(STOCK), help="stock: use only this provider")
    ap.add_argument("--out")
    a = ap.parse_args()
    load_dotenv()

    if not a.work:
        if not a.out or not (a.url or a.query):
            ap.error("give --work, or --out with --url / --query")
        item = {"kind": a.kind, "url": a.url, "query": a.query, "seconds": a.seconds, "speed": a.speed,
                "desktop": True if a.desktop else None}
        r = produce(item, Path(a.out).resolve(), only=a.provider)
        if r["status"] == "ok":
            write_json(Path(a.out).with_suffix(".json"), r)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        sys.exit(0 if r["status"] == "ok" else 3)

    work = Path(a.work).resolve()
    load_dotenv(work / ".env")
    plan = json.loads((work / "plan" / "scenes.json").read_text(encoding="utf-8"))
    out_dir = work / "broll"
    results = []
    for sc in plan.get("scenes", []):
        item = sc.get("broll")
        if not item or (a.scene and sc.get("id") != a.scene):
            continue
        sid = sc["id"]
        dst = out_dir / f"{sid}.mp4"
        side = out_dir / f"{sid}.json"
        if dst.is_file() and side.is_file() and not a.force:
            results.append(json.loads(side.read_text(encoding="utf-8")))
            log(f"[broll] {sid}: exists, skipped (--force to redo)")
            continue
        if "seconds" not in item:
            item = {**item, "seconds": round(float(sc["end"]) - float(sc["start"]), 2)}
        r = produce(item, dst, work, sid, a.provider)
        if r.get("file"):
            r["file"] = str(Path(r["file"]).relative_to(work))
        write_json(side, r)
        results.append(r)
        if r["status"] == "ok":
            record_used(dst, f"broll_{sid}", r["provider"], r.get("licence"))
        log(f"[broll] {sid}: {r['status']} ({r.get('provider') or r.get('note')})")
    if results:
        write_json(out_dir / "index.json", {"items": results})
        lines = credits_lines(results)
        if lines:
            write_credits(work, "broll", lines)
    print(json.dumps({"ok": all(r["status"] in ("ok", "slot", "needs_connector") for r in results),
                      "items": [{k: r.get(k) for k in ("scene", "status", "provider", "file", "licence")} for r in results]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
