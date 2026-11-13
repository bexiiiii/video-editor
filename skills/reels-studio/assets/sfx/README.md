# Bundled SFX kit — CC0 1.0 (public domain)

All 21 sounds here are synthesised from scratch (oscillators + filtered noise) by
`scripts/sfx_kit.py`; no recordings or third-party samples are involved. They are dedicated to
the public domain under CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/): use them
for anything, commercial included, without attribution.

Format: 48 kHz, mono, 16-bit PCM WAV, peak-normalised per sound (UI ticks quieter than impacts).

| name | length | use |
|---|---|---|
| click, tick, tap | 0.04–0.09 s | UI taps, cursor clicks, counters |
| pop | 0.18 s | element / sticker appears |
| whoosh_short, whip | 0.2–0.32 s | scene change, whip-pan |
| swoosh_up, swoosh_down | 0.34 s | element flies in / out |
| boom_sub | 1.1 s | portal / big reveal |
| bass_hit | 1.0 s | punchline, logo hit |
| glitch | 0.32 s | glitch transition |
| shutter | 0.25 s | screenshot / photo |
| chime, notification, success | 0.8–1.1 s | message, done, unlocked |
| typing_loop | exactly 1.0 s, seamless | typing text (loop it) |
| riser_1s | 1.0 s | build-up into a hit (place so it ends on the hit) |
| whoosh_long, whoosh_air | 0.45–0.55 s | default transition whooshes (sfx_plan.py alternates them) |
| impact_soft | 0.6 s | statement / punchline hit with a 350 Hz body (audible on phones, unlike bass_hit) |
| pop_bright | 0.15 s | hero / object entrance |

Regenerate (deterministic — identical bytes each run):
```bash
scripts/run sfx_kit.py                 # all
scripts/run sfx_kit.py --only pop,glitch
```
`scripts/sfx_plan.py` cues these automatically (energetic profile). Optional CC0 Freesound
replacements: `sfx_plan.py --freesound` (needs FREESOUND_API_KEY) → `work/<slug>/assets/sfx/`.
Custom one-off sounds (e.g. ElevenLabs Sound Effects) go in `work/<slug>/assets/sfx/<name>.wav`;
`mix.py` looks there before this folder.
