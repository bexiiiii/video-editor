# Style F — "Kinetic Talking Head" (cinematic head + poster-like kinetic words)

> Teardown with frame-level numbers: `teardowns/style-f/tt_7632011473379790097.md`. Pack: `assets/style-f/` (global `RSF`, API in `components.md` → "Style F"). Audio: `audio-policy.md`. Layout, variety and anti-AI rules: `layouts.md` (binding).

## When to use
Use it for expert / service talking heads that sell one clear idea per sentence: car and credit services, finance advice, personal brands, B2B services ("2 options", "the debt stays on you", "we find the buyer"). **Footage-first, always**: the base is the client's real talking-head video — the style needs footage (like D) and never draws people. Languages: kk / ru / uz with code-switching; Montserrat Alternates covers ә ғ қ ң ө ұ ү һ і and Uzbek oʻ gʻ.

## 1. Structure
- **Head segments of ≈ 2.2 s** (median; 0.8–4.8) cut hard on word boundaries. One camera, **two framings**: wide 1.0 ↔ tight ≈ 1.4 about the face, alternating on every head cut; after an insert the head returns **wide**; tight segments are shorter (≈ 2.0 s vs 2.7 s).
- **Two text layers that never overlap**: small literal captions on every head segment; a **kinetic stack** (huge mixed-size lowercase words) on the key phrase of a sentence (≈ 25 % of head time), during which the captions are muted.
- **Inserts** (1.2–2.2 s, ≈ 1 every 8–10 s): flat white `#FCFCFC` (most) or salmon `#EEB596` page + one cut-out object + a stack; once per reel a **tilted full-bleed screen recording** of the real product/site with a stack on top.
- **Hook**: the question stacks up word by word over the speaker's chest (words rise from below), then a hard cut to a white insert answering it ("2-ақ вариант бар!"). Visual question → answer in ≤ 3 s.
- **Ending**: hard cut to a black "link below" card (white double chevron + 2 lines, one yellow word). No logo, no follow button.
- Optional: one 3-frame **light-leak** flash over a cut that opens the closing argument.

## 2. Tokens (tokens.css, scoped `.rsf`)
- **Footage**: the client's video, untouched grade (ref: warm dark interior, mustard wall `#89712A`, cool shadows `#506474`). No vignette, no grain, no scrim boxes.
- **Kinetic colours**: white `#FCFCFC` · black `#000000` (on white / salmon) · **yellow `#FCF900`** (key word over footage, caption highlight; brand accent replaces it) · **red `#FC0000`** (negative / problem word) · dim white 62 % (trailing "…").
- **Insert pages**: white `#FCFCFC`, salmon `#EEB596` (brand accent2 replaces it), end card `#000000`.
- **Accent rule**: exactly one accent word or 2-word phrase per stack — yellow over footage (positive/neutral) or red (problem); red on white inserts; black on salmon.
- Text shadow only on white type over footage: `0 2px 12px rgba(0,0,0,.35)`.
- Column x 90–990 (ref stacks reach 97–990).

## 3. Type scale (Montserrat Alternates 800, −0.06 em, lowercase)

| Role | Spec |
|---|---|
| **XL** | 240 px (x-height ≈ 130) — the punch word ("жаяу", "жарна", "бар!") |
| **L** | 165 px (x-height 88) — the anchor line, usually the widest (750–860 px) |
| **M** | 122 px (x-height 66) |
| **S** | 90 px (x-height 48) — connective words tucked beside big ones |
| Condensed headline (inserts) | Oswald 700, 232 px, cap ≈ 183, uppercase black ("2-ВАРИАНТ") |
| Number (inserts) | keep-case digits 170 px + label 64 px above ("остаток / 2 000 000") |
| **Small caption** | 800, **56 px** (x-height 31), line pitch 52, −0.03 em, white, highlight yellow, centred, ≤ 2 lines, box top y 1300 |
| End card | 78 px lines, white + one yellow word; chevron 248×295 white |

Stacks auto-fit to 900 px (all sizes scale together). The reference face is ≈ 12 % narrower than the substitute; −0.06 em tracking keeps line widths within ±4 %.

## 4. Layout geometry (measured)
- **Stack over the head**: centred on x 540, x-bands in **y 1050–1460** (centre 1255 = chest/lap), never over the face (face y 300–900 wide, 250–1000 tight). Hook ref: x-bands 1102–1190 / 1218–1287 / 1338–1409.
- **Interlock**: next line's x-top = previous baseline + 0.17 × mean(font sizes), + 0.2 × next size when the next line has ascenders (б ё і һ, digits, ! ?). Descenders may kiss the next line.
- **Alignment grammar**: one anchor line; others **left / right / centre against the anchor's edges** (e.g. L full · S left · XL right · S right). Mixed sizes may share a baseline ("ақша" M + "алады" S).
- **Small caption**: box top 1300, x-band 1313–1343, second line 1365–1394.
- **Inserts**: content block centred on y ≈ 960 (ref 648–1383 / 253–1286 / 500–1553 / 452–1503); object 380–520 px (circle 400–460); condensed headline top 500.
- **Screen recording**: full-bleed, rotate −10°, rotateX 8°, scale 1.25 of an oversized plane, dim 20 %, scroll ≈ 60 px/s; stack centred on y 960.

