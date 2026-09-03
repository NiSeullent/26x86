#!/bin/bash
# 26x86 — macOS double-click entry (wizard-first)
cd "$(dirname "$0")" || exit 1
exec python3 "$(dirname "$0")/26x86.py" wizard "$@"
