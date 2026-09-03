#!/usr/bin/env python3
"""
26x86 root entry point → x86.cli
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from x86.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
