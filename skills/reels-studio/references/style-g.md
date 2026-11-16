# Style G — "Editorial Selfie" (phone-selfie head + editorial caption stacks)

> Teardown with frame-level numbers: `teardowns/style-g/DekIQiwIrSz.md`. Pack: `assets/style-g/` (global `RSG`, API in `components.md` → "Style G"). Audio: `audio-policy.md`. Layout, variety and anti-AI rules: `layouts.md` (binding). Caption contract: `contracts.md` → "Style G emphasis".

## When to use
Calm, reflective talking heads where **the words are the show**: personal brand, self-improvement, education, mentoring, faith / spirituality, values-driven founders. The footage is the client's own **phone selfie** (front camera, low angle, natural light, one take) — cheap to film, and the type makes it look designed. **Footage-first, always**: never a drawn person. Languages ru / kk / uz: every face ships cyrillic-ext (ә ғ қ ң ө ұ ү һ і) and Uzbek oʻ gʻ.

## 1. Structure
- **Head ≈ 90 % of the runtime, almost uncut**: one take, no punch-ins, no zoom (the editor still removes silences/retakes; cuts are hidden under inserts or land on word boundaries).
- **Every phrase is an editorial stack** on the chest band: small lead words + **one big emphasis word** wearing a semantic treatment. Phrases without a marked emphasis show only small lead lines; a few calm sentences become a white two-line **statement** (M).
- **Inserts are front-loaded**: 3–4 inserts in the first ≈ 15 s (≈ 1–2 s each), then pure head. Kinds: pale **mint kinetic page** (navy stack — the definition of the thesis), **cinematic generated scene** (image/video + huge translucent number/word behind a neon or serif word), **white page with client calligraphy / ornament** (faith content only, client-supplied file).
- **Hook**: the thesis in one stack ("один / **навык**") → 1-frame white flash → mint definition card. ≤ 2.5 s.
- **Ending**: the last stack builds (two emphasis lines framing a spread tuck line, "**слово** / даже · важнее / **жизни**") and holds to the last frame. Optional statement CTA ("подписывайся / @handle") only if the brief asks for one.

## 2. Tokens (tokens.css, scoped `.rsg`)
- **Footage**: untouched (no grade, vignette, grain, scrim). Ref: grey wall, navy T-shirt, soft daylight.
- **Lead words**: `#FFFAF6` over footage/scenes, navy `#0B297E` on mint, ink `#020003` on white.
- **Treatment palette** (`.rsg-t-<id>`):

| id | fill | glow | meaning — use for |
|---|---|---|---|
| `bold-yellow` | `#F9E376` (brand accent replaces it) | none | the **value / skill / benefit** word ("навык", "качество", "обещал") |
| `glow-pink` | `#FAE0F9` | wide lilac glow (10 / 30 / 64 px) | **devotion, gratitude, giving, emotion, the heart** ("Всевышнему", "себе", "другим") |
| `serif-pink` | `#F0D8F2` serif | none | **reflection, remembrance, negated imperatives said softly** ("не забывать") |
| `serif-grey` | `#C9C6CF` serif | none | quiet reflection when pink would clash with the footage |
| `serif-gold` | `#F8E377` serif, keeps case | none | **titles of honour / names / chapter titles** over a generated scene |
| `red` | `#D9031D` | none | **warning, contrast, the bad side** ("слов", "не словами", "требоваться") |
| `bold-white` | `#FBF9FE` | none | **duty / plain fact / the verb of the point** ("должны", "выполнить", "мужчина") |
| `glow-yellow` | `#F4FF15` neon | yellow halo + flicker-in | the **promise / potential** word on a generated scene only |
| `navy` | `#0B297E` (brand accent2) | none | emphasis on the mint page |
| `condensed` | white Roboto Condensed 800 | none | extension (not in ref): long compound nouns, numbers |

  Rules: one emphasis line per stack (two only in the closing stack); a treatment marks a **theme** and may repeat for 2–3 consecutive stacks (ref: 3 yellows, then 3 pinks), but never more than 4 in a row; **only glow-pink and glow-yellow glow**; ≥ 3 different treatments per reel, ≤ 1 glow-yellow per scene insert; red ≤ 30 % of stacks (it is a warning colour).
