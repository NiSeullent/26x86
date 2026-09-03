#!/bin/bash
# PyInstaller build entry — end users should use 26x86.command
cd "$(dirname "$0")" || exit 1
exec python3 "$(dirname "$0")/26x86.py" wizard "$@"
