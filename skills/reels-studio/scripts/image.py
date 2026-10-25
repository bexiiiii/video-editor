#!/usr/bin/env python3
"""reels-studio image generator / importer.

Generate one hero image (3D object, icon, emoji-style art) for a scene, with a
provider chain that degrades gracefully (see references/providers.md):

  1. OpenAI Images API      gpt-image-2 (opaque) · gpt-image-1.5 background=transparent
                            (or gpt-image-2 on flat chroma green + local cut-out)
  2. Gemini image           gemini-2.5-flash-image (generateContent, inline PNG) on chroma + cut-out
  3. Microsoft Fluent Emoji 3D PNG matching a keyword (MIT, cached in ~/.cache/reels-studio/)
  4. Local placeholder      rendered with Pillow (never fails)

Usage
  image.py --prompt "a rocket" --out assets/img/s03_rocket.png [--size 1024x1536]
           [--transparent] [--style a|b] [--keyword rocket] [--provider auto|openai|gemini|emoji|placeholder]
  image.py --import [PATH] --out assets/img/s03_rocket.png [--transparent]
           # copy a Codex `image_gen` result (newest file in $CODEX_HOME/generated_images or
           # ~/.codex/generated_images when PATH is omitted) and optionally cut out its background
  image.py --cutout IN.png --out OUT.png     # chroma-key an existing image only

Writes OUT plus a sidecar OUT.json {provider, model, prompt, transparent, size, notes}.
API keys are read from the environment (OPENAI_API_KEY, GEMINI_API_KEY / GOOGLE_API_KEY) or a
project `.env`; they are never printed or logged.

Requires: numpy + Pillow for cut-out / placeholder (`pip install numpy pillow`).
"""
from __future__ import annotations

import argparse
import base64
import difflib
import io
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

STYLE_PRESETS = {
    "a": "glossy inflated 3D object, soft studio light, centered, plain background",
    "b": "Apple 3D emoji style",
}
CHROMA_SUFFIX = (
    "Isolated single subject on a perfectly flat, uniform, pure chroma-key green background "
    "(#00FF00), no gradient, no floor, no cast shadow on the background, no green tones in the subject, "
    "generous empty margin around the subject."
)
CACHE = Path(os.environ.get("REELS_STUDIO_CACHE", Path.home() / ".cache" / "reels-studio"))
FLUENT_RAW = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/"
FLUENT_TREE = "https://api.github.com/repos/microsoft/fluentui-emoji/git/trees/main"
UA = {"User-Agent": "reels-studio/1.0"}