## 5. Layouts — `RSF.layout.<id>` mapped to the `layouts.md` catalogue

| id | layouts.md | Composition | Reference beat |
|---|---|---|---|
| `head` | `head` | footage with framings; small captions only | 3.04–3.8, 28.4–39.3 |
| `head-side` (`headSide`) | `head-side` | footage + kinetic stack(s) on the chest band (blur-out between two stacks) | 0–1.8, 9.1–10.3, 16–18, 23.4–26.2, 56.3–59.5 |
| `insert-statement` | `statement` / `stack` | colour page + (condensed headline) + big stack | 1.8–3.04 (with pills → use insert-object) |
| `insert-object` | `hero` | colour page + one cut-out object (drop/rise) + stack under (+ above) | 3.8–5.44, 39.3–41.5 (salmon, circle) |
| `media` | `media` | tilted screen recording + stack | 13.96–15.96 |
| `number` | `number` | label + big number + b/w cut-out rising over it + stack | 26.2–28.4 |
| `list` | `list` | condensed headline + 2–4 numbered kinetic lines | 18.2–21.2 ("2-ВАРИАНТ" + stack) |
| `cta` | — (ending) | black card, white chevrons, "link below" | 59.48–60.64 |

Variety: never two inserts in a row; alternate white and salmon only when there are ≥ 3 inserts (white is the default); ≤ 1 `media` per 20 s; no two consecutive head segments with stacks of the same alignment pattern.

## 6. Components (builders, see components.md)
`footage` (framings + labelled slot) · `stack` · `caption` · `insert` · `headline` · `object` · `broll` · `leak` · `cta` · `exit` · `layer` · `tx.swap`.

- Stacks rewrite a sentence into ≤ 6 key words (keep the speaker's words; literal is best).
- Objects are real cut-outs: product shot, app icon, brand logo the client supplied, b/w stock photo of a situation (eyes blurred), money/document props from `reels-art` (one consistent art direction). Missing → labelled slot.
- The screen recording is the client's real site/app/listing (`materials.md`); missing → labelled slot.

## 7. Motion
- **Word reveal**: in place on the spoken onset (lead 0.04 s): opacity 0→1, blur 16→0, scale 1.05→1, **0.22 s power1.out** (5–6 frames). No slides, no bounce, no typewriter.
- **Hook only**: words rise from +400 px with blur 18, 0.32 s power3.out, lead 0.2 s.
- **Objects**: drop from the top / rise from the bottom 760 px, 0.42 s power3.out with vertical motion blur; or blur-in 0.28 s.
- **Inserts** open on the empty colour page for **0.2 s**, then first word → object (+0.08) → next words.
- **Exit**: a stack dies with the hard cut; inside one segment it blurs out (0→18 px, 0.28 s power1.in), then ≥ 0.25 s of clean footage before the next stack or caption.
- **Camera**: hard framing sets on cuts (1.0 ↔ 1.4, origin 50 % 30 % or the detected face). No push-ins, whips or Ken Burns. Optional `drift` 0.02–0.03 inside segments ≥ 2.5 s (off in the reference).
- **Transitions**: hard cuts only (assembler default for style F); one optional light leak (3 frames).

## 8. Captions
- Literal words from `transcript.json`, lowercase, **1–3 words / ≤ 22 chars per phrase**, shown **whole on the first word** (0.06 s) and hard-swapped by the next phrase (assembler `CAP_STYLE["f"]`, `captions.py` limits).
- Highlight (yellow): numbers automatically, plus `brief.captions_highlight` words (the verb of the point: "білмейді").
- Muted while a stack is on screen: each head scene lists its stack windows in `"caption_mute": [[s, e]]` (scene-local).
- Never on inserts / B-roll / end card.

## 9. Audio
- **Reference profile**: dry voice only, −14 LUFS, LRA ≈ 2.4; **no music bed** (pauses fall to −45 dBFS), **no whooshes** on cuts or stacks; one sub-boom (30–80 Hz) on the end-card cut.
- **Energetic profile (default)**: real music bed per `audio-policy.md`, SFX sparse — soft pop on object entrances, one riser into the closing stack, impact on the end card; never a whoosh on every framing cut (cuts are the rhythm).

## 10. Pitfalls
- **Never put the reference channel's identity, footage, marketplace logo or app on screen.** Identity (handle) comes from the brief.
- Drawn people or avatars in place of footage; stock talking heads. Missing footage → stop and ask (footage-first style).
- Big captions on every phrase, or small captions under a stack (layers must not overlap).
- All lines the same size, evenly spaced, centred — no interlock; more than one accent colour per stack.
- Punch 1.12 (reads as a mistake) instead of 1.35–1.5 (reads as a second camera); slow zooms instead of hard framing cuts.
- Bouncy pops, slide-ins or typewriter on stack words; whoosh on every cut; a music bed in `reference`.
- Text over the face; stacks below y 1470 (Reels UI) or above the chin.
- A font without Kazakh glyphs (fallback mid-word on қ ғ ү ұ ө ә).
- Demo deviation: the footage, objects and screen recording are labelled slots; the slot re-frames per segment to show the two-framing logic.
