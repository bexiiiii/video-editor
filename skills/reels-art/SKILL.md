---
name: reels-art
description: Worker for reels-studio. Generates the images (glossy 3D hero objects, Apple-emoji-style icons, props) listed in a scene brief's assets[] and saves transparent PNGs to work/<slug>/assets/img/. Use only when the reels-studio orchestrator dispatches an art brief.
---

# reels-art — image worker

`$STUDIO` = sibling `reels-studio` skill dir. Provider chain: `$STUDIO/references/providers.md`.

For each `assets[]` item in your brief:
1. Build the prompt: item prompt + style preset (A: glossy inflated 3D, soft studio light, centered, plain background, no text · B: Apple 3D emoji style, centered, no text). Never put real people, trademarks presented as genuine UI, or text in images.
2. Generate:
   - **Codex**: use your built-in image generation tool (portrait/square as requested, plain flat background), then `$STUDIO/scripts/run image.py --import --out assets/img/<id>.png [--transparent]` (copies the newest file from `$CODEX_HOME/generated_images` and cuts out the background).
   - **Elsewhere**: `$STUDIO/scripts/run image.py --prompt "<prompt>" --style <a|b> --size <WxH> [--transparent] --out assets/img/<id>.png` (OpenAI → Gemini → Fluent Emoji 3D fallback).
3. Check the PNG: correct subject, transparent edges clean (no halo), subject fills ~80 % of the bbox, no text/watermark. Regenerate once if bad.
4. Write `scenes/<scene_id>/art_result.json` `{ "ok": true, "files": [...], "provider": "...", "warnings": [] }`.
Ask the orchestrator (not the user) before generating more than 2 images per asset.
