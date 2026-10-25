---
name: reels-scene
description: Worker for reels-studio. Builds ONE scene of a reel as a HyperFrames sub-composition from work/<slug>/scenes/<id>/brief.json using the style component library (A "3D Keyword" or B "iOS Keynote"). Use only when the reels-studio orchestrator dispatches a scene brief.
---

# reels-scene — scene builder worker

`$STUDIO` = the sibling `reels-studio` skill directory (`../reels-studio` from this file).

1. Read your brief `scenes/<id>/brief.json`, then `$STUDIO/references/contracts.md` (sub-composition contract), `$STUDIO/references/components.md` (your style section only) and the style reference `$STUDIO/references/style-<a|b>.md`. Open the teardown that inspired the component you use when you need exact numbers.
2. Copy `$STUDIO/assets/shared/scene-template.html` to `scenes/<id>/index.html` and fill it in:
   - the root is wrapped in `<template>`; put `<style>`/`<script>` **inside** the template (outside it they are dropped);
   - the same id for the template root `data-composition-id`, and the `window.__timelines["<id>"]` key; `data-duration` = (end − start) + the next scene's transition overlap;
   - GSAP, `RS`, `RSA`/`RSB` and the style tokens are already loaded by the root composition — do not load them again;
   - one paused timeline, built after `await RSB.ready()` / `RSA.ready()` (fonts), and registered in `window.__timelines` only AFTER the build; local time 0 = scene start, so subtract `scene.start` from every word/component time;
   - start from the scene's `layout` via `RSB.layout.<id>` / `RSC.layout.<id>` (style A: compose it from `RSA` builders) (spacing per `$STUDIO/references/layouts.md`: block centred at y 860–940, fills ≥ 45 % of the live area, nothing in the top 12 % / bottom 18 % except chrome), then
   - build everything through `RSA.*` / `RSB.*` / `RSC.*` builders (see `components.md`) — no ad-hoc styling unless a component is missing (then add a minimal, token-based element and say so in `result.json.warnings`);
   - images: root-relative `assets/img/<asset_id>.png` (never `../`); unique element ids prefixed with the scene id;
   - style B: draw `RSB.chrome` with this scene's chapter as `active` and the scene theme.
3. Never draw people/faces; never leave an empty container; emoji only as small UI accents, never as the hero.
   Rules: deterministic (no Date/Math.random → `RS.rand(seed)`), seek-safe `fromTo` tweens, words laid out at final positions, text never exits on its own, safe zones (top 8 %, bottom 15 %).
4. Self-check: no `../` paths, no CSS transform on an element you also tween, no `Math.random`/`Date`; the orchestrator lints the assembled project and sends you any errors.
5. Write `scenes/<id>/result.json` `{ "ok": true, "files": ["index.html"], "duration": …, "warnings": [] }`. Never touch files outside `scenes/<id>/`.
