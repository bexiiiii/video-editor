# Director guide — turning a transcript into `plan/scenes.json`

Input: `audio/transcript.json` (final timeline), `brief.json`, the style reference. Output: `plan/scenes.json` (contracts.md).
The transcript must come from forced-language ASR with word timestamps — ElevenLabs Scribe v2 or whisper `large-v3`
(`asr.py`, default model). `small`/`base` whisper models are for pipeline tests only: their word times drift and the
caption track and every reveal inherit the error.

## 1. Beat the speech
1. Split into sentences (already in transcript). Merge sentences shorter than 2.5 s with a neighbour; split sentences longer than 5 s at the largest internal pause.
2. Target scene length **3.4–4.2 s** (A) / **3.5–5 s** (B, components build up inside a scene). Never < 1.8 s except the hook flash.
3. Scene boundary = middle of the pause before the sentence's first word. Every boundary gets a transition drawn by the assembler (contracts.md → "Transitions"): set `transition_in` {type, dur 0.35–0.6} on the incoming scene or leave the style default (A/D blur-drift, B/C dissolve, E blur-swap); `cut` only at the hook. The outgoing layer stays visible up to ~0.5 s past the boundary — keep boundaries in breath pauses.
4. The **hook** is the first 1–3 s: it must state the tension (question, number, "POV", contrast). If the transcript's first sentence is weak, flag it to the user with 2 alternative hook lines.
5. The **CTA** scene is the last one; video ends ≤ 0.5 s after the last word (loops on Reels).

## 2. Words on screen
- **Style A — keywords.** Headline = 2–4 words that summarise the sentence, lowercase (tutorial steps may be imperative Sentence case). Caption (grey, bottom) = the second fragment of the sentence. Each headline word gets `t` = spoken time of the word it echoes + 0.10–0.15 s; if paraphrased, use the sentence start + stagger 0.08–0.15 s.
- **Style B — literal.** Headline words = exactly the spoken words (≤ 26–32 chars, one line, shrink to fit); `t` = word onset (0–80 ms). Kicker (grey label above) = the lead-in phrase. Components arrive ~0.25 s **before** their headline word.
- Numbers on screen whenever a number is spoken (roll/counter component).
- Brand / app names → icon or logo pops exactly on the spoken name.

## 3. Layout + variety (read `layouts.md` — binding)
- Give every scene a `layout`; obey the variety rules (no layout twice in a row, ≤ 30 % one layout, component not reused within 3 scenes, ≥ 4 layouts per video).
- Plan the visual mass across the video: centre → top → bottom → full-bleed; insert one `statement` breath scene per ~6 scenes.
- Talking-head material is real footage only — never request drawn people or faces.
- Run `$SKILL/scripts/run qa.py --work work/<slug> --plan-only` after writing the plan; fix any variety violations before fan-out.

## 3a. Techniques
- Pick 2–4 from `techniques.md` by trigger (spoken number → number_roll, demo → iphone_proof/pull_out_phone, list → paper_section/section_number, punchline → jump_zoom …); avoid the brand's last 3 reels (`history.py --avoid`).

