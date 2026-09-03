"""
Track H — Extreme QuartzCore / CoreAnimation userland merge PoC.

Latch: X86_EXTREME=1 + X86_EXTREME_IOSURFACE_CA=1 + payload present.
Merges QuartzCore.framework only; never Metal 3802 metallib / Enforcement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional

from .coreanimation_analysis import (
    analyze_coreanimation_gates,
    metal_vega_boot_args,
    resolve_quartzcore_framework_payload,
)
from .iosurface_analysis import (
    TAHOE_XNU_MAJOR,
    is_extreme_enabled,
    is_extreme_iosurface_ca_opt_in,
)

EXTREME_COREANIMATION_PATCH_NAME = "Track H Extreme QuartzCore Framework (opt-in)"


def extreme_coreanimation_merge_patches(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    if xnu_major < TAHOE_XNU_MAJOR:
        return {}
    if not is_extreme_iosurface_ca_opt_in(environ):
        return {}
    folder = resolve_quartzcore_framework_payload(xnu_major, search_roots=search_roots)
    if folder is None:
        return {}
    from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType
    return {
        EXTREME_COREANIMATION_PATCH_NAME: {
            PatchType.MERGE_SYSTEM_VOLUME: {
                "/System/Library/Frameworks": {"QuartzCore.framework": folder},
            },
        },
    }


def extreme_boot_combination(*, environ: Optional[dict[str, str]] = None) -> dict[str, Any]:
    return {
        "x86_extreme": is_extreme_enabled(environ),
        "boot_args": list(metal_vega_boot_args()),
        "avoid_boot_args": ["-igfxvesa", "ngfxgl=1"],
        "avoid_defaults": [
            "defaults write … com.apple.CoreDisplay useMetal -boolean no",
            "defaults write … com.apple.CoreDisplay useIOP -boolean no",
        ],
        "notes": [
            "agdpmod remains the primary AGDC yellow mitigation (Track D / EFI).",
            "QuartzCore merge is ABI-experimental; expect WindowServer crash if mismatched.",
        ],
    }


def extreme_coreanimation_status(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    report = analyze_coreanimation_gates(xnu_major, has_metal_amd=True, search_roots=search_roots)
    patches = extreme_coreanimation_merge_patches(xnu_major, search_roots=search_roots, environ=environ)
    return {
        "extreme_enabled": is_extreme_enabled(environ),
        "extreme_iosurface_ca_opt_in": is_extreme_iosurface_ca_opt_in(environ),
        "would_emit_merge": bool(patches),
        "patch_name": EXTREME_COREANIMATION_PATCH_NAME if patches else None,
        "payload_folder": report.framework_payload,
        "payload_present": report.payload_framework_present,
        "boot_combination": extreme_boot_combination(environ=environ),
        "full_non_metal_still_blocked": True,
        "notes": list(report.notes),
    }
