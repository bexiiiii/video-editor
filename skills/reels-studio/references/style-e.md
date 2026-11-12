# Style E — "Data News" (editorial news page with live data)

> Teardown with frame-level numbers: `teardowns/style-e/DfmpUlfuHod.md`. Pack: `assets/style-e/` (global `RSE`, API in `components.md` → "Style E"). Audio: `audio-policy.md`. Layout, variety and anti-AI rules: `layouts.md` (binding).

## When to use
Use it for news, statistics and "what changed and why" explainers, such as education/ҰБТ news, HR/market data or policy changes. It works when the script is built on **numbers and sources**. Faceless; real material (an official post image, screenshots, B-roll) lives inside cards. Languages: kk / ru / uz; Inter covers the Kazakh letters ә ғ қ ң ө ұ ү һ і.

## 1. Structure
- **One continuous white page.** It has no cuts and no theme changes.
- **Persistent chrome**: the channel header (logo, name, handle and rubric pill) and the chapter tabs below it.
- **Content beats** of 2–12 s replace each other with a blur swap that sits in a sentence pause.
- **Caption track**: literal uppercase captions run underneath, independent of the beats.
- **Chapters** (4–6 tabs, short nouns such as Жаңалық · Сандар · Себебі · Пікір · Болжам) follow the argument: news → numbers → reaction → reasons → forecast → question. A tab fills on the first beat of its chapter.
- **Hook**: the news cover card, with the key number in gold in the title, plus the first spoken sentence. There is no visual shock.
- **Ending**: a poll / comment question (`poll`) or a summary cover, held to the end. There is no follow button.
- **Rhythm**: a new beat every ≈ 4–6 s in a 30 s reel (the reference runs at 5–12 s, which is too slow for 30 s). New elements arrive every 0.4–1 s on the nouns that name them.

## 2. Tokens (tokens.css, scoped `.rse`)
- **Page**: `#FCFCFC`, flat, with no grid or grain.
- **Cards**: `#F4F4F6`, r 32 (cover r 36), padding 40, **no border, no shadow**, gap 22. Inner white rows (`#FFFFFF`) appear only in polls.
- **Ink and greys**:
  - ink `#101011`, card ink `#1C1C1E`
  - grey `#8A8A8E`, light grey `#B4B4B9`
  - track `#E7E7E9`
  - caption `#5E5E5E`
- **Accents**:
  - kicker `#A26A2A`
  - rubric dot `#FDC604`
  - **gold gradient** `#E89E0C → #C9822E → #A8672C`: horizontal on text and bars, vertical on big numbers and "?"
- **Column**: x 90–990 (900 px).
  - The reference uses 64–1016; `layouts.md` requires ≥ 90 px margins. Use `.rse-refmargin` for A/B checks only.

## 3. Type scale (Inter / Inter Tight)

| Role | Spec |
|---|---|
| Channel name / handle | 37/700 · 24/400 grey |
| Rubric pill | 23/600 · 56 px pill |
| Tab label | 20/500 (current 600 ink) |
| Kicker (source) | **30/600 `#A26A2A`** ("@source • Ресми пост", "2026 · Деректер") |
| Headline | **80/700 −0.035em**, lh 1.12, ≤ 2 lines, left-aligned, shrinks to fit 900 px; accent phrase in gold |
| Cover title | 84/700 white; cover kicker 30/700 +0.16em uppercase |
| Big number | **240/700** −0.055em gold + "/ max" at 0.31 em light grey (fits the card automatically) |
| Percent value | 132/700 gold |
| Question "?" | 400/800 gold; question line 72/700 |
| Card label / note | 26/500 grey · 26/600 ink; stat value 46/700 |
| **Caption** | **Inter Tight 800, 48 px, line pitch 58, −0.045em, uppercase `#5E5E5E`**, centred, ≤ 2 lines, top y 1430 |

## 4. Layout geometry (measured)
- **Header**: y 96–184. Logo 88 (r 22), name cap 107–134, pill y 112–168.
- **Tabs**: bar y 212–217 (6 px, gap 8), label cap 231.
- **Content block**:
  - The kicker line box starts at **y 338**; cards end at **≤ 1380** (reference 1350).
  - Rhythm: kicker → headline 18; headline → first visual **84** (layouts.md 70–110); cards gap 22.
  - The block ∪ caption tier (1430–1542) centres at y ≈ 936–940, within the layouts.md band of 860–940.
- **Caption tier**: y 1440–1542 (cap tops 1440 / 1498).

## 5. Layouts — `RSE.layout.<id>` mapped to the `layouts.md` catalogue