## 3b. Visual per scene
- A: one hero 3D object per scene (generated, transparent) OR a glass/UI card OR a screenshot frame. Alternate dark/light themes; accent backgrounds for hook and payoff scenes only (≤ 3 per video).
- F: every insert (`insert-object`, `number` with object) gets one generated object in `assets[]` — "glossy photoreal 3D <object>, studio light, white seamless background, soft shadow, no text", transparent, 1024x1024 (+ niche/brand words); the stack under it is plain black unless one word must be red. Stacks: ≤ 1 accent, many none (`style-f.md` §2).
- G (Editorial Selfie): head scenes need no scene HTML — the stacks come from the caption track. Mark the emphasis of
  **every sentence that has a point** in `scenes[].emphasis` (≈ 1 stack per 2–3 s; one word, or a 2-word negation like
  "не словами"), pick the treatment by **meaning** (`style-g.md` §2: value → bold-yellow · devotion/giving →
  glow-pink · reflection/remembrance → serif-pink · warning/contrast → red · duty/fact → bold-white), let a theme run
  2–3 stacks in one colour, ≥ 3 treatments per reel, red ≤ 30 %. Use `tuck` for 2 short words that complete the
  emphasis ("тем более"), `join` for the closing 2-emphasis stack, `statements` windows for calm 2-line sentences.
  Inserts (`kind: "motion"`) only in the first ≈ 15 s: `insert-kinetic` (mint, the thesis definition, white flash in),
  `insert-scene` (one generated image/video in `assets[]` — "cinematic dark scene, volumetric light, glowing
  particles, light streaks, slow motion, no text, no faces" + idea; optional backdrop number), `insert-calligraphy`
  (faith content, **client file only**). Head scenes are one take: no punch-ins (`edit_head.py --framing none`).
- **Sensitive content (religious topics, binding, `style-g.md` §8)**: never request or generate faces of prophets,
  companions or holy figures (light / silhouette / empty place only), never generate calligraphy or Arabic script of
  holy names (client-supplied and client-verified files only), keep honorifics exactly as the client writes them,
  no comic SFX or flicker on sacred words; same care for every faith. If unsure — ask the client before generating.
- B: one component per beat from `components.md` (card, capsule, player, ring, counter, calendar, notification, selection highlight, typing dots, profile card…). Theme flips per chapter: light → dark → blue ("masalan / for example" moments) → light. Chapter changes advance the page dots.
- Talking head (`head` / `head_overlay`): punch-in 1.0 ↔ 1.12 on cuts every 3–5 s; overlays only in the chest band (y 880–1460); head ↔ motion transitions come from the assembler (A/D blur-drift or whip, B/C dissolve or portal, E blur-swap). The literal caption track (`brief.captions` "auto") is added by the assembler — never plan subtitles inside scenes; keep scene text out of the caption band y 1400–1520 in head scenes.

## 3c. B-roll (`scenes[].broll`, `broll.md`)
- The script names a website / app / marketplace (kolesa, kaspi, krisha, olx, the client's site) → `{"kind":"screen","url":"https://<public page>","query":"<English fallback>","seconds":n}` — the exact public page (a listing/search page, never a login or personal page). The client's own screen recording beats it — request it in `materials.json` first.
- A generic action / place ("car dealership", "office team", "city traffic") → `{"kind":"stock","query":"<English>"}`.
- `generated` only if the client approved connector credits. Style F: ≤ 1 B-roll per 20 s on a `media` scene. Then run `$SKILL/scripts/run broll.py --work work/<slug>` (step 3, parallel with art).

## 4. Asset prompts (`assets[]`)
- Append the niche preset's `art_direction` words (`assets/niches.json`) to every prompt, plus the brand colours as the dominant accent of the object; same words for every image of the reel.
- A: "glossy inflated 3D <object>, soft studio lighting, subtle rim light, centered, isolated on plain background, high detail, no text" · transparent true · 1024x1024.
- B: "Apple 3D emoji style <object>, centered, isolated, no text" · transparent true · 1024x1024.
- Screenshots / screen recordings / logos / photos / real proof: add them to `plan/materials.json` and request them from the client (`materials.md`); scenes reference `input/<id>_*.png|mp4`. Never fabricate real metrics or real brands' UI as genuine.

## 5. Sound cues
Per `audio-policy.md`. Default profile `energetic` (all styles): write the cues that carry meaning (a `tap` on the exact cursor tap, `notification` on a banner, `impact_soft` on the punchline word, `riser_1s` ending on the reveal); `sfx_plan.py` then fills the rest — whoosh on every transition, `pop_bright` on hero entrances, `tick` on counters — under a density guard (≥ 0.6 s apart, ≤ 1 per 1.5 s) and never removes your cues. Mark a scene `"statement": true` / `"punchline": true` to get an impact / riser. Music runs under the whole piece (`audio.music.start: 0`). Profile `reference` only: A/D none; B `click`/`tap` on interactive components, `tick` on counters, `boom_sub` on portal, `notification` on banners, music after the hook.

## 6. Checklist before writing the file
- Scenes tile [0, duration] with no gaps/overlaps; ids `s01…`.
- Every headline word has a `t` inside its scene.
- No two consecutive scenes with the same component + theme.
- Asset ids unique; total images ≤ 1 per scene.
- Every scene has a `layout`; variety rules pass (`qa.py --plan-only`).
- One art direction for all generated images of the video (same material/light/angle words in every prompt).
