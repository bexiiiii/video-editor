# DekIQiwIrSz — "Один навык: умение держать своё слово" (Islamic self-improvement, Russian)

Creator: an individual creator (signature "Едіге") on Instagram. Named here only as the source; never reuse the name, face, footage, the generated religious scenes or the calligraphy.
Format: 1080x1920, **30 fps**, 56.54 s, VP9 + AAC 44.1 kHz stereo (L/R correlation 0.995 = mono in practice).
Evidence lives in `research/an/DekIQiwIrSz/`:
- `f_<t>.jpg`: full-res stills (0.8, 1.9, 2.2, 3.3, 3.5, 5.4, 6.8, 8.3, 9.3, 9.6, 11.6, 13.6, 14.3, 14.9, 15.3, 16.0, 17.0, 18.6, 21.6, 22.6, 24.2, 27.1, 29.7, 32.6, 32.8, 36.9, 46.0, 51.3, 55.8)
- `tr_<t>.jpg`: 30 fps strips (24 frames = 0.8 s, chest band crop 900 px wide, frame i = t + i/30) around every kind of reveal: "один / навык" (0.3), the white flash into the mint insert (1.0), the particle scene "свой / потенциал / 100 %" (4.4), "всевышнему" glow (7.6), "мы должны об этом / не забывать" serif (10.7), the prophet-scene title (12.4), the cut into the calligraphy insert (14.4), "где очень много / слов" (21.0), "мужчина / тем более" (36.2), the final stack "слово" (52.3)
- `sheet_01..04.jpg` (2 fps), `hook.jpg`, `cuts.txt` (8 cut points = 7 boundaries + a 1-frame white flash)
- `transcript.json`: forced `ru` ASR, local faster-whisper **small** (138 words). Good for timing; it garbles some words ("стопроцентр", "Наш вопрос слём" = "нашего пророка (с.а.с) …", "Алями" = "Аль-Амин"), so the copy below comes from the on-screen text.

All px values are at 1080 px width, measured with pixel masks (white `min>215`, yellow `R,G>180 B<150`, pink `R>200 B>190 G>140`, red `R>170 G<70 B<80`, navy `B−R>60`), ±3 px. Font sizes come from x-heights (substitute x-height 0.545 em for the grotesk). Glow was measured as the mean colour of 2–60 px rings grown around the text mask, compared with the bare shirt (`#262E3E` ≈ lum 45).

---

## 1. Format and structure

- **Phone selfie talking head, low angle** (camera at chest height looking up), handheld front camera, natural soft daylight from a window/ceiling, plain grey wall + ceiling corner, navy T-shirt. The face fills y ≈ 380–1250, eyes at y ≈ 760 (40 %). The speaker often looks up and to the side (a "thinking aloud" delivery), not into the lens. No grade, no vignette, no grain added.
- **Almost no cuts**: 7 boundaries, **all in the first 15.6 s**. From 15.57 to the end (41 s) it is **one continuous take** with no punch-ins, no zoom, no jump cuts. The rhythm comes entirely from the captions.
- **4 inserts, 6.3 s total, all at the start** (1.07–2.30 mint kinetic, 3.97–6.07 generated scene, 12.67–14.53 generated scene, 14.53–15.57 white calligraphy). Head 89 % of the runtime.
- **Speech**: ≈ 150 wpm, calm, with long breaths (gaps of 0.6–1.0 s at 17.0, 18.7, 37.1). Russian with Arabic terms.

### Beat list

