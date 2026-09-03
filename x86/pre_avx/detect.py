"""
Pre-AVX Mac Pro detection and Metal patch variant hints for 26x86 Phase 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from opencore_legacy_patcher.datasets.os_data import os_data

from x86.graphics.detect import (
    MAC_PRO_MODELS,
    detect_pre_avx_mac_pro,
    read_cpu_features_from_sysctl,
    serialize_graphics_detect_fields,
)

PHASE1_PRE_AVX_MAC_PRO_MODELS: frozenset[str] = frozenset({"MacPro5,1", "MacPro6,1"})


class MetalPatchVariant(str, Enum):
    METAL_3802 = "3802"
    METAL_31001 = "31001"
    NON_METAL = "non_metal"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PreAvxDetectFields:
    pre_avx_mac_pro: bool
    recommended_metal_patch: str
    avx_available: bool
    has_avx2: bool
    safari_pre_avx_fix_recommended: bool
    auto_pre_avx_patch_enabled: bool
    model: str
    notes: tuple[str, ...]
    xnu_major: Optional[int] = None
    cpu_features: Optional[list[str]] = None
    cpu_leaf7_features: Optional[list[str]] = None
    host_is_macos: bool = True
    cpu_flags: Optional[tuple[str, ...]] = None
    gpu_archs: Optional[tuple[Any, ...]] = None


def read_avx_capabilities(
    cpu_features: Optional[list[str]] = None,
    cpu_leaf7_features: Optional[list[str]] = None,
) -> tuple[bool, bool]:
    """Return (avx_available, has_avx2)."""
    if cpu_features is None or cpu_leaf7_features is None:
        sys_features, sys_leaf7, _brand = read_cpu_features_from_sysctl()
        if cpu_features is None:
            cpu_features = sys_features
        if cpu_leaf7_features is None:
            cpu_leaf7_features = sys_leaf7

    has_avx1 = "AVX1.0" in (cpu_features or [])
    has_avx2 = "AVX2" in (cpu_leaf7_features or [])
    return has_avx1, has_avx2


def is_pre_avx_mac_pro(model: str, avx_available: bool, has_avx2: bool) -> bool:
    """
    Phase 1 Pre-AVX Mac Pro gate (MacPro5,1 / MacPro6,1).

    MacPro5,1: pre-AVX when AVX1 absent (Westmere) or AVX2 absent.
    MacPro6,1: pre-AVX2 when AVX2 absent (Ivy Bridge Xeon).
    """
    if model not in PHASE1_PRE_AVX_MAC_PRO_MODELS:
        return False
    if model == "MacPro5,1":
        return not avx_available or not has_avx2
    if model == "MacPro6,1":
        return not has_avx2
    return False


def _gpu_name(value: Any) -> str:
    return str(getattr(value, "name", value or "")).lower()


def recommend_metal_patch(model: str, gpus: Optional[list[Any]] = None) -> MetalPatchVariant:
    """
    Heuristic Metal variant hint: 3802 / 31001 / non_metal.

    Community docs sometimes say 31002; OCLP uses METAL_31001 internally.
    """
    names = " ".join(_gpu_name(gpu) for gpu in (gpus or []))

    non_metal_tokens = (
        "iron lake",
        "sandy bridge",
        "geforce 9400",
        "geforce 320m",
        "geforce gt 330",
        "geforce gt 120",
        "geforce 8800",
        "geforce gtx 285",
        "radeon x",
        "mobility radeon",
        "terascale",
    )
    metal_3802_tokens = (
        "kepler",
        "ivy bridge",
        "haswell",
        "hd 4000",
        "hd 5000",
        "quadro k",
        "gtx 6",
        "gtx 7",
        "gt 6",
        "gt 7",
    )
    metal_31001_tokens = (
        "firepro d",
        "firepro w",
        "polaris",
        "vega",
        "navi",
        "radeon pro",
        "radeon rx",
        "legacy gcn",
        "broadwell",
        "skylake",
        "hd 5",
        "iris",
    )

    if any(token in names for token in non_metal_tokens):
        return MetalPatchVariant.NON_METAL
    if any(token in names for token in metal_31001_tokens):
        return MetalPatchVariant.METAL_31001
    if any(token in names for token in metal_3802_tokens):
        return MetalPatchVariant.METAL_3802

    if model == "MacPro6,1":
        return MetalPatchVariant.METAL_31001
    if model == "MacPro5,1":
        return MetalPatchVariant.METAL_3802
    if model in MAC_PRO_MODELS:
        return MetalPatchVariant.UNKNOWN
    return MetalPatchVariant.UNKNOWN


def build_detect_fields(
    model: str,
    *,
    gpus: Optional[list[Any]] = None,
    cpu_features: Optional[list[str]] = None,
    cpu_leaf7_features: Optional[list[str]] = None,
    auto_pre_avx_patch: bool = True,
    xnu_major: Optional[int] = None,
    host_is_macos: Optional[bool] = None,
) -> PreAvxDetectFields:
    """Build CLI/GUI detect payload fields for Pre-AVX Mac Pro handling."""
    from x86.platform import is_macos as _is_macos

    macos = _is_macos() if host_is_macos is None else host_is_macos
    avx_available, has_avx2 = read_avx_capabilities(
        cpu_features if cpu_features is not None else ([] if not macos else None),
        cpu_leaf7_features if cpu_leaf7_features is not None else ([] if not macos else None),
    )
    report = detect_pre_avx_mac_pro(
        model,
        cpu_features=cpu_features,
        cpu_leaf7_features=cpu_leaf7_features,
        xnu_major=xnu_major,
    )
    pre_avx = is_pre_avx_mac_pro(model, avx_available, has_avx2)
    metal = recommend_metal_patch(model, gpus)

    from x86.patch.safari26_preavx import evaluate

    combined_flags = list(cpu_features or []) + list(cpu_leaf7_features or [])
    safari_decision = evaluate(
        model,
        cpu_flags=combined_flags,
        settings={"auto_pre_avx_patch": auto_pre_avx_patch, "safari26_preavx_fix": auto_pre_avx_patch},
        host_is_macos=macos,
        respect_host_avx=True,
    )
    safari_fix = auto_pre_avx_patch and safari_decision.should_apply

    notes = list(report.notes)
    if pre_avx and auto_pre_avx_patch:
        notes.append("auto_pre_avx_patch 활성 — EFI 빌드 시 Safari26 Pre-AVX RestrictEvents 후보.")
    elif pre_avx:
        notes.append("auto_pre_avx_patch 비활성 — Pre-AVX 자동 패치 건너뜀.")

    return PreAvxDetectFields(
        pre_avx_mac_pro=pre_avx,
        recommended_metal_patch=metal.value,
        avx_available=avx_available,
        has_avx2=has_avx2,
        safari_pre_avx_fix_recommended=safari_fix,
        auto_pre_avx_patch_enabled=auto_pre_avx_patch,
        model=model,
        notes=tuple(notes),
        xnu_major=xnu_major,
        cpu_features=cpu_features,
        cpu_leaf7_features=cpu_leaf7_features,
        host_is_macos=macos,
        cpu_flags=tuple(combined_flags),
        gpu_archs=tuple(gpus) if gpus else (),
    )


def serialize_detect_fields(fields: PreAvxDetectFields) -> dict[str, Any]:
    from x86.patch.safari26_preavx import evaluate

    xnu = fields.xnu_major if fields.xnu_major is not None else os_data.tahoe.value
    graphics = serialize_graphics_detect_fields(
        fields.model,
        xnu_major=xnu,
        cpu_features=fields.cpu_features,
        cpu_leaf7_features=fields.cpu_leaf7_features,
        gpu_archs=list(fields.gpu_archs) if fields.gpu_archs else None,
    )
    payload = {
        "pre_avx_mac_pro": fields.pre_avx_mac_pro,
        "recommended_metal_patch": fields.recommended_metal_patch,
        "avx_available": fields.avx_available,
        "avx2_available": fields.has_avx2,
        "has_avx2": fields.has_avx2,
        "safari_pre_avx_fix_recommended": fields.safari_pre_avx_fix_recommended,
        "auto_pre_avx_patch": fields.auto_pre_avx_patch_enabled,
        "pre_avx_notes": list(fields.notes),
        "safari26_preavx": evaluate(
            fields.model,
            cpu_flags=list(fields.cpu_flags or ()),
            settings={
                "auto_pre_avx_patch": fields.auto_pre_avx_patch_enabled,
                "safari26_preavx_fix": fields.auto_pre_avx_patch_enabled,
            },
            host_is_macos=fields.host_is_macos,
        ).as_dict(),
    }
    payload.update(graphics)
    return payload
