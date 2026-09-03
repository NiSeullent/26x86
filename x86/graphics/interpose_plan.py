"""
Track I — Metal / SkyLight / CoreDisplay DYLD_INSERT & root-volume interpose plan.

Owned files only. Does not patch shared detect/yellow_screen/sys_patch modules.
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
            "notes": "WindowServer insert needs X86_EXTREME_INSTALL=1 on spare volumes.",
        },
        {
            "id": MODE_SKYLIGHT_PLUGIN,
            "title": "SkyLightPlugins dylib+txt (moraea protocol)",
            "armed": armed,
            "requires": [
                "SkyLightOld.dylib / patched SkyLight loader",
                "SHA-256 pin in skylight_lut.COMPOSITOR_PLUGIN_SHA256",
            ],
            "targets": ["WindowServer via patched SkyLight"],
            "notes": "Stock Tahoe SkyLight does not load SkyLightPlugins.",
        },
        {
            "id": MODE_ROOT_WRAPPER,
            "title": "Root-volume thin wrapper dylib beside framework",
            "armed": False,
            "requires": [
                ENV_X86_EXTREME,
                "X86_EXTREME_INSTALL=1",
                "sealed system volume remount",
                "pinned SHA-256 of built dylib",
            ],
            "targets": ["SkyLight / CoreDisplay / Metal load path"],
            "notes": "No Apple blob redistribution. Recipe empty until pin exists.",
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
    }


def root_volume_interpose_recipe() -> dict[str, Any]:
    from .interpose_payload import pinned_dylib_sha256, resolve_built_dylib

    if gate_blocks_reason(require_install=True):
        return {}
    dylib = resolve_built_dylib()
    pin = pinned_dylib_sha256()
    if dylib is None or not pin:
        return {}
    return {
        "Extreme Interpose Wrapper": {
            "note": "design recipe — wire into sys_patch only after review",
            "dylib": str(dylib),
            "sha256": pin,
        }
    }


def serialize_interpose_fields(
    *,
    repo_root: Optional[Path] = None,
    include_symbols: bool = False,
) -> dict[str, Any]:
    from .interpose_payload import enumerate_extreme_interpose_sources, payload_status

    payload: dict[str, Any] = {
        "skylight_track_I": plan_summary(),
        "extreme_interpose": {
            **serialize_interpose_gate_fields(),
            **payload_status(repo_root=repo_root),
            "sources": enumerate_extreme_interpose_sources(repo_root=repo_root),
        },
    }
    if include_symbols:
        payload["extreme_interpose"]["symbols"] = serialize_symbol_catalog()
    return payload
