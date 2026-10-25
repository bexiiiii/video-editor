# Der0UBDNBmZ: style teardown (zaytsevtech, "ИИ умнее всего человечества…")

How this was measured: 1080x1920, 60 fps, 59.24 s. Colours and positions come from pixel sampling of full-res frames, with a 5x5 average for colours. Motion comes from 30 fps strips (`tr_*.jpg`) and 60 fps row-profile tracking. Audio was measured with ebur128 and 50 ms RMS windows. Word timings come from `transcript.json`. All px values are at 1080 width. "%H" is the y position as a share of frame height.

---

## 1. Format and structure

- **Faceless motion graphics with voice-over.** There is no talking head. The only "person" is a cut-out PNG of Musk, shown as a centred half-body photo or a circular avatar.
- **Density.** There are 16 scenes in 59 s, so the average scene lasts about 3.7 s (range 1.5 to 7 s). Inside a scene, something new appears roughly every 0.8 to 1.2 s.
- **Voice.** 158 words at 160 wpm. Speech ratio is 0.89, meaning sentence gaps are trimmed to about 0.3 to 0.5 s.
- **Detected hard cuts:** only 2.05 s and 3.72 s. Every other change is a motion transition (see section 6).

| # | t (s) | BG | Content (on-screen text in quotes) | Entry transition |
|---|---|---|---|---|
| 1 | 0.00–2.05 | dark | tiny label «прогноз Маска» (y 16%), giant «ИИ» (y 27–47%), «УМНЕЕ» (y 53%), lime italic «всего человечества» with a double underline (y 60%) | starts mid-reveal on frame 0 |
| 2 | 2.05–3.55 | white | «сотни миллионов / роботов» (y 4–6% in the strip, about 8%H). One 3D robot, then the camera zooms out into an endless robot grid (3 → 5 → 9 columns in 0.5 s) | hard cut on the word «сотни» |
| 3 | 3.55–7.20 | dark | «Илон Маск» / «ожидает к» above a Musk cut-out (y 37–100%). At 5.4 s the stack reflows up about 30 px and «2031» drops in (spoken at 5.46) | white panel slides off to the left with horizontal motion blur (about 130 ms); dark scene blurs in behind it and Musk scales from about 0.9 to 1.0 |
| 4 | 7.20–11.40 | dark | «Forbes» wordmark (serif, y 30%), giant white „ quote glyphs, quote text in 4 lines, circular avatar plus «Илон Маск / перевод» | vertical whip up |
| 5 | 11.40–18.45 | white | Diagram: «ИИ ⟨avatar⟩ люди» row, «прогноз Маска» with a small 3D icon, a dotted lens-shaped connector, left card «цифровой интеллект / за 5 лет» (appears 15.0), right «все» with a 3D people icon, bottom «превзойдёт всех людей» | luminance crossfade dark→white; the avatar is a **shared element** that flies and scales into the new layout |
| 6 | 18.45–24.00 | white | «второй прогноз / касается ⟦роботов⟧» (dark pill). Robot (idle bob), caption «по оценке Маска» (20.5), counter «100 млн» plus pill «минимум» (22.6–23.1) | whip up |
| 7 | 24.00–27.40 | navy with light rays | «100 млн» → dashed curve → blue chip «возможно» → «1 млрд» → caption «человекоподобных машин» | crossfade plus whip |
| 8 | 27.40–30.30 | white | «Маск ожидает», «резкий рост» morphs to «рост экономики», then a gradient progress bar fills left to right | luminance crossfade navy→white, content blurs and drifts up |
| 9 | 30.30–33.25 | dark | «экономика может / удвоиться», line chart (grey baseline «сейчас», blue line with «2×»), «5–7 лет», caption «сценарий по прогнозу Маска» | luminance crossfade; the progress bar persists, slides up and dissolves |
| 10 | 33.25–36.00 | dark | Glass cards «роботы / собирают» → curved dotted label «сборка» → «продукция / готовая продукция». A dashed path runs down and the camera follows it | whip up |
| 11 | 36.00–38.20 | dark | «рядом / другой» (large), cards «производство / выпускает» and «сами роботы / человекоподобные», curved label «выпуск» | camera continues along the dashed path |
| 12 | 38.20–40.90 | green with light rays | «ИИ помогает управлять», blue chip «✕ ИИ», dashed tree to 2 cards, caption «двумя направлениями производства» | luminance crossfade dark→green, old cards slide **down** |
| 13 | 40.90–43.90 | dark | «масштаб автоматизации», 2 cards → «2×» → «экономика · прогноз Маска» | crossfade green→dark |
| 14 | 43.90–46.50 | dark | «Маск допускает / погрешность», «2031», text-selection highlight over «в несколько лет», caption «по его оценке» | whip **down**: old scene exits down, new one drops in from the top |
| 15 | 46.50–50.40 | white | «2031», «как его», pill «ориентир» (49.7) | luminance crossfade dark→white |
| 16 | 50.40–53.80 | dark | «сроки сдвинутся / остаётся вопрос» with karaoke-style line emphasis, «для человечества» | horizontal push left plus luminance crossfade |
| 17 | 53.80–59.24 | dark | «какие задачи / мы сможем выполнять», blue particle globe with 2 orbit ellipses, «в большем объёме?» | whip down |

