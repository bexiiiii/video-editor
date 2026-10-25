#!/usr/bin/env bash
# Copy the Style B library into demo/lib/ — HyperFrames rejects asset paths that traverse above the
# project root ("../"), so the demo (like an assembled composition) loads local copies:
#   lib/tokens-style-b.css  lib/runtime.js  lib/style-b.js
# Run after every edit of tokens.css / lib.js / shared/runtime.js, before lint/snapshot/render.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$here/lib"
cp "$here/../tokens.css" "$here/lib/tokens-style-b.css"
cp "$here/../lib.js" "$here/lib/style-b.js"
cp "$here/../../shared/runtime.js" "$here/lib/runtime.js"
echo "copied Style B lib → $here/lib"
