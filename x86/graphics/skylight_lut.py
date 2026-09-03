"""
Tahoe SkyLight / WindowServer / RenderBox LUT·shader compositor hooks.

Only evidence-backed actions:
- OCLP SkyLightPlugins protocol (moraea Plugins.m / ASentientBot) — data-volume
  dylib+txt pairs. Stock Tahoe SkyLight does **not** load this folder; the
  injector lives in patched Non-Metal SkyLight (SkyLightOld.dylib).
- Upstream Metal 31001 RenderBox ``default.metallib`` overwrite
  (OCLP macos-next / crystall1ne, PR #1176; kgp-macPro snapshot) **iff**
  ``RenderBox-<xnu>/.../default.metallib`` exists on disk.

Never: guessed CoreDisplay/SkyLight byte patches, Non-Metal SkyLight.framework
downgrade on Tahoe, Metal 3802 metallib, or CoreDisplay useMetal=no.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

TAHOE_XNU_MAJOR = 25
VENTURA_XNU_MAJOR = 22

# OCLP / moraea: /Library/Application Support/SkyLightPlugins/<stem>.dylib + .txt
SKYLIGHT_PLUGINS_INSTALL_DIR = "/Library/Application Support/SkyLightPlugins"
SKYLIGHT_STUB_MARKER = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLightOld.dylib"
)

# Installed only by Non-Metal / Monterey wireless — never as a Metal LUT "fix".
NON_METAL_SKYLIGHT_PLUGIN_STEMS: frozenset[str] = frozenset({
    "DropboxHack",
    "CoreWLAN",
    "CatalystButton",
})

# Future compositor interpose stems. A .dylib is installed only when its SHA-256
# is listed here (empty until a reviewed binary exists).
COMPOSITOR_PLUGIN_STEM_ALLOWLIST: frozenset[str] = frozenset({
    "CompositorLUT",
    "SkyLightLUT",
})
COMPOSITOR_PLUGIN_SHA256: dict[str, str] = {}

# Apple binaries (SIP may block nm; inventory is best-effort).
HOST_COMPOSITOR_BINARIES: tuple[str, ...] = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLight",
    "/System/Library/Frameworks/CoreDisplay.framework/Versions/A/CoreDisplay",
    "/System/Library/Frameworks/ColorSync.framework/Versions/A/ColorSync",
    "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/RenderBox",
    "/System/Library/CoreServices/WindowServer",
)

# Public ColorSync / CoreGraphics names (ColorSync.h / CGColorSpace.h) — not
# private LUT parser symbols. Private CoreDisplay hooks are unnamed in #194.
PUBLIC_COLOR_SYMBOL_NEEDLES: tuple[str, ...] = (
    "ColorSyncProfileCreateWithURL",
    "ColorSyncTransformCreate",
    "CGColorSpaceCreateWithICCData",
    "CGColorSpaceCreateWithName",
    "CGDisplayGammaTable",
)

RENDERBOX_METALLIB_RELATIVE = (
    "System/Library/PrivateFrameworks/RenderBox.framework/"
    "Versions/A/Resources/default.metallib"
)

RENDERBOX_PAYLOAD_PREFIX = "RenderBox-"
TAHOE_RENDERBOX_PAYLOAD_DIRS: tuple[str, ...] = ("RenderBox-25", "RenderBox-26")

OCLP_RENDERBOX_EVIDENCE_URL = (
    "https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1176"
)
OCLP_T2_YELLOW_SCREEN_ISSUE = (
    "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194"
)
ASENTIENTBOT_SKYLIGHT_PLUGINS = "https://github.com/ASentientBot/monterey"
MORAEA_NON_METAL_FRAMEWORKS = "https://github.com/moraea/non-metal-frameworks"

# Documented boot-args only. There is no Apple-documented
# "disable Metal WindowServer compositor" flag.
DOCUMENTED_GRAPHICS_BOOT_ARGS: tuple[str, ...] = (
    "agdpmod=vit9696",
    "agdpmod=pikera",
    "-igfxvesa",
    "ngfxgl=1",
)


def renderbox_payload_folder(xnu_major: int) -> str:
    return f"{RENDERBOX_PAYLOAD_PREFIX}{xnu_major}"


def _search_roots(search_roots: Optional[Iterable[Path]] = None) -> list[Path]:
    if search_roots is not None:
        return [Path(p) for p in search_roots]
    from x86.graphics.yellow_screen import default_psp_binaries_roots

    return default_psp_binaries_roots()


def resolve_renderbox_metallib_payload(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> Optional[str]:
    """
    Return ``RenderBox-<xnu>`` when that tree contains default.metallib.

    Missing payload must stay a no-op: preflight otherwise fails with
    ``Failed to find .../RenderBox-<xnu>/.../default.metallib``.
    """
    if xnu_major < VENTURA_XNU_MAJOR:
        return None
    folder = renderbox_payload_folder(xnu_major)
    for root in _search_roots(search_roots):
        metallib = Path(root) / folder / RENDERBOX_METALLIB_RELATIVE
        try:
            if metallib.is_file() and metallib.stat().st_size > 0:
                return folder
        except OSError:
            continue
    return None


def renderbox_overlay_copy_pairs(
    dest_root: Path,
    search_roots: Optional[Iterable[Path]] = None,
) -> list[tuple[Path, Path]]:
    """Ditto RenderBox-25+ overlay folders onto mounted Universal-Binaries."""
    pairs: list[tuple[Path, Path]] = []
    dest = Path(dest_root)
    seen: set[str] = set()
    for root in _search_roots(search_roots):
        try:
            if dest.exists() and root.exists() and root.resolve() == dest.resolve():
                continue
        except OSError:
            continue
        for version in TAHOE_RENDERBOX_PAYLOAD_DIRS:
            src = Path(root) / version
            key = str(src)
            if key in seen:
                continue
            try:
                if src.is_dir() and (src / RENDERBOX_METALLIB_RELATIVE).is_file():
                    seen.add(key)
                    pairs.append((src, dest / version))
            except OSError:
                continue
    return pairs


def stock_skylight_loads_plugins() -> bool:
    """True only when moraea Non-Metal SkyLight stubs are present."""
    try:
        return Path(SKYLIGHT_STUB_MARKER).is_file()
    except OSError:
        return False


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def enumerate_evidence_skylight_plugins(
    overlay_plugins_dir: Path,
) -> dict[str, str]:
    """
    Map filename -> payload source folder name ``SkyLightPlugins``.

    Requires a matching .dylib + .txt pair, compositor stem allowlist, and a
    SHA-256 pin. Non-Metal stems (DropboxHack, CoreWLAN) are rejected.
    """
    directory = Path(overlay_plugins_dir)
    files: dict[str, str] = {}
    if not directory.is_dir():
        return files
    try:
        entries = list(directory.iterdir())
    except OSError:
        return files
    by_name = {path.name: path for path in entries if path.is_file()}
    stems = {path.stem for path in by_name.values()}
    for stem in sorted(stems):
        if stem in NON_METAL_SKYLIGHT_PLUGIN_STEMS:
            continue
        if stem not in COMPOSITOR_PLUGIN_STEM_ALLOWLIST:
            continue
        dylib = by_name.get(f"{stem}.dylib")
        txt = by_name.get(f"{stem}.txt")
        if dylib is None or txt is None:
            continue
        expected = COMPOSITOR_PLUGIN_SHA256.get(stem)
        if not expected:
            continue
        try:
            if _sha256_file(dylib).lower() != expected.lower():
                continue
        except OSError:
            continue
        files[dylib.name] = "SkyLightPlugins"
        files[txt.name] = "SkyLightPlugins"
    return files


def metal_31001_common_patches(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict:
    """OCLP RenderBox default.metallib overwrite, gated on payload presence."""
    from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType

    folder = resolve_renderbox_metallib_payload(xnu_major, search_roots=search_roots)
    if not folder:
        return {}
    return {
        "Metal 31001 Common": {
            PatchType.OVERWRITE_SYSTEM_VOLUME: {
                "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources": {
                    "default.metallib": folder,
                },
            },
        },
    }


def inventory_host_compositor_symbols(
    binaries: Optional[Iterable[str]] = None,
) -> dict[str, Any]:
    """Best-effort ``nm -gU`` on compositor binaries (Darwin only)."""
    result: dict[str, Any] = {
        "platform": sys.platform,
        "stock_skylight_loads_plugins": False,
        "binaries": {},
        "public_color_needles_found": [],
    }
    if sys.platform != "darwin":
        return result
    result["stock_skylight_loads_plugins"] = stock_skylight_loads_plugins()
    found_needles: set[str] = set()
    for raw in binaries or HOST_COMPOSITOR_BINARIES:
        path = Path(raw)
        entry: dict[str, Any] = {"exists": False, "nm_ok": False, "sample": []}
        try:
            entry["exists"] = path.is_file()
        except OSError:
            result["binaries"][raw] = entry
            continue
        if not entry["exists"]:
            result["binaries"][raw] = entry
            continue
        try:
            proc = subprocess.run(
                ["/usr/bin/nm", "-gU", str(path)],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            result["binaries"][raw] = entry
            continue
        if proc.returncode != 0:
            result["binaries"][raw] = entry
            continue
        entry["nm_ok"] = True
        lines = [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]
        entry["sample"] = lines[:40]
        blob = proc.stdout or ""
        for needle in PUBLIC_COLOR_SYMBOL_NEEDLES:
            if needle in blob:
                found_needles.add(needle)
        result["binaries"][raw] = entry
    result["public_color_needles_found"] = sorted(found_needles)
    return result


def serialize_skylight_lut_fields(
    xnu_major: Optional[int] = None,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    probe_host_symbols: bool = False,
) -> dict[str, Any]:
    """Fields for ``python -m x86 detect --json`` / research fixtures."""
    major = TAHOE_XNU_MAJOR if xnu_major is None else xnu_major
    folder = resolve_renderbox_metallib_payload(major, search_roots=search_roots)
    payload: dict[str, Any] = {
        "renderbox_metallib_payload": folder,
        "renderbox_metallib_present": folder is not None,
        "skylight_plugins_require_nonmetal_stubs": True,
        "stock_skylight_loads_plugins": stock_skylight_loads_plugins(),
        "documented_graphics_boot_args": list(DOCUMENTED_GRAPHICS_BOOT_ARGS),
        "oclp_renderbox_evidence_url": OCLP_RENDERBOX_EVIDENCE_URL,
        "yellow_screen_issue_url": OCLP_T2_YELLOW_SCREEN_ISSUE,
        "asentientbot_skylight_plugins": ASENTIENTBOT_SKYLIGHT_PLUGINS,
        "moraea_non_metal_frameworks": MORAEA_NON_METAL_FRAMEWORKS,
        "compositor_plugin_stems_allowlisted": sorted(COMPOSITOR_PLUGIN_STEM_ALLOWLIST),
        "compositor_plugin_sha256_pinned": sorted(COMPOSITOR_PLUGIN_SHA256),
    }
    if probe_host_symbols:
        payload["host_compositor_symbols"] = inventory_host_compositor_symbols()
    return payload
