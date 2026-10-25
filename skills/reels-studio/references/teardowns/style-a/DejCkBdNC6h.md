# DejCkBdNC6h — "Awesome AI Plugins" (zaytsevtech) — forensic style breakdown

Source: 1080x1920, 60 fps, 58.08 s, AAC 44.1 kHz (L = R, so effectively mono).
Measured with ffmpeg: per-frame luma, frame difference and sharpness at 60 fps (`metrics.txt`), full-res stills (`f_*.png`), 60 fps transition strips (`tr60_*.jpg`), text strips (`txt_*.jpg`, `lab_4.3.jpg`), icon strips (`icon_*.jpg`) and 50 ms audio RMS (`rms_*.txt`). The transcript (`transcript.json`) was used for sync.

---------------------------------------------------------------------
## 1. Format & structure

- 58.1 s, 159 words, 164 wpm, speech fills 87% of the runtime. It is a faceless explainer: one voice-over, motion-graphics only, no footage and no presenter.
- 14 scenes. A transition starts every 4.1 s on average (range 1.9–8 s), and each scene ends on a sentence boundary of the voice-over.
- Hard cuts: `cuts.txt` lists only 36.07 and 51.0, and even those two are blurred dissolves. Real transitions were detected as sharpness dips plus luma swings.

| # | time (s) | BG | headline (on screen) | visual | VO gist |
|---|---|---|---|---|---|
| 1 | 0.00–2.00 | red pleated curtain | `нужны / плагины?` | Claude + Codex clay app icons, "или" between them, labels typed | "Нужны плагины для Claude или Codex?" |
| 2 | 2.00–3.80 | white #FBFDFD | `подборки / на гитхабе` | 3D glossy GitHub Octocat badge (black disc, white cat) rises from below | "Начни с этой подборки на гитхабе" |
| 3 | 3.80–11.30 | near-black #0B0D0D + dot grid | `Awesome AI / Plugins` | Claude Code icon slides in from the right → +Codex (8.5) → re-layout into a zig-zag + Gemini fades in (9.9). Typed labels; grey caption "в одном каталоге" | name of the repo, "в одном каталоге…" |
| 4 | 11.30–13.70 | white | (no headline) | 3D glossy blue coins drop from above and stack; label "экономии / токенов" sits to the right of the stack | "инструменты для экономии токенов" |
| 5 | 13.70–17.80 | dark | `сокращать объём / информации` | tilted dark repo card (GitHub icon + `awesome-ai-plugins`, then content morphs to "нужный контекст / README.md / plugins.json"); 2-line grey caption | "сокращать объём информации…" |
| 6 | 17.80–23.40 | dark | `проверки / кода` | code-window card (traffic-light dots), code typed line by line with syntax colours: `const plugins = catalogue .filter(supportsClient) .map(readInstallGuide);`. At 21.6 an icon row "проверять изменения" appears | "проверки кода…" |
| 7 | 23.40–27.80 | deep-space purple (stars) | `работаешь / с дизайном?` | two app screenshots in thick rounded frames, yellow #F7C400 and cyan #00BAFA; subtitle "референсы и проверка интерфейсов"; label "Memi Studio · Canvas preview" | design tools |
| 8a | 27.80–33.30 | white | `пишешь / тексты?` | white card ("текст" / "осуществлять проверку"; the text is retyped as "проверять"); caption "делать формулировки" + blue pill "естественнее" | writing skills |
| 8b | 33.30–35.90 | white (blur swap inside the scene) | `открываешь / подходящий проект` | light GitHub repo card (`mblode/agent-skills`, black "README" tab pill, tags, blue README.md link) + cursor click; caption "читаешь, что он делает" | how to read a repo |
| 9 | 36.00–39.80 | navy #111841 + diagonal light ray + dot grid | `с каким помощником / работает` | frosted-glass pill card "помощник / Claude Code · Codex" → second glass card "Install / mblode/agent-skills" joined by a dashed curved connector | compatibility, install |
| 10 | 39.80–42.20 | dark | `несколько / программ` | small pill "дополнение" with a dashed tree branching to the Claude / Codex / Gemini icons | one add-on, many apps |
| 11 | 42.20–46.50 | white | `только / одну` | Claude Code wordmark; card "всю подборку / ● общего установщика нет / [установить]"; caption "одной кнопкой не получится" | no one-click install |
| 12 | 46.50–50.90 | lavender radial (top) → white | `с конкретной / задачи` | card "задача" with a dashed input; coloured chips fly in (проверка / UI / до / релиза); blue button "выбрать" | start from a task |
| 13 | 50.90–52.90 | dark | `выбрать / инструмент` | dark dropdown `ui-verification` opens (blue highlighted row, ui-design, ui-animation); cursor; caption `mblode/agent-skills` | pick a tool |
| 14 | 52.90–58.08 | dark | `сохрани` | glossy 3D blue bookmark (CTA); "Awesome AI Plugins" in large light-grey type; caption "будет с чего начать поиск" | save CTA |

