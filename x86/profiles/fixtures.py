"""Detect fixtures for Track K — MacPro5,1 pre-AVX + Vega 64 Tahoe."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

MACPRO51_WESTMERE_FEATURES: list[str] = [
    "FPU", "VME", "DE", "PSE", "TSC", "MSR", "PAE", "MCE", "CX8", "APIC", "SEP",
    "MTRR", "PGE", "MCA", "CMOV", "PAT", "PSE36", "CLFSH", "DS", "ACPI", "MMX",
    "FXSR", "SSE", "SSE2", "SS", "HTT", "TM", "PBE", "SSE3", "DTES64", "MON",
    "DSCPL", "VMX", "SMX", "EST", "TM2", "SSSE3", "CX16", "TPR", "PDCM", "DCA",
    "SSE4.1", "SSE4.2", "x2APIC", "POPCNT", "AES",
]
MACPRO51_WESTMERE_LEAF7: list[str] = []
VEGA64_DEVICE_ID = 0x687F
TAHOE_XNU_MAJOR = 25


def vega64_gpu(*, name: str = "AMD Radeon RX Vega 64") -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        vendor_id=0x1002,
        device_id=VEGA64_DEVICE_ID,
        arch=SimpleNamespace(name="Vega"),
    )


def macpro5_vega64_detect_kwargs() -> dict[str, Any]:
    return {
        "model": "MacPro5,1",
        "gpus": [vega64_gpu()],
        "cpu_features": list(MACPRO51_WESTMERE_FEATURES),
        "cpu_leaf7_features": list(MACPRO51_WESTMERE_LEAF7),
        "auto_pre_avx_patch": True,
        "xnu_major": TAHOE_XNU_MAJOR,
        "host_is_macos": True,
    }


def macpro5_vega64_fixture_payload() -> dict[str, Any]:
    from x86.pre_avx.detect import build_detect_fields, serialize_detect_fields
    from x86.profiles.macpro5_vega64_tahoe import PROFILE, PROFILE_ID

    fields = build_detect_fields(**macpro5_vega64_detect_kwargs())
    payload = serialize_detect_fields(fields)
    payload.update(
        {
            "platform": "macOS",
            "host_is_mac": True,
            "model": "MacPro5,1",
            "marketing_name": "Mac Pro (2010–2012)",
            "real_model": "MacPro5,1",
            "build_model": "MacPro5,1",
            "cpu": "Intel(R) Xeon(R) CPU E5620 @ 2.40GHz",
            "gpus": [
                {
                    "name": "AMD Radeon RX Vega 64",
                    "vendor": hex(0x1002),
                    "device": hex(VEGA64_DEVICE_ID),
                }
            ],
            "os_version": "26.0",
            "os_build": "25A354",
            "profile_id": PROFILE_ID,
            "profile_match": True,
            "profile_title": PROFILE.title,
            "recommended_profile": PROFILE_ID,
            "profile_apply": "python -m x86.profiles apply macpro5-vega64-tahoe",
        }
    )
    return payload


def matches_macpro5_vega64_profile(
    *,
    model: str,
    gpu_family: str | None = None,
    gpu_archs: list[Any] | None = None,
    avx_available: bool | None = None,
    pre_avx_mac_pro: bool | None = None,
) -> bool:
    if model != "MacPro5,1":
        return False
    if pre_avx_mac_pro is False:
        return False
    if avx_available is True:
        return False
    family = gpu_family
    if family is None and gpu_archs is not None:
        from x86.graphics.yellow_screen import classify_gpu_family

        family = classify_gpu_family(model, gpu_archs)
    return family == "vega"
