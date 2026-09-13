"""
Track H — Extreme Non-Metal IOSurface PoC (double latch).

Default: emit nothing.
``X86_EXTREME=1`` + ``X86_EXTREME_IOSURFACE_CA=1`` + payloads on disk:
  - MERGE IOSurface.framework (Sequoia-capped Non-Metal userland)
  - OVERWRITE IOSurface.kext when ``10.15.7`` payload exists

No permanent blocked path. KP / ABI risk is the operator's under extreme.
Does not write ``useMetal=no`` (Enforcement stays out of Track H).
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
    resolve_iosurface_kext_payload,
)

EXTREME_IOSURFACE_PATCH_NAME = "Track H Extreme Non-Metal IOSurface (opt-in)"


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

    framework = resolve_iosurface_framework_payload(xnu_major, search_roots=search_roots)
    kext = resolve_iosurface_kext_payload(search_roots=search_roots)
    if framework is None and kext is None:
        return {}

    from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType

    body: dict[str, Any] = {}
    if framework is not None:
        body.setdefault(PatchType.MERGE_SYSTEM_VOLUME, {})
        body[PatchType.MERGE_SYSTEM_VOLUME]["/System/Library/Frameworks"] = {
            "IOSurface.framework": framework,
        }
    if kext is not None:
        body.setdefault(PatchType.OVERWRITE_SYSTEM_VOLUME, {})
        body[PatchType.OVERWRITE_SYSTEM_VOLUME]["/System/Library/Extensions"] = {
            "IOSurface.kext": kext,
        }
    return {EXTREME_IOSURFACE_PATCH_NAME: body}


def extreme_iosurface_status(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    report = analyze_iosurface_gates(
        xnu_major,
        has_metal_amd=True,
        search_roots=search_roots,
        environ=environ,
    )
    patches = extreme_iosurface_merge_patches(
        xnu_major, search_roots=search_roots, environ=environ
    )
    return {
        "extreme_enabled": is_extreme_enabled(environ),
        "extreme_iosurface_ca_opt_in": is_extreme_iosurface_ca_opt_in(environ),
        "non_metal_iosurface_experiment_open": report.non_metal_iosurface_experiment_open,
        "would_emit_merge": bool(patches),
        "patch_name": EXTREME_IOSURFACE_PATCH_NAME if patches else None,
        "payload_folder": report.framework_payload,
        "payload_present": report.payload_framework_present,
        "kext_payload": report.kext_payload,
        "kext_payload_present": report.payload_kext_present,
        "notes": list(report.notes),
    }
