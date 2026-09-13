#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DYLIB="$ROOT/build/libExtremeCompositorInterpose.dylib"
truthy() { case "${1:-}" in 1|true|TRUE|yes|YES|on|ON) return 0 ;; *) return 1 ;; esac; }
if ! truthy "${X86_EXTREME:-}"; then echo "Refusing: set X86_EXTREME=1" >&2; exit 2; fi
if ! truthy "${X86_EXTREME_INSTALL:-}"; then
  echo "Refusing: set X86_EXTREME_INSTALL=1" >&2; exit 2
fi
if [[ ! -f "$DYLIB" ]]; then echo "Missing $DYLIB — run scripts/build.sh" >&2; exit 1; fi
TARGET="${1:-}"
if [[ -z "$TARGET" ]]; then
  echo "Usage: X86_EXTREME=1 X86_EXTREME_INSTALL=1 $0 /path/to/binary" >&2
  exit 1
fi
export X86_EXTREME=1
export DYLD_INSERT_LIBRARIES="$DYLIB"
exec "$TARGET"
