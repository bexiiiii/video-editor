---
name: reels-studio
description: Produce professional vertical reels (Instagram/TikTok/Shorts, 1080x1920) end to end with a team of parallel agents — from self-shot talking-head footage or from a script with AI voiceover — in five styles (A "3D Keyword", B "iOS Keynote", C "Keynote 3D", D "3D Keyword Talking Head", E "Data News") tuned to the client's niche and brand colours, in Russian, Uzbek or Kazakh, with synced captions, generated images, music found online, sound design and loudness-mastered audio. Use when the user asks to make, edit or montage a reel/short/TikTok, a talking-head edit, a faceless motion explainer, or says "сделай рилс / монтаж / моушн".
---

# reels-studio — orchestrator

You are the **producer**. You own the brief, the plan and the final cut; specialised workers do the heavy lifting in parallel.
Everything is a file in `work/<slug>/` (see `references/contracts.md`). Every step is resumable: if its output exists and is valid, skip it.
`$SKILL` below means the directory containing this file. Scripts are host-agnostic: `$SKILL/scripts/run <name>.py`.

## 0 · Brief (talk to the user — never skip)
1. Run `$SKILL/scripts/run doctor.py --work work/<slug>` and read `env.json`. Tell the user in one line which providers are active and which fallbacks will be used (e.g. "Uzbek TTS via edge-tts — add ELEVENLABS_API_KEY for studio quality"). Missing ElevenLabs is fine — continue with fallbacks.
   **ElevenLabs connector:** if your own tool list has the ElevenLabs connector (tools ending in `creative_generate_speech` / `creative_transcribe_audio` / `creative_generate_image`), it is the preferred provider for TTS, ASR, voice design and images — but **ask the client first** (it spends their credits): show what would run and the `estimate_only` price, record the answer in `brief.providers.elevenlabs_connector`. Only you (the orchestrator) call connector tools; workers get the downloaded files. Full procedure: `references/connector-elevenlabs.md`.
2. Collect and write `brief.json`. Ask only what is missing, in this order:
   - **language — the very first question:** «На каком языке делаем видео? русский / oʻzbekcha / қазақша». It sets the voiceover, captions, on-screen text, ASR language and the language of the CTA button; talk to the client in the language they write in. Even if the topic or script hints at a language, confirm it. Write `brief.lang` (ru|uz|kk) before anything else;
   - **niche — second:** «Чем вы занимаетесь / какая ниша?» Detect it from the client's message with `assets/niches.json` (`match` keywords) and ask to confirm, e.g. «Похоже, ниша — стоматология. Верно?». Load the preset (`references/niches.md`): it ranks the styles, gives art direction for images, music mood, favoured techniques/layouts, typical materials, copy tone, hooks and compliance notes. Unknown niche → `default`;
   - **brand — third:** logo file, brand colours (hex or a screenshot of the site/Instagram — pick the colours from it and confirm), font if they have one. Brand colours always win over the niche palette; no colours → niche `palette`. Write `brief.brand` and run `$SKILL/scripts/make_brand_previews.sh work/<slug>` so the next question shows the styles **in the client's colours** (`references/branding.md`);
   - **style — next, with pictures.** Show the client the branded preview strips `work/<slug>/previews/style-*.jpg` (fallback: `$SKILL/assets/previews/style-{a,b,c,d,e}.jpg`), **recommended styles for their niche first** with the preset's one-line reason (4 real frames from our rendered demos each): attach/open the images if the host can (Claude Code desktop: send the files; Codex: open or print the paths), then list one line each and ask which one — A "3D Keyword" (dark/light, big 3D objects, keyword headlines, voice only) · B "iOS Keynote" (Apple-like UI cards, literal words, soft bed + UI clicks) · C "Keynote 3D" (B chrome/UI scenes alternating with A-style 3D scenes) · D "3D Keyword Talking Head" (Style A applied over the client's talking-head footage: A keyword headlines above/below the face, A 3D objects and cards beside the speaker, full-screen A inserts between head segments, voice only — needs footage). · E "Data News" (white editorial news page: channel header + chapter tabs, kicker + headline with gold accent words, news cover / post / data cards with gold count-ups and bars, literal uppercase captions under them, soft low bed, no SFX). Full descriptions: `assets/previews/README.md`, specs `references/style-{a,b,c,d,e}.md`. If the client already named a style, still show its preview once to confirm;
   - **mode**: `faceless` · `hook_cta` (talking head opens/closes) · `head_overlay` (talking head throughout + graphics);
   - **talking-head footage (modes `hook_cta`, `head_overlay`, or style D):** right after the mode, ask the client to send the video they filmed — «Пришлите видео, которое вы сняли (можно несколько дублей)». If they haven't filmed yet, send the shooting checklist from `references/modes.md` (vertical 9:16, face in the upper third, close mic, pause between thoughts, hook first) and **wait** — do not write a script, do not generate TTS. When it arrives: save to `input/`, check orientation, resolution ≥ 1080 wide, duration, audio level/noise, that the face is visible; report problems and ask for a re-take only if they make the edit impossible. From here the reel is **footage-first**: the client's speech is the timeline — editor cuts it (step 1), the director plans scenes on top of the cut transcript, no script/TTS;
   - audio: default `brief.audio_profile = "energetic"` (music + SFX); set `"reference"` only if the client asks for the voice-only / purist reference sound;
   - target length (for footage-first reels this comes from the cut, not a target); topic/script; footage paths; CTA.
   - **CTA identity: always ask the client** for the name shown at the end and the Instagram handle (e.g. "Link HR" / "@linkhr"), an optional subtitle line ("Маркетинг | Продажи"), an avatar photo (`input/avatar.jpg`; if none, use the brand logo, never a drawn face), the real follower count if the CTA shows a profile card (never invent numbers), and the button text in the reel language ("Подписаться" / "Obuna bo'ling" / "Жазылу"). Never reuse names or handles from the reference videos.
   - **Voice (faceless only): always ask the client** — clone their voice from a sample (needs ElevenLabs) or use a stock voice. Record the answer in `brief.voice`.