| t (s) | Shot | On screen (bold = emphasis word, treatment) |
|---|---|---|
| 0.00–1.03 | head | "один" (lead) → **навык** (bold-yellow), at its spoken onset 0.48 |
| 1.03–1.07 | **white flash** | 1 frame, near-white `#F5F9FA` with the next insert's text ghosted in |
| 1.07–2.30 | **mint insert** | navy stack built word by word: "-умение" (L) / "держать" (S) / "своё" (L) / **СЛОВО** (XL) on a radial mint page |
| 2.30–3.97 | head | "если мы / **сможем**" → "если мы / **научиться**" → "этому / **навыку**" (bold-yellow, lead line changes per stack) |
| 3.97–6.07 | **generated scene** | glowing particle figure reading a book (no face; light streaks); "то мы / сможем / раскрыть" (white, M+M) → "свой / **потенциал**" (glow-yellow neon, flicker) + translucent **100 %** behind |
| 6.07–12.67 | head | lead-only lines "в первую очередь", "которые мы давали" → **всевышнему** (glow-pink) → "мы давали / **себе**" → "и давали / **другим**" (glow-pink) → "мы должны · об этом / **не забывать**" (serif-pink) |
| 12.67–14.53 | **generated scene** | robed seated figure whose face is a **white light** (no features), circle of listeners in a dim hall; "нашего" (white S) → **Пророк(с.а.с)** (serif-gold) → "нашего · до · его" spread → **пророчества** (serif-gold) |
| 14.53–15.57 | **white insert** | Arabic calligraphy "الأمين" (al-Amīn) in grey `#7D7B7E`, ≈ 580×490 px, + "• его звали" (black S) over its top |
| 15.57–56.54 | head (one take) | ≈ 24 stacks: "честным", "надёжным" (white M) · "доверенным / человеком" (white M, 2 lines) · "и мы / **должны**" (bold-white) · "где очень много / **слов**" (red XL) · "мало / **действий**" (red) · "приведи это к себе / **качество**" (yellow) · "самое · важное / **качество**" · "это если ты / **обещал**" (yellow) · "то ты должен / **выполнить**" (white) · "больше от тебя / ничего не будет / **требоваться**" (red) · "говорить / **не словами**" (red) · "определяет / поступки" (white M) · "а если ты / **мужчина** / тем · более" (white + tuck) · "и по своим / **ресурсам**" · "давать какие-то / **обещания**" (white) · "непременно / **выполнить**" (white) · "**слово** / даже · важнее / **жизни**" (red, final, held to the end) |

- **Hook** (0–2.3 s): the claim "один навык" in one stack, then a white flash into a flat mint "definition card" ("-умение держать своё слово") — thesis + definition in 2.3 s.
- **Ending**: no CTA, no logo, no handle. The last stack ("слово даже важнее жизни") builds and is held to the final frame.

## 2. Backgrounds

| Surface | Values |
|---|---|
| Talking head | real footage, untouched (wall `#7E7A70`, shirt `#262E3E`) |
| Mint insert | radial gradient: centre `#C3E0DE` → mid `#B6CCC9` → edges/corners `#8DA09E` (a soft vignette is part of the page) |
| Generated scene 1 | dark navy `#121D39` space, a figure made of orange/white light streaks and particles, blue-teal rim light; motion streaks (the clip moves) |
| Generated scene 2 | dim warm hall (lamps, carved windows), low-key `#221F1D`, one bright white light in place of the main figure's face |
| White insert | flat `#FBF9FC` |
| Flash | 1 frame `#F5F9FA` |

## 3. Typography

