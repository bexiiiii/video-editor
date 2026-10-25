# Component libraries

One section per style pack. Builder signature for every component: `lib.<component>(container, props, tl, at) → HTMLElement` (see contracts.md).

## Style B — "iOS Keynote" (Umar) · `assets/style-b/`

Files: `tokens.css` (fonts, theme classes, all component CSS) · `lib.js` (global `RSB`) · `demo/` (31.6 s reel built only from `RSB.layout.*`; run `demo/prepare.sh` before lint/snapshot/render — HyperFrames rejects `../` asset paths, so libs are copied into `demo/lib/` exactly as the assembler copies them into `composition/lib/`).
Load order: GSAP → `lib/runtime.js` (RS) → `lib/tokens-style-b.css` → `lib/style-b.js`. Build inside `await RSB.ready()` (fonts must be loaded: headlines/cards are **measured at build time**), register the timeline last.
Every builder: `RSB.x(container, props, tl, at) → HTMLElement`; all times in props are absolute local seconds. Entrances are `fromTo`; every later state change uses `RSB.ft` (fromTo + `immediateRender:false`) so seeking anywhere is exact. Placement props shared by most builders: `x`, `y` (absolute px), `center:true` (horizontal centre), `flow:true` (in normal flow — used inside layout slots), `z`, `style` (object).

**Font substitution.** SF Pro Display is not on Google Fonts → Inter 4 variable (`opsz` 14–32 = Inter Display at large sizes) via Google Fonts `@import`; the HyperFrames compiler fetches and embeds it. Inter is wider than SF: tracking tuned and measured against the reference stills (headline −0.03em; kicker/sub 52px −0.01em; crumb 24px). Emoji: system font (Apple Color Emoji on macOS) — it is deliberately not named, because the compiler cannot embed the 180 MB Apple font (>128 MB Chrome limit). On Linux render hosts install Noto Color Emoji.

### Themes & layout (tokens.css)
| Class | Look | Source |
|---|---|---|
| `.theme-light` | `#F9F9F9→#EBEBED` + 2px `#E6E6E8` grid, lines x=20+130k (150…930), y=50+130k | DeZREMAtvBf §2 |
| `.theme-dark` | `#171719→#121214` + faint middle band, grid `#222225` | DeZREMAtvBf §2 |
| `.theme-dark2` | `#1A1A1A→#2E2E30` diagonal light wedge + grain (auto) | De1roE4t7Lf §2 |
| `.theme-dark3` | "studio floor" `#1A1A1C→#303033`, grid stronger at bottom | DelZA2dtAE6 §2 |
| `.theme-blue` | `#1C86FD→#0D4C90`, rings r=161n @ (540,980), no grid; chrome white | DeRXnpgtYe6 §2 |
| `.theme-paper` | warm radial `#F4F2F0→#DDDAD7`, no grid (older editorial) | Dd3Uz4Mgbn- §2 |
Type scale: kicker 56 Light `#727276` (dark `#A1A1A6`, blue white@80 %) · headline 108 Bold one line, shrink-to-fit ≤790 px (min 72) · second 60 Bold · sub 56 Light · callout 54 Semibold · card quote 46/70 Semibold · qcard quote 48/70 · crumb 24.

### Layouts — `RSB.layout.<id>(container, props, tl, at) → block` (v1.1, implements `layouts.md`)
Build every scene with a layout; builders below are what goes into its slots. The block (x 90–990) is measured at build time and **vertically centred in the live area** (default centre y 880, clamped to 250…1575); `block.metrics` = {top, bottom, height, centre, fill}, `block.slots` = named parts, `block.recentre()` after inserting extra content; a console warning fires if a block (except `statement`/`head*`) is < 600 px. Rhythm constants `RSB.layout.RHYTHM`: kicker→headline 34 · headline→sub 26 · headline→visual 96 · visual→caption 76 · step→kicker 46.
Text props = `RSB.line` props (`{words|text, at, highlight, emoji}`); `visual` = `(slot, tl) => el` **or** `{type:'player'|'card'|'ctaFollow'|…, at, …}` (called as `RSB[type](slot, {flow:true,…}, tl, at)`).
| id | Props (main) | Composition | Measured |
|---|---|---|---|
| `stack` | `step, kicker, headline, sub, second, visual \| visuals[], visualGap, caption{kicker,second}, cy` | centred column; visual in flow slot | DeZREMAtvBf 3.8 s: kicker 416 px wide / headline 730 px (ref 726) |
| `visual-top` (`visualTop`) | `visual, kicker, headline, cy=900` | visual first, text under it → headline lands y ≈ 1250–1450 | DeZREMAtvBf 33.6 s |
| `number` | `step, kicker, number{from,to,dur,size=400,suffix{text,size=96,color},color,at}, headline, sub, below` | giant counter (≈290 px digits) + labels + optional capsule row | DeRXnpgtYe6 3.5 s |
| `media` | `device:'iphone'\|'screenshot', src\|node\|html, width=565, text, textCls, textPos:'top'\|'bottom', deviceAt, enter, cy=905` | iPhone 565×1160 (60 % of frame) or 790×1150 framed shot; `slots.device.screen` for toggles/cursors | Dd1b9kEA-KL 16.0 s |
| `list` | `step, kicker, headline, rows[], variant:'cards'\|'timeline', skeleton≤0.45, rowH=168, gap=30, width, caption` | `RSB.listRows`, building down | DelZA2dtAE6 15.5 s: 790×168 rows, gap 30 |
| `compare` | `kicker, headline, mode:'columns'\|'stacked', left, right, pick, pickAt, caption` | `RSB.compare` | DeRXnpgtYe6 40.5 s, DeZREMAtvBf 53.6 s |
| `statement` | `kicker, lines[2], size=120, cy=900` | breath scene, no visual (≤ 1 per 6 scenes) | — |
| `head` | `footage{node\|src\|label,lens}, sticker{text,emoji,at}, caption{phrases}` | full-frame talking head; hide chrome | De1roE4t7Lf 2.0 s |
| `head-side` (`headSide`) | `footage, kicker, headline, visual\|visuals[], caption{phrases}, band=[880,1460]` | components centred in the chest band, face area clear; caption under band | DelZA2dtAE6 59.5 s, Dd1b9kEA-KL 39.8 s |
**People:** a human on screen is only real footage passed as `footage.node` (static framework `<video>`) or `footage.src` (photo). Without it `RSB.footage` renders a labelled neutral slot (dark frosted rectangle, camera icon, "ваше видео") — the library contains no drawn figures, faces or face emoji; CTA avatars fall back to an initials monogram.
**No empty containers:** `card` enters ≤ 0.25 s before its first text (unless `allowEmpty`), `skeletonRows`/`listRows` show a skeleton ≤ 0.45 s, `calendar` fills from `at+0.35`.

