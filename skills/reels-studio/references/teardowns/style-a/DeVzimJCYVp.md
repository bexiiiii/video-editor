# DeVzimJCYVp — "Как скачать ChatGPT/Claude на iPhone без AppStore" (zaytsevtech) — forensic style breakdown

Source: 1080x1920, 60 fps, 106.0 s, AAC 44.1 kHz (L = R, mono).
Same toolkit as the sibling video (DejCkBdNC6h/style.md): `metrics.txt` (60 fps luma/diff/sharpness), `f_*.png` stills, `hook30.jpg`, `end30.jpg`, `mont_a.jpg`, `rms_*.txt`, `transcript.json`.
**The design system is identical to DejCkBdNC6h.** This file restates what is shared and highlights what differs: sentence case, bottom-placed headlines, more BG colours, real UI screenshots.

---------------------------------------------------------------------
## 1. Format & structure

- 106 s, 286 words, 162 wpm, speech fills 88% of the runtime.
- Format: step-by-step tutorial, faceless, VO + motion graphics + tilted real screenshots.
- 26 scenes, 25 transitions, which gives a new beat every **4.2 s** (range 2.2–10 s).

| # | time (s) | BG | headline | visual |
|---|---|---|---|---|
| 1 | 0.00–5.40 | black → teal spotlight glow | `как скачать / приложения?` | 3D glossy blue iPhone flies up from the bottom; orbiting 3D logos (teal OpenAI knot, orange Claude asterisk, chrome "H" Happ) pop in staggered; caption "если их нет в App Store" |
| 2 | 5.40–8.70 | dark #0B0D0D | `отдельный аккаунт Apple` (below the object) | black glossy 3D Apple logo; labels iCloud / App Store |
| 3 | 8.70–14.20 | dark | `Турцию или США` | two 3D isometric diorama islands (Istanbul, Statue of Liberty / Capitol), dashed branch from the top; labels Турция / США |
| 4 | 14.20–20.00 | maroon + light ray + dot grid | small top caption "давай покажу, как создать аккаунт"; bottom headline `широкого каталога` | 5 dark app tiles in a 3+2 grid (ChatGPT, Happ, Claude, Gemini, Muse AI) with labels |
| 5 | 20.00–22.80 | dark | `можно через / браузер` | tilted browser screenshot slides in from the left with motion blur; dark pill button with Apple logo "Создать аккаунт" |
| 6 | 22.80–27.30 | white | `Открой / account.apple.com` | page screenshot; caption "Создание Аккаунта Apple" |
| 7 | 27.30–30.40 | white | `Укажи имя` | form screenshot (zoomed); caption "дату рождения и выбранную страну" |
| 8 | 30.40–40.40 | white | `Добавь новую почту` (moves **below** the form) | form; 2-line grey caption "смс с подтверждением может не прийти сразу…" + "если смс не пришла" (longest hold, 10 s) |
| 9 | 40.40–44.50 | dark | `Подтверди почту / и номер кодами` (bottom) | 3D envelope with red badge + white 3D phone |
| 10 | 44.50–47.00 | deep-space purple | `Открой настройки` (bottom) | 3D blue iPhone; caption "нажми на своё имя" |
| 11 | 47.00–51.40 | dark | `Контент и покупки` (top) | dark iOS Settings screenshot, tilted, red outline highlight on rows; caption "Нажми «Выйти» именно внутри раздела" |
| 12 | 51.40–54.00 | white | `Основной аккаунт` (bottom) | black glossy Apple logo with dotted branches to labels "iCloud подключён" / "покупки: выход" |
| 13 | 54.00–57.60 | dark | `Снова открой` (bottom) | iOS screenshot with alert sheet + red outline |
| 14 | 57.60–59.80 | white | `Введи почту` | light "Аккаунт Apple" login card (email/password rows, black "Войти" button); caption |
| 15 | 59.80–64.00 | dark | `Теперь открой App Store` (bottom, 1 line) | dark App Store card: search field, ChatGPT row, blue pill "Загрузить"; caption "найди нужное приложение" |
| 16 | 64.00–68.40 | white | `При первом скачивании` (top, 1 line) | card "Условия и положения" + black pill "Принимаю"; caption |
| 17 | 68.40–70.80 | dark | `Если доступен вариант` | dark card "Способ оплаты / Карта · Нет" (blue "Нет"); caption "выбери «Нет»" |
| 18 | 70.80–73.60 | white | `Адрес указывай / достоверный` | "Платёжный адрес" card (Улица/Город/Индекс); caption |
| 19 | 73.60–79.50 | dark | `Как оплачивать покупки` (bottom) | 3D glossy blue credit card, tilted; caption above the headline |
| 20 | 79.50–82.40 | black → emerald glow | `подарочной картой` (top) | 3D blue gift box with an Apple logo; caption "пополнить баланс App Store" |
| 21 | 82.40–85.60 | dark | `Пополнить счёт / из России` | small gift icon + pill "Карты Apple"; caption |
| 22 | 85.60–88.50 | dark | `Страна / подарочной карты` (bottom) | the two dioramas connected; caption "должна совпадать со страной аккаунта" |
| 23 | 88.50–91.00 | white | `Американский код` | dioramas placed diagonally (US top-left → TR bottom-right), dotted line; caption "не подойдёт турецкому аккаунту" |
| 24 | 91.00–97.60 | dark | `Перед оплатой / проверьте` | 3 glass list cards stacked (Страна / регион аккаунта; Стоимость / нужного приложения; Номинал / подарочной карты), each with a 3D mini icon, staggered |
| 25 | 97.60–103.50 | dark | `Код придёт` (top) | iOS "Активация по коду" screenshot; caption "Погасить подарочную карту или код" |
| 26 | 103.50–106.00 | white | `Сохрани инструкцию` | 3D blue bookmark; typed recap "создать аккаунт → войти в покупки → загрузить / проверить регион карты" |

