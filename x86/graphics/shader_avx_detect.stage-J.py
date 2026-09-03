"""
Track J stage hook — next INTEGRATE after MC ``d1093ef`` (H + L5 on tracks).

Aligned with live APIs (do **not** edit those shared files from Track J):

- ``x86.graphics.detect.serialize_graphics_detect_fields``
- ``x86.graphics.skylight_tracks`` @ ``d1093ef`` (H + L5 already registered)

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
# First extreme INTEGRATE that opened the J detect queue.
INTEGRATE_BASE = "52f7298"
# Current skylight_tracks / detect baseline for this stage (H iosurface + L5).
REBASE_ON = "d1093ef"
LIVE_API_NOTE = (
    "d1093ef skylight_tracks already has H + L5. "
    "detect: insert after payload.update(yellow), before Track G soft-merge. "
    "skylight_tracks: ADD J detect-only; never SYS_PATCH_TRACKS; "
    'tid becomes (…, "H", "J", "L5").'
)
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
    "REBASE_ON",
)

TRACK_CANDIDATES: tuple[str, ...] = (
    "x86.graphics.shader_avx_gate",
)

DETECT_ATTRS_J: tuple[str, ...] = (
    "serialize_track_detect_fields",
    "serialize_shader_avx_fields",
)

# Exact paste for MC — primary path (CPU flags from PreAvxMacProReport).
MC_MERGE_DETECT_PY = """
# --- BEGIN Track J (MC merge from shader_avx_detect.stage-J) ---
# FILE: x86/graphics/detect.py
# FN:   serialize_graphics_detect_fields
# BASE: d1093ef (detect yellow→G soft-merge unchanged)
# ANCHOR: immediately AFTER `payload.update(yellow)` and BEFORE
#         `# Track G: soft-merge B/C/D/E detect extras ...`
# WHY:   report.has_avx* is in scope here; merge_optional_detect_fields alone
#         does not pass CPU AVX flags into Track J.
# IDEMPOTENT: skip if payload already has "shader_avx".

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

# Exact paste checklist for MC — detect-only registration (no sys_patch).
MC_MERGE_SKYLIGHT_TRACKS_PY = """
# --- BEGIN Track J (MC merge from shader_avx_detect.stage-J) ---
# FILE: x86/graphics/skylight_tracks.py
# BASE: d1093ef — already has H + L5; ADD J only.
# RULE: detect-only — do NOT add "J" to SYS_PATCH_TRACKS
#       (live: SYS_PATCH_TRACKS = ("B", "C", "E", "F", "L5")).

# 1) TRACK_MODULE_CANDIDATES — add after L5 (or beside H/L5):
    "J": (
        "x86.graphics.shader_avx_gate",
    ),

# 2) TRACK_ROLES — add:
    "J": "shader_compiler_avx",

# 3) serialize_skylight_lut_tracks — REPLACE tid tuple with:
    for tid in ("A", "B", "C", "D", "E", "F", "G", "H", "J", "L5")
#   d1093ef was: ("A", "B", "C", "D", "E", "F", "G", "H", "L5")

# 4) merge_optional_detect_fields → detect_attrs — add alongside H/L5:
        "J": (
            "serialize_track_detect_fields",
            "serialize_shader_avx_fields",
        ),

# 5) track_status_entry — after F (and any H/L5) detect_fn fallbacks:
    if detect_fn is None and track_id == "J":
        detect_fn = _callable_attr(mod, "serialize_shader_avx_fields")
# --- END Track J ---
"""


def mc_merge_plan() -> dict[str, Any]:
    return {
        "stage_id": STAGE_ID,
        "integrate_after": INTEGRATE_BASE,
        "rebase_on": REBASE_ON,
        "queue_id": "next:J-detect-stage",
        "live_api_note": LIVE_API_NOTE,
        "do_not_modify_from_track_j": [
            "x86/graphics/detect.py",
            "x86/graphics/__init__.py",
            "x86/graphics/skylight_tracks.py",
        ],
        "stage_sidecar_files": [
            "x86/graphics/detect.py.stage-J",
            "x86/graphics/skylight_tracks.py.stage-J",
            "x86/graphics/shader_avx_detect.stage-J.py",
        ],
        "shared_targets": [
            {
                "path": "x86/graphics/detect.py",
                "fn": "serialize_graphics_detect_fields",
                "action": "insert_shader_avx_after_yellow_before_track_g",
                "anchor_after": "payload.update(yellow)",
                "anchor_before": "# Track G: soft-merge",
                "snippet_const": "MC_MERGE_DETECT_PY",
                "result_key": "shader_avx",
                "required": True,
            },
            {
                "path": "x86/graphics/skylight_tracks.py",
                "action": "register_track_J_detect_only",
                "snippet_const": "MC_MERGE_SKYLIGHT_TRACKS_PY",
                "track_candidates": list(TRACK_CANDIDATES),
                "detect_attrs": list(DETECT_ATTRS_J),
                "sys_patch": False,
                "tid_include": "J",
                "tid_tuple_after": [
                    "A",
                    "B",
                    "C",
                    "D",
                    "E",
                    "F",
                    "G",
                    "H",
                    "J",
                    "L5",
                ],
                "preserve_parallel_tids": ["H", "L5"],
                "required": True,
            },
        ],
        "verify": [
            "python3 -m unittest x86.graphics.test_shader_avx",
            "assert shader_avx in detect.serialize_graphics_detect_fields(...)",
            "assert J in skylight_lut_tracks['tracks']",
            "assert J not in SYS_PATCH_TRACKS",
            "assert H and L5 still in skylight_lut_tracks",
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
    """Non-destructive merge: only adds ``shader_avx`` if absent."""
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
    "LIVE_API_NOTE",
    "MC_MERGE_DETECT_PY",
    "MC_MERGE_SKYLIGHT_TRACKS_PY",
    "OWNED_EXPORTS",
    "REBASE_ON",
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
