#!/usr/bin/env python3
"""
Probe extreme Tahoe payloads (RenderBox-25 + L5 SkyLight/CoreDisplay Mach-O).

Never invents binaries. Missing → print acquire notes / exit 2 (soft fail for CI
gates that only need documentation). Exit 0 when L5 Mach-Os ready **and**
RenderBox-25 validates (authentic or provisional-from-24 staging).

Use ``--allow-renderbox-gap`` only when intentionally skipping Track E metallib.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _provisional_marker_present() -> bool:
    from x86.graphics.yellow_screen import default_psp_binaries_roots

    for root in default_psp_binaries_roots():
        marker = Path(root) / "RenderBox-25" / "PROVISIONAL_FROM_RENDERBOX_24"
        if marker.is_file():
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    allow_rb = "--allow-renderbox-gap" in args
    from x86.graphics.metallib_renderbox import renderbox_gap_status
    from x86.graphics.skylight_lut_rootpatch import probe_l5_macho_payloads

    rb = renderbox_gap_status(25)
    l5 = probe_l5_macho_payloads(25)
    provisional = _provisional_marker_present()
    payload = {
        "renderbox": rb,
        "l5_macho": l5,
        "l5_ready": bool(l5.get("ready_for_overwrite")),
        "renderbox_ready": bool(rb.get("valid_for_overwrite")),
        "renderbox_provisional": provisional,
        "fetch_hint": "python Tools/fetch_renderbox25.py [--provisional-from-24]",
    }
    print(json.dumps(payload, indent=2, default=str))
    if not payload["l5_ready"]:
        print(
            "\n# L5 Mach-O missing — update sibling 26x86-PatcherSupportPkg "
            "Universal-Binaries (10.14.6-24 / 10.14.4-24).",
            file=sys.stderr,
        )
        return 2
    if not payload["renderbox_ready"] and not allow_rb:
        print(
            "\n# RenderBox-25 gap. Try:\n"
            "  python Tools/fetch_renderbox25.py\n"
            "  python Tools/fetch_renderbox25.py --provisional-from-24\n"
            "See docs/EXTREME-TAHOE-VALIDATION.md",
            file=sys.stderr,
        )
        return 3
    if payload["renderbox_ready"] and provisional:
        print(
            "\n# NOTE: RenderBox-25 is provisional (copied from RenderBox-24). "
            "Authentic Tahoe metallib still unpublished on public PSP mirrors.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