**Hook (0–3 s), measured at 30 fps**
- 0.00–0.13: BG only (black with a teal glow).
- 0.10: "как" blurs in.
- 0.13: the phone enters from below the frame and rises to centre in ≈ 0.25 s, ease-out, with motion blur. It continues to grow slightly until 0.45.
- 0.27: the ChatGPT knot pops at the left.
- 0.33: "скачать".
- 0.40: the Claude asterisk pops at the right.
- 0.47: "приложения?".
- 0.50: the "H" pops at the bottom-left.
- The orbiting logos are staggered ≈ 0.12 s apart, each scaling 0 → 1 with a slight overshoot.
- ≈1.0: the caption "если их нет в App Store" types in.
- Static hold until the 5.3 s transition.

There is one long hook scene (5.4 s) holding the question while the VO lists the app names.

**CTA (103.5–106)**
- The previous scene pushes **up** with vertical motion blur while the BG cross-fades to white (≈ 0.25 s).
- The bookmark rises from below, blurred.
- "Сохрани" then "инструкцию" blur-rise in.
- The recap types at ~24 cps.
- It ends on the voice-over with no end card.

---------------------------------------------------------------------
## 2. Backgrounds

There are 7 BG types and the same dark/white alternation logic. The dark base `#0B0D0D` dominates (about 55% of scenes), white `#FBFDFD` covers about 30%.

| BG | values |
|---|---|
| Dark base | `#0B0D0D`, faint dot grid |
| White base | `#FBFDFD`; dot grid 3 px dots on a **24 px** pitch, colour `#E5E7E7`–`#F2F4F4` (luma 229–246 vs 252), visible mainly around objects, vignetted |
| **Teal spotlight** (hook) | top half pure `#000000`; from y≈1100 a teal glow rises: `#00171F` (y=1360) → `#022736` (1510) → `#003950` (1660) → `#044866` (1810), corners `#046D98`. The shape is a wide elliptical glow from the bottom, with a soft lighter "arch" behind the phone like a stage spotlight cone |
| **Maroon light-ray** | base `#380B19`, mid `#561326`, top-left highlight `#AF3956`; diagonal god-ray from the top-left (~35°); dot grid on a 20 px pitch (dots ≈ `#4A1525`) |
| **Deep-space purple** | as in DejCkBdNC6h: black with a violet `#270245` top-left glow and a magenta `#33003A` bottom-right glow, centre `#0B061C`, star dots |
| **Emerald glow** | top half `#000000`; bottom glow `#00190F` (y≈960) → `#00291B` → `#003E28` → `#045236` (y=1810), corners `#077A52`. Same construction as teal, different hue |
| Lavender radial | not used here |