# Small RU/UZ/KK → Fluent Emoji name hints (folder names in microsoft/fluentui-emoji/assets).
KEYWORD_HINTS = {
    "ракета": "Rocket", "raketa": "Rocket", "деньги": "Money bag", "pul": "Money bag", "ақша": "Money bag",
    "доллар": "Dollar banknote", "лампа": "Light bulb", "идея": "Light bulb", "g'oya": "Light bulb",
    "сердце": "Red heart", "yurak": "Red heart", "жүрек": "Red heart", "огонь": "Fire", "olov": "Fire",
    "от": "Fire", "звезда": "Star", "yulduz": "Star", "телефон": "Mobile phone", "смартфон": "Mobile phone",
    "ноутбук": "Laptop", "компьютер": "Desktop computer", "робот": "Robot", "ии": "Robot", "ai": "Robot",
    "мозг": "Brain", "miya": "Brain", "часы": "Alarm clock", "время": "Hourglass done", "vaqt": "Hourglass done",
    "уақыт": "Hourglass done", "цель": "Direct hit", "maqsad": "Direct hit", "мақсат": "Direct hit",
    "график": "Chart increasing", "рост": "Chart increasing", "o'sish": "Chart increasing", "өсу": "Chart increasing",
    "падение": "Chart decreasing", "замок": "Locked", "ключ": "Key", "kalit": "Key", "почта": "E-mail",
    "письмо": "Envelope", "камера": "Movie camera", "видео": "Movie camera", "фото": "Camera",
    "микрофон": "Microphone", "музыка": "Musical note", "книга": "Books", "kitob": "Books", "кітап": "Books",
    "подарок": "Wrapped gift", "sovg'a": "Wrapped gift", "трофей": "Trophy", "кубок": "Trophy",
    "медаль": "1st place medal", "корона": "Crown", "алмаз": "Gem stone", "бриллиант": "Gem stone",
    "глобус": "Globe showing Europe-Africa", "мир": "Globe with meridians", "дом": "House", "uy": "House",
    "машина": "Automobile", "mashina": "Automobile", "самолет": "Airplane", "молния": "High voltage",
    "энергия": "High voltage", "закладка": "Bookmark", "сохрани": "Bookmark", "saqla": "Bookmark",
    "лайк": "Thumbs up", "палец": "Thumbs up", "галочка": "Check mark button", "да": "Check mark button",
    "нет": "Cross mark", "вопрос": "Red question mark", "savol": "Red question mark", "сұрақ": "Red question mark",
    "внимание": "Warning", "предупреждение": "Warning", "календарь": "Calendar", "kalendar": "Calendar",
    "кофе": "Hot beverage", "пицца": "Pizza", "еда": "Pot of food", "ovqat": "Pot of food",
    "магнит": "Magnet", "инструмент": "Hammer and wrench", "настройки": "Gear", "шестеренка": "Gear",
    "поиск": "Magnifying glass tilted left", "лупа": "Magnifying glass tilted left", "чат": "Speech balloon",
    "сообщение": "Speech balloon", "xabar": "Speech balloon", "люди": "People hugging", "команда": "Handshake",
    "сделка": "Handshake", "рука": "Waving hand", "глаз": "Eyes", "мегафон": "Megaphone", "реклама": "Megaphone",
    "корзина": "Shopping cart", "покупка": "Shopping bags", "карта": "Credit card", "банк": "Bank",
    "школа": "School", "учеба": "Graduation cap", "работа": "Briefcase", "ish": "Briefcase", "жұмыс": "Briefcase",
    "бизнес": "Briefcase", "попкорн": "Popcorn", "праздник": "Party popper", "успех": "Party popper",
    "сон": "Zzz", "щит": "Shield", "безопасность": "Shield", "яблоко": "Red apple", "кнопка": "Red circle",
}

_KEYS_CACHE: dict | None = None


# ----------------------------------------------------------------------------- utilities

def log(msg: str) -> None:
    print(f"[image] {msg}", file=sys.stderr)


