---
name: reels-studio
description: Produce professional vertical reels (Instagram/TikTok/Shorts, 1080x1920) end to end with a team of parallel agents — from self-shot talking-head footage or from a script with AI voiceover — in two reference styles (A "3D Keyword" faceless 3D motion, B "iOS Keynote" Apple-UI motion), in Russian, Uzbek or Kazakh, with synced captions, generated images, sound design, music and loudness-mastered audio. Use when the user asks to make, edit or montage a reel/short/TikTok, a talking-head edit, a faceless motion explainer, or says "сделай рилс / монтаж / моушн".
---

# reels-studio — orchestrator

You are the **producer**. You own the brief, the plan and the final cut; specialised workers do the heavy lifting in parallel.
Everything is a file in `work/<slug>/` (see `references/contracts.md`). Every step is resumable: if its output exists and is valid, skip it.
`$SKILL` below means the directory containing this file. Scripts are host-agnostic: `$SKILL/scripts/run <name>.py`.

## 0 · Brief (talk to the user — never skip)
1. Run `$SKILL/scripts/run doctor.py --work work/<slug>` and read `env.json`. Tell the user in one line which providers are active and which fallbacks will be used (e.g. "Uzbek TTS via edge-tts — add ELEVENLABS_API_KEY for studio quality"). Missing ElevenLabs is fine — continue with fallbacks.
2. Collect and write `brief.json`. Ask only what is missing:
   - **style** A or B (show one line each: A = dark/light 3D objects, keywords, voice only · B = Apple-like UI cards, literal words, soft bed + UI clicks);
   - **mode**: `faceless` · `hook_cta` (talking head opens/closes) · `head_overlay` (talking head throughout + graphics);
   - **lang** ru / uz / kk; target length; topic/script; footage paths; CTA; brand.
   - **Voice (faceless only): always ask the client** — clone their voice from a sample (needs ElevenLabs) or use a stock voice. Record the answer in `brief.voice`.
3. If a script is needed and not given, draft it in the target language in the reference cadence (hook ≤ 3 s, ~140–170 wpm, one idea per 3.5–4 s, CTA at the end) and get approval before spending money.

## 1 · Voice & timing (worker: `reels-editor` or `reels-sound`)
- Footage present → spawn **editor**: `cleanup.py` → `asr.py --lang <lang>` (source timeline) → `edit_head.py` (silence/filler/retake cuts, remapped transcript, `edit/head.mp4`).
- Faceless with script → spawn **sound** for `tts.py` (writes `audio/voice.wav` + `audio/transcript.json`).
- Gate: `audio/transcript.json` has word timings, language forced, no gaps > 0.6 s left in the cut.

## 2 · Plan (you, the director)
Read `references/director.md` and the style reference (`references/style-a.md` or `references/style-b.md`), then write `plan/scenes.json`:
- Scenes tile the timeline, 3.4–4.2 s each, boundaries snapped to `transcript.pauses`; transitions sit in breath pauses.
- A: headline = 2–4 **keywords** (lowercase), caption = second fragment; one hero 3D object per scene → `assets[]` prompts.
- B: literal words, kicker + headline, one component per beat from `references/components.md`; chapters drive the page dots; theme flips per section (light/dark/blue).
- Modes: `head` scenes reuse `edit/head.mp4`; `head_overlay` puts components over the speaker in the chest band.
- Pick SFX per style policy (`references/audio-policy.md`).
Show the user a compact scene table (time · text · visual) and continue unless they object.

## 3 · Fan out (parallel workers)
Write one `scenes/<id>/brief.json` per scene (format in contracts.md), then spawn in parallel:
- **art** workers (skill `reels-art`) — one per scene that has `assets[]`; images land in `assets/img/`.
- **scene-builder** workers (skill `reels-scene`) — one per motion scene; each writes `scenes/<id>/index.html` + `result.json` using only `$SKILL/assets/<style>/lib.js` components.
- **sound** worker (skill `reels-sound`) — music bed + SFX + `mix.py` → `audio/mix.wav` (−14 LUFS / −1 dBTP).

How to spawn (same contract on both hosts — workers read their brief, write only into their `out` dir, finish with `result.json`):
- **Claude Code**: launch subagents with the Agent tool in ONE message (types `reels-art`, `reels-scene-builder`, `reels-sound`, `reels-editor`, `reels-qa` if installed, else general-purpose with the worker skill name in the prompt). Keep ≤ 8 concurrent.
- **Codex**: spawn subagents ("spawn one reels-scene worker per scenes/*/brief.json, wait for all"), roles from `codex/agents/*.toml`; or headless: `ls -d work/<slug>/scenes/*/ | xargs -P4 -I{} codex exec --sandbox workspace-write --skip-git-repo-check --ephemeral -o {}result.json '$reels-scene build {}brief.json'`.
- Images in Codex: workers may use the built-in image tool, then `$SKILL/scripts/run image.py --import --out <path> [--transparent]` to copy/cut out. Elsewhere `image.py --prompt …` picks the API chain from providers.md.
Gate: every `result.json` has `"ok": true`; re-dispatch failed scenes once with the error text.

## 4 · Assemble
`$SKILL/scripts/run assemble.py --work work/<slug>` → `composition/` (root index.html, scenes as sub-compositions, head video, mix.wav). Then `npx -y hyperframes@0.8.154 lint` inside `composition/` — fix errors before rendering.

## 5 · Render & QA (worker: `reels-qa`)
`$SKILL/scripts/run render.py --work work/<slug>` (disk guard built in) → `$SKILL/scripts/run qa.py --work work/<slug>` → spawn **qa** worker to eyeball `qa/sheet.jpg` + snapshots against `references/qa-checklist.md`.
Up to 2 fix rounds: route each issue to the worker that owns the file, re-assemble, re-render. Never ship with failing automatic checks.

## 6 · Deliver
Send `renders/final.mp4` to the user with: length, style/mode/lang, providers used (and which fallbacks), known compromises, cost estimate. Offer: caption text for the post, 2 alt hooks, cover frame.

## Hard rules
- Language is always forced from the brief (Uzbek is misdetected as Azerbaijani otherwise).
- Never print or commit API keys; read them from env / `.env` only.
- Deterministic compositions only (no Date/Math.random); text never exits by itself; words are laid out at final positions before they reveal.
- Respect style audio policy: A = voice only (no music, no SFX); B = quiet bed under graphics only (not under the hook) + soft UI clicks + sub-boom on portals.
- Ask before any paid generation larger than the plan (e.g. re-generating all images) and before deleting user files.

References: `contracts.md` · `providers.md` · `director.md` · `style-a.md` · `style-b.md` · `components.md` · `audio-policy.md` · `qa-checklist.md` · `modes.md` · `style-guide.md` · `teardowns/` (per-video forensic specs).
