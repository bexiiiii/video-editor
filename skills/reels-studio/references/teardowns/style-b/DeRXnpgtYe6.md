# DeRXnpgtYe6 — "30 kunlik kontent 20 daqiqada" (Barbers example) — forensic style report

Source: refs/DeRXnpgtYe6.mp4 · 1080×1920 · 25 fps · 56.28 s · AAC 44.1 kHz.
Faceless motion graphics + Uzbek voiceover (131 wpm, speech ratio 0.87). No footage, no talking head, no photos — only UI cards + Apple emoji.
Measured from full-res frames (f_*.png, x_*.png, seq/ in this folder) by pixel sampling; px values are at 1080 w. ±2 px / ±1 frame unless noted.

---------------------------------------------------------------------------------------------------

## 1. Format & structure

One continuous "Apple keynote / iOS widget" canvas. The only hard cuts (cuts.txt 56.12/56.20) are inside the end glitch. Every scene change is a ~0.6 s scale-down crossfade, and the background theme flips **dark → light → dark → light → blue → light → dark**. Each topic gets its own theme.

| # | t (s) | Theme | Kicker (light grey) | Headline (bold) | Body / components | VO anchor (word start) |
|---|---|---|---|---|---|---|
| 0 | 0.00–0.20 | dark | — | — | Leftover fade-out of the previous clip ("…bosh qotirasizmi?"). The reel opens mid-crossfade, which works as a loop seam. | — |
| 1 HOOK | 0.20–3.80 | dark #1A1A1C | "Hozir" | — | Widget A "Kontent 📅 / **30** / kun": a counter rolls 0→30. Widget B: a ring that draws, "**20** daqiqa". Under them: "tayyorlashni o'rgataman". | "30" 0.36 · "yigirma" 2.1 · "o'rgataman" 3.6 |
| T | 3.80–4.40 | →light | | | scale-down crossfade | |
| 2 | 4.40–13.60 | light #F3F3F5 | "Masalan," | "barbersiz 💈" | Sub "Sohangizni 6 bo'limga ajrating", then a 2×3 grid of 6 category cards (emoji + 01…06 + label), one per spoken word | "Masalan" 4.3 · "barbersiz" 4.9 · cards 7.8/8.8/9.3/10.4/11.1/12.0 |
| 3 | 13.60–15.40 | light | "Endi bittasini olaylik" | — | The other 5 cards fade out. The "Soqol" card moves to centre and grows (FLIP), gets a 2–3 px blue border, and a blue pill "1 ta bo'lim = 5 ta video" pops in under it | "Endi" 13.8 · "Saqol" 15.3 |
| T | 15.40–16.05 | →dark | | | | |
| 4 | 16.05–19.90 | dark | "Birinchi video" | "maslahat" | Dark card "💡 Maslahat 1/5" (green). Quote «Yuzingizga mos soqol shaklini qanday tanlaysiz?». The green progress bar fills linearly. Pagination dot 1 goes active. | "Masləxət" 16.7 |
| T | 19.90–20.40 | →light | | | | |
| 5 | 20.40–24.80 | light | "Ikkinchisi" | "xato" | White card "⚠️ Xato 2/5" (red bar). «Soqolni uyda tekislayotganda shaklini buzib qo'yadigan **3 ta xato»** (the last two words are red) | "xata" 21.1 · "uch" 24.4 |
| T | 24.80–25.40 | →dark | | | | |
| 6 | 25.40–29.90 | dark | "Uchinchisi" | "mif" | Dark card "🔴 Mif 3/5" (orange bar). «Soqolni tez-tez qirsangiz, qalinlashadi deyishadi. **Shu rostmi?»** (orange). Two pills "Rost / Mif" appear at 29.5 and Mif goes orange. | "mif" 26.2 · "rostmi" 29.6 |
| T | 29.90–30.50 | →light | | | | |
| 7 | 30.50–34.80 | light | "To'rtinchisi" | "savol-javob" | White card "💬 Savol-javob 4/5" (blue bar). Two grey iMessage bubbles, then a blue "•••" typing bubble | "savol" 31.2 · bubbles 32.1/33.8 |
| T | 34.80–35.50 | →BLUE | | | | |
| 8 | 35.50–42.30 | blue gradient | "Beshinchisi" | "real natija" | "Oldin" glass card (grey-tinted 🧔) — connector line — "Keyin" white card (✅ + ✨ + 🧔 in colour). Below: "Nega aynan shu shakl?" (semibold white), then a small "tushuntiring" | "real" 36.1 · "oldingi" 37.7 · "keyingi" 38.3 · "nega" 39.8 |
| T | 42.30–42.90 | →light | | | | |
| 9 | 42.90–50.90 | light | "Ko'rdingizmi?" | "Mavzu bitta" | Orbit diagram: a faint ring (r≈270) around a blue 200 px circle "🧔 Soqol". Five white label pills with coloured dots pop on the ring one at a time (Maslahat-green, Xato-red, Mif-orange, Savol-javob-blue, Natija-yellow). Bottom: "Format –" (grey), then "mavzuni qanday ochishingiz" (semibold black) | "Mavzu" 43.3 · pills 45.0–47.0 · "Format" 48.0 |
| T | 50.90–51.60 | →dark | | | | |
| 10 PAYOFF | 51.60–56.04 | dark | "6 bo'lim × 5 mavzu" | "30 ta kontent" (at the end) | Row of 6 category emoji, then a 6×5 grid of tiles filling column by column in Apple colours (green column first, since Soqol is the example), numbered 1–30. Then "30 ta kontent" and a small "tayyor". | "5 mavzu" 53.4 · "30" 55.0 · "kontent" 55.5 |
| END | 56.04–56.28 | | | | RGB-split / ghost-duplicate glitch over 6 frames (offset ~10–30 px, chromatic doubling) into the loop | — |