Each BG change rides on the blur-push dissolve (§6). The teal and emerald glow BGs are used only for "hero object" scenes (hook, gift card).

---------------------------------------------------------------------
## 3. Typography

Same family (Google-Sans-like grotesk; use **Google Sans Flex** / Onest), same colours, same blur reveals.

**Differences from DejCkBdNC6h:**
- **Case**: the hook and some emotional headlines are lowercase ("как скачать приложения?", "подарочной картой", "широкого каталога"). **Instruction steps use Sentence case**, imperative ("Добавь новую почту", "Открой настройки", "Теперь открой App Store", "Сохрани инструкцию").
- **Position varies with the visual**:
  - top block at y ≈ 18–25% when the visual is a tall screenshot ("Контент и покупки", "Код придёт", "При первом скачивании")
  - **bottom block at y ≈ 64–75%** when the visual is a 3D object or form above ("Добавь новую почту" baseline y≈1260 = 66%, "Теперь открой App Store" y≈1369–1439 = 73%, "Сохрани инструкцию" ≈ 80%)
  - with a bottom headline, the grey caption sits **between the visual and the headline** or just under it
- Sizes:

| role | px @1080 | notes |
|---|---|---|
| Hook headline (2 lines) | ≈ 78 px, x-height 40 px, line pitch 84 px | white, 600–700, centred, block y 343–482 (18–25%) |
| Step headline, single line | ≈ 72–76 px (cap height ~54 px; "Теперь открой App Store" spans **858 px = 79% width**, the max seen) | black on white / white on dark, SemiBold |
| Bottom headline on the maroon scene | ≈ 76 px ("широкого каталога" 658 px wide, y 1397–1452) | white |
| Small top caption | ≈ 42 px Regular, `#E8E0E4` on maroon (y≈410–447 = 22%) | lowercase |
| Grey caption | ≈ 40–44 px, line pitch ≈ 45–48 px, `#696C6C` on white, `#767878`-ish on dark, `#D1E2F3` (light blue-grey) on teal | lowercase |
| App labels | ≈ 44 px Regular `#E0D8DC` | Title case |
| Glass list card | title 44 px SemiBold white + sub 30 px grey `#9A9C9C` | left-aligned |

- Max chars per line about 18–24 for single-line steps (wider than in DejCkBdNC6h). 2–5 words on screen in the headline.

---------------------------------------------------------------------
## 4. Text animation

Identical grammar:
- **Headline: per-word blur-rise** (opacity 0 → 1, blur ≈ 12 → 0 px, y +25 → 0 px, ≈ 0.30 s, power3.out). Hook measured: "как" visible 0.10–0.27, "скачать" 0.33–0.40, "приложения?" 0.47–0.63.
- **Captions / labels / recap: per-character typewriter** ≈ 24 chars/s with a blurred leading glyph ("Сохр…", "если их нет в App…" partial states seen in the sheets). The text is anchored at its final centred position.
- No exit animation of its own: text leaves with the scene's blur-push.
- In the CTA the headline rises noticeably (≈ 40 px over 0.2 s) because it rides the incoming push.

---------------------------------------------------------------------
## 5. Graphics / objects