### Components
| Builder | Props (main) | Timing / behaviour | Reproduces |
|---|---|---|---|
| `page` | `theme`, `grain`, `visible` | static; `visible:false` = revealed by a transition; components go in `page.content` | all |
| `chrome` | `series, topic, dots, theme, active, hidden, steps[{at,active,theme,hidden}]` | crumb x=150 y≈187/221; dots 8px/22px pitch, right x=930, y 212; active = 24×8 pill; each step 0.45 s power2.inOut (colour + pill) | DeZREMAtvBf §1 |
| `line` | `cls: kicker\|headline\|sub\|second\|callout`, `words[{w,t}]` or `text+at+stagger`, `highlight`, `emoji{e,at}`, `fit`, `maxPx/minPx/maxW` | per word: blur 11→0, opacity 0→1 (≈0.5 at frame 1), x +22→0, 0.14 s power3.out; words pre-laid-out; `line.inner` = target for selection/strike | DeZREMAtvBf §4 |
| `stack` | `top`, `step`, `kicker`, `headline`, `sub`, `second`, `gap{kh,hs,ss,sk}` | centred column x 145–935; measured vs refs (kicker/headline/sub tops within ±6 px) | DeZREMAtvBf §3 |
| `slot` | `(parent, mt)` | flow container for components inside a stack | — |
| `dim` | element(s), `to=.5`, `dur=.3` | focus shift dimming | DeZREMAtvBf 14.8 s |
| `card` | `meta{left,right}`, `head{emoji,words,right:{type,…}}`, `lines[]`, `rows[]`, `slot` | enter y+20/scale .98/blur 8 → 0.4 s; height grows 0.3 s per new line; light `#FCFCFC` r40 hairline, dark `#2C2C2E` r44 | DeZREMAtvBf §5A/B |
| `quoteCard` | `emoji, title, count, accent, quote, emphasis[], barFrom, barTo` | enter 0.3 s expo.out; emoji circle accent@25 %; bar fills linearly over the section | DeRXnpgtYe6 §5 |
| `emojiCircle` | `emoji, size, tint, alpha, bg` | pop 0.3 s | DeRXnpgtYe6 |
| `capsule` | `text, kind: green\|redtext\|red\|orange\|blue\|grey\|outline\|step\|ok\|bad`, `icon`, `dot` | pop scale .8→1 + blur 6, back.out(1.6) 0.25 s (step/outline: rise 0.3 s) | DeZREMAtvBf §5E, De1roE4t7Lf §3 |
| `checkBadge` | `x, y, size=48, color, ring` | back.out(2) 0.25 s + check stroke draw 0.2 s; use ≈0.8 s after a selection | De1roE4t7Lf §5 |
| `player` | `time, fillAt, fillDur, fillTo, color, scale` (1.3 → 790 wide) | rise 0.3 s → red bar scaleX 0→1 0.22 s power2.inOut (at+0.28) → label 0.12 s | DeZREMAtvBf §5D |
| `ring` | `size=560, stroke=12, color, track, stop=.8, dur=.9, startDeg=-60, label, check` | clockwise from 10 o'clock, power2.inOut, stops at 80 %; `stop:1, check:true, size:230, stroke:8, color:#34C759` = closed loop | DeZREMAtvBf §5G |
| `countdown` | `from="00:59:59"`, `ticks` | orange capsule pop, then ticks −1 s per real second | DeZREMAtvBf 20 s |
| `counter` | `from, to, dur=.75, ease=power3.out, size, sep (narrow nbsp), suffix{text,size,color}, blur` | integer roll with vertical SVG motion blur; width reserved for the final value | DeRXnpgtYe6 §4, DelZA2dtAE6 §4 |
| `calendar` | `cols=6, rows=5, count, fillAt, stagger=.055, fillBg, fillInk` | glass 82px r22 cells pop (12 ms stagger), then fill 1..N sequentially | De1roE4t7Lf §5 |
| `colorGrid` | `cols=6, rows=5, colors[], startCol, tileStagger=.06, colGap=.32, numbers` | 98×99 r22 pitch 114, fills column by column starting at `startCol`, numbers column-major | DeRXnpgtYe6 §5 |
| `selection` | target = `line.inner`; `pad=14` | start caret+knob 0.12 s → 25 % blue box sweeps L→R 0.2 s → end caret 0.16 s at +0.32 | DelZA2dtAE6 §4 |
| `strike` | target = `line.inner`; `color, dim=.45, thickness=3` | line draws L→R 0.25 s power2.out, words dim | DelZA2dtAE6 §4 |
| `segmented` | `items[], active, steps[{at,active}]` | white thumb slides 0.4 s power3.inOut, active label blue | DelZA2dtAE6 §5 |
| `notification` | `icon\|default bubble, iconBg, title, time="hozir", text, skeleton=2, width, from` | drops from y−20 + blur, grey→white, 0.35 s expo.out | DeZREMAtvBf §5C |
| `typing` | `color, dur` | pop, dots pulse (finite repeat) | De1roE4t7Lf 29.4 s |
| `bubble` | `text, bg, color` | grey iMessage bubble pop | DeRXnpgtYe6 §5 |
| `skeletonRows` | `rows[{emoji,caption,title,at}], enterAt, stagger, height` | rows rise 0.35 s with skeleton; on `at`: skeleton blurs out 0.15 s, content in x+20 0.25 s expo.out | DelZA2dtAE6 §5 |
| `cursor` | `kind: glove\|arrow, color, path[{x,y,at,dur}], taps[], ripple` | moves 0.27 s power2.inOut; tap scale .85 (2 f) → 1 (3 f) + ripple | Dd1b9kEA-KL §5 |
| `ripple` | `x, y, color` | Ø90 ring ×0.4→1.8, fades 0.45 s | DelZA2dtAE6 §5 |
| `cursorBubble` | `x, y, text, color` | arrow arrives 0.3 s, bubble pops at +0.18 back.out(1.6) | DeZREMAtvBf §5F |
| `iphone` | `x, y, flow, width=565, src \| node (static framework <video>) \| html (none → labelled slot), enter: rise\|pullout\|fade, floor, float` | deep-purple titanium `#3B2A3D` rim `#6A4F6C`, island, floor shadow; rise y+260/scale .85 0.33 s expo.out; pullout scale 2→1 | Dd1b9kEA-KL §5, Dd3Uz4Mgbn- §5 |
| `ctaFollow` | `x, y, flow, avatar \| monogram (default: initials of name[0]), name[2] from the brief, button, unrollAt, typeAt, pressAt` | avatar pops → pill unrolls 206→619 back.out(1.2) → name types per word → button scale .5 + `#2B2B2B` (dark chip) | Dd1b9kEA-KL §5 |
| `igProfile` | `x, y, flow, avatar \| monogram, handle, verified, bio, posts[a,b], followers[a,b], following, button, done, buttonAt, tapAt, chip{text,icon,at}` | stats count 0.6 s → button → tap ripple → grey "Obuna bo'ldingiz", green ✓, followers +1 | De1roE4t7Lf §1 |
| `savePill` | `x, y, flow, text="Saqlash", done="Saqlandi", tapAt` | frosted→white; tap ripple + blue state | DelZA2dtAE6 §5 |
| `caption` | `y=1398, size=62, color, from, settle, phrases[{words\|text,at}]` | chest band; words grey→colour 0.21 s with 5px blur; phrase swap in 1 frame | Dd1b9kEA-KL §4, Dd3Uz4Mgbn- §4 |
| `sticker` | `text, emoji="🍿", y=1050, size=64, maxLines=2` | uppercase Heavy, auto-shrinks to 2 lines; frosted→sharp 0.2 s, emoji pops | De1roE4t7Lf §3 |
| `lens` | `(container, {blur})` | static lens-edge blur overlay for footage | Dd1b9kEA-KL §1 |
| `footage` | `node \| src, fit, lens, slot{x,y,w,h}, label="ваше видео", sub, compact` | real talking-head video/photo, or labelled neutral slot (never a figure) | layouts.md §4 |
| `listRows` | `rows[{emoji\|num, caption, title, at, right{type:'capsule'\|'check',…}}], variant:'cards'\|'timeline', width, rowH, gap, skeleton, flow` | each row rises WITH its content on its word (0.35 s); timeline: numbered dots + rail drawing down | DelZA2dtAE6 §5, DeZREMAtvBf 39.5 s |
| `compare` | `mode, left/right{tag{text,kind}, emoji, quote, meter{value,color,label}, at}, pick, pickAt, width` | tiles rise 0.4 s; meters fill 0.7 s; pick → loser 50 %, winner ×1.03 + ✓ | DeRXnpgtYe6 §5 |
| `screenshot` | `src \| node \| html, width=790, height=1150, radius, tilt, label, flow` | framed proof shot, rise y+80/scale .94 0.4 s expo.out | Dd3Uz4Mgbn- §5 |
| `monogram` | `(host, name)` | initials avatar fallback | — |

