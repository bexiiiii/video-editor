# Audio policy per style

| | Style A "3D Keyword" | Style B "iOS Keynote" |
|---|---|---|
| Voice | dry, mono-compatible, −14 LUFS, LRA ≈ 1.7, gaps trimmed to 0.3–0.5 s | dry, dominant, −14 LUFS |
| Music | **none** | quiet low beat / sub-bass bed 99–117 BPM, ~11 dB under voice, **only under graphics** (starts after the hook, e.g. 5.0 s); may drop out for a section |
| SFX | **none** (no whooshes, no pops) | soft UI clicks/taps on interactions, ticks on counters, sub-boom on portal transitions, notification blip on banners; nothing on plain text reveals |
| Talking-head footage | denoise + light compression | same; muffle voice −11 dB with low-pass when the script says "on mute" (optional gag) |
| Master | two-pass loudnorm I=−14, TP=−1 | same; sidechain duck music under voice |

Generation (see providers.md): music via ElevenLabs Music → Lyria → `music_local.py` (`--mood soft-subbass`). SFX from the bundled kit `assets/sfx/`; generate custom ones only when the plan needs a sound the kit lacks.
