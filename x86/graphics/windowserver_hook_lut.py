"""Track L-WS — public LUT recovery; private byte patches blocked."""

from __future__ import annotations

from typing import Any

from x86.graphics.skylight_lut import (
    OCLP_T2_YELLOW_SCREEN_ISSUE,
    PUBLIC_COLOR_SYMBOL_NEEDLES,
)
from x86.graphics.windowserver_hook_gate import (
    extreme_windowserver_hooks_allowed,
    require_extreme_windowserver_hooks,
)

PUBLIC_LUT_ACTIONS: tuple[dict[str, str], ...] = (
    {"id": "cg_display_gamma_identity", "api": "CGDisplayGammaTable / CGSetDisplayTransferByTable", "effect": "tint_only", "evidence": "ColorSync.h / CGDisplay public API"},
    {"id": "colorsync_profile_srgb_url", "api": "ColorSyncProfileCreateWithURL", "effect": "icc_fallback", "evidence": OCLP_T2_YELLOW_SCREEN_ISSUE},
    {"id": "colorsync_transform_rebuild", "api": "ColorSyncTransformCreate", "effect": "icc_fallback", "evidence": OCLP_T2_YELLOW_SCREEN_ISSUE},
)
PRIVATE_LUT_BYTE_PATCH_STATUS = "blocked_no_public_symbol"


def plan_public_lut_recovery(*, require_gate: bool = True) -> dict[str, Any]:
    if require_gate:
        require_extreme_windowserver_hooks()
    return {
        "gated": extreme_windowserver_hooks_allowed(),
        "actions": [dict(item) for item in PUBLIC_LUT_ACTIONS],
        "public_symbol_needles": list(PUBLIC_COLOR_SYMBOL_NEEDLES),
        "private_lut_byte_patch": PRIVATE_LUT_BYTE_PATCH_STATUS,
        "notes_ko": ["공개 API는 tint용.", "사설 LUT 바이트패치 금지.", f"근거: {OCLP_T2_YELLOW_SCREEN_ISSUE}"],
    }


def build_gamma_identity_table(entries: int = 256) -> dict[str, list[float]]:
    if entries < 2 or entries > 1024:
        raise ValueError("entries must be in [2, 1024]")
    ramp = [i / (entries - 1) for i in range(entries)]
    return {"red": list(ramp), "green": list(ramp), "blue": list(ramp), "samples": entries}


def apply_public_lut_recovery_dry_run() -> dict[str, Any]:
    require_extreme_windowserver_hooks()
    plan = plan_public_lut_recovery(require_gate=False)
    plan["dry_run"] = True
    plan["gamma_identity_preview"] = {"samples": 5, "head": build_gamma_identity_table(5)["red"]}
    plan["applied"] = False
    plan["reason"] = "Darwin CoreGraphics apply is host-side; CI ships dry-run only."
    return plan