**Hook (0–3 s).**
- Frame 0 already shows «ИИ» at about 20% opacity with heavy blur. There is no empty frame and no logo.
- The two letters of «ИИ» resolve with a per-letter stagger of about 70 ms. They are crisp by 0.47 s.
- «УМНЕЕ» starts at 0.30 s and «всего человечества» at about 0.65 s. This lands with the spoken words «умнее» at 0.38 and «всего» at 0.94.
- At 2.05 s there is a hard cut to pure white with the robot. This is the only black→white hard cut in the video: the contrast flip is the pattern interrupt.
- The robot multiplication (one robot becoming an endless grid) visualises «сотни миллионов».
- So inside 3.5 s the viewer gets 3 different visual ideas.

**Ending.**
- There is no CTA, logo or subscribe card.
- The video ends on an open question (rendered as text «в большем объёме?») over the slowly rotating globe, and cuts out at 59.24 s right after the last word, «машины?», at 58.72.
- The question works as the engagement hook.

---

## 2. Backgrounds

There are **4 colour themes** and the video alternates between them. Dark is used about 55% of the time, white about 30%, and colour light-ray scenes about 15%.

| Theme | Value |
|---|---|
| Dark (base) | **#0B0D0D** flat. The slight green/cyan tint is consistent, so this is not pure black. No vignette (corners equal centre). |
| Light | **#FBFDFD** flat (same cyan tint) |
| Navy light-ray | Base #131A43. Diagonal soft beams from the top-left: #5967CA at the corner, #4A55AA at (200,200), #353E88 at (300,500). Beams run at about 35–40° from vertical, 2–3 parallel bands, soft-edged. |
| Green light-ray | Base #052F21 / #063022. Beams #2DA371 at the corner → #23875D → #166648. Same geometry as navy. |

**Dot-grid texture.** It is on every flat background and is barely visible, but it gives a "canvas / Figma board" feel.
- Dark: dots about 4 px, **36 px pitch**, peak colour #2D2F2F on #0B0D0D (about +13% luminance). Example dot centres x = 73, 109, 145…
- Light: dots about 5 px, **24 px pitch**, colour #DADDDD on #FBFDFD.
- The grid is static. It moves with the camera during path-follow moves.

**How backgrounds change.** A background never changes by hard cut (except at 2.05 s). It changes by a **luminance crossfade of about 250 ms** (15 frames at 60 fps): the full-frame colour tweens linearly through the greys, for example #F6F9F9 → #838585 → #0B0D0D over 30.25–30.50. Content moves at the same time (section 6). The background changes 12 times in 59 s.

---

## 3. Typography

