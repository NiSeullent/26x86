"""
Track H — Extreme IOSurface userland merge PoC (X86_EXTREME).

Default: emit nothing. Double latch X86_EXTREME=1 + X86_EXTREME_IOSURFACE_CA=1
plus payload on disk → surgical IOSurface.framework MERGE only.
Never REMOVE IOGPU, never useMetal=no, never overwrite IOSurface.kext.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional

from .iosurface_analysis import (
    TAHOE_XNU_MAJOR,
    analyze_iosurface_gates,
    is_extreme_enabled,
    is_extreme_iosurface_ca_opt_in,
    resolve_iosurface_framework_payload,
)

EXTREME_IOSURFACE_PATCH_NAME = "Track H Extreme IOSurface Framework (opt-in)"


def extreme_iosurface_merge_patches(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    if xnu_major < TAHOE_XNU_MAJOR:
        return {}
    if not is_extreme_iosurface_ca_opt_in(environ):
        return {}
    folder = resolve_iosurface_framework_payload(xnu_major, search_roots=search_roots)
    if folder is None:
        return {}
    from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType
    return {
        EXTREME_IOSURFACE_PATCH_NAME: {
            PatchType.MERGE_SYSTEM_VOLUME: {
                "/System/Library/Frameworks": {"IOSurface.framework": folder},
            },
        },
    }


def extreme_iosurface_status(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    report = analyze_iosurface_gates(xnu_major, has_metal_amd=True, search_roots=search_roots)
    patches = extreme_iosurface_merge_patches(xnu_major, search_roots=search_roots, environ=environ)
    return {
        "extreme_enabled": is_extreme_enabled(environ),
        "extreme_iosurface_ca_opt_in": is_extreme_iosurface_ca_opt_in(environ),
        "would_emit_merge": bool(patches),
        "patch_name": EXTREME_IOSURFACE_PATCH_NAME if patches else None,
        "payload_folder": report.framework_payload,
        "payload_present": report.payload_framework_present,
        "full_non_metal_still_blocked": True,
        "notes": [
            "Full Non-Metal Common (IOGPU REMOVE + IOSurface.kext) stays blocked.",
            *report.notes,
        ],
    }
