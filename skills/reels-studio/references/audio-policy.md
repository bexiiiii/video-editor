# Audio policy

Two profiles, recorded in `brief.audio_profile`. **Default: `energetic` for every style (A–E).**
Client feedback that made this the default: "music barely audible, no dynamics, no sound effects,
voice not cleaned / then suppressed". A reel is watched on a phone speaker — a −35 LUFS sub-bass bed
and silence between words read as "no sound design".

| | `energetic` (default, all styles) | `reference` (only when the client asks for the purist look) |
|---|---|---|
| Voice | king: cleaned (footage) or TTS, stem −16 LUFS speech-gated, master −14 LUFS integrated / ≤ −1 dBTP; never attenuated by music | same |
| Music | real track from the internet search (or client track) under the **whole** piece; 9–12 dB below the voice under speech (speech-gated LUFS), rising to 4–6 dB below it in pauses (150 ms attack / 400 ms release); HP 60 Hz + mild presence so it reads on phones; never sub-bass-only | the per-style table below |
| SFX | auto-cued by `sfx_plan.py` + director cues: whoosh on every transition, pop on hero/object entrances, tap on UI, tick on counters, riser into CTA/punchline, soft impact on statements; ≥ 0.6 s apart, ≤ 1 per 1.5 s; 6–10 dB below voice peaks | the per-style table below |
| Credits | `CREDITS.txt` — CC BY tracks need the CAPTION line in the post | same |

How to choose: ask only if the client mentions the reference look ("как в референсе, без музыки",
"чисто голос"). Otherwise write `"audio_profile": "energetic"` and say in one line which track was
found (title · artist · licence) — offer the other 2 candidates from `audio/music_candidates.json`.

## Pipeline (sound worker)
1. Footage → `cleanup.py` always (editor step 1). It measures speech level + 2–4 kHz presence
   before/after, backs off the denoiser when the voice loses > 1.5 dB or > 3 dB presence, then
   de-esses, compresses 2.5:1 and normalises to −16 LUFS speech-gated.
2. `music.py --work … --dur <duration − start>`: `input/music.*` → internet search
   (`music_search.py`: Openverse, Jamendo with key) → ElevenLabs Music → Lyria → local generator.
3. `sfx_plan.py --work …` (energetic) → `scenes[].sfx`.
4. `mix.py --work …` — fails (exit 3) when the voice-to-music gap is outside 7–16 dB or the voice in
   the master is > 2 dB off −14 LUFS. Writes `audio/mix_report.json`, `audio/music_bed.wav`.
5. `qa_audio.py --work …` (also called from qa.py).

## `reference` profile — the measured reference videos per style

| | Style A "3D Keyword" | Style B "iOS Keynote" | Style C "Keynote 3D" | Style D "Talking Head × 3D Keyword" | Style E "Data News" |
|---|---|---|---|---|---|
| Voice | dry, mono-compatible, −14 LUFS, LRA ≈ 1.7, gaps 0.3–0.5 s | dry, dominant, −14 LUFS | dry, dominant, gaps 0.3–0.5 s | speaker's footage voice: cleanup.py, gaps 0.3–0.5 s | dry, ≈130 wpm (Kazakh), gaps 0.3–0.5 s |
| Music | none | low beat 99–117 BPM ~11 dB under voice, only under graphics (after the hook) | as B, off under hook/CTA footage | none | low pad under the whole piece, ≈15 dB under voice |
| SFX | none | UI clicks/taps, ticks on counters, boom on portals, notification blips | sparse UI SFX, one whoosh per whip (at − 0.12), boom on portals | none | none |
| Master | −14 LUFS, −1 dBTP | same; duck music under voice | same; whoosh peaks ≈ 6 dB below voice peaks | same | same |

Even in `reference`, music that is present must pass the mix.py gap check (7–16 dB) and be HP-filtered —
a bed nobody can hear on a phone is a bug, not a style.

Generation details: `providers.md`. SFX kit: `assets/sfx/` (CC0, synthesised; `sfx_kit.py`).