- **Inserts**: mint radial `#C3E0DE → #B6CCC9 → #8DA09E` (brand accent2 hue), white `#FBF9FC`, flash `#F5F9FA`, backdrop number `rgba(255,246,228,.42)`.

## 3. Type
| Role | Spec |
|---|---|
| Grotesk | **Inter Tight 700** (Helvetica-Neue-Bold class; width fit 1.01–1.04 × ref at **−0.09 em**; Roboto Condensed 1.04–1.08, Arimo 1.11–1.26, Golos 1.16–1.19), lowercase |
| Serif | **Noto Serif Display 500, wdth 62.5 %** (condensed Didone, cyrillic-ext), −0.02 em |
| Lead / small | 80 px (x-height 44; ref 40–53), −0.07 em |
| Statement M | 125 px (x-height 68), −0.08 em, line pitch 0.58 em |
| Emphasis L | 200 px (x-height 109; ref 101–123) |
| Emphasis XL | 288 px (x-height 157) for words of ≤ 4 letters ("слов") |
| Serif emphasis | 200 px |
| Fit | a word wider than **740 px** is squeezed horizontally (scaleX ≥ 0.68, ref "всевышнему" ≈ 0.69) then shrunk |
| Backdrop number | ≈ 530 px, translucent, overflowing the frame |

## 4. Layout geometry (measured)
- Stacks over the head: emphasis x-band centred on **y 1335** (ref 1259–1442), block centred on **x 520**; never above the chin (y < 1150) and never below 1500 (Reels UI). On inserts/scenes the stack centres on y 960.
- **Interlock**: emphasis x-top = lead baseline **+ 6 px** (ref 0–14); a tucked line's x-top **on** the emphasis baseline (−4); small-line pitch ≈ 0.94 em (gap 31 px); M lines gap 4 px. Lead descenders dig into the emphasis.
- **Alignment grammar**: lead left-aligned to the emphasis' left edge (1–2 words) or centred (3+ words); two small words that belong together are **spread** to the emphasis' left/right edges ("тем · · более", "даже · · важнее", "мы должны · · об этом"). Lead lines are pre-laid out (words appear in place).
- **Glide**: lines added below the emphasis push the block up by half their height (0.3 s), so the visible block stays centred.
- Mint insert stack: L / S / L / XL lines, navy, centred y 960. Calligraphy box 580×490 at (204, 626), black lead over its top third (cy 860).

## 5. Layouts — `RSG.layout.<id>` mapped to `layouts.md`
| id | layouts.md | Composition | Reference beat |
|---|---|---|---|
| `head` | `head` | footage + small lead lines only | 6.07–7.5 |
| `head-emphasis` (`headEmphasis`) | `head-side` | footage + editorial stacks (lead + emphasis treatment, tuck, glide) | 0–1.03, 2.3–3.97, 7.5–12.67, 15.6–56.5 |
| `insert-kinetic` | `statement` / `stack` | mint page + navy stack, 1-frame white flash in | 1.07–2.30 |
| `insert-scene` | `media` / `hero` | generated image/video + translucent backdrop number + neon/serif stack | 3.97–6.07, 12.67–14.53 |
| `insert-calligraphy` | `hero` | white page + client calligraphy image + black lead | 14.53–15.57 |
| `statement` | `statement` | footage (or dark page) + white M two-line statement; also the optional CTA | 16.0–17.6 |

Variety: inserts never adjacent to each other more than twice in a row; ≤ 1 calligraphy per reel; ≤ 2 generated scenes per 30 s; after the first 20 s prefer pure head (the reference has none after 15.6 s) — add an insert only for a real new idea.

