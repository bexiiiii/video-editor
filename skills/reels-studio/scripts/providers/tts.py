#!/usr/bin/env python3
"""Text-to-speech -> audio/voice.wav (48 kHz mono) + audio/transcript.json.

Chain (first available wins):
  1. ElevenLabs v3 /with-timestamps   (ELEVENLABS_API_KEY; char alignment -> word timings)
  2. Gemini TTS                       (GEMINI_API_KEY; model via GEMINI_TTS_MODEL)
  3. Yandex SpeechKit v3              (YANDEX_API_KEY + YANDEX_FOLDER_ID)
  4. Azure Neural TTS                 (AZURE_SPEECH_KEY + AZURE_SPEECH_REGION)
  5. edge-tts                         (free, no key; pip install edge-tts)

Providers that return no timings (or partial ones) are followed by ASR on the generated
audio with the known script (`asr.transcribe`). `--clone-from footage.wav` creates an
ElevenLabs Instant Voice Clone when the key exists; otherwise it warns and uses a stock voice.

Usage:
  tts.py --text script.txt --lang ru --voice auto --out audio/voice.wav --transcript audio/transcript.json
         [--gender female|male] [--provider auto|elevenlabs|gemini|yandex|azure|edge]
         [--clone-from input/take1.wav] [--asr-model large-v3]
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import re
import sys
import wave
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (LANGS, SAMPLE_RATE, ProviderError, align_script, build_transcript, die,  # noqa: E402
                    duration, has_keys, has_module, http, http_json, key, load_dotenv, log,
                    multipart, record_used, tmpdir, to_wav, write_json)

PROVIDERS = ("elevenlabs", "gemini", "yandex", "azure", "edge")
# Per-request character limits (conservative); longer scripts are split on sentences.
CHUNK_LIMIT = {"elevenlabs": 2500, "gemini": 3000, "yandex": 2000, "azure": 4000, "edge": 20000}

# Stock voices per provider / language / gender. Edge & Azure names verified with
# `edge-tts --list-voices` (2026-10). ElevenLabs premade voices are multilingual on v3.
VOICES = {
    "elevenlabs": {"female": "EXAVITQu4vr4xnSDxMaL", "male": "JBFqnCBsd6RMkjVDRZzb"},   # Sarah / George
    "gemini": {"female": "Kore", "male": "Charon"},
    "yandex": {"ru": {"female": "alena", "male": "filipp"},
               "uz": {"female": "nigora", "male": "nigora"},
               "kk": {"female": "saule", "male": "madi"}},
    "azure": {"ru": {"female": "ru-RU-SvetlanaNeural", "male": "ru-RU-DmitryNeural"},
              "uz": {"female": "uz-UZ-MadinaNeural", "male": "uz-UZ-SardorNeural"},
              "kk": {"female": "kk-KZ-AigulNeural", "male": "kk-KZ-DauletNeural"}},
}
VOICES["edge"] = VOICES["azure"]
LOCALE = {"ru": "ru-RU", "uz": "uz-UZ", "kk": "kk-KZ"}
# What an explicit --voice must look like to be valid for a provider.
VOICE_FORMAT = {"elevenlabs": r"^[A-Za-z0-9]{16,32}$", "gemini": r"^[A-Z][a-z]+$",
                "yandex": r"^[a-z_]+$", "azure": r"^[a-z]{2}-[A-Z]{2}-\w+Neural$"}
VOICE_FORMAT["edge"] = VOICE_FORMAT["azure"]


def available(name: str) -> bool:
    return {"elevenlabs": lambda: has_keys("ELEVENLABS_API_KEY"),
            "gemini": lambda: has_keys("GEMINI_API_KEY"),
            "yandex": lambda: has_keys("YANDEX_API_KEY", "YANDEX_FOLDER_ID"),
            "azure": lambda: has_keys("AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"),
            "edge": lambda: has_module("edge_tts")}[name]()


def pick_voice(provider: str, lang: str, voice: str, gender: str) -> str:
    """Explicit voice if it fits the provider's id format, else the stock voice."""
    if voice != "auto":
        if re.match(VOICE_FORMAT[provider], voice):
            return voice
        log(f"[tts] voice '{voice}' is not a {provider} voice id; using stock {gender} voice")
    table = VOICES[provider]
    return table[gender] if gender in table else table[lang][gender]


# --------------------------------------------------------------------------- text helpers
def clean_for_timing(text: str) -> str:
    """Script without ElevenLabs v3 audio tags like [whispers] — those are not spoken words."""
    return re.sub(r"\[[^\]]*\]", " ", text)


