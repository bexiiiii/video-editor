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
  audio/music.wav audio/sfx.wav   # step 3c sound (music.py / sfx_plan.py)
  audio/music_candidates.json # step 3c music_search.py: top-3 tracks {rank,title,artist,licence,licence_url,attribution,source_url,analysis{bpm,…},score,file}, "chosen"
  audio/music_src.<ext>      # step 3c original of the chosen track (client track or download)
  audio/music_bed.wav        # step 4  mix.py: ducked music stem at final level (qa_audio.py)
  audio/mix_report.json      # step 4  mix.py: voice/music LUFS, gaps, sfx count, problems[]
  CREDITS.txt                # step 3c [music]/[sfx] licences; CAPTION lines go into the post caption
  audio/mix.wav              # step 4  voice+music+sfx, −14 LUFS / −1 dBTP
  composition/               # step 4  assembled HyperFrames project (index.html + lib/ + scenes/ + media)
  composition/captions.json  # step 4  caption track (talking-head modes) — phrases + word reveal times, read by qa.py
  composition/lib/brand.{css,js,json}  # step 4  scripts/brand.py (run by assemble.py) when brief.brand has colours/font
  previews/style-<x>.jpg     # optional  scripts/make_brand_previews.sh — stock demos in the client's brand
  renders/final.mp4          # step 5
  qa/report.json             # step 5
```

## brief.json
```json
{
  "slug": "linkhr-ru-01",
  "style": "A",                       // "A" 3D Keyword | "B" iOS Keynote | "C" Keynote 3D | "D" 3D Keyword Talking Head = style A over footage (needs footage) — chosen from assets/previews
  "mode": "faceless",                 // "faceless" | "hook_cta" | "head_overlay"
  "lang": "ru",                       // "ru" | "uz" | "kk" — asked FIRST, before style
  "target_sec": 45,
  "topic": "…", "script": "…|null",   // script required for faceless+TTS
  "footage": ["input/take1.mov"],     // required for hook_cta / head_overlay, optional for faceless (user VO)
  "voice": {"source": "footage|tts_clone|tts_stock", "voice_id": null},   // ASK THE CLIENT clone vs stock
  "cta": {"type": "bookmark|follow|profile|save|none",       // ASK THE CLIENT name + handle — never copy from references
          "name": "Link HR", "handle": "@linkhr", "subtitle": "Учёт рабочего времени|null",
          "avatar": "input/avatar.jpg|null", "followers": 12400, "posts": 86, "button": "Подписаться"},
  "brand": {"name": "…", "logo": "input/logo.png|null",          // see references/branding.md
            "accent": "#…|null",      // main brand colour → the style's accent role (A/D blue UI + lime hook, B/C system blue, E gold)
            "accent2": "#…|null",     // optional 2nd colour: A/D hook accent (lime role), E rubric dot; null → derived from accent
            "ink": "#…|null",         // optional dark brand colour: A/D light-theme keyword pill, E headline ink
            "font": "Family|null",    // Google Fonts family with the script coverage of `lang` (ru Cyrillic · kk + ә ғ қ ң ө ұ ү һ і · uz Latin + oʻ gʻ); else style font kept
            "keep_style_palette": false},   // true → colours stay stock (font/logo still apply)
  "chrome": {"series": "…", "topic": "…"},  // style B breadcrumb text
  "audio_profile": "energetic",             // "energetic" (default, all styles: audible music + SFX) | "reference" (purist per-style policy, only on request) — audio-policy.md
  "captions": "auto",                       // "auto" (default: literal subtitles over every head|head_overlay scene in talking-head
                                            // reels — hook_cta, head_overlay, style D) | "all" (whole reel) | "off"
  "captions_y": null                        // optional caption centre y px (default 1440; style D 1470), keep inside 1250–1500
}
```

## Brand layer (step 4, `scripts/brand.py --work work/<slug>`, called by assemble.py)
`brief.brand` with no `accent`/`accent2`/`ink` and no `font` (or `keep_style_palette: true` and no font) → nothing is
written and the style renders exactly as stock. Otherwise brand.py derives the style's overridable tokens from the
brand colours (OKLCH ramps), enforces contrast per theme (text ≥ 4.5, display text ≥ 72 px bold and UI ≥ 3.0 — it moves
lightness only and reports every adjustment), and writes into `composition/lib/`:
- `brand.css` — overrides of the style's CSS variables/selectors (+ Google-Fonts `@import`); linked **after** `tokens-<pack>.css`;
- `brand.js` — `window.RS_BRAND = {version, name, style, accent, accent2, ink, font, logo, palette:{a|b|c|e:{…}}}`; loaded **before** `lib/runtime.js` and the packs (the libs read `RS_BRAND.palette.<pack>` with the stock value as fallback);
- `brand.json` — same data + `report{adjusted[], checks[], warnings[]}`; `lib/brand-logo.<ext>` when `brand.logo` exists (`RS_BRAND.logo`, root-relative — pass it as `logo`/`avatar` props).
Which tokens each style overrides and which stay fixed: `references/branding.md`. Branded client previews: `scripts/make_brand_previews.sh work/<slug>`.

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
      "transition_in": {"type": "dissolve", "dur": 0.5},    // drawn by the ASSEMBLER at this scene's start (see "Transitions");
                                                            // types blur-drift|whip|dissolve|portal|blur-swap|zoom|lum|cut,
                                                            // dur 0.35–0.6; omit → style default; "owner":"scene" = the scene draws it
      "captions": null,                                     // optional per-scene override of the caption track (true/false)
      "kicker": {"text": "…", "at": 7.9},
      "headline": {"text": "…", "highlight": ["word"],      // A: keywords (paraphrase) · B: literal words
                   "words": [{"w": "…", "t": 8.02}]},       // t = reveal time (from transcript)
      "caption": {"text": "…", "at": 9.1},
      "components": [{"type": "card", "at": 7.95, "props": {}}],
      "techniques": [{"id": "portal", "at": 11.6, "props": {}}],   // techniques.md — 2–4 per reel
      "assets": [{"id": "s03_rocket", "kind": "3d_object|icon|photo|screenshot", "prompt": "…",
                  "transparent": true, "size": "1024x1024"}],
      "sfx": [{"name": "click", "t": 8.40}],                // + sfx_plan.py cues {name,t,gain_db,auto:true,why}; "statement"/"punchline": true on a scene → impact / riser
      "notes": "…"
    }
  ],
  "audio": {"music": {"enabled": true, "mood": "…", "bpm": 100, "start": 0,      // energetic: under the whole piece
                      "gap_speech_db": 10, "gap_pause_db": 5},                 // music below voice (speech / pauses)
            "sfx_enabled": true}
}
```
Rules: scenes tile the timeline with no gaps; `start`/`end` snap to `transcript.pauses`; `kind:"head"` scenes show `edit/head.mp4` at the same time range.

