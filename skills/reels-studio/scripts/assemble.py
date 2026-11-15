#!/usr/bin/env python3
"""reels-studio assembler (step 4): work/<slug>/ → work/<slug>/composition/ (a HyperFrames project).

  assemble.py --work work/<slug> [--no-lint] [--gsap cdn|local]

Layout produced (mirrors the work dir, so the same relative paths work in both places):
  composition/index.html            root, data-composition-id="main", 1080×1920, duration = scenes.json
  composition/lib/runtime.js        $SKILL/assets/shared/runtime.js
  composition/lib/tokens-<s>.css    $SKILL/assets/style-<s>/tokens.css   (+ lib/tokens.css alias)
  composition/lib/<s>.js            $SKILL/assets/style-<s>/lib.js       (+ lib/lib.js alias)
  composition/lib/style-<s>/…       the whole style pack (fonts, textures …)
  composition/lib/techniques/…      $SKILL/assets/techniques/* (head-umar.css/js = RSX, loaded after the packs)
  composition/lib/brand.{css,js,json}  scripts/brand.py output when brief.brand has colours/font (references/branding.md):
                                    brand.css linked right AFTER the style tokens, brand.js loaded BEFORE runtime/libs
  composition/lib/gsap.min.js       pinned GSAP (cached in ~/.cache/reels-studio; CDN tag if offline)
  composition/scenes/<id>/…         scenes/<id>/index.html (+ any local files), mounted as sub-compositions
  composition/assets/img/…          assets/img/*
  composition/media/head.mp4        edit/head.mp4 without its audio track (the mix carries the voice)
  composition/media/mix.wav         audio/mix.wav — the single audio track

Path rules verified against hyperframes@0.8.154 (compositionAssembly / rewriteAssetPath): inside a
sub-composition, a relative URL that starts with "../" is resolved against the scene file's directory
(scenes/<id>/../../lib/x.js → lib/x.js); any other relative URL is kept as written — i.e. resolved
from the PROJECT ROOT — unless a file with that name exists next to the scene file. So scenes may use
either `lib/runtime.js` / `assets/img/x.png` (root-relative, the contract) or `../../lib/runtime.js`.

Timeline: every scene is a LAYER inside its own untimed shell div (.rs-shell, explicit z-index): kind "head" = a
<video> clip of head.mp4 (data-media-start = clip start, head.mp4 is on the final timeline, so the footage keeps
playing through any overlap), kind "motion" = the scene sub-composition host, kind "head_overlay" = both (scene on
top, transparent background). Punch-ins from edit/cuts.json are hard scale sets on the inner .headcam wrapper.

Transitions (references/contracts.md → "Transitions"): every boundary gets a real transition on the MAIN timeline,
never a hard switch. Overlap 0.35–0.6 s (scene.transition_in.dur, default 0.45). The OUTGOING layer's shell sits on top
and animates out (type from the incoming scene's transition_in.type, default per style: A/D blur-drift, B/C dissolve,
E blur-swap; also whip / portal / zoom / lum) while the incoming scene's own entrance plays underneath; an incoming
head clip starts ov/2 early and settles from scale 1.06 + blur. Host/clip windows are extended to cover the overlap.
head ↔ head_overlay = same footage: only the outgoing overlay fades. transition_in {"type":"cut"} = hook hard cut;
{"owner":"scene"} = the incoming scene draws its own transition (it then paints above the previous tail).
Style F ("Kinetic Talking Head") is a hard-cut style: its default boundary is "cut" (no warning), its caption track is
small Montserrat Alternates phrases shown whole (hard swap, digits / brief.captions_highlight in yellow), and
edit/cuts.json punch_ins may carry "drift" (slow linear zoom inside a segment).

Captions (talking-head modes, brief.captions auto|all|off): scripts/captions.py turns audio/transcript.json into
1–4-word phrases; they are rendered as ONE root-level layer (#rs-captions, z 900) with per-word reveals ending at
onset − 0.03 s, plus composition/captions.json for qa.py. window.RS_CAPTIONS tells the libs (RSD moves its
lower-zone headline up and drops the duplicate grey caption). After writing, scripts/lint_scenes.py runs (warnings).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
HF = "hyperframes@0.8.154"
GSAP_VER = "3.14.2"
GSAP_CDN = f"https://cdn.jsdelivr.net/npm/gsap@{GSAP_VER}/dist/gsap.min.js"
CACHE = Path(os.environ.get("REELS_STUDIO_CACHE", Path.home() / ".cache" / "reels-studio"))
W, H, FPS = 1080, 1920, 30
sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402  (scripts/captions.py — caption track planner)

# ---- cross-layer transitions (head ↔ motion, motion ↔ motion without a scene-owned transition)
OV_MIN, OV_MAX, OV_DEFAULT = 0.35, 0.6, 0.45
TX_DEFAULT = {"a": "blur-drift", "d": "blur-drift", "b": "dissolve", "c": "dissolve", "e": "blur-swap", "f": "cut"}
HARD_CUT_STYLES = ("f",)   # styles whose default boundary is a hard cut (no transition drawn, no warning)
TX_ALIAS = {"blur": "blur-drift", "drift": "blur-drift", "blurdrift": "blur-drift", "crossfade": "dissolve",
            "fade": "dissolve", "light-orb": "portal", "orb": "portal", "swap": "blur-swap", "blurswap": "blur-swap",
            "datamosh": "dissolve", "rgb-ghost": "dissolve", "rgbghost": "dissolve", "glitch": "dissolve",
            "zoom-through": "zoom", "luminance": "lum"}
# type → (from-vars JS, to-vars JS without duration, duration factor × overlap, ease) for the OUTGOING shell(s)
TX_OUT = {
    "blur-drift": ('{ y: 0, opacity: 1, filter: "blur(0px)" }', 'y: 200, opacity: 0, filter: "blur(24px)"', 1.0, "power1.in"),
    "whip":       ('{ y: 0, opacity: 1 }', 'y: -340, opacity: 0', 0.5, "power2.in"),
    "dissolve":   ('{ scale: 1, opacity: 1, filter: "blur(0px)" }', 'scale: 0.96, opacity: 0, filter: "blur(8px)"', 1.0, "power2.inOut"),
    "portal":     ('{ scale: 1, opacity: 1, filter: "blur(0px)" }', 'scale: 1.1, opacity: 0, filter: "blur(14px)"', 1.0, "power2.in"),
    "blur-swap":  ('{ scale: 1, opacity: 1, filter: "blur(0px)" }', 'scale: 1.02, opacity: 0, filter: "blur(18px)"', 0.85, "power1.inOut"),
    "zoom":       ('{ scale: 1, opacity: 1, filter: "blur(0px)" }', 'scale: 1.25, opacity: 0, filter: "blur(24px)"', 1.0, "power2.in"),
    "lum":        ('{ y: 0, opacity: 1, filter: "blur(0px)" }', 'y: -50, opacity: 0, filter: "blur(12px)"', 1.0, "power1.in"),
}
TX_TYPES = set(TX_OUT)
# caption typography per style (A/D Google-Sans 600 lowercase white + soft shadow · B/C karaoke grey→white · E uppercase grey)
_SH = "0 2px 14px rgba(0,0,0,.62), 0 0 3px rgba(0,0,0,.4)"
CAP_STYLE = {
    "a": {"font": "var(--rsa-font, 'Google Sans Flex', 'Google Sans', sans-serif)", "weight": 600, "size": 58, "ls": "-0.01em",
          "color": "#FFFFFF", "case": "lowercase", "shadow": _SH, "scrim": 0.42, "karaoke": False},
    "b": {"font": "var(--rsb-font, -apple-system, 'SF Pro Display', sans-serif)", "weight": 500, "size": 62, "ls": "-0.04em",
          "color": "#FFFFFF", "from": "#9A9A9A", "case": "none", "shadow": _SH, "scrim": 0.42, "karaoke": True},
    "e": {"font": "var(--rse-font, Inter, sans-serif)", "weight": 600, "size": 48, "ls": "0.01em",
          "color": "#D2D2D2", "case": "uppercase", "shadow": _SH, "scrim": 0.48, "karaoke": False},
}
CAP_STYLE["d"] = dict(CAP_STYLE["a"], scrim=0.30)   # D already has its own lower scrim
# F: small centred phrases (x-height 31 ≈ 56 px), white, highlight yellow, no scrim, whole phrase on the first word
CAP_STYLE["f"] = {"font": "var(--rsf-font, 'Montserrat Alternates', Montserrat, sans-serif)", "weight": 800, "size": 56,
                  "ls": "-0.03em", "color": "#FCFCFC", "case": "lowercase", "shadow": "0 2px 10px rgba(0,0,0,.45)",
                  "scrim": 0.0, "karaoke": False, "phrase": True, "hl": "#FCF900"}
CAP_STYLE["c"] = CAP_STYLE["b"]


def log(msg: str) -> None:
    print(f"[assemble] {msg}", file=sys.stderr)


def find_npx() -> str:
    """npx from PATH if node ≥ 22, else the newest nvm install."""
    def ver(node: Path) -> int:
        try:
            out = subprocess.run([str(node), "-v"], capture_output=True, text=True, timeout=10).stdout
            return int(out.strip().lstrip("v").split(".")[0])
        except Exception:
            return 0
    cands = []
    w = shutil.which("npx")
    if w:
        cands.append(Path(w))
    nvm = Path.home() / ".nvm" / "versions" / "node"
    if nvm.is_dir():
        cands += sorted(nvm.glob("v*/bin/npx"), key=lambda p: [int(x) for x in re.findall(r"\d+", p.parent.parent.name)],
                        reverse=True)
    for c in cands:
        node = c.parent / "node"
        if node.exists() and ver(node) >= 22:
            return str(c)
    if w and ver(Path(shutil.which("node") or "node")) >= 22:
        return w
    if cands:
        log("WARN Node.js >= 22 not found; trying " + str(cands[0]))
        return str(cands[0])
    raise SystemExit("npx not found — install Node.js ≥ 22")


def node_env(npx: str) -> dict:
    env = dict(os.environ)
    env["PATH"] = str(Path(npx).parent) + os.pathsep + env.get("PATH", "")
    env.setdefault("HYPERFRAMES_NO_TELEMETRY", "1")
    return env


def copy_tree(src: Path, dst: Path, skip=()) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.iterdir():
        if p.name in skip or p.name.startswith("."):
            continue
        if p.is_dir():
            copy_tree(p, dst / p.name, skip)
        else:
            shutil.copy2(p, dst / p.name)


def root_attrs(html_text: str, comp_id: str) -> dict:
    """Attributes of the element carrying data-composition-id="<comp_id>" (first root if not found)."""
    tags = re.findall(r"<[a-zA-Z][^>]*data-composition-id=[\"'][^\"']+[\"'][^>]*>", html_text)
    pick = next((t for t in tags if re.search(rf"data-composition-id=[\"']{re.escape(comp_id)}[\"']", t)), None)
    pick = pick or (tags[0] if tags else "")
    return dict(re.findall(r"([\w-]+)=[\"']([^\"']*)[\"']", pick))


def gsap_local(lib: Path, mode: str) -> str:
    """Return the <script src> to use for GSAP (local copy when possible)."""
    if mode == "cdn":
        return GSAP_CDN
    cached = CACHE / f"gsap-{GSAP_VER}.min.js"
    if not cached.is_file():
        try:
            CACHE.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(GSAP_CDN, headers={"User-Agent": "reels-studio"})
            data = urllib.request.urlopen(req, timeout=30).read()
            if b"gsap" not in data[:2000].lower():
                raise RuntimeError("unexpected GSAP payload")
            cached.write_bytes(data)
        except Exception as e:
            log(f"GSAP download failed ({e}); using CDN tag")
            return GSAP_CDN
    shutil.copy2(cached, lib / "gsap.min.js")
    return "lib/gsap.min.js"


def f3(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".") if x % 1 else str(int(x))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True, help="work/<slug> directory")
    ap.add_argument("--no-lint", action="store_true", help="skip `npx hyperframes lint`")
    ap.add_argument("--gsap", choices=["local", "cdn"], default="local", help="vendor GSAP locally (default) or CDN")
    ap.add_argument("--bg", default=None, help="root background colour (default by style: A/C #0B0D0D, B/D #1A1A1C, E #FCFCFC, F #000000)")
    a = ap.parse_args()

    work = Path(a.work).resolve()
    plan_p = work / "plan" / "scenes.json"
    if not plan_p.is_file():
        sys.exit(f"missing {plan_p}")
    plan = json.loads(plan_p.read_text())
    brief = json.loads((work / "brief.json").read_text()) if (work / "brief.json").is_file() else {}
    style = str(plan.get("style") or brief.get("style") or "A").lower()
    scenes = sorted(plan.get("scenes", []), key=lambda s: float(s["start"]))
    if not scenes:
        sys.exit("plan/scenes.json has no scenes")
    duration = float(plan.get("duration") or scenes[-1]["end"])
    fps = int(plan.get("fps", FPS))
    warnings: list[str] = []

    # tiling check
    t = 0.0
    for s in scenes:
        if abs(float(s["start"]) - t) > 0.02:
            warnings.append(f"scene {s['id']} starts at {s['start']} but previous ends at {t:.3f} (gap/overlap)")
        t = float(s["end"])
    if abs(t - duration) > 0.05:
        warnings.append(f"last scene ends at {t:.3f}, plan duration is {duration:.3f}")

    comp = work / "composition"
    if comp.exists():
        for sub in ("scenes", "lib", "assets", "media"):
            shutil.rmtree(comp / sub, ignore_errors=True)
    lib = comp / "lib"
    lib.mkdir(parents=True, exist_ok=True)

    # ---- libraries
    rt = SKILL / "assets" / "shared" / "runtime.js"
    if rt.is_file():
        shutil.copy2(rt, lib / "runtime.js")
    else:
        warnings.append("assets/shared/runtime.js missing")
    # style "c" (Keynote 3D) is built on the A and B packs: copy + load a → b → c
    # style "d" (Talking Head × 3D Keyword = Style A over the head) is built on the A pack: copy + load a → d
    # style "e" (Data News) is self-contained: pack e only (default branch below)
    # style "f" (Kinetic Talking Head) is self-contained as well: pack f only
    packs = {"c": ["a", "b", "c"], "d": ["a", "d"]}.get(style, [style])
    # technique pack assets/techniques/head-umar.{css,js} (global RSX) is always copied + loaded after the style
    # packs; it is inert unless a scene calls RSX. RSX depends on RSB, so when a scene uses it and the style does
    # not already load pack b, b is appended to the packs.
    uses_rsx = any("RSX." in (work / "scenes" / s["id"] / "index.html").read_text(errors="ignore")
                   for s in scenes if (work / "scenes" / s["id"] / "index.html").is_file())
    if uses_rsx and "b" not in packs:
        packs = packs + ["b"]
    head_links = []
    for pk in packs:
        sdir = SKILL / "assets" / f"style-{pk}"
        if sdir.is_dir() and any(sdir.iterdir()):
            copy_tree(sdir, lib / f"style-{pk}", skip=("demo", "examples", "README.md"))
        for src, names in (("tokens.css", [f"tokens-{pk}.css"] + (["tokens.css"] if pk == style else [])),
                           ("lib.js", [f"{pk}.js"] + (["lib.js"] if pk == style else []))):
            if (sdir / src).is_file():
                for n in names:
                    shutil.copy2(sdir / src, lib / n)
            else:
                warnings.append(f"style pack file missing: assets/style-{pk}/{src}")
    gsap_src = gsap_local(lib, a.gsap)
    head_links += [f'<link rel="stylesheet" href="lib/tokens-{pk}.css" />' for pk in packs if (lib / f"tokens-{pk}.css").is_file()]
    # ---- brand layer (brief.brand → lib/brand.css + lib/brand.js); no colours/font → nothing written, style pristine
    brand_res = None
    if (brief.get("brand") or {}):
        p = subprocess.run([sys.executable, str(SKILL / "scripts" / "brand.py"), "--work", str(work), "--style", style,
                            "--out", str(lib)], capture_output=True, text=True)
        if p.stderr.strip():
            print(p.stderr.strip(), file=sys.stderr)
        try:
            brand_res = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            brand_res = {"ok": False, "error": (p.stdout + p.stderr)[-800:]}
        if p.returncode != 0 or not brand_res.get("ok", False):
            warnings.append(f"brand.py: {brand_res}")
        warnings += [f"brand: {w}" for w in brand_res.get("warnings", [])]
    if (lib / "brand.css").is_file():
        head_links.append('<link rel="stylesheet" href="lib/brand.css" />')
    scripts = [gsap_src] + [p for p in (["lib/brand.js"] if (lib / "brand.css").is_file() else []) + ["lib/runtime.js"]
                            + [f"lib/{pk}.js" for pk in packs] if (comp / p).is_file()]
    tech = SKILL / "assets" / "techniques"
    if tech.is_dir():
        copy_tree(tech, lib / "techniques", skip=("README.md",))
        for name in ("head-umar",):
            if (lib / "techniques" / f"{name}.css").is_file():
                head_links.append(f'<link rel="stylesheet" href="lib/techniques/{name}.css" />')
            if (lib / "techniques" / f"{name}.js").is_file():
                scripts.append(f"lib/techniques/{name}.js")

    # ---- media
    media = comp / "media"
    media.mkdir(exist_ok=True)
    needs_head = any(s.get("kind") in ("head", "head_overlay") for s in scenes)
    head_src = work / "edit" / "head.mp4"
    if needs_head:
        if not head_src.is_file():
            sys.exit("scenes use kind head/head_overlay but edit/head.mp4 is missing (run edit_head.py)")
        p = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(head_src), "-map", "0:v:0", "-c:v", "copy",
                            "-an", "-movflags", "+faststart", str(media / "head.mp4")], capture_output=True, text=True)
        if p.returncode != 0:
            sys.exit(f"ffmpeg failed muting head.mp4: {p.stderr[-800:]}")
    mix = work / "audio" / "mix.wav"
    if mix.is_file():
        shutil.copy2(mix, media / "mix.wav")
    else:
        warnings.append("audio/mix.wav missing — composition will be silent")
    img = work / "assets" / "img"
    if img.is_dir():
        copy_tree(img, comp / "assets" / "img", skip=())
        for j in (comp / "assets" / "img").glob("*.json"):
            j.unlink()

    # ---- punch-ins
    punches = []
    cuts_p = work / "edit" / "cuts.json"
    anchor = {"x": 0.5, "y": 0.38}
    if needs_head and cuts_p.is_file():
        cuts = json.loads(cuts_p.read_text())
        punches = cuts.get("punch_ins", [])
        anchor = cuts.get("punch_anchor", anchor)

    # ---- layers: one per scene (head clip and/or scene host), each inside its own untimed shell
    layers = []
    for s in scenes:
        sid, st, en, kind = s["id"], float(s["start"]), float(s["end"]), s.get("kind", "motion")
        L = {"sid": sid, "st": st, "en": en, "kind": kind, "head": kind in ("head", "head_overlay"),
             "scene": s, "host": None, "sd": en - st, "lead": st, "tail": en}
        sfile = work / "scenes" / sid / "index.html"
        if not sfile.is_file():
            if kind == "head_overlay":
                warnings.append(f"scene {sid}: head_overlay without scenes/{sid}/index.html — head only")
            elif kind != "head":
                sys.exit(f"missing scenes/{sid}/index.html (kind {kind})")
        else:
            copy_tree(sfile.parent, comp / "scenes" / sid, skip=("brief.json", "result.json"))
            text = sfile.read_text()
            attrs = root_attrs(text, sid)
            inner_id = attrs.get("data-composition-id", sid)
            if inner_id != sid:
                warnings.append(f"scene {sid}: inner data-composition-id is {inner_id!r}; host uses it to match")
            if "<template" not in text:
                warnings.append(f"scene {sid}: no <template> wrapper — head <style>/<script> may be dropped")
            if f'__timelines["{inner_id}"]' not in text and f"__timelines['{inner_id}']" not in text:
                warnings.append(f"scene {sid}: no window.__timelines[\"{inner_id}\"] registration found")
            try:
                sd = float(attrs.get("data-duration", "nan"))
                if sd != sd:
                    raise ValueError
            except ValueError:
                res = sfile.parent / "result.json"
                sd = float(json.loads(res.read_text()).get("duration", en - st)) if res.is_file() else en - st
            if sd + 1e-3 < en - st:
                warnings.append(f"scene {sid}: duration {sd:.3f} shorter than its slot {en - st:.3f} — host slot extended to the scene range (last frame holds)")
                sd = en - st
            L["host"], L["sd"] = inner_id, sd
        layers.append(L)

    # ---- transitions at every boundary (references/contracts.md → "Transitions"): the OUTGOING layer animates out
    # on top while the incoming scene's own entrance plays underneath; head clips keep playing through the overlap.
    tx_default = TX_DEFAULT.get(style, "dissolve")
    bounds, tx_lines, flashes = [], [], []
    for i in range(len(layers) - 1):
        P, N = layers[i], layers[i + 1]
        T = N["st"]
        tin = N["scene"].get("transition_in") or {}
        ttype = str(tin.get("type") or "").lower().replace("_", "-")
        ttype = TX_ALIAS.get(ttype, ttype)
        ov = min(OV_MAX, max(OV_MIN, float(tin.get("dur") or OV_DEFAULT)))
        if ttype in ("", "none") and style in HARD_CUT_STYLES and tin.get("owner") != "scene":
            ttype = "cut"
        if ttype == "cut":
            mode = "cut"
            if T > 3.5 and style not in HARD_CUT_STYLES:
                warnings.append(f"{P['sid']}→{N['sid']}: hard cut at {T:.2f}s — only allowed at the hook")
        elif tin.get("owner") == "scene":
            mode = "scene"  # the incoming scene draws its own transition over the previous scene's tail
        elif P["head"] and N["head"]:
            mode = "continuous"  # same footage on both sides: only the outgoing overlay fades
        else:
            mode = "xfade"
        if ttype not in TX_TYPES and mode != "cut":
            if ttype not in ("", "none"):
                warnings.append(f"{N['sid']}: transition_in.type {ttype!r} not supported across layers — using {tx_default}")
            ttype = tx_default
        lead_a = ov * 0.5 if (mode == "xfade" and N["head"]) else 0.0  # a head clip can start early (timeline-aligned)
        ws, we = max(0.0, T - lead_a), T - lead_a + ov
        b = {"i": i, "from": P["sid"], "to": N["sid"], "t": round(T, 3), "mode": mode, "type": ttype,
             "ov": round(ov, 3), "start": round(ws, 3), "end": round(we, 3)}
        bounds.append(b)
        if mode == "xfade":
            P["tail"] = max(P["tail"], we)
            if N["head"]:
                N["lead"] = min(N["lead"], ws)
        elif mode == "continuous" and P["host"]:
            P["tail"] = max(P["tail"], T + 0.3)

    # z-order: outgoing above incoming (assembler transitions); incoming above outgoing when the scene owns it
    z = [0] * len(layers)
    for i in range(len(layers) - 2, -1, -1):
        z[i] = z[i + 1] - 4 if bounds[i]["mode"] == "scene" else z[i + 1] + 4
    zmin = min(z) if z else 0
    z = [10 + v - zmin for v in z]

    body, tl_lines, head_clips, scene_hosts = [], [], [], []
    for i, L in enumerate(layers):
        sid, st = L["sid"], L["st"]
        if L["head"]:
            cs, ce = max(0.0, L["lead"]), min(duration, L["tail"])
            clip = (f'    <div id="shell-h-{sid}" class="rs-shell" style="z-index:{z[i]}">\n'
                    f'      <div id="headcam-{sid}" class="headcam">\n'
                    f'        <video id="head-{sid}" class="clip headclip" src="media/head.mp4" muted playsinline '
                    f'data-start="{f3(cs)}" data-duration="{f3(ce - cs)}" data-media-start="{f3(cs)}" '
                    f'data-track-index="0"></video>\n      </div>\n    </div>')
            head_clips.append(clip)
            body.append(clip)
        if L["host"]:
            sd = min(max(L["sd"], L["tail"] - st), duration - st)
            track = 2 if L["kind"] == "head_overlay" else 1 + (len(scene_hosts) % 2)
            host = (f'    <div id="shell-s-{sid}" class="rs-shell" style="z-index:{z[i] + 1}">\n'
                    f'      <div id="scene-{sid}" class="scene-host" data-composition-id="{html.escape(L["host"])}" '
                    f'data-composition-src="scenes/{sid}/index.html" data-start="{f3(st)}" data-duration="{f3(sd)}" '
                    f'data-track-index="{track + (2 if L["kind"] != "head_overlay" else 0)}" data-width="{W}" data-height="{H}"></div>\n    </div>')
            scene_hosts.append(host)
            body.append(host)

    def shells(L):
        return ([f"#shell-h-{L['sid']}"] if L["head"] else []) + ([f"#shell-s-{L['sid']}"] if L["host"] else [])

    mb = 0
    for b in bounds:
        P, N = layers[b["i"]], layers[b["i"] + 1]
        ws, ov, ty = b["start"], b["ov"], b["type"]
        if b["mode"] == "continuous" and P["host"]:
            t0 = round(b["t"] - 0.1, 3)
            tx_lines.append(f'      tl.fromTo("#shell-s-{P["sid"]}", {{ opacity: 1, y: 0, filter: "blur(0px)" }}, '
                            f'{{ opacity: 0, y: 24, filter: "blur(10px)", duration: 0.38, ease: "power2.in", immediateRender: false }}, {t0});')
            continue
        if b["mode"] != "xfade":
            continue
        out = ", ".join(f'"{x}"' for x in shells(P))
        if not out:
            continue
        frm, to, dur, ease = TX_OUT[ty]
        dur = round(ov * dur, 3)
        tx_lines.append(f"      tl.fromTo([{out}], {frm}, {{ {to}, duration: {dur}, ease: \"{ease}\", immediateRender: false }}, {ws});")
        if ty == "whip":
            mb += 1
            fid = f"rs-mb-{mb}"
            flashes.append(f'<svg width="0" height="0" style="position:absolute"><filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%">'
                           f'<feGaussianBlur id="{fid}-g" stdDeviation="0 0"/></filter></svg>')
            tx_lines.append(f'      tl.set([{out}], {{ filter: "url(#{fid})" }}, {ws});')
            tx_lines.append(f'      tl.fromTo("#{fid}-g", {{ attr: {{ stdDeviation: "0 0" }} }}, {{ attr: {{ stdDeviation: "0 34" }}, duration: {dur}, ease: "power2.in", immediateRender: false }}, {ws});')
            tx_lines.append(f'      tl.set([{out}], {{ filter: "none" }}, {round(ws + dur, 3)});')
            inc = ", ".join(f'"{x}"' for x in shells(N))
            if inc:
                tx_lines.append(f'      tl.fromTo([{inc}], {{ y: 260 }}, {{ y: 0, duration: {round(ov + 0.1, 3)}, ease: "expo.out", immediateRender: false }}, {ws});')
        if ty == "portal":
            fl = f"rs-flash-{b['i']}"
            flashes.append(f'<div id="{fl}" class="rs-flash"></div>')
            k = round(ov * 0.55, 3)
            tx_lines.append(f'      tl.fromTo("#{fl}", {{ opacity: 0, scale: 0.2 }}, {{ opacity: 0.95, scale: 1.6, duration: {k}, ease: "expo.in", immediateRender: false }}, {ws});')
            tx_lines.append(f'      tl.fromTo("#{fl}", {{ opacity: 0.95 }}, {{ opacity: 0, duration: 0.42, ease: "power2.out", immediateRender: false }}, {round(ws + k, 3)});')
        if N["head"] and ty != "whip":
            # incoming head: settles from a soft zoom-blur while the outgoing layer clears (video keeps playing)
            tx_lines.append(f'      tl.fromTo("#shell-h-{N["sid"]}", {{ scale: 1.06, filter: "blur(10px)" }}, '
                            f'{{ scale: 1, filter: "blur(0px)", duration: {round(ov + 0.15, 3)}, ease: "power3.out", immediateRender: false }}, {ws});')

    if head_clips:
        # a punch-in must never snap inside a head ↔ motion transition: move it out of the overlap window
        # (before it when the head comes in, after it when the head goes out)
        def punch_time(pt: float) -> float:
            for bd in bounds:
                if bd["mode"] != "xfade" or not (bd["start"] - 0.05 <= pt <= bd["end"] + 0.05):
                    continue
                if layers[bd["i"] + 1]["head"]:
                    return max(0.0, bd["start"] - 0.034)
                if layers[bd["i"]]["head"]:
                    return bd["end"] + 0.034
            return pt
        z0 = 1.0
        for p in punches:
            sc = float(p.get("scale", 1.0))
            t0 = round(punch_time(float(p["start"])), 3)
            if abs(sc - z0) > 1e-4 or not tl_lines or p.get("drift"):
                tl_lines.append(f'      tl.set(".headcam", {{ scale: {sc} }}, {f3(t0)});')
                z0 = sc
            if p.get("drift"):  # slow linear zoom inside the segment (edit_head.py --drift, style F option)
                d_ = max(0.1, float(p.get("end", t0 + 3)) - t0 - 0.04)
                z1 = round(sc * (1 + float(p["drift"])), 4)
                tl_lines.append(f'      tl.fromTo(".headcam", {{ scale: {sc} }}, {{ scale: {z1}, duration: {f3(round(d_, 3))}, ease: "none", immediateRender: false }}, {f3(t0)});')
                z0 = z1
        if not tl_lines:
            tl_lines.append('      tl.set(".headcam", { scale: 1 }, 0);')
    n_punch = len(tl_lines)

    # ---- caption track (talking-head modes): root-level layer from audio/transcript.json, exact word sync
    capres = captions.plan_captions(work, plan, brief)
    cap_html, cap_css, cap_lines = "", "", []
    if capres and capres.get("error"):
        warnings.append(f"captions: {capres['error']}")
    elif capres:
        cs_ = CAP_STYLE.get(style, CAP_STYLE["a"])
        y = capres["y"]
        cap_css = (f".rs-cap {{ position: absolute; left: 60px; right: 60px; top: {y - 60}px; height: 120px; z-index: 900; pointer-events: none; }}\n"
                   f"      .rs-cap .ph {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; white-space: nowrap; opacity: 0; "
                   f"font-family: {cs_['font']}; font-weight: {cs_['weight']}; font-size: {cs_['size']}px; letter-spacing: {cs_['ls']}; "
                   f"color: {cs_['color']}; text-transform: {cs_['case']}; text-shadow: {cs_['shadow']}; line-height: 1; }}\n"
                   f"      .rs-cap .cw {{ display: inline-block; margin: 0 0.14em; }}\n"
                   f"      .rs-capscrim {{ position: absolute; left: 0; right: 0; top: {y - 330}px; bottom: 0; z-index: 899; opacity: 0; pointer-events: none; "
                   f"background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,{cs_['scrim']}) 55%, rgba(0,0,0,{cs_['scrim']}) 100%); }}")
        rows = []
        for k, p in enumerate(capres["phrases"]):
            ws_ = "".join(f'<span class="cw" id="cw-{k}-{j}"'
                          + (f' style="color:{cs_["hl"]}"' if w.get("hl") and cs_.get("hl") else "")
                          + f'>{html.escape(w["w"])}</span>' for j, w in enumerate(p["words"]))
            rows.append(f'      <div class="ph" id="cph-{k}">{ws_}</div>')
            cap_lines.append(f'      tl.set("#cph-{k}", {{ opacity: 1 }}, {p["show"]});')
            if p.get("swap"):
                cap_lines.append(f'      tl.set("#cph-{k}", {{ opacity: 0 }}, {p["hide"]});')
            else:  # end of a caption run (pause / range end): soft fade with the layer transition
                cap_lines.append(f'      tl.fromTo("#cph-{k}", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.2, ease: "power1.in", immediateRender: false }}, {p["hide"]});')
            for j, w in enumerate(p["words"]):
                if cs_.get("phrase"):
                    continue  # style F: the whole phrase appears at once (hard swap), no per-word reveal
                if cs_["karaoke"]:
                    cap_lines.append(f'      tl.fromTo("#cw-{k}-{j}", {{ color: "{cs_["from"]}" }}, {{ color: "{cs_["color"]}", duration: {w["dur"]}, ease: "power2.out", immediateRender: false }}, {w["t0"]});')
                else:
                    cap_lines.append(f'      tl.fromTo("#cw-{k}-{j}", {{ opacity: 0, y: 10, filter: "blur(6px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: {w["dur"]}, ease: "power2.out" }}, {w["t0"]});')
        for s_, e_ in capres["ranges"]:
            cap_lines.append(f'      tl.fromTo(".rs-capscrim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power1.out", immediateRender: false }}, {round(max(0, s_ - 0.15), 3)});')
            cap_lines.append(f'      tl.fromTo(".rs-capscrim", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.3, ease: "power1.in", immediateRender: false }}, {round(e_ - 0.15, 3)});')
        cap_html = ('    <div class="rs-capscrim"></div>\n    <div id="rs-captions" class="rs-cap">\n'
                    + "\n".join(rows) + "\n    </div>")
        (comp / "captions.json").write_text(json.dumps(capres, ensure_ascii=False, indent=1))
        body.append(cap_html)
        cov = capres["coverage"]
        if cov["pct_in_ranges"] is not None and cov["pct_in_ranges"] < 98:
            warnings.append(f"captions cover {cov['pct_in_ranges']}% of the words in caption ranges (< 98%)")
    for f in flashes:
        body.append("    " + f)
    if (media / "mix.wav").is_file():
        body.append(f'    <audio id="mix" src="media/mix.wav" data-start="0" data-duration="{f3(duration)}" '
                    f'data-track-index="9" data-volume="1"></audio>')

    bg = a.bg or ("#0B0D0D" if style in ("a", "c") else "#FCFCFC" if style == "e" else "#000000" if style == "f" else "#1A1A1C")
    script_tags = "\n".join(f'    <script src="{s}"></script>' for s in scripts)
    rs_caps = json.dumps({"on": bool(capres and not capres.get("error")), "y": (capres or {}).get("y"),
                          "ranges": (capres or {}).get("ranges", [])})
    doc = f"""<!doctype html>
