# DeZREMAtvBf — "Qanday qilib e'tibor ushlab qolish mumkin?" (Open Loop script lesson)

Creator: Umar Jamoldinov / 0mar.uz ("Shaxsiy brend"). 1080x1920, **25 fps**, 58.56 s, AAC 44.1 kHz.
Hard cuts (cuts.txt): one at 54.28 s (motion graphics -> live talking head, hidden under a glitch).
Evidence files in this folder: `f_*.png` (full-res stills), `tr_*.jpg` (25 fps transition strips), `wd_1.4.jpg` (word blur-in),
`pl_2.2.jpg` (player pill), `cd_7.9.jpg` (card build), `timeline_px.txt` (bg + pager pixels every 0.25 s), `audio_bands.txt`, `spectro.png`.
All px values are at 1080 px width. Measurements come from pixel sampling; font sizes are estimated from glyph metrics (SF Pro cap height 0.705 em, x-height ~0.52 em). Treat them as accurate to about ±4 px.

---

## 1. Format and structure

- Faceless motion graphics with a voiceover for **0–54.3 s**. The last 4.3 s are a live talking-head CTA, the only time the creator appears.
- The piece looks like a **fake iOS onboarding/app screen**. Persistent chrome sits at the top:
  - **Top-left, 2-line "breadcrumb"**: `Ssenariy` (series/category, semibold) over `Open Loop` (episode topic, regular). Both are grey `#7f7d81`, about 28 px, left edge at **x=150** (exactly on a grid line). Baselines are at about y=209 and y=239, so the line pitch is about 34 px.
  - **Top-right, iOS page-control dots**: 4 dots, each 8 px in diameter, on a 22 px pitch (x = 856/878/900/922 .. +8). Their vertical center is y=212 and the right edge is x=930 (on a grid line). The active dot becomes a **24x8 px pill `#007AFF`**.
    It is a **chapter progress indicator**. The pill slides to the next dot at each big theme change, animating together with the background crossfade (about 0.5 s):
    - none active 0–8 s (intro)
    - dot 1: 8–16 s
    - dot 2: 16.3–25.5 s
    - dot 3: 25.8–34 s
    - dot 4: 34.5–54 s
  - Inactive dots are `#8a8a8c` on light/dark backgrounds and white on blue.
  - The chrome never animates out. It sits on the "page", so it crossfades its color with the theme.
- **Content column**: x 145–935 (790 px wide, 145 px side margins). Content is center-aligned.
- **Vertical layout**: the stack's optical center sits at about **y=835**, roughly 125 px above the frame center. The first label sits at y≈390 (top of glyphs) on dense screens and around y≈495 on sparse screens.

### Beat list (time = first visible frame; spoken word timing in brackets)

