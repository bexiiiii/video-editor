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

Timeline: scene i is mounted at scenes.json start with data-duration = the sub-composition's own root
data-duration (end-start + transition overlap) clamped to the root duration; later scenes are later in
DOM order, so they paint on top of the previous scene's overlap tail. kind "head" scenes are <video>
clips of head.mp4 at the same time range (data-media-start = start, since head.mp4 is on the final
timeline); kind "head_overlay" = head video underneath + the scene sub-composition on top (scene must
have a transparent background). Punch-ins from edit/cuts.json are hard scale sets on a non-timed wrapper
(.headcam, one per head scene, interleaved in DOM order with the scene hosts so a head clip paints
above the previous scene's overlap tail) on the main timeline at global time.
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
    ap.add_argument("--bg", default=None, help="root background colour (default by style: A/C #0B0D0D, B/D #1A1A1C, E #FCFCFC)")
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

    # ---- body
    body, tl_lines = [], []
    head_clips, scene_hosts = [], []
    for i, s in enumerate(scenes):
        sid, st, en, kind = s["id"], float(s["start"]), float(s["end"]), s.get("kind", "motion")
        if kind in ("head", "head_overlay"):
            d = min(en, duration) - st
            clip = (f'    <div id="headcam-{sid}" class="headcam">\n'
                    f'      <video id="head-{sid}" class="clip headclip" src="media/head.mp4" muted playsinline '
                    f'data-start="{f3(st)}" data-duration="{f3(d)}" data-media-start="{f3(st)}" '
                    f'data-track-index="0"></video>\n    </div>')
            head_clips.append(clip)
            body.append(clip)
        sfile = work / "scenes" / sid / "index.html"
        if not sfile.is_file():
            if kind == "head":
                continue
            if kind == "head_overlay":
                warnings.append(f"scene {sid}: head_overlay without scenes/{sid}/index.html — head only")
                continue
            sys.exit(f"missing scenes/{sid}/index.html (kind {kind})")
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
        sd = min(sd, duration - st)
        track = 2 if kind == "head_overlay" else 1 + (len(scene_hosts) % 2)
        scene_hosts.append(
            f'    <div id="scene-{sid}" class="scene-host" data-composition-id="{html.escape(inner_id)}" '
            f'data-composition-src="scenes/{sid}/index.html" data-start="{f3(st)}" data-duration="{f3(sd)}" '
            f'data-track-index="{track + (2 if kind != "head_overlay" else 0)}" data-width="{W}" data-height="{H}"></div>')
        body.append(scene_hosts[-1])

    if head_clips:
        z = 1.0
        for p in punches:
            sc = float(p.get("scale", 1.0))
            if abs(sc - z) > 1e-4 or not tl_lines:
                tl_lines.append(f'      tl.set(".headcam", {{ scale: {sc} }}, {f3(float(p["start"]))});')
                z = sc
        if not tl_lines:
            tl_lines.append('      tl.set(".headcam", { scale: 1 }, 0);')
    if (media / "mix.wav").is_file():
        body.append(f'    <audio id="mix" src="media/mix.wav" data-start="0" data-duration="{f3(duration)}" '
                    f'data-track-index="9" data-volume="1"></audio>')

    bg = a.bg or ("#0B0D0D" if style in ("a", "c") else "#FCFCFC" if style == "e" else "#1A1A1C")
    script_tags = "\n".join(f'    <script src="{s}"></script>' for s in scripts)
    doc = f"""<!doctype html>
<html lang="{html.escape(brief.get('lang', 'ru'))}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{html.escape(brief.get('slug', work.name))}</title>
{script_tags}
    {' '.join(head_links)}
    <style>
      html, body {{ margin: 0; background: {bg}; }}
      #main {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: {bg}; }}
      .headcam {{ position: absolute; inset: 0; transform-origin: {anchor.get('x', 0.5) * 100:.0f}% {anchor.get('y', 0.38) * 100:.0f}%; }}
      .headclip {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .scene-host {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-fps="{fps}" data-duration="{f3(duration)}">
{chr(10).join(body)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl_lines)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (comp / "index.html").write_text(doc)
    report = {"ok": True, "composition": str(comp), "duration": duration, "style": style,
              "scenes": len(scene_hosts), "head_clips": len(head_clips), "punch_sets": len(tl_lines),
              "brand": brand_res, "warnings": warnings}

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
                     | {"warnings": len(warnings), "lint_exit": report.get("lint", {}).get("exit")}))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
