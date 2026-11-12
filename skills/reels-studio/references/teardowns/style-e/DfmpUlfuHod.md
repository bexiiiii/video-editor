# DfmpUlfuHod — "MNU шекті балды 140-қа көтерді" (ҰБТ news explainer, Kazakh)

Creator: a Kazakh history / ҰБТ (UNT) exam-prep channel (education news rubric). It is named here only as the source; never reuse its name, logo or handle.
Format: 1080x1920, **30 fps**, 112.64 s, VP9 + AAC 44.1 kHz stereo.
Evidence lives in `research/an/DfmpUlfuHod/`:
- `f_*.png`: full-res stills
- `tr_*.jpg`: 30 fps strips around a beat swap, a data-card build and the question beat
- `tabs.txt`: tab fill sampled at 10 fps
- `activity.txt`: content and caption ink per frame
- `transcript.json`: forced `kk` ASR (faster-whisper small, 242 words)
- `boxes.py`: card detector
- `cmp_ref_vs_demo.jpg`: the reference against the Style E demo

All px values are at 1080 px width, measured by pixel sampling (±3 px). Font sizes are derived from glyph cap height, using Inter cap = 0.727 em.

---

## 1. Format and structure

- Faceless motion piece with a voiceover. It is **one continuous page with no hard cuts** (`cuts.txt` is empty).
  - Real B-roll appears only *inside* rounded video cards. The footage has its own cuts there.
- **Persistent chrome**, the same from frame 0 to the end:
  - **Channel header** at y 96–184:
    - Logo: 88 px rounded square (r ≈ 22) at x 64.
    - Name: 37 px / 700, cap 109–135, at x 175.
    - Handle: 24 px grey, y 153–173.
    - **Rubric pill** on the right, x 760–1016, y 112–168:
      - bg `#F4F4F6`, fully rounded
      - yellow dot `#FDC604` ~14 px
      - text 23 px / 600 `#1B1B1E`, e.g. "ҰБТ жаңалығы"
  - **Chapter tabs** under the header: 6 segments at x 64–1016, each 152 px wide with an 8 px gap.
    - Bar: y 212–217 (6 px, r 3). Inactive bars are `#E7E7E9`; done and current bars use the gold gradient.
    - Label: 20 px, cap top 231. The current label is black / 600; the others are light grey.
    - Chapter names: Жаңалық · Шекті балл · Реакция · Статистика · Себебі · Болжам.
- **Content column**: x 64–1016 (952 px), left-aligned.
  - Vertically, the content block always starts at **y ≈ 338** (kicker line box) and the cards end at **y 1350**.
- **Caption tier**: two centred lines at y 1440–1535, independent of the beats.
- Speech: 242 words in 112.6 s ≈ **129 wpm** (agglutinative Kazakh). Sentence pauses are 0.3–0.5 s.

### Beat list (first sharp frame; spoken sentence in brackets)

