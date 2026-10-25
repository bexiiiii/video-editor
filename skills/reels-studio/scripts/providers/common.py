"""Shared plumbing for every reels-studio audio script.

Kept dependency-free (stdlib only) so that `doctor.py` and the CLI wrappers can import it
before we know whether numpy / requests exist. Responsibilities:

* `.env` loading and key presence checks (values are never printed or logged)
* a tiny HTTP client on urllib (JSON + multipart) — `requests` is optional everywhere
* ffmpeg helpers: decode-to-wav, probe duration, loudness measurement
* transcript building (word list -> contracts.md transcript with sentences + pauses)
* recording which provider produced an artefact into `work/<slug>/env.json -> used`
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
import uuid
from difflib import SequenceMatcher
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
SFX_DIR = SKILL_DIR / "assets" / "sfx"
LANGS = ("ru", "uz", "kk")
PAUSE_MIN = 0.25          # seconds; gaps >= this become transcript "pauses"
SAMPLE_RATE = 48000       # every audio artefact in the pipeline is 48 kHz


class ProviderError(RuntimeError):
    """A provider failed in a way that should make the chain try the next one."""


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- env / keys
def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE pairs from ./.env without overriding the real environment."""
    path = path or Path.cwd() / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip().removeprefix("export ").strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def has_keys(*names: str) -> bool:
    return all(os.environ.get(n, "").strip() for n in names)