**Hook (0–3 s):** No title card. The first thing shown is a big number counting up (0→30 in about 0.75 s) while the VO says "30". Then a second widget's ring draws while the VO says "20". This is a "numbers-first" Apple-widget promise: "30 days of content in 20 minutes". The dark theme in the hook sets up the contrast for the light scene at 4.4 s.

**Ending:** No CTA card, no logo. The payoff grid ends on "30 ta kontent / tayyor", then a short glitch that loops back to the start.

**Persistent chrome (never animates out, adapts colour per theme):**
- Top-left two-line label at x=150. Line 1 is "Barberlar uchun" (24 px, SemiBold, cap-top y=187). Line 2 is "30 kunlik kontent" (24 px, Regular, cap-top y=221, so 34 px line pitch). Colour: grey #8E8E93-ish (#7E7E81 on light, #98989A on dark), pure white on blue.
- Top-right pagination: 5 dots, 8 px diameter, centres 22 px apart, right edge x=930, y=212. The active dot stretches into a 22×8 pill in #007AFF (#0077F5 measured); the others are grey #8B8B8D. In the intro (0–16 s) no dot is active. Dot n goes active when section n starts and moves with the scene transition. On blue, the active pill is white.
- A 130 px square grid texture on light and dark themes (see §2).

## 2. Backgrounds

All backgrounds are full-frame CSS-able gradients plus a faint line pattern. Nothing has texture or noise beyond video compression.

| Theme | Fill | Pattern |
|---|---|---|
| **Light** | Vertical linear gradient: #F7F7F7 (y=0) → #F5F5F7 (490) → #F3F3F5 (880) → #EFEFF2 (1140) → #ECECEE (1790) | Square grid with a 130 px pitch, lines at x = 20 + 130k and y = 50 + 130k. Lines are 1–2 px, colour ≈ #E2E2E5 on #EDEDEF (≈ rgba(0,0,0,0.035)). They fade slightly toward the bottom. The content column 150–930 sits exactly on grid lines. |
| **Dark** | #1A1A1C in the centre with a soft radial vignette: #171719 at the top, #131316 at the bottom (y=1790). A soft radial lift (≈ #1C1C1F) sits behind the main widget area. | Same 130 px grid, lines #222225–#232326 on #1A1A1C (≈ rgba(255,255,255,0.03)). |
| **Blue** (one "takeover" scene) | Vertical gradient: #1B88FB (flat to y≈300) → #1A7FEF (480) → #1877DE (720) → #176ECD (960) → #1466BB (1200) → #115BAD (1440) → #0F539A (1680) | No grid. Concentric circles centred at (540, 980) with radii 161·n, 1–1.5 px, ≈ rgba(255,255,255,0.06–0.08). They read like a radar or ripple. |

