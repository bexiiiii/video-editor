#!/usr/bin/env bash
# Branded style previews: the stock demos re-rendered with the client's brand layer (references/branding.md).
#
#   make_brand_previews.sh <work/<slug> | brief.json> [a b c d e]      (default: all five styles)
#     options (before the positional args):
#       --out DIR     where style-<x>.jpg go (default: <work>/previews, or <dir of brief.json>/previews)
#       --at T1,T2…   override the timestamps (default: assets/previews/timestamps.json — the same 4 instants as
#                     assets/previews/style-<x>.jpg, so branded and stock strips compare 1:1)
#       --plain       skip the brand layer (stock look; used to diff no-brand renders)
#       --assets DIR  use another assets/ tree (e.g. a `git archive` of an older revision) instead of $SKILL/assets
#
# Per style: copy the demo + the packs it needs into a temp dir, run that demo's own prepare.sh (same lib/ layout
# as the assembler), write lib/brand.{css,js,json} with scripts/brand.py, link brand.css AFTER the style tokens and
# brand.js BEFORE lib/runtime.js, `hyperframes snapshot --at …` and hstack 4 frames at 360 px. Default previews in
# assets/previews/ are never touched. Needs ≥ 1 GB free disk (checked). Temp dirs are always removed.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HF="hyperframes@0.8.154"
out="" ; at_override="" ; plain=0 ; assets="$here/assets"
while [[ $# -gt 0 && "$1" == --* ]]; do
  case "$1" in
    --out) out="$2"; shift 2 ;;
    --at) at_override="$2"; shift 2 ;;
    --plain) plain=1; shift ;;
    --assets) assets="$(cd "$2" && pwd)"; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
src="${1:?usage: make_brand_previews.sh [--out DIR] [--at T,..] [--plain] <work-dir|brief.json> [styles…]}"; shift
if [[ -d "$src" ]]; then brief="$(cd "$src" && pwd)/brief.json"; base="$(cd "$src" && pwd)"
else brief="$(cd "$(dirname "$src")" && pwd)/$(basename "$src")"; base="$(dirname "$brief")"; fi
[[ -f "$brief" ]] || { echo "no brief.json at $brief" >&2; exit 2; }
out="${out:-$base/previews}"; mkdir -p "$out"; out="$(cd "$out" && pwd)"
styles=("$@"); [[ ${#styles[@]} -gt 0 ]] || styles=(a b c d e)

# node ≥ 22 (nvm fallback)
if ! command -v node >/dev/null || [[ "$(node -v | sed 's/v\([0-9]*\).*/\1/')" -lt 22 ]]; then
  nv="$(ls -d "$HOME"/.nvm/versions/node/v2[2-9]* 2>/dev/null | sort -V | tail -1)"; [[ -n "$nv" ]] && export PATH="$nv/bin:$PATH"
fi
export HYPERFRAMES_NO_TELEMETRY=1

free_kb="$(df -k "$out" | awk 'NR==2{print $4}')"
if [[ "$free_kb" -lt 1048576 ]]; then echo "only $((free_kb/1024)) MB free — need ≥ 1 GB for snapshots; aborting" >&2; exit 3; fi

tmp="$(mktemp -d "${TMPDIR:-/tmp}/rs-brandprev.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
# packs each demo's prepare.sh reads (relative to assets/)
deps() { case "$1" in a) echo "shared style-a";; b) echo "shared style-b";; c) echo "shared style-a style-b style-c";;
                      d) echo "shared style-a style-d";; e) echo "shared style-e";; esac; }

for s in "${styles[@]}"; do
  s="$(echo "$s" | tr 'A-Z' 'a-z')"
  [[ -d "$assets/style-$s/demo" ]] || { echo "no demo for style $s" >&2; continue; }
  t="$tmp/$s/assets"; mkdir -p "$t"
  for d in $(deps "$s"); do
    rsync -a --exclude '*.mp4' --exclude '.hyperframes' --exclude 'demo/lib' --exclude 'demo/renders' "$assets/$d/" "$t/$d/"
  done
  demo="$t/style-$s/demo"
  bash "$demo/prepare.sh" >/dev/null
  if [[ $plain -eq 0 ]]; then
    python3 "$here/scripts/brand.py" --brief "$brief" --style "$s" --out "$demo/lib" >"$tmp/$s.brand.json"
    if [[ -f "$demo/lib/brand.css" ]]; then
      python3 - "$demo/index.html" <<'PY'
import re, sys
p = sys.argv[1]; t = open(p).read()
links = list(re.finditer(r'<link rel="stylesheet" href="lib/tokens-[^"]+" />', t))
assert links, "no lib/tokens-*.css link in demo"
e = links[-1].end(); t = t[:e] + '\n    <link rel="stylesheet" href="lib/brand.css" />' + t[e:]
i = t.index('<script src="lib/runtime.js"></script>')
t = t[:i] + '<script src="lib/brand.js"></script>\n    ' + t[i:]
open(p, "w").write(t)
PY
      echo "style $s: $(cat "$tmp/$s.brand.json")"
    else
      echo "style $s: brief has no brand colours/font — stock look" >&2
    fi
  fi
  ats="$at_override"
  [[ -n "$ats" ]] || ats="$(python3 -c "import json,sys; print(','.join(str(x) for x in json.load(open(sys.argv[1]))[sys.argv[2]]))" "$here/assets/previews/timestamps.json" "$s")"
  npx -y "$HF" snapshot "$demo" --at "$ats" --no-end --describe false --no-browser-gpu -o "$tmp/$s/snap" >"$tmp/$s.snap.log" 2>&1 \
    || { cat "$tmp/$s.snap.log" >&2; echo "snapshot failed for style $s" >&2; exit 1; }
  frames=( $(ls "$tmp/$s/snap"/*.png | sort -V) )
  args=(); for f in "${frames[@]}"; do args+=(-i "$f"); done
  if [[ ${#frames[@]} -gt 1 ]]; then
    ffmpeg -v error -y "${args[@]}" -filter_complex "$(for i in "${!frames[@]}"; do printf '[%d:v]scale=360:-1[v%d];' "$i" "$i"; done)$(for i in "${!frames[@]}"; do printf '[v%d]' "$i"; done)hstack=inputs=${#frames[@]}" -q:v 3 "$out/style-$s.jpg"
  else
    ffmpeg -v error -y "${args[@]}" -vf scale=360:-1 -q:v 3 "$out/style-$s.jpg"
  fi
  [[ -n "${KEEP_FRAMES:-}" ]] && { mkdir -p "$out/frames-$s"; cp "${frames[@]}" "$out/frames-$s/"; }
  rm -rf "$tmp/$s"
  echo "wrote $out/style-$s.jpg"
done