3. If a script is needed and not given, draft it in the target language in the reference cadence (hook ≤ 3 s, ~140–170 wpm, one idea per 3.5–4 s, CTA at the end) and get approval before spending money.

## 1 · Voice & timing (worker: `reels-editor` or `reels-sound`)
- Footage present (always for head modes / style D) → spawn **editor**: `cleanup.py` → `asr.py --lang <lang>` (source timeline) → `edit_head.py` (silence/filler/retake cuts, remapped transcript, `edit/head.mp4`).
- Faceless with script → spawn **sound** for `tts.py` (writes `audio/voice.wav` + `audio/transcript.json`).
- Gate: `audio/transcript.json` has word timings from forced-language ASR (Scribe v2 / whisper `large-v3` — `small` is test-only), no gaps > 0.6 s left in the cut.

## 2 · Plan (you, the director)
Read `references/director.md` and the style reference (`references/style-a.md` or `references/style-b.md`), then write `plan/scenes.json`:
- Scenes tile the timeline, 3.4–4.2 s each, boundaries snapped to `transcript.pauses`; transitions sit in breath pauses.
- A: headline = 2–4 **keywords** (lowercase), caption = second fragment; one hero 3D object per scene → `assets[]` prompts.
- B: literal words, kicker + headline, one component per beat from `references/components.md`; chapters drive the page dots; theme flips per section (light/dark/blue).
- Modes: `head` scenes reuse `edit/head.mp4`; `head_overlay` puts components over the speaker in the chest band.
- Pick SFX per style policy (`references/audio-policy.md`).
- Add 2–4 **techniques** from `references/techniques.md` that match the script (portal, jump zoom, iPhone proof, paper section, karaoke, chest widget…), skipping what this brand used in its last 3 reels: `$SKILL/scripts/run history.py --avoid --brand "<brand>"`.
Show the user a compact scene table (time · text · visual · technique) and continue unless they object.

## 2b · Materials (ask the client — read `references/materials.md`)
From the plan, list every real asset the reel needs — screenshots, screen recordings, logos, photos/B-roll, stats screenshots, footage, avatar, voice sample — with exact specs and the scene it serves, write `plan/materials.json`, and ask the client in ONE short numbered message (≤ 6 items, required/optional). Also ask up front at the brief stage if the topic obviously needs them (an app demo → screenshots/recording). Wait for the answer; save files to `input/`; missing items fall back to graphics and are listed in the final report. Never invent real metrics or a real company's UI.