The bg changes only at scene transitions (§6). There is no drifting or parallax of the grid between transitions.

## 3. Typography

Font: **SF Pro Display** (Apple system; the "a", "t" and "y" shapes and the tight bold match). A web substitute is "Inter Display" or "Inter" with tighter tracking, but SF Pro gives the exact look. The Uzbek apostrophe is the typographic ʻ (o'/g' use U+02BB/U+2019).

Size is derived from measured cap/x-height. SF cap height is 0.705 em and x-height 0.53 em.

| Role | Example | Size | Weight | Colour | Notes |
|---|---|---|---|---|---|
| Kicker (scene label) | "Masalan," "Birinchi video" | **52 px** (cap 36 px) | Light (300) | light #7D7D7F · dark #9A9A9D · blue rgba(255,255,255,.72) | Centred. Cap-top y≈372–391, so the baseline is ~408–427. Sentence case. |
| Headline | "barbersiz" "maslahat" "savol-javob" | **108 px** (ascender 75–79, x-height 57–58) | Bold (700) | light #060609 (≈#000 at 98%) · dark/blue #FFFFFF | Centred. Baseline y≈540 (light, with kicker at 372) or ≈565 (dark). The kicker baseline sits 125–140 px above the headline baseline. Lowercase unless it starts a sentence. Tracking ≈ −0.02 em. One line only, max ~12 chars (≤ 780 px). An emoji can be attached top-right as a superscript (💈 at ~70 px, top aligned to the ascender, 25 px gap). |
| Subhead | "Sohangizni 6 bo'limga ajrating" | **44 px** (cap 31) | Light/Regular (300–400) | #7E7E81 | Baseline y≈624, ~85 px below the headline baseline |
| Big numeric | "30" "20" in the widgets, "30 ta kontent" | 30 in widget ≈ 150 px · 20 in ring ≈ 110 px · "30 ta kontent" **108 px** | Bold | #FFF | Tabular figures |
| Card title | "Soch kesish" "Soqol" | **36 px** (cap 26) | SemiBold (600) | #000 / #FFF | Left-aligned at card x + 24 |
| Card header label | "Maslahat" | **33 px** (cap 23) | SemiBold | #FFF / #000 | Next to a 70 px emoji circle |
| Card counter | "1 / 5", "01" | 22–30 px | Medium | #8E8E93 | Right-aligned |
| Card body quote | «Yuzingizga mos soqol shaklini qanday tanlaysiz?» | **48 px** (cap 34) | SemiBold/Medium (500–600) | #FFF on dark, #000 on light | Left-aligned. Line-height 70 px (1.45). Max ~28 chars per line, card text width ~714 px. Guillemets « » included. The emphasis words at the end are coloured with the section accent (red #FF3B30, orange #FF9500). |
| Callout line | "Nega aynan shu shakl?" "mavzuni qanday ochishingiz" | 54 px (cap 39) | SemiBold | #FFF / #000 | Centred |
| Small caption | "tushuntiring", "tayyor", "kun", "daqiqa" | 30–36 px | Regular | grey | |

Hierarchy is always: grey thin kicker → black/white heavy headline → component. The weight jump (300 → 700) together with the colour jump (grey → black) is the signature.

## 4. Text animation

