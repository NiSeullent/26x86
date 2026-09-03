"""
Track J stage hook — INTEGRATE queue for detect / skylight_tracks (post-52f7298).

Aligned with live APIs (do **not** edit those shared files from Track J):

- ``x86.graphics.detect.serialize_graphics_detect_fields``
- ``x86.graphics.skylight_tracks.merge_optional_detect_fields``

MC applies ``MC_MERGE_*`` / ``mc_merge_plan()``. Filename ``*.stage-J.py``.
"""

from __future__ import annotations

from typing import Any, Optional

from x86.graphics.shader_avx_gate import (
    DOC_PATH,
    TRACK_ID,
    evaluate_shader_avx_gate,
    serialize_shader_avx_fields,
    serialize_track_detect_fields,
    sys_patch_hooks,
)

STAGE_ID = "J"
STAGE_MODULE = "shader_avx_detect.stage-J"
INTEGRATE_BASE = "52f7298"
OWNED_EXPORTS = (
    "serialize_shader_avx_fields",
    "serialize_track_detect_fields",
    "sys_patch_hooks",
    "merge_into_graphics_payload",
    "mc_merge_plan",
    "TRACK_CANDIDATES",
    "DETECT_ATTRS_J",
    "MC_MERGE_DETECT_PY",
    "MC_MERGE_SKYLIGHT_TRACKS_PY",
)

TRACK_CANDIDATES: tuple[str, ...] = (
    "x86.graphics.shader_avx_gate",
)

DETECT_ATTRS_J: tuple[str, ...] = (
    "serialize_track_detect_fields",
    "serialize_shader_avx_fields",
)

MC_MERGE_DETECT_PY = """
# --- BEGIN Track J (MC merge from shader_avx_detect.stage-J) ---
# Insert in serialize_graphics_detect_fields AFTER payload.update(yellow).

    from x86.graphics.shader_avx_gate import serialize_shader_avx_fields

    if "shader_avx" not in payload:
        payload.update(
            serialize_shader_avx_fields(
                cpu_has_avx1=report.has_avx1,
                cpu_has_avx2=report.has_avx2,
            )
        )
# --- END Track J ---
"""

MC_MERGE_SKYLIGHT_TRACKS_PY = """
# --- BEGIN Track J (MC merge from shader_avx_detect.stage-J) ---
# TRACK_MODULE_CANDIDATES:
    "J": (
        "x86.graphics.shader_avx_gate",
    ),
# TRACK_ROLES:
    "J": "shader_compiler_avx",
# serialize_skylight_lut_tracks:
    for tid in ("A", "B", "C", "D", "E", "F", "G", "J")
# detect_attrs:
        "J": (
            "serialize_track_detect_fields",
            "serialize_shader_avx_fields",
        ),
# track_status_entry optional:
    if detect_fn is None and track_id == "J":
        detect_fn = _callable_attr(mod, "serialize_shader_avx_fields")
# Do NOT add J to SYS_PATCH_TRACKS.
# --- END Track J ---
"""


def mc_merge_plan() -> dict[str, Any]:
    return {
        "stage_id": STAGE_ID,
        "integrate_after": INTEGRATE_BASE,
        "queue_id": "next:J-detect-stage",
        "do_not_modify_from_track_j": [
            "x86/graphics/detect.py",
            "x86/graphics/__init__.py",
            "x86/graphics/skylight_tracks.py",
        ],
        "shared_targets": [
            {
                "path": "x86/graphics/detect.py",
                "fn": "serialize_graphics_detect_fields",
                "action": "insert_shader_avx_after_yellow",
                "snippet_const": "MC_MERGE_DETECT_PY",
                "result_key": "shader_avx",
            },
            {
                "path": "x86/graphics/skylight_tracks.py",
                "action": "register_track_J_detect_only",
                "snippet_const": "MC_MERGE_SKYLIGHT_TRACKS_PY",
                "track_candidates": list(TRACK_CANDIDATES),
                "detect_attrs": list(DETECT_ATTRS_J),
                "sys_patch": False,
            },
        ],
        "verify": [
            "python3 -m unittest x86.graphics.test_shader_avx",
            "assert shader_avx in detect payload",
            "assert J in skylight_lut_tracks",
        ],
        "doc": DOC_PATH,
        "snippets": {
            "detect.py": MC_MERGE_DETECT_PY.strip(),
            "skylight_tracks.py": MC_MERGE_SKYLIGHT_TRACKS_PY.strip(),
        },
    }


def merge_into_graphics_payload(
    payload: dict[str, Any],
    *,
    cpu_has_avx1: Optional[bool] = None,
    cpu_has_avx2: Optional[bool] = None,
    probe_host: bool = False,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    if "shader_avx" in payload:
        return payload
    if cpu_has_avx1 is None and "avx_available" in payload:
        cpu_has_avx1 = bool(payload.get("avx_available"))
    if cpu_has_avx2 is None and "avx2_available" in payload:
        cpu_has_avx2 = bool(payload.get("avx2_available"))
    extra = serialize_shader_avx_fields(
        cpu_has_avx1=cpu_has_avx1,
        cpu_has_avx2=cpu_has_avx2,
        probe_host=probe_host,
        environ=environ,
    )
    out = dict(payload)
    out.update(extra)
    return out


__all__ = [
    "DETECT_ATTRS_J",
    "DOC_PATH",
    "INTEGRATE_BASE",
    "MC_MERGE_DETECT_PY",
    "MC_MERGE_SKYLIGHT_TRACKS_PY",
    "OWNED_EXPORTS",
    "STAGE_ID",
    "STAGE_MODULE",
    "TRACK_CANDIDATES",
    "TRACK_ID",
    "evaluate_shader_avx_gate",
    "mc_merge_plan",
    "merge_into_graphics_payload",
    "serialize_shader_avx_fields",
    "serialize_track_detect_fields",
    "sys_patch_hooks",
]