### Transitions — `RSB.tx.<name>(tl, outEl, inEl, at, opts)`
| Name | Behaviour | Source |
|---|---|---|
| `dissolve` | out: scale 1→.97, blur 0→6, opacity →0 over near-black (0.55 s power2.inOut, `lift` for drift-up variant); in fades from at+0.06. Put the chrome step at the same `at`. | DeRXnpgtYe6 §6 |
| `portal(…, opts, layer)` | white orb with bloom travels an arc (0–0.4 s), grows ×32 expo.in (0.33–0.58), white-out at +0.46, layers swap at +0.6, white fades 0.55 s. Add sub-boom SFX at at−0.15. | De1roE4t7Lf §6 |
| `datamosh` | 8 frames: SVG turbulence → discrete bands → horizontal displacement + RGB split on out; swap mid; block smear on in; seeded by `RS.rand(seed)` | DelZA2dtAE6 §6 |
| `rgbGhost` | 6 frames: vertical ghost offsets +12…40 px with chroma split, swap mid | DeRXnpgtYe6 §6 |

### Verification (demo)
Demo = 10 scenes / 31.6 s: head → stack → number → list → visual-top → compare → stack → media → statement → head-side (9 distinct layouts, no layout twice in a row, ≥ 14 component types, themes dark/light/blue/dark/light/dark2/light/paper/dark3, chrome on every graphic scene, hidden over footage). `lint` 0/0. Content-block bbox at each scene's final state (measured on snapshots, live area): centres 866–916 px (refs 830–950), heights 676–1264 px (refs 660–1150); before v1.1 (same measurement on the audit sheet) centres were 674–846 px and blocks ended at y 976–1320, leaving 255–600 px of the live area empty below; now they end at 1208–1548. Kicker 56 px measured against DeZREMAtvBf 3.8 s (same copy): 416 px wide vs ref 416 (was 385); headline 730 vs 726 px. Rendered `demo/demo.mp4` (1080×1920, 30 fps, 31.6 s).
Known deviations: Inter vs SF Pro (glyph shapes); emoji depend on host fonts; head scenes show the labelled footage slot until a real `head.mp4` is passed; datamosh is an SVG-filter approximation; paper theme omits the embossed column lines and giant numerals.

