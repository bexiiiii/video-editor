#!/usr/bin/env python3
"""reels-studio static scene linter — "no sudden appearances" (best effort, regex-level, never blocks a build).

  lint_scenes.py --work work/<slug> [--json] [--strict]

Parses every scenes/<id>/index.html <script> and flags:
  untweened      an element created by hand (RS.el / el / document.createElement / innerHTML) that never appears in a
                 tween (tl.fromTo/from/to, RS.blurIn/pop/words/type, a lib builder) → it pops in on the scene's first frame
  short_tween    a tween with duration < 0.2 s that animates opacity/autoAlpha FROM 0 (an entrance that pops);
                 colour/filter/stroke micro-tweens and hard swaps of phrases are ignored
  set_show       tl.set(…, {opacity: 1 | autoAlpha: 1 | visibility: "visible"}) — a hard pop-in
  static_t0      content builder called at local t = 0 with no entrance (only plates may: page/layer/background/chrome …)
  early_word     a word reveal time t < 0 (text visible before the scene / before its word)
  no_lib         no RSA/RSB/RSC/RSD/RSE/RSF/RSG/RSX builder call at all (hand-made scene — review its entrances)
Rules come from references/contracts.md → "Entrances" and skills/reels-scene/SKILL.md. Exit code 0 unless --strict.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LIBS = ("RSA", "RSB", "RSC", "RSD", "RSE", "RSF", "RSG", "RSX")
# (RSF / RSG builders take word times inside their specs — `RSG.layout.x(clip, spec, tl)` at 0 is normal — so the
#  static_t0 check below only covers A–E/X; RSG words are checked by the negative-time rule: `at: -…`)
# builders that draw plates/containers only (allowed static at t=0 — the assembler transition covers them)
PLATES = {"page", "layer", "background", "chrome", "headBase", "headLayer", "insertLayer", "scrim", "slot", "band",
          "beat", "footage", "lens", "ready", "header", "tabs", "window"}


def scripts_of(html: str) -> list[tuple[int, str]]:
    out = []
    for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", html, re.S | re.I):
        out.append((html[:m.start(1)].count("\n") + 1, m.group(1)))
    return out


def line_of(base: int, js: str, pos: int) -> int:
    return base + js[:pos].count("\n")


def lint_file(path: Path) -> list[dict]:
    sid = path.parent.name
    html = path.read_text(errors="ignore")
    finds: list[dict] = []

    def add(rule, msg, line=None):
        finds.append({"scene": sid, "rule": rule, "msg": msg, "line": line})

    joined = "\n".join(js for _, js in scripts_of(html))
    if not any(f"{lib}." in joined for lib in LIBS):
        add("no_lib", "no style-library builder calls — check every entrance by hand")
    for base, js in scripts_of(html):
        # 1) hand-made elements never tweened
        for m in re.finditer(r"(?:const|let|var)\s+(\w+)\s*=\s*(?:RS\.el|el|document\.createElement)\s*\(", js):
            name = m.group(1)
            rest = js[m.end():]
            used = re.search(rf"(?:tl\.(?:fromTo|from|to)|RS\.(?:blurIn|pop|words|type|numRoll))\s*\(\s*\[?[^;]*?\b{name}\b", rest)
            used = used or re.search(rf"R(?:SA|SB|SC|SD|SE|SX)\.\w+\s*\(\s*{name}\b", rest)  # used as a container
            used = used or re.search(rf"\b{name}\.appendChild|\bRS\.el\([^)]*\b{name}\s*[,)]|\bel\([^)]*,\s*{name}\b", rest)
            if not used:
                add("untweened", f"element `{name}` is created but never animated (pops in)", line_of(base, js, m.start()))
        # 2) short entrances
        for m in re.finditer(r"tl\.(fromTo|from)\s*\(", js):
            seg = js[m.end(): m.end() + 400]
            seg = seg[: seg.find(");") + 1] if ");" in seg else seg
            d = re.search(r"duration\s*:\s*([\d.]+)", seg)
            from_zero = re.search(r"(?:opacity|autoAlpha)\s*:\s*0(?:\.0+)?\s*[,}]", seg.split("}", 1)[0] + "}") if seg else None
            if d and from_zero and float(d.group(1)) < 0.2:
                add("short_tween", f"entrance tween {float(d.group(1)):.2f}s < 0.2s from opacity 0", line_of(base, js, m.start()))
        # 3) hard pop-ins
        for m in re.finditer(r"tl\.set\s*\([^;]*?\{[^}]*(?:opacity\s*:\s*1\b|autoAlpha\s*:\s*1\b|visibility\s*:\s*[\"']visible)", js):
            add("set_show", "hard pop-in via tl.set(…{opacity:1}) — use a ≥ 0.25 s eased entrance", line_of(base, js, m.start()))
        # 4) content at t=0 without entrance: builder(..., tl, 0) whose name is not a plate and that has no internal entrance
        for m in re.finditer(r"\b(R(?:SA|SB|SC|SD|SE|SX))\.(?:layout\.)?(\w+)\s*\(", js):
            name = m.group(2)
            if name in PLATES:
                continue
            seg = js[m.end(): m.end() + 600]
            depth, end = 1, 0
            for k, ch in enumerate(seg):
                depth += ch == "(" or -(ch == ")")
                if depth == 0:
                    end = k
                    break
            call = seg[:end]
            if re.search(r",\s*tl\s*\)\s*$", call) or re.search(r",\s*null\s*,\s*0\s*$", call):
                add("static_t0", f"{m.group(1)}.{name} called without a timeline/at — no entrance", line_of(base, js, m.start()))
        # 5) negative word times
        for m in re.finditer(r"\b(?:t|at)\s*:\s*(-[\d.]+)", js):
            add("early_word", f"word time {m.group(1)} < 0 (visible before the scene starts)", line_of(base, js, m.start()))
    return finds


def lint_work(work: Path) -> dict:
    files = sorted((work / "scenes").glob("*/index.html"))
    finds = []
    for f in files:
        try:
            finds += lint_file(f)
        except Exception as e:  # pragma: no cover
            finds.append({"scene": f.parent.name, "rule": "parse_error", "msg": str(e), "line": None})
    return {"files": len(files), "findings": finds}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 when anything is flagged")
    a = ap.parse_args()
    res = lint_work(Path(a.work).resolve())
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for f in res["findings"]:
            print(f"[lint_scenes] WARN {f['scene']}:{f.get('line') or '?'} {f['rule']}: {f['msg']}", file=sys.stderr)
        print(json.dumps({"files": res["files"], "warnings": len(res["findings"])}))
    sys.exit(1 if (a.strict and res["findings"]) else 0)


if __name__ == "__main__":
    main()