def chunks(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for sent in re.split(r"(?<=[.!?…])\s+", text):
        if cur and len(cur) + len(sent) + 1 > limit:
            parts.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    return parts + ([cur] if cur else [])


def char_alignment_to_words(al: dict) -> list[dict]:
    """ElevenLabs char-level alignment -> words (runs of non-space chars, tags removed)."""
    words, cur, s, e = [], "", 0.0, 0.0
    for ch, cs, ce in zip(al["characters"], al["character_start_times_seconds"],
                          al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                words.append({"w": cur, "s": s, "e": e})
            cur = ""
            continue
        if not cur:
            s = cs
        cur, e = cur + ch, ce
    if cur:
        words.append({"w": cur, "s": s, "e": e})
    return [w for w in words if not re.fullmatch(r"\[[^\]]*\]", w["w"])]


def write_pcm_wav(path: Path, pcm: bytes, sr: int) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm)
    return path


# --------------------------------------------------------------------------- providers
# Each synth function writes `dst` (any format ffmpeg reads) and returns words or None.
def _elevenlabs(text: str, lang: str, voice: str, dst: Path) -> list[dict] | None:
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"
           "?output_format=mp3_44100_128")
    data = http_json("POST", url, {"text": text, "model_id": os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_v3"),
                                   "language_code": lang},
                     headers={"xi-api-key": key("ELEVENLABS_API_KEY")})
    dst.write_bytes(base64.b64decode(data["audio_base64"]))
    al = data.get("alignment") or data.get("normalized_alignment")
    return char_alignment_to_words(al) if al and al.get("characters") else None


