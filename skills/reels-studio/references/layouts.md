# Layouts, spacing and variety — the anti-template rules

Every scene in `plan/scenes.json` gets a `"layout"` id. Builders implement it with `RSB.layout.*` / `RSC.layout.*`; style A has no layout helpers — compose the layout from `RSA` builders (`headline`, `hero`, `caption`, `card`, …) following the spacing rules below.
Frame 1080×1920. Reels UI covers the top ~12 % and the bottom ~18 %, so the **live area** is y 230 → 1575, x 90 → 990.

## 1. Spacing rules (all styles)
- The **content block** (all text + visuals in a scene, union bbox at its final state) is centred in the live area. Its vertical centre sits at y = 860–940 (≈ 46 %), never higher than y 760.
- The block fills ≥ 45 % of the live-area height (≥ 600 px), except layout `statement`. **No scene may leave the lower 40 % of the frame empty** while the upper part is crowded.
- Horizontal margins ≥ 90 px. Cards and visuals ≥ 70 % of the column width (≥ 630 px) unless they are deliberately small icons in a row.
- Vertical rhythm: kicker → headline 30–40 px; headline → visual 70–110 px; visual → caption 60–90 px. Use the same rhythm in every scene of a video.
- Hero objects (style A) are 46–60 % of frame width (500–650 px), never < 380 px. Hero numbers 300–420 px tall.
- Never show an empty container. A card, skeleton or frame is either filled with content or appears together with its content.
- Nothing overlaps text unless it is a highlight, pill or selection that belongs to that text.

## 2. Layout catalogue
| id | composition | typical use |
|---|---|---|
| `stack` | kicker + headline + one component, whole block centred | B default, statements with a visual |
| `hero` | headline top (y 360–520) + big visual centre + caption (y ≈ 1450) | A default |
| `visual-top` | big visual first (up to 55 % height) + headline below (y 1250–1450) | variety, tall visuals |
| `number` | giant number/stat centre + label above/below | any spoken number |
| `media` | real photo / screenshot / footage frame / iPhone mockup at 60–75 % height, short text overlay or under | proof, tutorials |
| `list` | 3–4 rows/cards building downward, centred column | steps, features |
| `compare` | two columns or two stacked states (before → after, A vs B) | contrasts |
| `statement` | 2-line big headline only, no visual (breath scene) | punchlines, max 1 per 6 scenes |
| `head` | full-frame talking head (real footage only) | hook / CTA / emphasis |
| `head-side` | talking head + one component in the chest band (y 880–1460) beside or below the face | head_overlay mode |

## 3. Variety rules (director must obey; QA enforces)
- No two consecutive scenes with the same `layout`. One layout ≤ 30 % of scenes.
- A component type is not reused within 3 scenes; ≥ 5 distinct component types in videos with ≥ 8 scenes; ≥ 4 distinct layouts per video.
- Alternate the visual mass: centre → top → bottom → full-bleed.
- Vary entrances: no more than two consecutive scenes using the same entrance (blur-rise, pop, slide, drop, build-down, wipe).
- Themes follow the style rules (A dark/light alternation + accents ≤ 3; B light/dark/blue by chapter).

## 4. Anti-"AI look" rules
- **Never draw people, faces or bodies.** A human on screen is always real footage (`edit/head.mp4`) or a real photo supplied by the user. If there is no footage, use a non-human visual.
- Emoji are allowed only as small accents inside UI (like an iOS notification) — never as the hero visual in a final render. Hero visuals are generated images (one consistent art direction per video: same material, lighting, camera angle; see `director.md` §4), real screenshots, or real brand logos the user supplied.
- No CSS "blobs" or placeholder shapes in final renders (demos may use them, clearly labelled).
- Prefer real proof: screenshots, screen recordings, numbers from the brief. A scene with real material beats a generic illustration.
- Keep copy human: short, specific, concrete numbers and names; no filler phrases ("в современном мире", "инновационное решение").
- Imperfection that the references have is OK (grain on dark, slight 3D tilt on cards); uniform perfect symmetry in every scene is not — use asymmetric layouts (`visual-top`, `compare`, `head-side`) regularly.