## Transitions (assembler-owned, `scripts/assemble.py`)
Every boundary between two scenes gets a real transition on the root timeline — never a hard switch (only
`transition_in.type:"cut"` at the hook, ≤ 3.5 s). Each scene is a layer inside an untimed shell; the **outgoing** layer
sits on top and animates out while the incoming scene's own entrance plays underneath:
- overlap = `transition_in.dur` clamped 0.35–0.6 s (default 0.45); the outgoing host / head clip is extended to cover it,
  an incoming head clip starts ov/2 early (head.mp4 is on the final timeline, so the footage keeps playing — no freeze)
  and settles from scale 1.06 + blur 10 px;
- outgoing animation by type (default per style): A/D `blur-drift` (drift 200 px + blur 24 px + fade) or `whip`
  (fast up-move + directional SVG motion blur, incoming rises from +260 px); B/C `dissolve` (scale 0.96 + blur 8 px)
  or `portal` (white orb flash); E `blur-swap` (blur 18 px fade); also `zoom`, `lum`;
- head ↔ head_overlay (same footage): no video transition, the outgoing overlay fades (0.38 s, blur 10 px);
- `transition_in.owner:"scene"` → the assembler stays out; the incoming scene draws its own transition and paints
  above the previous scene's tail.
Scene builders never fake a transition with an instant background: their job is the entrance of their own elements.

## Entrances (no sudden appearances — `scripts/lint_scenes.py`, run by assemble.py)
- Every element enters with an eased tween ≥ 0.25 s (blur / fade / scale / rise per style), staggered 0.06–0.15 s;
  nothing pops in on the scene's first frame without animation; no `tl.set(…{opacity:1})` pop-ins.
