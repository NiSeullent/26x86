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
from .metallib_opaque import (
    opaque_shader_windowserver_relationship,
    probe_window_server_opaque_cache,
    serialize_opaque_shader_fields,
)
from .metallib_preflight import (
    assess_metallib_gaps,
    gated_metal_31001_common_patches,
    serialize_metallib_preflight_fields,
)
from .skylight_lut import (
    enumerate_evidence_skylight_plugins,
    resolve_renderbox_metallib_payload,
    serialize_skylight_lut_fields,
)
from .skylight_tracks import (
    merge_sys_patch_hooks,
    serialize_skylight_lut_tracks,
)
from .yellow_screen import (
    SOCKET_AMD_YELLOW_SCREEN_MODELS,
    STOCK_GCN_AGDP_MODELS,
    classify_gpu_family,
    recommended_efi_graphics_fixes,
    resolve_legacy_amd_mtl_payload,
    serialize_yellow_screen_fields,
    should_disable_window_server_caching,
    socket_amd_needs_kdkless,
    yellow_screen_mitigations,
    yellow_screen_risk,
)

__all__ = [
    "PreAvxMacProReport",
    "SOCKET_AMD_YELLOW_SCREEN_MODELS",
    "STOCK_GCN_AGDP_MODELS",
    "TAHOE_BLOCKED_PATCH_IDS",
    "TAHOE_XNU_MAJOR",
    "assess_metallib_gaps",
    "classify_gpu_family",
    "detect_pre_avx_mac_pro",
    "enumerate_evidence_skylight_plugins",
    "gated_metal_31001_common_patches",
    "merge_sys_patch_hooks",
    "opaque_shader_windowserver_relationship",
    "probe_window_server_opaque_cache",
    "read_cpu_features_from_sysctl",
    "recommended_efi_graphics_fixes",
    "resolve_legacy_amd_mtl_payload",
    "resolve_renderbox_metallib_payload",
    "serialize_graphics_detect_fields",
    "serialize_metallib_preflight_fields",
    "serialize_opaque_shader_fields",
    "serialize_skylight_lut_fields",
    "serialize_skylight_lut_tracks",
    "serialize_yellow_screen_fields",
    "should_disable_window_server_caching",
    "should_strip_tahoe_legacy_gpu_patches",
    "socket_amd_needs_kdkless",
    "tahoe_blocked_patch_ids",
    "yellow_screen_mitigations",
    "yellow_screen_risk",
]
