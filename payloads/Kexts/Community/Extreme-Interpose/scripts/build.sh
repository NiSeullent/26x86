#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
make clean
make all
make plugin
ls -la "$ROOT/build"
shasum -a 256 "$ROOT/build/"*.dylib 2>/dev/null || true
