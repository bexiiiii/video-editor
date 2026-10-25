#!/usr/bin/env bash
# HyperFrames refuses asset paths that climb above the project root ("../"), so the demo gets local copies of
# the shared runtime + Style A + Style D packs under demo/lib/ — the same names the assembler writes into
# work/<slug>/composition/lib/ for style "d" (load order a → d; D is Style A over the talking head).
# Run after every edit of any pack, before lint/snapshot/render. Delete demo/lib afterwards.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
assets="$here/../.."
mkdir -p "$here/lib"
cp "$assets/shared/runtime.js"  "$here/lib/runtime.js"
cp "$assets/style-a/tokens.css" "$here/lib/tokens-a.css"
cp "$assets/style-a/lib.js"     "$here/lib/a.js"
cp "$assets/style-d/tokens.css" "$here/lib/tokens-d.css"
cp "$assets/style-d/lib.js"     "$here/lib/d.js"
echo "demo/lib ready (runtime + a + d)"
