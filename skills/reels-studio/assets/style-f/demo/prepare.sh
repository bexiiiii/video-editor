#!/usr/bin/env bash
# HyperFrames refuses asset paths that climb above the project root ("../"), so the demo gets local copies of
# the shared runtime + the Style F pack under demo/lib/ — the same names the assembler writes into
# work/<slug>/composition/lib/ for style "f".
# Run after every edit of the pack, before lint/snapshot/render. Delete demo/lib afterwards.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
assets="$here/../.."
mkdir -p "$here/lib"
cp "$assets/shared/runtime.js"  "$here/lib/runtime.js"
cp "$assets/style-f/tokens.css" "$here/lib/tokens-f.css"
cp "$assets/style-f/lib.js"     "$here/lib/f.js"
echo "demo/lib ready (runtime + f)"
