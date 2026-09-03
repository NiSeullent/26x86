"""
Track E — RenderBox / Metal 31001 metallib soft-import surface.

Wraps ``metallib_preflight`` + ``skylight_lut`` so Track G can resolve
``x86.graphics.metallib_renderbox`` (see ``skylight_tracks.TRACK_MODULE_CANDIDATES``).

Never invents ``.metallib`` bytes. Tahoe without ``RenderBox-25`` stays a
documented no-op; acquisition is ``Tools/check_extreme_payloads.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional

from x86.graphics.metallib_opaque import serialize_opaque_shader_fields
from x86.graphics.metallib_preflight import (
    TAHOE_XNU_MAJOR,
    assess_metallib_gaps,
    gated_metal_31001_common_patches,
    metal_31001_root_patch_plan,
    probe_renderbox_metallib,
    serialize_metallib_preflight_fields,
)
from x86.graphics.skylight_lut import (
    OCLP_RENDERBOX_EVIDENCE_URL,
    RENDERBOX_METALLIB_RELATIVE,
    TAHOE_RENDERBOX_PAYLOAD_DIRS,
    renderbox_payload_folder,
    resolve_renderbox_metallib_payload,
)

# Acquisition hints (no auto-download of proprietary blobs).
RENDERBOX_ACQUIRE_DOC = "docs/EXTREME-TAHOE-VALIDATION.md"
RENDERBOX_ACQUIRE_NOTES: tuple[str, ...] = (
    "PatcherSupportPkg DRAFT / OCLP nightly often ships RenderBox-25 late.",
    "Do not substitute MetallibSupportPkg 3802 rewrites for 31001 RenderBox.",
    "Copying RenderBox-24 → RenderBox-25 is ABI-unsafe research only.",
    f"Evidence: {OCLP_RENDERBOX_EVIDENCE_URL}",
)


def renderbox_gap_status(
    xnu_major: int = TAHOE_XNU_MAJOR,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, Any]:
    """Human/automation status for Tahoe RenderBox-25 gap."""
    report = assess_metallib_gaps(xnu_major, search_roots=search_roots)
    probe = report.renderbox_probe
    plan = metal_31001_root_patch_plan(
        xnu_major, search_roots=search_roots, dry_run=True
    )
    return {
        "track": "E",
        "xnu_major": xnu_major,
        "expected_folder": renderbox_payload_folder(xnu_major),
        "tahoe_dirs": list(TAHOE_RENDERBOX_PAYLOAD_DIRS),
        "present": probe.present,
        "valid_for_overwrite": probe.valid_for_overwrite,
        "provisional": report.provisional,
        "liquid_glass_abi_incomplete": report.provisional,
        "noop": report.legacy_metal_31001_noop,
        "reason": report.legacy_metal_31001_reason,
        "gaps": list(report.gaps),
        "acquire_doc": RENDERBOX_ACQUIRE_DOC,
        "acquire_notes": list(RENDERBOX_ACQUIRE_NOTES),
        "metallib_relative": RENDERBOX_METALLIB_RELATIVE,
        "resolved_folder": resolve_renderbox_metallib_payload(
            xnu_major, search_roots=search_roots
        ),
        "root_patch_plan": {
            k: v for k, v in plan.items() if k != "patches"
        },
    }


def sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int = 0,
    marketing_version: str = "",
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, Any]:
    """
    Track G contract — emit Metal 31001 Common only when RenderBox payload is valid.

    Provisional RenderBox-24→25 still emits (same as LegacyMetal31001 root path)
    with ABI warnings via ``metal_31001_root_patch_plan`` / logging.
    Always empty on missing ``RenderBox-<xnu>`` (safe preflight).
    """
    del xnu_minor, marketing_version
    return gated_metal_31001_common_patches(xnu_major, search_roots=search_roots)


def serialize_track_detect_fields(
    xnu_major: Optional[int] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Track G detect serializer (+ opaque relationship)."""
    major = TAHOE_XNU_MAJOR if xnu_major is None else int(xnu_major)
    search_roots = kwargs.get("search_roots")
    payload = serialize_metallib_preflight_fields(
        major, search_roots=search_roots
    )
    payload.update(
        serialize_opaque_shader_fields(
            renderbox_metallib_present=bool(
                payload.get("renderbox_metallib_present")
            ),
            legacy_metal_31001_noop=bool(
                payload.get("legacy_metal_31001_noop", True)
            ),
            provisional_renderbox=bool(
                payload.get("renderbox_metallib_provisional")
            ),
        )
    )
    payload["renderbox_track_e"] = renderbox_gap_status(
        major, search_roots=search_roots
    )
    return payload


def serialize_metallib_fields(
    xnu_major: Optional[int] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Alias used by ``skylight_tracks`` optional detect merge."""
    return serialize_track_detect_fields(xnu_major, **kwargs)


__all__ = (
    "RENDERBOX_ACQUIRE_DOC",
    "RENDERBOX_ACQUIRE_NOTES",
    "TAHOE_XNU_MAJOR",
    "gated_metal_31001_common_patches",
    "metal_31001_root_patch_plan",
    "probe_renderbox_metallib",
    "renderbox_gap_status",
    "serialize_metallib_fields",
    "serialize_track_detect_fields",
    "sys_patch_hooks",
)