## 6. Components (builders, see components.md)
`footage` · `stack` · `stacks` · `captionTrack` · `insert` · `flash` · `scene` · `backdrop` · `calligraphy` · `layer` · `fitSize` · `audit`.
- In assembled runs the stacks over the head come **from the caption track** (`captions.py` style g + `scenes[].emphasis`), not from scene builders. Head scenes therefore stay `kind: "head"` (no scene HTML); inserts are `kind: "motion"` scenes built with `RSG.layout.insert*`.
- The director marks emphasis words in `scenes[].emphasis` (`contracts.md`), choosing the treatment by **meaning** (§2 table), plus `tuck` for words to spread under the emphasis and `join` for a second emphasis line.

## 7. Generated-scene art direction (reels-art / connector)
- Brief: **"cinematic dark scene, volumetric light, glowing particles and light streaks, slow motion, shallow depth of field, deep navy / warm amber palette, 9:16, no text"** + the idea (a figure made of light reading, an open book of light, a path of lanterns, hands releasing light). Abstract and symbolic beats literal.
- People only as **silhouettes or light**; never photoreal faces in scenes. Image-to-video (5 s) when credits are approved, else a still with the 1 → 1.06 push.
- Leave the centre band (y 760–1160) calm and darker for the stack; the brightest point sits above it.

## 8. Sensitive content rule (religious topics — binding)
- **Never depict the faces of prophets, companions (sahaba), saints or other holy figures** — not generated, not drawn, not from stock. Show them only as **light, silhouette, or an empty place** (the reference shows the main figure's face as pure light; we go further: no visible faces of companions or listeners either).
- **No AI-generated calligraphy or typeset Arabic of holy names** (Allah, the Prophet's names, Quran verses). Calligraphy comes **only as a client-supplied file**, verified by the client (spelling, harakat, orientation); otherwise the insert is skipped (the slot is for drafts only, never delivered).
- Honorifics stay exactly as the client writes them ("(с.а.с)", "ﷺ"); never shortened, stylised into jokes or used as decoration.
- Respectful tone: no meme SFX, no comic treatments, no red on holy names, no glow-flicker on sacred words, calm audio profile (§9). Same care for **any faith** (Christian icons, Buddhist imagery, etc.): no faces of holy figures unless the client supplies approved art, no generated sacred script.
- When in doubt, the director asks the client before generating.

## 9. Audio
- **Reference profile**: voice (phone mic, −14.6 LUFS, LRA 3.9) + a **barely audible tonal bed** ≈ 14–16 dB under the voice (soft pad / hum, harmonics ≈ 150–300 Hz, no beat), **no SFX**.
- **Energetic profile (default)**: soft ambient / piano bed ≈ −20 dB under the voice, one soft riser into the closing stack, no whooshes on cuts. **Faith content**: the client chooses — voice-only, a vocal-only / nasheed bed, or an instrumental bed; ask, never assume.

## 10. Pitfalls
- **Never reuse the reference creator's identity, footage, generated scenes or calligraphy.** Identity comes from the brief.
- Drawn people / avatars instead of footage; faces of holy figures; AI calligraphy (§8).
- A glow on every coloured word (only pink and neon glow); more than one emphasis line per stack (except the closer); emphasis words not fitted (long words must squeeze, short words go XL).
- Lead and emphasis the same size; even leading; everything centred; no spread/tuck lines.
- Blur-ins longer than 3–4 frames, bounces, typewriter, exit animations — stacks swap hard.
- Reveals early: every word starts on its onset (never before it).
- Punctuation in stacks; uppercase (stacks are lowercase; only serif titles keep case).
- Inserts spread evenly through the reel (they are front-loaded), or punch-ins / Ken Burns on the head.
- A font without Kazakh glyphs; a wide Didone at 100 % width.
- Demo deviation: the footage is a labelled slot and the generated scene a procedural abstract placeholder (light streaks, no people); the calligraphy insert is a labelled slot (client file only).