| id | Composition | Reference beat |
|---|---|---|
| `hero` | news cover card (≈ 900×1012, title inside the photo) | 0–5 s, 98.7–105.6 s |
| `media` | headline + photo/video card (60 %) + stats column, or a full-width photo + `below` | 5–10 s (official post), 28–40 s (B-roll) |
| `number` | headline + numbered chips + data card (count-up "x / max" + bar) | 10.6–15.6 s |
| `list` | headline + percent rows (or tiles / toggles through `visual`) | 50.5–62.6 s, 15.8–21.7 s, 90–98.6 s |
| `compare` | headline + (chart / photo) + compare row "A → B" | 28–40 s, 26–28 s |
| `stack` | headline + 1–3 components (e.g. question card + dot row) | 40–50 s |
| `statement` | big gold "?" + one question line (≤ 1 per 6 beats) | 62.8–64 s |
| `visual-top` | components first, kicker + headline under them (variety) | — (variety rule) |

- `head` / `head-side` do not exist in E. The style is faceless; people appear only in real B-roll inside `photo` cards.
- Variety: never use the same layout twice in a row. Alternate cover/photo beats (visual mass) with data beats (number mass).

## 6. Components (builders, see components.md)
`page` · `header` · `tabs` · `title` (kicker + headline + accent) · `cover` · `photo` · `stats` · `chips` · `dataCard` · `percentRows` · `questionCard` · `dotRow` · `question` · `post` · `compare` · `chart` · `toggles` · `poll` · `tiles` · `caption`.

- One accent per headline: gold marks exactly the key fact ("140 балл", "MNU-да", "сапа").
- Every number counts up. A bar fills together with its number.
- Proof material goes into cards:
  - an official post image (`photo` + `stats`)
  - comment / post screenshots (`photo src`)
  - B-roll (`photo node` = static framework `<video>`)
  - no material → a labelled neutral slot (never a drawn person)

## 7. Motion
- **Element entrance**: blur 14 → 0, opacity, y +22, scale .98 → 1, **0.32 s power2.out**. Order: kicker → headline (+0.08) → cards (+0.12 each), or each card on its noun.
- **Headlines are revealed as blocks.** Word sync lives in the captions.
- **Count-ups**: 0.9 s power3.out (data card, stats); compare 1.0–1.2 s; percent rows **3–4 s power2.out** (slow, with one decimal comma).
- **Charts**: draw over 1 s for a fact, 3–5 s for a trend.
- **Toggles**: 0.3 s power2.inOut.
- **Dot fill**: 0.09 s stagger.
- **Tab step**: 0.6 s power3.out.
- **Beat swap** (`RSE.tx.blur`): the outgoing beat blurs 0 → 20 px and fades over **0.21 s** (power1.in), followed by **0.17 s of empty page**; the next beat starts at swap + 0.38. Place it in the ASR pause before the next sentence. Header, tabs and captions do not move.
- **Inside a beat**: build down only. Use `RSE.tx.swap` to replace one component in place ("?" → number).
- **Camera**: none. Only the photo inside a cover/photo card eases its scale from 1.06 to 1.

## 8. Captions
- Literal words from `transcript.json`, uppercase, phrases of 2–7 words, ≤ 2 balanced centred lines.
  - Use `/` to force the break; use NBSP to keep "1 240" together.
- **Pre-laid-out**: lines never re-centre.
- Each word wipes in L→R letter by letter (opacity + blur 6 → 0), spread over the spoken word (≤ 0.45 s).
- The phrase disappears in one frame when the next phrase starts. No highlight colour, no bounce.
- Captions continue across beat swaps (they are not part of the beat).

## 9. Audio
- Dry VO at −14 LUFS.
- A **soft low bed (< 120 Hz pad / sub) under the whole reel, including the hook**, ≈ 15 dB under the voice, fading out over the last 1.5 s.
- **No SFX** (no whoosh on swaps, no ticks on counters).
- See `audio-policy.md`.

## 10. Pitfalls
- **Never put the reference channel's identity on screen.** `RSE.header` needs `name` from the brief; without a logo it uses a monogram.
- Cards with shadows or borders, a grid background, or theme flips (that is Style B, not E).
- Gold on labels or on more than one phrase per headline; centred headlines.
- Static numbers, or a bar that fills without its number.
- Word-by-word headlines, or bouncing / colour-karaoke captions.
- A font without Kazakh glyphs (fallback mid-word). Inter / Inter Tight are required.
- Swaps that are not in pauses, or whoosh SFX on them.
- An empty card before its content (the reference shows an empty poll card for 0.4 s; we don't).
- Person glyphs in the dot row, or drawn people in slots.
- Demo deviation: the photos are labelled slots, so real runs need the materials (official post image, B-roll, screenshots → `materials.md`).
