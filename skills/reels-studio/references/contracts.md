# Contracts — files every agent reads/writes

All state lives in `work/<slug>/`. Every step is resumable: if its output exists and is valid, skip it.
Frame: 1080×1920, 30 fps. Times are seconds (float, 3 decimals) on the **final** timeline unless noted.
Renderer: HyperFrames, pinned `npx -y hyperframes@0.8.154`. `$SKILL` = this skill's directory.

```
work/<slug>/
  brief.json                 # step 0  (orchestrator + user)
  env.json                   # step 0  scripts/doctor.py → available providers
  input/                     # user footage / script.txt / logo
  audio/voice.wav            # step 1  clean voice on the FINAL timeline, 48 kHz mono (edit_head keeps voice.source.wav)
  audio/transcript.json      # step 1  word timings on the FINAL timeline
  edit/cuts.json             # step 1a footage only: kept source ranges
  edit/head.mp4              # step 1a footage only: cut talking head, 1080×1920 30fps, audio = voice.wav
  plan/scenes.json           # step 2  director
  plan/materials.json        # step 2b assets requested from the client (materials.md)
  scenes/<id>/brief.json     # step 3  slice of scenes.json for one worker
  scenes/<id>/index.html     # step 3b sub-composition (scene-builder)
  scenes/<id>/result.json    # step 3b {ok, duration, notes, warnings[]}
  assets/img/<asset_id>.png  # step 3a art (transparent PNG where requested)
  audio/music.wav audio/sfx.wav   # step 3c sound
  audio/mix.wav              # step 4  voice+music+sfx, −14 LUFS / −1 dBTP
  composition/               # step 4  assembled HyperFrames project (index.html + lib/ + scenes/ + media)
  renders/final.mp4          # step 5
  qa/report.json             # step 5
```

## brief.json
```json
{
  "slug": "linkhr-ru-01",
  "style": "A",                       // "A" 3D Keyword | "B" iOS Keynote | "C" Keynote 3D | "D" Talking Head Editorial (needs footage) — chosen from assets/previews
  "mode": "faceless",                 // "faceless" | "hook_cta" | "head_overlay"
  "lang": "ru",                       // "ru" | "uz" | "kk"
  "target_sec": 45,
  "topic": "…", "script": "…|null",   // script required for faceless+TTS
  "footage": ["input/take1.mov"],     // required for hook_cta / head_overlay, optional for faceless (user VO)
  "voice": {"source": "footage|tts_clone|tts_stock", "voice_id": null},   // ASK THE CLIENT clone vs stock
  "cta": {"type": "bookmark|follow|profile|save|none",       // ASK THE CLIENT name + handle — never copy from references
          "name": "Link HR", "handle": "@linkhr", "subtitle": "Учёт рабочего времени|null",
          "avatar": "input/avatar.jpg|null", "followers": 12400, "posts": 86, "button": "Подписаться"},
  "brand": {"name": "…", "accent": "#…|null", "logo": "input/logo.png|null"},
  "chrome": {"series": "…", "topic": "…"}   // style B breadcrumb text
}
```

## audio/transcript.json
```json
{"lang": "ru", "source": "elevenlabs-scribe|openai-whisper|faster-whisper|tts-timestamps",
 "duration": 41.2,
 "words": [{"w": "кто", "s": 0.12, "e": 0.31}],
 "sentences": [{"text": "…", "s": 0.12, "e": 2.40, "w0": 0, "w1": 5}],
 "pauses": [{"s": 2.40, "e": 2.81}]}
```

## plan/scenes.json (director output — the single source of truth)
```json
{
  "style": "B", "fps": 30, "width": 1080, "height": 1920, "duration": 41.2,
  "chapters": [{"title": "…", "start": 0}],                 // style B page dots
  "scenes": [
    {
      "id": "s03", "start": 7.84, "end": 11.92,
      "kind": "motion",                                     // "motion" | "head" | "head_overlay"
      "layout": "hero",                                     // layouts.md catalogue — no repeats back-to-back
      "theme": "light",                                     // A: dark|light|accent:<name>   B: light|dark|blue
      "transition_in": {"type": "dissolve", "dur": 0.5},    // per-style list, see style refs
      "kicker": {"text": "…", "at": 7.9},
      "headline": {"text": "…", "highlight": ["word"],      // A: keywords (paraphrase) · B: literal words
                   "words": [{"w": "…", "t": 8.02}]},       // t = reveal time (from transcript)
      "caption": {"text": "…", "at": 9.1},
      "components": [{"type": "card", "at": 7.95, "props": {}}],
      "assets": [{"id": "s03_rocket", "kind": "3d_object|icon|photo|screenshot", "prompt": "…",
                  "transparent": true, "size": "1024x1024"}],
      "sfx": [{"name": "click", "t": 8.40}],
      "notes": "…"
    }
  ],
  "audio": {"music": {"enabled": true, "mood": "…", "bpm": 100, "duck_db": -11, "start": 5.0},
            "sfx_enabled": true}
}
```
Rules: scenes tile the timeline with no gaps; `start`/`end` snap to `transcript.pauses`; `kind:"head"` scenes show `edit/head.mp4` at the same time range.

## scenes/<id>/brief.json (what a scene-builder or art worker gets)
`{ "scene": {...one scene...}, "style": "B", "theme_tokens": "$SKILL/assets/style-b/tokens.css", "lib": "$SKILL/assets/style-b/lib.js", "chapter_index": 2, "chapter_count": 4, "assets_dir": "work/<slug>/assets/img", "out": "work/<slug>/scenes/s03/" }`

## Sub-composition contract (scene-builder output)
- `scenes/<id>/index.html` is a HyperFrames sub-composition: root element `data-composition-id="<id>"`, `data-width=1080 data-height=1920`, `data-duration = end-start + transition overlap`.
- Local time 0 = scene start. Register one paused timeline `window.__timelines["<id>"]`.
- Wrap the root in `<template>` with `<style>`/`<script>` inside it (template: `assets/shared/scene-template.html`).
- The assembled root already loads GSAP (local copy), `lib/runtime.js`, `lib/<style>.js`, `lib/tokens-<style>.css` — scenes must not load them.
- Asset URLs are root-relative (`assets/img/x.png`); HyperFrames lint rejects other `../` paths.
- Deterministic only (no Date/Math.random); text never exits by itself; words placed at final positions before reveal.

## Component library API (`assets/<style>/lib.js`, shared `assets/shared/runtime.js`)
Each library exposes a global (`RSA` / `RSB`) of builder functions with one signature:
`lib.<component>(container, props, tl, at) → HTMLElement` — builds DOM inside `container`, adds its tweens to `tl` starting at local time `at`, returns the root element. Shared runtime `RS` provides: `RS.words(el, words[{w,t}], opts)`, `RS.type(el, text, at, cps)`, `RS.blurIn(tl, el, at, opts)`, `RS.motionBlur(...)`, `RS.numRoll(...)`, seeded `RS.rand(seed)`.
Every component is listed in `references/components.md` with props, timing and the teardown it reproduces.

## Worker result
`result.json`: `{"ok": true, "files": ["…"], "duration": 4.08, "warnings": [], "notes": "…"}` — workers never edit files outside their `out` dir.
