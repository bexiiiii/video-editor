# Dd1b9kEA-KL — "Instagram cheatcode" (Umar Jamoldinov / 0mar.uz) — Style Forensics

1080x1920, 24 fps, 42.83 s, AAC 44.1k stereo. Uzbek voiceover is the speaker's own sync-sound (~170 wpm, speech ratio 0.94).
Hard cuts (cuts.txt): 8.583 / 21.417 / 28.583 / 38.167.
Evidence files in this folder: sheet_01-03.jpg, hook.jpg, f_*.png (full-res stills), tr_*.jpg (24 fps strips; the timestamps burned into each strip are relative to the strip's start time in its filename), tr_cta_btn.jpg, tr_end.jpg.

This is NOT faceless. Its structure is a talking-head sandwich: **A-roll talking head (8.6 s) → light-grey phone screen tutorial (12.8 s) → dark "widget" explainer (16.8 s) → A-roll talking head with a subscribe pill (4.7 s)**. It shares the Apple-widget language seen in the sibling videos, but adds a dark mode section.

---

## 1. Format and structure

| t (s) | Scene | What is on screen | Caption / on-screen words |
|---|---|---|---|
| 0.00–3.05 | A-roll, title hook | Speaker outdoors (Tashkent City towers + birch trees, golden-hour sun), with a 3-line title stack in the centre of the chest area | "Instagramda" (0.30) / "CHEATCODE" (0.60) / "bor" (0.90) "foydalanmaysiz" (1.15). The spoken filler "shunaqangi" is dropped |
| 3.05–5.0 | A-roll + proof cards | 3 reel thumbnails build up left→right, at y 885–1338 | "Biz bu orqali mijozimizga" then "20 million prasmotr" (5.0) |
| 5.55–8.58 | A-roll + profile card | A dark IG profile header ("XURSHID TOYIROV / 238 posts / 233K followers") flies in rotated from the bottom-left and lands over the thumbnails; the thumbnails dim to about 60% | "100K ga yaqin organik" then "auditoriya olib kirganmiz" |
| 8.58–21.0 | Light tutorial (#edebe9) | iPhone mockup showing a screen recording of the IG "New reel" screen, a white glove cursor taps through: Save draft → Drafts → duplicate → scroll → **Trial** toggle → back → Share | Label above the phone, one phrase at a time: "Gap shundaki" / "reels'ni joylashdan oldin" / "chernovikga saxranit qilasiz" / "va uni dublikat qilib" / "ustiga bosganizdan keyin" / "pastroqqa tushasiz" / "u yerda Trial knopkasini" / "yoqib qo'yishingiz kerak bo'ladi" / "va ortga qaytib" / "dublikatni odatiy holatda joylaysiz" |
| 21.0–21.42 | Exit | The phone drifts up about 40 px per frame, then a hard cut | — |
| 21.42–28.58 | Dark explainer, widget 1 | A 16 px dot grows into a 90 px app-icon tile (🎬) at 21.5, then at 22.5 expands into a 559 px square widget: "Odatiy joylagan reels'ingiz  1." + 4 green dots that get checked one by one + "Natija / Kuzatuvchiga 68%" + progress bar | "Sababi odatiy joylangan" / "reels'ingiz birinchi soatlarda" / "obunachilaringizga ko'rsatiladi" / "ularga qiziq bo'lsa" / "keyin boshqalarga chiqadi". The result word swaps Kuzatuvchiga → Ular → Ular qiziqsa → Boshqalarga |
| 28.58–32.85 | Dark explainer, widget 2 | Widget 1 squashes into a flat 400x90 bar, then re-inflates as a 419 px "gauge" widget (Trial / joylangani arc, "Avval boshqalarga chiqadi", 3 blue player buttons). It enters tilted about −8° and settles to 0° | "Trail'ga joylangani esa" / "sizga obuna bo'lmagan" / "insonlarga ko'rinishni boshlaydi" |
| 32.85–33.1 | Widget exit | The content fades, the tile shrinks to a blank 300 px square, then disappears (6 frames) | — |
| 33.1–38.17 | Dark, text only | Caption alone, centred at y≈945 | "yana bir maslahat" / "Trial'ga joylashdan oldin" / "Reel'singiz birinchi 3 soniyasini" / "birozgina o'zgartiring" |
| 38.17–42.83 | A-roll CTA | Avatar tile pops at 38.3 (chest, y≈1290) → expands into a white pill at 39.0 → name types in → blue "Obuna bo'ling" button → button is pressed at 40.55 and turns dark | Spoken CTA ("save it, subscribe…"). The pill falls apart in the last 0.3 s and the video ends abruptly (loop-friendly) |

**Hook (first 3 s):** cold open on the speaker mid-gesture with no intro. A huge thin condensed "CHEATCODE" sits between two small medium-weight lines. Everything is white and unboxed, centred over the speaker's white T-shirt (x 219–862, y 1088–1397). The words are revealed one at a time, but the stack takes its final shape within 1.2 s. It disappears with a hard cut at 3.05 s as the proof cards begin.

**A-roll treatment:** a single static take, handheld, medium close-up. The head top is at about y 360, the eyes at about y 590 (31% of height), and the shirt fills the bottom half. Hands gesture towards the lens and blur heavily (shallow depth of field). A **strong lens edge blur** (Lensbaby / "swing-tilt" look: sharp ellipse over the face and torso, radial smear at the frame edges) plus warm grading are baked in. There are no punch-ins inside the A-roll and no jump cuts within the 0–8.58 block. The CTA block (38.17+) is a separate take with slightly different framing (head larger and shifted left at about 39.8).

**Persistent chrome:** none. There is no logo, handle, progress bar or watermark.

**Graphics over the speaker:** every overlay sits in the **chest band y 880–1460**, never over the face. Overlays are not boxed; they are white text or white cards with soft glow.

---

## 2. Backgrounds

| Section | Colour | Texture / gradient |
|---|---|---|
| A-roll | Footage | Warm grade: foliage #9fb04a-ish, sky #3e8fe0, skin highlights pushed orange. Heavy radial edge blur |
| Light tutorial | **#EDEBE9** (sampled at the corners and centre, flat, no vignette) | A soft floor-shadow ellipse under the phone: about 640x30 px, centre about y 1595, darkest #828282 → transparent, blurred about 20 px |
| Dark explainer | **#212121** (corners #202020–#222222) | (a) A fine linen/film-grain noise of about ±6 luminance at 1–2 px scale. (b) A thin line grid with cells of about 52–56 px, lines about #2a2a2a, only visible inside a radial mask about 900 px wide around the widget. Near the widget the lines are lit up by its glow (about #3a3a3a) |

Background changes are always **hard cuts**: A-roll → light at 8.583, light → dark at 21.417, dark → A-roll at 38.167. There are no fades or wipes.

---

## 3. Typography

All sizes are for 1080 px width and were measured from glyph bounding boxes.

| Role | Font guess | Size | Weight | Tracking | Colour | Position |
|---|---|---|---|---|---|---|
| Hook kicker "Instagramda" / "bor foydalanmaysiz" | SF Pro Display / Inter Display | 58 px (ascender-to-descender 56–59 px) | 500–600 | −0.04em | #FFFFFF, faint 0 2 10 rgba(0,0,0,.25) shadow | Centred, y 1088–1144 and 1338–1397 |
| Hook hero "CHEATCODE" | Thin condensed grotesk: Antonio 200–300 / Bebas Neue Pro Light / Oswald 200 | about 215 px (cap height 155 px), all caps | 200–300 | −0.01em | #FFFFFF | Centred, x 219–862, y 1163–1318 |
| A-roll captions ("100K ga yaqin organik") | Same sans | about 62 px (ascender-to-descender 60 px) | 500 | −0.05em (very tight; about 0.42em per char) | #FFFFFF (#fffefd) | Centred, y 1398–1458 (baseline about 1445) |
| Dark-scene captions | Same sans | about 48 px (ascender-to-descender 46 px) | 500 | −0.05em | #FFFFFF | Centred, y 1375–1421 when a widget is shown. Vertically centred (y≈945) when it is text only |
| Light-scene label above phone | Same sans | about 44 px (ascender-to-descender 37 px for "reels'ni") | 500 | −0.05em | #211F1E (settled) | y 295–332, phrase centred on x=540 |
| Widget header "Odatiy joylagan reels'ingiz" | Same sans | 38–40 px, 2 lines, line-height 1.2 | 400 | −0.05em | #1a1a1a | Left of the card, next to the emoji |
| Widget index "1." | Same | 56 px | 600 | 0 | #111 | Top-right |
| "Natija" label | Same | 32 px | 400 | −0.04em | #0a1110 | — |
| Result word "Kuzatuvchiga" / "Boshqalarga" | Same | about 62 px (glyph height 53) | 600 | −0.04em | #0C120C | Left-aligned in the card |
| Percent "68%" | Same | 30 px | 400 | 0 | #222 | Right-aligned, on the same baseline |
| Gauge "boshqalarga" / "chiqadi" / "Avval" / "Trial" | Same | 52 px (600) / 44 px (400) / 28 px / 26 px | — | −0.04em | #051011 | Centred in the arc |
| CTA name "Umar \| Shaxsiy brend" / "Marketing, Sotuv" | Same | 40 px, 2 lines, line-height 1.1 | 500–600 | −0.03em | #000 | Left, x 452 |
| CTA button "Obuna bo'ling" | Same | 26 px | 300–400 | −0.02em | #FFF on #227DE5 | — |

- **Case:** sentence case (lowercase Uzbek). ALL CAPS is used only for the one hero word.
- **Line length:** captions are one line only, at most about 32 characters (about 600 px wide). Long sentences are chunked into 2–4-word phrases.
- **Hierarchy:** one hero word per beat. Everything else is a small, uniform, tightly tracked medium sans.

---

## 4. Text / subtitle animation

**Reveal type:** a word-by-word additive reveal **in place**. The whole phrase is laid out centred in its final positions, and each word appears where it will finally sit (at 9.5 s "reels'ni" sits at x 311–445, not centred on its own).

- Each new word enters at about 35–45% opacity (on the dark scene it shows as #9a9a9a grey; on the light scene as light grey). It reaches full opacity and full colour over **4–5 frames (170–210 ms)**, with ease-out. There is a hint of a 4–6 px blur at the start and no positional movement.
- **Timing:** word onset is at the spoken word onset, ±1–2 frames ("Gap" 8.73 vs speech 8.72; "shundaki" appears about 0.25 s later as spoken).
- **Phrase change:** a hard swap. The old phrase disappears in one frame and the first word of the next phrase starts its fade-in in the same frame. There are no exit animations on captions.
- **Hook stack:** the same word logic. "Instagramda" at 0.30, "CHEATCODE" at 0.60 (pops in at full size, with about 3 frames of opacity), "bor" at 0.90, "foydalanmaysiz" at 1.10–1.20.
- **Dark scenes:** the caption hard-cuts out together with the widget exit.

---

## 5. UI components and imagery

### Proof thumbnails (A-roll, 3.05–8.58)
- 3 vertical reel covers, each about 255x455 px with a 14–16 px gap. Together they span x 135–937 and y 885–1338. Radius about 6 px (nearly square).
- Each has an eye-icon view count at the bottom-left ("9,5M", "7,1M", "3,6M"), 28 px white.
- **Entry:** each slides up from about +180 px with motion blur and opacity 0→1 over about 6 frames (ease-out), staggered at about 0.45 s (3.10, 3.55, 4.05), synced with the words.
- They dim to about 55–60% opacity when the profile card lands.

### IG profile card
- About 550x165 px, radius 22, fill **#1C1F23** at about 95% opacity.
- 128 px avatar with the IG gradient story ring (magenta #d6249f → orange #fd5949 → yellow).
- Name 26 px uppercase semibold; stats 30 px / labels 26 px, white.
- A thin red arc is drawn around "233K" (a hand-drawn highlight).
- **Entry:** flies from the bottom-left (−300, +350) rotated about −25°, to its rest position at 0° over **10 frames (≈420 ms)**, expo/back-out with a small overshoot (5.55–5.97). The caption "100K" appears during the flight.

### Phone mockup (light scene)
- iPhone 15 Pro style. The body spans about 565x1160 px (x 260–825, y 380–1540) and is centred.
- Frame: deep purple titanium, about #3b2a3d, with a lighter rim highlight. The screen inset is about 26 px and the screen radius about 90 px.
- The screen is a real screen recording of Instagram's dark UI (#0c0f12; IG blue #3d50f5 "Share" button).
- **Entry (8.58):** the phone rises from about +260 px and from about 0.85 scale to rest over about 8 frames, easing out (expo.out). Its floor shadow tracks it.
- Between steps the phone keeps a subtle float/drift of about 10–20 px.
- **Exit (21.0):** it accelerates upward (power2.in) about 160 px over 5 frames, then a hard cut.

### Hand cursor
- White glove pointer with a 6 px black outline (macOS "pointing hand"), about 120 px tall.
- It moves to the target over about 6–8 frames (power2.inOut).
- **Tap:** it scales to 0.85 over 2 frames and back over 3 frames. The UI then reacts (toggle, navigation) on the next frame.

### Dark widget (main hero component)
- 559x559 px squircle, radius about 120 px (21%).
- Fill: off-white #E9E9ED with a mint tint near the green dots (#DCE9E3).
- **Glow:** white outer bloom, box-shadow 0 0 60px 10px rgba(255,255,255,.35) plus 0 0 140px rgba(255,255,255,.12), so the grid around the card appears lit.
- **Layout:** padding 64 px. Row 1 is the 🎬 Apple emoji (80 px), header text and "1.". Then a 1 px divider (#bfc3c0). Then 4 circles of 100 px diameter in iOS green #4AD477 (between #34C759 and #58E082) with a green glow (0 0 40px rgba(74,212,119,.55)) and a 14 px gap. Then "Natija", the result word with "68%", and a progress bar 430x18 px with full radius, track #8EA595 and fill #4AD477, carrying a moving white specular highlight.
- **Check animation:** a white ✓ (stroke 6 px) draws into one dot at a time (≈1 per 1–1.5 s, synced to phrases). The result word swaps with a hard text replacement.
- **Entry sequence:** a 16 px white dot appears at the widget centre (21.5). Over **8 frames** it grows into a 90 px app-icon tile (radius 22, 🎬, with glow), with a back.out overshoot. It holds about 0.9 s. Then it expands into the full widget over about 8–10 frames, with the content fading in on the last 4 frames — like an iOS app-icon-to-widget expansion.

### Gauge widget
- 419x419 px, radius about 90, fill **#E9FDFC** (mint-white), same white glow.
- Arc gauge of about 270°, stroke 16 px, round caps. The filled part is green #34C759; the remainder is #8B8B91.
- Labels: "Trial" at the top-left, "joylangani" at the top-right; centre stack "Avval / boshqalarga / chiqadi".
- 3 blue circles in #1A7CF5–#227DE5 (60/84/60 px): ⏸ ▶ ✕ glyphs in white.
- **Morph-in at 28.58:**
  - Frames 1–2: the previous widget's content blanks.
  - Frames 3–7: it squashes to a 400x90 bar (scaleY 0.16).
  - Frames 8–14: it re-inflates into a 270 px tile tilted −8°, which grows to 419 px and rotates back to 0° (back.out 1.4).
  - Frames 10–20: the arc draws in from 0 and the labels pop in one by one.

### CTA subscribe pill (38.3–42.8)
- 619x206 px, radius about 70 px (it reads as a fat pill), fill #EEEEEC, white glow 0 0 30px rgba(255,255,255,.7) plus a 6 px pale rim.
- Avatar: B&W photo, 166 px square, radius 34.
- Name text in two lines; button 190x56 px, radius 14, fill #227DE5, inner shadow.
- **Build:**
  1. 38.30–38.50: the avatar tile pops from 0 to 115% to 100% (5 frames) inside a white 6 px rim.
  2. 38.95–39.25: the pill **unrolls to the right** from the avatar (width 166→619, back.out), and the blue button bar slides in.
  3. 39.25–39.9: the text types word by word ("Umar", "|", "Shaxsiy", …), with a blinking text cursor after "Umar |".
  4. 40.55: the button press — it shrinks to 0.5 scale over 4 frames and becomes a small dark #2B2B2B chip (the "subscribed" state).
  5. Exit at 42.5: the elements drop out one by one (avatar, name line 1, pill), each lasting 1 frame.

---

## 6. Transitions and camera

| t | Type | Duration |
|---|---|---|
| 3.05 | Title stack hard-off, cards start | 0 |
| 8.583 | Hard cut A-roll → light; the phone rises in | Cut, then 8 frames (333 ms) entry |
| 21.417 | Phone exits up (5 frames), hard cut to dark; the icon dot pops 2 frames later | 5 frames + 0 |
| 28.583 | Widget squash-morph (not a cut, despite cuts.txt) | 14 frames (≈580 ms) |
| 32.85 | Widget implode: content fade 3 frames → tile shrink 0.7 → gone | 6 frames (250 ms) |
| 38.167 | Hard cut dark → A-roll | 0 |

There are no virtual camera moves in the graphics sections. The only "camera" is the handheld A-roll.

---

## 7. Sync with voice

- Captions are **near-verbatim** but edited: filler is dropped ("shunaqangi"), spelling is normalised, keywords are sometimes promoted ("CHEATCODE").
- Captions sync at word onset (±2 frames).
- **Graphic beats land exactly on the noun they illustrate:**
  - cards on "Biz bu orqali" (3.1)
  - "20 million prasmotr" at 4.68–5.04
  - the profile card on "100 ming" (5.6)
  - the cursor tap on "saxranit" (11.1)
  - the toggle flip on "yoqib" (17.1)
  - each green check on "birinchi soatlarda" / "ko'rsatiladi" / "qiziq bo'lsa"
  - the result word swapping on the matching spoken word (Kuzatuvchiga → Ular → Boshqalarga)
- The tutorial is **literal**: the cursor performs exactly what is said, step by step.

---

## 8. Audio

- The voice is the speaker's lav/on-camera sound. It is clean and compressed; RMS is about −16 dBFS in speech, with no gaps longer than 0.5 s (fast, jump-free delivery).
- **Music bed:** low-end energy (<150 Hz) is about −25 dB throughout and rises about 3–8 dB from the 8.58 s cut (the graphic section). That points to a soft beat or pad under the voice, roughly 10–12 dB below it, running to the end. No music-only breaks.
- **SFX (high-frequency transient peaks over a −50 dB HF floor):**
  - 0.08 s (−27 dB): a whoosh/pop at the cold open, under the title
  - 3.17, 5.25–5.83: card pops / profile fly-in
  - 8.33–8.42: around the hard cut into the phone
  - 13.25, 14.58, 17.42: tap clicks on the cursor taps (the toggle flip at about 17.4)
  - 23.0–23.75: dot checks
  - 30.08: gauge morph
  - **39.08 (−24 dB): the strongest SFX, on the CTA pill expansion**, followed by a softer one at 39.5
- The SFX are subtle UI ticks/pops of about 80–120 ms, not loud whooshes.

---

## 9. Secret sauce (premium details)

1. **Lens edge blur on the A-roll.** The frame edges smear radially and only the face and torso are sharp. It looks shot on a cinema lens, and the white text over the shirt stays legible.
2. **Captions reveal in their final layout positions.** The line never re-centres or jumps, which reads as "typeset", not "auto-captions".
3. **Glow instead of shadow on dark mode.** Widgets emit a white bloom that lights up the background grid, so they feel like lit glass, iOS-style.
4. **Texture on dark.** #212121 is never flat: film-grain noise plus a radially masked grid.
5. **Morphs, not cuts, between widgets.** Icon dot → app tile → widget; widget → flat bar → tilted new widget.
6. **State-based storytelling inside one component.** The checks fill and the result word changes, so the viewer watches one object evolve instead of new slides.
7. **Real product footage.** An actual IG screen recording sits inside a mockup with a floor shadow, and the glove cursor does literal taps.
8. **The CTA pill "unrolls" from the avatar, then the button gets pressed** and changes state — a micro-story inside the CTA.
9. **Hero-word typography.** One ultra-thin condensed caps word at about 215 px, between two 58 px lines.

**Naive-recreation pitfalls**
- Using a bold condensed font for CHEATCODE. It is *thin* (weight 200–300). Bold kills the elegance.
- Loose tracking. All the sans text is at −0.04 to −0.05em. Default tracking looks cheap.
- Drop shadows on the white widgets on dark. They must glow outward (white bloom), not cast black shadows.
- A flat #212121 or flat #EDEBE9 vignette. Dark needs grain plus a grid; the light scene is flat with only a phone floor shadow.
- Re-centring captions word by word, or fading phrases out. The phrase must swap in one frame.
- Scaling or "bouncing" every word. Only opacity/colour animates, over about 180 ms.
- Overlays over the face. Keep everything in y 880–1460 on the A-roll.

---

## 10. Reproducible spec (CSS + GSAP)

```css
:root{
  --bg-light:#EDEBE9; --bg-dark:#212121; --ink:#111; --ink-soft:#211F1E;
  --green:#4AD477; --ios-blue:#227DE5; --card:#E9E9ED; --card-mint:#E9FDFC;
  --font: "SF Pro Display","Inter Display","Inter",system-ui,sans-serif;
  --font-cond: "Antonio","Bebas Neue Pro","Oswald",sans-serif;
}
/* 1. Caption line (centred, word spans pre-laid-out) */
.cap{position:absolute;left:0;right:0;top:1375px;text-align:center;
  font:500 48px/1 var(--font);letter-spacing:-.05em;color:#fff;white-space:nowrap}
.cap.on-aroll{top:1398px;font-size:62px;text-shadow:0 2px 10px rgba(0,0,0,.25)}
.cap.on-light{top:295px;font-size:44px;color:var(--ink-soft)}
.cap .w{display:inline-block;margin:0 .12em;opacity:0}
/* 2. Hook stack */
.kicker{font:550 58px/1 var(--font);letter-spacing:-.04em;color:#fff;text-align:center}
.hero{font:250 215px/0.9 var(--font-cond);letter-spacing:-.01em;text-transform:uppercase;color:#fff}
/* 3. Dark widget */
.dark-bg{background:#212121 url(noise.png);}
.dark-bg::after{content:"";position:absolute;inset:0;
  background-image:linear-gradient(#2b2b2b 1px,transparent 1px),linear-gradient(90deg,#2b2b2b 1px,transparent 1px);
  background-size:54px 54px;-webkit-mask:radial-gradient(circle at 50% 50%,#000 0,transparent 480px)}
.widget{position:absolute;left:260px;top:680px;width:559px;height:559px;border-radius:120px;
  background:var(--card);padding:64px;box-sizing:border-box;
  box-shadow:0 0 60px 10px rgba(255,255,255,.35),0 0 140px rgba(255,255,255,.12)}
.dot{width:100px;height:100px;border-radius:50%;background:var(--green);box-shadow:0 0 40px rgba(74,212,119,.55)}
.bar{height:18px;border-radius:9px;background:#8EA595;overflow:hidden}
.bar i{display:block;height:100%;width:50%;background:linear-gradient(90deg,#4AD477 70%,#c9ffd9 85%,#4AD477)}
/* 4. Phone mockup */
.phone{position:absolute;left:260px;top:380px;width:565px;height:1160px;border-radius:118px;
  background:#3b2a3d;padding:26px;box-sizing:border-box;box-shadow:inset 0 0 0 3px #6a4f6c}
.phone .screen{border-radius:92px;overflow:hidden;background:#0c0f12;height:100%}
.floor{position:absolute;left:220px;top:1580px;width:640px;height:30px;border-radius:50%;
  background:radial-gradient(#828282,transparent 70%);filter:blur(12px)}
/* 5. CTA pill */
.cta{position:absolute;left:230px;top:1184px;height:206px;width:619px;border-radius:70px;background:#EEEEEC;
  box-shadow:0 0 0 6px rgba(255,255,255,.55),0 0 30px rgba(255,255,255,.7);display:flex;align-items:center;padding:18px}
.cta img{width:166px;height:166px;border-radius:34px;filter:grayscale(1)}
.cta .name{font:550 40px/1.1 var(--font);letter-spacing:-.03em;color:#000}
.cta .btn{margin-top:14px;width:190px;height:56px;border-radius:14px;background:var(--ios-blue);
  color:#fff;font:350 26px/56px var(--font);text-align:center}
```

```js
// 1. Word-by-word in-place reveal (call at each word's spoken onset)
tl.fromTo(word,{opacity:0.4,filter:"blur(5px)"},{opacity:1,filter:"blur(0px)",duration:0.19,ease:"power2.out"},t);
// phrase swap: tl.set(prevPhrase,{display:"none"},tNext)

// 2. Hook hero word pop
tl.fromTo(".hero",{opacity:0,scale:1.04},{opacity:1,scale:1,duration:0.125,ease:"power1.out"},0.60);

// 3. Icon dot -> tile -> widget expansion
tl.fromTo(".tile",{scale:0.18,opacity:0},{scale:1,opacity:1,duration:0.33,ease:"back.out(1.7)"},21.5)
  .to(".tile",{width:559,height:559,left:260,top:680,borderRadius:120,duration:0.38,ease:"expo.out"},22.45)
  .from(".widget-content",{opacity:0,y:12,duration:0.17,ease:"power2.out"},22.65);
// checks
tl.from(".dot:nth-child(1) .check",{drawSVG:"0%",duration:0.2,ease:"power2.out"},23.0);

// 4. Widget squash-morph into the next widget
tl.to(".w1 .content",{opacity:0,duration:0.08},28.58)
  .to(".w1",{scaleY:0.16,scaleX:0.72,duration:0.2,ease:"power3.in"},28.62)
  .set(".w1",{display:"none"}).set(".w2",{display:"block"})
  .fromTo(".w2",{scale:0.45,rotation:-8},{scale:1,rotation:0,duration:0.35,ease:"back.out(1.4)"},28.84)
  .from(".w2 .arc",{strokeDashoffset:900,duration:0.45,ease:"power2.out"},28.95);

// 5. Phone entry / exit
tl.fromTo(".phone,.floor",{y:260,scale:0.85},{y:0,scale:1,duration:0.33,ease:"expo.out"},8.583)
  .to(".phone",{y:-160,duration:0.21,ease:"power2.in"},21.2);

// CTA pill unroll + press
tl.fromTo(".cta",{width:202},{width:619,duration:0.3,ease:"back.out(1.2)"},38.95)
  .to(".cta .btn",{scale:0.5,backgroundColor:"#2B2B2B",duration:0.17,ease:"power2.in"},40.55);
```
