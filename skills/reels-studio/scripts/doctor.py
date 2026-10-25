#!/usr/bin/env python3
"""Environment check: tools, python packages, API keys (presence only) -> provider per capability.

Prints a human-readable table and, with --work, writes work/<slug>/env.json:
  {"checked_at", "platform", "tools", "python_packages", "keys", "providers": {cap: {chosen, chain}},
   "notes": [...], "used": {...preserved from an existing env.json...}}

Loads ./.env first (never overriding the real environment). Key VALUES are never printed.
Exit code is 0 unless a hard requirement (ffmpeg, python >= 3.10) is missing.

Usage: doctor.py [--work work/<slug>] [--json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
from common import SFX_DIR, has_keys, has_module, load_dotenv, write_json  # noqa: E402

KEYS = ["ELEVENLABS_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "YANDEX_API_KEY", "YANDEX_FOLDER_ID",
        "AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION", "GEMINI_MUSIC_MODEL"]
PACKAGES = {"numpy": "numpy", "scipy": "scipy", "requests": "requests", "faster_whisper": "faster-whisper",
            "mlx_whisper": "mlx-whisper", "edge_tts": "edge-tts", "df": "deepfilternet"}
FFMPEG_FILTERS = ("loudnorm", "afftdn", "deesser", "sidechaincompress")


# --------------------------------------------------------------------------- probes
def version_of(cmd: list[str]) -> str | None:
    if not shutil.which(cmd[0]):
        return None
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (out.stdout or out.stderr).strip().splitlines()
    return text[0][:80] if text else "present"


def probe_tools() -> dict:
    tools = {
        "python": {"version": platform.python_version(), "ok": sys.version_info >= (3, 10)},
        "ffmpeg": {"version": version_of(["ffmpeg", "-version"])},
        "ffprobe": {"version": version_of(["ffprobe", "-version"])},
        "node": {"version": version_of(["node", "--version"])},
        "npx": {"version": version_of(["npx", "--version"])},
        "edge-tts": {"version": "present" if shutil.which("edge-tts") else None},
        "deepFilter": {"version": "present" if shutil.which("deepFilter") else None},
        "codex": {"version": version_of(["codex", "--version"])},
    }
    if tools["ffmpeg"]["version"]:
        filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        tools["ffmpeg"]["filters_missing"] = [f for f in FFMPEG_FILTERS if not re.search(rf"\b{f}\b", filters)]
    node = tools["node"]["version"] or ""
    m = re.match(r"v(\d+)", node)
    tools["node"]["ok"] = bool(m and int(m.group(1)) >= 20)
    for name, t in tools.items():
        t.setdefault("ok", t["version"] is not None)
    return tools


def codex_image_gen_hint(tools: dict) -> dict:
    """We cannot call Codex's built-in image_gen from here; report whether it is plausible."""
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    in_codex = any(k.startswith("CODEX_") for k in os.environ)
    likely = in_codex or tools["codex"]["ok"]
    return {"likely": likely, "generated_images_dir": str(codex_home / "generated_images"),
            "hint": "running under Codex: agent may use built-in image_gen" if in_codex else
                    ("codex CLI installed; image_gen only available inside a Codex session" if likely
                     else "not running under Codex")}


# --------------------------------------------------------------------------- provider chains
def chains(tools: dict, pkgs: dict, codex: dict) -> dict:
    """Each capability -> ordered [(provider, available, requirement)]."""
    k = has_keys
    apple = platform.system() == "Darwin" and platform.machine() == "arm64"
    np_ok = pkgs["numpy"] and pkgs["scipy"]
    return {
        "asr": [("elevenlabs-scribe", k("ELEVENLABS_API_KEY"), "ELEVENLABS_API_KEY"),
                ("openai-whisper", k("OPENAI_API_KEY"), "OPENAI_API_KEY"),
                ("mlx-whisper", apple and pkgs["mlx_whisper"], "pip mlx-whisper (Apple Silicon)"),
                ("faster-whisper", pkgs["faster_whisper"] and pkgs["numpy"], "pip faster-whisper")],
        "tts": [("elevenlabs", k("ELEVENLABS_API_KEY"), "ELEVENLABS_API_KEY"),
                ("gemini", k("GEMINI_API_KEY"), "GEMINI_API_KEY"),
                ("yandex", k("YANDEX_API_KEY", "YANDEX_FOLDER_ID"), "YANDEX_API_KEY+YANDEX_FOLDER_ID"),
                ("azure", k("AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"), "AZURE_SPEECH_KEY+AZURE_SPEECH_REGION"),
                ("edge-tts", pkgs["edge_tts"], "pip edge-tts")],
        "voice_clone": [("elevenlabs-ivc", k("ELEVENLABS_API_KEY"), "ELEVENLABS_API_KEY"),
                        ("stock-voice", True, "-")],
        "cleanup": [("deepfilternet3", tools["deepFilter"]["ok"], "pip deepfilternet"),
                    ("ffmpeg-chain", tools["ffmpeg"]["ok"], "ffmpeg")],
        "voice_isolator": [("elevenlabs-isolator", k("ELEVENLABS_API_KEY"), "ELEVENLABS_API_KEY")],
        "music": [("elevenlabs-music", k("ELEVENLABS_API_KEY"), "ELEVENLABS_API_KEY"),
                  ("lyria", k("GEMINI_API_KEY", "GEMINI_MUSIC_MODEL"), "GEMINI_API_KEY+GEMINI_MUSIC_MODEL"),
                  ("local-procedural", np_ok, "pip numpy scipy")],
        "sfx": [("bundled-kit", any(SFX_DIR.glob("*.wav")), "assets/sfx/*.wav (scripts/sfx_kit.py)"),
                ("elevenlabs-sfx", k("ELEVENLABS_API_KEY"), "ELEVENLABS_API_KEY")],
        "images": [("codex-image_gen", codex["likely"], "Codex session"),
                   ("openai-images", k("OPENAI_API_KEY"), "OPENAI_API_KEY"),
                   ("gemini-image", k("GEMINI_API_KEY"), "GEMINI_API_KEY"),
                   ("fluent-emoji-3d", True, "bundled / MIT")],
        "mix": [("ffmpeg-loudnorm-2pass", tools["ffmpeg"]["ok"] and np_ok, "ffmpeg + numpy")],
        "render": [("hyperframes@0.8.154", tools["node"]["ok"] and tools["npx"]["ok"], "node>=20 + npx")],
    }


