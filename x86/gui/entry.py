"""Portable GUI packaging entry; never starts the macOS legacy application on Windows."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-report", type=Path, help="Write a backend smoke report without opening a window")
    parser.add_argument("--gui-smoke-report", type=Path, help="Open the native window, verify its DOM and close it")
    parser.add_argument("--profile", choices=["surface-pro6-i5-tahoe"], help="Lock the GUI to this target, independent of the preparation host")
    parser.add_argument("--efi", type=Path, help="Pre-fill the Surface EFI validation directory; no automatic disk writes")
    args = parser.parse_args()
    if args.profile:
        os.environ["X86_TARGET_PROFILE"] = args.profile
    if args.efi:
        os.environ["X86_SURFACE_EFI"] = str(args.efi)
    from x86.gui.webview_app import _ensure_stdio_for_frozen_gui, smoke_test_bridge, launch_webview_wizard, _launch_pywebview_wizard
    _ensure_stdio_for_frozen_gui()
    if args.smoke_report:
        report = smoke_test_bridge()
        args.smoke_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if report["ok"] else 1
    if args.gui_smoke_report:
        _launch_pywebview_wizard(advanced=False, requested="auto", smoke_report=args.gui_smoke_report)
        if not args.gui_smoke_report.exists():
            return 1
        return 0 if json.loads(args.gui_smoke_report.read_text(encoding="utf-8")).get("ok") else 1
    launch_webview_wizard()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
