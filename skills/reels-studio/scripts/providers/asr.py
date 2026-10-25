#!/usr/bin/env python3
"""ASR with word timings -> contracts.md transcript.json.

Chain (first available wins, language ALWAYS forced — uz is misdetected as az otherwise):
  1. ElevenLabs Scribe v2        (ELEVENLABS_API_KEY)
  2. OpenAI whisper-1            (OPENAI_API_KEY; verbose_json + word granularity)
  3. local mlx-whisper           (Apple Silicon, if `mlx_whisper` is installed)
  4. local faster-whisper        (`faster-whisper`; default model large-v3)

When the script is known (`--text`), recognised words are re-labelled with the script's
tokens (spelling + punctuation preserved) and timings transferred via sequence alignment.

Usage:
  asr.py IN.wav --lang ru --out audio/transcript.json [--text script.txt]
         [--provider auto|elevenlabs|openai|mlx-whisper|faster-whisper] [--model large-v3] [--vad]
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (LANGS, ProviderError, align_script, build_transcript, die, duration,  # noqa: E402
                    has_keys, has_module, http, key, load_dotenv, log, multipart, record_used,
                    tmpdir, to_wav, validate_transcript, write_json)

PROVIDERS = ("elevenlabs", "openai", "mlx-whisper", "faster-whisper")
SOURCE_NAME = {"elevenlabs": "elevenlabs-scribe", "openai": "openai-whisper",
               "mlx-whisper": "faster-whisper", "faster-whisper": "faster-whisper"}
MLX_REPOS = {"large-v3": "mlx-community/whisper-large-v3-mlx", "small": "mlx-community/whisper-small-mlx",
             "medium": "mlx-community/whisper-medium-mlx", "large-v3-turbo": "mlx-community/whisper-large-v3-turbo"}


def available(name: str) -> bool:
    if name == "elevenlabs":
        return has_keys("ELEVENLABS_API_KEY")
    if name == "openai":
        return has_keys("OPENAI_API_KEY")
    if name == "mlx-whisper":
        return platform.system() == "Darwin" and platform.machine() == "arm64" and has_module("mlx_whisper")
    if name == "faster-whisper":
        return has_module("faster_whisper") and has_module("numpy")
    return False


# --------------------------------------------------------------------------- providers
def _elevenlabs(audio: Path, lang: str, prompt: str | None, model: str, vad: bool) -> list[dict]:
    with tmpdir() as td:
        wav = to_wav(audio, Path(td) / "in.wav", sr=16000)
        body, ctype = multipart({"model_id": "scribe_v2", "language_code": lang,
                                 "timestamps_granularity": "word", "tag_audio_events": "false"},
                                {"file": wav})
        raw = http("POST", "https://api.elevenlabs.io/v1/speech-to-text",
                   {"xi-api-key": key("ELEVENLABS_API_KEY"), "Content-Type": ctype}, body)
    data = json.loads(raw)
    return [{"w": w["text"], "s": w["start"], "e": w["end"]}
            for w in data.get("words", []) if w.get("type", "word") == "word"]


def _openai(audio: Path, lang: str, prompt: str | None, model: str, vad: bool) -> list[dict]:
    with tmpdir() as td:
        flac = Path(td) / "in.flac"   # 16 kHz mono flac keeps uploads far below the 25 MB cap
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-vn", "-ac", "1",
                        "-ar", "16000", str(flac)], check=True)
        fields = {"model": "whisper-1", "language": lang, "response_format": "verbose_json",
                  "timestamp_granularities[]": "word"}
        if prompt:
            fields["prompt"] = prompt[:800]
        body, ctype = multipart(fields, {"file": flac})
        raw = http("POST", "https://api.openai.com/v1/audio/transcriptions",
                   {"Authorization": f"Bearer {key('OPENAI_API_KEY')}", "Content-Type": ctype}, body)
    data = json.loads(raw)
    return [{"w": w["word"], "s": w["start"], "e": w["end"]} for w in data.get("words", [])]


def _pcm16k(audio: Path):
    """Decode with ffmpeg to float32 mono 16 kHz. faster-whisper's own PyAV decode breaks on
    Python 3.14, and passing a numpy array sidesteps it on every version."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def _mlx(audio: Path, lang: str, prompt: str | None, model: str, vad: bool) -> list[dict]:
    import mlx_whisper  # type: ignore
    repo = model if "/" in model else MLX_REPOS.get(model, f"mlx-community/whisper-{model}-mlx")
    res = mlx_whisper.transcribe(_pcm16k(audio), path_or_hf_repo=repo, language=lang,
                                 word_timestamps=True, initial_prompt=(prompt or None) and prompt[:400])
    return [{"w": w["word"], "s": w["start"], "e": w["end"]}
            for seg in res.get("segments", []) for w in seg.get("words", [])]


