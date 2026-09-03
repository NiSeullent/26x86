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

__all__ = [
    "PreAvxMacProReport",
    "TAHOE_BLOCKED_PATCH_IDS",
    "TAHOE_XNU_MAJOR",
    "detect_pre_avx_mac_pro",
    "read_cpu_features_from_sysctl",
    "serialize_graphics_detect_fields",
    "should_strip_tahoe_legacy_gpu_patches",
    "tahoe_blocked_patch_ids",
]
