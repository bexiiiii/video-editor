#!/usr/bin/env python3
"""Reel history — remembers what each delivered reel used, so the next one looks different.

  history.py --record --work work/<slug>          append style/layouts/components/techniques/brand of a finished reel
  history.py --show [--brand "Link HR"] [--n 5]   print the last N reels (optionally for one brand) as JSON
  history.py --avoid --brand "Link HR" [--n 3]    techniques + layout sequence used in the last N reels of the brand

Stored in ~/.reels-studio/history.json (override with REELS_STUDIO_HOME). Never stores keys or media.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

HOME = Path(os.environ.get("REELS_STUDIO_HOME", Path.home() / ".reels-studio"))
FILE = HOME / "history.json"


def load() -> list[dict]:
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def summarise(work: Path) -> dict:
    """Pull the variety-relevant facts out of a finished work dir."""
    brief = json.loads((work / "brief.json").read_text(encoding="utf-8"))
    plan = json.loads((work / "plan" / "scenes.json").read_text(encoding="utf-8"))
    scenes = plan.get("scenes", [])
    return {
        "slug": brief.get("slug", work.name),
        "brand": (brief.get("brand") or {}).get("name") or (brief.get("cta") or {}).get("name"),
        "style": brief.get("style"), "mode": brief.get("mode"), "lang": brief.get("lang"),
        "recorded": time.strftime("%Y-%m-%d %H:%M"),
        "layouts": [s.get("layout") for s in scenes],
        "components": sorted({c.get("type") for s in scenes for c in s.get("components", []) if c.get("type")}),
        "techniques": sorted({t.get("id") for s in scenes for t in s.get("techniques", []) if t.get("id")}),
        "themes": [s.get("theme") for s in scenes],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--record", action="store_true")
    g.add_argument("--show", action="store_true")
    g.add_argument("--avoid", action="store_true")
    ap.add_argument("--work")
    ap.add_argument("--brand")
    ap.add_argument("--n", type=int, default=None)
    a = ap.parse_args()

    hist = load()
    if a.record:
        if not a.work:
            sys.exit("--record needs --work")
        entry = summarise(Path(a.work).resolve())
        hist = [h for h in hist if h.get("slug") != entry["slug"]] + [entry]
        HOME.mkdir(parents=True, exist_ok=True)
        FILE.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({"recorded": entry["slug"], "total": len(hist)}, ensure_ascii=False))
        return

    sel = [h for h in hist if not a.brand or (h.get("brand") or "").lower() == a.brand.lower()]
    if a.show:
        print(json.dumps(sel[-(a.n or 5):], ensure_ascii=False, indent=1))
        return
    recent = sel[-(a.n or 3):]
    print(json.dumps({
        "brand": a.brand, "reels": [h["slug"] for h in recent],
        "avoid_techniques": sorted({t for h in recent for t in h.get("techniques", [])}),
        "recent_styles": [h.get("style") for h in recent],
        "recent_layout_openers": [(h.get("layouts") or [None])[0] for h in recent],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
