"""
Track I — Metal / SkyLight / CoreDisplay DYLD_INSERT & root-volume interpose plan.

Owned files only. Does not patch shared detect/yellow_screen/sys_patch modules.
When ``X86_EXTREME=1``, recipes are armed and apply attempts build→copy→guide
(no SHA-256 pin empty-dict gate).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from .interpose_gate import (
    AVX_MODE_PASSTHROUGH,
    AVX_MODE_REPORT1,
    LUT_MODE_IDENTITY,
    ENV_X86_EXTREME,
    extreme_opt_in,
    gate_blocks_reason,
    serialize_interpose_gate_fields,
)
from .interpose_symbols import (
    AVX_SYSCTL_KEYS,
    EVIDENCE_URLS,
    FORBIDDEN_ACTIONS,
    INTERPOSE_SYMBOLS,
    serialize_symbol_catalog,
)

TRACK_ID = "I"
TRACK_NAME = "Metal/SkyLight dylib interpose"
COMMIT_PREFIX = "feat(skylight-I):"

COMMUNITY_PAYLOAD_REL = Path("payloads/Kexts/Community/Extreme-Interpose")
DYLIB_STEM = "libExtremeCompositorInterpose"
PLUGIN_STEM = "ExtremeCompositor"

MODE_DYLD_INSERT = "dyld_insert"
MODE_SKYLIGHT_PLUGIN = "skylight_plugins"
MODE_ROOT_WRAPPER = "root_volume_wrapper"


def community_payload_root(repo_root: Optional[Path] = None) -> Path:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    return Path(repo_root) / COMMUNITY_PAYLOAD_REL


def injection_modes(*, extreme: Optional[bool] = None) -> list[dict[str, Any]]:
    armed = extreme_opt_in() if extreme is None else extreme
    return [
        {
            "id": MODE_DYLD_INSERT,
            "title": "DYLD_INSERT_LIBRARIES (user or LaunchDaemon)",
            "armed": armed,
            "requires": [ENV_X86_EXTREME, "SIP considerations", "ad-hoc / disabled AMFI"],
            "targets": ["Metal client apps", "optional WindowServer (extreme)"],
            "notes": (
                f"{ENV_X86_EXTREME}=1 runs build→staging copy→guide via "
                "interpose_apply.apply_extreme_interpose."
            ),
        },
        {
            "id": MODE_SKYLIGHT_PLUGIN,
            "title": "SkyLightPlugins dylib+txt (moraea protocol)",
            "armed": armed,
            "requires": [
                ENV_X86_EXTREME,
                "SkyLightOld.dylib / patched SkyLight loader for live effect",
            ],
            "targets": ["WindowServer via patched SkyLight"],
            "notes": (
                "Stock Tahoe SkyLight does not load SkyLightPlugins; "
                "overlay is still installed under Extreme-Interpose when extreme."
            ),
        },
        {
            "id": MODE_ROOT_WRAPPER,
            "title": "Staging wrapper + install manifest (community dylib)",
            "armed": armed,
            "requires": [ENV_X86_EXTREME],
            "targets": ["staging/", "SkyLightPlugins overlay", "optional /Library copy"],
            "notes": (
                "No Apple blob redistribution. Recipe emits built dylib path + "
                "sha256 of the local build (pin file optional, not a gate)."
            ),
        },
    ]


def lut_bypass_candidates() -> list[dict[str, str]]:
    return [
        {
            "symbol": s.name,
            "library": s.library,
            "purpose": s.purpose,
            "risk": s.risk,
            "evidence": s.evidence,
        }
        for s in INTERPOSE_SYMBOLS
        if s.mode_group == "lut"
    ]


def avx_spoof_plan() -> dict[str, Any]:
    return {
        "sysctl_keys": list(AVX_SYSCTL_KEYS),
        "default_mode": AVX_MODE_PASSTHROUGH,
        "dangerous_mode": AVX_MODE_REPORT1,
        "warning": (
            "report1 without opcode emulation SIGILLs on pre-AVX CPUs. "
            "Prefer report0/passthrough + Track J for production pre-AVX+Vega64."
        ),
        "related_safari_fix": EVIDENCE_URLS["safari26_preavx"],
        "not_a_substitute_for": "Safari26-PreAVX-Fix / RestrictEvents jsc trampoline",
    }


def plan_summary(*, extreme: Optional[bool] = None) -> dict[str, Any]:
    blocked = gate_blocks_reason(require_install=False)
    armed = extreme_opt_in() if extreme is None else extreme
    return {
        "track": TRACK_ID,
        "track_name": TRACK_NAME,
        "commit_prefix": COMMIT_PREFIX,
        "armed": armed,
        "blocked_reason": blocked,
        "payload_relative": COMMUNITY_PAYLOAD_REL.as_posix(),
        "dylib_stem": DYLIB_STEM,
        "plugin_stem": PLUGIN_STEM,
        "injection_modes": injection_modes(extreme=armed),
        "lut_bypass_candidates": lut_bypass_candidates(),
        "avx_spoof": avx_spoof_plan(),
        "forbidden": list(FORBIDDEN_ACTIONS),
        "evidence_urls": dict(EVIDENCE_URLS),
        "symbol_count": len(INTERPOSE_SYMBOLS),
        "identity_lut_env": LUT_MODE_IDENTITY,
        "sha_pin_required": False,
        "apply_module": "x86.graphics.interpose_apply",
    }


def root_volume_interpose_recipe(
    repo_root: Optional[Path] = None,
) -> dict[str, Any]:
    """
    Extreme install recipe. Armed by ``X86_EXTREME=1`` alone.

    Builds the community dylib if needed. Does **not** require a pre-declared
    SHA-256 pin (recorded digest is informational).
    """
    if not extreme_opt_in():
        return {}

    from .interpose_apply import interpose_install_manifest

    manifest = interpose_install_manifest(repo_root)
    if not manifest.get("ok"):
        return {
            "Extreme Interpose Compositor": {
                "status": "build_failed",
                "detail": manifest,
            }
        }

    return {
        "Extreme Interpose Compositor": {
            "status": "ready",
            "dylib": manifest["dylib"],
            "sha256": manifest["dylib_sha256"],
            "plugin_dylib": manifest.get("plugin_dylib"),
            "plugin_txt": manifest.get("plugin_txt"),
            "staging_dir": manifest["staging_dir"],
            "skylight_plugins_overlay": manifest["skylight_plugins_overlay"],
            "live_skylight_plugins": manifest["live_skylight_plugins"],
            "install_actions": list(manifest["install_actions"]),
            "note": (
                "Community dylib only — no Apple frameworks. "
                "Run: X86_EXTREME=1 python3 -m x86.graphics.interpose_apply"
            ),
        }
    }


def serialize_interpose_fields(
    *,
    repo_root: Optional[Path] = None,
    include_symbols: bool = False,
    attempt_apply: bool = False,
) -> dict[str, Any]:
    from .interpose_payload import enumerate_extreme_interpose_sources, payload_status

    summary = plan_summary()
    status = payload_status(repo_root=repo_root)
    payload: dict[str, Any] = {
        "skylight_track_I": summary,
        "extreme_interpose": {
            **serialize_interpose_gate_fields(),
            **status,
            "sources": enumerate_extreme_interpose_sources(repo_root=repo_root),
            "recipe": root_volume_interpose_recipe(repo_root=repo_root),
        },
    }
    if include_symbols:
        payload["extreme_interpose"]["symbols"] = serialize_symbol_catalog()
    if attempt_apply and extreme_opt_in():
        from .interpose_apply import apply_extreme_interpose

        payload["extreme_interpose"]["apply"] = apply_extreme_interpose(
            repo_root=repo_root
        )
    return payload
