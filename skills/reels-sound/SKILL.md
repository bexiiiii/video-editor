---
name: reels-sound
description: Worker for reels-studio. Produces the voice (TTS, optional client voice clone), music bed, sound effects and the loudness-mastered mix (audio/mix.wav, −14 LUFS) for a reel according to the style audio policy. Use only when the reels-studio orchestrator dispatches audio work.
---

# reels-sound — audio worker

`$STUDIO` = sibling `reels-studio` skill dir. Read `$STUDIO/references/audio-policy.md` and `providers.md`.

- If `brief.providers.elevenlabs_connector.allowed` and `audio/voice.wav` already exists (the orchestrator generated it through the connector), skip TTS and only build timings/mix.
- **TTS job** (faceless): `$STUDIO/scripts/run providers/tts.py --text input/script.txt --lang <lang> --voice <brief.voice> [--clone-from input/voice_sample.wav] --out audio/voice.wav --transcript audio/transcript.json`. Clone only if `brief.voice.source == "tts_clone"` and the client agreed.
- **Mix job** (after the plan exists): music per policy → `$STUDIO/scripts/run providers/music.py --dur <plan.duration - music.start> --mood <mood> --bpm <bpm> --out audio/music.wav` (skip for style A); then `$STUDIO/scripts/run mix.py --work work/<slug>` → `audio/mix.wav`.
- Verify: integrated loudness −14 ±1 LUFS, TP ≤ −1 dBTP, voice intelligible over music (music ≥ 10 dB below voice in speech).
- Write `audio/sound_result.json` `{ "ok": true, "providers": {...}, "lufs": …, "warnings": [] }`.
