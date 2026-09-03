"""
Tahoe CoreDisplay preference / policy (Track C — dedicated module).

OCLP-T2 #194: private CoreDisplay LUT symbols unpublished → no byte patches.
Cleanup leftover useMetal/useIOP only. Never write useMetal=no on Tahoe.
GPU-agnostic (Vega 64 unpublished). ``X86_EXTREME`` does not unlock Non-Metal.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

OCLP_T2_YELLOW_SCREEN_ISSUE = (
    "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194"
)

CORE_DISPLAY_PREF_PATH = "/Library/Preferences/com.apple.CoreDisplay"
CORE_DISPLAY_FRAMEWORK = (
    "/System/Library/Frameworks/CoreDisplay.framework/Versions/A/CoreDisplay"
)

METAL_ENFORCEMENT_KEYS: tuple[str, ...] = ("useMetal", "useIOP")

FORBIDDEN_TAHOE_COREDISPLAY_WRITES: tuple[str, ...] = (
    f"/usr/bin/defaults write {CORE_DISPLAY_PREF_PATH} useMetal -boolean no",
    f"/usr/bin/defaults write {CORE_DISPLAY_PREF_PATH} useIOP -boolean no",
)


def coredisplay_cleanup_execute_patches() -> dict[str, bool]:
    """Empty EXECUTE map: defaults delete is not argv-safe under verify."""
    return {}


def is_forbidden_tahoe_coredisplay_write(command: str) -> bool:
    normalized = " ".join(command.split())
    return any(normalized == forbidden for forbidden in FORBIDDEN_TAHOE_COREDISPLAY_WRITES)


def apply_coredisplay_pref_cleanup(*, run_root=None) -> dict[str, Any]:
    """Delete leftover useMetal/useIOP without failing when absent."""
    result: dict[str, Any] = {
        "deleted": [],
        "absent": [],
        "forbidden_writes_blocked": list(FORBIDDEN_TAHOE_COREDISPLAY_WRITES),
    }
    for key in METAL_ENFORCEMENT_KEYS:
        argv = ["/usr/bin/defaults", "delete", CORE_DISPLAY_PREF_PATH, key]
        if run_root is not None:
            code = int(run_root(argv))
        elif sys.platform != "darwin":
            result["absent"].append(key)
            continue
        else:
            try:
                code = subprocess.run(
                    argv, capture_output=True, text=True, check=False
                ).returncode
            except OSError:
                result["absent"].append(key)
                continue
        if code == 0:
            result["deleted"].append(key)
        else:
            result["absent"].append(key)
    return result


def serialize_coredisplay_fields(*, probe_host: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "coredisplay_pref_path": CORE_DISPLAY_PREF_PATH,
        "coredisplay_metal_enforcement_keys": list(METAL_ENFORCEMENT_KEYS),
        "coredisplay_tahoe_forbids_usemetal_no": True,
        "coredisplay_forbidden_tahoe_writes": list(FORBIDDEN_TAHOE_COREDISPLAY_WRITES),
        "coredisplay_yellow_screen_issue_url": OCLP_T2_YELLOW_SCREEN_ISSUE,
        "coredisplay_gpu_agnostic": True,
        "coredisplay_extreme_does_not_unlock_nonmetal": True,
    }
    if probe_host:
        present = False
        if sys.platform == "darwin":
            try:
                present = Path(CORE_DISPLAY_FRAMEWORK).is_file()
            except OSError:
                present = False
        payload["coredisplay_host"] = {
            "framework_present": present,
            "tahoe_forbids_usemetal_no": True,
        }
    return payload


def serialize_track_detect_fields(**_kwargs: Any) -> dict[str, Any]:
    """Secondary Track G detect entry (colorsync_icc is preferred first)."""
    return serialize_coredisplay_fields()
