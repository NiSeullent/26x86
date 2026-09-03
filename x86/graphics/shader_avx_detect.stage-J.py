"""
Track J stage hook — merge into detect / skylight_tracks without editing them.

Load via importlib (hyphen in filename):

    spec_from_file_location("shader_avx_detect_stage_J", path_to_this_file)

Filename ``*.stage-J.py`` so parallel tracks do not touch ``detect.py`` /
``__init__.py`` / ``skylight_tracks.py``.
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

# Explicit stage metadata for Mission Control / Track G importers.
STAGE_ID = "J"
STAGE_MODULE = "shader_avx_detect.stage-J"
OWNED_EXPORTS = (
    "serialize_shader_avx_fields",
    "serialize_track_detect_fields",
    "sys_patch_hooks",
    "merge_into_graphics_payload",
    "TRACK_CANDIDATES",
)

# Suggested addition for skylight_tracks.TRACK_MODULE_CANDIDATES["J"] (do not edit
# that file from Track J — paste via G merge).
TRACK_CANDIDATES: tuple[str, ...] = (
    "x86.graphics.shader_avx_gate",
    "x86.graphics.shader_avx_scan",
)


def merge_into_graphics_payload(
    payload: dict[str, Any],
    *,
    cpu_has_avx1: Optional[bool] = None,
    cpu_has_avx2: Optional[bool] = None,
    probe_host: bool = False,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """
    Non-destructive merge: only adds ``shader_avx`` if absent.

    Callers own ``detect.py``; Track J never patches that file.
    """
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
    "DOC_PATH",
    "OWNED_EXPORTS",
    "STAGE_ID",
    "STAGE_MODULE",
    "TRACK_CANDIDATES",
    "TRACK_ID",
    "evaluate_shader_avx_gate",
    "merge_into_graphics_payload",
    "serialize_shader_avx_fields",
    "serialize_track_detect_fields",
    "sys_patch_hooks",
]
