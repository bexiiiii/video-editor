#!/usr/bin/env bash
# Rebuild assets/previews/style-<x>.jpg from a demo: make_previews.sh <style> <demo.mp4> t1 t2 t3 t4
# Pick timestamps where every text is fully revealed and no transition is running.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
style="$1"; demo="$2"; shift 2
tmp="$(mktemp -d)"; args=(); i=0
for t in "$@"; do
  ffmpeg -v error -y -ss "$t" -i "$demo" -frames:v 1 -vf scale=360:-1 "$tmp/$i.png"
  args+=(-i "$tmp/$i.png"); i=$((i+1))
done
ffmpeg -v error -y "${args[@]}" -filter_complex "hstack=inputs=$i" -q:v 3 "$here/assets/previews/style-$style.jpg"
rm -r "$tmp"
echo "wrote assets/previews/style-$style.jpg"
