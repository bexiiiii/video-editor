#!/usr/bin/env bash
# reels-studio installer — one source tree for Claude Code and OpenAI Codex.
#   ./install.sh            install for both hosts (symlinks, so `git pull` updates them)
#   ./install.sh --claude   Claude Code only      ./install.sh --codex   Codex only
#   ./install.sh --deps     also create ~/.reels-studio/venv with Python dependencies
#   ./install.sh --copy     copy instead of symlink
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
want_claude=1 want_codex=1 deps=0 mode=link
for a in "$@"; do case "$a" in
  --claude) want_codex=0 ;; --codex) want_claude=0 ;; --deps) deps=1 ;; --copy) mode=copy ;;
  -h|--help) sed -n '2,7p' "$0"; exit 0 ;; *) echo "unknown option: $a" >&2; exit 2 ;;
esac; done

place() {  # place <src> <dst>
  mkdir -p "$(dirname "$2")"
  if [ -e "$2" ] || [ -L "$2" ]; then
    if [ -L "$2" ]; then rm "$2"; else echo "  skip $2 (exists, not a symlink — remove it manually to reinstall)"; return; fi
  fi
  if [ "$mode" = copy ]; then cp -R "$1" "$2"; else ln -s "$1" "$2"; fi
  echo "  $2"
}

python3 "$repo/tools/gen_agents.py" >/dev/null

if [ "$want_claude" = 1 ]; then
  echo "Claude Code:"
  for s in "$repo"/skills/*/; do place "${s%/}" "$HOME/.claude/skills/$(basename "$s")"; done
  for a in "$repo"/agents/*.md; do place "$a" "$HOME/.claude/agents/$(basename "$a")"; done
fi
if [ "$want_codex" = 1 ]; then
  echo "Codex:"
  for s in "$repo"/skills/*/; do place "${s%/}" "$HOME/.agents/skills/$(basename "$s")"; done
  for a in "$repo"/codex/agents/*.toml; do place "$a" "$HOME/.codex/agents/$(basename "$a")"; done
  echo "  → merge codex/config.example.toml into ~/.codex/config.toml (network access + agent roles)."
fi

if [ "$deps" = 1 ]; then
  # The newest Python often has no prebuilt wheels yet for scipy/numpy/onnx (pip then tries to
  # compile them and fails), so prefer the newest version with wheels. Override with REELS_PYTHON.
  py="${REELS_PYTHON:-}"
  if [ -z "$py" ]; then
    for c in python3.13 python3.12 python3.11 python3.14 python3; do
      if command -v "$c" >/dev/null; then py="$(command -v "$c")"; break; fi
    done
  fi
  [ -n "$py" ] || { echo "no python3 found" >&2; exit 1; }
  venv="$HOME/.reels-studio/venv"
  want="$("$py" -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
  have="$([ -x "$venv/bin/python" ] && "$venv/bin/python" -c 'import sys;print("%d.%d"%sys.version_info[:2])' || true)"
  if [ -n "$have" ] && [ "$have" != "$want" ]; then
    echo "  existing venv uses Python $have — recreating with $want"
    rm -rf "$venv"
  fi
  echo "Python deps → $venv (Python $want)"
  "$py" -m venv "$venv"
  "$venv/bin/pip" install -q --upgrade pip
  "$venv/bin/pip" install -q --prefer-binary -r "$repo/skills/reels-studio/scripts/requirements.txt"
fi

echo "Checks:"
for b in ffmpeg ffprobe node npx python3; do
  if command -v "$b" >/dev/null; then echo "  ok  $b"; else echo "  MISSING $b"; fi
done
echo "Done. Optional keys (any subset): ELEVENLABS_API_KEY OPENAI_API_KEY GEMINI_API_KEY YANDEX_API_KEY AZURE_SPEECH_KEY — see .env.example"
