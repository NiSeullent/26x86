"""
Pre-AVX Mac Pro / graphics capability detection for 26x86.

Used by x86 CLI (`detect --json`), GUI bridge status, and
HardwarePatchsetDetection (Tahoe graphics gating).
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

# macOS 26 Tahoe kernel major (matches opencore_legacy_patcher.datasets.os_data.tahoe).
TAHOE_XNU_MAJOR = 25

# Mac Pro models commonly associated with pre-AVX2 CPUs or legacy GPU stacks.
MAC_PRO_MODELS: frozenset[str] = frozenset({
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "MacPro6,1",
})

# Westmere-and-older socket Macs that share the same AVX profile as Mac Pro 5,1.
PRE_AVX2_MAC_PRO_LIKE: frozenset[str] = frozenset({
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "Xserve2,1",
    "Xserve3,1",
})

# Shared root patches intentionally blocked on Tahoe (safety guards in shared_patches/).
TAHOE_BLOCKED_PATCH_IDS: tuple[str, ...] = (
    "Metal 3802 Common",
    "Metal 3802 Common Extended",
    "Metal 3802 .metallibs",
    "Non-Metal Common",
    "Non-Metal IOAccelerator Common",
    "Non-Metal CoreDisplay Common",
    "Non-Metal Enforcement",
)


@dataclass(frozen=True)
class PreAvxMacProReport:
    """Structured result for graphics gating decisions."""

    model: str
    is_mac_pro: bool
    is_pre_avx2_mac_pro_like: bool
    has_avx1: bool
    has_avx2: bool
    cpu_brand: str = ""
    recommended_tahoe_graphics_policy: str = "unknown"
    tahoe_blocked_patches: tuple[str, ...] = ()
    notes: list[str] = field(default_factory=list)


def tahoe_blocked_patch_ids(xnu_major: int) -> list[str]:
    """Return shared patch IDs blocked on Tahoe when xnu_major >= 25."""
    if xnu_major >= TAHOE_XNU_MAJOR:
        return list(TAHOE_BLOCKED_PATCH_IDS)
    return []


def read_cpu_features_from_sysctl() -> tuple[list[str], list[str], str]:
    """
    Read CPU feature flags via sysctl (macOS only).

    Returns:
        (features, leaf7_features, brand_string)
        Empty lists / brand on non-macOS or sysctl failure.
    """
    if sys.platform != "darwin":
        return [], [], ""

    def _sysctl(key: str) -> str:
        try:
            result = subprocess.run(
                ["/usr/sbin/sysctl", "-n", key],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return ""
            return result.stdout.strip()
        except OSError:
            return ""

    brand = _sysctl("machdep.cpu.brand_string")
    features_raw = _sysctl("machdep.cpu.features")
    leaf7_raw = _sysctl("machdep.cpu.leaf7_features")

    features = features_raw.split() if features_raw else []
    leaf7 = leaf7_raw.split() if leaf7_raw else []
    return features, leaf7, brand


def detect_pre_avx_mac_pro(
    model: str,
    cpu_features: Optional[list[str]] = None,
    cpu_leaf7_features: Optional[list[str]] = None,
    cpu_brand: Optional[str] = None,
    xnu_major: Optional[int] = None,
) -> PreAvxMacProReport:
    """
    Detect whether the host is a Mac Pro (or Xserve) class machine with
    pre-AVX2 CPU characteristics relevant to Tahoe graphics patching.

    Args:
        model: SMBIOS model (real_model preferred over spoofed).
        cpu_features: machdep.cpu.features tokens; sysctl if None on macOS.
        cpu_leaf7_features: machdep.cpu.leaf7_features tokens.
        cpu_brand: optional brand string for logging.
        xnu_major: optional kernel major for tahoe_blocked_patches list.
    """
    notes: list[str] = []
    is_mac_pro = model in MAC_PRO_MODELS
    is_pre_avx2_socket_class = model in PRE_AVX2_MAC_PRO_LIKE

    if cpu_features is None or cpu_leaf7_features is None:
        sys_features, sys_leaf7, sys_brand = read_cpu_features_from_sysctl()
        if cpu_features is None:
            cpu_features = sys_features
        if cpu_leaf7_features is None:
            cpu_leaf7_features = sys_leaf7
        if cpu_brand is None and sys_brand:
            cpu_brand = sys_brand

    has_avx1 = "AVX1.0" in (cpu_features or [])
    has_avx2 = "AVX2" in (cpu_leaf7_features or [])

    if model == "MacPro6,1":
        # Ivy Bridge Xeon: AVX1 yes, AVX2 no — dual GCN 7000, EFI agdpmod critical.
        policy = "tahoe_gcn_efi_only"
        notes.append(
            "MacPro6,1: Metal 3802/Non-Metal root patches are blocked on Tahoe "
            "(kernel panic / yellow screen risk). Use AMD Legacy GCN kext patches "
            "and EFI DeviceProperties (agdpmod / shikigva) instead."
        )
    elif is_pre_avx2_socket_class and not has_avx2:
        policy = "tahoe_no_legacy_gpu_root_patch"
        notes.append(
            "Pre-AVX2 Mac Pro / Xserve: Metal 3802 and Non-Metal shared patches "
            "are safety-guarded on Tahoe; expect software/fallback rendering."
        )
    elif is_mac_pro and has_avx2:
        policy = "tahoe_modern_mac_pro"
        notes.append(
            "AVX2-capable Mac Pro (e.g. CPU upgrade): Polaris/Vega root kext path "
            "may apply; Metal 3802/Non-Metal shared patches remain blocked on Tahoe."
        )
    elif is_mac_pro:
        policy = "tahoe_mac_pro_review"
        notes.append("Mac Pro detected; verify CPU upgrade and GPU arch manually.")
    else:
        policy = "not_mac_pro"

    if not has_avx1:
        notes.append(
            "CPU lacks AVX1.0 — Safari 18.2+ / system AVX assumptions may crash."
        )

    blocked: tuple[str, ...] = ()
    if xnu_major is not None and is_mac_pro and tahoe_blocked_patch_ids(xnu_major):
        blocked = tuple(tahoe_blocked_patch_ids(xnu_major))

    return PreAvxMacProReport(
        model=model,
        is_mac_pro=is_mac_pro,
        is_pre_avx2_mac_pro_like=is_mac_pro and not has_avx2,
        has_avx1=has_avx1,
        has_avx2=has_avx2,
        cpu_brand=cpu_brand or "",
        recommended_tahoe_graphics_policy=policy,
        tahoe_blocked_patches=blocked,
        notes=notes,
    )


def should_strip_tahoe_legacy_gpu_patches(report: PreAvxMacProReport) -> bool:
    """True when 3802/Non-Metal hardware variants should be removed on Tahoe."""
    return report.recommended_tahoe_graphics_policy in {
        "tahoe_gcn_efi_only",
        "tahoe_no_legacy_gpu_root_patch",
    }


def serialize_graphics_detect_fields(
    model: str,
    xnu_major: Optional[int] = None,
    cpu_features: Optional[list[str]] = None,
    cpu_leaf7_features: Optional[list[str]] = None,
    cpu_brand: Optional[str] = None,
) -> dict[str, Any]:
    """JSON-friendly graphics policy fields for `x86 detect --json`."""
    report = detect_pre_avx_mac_pro(
        model=model,
        cpu_features=cpu_features,
        cpu_leaf7_features=cpu_leaf7_features,
        cpu_brand=cpu_brand,
        xnu_major=xnu_major,
    )
    return {
        "pre_avx_mac_pro": report.is_pre_avx2_mac_pro_like,
        "avx_available": report.has_avx1,
        "avx2_available": report.has_avx2,
        "recommended_tahoe_graphics_policy": report.recommended_tahoe_graphics_policy,
        "tahoe_blocked_patches": list(report.tahoe_blocked_patches),
        "graphics_policy_notes": list(report.notes),
    }
