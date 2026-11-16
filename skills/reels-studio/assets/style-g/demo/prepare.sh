#!/usr/bin/env bash
# HyperFrames refuses asset paths that climb above the project root ("../"), so the demo gets local copies of
# the shared runtime + the Style G pack under demo/lib/ — the same names the assembler writes into
# work/<slug>/composition/lib/ for style "g".
# Run after every edit of the pack, before lint/snapshot/render. Delete demo/lib afterwards.
# scene-light.jpg is a procedural abstract placeholder (light streaks + embers, no people) standing in for the
# reels-art / connector generated scene of a real run.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
assets="$here/../.."
mkdir -p "$here/lib"
cp "$assets/shared/runtime.js"  "$here/lib/runtime.js"
cp "$assets/style-g/tokens.css" "$here/lib/tokens-g.css"
cp "$assets/style-g/lib.js"     "$here/lib/g.js"
echo "demo/lib ready (runtime + g)"
