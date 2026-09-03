"""
Mission Control — extreme mission gap + env gates.

No permanent block flags. ``X86_EXTREME=1`` enables all extreme experiments.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Optional

EXTREME_ENV = "X86_EXTREME"
TAHOE_3802_ENV = "X86_TAHOE_3802"
TAHOE_NONMETAL_ENV = "X86_TAHOE_NONMETAL"
DOC = "docs/EXTREME-Tahoe-PreAVX-Vega64.md"


def _truthy(name: str, environ: Optional[dict[str, str]] = None) -> bool:
    env = environ if environ is not None else os.environ
    return str(env.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def extreme_enabled(environ: Optional[dict[str, str]] = None) -> bool:
    return _truthy(EXTREME_ENV, environ)


@dataclass(frozen=True)
class TrackGap:
    track_id: str
    status: str
    note: str


def track_gaps() -> list[TrackGap]:
    return [
        TrackGap("A", "integrated", "STAGE-WORKFLOW + Tracks"),
        TrackGap("B", "extreme_unlocked", "SL-BYTEPATCH-LUT; coordinate L5-R"),
        TrackGap("C", "connected", "colorsync/coredisplay"),
        TrackGap("D", "connected", "agdc; diagnostics live"),
        TrackGap("E", "soft_import", "metallib_renderbox + RenderBox-25 gap docs/probe"),
        TrackGap("F", "integrated", "psp overlay dmg_mount/yellow_screen"),
        TrackGap("G", "connected", "skylight_lut_tracks"),
        TrackGap("H", "integrated", "IOSurface/CA; parallel with N under extreme"),
        TrackGap(
            "I",
            "apply_live",
            "interpose_apply on EXTREME+Tahoe; INSTALL for /Library",
        ),
        TrackGap("J", "integrated", "shader_avx detect soft-merge 33e506a"),
        TrackGap("K", "landed", "E2E profile --extreme → interpose_apply"),
        TrackGap("L", "landed", "L5=refused_by_agent; L5-R root-volume patchset"),
        TrackGap("M", "integrated", "metal_3802 live opt-in + tahoe_gate"),
        TrackGap(
            "N",
            "integrated",
            "non_metal* + tahoe_gate; H latch → IOSurface 10.15.7 prefer",
        ),
    ]


def integrate_queue() -> list[str]:
    """Post J+gate: deploy owns app/PKG; research gaps remain."""
    return [
        "done:A-docs",
        "done:M-3802",
        "done:N-nonmetal",
        "done:F-psp",
        "done:H-iosurface-stage",
        "done:J-detect-stage",
        "done:tahoe-gate-sweep",
        "deferred:D-diagnostics-deploy-agent",
        "deferred:L5R-B-deploy-agent",
        "deferred:app-pkg-deploy-agent",
        "host_gate:root_patches_require_is_tahoe",
        "host_gate:sequoia_extreme_root_noop",
    ]


def serialize_extreme_mission(environ: Optional[dict[str, str]] = None) -> dict[str, Any]:
    ex = extreme_enabled(environ)
    return {
        "mission_id": "tahoe-extreme-graphics",
        "doc": DOC,
        "extreme_enabled": ex,
        "tahoe_3802_opt_in": ex or _truthy(TAHOE_3802_ENV, environ),
        "tahoe_nonmetal_opt_in": ex or _truthy(TAHOE_NONMETAL_ENV, environ),
        "permanent_blocks": [],  # never populate — user policy
        "tracks": {t.track_id: asdict(t) for t in track_gaps()},
        "integrate_queue": integrate_queue(),
        "gate": {
            "env_extreme": EXTREME_ENV,
            "env_3802": TAHOE_3802_ENV,
            "env_nonmetal": TAHOE_NONMETAL_ENV,
            "policy": "default safe empty; X86_EXTREME allows all experiments",
        },
        "g_merge_note": "skylight_lut_tracks (G) coexists with extreme_mission (MC)",
    }
