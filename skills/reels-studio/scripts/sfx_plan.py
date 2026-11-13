#!/usr/bin/env python3
"""Auto-cue sound effects from plan/scenes.json (energetic profile default) -> scenes[].sfx.

Cues the director did not write (director cues are always kept and win conflicts):
  transition  every scene change (head<->motion and scene<->scene): whoosh_long / whoosh_air
              alternating, peak on the cut (t = start − 0.25); `whip` transitions -> whip at
              start − 0.12; dissolves a little softer
  riser       riser_1s ending on the CTA / punchline scene start (replaces that scene's whoosh)
  impact      impact_soft on `statement` scenes (first headline word) and on portal techniques
  pop         pop_bright on hero / object / sticker / card / logo entrances (component `at`, or
              scene start + 0.3 when a motion scene has a 3d_object asset and no component)
  tap         tap on UI interactions (cursor, button, toggle, chat, iphone…); notification on banners
  tick        tick on number rolls / counters / stats
Density guard: cues ≥ 0.6 s apart and ≤ 2 in any 3 s window (≈ 1 per 1.5 s); higher-priority
cues win (director > riser > transition > impact > notification > tap > pop > tick).
Re-running replaces the previous auto cues (marked "auto": true). First run backs the plan up to
plan/scenes.pre_sfx.json. Profile "reference" (brief.audio_profile) -> no-op unless --force.

Usage: sfx_plan.py --work work/<slug> [--force] [--freesound] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
from common import SFX_DIR, load_dotenv, log, write_json  # noqa: E402

MIN_GAP, WINDOW, MAX_IN_WINDOW = 0.6, 3.0, 2
PRIO = {"director": 10, "riser": 8, "transition": 7, "impact": 6, "notification": 5, "tap": 4, "pop": 3, "tick": 2}
UI = ("tap", "click", "cursor", "button", "toggle", "switch", "iphone", "phone", "chat", "message", "search",
      "input", "keyboard", "checkbox", "slider", "menu", "app")
NOTIFY = ("notification", "banner", "toast", "alert", "push")
NUMBER = ("counter", "count", "number", "numroll", "stat", "kpi", "percent", "price", "chart", "bar", "metric")
ENTRANCE = ("hero", "object", "sticker", "badge", "card", "image", "photo", "logo", "icon", "emoji", "3d",
            "product", "avatar", "pill", "tag")
FREESOUND_QUERIES = {"whoosh_long": "whoosh transition", "pop_bright": "pop bubble ui", "impact_soft": "soft impact hit"}


def classify(ctype: str) -> str | None:
    t = (ctype or "").lower()
    for kind, words in (("notification", NOTIFY), ("tick", NUMBER), ("tap", UI), ("pop", ENTRANCE)):
        if any(w in t for w in words):
            return kind
    return None


def is_cta(scene: dict, last: bool) -> bool:
    text = " ".join(str(scene.get(k, "")) for k in ("layout", "kind", "id", "notes")).lower()
    return bool(scene.get("punchline")) or "cta" in text or "punchline" in text or last


def propose(scenes: list[dict], duration: float) -> list[dict]:
    cues: list[dict] = []

    def add(kind, name, t, sid, gain=0.0, anchor=None, why=""):
        if -0.05 <= t <= duration - 0.15:
            cues.append({"kind": kind, "name": name, "t": round(max(0.0, t), 3), "scene": sid,
                         "gain_db": gain, "anchor": round(anchor if anchor is not None else t, 3), "why": why})

    whoosh_i = 0
    for i, sc in enumerate(scenes):
        sid, start, end = sc.get("id", f"s{i:02d}"), float(sc["start"]), float(sc["end"])
        last = i == len(scenes) - 1
        tr = (sc.get("transition_in") or {}).get("type", "cut") if i else None
        cta = i > 0 and is_cta(sc, last)
        if cta and start >= 1.2:
            add("riser", "riser_1s", start - 1.0, sid, -3.0, anchor=start, why="riser into CTA/punchline")
        if i > 0:
            prev_kind = scenes[i - 1].get("kind", "motion")
            what = f"{prev_kind}->{sc.get('kind', 'motion')} {tr}"
            if tr == "whip":
                add("transition", "whip", start - 0.12, sid, 0.0, anchor=start, why=what)
            else:
                name = ("whoosh_long", "whoosh_air")[whoosh_i % 2]
                whoosh_i += 1
                add("transition", name, start - 0.25, sid, -3.0 if tr == "dissolve" else 0.0, anchor=start, why=what)
        for tq in sc.get("techniques") or []:
            if "portal" in str(tq.get("id", "")).lower() and tq.get("at") is not None:
                add("impact", "impact_soft", float(tq["at"]), sid, -2.0, why="portal")
        if "statement" in str(sc.get("layout", "")).lower() or sc.get("statement"):
            words = (sc.get("headline") or {}).get("words") or []
            t = float(words[0]["t"]) if words and words[0].get("t") is not None else start + 0.15
            if i > 0:
                t = max(t, start + MIN_GAP)          # leave room for the transition whoosh on the cut
            add("impact", "impact_soft", t, sid, -3.0, why="statement scene")
        popped = False
        for comp in sc.get("components") or []:
            kind = classify(comp.get("type", ""))
            if not kind or comp.get("at") is None:
                continue
            at = float(comp["at"])
            if kind == "tap":
                props = comp.get("props") or {}
                taps = [v for k, v in props.items() if "tap" in k.lower() and isinstance(v, (int, float))]
                for t in taps or [at + 0.35]:
                    add("tap", "tap", float(t), sid, -2.0, why=f"UI {comp.get('type')}")
            elif kind == "notification":
                add("notification", "notification", at, sid, -3.0, why=comp.get("type"))
            elif kind == "tick":
                add("tick", "tick", at + 0.05, sid, -4.0, why=f"number roll {comp.get('type')}")
            else:
                add("pop", "pop_bright", at, sid, -1.0, why=f"entrance {comp.get('type')}")
                popped = True
        if not popped and sc.get("kind", "motion") == "motion" and \
                any(a.get("kind") == "3d_object" for a in sc.get("assets") or []):
            add("pop", "pop_bright", start + 0.3, sid, -1.0, why="hero object entrance")
    return cues


def density_filter(cues: list[dict], fixed: list[float]) -> tuple[list[dict], list[dict]]:
    accepted_t = list(fixed)
    kept, dropped = [], []
    for c in sorted(cues, key=lambda c: (-PRIO[c["kind"]], c["anchor"])):
        a = c["anchor"]
        if any(abs(a - t) < MIN_GAP for t in accepted_t):
            dropped.append(c)
            continue
        if sum(1 for t in accepted_t if abs(a - t) < WINDOW / 2) >= MAX_IN_WINDOW:   # 3 s window centred on a
            dropped.append(c)
            continue
        accepted_t.append(a)
        kept.append(c)
    return sorted(kept, key=lambda c: c["t"]), dropped


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--force", action="store_true", help="cue SFX even for the 'reference' audio profile")
    ap.add_argument("--freesound", action="store_true", help="fetch CC0 replacements (FREESOUND_API_KEY)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    load_dotenv()
    work = a.work
    plan_p = work / "plan" / "scenes.json"
    if not plan_p.is_file():
        sys.exit(f"error: {plan_p} not found")
    brief_p = work / "brief.json"
    brief = json.loads(brief_p.read_text(encoding="utf-8")) if brief_p.is_file() else {}
    profile = brief.get("audio_profile", "energetic")
    if profile == "reference" and not a.force:
        print(f"audio_profile=reference — leaving SFX to the style policy (use --force to cue anyway)")
        return
    plan = json.loads(plan_p.read_text(encoding="utf-8"))
    scenes = plan.get("scenes") or []
    if not scenes:
        sys.exit("error: plan has no scenes")
    duration = float(plan.get("duration") or scenes[-1]["end"])

    director = []
    for sc in scenes:
        sc["sfx"] = [c for c in (sc.get("sfx") or []) if not c.get("auto")]
        director += [float(c["t"]) + (1.0 if c.get("name", "").startswith("riser") else 0.0) for c in sc["sfx"]]
    kept, dropped = density_filter(propose(scenes, duration), director)

    by_id = {sc.get("id"): sc for sc in scenes}
    for c in kept:
        by_id[c["scene"]]["sfx"].append({"name": c["name"], "t": c["t"], "gain_db": c["gain_db"], "auto": True,
                                         "why": c["why"]})
    for sc in scenes:
        sc["sfx"].sort(key=lambda c: float(c["t"]))
    plan.setdefault("audio", {})["sfx_enabled"] = True

    missing = sorted({c["name"] for c in kept if not (work / "assets" / "sfx" / f"{c['name']}.wav").is_file()
                      and not (SFX_DIR / f"{c['name']}.wav").is_file()})
    for c in kept:
        print(f"  {c['t']:7.3f}s  {c['name']:13s} {c['gain_db']:+.0f} dB  {c['scene']:>5}  {c['why']}")
    print(f"{len(kept)} auto cues + {len(director)} director cues; {len(dropped)} dropped by the density guard"
          + (f"; MISSING files: {missing}" if missing else ""))
    if a.dry_run:
        return
    backup = work / "plan" / "scenes.pre_sfx.json"
    if not backup.exists():
        shutil.copy2(plan_p, backup)
    write_json(plan_p, plan)

    credits = ["bundled reels-studio SFX kit (assets/sfx) — CC0 1.0, synthesised; no attribution needed",
               "CAPTION: (not required)"]
    if a.freesound:
        from music_search import freesound_sfx
        out_dir = work / "assets" / "sfx"
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in sorted({c["name"] for c in kept} & set(FREESOUND_QUERIES)):
            cr = freesound_sfx(FREESOUND_QUERIES[name], out_dir / f"{name}.wav")
            if cr:
                credits.insert(0, f"{name}: \"{cr['title']}\" by {cr['artist']} — CC0 — {cr['source_url']}")
                log(f"[sfx_plan] {name} <- freesound \"{cr['title']}\" (CC0)")
            else:
                log(f"[sfx_plan] {name}: freesound unavailable — bundled kit sound used")
    try:
        from music_search import write_credits
        write_credits(work, "sfx", credits)
    except ImportError:
        pass
    print(f"wrote {plan_p}")


if __name__ == "__main__":
    main()
