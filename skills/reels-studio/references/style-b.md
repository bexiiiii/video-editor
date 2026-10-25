# Style B — "iOS Keynote" (Umar)

> Teardowns with frame-level numbers: `teardowns/style-b/`. Shared rules:

## Shared truths (both systems)

1. **Text never exits on its own.** It leaves only with the scene. Words land in **pre-computed final positions** — lines never re-centre or reflow as words arrive.
2. **Per-word blur-in** synced to speech (blur 10–16px→0, small y/x offset, 140–400ms, expo/power3.out).
3. **Never pure #000 / #FFF.** Tinted neutrals + barely visible grid (dots or lines).
4. **Transitions sit in breath pauses**, centred on the next sentence's first word.
5. Voice mastered to **−14 LUFS**, dry, gaps trimmed to 0.3–0.5s, ~131–175 wpm.
6. One hero visual per scene, centred column, static camera on graphics.
7. Ending is abrupt (loops): bookmark "сохрани" (A) or follow-button tap (B).

## Style B spec

**Chrome (always on):** top-left 2-line breadcrumb at x=150, ~28px grey (series semibold / topic regular, e.g. "Ssenariy / Open Loop"). Top-right iOS page dots: 8px on 22px pitch, right edge x=930; active dot stretches to 24×8 `#007AFF` pill = chapter progress (4–8 dots).

**Themes** (flip every section)
- Light: vertical gradient `#F7F7F7/#F9F9F9 → #EBEBED/#ECECEE` + 130px grid of 2px `#E6E6E8` lines aligned to content column (x 150–930).
- Dark: `#1A1A1C` or `#171719→#121214` (variant: lighter toward bottom `#1A1A1C→#303033`, light wedge, fine grain) + grid.
- Blue takeover ("masalan / for example"): `#1B88FB→#0F539A`, faint concentric rings ~161px; frosted-glass tiles only on blue.
- Older editorial variant: warm radial `#F4F2F0→#DDDAD7`, embossed 3-col grid, giant pale numerals 01/02/03 (`#C2C2C2`, ~1150px).

**Typography** — SF Pro Display (fallback Inter Display)
- Kicker: 50–52px Light 300, `#7B7B7E` / `#7D7D7F` (dark `#9A9A9D`, blue white@72%).
- Headline: 108px Bold, `#0B0B0B` or white, tracking −0.02em, **always one line**, shrinks (to 96) to fit ≤760–790px.
- Secondary bold 60px. Card title 36 SemiBold. Card quote 48/70 left-aligned.
- Centred stack, column x 145–935, centred around y≈835.
- Talking-head captions (older): weight 500, tracking −0.05em, one centred line ≤26–32 chars, 1–4 words, chest band y 880–1460.

**Text motion**
- Word: `blur 10–12→0, opacity 0.5→1, x +22–40→0`, 120–200ms (3–5 frames), power3/expo.out, on spoken onset (0–80ms).
- Talking-head captions: words pre-placed, grey→full colour over 180–250ms; phrase swap in 1 frame, no exit.
- Previous content dims to ~50% when focus moves on. Literal words (= subtitles), not paraphrase.
- Components arrive ~0.25s **before** their headline word.

**Components** (≈15, Apple system colours only: `#007AFF #34C759 #FF9500/#FF9F0A #FF3B30 #FFCC00`; imagery = Apple 3D emoji)
- Card light: `#FBFBFD/#FCFCFC`, radius 36–40, 1px rgba(0,0,0,.08), soft shadow ~7% below. Dark: `#29292C/#2C2C2E`, radius 44, 1px inner highlight, emoji circle, linear progress bar filling over the section.
- Older: off-white `#EEE/#E9E9ED` squircles with **white glow** instead of shadow; morphs dot→icon→widget.
- Capsules/badges (red "Hammasi aytildi", green ✓, "N-qadam" steps), audio-player pill with filling bar, Open-Loop ring stopping at 80%, cursor with question, countdown timer, notification banner, iOS text-selection highlight (blue 25% box sweeps L→R in 5 frames + handles), segmented control, rolling counter with motion blur, strike-through correction, skeleton placeholders filling in, calendar grid filling by day, typing "•••", select→dim others→✓ badge after 0.8s, 6×5 colour grid filling by column.
- Entry: fade + rise + blur, 0.3–0.4s.
- Proof: real screen recordings / view counts / IG profile in iPhone mockup (deep-purple titanium frame); white glove cursor taps.

**Transitions**
- Scene dissolve 0.5–0.7s: old scales to 0.96–0.975 + slight blur + fades (over near-black), new fades in.
- Into/out of talking head: **portal** (travelling light orb grows to white-out + sub-bass boom), **pixel/datamosh glitch** 6–9 frames, RGB ghost glitch into loop.
- Older: hard cuts, 2.4× jump zoom, full-frame→phone pull-out.

**Talking head:** strong lens edge blur, overlays in chest band, uppercase white title sticker + 🍿 on hook.

**Audio:** dry VO ~−14/−16 dBFS; quiet sub-bass/low beat bed ~99–117 BPM, ~11dB under voice, only under graphics (not under hook); soft UI clicks/ticks; sub-boom on portal; voice muffled −11dB when "on mute" is mentioned.

**CTA:** B&W avatar tile pops → unrolls to pill → name types → blue `#227DE5` "Obuna bo'ling" pressed → dark `#2B2B2B` chip; or fake IG profile card with ticking followers + follow tap; or "Saqlash"→"Saqlandi" pill. Abrupt end → loop.

**Pitfalls:** bold hero word where thin is used, default tracking, black drop shadows on dark, flat bg without grid/grain, captions that bounce/re-centre, grid/numerals too visible, music under the hook.