- **3D glossy "inflated" objects** (same AI-render family):
  - blue iPhone (the screen shows blue wave wallpaper), ~330×580 px in the hook, centred
  - logo set: teal OpenAI knot (`#2ED3C0`-ish), orange Claude asterisk, chrome italic "H"
  - black glossy Apple logo
  - kraft envelope with a red dot + white phone
  - blue credit card (tilted ~15°)
  - blue gift box with a ribbon and white Apple logo
  - isometric city diorama islands, grass base (Turkey: Galata tower + flag + balloon; USA: Capitol + Statue of Liberty + flag)
  - blue bookmark
- **App tile grid** (scene 4): dark squircles `#20272C`, 158×158 px, radius ≈ 38 px, 2 px light rim, small 3D logo (~70 px) inside, soft shadow. Labels 44 px under each. Layout 3 + 2, columns at x ≈ 250 / 540 / 832, rows at y ≈ 745 / 1075.
- **Real screenshots** (Apple ID web form, iOS Settings dark, App Store activation screen):
  - placed as flat images with a **slight 3D perspective tilt** (the top edge is a few px shorter, ≈ rotateX 4–6°), a soft shadow, and no device frame
  - important rows get **red rounded outline boxes** (2–3 px `#E5484D`)
  - white screenshots sit on white BGs, dark ones on dark BGs; the page itself disappears into the BG
- **Generated UI cards**:
  - light cards: white `#FFFFFF` on `#FBFDFD`, radius ~36 px, very soft shadow, black "Войти"/"Принимаю" pills, round grey arrow buttons
  - dark cards: `#121414`/`#171A1A`, radius ~36–40, 1.5 px light rim
  - blue CTA pill `#2F7CF6` with white text ("Загрузить")
- **Glass list cards** (scene 24): 3 stacked 520×150 px rounded rects (r ≈ 26), dark translucent fill, **2 px bright white/60% rim with a highlight**, 3D mini icon at the left, title + sub text; slight individual tilts.
- **Dashed / dotted connectors**: dotted curves (4 px dots) between the Apple logo and its labels; dashed lines between the dioramas.
- **Entrances**:
  - rise from below with motion blur (phone, bookmark)
  - pop-scale with stagger (logos, tiles)
  - slide in from the side with heavy directional blur (browser screenshot, scene 5)
  - list cards cascade top → bottom (~0.12 s stagger)
- **Idle**: static holds.

---------------------------------------------------------------------
## 6. Transitions

Measured sharpness dips: all are **blur-push dissolves** of **15–27 frames (0.25–0.45 s, mode 17 frames = 0.28 s)**.

Timestamps (s), with frame counts in parentheses:
- 5.32 (23)
- 8.60 (21)
- 14.12 (16)
- 19.97 (18)
- 22.62 (25)
- 27.23 (15)
- 30.38 (in-place swap)
- 40.32 (17)
- 44.42 (21)
- 46.95 (15)
- 51.33 (17)
- 53.92 (17)
- 57.43 (20)
- 59.65 (26)
- 63.75 (17)
- 68.20 (17)
- 70.60 (17)
- 73.35 (26)
- 79.43 (27)
- 82.35 (15)
- 85.55 (15)
- 88.45 (17)
- 90.93 (17)
- 97.53 (15)
- 103.45 (17)

Directions seen:
- vertical push up (end)
- vertical drift down
- horizontal push (the browser screenshot enters from the left)
- in-place blur swap (white → white at 27.2 and 30.4, where only the headline and zoom change)

Dark ↔ white flips go through a visible mid-grey frame. There are no hard cuts, wipes or flashes.

---------------------------------------------------------------------
## 7. Sync

- Transitions are centred on the next sentence onset, inside the breath gap: e.g. 57.43–57.75 for "Введи" at 57.52; 103.45–103.72 for "Сохрани" at 103.58; 20.0 for "Создать" at 20.00.
- Headline word reveal starts about +0.1–0.15 s after the spoken word and is sharp at about +0.3 s.
- Headlines are **condensed imperatives or keywords**:
  - VO "Для этого понадобится отдельный аккаунт Apple с другим регионом" → `отдельный аккаунт Apple`
  - VO "Рекомендую выбрать Турцию или Америку" → `Турцию или США`