def summarize(ch: dict) -> dict:
    out = {}
    for cap, items in ch.items():
        chosen = next((name for name, ok, _ in items if ok), None)
        out[cap] = {"chosen": chosen,
                    "chain": [{"provider": n, "available": bool(ok), "needs": req} for n, ok, req in items]}
    return out


def notes_for(providers: dict, tools: dict) -> list[str]:
    notes = []
    if providers["tts"]["chosen"] == "edge-tts":
        notes.append("TTS via edge-tts (free) — set ELEVENLABS_API_KEY for higher quality uz/kk voices")
    if providers["asr"]["chosen"] == "faster-whisper":
        notes.append("ASR via local faster-whisper large-v3 (~3 GB download on first use, slow on CPU)")
    if providers["music"]["chosen"] == "local-procedural":
        notes.append("Music via local procedural generator — set ELEVENLABS_API_KEY for generated music")
    if providers["cleanup"]["chosen"] == "ffmpeg-chain":
        notes.append("Voice cleanup via ffmpeg filters — pip install deepfilternet for better denoising")
    if tools["ffmpeg"].get("filters_missing"):
        notes.append("ffmpeg lacks filters: " + ", ".join(tools["ffmpeg"]["filters_missing"]))
    for cap, info in providers.items():
        if info["chosen"] is None and cap != "voice_isolator":
            notes.append(f"NO provider for {cap}: install one of " +
                         ", ".join(c["needs"] for c in info["chain"]))
    return notes


# --------------------------------------------------------------------------- output
def print_table(tools: dict, pkgs: dict, keys: dict, providers: dict, codex: dict, notes: list[str]) -> None:
    def row(a, b, c=""):
        print(f"  {a:<22} {b:<10} {c}")
    print("Tools")
    for name, t in tools.items():
        row(name, "ok" if t["ok"] else ("MISSING" if name in ("ffmpeg", "python") else "absent"),
            t["version"] or "")
    print("Python packages")
    for mod, ok in pkgs.items():
        row(PACKAGES[mod], "ok" if ok else "absent")
    print("API keys (presence only)")
    for name, ok in keys.items():
        row(name, "present" if ok else "absent")
    print("Providers (first available wins)")
    for cap, info in providers.items():
        alt = [c["provider"] for c in info["chain"] if c["available"] and c["provider"] != info["chosen"]]
        row(cap, info["chosen"] or "NONE", ("fallbacks: " + ", ".join(alt)) if alt else "")
    print(f"Codex image_gen: {codex['hint']}")
    for n in notes:
        print(f"note: {n}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--work", type=Path, help="work/<slug> directory; env.json is written there")
    ap.add_argument("--json", action="store_true", help="print env.json to stdout instead of the table")
    args = ap.parse_args(argv)
    load_dotenv()

    tools = probe_tools()
    pkgs = {mod: has_module(mod) for mod in PACKAGES}
    keys = {k: has_keys(k) for k in KEYS}
    codex = codex_image_gen_hint(tools)
    providers = summarize(chains(tools, pkgs, codex))
    notes = notes_for(providers, tools)
    env = {"checked_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "platform": f"{platform.system()} {platform.machine()}",
           "tools": tools, "python_packages": pkgs, "keys": keys, "codex_image_gen": codex,
           "providers": providers, "notes": notes, "used": {}}

    if args.work:
        path = args.work / "env.json"
        if path.is_file():                                   # keep provenance of earlier steps
            try:
                env["used"] = json.loads(path.read_text(encoding="utf-8")).get("used", {})
            except json.JSONDecodeError:
                pass
        write_json(path, env)
    if args.json:
        print(json.dumps(env, ensure_ascii=False, indent=1))
    else:
        print_table(tools, pkgs, keys, providers, codex, notes)
        if args.work:
            print(f"wrote {args.work / 'env.json'}")

    hard_fail = [n for n in ("python", "ffmpeg") if not tools[n]["ok"]]
    if hard_fail:
        print(f"error: required tools missing: {', '.join(hard_fail)}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
