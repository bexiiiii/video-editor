# Audio policy per style

| | Style A "3D Keyword" | Style B "iOS Keynote" | Style C "Keynote 3D" | Style D "Talking Head × 3D Keyword" |
|---|---|---|---|---|
| Voice | dry, mono-compatible, −14 LUFS, LRA ≈ 1.7, gaps trimmed to 0.3–0.5 s | dry, dominant, −14 LUFS | dry, dominant, −14 LUFS, gaps 0.3–0.5 s | speaker's own footage voice: denoise + light compression, dry, −14 LUFS, gaps trimmed 0.3–0.5 s (as A) |
| Music | **none** | quiet low beat / sub-bass bed 99–117 BPM, ~11 dB under voice, **only under graphics** (starts after the hook, e.g. 5.0 s); may drop out for a section | B's soft sub-bass bed (`--mood soft-subbass`, 99–117 BPM) ~11 dB under voice, **only under graphics** — off under hook/CTA footage; may drop out on the `statement` breath scene | **none** (= A) |
| SFX | **none** (no whooshes, no pops) | soft UI clicks/taps on interactions, ticks on counters, sub-boom on portal transitions, notification blip on banners; nothing on plain text reveals | sparse UI SFX (tap on cursor taps, tick on counter rolls, blip on notifications — max ~1 per scene); **exactly one `whoosh_short` per whip**, at whip `at` − 0.12; sub-boom on portals at `at` − 0.15; nothing on dissolves or text reveals | **none** (= A) — no whooshes on blur-drift/whip |
| Talking-head footage | denoise + light compression | same; muffle voice −11 dB with low-pass when the script says "on mute" (optional gag) | same as B | the base layer: denoise + light compression; no muffle gag by default (the RSX technique pack offers `RSX.muffle` as an opt-in cue) |
| Master | two-pass loudnorm I=−14, TP=−1 | same; sidechain duck music under voice | same as B; whoosh peaks ≈ 6 dB below voice peaks | two-pass loudnorm I=−14, TP=−1 (= A) |

Generation (see providers.md): music via ElevenLabs Music → Lyria → `music_local.py` (`--mood soft-subbass`). SFX from the bundled kit `assets/sfx/`; generate custom ones only when the plan needs a sound the kit lacks.
