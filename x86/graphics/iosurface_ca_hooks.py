"""
Track H — combined IOSurface + QuartzCore extreme hooks (no shared-tree edits).

Live sys_patch wiring is proposed only via
``tahoe_iosurface_ca.py.stage-H`` / ``amd_*_patches.stage-H`` for Mission Control
merge — this module itself is import-safe and default no-op.
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
    }
    return payload
