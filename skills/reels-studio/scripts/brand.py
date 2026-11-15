#!/usr/bin/env python3
"""reels-studio brand layer: brief.brand → composition/lib/brand.{css,js,json}. Stdlib only.

  brand.py --work work/<slug>                       # reads brief.json (+ plan/scenes.json style), writes composition/lib/
  brand.py --brief brief.json --style b --out DIR    # same, explicit (used by make_brand_previews.sh)
  brand.py --accent "#E85D9E" [--accent2 …] [--ink …] [--font …] [--lang ru] --style a --out DIR   # ad-hoc test
  add --check to print the report without writing files.

What it does (references/branding.md is the spec):
  * derives every brand-overridable token of the style's packs (A/D → a, B → b, C → a+b+c, E → e) from 1–2 brand
    colours with OKLCH math: the stock ramp of each token family (e.g. A's 3D bookmark #1E8BFF → #7CCBFF/#0A4FD0…,
    E's gold #E89E0C → #C9822E → #A8672C, B's blue takeover #1C86FD → #0D4C90) is re-based onto the brand colour by
    transferring each stop's OKLCH offset (ΔL, C ratio, Δh) — so ramps keep the style's shading, only the hue changes;
  * enforces WCAG 2.x contrast for every text/UI role in every theme the style uses (light, dark, blue takeover,
    card surfaces) by moving OKLCH lightness only (hue kept, chroma gamut-clipped) and reports each adjustment;
  * writes brand.css (overrides of the style's CSS variables / literal-colour selectors; loaded AFTER the style
    tokens), brand.js (`window.RS_BRAND = {…}` for the JS libs; loaded BEFORE the libs) and brand.json (same data +
    report). No brand colours and no font → nothing is written (style stays pristine) and stale files are removed.
  * optional brand.font (Google Fonts family): verified against the reel language through the Google Fonts css2
    API's unicode-range (ru → Cyrillic, kk → + ә ғ қ ң ө ұ ү һ і, uz → Latin + oʻ gʻ (U+02BB)). Not covered, not
    found, or offline → the style font is kept and a warning is printed.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# ───────────────────────────── colour math (sRGB ↔ OKLab/OKLCH, WCAG) ─────────────────────────────

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def parse_hex(s: str) -> tuple[float, float, float]:
    m = HEX_RE.match(str(s).strip())
    if not m:
        raise ValueError(f"not a hex colour: {s!r}")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def to_hex(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in rgb)


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1 / 3), x)


def rgb_to_oklch(rgb) -> tuple[float, float, float]:
    r, g, b = (_lin(c) for c in rgb)
    l_ = _cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m_ = _cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s_ = _cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def _oklch_to_lin(L: float, C: float, h: float):
    A, B = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m_ = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s_ = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
            -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)


def oklch_to_rgb(L: float, C: float, h: float):
    """OKLCH → sRGB, gamut-mapped by reducing chroma (hue + lightness preserved)."""
    L = max(0.0, min(1.0, L))
    C = max(0.0, C)

    def ok(c):
        return all(-1e-6 <= v <= 1 + 1e-6 for v in _oklch_to_lin(L, c, h))
    if not ok(C):
        lo, hi = 0.0, C
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if ok(mid) else (lo, mid)
        C = lo
    return tuple(_gam(max(0.0, min(1.0, v))) for v in _oklch_to_lin(L, C, h))


def lch_hex(L, C, h) -> str:
    return to_hex(oklch_to_rgb(L, C, h))


def luminance(hex_: str) -> float:
    r, g, b = (_lin(c) for c in parse_hex(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def over(fg: str, alpha: float, bg: str) -> str:
    """Composite fg@alpha over an opaque bg (sRGB, as browsers do)."""
    f, b = parse_hex(fg), parse_hex(bg)
    return to_hex(tuple(alpha * x + (1 - alpha) * y for x, y in zip(f, b)))


def rgba(hex_: str, a: float) -> str:
    r, g, b = (round(c * 255) for c in parse_hex(hex_))
    return f"rgba({r},{g},{b},{a:g})"


def set_L(hex_: str, L: float) -> str:
    _, C, h = rgb_to_oklch(parse_hex(hex_))
    return lch_hex(L, C, h)


def shift_L(hex_: str, dL: float, c_mul: float = 1.0) -> str:
    L, C, h = rgb_to_oklch(parse_hex(hex_))
    return lch_hex(L + dL, C * c_mul, h)


def transfer(orig_base: str, orig_stop: str, new_base: str, hue: float = 0.0) -> str:
    """Re-base one stop of a stock ramp: apply the stop's OKLCH offset (ΔL, chroma ratio) from its stock base to the
    brand base. Hue stays the brand's (`hue`=1 would also carry the stock hue drift, e.g. gold's yellow sheen —
    that turns other hues muddy/purple, so it is off)."""
    Lb, Cb, hb = rgb_to_oklch(parse_hex(orig_base))
    Ls, Cs, hs = rgb_to_oklch(parse_hex(orig_stop))
    Ln, Cn, hn = rgb_to_oklch(parse_hex(new_base))
    ratio = Cs / Cb if Cb > 0.02 else 1.0
    dh = (((hs - hb + 180) % 360) - 180) * hue
    if Cn < 0.03:            # achromatic brand colour: keep it neutral, don't invent a hue
        dh, ratio = 0.0, 1.0
    return lch_hex(Ln + (Ls - Lb), Cn * ratio, hn + dh)


WHITE, NEAR_BLACK = "#FFFFFF", "#0B0D0D"


# ───────────────────────────── report + contrast enforcement ─────────────────────────────

class Report:
    def __init__(self) -> None:
        self.checks: list[dict] = []
        self.adjusted: list[dict] = []
        self.warnings: list[str] = []

    def fit(self, token: str, color: str, bgs: list[tuple[str, str]], minr: float, role: str = "text") -> str:
        """Return `color` with OKLCH lightness moved the least amount so contrast ≥ minr against every bg."""
        def worst(c):
            return min(contrast(c, b) for _, b in bgs)
        before = worst(color)
        out = color
        if before + 1e-9 < minr:
            L0, C0, h0 = rgb_to_oklch(parse_hex(color))
            best = None
            for i in range(1, 201):
                d = i * 0.005
                for L in (L0 + d, L0 - d):
                    if 0 <= L <= 1:
                        c = lch_hex(L, C0, h0)
                        if worst(c) + 1e-9 >= minr:
                            best = c
                            break
                if best:
                    break
            if best is None:
                # unreachable target (e.g. needs to clear both a dark and a light bg at 4.5+): take the best L
                cands = [lch_hex(i / 200, C0, h0) for i in range(201)]
                best = max(cands, key=worst)
                self.warnings.append(f"{token}: no lightness reaches {minr}:1 against "
                                     f"{', '.join(n for n, _ in bgs)} — best {worst(best):.2f}:1 ({best})")
            out = best
            self.adjusted.append({"token": token, "role": role, "from": color, "to": out,
                                  "min": minr, "before": round(before, 2), "after": round(worst(out), 2),
                                  "against": [n for n, _ in bgs]})
        for n, b in bgs:
            self.checks.append({"token": token, "role": role, "fg": out, "bg": b, "bg_name": n,
                                "ratio": round(contrast(out, b), 2), "min": minr,
                                "ok": contrast(out, b) + 1e-9 >= minr})
        return out

    def on_accent(self, token: str, surface: str, minr: float = 4.5, max_dl: float = 0.12) -> tuple[str, str]:
        """Label colour on a filled accent surface. Prefer white (the styles' look); darken the surface by up to
        `max_dl` OKLCH L to get white to `minr`; else switch the label to near-black; else darken further."""
        cw = contrast(WHITE, surface)
        if cw + 1e-9 >= minr:
            out = (surface, WHITE)
        else:
            L0, C0, h0 = rgb_to_oklch(parse_hex(surface))
            dark = None
            for i in range(1, int(max_dl / 0.005) + 1):
                c = lch_hex(L0 - i * 0.005, C0, h0)
                if contrast(WHITE, c) + 1e-9 >= minr:
                    dark = c
                    break
            if dark:
                out = (dark, WHITE)
                self.adjusted.append({"token": token, "role": "surface (white label)", "from": surface, "to": dark,
                                      "min": minr, "before": round(cw, 2), "after": round(contrast(WHITE, dark), 2),
                                      "against": ["#FFFFFF label"]})
            elif contrast(NEAR_BLACK, surface) + 1e-9 >= minr:
                out = (surface, NEAR_BLACK)
                self.adjusted.append({"token": token, "role": "label", "from": WHITE, "to": NEAR_BLACK, "min": minr,
                                      "before": round(cw, 2), "after": round(contrast(NEAR_BLACK, surface), 2),
                                      "against": [surface]})
            else:
                s = self.fit(token + " (surface)", surface, [("#FFFFFF label", WHITE)], minr, "surface")
                out = (s, WHITE)
        self.checks.append({"token": token, "role": "label on accent", "fg": out[1], "bg": out[0], "bg_name": "accent surface",
                            "ratio": round(contrast(out[1], out[0]), 2), "min": minr,
                            "ok": contrast(out[1], out[0]) + 1e-9 >= minr})
        return out

    def info(self, token: str, fg: str, bg: str, bg_name: str, note: str) -> None:
        self.checks.append({"token": token, "role": note, "fg": fg, "bg": bg, "bg_name": bg_name,
                            "ratio": round(contrast(fg, bg), 2), "min": None, "ok": True})


# Contrast policy (references/branding.md): text ≥ 4.5 (WCAG AA); display text ≥ 72 px bold at 1080 wide
# (≈ 27 CSS px on a 400-px-wide phone = WCAG "large") ≥ 3.0; non-text UI (dots, handles, rings, bars) ≥ 3.0
# (WCAG 1.4.11). Decorative glows/shadows/gradient highlights are not checked.
TEXT, LARGE, UI = 4.5, 3.0, 3.0

# Theme backgrounds each pack renders on (sampled from tokens.css).
A_DARK, A_LIGHT, A_CARD_LIGHT = "#0B0D0D", "#FBFDFD", "#F3F5F5"
B_LIGHT, B_CARD, B_DARK, B_DARK_CARD, B_THUMB = "#F0F0F3", "#FCFCFC", "#1A1A1C", "#2C2C2E", "#FFFFFF"
E_BG, E_CARD = "#FCFCFC", "#F4F4F6"


# ───────────────────────────── per-pack token builders ─────────────────────────────
# Each returns (css_rules: list[str], js_palette: dict). Stock values are cited next to every override.

def pack_a(br: dict, R: Report):
    acc, acc2, ink = br["accent"], br.get("accent2"), br.get("ink")
    css, js = [], {}
    # UI accent (stock blue family #257CFA/#2C7CF4/#0084F0/#2A90F6/#2478F6): handles, rims, connectors, 3D objects —
    # must read on A's dark AND light pages.
    ui = R.fit("a.accent-ui", acc, [("A dark", A_DARK), ("A light", A_LIGHT)], UI, "ui")
    chip, chip_on = R.on_accent("a.chip/marker", ui, TEXT)
    hook_src = acc2 or acc
    hook = R.fit("a.hook-accent (lime)", hook_src, [("A dark", A_DARK)], TEXT, "text")
    L, C, h = rgb_to_oklch(parse_hex(ui))
    sel_dark = R.fit("a.selection-dark", lch_hex(0.36, min(C, 0.075), h), [("ink #FBFDFD", "#FBFDFD")], TEXT, "selection fill")
    sel_light_a = 0.24
    R.info("a.selection-light", NEAR_BLACK, over(ui, sel_light_a, A_LIGHT), "ui@24% on light", "text on selection")
    if contrast(NEAR_BLACK, over(ui, sel_light_a, A_LIGHT)) < TEXT:
        sel_light_a = 0.16
    root = {
        "--rsa-blue": ui, "--rsa-chip": chip, "--rsa-line-blue": ui, "--rsa-handle": ui, "--rsa-sel": sel_dark,
        "--rsa-lime": hook, "--rsa-lime-alt": transfer("#BAE436", "#C0EA4E", hook),
    }
    css.append(":root { " + " ".join(f"{k}: {v};" for k, v in root.items()) + " }")
    css.append(f".rsa-theme-light .rsa-sel-box {{ background: {rgba(ui, sel_light_a)}; }}")
    css.append(f".rsa-chip {{ color: {chip_on}; box-shadow: inset 0 1px 0 rgba(255,255,255,.35), 0 10px 24px {rgba(chip, .30)}; }}")
    css.append(f".rsa-marker-bg {{ background: {chip}; }} .rsa-marker-tx {{ color: {chip_on}; }}")
    css.append(f".rsa-card--light {{ --rim-grad: linear-gradient(225deg, {rgba(ui, .15)} 0%, {rgba(ui, .9)} 40%, {ui} 100%); "
               f"box-shadow: 0 30px 60px {rgba(shift_L(ui, -0.3), .10)}; }}")
    bar = [transfer("#3CA4FC", s, shift_L(ui, 0.08)) for s in ("#1C74F4", "#3CA4FC", "#ACE4FC")]
    css.append(f".rsa-bar-fill {{ background: linear-gradient(90deg, {bar[0]} 0%, {bar[1]} 25%, {bar[2]} 50%, {bar[1]} 75%, {bar[0]} 100%); "
               f"background-size: 200% 100%; }}")
    if ink:
        pill = R.fit("a.pill-light (ink)", ink, [("pill text #FBFDFD", "#FBFDFD"), ("A light", A_LIGHT)], TEXT, "surface")
        css.append(f".rsa-theme-light {{ --pill-bg: {pill}; }}")
    # 3D placeholder objects (lib.js): stock ramps re-based onto the UI accent
    bm = {k: transfer("#1E8BFF", v, ui) for k, v in
          {"hi": "#7CCBFF", "lo": "#0A4FD0", "d0": "#0B57D8", "d1": "#06328F", "line": "#04318A"}.items()}
    bm["base"], bm["shadow"] = ui, rgba(transfer("#1E8BFF", "#001E5A", ui), .30)
    coin = {k: transfer("#1E8BFF", v, ui) for k, v in
            {"s0": "#0B4FC4", "s55": "#7CC4FF", "s1": "#0A44B0", "t0": "#E8F5FF", "t25": "#6DB8FF", "t1": "#0D5AD8"}.items()}
    coin["base"] = ui
    js.update({"accent": ui, "bookmark": bm, "coin": coin})
    return css, js


def takeover(acc: str, R: Report, token: str) -> list[str]:
    """B/C blue takeover gradient re-based on the brand: the 50 % stop (#176ECD, behind the content) carries white
    text ≥ 4.5; the top stop (#1C86FD) carries the white display headline ≥ 3.0."""
    stock = ["#1C86FD", "#1C86FD", "#1A7FEF", "#1877DE", "#176ECD", "#1466BB", "#115BAD", "#0F539A", "#0D4C90"]
    base = R.fit(token + " (50% stop)", acc, [("white text", WHITE)], TEXT, "takeover bg")
    stops = [transfer("#176ECD", s, base) for s in stock]
    top = stops[0]
    if contrast(WHITE, top) < LARGE:
        fixed = R.fit(token + " (top stop)", top, [("white headline", WHITE)], LARGE, "takeover bg")
        d = rgb_to_oklch(parse_hex(fixed))[0] - rgb_to_oklch(parse_hex(top))[0]
        stops = [shift_L(s, d) if rgb_to_oklch(parse_hex(s))[0] > rgb_to_oklch(parse_hex(fixed))[0] else s for s in stops]
        stops[0] = stops[1] = fixed
    else:
        R.info(token + " (top stop)", WHITE, top, "takeover top", "white headline")
    return stops


def pack_b(br: dict, R: Report):
    acc = br["accent"]
    css, js = [], {}
    light_bgs = [("B light page", B_LIGHT), ("B card", B_CARD)]
    dark_bgs = [("B dark page", B_DARK), ("B dark card", B_DARK_CARD)]
    blue, blue_on = R.on_accent("b.blue (capsule/typing/save/caret)", R.fit("b.blue", acc, light_bgs, UI, "ui"), TEXT)
    blue2 = R.fit("b.blue-2 (highlight text, list numbers)", acc, light_bgs, TEXT, "text")
    b2_surface, b2_on = R.on_accent("b.blue-2 badges (timeline dot, check)", blue2, TEXT)
    blue_dark = R.fit("b.blue-dark", acc, dark_bgs, TEXT, "text")
    cta, cta_on = R.on_accent("b.cta button", R.fit("b.cta", acc, [("CTA pill #EEEEEC", "#EEEEEC")], UI, "ui"), TEXT)
    dot_on = R.fit("b.dot-on (light themes)", acc, [("B light page", B_LIGHT)], UI, "ui")
    dot_on_dark = R.fit("b.dot-on (dark themes)", acc, [("B dark page", B_DARK), ("dark2/3", "#2E2E30")], UI, "ui")
    seg_on = R.fit("b.segment label", acc, [("white thumb", B_THUMB)], TEXT, "text")
    R.info("b.selection", "#0B0B0B", over(blue, .25, B_CARD), "blue@25% on card", "text on selection")
    stops = takeover(acc, R, "b.takeover")
    root = {"--rsb-blue": blue, "--rsb-blue-2": blue2, "--rsb-blue-dark": blue_dark, "--rsb-blue-cta": cta}
    css.append(":root { " + " ".join(f"{k}: {v};" for k, v in root.items()) + " }")
    for th in ("light", "paper"):
        css.append(f".theme-{th} {{ --rsb-dot-on: {dot_on}; --rsb-seg-on-ink: {seg_on}; }}")
    for th in ("dark", "dark2", "dark3"):
        css.append(f".theme-{th} {{ --rsb-dot-on: {dot_on_dark}; --rsb-seg-on-ink: {seg_on}; }}")
    pct = [0, 17, 25, 37, 50, 62, 75, 88, 100]
    grad = ", ".join(f"{s} {p}%" for s, p in zip(stops, pct))
    css.append(f".theme-blue {{ --rsb-bg: linear-gradient(180deg, {grad}); --rsb-seg-on-ink: {seg_on}; "
               f"--rsb-card-shadow: 0 20px 40px {rgba(transfer('#176ECD', '#001E50', stops[4]), .25)}; }}")
    css.append(f".rsb-sel .box {{ background: {rgba(blue, .25)}; }}")
    if blue_on != WHITE:
        css.append(f".rsb-capsule.blue, .rsb-save .on {{ color: {blue_on}; }} .rsb-typing i {{ background: {blue_on}; }}")
    if b2_on != WHITE or b2_surface != blue2:
        css.append(f".rsb-list.timeline .rsb-lrow > .dot, .rsb-check {{ background: {b2_surface}; color: {b2_on}; }}")
    if cta_on != WHITE:
        css.append(f".rsb-cta .btn {{ color: {cta_on}; }}")
    bubble, bubble_on = R.on_accent("b.cursor bubble", blue2, TEXT)
    js.update({"accent": blue2, "dotOn": dot_on, "dotOnDark": dot_on_dark, "ring": blue2, "cursor": blue2,
               "bubble": bubble, "bubbleInk": bubble_on, "grid0": blue, "segOn": seg_on, "cta": cta, "takeover": stops})
    return css, js


def pack_c(br: dict, R: Report):
    acc = br["accent"]
    css, js = [], {}
    a_dark = R.fit("c.accent-dark (highlight on dark)", acc, [("C dark", A_DARK)], LARGE, "display text")
    a_light = R.fit("c.accent-light (highlight on light)", acc, [("C light", A_LIGHT)], LARGE, "display text")
    stops = takeover(acc, R, "c.takeover")
    css.append(f":root {{ --rsc-accent-dark: {a_dark}; --rsc-accent-light: {a_light}; --rsc-blue-a: {stops[0]}; --rsc-blue-b: {stops[-1]}; }}")
    css.append(f".rsc-plate--blue {{ background: linear-gradient(180deg, {stops[0]} 0%, {stops[2]} 25%, {stops[4]} 50%, {stops[6]} 75%, {stops[8]} 100%); }}")
    css.append(f".rsc-hero-glow {{ --glow: {rgba(a_dark, .42)}; }}")
    css.append(f".rsc-chrome .rsb-dots {{ filter: drop-shadow(0 0 6px {rgba(a_dark, .45)}); }}")
    js.update({"accent": a_dark, "portalGlow": rgba(a_dark, .45)})
    return css, js


def pack_e(br: dict, R: Report):
    acc, acc2, ink = br["accent"], br.get("accent2"), br.get("ink")
    css, js = [], {}
    bgs = [("E page", E_BG), ("E card", E_CARD)]
    # gold-2 (#C9822E) is the gradient's body: gradient display text (headline accent 80/700, big numbers) ≥ 3.0
    g2 = R.fit("e.gold-2 (gradient body)", acc, bgs, LARGE, "display text")
    g1, g3 = transfer("#C9822E", "#E89E0C", g2), transfer("#C9822E", "#A8672C", g2)
    gv0 = transfer("#C9822E", "#EBA51A", g2)
    R.fit("e.gold-3 (gradient end)", g3, bgs, LARGE, "display text")
    R.info("e.gold-1 (highlight stop)", g1, E_BG, "E page", "gradient highlight (stock #E89E0C is 2.1:1)")
    kicker = R.fit("e.kicker", transfer("#C9822E", "#A26A2A", g2), bgs, TEXT, "text")
    dot = acc2 or transfer("#C9822E", "#FDC604", g2)  # rubric pill dot (stock #FDC604), decorative
    num_bg, num_on = R.on_accent("e.number badge (gold-v)", g2, TEXT, max_dl=0.10)
    rules = {"--rse-gold-1": g1, "--rse-gold-2": g2, "--rse-gold-3": g3, "--rse-kicker": kicker, "--rse-dot": dot,
             "--rse-gold": "linear-gradient(90deg, var(--rse-gold-1) 0%, var(--rse-gold-2) 55%, var(--rse-gold-3) 100%)",
             "--rse-gold-v": f"linear-gradient(180deg, {gv0} 0%, {g2} 60%, {g3} 100%)"}
    if ink:
        rules["--rse-ink"] = R.fit("e.ink (headline)", ink, bgs, TEXT, "text")
    css.append(".rse { " + " ".join(f"{k}: {v};" for k, v in rules.items()) + " }")
    if num_on != WHITE or num_bg != g2:
        css.append(f".rse .rse-num, .rse .rse-stat .ic.gold, .rse .rse-tile .up {{ color: {num_on}; }}")
        if num_bg != g2:
            css.append(f".rse .rse-num, .rse .rse-stat .ic.gold, .rse .rse-tile .up {{ background: linear-gradient(180deg, {transfer(g2, gv0, num_bg)} 0%, {num_bg} 60%, {transfer(g2, g3, num_bg)} 100%); }}")
    js.update({"accent": g2, "cell": transfer("#C9822E", "#D4902A", g2), "chart": [g1, g2, g3]})
    return css, js


def pack_f(br: dict, R: Report):
    """Style F: brand accent → the key-word colour over footage (stock yellow #FCF900) and the caption highlight;
    accent2 → the salmon insert page. Red (negative word) and black/white stay fixed."""
    acc, acc2 = br["accent"], br.get("accent2")
    css, js = [], {}
    key = R.fit("f.accent (key word over dark footage)", acc, [("F footage", "#1A1612")], LARGE, "display text")
    rules = {"--rsf-yellow": key}
    js["accent"] = key
    if acc2:
        rules["--rsf-salmon"] = acc2
        js["salmon"] = acc2
    css.append(".rsf { " + " ".join(f"{k}: {v};" for k, v in rules.items()) + " }")
    return css, js


PACKS = {"a": pack_a, "b": pack_b, "c": pack_c, "e": pack_e, "f": pack_f}
STYLE_PACKS = {"a": ["a"], "b": ["b"], "c": ["a", "b", "c"], "d": ["a"], "e": ["e"], "f": ["f"]}

# CSS font variables per pack (display/accent/caption faces that define a style's signature stay fixed)
FONT_VARS = {"a": (":root", ["--rsa-font"]), "b": (":root", ["--rsb-font"]), "c": (":root", ["--rsc-font"]),
             "e": (".rse", ["--rse-font"]), "f": (".rsf", ["--rsf-font"])}
STOCK_FONT = {"--rsa-font": '"Google Sans Flex", "Google Sans", "Onest", "Manrope", sans-serif',
              "--rsb-font": '"Inter", "SF Pro Display", system-ui, sans-serif',
              "--rsc-font": '"Inter", "SF Pro Display", system-ui, sans-serif',
              "--rse-font": '"Inter", "SF Pro Display", system-ui, sans-serif',
              "--rsf-font": '"Montserrat Alternates", "Montserrat", system-ui, sans-serif'}

# ───────────────────────────── fonts ─────────────────────────────

LANG_CHARS = {
    "ru": "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    "kk": "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" + "ӘәҒғҚқҢңӨөҰұҮүҺһІі",
    "uz": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "ʻ’" + "OʻoʻGʻgʻ",
}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _ranges(css: str) -> list[tuple[int, int]]:
    out = []
    for block in re.findall(r"unicode-range:\s*([^;]+);", css):
        for part in block.split(","):
            part = part.strip().upper().replace("U+", "")
            if "-" in part:
                a, b = part.split("-")
                out.append((int(a, 16), int(b, 16)))
            elif "?" in part:
                out.append((int(part.replace("?", "0"), 16), int(part.replace("?", "F"), 16)))
            elif part:
                out.append((int(part, 16), int(part, 16)))
    return out


def font_check(family: str, lang: str, R: Report) -> str | None:
    """Return the Google-Fonts css2 @import URL when `family` covers the reel language, else None (+ warning)."""
    fam = family.strip()
    q = urllib.parse.quote_plus(fam)
    tried = [f"family={q}:wght@300..800", f"family={q}:wght@400;500;600;700", f"family={q}:wght@400;700", f"family={q}"]
    css, url = None, None
    for t in tried:
        u = f"https://fonts.googleapis.com/css2?{t}&display=block"
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            css = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
            url = u
            break
        except Exception as e:  # 400 = family/axis not found, URLError = offline
            last = e
            continue
    if css is None:
        R.warnings.append(f"font {fam!r}: Google Fonts lookup failed ({last}); keeping the style font")
        return None
    rngs = _ranges(css)
    need = sorted(set(LANG_CHARS.get(lang, LANG_CHARS["ru"])) - set(" "))
    if not rngs:  # no unicode-range at all = a single file with everything Google has for it (rare); trust it
        return url
    missing = [ch for ch in need if not any(a <= ord(ch) <= b for a, b in rngs)]
    if missing:
        R.warnings.append(f"font {fam!r} does not cover {lang}: missing {''.join(missing)!r}; keeping the style font")
        return None
    return url


# ───────────────────────────── main ─────────────────────────────

def norm_hex(v):
    if v in (None, "", False):
        return None
    return to_hex(parse_hex(v))


LOGO_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def safe_logo(base: Path, logo: str | None, R: "Report") -> Path | None:
    """Resolve brief.brand.logo inside the work dir only (no traversal, no symlinks, images only).

    The brief comes from the client, so a value like "../../.ssh/id_rsa" must never be copied into
    the composition (which gets rendered and may be shared)."""
    if not logo:
        return None
    raw = base / logo
    try:
        resolved = raw.resolve(strict=True)
    except (FileNotFoundError, RuntimeError):
        R.warnings.append(f"logo not found: {logo} — skipped")
        return None
    if not resolved.is_relative_to(base.resolve()):
        R.warnings.append(f"logo path leaves the work dir: {logo} — skipped")
        return None
    if raw.is_symlink() or resolved.suffix.lower() not in LOGO_SUFFIXES or not resolved.is_file():
        R.warnings.append(f"logo must be a regular {'/'.join(sorted(LOGO_SUFFIXES))} file inside the work dir: {logo} — skipped")
        return None
    return resolved


def build(brand: dict, style: str, lang: str, out: Path | None, logo_src: Path | None, R: Report) -> dict | None:
    style = style.lower()
    packs = STYLE_PACKS.get(style)
    if not packs:
        raise SystemExit(f"unknown style {style!r}")
    keep = bool(brand.get("keep_style_palette"))
    acc = norm_hex(brand.get("accent"))
    br = {"accent": acc, "accent2": norm_hex(brand.get("accent2")), "ink": norm_hex(brand.get("ink"))}
    if not acc and (br["accent2"] or br["ink"]):
        br["accent"] = acc = br["accent2"] or br["ink"]
        R.warnings.append("brand.accent missing — using accent2/ink as the accent")
    colours = bool(acc) and not keep
    font = (brand.get("font") or "").strip() or None
    font_url = font_check(font, lang, R) if font else None
    if not colours and not font_url:
        return None
    css: list[str] = []
    palette: dict = {}
    if colours:
        for pk in packs:
            if pk in PACKS and pk not in palette:
                c, j = PACKS[pk](br, R)
                css.append(f"/* ── pack {pk} ── */")
                css += c
                palette[pk] = j
    head = [f"/* reels-studio brand layer — generated by scripts/brand.py (do not edit; re-run it).",
            f" * brand: {brand.get('name') or '—'} · style {style.upper()} · packs {'+'.join(packs + (['c'] if style == 'c' else []))}"
            f" · accent {acc or '—'} accent2 {br['accent2'] or '—'} ink {br['ink'] or '—'}"
            f"{' · keep_style_palette' if keep else ''} · font {font if font_url else '— (style font)'}",
            " * Load AFTER the style tokens (same specificity, later wins). */"]
    if font_url:
        head.insert(0, f'@import url("{font_url}");')
        seen = set()
        for pk in packs:
            sel, vars_ = FONT_VARS[pk]
            for v in vars_:
                if v not in seen:
                    seen.add(v)
                    css.append(f'{sel} {{ {v}: "{font}", {STOCK_FONT[v]}; }}')
    logo_rel = None
    if out and logo_src and logo_src.is_file():
        logo_rel = f"lib/brand-logo{logo_src.suffix.lower()}"
        shutil.copy2(logo_src, out / f"brand-logo{logo_src.suffix.lower()}")
    data = {"version": 1, "name": brand.get("name"), "style": style, "packs": list(palette) or packs,
            "accent": acc if colours else None, "accent2": br["accent2"] if colours else None,
            "ink": br["ink"] if colours else None, "keep_style_palette": keep,
            "font": {"family": font, "applied": bool(font_url), "url": font_url} if font else None,
            "logo": logo_rel, "palette": palette,
            "report": {"adjusted": R.adjusted, "checks": R.checks, "warnings": R.warnings}}
    if out:
        out.mkdir(parents=True, exist_ok=True)
        (out / "brand.css").write_text("\n".join(head + css) + "\n")
        js_data = {k: data[k] for k in ("version", "name", "style", "accent", "accent2", "ink", "font", "logo", "palette")}
        (out / "brand.js").write_text("/* generated by scripts/brand.py — window.RS_BRAND is read by the style libs (load before them) */\n"
                                      f"window.RS_BRAND = {json.dumps(js_data, ensure_ascii=False)};\n")
        (out / "brand.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return data


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", help="work/<slug>: reads brief.json (+ plan/scenes.json), writes composition/lib/")
    ap.add_argument("--brief", help="explicit brief.json")
    ap.add_argument("--style", help="a|b|c|d|e (default: plan/brief style)")
    ap.add_argument("--lang", help="ru|kk|uz (default: brief.lang or ru)")
    ap.add_argument("--out", help="output dir for brand.css/js/json")
    ap.add_argument("--accent"), ap.add_argument("--accent2"), ap.add_argument("--ink"), ap.add_argument("--font")
    ap.add_argument("--check", action="store_true", help="print the report, write nothing")
    a = ap.parse_args()

    brief, base = {}, Path.cwd()
    if a.work:
        base = Path(a.work).resolve()
        if (base / "brief.json").is_file():
            brief = json.loads((base / "brief.json").read_text())
        plan = base / "plan" / "scenes.json"
        style = a.style or (json.loads(plan.read_text()).get("style") if plan.is_file() else None) or brief.get("style")
        out = Path(a.out) if a.out else base / "composition" / "lib"
    else:
        if a.brief:
            bp = Path(a.brief).resolve()
            brief, base = json.loads(bp.read_text()), bp.parent
        style = a.style or brief.get("style")
        out = Path(a.out).resolve() if a.out else None
    brand = dict(brief.get("brand") or {})
    for k in ("accent", "accent2", "ink", "font"):
        if getattr(a, k):
            brand[k] = getattr(a, k)
    if not style:
        sys.exit("no style (pass --style or set brief.style)")
    lang = a.lang or brief.get("lang") or "ru"
    R = Report()
    logo_src = safe_logo(base, brand.get("logo"), R)
    data = build(brand, str(style), lang, None if a.check else out, logo_src, R)
    if data is None:
        if out and not a.check:
            for n in ("brand.css", "brand.js", "brand.json"):
                (out / n).unlink(missing_ok=True)
        print(json.dumps({"ok": True, "branded": False, "warnings": R.warnings}, ensure_ascii=False))
        for w in R.warnings:
            print(f"[brand] WARN {w}", file=sys.stderr)
        return
    for adj in R.adjusted:
        print(f"[brand] adjusted {adj['token']}: {adj['from']} → {adj['to']} "
              f"({adj['before']} → {adj['after']}:1, min {adj['min']} vs {', '.join(adj['against'])})", file=sys.stderr)
    for w in R.warnings:
        print(f"[brand] WARN {w}", file=sys.stderr)
    fails = [c for c in R.checks if not c["ok"]]
    if a.check:
        for c in R.checks:
            print(f"  {c['token']:<44} {c['fg']} on {c['bg']} ({c['bg_name']}): {c['ratio']:>5}:1"
                  f"{'' if c['min'] is None else ('  ✓ ≥' if c['ok'] else '  ✗ <') + str(c['min'])}", file=sys.stderr)
    print(json.dumps({"ok": not fails, "branded": True, "style": data["style"], "packs": data["packs"],
                      "font": data["font"], "adjusted": len(R.adjusted), "checks": len(R.checks),
                      "failed": len(fails), "warnings": R.warnings,
                      "out": None if a.check else str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
