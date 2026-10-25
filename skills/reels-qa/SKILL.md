---
name: reels-qa
description: Worker for reels-studio. Reviews a rendered reel against the automatic QA report and the style checklist (frames, typography, sync, audio policy) and returns a prioritised fix list routed to the responsible worker. Use only when the reels-studio orchestrator dispatches QA.
---

# reels-qa — quality worker

`$STUDIO` = sibling `reels-studio` skill dir.

1. Run `$STUDIO/scripts/run qa.py --work work/<slug>` if `qa/report.json` is missing or stale.
2. Read `qa/report.json`, view `qa/sheet.jpg` and the per-scene snapshots, and compare against `$STUDIO/references/qa-checklist.md` and the style reference (`style-a.md` / `style-b.md`); open teardown reference frames when unsure.
3. Output `qa/review.json`: `{ "pass": bool, "issues": [{ "severity": "blocker|major|minor", "scene": "s04", "owner": "scene|art|sound|editor|director", "problem": "…", "fix": "…" }] }`. Be specific (px, seconds, hex). Max 12 issues, most severe first. No praise.