| t (s) | Tab | Beat |
|---|---|---|
| 0.00–5.03 | Жаңалық (fills 0.5–1.1) | **News cover card** (photo of the university, 952×1020). Spaced kicker "ҰБТ-2027 · ЖАҢАЛЫҚ"; white title "MNU шекті балды / **140**-қа көтерді" (gold "140"); at 3.0 a gold dash + "Бұл шешімнің артында не тұр?". The card is on screen, blurred, from frame 0 and sharp by 0.5. |
| 5.23–10.43 | | Kicker "@mnu.kz • Ресми пост"; headline "2027 жылғы MNU-дағы / **шекті балдар**". **Post image** (576×765, left) plus a **stats column** that builds 6.0 / 6.5 / 6.8 / 7.2: ♥ 8 061 лайк (gold disc) · 💬 667 пікір · ⇄ 99 репост · ➤ 17,4 мың бөлісу. |
| 10.60–15.60 | Шекті балл (10.45) | "2027 · Мемлекеттік грант"; "Шекті балл - **140 балл**". **Numbered chips** ① Халықаралық қатынастар (11.0) ② Аударма ісі (12.2). **Data card** (13.53): "Шекті балл", gold **140 / 140** count-up 13.7–14.6, gold bar, note "ҰБТ-ның ең жоғары нәтижесі". |
| 15.83–21.73 | | "Шекті балл - **135 балл**". **2×2 tiles** on their spoken words (15.9 / 16.4 / 16.9 / 17.4): line icon, gold ↑ badge, title (Құқық, Маркетинг, Менеджмент, Қаржы), gold sub "шекті балл · 135". |
| 21.97–26.03 | Реакция (21.75) | "Ресми пост · Пікірлер"; "Оқушылар реакциясы **қандай?**". A real **comment screenshot** card scrolls up slowly. |
| 26.30–28.00 | | "MNU · Статистика"; "Сандар нені **көрсетеді?**". **Chart card** "Университетке қызығушылық артып келеді" with a gold pill "Қызығушылық". The gold curve draws 26.5–27.5. |
| 28.27–39.83 | Статистика (28.05) | "MNU · Қабылдау статистикасы"; "Студенттер саны / **артып келеді**". **Video card** (B-roll, inner cuts every 1–2 s) plus a **compare row**: "2025 жылы қабылданды" counts 0 → **1800+** (33.0–34.0); at 37.3 a gold → and "2026 жылы" **2500+** (count 37.5–38.5). |
| 40.03–50.30 | | "2026 жыл · ҰБТ нәтижесі"; "Үздік талапкерлердің / таңдауы - **MNU**". **Question card**: gold **?**/12 + question text with gold accent words (40.5). **Dot row**: 12 grey discs pop in 41.0–42.0, then at 47.8–48.5 the first 8 turn gold (one per ≈ 0.09 s) while ? → 6 → **8**. Legend "● MNU · 8 ● Басқа университеттер · 4". |
| 50.53–62.63 | | "Мемлекеттік грант · Қазақстан бойынша"; "Грант иегерлерінің / көбі - **MNU-да**". **Percent rows**: "Халықаралық қатынастар" **86%** (count + bar 50.9–55.0), then "Аударма және лингвистика" **93,2%** (57.0–61.0), note "грант иегерлерінің үлесі". |
| 62.83–64.03 | | **Question beat**: big gold **?** + "Бұл нені білдіреді?", centred, alone. |
| 64.27–74.97 | Себебі (64.05) | "Жоғары сұраныс · Жоғары талап"; "Академиялық іріктеу / **күшейіп келеді**". Video card plus two **icon chips** (gold ↑ disc + 2 lines) at 67.0 and 70.5. |
| 75.13–89.93 | Болжам (74.95) | "Ықтимал өзгерістер"; "Іріктеу талаптары / **күшеюі** мүмкін". **Chart card** "Талапкерлер мен гранттар": the gold "Бәсекелестік" line draws *slowly* (75.5–81.0); a grey dotted "Грант саны" line follows at 86.5–88. |
| 90.17–98.63 | | "Қабылдау саясаты · Білім сапасы"; "Басты басымдық - **сапа**". **Toggle card**: "Тек / Студент санын көбейту" is ON (gold) and flips OFF at 93.5 (title greys out). A chip "Академиялық көрсеткіші жоғары талапкерлер" appears; at 97.0 "Басымдық / Жоғары балл" flips ON. |
| 98.70–105.67 | | **Cover card** again (summary): "MNU · ЖАҢА ҮРДІС" / "Жоғары білімдегі / **өзгерістердің** / бастауы". |
| 105.97–112.64 | | "Сіздің пікіріңіз"; "Өзге университеттер де шекті / балды **140**-қа көтере ме?". **Poll card** (Иә, көтереді / Жоқ, көтермейді) plus a comment input with the channel avatar. The video ends on this (loop). |

- **Hook**: there is no visual shock. It is the news cover card plus a hard number in the first spoken sentence (the "140" is gold on the cover).
- **Ending**: a poll / comment CTA, held. There is no follow button and no "save" prompt.