| Role | Font (closest) | Size at 1080w | Weight | Colour | Notes |
|---|---|---|---|---|---|
| Main headline | **Google Sans / Google Sans Flex** (fallbacks: Onest, Manrope, Product Sans) | ≈72 px cap (6.7% W). Measured glyph box cap→descender 67 px. Line pitch 84 px → line-height ≈1.15 | 500 (Medium) | #FBFDFD on dark, #0B0D0D on white | Lowercase sentence case, centred, 1–2 lines, ≤22 chars/line, letter-spacing 0 to −0.01em |
| Hero number («2031», «5–7 лет», «100 млн», «1 млрд») | Google Sans | ≈100–108 px (cap height 74–77 px) | 500 | same | Counters roll (slot style) |
| Large statement («рядом другой») | Google Sans | ≈90 px | 500 | white | 2 short lines |
| Caption / footnote | Google Sans | ≈40–44 px (glyph box 31–42 px) | 400–500 | white on dark (#F4F4F4). Mid-grey #7A7A7A on white («по оценке Маска») | Always at **y ≈ 74–80%** |
| Secondary / dimmed line | Google Sans | same as headline | 500 | #6C7474 (about 45% white) | Used for karaoke emphasis (scene 16) |
| Top micro-label «прогноз Маска» | Google Sans | ≈24 px | 500 | #8A8A8A | Letter-spacing about +0.08em, y 16% |
| Hook display «ИИ» | **Unbounded 900** / Benzin ExtraBold (ultra-wide grotesk) | Cap 392 px (≈540 px font). Block 786 px wide = 73% W | 900 | #F4F4F4 | Caps |
| Hook «УМНЕЕ» | same wide grotesk | Cap 93 px, width 454 px | 800 | #F4F4F4 | Caps |
| Hook accent «всего человечества» | Bold italic with cursive Cyrillic forms (PT Sans Bold Italic / Montserrat ExtraBold Italic) | ≈56 px | 700–800 | **#BAE436** lime | Rotated about −5°, two thin lime underlines (2 px) offset 20 and 40 px below and shorter, like a hand-drawn emphasis |
| Card title / subtitle | Google Sans | 52 px / 34 px | 500 / 400 | #FBFDFD / #6E7070 | Inside glass cards |
| Forbes wordmark | Forbes logo (Didone serif) | ≈140 px cap | n/a | white | Logo asset |

**Layout grid.** It is a 3-tier vertical stack, all centre-aligned on x = 540:
- headline at **y 22–30%**,
- hero visual at **y 40–65%**,
- caption at **y 74–80%**.

Side margins are at least 100 px. Text never goes closer than about 110 px to the left or right edge.

**On screen at once.** Typically 2–6 headline words plus a 2–4 word caption. Never a paragraph, except the Forbes quote (4 lines at ≈30 px, deliberately "document-like").

---

## 4. Text animation (measured)

1. **Word blur-in (default).**
   - Each word: opacity 0→1, blur about 16 px→0, y +20 to 30 px→0, scale 0.96→1.
   - Duration about 350–450 ms, ease out (expo/power3).
   - Stagger between words in a headline is about 80–120 ms (for example «для» → «человечества»).
   - On a fresh scene the whole headline usually lands in about 0.4–0.6 s, before the matching words are spoken.
2. **Per-letter variant (hook only).** «ИИ»: each letter fades and un-blurs from blur 20 px / opacity 0.2 with a 70 ms letter stagger and about a 30 px rise. Fully crisp at 470 ms.
3. **Rolling counter.** «100 млн» and later «0%»-type numbers:
   - Digits scroll vertically with motion blur (slot machine), about 350 ms, ease out.
   - The unit «млн» fades and blurs in about 50 ms after the digits.
4. **Pill wipe.** «роботов», «ориентир», «минимум»:
   - A rounded dark pill (#141414 to #1C1C1C on white, radius = height/2) grows left→right as a clip reveal.
   - It starts rotated about −8° and straightens to 0°.
   - Text is white inside the pill. About 300–400 ms, ease out.
5. **Text-selection highlight.** «в несколько лет»:
   - Mimics a macOS/Figma text selection: fill #1C3C5C behind white text.
   - Blue caret handles (#2A90F6): a 2 px vertical bar with a 10 px dot on top-left and bottom-right.
   - The selection sweeps left→right over about 300 ms (9 frames) with the end handle travelling with it.
6. **Karaoke line emphasis.** Two stacked lines. The line currently being spoken is #FBFDFD and the other drops to #6C7474, crossfading over about 200 ms.
7. **Word swap.** «резкий рост» → «рост экономики»: the old word blurs out and the new one blurs in at the same spot.
8. **Layout reflow.** When a new line is added, existing lines glide up by about 20–30 px over about 400 ms (ease out) instead of jumping. Example: the Musk header at 5.4 s.

**Exit.** Text never exits on its own. It leaves with the whole scene during the transition (blur, move, fade).

---

## 5. Graphics and objects

- **3D icons.**
  - Glossy cartoon robot in blue #1EB4F6 / #069CF6 with black visor and cyan eyes. About 240 x 310 px at centre (y 57–73%).
  - Microsoft Fluent-3D-style emoji (factory conveyor, gear, robot hand, people, small book stack), about 60–110 px, used inside cards and chips.
  - No outlines. Soft natural shading. No added drop shadow on dark; a very soft one on white.
- **Idle motion.** The robot bobs ±8 px vertically and ±4 px horizontally over a period of about 3 s (sine). The globe rotates slowly (about 10°/s) and its orbit ellipses precess. Other elements hold still.
- **Glass cards (dark scenes).**
  - About 600 x 172 px, radius about 24 px.
  - Fill equals the background (transparent).
  - Inner glow: white about 20% fading to 0 over about 22 px inward (inset shadow).
  - Border 2–3 px, bright #DDDFDF / #E7E9E9 on the top and bottom edges, dimmer #929494 on the sides (a gradient stroke, like a lit glass edge).
  - Icon on the left (≈110 px), title 52 px white, subtitle 34 px grey.
  - Cards are offset diagonally (the second card shifted right by about 200 px and down by about 150 px), joined by a dotted curved connector with a rotated tiny label («сборка», «выпуск»).
- **Light cards (white scenes).** «цифровой интеллект» card: white, radius 16, 1.5 px #DADADA border, soft shadow 0 6px 20px rgba(0,0,0,.08).
- **Chips.** Blue «возможно» and «✕ ИИ» chips: fill #2C7CF4, radius full, white 30 px Medium text, 1 px lighter top highlight.
- **Connectors.** Dashed lines 2 px, dash 10 / gap 10, colour #3A3D3D on dark and #CFCFCF on white. Dotted connectors use 4 px dots and 12 px gaps. They draw on with a stroke-dashoffset reveal (about 400 ms).
- **Charts.**
  - Line chart: baseline 2 px #6E7070 with a dot end and label «сейчас».
  - Rising line 3 px #0084F0 with a 10 px dot and «2×» in #0084F0 at 56 px Medium.
  - Under the line there is a soft blue-to-transparent area fill (10% opacity).
  - The line draws left→right (about 500 ms).
- **Progress bar.** About 800 x 26 px, radius full, track #E6E8E8. Fill is a gradient #1C74F4 → #3CA4FC → #ACE4FC → #1C74F4 with a moving highlight band (shimmer). It fills over about 2 s.
- **Musk photo.** Clean cut-out (no background), centred and bleeding off the bottom (y 37%→100%), about 650 px wide. No border or shadow. Small scale-up on entry, about 0.9→1.0 over 0.4 s.
- **Avatar.** Circle about 130 px (on white) or 100 px (in the quote). Light grey #E5E5E5 background behind the cut-out, no border.
- **Particle globe.** Sphere about 650 px wide made of about 2000 tiny blue dots (#2A6A9A to #3B8BD0, 2 px), plus 2 thin (1.5 px) #2A4A6A orbit ellipses tilted about ±20°. Rotates slowly.
- **Camera.**
  - The zoom-out into the robot grid (scale about 3→1 over 0.5 s) is an infinite-grid reveal.
  - Path-follow in scenes 10–11: the canvas translates up along a dashed line so the camera "travels" from card to card.
  - There is no constant drift: holds are static.

---

## 6. Transitions between beats

| Type | Measured timing | Count | Notes |
|---|---|---|---|
| **Vertical whip (up)** | Exit: content accelerates up about 300 px in **150 ms** (ease in) with vertical motion blur. Entry: new content arrives at +270 px below its final position and decelerates (deltas 48, 48, 28, 32, 28, 16, 20, 12, 8…) over about **400 ms** (expo.out). Total about 0.55 s. | 4 (7.2, 18.45, 33.25, part of 24.0) | The background stays the same |
| **Vertical whip (down)** | Mirror of the above | 3 (38.2, 43.9, 53.8) | Gives variety |
| **Luminance crossfade plus content move** | BG colour tween **250 ms**. Old content blurs (0→12 px), fades and drifts about 40–80 px. New content enters from about +250 px with blur and decelerates over about 350 ms. | 7 (11.4, 24.0, 27.4, 30.3, 38.2, 40.9, 46.5) | Often keeps one **shared element** (avatar at 11.4, progress bar at 30.3) |
| **Horizontal slide/push** | About 130–200 ms, horizontal motion blur, new content from the right | 2 (3.55, 50.4) | |
| **Hard cut** | 0 frames | 1 (2.05) | Hook pattern interrupt |

- Transitions always sit **inside speech pauses**. The RMS at every transition is −45 to −49 dB, which is the noise floor.
- The new scene settles right at the next sentence onset.

---

## 7. Sync with voice

- **Not literal subtitles.** On-screen text is a keyword paraphrase. For example the voice says «По его оценке, за тот же срок их может стать минимум 100 миллионов» and the screen shows «по оценке Маска» … «минимум» … «100 млн».
- **Scene headline.** It appears at the start of the sentence (lead 0.3–0.8 s) as a summary.
- **Hero tokens.** Numbers, pills and icons are frame-synced to the spoken word within about ±0.1 s:

| Token | Visible | Spoken |
|---|---|---|
| «2031» | 5.40 | 5.46 |
| «100 млн» | 23.0 | 23.06 |
| «возможно» | 24.2 | 24.16 |
| «1 млрд» | 24.9 | 24.82 |
| «человекоподобных машин» | 25.7 | 26.12 |
| «ориентир» | 49.7 | 49.76 |
| robot grid | 2.4 | «миллионов» 2.56 |

---

## 8. Audio

- **Voice only. No music bed and no SFX.**
- Every sentence gap drops to −45 to −49 dBFS RMS, which is the noise floor. Transitions make no whoosh: the 5 kHz+ band shows only sibilant peaks.
- Integrated loudness **−14.1 LUFS**, LRA **1.7 LU** (heavily compressed and limited). The voice has a broadcast or podcast feel: close-miked, de-essed, possibly AI-cleaned or TTS-like even delivery at 160 wpm.
- Pauses are trimmed to about 0.3–0.5 s.

---

## 9. Secret sauce

1. **Tinted neutrals.** The backgrounds are #0B0D0D and #FBFDFD (cyan-tinted), not #000 or #FFF. Text uses the opposite neutral. It reads "designed".
2. **36 px dot grid at about 13% luminance.** You only feel it, but without it the dark frames look like empty slides.
3. **Motion blur on every transition and entry.** Directional blur matched to velocity, plus a Gaussian blur-in on every word. A naive recreation would use plain fades and slides and look cheap.
4. **Very fast transitions (150 ms exit) with long expo settles (400 ms).** The snap then glide is the premium feel. Linear or ease-in-out at 600 ms would feel slow.
5. **Theme alternation dark ↔ white ↔ colour-ray every 3–4 s,** done as a luminance crossfade, often with one persisting shared element (avatar, progress bar) for continuity.
6. **One idea per scene, 3-tier centred stack,** big quiet type (Medium weight, not Bold) and lots of empty space. Hero numbers about 104 px, headlines about 72 px, captions about 42 px: a ratio of roughly 2.5 : 1.7 : 1.
7. **UI metaphors** (text-selection handles, chips, glass cards, dashed flow paths) make abstract statements feel like a product demo.
8. **Hero tokens hit on the syllable.** Everything else leads the voice, so the viewer reads first and then hears confirmation.
9. **Silence is used:** no music. Transitions fall in pauses, so the cut rhythm is the speech rhythm.

**What a naive recreation gets wrong:**
- pure black or white backgrounds;
- Bold or Black weights for headlines (they are Medium);
- uppercase text;
- adding music and whooshes;
- slow crossfades;
- literal word-by-word subtitles;
- text exiting on its own;
- missing motion blur;
- forgetting that numbers roll;
- placing captions at the very bottom instead of at about 77%.

---

## 10. Reproducible spec (HyperFrames / GSAP)

```css
:root{--dark:#0B0D0D;--light:#FBFDFD;--dim:#6C7474;--blue:#0084F0;--chip:#2C7CF4;--sel:#1C3C5C;--handle:#2A90F6;--lime:#BAE436;}
.scene{width:1080px;height:1920px;background:var(--dark);
  background-image:radial-gradient(circle,#2D2F2F 2px,transparent 2.5px);background-size:36px 36px;background-position:-1px -1px;}
.scene.light{background-color:var(--light);background-image:radial-gradient(circle,#DADDDD 2.5px,transparent 3px);background-size:24px 24px;}
.scene.navy{background:linear-gradient(135deg,#5967CA 0%,#353E88 18%,#222864 38%,#131A43 60%);} /* plus 2-3 blurred white beams at 35deg, opacity .12 */
.scene.green{background:linear-gradient(135deg,#2DA371 0%,#166648 22%,#0A4A33 40%,#052F21 62%);}
.h1{font:500 72px/1.15 "Google Sans Flex","Onest",sans-serif;letter-spacing:-0.01em;color:var(--light);text-align:center;position:absolute;left:110px;right:110px;top:24%;}
.hero{font:500 104px/1 "Google Sans Flex";top:45%;}
.cap{font:500 42px/1.2 "Google Sans Flex";top:76%;}
.pill{background:#151515;color:#fff;border-radius:999px;padding:0 .35em;display:inline-block;}
.glass{width:600px;height:172px;border-radius:24px;border:2.5px solid rgba(225,228,228,.9);
  box-shadow:inset 0 0 22px rgba(255,255,255,.18);background:transparent;}
.sel{background:var(--sel);box-shadow:-3px 0 0 var(--handle),3px 0 0 var(--handle);} /* plus 10px dots at the TL and BR corners */
```

```js
// 1) Word blur-in (headline/caption). Split into words.
tl.from(words,{opacity:0,y:26,scale:.96,filter:"blur(16px)",duration:.42,ease:"expo.out",stagger:.09},t);

// 2) Scene whip-up transition (old -> new), BG constant
tl.to(oldScene,{y:-320,filter:"blur(10px)",opacity:0,duration:.15,ease:"power2.in"},T)
  .fromTo(newScene,{y:270,filter:"blur(14px)"},{y:0,filter:"blur(0px)",duration:.45,ease:"expo.out"},T+.15);
// For a direction-correct streak, add a vertical-only motion-blur SVG filter (feGaussianBlur stdDeviation="0 18") instead of uniform blur.

// 3) Luminance crossfade plus content move (dark <-> light)
tl.to(bg,{backgroundColor:"#FBFDFD",duration:.25,ease:"none"},T)
  .to(oldContent,{y:-60,opacity:0,filter:"blur(12px)",duration:.25,ease:"power1.in"},T)
  .from(newContent,{y:250,opacity:0,filter:"blur(14px)",duration:.4,ease:"expo.out"},T+.22);
// Shared element: FLIP the avatar/bar from old rect to new rect, .5s, "expo.inOut".

// 4) Pill wipe on a keyword (sync to the word's start time)
tl.fromTo(pill,{clipPath:"inset(0 100% 0 0 round 999px)",rotate:-8},
               {clipPath:"inset(0 0% 0 0 round 999px)",rotate:0,duration:.35,ease:"power3.out"},wordT);

// 5) Rolling counter "100 млн" (digit column translateY), then unit blur-in
tl.fromTo(digitCols,{yPercent:-900},{yPercent:0,duration:.38,ease:"power3.out",stagger:.03},wordT)
  .from(unit,{opacity:0,filter:"blur(10px)",x:-10,duration:.3,ease:"expo.out"},wordT+.05);

// Extras
// Selection: tl.fromTo(selBox,{scaleX:0,transformOrigin:"0 50%"},{scaleX:1,duration:.3,ease:"power2.out"}); move the end handle with it.
// Reflow:    tl.to(stackAbove,{y:"-=28",duration:.4,ease:"expo.out"},t);
// Idle bob:  gsap.to(robot,{y:"+=8",x:"+=4",duration:1.5,ease:"sine.inOut",yoyo:true,repeat:-1}). In seek-safe HyperFrames, express this as a sin(t) keyframe.
// Hook per-letter: tl.from(letters,{opacity:.2,filter:"blur(20px)",y:30,duration:.47,ease:"power2.out",stagger:.07},0); start at t=0 already partially visible.
```
