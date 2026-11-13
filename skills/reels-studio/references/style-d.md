# Style D — "Talking Head × 3D Keyword" (Style A over the client's footage)

> Style D is **Style A, unchanged, applied over the client's talking-head footage.** Every visual rule, number and
> motion comes from `style-a.md` + `teardowns/style-a/` and is produced by the original A pack (`assets/style-a`, `RSA`).
> `assets/style-d/` (global `RSD`) only adds the footage base layer, punch-ins, face-safe placement, scrims, the
> head ↔ insert layouts and the CTA wrapper. API: `components.md` → "Style D". Audio: `audio-policy.md` (= A).
> The earlier "Umar editorial" talking-head look is NOT Style D; its techniques live in the optional pack
> `assets/techniques/head-umar.{css,js}` (`RSX`, see components.md) and are not used by D by default.

**Needs real footage** (`brief.footage`, `edit/head.mp4`). A human on screen is only real footage — never drawn.

## 1. Structure
Head segments (the speaker talks, A graphics around/below the face) alternate with **full-screen A inserts of 2–4 s**
(A backgrounds + hero object + headline, exactly like Style A scenes). Typical 30 s: head → insert-hero → head-side →
insert-number → head → insert-media → head-side → statement → cta. Rhythm as A: a new beat every 3.4–4.2 s, a new
element every 0.8–1 s. Hook = head with keyword; ending = A bookmark "сохрани" held to the end.

## 2. Head segments
- **Base:** full-frame footage, no frame/window, **no lens-edge blur or other gimmicks**. Punch-ins are hard scale sets on
  cuts, 1.0 ↔ 1.12, about the eye line (`footage.punches`).
- **Face-safe zones** (face assumed in the upper third, eyes ≈ 38 % = y 730):
  - `zone:"lower"` (default) — A headline centred at y 1340 (A bottom tier; block y 1250–1500), A grey caption at y ≈ 1528;
  - `zone:"upper"` — only when the face sits low in the take: headline centred at y 390 (block y 230–520), caption ≈ 548.
  Text never covers the face or eyes.
- **Readability:** a soft dark gradient scrim (A dark `#0B0D0D`, 0.78 → 0 over the lower 52 % or upper 38 %) + A's halo
  exception for text over photos. **No boxes.** Keywords stay A (headline = summary).
- **Literal subtitles (client feedback: "too few, late"):** with `brief.captions` "auto" (default) the assembler adds a
  continuous caption track over every head segment (contracts.md → "Caption track"): A typography (Google Sans 600,
  lowercase, white, soft shadow), 1–4 words, centre y 1470, each word visible at its onset − 0.03 s. RSD then lifts the
  lower-zone keyword headline to y 1255 and drops the grey A caption (no duplicate text); `below` components move up
  50 px. Scenes never build subtitles themselves.
- **Components beside / below the face** (`head-side`): one A component per segment — 3D hero object (≈ 35–45 % of
  frame width, default 400 px, at the torso side x 820/260, y ≈ 1000, or below the chin y ≈ 1045), number roll, glass
  pill, chip, keyword pill, selection, glass card. Entries are A's (pop, side-slide with motion blur, rise, drop).

## 3. Inserts (pure Style A)
`insert-hero` (headline y 545 + 3D hero 500 px at y 1000 + caption 1460), `insert-number` (A slot-machine roll 106 px +
pill/selection/progress bar), `insert-media` (glass/frost cards, dashed connector, blue chip, or a tilted screenshot
without device frame), `statement` (headline centred + inline keyword pill, max 1 per 6 scenes), `cta` (bookmark).
Backgrounds: A dark/light dot grids alternating, accents (curtain, space, navy, green, maroon, teal, emerald, orange,
lavender) for hook/payoff/CTA.

## 4. Typography & motion (from A — do not restyle)
Google Sans Flex (fallback Google Sans → Cyrillic), headline 74 px / 600 / lh 1.06 (56 px when a line > 16 chars),
**lowercase**, 2–4 words, ≤ 2 lines, per-word blur-rise (blur 14 → 0, y +24 → 0, 0.36 s expo.out). Grey caption 42 px
typewriter ~24 cps with per-char blur (over footage a lighter grey `#C9CCCC` for contrast). Hero number 106 px / 500.

## 5. Transitions
head ↔ insert and insert ↔ insert = A **blur-drift** (default) or **whip** (`transition_in.type`), drawn by the
assembler on the root timeline (contracts.md → "Transitions"): overlap 0.35–0.6 s, the outgoing layer drifts/whips out
with blur on top while the insert's own A entrance plays underneath; an incoming head clip starts ov/2 early and
settles from scale 1.06 + blur — the footage never freezes. One hard cut (`"cut"`) allowed at the hook. Boundaries sit
in the breath pause before the next sentence. Inside a single composition (demos) use `RSD.tx` / `RSA.transition`.

## 6. Audio — same as A
Default `energetic` profile: cleaned voice dominant, audible music bed and SFX (`audio-policy.md`). The `reference` profile keeps it voice only, dry, −14 LUFS, with no music and no SFX, as in style A's references.

## 7. Assembled runs
Assembler loads packs **a → d** (`tokens-a.css`, `a.js`, `tokens-d.css`, `d.js`). Head scenes are `kind:"head_overlay"`:
head.mp4 plays underneath, the scene uses `footage:{transparent:true}` (scrim + text + components only), punch-ins come
from `edit/cuts.json`. Inserts are `kind:"motion"`.

## 8. Pitfalls
Text over the face/eyes · subtitles built inside scenes (the assembler owns the caption track) · keyword headlines replaced by subtitles · boxes behind text · uppercase/bold restyles · music or
whooshes · lens blur / glitch / glow-widget gimmicks (that is the RSX pack, not D) · tiny hero objects in inserts
(< 46 % width) · drawn people · the reference creator's name instead of `brief.cta`.
