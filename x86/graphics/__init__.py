"""
26x86 graphics detection — Pre-AVX Mac Pro / Tahoe policy gating.
"""

from .detect import (
    PreAvxMacProReport,
    TAHOE_BLOCKED_PATCH_IDS,
    TAHOE_XNU_MAJOR,
    detect_pre_avx_mac_pro,
    read_cpu_features_from_sysctl,
    serialize_graphics_detect_fields,
    should_strip_tahoe_legacy_gpu_patches,
    tahoe_blocked_patch_ids,
)
from .yellow_screen import (
    SOCKET_AMD_YELLOW_SCREEN_MODELS,
    STOCK_GCN_AGDP_MODELS,
    classify_gpu_family,
    recommended_efi_graphics_fixes,
    serialize_yellow_screen_fields,
    yellow_screen_risk,
)

__all__ = [
    "PreAvxMacProReport",
    "SOCKET_AMD_YELLOW_SCREEN_MODELS",
    "STOCK_GCN_AGDP_MODELS",
    "TAHOE_BLOCKED_PATCH_IDS",
    "TAHOE_XNU_MAJOR",
    "classify_gpu_family",
    "detect_pre_avx_mac_pro",
    "read_cpu_features_from_sysctl",
    "recommended_efi_graphics_fixes",
    "serialize_graphics_detect_fields",
    "serialize_yellow_screen_fields",
    "should_strip_tahoe_legacy_gpu_patches",
    "tahoe_blocked_patch_ids",
    "yellow_screen_risk",
]