| t (s) | Theme | Beat |
|---|---|---|
| 0.00 | light | Empty grid page with the chrome only. VO starts immediately ("Videoning…"); there is no visual hook other than the UI itself. |
| 0.50 | light | Grey label **"Birinchi gapdayoq"** blurs in word by word (0.50 / 0.60) [birinchi 0.44, gapdayoq 0.88]. |
| 1.52 | light | Black headline **"butun"** (1.52), **"hikoyani"** (1.60) [bütün 1.46, hikoyani 1.72]. |
| 2.36 | light | Grey sub **"aytib qo'ysangiz,"** [2.32]. |
| 2.40–2.60 | light | **Audio-player pill** rises in under it. 2.64–2.84: the red progress bar shoots to 100 % and "0:30 / 0:30" fades in (metaphor: the whole story is already "played"). |
| 3.50 | light | Grey **"odam davomini"** [3.48]. 4.3: bold **"nega ko'rsin?"** [4.26]. |
| 4.75–5.30 | ->blue | Theme crossfade to blue (see §6). |
| 5.30 | blue | Outlined white pill **"Masalan"** [5.26]. 5.84: white headline **"qandolatchisiz"**. 6.3: 🎂 emoji pops. 6.9: light sub **"Shunday boshladingiz:"**. |
| 7.50–8.20 | ->light | Theme crossfade. Pager dot 1 activates. |
| 8.00 | light | A **white card** fades and rises in. Label "Birinchi gap"; the quote **«Mijoz tortning rangini yoqtirmadi,** types in word by word (8.14–9.3). 10.1–11.0: line 2 **men pulini qaytarib berdim»** (the card grows taller). |
| 11.0 | light | Badge **"Hammasi aytildi"** (red text on a grey capsule) fades in at the card's top-right. |
| 11.5 | light | A second card slides up below. "Nima bo'ldi?" + green **"Bildi"** capsule (12.2). Divider. "Qanday tugadi?" + "Bildi" (13.5). |
| 14.8 | light | Both cards dim to about 50 % opacity. "Endi davomida" (15.0), **"nimani kutadi?"** (15.5). |
| 15.75–16.50 | ->dark | Theme crossfade. Pager dot 2. |
| 16.5 | dark | "Shu voqeani" (16.5), **"boshqacha boshlang"** (17.1). 17.6: dark card. 18.3: "🎂 «Tort tayyor." 19.3: "Yetkazishga 1 soat qolgan edi." 20.0: orange countdown capsule **00:59:59**. 21.6: **iOS notification banner** drops in (blue Messages icon, "Mijoz", "hozir", skeleton lines). 22.8–24.7: "Uni o'qib, buyurtma pulini / qaytarishga qaror qildim.»" |
| 25.25–25.75 | ->light | Theme crossfade. Pager dot 3. |
| 26.0 | light | "Endi savollar paydo bo'ladi". 27.4: **blue Figma-style cursor plus blue chat bubble "Nima yozdi?"**. 28.3: **orange cursor plus orange bubble "Nega tortni tuzatib bermadi?"**. |
| 29.5–30.4 | light | A **blue ring strokes on** clockwise and stops about 80 % closed, leaving a grey track gap: the literal "open loop". 30.4: **"Open Loop"** blurs in inside the ring [open 30.36]. 31.3: "odam javobini bilmoqchi bo'lgan". 33.6: bold "savolni ochasiz". |
| 33.9–34.6 | ->dark | Theme crossfade. Pager dot 4. |
| 34.8 | dark | "Keyin aytasiz". 35.0 / 36.6 / 38.3: a **vertical timeline** of 3 dark row-cards with numbered blue nodes and a connector line: "📝 Nima kelishilgan / buyurtma shartlari", "⚠️ Qayerda muammo chiqdi / rang, dizayn, sabab", "💸 Nega pul qaytarildi / qaror sababi". Each arrives on its spoken word. |
| 40.0–40.7 | ->light | Theme crossfade. |
| 41.3 | light | "Javobni ataylab", **"cho'zavermang"** (42.0). 42.5–45.0: a **5-node stepper**; the blue line fills node to node (about 0.45 s per segment); caption "Har bir gap – oldinga". |
| 45.0–47.4 | light | A **green ring draws** and the check fills at 47.4. "Oxirida savolga" (45.7), **"javob bering"** (47.4). |
| 47.6–48.4 | ->dark | Theme crossfade. |
| 48.6 | dark | "Keyingi ssenariyingizning", **"birinchi gapini o'qing"** (49.5–50.3). A skeleton text card with a white highlight sweep. 51.0: green-outlined capsule **"✓ Savol qoldiryaptimi?"**. 52.6: "yoki". 53.0: red-outlined capsule **"✕ Hammasini aytib bo'ldimi?"**. |
| 54.1–54.5 | ->live | **Digital glitch / slice displacement transition** (about 0.3 s) into the talking head. Hard cut at 54.28. |
| 54.9–58.5 | live | CTA over footage: white "Sahifaga" (light) + **"obuna bo'ling"** (bold). 55.5: blue capsule button "Obuna bo'lish". A mouse cursor clicks at about 56.8 and the button turns grey "Obunadasiz". |

- **Hook (0–3 s)**: there is no visual shock. The hook is the voice plus instant clean UI: the label at 0.5 s, the headline at 1.5 s, and the progress-bar "payoff" gag at 2.6 s. The first frame is the empty branded page, so the brand look itself acts as the thumbnail.
- **Ending**: a talking-head CTA asking the viewer to subscribe. A simulated click turns "Obuna bo'lish" into "Obunadasiz".

