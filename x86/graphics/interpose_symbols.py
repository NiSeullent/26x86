"""
Track I — Symbol catalog for Metal / SkyLight / CoreDisplay interpose.

Evidence-backed public / documented symbols only. No guessed private
CoreDisplay LUT byte offsets (OCLP-T2 #194 leaves private names unpublished).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class InterposeSymbol:
    name: str
    library: str
    purpose: str
    evidence: str
    risk: str
    mode_group: str
    default_enabled: bool = False


INTERPOSE_SYMBOLS: tuple[InterposeSymbol, ...] = (
    InterposeSymbol(
        name="sysctlbyname",
        library="libSystem.B.dylib",
        purpose="Userspace AVX feature-bit probe spoof (hw.optional.avx*). No opcode emulation.",
        evidence="Darwin sysctl(3); Safari26-PreAVX is JSC-only",
        risk="high",
        mode_group="avx",
    ),
    InterposeSymbol(
        name="sysctl",
        library="libSystem.B.dylib",
        purpose="MIB-based AVX feature queries (companion to sysctlbyname).",
        evidence="Darwin sysctl(3)",
        risk="high",
        mode_group="avx",
    ),
    InterposeSymbol(
        name="CGDisplayGammaTableCapacity",
        library="CoreGraphics",
        purpose="Observe display gamma table size (LUT path probe).",
        evidence="CGDisplay.h; OCLP-T2 #194 ICC/LUT hypotheses",
        risk="medium",
        mode_group="lut",
    ),
    InterposeSymbol(
        name="CGGetDisplayTransferByTable",
        library="CoreGraphics",
        purpose="Read per-channel transfer tables (log / identity override).",
        evidence="CGDisplay.h",
        risk="medium",
        mode_group="lut",
    ),
    InterposeSymbol(
        name="CGSetDisplayTransferByTable",
        library="CoreGraphics",
        purpose="Force identity gamma when X86_INTERPOSE_LUT=identity.",
        evidence="CGDisplay.h",
        risk="extreme",
        mode_group="lut",
    ),
    InterposeSymbol(
        name="ColorSyncProfileCreateWithURL",
        library="ColorSync",
        purpose="ICC profile open probe.",
        evidence="ColorSync.h",
        risk="low",
        mode_group="lut",
    ),
    InterposeSymbol(
        name="ColorSyncTransformCreate",
        library="ColorSync",
        purpose="Color transform creation probe (LUT pipeline).",
        evidence="ColorSync.h",
        risk="medium",
        mode_group="lut",
    ),
    InterposeSymbol(
        name="SkyLightPluginEntry",
        library="SkyLightPlugins/<stem>.dylib",
        purpose="moraea/ASentientBot plugin entry; stock Tahoe SkyLight does not call this.",
        evidence="ASentientBot/monterey 2022-1-16",
        risk="high",
        mode_group="loader",
    ),
    InterposeSymbol(
        name="MTLCreateSystemDefaultDevice",
        library="Metal",
        purpose="Log default Metal device selection (catalog; ObjC companion TBD).",
        evidence="Metal.h; moraea sequoia 31001 interposer lineage",
        risk="medium",
        mode_group="metal",
    ),
)

EVIDENCE_URLS: dict[str, str] = {
    "oclp_t2_194": "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194",
    "asentientbot_skylight_plugins": "https://github.com/ASentientBot/monterey",
    "moraea_31001_interposer": (
        "https://github.com/moraea/misc-patches/tree/main/sequoia%2031001%20interposer"
    ),
    "moraea_non_metal": "https://github.com/moraea/non-metal-frameworks",
    "safari26_preavx": "https://github.com/kilinccagatay/Safari26-PreAVX-Fix",
    "dyld_interpose": (
        "https://opensource.apple.com/source/dyld/dyld-852.2/"
        "include/mach-o/dyld-interposing.h.auto.html"
    ),
}

AVX_SYSCTL_KEYS: tuple[str, ...] = (
    "hw.optional.avx1_0",
    "hw.optional.avx2_0",
    "hw.optional.avx512f",
)

FORBIDDEN_ACTIONS: tuple[str, ...] = (
    "Guessed CoreDisplay/SkyLight private byte patches",
    "Redistributing Apple proprietary frameworks or metallibs",
    "Enabling Metal 3802 / Non-Metal shared Tahoe patches by default",
    "DYLD_INSERT into WindowServer without SIP-aware opt-in",
)


def symbols_by_mode_group(group: str) -> list[InterposeSymbol]:
    return [s for s in INTERPOSE_SYMBOLS if s.mode_group == group]


def serialize_symbol_catalog() -> list[dict[str, Any]]:
    return [asdict(s) for s in INTERPOSE_SYMBOLS]
