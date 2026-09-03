"""
Tahoe full-screen yellow/orange display detection.

Independent of AVX / Safari SIGILL. Vega 64 reproduction (unpublished,
internal reporter) showed the failure is not GCN-LUT-only: Tahoe
WindowServer / CoreDisplay / SkyLight / ColorSync compositor plus
PatcherSupportPkg kext gaps. EFI agdpmod/shikigva remains a mitigation,
not a complete fix.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

# SMBIOS that always get EFI AGDP even without a live GPU probe
# (stock GCN iMacs, Mac Pro sockets including aftermarket Vega 64).
STOCK_GCN_AGDP_MODELS: frozenset[str] = frozenset({
    "MacPro6,1",
    "iMac15,1",
    "iMac17,1",
})

SOCKET_AMD_YELLOW_SCREEN_MODELS: frozenset[str] = frozenset({
    "MacPro3,1",
    "MacPro4,1",
    "MacPro5,1",
    "MacPro6,1",
    "iMacPro1,1",
})

EFI_GRAPHICS_FIXES: tuple[str, ...] = ("agdpmod", "shikigva")

# Root-patch dict keys that must trigger WindowServer cache disable.
# amd_vega.py / amd_polaris.py use "AMD Vega" / "AMD Polaris", not "AMD Legacy *".
WINDOW_SERVER_CACHE_PATCH_KEYS: frozenset[str] = frozenset({
    "AMD Legacy GCN",
    "AMD Polaris",
    "AMD Vega",
    "AMD Vega Extended",
    "Tahoe Yellow Screen Mitigations",
})

TAHOE_YELLOW_SCREEN_PATCH_NAME = "Tahoe Yellow Screen Mitigations"

# PatcherSupportPkg has no 12.5-25 tree yet (PSP #16/#18). Prefer it when an
# overlay or updated DMG ships Tahoe MTL bundles; otherwise keep 12.5-24.
TAHOE_MTL_PAYLOAD_PREFERRED = "12.5-25"
TAHOE_MTL_PAYLOAD_FALLBACK = "12.5-24"
TAHOE_PSP_VERSION_DIRS: tuple[str, ...] = ("12.5-25", "12.5-26")

# cpu_data.CPUGen.ivy_bridge — avoid importing datasets from detect JSON path.
IVY_BRIDGE_CPU_GEN = 6

COMMUNITY_YELLOW_SCREEN_RELATIVE = (
    "payloads/Kexts/Community/Tahoe-Yellow-Screen/Universal-Binaries"
)

GRAPHICS_DIAGNOSTICS_TOOL = "Tools/collect_graphics_diagnostics.command"

OCLP_T2_YELLOW_SCREEN_ISSUE = (
    "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194"
)

UNPUBLISHED_VEGA64_ISSUE = "unpublished / reporter: 내부"

_FAMILY_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("vega", ("Vega", "vega", "0x687F", "687f", "rx vega")),
    ("polaris", ("Polaris", "polaris", "RX 580", "RX 570", "rx 570", "rx 580")),
    ("gcn", (
        "Legacy_GCN_7000",
        "Legacy_GCN_8000",
        "Legacy_GCN_9000",
        "legacy_gcn",
        "firepro d",
        "FirePro D",
    )),
    ("navi", ("Navi", "navi", "RX 5700", "RX 6800")),
)


def is_tahoe_os(os_version: Optional[str] = None, xnu_major: Optional[int] = None) -> bool:
    """True when the target OS is macOS 26 Tahoe (XNU 25+ or 26.x product version)."""
    if xnu_major is not None and xnu_major >= 25:
        return True
    if os_version:
        text = str(os_version).strip()
        if text.startswith("26.") or text == "26":
            return True
    return False


def _gpu_arch_token(gpu: Any) -> str:
    if gpu is None:
        return ""
    if isinstance(gpu, str):
        return gpu
    arch = getattr(gpu, "arch", None)
    if arch is not None:
        name = str(getattr(arch, "name", arch))
        device = getattr(gpu, "device_id", None)
        extra = f" {hex(device)}" if isinstance(device, int) else ""
        return name + extra
    name = getattr(gpu, "name", None)
    if name:
        return str(name)
    if isinstance(gpu, dict):
        return str(gpu.get("arch") or gpu.get("name") or gpu.get("device") or "")
    return str(gpu)


def classify_gpu_family(
    model: str,
    gpu_archs: Optional[Iterable[Any]] = None,
) -> str:
    """Primary GPU family for detect JSON: vega / polaris / gcn / navi / socket_amd / none."""
    tokens = [_gpu_arch_token(gpu) for gpu in (gpu_archs or [])]
    joined = " ".join(tokens)
    for family, markers in _FAMILY_MARKERS:
        for marker in markers:
            if marker in joined:
                return family
    if model in STOCK_GCN_AGDP_MODELS:
        return "gcn"
    if model in SOCKET_AMD_YELLOW_SCREEN_MODELS:
        return "socket_amd"
    return "none"


def is_legacy_gcn_arch(token: Any) -> bool:
    return classify_gpu_family("", [token]) == "gcn"


def is_compositor_yellow_screen_hardware(
    model: str,
    gpu_archs: Optional[Iterable[Any]] = None,
) -> bool:
    """
    Tahoe yellow screen is GPU-generation-agnostic for legacy AMD dGPUs:
    GCN, Polaris (RX 570), Vega 64 (including Mac Pro aftermarket).
    """
    family = classify_gpu_family(model, gpu_archs)
    if family in {"vega", "polaris", "gcn", "socket_amd"}:
        return True
    if model in STOCK_GCN_AGDP_MODELS or model in SOCKET_AMD_YELLOW_SCREEN_MODELS:
        return True
    return False


def is_gcn_yellow_screen_hardware(
    model: str,
    gpu_archs: Optional[Iterable[Any]] = None,
) -> bool:
    """Backward-compatible alias; includes Vega/Polaris/socket AMD."""
    return is_compositor_yellow_screen_hardware(model, gpu_archs)


def recommended_efi_graphics_fixes(
    model: str,
    gpu_archs: Optional[Iterable[Any]] = None,
) -> list[str]:
    if is_compositor_yellow_screen_hardware(model, gpu_archs):
        return list(EFI_GRAPHICS_FIXES)
    return []


def community_yellow_screen_overlay() -> Path:
    from x86.paths import Paths

    return Paths.repo_root() / COMMUNITY_YELLOW_SCREEN_RELATIVE


def default_psp_binaries_roots() -> list[Path]:
    """Overlay first, then mounted Universal-Binaries, then sibling PatcherSupportPkg checkout."""
    from x86.paths import Paths

    roots = [
        community_yellow_screen_overlay(),
        Paths.universal_binaries_mount(),
        Paths.repo_root().parent / "26x86-PatcherSupportPkg" / "Universal-Binaries",
    ]
    return roots


def resolve_legacy_amd_mtl_payload(
    xnu_major: int,
    *,
    bundle_name: str = "AMDRadeonX5000MTLDriver.bundle",
    search_roots: Optional[Iterable[Path]] = None,
) -> str:
    """
    Folder name under PatcherSupportPkg Universal-Binaries for AMD MTL/Bronze bundles.

    Sequoia+ historically caps at 12.5-24 because 12.5-25 does not exist in the
    stock DMG. When a Tahoe overlay (payloads/.../Tahoe-Yellow-Screen or PSP #16)
    actually contains the bundle, use that tree instead of silently staying on -24.
    """
    if xnu_major < 24:
        return f"12.5-{xnu_major}"

    candidates: list[str] = []
    if xnu_major >= 25:
        candidates.append(f"12.5-{xnu_major}")
        candidates.append(TAHOE_MTL_PAYLOAD_PREFERRED)
    candidates.append(TAHOE_MTL_PAYLOAD_FALLBACK)

    ordered: list[str] = []
    for name in candidates:
        if name not in ordered:
            ordered.append(name)

    roots = [Path(p) for p in (search_roots if search_roots is not None else default_psp_binaries_roots())]
    for version in ordered:
        for root in roots:
            bundle = root / version / "System/Library/Extensions" / bundle_name
            try:
                if bundle.exists():
                    return version
            except OSError:
                continue
    return TAHOE_MTL_PAYLOAD_FALLBACK if xnu_major >= 24 else f"12.5-{xnu_major}"


def tahoe_psp_overlay_copy_pairs(
    dest_root: Path,
    search_roots: Optional[Iterable[Path]] = None,
) -> list[tuple[Path, Path]]:
    """
    (source, dest) directories to ditto into the mounted Universal-Binaries tree.

    Only Tahoe-specific version folders (12.5-25+) are copied. 12.5-24 already
    lives in Universal-Binaries.dmg and is not duplicated. RenderBox-25+ trees
    (OCLP Metal 31001 metallib) are merged when present.
    """
    from x86.graphics.skylight_lut import renderbox_overlay_copy_pairs

    pairs: list[tuple[Path, Path]] = []
    dest = Path(dest_root)
    roots = [Path(p) for p in (search_roots if search_roots is not None else default_psp_binaries_roots())]
    seen: set[str] = set()
    for root in roots:
        try:
            if dest.exists() and root.exists() and root.resolve() == dest.resolve():
                continue
        except OSError:
            continue
        for version in TAHOE_PSP_VERSION_DIRS:
            src = root / version
            key = str(src)
            if key in seen:
                continue
            try:
                if src.is_dir() and any(src.rglob("*")):
                    seen.add(key)
                    pairs.append((src, dest / version))
            except OSError:
                continue
    pairs.extend(renderbox_overlay_copy_pairs(dest, search_roots=roots))
    return pairs


def socket_amd_needs_kdkless(
    model: str,
    cpu_generation: Optional[int] = None,
) -> bool:
    """
    Mac Pro sockets (aftermarket Vega 64 / Polaris) need KDKlessWorkaround so
    WindowServer does not spin when MTL bundles are missing (RSR / PSP gap).

    iMacPro1,1 (Skylake, AVX2) is in the socket set but is skipped when
    cpu_generation is above Ivy Bridge.
    """
    if model not in SOCKET_AMD_YELLOW_SCREEN_MODELS:
        return False
    if cpu_generation is not None and cpu_generation > IVY_BRIDGE_CPU_GEN:
        return False
    return True


def should_disable_window_server_caching(
    required_patches: Optional[dict] = None,
    model: str = "",
) -> bool:
    """True when root patching should lock WindowServer shader caches."""
    patches = required_patches or {}
    if any(key in patches for key in WINDOW_SERVER_CACHE_PATCH_KEYS):
        return True
    if model and is_compositor_yellow_screen_hardware(model) and any(
        str(key).startswith("AMD ") for key in patches
    ):
        return True
    return False


def yellow_screen_mitigations(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    assume_tahoe: bool = False,
    cpu_generation: Optional[int] = None,
    search_roots: Optional[Iterable[Path]] = None,
) -> list[str]:
    """Mitigations the patcher will apply (not a full LUT/shader compositor fix)."""
    if not is_compositor_yellow_screen_hardware(model, gpu_archs):
        return []
    if not (is_tahoe_os(os_version, xnu_major) or assume_tahoe):
        return []
    items = [
        "window_server_cache_disable",
        "colorsync_srgb_fallback",
        "coredisplay_clear_nonmetal_prefs",
        "psp_mtl_payload_prefer_12.5-25",
    ]
    from x86.graphics.skylight_lut import resolve_renderbox_metallib_payload

    major = xnu_major if xnu_major is not None else 25
    if resolve_renderbox_metallib_payload(major, search_roots=search_roots):
        items.append("renderbox_metallib_if_payload")
    if socket_amd_needs_kdkless(model, cpu_generation):
        items.append("kdkless_workaround")
    items.extend(recommended_efi_graphics_fixes(model, gpu_archs))
    return items


def detect_host_agdpmod_present() -> Optional[bool]:
    """
    Best-effort live check. OpenCore DeviceProperties are not in NVRAM boot-args,
    so False means 'not visible in boot-args' rather than 'EFI is unpatched'.
    """
    if sys.platform != "darwin":
        return None
    try:
        result = subprocess.run(
            ["/usr/sbin/nvram", "boot-args"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if "agdpmod=" in output:
            return True
        if result.returncode == 0:
            return False
    except OSError:
        return None
    return None


def yellow_screen_risk(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    agdpmod_present: Optional[bool] = None,
    assume_tahoe: bool = False,
) -> bool:
    """True on Tahoe when a legacy AMD dGPU / Mac Pro socket may hit compositor yellow."""
    if not is_compositor_yellow_screen_hardware(model, gpu_archs):
        return False
    tahoe = is_tahoe_os(os_version, xnu_major) or assume_tahoe
    if not tahoe:
        return False
    return agdpmod_present is not True


def patcher_support_pkg_kexts_present(
    search_paths: Optional[Iterable[Path]] = None,
) -> bool:
    """True when Universal-Binaries.dmg or an extracted tree with .kexts is on disk."""
    paths = [Path(p) for p in search_paths] if search_paths is not None else _default_psp_search_paths()
    for path in paths:
        try:
            if path.is_file() and path.suffix.lower() == ".dmg" and path.stat().st_size > 0:
                return True
            if path.is_dir() and any(path.rglob("*.kext")):
                return True
        except OSError:
            continue
    return False


def _default_psp_search_paths() -> list[Path]:
    from x86.manifest import PATCHER_SUPPORT_PKG_VERSION
    from x86.paths import Paths

    return [
        Paths.universal_binaries_dmg(),
        Paths.cached_universal_binaries_dmg(PATCHER_SUPPORT_PKG_VERSION),
        Paths.universal_binaries_mount(),
    ]


def serialize_yellow_screen_fields(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    agdpmod_present: Optional[bool] = None,
    probe_host_agdpmod: bool = False,
    assume_tahoe: bool = False,
    psp_search_paths: Optional[Iterable[Path]] = None,
) -> dict[str, Any]:
    """Fields merged into `python -m x86 detect --json`."""
    present = agdpmod_present
    if present is None and probe_host_agdpmod:
        present = detect_host_agdpmod_present()

    family = classify_gpu_family(model, gpu_archs)
    tahoe = is_tahoe_os(os_version, xnu_major) or assume_tahoe
    fixes = recommended_efi_graphics_fixes(model, gpu_archs)
    risk = yellow_screen_risk(
        model,
        gpu_archs=gpu_archs,
        os_version=os_version,
        xnu_major=xnu_major,
        agdpmod_present=present,
        assume_tahoe=assume_tahoe,
    )
    mitigations = yellow_screen_mitigations(
        model,
        gpu_archs=gpu_archs,
        os_version=os_version,
        xnu_major=xnu_major,
        assume_tahoe=assume_tahoe,
        search_roots=psp_search_paths,
    )
    from x86.graphics.skylight_lut import serialize_skylight_lut_fields

    payload = {
        "gpu_family": family,
        "recommended_efi_graphics_fixes": fixes,
        "yellow_screen_risk": risk,
        "yellow_screen_mitigations": mitigations,
        "patcher_support_pkg_kexts_present": patcher_support_pkg_kexts_present(psp_search_paths),
        "agdpmod_detected": present,
        "gcn_yellow_screen_hardware": is_compositor_yellow_screen_hardware(model, gpu_archs),
        "graphics_diagnostics_tool": GRAPHICS_DIAGNOSTICS_TOOL,
        "yellow_screen_issue_url": OCLP_T2_YELLOW_SCREEN_ISSUE,
        "yellow_screen_unpublished_issue": UNPUBLISHED_VEGA64_ISSUE,
        "yellow_screen_notes": _notes(model, family, fixes, risk, tahoe, present),
    }
    major = xnu_major if xnu_major is not None else (25 if tahoe else None)
    if major is not None:
        payload.update(
            serialize_skylight_lut_fields(major, search_roots=psp_search_paths)
        )
    return payload



def _notes(
    model: str,
    family: str,
    fixes: list[str],
    risk: bool,
    tahoe: bool,
    agdpmod_present: Optional[bool],
) -> list[str]:
    notes = [
        "전체 화면 노란/주황은 AVX와 무관합니다. Vega 64에서도 재현되어 GPU 세대(GCN LUT만)가 본질이 아닙니다.",
        "본질: Tahoe WindowServer / SkyLight / CoreDisplay / ColorSync(ICC) 합성 실패 + PatcherSupportPkg kext 공백.",
        "Safari SIGILL은 RestrictEvents/Safari26-PreAVX-Fix 경로이며 WindowServer와 별개입니다.",
        "코드베이스에 Metal 31002 상수는 없습니다 (31001 혼동).",
        f"공개 이슈: {OCLP_T2_YELLOW_SCREEN_ISSUE}",
        f"Vega 64 재현: {UNPUBLISHED_VEGA64_ISSUE}",
    ]
    if family:
        notes.append(f"{model} gpu_family={family}")
    if fixes:
        notes.append(
            f"{model}: EFI에 {', '.join(fixes)}가 실제 dGPU PCI path(또는 boot-args 폴백)로 들어가야 합니다."
        )
    if risk:
        notes.append(
            "Tahoe + 레거시 AMD(GCN/Polaris/Vega)에서 agdpmod 경로가 확인되지 않았습니다. EFI를 재빌드한 뒤 "
            f"{GRAPHICS_DIAGNOSTICS_TOOL}로 WindowServer/CoreDisplay 로그를 수집하세요."
        )
    elif tahoe and agdpmod_present is True:
        notes.append("boot-args에서 agdpmod가 보입니다. DeviceProperties PCI path도 맞는지 확인하세요.")
    return notes