**Hook (0–3 s)**
- 0.00–0.13: the background (red curtain) is visible alone. There is no black frame, the curtain is lit from frame 0.
- 0.10: word "нужны" starts its blur-in.
- 0.13: the Claude icon pops (scale 0.1 → 1).
- 0.23: the Codex icon pops, 0.1 s stagger.
- 0.43: "плагины?" blurs in.
- 0.6: "или" appears.
- 0.65–1.0: the labels "Claude" and "Codex" type in letter by letter.
- 1.0–1.9: the layout drifts up about 40 px.
- 1.92–2.33: zoom-through, blur-dissolve to a white scene. The icons scale up and blur while the BG cross-fades red → grey → white.
- 2.43: the 3D GitHub badge rises from below with motion blur and settles by 2.6.
- 2.5: "подборки" blurs in, then "на гитхабе".

The question → answer structure gives two scenes in 3 s.

**Ending / CTA**
- 52.9: the previous dropdown scene blurs out.
- 53.0: the bookmark icon rises from below.
- 53.2: "сохрани" blurs in.
- 53.5: "Awesome AI Plugins" types in.
- 54.0: the caption types in.
- The CTA is held still for about 4 s until 58.08. There is no end card, no logo and no handle on screen. The hard stop is the end of the voice-over.

---------------------------------------------------------------------
## 2. Backgrounds

There are 8 BG types; the BG changes at almost every scene. The canvas alternates dark / light so that consecutive scenes contrast: dark → white → dark → white … (luma swings 20 ↔ 250).