## 2. Backgrounds

Three themes, all of them full-frame vertical gradients. The chrome and grid persist across them.

| Theme | Top (y≈5) | y≈600 | y≈960 | y≈1300 | Bottom (y≈1900) | Overlay |
|---|---|---|---|---|---|---|
| **Light** | `#F9F9F9` | `#F5F5F7` | `#F0F0F3` | `#EEEEF0` | `#EBEBED` | Square grid: **130 px cells**, **2 px lines**, lines at x = 20 + 130k and y = 50 + 130k, line color `#E6E6E8` (about 4 % darker than the bg) |
| **Dark** | `#171719` | `#1A1A1C` | `#202022` (a faint lighter band/glow through the middle) | `#171719` | `#121214` | The same grid, lines about `#222225` (≈ +5 % luminance) |
| **Blue** | `#1C86FD` (flat to y≈400) | `#187CE6` | `#176ECD` | `#1261B5` | `#0D4C90` | **Concentric ellipses** centered at about (540, 980): 1 px hairlines, white at about 8–10 % opacity, radius step ≈155 px (vertical), ellipse aspect ≈1.2 tall. No grid. |

- CSS, light: `linear-gradient(180deg,#F9F9F9 0%,#F5F5F7 30%,#EEEEF0 68%,#EBEBED 100%)`
- CSS, blue: `linear-gradient(180deg,#1C86FD 0%,#1C86FD 18%,#176ECD 50%,#1261B5 68%,#0D4C90 100%)`
- CSS, dark: `radial-gradient(120% 40% at 50% 50%, #202022 0%, rgba(32,32,34,0) 70%), linear-gradient(180deg,#171719,#121214)`
- No visible noise or grain on the graphics (H.264 banding only).
- **Theme change**: a ~0.5 s dissolve (12–13 frames at 25 fps). See §6.

## 3. Typography

- **Family: SF Pro Display** (Apple system font). Evidence: the double-storey `a`, flat-terminal `t`, round `?`, SF numerals in "00:59:59", and Apple Color Emoji everywhere.
  - Fallback for the web: `-apple-system, "SF Pro Display", "Inter", system-ui`. With Inter, use tracking −0.02 em.
- **Hierarchy system** (stacked and centered): **eyebrow label (light, grey) -> headline (bold, black/white) -> sub (light, grey) -> optional second bold line**.

| Role | Size (px @1080w) | Weight | Color (light theme) | Color (dark/blue) | Notes |
|---|---|---|---|---|---|
| Eyebrow / connector label ("Birinchi gapdayoq", "Endi davomida") | **48–52** | Light 300 (SF Display Light) | `#7B7B7E` | dark: `#8E8E93`; blue: white @ ~75 % | Sentence case, tracking ≈ −0.01 em |
| Primary headline ("butun hikoyani", "qandolatchisiz") | **~106–110 at max**; auto-shrinks to fit ≤ 790 px (e.g. "boshqacha boshlang" ≈ 80 px, "Open Loop" ≈ 78 px) | Bold 700 | `#000`–`#0B0B0B` (sampled `#010103`) | `#FFFFFF` | Lowercase or sentence case; tracking ≈ −0.02 em; one line only, never wraps |
| Secondary bold line ("nega ko'rsin?", "savolni ochasiz", "javob bering") | **58–62** | Bold 700 | `#111` | white | |
| Sub ("aytib qo'ysangiz,", "odam javobini…") | 43–50 | Light 300 | `#7F7F82` | as eyebrow | |
| Card body / quote | **46** | Semibold 600 | `#080808` | white | Line pitch **71 px** (line-height ≈ 1.5) |
| Card meta label ("Birinchi gap") | 24–26 | Regular 400 | `#7C7C7C` | `#8E8E93` | |
| List row text ("Nima bo'ldi?") | 40 | Regular 400 | `#0B0B0B` | white | |
| Chrome breadcrumb | ~28 / ~28 | Semibold / Regular | `#7F7D81` | white (blue), `#8E8E93` (dark) | Left-aligned at x=150 |
| Capsule text | 26–30 | Semibold 600 | per capsule | | |

