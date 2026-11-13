---
name: reels-sound
description: Worker for reels-studio. Produces the voice (TTS, optional client voice clone), music bed (client track or internet search with licences), sound effects and the loudness-mastered mix (audio/mix.wav, −14 LUFS) for a reel according to the audio profile. Use only when the reels-studio orchestrator dispatches audio work.
---

# reels-sound — audio worker

`$STUDIO` = sibling `reels-studio` skill dir. Read `$STUDIO/references/audio-policy.md` and `providers.md`.
Profile = `brief.audio_profile` (default `energetic`: audible music + SFX for every style; `reference` = purist per-style table).

- If `brief.providers.elevenlabs_connector.allowed` and `audio/voice.wav` already exists (the orchestrator generated it through the connector), skip TTS and only build timings/mix.
- **TTS job** (faceless): `$STUDIO/scripts/run providers/tts.py --text input/script.txt --lang <lang> --voice <brief.voice> [--clone-from input/voice_sample.wav] --out audio/voice.wav --transcript audio/transcript.json`. Clone only if `brief.voice.source == "tts_clone"` and the client agreed.
- **Mix job** (after the plan exists):
  1. Music (skip only when profile `reference` says none): `$STUDIO/scripts/run providers/music.py --work work/<slug> --dur <plan.duration - music.start> --mood <mood> --bpm <bpm> --out audio/music.wav` — chain: `input/music.*` → internet search (Openverse/Jamendo, CC0/CC BY, ranked) → ElevenLabs → Lyria → local. Report the chosen track and the other 2 from `audio/music_candidates.json` (`music_search.py --work … --pick N` switches).
  2. SFX: `$STUDIO/scripts/run sfx_plan.py --work work/<slug>` (energetic; keeps director cues).
  3. `$STUDIO/scripts/run mix.py --work work/<slug>` → `audio/mix.wav`. Exit 3 = level check failed (gap / voice level) — read the printed numbers, fix (e.g. `--gap-speech 11`), never ship it.
  4. `$STUDIO/scripts/run qa_audio.py --work work/<slug>` — all checks pass.
- Verify: integrated −14 ±1 LUFS, TP ≤ −1 dBTP, voice −14 ±2 LUFS speech-gated in the master, music 9–12 dB below the voice under speech and audible in pauses (≥ −30 LUFS short-term), SFX present (energetic).
- Write `audio/sound_result.json` `{ "ok": true, "providers": {...}, "lufs": …, "music": {"title", "artist", "licence", "attribution_required"}, "warnings": [] }`; CC BY → remind the orchestrator of the CAPTION line in `CREDITS.txt`.