- **Word-by-word reveal, synced to the VO.** Each word fades in with opacity 0→1, filter blur(10–12 px)→0 and translateY 8→0 px over **~120–160 ms (3–4 frames)**. Ease is power2.out/expo.out. Words are triggered on their spoken onset (±2 frames). Example: kicker "Birinchi" at 15.76 and "video" at 15.84; headline "maslahat" 16.68→16.80 (blurred at 16.72, sharp at 16.76).
- **Headline:** blur-in reveal, ~4 frames: 16.68 invisible, 16.72 heavy blur (~12 px) at 60% opacity, 16.76 sharp. There is no scale bounce. After landing it sits completely still.
- **Card body quotes** are revealed in 1–3-word chunks with the same blur-fade, following the VO. A later chunk can be visibly blurred while the previous one is sharp (e.g. "shaklini" blurred at 18.5).
- **Number counters:** 0→30 over 0.75 s (0.25→1.0 s), ease-out (sampled values 0, 2, 5, 17, 22, 27, 28, 30 at 0.1 s steps). This is roughly power3.out with integer rounding.
- **Exits:** text never animates out on its own. Everything leaves together with the scene via the scale-down crossfade. The one exception is the FLIP at 13.6: unselected cards fade (opacity→0, ~0.3 s) while the chosen card travels.
- **Stacking:** kicker, headline, subhead and component stack vertically and stay put. New elements push nothing; positions are pre-laid out. The whole content group drifts upward slowly by ~20 px over ~1 s after a card lands (a long expo.out settle).

## 5. UI components & imagery

All imagery is **Apple Color Emoji** (💈✂️🧔🧴🪮🧼🪞💡⚠️💬✅✨📅). No photos, footage or illustrations.

