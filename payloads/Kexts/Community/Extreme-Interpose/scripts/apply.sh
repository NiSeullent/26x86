#!/bin/bash
# Track I apply: build → staging/SkyLightPlugins copy → guide.
# Requires X86_EXTREME=1. Optional --live-library needs X86_EXTREME_INSTALL=1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT"
if [[ "${X86_EXTREME:-}" != "1" && "${X86_EXTREME:-}" != "true" ]]; then
  echo "Set X86_EXTREME=1" >&2
  exit 2
fi
exec python3 -m x86.graphics.interpose_apply "$@"