## 2. Backgrounds

- **Flat near-white `#FCFCFC`** (sampled #FCFCFC–#FDFDFD at the top, middle and bottom).
  - No gradient, no grid, no grain, no theme changes. The page never changes colour in 112 s.
- **Cards**: `#F4F4F6`, radius ≈ 32 (cover ≈ 36). **No border, no shadow**: the edge is a 1-step colour change (`#F4F4F6` → `#FDFDFD`).
- Inner white rows (`#FFFFFF`) appear only in the poll card.
- The cover card sits on a dark photo with a bottom gradient (≈ 40 % → 100 % to `#110F0D`). This is the only dark area.

## 3. Typography

- **Family**: an SF-Pro-like neo-grotesk. Evidence: double-storey a, flat terminals, tight spacing, and the full Kazakh set ә ғ қ ң ө ұ ү і.
  - Substitute: **Inter** (opsz). Kazakh Cyrillic is in its cyrillic-ext subset.
  - The caption track is a **condensed-feeling heavy uppercase with very tight tracking**. Substitute: **Inter Tight 800**.

| Role | Measured | Size / weight | Colour |
|---|---|---|---|
| Source kicker ("@mnu.kz • Ресми пост", "2027 · Мемлекеттік грант") | cap 22, y 347–377 | **30 / 600** | brown-gold `#A26A2A` (darkest sampled #83592E) |
| Headline | Ш cap 59 (405–464), line pitch ≈ 90 | **80 / 700**, −0.035 em, ≤ 2 lines | `#101011`; accent words in the **gold gradient** |
| Cover title | lines 1010–1109 / 1120–1199 | 84 / 700 white, −0.04 em | gold accent `#E89E0C→#A8672C` |
| Cover kicker | | 30 / 700, tracking +0.16 em, uppercase | white @ 72 % |
| Big number (data card) | digits **176 px** tall (951–1127) | **240 / 700**, −0.055 em | gold gradient; "/ 140" ≈ 74 px `#B4B4B9` |
| Percent value | digits ≈ 97 px | ≈ 132 / 700 | gold gradient, decimal comma "93,2%" |
| "?" (question beat) | glyph 206 px tall (580–786) | ≈ 400 / 800 | gold vertical gradient |
| Question line | cap ≈ 57 | ≈ 72 / 700 | ink |
| Card label / note | | 26 / 500 grey · 26 / 600 ink | |
| Stat value / label | | 46 / 700 · 24 / 600 grey | |
| Channel name / handle | cap 27 · x-height 15 | 37 / 700 · 24 / 400 | ink · grey |
| Tab label | cap 16 | 20 / 500 (current 600) | grey / ink |
| **Caption** | cap **35** (1440–1475), line pitch **58** | **48 / 800 uppercase**, ≈ −0.045 em | **`#5E5E5E`** (darkest sampled #676767) |

- **Alignment**: everything is left-aligned (kicker, headline, cards) except the caption track and the question beat, which are centred.
- **Gold gradient**: horizontal `#E59904 / #E49B05` (left) → `#CF8328` → `#AD692E / #A86827` (right), sampled on the tab bars and the "140". Numbers and the "?" use a top-to-bottom version.

## 4. Text animation

- **Headline and kicker are revealed as blocks, not word by word.**
  - Each element blurs in (blur ≈ 14–18 px → 0, opacity 0 → 1, slight scale/rise) over **≈ 0.25–0.35 s**, ease-out.
  - Order: kicker → headline (+≈ 0.07 s) → cards (+≈ 0.1 s each).
  - Strip `tr_4.85.jpg`: kicker at 5.23, the headline's 2 lines together at ≈ 5.30, the post card at ≈ 5.33, all sharp by ≈ 5.55.
- **Word-level sync lives in the caption track** (§7).
- **Text never exits on its own.** Everything leaves together with the beat swap.
- **Count-ups**:
  - 0 → 140 in **0.9 s power3.out** (107 at +0.3 s). The bar fills with the count.
  - 1800+: 1157 → 1783 → 1800 over ≈ 1.2 s.
  - Percentages are slow: 86 % takes **≈ 4 s, power2.out** (4 / 21 / 42 / 58 / 70 / 77 / 82 / 85 / 86 at 0.5 s steps). 93,2 % takes ≈ 3.5 s with one decimal.
  - Non-tabular digits shift the "/ 140" while counting (a reference artefact; we reserve the final width).

## 5. UI components

**A. Channel header + rubric pill**: see §1. It is static and never animates.

**B. Chapter tabs**
- A segment fills from the left: scaleX 0 → 1 in **0.6 s power3.out**. The 10 fps samples are 16/60/100/126/140/148/152 px (`tabs.txt`).
- The label switches to black at the same time.
- Steps land on the first new beat of a chapter: 0.5, 10.45, 21.75, 28.05, 64.05, 74.95.

**C. News cover card** (0–5 s, 98.7–105.6 s)
- 952 × 1020, r ≈ 36, photo with a dark bottom gradient.
- Text block is inset 52 px from the left and ≈ 58 px from the bottom.
- Enter: blur ≈ 18 → 0 + fade, slight scale.

**D. Post image + stats column** (5–10 s)
- Image 576 × 765, r 32.
- Chips are 360 × 172, gap 22. Each has a 64 px icon disc (first one gold, the rest white), a value of 46 / 700 and a label of 24 grey.
- Each chip blurs in on its spoken word, and its value counts up.

**E. Numbered chips**: 465 × 190, gap 22. Gold numbered disc (50 px), 2-line semibold label.

**F. Data card**
- 952 × ≈ 510: label (y 890), big gold number (cap top 951), bar (24 px, r 12, track `#E7E7E9`), bold note.

**G. 2×2 tiles**: 460 × 355, gap 22. Line icon top-left, gold ↑ disc top-right, title 40 / 700, gold sub.

**H. Comment screenshot card**: a real screenshot scrolled inside a card (proof). It is not reproduced as fake UI.

**I. Chart card**
- Faint horizontal guides. A gold curve draws L→R; a grey dotted comparison line follows. Legend chips sit below.
- Draw speed follows the sentence: 1 s for a quick fact, ≈ 5 s for a slow trend.

**J. Video card + compare row**
- B-roll card ≈ 952 × 530.
- Compare row card: "2025 … / 1800+" → gold arrow → "2026 … / **2500+**" in gold.

**K. Question card + dot row ("?/12" → 8/12)**
- Gold "?" swaps to the count.
- 12 discs (65 px, pitch 72) turn gold one by one, then the legend appears.
- The reference discs use a generic person glyph. **We draw plain discs with a check (no figures).**

**L. Percent rows**: 952 × 216 cards, gap 22. 2-line title left, gold % right, bar, grey note.

**M. Icon chips** (Себебі): gold ↑ disc + grey line + bold line, ≈ 440 × 110.

**N. Toggle card**: iOS-style switches with a gold track. Flip = knob slide + track colour ≈ 0.3 s; the row title greys out when off.

**O. Question beat**: big gold "?" + one line, centred, nothing else.

**P. Poll card**: white option rows with radio rings, plus a comment input row with the channel avatar.

## 6. Transitions and camera

- **The only transition is a beat swap on the same page** (`tr_10.0.jpg`, `tr_4.85.jpg`, `tr_62.1.jpg`):
  1. The whole outgoing beat (kicker, headline and cards) blurs **0 → ≈ 20 px** and fades out over **6–7 frames (≈ 0.2 s)**.
  2. The page then stays **empty for ≈ 5 frames (0.17 s)**. `activity.txt` shows blanks at 5.03, 10.43, 15.60, 21.73, 26.03, 28.00, 39.83, 50.30, 62.63, 64.03, 74.97, 89.93, 98.63, 105.67, each 0.07–0.3 s long.
  3. The new beat blurs in element by element.
- Header, tabs and captions are untouched by the swap.
- Swaps sit **in the sentence pauses**: ASR pauses 4.62–4.92, 10.08–10.48, 21.38–21.80, 27.84–28.14, 39.36–39.86, 50.36–50.76, 62.26–62.68, 74.54–74.96, 89.96–90.34, 105.64–106.02.
- Inside a beat, components are only added (build-down). An old component is sometimes replaced by a blur-swap, e.g. "?" → number.
- **No camera moves.** No zoom or pan on the page. Only the photo inside the cover card eases its scale slightly, and B-roll moves inside its card.

## 7. Captions and voice sync

- **Literal, uppercase transcription** of the VO, in **phrases of 2–7 words on 1–2 centred lines** (line 1 is usually the longer one). There is never a third line.
- A phrase is **pre-laid-out at its final centred position**. Example at 3.6 s: "БҰЛ ШЕШІМНІҢ" sits at x 362–719 and the second line starts at x 326 before it is complete.
- Each word appears with a **soft left→right wipe/blur across its letters**, spread over the spoken word.
  - Caption ink grows smoothly during speech (`activity.txt` col 3). Letters ahead of the wipe are blurred and light.
  - The wipe leads the audio by ≈ 0–0.2 s.
- **Phrase swap is a hard cut**: the old phrase disappears in 1 frame right before the next phrase's first word. 57 clears in 112 s, i.e. a new phrase every ≈ 1.9 s.
- No exit animation, no highlight colour, no karaoke colour change. Numbers are written as digits ("140 ЖЕТТІ!", "93.2 ПАЙЫЗҒА").
- **Components arrive on the noun that names them**: "лайк" → stats chip, "140" → data card, "сегізі" → dots fill, "86 пайызы" → % row.

## 8. Audio

- **Voice**: dry, close, dominant. Integrated **−14.2 LUFS**, LRA 3.2 LU.
  - Sample peaks clip slightly above 0 dBFS after the AAC decode. Master to −1 dBTP instead.
  - 0.5 s RMS percentiles: 5 / 50 / 95 % = −22.3 / −14.7 / −11.5 dBFS.
- **Music**: a **soft low-frequency bed under the whole piece, including the hook**.
  - In every pause the level is ≈ −30 dBFS, with almost all energy below 120 Hz (bands 20–120 Hz ≈ 30 dB above 2–6 kHz).
  - Above 5 kHz it is silent: the pause median is −68 dBFS. So there are no hats, no melody and no beat transients.
  - It sits ≈ 15 dB under the voice and fades out in the last 1.7 s (−36.6 dBFS).
- **SFX**: **none**. The HF envelope in pauses never exceeds −33 dBFS. Swaps, count-ups, toggles and dot fills are silent.
- There are no voice gaps longer than 0.5 s.

## 9. Secret sauce

1. **It reads as a news app page, not a video.** A persistent channel header with a rubric pill plus story-style chapter tabs make 112 s of data feel like one scrolling article. Only the content beats change.
2. **One accent colour.** Black ink + a gold gradient on exactly the key fact of each headline ("140 балл", "MNU-да", "сапа") and on every number. Nothing else is coloured.
3. **Every claim gets a data widget.** Count-ups, bars, % rows, dot rows, charts, toggles. Numbers always animate and bars always fill with them.
4. **Proof first.** The official post image, the like counts, the real comments and real campus B-roll sit inside the same flat cards.
5. **Flat, borderless cards** (`#F4F4F6`, r 32, no shadow) on `#FCFCFC`. The calm surface lets the gold do the work.
6. **Captions as a second text layer.** Uppercase grey literal words under the cards carry the voice word by word, while the headline stays a short editorial summary.
7. **Swaps in breath pauses**, with a 5-frame empty page. This gives a "page turn" rhythm every ≈ 5–10 s.

**What a naive recreation gets wrong**
- It adds shadows, borders or gradients to cards, or a grid background.
- It colours many words, or uses gold for labels.
- It reveals headlines word by word, or makes captions bounce or highlight.
- It centres the headline (it is left-aligned).
- It lets numbers appear static instead of counting.
- It adds whooshes on the swaps.
- It uses a font without Kazakh glyphs, which falls back mid-word on ә ғ қ ң ө ұ ү і.
- It lets the caption re-centre while words arrive.

## 10. Reproducible spec (CSS + GSAP)

```css
.page{background:#FCFCFC;font-family:"Inter",system-ui;color:#101011}
.head{position:absolute;left:64px;right:64px;top:96px;height:88px}
.logo{width:88px;height:88px;border-radius:22px}
.name{position:absolute;left:110px;top:4px;font:700 37px/44px Inter;letter-spacing:-.02em}
.handle{position:absolute;left:110px;top:50px;font:400 24px/30px Inter;color:#8A8A8E}
.pill{position:absolute;right:0;top:16px;height:56px;padding:0 26px 0 22px;border-radius:28px;background:#F4F4F6;font:600 23px Inter}
.pill i{width:14px;height:14px;border-radius:50%;background:#FDC604}
.tabs{position:absolute;left:64px;right:64px;top:212px;display:flex;gap:8px}
.tab .bar{height:6px;border-radius:3px;background:#E7E7E9}
.tab .fill{background:linear-gradient(90deg,#E89E0C,#C9822E 55%,#A8672C);transform-origin:0 50%}
.tab .lbl{margin-top:9px;font:500 20px/24px Inter;color:#B4B4B9}
.kicker{font:600 30px/38px Inter;color:#A26A2A}                 /* block top y 338 */
.headline{margin-top:18px;font:700 80px/1.12 Inter;letter-spacing:-.035em}
.ac{background:linear-gradient(90deg,#E89E0C,#C9822E 55%,#A8672C);-webkit-background-clip:text;color:transparent}
.card{background:#F4F4F6;border-radius:32px;padding:40px}       /* no border, no shadow; gap 22 */
.big{font:700 240px/.9 Inter;letter-spacing:-.055em}            /* + "/ max" 0.31em #B4B4B9 */
.bar{height:24px;border-radius:12px;background:#E7E7E9}
.caption{position:absolute;left:64px;right:64px;top:1430px;text-align:center;
  font:800 48px/58px "Inter Tight";letter-spacing:-.045em;color:#5E5E5E;text-transform:uppercase}
```

```js
// element blur-in (kicker at t, headline t+.07, cards +.1 each)
tl.fromTo(el,{opacity:0,filter:"blur(14px)",y:22,scale:.98},{opacity:1,filter:"blur(0px)",y:0,scale:1,duration:.32,ease:"power2.out"},t);
// beat swap in a breath pause: blur-out 0.21 s, 0.17 s empty page, next beat at +0.38
tl.fromTo(beat,{opacity:1,filter:"blur(0px)"},{opacity:0,filter:"blur(20px)",duration:.21,ease:"power1.in",immediateRender:false},t);
// tab step
tl.fromTo(fill,{scaleX:0},{scaleX:1,duration:.6,ease:"power3.out",immediateRender:false},t);
// count-up + bar (data card) / slow % rows
tl.fromTo(o,{v:0},{v:140,duration:.9,ease:"power3.out",onUpdate:()=>n.textContent=fmt(o.v)},t);
tl.fromTo(barFill,{scaleX:0},{scaleX:1,duration:.9,ease:"power3.out"},t);
tl.fromTo(o2,{v:0},{v:86,duration:3.6,ease:"power2.out",onUpdate:…},t);
// caption word: letters of the pre-laid-out word wipe in L→R over the spoken word (≤ .45 s)
tl.fromTo(chars,{opacity:0,filter:"blur(6px)"},{opacity:1,filter:"blur(0px)",duration:.12,stagger:wordDur/chars.length},wordStart);
tl.set(phrase,{autoAlpha:0},nextPhraseStart-.02);  // hard swap, no exit
```