- **Vertical rhythm** (the stack measured at 3.8 s):
  - label top 493 / baseline ≈533
  - headline top 593 / baseline **674** / descender 694
  - sub top 737
  - player 899–1010
  - grey line top 1144
  - Gaps are about 50 px between text blocks and about 110 px around components.
- **Max characters per line**: the headline is ≤ 18 characters (it shrinks to fit 790 px), labels ≤ 30, card body ≈ 36.
- **Alignment**: everything is centered except card interiors, which are left-aligned with 40 px padding.

## 4. Text animation

- **Per-word "blur-in" reveal**, timed to the spoken word (see `wd_1.4.jpg`). Each word goes from:
  - `filter: blur(10–12px)`, `opacity: 0.5`, `x: +20–24 px` (it drifts left into place), color slightly grey
  - to sharp, opacity 1, x 0, in **3–4 frames (120–160 ms)**
  - ease ≈ `power3.out` / `expo.out`
- **Stagger = speech**: words appear at their individual onset, usually 0–60 ms before or at the spoken onset. Measured gaps: "butun" 1.52 -> "hikoyani" 1.60 (80 ms); "Birinchi" 0.50 -> "gapdayoq" 0.60.
- **Layout is pre-computed**: words appear in their final centered positions. The line does not re-center as words arrive, so the first word appears left of center.
- **Stacking**: new lines are appended below. Previous lines never move or shrink (there is no push-up within a scene). When a scene ends, everything leaves together via the theme dissolve. Within a scene, older content may **dim** to about 45–50 % opacity when focus shifts (cards at 14.8 s).
- **Exits**: there are no per-word exits. The whole page dissolves (opacity plus a slight blur) during the theme transition.
- Bold words and grey words use the identical animation.

## 5. UI components

**A. White card** (8–16 s)
- 790 x 322 px at x 145–935, y 534–856.
- **Radius 40 px**, bg `#FCFCFC`, **1 px border `#E0E0E2`** (≈ rgba(0,0,0,0.08)).
- **Shadow below only**: darkest `#D9D9DB` right under the edge, fading to the bg (`#E7E7E9`) over about 40 px; there is no shadow above. Approximate: `box-shadow: 0 1px 0 rgba(0,0,0,.04), 0 18px 40px -8px rgba(0,0,0,.10)`.
- Padding 40 px (left text at x=185). The card height animates when a new line is added (≈0.3 s, `power2.out`).
- The second card sits **38 px below** (y 894–1127, 233 tall). Row dividers are 2 px `#E2E2E2`, inset 40 px.
- **Enter**: opacity 0 -> 1, y +20 -> 0, blur 8 -> 0, scale 0.98 -> 1 over ≈0.4 s (`cd_7.9.jpg`).

**B. Dark card** (16–25 s)
- Same geometry. Bg `#2C2C2E` (iOS secondarySystemBackground dark), 1 px border `rgba(255,255,255,.08)`, deep shadow `0 20px 50px rgba(0,0,0,.5)`.

**C. iOS notification banner** (inside the dark card)
- White `#FFFFFF`, radius ≈36, 714 x 152 px.
- Blue `#0A7AFF` app squircle (78 px, radius 18) containing a white speech bubble.
- Title "Mijoz" 32 px semibold; "hozir" 24 px grey right-aligned.
- Two skeleton bars (`#E5E5EA`, 14 px tall, rounded).
- **Enter**: drops from y −20 with blur, grey -> white, ≈0.35 s.

**D. Audio-player pill**
- 608 x 112 px (x 236–843, y 899–1010), radius 56 (full).
- Bg `#FCFCFC`, faint top border, soft shadow below (`#E0E0E2` -> bg over ~35 px).
- Black ▶ triangle, 28 x 34 px, at x 292.
- Track: 6 px tall, radius 3, x 358–740. Fill **`#FC3634`** (Apple red `#FF3B30`), unfilled track `#E5E5EA`.
- Time label "0:30 / 0:30": 22 px, grey.
- **Build**:
  1. Pill fades and rises (y +12 -> 0, blur 6 -> 0, 0.3 s).
  2. Progress `scaleX 0 -> 1` from the left over **0.20–0.25 s** (`power2.inOut`) with a feathered leading edge.
  3. The time label fades in 0.1 s after the fill finishes.

