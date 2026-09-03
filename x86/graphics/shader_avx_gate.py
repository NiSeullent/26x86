"""
Track J — Metal / compositor AVX gate decisions (separate from Safari jsc).

RestrictEvents ``revpatch=jsc`` is Safari/JavaScriptCore only. This module
plans graphics-side PoCs (opcode scan, SSE substitution, feature-bit spoof).

All mutating PoCs require ``X86_EXTREME=1``. Default path never rewrites
system binaries. Does **not** patch shared detect/__init__/skylight_tracks —
consumers import from here or from ``shader_avx_detect.stage-J``.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from x86.graphics.shader_avx_opcodes import (
    GRAPHICS_NOT_JSC_NOTE,
    SAFARI26_TECHNICAL_NOTE,
    SSE_SUBSTITUTIONS,
)
from x86.graphics.shader_avx_scan import (
    SEQUOIA_155_BASELINE,
    scan_graphics_avx_surface,
)

EXTREME_ENV = "X86_EXTREME"
TRACK_ID = "J"
DOC_PATH = "docs/Tahoe-Shader-Compiler-AVX.md"
PROPOSED_REVPATCH_TOKEN = "gfx"
PROPOSED_REVPATCH_NOTE = (
    f"Proposed graphics token revpatch={PROPOSED_REVPATCH_TOKEN} would target "
    "compositor/compiler images, never JavaScriptCore. Not implemented in "
    "RestrictEvents upstream; Track J documents signatures only."
)


def extreme_enabled(environ: Optional[dict[str, str]] = None) -> bool:
    env = environ if environ is not None else os.environ
    raw = str(env.get(EXTREME_ENV, "")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


@dataclass
class ShaderAvxGateDecision:
    track: str = TRACK_ID
    extreme: bool = False
    safari_jsc_path: str = "separate — use x86.patch.safari26_preavx / RestrictEvents"
    graphics_sigill_suspected: bool = False
    sse_poc_armed: bool = False
    feature_spoof_armed: bool = False
    recommended_action: str = "monitor"
    reason: str = ""
    substitutions: list[str] = field(default_factory=list)
    feature_spoof_plan: dict[str, Any] = field(default_factory=dict)
    scan_summary: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def feature_bit_spoof_plan(*, cpu_has_avx1: bool, cpu_has_avx2: bool) -> dict[str, Any]:
    return {
        "observed_queries": list(
            SEQUOIA_155_BASELINE["findings"]["coredisplay_feature_strings"]
        )
        + list(SEQUOIA_155_BASELINE["findings"]["skylight_feature_strings"]),
        "host_avx1": cpu_has_avx1,
        "host_avx2": cpu_has_avx2,
        "safe_default_on_pre_avx": (
            "Leave sysctl as-is (already 0). Do not force AVX=1 — that can "
            "steer code into SIGILL paths."
        ),
        "experimental_spoof_off": (
            "Only useful on AVX-capable CPUs to force SSE paths for A/B tests; "
            f"requires {EXTREME_ENV}=1 and is not a yellow-screen fix."
        ),
        "experimental_spoof_on": (
            "FORBIDDEN on Westmere/pre-AVX — will increase SIGILL risk if any "
            "path trusts the bit and emits VEX."
        ),
        "revpatch_token": PROPOSED_REVPATCH_TOKEN,
        "revpatch_note": PROPOSED_REVPATCH_NOTE,
        "not_jsc": GRAPHICS_NOT_JSC_NOTE,
    }


def evaluate_shader_avx_gate(
    *,
    cpu_has_avx1: Optional[bool] = None,
    cpu_has_avx2: Optional[bool] = None,
    probe_host: bool = False,
    include_shared_cache: bool = False,
    environ: Optional[dict[str, str]] = None,
) -> ShaderAvxGateDecision:
    extreme = extreme_enabled(environ)
    scan = scan_graphics_avx_surface(
        probe_host=probe_host,
        include_shared_cache=include_shared_cache and (probe_host or extreme),
        environ=environ,
    )
    dense = int(scan.get("dense_trampoline_hints") or 0)
    baseline_dense = int(
        SEQUOIA_155_BASELINE["findings"].get("safari_style_dense_runs") or 0
    )

    notes = [
        SAFARI26_TECHNICAL_NOTE,
        GRAPHICS_NOT_JSC_NOTE,
        SEQUOIA_155_BASELINE["verdict"],
        DOC_PATH,
    ]

    has_avx1 = bool(cpu_has_avx1) if cpu_has_avx1 is not None else False
    has_avx2 = bool(cpu_has_avx2) if cpu_has_avx2 is not None else False
    spoof = feature_bit_spoof_plan(cpu_has_avx1=has_avx1, cpu_has_avx2=has_avx2)

    graphics_sigill = dense > 0
    if not has_avx1 and dense > baseline_dense:
        graphics_sigill = True

    if graphics_sigill and extreme:
        action = "sse_substitute_poc"
        reason = (
            f"Dense vmovaps windows={dense}; {EXTREME_ENV}=1 arms length-matched "
            "SSE PoC (no auto root-patch)."
        )
        sse_armed = True
    elif graphics_sigill and not extreme:
        action = "needs_extreme"
        reason = (
            f"Trampoline hint dense={dense} but {EXTREME_ENV} unset — document only."
        )
        sse_armed = False
    elif not has_avx1:
        action = "monitor_demote_j_priority"
        reason = (
            "pre-AVX CPU but no Safari-style graphics trampoline in baseline/"
            f"scan (dense={dense}). Yellow screen is compositor/metallib, not AVX SIGILL."
        )
        sse_armed = False
    else:
        action = "n_a_host_has_avx"
        reason = "Host reports AVX1 — graphics AVX SIGILL PoC not applicable."
        sse_armed = False

    return ShaderAvxGateDecision(
        extreme=extreme,
        graphics_sigill_suspected=graphics_sigill,
        sse_poc_armed=sse_armed,
        feature_spoof_armed=extreme and not has_avx1,
        recommended_action=action,
        reason=reason,
        substitutions=[s.name for s in SSE_SUBSTITUTIONS],
        feature_spoof_plan=spoof,
        scan_summary={
            "live_scan": scan.get("live_scan"),
            "shared_cache_scanned": scan.get("shared_cache_scanned"),
            "dense_trampoline_hints": dense,
            "feature_string_hits": scan.get("feature_string_hits"),
            "baseline_verdict": SEQUOIA_155_BASELINE["verdict"],
        },
        notes=notes,
    )


def serialize_shader_avx_fields(
    *,
    cpu_has_avx1: Optional[bool] = None,
    cpu_has_avx2: Optional[bool] = None,
    probe_host: bool = False,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """Detect JSON fragment under ``shader_avx`` (merge via stage-J hook)."""
    decision = evaluate_shader_avx_gate(
        cpu_has_avx1=cpu_has_avx1,
        cpu_has_avx2=cpu_has_avx2,
        probe_host=probe_host,
        environ=environ,
    )
    payload = decision.as_dict()
    payload["doc"] = DOC_PATH
    payload["extreme_env"] = EXTREME_ENV
    return {"shader_avx": payload}


def sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int,
    marketing_version: str,
) -> dict:
    """Never emits root patches — even under X86_EXTREME (scaffold only)."""
    _ = (xnu_major, xnu_minor, marketing_version)
    return {}


def serialize_track_detect_fields(
    model: str = "",
    *,
    gpu_archs: Any = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    agdpmod_present: Optional[bool] = None,
    assume_tahoe: bool = False,
    **_kwargs: Any,
) -> dict[str, Any]:
    """G-orchestrator detect merge export (Track J)."""
    _ = (model, gpu_archs, os_version, xnu_major, agdpmod_present, assume_tahoe)
    return serialize_shader_avx_fields()