- Captions carry a secondary fact, sometimes from the *next* sentence ("смс… попробуйте через пару часов").

---------------------------------------------------------------------
## 8. Audio

- **−14.2 LUFS integrated, LRA 1.6 LU**, mono.
- Gap level median −46 dB (lowest −79 dB), so **no music, no SFX**. High-frequency (>6 kHz) peaks only appear inside speech.
- Same dry, compressed, gated narrator voice.
- One minor tell of scripting/TTS: the VO mixes "ты" and "вы" forms ("Попробуйте", "проверьте").

---------------------------------------------------------------------
## 9. Secret sauce (adds to the list in DejCkBdNC6h)

1. Real screenshots are **embedded on matching-luminance BGs** with a small perspective tilt and red focus outlines. They read as designed objects, not pasted images.
2. **Headline position flips (top ↔ bottom)** depending on the visual's height, which keeps the central "hero" area always clear.
3. The **imperative Sentence-case step headline** ("Открой…", "Нажми…", "Введи…") works as a checklist rhythm for tutorials. Hooks stay lowercase questions.
4. Coloured "glow-from-bottom" BGs (teal, emerald) are reserved for hero-object beats; maroon and purple provide variety. Dark and white carry the procedure steps.
5. The same 3D assets recur (dioramas, phone, Apple logo) across scenes, which gives visual callbacks.
6. Steps are paced at about 4 s each, and a long hold (10 s) is allowed when the VO explains a caveat.

Naive pitfalls:
- framing screenshots in a device mock-up (they don't)
- big drop shadows
- putting every headline at the top
- capitalising the hook
- adding music

---------------------------------------------------------------------
## 10. Reproducible spec

Use the CSS/GSAP block in `../DejCkBdNC6h/style.md` §10, plus:

```css
.bg-teal{background:radial-gradient(120% 55% at 50% 100%,#046D98 0%,#044866 25%,#00171F 55%,#000 75%);}
.bg-emerald{background:radial-gradient(120% 55% at 50% 100%,#077A52 0%,#045236 25%,#00190F 55%,#000 75%);}
.bg-maroon{background:linear-gradient(145deg,#AF3956 0%,#561326 30%,#380B19 70%);}            /* + diagonal ray + 20px dot grid */
.headline.step{font-size:74px;text-transform:none;max-width:860px;}                          /* Sentence case */
.headline.bottom{top:auto;bottom:25%;}
.shot{transform:perspective(1600px) rotateX(5deg);box-shadow:0 30px 60px rgba(0,0,0,.18);border-radius:18px;}
.focus{outline:3px solid #E5484D;border-radius:12px;}
.glass-row{width:520px;height:150px;border-radius:26px;background:rgba(255,255,255,.04);
  box-shadow:inset 0 0 0 2px rgba(255,255,255,.55),0 20px 40px rgba(0,0,0,.4);}
.tile{width:158px;height:158px;border-radius:38px;background:#20272C;box-shadow:inset 0 0 0 2px rgba(255,255,255,.18),0 16px 30px rgba(0,0,0,.35);}
```

```js
// hero phone rise (hook)
tl.fromTo(phone,{y:900,scale:0.8,filter:"blur(12px)"},{y:0,scale:1,filter:"blur(0px)",duration:0.35,ease:"expo.out"},0.13);
// orbiting logos pop
tl.fromTo([knot,asterisk,H],{scale:0,opacity:0},{scale:1,opacity:1,duration:0.3,ease:"back.out(1.6)",stagger:0.12},0.27);
// glass list cascade
tl.fromTo(rows,{y:40,opacity:0,filter:"blur(10px)"},{y:0,opacity:1,filter:"blur(0px)",duration:0.35,ease:"power3.out",stagger:0.12},t);
// screenshot slide-in from left
tl.fromTo(shot,{x:-500,filter:"blur(20px)",opacity:0},{x:0,filter:"blur(0px)",opacity:1,duration:0.4,ease:"expo.out"},t);
```