<html lang="{html.escape(brief.get('lang', 'ru'))}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{html.escape(brief.get('slug', work.name))}</title>
    <script>window.RS_CAPTIONS = {rs_caps};</script>
{script_tags}
    {' '.join(head_links)}
    <style>
      html, body {{ margin: 0; background: {bg}; }}
      #main {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: {bg}; }}
      .rs-shell {{ position: absolute; inset: 0; transform-origin: 50% 46%; }}
      .headcam {{ position: absolute; inset: 0; transform-origin: {anchor.get('x', 0.5) * 100:.0f}% {anchor.get('y', 0.38) * 100:.0f}%; }}
      .headclip {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .scene-host {{ position: absolute; inset: 0; }}
      .rs-flash {{ position: absolute; left: 140px; top: 560px; width: 800px; height: 800px; border-radius: 50%; z-index: 950; opacity: 0; pointer-events: none;
        background: radial-gradient(circle, #FFFFFF 0%, #FFFFFF 38%, rgba(255,255,255,.55) 62%, rgba(255,255,255,0) 72%); }}
      {cap_css}
    </style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-fps="{fps}" data-duration="{f3(duration)}">
{chr(10).join(body)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl_lines + tx_lines + cap_lines)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (comp / "index.html").write_text(doc)
    report = {"ok": True, "composition": str(comp), "duration": duration, "style": style,
              "scenes": len(scene_hosts), "head_clips": len(head_clips), "punch_sets": n_punch,
              "transitions": bounds, "captions": (capres or {}).get("coverage"),
              "brand": brand_res, "warnings": warnings}
    # static scene linter (no sudden appearances) — warnings only, never blocks the build
    try:
        import lint_scenes
        lint = lint_scenes.lint_work(work)
        report["scene_lint"] = lint
        for f in lint["findings"]:
            log(f"LINT {f['scene']}:{f.get('line', '?')} {f['rule']}: {f['msg']}")
    except Exception as e:  # pragma: no cover - best effort
        log(f"WARN lint_scenes failed: {e}")

    if not a.no_lint:
        npx = find_npx()
        p = subprocess.run([npx, "-y", HF, "lint"], cwd=comp, capture_output=True, text=True, env=node_env(npx))
        out = (p.stdout + p.stderr).strip()
        report["lint"] = {"exit": p.returncode, "output": out[-4000:]}
        if p.returncode != 0:
            report["ok"] = False
        print(out[-3000:], file=sys.stderr)
    for w in warnings:
        log("WARN " + w)
    (comp / "assemble.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(json.dumps({k: report[k] for k in ("ok", "composition", "duration", "scenes", "head_clips")}
                     | {"transitions": len([b for b in bounds if b["mode"] in ("xfade", "continuous")]),
                        "caption_pct": ((capres or {}).get("coverage") or {}).get("pct_in_ranges"),
                        "scene_lint": len(report.get("scene_lint", {}).get("findings", [])),
                        "warnings": len(warnings), "lint_exit": report.get("lint", {}).get("exit")}))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