**E. Capsules / badges**
- **Outlined "Masalan"** (on blue): 156 x 58 px, 2 px white border, transparent fill, white 30 px semibold.
- **"Hammasi aytildi"**: capsule ≈204 x 44 px, bg `#E5E5EA` (sampled `#E1E1E5`), text Apple red `#FF3B30`, 28 px semibold.
- **"Bildi"**: 90 x 48 px, bg **`#31C456`** (≈ `#34C759`), white 28 px semibold text. **Enter**: a blurred green blob that sharpens and scales 0.8 -> 1 over ≈0.25 s.
- **Countdown "00:59:59"**: bg `#FF9F0A` (orange), black-brown text, about 148 x 50 px.
- **Outlined result capsules** (48–53 s): dark fill `#1C1C1E`, 2 px border green `#30D158` / red `#FF453A`, with a leading ✓ / ✕ circle icon.

**F. Chat bubbles with cursors**
- Bubble fill `#0A7AFF` (blue) or `#FF9500` (orange), white 34 px semibold text, radius full, height 68 px.
- A matching colored arrow cursor (≈30 px) sits at the bubble's top-left, Figma multiplayer style.
- **Enter**: the cursor arrives first, then the bubble pops (scale 0.6 -> 1, back.out(1.6), 0.3 s).

**G. Progress ring "Open Loop"**
- Ring diameter ≈560 px (center about (540, 1040)), stroke **12 px `#0A7AFF`** with round caps.
- Grey track `#E5E5EA` visible in the gap from roughly 8 o'clock to 10 o'clock.
- Draws clockwise from 10 o'clock over ≈0.9 s (`power2.inOut`) and stops at ≈80 %.
- The green version (45–47 s) is ≈230 px, stroke 8 px `#34C759`. It closes 100 %, then a filled green check circle pops in.

**H. Stepper / timeline**
- **Horizontal** (42–45 s): 5 blue nodes, 14 px each, connected by a 4 px line. The line fills node to node.
- **Vertical** (35–39 s): blue numbered nodes (24 px) with a 2 px connector line. Dark row cards 410 x 90 px, radius 18, `#2C2C2E`, each with an emoji icon in a 40 px tile.

**Emoji**: Apple Color Emoji only (🎂 📝 ⚠️ 💸), used as icons, never decoratively scattered.

## 6. Transitions and camera

- **Theme change (light <-> blue <-> dark)**: 12–14 frames, **480–560 ms**.
  1. The old page (content plus bg) fades out while the new bg fades in. The midpoint mixes, e.g. light -> blue passes through pale `#BFD8F8`.
  2. The old content also blurs slightly, and the old "page" appears to **scale down ~2–3 %** (a thin page edge is visible in `tr_4.5.jpg` / `tr_15.6.jpg` frames 0.36–0.50).
  3. New content starts blurring in ≈0.2 s before the dissolve completes, so the two overlap.
  4. Pager pill moves simultaneously.
  - Ease ≈ `power2.inOut`.
- **Within a theme there are no cuts**: new components build into the same page.
- **No camera moves**: no zoom, pan or parallax during the graphics. The frame is static, which reads as a real app screen.
- **Graphics -> live (54.1–54.5 s)**: RGB/slice glitch for 8–10 frames. Horizontal slices displace, text duplicates, the footage bleeds in, then settles clean.

## 7. Voice sync

- Text is **semi-literal**: the on-screen words are the key clause of each sentence, copied verbatim. Filler words ("Videoning…", "Bu,", "Yani") are dropped.
- Each word appears on its own spoken onset (±60 ms). Bold weight is reserved for the payload noun/verb phrase.
- Components appear on the noun that names them: player on "aytib qo'ysangiz", ring on "open loop", "Bildi" capsules on "bildi", timeline rows on each enumerated clause.
- Speech is 147 wpm with a speech ratio of 0.87. Pauses between sentences are only 0.3–0.6 s, and every pause gets a new visual.

## 8. Audio