## Style A — "3D Keyword" (Zaytsev) · `assets/style-a/`

Files: `tokens.css` (fonts, palette, 11 CSS-only backgrounds, type scale, three-tier layout, component CSS) · `lib.js` (global `RSA`) · `demo/` (31.5 s showcase of every component/background/transition; run `demo/prepare.sh` first — it copies `runtime.js`, `tokens-a.css`, `a.js` into `demo/lib/`, the same layout the assembler builds).
Load order: `lib/tokens-a.css` → GSAP → `lib/runtime.js` (RS) → `lib/a.js`. Build synchronously (nothing is measured at build time; all geometry comes from props), register the timeline last.
Every builder: `RSA.x(container, props, tl, at) → HTMLElement`; `x`/`y` = stage px of the element **centre** (0×0 flex anchor, so GSAP owns `transform`); times are absolute local seconds. Entrances are seek-safe `fromTo`; follow-up states use `immediateRender:false`. Text never exits on its own — only `RSA.transition*` moves old content out.

**Fonts.** Google Sans Flex has **no Cyrillic** on Google Fonts, so the stack is `"Google Sans Flex", "Google Sans", "Onest"` — Russian glyphs come from Google Sans (same design). Hook display = Unbounded 900 (squeezed `scaleX(.8)` to the ref's 786 px width at 392 px cap height); lime accent = Montserrat 800 italic; code = JetBrains Mono. Placeholder 3D objects use colour emoji via `@font-face "RSA Emoji" { src: local(...) }` or CSS/SVG blobs — **real runs pass generated transparent PNGs via `src`**.

### Themes & layout (tokens.css)
| Theme (`RSA.layer({theme})`) | Recipe | Source |
|---|---|---|
| `dark` / `light` | `#0B0D0D` + 3 px dots 36 px `#2D2F2F` · `#FBFDFD` + 3 px dots 24 px `#DADDDD` (soft edge fade) | Der0 §2 |
| `curtain` | seeded pleat gradient (13→36 px pleats, contrast falls L→R) × red→black vertical + gold leak `#CAA277` bottom-right | Dej §2 |
| `space` | `#050311`, violet TL `#2D044F`, magenta BR `#370040`, centre glow, 44 seeded box-shadow stars | Dej/DeV §2 |
| `navy` / `green` / `maroon` | 135°/145° base gradient + 3 blurred 35° god-ray bands masked from TL + dot grid (maroon 20 px `#4A1525`) | Der0/DeV §2 |
| `teal` / `emerald` | bottom elliptical glow `#046D98`/`#077A52` → black by 75% + spotlight arch | DeV §2 |
| `orange` | 1500×820 radial at (800,300) `#C84A00`→`#130200` at 50%H → black | Dey §2 |
| `lavender` | top radial `#C3D3FA`→`#FBFDFD` by 72% + faint ring banding | Dej §2 |

Type: headline 74 px / 600 / lh 1.06 / −0.01em, 56 px when a line > 16 chars (measured on ref stills; ≤2 lines, lowercase is the copy's job) · hero number 106 px / 500 · caption 42 px / 400 / lh 1.18 `#767878` (dark) `#686B6B` (light) · label 44 px. Tiers: headline centre y 545 (≈28%), bottom variant 1340 (≈70%), visual ≈1000, caption centre 1460 (≈76%), side margin 100.

### Components
| Builder | Props (main) | Motion / timing | Ref |
|---|---|---|---|
| `layer` | `theme, drift` → `{bg, content, inner, over, theme}` | bg ray/glow drift only | — |
| `background` | `theme, drift, grid` | static | all |
| `headline` | `text` ("a / b"), `words[{w,t}]`, `stagger=.12`, `pills[]`, `position`, `size`, `weight`, `halo` | per word: opacity 0→1, blur 14→0, y 24→0, .36 s expo.out; pre-laid-out lines | Dej §4A, Der0 §4.1 |
| `caption` | `text` (string/lines), `y`, `cps=24`, `color` | typewriter, per-char blur 6→0 in .12 s, anchored (word-grouped, no reflow) | Dej §4B |
| `label` | `text, x, y, size, color, cps` | typewriter | Dej §3 |
| `hero` | `src`/`emoji`/`blob` (`tile`,`tile-dark`,`disc`,`coin`,`orb`,`bookmark`), `size`, `x,y`, `entry` (`pop`,`rise`,`slide`,`drop`,`ghost`), `from`, `idle{amp,period,until}` | pop .1→1 back.out(1.4) .3 s · rise from +900, .38 s expo.out + vertical SVG motion blur · slide ±640 px .4 s + horizontal blur · drop power3.in .32 s + squash · idle off by default | Dej §5, DeV §5 |
| `stack` | `count, x, y, step=44, interval=.15, blob` | drop-and-stack | Dej scene 4 |
| `iconRow` | `items[{emoji/src,label,t}]`, `y, size=200, gap=400, zigzag, between` | pop on word time, .1 s sibling stagger, labels type +.45 s | Dej hook, Dey §5 |
| `card` | `variant` (`dark`,`glass`,`frost`,`light`,`white`), `width,height,radius`, `tilt{rx:2,ry:-4}`, `icon,title,sub,body` | y 80→0, blur 16→0, rotateX 8°→2°, .4 s power3.out; sub types +.25 s; gradient rim via mask + inner glow | Dej §5, Der0 §5 |
| `glassPill` | `text, icon, x, y, size` | scale .6→1 back.out(1.6) .35 s | Dey §5 |
| `codeWindow` | `lines[], width, cps=40, size=40` | traffic lights; lines typed with syntax colours | Dej scene 6 |
| `repoCard` | `name, title, lines[]` | GitHub mark + typed name/lines | Dej scene 5 |
| `screenshot` | `src` or placeholder `rows`, `theme`, `width,height,tilt=5`, `highlights[{x,y,w,h,t}]`, `hlColor`, `lens{x,y,t,zoom}`, `entry` | no device frame; red 3 px box jumps .28 s expo.out; lens = zoomed clone, back.out(1.8) | DeV/Dey §5 |
| `numberRoll` | `value, unit, x, y, size=106` | per-digit slot roll .38 s power3.out, .03 s stagger, vertical motion blur; unit blurs in +.05 s | Der0 §4.3 |
| `pill` | `text, x, y, size=56` (inline: `headline.pills`) | clip wipe L→R + rotate −8°→0, .35 s power3.out | Der0 §4.4 |
| `selection` | `text, before, after, x, y, size=62, selectAt` | fill `#1C3C5C` sweeps .3 s power2.out, end handle travels | Der0 §4.5 |
| `chip` | `text, icon, x, y, size=30, variant` (`chip`/`marker`) | pop back.out(1.7) .32 s · marker wipes behind words | Der0/Dey |
| `connector` | `from[x,y], to[x,y], style` (`dashed` 10/10, `dotted`), `curve` | masked dash draw-on .45 s | Der0 §5 |
| `flow` | `nodes[{id,type,t,h,props}]`, `edges[{from,to,t}]`, `pans[{t,y,dur}]`, `grid`, `gridOffset` | camera pan power2.inOut (grid scrolls with it) | Dey 5.7–11 s |
| `progressBar` | `x, y, width=800, height=26, dur=2` | fill scaleX power1.inOut + shimmer | Der0 scene 8 |
| `globe` | `x, y, size=650, count=2000, speed=10, dur, seed` | Fibonacci sphere on canvas, redrawn from a timeline proxy (seek-safe); 2 precessing orbits | Der0 finale |
| `bookmarkCTA` | `headline='сохрани', title, caption, layout, src, size=370` | bookmark rises, headline +.2, title types +.5, caption ≥ +1.0, held | Dej/DeV ending |
| `hookDisplay` | `label, word, sub, accent, wordSize=540, squeeze=.8` | per-letter blur 20→0 from opacity .2, 70 ms stagger (mid-reveal on frame 0); lime accent −5° + 2 underlines | Der0 hook |

### Transitions — `RSA.transition(tl, fromLayer, toLayer, tc, {type, dir, bg, shared})`
`tc` = next sentence onset. Clips must overlap: new layer starts by `tc−0.25`, old ends after `tc+0.15` (`RSA.transitionWindow`). Split halves `transitionOut` / `transitionIn` for per-scene sub-compositions.
| type | Spec | Ref |
|---|---|---|
| `blur-drift` (`dir`) | old drifts 260 px + blur 0→24 + fade, .28 s power2.in from tc−.18; bg crossfade .28 s linear; new from −160 px, blur 20, .32 s expo.out at tc−.05 | Dej §6 |
| `zoom` | old scale 1.3 + blur 28 (zoom-through) | Dej 1.92 s |
| `whip` (`up/down/left/right`) | old ±320 px in .15 s power2.in + directional SVG blur 0→26; new from ∓270 px, .4 s expo.out, blur 18→0; bg swaps at tc (same theme) or fades .25 s | Der0/Dey §6 |
| `lum` (`shared:{el, from:{x,y,scale}, twin}`) | bg .25 s linear; old y −60, blur 12; new from +250, blur 14, .4 s expo.out at tc+.1; shared element (in `to.over`) FLIPs .5 s expo.inOut | Der0 §6 |
| `cut` | hook only | Der0 2.05 s |

### Verification (demo)
`lint` 0 errors (2 track-density warnings) · `check` passes (layout infos only; lens/roll/selection carry `data-layout-allow-*` waivers) · contrast 91/91 AA. Side-by-side sheets vs Dej 1.9/3.0/22.8/37.5/55, Der0 1.5/20.5/45/56, DeV 81: headline width within ~4%, positions within ~30 px after calibration (headline 74 px, long 56 px, centre y 545, mono 40 px, selection 62 px, bookmark 370 px). Rendered `demo/style-a-demo.mp4` (1080×1920, 30 fps, 31.5 s, 8.4 MB, `--workers 1 --low-memory-mode`).
Known deviations: Google Sans/Unbounded/Montserrat stand in for the refs' exact faces; placeholder objects are emoji/SVG blobs (not AI-rendered clay 3D); curtain pleats are a seeded gradient (no real fabric shading); frosted cards lose backdrop blur inside filtered layers; drop entry is a simple squash, not physics; iPhone-mockup proof frames (Dey) are not part of the library.

## Style C — "Keynote 3D" (A × B fusion) · `assets/style-c/`

Files: `tokens.css` (C tokens, themes `.rsc-dark/.rsc-light/.rsc-blue`, A-glow overlays, C type scale, glass-on-dark skin for B components, footage slot) · `lib.js` (global `RSC`) · `demo/` (31 s Russian "Link HR" showcase, 9 scenes / 9 layouts; run `demo/prepare.sh` first — copies runtime + A + B + C into `demo/lib/` with the assembler's names). Spec: `style-c.md`.
Load order: CSS `tokens-a.css` → `tokens-b.css` → `tokens-c.css`; JS GSAP → `runtime.js` → `a.js` → `b.js` → `c.js` (assembler does this for style `c`). Build inside `await RSC.ready()` (headlines are measured), register the timeline last. Every builder `RSC.x(container, props, tl, at)`, absolute local seconds; C reuses RSA/RSB public builders, so all A and B components are available on C pages too (B ones get the glass skin automatically on cinematic-dark and blue pages).

### Builders
| Builder | Props (main) | Behaviour | Built on |
|---|---|---|---|
| `page` | `theme: dark\|light\|blue`, `glow: orange\|teal\|emerald\|navy\|violet\|lavender`, `kind: cinematic\|ui\|head`, `glass` | root with `.bg .content .inner .live .theme` (RSA layer shape → A transitions work); `.live` = flex column over y 230–1575 | RSA.background |
| `chrome` | as RSB.chrome; step themes may carry `:glow` | breadcrumb + page dots, dots glow on dark | RSB.chrome |
| `headline` | `text "a / b"`, `words[{w,t}]`, `mode: keyword\|ui\|statement`, `highlight`, `maxW=900` | 92 / 100 / 124 px Bold −0.035em; per word blur 14 + y 22 → 0, 0.3 s power3.out; shrink-to-fit at build | RS.words |
| `kicker` / `sub` | `text\|words, at, highlight, mt` | 46 px Light grey, B word reveal (blur 11, x +22, 0.14 s) | RS.words |
| `caption` | `text, at, cps=26, mt` | A grey typewriter, per-char blur, anchored | — |
| `hero3d` | `src\|emoji\|blob, size 500–650, entry pop\|rise\|slide\|drop, glow, idle` | in-flow box; accent glow + floor contact; A entry with motion blur; finite idle bob | RSA.hero |
| `glassCard` | `width, height, ry, padding, radius` | in-flow A glass card (lit rim, inner glow, tilt), `.card` = content box | RSA.card |
| `stat` | `value "5,1", unit, size, color, width` | A slot-machine roll centred in an in-flow box | RSA.numberRoll |
| `uiCard` | `kind` = any RSB builder, `glass` | calls RSB[kind]; `glass:true` forces the glass skin | RSB.* |
| `footage` | `label, sub, transparent` | labelled neutral footage slot (demo); `transparent` in real runs | — |
| `audit(page)` | — | `{top,bottom,centre,height,fill}` of `.rsc-m` blocks at the current seek (QA vs layouts.md) | — |

### Layouts — `RSC.layout.<id>(page, spec, tl, at)` → `{root, …parts}`
| id | spec | parts |
|---|---|---|
| `stack` | `kicker, headline, sub, visual(slot), visualW/H, caption` | kicker, headline, slot, visual, caption |
| `hero` | `headline, hero{…hero3d, at} \| visual(slot), caption, headlineY=440, visualY=965, captionY=1450` | headline, hero, caption |
| `visualTop` / `visual-top` | `hero \| visual(slot), extra(slot), headline, caption` | slot, hero, headline, caption |
| `number` | `kicker, value{from,to,dur,at,size,suffix,sep}, sub, badge{text,kind,at}` | number (RSB.counter), sub, badge |
| `media` | `kicker, headline, phone{width=460, html\|src\|node, at, enter}, after(slot, phone, geo)` | phone, slot, `geo.toSlot(sx,sy)` (screen px → slot px for cursors) |
| `list` | `kicker, headline, notification{…, at}, rows[{emoji,caption,title,at}], enterAt, stagger, rowHeight=150` | notification, rows |
| `compare` | `headline, left/right{title, src, value, unit, color, note, at}, caption, cardH=560` | left, right, row, caption |
| `statement` | `headline{text, words, highlight}` | headline |
| `head` | `footage, sticker{text,emoji,y,at}, phrases[{words}], captionY=1398` | footage, sticker, caption |
| `headSide` / `head-side` | `footage, component(band), bandY=900, bandH=380, phrases, captionY=1420` | footage, band, component, caption |

### Transitions — `RSC.tx.<name>(tl, from, to, at, opts)` · clip windows `RSC.txWindow(type, at)`
| Name | Use | Behaviour |
|---|---|---|
| `whip` (`dir`) | between chapters | RSA whip on the pages (150 ms out + directional SVG blur, 400 ms expo settle from 270 px); bg cut if same theme else 0.25 s fade; window [at−0.25, at+0.15]; one whoosh at at−0.12 |
| `dissolve` | within a chapter | RSB dissolve + incoming content un-blurs 10→0; window [at, at+0.6] |
| `portal` (`opts, layer`) | head ↔ motion | RSB portal, blue bloom, `#FBFDFD` flash; window [at, at+1.25]; sub-boom at at−0.15 |

### Verification (demo)
`lint` 0 errors (2 track-density warnings, same as A). `RSC.audit` at each scene's final state: block centres y 902–909 for all motion scenes, fill 0.46 (number) – 0.90 (media); statement and head-side exempt. Snapshot sheet of all 9 final states reviewed; rendered `demo/style-c-demo.mp4` (1080×1920, 30 fps, 31 s, 6.5 MB, `--workers 2`). Glyph check: Russian, Uzbek Latin ("Oʻtkir") and Kazakh ("Айгерім") render in Inter.
Known gaps: Fluent Emoji 3D PNGs are 256 px (upscaled ≈2.2× at hero size — real runs use generated 1024 px art); demo is silent (audio policy documented, not mixed); footage is a placeholder slot; glass skin has no backdrop blur (filters on parent layers would drop it anyway); A's whip blur is 1-axis SVG blur, not true shutter blur.

## Style D — "Talking Head × 3D Keyword" (Style A over the head) · `assets/style-d/`

Files: `tokens.css` (footage base, punch camera, face-safe zones, scrims, slot) · `lib.js` (global `RSD`, thin layer over `RSA`) · `demo/` (30 s Russian "Link HR" showcase, 9 scenes; run `demo/prepare.sh` first — copies runtime + A + D into `demo/lib/` with the assembler's names). Spec: `style-d.md`.
Load order: CSS `tokens-a.css` → `tokens-d.css`; JS GSAP → `runtime.js` → `a.js` → `d.js` (assembler does this for style `d`). `await RSD.ready()` (fonts), register the timeline last. Everything visual is an unmodified RSA builder; RSD layers have RSA's layer shape (`bg/content/inner/over/theme`) so `RSA.transition` runs between head and insert layers.

### Builders
| Builder | Props (main) | Behaviour |
|---|---|---|
| `headBase` | `node \| src \| transparent, fit, label, sub, face:'upper'\|'lower', punches[{at, scale=1.12}]` | full-frame footage, no lens effects; punch-ins = hard scale sets about the eye line (origin 50 % 38 %); no source → labelled neutral slot with the assumed face box + eye line (never a drawn person); `transparent` for assembled `head_overlay` scenes |
| `scrim` | `where:'lower'\|'upper', opacity` | soft `#0B0D0D`-based gradient (0.78 → 0 over 52 % / 0.72 → 0 over 38 %) — no boxes |
| `headLayer` | `footage, zone, scrim` | RSA-shaped layer: bg = footage + scrim, A dark ink, A halo on text |
| `insertLayer` | RSA.layer props | full-screen A layer (any A theme) |
| `headline` / `caption` | RSA.headline / RSA.caption props + `zone` | A headline at y 1340 (lower) / 390 (upper); caption 1528 / 548 (lighter grey `#C9CCCC` over footage) |
| `component` | `{type: any RSA builder, side:'below'\|'right'\|'left', at, …}` | places one A component beside/below the face (below 540/1045, right 820/1000, left 260/1000); heroes default 400 px (≈ 37 %) |
| `cta` | `name, handle, headline='сохрани'` | RSA.bookmarkCTA with identity from `brief.cta` (throws without a name) |
| `tx.go / tx.blurDrift / tx.whip` | `(tl, from, to, tc, o)` | RSA.transition (blur-drift 0.28 s, whip 150 + 400 ms with motion blur, lum, zoom, cut) |
| `window(tcIn, tcOut, typeIn, typeOut)` | — | clip window via RSA.transitionWindow |

### Layouts — `RSD.layout.<id>(clip, spec, tl, at)` → layer (`.parts`, `.layout`)
| id | spec | composition |
|---|---|---|
| `head` | `footage, zone, headline{text,words,at,pills}, caption{text,at}` | footage + scrim + zone headline (+ caption) |
| `head-side` (`headSide`) | `+ component{type, side, …}` | head + one A component beside/below the face |
| `insert-hero` (`insertHero`) | `theme, headline, hero{emoji\|src\|blob, entry, size=500}, caption` | A scene: headline y 545, hero y 1000 (46–60 % width), caption 1460 |
| `insert-number` (`insertNumber`) | `theme='light', headline, number{value,unit}, pill, selection, bar, caption` | A number roll 106 px + pill/selection/progress |
| `insert-media` (`insertMedia`) | `theme='navy', headline, cards[], screenshot, connector, chip, caption` | A glass/frost cards or tilted screenshot (no device frame) |
| `statement` | `theme, headline{text, pills}, caption` | headline centred y 900 + inline pill wipe |
| `cta` | `theme='lavender', name, handle` | A bookmark ending held to the end |

### Verification (demo)
Demo = 9 scenes / 30 s: head → insert-hero → head-side → insert-number → head (upper zone) → insert-media (curtain) → head-side → statement → cta (7 distinct layouts, head-type 4/9 split over two ids, no repeats back-to-back; themes footage/dark/footage/light/footage/curtain/footage/dark/lavender; transitions blur-drift/whip/lum alternating). `lint` 0 errors (2 track-density warnings, same as the A demo). Snapshots of every scene's final state compared side by side with the A demo (6.5 s, 14 s) and A refs (Dej 3.0 s, Der0 20.5 s, DeV 11 s): headline tier y ≈ 545 and size/weight identical (same RSA code), caption tier 1460, insert hero 500 px ≈ Dej's 520 px (was 320 — too small, fixed); head headlines sit in y 1262–1418 (lower) / 312–468 (upper), clear of the face box.
Known gaps: footage is the labelled slot until a real head.mp4 is passed; placeholder 3D objects are emoji (real runs use generated PNGs); demo silent (A policy = voice only).

## Technique pack "head-umar" (optional, any style) · `assets/techniques/head-umar.{css,js}` → global `RSX`

The talking-head editorial techniques from the creator's earlier reels (teardowns `style-b/Dd1b9kEA-KL.md`, `Dd3Uz4Mgbn-.md`), kept as opt-in tools — **not** part of Style D. Depends on RS + RSB (if RSB is missing, `RSX.available === false` and nothing is defined beyond that flag). Assembler always copies `assets/techniques/*` to `composition/lib/techniques/` and loads `head-umar.css/js` after the style packs; if a scene calls `RSX.` and the style lacks pack b, b is added. All CSS is scoped to `.rsx-*`, so loading it is inert. Build after `await RSX.ready()` (glyph metrics). Lint-checked with a 3-technique test scene (lens + jump zoom, chest-band stat morph, karaoke caption) over a footage slot: 0 errors.
| Builder | What | Ref |
|---|---|---|
| `caption` | one-line karaoke (grey → colour 0.21 s, phrase swap in 1 frame; themes head/paper/dark/light) | Dd1b9kEA-KL §4 |
| `band` | chest-band host y 880–1460 | §1 |
| `morphIn` · `stat` · `widget` · `gauge` · `implode` | dot → icon → widget morph, white-glow cards, green checks, squash/re-inflate −8°, 6-frame implode | Dd1b9kEA-KL §5 |
| `ctaPill` | avatar → pill → name types → blue press → dark chip (RSB.ctaFollow, identity from props) | §5 |
| `page` | paper (warm radial + embossed grid + lens pass), light, dark (grain + masked 54 px grid) | Dd3Uz4Mgbn- §2 |
| `ghostNumeral` · `sectionNumbers` · `heroWord` · `window` · `checks` · `label` | giant pale 01/02/03, bold condensed 1 2 3 with motion blur, thin condensed hero word between two lines, speaker grid-cell window, checks list, typed label pill | Dd3Uz4Mgbn-, Dd1b9kEA-KL hook |
| `headBase` · `lens` · `zoomAbout` / `jumpZoom` · `pullout` | lens-edge blur footage, 2.4× jump zoom, full-frame → phone pull-out | both §6 |
| `tx.cut` · `tx.glitch` · `tx.blank` | hard cut, 6-frame pixel glitch (RSB datamosh), blank beat | Dd3Uz4Mgbn- §6 |
| `muffle` | voice-muffle cue (−11 dB + low-pass) recorded to `RSX.cues` / `data-rsx-muffle` for the director/mixer (scripts/mix.py does not read it yet) | Dd3Uz4Mgbn- §8 |