def load_env_key(*names: str) -> str | None:
    """Return the first non-empty key from the environment or a project .env (never logged)."""
    global _KEYS_CACHE
    for n in names:
        v = os.environ.get(n)
        if v:
            return v.strip()
    if _KEYS_CACHE is None:
        _KEYS_CACHE = {}
        for base in [Path.cwd(), *Path.cwd().parents][:6]:
            f = base / ".env"
            if f.is_file():
                for line in f.read_text(errors="ignore").splitlines():
                    m = re.match(r"\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.*)\s*$", line)
                    if m and m.group(1) not in _KEYS_CACHE:
                        _KEYS_CACHE[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    for n in names:
        if _KEYS_CACHE.get(n):
            return _KEYS_CACHE[n]
    return None


def http_json(url: str, payload: dict | None, headers: dict, timeout: int = 240) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={**UA, **headers,
                                 **({"Content-Type": "application/json"} if data else {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")[:600]
        raise RuntimeError(f"HTTP {e.code} from {urllib.parse.urlsplit(url).netloc}: {body}") from None


def http_bytes(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def need_pil():
    try:
        import numpy  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError:
        sys.exit("image.py: numpy + Pillow are required for this step (pip install numpy pillow)")


def parse_size(s: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)x(\d+)", s.strip())
    if not m:
        raise SystemExit(f"--size must look like 1024x1536, got {s!r}")
    return int(m.group(1)), int(m.group(2))


def build_prompt(prompt: str, style: str | None, chroma: bool) -> str:
    preset = STYLE_PRESETS.get((style or "").lower(), "")
    if chroma:
        preset = preset.replace(", plain background", "")
    parts = [prompt.strip().rstrip(".")]
    if preset:
        parts.append(preset)
    if chroma:
        parts.append(CHROMA_SUFFIX)
    return ". ".join(parts)


# ----------------------------------------------------------------------------- chroma key

def has_real_alpha(img) -> bool:
    """True if the image already carries meaningful transparency (e.g. native transparent output)."""
    import numpy as np
    if img.mode not in ("RGBA", "LA"):
        return False
    a = np.asarray(img.getchannel("A"))
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    return bool((border < 128).mean() > 0.5)


def chroma_key(img, key: str = "auto", softness: float = 1.0, despill: bool = True,
               trim: bool = True, pad: int = 12):
    """High-quality chroma key → RGBA Pillow image.

    Algorithm: estimate key colour from the border (or green/magenta/blue/#hex), measure each pixel's
    distance from the key in the CbCr chroma plane (luma-independent, so shading on the backdrop is
    ignored), derive thresholds from the border's own distance spread, build a soft matte with a
    smoothstep, shrink it by ~1 px and feather (kills the bright fringe), un-mix the key colour from
    semi-transparent edge pixels (colour decontamination), suppress spill on opaque pixels, and trim to
    the alpha bounding box.
    """
    import numpy as np
    from PIL import Image, ImageFilter

    rgb = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    h, w, _ = rgb.shape
    bw = max(2, min(h, w) // 64)
    border = np.concatenate([rgb[:bw].reshape(-1, 3), rgb[-bw:].reshape(-1, 3),
                             rgb[:, :bw].reshape(-1, 3), rgb[:, -bw:].reshape(-1, 3)])
    named = {"green": (0.0, 1.0, 0.0), "magenta": (1.0, 0.0, 1.0), "blue": (0.0, 0.0, 1.0)}
    if key in named:
        # use the border median if it is close to the named colour (real renders are never pure)
        k = np.array(named[key], np.float32)
        med = np.median(border, axis=0)
        if np.linalg.norm(med - k) < 0.6:
            k = med
    elif key.startswith("#") and len(key) == 7:
        k = np.array([int(key[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0
    else:
        k = np.median(border, axis=0)

    def cbcr(x):
        y = 0.299 * x[..., 0] + 0.587 * x[..., 1] + 0.114 * x[..., 2]
        return np.stack([(x[..., 2] - y) * 0.564, (x[..., 0] - y) * 0.713], axis=-1), y

    cc, _ = cbcr(rgb)
    kc, _ = cbcr(k[None, None, :])
    dist = np.linalg.norm(cc - kc[0, 0], axis=-1)
    kmag = float(np.linalg.norm(kc)) or 0.2
    bd = np.linalg.norm(cbcr(border[None, :, :])[0][0] - kc[0, 0], axis=-1)
    t0 = max(float(np.percentile(bd, 98)) * 1.15, 0.04 * kmag / 0.3)
    t1 = t0 + max(0.10, 0.45 * kmag) * softness
    a = np.clip((dist - t0) / (t1 - t0), 0, 1)
    a = a * a * (3 - 2 * a)  # smoothstep

    # matte cleanup: erode 1px then feather 0.8px
    am = Image.fromarray((a * 255).astype(np.uint8), "L")
    am = am.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    a = np.asarray(am).astype(np.float32) / 255.0

    out = rgb.copy()
    # colour decontamination: C = a*F + (1-a)*K  →  F = (C - (1-a)K)/a  on the soft edge
    edge = (a > 0.02) & (a < 0.98)
    ae = a[edge][:, None]
    out[edge] = np.clip((rgb[edge] - (1 - ae) * k) / np.maximum(ae, 0.02), 0, 1)
    if despill:
        r, g, b = out[..., 0], out[..., 1], out[..., 2]
        dom = int(np.argmax(k))
        if k[1] > k[0] and k[1] > k[2]:            # green key
            lim = np.maximum(r, b)
            g[:] = np.where(g > lim, lim + (g - lim) * 0.15, g)
        elif k[0] > k[1] and k[2] > k[1]:          # magenta key
            m = np.minimum(r, b)
            spill = np.clip(m - g, 0, None) * 0.85
            r -= spill; b -= spill                  # noqa: E702
        else:                                      # generic: pull dominant channel toward the others
            others = [i for i in range(3) if i != dom]
            lim = np.maximum(out[..., others[0]], out[..., others[1]])
            ch = out[..., dom]
            ch[:] = np.where(ch > lim, lim + (ch - lim) * 0.2, ch)
    rgba = np.dstack([np.clip(out, 0, 1), a])
    res = Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA")
    if trim:
        res = trim_to_bbox(res, pad)
    return res


def trim_to_bbox(img, pad: int = 12, thresh: int = 8):
    import numpy as np
    a = np.asarray(img.getchannel("A"))
    ys, xs = np.where(a > thresh)
    if len(xs) == 0:
        return img
    x0, x1 = max(0, xs.min() - pad), min(img.width, xs.max() + 1 + pad)
    y0, y1 = max(0, ys.min() - pad), min(img.height, ys.max() + 1 + pad)
    return img.crop((int(x0), int(y0), int(x1), int(y1)))


# ----------------------------------------------------------------------------- providers

def gen_openai(prompt: str, size: str, transparent: bool, style: str | None, quality: str):
    """Return (PIL image, meta) or raise. Native transparency via gpt-image-1.5, else chroma cut-out."""
    from PIL import Image
    key = load_env_key("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/images/generations"
    hdr = {"Authorization": f"Bearer {key}"}
    attempts = []
    if transparent:
        tsize = size if size in ("1024x1024", "1024x1536", "1536x1024") else "1024x1536"
        attempts.append(("gpt-image-1.5", {"prompt": build_prompt(prompt, style, False).replace(", plain background", "")
                                           + ". Transparent background.", "size": tsize,
                                           "background": "transparent", "output_format": "png"}, False))
        attempts.append(("gpt-image-2", {"prompt": build_prompt(prompt, style, True), "size": size}, True))
    else:
        attempts.append(("gpt-image-2", {"prompt": build_prompt(prompt, style, False), "size": size}, False))
    last = None
    for model, body, cut in attempts:
        try:
            body = {"model": model, "n": 1, "quality": quality, **body}
            res = http_json(url, body, hdr)
            b64 = res["data"][0].get("b64_json")
            if not b64:
                raise RuntimeError("no b64_json in response")
            img = Image.open(io.BytesIO(base64.b64decode(b64)))
            img.load()
            notes = []
            if transparent and (cut or not has_real_alpha(img)):
                img = chroma_key(img, "green" if cut else "auto")
                notes.append("chroma-key cut-out")
            elif transparent:
                img = trim_to_bbox(img.convert("RGBA"))
            return img, {"provider": "openai", "model": model, "prompt": body["prompt"], "notes": notes}
        except Exception as e:  # try next model
            last = e
            log(f"openai {model} failed: {e}")
    raise RuntimeError(f"openai failed: {last}")


def gen_gemini(prompt: str, size: str, transparent: bool, style: str | None):
    from PIL import Image
    key = load_env_key("GEMINI_API_KEY", "GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set")
    model = os.environ.get("REELS_GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    w, h = parse_size(size)
    ratios = {"1:1": 1.0, "2:3": 2 / 3, "3:2": 1.5, "3:4": 0.75, "4:3": 4 / 3, "9:16": 9 / 16, "16:9": 16 / 9}
    ar = min(ratios, key=lambda r: abs(ratios[r] - w / h))
    p = build_prompt(prompt, style, transparent)
    body = {"contents": [{"parts": [{"text": p}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": ar}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    res = http_json(url, body, {"x-goog-api-key": key})
    for cand in res.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if data:
                img = Image.open(io.BytesIO(base64.b64decode(data)))
                img.load()
                notes = []
                if transparent:
                    img = chroma_key(img, "green")
                    notes.append("chroma-key cut-out")
                return img, {"provider": "gemini", "model": model, "prompt": p, "notes": notes}
    raise RuntimeError("gemini returned no image part")


def _fluent_index() -> list[str]:
    """List of Fluent Emoji folder names (cached for 30 days)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    idx = CACHE / "fluent_index.json"
    if idx.is_file() and time.time() - idx.stat().st_mtime < 30 * 86400:
        return json.loads(idx.read_text())
    root = http_json(FLUENT_TREE, None, {}, timeout=30)
    sha = next(t["sha"] for t in root["tree"] if t["path"] == "assets")
    tree = http_json(f"https://api.github.com/repos/microsoft/fluentui-emoji/git/trees/{sha}", None, {}, timeout=60)
    names = sorted(t["path"] for t in tree["tree"] if t["type"] == "tree")
    idx.write_text(json.dumps(names, ensure_ascii=False))
    return names


def fluent_lookup(keyword: str, prompt: str) -> str | None:
    """Pick the best Fluent Emoji folder name for a keyword (or words of the prompt)."""
    try:
        names = _fluent_index()
    except Exception as e:
        log(f"fluent index unavailable ({e}); trying hint table only")
        names = []
    lower = {n.lower(): n for n in names}
    cands = [c for c in [keyword] if c] + re.findall(r"[\w'-]+", prompt.lower())
    for c in cands:
        c = c.lower().strip()
        if c in KEYWORD_HINTS:
            return KEYWORD_HINTS[c]
        if c in lower:
            return lower[c]
    for c in cands:  # fuzzy (English words / multiword names)
        c = c.lower().strip()
        if len(c) < 3:
            continue
        starts = [n for n in names if n.lower().startswith(c + " ") or n.lower() == c]
        if starts:
            return min(starts, key=len)
        m = difflib.get_close_matches(c, list(lower), n=1, cutoff=0.82)
        if m:
            return lower[m[0]]
    return None


def gen_emoji(keyword: str, prompt: str, transparent: bool):
    from PIL import Image
    name = fluent_lookup(keyword, prompt)
    if not name:
        raise RuntimeError(f"no Fluent Emoji matches {keyword or prompt!r}")
    snake = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    cache_dir = CACHE / "fluent"
    cache_dir.mkdir(parents=True, exist_ok=True)
    local = cache_dir / f"{snake}_3d.png"
    if not local.is_file():
        q = urllib.parse.quote(name)
        last = None
        for rel in (f"{q}/3D/{snake}_3d.png", f"{q}/Default/3D/{snake}_3d_default.png"):
            try:
                data = http_bytes(FLUENT_RAW + rel)
                local.write_bytes(data)
                break
            except Exception as e:
                last = e
        else:
            raise RuntimeError(f"fluent download failed for {name!r}: {last}")
    img = Image.open(local)
    img.load()
    img = img.convert("RGBA")
    if not transparent:
        bg = Image.new("RGBA", img.size, (0, 0, 0, 0))
        img = Image.alpha_composite(bg, img)
    return img, {"provider": "fluent-emoji", "model": f"fluentui-emoji/{name}/3D", "prompt": prompt,
                 "notes": ["Microsoft Fluent Emoji (MIT); 256px source — keep it ≤ ~360px on screen"]}


def gen_placeholder(prompt: str, size: str, transparent: bool, keyword: str):
    from PIL import Image, ImageDraw, ImageFont
    w, h = parse_size(size)
    s = min(w, h)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0) if transparent else (236, 237, 240, 255))
    d = ImageDraw.Draw(img)
    r = int(s * 0.36)
    cx, cy = w // 2, h // 2
    for i in range(r, 0, -2):  # soft radial "inflated" disc
        t = i / r
        col = (int(70 + 120 * (1 - t)), int(110 + 110 * (1 - t)), int(230 + 20 * (1 - t)), 255)
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=col)
    label = (keyword or (re.findall(r"\w+", prompt) or ["?"])[0])[:14]
    font = None
    for f in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            try:
                font = ImageFont.truetype(f, int(s * 0.07))
                break
            except Exception:
                pass
    font = font or ImageFont.load_default()
    d.text((cx, cy), label, fill=(255, 255, 255, 255), anchor="mm", font=font)
    if transparent:
        img = trim_to_bbox(img)
    return img, {"provider": "placeholder", "model": "pillow", "prompt": prompt,
                 "notes": ["PLACEHOLDER — no image provider available; replace before delivery"]}


# ----------------------------------------------------------------------------- import (Codex image_gen)

def newest_codex_image() -> Path:
    roots = []
    if os.environ.get("CODEX_HOME"):
        roots.append(Path(os.environ["CODEX_HOME"]) / "generated_images")
    roots.append(Path.home() / ".codex" / "generated_images")
    files = []
    for r in roots:
        if r.is_dir():
            files += [p for p in r.rglob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and p.is_file()]
    if not files:
        raise SystemExit("image.py --import: no images in $CODEX_HOME/generated_images or ~/.codex/generated_images")
    return max(files, key=lambda p: p.stat().st_mtime)


# ----------------------------------------------------------------------------- main

def save(img, out: Path, meta: dict) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() in (".jpg", ".jpeg"):
        img.convert("RGB").save(out, quality=92)
    else:
        img.save(out, optimize=True)
    meta = {**meta, "size": f"{img.width}x{img.height}", "mode": img.mode}
    Path(str(out) + ".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(json.dumps({"ok": True, "out": str(out), **{k: meta[k] for k in ("provider", "model", "size")},
                      "notes": meta.get("notes", [])}, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", help="what to draw (subject only; style preset is appended)")
    ap.add_argument("--out", required=True, help="output PNG path, e.g. work/<slug>/assets/img/s03_rocket.png")
    ap.add_argument("--size", default="1024x1024", help="WxH, e.g. 1024x1536 (default 1024x1024)")
    ap.add_argument("--transparent", action="store_true", help="transparent background (native or chroma cut-out)")
    ap.add_argument("--style", choices=["a", "b", "A", "B"], help="style preset A (glossy 3D) / B (Apple 3D emoji)")
    ap.add_argument("--keyword", default="", help="keyword for the Fluent Emoji fallback (en/ru/uz/kk)")
    ap.add_argument("--provider", default="auto", choices=["auto", "openai", "gemini", "emoji", "placeholder"])
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    ap.add_argument("--import", dest="import_", nargs="?", const="", default=None, metavar="PATH",
                    help="import a Codex image_gen output; pass the exact PATH (newest file is only a single-worker convenience — unsafe with parallel art workers)")
    ap.add_argument("--cutout", metavar="IN", help="only chroma-key an existing image into --out")
    ap.add_argument("--key", default="auto", help="chroma key: auto (border) | green | magenta | blue | #rrggbb")
    ap.add_argument("--softness", type=float, default=1.0, help="matte softness multiplier (default 1.0)")
    args = ap.parse_args()
    out = Path(args.out)
    style = args.style.lower() if args.style else None

    if args.import_ is not None or args.cutout:
        need_pil()
        from PIL import Image
        src = Path(args.cutout) if args.cutout else (Path(args.import_) if args.import_ else newest_codex_image())
        if not src.is_file():
            sys.exit(f"image.py: source image not found: {src}")
        img = Image.open(src)
        img.load()
        notes = []
        if args.transparent or args.cutout:
            if has_real_alpha(img):
                img = trim_to_bbox(img.convert("RGBA"))
                notes.append("source already transparent")
            else:
                img = chroma_key(img, args.key, args.softness)
                notes.append(f"chroma-key cut-out (key={args.key})")
        save(img, out, {"provider": "codex-image_gen" if args.import_ is not None else "cutout",
                        "model": "gpt-image-2 (Codex built-in)" if args.import_ is not None else "local",
                        "prompt": args.prompt or "", "source": src.name, "transparent": bool(args.transparent),
                        "notes": notes})
        return

    if not args.prompt:
        ap.error("--prompt is required (or use --import / --cutout)")
    parse_size(args.size)
    need_pil()
    chain = ["openai", "gemini", "emoji", "placeholder"] if args.provider == "auto" else [args.provider]
    errors = []
    for prov in chain:
        try:
            if prov == "openai":
                img, meta = gen_openai(args.prompt, args.size, args.transparent, style, args.quality)
            elif prov == "gemini":
                img, meta = gen_gemini(args.prompt, args.size, args.transparent, style)
            elif prov == "emoji":
                img, meta = gen_emoji(args.keyword, args.prompt, args.transparent)
            else:
                img, meta = gen_placeholder(args.prompt, args.size, args.transparent, args.keyword)
            if errors:
                meta.setdefault("notes", []).append("fallback after: " + "; ".join(errors))
            meta["transparent"] = bool(args.transparent)
            meta["style"] = style
            save(img, out, meta)
            return
        except Exception as e:
            msg = str(e)
            errors.append(f"{prov}: {msg[:160]}")
            log(f"{prov} unavailable: {msg[:300]}")
    sys.exit("image.py: all providers failed: " + " | ".join(errors))


if __name__ == "__main__":
    main()
