"""
Track J — scan GPU compiler / compositor binaries for host AVX opcodes.

Scans standalone Metal/GPUCompiler paths and optional dyld shared-cache
``__TEXT`` slices. Does not modify binaries. Live shared-cache I/O is opt-in
(``probe_host=True`` or ``X86_EXTREME=1``).
"""

from __future__ import annotations

import os
import re
import struct
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

from x86.graphics.shader_avx_opcodes import (
    count_feature_strings,
    count_opcode_hits,
    dense_vmovaps_windows,
)

STANDALONE_TARGETS: tuple[str, ...] = (
    "/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions/Current/"
    "Libraries/libGPUCompilerImplLazy.dylib",
    "/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions/A/"
    "Libraries/openclc",
    "/System/Library/Frameworks/Metal.framework/Versions/A/XPCServices/"
    "MTLCompilerService.xpc/Contents/MacOS/MTLCompilerService",
    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources/"
    "default.metallib",
    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources/"
    "archive.metallib",
)

SHARED_CACHE_IMAGES: tuple[str, ...] = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLight",
    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/RenderBox",
    "/System/Library/Frameworks/Metal.framework/Versions/A/Metal",
    "/System/Library/Frameworks/QuartzCore.framework/Versions/A/QuartzCore",
    "/System/Library/Frameworks/CoreDisplay.framework/Versions/A/CoreDisplay",
    "/System/Library/PrivateFrameworks/MTLCompiler.framework/Versions/32023/MTLCompiler",
    "/System/Library/PrivateFrameworks/MTLCompiler.framework/Versions/32024/MTLCompiler",
    "/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions/32023/"
    "Libraries/libGPUCompilerImpl.dylib",
    "/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions/A/"
    "Libraries/libairutility.dylib",
    "/System/Library/PrivateFrameworks/GPUCompiler.framework/Versions/A/"
    "Libraries/libmetallinker.dylib",
)

DEFAULT_DYLD_DIR = Path(
    "/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld"
)
DEFAULT_CACHE_STEM = "dyld_shared_cache_x86_64"

SEQUOIA_155_BASELINE: dict[str, Any] = {
    "host": "MacPro5,1 Xeon X5675 Sequoia 15.5 24F74",
    "avx1_sysctl": 0,
    "findings": {
        "skylight_text_vmovaps_blocks": 0,
        "renderbox_text_vmovaps_blocks": 0,
        "metal_text_vmovaps_blocks": 0,
        "mtlcompiler_32023_vmovaps_blocks": 0,
        "mtlcompiler_32024_vmovaps_blocks": 0,
        "quartzcore_text_vmovaps_blocks": 0,
        "coredisplay_feature_strings": [
            "hw.optional.avx1_0",
            "hw.optional.avx2_0",
        ],
        "skylight_feature_strings": ["hw.optional.avx2_0"],
        "libGPUCompilerImplLazy_avx_macro_strings": True,
        "libGPUCompilerImplLazy_note": (
            "LLVM target-feature macros (+avx/-avx), not Safari-style trampoline"
        ),
        "metallib_host_vmovaps": 0,
        "safari_style_dense_runs": 0,
    },
    "verdict": (
        "No Safari26-style unconditional vmovaps save/restore trampoline in "
        "SkyLight/RenderBox/Metal/MTLCompiler/QuartzCore TEXT on this build. "
        "Compositor queries hw.optional.avx*; GPUCompiler strings are LLVM "
        "host-codegen feature toggles. Yellow screen ≠ AVX SIGILL."
    ),
}


@dataclass
class TargetScan:
    path: str
    present: bool
    source: str
    size_bytes: int = 0
    opcodes: dict[str, int] = field(default_factory=dict)
    feature_strings: dict[str, int] = field(default_factory=dict)
    dense_store_lo_runs: int = 0
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _scan_bytes(path: str, data: bytes, source: str) -> TargetScan:
    opcodes = count_opcode_hits(data)
    features = count_feature_strings(data)
    runs = len(dense_vmovaps_windows(data))
    notes: list[str] = []
    if path.endswith(".metallib") and sum(opcodes.values()) == 0:
        notes.append("metallib: no host VEX vmovaps prefixes (expected for AIR)")
    if runs:
        notes.append(
            f"dense vmovaps_store_lo windows: {runs} (Safari-like trampoline hint)"
        )
    if features:
        notes.append(f"feature needles: {sorted(features)}")
    return TargetScan(
        path=path,
        present=True,
        source=source,
        size_bytes=len(data),
        opcodes=opcodes,
        feature_strings=features,
        dense_store_lo_runs=runs,
        notes=notes,
    )


def scan_standalone_file(path: str | Path) -> TargetScan:
    p = Path(path)
    if not p.is_file():
        return TargetScan(path=str(path), present=False, source="missing")
    try:
        data = p.read_bytes()
    except OSError as exc:
        return TargetScan(
            path=str(path),
            present=False,
            source="missing",
            notes=[f"read failed: {exc}"],
        )
    return _scan_bytes(str(path), data, "standalone")


def _read_u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def _read_u64(buf: bytes, off: int) -> int:
    return struct.unpack_from("<Q", buf, off)[0]