def _faster_whisper(audio: Path, lang: str, prompt: str | None, model: str, vad: bool) -> list[dict]:
    from faster_whisper import WhisperModel  # type: ignore
    log(f"faster-whisper: loading model '{model}' (first run downloads it)")
    wm = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _info = wm.transcribe(_pcm16k(audio), language=lang, word_timestamps=True,
                                    initial_prompt=(prompt or None) and prompt[:400],
                                    vad_filter=vad, beam_size=5, condition_on_previous_text=False)
    return [{"w": w.word, "s": w.start, "e": w.end} for seg in segments for w in (seg.words or [])]


IMPL = {"elevenlabs": _elevenlabs, "openai": _openai, "mlx-whisper": _mlx, "faster-whisper": _faster_whisper}


# --------------------------------------------------------------------------- public API
def transcribe(audio: Path, lang: str, text: str | None = None, provider: str = "auto",
               model: str = "large-v3", vad: bool = False) -> tuple[dict, str]:
    """Run the ASR chain. Returns (transcript, provider_name). Raises RuntimeError if all fail."""
    if lang not in LANGS:
        raise ValueError(f"--lang must be one of {LANGS}")
    chain = PROVIDERS if provider == "auto" else (provider,)
    errors = []
    for name in chain:
        if not available(name):
            errors.append(f"{name}: unavailable")
            continue
        try:
            words = IMPL[name](audio, lang, text, model, vad)
            if not words:
                raise ProviderError("no words recognised")
        except (ProviderError, RuntimeError, subprocess.CalledProcessError, OSError) as e:
            log(f"[asr] {name} failed: {e}")
            errors.append(f"{name}: {e}")
            continue
        if text:
            words = align_script(words, text)
        return build_transcript(words, lang, SOURCE_NAME[name], duration(audio)), name
    raise RuntimeError("all ASR providers failed: " + "; ".join(errors))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", type=Path, help="audio or video file")
    ap.add_argument("--lang", required=True, choices=LANGS)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--text", type=Path, help="known script (improves spelling, restores punctuation)")
    ap.add_argument("--provider", default="auto", choices=("auto", *PROVIDERS))
    ap.add_argument("--model", default="large-v3", help="local whisper model (large-v3 | small | ...)")
    ap.add_argument("--vad", action="store_true", help="local: enable VAD filter (noisy footage)")
    args = ap.parse_args(argv)
    load_dotenv()
    if not args.input.is_file():
        die(f"input not found: {args.input}")
    text = args.text.read_text(encoding="utf-8").strip() if args.text else None
    try:
        tr, name = transcribe(args.input, args.lang, text, args.provider, args.model, args.vad)
    except (RuntimeError, ValueError) as e:
        die(str(e))
    problems = validate_transcript(tr)
    if problems:
        log("warning: transcript issues: " + "; ".join(problems[:5]))
    write_json(args.out, tr)
    record_used(args.out, "asr", name, f"model={args.model}" if "whisper" in name and name != "openai" else None)
    print(f"{args.out}: {len(tr['words'])} words, {len(tr['sentences'])} sentences, "
          f"{len(tr['pauses'])} pauses, {tr['duration']}s via {name}")


if __name__ == "__main__":
    main()
