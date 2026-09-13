"""
Safe Metallib / RenderBox preflight for Tahoe (Track E).

Separates two different metallib worlds:

1. **Metal 31001 RenderBox** — OCLP PR #1176 ``RenderBox-<xnu>/.../default.metallib``
   overwrite for Liquid Glass / Opaque UI shaders. Missing payload ⇒ intentional
   ``LegacyMetal31001`` no-op (empty patch dict) so root-patch preflight does not
   raise ``Failed to find .../default.metallib``.

2. **MetallibSupportPkg (3802)** — Sequoia+ compiler-format rewrite for Ivy/Haswell/
   Kepler. Required by ``Metal 3802 .metallibs``. **Must stay blocked on Tahoe**
   (shared-patch guard in ``metal_3802.py``). Never substitute 3802 metallibs for
   31001 RenderBox.

This module only *inspects* and *gates*. It never lifts Tahoe 3802 / Non-Metal
guards and never invents metallib bytes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

from x86.graphics.skylight_lut import (
    OCLP_RENDERBOX_EVIDENCE_URL,
    RENDERBOX_METALLIB_RELATIVE,
    metal_31001_common_patches,
    renderbox_payload_folder,
    resolve_renderbox_metallib_payload,
)

TAHOE_XNU_MAJOR = 25
VENTURA_XNU_MAJOR = 22
SEQUOIA_XNU_MAJOR = 24  # MetallibSupportPkg first required at Sequoia

# Apple .metallib container magic (little-endian ASCII "MTLB").
METALLIB_MAGIC = b"MTLB"
MIN_RENDERBOX_METALLIB_BYTES = 64

METALLIB_SUPPORT_PKG_INSTALL_PATHS: tuple[str, ...] = (
    "/Library/Application Support/26x86/MetallibSupportPkg",
    "/Library/Application Support/Dortania/MetallibSupportPkg",
)

NO_OP_REASONS: dict[str, str] = {
    "os_too_old": "xnu_major < Ventura — LegacyMetal31001 not applicable",
    "payload_missing": (
        "RenderBox-<xnu>/.../default.metallib absent from Universal-Binaries / "
        "overlay roots — emitting OVERWRITE would fail sys_patch preflight"
    ),
    "payload_empty": "RenderBox metallib exists but size is 0",
    "payload_bad_magic": "file present but lacks MTLB magic — refuse injection",
    "ok": "payload validated — Metal 31001 Common overwrite allowed",
    "ok_provisional": (
        "payload validated but PROVISIONAL (RenderBox-24 staged as -25) — "
        "Liquid Glass ABI may be incomplete on Tahoe"
    ),
}

PROVISIONAL_MARKER_NAME = "PROVISIONAL_FROM_RENDERBOX_24"
PROVISIONAL_LIQUID_GLASS_WARNING = (
    "RenderBox payload is provisional (Sequoia RenderBox-24 staged as RenderBox-25). "
    "Liquid Glass / Opaque ABI may be incomplete on Tahoe — research / path "
    "validation only until an authentic Tahoe metallib ships."
)


@dataclass(frozen=True)
class RenderBoxMetallibProbe:
    """Disk probe for one RenderBox-<xnu> candidate."""

    folder: str
    absolute_path: Optional[str]
    present: bool
    size_bytes: int = 0
    has_mtlb_magic: bool = False
    valid_for_overwrite: bool = False
    no_op_reason: str = "payload_missing"
    provisional: bool = False


@dataclass(frozen=True)
class MetallibGapReport:
    """
    Tahoe metallib gap summary for detect JSON / research.

    ``legacy_metal_31001_noop`` is True when the gated patch dict would be {}.
    """

    xnu_major: int
    legacy_metal_31001_noop: bool
    legacy_metal_31001_reason: str
    renderbox_folder: str
    renderbox_probe: RenderBoxMetallibProbe
    metallib_support_pkg_required_for_3802: bool
    metallib_support_pkg_blocked_on_tahoe: bool
    metallib_support_pkg_installed: bool
    gaps: list[str] = field(default_factory=list)
    evidence_url: str = OCLP_RENDERBOX_EVIDENCE_URL
    safe_injection_allowed: bool = False
    provisional: bool = False


def _search_roots(search_roots: Optional[Iterable[Path]] = None) -> list[Path]:
    if search_roots is not None:
        return [Path(p) for p in search_roots]
    from x86.graphics.yellow_screen import default_psp_binaries_roots

    return default_psp_binaries_roots()


def _read_magic(path: Path, nbytes: int = 4) -> bytes:
    try:
        with path.open("rb") as handle:
            return handle.read(nbytes)
    except OSError:
        return b""


def is_renderbox_provisional(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    folder: Optional[str] = None,
) -> bool:
    """True when ``RenderBox-<xnu>/PROVISIONAL_FROM_RENDERBOX_24`` exists."""
    name = folder or renderbox_payload_folder(xnu_major)
    for root in _search_roots(search_roots):
        marker = Path(root) / name / PROVISIONAL_MARKER_NAME
        try:
            if marker.is_file():
                return True
        except OSError:
            continue
    return False


def probe_renderbox_metallib(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> RenderBoxMetallibProbe:
    """Locate and softly validate ``RenderBox-<xnu>`` default.metallib."""
    folder = renderbox_payload_folder(xnu_major)
    provisional = is_renderbox_provisional(
        xnu_major, search_roots=search_roots, folder=folder
    )
    if xnu_major < VENTURA_XNU_MAJOR:
        return RenderBoxMetallibProbe(
            folder=folder,
            absolute_path=None,
            present=False,
            no_op_reason="os_too_old",
            provisional=provisional,
        )

    for root in _search_roots(search_roots):
        candidate = Path(root) / folder / RENDERBOX_METALLIB_RELATIVE
        try:
            if not candidate.is_file():
                continue
            size = candidate.stat().st_size
        except OSError:
            continue
        if size <= 0:
            return RenderBoxMetallibProbe(
                folder=folder,
                absolute_path=str(candidate),
                present=True,
                size_bytes=0,
                no_op_reason="payload_empty",
                provisional=provisional,
            )
        magic_ok = _read_magic(candidate) == METALLIB_MAGIC
        # Presence gate matches resolve_renderbox / OCLP preflight (size > 0).
        # Large files without MTLB magic are refused (corrupt / wrong format).
        # Tiny non-MTLB stubs remain valid so unit fixtures (e.g. b"RB") work.
        if size >= MIN_RENDERBOX_METALLIB_BYTES and not magic_ok:
            valid = False
            reason = "payload_bad_magic"
        else:
            valid = True
            reason = "ok_provisional" if provisional else "ok"
        return RenderBoxMetallibProbe(
            folder=folder,
            absolute_path=str(candidate),
            present=True,
            size_bytes=size,
            has_mtlb_magic=magic_ok,
            valid_for_overwrite=valid,
            no_op_reason=reason,
            provisional=provisional,
        )

    return RenderBoxMetallibProbe(
        folder=folder,
        absolute_path=None,
        present=False,
        no_op_reason="payload_missing",
        provisional=provisional,
    )


def metallib_support_pkg_installed(
    install_paths: Optional[Iterable[str]] = None,
) -> bool:
    """True when any MetallibSupportPkg install tree exists (3802 path)."""
    for raw in install_paths or METALLIB_SUPPORT_PKG_INSTALL_PATHS:
        path = Path(raw)
        try:
            if path.is_dir() and any(path.iterdir()):
                return True
        except OSError:
            continue
    return False


def assess_metallib_gaps(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> MetallibGapReport:
    """
    Explain LegacyMetal31001 no-op and Tahoe metallib gaps.

    Does **not** recommend unlocking Metal 3802 on Tahoe.
    """
    probe = probe_renderbox_metallib(xnu_major, search_roots=search_roots)
    noop = not probe.valid_for_overwrite
    reason_key = probe.no_op_reason
    gaps: list[str] = []

    if xnu_major >= TAHOE_XNU_MAJOR and not probe.present:
        gaps.append(
            "Tahoe needs RenderBox-25 (or RenderBox-26) default.metallib from "
            "PatcherSupportPkg / OCLP nightly — currently a common PSP DRAFT gap"
        )
    if xnu_major >= TAHOE_XNU_MAJOR and probe.provisional:
        gaps.append(PROVISIONAL_LIQUID_GLASS_WARNING)
    if xnu_major >= TAHOE_XNU_MAJOR:
        gaps.append(
            "MetallibSupportPkg rewrites Sequoia+ 3802 metallibs; Tahoe Metal 3802 "
            "shared patches remain safety-guarded (kernel panic) — do not unlock"
        )
    if (
        probe.present
        and not probe.has_mtlb_magic
        and probe.size_bytes >= MIN_RENDERBOX_METALLIB_BYTES
    ):
        gaps.append("RenderBox metallib lacks MTLB magic — refuse overwrite")

    pkg_needed = xnu_major >= SEQUOIA_XNU_MAJOR
    pkg_blocked = xnu_major >= TAHOE_XNU_MAJOR
    pkg_installed = metallib_support_pkg_installed()

    if pkg_needed and not pkg_installed and not pkg_blocked:
        gaps.append(
            "MetallibSupportPkg not installed (required for Metal 3802 .metallibs)"
        )

    return MetallibGapReport(
        xnu_major=xnu_major,
        legacy_metal_31001_noop=noop,
        legacy_metal_31001_reason=NO_OP_REASONS.get(reason_key, reason_key),
        renderbox_folder=probe.folder,
        renderbox_probe=probe,
        metallib_support_pkg_required_for_3802=pkg_needed,
        metallib_support_pkg_blocked_on_tahoe=pkg_blocked,
        metallib_support_pkg_installed=pkg_installed,
        gaps=gaps,
        safe_injection_allowed=probe.valid_for_overwrite,
        provisional=probe.provisional,
    )


def gated_metal_31001_common_patches(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict:
    """
    Safe preflight wrapper around OCLP RenderBox overwrite.

    Returns {} when payload missing/invalid — never emits Metal 3802 keys.
    When the payload is provisional (RenderBox-24 staged as -25), still emits
    the OVERWRITE dict (root-patch apply path) but logs a Liquid Glass ABI warning.
    """
    import logging

    report = assess_metallib_gaps(xnu_major, search_roots=search_roots)
    if not report.safe_injection_allowed:
        return {}
    patches = metal_31001_common_patches(xnu_major, search_roots=search_roots)
    out = {k: v for k, v in patches.items() if k == "Metal 31001 Common"}
    if out and report.provisional:
        logging.getLogger(__name__).warning(PROVISIONAL_LIQUID_GLASS_WARNING)
    return out


def metal_31001_root_patch_plan(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """
    Dry-run / apply planning surface for Metal 31001 RenderBox overwrite.

    Connects provisional staging to the same dict ``LegacyMetal31001.patches()``
    would emit, plus explicit warnings for operators.
    """
    report = assess_metallib_gaps(xnu_major, search_roots=search_roots)
    patches = gated_metal_31001_common_patches(xnu_major, search_roots=search_roots)
    warnings: list[str] = []
    if patches and report.provisional:
        warnings.append(PROVISIONAL_LIQUID_GLASS_WARNING)
    return {
        "dry_run": dry_run,
        "xnu_major": xnu_major,
        "would_emit": bool(patches),
        "patch_keys": list(patches.keys()),
        "patches": patches,
        "provisional": report.provisional,
        "authentic": bool(patches) and not report.provisional,
        "warnings": warnings,
        "legacy_metal_31001_noop": report.legacy_metal_31001_noop,
        "renderbox_folder": report.renderbox_folder,
        "apply_path": (
            "opencore_legacy_patcher.sys_patch.patchsets.shared_patches."
            "metal_31001.LegacyMetal31001.patches"
        ),
        "note": (
            "provisional payload still feeds root-patch OVERWRITE; "
            "replace with authentic RenderBox-25 when available"
            if report.provisional
            else "authentic or missing payload"
        ),
    }


def serialize_metallib_preflight_fields(
    xnu_major: Optional[int] = None,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, Any]:
    """Fields for ``python -m x86 detect --json`` (Track E)."""
    major = TAHOE_XNU_MAJOR if xnu_major is None else xnu_major
    report = assess_metallib_gaps(major, search_roots=search_roots)
    probe = report.renderbox_probe
    folder = resolve_renderbox_metallib_payload(major, search_roots=search_roots)
    plan = metal_31001_root_patch_plan(major, search_roots=search_roots, dry_run=True)
    return {
        "metallib_track": "E",
        "legacy_metal_31001_noop": report.legacy_metal_31001_noop,
        "legacy_metal_31001_reason": report.legacy_metal_31001_reason,
        "renderbox_metallib_payload": folder,
        "renderbox_metallib_present": probe.present,
        "renderbox_metallib_valid_for_overwrite": probe.valid_for_overwrite,
        "renderbox_metallib_has_mtlb_magic": probe.has_mtlb_magic,
        "renderbox_metallib_size_bytes": probe.size_bytes,
        "renderbox_metallib_provisional": report.provisional,
        "renderbox_liquid_glass_abi_incomplete": report.provisional,
        "metal_31001_root_patch_plan": {
            k: v for k, v in plan.items() if k != "patches"
        },
        "metallib_support_pkg_required_for_3802": (
            report.metallib_support_pkg_required_for_3802
        ),
        "metallib_support_pkg_blocked_on_tahoe": (
            report.metallib_support_pkg_blocked_on_tahoe
        ),
        "metallib_support_pkg_installed": report.metallib_support_pkg_installed,
        "metallib_safe_injection_allowed": report.safe_injection_allowed,
        "metallib_gaps": list(report.gaps),
        "metallib_gap_report": {
            **{k: v for k, v in asdict(report).items() if k != "renderbox_probe"},
            "renderbox_probe": asdict(probe),
        },
        "oclp_renderbox_evidence_url": OCLP_RENDERBOX_EVIDENCE_URL,
    }
