---
name: reels-editor
description: Worker for reels-studio. Edits self-shot talking-head footage — voice cleanup, forced-language word-level transcription (ru/uz/kk), silence/filler/retake removal, punch-in plan — producing edit/head.mp4, audio/voice.wav and audio/transcript.json on the final timeline. Use only when the reels-studio orchestrator dispatches footage.
---

# reels-editor — talking-head worker

`$STUDIO` = sibling `reels-studio` skill dir.

1. `$STUDIO/scripts/run providers/cleanup.py input/<take> --out audio/voice_src.wav` (add `--isolator` only if the audio is noisy and ElevenLabs is available).
2. `$STUDIO/scripts/run providers/asr.py audio/voice_src.wav --lang <brief.lang> --out audio/transcript.source.json` — language is always forced.
3. `$STUDIO/scripts/run edit_head.py --work work/<slug>` → `edit/cuts.json`, `edit/head.mp4`, `audio/voice.wav`, remapped `audio/transcript.json`.
4. Review the cut list: no word clipped (pads ≥ 0.12 s), retakes keep the last clean take, hook is the first sentence. Spot-check 3 cut points by extracting 1 s audio around them.
5. Write `edit/editor_result.json` `{ "ok": true, "kept_sec": …, "removed_sec": …, "warnings": [] }`.
