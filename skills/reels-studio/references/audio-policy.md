# Audio policy per style

| | Style A "3D Keyword" | Style B "iOS Keynote" | Style C "Keynote 3D" |
|---|---|---|---|
| Voice | dry, mono-compatible, −14 LUFS, LRA ≈ 1.7, gaps trimmed to 0.3–0.5 s | dry, dominant, −14 LUFS | dry, dominant, −14 LUFS, gaps 0.3–0.5 s |
| Music | **none** | quiet low beat / sub-bass bed 99–117 BPM, ~11 dB under voice, **only under graphics** (starts after the hook, e.g. 5.0 s); may drop out for a section | B's soft sub-bass bed (`--mood soft-subbass`, 99–117 BPM) ~11 dB under voice, **only under graphics** — off under hook/CTA footage; may drop out on the `statement` breath scene |
| SFX | **none** (no whooshes, no pops) | soft UI clicks/taps on interactions, ticks on counters, sub-boom on portal transitions, notification blip on banners; nothing on plain text reveals | sparse UI SFX (tap on cursor taps, tick on counter rolls, blip on notifications — max ~1 per scene); **exactly one `whoosh_short` per whip**, at whip `at` − 0.12; sub-boom on portals at `at` − 0.15; nothing on dissolves or text reveals |
| Talking-head footage | denoise + light compression | same; muffle voice −11 dB with low-pass when the script says "on mute" (optional gag) | same as B |
| Master | two-pass loudnorm I=−14, TP=−1 | same; sidechain duck music under voice | same as B; whoosh peaks ≈ 6 dB below voice peaks |

Generation (see providers.md): music via ElevenLabs Music → Lyria → `music_local.py` (`--mood soft-subbass`). SFX from the bundled kit `assets/sfx/`; generate custom ones only when the plan needs a sound the kit lacks.
