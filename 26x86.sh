#!/usr/bin/env bash
# 26x86 — Linux entry (wizard-first)
cd "$(dirname "$0")" || exit 1
exec python3 -m x86 wizard "$@"
