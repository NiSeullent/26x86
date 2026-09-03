#!/bin/bash
# DEPRECATED: use 26x86.command or bin/26x86 instead.
echo "[경고] OpenCore-Patcher-GUI.command는 deprecated. 26x86.command를 사용하세요." >&2
cd "$(dirname "$0")" || exit 1
exec python3 "$(dirname "$0")/26x86.py" wizard "$@"
