#!/usr/bin/env bash
# HyperFrames refuses asset paths that climb above the project root ("../"), so the demo gets local copies of
# the shared runtime + Style A + Style B + Style C packs under demo/lib/ — the same names the assembler writes
# into work/<slug>/composition/lib/ for style "c" (load order a → b → c).
# Run after every edit of any pack, before lint/snapshot/render. Delete demo/lib afterwards.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
assets="$here/../.."
mkdir -p "$here/lib"
cp "$assets/shared/runtime.js"   "$here/lib/runtime.js"
cp "$assets/style-a/tokens.css"  "$here/lib/tokens-a.css"
cp "$assets/style-a/lib.js"      "$here/lib/a.js"
cp "$assets/style-b/tokens.css"  "$here/lib/tokens-b.css"
cp "$assets/style-b/lib.js"      "$here/lib/b.js"
cp "$assets/style-c/tokens.css"  "$here/lib/tokens-c.css"
cp "$assets/style-c/lib.js"      "$here/lib/c.js"
echo "demo/lib ready (runtime + a + b + c)"