def _gemini(text: str, lang: str, voice: str, dst: Path) -> list[dict] | None:
    model = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
    payload = {"contents": [{"parts": [{"text": text}]}],
               "generationConfig": {"responseModalities": ["AUDIO"],
                                    "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    data = http_json("POST", f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                     payload, headers={"x-goog-api-key": key("GEMINI_API_KEY")})
    try:
        inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]
    except (KeyError, IndexError):
        raise ProviderError("Gemini returned no audio") from None
    rate = int(re.search(r"rate=(\d+)", inline.get("mimeType", "")).group(1)) if "rate=" in inline.get("mimeType", "") else 24000
    write_pcm_wav(dst, base64.b64decode(inline["data"]), rate)   # raw s16le PCM
    return None


def _yandex(text: str, lang: str, voice: str, dst: Path) -> list[dict] | None:
    payload = {"text": text, "hints": [{"voice": voice}],
               "outputAudioSpec": {"rawAudio": {"audioEncoding": "LINEAR16_PCM", "sampleRateHertz": SAMPLE_RATE}}}
    raw = http("POST", "https://tts.api.cloud.yandex.net/tts/v3/utteranceSynthesis",
               {"Authorization": f"Api-Key {key('YANDEX_API_KEY')}", "x-folder-id": key("YANDEX_FOLDER_ID"),
                "Content-Type": "application/json"}, json.dumps(payload).encode())
    pcm = bytearray()
    for line in raw.decode().splitlines():   # streamed: one JSON object per line
        line = line.strip()
        if line:
            chunk = json.loads(line).get("result", {}).get("audioChunk", {}).get("data")
            if chunk:
                pcm += base64.b64decode(chunk)
    if not pcm:
        raise ProviderError("Yandex returned no audio")
    write_pcm_wav(dst, bytes(pcm), SAMPLE_RATE)
    return None


def _azure(text: str, lang: str, voice: str, dst: Path) -> list[dict] | None:
    region = key("AZURE_SPEECH_REGION")
    ssml = (f"<speak version='1.0' xml:lang='{LOCALE[lang]}'><voice name='{voice}'>"
            f"{escape(text)}</voice></speak>")
    audio = http("POST", f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
                 {"Ocp-Apim-Subscription-Key": key("AZURE_SPEECH_KEY"),
                  "Content-Type": "application/ssml+xml",
                  "X-Microsoft-OutputFormat": "riff-48khz-16bit-mono-pcm",
                  "User-Agent": "reels-studio"}, ssml.encode())
    dst.write_bytes(audio)
    return None


def _edge(text: str, lang: str, voice: str, dst: Path) -> list[dict] | None:
    import edge_tts  # type: ignore

    async def run() -> list[dict]:
        comm = edge_tts.Communicate(text, voice, boundary="WordBoundary")
        words, audio = [], bytearray()
        async for ev in comm.stream():
            if ev["type"] == "audio":
                audio.extend(ev["data"])
            elif ev["type"] == "WordBoundary":   # offsets are in 100 ns ticks
                s = ev["offset"] / 1e7
                words.append({"w": ev["text"], "s": s, "e": s + ev["duration"] / 1e7})
        if not audio:
            raise ProviderError("edge-tts returned no audio")
        dst.write_bytes(bytes(audio))
        return words

    try:
        words = asyncio.run(run())
    except ProviderError:
        raise
    except Exception as e:   # edge-tts raises aiohttp / NoAudioReceived etc.
        raise ProviderError(f"edge-tts: {type(e).__name__}: {e}") from None
    return words or None


IMPL = {"elevenlabs": _elevenlabs, "gemini": _gemini, "yandex": _yandex, "azure": _azure, "edge": _edge}


# --------------------------------------------------------------------------- orchestration
def synthesize(provider: str, text: str, lang: str, voice: str, out: Path) -> list[dict] | None:
    """Synthesize (chunked) into `out` as 48 kHz mono wav. Returns word timings or None."""
    all_words: list[dict] | None = []
    pcm, offset = bytearray(), 0.0
    with tmpdir() as td:
        for i, part in enumerate(chunks(text, CHUNK_LIMIT[provider])):
            raw = Path(td) / f"part{i}.bin"
            words = IMPL[provider](part, lang, voice, raw)
            wav = to_wav(raw, Path(td) / f"part{i}.wav")
            with wave.open(str(wav)) as w:
                frames = w.readframes(w.getnframes())
            if words is None or all_words is None:
                all_words = None
            else:
                all_words += [{**w_, "s": w_["s"] + offset, "e": w_["e"] + offset} for w_ in words]
            pcm += frames
            offset += len(frames) / 2 / SAMPLE_RATE
    out.parent.mkdir(parents=True, exist_ok=True)
    write_pcm_wav(out, bytes(pcm), SAMPLE_RATE)
    return all_words


def clone_voice(sample: Path, name: str) -> str | None:
    """ElevenLabs Instant Voice Clone. Returns voice_id, or None when not possible."""
    if not has_keys("ELEVENLABS_API_KEY"):
        log("warning: voice clone requested but ELEVENLABS_API_KEY is not set — using a stock voice")
        return None
    with tmpdir() as td:
        wav = to_wav(sample, Path(td) / "sample.wav", sr=44100)
        body, ctype = multipart({"name": name, "remove_background_noise": "true"}, {"files": wav})
        try:
            raw = http("POST", "https://api.elevenlabs.io/v1/voices/add",
                       {"xi-api-key": key("ELEVENLABS_API_KEY"), "Content-Type": ctype}, body)
        except ProviderError as e:
            log(f"warning: voice clone failed ({e}) — using a stock voice")
            return None
    return json.loads(raw)["voice_id"]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--text", required=True, type=Path, help="script file (UTF-8)")
    ap.add_argument("--lang", required=True, choices=LANGS)
    ap.add_argument("--voice", default="auto", help="provider voice id/name, or 'auto'")
    ap.add_argument("--gender", default="female", choices=("female", "male"))
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--transcript", required=True, type=Path)
    ap.add_argument("--provider", default="auto", choices=("auto", *PROVIDERS))
    ap.add_argument("--clone-from", type=Path, help="footage/audio to clone the voice from (ElevenLabs)")
    ap.add_argument("--asr-provider", default="auto", help="ASR provider when TTS has no timings")
    ap.add_argument("--asr-model", default="large-v3", help="local whisper model for timing fallback")
    args = ap.parse_args(argv)
    load_dotenv()
    text = args.text.read_text(encoding="utf-8").strip()
    if not text:
        die(f"script is empty: {args.text}")

    voice, chain = args.voice, PROVIDERS if args.provider == "auto" else (args.provider,)
    if args.clone_from:
        cloned = clone_voice(args.clone_from, f"reels-studio-{args.out.resolve().parents[1].name}")
        if cloned:
            print(f"cloned voice_id: {cloned}")
            voice, chain = cloned, ("elevenlabs",)

    errors, used, words = [], None, None
    for name in chain:
        if not available(name):
            errors.append(f"{name}: unavailable")
            continue
        v = pick_voice(name, args.lang, voice, args.gender)
        try:
            words = synthesize(name, text, args.lang, v, args.out)
            used = (name, v)
            break
        except (ProviderError, RuntimeError, KeyError) as e:
            log(f"[tts] {name} failed: {e}")
            errors.append(f"{name}: {e}")
    if not used:
        die("all TTS providers failed: " + "; ".join(errors) + "  (pip install edge-tts for a free fallback)")

    total = duration(args.out)
    spoken = clean_for_timing(text)
    if words:
        tr = build_transcript(align_script(words, spoken), args.lang, "tts-timestamps", total)
    else:
        from asr import transcribe   # sibling module; imported lazily (heavy optional deps)
        log("[tts] provider returned no timings — aligning with ASR on the known script")
        try:
            tr, asr_name = transcribe(args.out, args.lang, spoken, args.asr_provider, args.asr_model)
        except RuntimeError as e:
            die(f"TTS audio written to {args.out} but timing alignment failed: {e}")
        record_used(args.transcript, "tts_timing", asr_name)
    write_json(args.transcript, tr)
    note = None if used[0] == "elevenlabs" else f"{args.lang} TTS via {used[0]} — set ELEVENLABS_API_KEY for higher quality"
    record_used(args.out, "tts", f"{used[0]}:{used[1]}", note)
    print(f"{args.out}: {total}s via {used[0]} ({used[1]}); transcript {len(tr['words'])} words "
          f"[{tr['source']}] -> {args.transcript}")


if __name__ == "__main__":
    main()
