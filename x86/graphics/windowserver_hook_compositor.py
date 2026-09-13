"""Track L-WS — software compositor probes; no Apple WS Metal-off flag."""

from __future__ import annotations

from typing import Any

from x86.graphics.skylight_lut import DOCUMENTED_GRAPHICS_BOOT_ARGS
from x86.graphics.windowserver_hook_gate import (
    extreme_windowserver_hooks_allowed,
    require_extreme_windowserver_hooks,
)

TAHOE_FORBIDDEN_COMPOSITOR_FLAGS: tuple[str, ...] = (
    "useMetal=no",
    "Non-Metal Enforcement",
    "SkyLight.framework 10.14.6 downgrade",
)
SOFTWARE_COMPOSITOR_PROBES: tuple[dict[str, str], ...] = (
    {"id": "ngfxgl", "boot_arg": "ngfxgl=1", "scope": "NVIDIA GeForce (legacy)", "effect": "force_opengl_path_vendor", "evidence": "WhateverGreen"},
    {"id": "igfxvesa", "boot_arg": "-igfxvesa", "scope": "Intel iGPU", "effect": "vesa_fallback", "evidence": "WhateverGreen"},
    {"id": "agdpmod_pikera", "boot_arg": "agdpmod=pikera", "scope": "AMD AGDC board-id", "effect": "agdc_yellow_mitigation", "evidence": "WhateverGreen / OCLP EFI"},
)
APPLE_METAL_WS_OFF_FLAG = None


def plan_software_compositor(*, require_gate: bool = True) -> dict[str, Any]:
    if require_gate:
        require_extreme_windowserver_hooks()
    return {
        "gated": extreme_windowserver_hooks_allowed(),
        "apple_metal_windowserver_off_flag": APPLE_METAL_WS_OFF_FLAG,
        "documented_graphics_boot_args": list(DOCUMENTED_GRAPHICS_BOOT_ARGS),
        "probes": [dict(item) for item in SOFTWARE_COMPOSITOR_PROBES],
        "tahoe_forbidden": list(TAHOE_FORBIDDEN_COMPOSITOR_FLAGS),
        "notes_ko": ["Apple WS Metal off 플래그 없음.", "Tahoe Non-Metal 강제 = KP."],
    }


def force_software_compositor_status() -> dict[str, Any]:
    require_extreme_windowserver_hooks()
    plan = plan_software_compositor(require_gate=False)
    plan["forced"] = False
    plan["status"] = "planned_only"
    plan["blocker"] = "No Apple software-compositor switch; Tahoe Non-Metal KP-guarded."
    return plan
