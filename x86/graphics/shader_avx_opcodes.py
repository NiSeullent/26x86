"""
Track J — AVX / VEX opcode patterns for graphics-stack analysis.

Mirrors Safari26-PreAVX-Fix TECHNICAL.md length-matched SSE substitutions
(``vmovaps`` ↔ ``movaps``) but is **not** the RestrictEvents ``revpatch=jsc``
path. That kext only rewrites JavaScriptCore; graphics binaries need a
separate scanner / PoC (see ``shader_avx_gate``).

Evidence: Safari26-PreAVX-Fix docs/TECHNICAL.md — ``c5 f8 29`` = VEX vmovaps.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

VMOVAPS_LOAD_LO = bytes([0xC5, 0xF8, 0x28])
VMOVAPS_STORE_LO = bytes([0xC5, 0xF8, 0x29])
VMOVAPS_LOAD_HI = bytes([0xC5, 0x78, 0x28])
VMOVAPS_STORE_HI = bytes([0xC5, 0x78, 0x29])
VZEROUPPER = bytes([0xC5, 0xF8, 0x77])

SSE_MOVAPS_LOAD_LO_PREFIX = bytes([0x90, 0x0F, 0x28])
SSE_MOVAPS_STORE_LO_PREFIX = bytes([0x90, 0x0F, 0x29])
SSE_MOVAPS_LOAD_HI_PREFIX = bytes([0x44, 0x0F, 0x28])
SSE_MOVAPS_STORE_HI_PREFIX = bytes([0x44, 0x0F, 0x29])

OPCODE_NEEDLES: dict[str, bytes] = {
    "vmovaps_load_lo": VMOVAPS_LOAD_LO,
    "vmovaps_store_lo": VMOVAPS_STORE_LO,
    "vmovaps_load_hi": VMOVAPS_LOAD_HI,
    "vmovaps_store_hi": VMOVAPS_STORE_HI,
    "vzeroupper": VZEROUPPER,
}

FEATURE_STRING_NEEDLES: tuple[bytes, ...] = (
    b"hw.optional.avx1_0",
    b"hw.optional.avx2_0",
    b"hw.optional.avx",
    b"__builtin_cpu_supports",
    b"__AVX__",
    b"__AVX2__",
)

SAFARI26_TECHNICAL_NOTE = (
    "Safari26-PreAVX-Fix replaces complete 16-instruction XMM save/restore "
    "vmovaps blocks with equal-length SSE movaps; capability hiding alone is "
    "insufficient when opcodes are unconditional."
)

GRAPHICS_NOT_JSC_NOTE = (
    "RestrictEvents revpatch=jsc patches JavaScriptCore only. Graphics "
    "SIGILL/gates require a separate path (Track J)."
)


@dataclass(frozen=True)
class SseSubstitution:
    name: str
    avx_prefix: bytes
    sse_prefix: bytes

    def apply_at(self, data: bytearray, offset: int) -> bool:
        n = len(self.avx_prefix)
        if offset < 0 or offset + n > len(data):
            return False
        if bytes(data[offset : offset + n]) != self.avx_prefix:
            return False
        if len(self.sse_prefix) != n:
            return False
        data[offset : offset + n] = self.sse_prefix
        return True


SSE_SUBSTITUTIONS: tuple[SseSubstitution, ...] = (
    SseSubstitution("vmovaps_load_lo", VMOVAPS_LOAD_LO, SSE_MOVAPS_LOAD_LO_PREFIX),
    SseSubstitution("vmovaps_store_lo", VMOVAPS_STORE_LO, SSE_MOVAPS_STORE_LO_PREFIX),
    SseSubstitution("vmovaps_load_hi", VMOVAPS_LOAD_HI, SSE_MOVAPS_LOAD_HI_PREFIX),
    SseSubstitution("vmovaps_store_hi", VMOVAPS_STORE_HI, SSE_MOVAPS_STORE_HI_PREFIX),
)


def count_occurrences(data: bytes, needle: bytes) -> int:
    if not needle:
        return 0
    count = 0
    start = 0
    while True:
        i = data.find(needle, start)
        if i < 0:
            break
        count += 1
        start = i + 1
    return count


def count_opcode_hits(data: bytes) -> dict[str, int]:
    return {name: count_occurrences(data, needle) for name, needle in OPCODE_NEEDLES.items()}


def count_feature_strings(data: bytes) -> dict[str, int]:
    out: dict[str, int] = {}
    for needle in FEATURE_STRING_NEEDLES:
        c = count_occurrences(data, needle)
        if c:
            out[needle.decode("latin1", errors="replace")] = c
    return out


def dense_vmovaps_windows(
    data: bytes,
    opcode: bytes = VMOVAPS_STORE_LO,
    *,
    window: int = 100,
    min_hits: int = 8,
) -> list[int]:
    hits: list[int] = []
    start = 0
    while True:
        i = data.find(opcode, start)
        if i < 0:
            break
        if data[i : i + window].count(opcode) >= min_hits:
            hits.append(i)
            start = i + window
        else:
            start = i + 1
    return hits


def propose_sse_rewrites(data: bytes, offsets: Iterable[int], kind: str) -> bytearray:
    sub = next((s for s in SSE_SUBSTITUTIONS if s.name == kind), None)
    if sub is None:
        raise ValueError(f"unknown substitution kind: {kind}")
    out = bytearray(data)
    for off in offsets:
        sub.apply_at(out, int(off))
    return out
