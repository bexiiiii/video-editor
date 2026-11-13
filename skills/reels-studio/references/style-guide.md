# Reference style guide — 10 reels, 2 design systems

Source: 10 Instagram reels (2 of 12 links need login, not analysed). Per-video forensic reports with
frame strips, sampled colours and CSS/GSAP specs: `an/<id>/style.md`. Word-timed transcripts: `an/<id>/transcript.json`.
Font names are closest-match guesses; px sizes derived from glyph heights (±5%). All values at 1080×1920.

| System | Creator | Videos | Mode |
|---|---|---|---|
| **A · "3D Keyword"** | Maksim Zaytsev (RU, AI/tech) | DejCkBdNC6h, DeVzimJCYVp, Der0UBDNBmZ, DeyJKx9t_aA | faceless VO + 3D motion |
| **B · "iOS Keynote"** | Umar Jamoldinov (UZ, personal brand) | DeZREMAtvBf, De1roE4t7Lf, DeRXnpgtYe6, DelZA2dtAE6 (new) · Dd1b9kEA-KL, Dd3Uz4Mgbn- (older) | faceless VO + UI motion, talking-head hook/CTA, or talking head + overlays |

---

## Shared truths (both systems)

1. **Text never exits on its own.** It leaves only with the scene. Words land in **pre-computed final positions** — lines never re-centre or reflow as words arrive.
2. **Per-word blur-in** synced to speech (blur 10–16px→0, small y/x offset, 140–400ms, expo/power3.out).
3. **Never pure #000 / #FFF.** Tinted neutrals + barely visible grid (dots or lines).
4. **Transitions sit in breath pauses**, centred on the next sentence's first word.
5. Voice mastered to **−14 LUFS**, dry, gaps trimmed to 0.3–0.5s, ~131–175 wpm.
6. One hero visual per scene, centred column, static camera on graphics.
7. Ending is abrupt (loops): bookmark "сохрани" (A) or follow-button tap (B).

---

## System A — "3D Keyword" (Zaytsev)

**Rhythm:** new scene every 3.4–4.2s; new element every 0.8–1s. 14–26 scenes per video.

**Backgrounds**
- Base: dark `#0B0D0D` ↔ light `#FBFDFD`, alternating. Dot grid 3px dots: dark 36px pitch `#2D2F2F`, light 24px pitch `#DADDDD`.
- Accent bgs (hook / payoff): red pleated curtain + gold light leak; deep-space purple + stars; navy `#131A43` / green `#052F21` / maroon with diagonal light ray; teal/emerald glow from bottom; orange `#C84A00` top-right glow on black; lavender radial.

**Typography** — Google Sans Flex (fallback Onest)
- Headline 72–78px (64 if long), weight 500–700, line-height 1.06, ≤2 lines, ≤22 chars/line, 2–4 words.
- Hero numbers 104–108px. Grey caption 40–44px Regular: `#767878` on dark, `#686B6B` on light.
- **lowercase** sentence case (tutorial steps may be imperative Sentence case: "Открой настройки").
- No boxes, outlines, shadows on text (exception: soft dark halo over photos).
- Layout 3 tiers: headline y≈19–30% · visual centre · caption y≈74–80%. Headline drops to bottom when visual is tall.

**Text motion**
- Headline word: `opacity 0→1, filter blur(12–16px)→0, y +20–25→0`, 0.30–0.40s, expo.out / power3.out, stagger 80–150ms; starts 0.1–0.15s after the spoken word.
- Labels/code: typewriter ~24 chars/s, each char blurs in, anchored (no reflow).
- **Keywords, not subtitles.** Headline = summary; caption = second fragment of the sentence.

**Objects**
- One glossy **inflated 3D** hero object per scene (3D app/brand icons, Fluent-style 3D emoji, cartoon 3D).
- Entries: pop with back.out overshoot (stagger 0.10–0.12s), rise from below, side-slide with motion blur, drop-and-stack. Brand icons pop exactly on their spoken name.
- UI/glass cards: slight 3D tilt, radius 40–56, 1–3px bright rim + inner glow.
- Real screenshots: no device frame or iPhone mockup, brightness-matched bg, slight tilt, red/outline highlight boxes, magnifier lens.
- Devices: slot-machine number rolls, keyword pill wipes, iOS text-selection highlight with blue handles, blue chips, dashed flow connectors, gradient progress bar, particle globe.

**Transitions** (no hard cuts / wipes / flashes, except one hook hard cut)
- *Blur-drift*: old scene drifts + blurs 0→25px, bg cross-fades, new arrives blurred; 0.28s (14–27 frames).
- *Whip*: ~150ms out with ease-in + directional motion blur, then 400ms expo settle from ~270px. Vertical or horizontal per video.
- *Luminance crossfade* 250ms dark↔light, often carrying one shared element across.
- Continuous camera pan only for flow trees.

**Audio:** the reference reels are voice only (mono, −14.1 LUFS, LRA ~1.7, no music, no SFX). That is the `reference` audio profile, used only when the client asks for the purist look. The default `energetic` profile adds an audible music bed and SFX (`audio-policy.md`).

**Ending:** 3D blue bookmark + "сохрани…", held 2.5–5s, no end card.

**Pitfalls:** pure bg colours, bold/uppercase, adding music/whooshes, slow eased fades without blur, flat icons, raw screenshots, literal subtitles, centred typewriter that shifts.

---

## System B — "iOS Keynote" (Umar)

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

---

## Implications for the multi-agent skill

- Two **style packs** (A, B) as token files + component libraries; style chosen per brief.
- Three **edit modes**: faceless VO+motion · talking-head hook/CTA + motion body · talking head + overlays.
- Pipeline needs: word-level ASR **with explicit language** (Uzbek was misdetected as `az`), keyword extraction (A) vs literal captions (B), scene planner at ~4s/scene snapped to speech pauses, image gen for 3D hero objects (A) and emoji-style icons, component builder, audio policy per pack (A = voice only; B = bed + clicks + portal boom), render + QA against the pitfalls lists.
