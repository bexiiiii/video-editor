# Dd3Uz4Mgbn- — "Reels million ko'rilishi uchun…" (Umar Jamoldinov / 0mar.uz) — Style Forensics

1080x1920, 24 fps, 42.21 s, AAC 44.1k stereo. Uzbek, speaker's own voice (~154 wpm, speech ratio 0.90).
Detected cuts: 6.125/6.167 (zoom jump), 8.5, 12.875/12.917 (phone pull-out), 19.875, 36.33/36.375 (glitch).
Evidence files in this folder: sheet_01-03.jpg, hook.jpg, f_*.png, tr_*.jpg (the timestamps burned into each strip are relative to the strip's start time in its filename), marquee.jpg.

**Format:** a numbered listicle, "3 things your video needs in the first seconds". Sections 01 visual hook → 02 text hook → 03 gap hook run on a **light editorial canvas** with a giant grey section numeral. The talking head appears only as framed footage (a window or phone mockup) and as a full-frame A-roll for the final CTA. Unlike its sibling (Dd1b9kEA-KL), this video has **no dark mode**, and a **global lens-blur / chromatic-aberration treatment** sits over the graphics as well.

---

## 1. Format and structure

| t (s) | Scene | Visual | On-screen caption phrases |
|---|---|---|---|
| 0.00–5.00 | **Intro / hook** | Warm-light canvas with an embossed 3-column grid. The speaker footage lives in a **392x595 window** that fills the middle grid cell (x 344–736, y 662–1257). Above it sit **"1 2 3"** in huge black condensed numerals, one per column | "Videolaringiz boshida" / "aynan mana shu" / "uchta narsa bo'lishi kerak" / "agarda bular bo'lmasa" / "videoyingiz aniq topga chiqmaydi" |
| 5.00–5.10 | Intro exit | The window collapses to a small rectangle at the centre (3 frames), the numerals cut off, then a blank canvas for 4 frames | — |
| 5.10–12.875 | **Section 01 — visual hook** | A grey giant **"01"** rises from the bottom. A 3x3 grid of viral reel covers (635x844, x 246–881, y 439–1283, 3 px gutters, eye-icon view counts) builds tile by tile. At **6.125 a 2-frame jump zoom to about 2.4x** onto the middle/right tiles; the view drifts while zoomed, then cuts back to the full grid at 8.5. At 12.3–12.85 the grid slides out to the left with motion blur | "Birinchisi vizual hook" / "yani odamlar" / "sizning videoingizni" / "birinchi soniyalardayoq" / "nima haqidaligini" / "u uchun kerakligini" / "aniqlashtirib olishi kerak bo'ladi" |
| 12.875–19.875 | **Section 02 — text hook** | A full-frame speaker shot starts at about 2x and **pulls out into an iPhone mockup** over about 8 frames (phone body about 560x1180, centred, top about 1210/… → rest y 200–1440). The giant "02" sits behind. A white rounded label "Text" types into "Text hook" over the speaker's chest. The glove cursor taps it (13.5–16.0). **15.75–18.6: the voice is muffled/ducked by about 11 dB to simulate the phone being on mute.** At 19.5 the phone rises up and out | "Ikkinchisi text hook" / "kuzatuvchi videoni" / "ovozsiz holatda" / "ko'rayotgan bo'lsa ham" / "sizning" / "nima haqidaligini" / "o'qib bilib olishi kerak" |
| 19.875–36.33 | **Section 03 — gap hook** | Fade/blur-in of a case study: an IG profile header bar (dark, 600x165, y 250–418) plus an example reel playing **with its own audio** (495x880, x 294–789, y 518–1400; doctor, "9,5 mln" views strip, its own burned-in captions using a serif italic accent word). A giant "03" sits behind. A bookmark icon flashes on it at 29.5–31 | "Uchinchisi gap hook" (held 20.0–29.0 while the example plays) / "Videoni boshidayoq" / "odamlarning muammosini" / "gapirib chiqishingiz kerak" / "va bunga yechimingiz" / "borligini videoni" / "oxirigacha ko'rishi" / "kerakligini aytishingiz kerak" |
| 36.33–36.6 | **Glitch transition** | Datamosh / pixel-sort block glitch into the A-roll (≈6 frames) | — |
| 36.4–42.21 | **CTA A-roll** | Full-frame speaker (Tashkent City tower, pines, strong sun-flare halo, lens edge blur). The avatar tile pops at the chest (36.45) → the pill unrolls (37.0) → the name types → a blue "Obuna bo'ling" button → press at 39.0 → dark "subscribed" chip | Spoken CTA (no captions) |

**Hook (0–3 s), from hook.jpg at 10 fps:**
- 0.04: a 1 px horizontal sliver appears at screen centre.
- 0.08–0.25: it unfolds into the speaker window (width first, then height; scale 0→1 with back.out).
- 0.125: "1" appears; 0.29: "2"; 0.46: "3". That is a **4-frame (167 ms) stagger**. Each numeral fades in from about 40% grey to black over about 4 frames.
- 0.17: the first caption word.
- The "1" is permanently **vertically motion-blurred / doubled** (a stylised "fast" look). "2" and "3" are crisp.
- This is the "three things" promise, made visual within 0.5 s.

**Ending:** the CTA pill stays to the end. There is no outro card; the video cuts out mid-sentence ("…ko'rishguncha"), which makes it loop-friendly.

**Persistent chrome:** none on the A-roll. During sections the giant section numeral acts as a quasi-persistent chapter marker.

---

## 2. Backgrounds

**Light canvas (0–36.33):** a **radial gradient**. The centre is #F4F2F0 (sampled at x 200, y 960) and #EFEDEC at the lower centre. It falls off to **#DDDAD7** at all four corners, with a top-centre of about #E6E4E3. The tone is warm off-white, like paper under a soft spotlight.
- CSS: `radial-gradient(ellipse 70% 55% at 50% 52%, #F4F2F0 0%, #ECEAE8 55%, #DDDAD7 100%)`.

**Embossed grid lines (intro and section 03):**
- Vertical lines at x≈342 and x≈736, so the three columns are 342 / 394 / 344 px wide; the middle column is exactly the window width.
- Horizontal lines at y≈660 and y≈1257 frame the window cell. In section 03 the lines are at x≈238 and x≈842, framing the profile bar.
- Each line is about 4 px wide, about 6 luminance below the background (≈ rgba(0,0,0,.035)), with a 2 px highlight of about +3 luminance on the left. This is an engraved/embossed hairline, barely visible.

**Giant section numeral "01/02/03":**
- Colour #C0C0C0 to #CBCBCB (flat grey about 20% darker than the background), with a soft 2–4 px blur.
- About **1150 px font size** (the "0" is about 670 px wide and its top sits at y≈1130). It bleeds off the bottom and right edges.
- Font: a geometric/neo-grotesk medium (Inter / SF Pro Display 500).
- It sits behind all content. It is **static during a section** (the sheets only look like "0101" because adjacent cells line up).
- **Entry:** the digits rise from below (+400 px) with a 2–3 frame stagger between the "0" and the number, over about 8 frames, starting about 2 frames before the section's first caption word.

**Global lens treatment (the whole graphic canvas, not just the footage):**
- A sharp ellipse in the centre.
- **Directional horizontal blur on the left about 25% of the frame** (the first caption word "uchta" and the left grid column smear sideways).
- **Chromatic aberration** fringes of about 4–6 px (blue/cyan on the left edges, orange on the right).
- A slight overall bloom.
- It reads as a real anamorphic/tilt lens filming a screen. It is applied as an adjustment layer.

**Background change:** canvas ↔ A-roll only at 12.875 (pull-out from full frame), 19.875 (a brief white flash/blank, then fade-in) and 36.33 (glitch).

---

## 3. Typography

All sizes are for 1080 px width and were measured.

| Role | Font guess | Size | Weight | Tracking | Colour | Position |
|---|---|---|---|---|---|---|
| Caption (all sections) | SF Pro Display / Inter Display | **≈62–64 px** (ascender-to-descender 60 px for "soniyalardayoq"; ascender-to-baseline 48 px for "bo'lishi kerak") | 500 | **−0.05em** | Settled #111–#1A1A1A; incoming word #7A7879 | Single centred line, baseline about y 1377 (top 1329), i.e. 68–72% of height. In section 02 it sits under the phone at y≈1500 (moves with the phone) |
| Numerals "1 2 3" | Bold condensed grotesk: Bebas Neue / Antonio 700 / Oswald 600 | Cap height 235 px → **≈330 px** | 700 | — | #121313 | Centred in each column (x≈190, 544, 896), y 276–513 |
| Giant section numeral | Inter / SF Pro 500 | ≈1150 px | 500 | −0.04em | #C2C2C2 | Bottom-anchored, bleeding off-canvas |
| "Text hook" label | Same sans | Glyph height 68 → **≈90 px** | 500 | −0.04em | #111 | Centred on the phone, y 960–1028 |
| CTA name | Same sans | 2 lines of about 36 px (scaled pill) | 500–600 | −0.03em | #000 | — |
| CTA button | Same sans | about 24 px | 300 | — | #FFF on #4FA3E4–#227DE5 | — |

Captions are sentence case, one line, **at most about 26 characters (≈620 px)**, in chunks of 1–3 words. Hierarchy comes from scale contrast between the giant numerals and the captions, not from weight changes.

---

## 4. Text / subtitle animation

- **Additive word-by-word, in the final centred layout.** The phrase is pre-laid-out; each word appears in its slot.
- **Each word:**
  - opacity 0→1 with colour #8A8A8A → #1A1A1A
  - a small **x slide of about +25–30 px → 0** (new words drift in from the right and settle; visible in tr_0.0 with "boshida")
  - blur about 6 px → 0
  - **≈5–6 frames (210–250 ms)**, power2.out
  - So the latest word always reads lighter grey for about 0.2 s: a "karaoke from grey to ink" effect.
- **Onset:** at the spoken word onset (±2 frames).
- **Phrase change:** hard swap, no exit animation.
- Section headers ("Birinchisi vizual hook", "Ikkinchisi text hook", "Uchinchisi gap hook") use the same caption style. They are not bigger — the giant numeral carries the chapter emphasis.
- **"Text hook" label:** typewriter. The pill first appears as a blank white rounded rectangle (scale-in from the full-frame shot), then "Text" types in, then " hook" at 13.5.

---

## 5. UI components and imagery

### Speaker window (intro)
- 392x595 px, radius 0 (hard rectangle), no border or shadow. Its edges align with the grid lines (it *is* a grid cell).
- **Unfold:** 1 px horizontal line → full width (2 frames) → full height (3 frames), back.out(1.2).
- **Collapse at 5.0:** it shrinks to about 60x100 at the centre over 3 frames (power3.in), then disappears.

### Reel-cover grid (section 01)
- 3x3 tiles of about 210x280 px with **3 px white gutters**; an eye icon plus a white 28 px semibold view count at the bottom-left ("16M", "101K", "7M", "1,8M", "347K", "375K", "57,2K").
- **Build:** tiles fade in from 0 opacity (with about 10 px blur → 0) in row order, **1 tile every 2 frames** (5.15–5.6 s), linear-ish.
- **Zoom beat 6.125:** a 2-frame jump scale to about 2.4x (anchored right of centre). It holds and drifts about −40 px/s to the left for 2.4 s, then hard-cuts back to 1x at 8.5. It is effectively a punch-in on "odamlar sizning videoingizni".
- **Exit 12.3–12.85:** it slides left about 900 px, accelerating (power2.in), with the canvas lens blur smearing it.

### Phone mockup (section 02)
- iPhone 15 Pro, deep-purple titanium frame (#3b2a40), screen radius about 80. The screen is the full-res speaker footage.
- **Pull-out entry 12.875–13.2:** the footage starts full-bleed at about 1.9x. The phone body scales from about 2.0 to 1.0 around the centre over **8 frames (≈333 ms), expo.out**, so the bezel "closes in" around the footage.
- Rest: x 255–830, y 270–1440.
- A white label pill sits on it: **438x122 px, radius ≈30**, fill #F3F3F3, with a subtle shadow 0 6px 20px rgba(0,0,0,.18) and a 1 px white inner rim.
- Glove cursor (white, black outline, about 120 px) enters from the bottom-left at 13.4 and taps the pill (scale 0.85 bounce). It exits down at 16.0.
- **Exit 19.45–19.85:** the phone moves up about 300 px and scales to 0.96 with power2.in; the caption rides with it. Then a white blank for 2 frames.

### Case-study block (section 03)
- **Entry 19.9–20.25:** opacity 0→1 with blur 12→0, plus a slight drop of y −20→0 over 8 frames. The profile bar and the video arrive together. The example video plays with its own audio.
- **Profile bar:** #16191C, 600x165, square corners. Avatar circle 128 px. "XURSHID TOYIROV | KINEZIOLOG SHIFOKOR" 24 px semibold uppercase, white. Stats "106 posts / 155K followers / 4 following" at 28/24 px.
- **Example reel:** 495x880, square corners, a black 80 px bottom strip with "9,5 mln" in 44 px bold white.
- A bookmark icon outline (blue-white) pops onto the video at 29.5 and stays to 31 (it illustrates "save").

### CTA pill (36.45–42.2)
- 543x167 px, radius about 60, fill #EEEEEE, a 4 px white rim plus a white glow (0 0 26px rgba(255,255,255,.7)).
- B&W avatar about 145 px, radius 28. Name text in 2 lines. Button 165x48, radius 12, #227DE5 (sampled #4FA3E4 when anti-aliased).
- **Build:**
  1. 36.45: the avatar tile pops through the glitch (back.out).
  2. 37.0–37.3: the pill unrolls to the right with a blue placeholder bar.
  3. 37.3–38.0: the name types.
  4. 39.0: button press → small dark #2B2B2B chip.

---

## 6. Transitions and camera

| t | Transition | Duration |
|---|---|---|
| 0.04 | Line-unfold window open | 5 frames (208 ms) |
| 5.00 | Window implode + numerals off + 4-frame blank | 7 frames |
| 5.15 | Giant numeral rise + tile cascade | 8 frames + 11 frames |
| 6.125 | Jump-zoom punch-in (2.4x) | 1–2 frames |
| 8.50 | Hard cut back to 1x | 0 |
| 12.3 | Grid whip-slide left (motion blur) | 13 frames |
| 12.875 | Full-frame → phone pull-out (zoom-out reveal) | 8 frames (333 ms) |
| 19.45 | Phone lift-off up + white blank | 10 frames + 2 frames |
| 19.9 | Blur/fade-in of the case study | 8 frames |
| 36.33 | **Datamosh / pixel-sort glitch** into the A-roll (blocks of the old frame tear horizontally, the new frame bleeds through) | 6 frames (250 ms) |

Camera: virtual zooms only (6.125 punch-in, 12.875 pull-out). The A-roll is handheld and static.

---

## 7. Sync with voice

- Captions are near-verbatim and lightly cleaned. Word onsets match speech onsets, e.g. "Birinchisi vizual hook" visual at 5.25/5.40/5.60 vs speech 5.12–5.58.
- **Structure markers are literal:**
  - the numerals 1-2-3 appear on "uchta narsa"-adjacent lines in the first 0.5 s
  - each section's giant numeral rises on "Birinchisi" / "Ikkinchisi" / "Uchinchisi"
- **Concept demos are literal:**
  - the "Text hook" label types on "text hook"
  - the voice is **muffled exactly while "ovozsiz holatda" (on mute) is being explained** (15.75–18.6)
  - the bookmark appears when "saqlab" is implied
  - the example reel's own audio plays while the header caption holds for 9 s
- Visual beats change about every 2–3 s; captions change every 0.8–1.5 s.

---

## 8. Audio

- Voice RMS is about −16 dBFS. Dry intro: **no music for 0–5.0 s** (low end <150 Hz at about −46 dB).
- **Music bed enters at 5.0 s exactly on section 01** ("Birinchisi"). Low end jumps to about −31 dB (+15 dB) and stays under everything to the end, about 11 dB below the voice. That points to a soft beat/pad.
- **15.75–18.6:** voice mid band −11 dB, HF −10 dB (muffled/ducked mute effect). Music continues at about −27 dB RMS. This is the only "music-forward" moment.
- **20–29:** the example reel's original audio (the doctor talking) replaces the narrator.
- **SFX (HF transients):**
  - 0.33–0.5 and 1.42–1.67: numeral pops / tile clicks
  - 5.33–5.75: tile cascade ticks
  - 7.25–7.33: zoom whoosh
  - 13.17–13.6: typewriter/tap on "Text hook"
  - 20.0–20.25: case-study entry
  - 25.17, 26.25: from the example clip
  - **36.42–36.5: glitch noise burst**
  - 37.17 (−30 dB): CTA pill pop
- All SFX are short and soft (UI clicks, digital glitch), never cinematic booms.

---

## 9. Secret sauce

1. **Editorial grid as layout logic.** The faint embossed column lines are the actual container for the footage window and the numerals, so everything feels "designed on a grid".
2. **Giant ghost section numerals** (#C2C2C2, ≈1150 px, bleeding off-frame). Instant chapter orientation without a title card.
3. **Lens physics on flat graphics.** Left-side directional blur plus chromatic aberration make motion graphics look *photographed*, not rendered.
4. **The "1" is permanently motion-blurred** while "2" and "3" are sharp — a tiny asymmetry that implies speed.
5. **Captions ink up from grey to black** with a 25 px settle. The newest word is always readable as "new".
6. **Audio acts out the content.** Muffled voice while explaining "watching on mute"; the example's real audio for the case study; music withheld until the first point lands (5 s).
7. **Pull-out-to-phone reveal.** Starting full-frame and zooming out into a phone tells you "this is what the viewer sees".
8. **Proof everywhere.** Real viral covers with view counts, a real profile with 155K followers, "9,5 mln".
9. **Glitch transition used exactly once**, as the "back to me" CTA punctuation.

**Pitfalls**
- A flat #F2F2F2 background. It needs the warm radial falloff to #DDDAD7.
- Grid lines that are too visible (they are about 3.5% black, 4 px, embossed). Visible strokes look like a spreadsheet.
- A black or high-opacity section numeral. It must be pale grey and blurred, behind everything.
- Using the same font for the numerals and the captions. The "1 2 3" are bold *condensed*; the captions are tight neo-grotesk medium.
- Left-aligned or multi-line captions. Always one centred line, at most about 26 characters.
- Animating captions with bounces or scale. Only opacity/colour/small x-settle/blur.
- Leaving music on during the hook. It must start at the first section.
- Forgetting the lens CA/blur pass, which makes it look like a generic template.

---

## 10. Reproducible spec (CSS + GSAP)

```css
:root{--paper-c:#F4F2F0;--paper-e:#DDDAD7;--ink:#1A1A1A;--ghost:#C2C2C2;
  --font:"SF Pro Display","Inter Display","Inter",sans-serif;--cond:"Bebas Neue","Antonio","Oswald",sans-serif}
/* 1. Canvas + embossed grid */
.canvas{background:radial-gradient(ellipse 70% 55% at 50% 52%,#F4F2F0 0%,#ECEAE8 55%,#DDDAD7 100%)}
.vline{position:absolute;top:0;bottom:0;width:4px;background:rgba(0,0,0,.035);box-shadow:-2px 0 0 rgba(255,255,255,.5)}
.vline.a{left:340px}.vline.b{left:734px}
.hline{position:absolute;left:0;right:0;height:3px;background:rgba(0,0,0,.03)} .hline.a{top:659px}.hline.b{top:1256px}
/* 2. Caption */
.cap{position:absolute;left:0;right:0;top:1329px;text-align:center;font:500 63px/1 var(--font);
  letter-spacing:-.05em;color:var(--ink);white-space:nowrap}
.cap .w{display:inline-block;margin:0 .1em;opacity:0}
/* 3. Ghost numeral + 1-2-3 */
.ghost{position:absolute;left:-10px;top:1120px;font:500 1150px/0.8 var(--font);letter-spacing:-.04em;
  color:var(--ghost);filter:blur(3px);z-index:0}
.num{position:absolute;top:250px;font:700 330px/1 var(--cond);color:#121313}
.num.n1{left:150px;filter:url(#vblur)} /* vertical motion blur 12px */
/* 4. Phone + label pill */
.phone{position:absolute;left:255px;top:270px;width:575px;height:1170px;border-radius:110px;background:#3b2a40;padding:22px}
.phone video{width:100%;height:100%;object-fit:cover;border-radius:88px}
.label{position:absolute;left:324px;top:934px;width:438px;height:122px;border-radius:30px;background:#F3F3F3;
  box-shadow:0 6px 20px rgba(0,0,0,.18),inset 0 0 0 1px #fff;font:500 90px/122px var(--font);letter-spacing:-.04em;text-align:center;color:#111}
/* 5. CTA pill */
.cta{position:absolute;left:268px;top:1080px;width:543px;height:167px;border-radius:60px;background:#EEE;
  box-shadow:0 0 0 4px rgba(255,255,255,.6),0 0 26px rgba(255,255,255,.7)}
.cta .btn{width:165px;height:48px;border-radius:12px;background:#227DE5;color:#fff;font:300 24px/48px var(--font)}
/* Global lens pass (overlay layer above everything) */
.lens{position:absolute;inset:0;pointer-events:none;backdrop-filter:blur(6px);
  -webkit-mask:linear-gradient(90deg,#000 0,transparent 28%,transparent 85%,rgba(0,0,0,.5) 100%)}
```

```js
// 1. Word reveal: grey->ink with x-settle
tl.fromTo(w,{opacity:0,x:28,color:"#8A8A8A",filter:"blur(6px)"},
  {opacity:1,x:0,color:"#1A1A1A",filter:"blur(0px)",duration:0.23,ease:"power2.out"},tWord);

// 2. Intro: line-unfold window + staggered numerals
tl.fromTo(".win",{scaleX:0.02,scaleY:0.004},{scaleX:1,duration:0.09,ease:"power2.out"},0.04)
  .to(".win",{scaleY:1,duration:0.13,ease:"back.out(1.2)"},0.12)
  .fromTo(".num",{opacity:0,color:"#9a9a9a"},{opacity:1,color:"#121313",duration:0.17,stagger:0.167,ease:"power1.out"},0.125);

// 3. Section start: ghost numeral rise + tile cascade + punch-in
tl.fromTo(".ghost .d",{y:420},{y:0,duration:0.33,stagger:0.1,ease:"expo.out"},5.1)
  .fromTo(".tile",{opacity:0,filter:"blur(10px)"},{opacity:1,filter:"blur(0px)",duration:0.12,stagger:0.083},5.15)
  .set(".grid",{scale:2.4,transformOrigin:"62% 40%"},6.125)
  .to(".grid",{x:-96,duration:2.375,ease:"none"},6.125)
  .set(".grid",{scale:1,x:0},8.5)
  .to(".grid",{x:-900,duration:0.54,ease:"power2.in"},12.3);

// 4. Full-frame -> phone pull-out
tl.fromTo(".phone",{scale:2.0},{scale:1,duration:0.333,ease:"expo.out"},12.875)
  .fromTo(".label",{scaleX:0.6,opacity:0},{scaleX:1,opacity:1,duration:0.2,ease:"back.out(1.4)"},12.9)
  .to(".phone,.cap",{y:-300,scale:0.96,duration:0.4,ease:"power2.in"},19.45);

// 5. CTA build (after glitch at 36.33)
tl.fromTo(".cta .ava",{scale:0},{scale:1,duration:0.21,ease:"back.out(1.8)"},36.45)
  .fromTo(".cta",{width:170},{width:543,duration:0.3,ease:"back.out(1.2)"},37.0)
  .from(".cta .name .w",{opacity:0,duration:0.04,stagger:0.12},37.3)
  .to(".cta .btn",{scale:0.5,backgroundColor:"#2B2B2B",duration:0.17,ease:"power2.in"},39.0);
```