- **Voice dominant**, dry, close-mic, normalized. Peaks ≈ −8 dBFS; short-term loudness around −14 dBFS.
- **Music bed**: very low. Energy below 90 Hz holds at about −28 to −30 dBFS throughout 5–54 s, against about −35 to −45 dBFS for 0–4 s. The gaps between words never drop below about −40 dBFS. This suggests a soft, low, beat-less pad/bass bed entering around the first theme change (≈5 s) and ducked under the voice.
- **SFX**: subtle. High-band (>6 kHz) bumps of about −33 to −35 dBFS coincide with theme dissolves (16.5, 26.0, 48.6) and component pops (3.2, 19.7). These suggest soft "whoosh" and "tick" UI sounds. There are no loud risers, booms or clicks.
- There is a voice-edit gap (silence) at ≈5.0 s and at 34.3 s, exactly at the theme transitions. The VO was edited so that transitions land on breaths.
- The live CTA (54.3+) carries room-tone audio from the footage.

## 9. Secret sauce

1. **It is an app, not a slide.** Chrome breadcrumb, iOS page dots as chapter progress, grid paper and system colors make it feel like a real product UI. Viewers parse it instantly as "Apple".
2. **One font, three weights, two greys.** Only SF Pro Light grey + Bold black, with a huge contrast in size (≈52 vs ≈108 px) and weight. There is no colored text except system-color capsules.
3. **Words land on syllables.** Per-word blur-in is synced to the voice within about 2 frames and is very short (≈140 ms). It feels "spoken", not "animated".
4. **Metaphor components**: a progress bar already at 100 % ("story told"), an 80 % ring (open loop), cursors asking questions, a 00:59:59 timer, a notification banner. Each concept gets one literal iOS widget.
5. **Disciplined grid**: 130 px grid, 145/150 px margins, everything snaps to grid lines (chrome at x=150, dots end at x=930).
6. **Theme rhythm**: light -> blue (example) -> light -> dark (story) -> light (insight) -> dark (instruction). The color change is the chapter break, roughly every 8–10 s.
7. **Static camera, rich micro-motion**: nothing zooms, so the small builds (fills, pops, ticks) carry all the energy.
8. **Shadows only below, 1 px hairline borders, radius 40**: real iOS card physics.

**What a naive recreation gets wrong**
- It uses Inter/Montserrat at one weight, or animates whole lines instead of words.
- It uses fades that are too slow (400 ms+). The blur-in here is about 140 ms.
- It re-centers the line as each word arrives.
- It adds camera zooms, Ken Burns or bouncy easing everywhere.
- It uses pure `#FFFFFF` backgrounds without the subtle gradient and 2 px grid.
- It gives shadows a 0 offset, which makes a glow instead of a lift.
- It skips the page-dot chapter indicator.
- It adds loud music or whooshes.
- It lets headlines wrap instead of shrinking them to fit one line.

## 10. Reproducible spec (CSS + GSAP)

