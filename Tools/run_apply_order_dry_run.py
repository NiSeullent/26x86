#!/usr/bin/env python3
"""Dry-run EFI→root→yellow→extreme apply order for macpro5-vega64-tahoe."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.extreme.apply_order import main

if __name__ == "__main__":
    raise SystemExit(main(["--extreme", *sys.argv[1:]]))