def key(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise ProviderError(f"{name} not set")
    return val


def has_module(name: str) -> bool:
    import importlib.util
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


# --------------------------------------------------------------------------- HTTP
def _redact(text: str) -> str:
    """Strip anything that looks like a credential from provider error bodies."""
    for name in ("ELEVENLABS_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                 "YANDEX_API_KEY", "AZURE_SPEECH_KEY"):
        val = os.environ.get(name)
        if val:
            text = text.replace(val, "***")
    return text[:500]


def http(method: str, url: str, headers: dict | None = None, body: bytes | None = None,
         timeout: float = 300) -> bytes:
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        detail = _redact(e.read().decode("utf-8", "replace"))
        raise ProviderError(f"HTTP {e.code} from {url.split('?')[0]}: {detail}") from None
    except urllib.error.URLError as e:
        raise ProviderError(f"network error for {url.split('?')[0]}: {e.reason}") from None


def http_json(method: str, url: str, payload: dict | None = None,
              headers: dict | None = None, timeout: float = 300) -> dict:
    hdrs = {"Content-Type": "application/json", **(headers or {})}
    body = json.dumps(payload).encode() if payload is not None else None
    return json.loads(http(method, url, hdrs, body, timeout))


def multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    """Encode a multipart/form-data body. `fields` values may be lists (repeated keys);
    `files` maps field -> Path. Returns (body, content_type)."""
    boundary = uuid.uuid4().hex
    out = bytearray()
    for name, value in fields.items():
        for v in value if isinstance(value, list) else [value]:
            out += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{v}\r\n".encode()
    for name, path in files.items():
        path = Path(path)
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; "
                f"filename=\"{path.name}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
        out += path.read_bytes() + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


# --------------------------------------------------------------------------- ffmpeg
def ffmpeg(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    if not shutil.which("ffmpeg"):
        die("ffmpeg not found on PATH (required). Install it: brew install ffmpeg / apt install ffmpeg")
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y", *args]
    proc = subprocess.run(cmd, capture_output=True, text=not capture)
    if proc.returncode != 0:
        err = proc.stderr if isinstance(proc.stderr, str) else proc.stderr.decode("utf-8", "replace")
        raise RuntimeError(f"ffmpeg failed: {' '.join(args[:6])} ...\n{err[-1500:]}")
    return proc


def to_wav(src: Path, dst: Path, sr: int = SAMPLE_RATE, channels: int = 1,
           afilter: str | None = None) -> Path:
    """Decode any audio/video file to PCM s16 WAV (optionally through a filter chain)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    args = ["-i", str(src), "-vn"]
    if afilter:
        args += ["-af", afilter]
    ffmpeg(*args, "-ac", str(channels), "-ar", str(sr), "-c:a", "pcm_s16le", str(dst))
    return dst


def duration(path: Path) -> float:
    proc = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    try:
        return round(float(proc.stdout.strip()), 3)
    except ValueError:
        raise RuntimeError(f"cannot probe duration of {path}") from None


def loudness(path: Path) -> dict:
    """EBU R128 measurement via loudnorm's analysis pass (input_i, input_tp, input_lra...)."""
    proc = ffmpeg("-i", str(path), "-af", "loudnorm=I=-14:TP=-1:LRA=7:print_format=json",
                  "-f", "null", "-")
    match = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", proc.stderr, re.S)
    if not match:
        raise RuntimeError(f"could not measure loudness of {path}")
    return json.loads(match.group(0))


def tmpdir(prefix: str = "rs-") -> tempfile.TemporaryDirectory:
    """Temp dir that is always removed (callers use it as a context manager)."""
    return tempfile.TemporaryDirectory(prefix=prefix)


# --------------------------------------------------------------------------- transcripts
_SENT_END = re.compile(r"[.!?…]+[»\"')\]]*$")


def norm_token(tok: str) -> str:
    """Lower-case, strip punctuation; used only for matching ASR words to script words."""
    tok = unicodedata.normalize("NFC", tok).lower().replace("ё", "е")
    return "".join(ch for ch in tok if ch.isalnum())


def script_tokens(text: str) -> list[str]:
    """Whitespace tokens of the known script, dropping pure-punctuation tokens like '—'."""
    return [t for t in text.split() if norm_token(t)]


def align_script(words: list[dict], text: str) -> list[dict]:
    """Transfer timings from recognised `words` onto the known script tokens.

    Matching uses difflib on normalised tokens. Script tokens with no match get timings
    interpolated between their timed neighbours, so the output has exactly one entry per
    script token with correct spelling/punctuation. If the ASR heard nothing usable we
    return the ASR words unchanged.
    """
    toks = script_tokens(text)
    if not toks or not words:
        return words
    a = [norm_token(t) for t in toks]
    b = [norm_token(w["w"]) for w in words]
    timed: list[dict | None] = [None] * len(toks)
    sm = SequenceMatcher(a=a, b=b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                timed[i1 + k] = {"s": words[j1 + k]["s"], "e": words[j1 + k]["e"]}
        elif tag == "replace":
            # Spread the replaced ASR span evenly over the replaced script span.
            s0, e0 = words[j1]["s"], words[j2 - 1]["e"]
            n = i2 - i1
            for k in range(n):
                timed[i1 + k] = {"s": s0 + (e0 - s0) * k / n, "e": s0 + (e0 - s0) * (k + 1) / n}
    if sum(t is not None for t in timed) < max(1, len(toks) // 4):
        log("warning: known script matched <25% of recognised words; keeping raw ASR words")
        return words
    _interpolate(timed, words[0]["s"], words[-1]["e"])
    return [{"w": tok, "s": round(t["s"], 3), "e": round(t["e"], 3)} for tok, t in zip(toks, timed)]


def _interpolate(timed: list, start: float, end: float) -> None:
    """Fill None gaps in-place by splitting the time between known neighbours."""
    i = 0
    while i < len(timed):
        if timed[i] is not None:
            i += 1
            continue
        j = i
        while j < len(timed) and timed[j] is None:
            j += 1
        left = timed[i - 1]["e"] if i > 0 else start
        right = timed[j]["s"] if j < len(timed) else end
        n = j - i
        span = max(right - left, 0.06 * n)
        for k in range(n):
            timed[i + k] = {"s": left + span * k / n, "e": left + span * (k + 1) / n}
        i = j


def build_transcript(words: list[dict], lang: str, source: str, total: float) -> dict:
    """Assemble the contracts.md transcript: words, sentences (by terminal punctuation,
    or by long pauses when the text has none) and pauses (gaps >= PAUSE_MIN)."""
    words = [w for w in words if w["w"].strip()]
    for w in words:
        w["w"] = w["w"].strip()
        w["s"], w["e"] = round(float(w["s"]), 3), round(max(float(w["e"]), float(w["s"])), 3)
    pauses = _pauses(words, total)
    has_punct = any(_SENT_END.search(w["w"]) for w in words)
    sentences, w0 = [], 0
    for i, w in enumerate(words):
        nxt_gap = (words[i + 1]["s"] - w["e"]) if i + 1 < len(words) else 99
        boundary = _SENT_END.search(w["w"]) if has_punct else nxt_gap >= 0.5
        if boundary or i == len(words) - 1:
            sentences.append({"text": " ".join(x["w"] for x in words[w0:i + 1]),
                              "s": words[w0]["s"], "e": w["e"], "w0": w0, "w1": i})
            w0 = i + 1
    return {"lang": lang, "source": source, "duration": round(total, 3),
            "words": words, "sentences": sentences, "pauses": pauses}


def _pauses(words: list[dict], total: float) -> list[dict]:
    out = []
    edges = [(0.0, words[0]["s"])] if words else []
    edges += [(a["e"], b["s"]) for a, b in zip(words, words[1:])]
    if words:
        edges.append((words[-1]["e"], total))
    for s, e in edges:
        if e - s >= PAUSE_MIN:
            out.append({"s": round(s, 3), "e": round(e, 3)})
    return out


def validate_transcript(t: dict) -> list[str]:
    """Cheap structural checks; returns a list of problems (empty = valid)."""
    problems = []
    for k in ("lang", "source", "duration", "words", "sentences", "pauses"):
        if k not in t:
            problems.append(f"missing key {k}")
    prev = -1.0
    for i, w in enumerate(t.get("words", [])):
        if not (w["s"] <= w["e"]):
            problems.append(f"word {i} has s>e")
        if w["s"] + 1e-3 < prev:
            problems.append(f"word {i} starts before previous word")
        prev = w["s"]
    return problems


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- env.json
def find_env_json(out_path: Path) -> Path | None:
    """env.json lives in work/<slug>/; artefacts are 1-2 levels below it."""
    for parent in list(Path(out_path).resolve().parents)[:3]:
        cand = parent / "env.json"
        if cand.is_file():
            return cand
    return None


def record_used(out_path: Path, capability: str, provider: str, note: str | None = None) -> None:
    """Append `{capability: {provider, file, note}}` to env.json -> used (if env.json exists)."""
    log(f"[{capability}] provider: {provider}" + (f" ({note})" if note else ""))
    env_path = find_env_json(out_path)
    if not env_path:
        return
    try:
        env = json.loads(env_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    entry = {"provider": provider, "file": str(Path(out_path).resolve().relative_to(env_path.parent))
             if Path(out_path).resolve().is_relative_to(env_path.parent) else str(out_path)}
    if note:
        entry["note"] = note
    env.setdefault("used", {})[capability] = entry
    write_json(env_path, env)
