"""
Track H — combined IOSurface + QuartzCore extreme hooks (no shared-tree edits).

MC promote (base INTEGRATE ``52f7298``): see
``tahoe_iosurface_ca.py.stage-H`` + ``MC-PROMOTE-H.md.stage-H``.
Parallel with Track N is allowed (same IOSurface/QC payload IDs = idempotent);
IOAccel ``IOSurface.kext=10.14.6`` vs H ``10.15.7`` is noted for MC resolve.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional

from .coreanimation_analysis import serialize_coreanimation_fields
from .coreanimation_extreme import (
    extreme_boot_combination,
    extreme_coreanimation_merge_patches,
    extreme_coreanimation_status,
)
from .iosurface_analysis import serialize_iosurface_fields
from .iosurface_extreme import extreme_iosurface_merge_patches, extreme_iosurface_status


def iosurface_ca_extreme_patches(
    xnu_major: int,
    xnu_minor: int = 0,
    marketing_version: str = "",
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    del xnu_minor, marketing_version
    return {
        **extreme_iosurface_merge_patches(xnu_major, search_roots=search_roots, environ=environ),
        **extreme_coreanimation_merge_patches(xnu_major, search_roots=search_roots, environ=environ),
    }


def serialize_iosurface_ca_fields(
    xnu_major: Optional[int] = None,
    *,
    has_metal_amd: bool = True,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    major = 25 if xnu_major is None else int(xnu_major)
    payload: dict[str, Any] = {}
    payload.update(
        serialize_iosurface_fields(
            major, has_metal_amd=has_metal_amd, search_roots=search_roots, environ=environ
        )
    )
    payload.update(
        serialize_coreanimation_fields(
            major, has_metal_amd=has_metal_amd, search_roots=search_roots, environ=environ
        )
    )
    payload["iosurface_ca_extreme"] = {
        "iosurface": extreme_iosurface_status(major, search_roots=search_roots, environ=environ),
        "coreanimation": extreme_coreanimation_status(
            major, search_roots=search_roots, environ=environ
        ),
        "boot_combination": extreme_boot_combination(environ=environ),
        "would_emit_root_patches": bool(
            iosurface_ca_extreme_patches(major, search_roots=search_roots, environ=environ)
        ),
        "parallel_track_n": {
            "allowed": True,
            "integrate_base": "52f7298",
            "idempotent_overlap": [
                "IOSurface.kext=10.15.7",
                "IOSurface.framework=10.15.7-24",
                "QuartzCore.framework=10.15.7-24",
            ],
            "conflict_note": (
                "N IOAccel may use IOSurface.kext=10.14.6; prefer 10.15.7 when H latch on"
            ),
        },
    }
    return payload