**Light card (category / topic card)**
- 384×200 px, gap 13 px horizontal and ~19 px vertical. 2-column grid spanning x 150–930.
- Radius **36 px**. Fill #FBFBFD. 1 px border rgba(0,0,0,0.06).
- Shadow: soft and short, about `0 6px 16px rgba(0,0,0,0.07)` (shadow band visible for ~16 px below the card, #E0E0E2→#E6E6E8).
- Emoji 56 px at (24, 24). Index "01" 22 px #8E8E93 top-right (24 px inset). Title 36 px SemiBold, baseline at card bottom −38 px.
- Selected state: 2–3 px #007AFF border plus a slight scale-up (1.0→1.15 when centred).

**Dark section card ("Maslahat 1/5")**
- x 141–938 (798 px), height ~405, radius **44 px**. Fill #29292C.
- Top inner highlight / border: 1–2 px #3C3C3E (rgba(255,255,255,.08)).
- Header row 117 px tall containing: a 70 px emoji circle tinted with the accent at 25% (green #2D4C35 behind 💡), the title 33 px SemiBold, and "1 / 5" right-aligned. A divider #343436 (1 px) sits under the header.
- Body padding 42 px.
- Progress bar at the bottom: 10 px tall, full radius. Track #37373A (dark) or #E5E5EA (light); fill is the accent.
- Accents: Maslahat #34C759 (#30C452 measured), Xato #FF3B30, Mif #FF9500, Savol-javob #007AFF.
- The bar **fills linearly over the whole section duration** (it acts as a section timer: 16.6 → ~19.9 s).
- Shadow under the card: `0 12px 30px rgba(0,0,0,0.45)`.
- The light variant (Xato, Savol-javob) is the same layout in white #FFFFFF with a #E5E5EA divider.

**Hook widgets** (iOS home-screen widget look)
- Two 376×376 squircles at x 152–530 and 550–928, gap 20, radius ~56. Fill #2A2A2D, inner top highlight, dark drop shadow.
- Widget A: "Kontent" 30 px Medium grey at (36, 40), 📅 at the top-right, "30" ~150 px Bold, "kun" 36 px grey.
- Widget B: ring with diameter ~260 and stroke 14 px. Track #3A3A3C, progress #34C759 (light-green gradient #30D158→#28B44A). It draws clockwise from 12 o'clock over ~0.8 s (2.1→2.9, ease-out). Centre "20" Bold ~110 px plus "daqiqa".

**Chat bubbles (Savol-javob):** grey bubbles #E9E9EB with black 30 px Regular text, radius 30, padding 14/22, stacked 14 px apart. The typing indicator is a blue #007AFF pill 92×44 with three white dots.

**Blue-scene cards**
- "Oldin": glass card, fill rgba(255,255,255,0.12), 1.5 px border rgba(255,255,255,0.3), radius 44, 376×448; the emoji is desaturated or blue-tinted.
- "Keyin": white card #FBFBFB, radius 44, shadow `0 20px 40px rgba(0,30,80,.25)`, with a green ✅ circle (44 px) at the top-left and ✨ at the top-right.
- A 40 px white connector line joins the two cards.

**Orbit diagram:** a centre circle of 200 px, #007AFF, holding 🧔 + "Soqol" (white SemiBold 30), with shadow `0 10px 30px rgba(0,122,255,.35)`. The ring is 1.5 px #E5E5EA with r ≈ 270. The 5 node pills are white, radius full, padding 10/18, 26 px SemiBold, each with an 12 px accent dot and a light shadow. They pop in one by one, ~0.4 s apart: scale 0.6→1 + opacity, back.out(1.6).

**Pills:** the blue info pill "1 ta bo'lim = 5 ta video" is #007AFF with white 22 px SemiBold, height ~40, full radius. The "Rost / Mif" toggles are grey #3A3A3C, with the active one #FF9500.

**Payoff grid**
- 6 cols × 5 rows. Tiles 98×99, pitch 114 (gap 16), radius **22**. Grid spans x 206–872 and y 614–1167. White tile numbers 26 px SemiBold (black on white tiles).
- Column colours: #007AFF, #34C759, #FF9500, #FF3B30, #FFCC00, #FFFFFF.
- Empty tiles are #2C2C2E.
- The emoji header row sits at y≈550, 44 px.

**Component entry:** cards fade + blur in and translate up 30–40 px over ~0.25 s, expo.out (e.g. the 16.44→16.68 dark card), then settle another ~20 px over 0.5 s. Grid cards pop in sequence on their spoken word. Skeleton → content morphs are used in the light scenes.

## 6. Transitions & camera

- **Scene transition (used 9×), "scale-down crossfade":** duration **0.6–0.7 s (15–17 frames)**, ease power2.inOut.
  - The outgoing scene (bg + content as one layer) scales 1 → ~0.96 (it shrinks 20 px from each side at row 960) while its opacity goes 1 → 0.
  - Underneath, the incoming scene fades up from near-black (frame edges briefly show #00030B–#0A2546 at the transition's darkest point).
  - The new kicker starts revealing ~0.3 s into the transition, while the old scene is still ghosted.
  - Measured on 34.80→35.50 (light→blue). The centre colour goes #E0E0E4 → #1970CD with an S-curve: slow 34.8–34.9, fast 35.0–35.3, settling by 35.45.
- **FLIP move** (13.6–14.1): the selected card travels to centre and scales ~1.15 over ~0.5 s, power3.inOut.
- **Camera:** no zooms or pans. There is only a slow post-entry upward settle of the content (~20 px).
- **End glitch:** 56.04–56.28 (6 frames). Digital "ghost/RGB split": the frame is duplicated at +12..+40 px vertical offsets with lightened copies and chromatic fringing, sharp, with no blur. It reads as a datamosh into the loop.

## 7. Sync with voice

- **Literal, word-level sync.** The VO text is shown almost verbatim. The kicker and headline are the spoken words themselves: "Birinchi video — maslahat", "Ikkinchisi — xato".
- Visual onset lands **0–80 ms after** the word onset in the transcript: "maslahat" 16.68 vs VO 16.7; the cards on each listed category; the counter "30" begins on the spoken "30" (0.36).
- Components come in ~0.2–0.3 s **before** the headline word (the card at 16.44 before "maslahat" at 16.7), so the eye is already on the card when the word lands.
- Quotes on the cards follow the VO phrase by phrase. The final emphasis words ("3 ta xato", "Shu rostmi?") switch to the accent colour exactly on the spoken word.
- The section progress bar visualises the time until the next section.

## 8. Audio

- Voiceover is dry and close-mic'd, about −14 dBFS RMS on speech, with no reverb.
- **Music bed:** a sub-bass / 808-style bed. Energy below 120 Hz sits steady at **≈ −20 dBFS**, with slow decays (−20→−25 over ~0.8 s, i.e. long sustained bass notes). There is almost nothing audible above ~4 kHz between words; HF falls to −80 dB in pauses. So the music is a minimal low-end bed mixed very low and felt more than heard. Tempo estimate ≈ 98–99 BPM.
- **Breakdown:** the bass drops out from **~17.0 to 23.7 s** (the Maslahat→Xato sections, LO −35..−60 dB) and returns at 23.8. The same breakdown appears at the same timestamps in DelZA2dtAE6, which suggests a shared music template.
- **SFX:** no clear whooshes or clicks were detectable. The HF band shows no transient on transitions beyond speech sibilance. If any UI ticks exist, they sit below the speech. Recommendation: soft UI "tick" ≤ −30 dB on card pops, optional.

## 9. Secret sauce (premium details) & naive-recreation pitfalls

1. **The theme flip per section** (dark ↔ light, one blue takeover) is the rhythm device: a new section means a new world. Don't keep one bg.
2. **Weight contrast:** a 52 px Light grey kicker over a 108 px Bold near-black headline. Using Regular for the kicker or Semibold for the headline kills the Apple feel.
3. **Exact grid alignment:** the 130 px grid lines coincide with the content column (x=150/930). The chrome, cards and grid share edges.
4. **Blur-in, not slide-in:** words resolve from a 10–12 px blur in 3–4 frames. A 0.5 s fade or a typewriter effect looks cheap.
5. **The section progress bar fills linearly the whole time.** It is the subtle motion that keeps static scenes alive.
6. **Pagination dots in the chrome** turn the reel into an "app with pages". The active pill moves on each section change.
7. **Apple system colours only:** #007AFF, #34C759, #FF9500, #FF3B30, #FFCC00, plus iOS greys #8E8E93/#E5E5EA/#2C2C2E. Saturated web blues/greens look off.
8. **Apple emoji as the only imagery,** and tinted emoji circles (25% accent) behind header icons.
9. **Crossfade with a 0.96 scale-down over near-black.** It gives a "page sinks away" depth. A plain dissolve looks flat.
10. **Payoff grid fills column by column on the VO count,** and starts with the column of the example category.

Pitfalls:
- Shadows too dark or too large on light cards. They are ~7% black, short and soft.
- Pure white bg. It's #F3–F7 with a gradient.
- Pure black dark bg. It's #1A1A1C.
- Forgetting the 1 px inner highlight on dark cards.
- Centring the card body text. It's left-aligned; only the kicker and headline are centred.
- Animating out individual elements. They leave only with the scene.
- Adding loud music: the bed is sub-bass only.

## 10. Reproducible spec (CSS + GSAP) — 5 most common elements

```css
:root{
  --blue:#007AFF; --green:#34C759; --orange:#FF9500; --red:#FF3B30; --yellow:#FFCC00;
  --g-label:#8E8E93; --font:"SF Pro Display","Inter Display",Inter,system-ui,sans-serif;
}
.stage{width:1080px;height:1920px;position:relative;overflow:hidden;background:#000;font-family:var(--font)}
.scene{position:absolute;inset:0;transform-origin:50% 50%}
.scene.light{background:
  repeating-linear-gradient(90deg,transparent 0 19px,rgba(0,0,0,.035) 19px 21px,transparent 21px 130px),
  repeating-linear-gradient(0deg,transparent 0 49px,rgba(0,0,0,.035) 49px 51px,transparent 51px 130px),
  linear-gradient(#F7F7F7,#F3F3F5 46%,#ECECEE)}
.scene.dark{background:
  repeating-linear-gradient(90deg,transparent 0 19px,rgba(255,255,255,.03) 19px 21px,transparent 21px 130px),
  repeating-linear-gradient(0deg,transparent 0 49px,rgba(255,255,255,.03) 49px 51px,transparent 51px 130px),
  radial-gradient(120% 80% at 50% 45%,#1C1C1F 0%,#1A1A1C 50%,#131316 100%)}
.scene.blue{background:
  repeating-radial-gradient(circle at 540px 980px,transparent 0 160px,rgba(255,255,255,.07) 160px 161.5px),
  linear-gradient(#1B88FB 0%,#1B88FB 15%,#176ECD 50%,#0F539A 88%)}
/* 1 kicker + 2 headline */
.kicker{position:absolute;top:360px;width:100%;text-align:center;font:300 52px/1 var(--font);color:#7D7D7F;letter-spacing:-.01em}
.dark .kicker{color:#9A9A9D}.blue .kicker{color:rgba(255,255,255,.72)}
.headline{position:absolute;top:452px;width:100%;text-align:center;font:700 108px/1 var(--font);letter-spacing:-.02em;color:#060609}
.dark .headline,.blue .headline{color:#fff}
.word{display:inline-block;will-change:filter,opacity,transform}
/* 3 light card */
.card-l{width:384px;height:200px;border-radius:36px;background:#FBFBFD;border:1px solid rgba(0,0,0,.06);
  box-shadow:0 6px 16px rgba(0,0,0,.07);position:relative}
.card-l .t{position:absolute;left:24px;bottom:30px;font:600 36px/1 var(--font);color:#000}
.card-l .n{position:absolute;right:28px;top:30px;font:500 22px var(--font);color:var(--g-label)}
/* 4 dark section card */
.card-d{position:absolute;left:141px;width:798px;top:683px;border-radius:44px;background:#29292C;
  box-shadow:inset 0 1.5px 0 rgba(255,255,255,.08),0 12px 30px rgba(0,0,0,.45);color:#fff}
.card-d .hd{height:117px;display:flex;align-items:center;gap:18px;padding:0 42px;border-bottom:1px solid #343436;font:600 33px var(--font)}
.card-d .ic{width:70px;height:70px;border-radius:50%;background:color-mix(in srgb,var(--accent) 25%,#29292C);display:grid;place-items:center;font-size:40px}
.card-d .bd{padding:40px 42px 0;font:600 48px/70px var(--font)}
.card-d .bar{margin:50px 42px 50px;height:10px;border-radius:5px;background:#37373A;overflow:hidden}
.card-d .bar i{display:block;height:100%;width:0;background:var(--accent);border-radius:5px}
/* 5 chrome */
.chrome{position:absolute;left:150px;top:180px;font:600 24px/34px var(--font);color:#7E7E81}
.chrome b{display:block;font-weight:400}
.dots{position:absolute;right:150px;top:208px;display:flex;gap:14px}
.dots i{width:8px;height:8px;border-radius:4px;background:#8B8B8D;transition:none}
.dots i.on{width:22px;background:var(--blue)}
```

```js
// word reveal (kicker/headline/quote chunks) — call at the VO word onset
const wordIn = (el,t)=> tl.fromTo(el,{opacity:0,filter:"blur(12px)",y:8},
  {opacity:1,filter:"blur(0px)",y:0,duration:0.14,ease:"power2.out"},t);
// card / component entry (0.25 s before its headline word), then slow settle
const cardIn = (el,t)=>{ tl.fromTo(el,{opacity:0,filter:"blur(8px)",y:40,scale:0.98},
  {opacity:1,filter:"blur(0px)",y:20,scale:1,duration:0.26,ease:"expo.out"},t)
  .to(el,{y:0,duration:0.8,ease:"expo.out"},t+0.2); };
// section progress bar = section timer
const barRun = (el,t0,t1)=> tl.fromTo(el,{width:"0%"},{width:"100%",duration:t1-t0,ease:"none"},t0);
// counter 0->30
const count = (el,to,t)=>{const o={v:0}; tl.to(o,{v:to,duration:0.75,ease:"power3.out",
  onUpdate:()=>el.textContent=Math.round(o.v)},t);};
// scene transition (outgoing over incoming, stage bg #000)
const sceneSwap = (outEl,inEl,t)=>{ tl.set(inEl,{opacity:0,zIndex:1}).set(outEl,{zIndex:2},t)
  .to(outEl,{scale:0.962,opacity:0,duration:0.64,ease:"power2.inOut"},t)
  .to(inEl,{opacity:1,duration:0.5,ease:"power2.out"},t+0.06); };
// orbit node pop
const pop = (el,t)=> tl.fromTo(el,{scale:0.6,opacity:0},{scale:1,opacity:1,duration:0.35,ease:"back.out(1.6)"},t);
// payoff tile fill: per tile stagger 0.08, per column 0.5
// tl.to(col.tiles,{backgroundColor:c,color:"#fff",duration:0.2,stagger:0.08},t)
```
