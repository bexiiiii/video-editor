# Branding — client colours, font and logo on any style

Every style (A–G) can wear a client's brand without losing its look: the brand replaces the style's **accent role**
only. Backgrounds, greys, typography scale, layouts, motion, signature display faces and semantic colours stay stock.

Input: `brief.brand` (contracts.md) → `{name, logo, accent, accent2|null, ink|null, font|null, keep_style_palette}`.
Tool: `scripts/brand.py` (stdlib; run by `assemble.py`) → `composition/lib/brand.css` (after the style tokens),
`brand.js` (`window.RS_BRAND`, before the libs), `brand.json` (data + contrast report).
No colours and no font → nothing is written; the style is byte-for-byte stock.

## Colour derivation
- Every stock accent family is a ramp around one base (A's bookmark `#1E8BFF → #7CCBFF/#0A4FD0/#06328F`, B's takeover
  `#1C86FD → #0D4C90`, E's gold `#E89E0C → #C9822E → #A8672C`, …). brand.py re-bases each stop on the brand colour by
  transferring its **OKLCH offset** (ΔL, chroma ratio; hue = the brand's). So shading/gloss/gradients keep the
  style's depth, only the hue changes. Near-grey brands (C < 0.03) stay neutral.
- Hover/pressed or darker surfaces = OKLCH L − n (hue kept, chroma gamut-clipped). Translucent tints (selection
  boxes, glows, shadows) = `rgba(<brand>, <stock alpha>)`.
- `accent2` (optional) takes A/D's lime **hook** role and E's rubric dot; else they derive from `accent`.
- `ink` (optional, dark) becomes A/D's light-theme keyword pill and E's headline ink.
- `keep_style_palette: true` → stock colours, but font/logo still apply.

## Contrast rules (enforced per theme, reported)
Thresholds — WCAG 2.x, sized for a phone (1080 px video ≈ 400 CSS px, so 72 px bold ≈ WCAG "large"):

| role | min | examples |
|---|---|---|
| text | **4.5** | B list numbers / segment labels, E kicker, labels on accent fills (chips, buttons, badges), text over selection |
| display text (≥ 72 px bold) | **3.0** | C keyword highlight, E gold gradient body (`gold-2`, `gold-3`) |
| non-text UI | **3.0** | handles, page dots, rings, cursor, A UI accent on both A pages |

- Each token is checked against **every background it lands on**: A dark `#0B0D0D` + light `#FBFDFD`; B light page
  `#F0F0F3` + card `#FCFCFC`, dark `#1A1A1C` + `#2C2C2E`/`#2E2E30`, white segment thumb, CTA pill `#EEEEEC`; the
  generated blue takeover (white text on the 50 % stop ≥ 4.5, white headline on the top stop ≥ 3.0); C dark/light;
  E page `#FCFCFC` + card `#F4F4F6`.
- Fails → brand.py moves **OKLCH lightness only** (smallest step that passes; lighter on dark themes, darker on light)
  and logs `adjusted <token>: <from> → <to> (<before> → <after>:1)`. Labels on accent fills prefer white: the fill is
  darkened up to ΔL 0.12 (E badges 0.10); if white still fails the label turns near-black `#0B0D0D`.
- Unreachable targets become a warning (best lightness used). `brand.json.report` lists every check.
- Stock palettes are not re-checked (they are the reference look; e.g. stock white-on-`#007AFF` is 4.0:1).
- Example results (2026-11): pharmacy green `#1FA971` → B text `#007D51` (2.65 → 4.56), chips/buttons `#008758`
  with white (3.08 → 4.56); beauty pink `#E85D9E` → B highlight `#C0377B`, chips `#CA4184`, A hook unchanged (5.3:1 on
  dark); navy `#1E2A78` → A UI `#4559AB`, A hook `#5E75CA`, B dark-theme dots `#5B72C7`, E gold = navy as is (12.3:1).

## Tokens per style

| style | brand overrides | stays fixed |
|---|---|---|
| **A** 3D Keyword | `--rsa-blue/--rsa-chip/--rsa-line-blue/--rsa-handle` (UI accent), chip + marker fill/label/glow, selection fill dark (`--rsa-sel`) + light (`.rsa-sel-box`), light-card rim, progress-bar gradient, **hook** `--rsa-lime(-alt)` (accent2 or accent), light keyword pill `--pill-bg` (ink only), JS: 3D bookmark + coin ramps (`RS_BRAND.palette.a`) | dark/light pages, dot grids, accent backgrounds (curtain, space, navy, green, maroon, teal, emerald, orange, lavender), greys/captions, dark-theme pill, glass cards, code-window/iOS-settings mock colours, red screenshot highlight, particle globe, Unbounded/Montserrat hook faces, type scale, motion |
| **B** iOS Keynote | system blue: `--rsb-blue/-2/-dark/-cta`, page-dot on (`--rsb-dot-on` per theme + `RSB.PALETTE.on`), segment label, selection box/caret/knob, typing bubble, save "on", CTA button + caret, timeline dots/check badge, ring/cursor/cursor-bubble defaults, colour-grid first tile, **blue takeover** gradient (`.theme-blue`) | Apple semantic colours (green = ok, red = error, orange, yellow, greys), Instagram `#0095F6` (IG card), all theme backgrounds except the takeover, cards, grid, titanium phone, dark pressed chip `#2B2B2B`, type scale, motion |
| **C** Keynote 3D | everything of A and B above + `--rsc-accent-dark/light` (keyword highlight), `--rsc-blue-a/b` + `.rsc-plate--blue`, hero glow default, chrome-dot glow, portal bloom (`RS_BRAND.palette.c`) | cinematic glows (orange/teal/emerald/navy/violet/lavender), glass, footage plate, greys, motion |
| **D** 3D Keyword × head | = A (D loads pack a; scrims, footage slot and face-safe zones stay fixed) | = A + scrims |
| **E** Data News | gold ramp `--rse-gold-1/2/3`, `--rse-gold` / `--rse-gold-v` gradients (headline accent, big numbers, bars, tabs, toggles, badges), kicker brown `--rse-kicker`, rubric dot `--rse-dot` (accent2 or derived), badge label colour if white fails, headline `--rse-ink` (ink only), JS: dot-row fill + line-chart gradient (`RS_BRAND.palette.e`) | page `#FCFCFC`, cards `#F4F4F6`, greys, track, Inter Tight caption track, type scale, motion |
| **F** Kinetic Talking Head | key word / caption highlight `--rsf-yellow` (accent), salmon insert `--rsf-salmon` (accent2) | red negative word, black/white, footage, type, motion |
| **G** Editorial Selfie | only the **value** treatment `--rsg-value` (bold-yellow, fitted ≥ 3:1 over dark footage `#262E3E`); accent2 → the kinetic insert: pale page `--rsg-mint`/`--rsg-mint-edge` (accent2 hue at L .885 / .68, low chroma) + ink `--rsg-navy` (accent2 darkened to ≥ 7:1); `--rsg-font` (grotesk) | **semantic treatments**: glow-pink (devotion/giving), serif-pink/grey/gold (reflection, honour), red (warning), bold-white (duty), glow-yellow neon (scenes); the serif face (Noto Serif Display condensed); lead white; white calligraphy page; footage; motion. Treatments carry meaning across reels, so a brand never recolours them |

JS libs read `window.RS_BRAND.palette.<pack>.<key>` through a `brand(key, stock)` helper — absent brand = stock
literal, so APIs and unbranded output are unchanged. Explicit props (`color`, `colors`, …) always win; a 3D object
with an explicit `color` keeps the stock shading stops.

## Fonts
- `brand.font` = a Google Fonts family. brand.py queries the css2 API and checks the `unicode-range` union covers the
  reel language: **ru** Cyrillic А–я Ёё · **kk** + Ә ә Ғ ғ Қ қ Ң ң Ө ө Ұ ұ Ү ү Һ һ І і (cyrillic-ext) ·
  **uz** Latin A–z + ʻ (U+02BB, oʻ gʻ) and ’.
- Covered → `@import` (weights 300–800 when variable, else the static weights) and the **body** font variable becomes
  `"<Brand>", <stock stack>`: A/D `--rsa-font`, B `--rsb-font`, C `--rsc-font` (A inside C follows it), E `--rse-font`, F `--rsf-font`, G `--rsg-font` (grotesk only; the G serif treatment face stays).
- Not covered / family not found / offline → stock font kept + warning. Signature faces never change (A hook
  Unbounded + Montserrat italic, A mono, E Inter Tight captions). Tracking was tuned for the stock fonts — check the
  branded preview for wide families (shrink-to-fit still protects line width).

## Logo
`brand.logo` (path relative to the work dir) is copied to `composition/lib/brand-logo.<ext>`; `RS_BRAND.logo` holds
the root-relative path. Scene-builders pass it as `avatar`/`logo` (B `ctaFollow`, E `header`/`post`/`poll`) unless
`brief.cta.avatar` is set. Libraries never inject it on their own.

## Previews (show the client before building)
```
scripts/make_brand_previews.sh work/<slug>            # all styles → work/<slug>/previews/style-<x>.jpg
scripts/make_brand_previews.sh brief.json b e         # some styles, next to the brief
  --at T1,T2,…  --out DIR  --plain (stock, for diffs)  --assets DIR (another assets tree)   KEEP_FRAMES=1 keeps PNGs
```
Same 4 instants as `assets/previews/style-*.jpg` (`assets/previews/timestamps.json`), so stock vs branded strips
compare tile by tile. Needs Node ≥ 22 and ≥ 1 GB free disk; temp dirs are removed. Stock previews are never touched.
Check with `python3 scripts/brand.py --work work/<slug> --check` (prints every contrast check) before rendering.
