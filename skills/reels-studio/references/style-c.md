# Style C — "Keynote 3D" (A × B fusion)

> A deliberate fusion: **B's information architecture** (persistent chrome, kicker → headline hierarchy, iOS
> components, Apple system colours, literal word-synced captions over talking head) + **A's cinematic energy**
> (#0B0D0D / #FBFDFD with dot grid and A's accent glows, glossy 3D hero objects, keyword headlines, glass with a
> bright rim, whip with motion blur). Pack: `assets/style-c/` (needs A and B packs loaded first). Shared rules:

## Shared truths (all systems)

1. **Text never exits on its own.** It leaves only with the scene. Words land in **pre-computed final positions** — lines never re-centre or reflow as words arrive.
2. **Per-word blur-in** synced to speech (blur 10–16px→0, small y/x offset, 140–400ms, expo/power3.out).
3. **Never pure #000 / #FFF.** Tinted neutrals + barely visible grid (dots or lines).
4. **Transitions sit in breath pauses**, centred on the next sentence's first word.
5. Voice mastered to **−14 LUFS**, dry, gaps trimmed to 0.3–0.5s, ~131–175 wpm.
6. One hero visual per scene, centred column, static camera on graphics.
7. Ending is abrupt (loops): follow-pill press (C default) or bookmark "сохрани".

## Style C spec

**Rhythm:** new scene every 3.4–4.2 s; new element every 0.8–1 s. Chapters of 1–2 scenes; **scenes alternate
cinematic ↔ UI** (cinematic = A look: dark/glow, 3D hero, keyword headline · UI = B look: light or blue, one iOS
component, literal headline). Talking head (real footage) at the hook and the CTA, optional mid-video.

**Chrome (always on over motion, hidden over footage):** B breadcrumb top-left x=150 (series semibold / topic
regular, 24 px) + page dots right edge x=930, active dot = 24×8 `#007AFF` pill = chapter. C variant: on dark the
dots carry a soft blue glow. One dot per chapter (4–6). Step the chrome at every transition `at`.

**Themes**
| theme | plate | use |
|---|---|---|
| `dark` | `#0B0D0D` + 3 px dots 36 px `#2D2F2F` (A) | cinematic default |
| `dark` + glow `orange` / `teal` / `emerald` / `navy` / `violet` | A accent glow as an overlay — dot grid stays visible | hook payoff, chapter openers (≤ 3 accents per video) |
| `light` | `#FBFDFD` + 3 px dots 24 px `#DADDDD` (A) | UI default |
| `light` + glow `lavender` | top lavender radial | statement / breath |
| `blue` | B takeover `#1C86FD→#0D4C90` + white dot grid 16 % | "например / masalan" moments, glass rows |
Glass-on-dark (`.rsc-glass`): automatic on cinematic dark pages and on blue — every B card/row/notification/
segmented/player becomes white-6–8 % fill + A's 1.5 px lit rim (bright top-left) + inner glow, no shadow-as-border.

**Typography** — one family: **Inter 4 variable** (opsz → Inter Display at large sizes), already loaded by style-b.
Why: the only family in the stack that covers Russian, **Kazakh Cyrillic** (ә ғ қ ң ө ұ ү һ і) and **Uzbek Latin**
(oʻ gʻ, U+02BB) in all weights; Google Sans (A) lacks Kazakh letters, SF Pro (B) cannot be embedded. Sizes sit
between A (74) and B (108) with B's tight tracking.
| role | size / weight / tracking | colour dark · light |
|---|---|---|
| crumb | 24 / 600+400 / 0 | `#8E8E93` · `#7F7D81` |
| kicker | 46 / 300 / −0.01em, literal | `#9A9A9D` · `#7B7B7E` (blue: white 74 %) |
| keyword headline (cinematic) | 92 / 700 / −0.035em, lh 1.04, ≤ 2 lines, lowercase, shrink-to-fit 900 px | `#FBFDFD` · `#0B0D0D`, highlight = iOS blue `#0A84FF`/`#007AFF` |
| UI headline | 100 / 700 / −0.035em, **one line**, literal, shrink-to-fit (min 72) | same |
| statement | 124 / 700 / −0.045em, 2 lines | same |
| sub | 46 / 300 | as kicker |
| caption (cinematic) | 40 / 400, A grey, typewriter ~26 cps | `#8A8C8C` · `#686B6B` |
| hero number | 330–380 / 700 / −0.05em tabular, suffix 96 Light grey | ink |
| card title · note | 36 / 600 · 30 / 400 | `#FBFDFD` · `#9A9A9D` |
| talking-head caption | 62 / 500 / −0.05em (B), chest band y≈1398–1420 | white, grey→white per word |

**Text motion**
- Headline word (C): opacity 0→1, blur 14→0, y +22→0, 0.30 s power3.out — A's blur-rise at B's tempo; keyword
  headlines start 0.1–0.15 s after the spoken word, UI headlines on the onset.