def _cache_files(dyld_dir: Path, stem: str) -> list[Path]:
    files = [dyld_dir / stem]
    files.extend(dyld_dir / f"{stem}.{i:02d}" for i in range(1, 8))
    return [p for p in files if p.is_file()]


def _parse_map_text_ranges(map_text: str) -> dict[str, tuple[int, int]]:
    images: dict[str, tuple[int, int]] = {}
    current: Optional[str] = None
    for line in map_text.splitlines():
        if line.startswith("/"):
            current = line.strip()
        elif current and "__TEXT" in line:
            m = re.search(
                r"__TEXT\s+(0x[0-9A-Fa-f]+)\s+->\s+(0x[0-9A-Fa-f]+)",
                line,
            )
            if m:
                images[current] = (int(m.group(1), 16), int(m.group(2), 16))
    return images


def extract_shared_cache_text(
    va_start: int,
    va_end: int,
    *,
    dyld_dir: Path = DEFAULT_DYLD_DIR,
    stem: str = DEFAULT_CACHE_STEM,
) -> Optional[bytes]:
    size = va_end - va_start
    if size <= 0 or size > 200_000_000:
        return None
    for path in _cache_files(dyld_dir, stem):
        try:
            with path.open("rb") as fh:
                hdr = fh.read(0x1000)
                if not hdr.startswith(b"dyld_v1"):
                    continue
                mapping_offset = _read_u32(hdr, 16)
                mapping_count = _read_u32(hdr, 20)
                need = mapping_offset + mapping_count * 32
                if need > len(hdr):
                    fh.seek(0)
                    hdr = fh.read(need)
                for i in range(mapping_count):
                    base = mapping_offset + i * 32
                    if base + 32 > len(hdr):
                        break
                    addr = _read_u64(hdr, base)
                    msize = _read_u64(hdr, base + 8)
                    file_offset = _read_u64(hdr, base + 16)
                    if addr <= va_start < addr + msize:
                        off = file_offset + (va_start - addr)
                        take = min(size, addr + msize - va_start)
                        fh.seek(off)
                        return fh.read(take)
        except OSError:
            continue
    return None


def scan_shared_cache_images(
    images: Optional[Iterable[str]] = None,
    *,
    dyld_dir: Path = DEFAULT_DYLD_DIR,
    stem: str = DEFAULT_CACHE_STEM,
) -> list[TargetScan]:
    map_path = dyld_dir / f"{stem}.map"
    if not map_path.is_file():
        return [
            TargetScan(
                path="(shared_cache)",
                present=False,
                source="missing",
                notes=[f"map not found: {map_path}"],
            )
        ]
    try:
        ranges = _parse_map_text_ranges(map_path.read_text(errors="replace"))
    except OSError as exc:
        return [
            TargetScan(
                path="(shared_cache)",
                present=False,
                source="missing",
                notes=[f"map read failed: {exc}"],
            )
        ]

    out: list[TargetScan] = []
    for path in images or SHARED_CACHE_IMAGES:
        span = ranges.get(path)
        if not span:
            out.append(TargetScan(path=path, present=False, source="missing"))
            continue
        data = extract_shared_cache_text(span[0], span[1], dyld_dir=dyld_dir, stem=stem)
        if not data:
            out.append(
                TargetScan(
                    path=path,
                    present=False,
                    source="shared_cache",
                    notes=["TEXT extract failed"],
                )
            )
            continue
        out.append(_scan_bytes(path, data, "shared_cache"))
    return out


def scan_graphics_avx_surface(
    *,
    probe_host: bool = False,
    include_shared_cache: bool = False,
    dyld_dir: Path = DEFAULT_DYLD_DIR,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    env = environ if environ is not None else os.environ
    extreme = str(env.get("X86_EXTREME", "")).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    live = probe_host or extreme

    standalone: list[TargetScan] = []
    for path in STANDALONE_TARGETS:
        if live:
            standalone.append(scan_standalone_file(path))
        else:
            present = Path(path).is_file()
            standalone.append(
                TargetScan(
                    path=path,
                    present=present,
                    source="standalone" if present else "missing",
                    notes=(
                        []
                        if present
                        else ["skipped full read (set probe_host or X86_EXTREME=1)"]
                    ),
                )
            )

    shared: list[TargetScan] = []
    if live and include_shared_cache:
        shared = scan_shared_cache_images(dyld_dir=dyld_dir)

    dense_total = sum(t.dense_store_lo_runs for t in standalone + shared)
    feature_hits = {
        t.path.split("/")[-1]: t.feature_strings
        for t in standalone + shared
        if t.feature_strings
    }

    return {
        "track": "J",
        "live_scan": live,
        "shared_cache_scanned": bool(shared),
        "standalone": [t.as_dict() for t in standalone],
        "shared_cache": [t.as_dict() for t in shared],
        "dense_trampoline_hints": dense_total,
        "feature_string_hits": feature_hits,
        "baseline_sequoia_15_5": SEQUOIA_155_BASELINE,
        "doc": "docs/Tahoe-Shader-Compiler-AVX.md",
    }
