#!/usr/bin/env python3
"""
PyInstaller Entry Point - Hardened with Full Extraction Fix
"""
import sys
import logging
import os
import zipfile
import shutil
import subprocess
from pathlib import Path

# Fast path: show CLI help without loading the full GUI stack
if "--help" in sys.argv or "-h" in sys.argv:
    _lang = "en"
    for i, arg in enumerate(sys.argv):
        if arg == "--lang" and i + 1 < len(sys.argv):
            _lang = sys.argv[i + 1]
            break
        if arg.startswith("--lang="):
            _lang = arg.split("=", 1)[1]
            break
    if _lang not in ("ko", "en"):
        _lang = "en"
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import importlib.util
    _cli_path = Path(__file__).resolve().parent / "opencore_legacy_patcher" / "support" / "cli.py"
    _spec = importlib.util.spec_from_file_location("oclp_cli", _cli_path)
    _cli_mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_cli_mod)
    _cli_mod.build_parser(_lang).print_help()
    sys.exit(0)

# SECURITY FIX: Remove the current directory from the search path.
if "" in sys.path:
    sys.path.remove("")

# We configure logging to write to sys.stdout (the Terminal window)
logging.basicConfig(
    level=logging.ERROR,
    format='%(message)s', # Keep it clean for the Terminal
    stream=sys.stdout
)

from opencore_legacy_patcher import main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("\n" + "="*60)
        logging.error("Whoops, the app crashed because of the following error:")
        print(f"Direct Error: {e}")
        print("-" * 60)
        logging.exception("Stack Trace:")
        print("="*60)
        input("\nPress ENTER to close this window...")
        sys.exit(3)
