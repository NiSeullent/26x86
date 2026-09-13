"""Track L-WS — staged plan L0–L5 beyond cache uchg."""

from __future__ import annotations

from typing import Any

from x86.graphics.windowserver_hook_compositor import plan_software_compositor
from x86.graphics.windowserver_hook_gate import extreme_windowserver_hooks_allowed, serialize_windowserver_hook_gate
from x86.graphics.windowserver_hook_inject import plan_process_injection
from x86.graphics.windowserver_hook_lut import plan_public_lut_recovery

STAGE_L0_SHIPPED: tuple[str, ...] = (
    "window_server_cache_disable",
    "colorsync_srgb_fallback",
    "efi_agdpmod_shikigva",
    "renderbox_metallib_if_payload",
    "kdkless_workaround",
)


def build_windowserver_hook_plan(*, include_extreme_detail: bool = False) -> dict[str, Any]:
    gate = serialize_windowserver_hook_gate()
    fill = extreme_windowserver_hooks_allowed() or include_extreme_detail
    stages = [
        {"id": "L0", "title": "shipped_mitigations", "gated": False, "items": list(STAGE_L0_SHIPPED), "status": "do_not_reimplement"},
        {"id": "L1", "title": "public_lut_api", "gated": True, "status": "ready_when_gated" if fill else "locked", "plan": plan_public_lut_recovery(require_gate=False) if fill else None},
        {"id": "L2", "title": "skylight_plugins_injection", "gated": True, "status": "ready_when_gated" if fill else "locked", "plan": plan_process_injection(require_gate=False)["paths"][0] if fill else None},
        {"id": "L3", "title": "dyld_insert_launchd", "gated": True, "status": "sip_blocked_research" if fill else "locked", "plan": plan_process_injection(require_gate=False)["paths"][1] if fill else None},
        {"id": "L4", "title": "software_compositor_force", "gated": True, "status": "no_apple_flag" if fill else "locked", "plan": plan_software_compositor(require_gate=False) if fill else None},
        {"id": "L5", "title": "private_lut_byte_patch_function_hook", "gated": True, "status": "blocked_no_public_symbol", "plan": None, "notes_ko": "사설 심볼 미공개 — R4 금지."},
    ]
    return {"gate": gate, "beyond_cache_lock": True, "stages": stages, "next_when_locked": "export X86_EXTREME=1 X86_EXTREME_WINDOWSERVER_HOOK=1"}


def run_extreme_windowserver_plan() -> dict[str, Any]:
    from x86.graphics.windowserver_hook_compositor import force_software_compositor_status
    from x86.graphics.windowserver_hook_gate import require_extreme_windowserver_hooks
    from x86.graphics.windowserver_hook_lut import apply_public_lut_recovery_dry_run

    require_extreme_windowserver_hooks()
    return {
        "gate": serialize_windowserver_hook_gate(),
        "L1_lut": apply_public_lut_recovery_dry_run(),
        "L2_L3_inject": plan_process_injection(require_gate=False),
        "L4_compositor": force_software_compositor_status(),
        "L5": {"status": "blocked_no_public_symbol"},
        "mutated_host": False,
    }