### 3.1 The base face (lead words, small lines, most emphasis words)
- A **neo-grotesk bold of the Helvetica Neue Bold class** (double-storey а, straight-legged у, flat-topped б, rectangular ы with the bar touching), set **very tight**: letters touch or overlap ("мы" → "м|ы", "ы" reads "ь|"). All lowercase (Cyrillic lowercase reads like small caps at this size: "слов", "выполнить").
- **Substitute fit** (2026-11, browser-measured: each candidate set at the reference x-height, ink width compared with 7 reference emphasis words — навык 501, качество 711, всевышнему 725, слов 538, жизни 508, мужчина 582, не забывать 740). All candidates have cyrillic-ext (Kazakh ә ғ қ ң ө ұ ү һ і) and latin-ext (Uzbek oʻ gʻ U+02BB):
  | face | x-height/em | tracking | width ÷ ref (навык · качество · слов · жизни) | notes |
  |---|---|---|---|---|
  | **Inter Tight 700** | 0.546 | **−0.09 em** | **1.02 · 1.04 · 1.01 · 1.03** | chosen; at −0.06 em 1.08–1.10 |
  | Roboto Condensed 700 | 0.528 | −0.02 em | 1.08 · 1.07 · 1.04 · 1.06 | close widths, but condensed shapes (narrow о) |
  | Arimo 700 (Arial metrics) | 0.528 | −0.03…−0.06 | 1.18–1.24 · 1.14–1.21 · 1.20–1.26 · 1.11–1.17 | right outlines, too wide at this x-height |
  | Golos Text 700 | 0.530 | −0.06 | 1.16 · 1.19 · 1.16 · 1.18 | rounder, wide |
  Long words are narrower than any face predicts (всевышнему ÷ 1.44, мужчина ÷ 1.19, не забывать ÷ 1.16 even for the best fit): the editor **squeezes long words horizontally** (CapCut-style box fit, ≈ 0.69 × for всевышнему) instead of shrinking them — x-heights stay 101–123 px while widths stay ≤ 740 px.
- Lead words: same face, ≈ −0.07 em ("один" 154 px at x-height 44).
- **Size roles** (x-height → font px with Inter Tight):
  | role | x-height | font | examples (width) |
  |---|---|---|---|
  | **XL** emphasis (short word) | 123–157 | **230–290 px** | слов 157 (538 w), слово 123 (528 w), СЛОВО on mint |
  | **L** emphasis | 101–112 | **185–205 px** | навык 110 (501 w), всевышнему 107 (725 w), качество 109 (711 w), мужчина 101 (582 w), жизни 109 (508 w) |
  | **M** statement | ≈ 68 | **≈ 125 px** | доверенным / человеком (662 w), надёжным, определяет / поступки |
  | **S** lead / small line | 40–53 | **75–98 px** | один 44, а если ты 45, впервую очередь 40, где очень много 52, нашего 53, даже важнее 42 |
- **Emphasis width fit**: emphasis words land between **500 and 740 px** wide. Short words (≤ 4 letters) go XL (слов x-height 157); others keep an L x-height of 101–123 and long words are **squeezed horizontally** to ≤ ≈ 740 px rather than shrunk (всевышнему keeps x-height ≈ 107 at ≈ 0.69 × width).

### 3.2 Emphasis treatments (each emphasis word wears one)
| id | where | face | fill | glow | notes |
|---|---|---|---|---|---|
| **bold-yellow** | навык, сможем, научиться, навыку, качество ×2, обещал | grotesk 700 | **`#F9E376`** (butter yellow) | **none** (ring at 4 px already = background) | the "value / skill" word. The first look called it a glow: it is flat |
| **glow-yellow** | потенциал (generated scene only) | grotesk 700 | **`#F4FF15`** (neon lime-yellow) | strong yellow halo (over bright scene) | **neon flicker** on entrance: on/off every other frame for 0.3 s, then steady (`tr_4.4`) |
| **glow-pink** | всевышнему, себе, другим | grotesk 700 | **`#FAE0F9`** (pale pink) | **wide lilac glow**: ring means 3 px `#826B82` (lum 113) → 10 px `#6F5970` (95) → 28 px `#605262` (86) → 64 px `#594E59` (81) over a lum-50 shirt → two layers ≈ 0 0 10 px rgba(255,190,250,.75) + 0 0 40–60 px rgba(200,120,220,.45) | devotion / giving / the heart |
| **serif-pink** | не забывать | **high-contrast condensed Didone** (ball terminals, hairline joins, narrow) | **`#F0D8F2`** (pale lilac-pink; mid-fade frames look grey) | none | reflection / "remember". Substitute: **Noto Serif Display, wdth 62.5 (font-stretch 62.5 %), wght 400** (cyrillic-ext); Playfair Display as a wider fallback |
| **serif-gold** | Пророк(с.а.с), пророчества (scene 2) | same Didone | **`#F8E377`** | none | titles of honour over a generated scene; initial capital kept |
| **red** | слов, действий, требоваться, не словами, слово, жизни | grotesk 700 | **`#D9031D`** | none | warning / contrast / "words vs deeds" |
| **bold-white** | должны, выполнить ×2, мужчина, ресурсам, обещания | grotesk 700 | **`#FBF9FE`** | none (no shadow either) | duty / plain fact |
| **navy** | СЛОВО (mint insert) | grotesk 700 | **`#0B297E`** | none | the only colour on the mint page |
| grey (calligraphy) | الأمين | client calligraphy image | `#7D7B7E` | none | a picture, not type |

