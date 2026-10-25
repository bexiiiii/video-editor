---
name: reels-art
description: Worker for reels-studio. Generates the images (glossy 3D hero objects, Apple-emoji-style icons, props) listed in a scene brief's assets[] and saves transparent PNGs to work/<slug>/assets/img/. Use only when the reels-studio orchestrator dispatches an art brief.
---

# reels-art — image worker

`$STUDIO` = sibling `reels-studio` skill dir. Provider chain: `$STUDIO/references/providers.md`.

For each `assets[]` item in your brief:
1. Build the prompt: item prompt + style preset (A: glossy inflated 3D, soft studio light, centered, plain background, no text · B: Apple 3D emoji style, centered, no text). Never put real people, trademarks presented as genuine UI, or text in images.
2. Generate:
   - **Codex**: use your built-in image generation tool (portrait/square as requested, plain flat background — never fetch stock or existing images), note the exact file path it returns, then `$STUDIO/scripts/run image.py --import <that exact path> --out assets/img/<id>.png [--transparent]` (cuts out the background). Always pass the path: art workers run in parallel, so "newest file" could be another worker's image.
   - **Elsewhere**: `$STUDIO/scripts/run image.py --prompt "<prompt>" --style <a|b> --size <WxH> [--transparent] --out assets/img/<id>.png` (OpenAI → Gemini → Fluent Emoji 3D fallback).
3. Check the PNG: correct subject, transparent edges clean (no halo), subject fills ~80 % of the bbox, no text/watermark. Regenerate once if bad.
4. Write `scenes/<scene_id>/art_result.json` `{ "ok": true, "files": [...], "provider": "...", "warnings": [] }`.
Ask the orchestrator (not the user) before generating more than 2 images per asset.
