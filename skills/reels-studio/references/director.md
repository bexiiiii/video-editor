# Director guide — turning a transcript into `plan/scenes.json`

Input: `audio/transcript.json` (final timeline), `brief.json`, the style reference. Output: `plan/scenes.json` (contracts.md).

## 1. Beat the speech
1. Split into sentences (already in transcript). Merge sentences shorter than 2.5 s with a neighbour; split sentences longer than 5 s at the largest internal pause.
2. Target scene length **3.4–4.2 s** (A) / **3.5–5 s** (B, components build up inside a scene). Never < 1.8 s except the hook flash.
3. Scene boundary = middle of the pause before the sentence's first word. The transition starts ~half its duration before that word.
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
- B: one component per beat from `components.md` (card, capsule, player, ring, counter, calendar, notification, selection highlight, typing dots, profile card…). Theme flips per chapter: light → dark → blue ("masalan / for example" moments) → light. Chapter changes advance the page dots.
- Talking head (`head` / `head_overlay`): punch-in 1.0 ↔ 1.12 on cuts every 3–5 s; overlays only in the chest band (y 880–1460); B portal or glitch transition between head and motion.

## 4. Asset prompts (`assets[]`)
- A: "glossy inflated 3D <object>, soft studio lighting, subtle rim light, centered, isolated on plain background, high detail, no text" · transparent true · 1024x1024.
- B: "Apple 3D emoji style <object>, centered, isolated, no text" · transparent true · 1024x1024.
- Screenshots / screen recordings / logos / photos / real proof: add them to `plan/materials.json` and request them from the client (`materials.md`); scenes reference `input/<id>_*.png|mp4`. Never fabricate real metrics or real brands' UI as genuine.

## 5. Sound cues
Per `audio-policy.md`. A: none. B: `click`/`tap` on every interactive component, `tick` on counters, `boom_sub` on portal, `notification` on banners; music starts after the hook.

## 6. Checklist before writing the file
- Scenes tile [0, duration] with no gaps/overlaps; ids `s01…`.
- Every headline word has a `t` inside its scene.
- No two consecutive scenes with the same component + theme.
- Asset ids unique; total images ≤ 1 per scene.
- Every scene has a `layout`; variety rules pass (`qa.py --plan-only`).
- One art direction for all generated images of the video (same material/light/angle words in every prompt).
