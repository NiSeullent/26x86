"""
Track H — CoreAnimation / QuartzCore gate analysis (Tahoe Metal AMD).

Default: stock Tahoe QuartzCore. Extreme double latch opens Non-Metal
QuartzCore.framework experiment (no permanent blocked=True path).
Integration into shared sys_patch: ``*.stage-H`` only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

from .iosurface_analysis import (
    EVIDENCE_URLS,
    SEQUOIA_XNU_MAJOR,
    TAHOE_XNU_MAJOR,
    is_extreme_enabled,
    is_extreme_iosurface_ca_opt_in,
    scan_avx_markers,
)

QUARTZCORE_FRAMEWORK_PAYLOAD_PREFIX = "10.15.7-"

CA_BOOT_ARG_RECOMMENDATIONS: tuple[dict[str, str], ...] = (
    {"arg": "agdpmod=pikera", "role": "WhateverGreen AGDC (Vega/Polaris)", "safe_for_metal_vega": "yes"},
    {"arg": "agdpmod=vit9696", "role": "WhateverGreen AGDC alternate", "safe_for_metal_vega": "yes"},
    {"arg": "keepsyms=1", "role": "panic symbolication for extreme probes", "safe_for_metal_vega": "yes"},
    {"arg": "-igfxvesa", "role": "Intel VESA — not AMD Vega", "safe_for_metal_vega": "no"},
    {"arg": "ngfxgl=1", "role": "Nvidia GL — not AMD Vega", "safe_for_metal_vega": "no"},
)

CA_DEBUG_ENV_HINTS: tuple[str, ...] = (
    "CA_DEBUG_TRANSACTIONS=1",
    "MTL_HUD_ENABLED=1",
    "OS_ACTIVITY_MODE=debug",
)


@dataclass(frozen=True)
class CoreAnimationGateReport:
    xnu_major: int
    metal_path_recommended: bool
    non_metal_quartzcore_experiment_open: bool
    framework_payload: Optional[str]
    payload_framework_present: bool
    avx_markers_in_payload: dict[str, int] = field(default_factory=dict)
    cametal_string_hits: int = 0
    notes: tuple[str, ...] = ()
    boot_args_metal_vega: tuple[str, ...] = ()
    evidence_urls: tuple[str, ...] = EVIDENCE_URLS


def quartzcore_framework_payload_folder(xnu_major: int) -> str:
    return f"{QUARTZCORE_FRAMEWORK_PAYLOAD_PREFIX}{min(xnu_major, SEQUOIA_XNU_MAJOR)}"


def _search_roots(search_roots: Optional[Iterable[Path]] = None) -> list[Path]:
    if search_roots is not None:
        return [Path(p) for p in search_roots]
    repo = Path(__file__).resolve().parents[2]
    candidates = [
        repo / "payloads" / "Kexts" / "Universal-Binaries",
        repo.parent / "26x86-PatcherSupportPkg" / "Universal-Binaries",
        repo / "payloads" / "Kexts" / "Community" / "Tahoe-Yellow-Screen" / "Universal-Binaries",
    ]
    return [p for p in candidates if p.is_dir()] or candidates


def resolve_quartzcore_framework_payload(
    xnu_major: int, search_roots: Optional[Iterable[Path]] = None
) -> Optional[str]:
    folder = quartzcore_framework_payload_folder(xnu_major)
    rel = Path("System/Library/Frameworks/QuartzCore.framework/Versions/A/QuartzCore")
    for root in _search_roots(search_roots):
        candidate = root / folder / rel
        if candidate.is_file() and candidate.stat().st_size > 0:
            return folder
    return None


def metal_vega_boot_args() -> tuple[str, ...]:
    return tuple(r["arg"] for r in CA_BOOT_ARG_RECOMMENDATIONS if r["safe_for_metal_vega"] == "yes")


def analyze_coreanimation_gates(
    xnu_major: int,
    *,
    has_metal_amd: bool = True,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> CoreAnimationGateReport:
    notes: list[str] = []
    experiment_open = is_extreme_iosurface_ca_opt_in(environ)
    folder = resolve_quartzcore_framework_payload(xnu_major, search_roots=search_roots)
    avx: dict[str, int] = {}
    cametal = 0
    if folder is not None:
        for root in _search_roots(search_roots):
            binary = (
                root
                / folder
                / "System/Library/Frameworks/QuartzCore.framework/Versions/A/QuartzCore"
            )
            if binary.is_file():
                avx = scan_avx_markers(binary)
                try:
                    data = binary.read_bytes()
                except OSError:
                    data = b""
                cametal = data.count(b"CAMetal")
                break

    if experiment_open:
        notes.append(
            "Extreme latch on: Non-Metal QuartzCore.framework experiment is open "
            "(ABI / WindowServer crash risk)."
        )
    else:
        notes.append(
            "Default: stock Tahoe QuartzCore. Double latch opens Non-Metal CA experiment."
        )
    if has_metal_amd and not experiment_open:
        notes.append(
            "Metal 31001 Vega default prefers Tahoe QuartzCore over Metal 3802 "
            "QuartzCore default.metallib."
        )
    if cametal:
        notes.append(
            f"Catalina QuartzCore payload contains CAMetal markers ({cametal})."
        )
    if not any(avx.get(k, 0) for k in ("AVX", "avx", "vzeroupper")):
        notes.append(
            "QuartzCore Non-Metal payload lacks AVX string markers; compiler AVX2 gates "
            "remain in AMD OpenCL/GL non-AVX2.0 (already on Vega path)."
        )

    return CoreAnimationGateReport(
        xnu_major=xnu_major,
        metal_path_recommended=has_metal_amd and not experiment_open,
        non_metal_quartzcore_experiment_open=experiment_open,
        framework_payload=folder or quartzcore_framework_payload_folder(xnu_major),
        payload_framework_present=folder is not None,
        avx_markers_in_payload=avx,
        cametal_string_hits=cametal,
        notes=tuple(notes),
        boot_args_metal_vega=metal_vega_boot_args(),
    )


def serialize_coreanimation_fields(
    xnu_major: Optional[int] = None,
    *,
    has_metal_amd: bool = True,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    major = TAHOE_XNU_MAJOR if xnu_major is None else int(xnu_major)
    report = analyze_coreanimation_gates(
        major,
        has_metal_amd=has_metal_amd,
        search_roots=search_roots,
        environ=environ,
    )
    return {
        "coreanimation_metal_path_recommended": report.metal_path_recommended,
        "coreanimation_non_metal_experiment_open": report.non_metal_quartzcore_experiment_open,
        "coreanimation_framework_payload": report.framework_payload,
        "coreanimation_payload_present": report.payload_framework_present,
        "coreanimation_avx_markers": dict(report.avx_markers_in_payload),
        "coreanimation_cametal_markers": report.cametal_string_hits,
        "coreanimation_notes": list(report.notes),
        "coreanimation_boot_args_metal_vega": list(report.boot_args_metal_vega),
        "coreanimation_debug_env_hints": list(CA_DEBUG_ENV_HINTS),
        "coreanimation_evidence_urls": list(report.evidence_urls),
        "x86_extreme": is_extreme_enabled(environ),
        "x86_extreme_iosurface_ca": is_extreme_iosurface_ca_opt_in(environ),
    }
