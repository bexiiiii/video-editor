# reels-studio scripts

Deterministic helpers the agents call. Every script has `--help`, exits non-zero with a clear
`error:` line on real failure, never prints API key values, and records the provider it used in
`work/<slug>/env.json → used` (when an env.json exists 1–2 levels above the output).
Data formats: `../references/contracts.md`. Provider chains: `../references/providers.md`.

Run scripts with the skill's interpreter: `scripts/run <script> ...` (uses `~/.reels-studio/venv`
when present, else `python3`). API keys come from the environment or `./.env` in the cwd.

## Layout
```
doctor.py            environment check -> env.json
asr.py tts.py cleanup.py music.py music_local.py music_search.py broll.py   thin CLI wrappers for providers/*.py
providers/common.py  .env, urllib HTTP + multipart, ffmpeg helpers, transcript building, env.json
providers/asr.py     ElevenLabs Scribe v2 -> OpenAI whisper-1 -> mlx-whisper -> faster-whisper
providers/tts.py     ElevenLabs v3 -> Gemini -> Yandex v3 -> Azure -> edge-tts (+ASR timing fallback)
providers/cleanup.py (ElevenLabs Isolator) -> DeepFilterNet 3 (atten-lim ladder) -> ffmpeg afftdn ladder; guard + −16 LUFS speech-gated
providers/music.py   input/music.* -> music_search (Openverse/Jamendo) -> ElevenLabs Music -> Lyria (opt-in) -> music_local
providers/music_search.py  internet music search, licence filter, librosa ranking, downbeat fit, CREDITS.txt
providers/broll.py   scene B-roll: client clip -> screen capture (screen_capture.mjs, HyperFrames Chrome, Node 22 CDP) -> Pexels/Pixabay/Wikimedia -> slot
providers/audio_meter.py   BS.1770 meter: speech-gated / masked loudness, short-term curve, true peak
providers/music_local.py  procedural beds: soft-subbass | upbeat | tense
sfx_kit.py           regenerates assets/sfx/*.wav (CC0)
sfx_plan.py          auto SFX cues (transitions, entrances, UI, counters, riser, impact) -> scenes[].sfx
mix.py               voice-relative mix (music 9–12 dB under speech, 4–6 dB in pauses) + SFX -> audio/mix.wav, -14 LUFS / -1 dBTP
qa_audio.py          audio QA checks (gap, music in pauses, voice level, SFX, clipping); used by qa.py
captions.py          caption track planner (transcript -> 1–4-word phrases, word reveal at onset − 0.03 s); used by assemble.py/qa.py
lint_scenes.py       static "no sudden appearances" linter for scenes/*/index.html (run by assemble.py, warnings only)
```

## Usage
```bash
# 0. environment -> work/<slug>/env.json (always exit 0 unless ffmpeg/python missing)
scripts/run doctor.py --work work/my-reel            # add --json for machine output

# 1a. faceless: TTS + word timings (provider timings, else ASR with the known script)
scripts/run tts.py --text work/my-reel/input/script.txt --lang uz --voice auto --gender female \
    --out work/my-reel/audio/voice.wav --transcript work/my-reel/audio/transcript.json
#     --provider edge|azure|yandex|gemini|elevenlabs   force one provider (no fallback)
#     --clone-from input/take1.mov                      ElevenLabs instant clone (key required, else stock)
#     --asr-model small                                 local whisper size for the timing fallback

# 1b. footage: clean the voice, then transcribe (language is always forced)
scripts/run cleanup.py work/my-reel/input/take1.mov --out work/my-reel/audio/voice.wav [--isolator]
scripts/run asr.py work/my-reel/audio/voice.wav --lang kk --out work/my-reel/audio/transcript.json \
    [--text script.txt] [--provider faster-whisper --model large-v3] [--vad]

# 3c. music bed (exact length, faded) and SFX kit
scripts/run music.py --dur 41.2 --mood "soft-subbass, calm tech" --bpm 108 --out work/my-reel/audio/music.wav
scripts/run music_local.py --dur 20 --mood tense --seed 7 --out /tmp/bed.wav   # offline generator directly
scripts/run sfx_kit.py --list          # regenerate: scripts/run sfx_kit.py [--only click,pop]

# 4. mix & master (reads plan/scenes.json audio.music + scenes[].sfx)
scripts/run mix.py --work work/my-reel   # prints measured LUFS / dBTP
```

## Notes
- **Transcripts**: words / sentences / pauses (gaps ≥ 0.25 s) per contracts.md. With a known
  script, recognised words are replaced by the script tokens (spelling + punctuation kept) and
  timings are transferred by sequence alignment; unmatched tokens are interpolated.
- **edge-tts** returns word boundaries for ru/uz/kk, so no ASR pass is needed on the free path.
  Stock voices: ru-RU-SvetlanaNeural/DmitryNeural, uz-UZ-MadinaNeural/SardorNeural,
  kk-KZ-AigulNeural/DauletNeural (verified with `edge-tts --list-voices`).
- **faster-whisper** gets an ffmpeg-decoded float32 array (its PyAV decode fails on Python 3.14).
- **mix.py** normalises the voice to −16 LUFS speech-gated (as dual-mono in the stereo mix),
  high-passes the music at 60 Hz with a mild presence lift, and sets its level closed-loop
  relative to the voice: `gap_speech_db` (10) under speech, `gap_pause_db` (5) in pauses, with a
  150/400 ms attack/release envelope (200 ms look-ahead). SFX are peak-levelled 6–10 dB below the
  voice peaks (+ `audio.sfx_gain_db` + per-cue `gain_db`). Then limit + two-pass linear `loudnorm`.
  Writes `audio/mix_report.json`, `audio/music_bed.wav`, `audio/sfx.wav` (stems at final level);
  exit 3 when the gap leaves 7–16 dB or the voice in the master is > 2 dB off −14 LUFS.
- SFX lookup: `work/<slug>/assets/sfx/<name>.wav` (custom one-offs) before the bundled kit;
  a cue may also give `"file": "path.wav"`. Unknown names are skipped with a warning.
- Env overrides: `ELEVENLABS_TTS_MODEL` (default `eleven_v3`), `ELEVENLABS_MUSIC_MODEL`
  (`music_v1`), `GEMINI_TTS_MODEL` (`gemini-2.5-flash-preview-tts`), `GEMINI_MUSIC_MODEL`
  (unset = Lyria disabled; its endpoint shape is unverified).