- Kicker / sub: B word reveal (blur 11, x +22, 0.14 s). Caption: A typewriter with per-char blur.
- Components arrive ≈0.25 s **before** their headline word (B). Previous content may dim to 50 % (B) on UI pages.

**Layouts** (`RSC.layout.*`, layouts.md catalogue; block centred in the live area y 230–1575 → centre y≈902)
| id | C composition | scene kind |
|---|---|---|
| `stack` | kicker + UI headline + one component + caption | UI |
| `hero` | A three tiers: keyword headline centre y 440 · 3D hero (500–650 px) centre y 965 · caption y 1450 | cinematic |
| `visual-top` | 3D hero/visual first (≤ 55 %), keyword headline below (+90), caption (+40) | cinematic |
| `number` | kicker + B counter 330–380 px with vertical motion blur + sub + red capsule | UI |
| `media` | kicker + UI headline + iPhone (B, 460 px wide ≈ 945 tall) with real screen; cursor/overlays via `geo.toSlot()` | UI |
| `list` | kicker + headline + notification + 3–4 skeleton rows building down (glass on blue/dark) | UI |
| `compare` | keyword headline + two A glass cards (title, 3D object, A slot-roll stat, note), tilted ±4° | cinematic |
| `statement` | 2-line 124 px headline only (breath, ≤ 1 per 6 scenes) | cinematic |
| `head` | footage + B hook sticker + literal captions | head |
| `head-side` | footage + one component in the chest band y 900–1280 + captions y 1420 | head_overlay |
Rhythm everywhere: kicker→headline 34, headline→visual 90, visual→caption 74.

**Objects**
- One glossy 3D hero per cinematic scene (generated PNG, one art direction per video; Fluent-3D-style clay/glass),
  500–650 px, entering via A (pop back.out / rise with vertical motion blur / slide with horizontal blur / drop).
  C framing: accent glow disc behind (scene glow colour, 40 %), soft floor contact, finite idle bob (amp 10, 3.2 s).
- UI scenes: B components only, Apple system colours `#007AFF #34C759 #FF9500 #FF3B30 #FFCC00`; emoji only as
  small accents inside UI (notification icon, row icons, sticker).
- Glass cards (A `glass`): radius 48, 2.5 px rim, inner glow 22 px, tilt rx 2° / ry ±3–4°.

**Transitions** (`RSC.tx.*`, all centred on the next sentence onset)
| where | type | spec | clip window |
|---|---|---|---|
| between chapters | `whip` (dir per video: up/left) | A: old content ±320 px in 150 ms power2.in + directional SVG blur 0→26; new from ∓270 px, 400 ms expo.out, blur 18→0; bg cut (same theme) or 0.25 s fade | next ≥ at−0.25, prev ≤ at+0.15 |
| within a chapter | `dissolve` | B: old page scale .97 + blur 6 + fade 0.55 s over near-black; new fades from at+0.06, content un-blurs 10→0 | next ≥ at, prev ≤ at+0.6 |
| talking head ↔ motion | `portal` | B orb (C: blue bloom) travels, grows ×32, `#FBFDFD` flash swaps pages at +0.6, fades by +1.2 | next ≥ at, prev ≤ at+1.25 |
No hard cuts except an optional hook cut; no datamosh/glitch in C (too loud next to 3D).

**Audio:** B's soft sub-bass bed ~11 dB under voice, **only under graphics** (not under the hook/CTA footage);
sparse UI SFX (tap on cursor taps, tick on counters, blip on notifications — max ~1 per scene); **exactly one
whoosh per whip** (at at−0.12); sub-boom on portals. Nothing on plain text reveals. See `audio-policy.md`.

**Talking head:** real footage only (`edit/head.mp4`); B literal captions in the chest band, hook sticker allowed;
chrome hidden. Demos use the labelled neutral `RSC.footage` slot — never a drawn person.

**CTA:** `head-side` with `RSB.ctaFollow` (avatar = brand logo, name + handle from `brief.cta`, "Подписаться"
press → dark chip) or `RSB.igProfile`; abrupt end → loop.

**Pitfalls:** two cinematic (or two UI) scenes in a row; whip inside a chapter or dissolve between chapters;
B white cards on dark cinematic pages (use glass); 3D hero on UI scenes competing with the component; A lowercase
keyword on a UI headline (UI = literal words); more than one family/weight soup (Inter only); hero < 500 px;
emoji as hero; glow on every scene (≤ 3 accents); whoosh on dissolves; music under footage; chrome over footage.

**Implementation notes:** build after `await RSC.ready()`; pages = `RSC.page(host,{theme,glow,kind})` inside clips
whose windows follow `RSC.txWindow`; `RSC.audit(page)` returns the block bbox/centre/fill at the current seek time
(demo: all motion scenes centre 902–909, fill 0.46–0.90).
