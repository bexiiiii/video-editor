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
asr.py tts.py cleanup.py music.py music_local.py   thin CLI wrappers for providers/*.py
providers/common.py  .env, urllib HTTP + multipart, ffmpeg helpers, transcript building, env.json
providers/asr.py     ElevenLabs Scribe v2 -> OpenAI whisper-1 -> mlx-whisper -> faster-whisper
providers/tts.py     ElevenLabs v3 -> Gemini -> Yandex v3 -> Azure -> edge-tts (+ASR timing fallback)
providers/cleanup.py (ElevenLabs Isolator) -> DeepFilterNet 3 -> ffmpeg chain
providers/music.py   ElevenLabs Music -> Lyria (opt-in) -> music_local
providers/music_local.py  procedural beds: soft-subbass | upbeat | tense
sfx_kit.py           regenerates assets/sfx/*.wav (CC0)
mix.py               voice + ducked music + SFX -> audio/mix.wav, -14 LUFS / -1 dBTP
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
- **mix.py** gain-stages stems by loudness (voice −16 LUFS, music −24 LUFS + `music.gain_db`),
  ducks music by exactly `duck_db` under speech (RMS sidechain, 60 ms look-ahead, 40/350 ms
  attack/release), SFX bus at `audio.sfx_gain_db` (default −6) + per-cue `gain_db`, then limits
  and runs two-pass `loudnorm` in linear mode. The LRA target is relaxed to the measured LRA
  so loudnorm never falls back to dynamic mode (short reels with pauses measure LRA 8–13).
  Style A (music disabled, no SFX) is a voice-only master. Also writes `audio/sfx.wav`.
- SFX lookup: `work/<slug>/assets/sfx/<name>.wav` (custom one-offs) before the bundled kit;
  a cue may also give `"file": "path.wav"`. Unknown names are skipped with a warning.
- Env overrides: `ELEVENLABS_TTS_MODEL` (default `eleven_v3`), `ELEVENLABS_MUSIC_MODEL`
  (`music_v1`), `GEMINI_TTS_MODEL` (`gemini-2.5-flash-preview-tts`), `GEMINI_MUSIC_MODEL`
  (unset = Lyria disabled; its endpoint shape is unverified).
