"""
Pre-AVX Mac Pro detection and Safari26 RestrictEvents integration for 26x86.
"""

from .detect import (
    MetalPatchVariant,
    PreAvxDetectFields,
    build_detect_fields,
    detect_pre_avx_mac_pro,
    is_pre_avx_mac_pro,
    read_avx_capabilities,
)
from .patch import (
    SAFARI26_PRE_AVX_FIX_NOTICE,
    SAFARI26_PRE_AVX_FIX_SOURCE,
    resolve_restrict_events_bundle,
    should_apply_safari26_pre_avx_fix,
)

__all__ = [
    "MetalPatchVariant",
    "PreAvxDetectFields",
    "SAFARI26_PRE_AVX_FIX_NOTICE",
    "SAFARI26_PRE_AVX_FIX_SOURCE",
    "build_detect_fields",
    "detect_pre_avx_mac_pro",
    "is_pre_avx_mac_pro",
    "read_avx_capabilities",
    "resolve_restrict_events_bundle",
    "should_apply_safari26_pre_avx_fix",
]