Lead words: white `#FFFAF6` on footage/scenes (no shadow), navy on mint, black `#020003` on white. Exactly **one emphasis line per stack** (the final stack has two red words framing a white tuck line). Treatments repeat in runs (3 yellows in a row at 2.3–3.97, 3 pinks at 7.6–9.6) — the colour marks a *theme*, not a single word.

## 4. Stack grammar (chest band)

- Band: emphasis x-band **y 1259–1442** (centre ≈ 1335), leads above at 1184–1298; the whole block sits on the **chest, under the chin** (chin ≈ y 1150–1250), never over the mouth. Horizontal centre of the emphasis **x ≈ 520 ± 25** (slightly left of 540).
- **Lead line → emphasis**: emphasis x-top = lead baseline **+ 0 … 14 px** (один → навык −4 = touching; а если ты → мужчина +9; приведи… → качество +8; где очень много → слов +14). Lead descenders (д р у) dip into the emphasis, ascenders of the emphasis (б in "обещал") rise into the lead line.
- **Lead alignment**: left-aligned with the emphasis' left edge (один +17 px, где очень много 0, приведи это к себе +1) or centred over it (которые мы давали, а если ты). Lead lines are pre-laid out: words of the lead appear in place one by one, the line never re-centres while it fills (`tr_21.0`: "где очень" fixed, "много" fades in at its right).
- **Spread (justified) small lines**: when two small words belong to one line they are pushed to the **left and right edges of the emphasis word** with a big gap: "мы должны · · об этом" (над не забывать), "самое · · важное", "тем · · более" (under мужчина), "даже · · важнее" (between слово and жизни; 263 → 779 vs слово 263–790), "нашего · до · его" (three words spread across the serif title).
- **Tucked line under the emphasis**: "тем более" sits with its x-top **on the emphasis baseline** (overlap ≈ 4 px), the у descender of "мужчина" passing between the two spread words.
- **Two-line statements without emphasis** (M, white): line pitch ≈ 0.58 em (≈ 72 px at 125 px) — the second line's ascenders/caps touch the first line's descenders ("доверенным / человеком", "определяет / поступки", "научиться / адекватно").
- **Small-only captions** (no emphasis in the phrase): 1–3 words, S size (≈ 75–85 px), white, same band (x-band ≈ 1289–1340), word-by-word reveal; two lines max with pitch ≈ 75 px ("больше от тебя / ничего не будет").

## 5. Text animation (30 fps strips)

