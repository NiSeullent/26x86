"""x86 hardware E2E profiles (Track K). Shared CLI is not patched."""

from __future__ import annotations

from typing import Any, Optional

from x86.profiles.base import HardwareProfile, extreme_enabled
from x86.profiles.macpro5_vega64_tahoe import (
    PROFILE as MACPRO5_VEGA64_TAHOE,
    PROFILE_ID as MACPRO5_VEGA64_TAHOE_ID,
    apply_profile as apply_macpro5_vega64_tahoe,
    apply_to_config_path as apply_macpro5_vega64_tahoe_config,
)

_REGISTRY: dict[str, HardwareProfile] = {
    MACPRO5_VEGA64_TAHOE_ID: MACPRO5_VEGA64_TAHOE,
}
_APPLY = {MACPRO5_VEGA64_TAHOE_ID: apply_macpro5_vega64_tahoe}
_APPLY_CONFIG = {MACPRO5_VEGA64_TAHOE_ID: apply_macpro5_vega64_tahoe_config}


def list_profiles() -> list[HardwareProfile]:
    return [_REGISTRY[key] for key in sorted(_REGISTRY)]


def get_profile(profile_id: str) -> HardwareProfile:
    key = (profile_id or "").strip().lower()
    if key not in _REGISTRY:
        known = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise KeyError(f"Unknown profile '{profile_id}'. Known: {known}")
    return _REGISTRY[key]


def apply(
    profile_id: str,
    *,
    config: Optional[dict[str, Any]] = None,
    config_path: Optional[Any] = None,
    dry_run: bool = False,
    include_extreme: bool = False,
) -> dict[str, Any]:
    key = (profile_id or "").strip().lower()
    if key not in _APPLY:
        raise KeyError(f"Unknown profile '{profile_id}'")
    if config_path is not None:
        from pathlib import Path

        return _APPLY_CONFIG[key](
            Path(config_path),
            dry_run=dry_run,
            include_extreme=include_extreme,
        )
    return _APPLY[key](config=config, dry_run=dry_run, include_extreme=include_extreme)


def serialize_profile_match_fields(
    *,
    model: str,
    gpu_family: Optional[str] = None,
    gpu_archs: Optional[list[Any]] = None,
    avx_available: Optional[bool] = None,
    pre_avx_mac_pro: Optional[bool] = None,
) -> dict[str, Any]:
    from x86.profiles.fixtures import matches_macpro5_vega64_profile

    match = matches_macpro5_vega64_profile(
        model=model,
        gpu_family=gpu_family,
        gpu_archs=gpu_archs,
        avx_available=avx_available,
        pre_avx_mac_pro=pre_avx_mac_pro,
    )
    if not match:
        return {"recommended_profile": None, "profile_match": False}
    return {
        "recommended_profile": MACPRO5_VEGA64_TAHOE_ID,
        "profile_match": True,
        "profile_title": MACPRO5_VEGA64_TAHOE.title,
        "profile_apply": f"python -m x86.profiles apply {MACPRO5_VEGA64_TAHOE_ID}",
    }


__all__ = [
    "HardwareProfile",
    "MACPRO5_VEGA64_TAHOE",
    "MACPRO5_VEGA64_TAHOE_ID",
    "apply",
    "extreme_enabled",
    "get_profile",
    "list_profiles",
    "serialize_profile_match_fields",
]
