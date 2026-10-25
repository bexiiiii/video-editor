#!/usr/bin/env bash
# HyperFrames refuses asset paths that climb above the project root ("../"), so the demo
# gets local copies of the shared runtime + Style A tokens/lib under demo/lib/ — the same
# layout the assembler produces in work/<slug>/composition/lib/ (contracts.md).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$here/lib"
cp "$here/../../shared/runtime.js" "$here/lib/runtime.js"
cp "$here/../tokens.css"           "$here/lib/tokens-a.css"
cp "$here/../lib.js"               "$here/lib/a.js"
echo "demo/lib ready"