| BG | exact values |
|---|---|
| **Dark base** (used most) | flat `#0B0D0D` (slightly cool near-black). It carries a **dot grid**: 3 px dots on a **36 px** pitch, dot colour about `#16191A`–`#1E2121` (≈ rgba(255,255,255,0.04–0.08)). The grid is barely visible: it fades toward the edges and is only clear in the mid-frame |
| **White base** | flat `#FBFDFD` (cool off-white, never pure #FFF). It carries a light dot grid, 24 px pitch, dots `#E6E8E8`–`#F0F2F2`, also faint |
| **Red curtain** (hook only) | Vertical pleated stripes, roughly 15–30 px per pleat. Pleats are narrow at the left, wider and softer to the right, like a curtain lit from the left. Top-left is bright red `#DB1D16`–`#E22016`, the darker stripes in the same area are `#A2150E`/`#85120C`. Colour stops: centre `#550D09`, x=40 column fades `#E11E16` (y=0) → `#7C1009` (y≈490) → `#430B0C` (y≈970) → `#080707` (y≈1690). The bottom-right gets a **warm beige/gold light leak** `#C49D74`–`#CAA277` at y≈1450–1570, the right edge is dark `#140B09` at y≈730. To build it: stripes from `repeating-linear-gradient(90deg)` with varying widths, multiplied by a red→black vertical gradient, plus a radial gold glow at the bottom-right |
| **Deep-space purple** | almost black `#000000`–`#060313`, centre `#20164B`; a violet glow in the top-left corner `#2D044F` and a magenta glow in the bottom-right `#370040`; a soft blue-violet radial light around the centre; sparse white star dots (2–4 px, random, about 40 on screen) |
| **Navy light-ray** | base `#111841`; top-left `#5765C8`; a diagonal **god-ray** beam from the top-left going down-right (about 35° from vertical, soft edges, ~250 px wide, `#3A47A0`→transparent); the dot grid sits on top |
| **Lavender radial** | top centre `#C3D3FA`, edges `#CFDBFA`, ellipse fading to `#FBFDFD` by y≈1300. It reads as a soft concentric "ripple" (faint ring banding) |
| **Grey mid-transition** | not a real BG: it is the 50% cross-fade between dark and white (`#7F8080`) visible for 2–3 frames |

How the BG changes: always by **cross-dissolve inside a blur transition** (§6), never a flash and never a slide. The BG itself never moves. The only BG motion is the slow drift of the light rays / glows.

---------------------------------------------------------------------
## 3. Typography

**Family**: a geometric grotesk with Cyrillic support, looking like **Google Sans / Product Sans** (single-storey feel, round "о/с", double-storey "а", "Claude/Codex" look exactly like Google Sans). The closest free option is **Google Sans Flex** (Google Fonts); fallbacks are *Onest*, *Manrope* or *Golos Text*. Code uses a monospace font that looks like SF Mono / JetBrains Mono (`README.md`, `plugins.json`).

| role | size @1080w | % width | weight | colour | case | position |
|---|---|---|---|---|---|---|
| **Headline** (short, ≤ 2 words per line) | ≈ **78 px** (x-height 40 px, line pitch 83–84 px) | 7.2% | SemiBold/Bold (600–700) | `#FFFFFF` on dark, `#000000` on light | **all lowercase** (even the first word; brand names keep their case: "Awesome AI Plugins") | centred, block centre y ≈ **29–31%** (line 1 top ≈ 518, line 2 bottom ≈ 641) |
| **Headline** (longer lines, e.g. "сокращать объём / информации", "с каким помощником / работает") | ≈ **62–66 px** (line pitch 66–67) | 6% | 600 | same | lowercase | same block, y ≈ 25–37% |
| **Subtitle / descriptor** (under the visual) | ≈ 44 px (line height 42–43) | 4% | Regular 400 | `#E2E0E8` (≈ 88% white) on dark | lowercase | centred, y ≈ 68–76% |
| **Grey caption** (explanatory, 1–2 lines) | ≈ 44–46 px, line pitch 53 px (lh ≈ 1.18) | 4.2% | Regular 400 | **`#767878`** on dark, `#686B6B` on light | lowercase | centred, y ≈ 72–76% |
| **Item label** under an icon | ≈ 44–46 px (cap height 33) | 4.2% | Regular 400 | `#E4E1E2` on the curtain, `#6E7070`-ish grey on dark | Title case for product names | centred under the icon, about 45 px gap |
| **Connector word** ("или") | ≈ 44 px | — | Medium | `#E4E1E2` | lowercase | vertically centred between the icons |
| **Card title** ("нужный контекст", "задача") | 46–70 px | — | SemiBold | white / black | lowercase | left-aligned inside the card with ~40 px padding |
| **Mono / code** | 30–34 px | — | Regular | `#E8EAEA`; syntax: keyword pink/magenta, identifier blue `#4FA3FF`, string/grey `#9A9C9C` | as code | left |

- Headline line-height ≈ **1.05–1.08**, letter-spacing about 0 to −0.01em (tight, no tracking).
- Max chars per headline line: about **10–18**. The text is always broken by meaning into 2 short lines ("нужны / плагины?").
- Words on screen: headline 2–4 words, plus at most one label row, plus one caption. The headline alone is never more than 4 words.
- Hierarchy: big white/black headline at the top → visual in the middle (y≈45–60%) → small grey caption below. That vertical stack is used in every scene.
- Text is never boxed, never outlined, never shadowed, never gradient-filled.

---------------------------------------------------------------------
## 4. Text animation (measured at 30/60 fps)

**A. Headline words: per-word blur-rise-fade.** Each word is a separate unit, triggered when that word is spoken.
- opacity 0 → 1 over ≈ 0.20 s
- blur ≈ 12 px → 0 over ≈ 0.25–0.30 s (it is still slightly soft at +0.2 s and sharp at +0.27–0.30 s)
- translateY +24…+30 px → 0 (measured: "нужны" 13 px of rise at half-res across 0.1→0.4 s; "плагины?" 15 px at half-res)
- very slight horizontal settle in some cases (≈ +15–30 px)
- easing: strong ease-out (power3/expo.out), no overshoot
- total ≈ **300 ms** per word
- the gap between words follows the speech (0.13–0.4 s), not a fixed stagger
- the second line appears below the first without moving the first line: the layout is pre-computed with final positions and **nothing reflows**

**B. Labels / captions / UI text: per-character typewriter with a soft leading edge.** Measured on "Claude Code":
- 11 characters in 0.46 s ≈ **24 chars/s (≈ 42 ms per char, 2–3 frames)**
- each new character fades and blurs in over ~3 frames, so a blurred "ghost" glyph leads the typing
- text is anchored at its final centred box; characters appear left to right in place, no cursor
- the same method is used for code lines in the code window, file names and repo names

**C. In-card text replacement** ("осуществлять проверку" → "проверять"): the old text is deleted or retyped in typewriter style, it does not cross-fade.

**Exit**: text never animates out on its own. Everything leaves together with the scene transition: content blur ~0 → 20 px+ and drifts with the push direction while the BG cross-fades.

---------------------------------------------------------------------
## 5. Graphics / objects

- **Icon style**: AI-rendered **3D glossy "clay / inflated" icons**: soft, puffy, specular highlights, slight subsurface feel.
  - App icons: white squircles (iOS superellipse) with a puffy 3D logo inside (Claude orange asterisk, black OpenAI knot, Gemini spectrum star), **223×223 px** (20.6% width) in the hook, ~190 px later. A soft contact shadow sits under each.
  - Standalone objects: GitHub badge (~260 px), blue coin stack, blue bookmark (~170×200 px).
  - The glossy blue in the coins and bookmark is around `#1E8BFF`/`#3AA0FF`, with white highlights.
- **Layout**: 2 icons at x = 343 / 743 (400 px apart, symmetric about 540), centre y ≈ 994 (51.8%). With 3 icons the layout becomes a **zig-zag** (centre one lower by ~60 px).
- **Icon entrance**:
  - (a) pop: scale 0.1 → 1.0 over ~0.25 s (0.133 → 0.40 s), with blur at the start, ease-out (back.out(1.2)-ish, very small overshoot), and a **0.10 s stagger** between siblings
  - (b) slide-in from off-screen right with horizontal motion blur, decelerating, ~0.3 s (Claude Code icon at 3.9 s)
  - (c) rise from below with motion blur (GitHub badge, bookmark)
  - (d) gravity drop and stack (coins fall from the top edge one by one, ~0.15 s each)
  - (e) ghost fade-in: semi-transparent grey → full colour (Gemini at 9.9 s, ~0.25 s)
- **Re-layout**: when a new item joins, the existing items glide to their new positions (~0.35 s, ease-in-out) before the newcomer appears.
- **Idle motion**: essentially none (title bbox identical at 4.6/6.0/7.5/9.0 s). Hold frames are static, apart from slow drift right before a transition.
- **UI cards**:
  - Dark card: bg `#121414` on `#0B0D0D`, size ~800×420 (74% width), radius ≈ 44–48 px, **1–2 px light rim** `#353838` (brighter top-left, fading), soft drop shadow, and **3D perspective tilt** (≈ rotateY −4°, rotateX 2°, the right edge slightly shorter). Inner padding ~40 px. Icon row: GitHub mark 92 px + repo name 40 px Regular white.
  - Light card: bg `#F3F5F5` on white, radius ≈ 56 px, **3–4 px blue gradient border** (`#257CFA` → transparent/light at top-right), soft 30–40 px shadow `rgba(0,40,120,.10)`, the same 3D tilt. Dashed inner input box (2 px dashed `#9A9C9C`, radius 28). Primary button `#257CFA`/`#2B7FFF`, radius ~28, white SemiBold 46 px label.
  - Frosted-glass pill cards (navy scene): translucent `rgba(255,255,255,0.08)` with backdrop blur, 2 px white/40% rim, radius ~40, 680×200.
  - Chips: tiny coloured pills (blue/purple/pink/cyan) with an icon glyph + label.
  - Dashed connectors: 3 px dashed white/50% curved lines between cards / icons.
  - Cursor: macOS black arrow with a white outline, moves and clicks.
- **Camera**: no global zoom or parallax during holds. Movement only happens in transitions (push/zoom-through) and in the hook (slight upward drift, ~40 px over 0.9 s).

---------------------------------------------------------------------
## 6. Transitions (all measured at 60 fps)

Every scene change is the same family: a **"blur-push dissolve"**.
1. The outgoing layer translates in a direction, accelerating (≈ 150–300 px), while getting a Gaussian/motion blur of 0 → 25 px and fading out.
2. The BG cross-fades linearly to the new BG.
3. Incoming elements arrive from the opposite side, decelerating, blurred → sharp. The new headline's first word is already blurring in during the tail.

| time | frames | from → to | direction / flavour |
|---|---|---|---|
| 1.92–2.33 | 25 | curtain → white | zoom-through (icons scale up ~1.3× + blur), BG red → grey → white |
| 3.67–3.95 | 17 | white → dark | outgoing GitHub exits left, incoming Claude icon enters from the right (horizontal push) |
| 11.20–11.60 | ~24 | dark → white | content drifts down + blur; coins drop in from the top |
| 13.67–13.93 | 16 | white → dark | push |
| 17.77–18.00 | 14 | dark → dark | blur swap (BG constant) |
| 23.33–23.67 | 20 | dark → purple | blur dissolve |
| 27.72–27.98 | 16 | purple → white | outgoing cards drift **down** ~275 px (at 1080) + blur; new headline comes from above |
| 33.30 | ~8 | white → white | in-place blur swap of headline + card |
| 35.80–36.07 | 17 | white → navy | push |
| 39.72–39.95 | 14 | navy → dark | blur dissolve |
| 42.07–42.43 | 22 | dark → white | blur + zoom |
| 46.38–46.62 | 15 | white → lavender | blur swap |
| 50.73–51.43 | ~40 incl. tail | lavender → dark | slower dissolve |
| 52.88–52.93 | 4 | dark → dark | quick blur swap into the CTA |

- Typical length is **15–17 frames (≈ 0.27 s)**, 14–25 frames overall.
- BG luma moves linearly across the window.
- Outgoing motion is ease-in, incoming is ease-out. Combined, it feels like expo.inOut centred on the cut.
- Total: 14 transitions in 58 s, all from this family. There are no wipes, no glitches, no flashes and no shape transitions.

---------------------------------------------------------------------
## 7. Sync with voice

- A transition is centred on the **first word of the next sentence**:
  - transition 27.72–27.98, "Пишешь" at 27.94
  - 35.80–36.07, "Проверяешь" at 36.02
  - 23.33–23.67, "Работаешь" at 23.46
  - 1.92–2.33, "Начни" at 2.14
- Rule: the transition starts about 0.2 s before the sentence onset and ends just after it, inside the breath pause (audio RMS falls to −50 dB there).
- Headline words start appearing **+0.10–0.15 s after the spoken word onset** and are fully sharp at about +0.3 s ("нужны" 0.00 → visible 0.10, sharp 0.35; "плагины" 0.30 → 0.43–0.66).
- Text is **summarised keywords, not literal subtitles**. From each sentence 2–4 key words are chosen ("Нужны плагины для Claude или Codex?" → `нужны плагины?` + labels Claude / или / Codex). The caption line carries a second paraphrased fragment of the same sentence ("которую нейросеть обрабатывает во время работы").
- Labels and captions type in slightly after the matching phrase, as a "footnote".

---------------------------------------------------------------------
## 8. Audio

- Integrated loudness **−14.1 LUFS**, **LRA 1.6 LU** (heavily compressed / limited), true peak about −2.8 dBFS. **Mono** (L−R = −inf).
- **No music bed**: RMS between phrases is about −50 dB (median of 85 gaps). The 150 Hz low-pass in the gaps reads −48 dB.
- **No SFX**: no whooshes, pops or risers. Above 6 kHz, every energy peak coincides with speech sibilants; at transitions the 6 kHz+ band sits at −82 dB.
- Voice: clean, close, bright, consistent level, fast delivery (164 wpm). Gaps are gated almost to silence. It sounds possibly like a TTS / voice-clone or a heavily processed VO; it has a neutral "narrator" feel.
- Implication: the pacing and the premium feel come entirely from the visuals plus the dense VO. Recreate it with **VO only**, normalised to −14 LUFS.

---------------------------------------------------------------------
## 9. Secret sauce

1. **Alternating dark/white canvases**: every scene flips luminance, so every transition reads as a "page turn" even without SFX.
2. **Blur everywhere**: words, characters, icons and whole scenes enter and exit through a Gaussian/motion blur, never a plain fade. That gives a camera-focus, optical feel.
3. **Off-white and off-black**: `#FBFDFD` and `#0B0D0D` with faint 24–36 px dot grids, not #FFF / #000. A naive build looks flat and digital without them.
4. **Lowercase headlines, at most 2 short lines, tight leading (1.05)**, in a Google-Sans-like grotesk. Large type with plenty of negative space.
5. **One hero 3D clay/glossy object per scene**, centred, with a soft contact shadow. These are consistent AI-rendered assets, not flat icons or emoji.
6. **Two text-reveal grammars**: headline = per-word blur-rise; secondary = 24 cps typewriter with a soft leading glyph. Mixing them gives clear hierarchy.
7. **UI cards with a subtle 3D perspective tilt** and a 1–2 px light rim, which makes the mock-ups feel physical.
8. **Transitions only in breath pauses**, centred on the next sentence onset, so the visuals breathe with the voice.
9. **No reflow**: lines are laid out in their final positions, and words or chars appear in place.
10. **No music and no SFX**, which a naive recreation would add; the restraint is part of the premium tone.

What a naive build would get wrong:
- fading text without blur
- capitalising headlines
- pure white/black BGs
- flat icons
- hard cuts or slide transitions without blur
- adding whooshes or a music bed
- centred typewriter text that reflows as it grows
- headlines that are literal subtitles

---------------------------------------------------------------------
## 10. Reproducible spec (HyperFrames / GSAP)

```css
:root{--bg-dark:#0B0D0D;--bg-light:#FBFDFD;--ink-dark:#FFFFFF;--ink-light:#000000;
  --cap-dark:#767878;--cap-light:#686B6B;--sub-dark:#E2E0E8;--card-dark:#121414;--card-light:#F3F5F5;--accent:#257CFA;}
.stage{width:1080px;height:1920px;font-family:"Google Sans Flex","Onest",sans-serif;}
.dots-dark{background:radial-gradient(circle,rgba(255,255,255,.07) 1.5px,transparent 1.6px) 0 0/36px 36px, var(--bg-dark);}
.dots-light{background:radial-gradient(circle,rgba(0,0,0,.05) 1.5px,transparent 1.6px) 0 0/24px 24px, var(--bg-light);}
.headline{position:absolute;top:27%;width:100%;text-align:center;font-weight:650;font-size:78px;line-height:1.06;letter-spacing:-.01em;text-transform:lowercase;}
.headline.long{font-size:64px;}
.caption{position:absolute;top:72%;width:100%;text-align:center;font-weight:400;font-size:45px;line-height:1.18;color:var(--cap-dark);}
.label{font-size:45px;font-weight:400;color:#E4E1E2;}
.card{border-radius:46px;background:var(--card-dark);box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.14),0 30px 60px rgba(0,0,0,.35);
  transform:perspective(1400px) rotateY(-4deg) rotateX(2deg);padding:40px;width:800px;}
.card.light{background:var(--card-light);box-shadow:0 0 0 3px rgba(37,124,250,.85),0 30px 60px rgba(0,40,120,.10);}
.icon-tile{width:223px;height:223px;filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));}
```

```js
// 1) Headline word (per spoken word, start = wordStart + 0.10)
tl.fromTo(word,{opacity:0,y:28,filter:"blur(12px)"},{opacity:1,y:0,filter:"blur(0px)",duration:0.30,ease:"power3.out"},t);

// 2) Label / caption typewriter (chars pre-split, laid out at final positions)
tl.fromTo(chars,{opacity:0,filter:"blur(6px)"},{opacity:1,filter:"blur(0px)",duration:0.06,ease:"none",stagger:0.042},t);

// 3) 3D icon pop (siblings staggered 0.10 s)
tl.fromTo(icons,{scale:0.1,opacity:0,filter:"blur(10px)"},{scale:1,opacity:1,filter:"blur(0px)",duration:0.28,ease:"back.out(1.3)",stagger:0.10},t);
//    variant: rise from below
tl.fromTo(hero,{y:420,filter:"blur(14px)"},{y:0,filter:"blur(0px)",duration:0.32,ease:"expo.out"},t);

// 4) Card entrance (tilted UI mock-up)
tl.fromTo(card,{y:80,opacity:0,filter:"blur(16px)",rotateX:8},{y:0,opacity:1,filter:"blur(0px)",rotateX:2,duration:0.40,ease:"power3.out"},t);

// 5) Scene transition "blur-push dissolve" (centre it on the next sentence onset; D = 0.28 s)
tl.to(outScene,{y:260 /*or x:-300*/,filter:"blur(24px)",opacity:0,duration:0.28,ease:"power2.in"},tc-0.18)
  .fromTo(inBG,{opacity:0},{opacity:1,duration:0.28,ease:"none"},tc-0.18)
  .fromTo(inScene,{y:-160,filter:"blur(20px)",opacity:0},{y:0,filter:"blur(0px)",opacity:1,duration:0.32,ease:"expo.out"},tc-0.05);
//    hook->scene2 variant: outScene {scale:1.3, filter:"blur(28px)"} (zoom-through)
```
