"""
Track H — IOSurface gate / fallback analysis for Tahoe Metal AMD (Vega).

Default (no extreme): recommend stock Tahoe Metal IOSurface.
Extreme double latch (``X86_EXTREME=1`` + ``X86_EXTREME_IOSURFACE_CA=1``):
Non-Metal IOSurface framework/kext experiments are **open** (KP risk on host).

No permanent blocked=True code path. Shared sys_patch/detect untouched
(integration via ``*.stage-H`` only).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

TAHOE_XNU_MAJOR = 25
SEQUOIA_XNU_MAJOR = 24
IOSURFACE_FRAMEWORK_PAYLOAD_PREFIX = "10.15.7-"
IOSURFACE_KEXT_PAYLOAD = "10.15.7"
EVIDENCE_URLS: tuple[str, ...] = (
    "https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167",
    "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194",
    "https://github.com/moraea/non-metal-frameworks",
)
AVX_STRING_NEEDLES: tuple[bytes, ...] = (b"AVX", b"avx", b"vzeroupper", b"vmovaps")


@dataclass(frozen=True)
class IOSurfaceGateReport:
    xnu_major: int
    metal_path_recommended: bool
    non_metal_iosurface_experiment_open: bool
    framework_payload: Optional[str]
    kext_payload: Optional[str]
    payload_framework_present: bool
    payload_kext_present: bool
    avx_markers_in_payload: dict[str, int] = field(default_factory=dict)
    notes: tuple[str, ...] = ()
    evidence_urls: tuple[str, ...] = EVIDENCE_URLS


def is_extreme_enabled(environ: Optional[dict[str, str]] = None) -> bool:
    env = environ if environ is not None else os.environ
    return str(env.get("X86_EXTREME", "")).strip() == "1"


def is_extreme_iosurface_ca_opt_in(environ: Optional[dict[str, str]] = None) -> bool:
    """Double latch opens Non-Metal IOSurface / QuartzCore experiments."""
    env = environ if environ is not None else os.environ
    return is_extreme_enabled(env) and str(
        env.get("X86_EXTREME_IOSURFACE_CA", "")
    ).strip() == "1"


def iosurface_framework_payload_folder(xnu_major: int) -> str:
    return f"{IOSURFACE_FRAMEWORK_PAYLOAD_PREFIX}{min(xnu_major, SEQUOIA_XNU_MAJOR)}"


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


def resolve_iosurface_framework_payload(
    xnu_major: int, search_roots: Optional[Iterable[Path]] = None
) -> Optional[str]:
    folder = iosurface_framework_payload_folder(xnu_major)
    rel = Path("System/Library/Frameworks/IOSurface.framework/Versions/A/IOSurface")
    for root in _search_roots(search_roots):
        candidate = root / folder / rel
        if candidate.is_file() and candidate.stat().st_size > 0:
            return folder
    return None


def resolve_iosurface_kext_payload(
    search_roots: Optional[Iterable[Path]] = None,
) -> Optional[str]:
    """Non-Metal Common uses IOSurface.kext from ``10.15.7``."""
    rel = Path("System/Library/Extensions/IOSurface.kext")
    for root in _search_roots(search_roots):
        candidate = root / IOSURFACE_KEXT_PAYLOAD / rel
        if candidate.is_dir() or (candidate / "Contents" / "Info.plist").is_file():
            return IOSURFACE_KEXT_PAYLOAD
        # binary may sit under MacOS/
        binary = candidate / "Contents" / "MacOS" / "IOSurface"
        if binary.is_file():
            return IOSURFACE_KEXT_PAYLOAD
    return None


def scan_avx_markers(path: Path) -> dict[str, int]:
    try:
        data = path.read_bytes()
    except OSError:
        return {}
    return {n.decode("latin1"): data.count(n) for n in AVX_STRING_NEEDLES if n in data}


def analyze_iosurface_gates(
    xnu_major: int,
    *,
    has_metal_amd: bool = True,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> IOSurfaceGateReport:
    notes: list[str] = []
    experiment_open = is_extreme_iosurface_ca_opt_in(environ)
    folder = resolve_iosurface_framework_payload(xnu_major, search_roots=search_roots)
    kext_folder = resolve_iosurface_kext_payload(search_roots=search_roots)
    avx: dict[str, int] = {}
    if folder is not None:
        for root in _search_roots(search_roots):
            binary = (
                root
                / folder
                / "System/Library/Frameworks/IOSurface.framework/Versions/A/IOSurface"
            )
            if binary.is_file():
                avx = scan_avx_markers(binary)
                break

    if experiment_open:
        notes.append(
            "Extreme latch on: Non-Metal IOSurface.framework/kext experiment is open "
            "(host KP / ABI risk — spare machine only)."
        )
    else:
        notes.append(
            "Default: stock Tahoe Metal IOSurface. Set X86_EXTREME=1 and "
            "X86_EXTREME_IOSURFACE_CA=1 to open Non-Metal IOSurface experiments."
        )
    if has_metal_amd and not experiment_open:
        notes.append("Metal 31001 default path prefers stock Tahoe IOSurface.")
    if avx:
        notes.append(f"Payload AVX string markers (informational): {avx}")
    else:
        notes.append(
            "Catalina IOSurface payload has no AVX string markers; AVX2 graphics SIGILL "
            "risk is documented in AMD OpenCL/GL (12.5 non-AVX2.0), not IOSurface."
        )

    return IOSurfaceGateReport(
        xnu_major=xnu_major,
        metal_path_recommended=has_metal_amd and not experiment_open,
        non_metal_iosurface_experiment_open=experiment_open,
        framework_payload=folder or iosurface_framework_payload_folder(xnu_major),
        kext_payload=kext_folder,
        payload_framework_present=folder is not None,
        payload_kext_present=kext_folder is not None,
        avx_markers_in_payload=avx,
        notes=tuple(notes),
    )


def serialize_iosurface_fields(
    xnu_major: Optional[int] = None,
    *,
    has_metal_amd: bool = True,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    major = TAHOE_XNU_MAJOR if xnu_major is None else int(xnu_major)
    report = analyze_iosurface_gates(
        major,
        has_metal_amd=has_metal_amd,
        search_roots=search_roots,
        environ=environ,
    )
    return {
        "iosurface_metal_path_recommended": report.metal_path_recommended,
        "iosurface_non_metal_experiment_open": report.non_metal_iosurface_experiment_open,
        "iosurface_framework_payload": report.framework_payload,
        "iosurface_kext_payload": report.kext_payload,
        "iosurface_payload_present": report.payload_framework_present,
        "iosurface_kext_payload_present": report.payload_kext_present,
        "iosurface_avx_markers": dict(report.avx_markers_in_payload),
        "iosurface_notes": list(report.notes),
        "iosurface_evidence_urls": list(report.evidence_urls),
        "x86_extreme": is_extreme_enabled(environ),
        "x86_extreme_iosurface_ca": is_extreme_iosurface_ca_opt_in(environ),
    }