## 3 · Fan out (parallel workers)
Write one `scenes/<id>/brief.json` per scene (format in contracts.md), then spawn in parallel:
- **art** workers (skill `reels-art`) — one per scene that has `assets[]`; images land in `assets/img/`.
- **scene-builder** workers (skill `reels-scene`) — one per motion scene; each writes `scenes/<id>/index.html` + `result.json` using only `$SKILL/assets/<style>/lib.js` components.
- **sound** worker (skill `reels-sound`) — `music.py` (client track → internet search `music_search.py` → generators; top-3 in `audio/music_candidates.json`) + `sfx_plan.py` (auto SFX cues) + `mix.py` → `audio/mix.wav` (−14 LUFS / −1 dBTP, voice king, music 9–12 dB under it) + `qa_audio.py`.

How to spawn (same contract on both hosts — workers read their brief, write only into their `out` dir, finish with `result.json`):
- **Claude Code**: launch subagents with the Agent tool in ONE message (types `reels-art`, `reels-scene-builder`, `reels-sound`, `reels-editor`, `reels-qa` if installed, else general-purpose with the worker skill name in the prompt). Keep ≤ 8 concurrent.
- **Codex**: spawn subagents ("spawn one reels-scene worker per scenes/*/brief.json, wait for all"), roles from `codex/agents/*.toml`; or headless: `ls -d work/<slug>/scenes/*/ | xargs -P4 -I{} codex exec --sandbox workspace-write --skip-git-repo-check --ephemeral -o {}result.json '$reels-scene build {}brief.json'`.
- Images in Codex: workers may use the built-in image tool, then `$SKILL/scripts/run image.py --import --out <path> [--transparent]` to copy/cut out. Elsewhere `image.py --prompt …` picks the API chain from providers.md.
Gate: every `result.json` has `"ok": true`; re-dispatch failed scenes once with the error text.

## 4 · Assemble
`$SKILL/scripts/run assemble.py --work work/<slug>` → `composition/` (root index.html, scenes as sub-compositions, head video, mix.wav). The assembler also draws a transition at every scene boundary (head ↔ motion included), adds the literal caption track in talking-head modes (`brief.captions`) and runs `scripts/lint_scenes.py` (no sudden appearances) — route its warnings to the scene builders. Then `npx -y hyperframes@0.8.154 lint` inside `composition/` — fix errors before rendering.

## 5 · Render & QA (worker: `reels-qa`)
`$SKILL/scripts/run render.py --work work/<slug>` (disk guard built in) → `$SKILL/scripts/run qa.py --work work/<slug>` → spawn **qa** worker to eyeball `qa/sheet.jpg` + snapshots against `references/qa-checklist.md`.
Up to 2 fix rounds: route each issue to the worker that owns the file, re-assemble, re-render. Never ship with failing automatic checks.

## 6 · Deliver
Record the reel so the next one differs: `$SKILL/scripts/run history.py --record --work work/<slug>`.
Send `renders/final.mp4` to the user with: length, style/mode/lang, providers used (and which fallbacks), the music track (title · artist · licence; offer the 2 other candidates), known compromises, cost estimate. Offer: caption text for the post — **it must include the CAPTION line(s) from `work/<slug>/CREDITS.txt`** (CC BY attribution) — 2 alt hooks, cover frame.

## Hard rules
- Language is always forced from the brief (Uzbek is misdetected as Azerbaijani otherwise).
- Never print or commit API keys; read them from env / `.env` only.
- Deterministic compositions only (no Date/Math.random); text never exits by itself; words are laid out at final positions before they reveal.
- Audio profile (`brief.audio_profile`, `references/audio-policy.md`): default `energetic` for every style — audible music + SFX, voice always king; `reference` (A/D voice only, B bed under graphics only…) only when the client asks for the purist look. Footage voice always goes through `cleanup.py`.
- Ask before any paid generation larger than the plan (e.g. re-generating all images) and before deleting user files.

References: `contracts.md` · `providers.md` · `director.md` · `materials.md` · `layouts.md` · `techniques.md` · `connector-elevenlabs.md` · `style-a.md` · `style-b.md` · `components.md` · `audio-policy.md` · `qa-checklist.md` · `modes.md` · `style-guide.md` · `teardowns/` (per-video forensic specs).