- Plates (page/layer/background/chrome/scrim) may be static at local 0 — the assembler transition reveals them.
- Text is laid out at final positions and never visible before its word (`t` ≥ spoken onset − 0.08 s, never < 0).
- Lib builders already follow this; hand-made elements need their own `tl.fromTo` entrance.

## Caption track (talking-head modes, `scripts/captions.py` → assemble.py)
`brief.captions` "auto" puts a continuous **literal** subtitle track over every head / head_overlay scene (and scenes
with `"captions": true`); "all" = whole reel; "off" = none. Built from `audio/transcript.json` (final timeline) as ONE
root-level layer (`#rs-captions`, above all scenes) — independent of scene builders, always present, exactly synced:
- phrases of 1–4 words / ≤ 26 chars; a phrase swaps on a pause ≥ 0.28 s, after sentence punctuation, or at a range edge;
- each word's reveal (0.08 s) ends at **onset − 0.03 s** (never late); the phrase stays until the next one starts
  (or last word + 0.55 s);
- face-safe lower third: centre y 1440 (D 1470), band 1250–1500, soft scrim; typography per style: A/D Google Sans 600
  lowercase white + soft shadow · B/C RSX karaoke grey #9A9A9A → white · E uppercase grey;
- the libs see `window.RS_CAPTIONS = {on, y, ranges}`: RSD lifts its lower-zone headline to y 1255 and drops the
  duplicate grey caption; keyword headlines in motion scenes stay as they are;
- targets: ≥ 98 % of spoken words in caption ranges, sync −0.10…+0.05 s (qa.py `caption_coverage` / `caption_sync`).
  Sync is only as good as the transcript: forced-language ASR with word timestamps (Scribe v2 or whisper `large-v3`);
  `small`/`base` whisper models are for pipeline tests only.

## scenes/<id>/brief.json (what a scene-builder or art worker gets)
`{ "scene": {...one scene...}, "style": "B", "theme_tokens": "$SKILL/assets/style-b/tokens.css", "lib": "$SKILL/assets/style-b/lib.js", "chapter_index": 2, "chapter_count": 4, "assets_dir": "work/<slug>/assets/img", "out": "work/<slug>/scenes/s03/" }`

## Sub-composition contract (scene-builder output)
- `scenes/<id>/index.html` is a HyperFrames sub-composition: root element `data-composition-id="<id>"`, `data-width=1080 data-height=1920`, `data-duration = end-start` (the assembler extends the host window to cover the outgoing transition; the last frame holds).
- Every element has an eased entrance (≥ 0.25 s) — see "Entrances"; check with `scripts/lint_scenes.py --work work/<slug>`.
- Local time 0 = scene start. Register one paused timeline `window.__timelines["<id>"]`.
- Wrap the root in `<template>` with `<style>`/`<script>` inside it (template: `assets/shared/scene-template.html`).
- The assembled root already loads GSAP (local copy), `lib/runtime.js`, `lib/<style>.js`, `lib/tokens-<style>.css` (+ `lib/brand.js`/`lib/brand.css` when branded) — scenes must not load them. Scenes never hard-code accent hex: use the style's CSS variables / lib defaults so the brand layer reaches them.
- Asset URLs are root-relative (`assets/img/x.png`); HyperFrames lint rejects other `../` paths.
- Deterministic only (no Date/Math.random); text never exits by itself; words placed at final positions before reveal.

## Component library API (`assets/<style>/lib.js`, shared `assets/shared/runtime.js`)
Each library exposes a global (`RSA` / `RSB`) of builder functions with one signature:
`lib.<component>(container, props, tl, at) → HTMLElement` — builds DOM inside `container`, adds its tweens to `tl` starting at local time `at`, returns the root element. Shared runtime `RS` provides: `RS.words(el, words[{w,t}], opts)`, `RS.type(el, text, at, cps)`, `RS.blurIn(tl, el, at, opts)`, `RS.motionBlur(...)`, `RS.numRoll(...)`, seeded `RS.rand(seed)`.
Every component is listed in `references/components.md` with props, timing and the teardown it reproduces.

## Worker result
`result.json`: `{"ok": true, "files": ["…"], "duration": 4.08, "warnings": [], "notes": "…"}` — workers never edit files outside their `out` dir.
