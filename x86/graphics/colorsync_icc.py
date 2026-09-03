"""
Tahoe ColorSync / ICC / gamma / LUT (Track C — dedicated module).

Evidence: OCLP-T2 #194 ICC/LUT; Apple ColorSync layout;
``CGDisplayRestoreColorSyncSettings``. GPU-agnostic (Vega 64 unpublished).

Track G contract (``skylight_tracks``):
- ``sys_patch_hooks(xnu_major, xnu_minor, marketing_version)``
- ``serialize_track_detect_fields()``
Also exposes ``colorsync_lut_execute_patches`` for G soft-adapt path.

Never: useMetal=no, CoreDisplay/SkyLight byte patches, Metal 3802 / Non-Metal
Tahoe guard lift. Extreme (``X86_EXTREME``) does not unlock Non-Metal here.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Optional

OCLP_T2_YELLOW_SCREEN_ISSUE = (
    "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194"
)

SYSTEM_SRGB_ICC = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"
DISPLAY_PROFILES_DIR = "/Library/ColorSync/Profiles/Displays"
DISPLAY_SRGB_LINK = f"{DISPLAY_PROFILES_DIR}/sRGB Profile.icc"
COLORSYNCD_CACHE_DIR = "/Library/Caches/com.apple.colorsyncd"

PUBLIC_COLORSYNC_NEEDLES: tuple[str, ...] = (
    "ColorSyncProfileCreateWithURL",
    "ColorSyncTransformCreate",
    "CGColorSpaceCreateWithICCData",
    "CGColorSpaceCreateWithName",
    "CGDisplayGammaTable",
    "CGDisplayRestoreColorSyncSettings",
)

COLORSYNC_LUT_EXECUTE_COMMANDS: tuple[str, ...] = (
    f"/bin/rm -rf {COLORSYNCD_CACHE_DIR}",
    f"/bin/mkdir -p {DISPLAY_PROFILES_DIR}",
)

COLORSYNC_LUT_MITIGATION_MARKER = "colorsync_lut_deep"


def colorsync_lut_mitigation_marker() -> str:
    return COLORSYNC_LUT_MITIGATION_MARKER


def colorsync_lut_execute_patches() -> dict[str, bool]:
    """Evidence-backed EXECUTE map (colorsyncd cache + Displays mkdir)."""
    return {cmd: True for cmd in COLORSYNC_LUT_EXECUTE_COMMANDS}


def restore_display_colorsync_settings() -> bool:
    """Public ``CGDisplayRestoreColorSyncSettings`` — tint/gamma soft reset."""
    if sys.platform != "darwin":
        return False
    try:
        from Quartz import CGDisplayRestoreColorSyncSettings  # type: ignore
    except Exception:
        return False
    try:
        CGDisplayRestoreColorSyncSettings()
        logging.info("colorsync_icc: CGDisplayRestoreColorSyncSettings applied")
        return True
    except Exception as exc:
        logging.warning("colorsync_icc: gamma restore failed: %s", exc)
        return False


def purge_non_srgb_display_icc_overrides(
    displays_dir: Optional[Path] = None,
) -> list[str]:
    """Remove non-sRGB files under Displays/ (keep sRGB Profile.icc)."""
    directory = Path(displays_dir) if displays_dir is not None else Path(DISPLAY_PROFILES_DIR)
    removed: list[str] = []
    try:
        if not directory.is_dir():
            return removed
        for path in directory.iterdir():
            if not path.is_file() and not path.is_symlink():
                continue
            if path.name == "sRGB Profile.icc":
                continue
            try:
                path.unlink()
                removed.append(str(path))
            except OSError as exc:
                logging.warning("colorsync_icc: could not remove %s: %s", path, exc)
    except OSError as exc:
        logging.warning("colorsync_icc: Displays/ scan failed: %s", exc)
    return removed


def apply_colorsync_lut_deep_mitigations(*, restore_gamma: bool = True) -> dict[str, Any]:
    result: dict[str, Any] = {
        "purged_display_icc": [],
        "gamma_restored": False,
        "system_srgb_present": False,
    }
    try:
        result["system_srgb_present"] = Path(SYSTEM_SRGB_ICC).is_file()
    except OSError:
        pass
    result["purged_display_icc"] = purge_non_srgb_display_icc_overrides()
    if restore_gamma:
        result["gamma_restored"] = restore_display_colorsync_settings()
    return result


def serialize_colorsync_fields(*, probe_host: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "colorsync_srgb_system_icc": SYSTEM_SRGB_ICC,
        "colorsync_display_profiles_dir": DISPLAY_PROFILES_DIR,
        "colorsync_lut_execute_commands": list(COLORSYNC_LUT_EXECUTE_COMMANDS),
        "colorsync_gamma_restore_api": "CGDisplayRestoreColorSyncSettings",
        "colorsync_yellow_screen_issue_url": OCLP_T2_YELLOW_SCREEN_ISSUE,
        "colorsync_gpu_agnostic": True,
        "colorsync_never_usemetal_no": True,
        "colorsync_extreme_does_not_unlock_nonmetal": True,
    }
    if probe_host and sys.platform == "darwin":
        host: dict[str, Any] = {
            "system_srgb_present": False,
            "display_srgb_linked": False,
            "display_icc_overrides": [],
        }
        try:
            host["system_srgb_present"] = Path(SYSTEM_SRGB_ICC).is_file()
        except OSError:
            pass
        try:
            link = Path(DISPLAY_SRGB_LINK)
            host["display_srgb_linked"] = link.is_file() or link.is_symlink()
        except OSError:
            pass
        try:
            displays = Path(DISPLAY_PROFILES_DIR)
            if displays.is_dir():
                host["display_icc_overrides"] = sorted(
                    p.name for p in displays.iterdir() if p.is_file() or p.is_symlink()
                )
        except OSError:
            pass
        payload["colorsync_host"] = host
    return payload


def serialize_track_detect_fields(**_kwargs: Any) -> dict[str, Any]:
    """Track G ``DETECT_FIELDS`` entry point."""
    fields = serialize_colorsync_fields()
    try:
        from x86.graphics.coredisplay_prefs import serialize_coredisplay_fields

        fields.update(serialize_coredisplay_fields())
    except ImportError:
        pass
    return fields


def sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int = 0,
    marketing_version: str = "",
) -> dict:
    """Track G ``SYS_PATCH_HOOKS`` — Tahoe EXECUTE for ColorSync LUT soft path."""
    del marketing_version
    if xnu_major < 25:
        return {}
    execute = dict(colorsync_lut_execute_patches())
    try:
        from x86.graphics.coredisplay_prefs import coredisplay_cleanup_execute_patches

        execute.update(coredisplay_cleanup_execute_patches() or {})
    except ImportError:
        pass
    if not execute:
        return {}
    from x86.graphics.yellow_screen import TAHOE_YELLOW_SCREEN_PATCH_NAME

    try:
        from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType
    except Exception:
        return {}
    return {TAHOE_YELLOW_SCREEN_PATCH_NAME: {PatchType.EXECUTE: execute}}