```css
:root{
  --font: -apple-system,"SF Pro Display","Inter",system-ui,sans-serif;
  --ink:#0B0B0B; --grey:#7B7B7E; --blue:#007AFF; --red:#FF3B30; --green:#34C759; --orange:#FF9F0A;
}
.page{position:absolute;inset:0;font-family:var(--font);}
.page.light{background:linear-gradient(180deg,#F9F9F9 0%,#F5F5F7 30%,#EEEEF0 68%,#EBEBED 100%);}
.grid{position:absolute;inset:0;background-image:
   repeating-linear-gradient(90deg,transparent 0 19px,var(--gl) 19px 21px,transparent 21px 130px),
   repeating-linear-gradient(180deg,transparent 0 49px,var(--gl) 49px 51px,transparent 51px 130px);}
.light .grid{--gl:#E6E6E8} .dark .grid{--gl:#222225}
.page.dark{background:radial-gradient(120% 40% at 50% 50%,#202022,rgba(32,32,34,0) 70%),linear-gradient(180deg,#171719,#121214);}
.page.blue{background:linear-gradient(180deg,#1C86FD 0%,#1C86FD 18%,#176ECD 50%,#1261B5 68%,#0D4C90 100%);}
/* chrome */
.crumb{position:absolute;left:150px;top:182px;font-size:28px;line-height:34px;color:#7F7D81}
.crumb b{font-weight:600;display:block}
.dots{position:absolute;right:150px;top:208px;display:flex;gap:14px}
.dots i{width:8px;height:8px;border-radius:4px;background:#8A8A8C;transition:none}
.dots i.on{width:24px;background:var(--blue)}
/* type */
.eyebrow{font:300 50px/1.15 var(--font);color:var(--grey);letter-spacing:-.01em;text-align:center}
.headline{font:700 108px/1.05 var(--font);color:var(--ink);letter-spacing:-.02em;text-align:center;white-space:nowrap}
.word{display:inline-block;will-change:filter,transform,opacity}
/* card */
.card{position:absolute;left:145px;width:790px;border-radius:40px;background:#FCFCFC;
  border:1px solid rgba(0,0,0,.08);padding:40px;box-shadow:0 18px 40px -8px rgba(0,0,0,.10),0 2px 6px rgba(0,0,0,.04)}
.dark .card{background:#2C2C2E;border-color:rgba(255,255,255,.08);box-shadow:0 20px 50px rgba(0,0,0,.5)}
/* player pill */
.player{width:608px;height:112px;border-radius:56px;background:#FCFCFC;box-shadow:0 14px 30px -10px rgba(0,0,0,.12)}
.player .track{position:absolute;left:122px;width:382px;top:53px;height:6px;border-radius:3px;background:#E5E5EA}
.player .fill{height:100%;border-radius:3px;background:#FC3634;transform-origin:0 50%}
/* capsule */
.capsule{display:inline-flex;align-items:center;height:48px;padding:0 20px;border-radius:24px;font:600 28px var(--font)}
.capsule.green{background:#34C759;color:#fff}.capsule.redtext{background:#E5E5EA;color:#FF3B30}
.capsule.outline{border:2px solid currentColor;background:transparent;color:#fff;height:58px}
```

```js
// 1. per-word blur-in (call at each word's VO onset; layout precomputed, final positions)
tl.fromTo(word,{opacity:.5,filter:"blur(12px)",x:22},{opacity:1,filter:"blur(0px)",x:0,duration:0.14,ease:"power3.out"},t);

// 2. card / component enter
tl.fromTo(card,{opacity:0,y:20,scale:.98,filter:"blur(8px)"},{opacity:1,y:0,scale:1,filter:"blur(0px)",duration:0.4,ease:"power3.out"},t);
// card grows when a line is appended
tl.to(card,{height:"+=71",duration:0.3,ease:"power2.out"},t2);

// 3. player pill + progress
tl.fromTo(player,{opacity:0,y:12,filter:"blur(6px)"},{opacity:1,y:0,filter:"blur(0px)",duration:0.3,ease:"power2.out"},t)
  .fromTo(fill,{scaleX:0},{scaleX:1,duration:0.22,ease:"power2.inOut"},t+0.28)
  .fromTo(timeLabel,{opacity:0},{opacity:1,duration:0.12},t+0.52);

// 4. capsule pop (Bildi / chat bubble)
tl.fromTo(cap,{opacity:0,scale:.8,filter:"blur(6px)"},{opacity:1,scale:1,filter:"blur(0px)",duration:0.25,ease:"back.out(1.6)"},t);

// 5. theme transition (≈0.5 s) + pager
tl.to(oldPage,{opacity:0,scale:.975,filter:"blur(6px)",duration:0.5,ease:"power2.inOut"},t)
  .fromTo(newPage,{opacity:0},{opacity:1,duration:0.5,ease:"power2.inOut"},t)
  .to(dotOld,{width:8,background:"#8A8A8C",duration:0.4,ease:"power2.inOut"},t)
  .to(dotNew,{width:24,background:"#007AFF",duration:0.4,ease:"power2.inOut"},t);

// ring (open loop): SVG circle r=274, stroke 12, round caps
tl.fromTo(ring,{strokeDashoffset:C},{strokeDashoffset:C*0.2,duration:0.9,ease:"power2.inOut"},t);
// emphasis dim of older content
tl.to(olderCards,{opacity:.5,duration:0.3,ease:"power1.out"},t);
```