- **Word reveal** (every word, lead or emphasis): opacity **0 → 1 in 3 frames (0.10 s)**, a faint blur on the first frame (≈ 4–6 px), and a small **rise of ≈ 6–24 px** that settles over ≈ 0.25–0.3 s (power2.out). Emphasis words rise more (≈ 24 px, "слово" `tr_52.3`), lead words ≈ 6 px (`tr_0.3` "навык" 5 px). No scale, no bounce, no typewriter.
- **Timing vs speech**: the word starts revealing **on its onset or up to 0.06 s after** (навык 0.48 → first frame 0.53; слов 21.24 → 21.30; мужчина 36.26 → 36.30; об этом 10.92 → 10.97). Never early.
- **Block re-centring**: when a line is added under existing lines (tuck line, second emphasis), the existing lines **glide up** by about half the new line's height over ≈ 0.3 s (мужчина moves up ≈ 27 px when "тем более" arrives; the final "слово" climbs ≈ 160 px in total as "даже важнее" and "жизни" are added: centre stays ≈ y 1330).
- **Neon flicker** (glow-yellow only): 1-frame on / 1-frame off ×3, then steady.
- **Translucent backdrop number** ("100 %"): fades in ≈ 0.3 s after the emphasis word to ≈ 40 % white opacity, behind the text, huge (cap ≈ 380 px, ≈ 530 px font, overflowing the frame edges), no motion.
- **Exit**: a stack is replaced by a **hard swap** (the next stack's first word appears on the next frame — `tr_52.3` "как бы" → empty 3 frames → "слово"), or dies with the cut. No exit animation.
- **Serif titles** (scene 2): fade 0 → 1 in ≈ 4 frames, no rise; the small white lead appears first, the title lands *above* it (the lead is at the bottom of the title's band).
- **Calligraphy**: fades in ≈ 4 frames behind the black words, together with a small black bullet dot.

## 6. Inserts and generated scenes

- **A. Mint kinetic insert** (1.07–2.30): navy grotesk stack, lines of L / S / L / XL ("-умение" 747–910, w 487, x-height ≈ 118 (f ≈ 218) · "держать" 922–996, f ≈ 100, indented +20 left of "-умение"'s stem · "своё" 998–1126, f ≈ 195 · "СЛОВО" XL), lines overlap the same way as on footage (держать tucks under умение's у descender, rising ≈ 5 px into it). Block centred on x 520, y 750–1200 (upper-middle: there is no face to avoid).
- **B. Generated cinematic scene** (2 of 4 inserts): full-bleed AI image-to-video, slow motion, dark, light-driven; text on top uses the same stack grammar centred on y ≈ 900–1050 (no chest to sit on): scene 1 = abstract glowing figure + neon emphasis + translucent number; scene 2 = honour title in serif-gold. Faces: the main figure is **light only**. (Scene 2 also shows background listeners with visible faces — our rule is stricter, see §9.)
- **C. White calligraphy insert**: flat white, a big grey Arabic word (the honorific "al-Amīn", "the trustworthy") ≈ 580×490 at x 204–781, y 626–1117, with the black lead "• его звали" (f ≈ 95) laid over its upper third.
- The **number backdrop** and the **serif title** are the only non-grotesk elements besides the serif emphasis.

## 7. Transitions and camera

- Head → mint: **1-frame white flash** (1.033), then the mint page (its first 3 frames brighten from the flash colour into mint while the first word fades in).
- All other boundaries: **hard cuts** on word boundaries. Inserts start with their first word already revealing within 0–4 frames of the cut.
- Camera: handheld phone, slight natural sway; no digital zoom, no punch-ins, no reframing in 56 s.

## 8. Audio

- **Voice**: phone mic, close, slightly roomy. Integrated **−14.6 LUFS**, LRA 3.9 LU; 40 ms RMS percentiles 5 / 50 / 95 % = −28 / −19 / −12 dBFS.
- **A quiet tonal bed is present**: pauses only fall to **−28…−32 dBFS** (17.8, 18.7, 37.1, 37.6 s), and their spectrum is harmonic (peaks ≈ 53–78, 150–160, 195–206, 292–320 Hz) — a soft sustained pad/hum-like bed ≈ 14–16 dB under the voice, no beat. The first 0.28 s is digital silence (−105 dB): the bed starts with the voice. Whether it is instrumental or vocal cannot be told from the spectrum alone.
- **SFX: none audible** (HF bands track the voice; no whooshes on the cuts, the flash or the reveals).

## 9. Secret sauce

1. **Captions as editorial typography**: every phrase is a mini poster — small lead words + ONE big emphasis word — so the reel reads like a magazine page laid over a casual selfie.
2. **A treatment per meaning**: yellow = the skill/value, pink glow = the divine/giving, serif = reflection/remembrance and honour, red = words-vs-deeds warnings, white = duty. The colour change itself tells the viewer the topic changed.
3. **Tight, interlocking lines** (descenders into caps, spread words hugging the emphasis edges) — the stack is one object, not lines of subtitles.
4. **Front-loaded inserts**: four rich inserts in 15 s buy attention, then 41 s of uncut talking with only type — cheap to produce, still feels designed.
5. **Light instead of faces** in sacred imagery: respectful, and visually the brightest point of the frame.
6. Calm sound: voice + a barely audible bed, no SFX — matches the topic.

**What a naive recreation gets wrong**
- A glow on every coloured word (only pink — and the neon scene word — glow; yellow, red, white, serif are flat).
- One subtitle line with a coloured word instead of a two-size stack; even leading; centred lines everywhere.
- Lead and emphasis in the same size, or emphasis sizes not fitted to word length (short words must get bigger).
- Pops, bounces, typewriter; blur-ins longer than 3–4 frames; exit animations.
- Faces of holy figures (or of companions) in generated scenes; AI-generated Arabic calligraphy of holy names.
- Whooshes on cuts; a loud music bed.
- Fonts without Kazakh glyphs; a wide Didone (Playfair at 100 % width) instead of a condensed one.

## 10. Reproducible spec (CSS + GSAP)

```css
.stack{position:absolute;left:0;right:0;display:flex;flex-direction:column;align-items:center}
.lead{font:700 80px/1 "Inter Tight",Arimo,sans-serif;letter-spacing:-.07em;color:#FFFAF6;text-transform:lowercase}
.emph{font:700 200px/1 "Inter Tight",Arimo,sans-serif;letter-spacing:-.09em;text-transform:lowercase}
/* ≤ 4 letters → 288px; wider than 700–740px → transform:scaleX(≥ .68); emphasis x-top = lead baseline + 6px */
.bold-yellow{color:#F9E376}
.glow-yellow{color:#F4FF15;text-shadow:0 0 8px rgba(244,255,21,.9),0 0 30px rgba(230,255,0,.55)}
.glow-pink{color:#FAE0F9;text-shadow:0 0 10px rgba(255,190,250,.75),0 0 46px rgba(200,120,220,.45)}
.serif-pink{font-family:"Noto Serif Display";font-stretch:62.5%;font-weight:400;letter-spacing:-.02em;color:#F0D8F2}
.serif-gold{font-family:"Noto Serif Display";font-stretch:62.5%;color:#F8E377;text-transform:none}
.red{color:#D9031D}.bold-white{color:#FBF9FE}.navy{color:#0B297E}
.spread{display:flex;justify-content:space-between;align-self:stretch}
.mint{background:radial-gradient(120% 80% at 50% 45%,#C3E0DE 0%,#B6CCC9 55%,#8DA09E 100%)}
```

```js
// word reveal on its onset (never early)
tl.fromTo(w,{opacity:0,y:rise,filter:"blur(5px)"},{opacity:1,filter:"blur(0px)",duration:.1,ease:"none"},t);
tl.fromTo(w,{y:rise},{y:0,duration:.3,ease:"power2.out",immediateRender:false},t);   // rise 6 lead / 24 emphasis
// block glide when a line is added below
tl.fromTo(block,{y:y0},{y:y0-newLineH/2,duration:.3,ease:"power2.out",immediateRender:false},t);
// neon flicker (glow-yellow)
[0,1,2,3,4,5].forEach(i=>tl.set(w,{opacity:i%2?0.15:1},t+i/30)); tl.set(w,{opacity:1},t+6/30);
// stack swap: hard
tl.set(prev,{opacity:0},tNext);
// white flash into an insert (1 frame)
tl.set(flash,{opacity:1},tCut); tl.set(flash,{opacity:0},tCut+1/30);
```
