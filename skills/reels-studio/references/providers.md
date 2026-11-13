# Providers — every capability degrades gracefully

`scripts/doctor.py` detects keys/tools and writes `work/<slug>/env.json`; scripts pick the first available provider.
**Nothing is mandatory except ffmpeg, python3 ≥3.10, node ≥20.** ElevenLabs is optional everywhere.

**ElevenLabs connector (MCP).** If the connector is attached to the host and the client approved it (`connector-elevenlabs.md`), it goes first for TTS, ASR, voice design and images. The orchestrator calls it; scripts only post-process (`connector_words.py`, `image.py --cutout`). Otherwise use the chains below.

| Capability | Chain (first available wins) | Env / dependency |
|---|---|---|
| ASR + word timings | ElevenLabs Scribe v2 → OpenAI `whisper-1` (verbose_json, word granularity) → local faster-whisper `large-v3` (mlx-whisper on Apple Silicon) | `ELEVENLABS_API_KEY` · `OPENAI_API_KEY` · pip `faster-whisper` |
| Language | always forced from `brief.lang` (`ru`/`uz`/`kk`) — never auto-detect (uz is misdetected as az) | — |
| TTS | ElevenLabs v3/v4 with-timestamps → Gemini TTS → Yandex SpeechKit v3 → Azure Neural → `edge-tts` (free, no key) | `ELEVENLABS_API_KEY` · `GEMINI_API_KEY` · `YANDEX_API_KEY`+`YANDEX_FOLDER_ID` · `AZURE_SPEECH_KEY`+`AZURE_SPEECH_REGION` · pip `edge-tts` |
| TTS timings | provider timestamps if returned, else run ASR on the TTS audio with the known text | — |
| Voice clone | ElevenLabs Instant Voice Clone (only if client chose clone **and** key present); otherwise tell the user and use stock voice | `ELEVENLABS_API_KEY` |
| Voice cleanup | DeepFilterNet 3 (`--atten-lim` 15→10→6 dB) → ffmpeg `highpass 80, afftdn nr 12/nf −30` ladder; guard backs off when speech loses > 1.5 dB or > 3 dB 2–4 kHz presence; then de-esser, 2.5:1 comp, −16 LUFS speech-gated. ElevenLabs Voice Isolator only when footage is bad and key present | pip `deepfilternet` |
| Music bed | client track `input/music.*` → **internet search** `music_search.py` (Openverse, no key; Jamendo with `JAMENDO_CLIENT_ID`; CC0/CC BY only, librosa-ranked, top-3 → `audio/music_candidates.json`, attribution → `CREDITS.txt`) → ElevenLabs Music → Google Lyria → local generator `providers/music_local.py` | none (optional `JAMENDO_CLIENT_ID`) |
| SFX | auto-cued by `sfx_plan.py` from the bundled kit `assets/sfx/*.wav` (procedurally generated, CC0) → optional CC0 Freesound replacements (`--freesound`, `FREESOUND_API_KEY`) → ElevenLabs Sound Effects for custom one-offs | optional `FREESOUND_API_KEY` |
| Images | Codex built-in `image_gen` (agent copies from `$CODEX_HOME/generated_images/`) → OpenAI Images `gpt-image-2` (1024x1536 ok; no transparent bg → chroma-key cut-out; `gpt-image-1.5` for native transparency) → Gemini image → Microsoft Fluent Emoji 3D (MIT) / bundled icons | `OPENAI_API_KEY` · `GEMINI_API_KEY` |
| Mix & master | `mix.py`: BS.1770 speech-gated metering (`providers/audio_meter.py`), voice −16 LUFS, music closed-loop 9–12 dB under voice in speech / 4–6 dB in pauses (150/400 ms), SFX 6–10 dB under voice peaks → limit → two-pass `loudnorm I=-14:TP=-1` (linear); `qa_audio.py` re-checks the render | ffmpeg, numpy, scipy (librosa for music search) |
| Render | HyperFrames `hyperframes@0.8.154` (headless Chrome) | node, npx |

Policy:
- Never print or log key values. Read keys only from environment / `.env` in the project (gitignored).
- Record which provider produced each artefact in `env.json → used` so QA and the user can see it.
- When a better provider is missing, continue with the fallback and add a one-line note to the final report ("Uzbek TTS via edge-tts — set ELEVENLABS_API_KEY for higher quality").
