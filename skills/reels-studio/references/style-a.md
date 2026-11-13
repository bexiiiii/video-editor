# Style A — "3D Keyword" (Zaytsev)

> Teardowns with frame-level numbers: `teardowns/style-a/`. Shared rules:

## Shared truths (both systems)

1. **Text never exits on its own.** It leaves only with the scene. Words land in **pre-computed final positions** — lines never re-centre or reflow as words arrive.
2. **Per-word blur-in** synced to speech (blur 10–16px→0, small y/x offset, 140–400ms, expo/power3.out).
3. **Never pure #000 / #FFF.** Tinted neutrals + barely visible grid (dots or lines).
4. **Transitions sit in breath pauses**, centred on the next sentence's first word.
5. Voice mastered to **−14 LUFS**, dry, gaps trimmed to 0.3–0.5s, ~131–175 wpm.
6. One hero visual per scene, centred column, static camera on graphics.
7. Ending is abrupt (loops): bookmark "сохрани" (A) or follow-button tap (B).

## Style A spec

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
