"""
Track I — Extreme-Interpose community payload resolver.

Owns ``payloads/Kexts/Community/Extreme-Interpose/``.
Never redistributes Apple proprietary blobs.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

from .interpose_gate import extreme_opt_in, gate_blocks_reason
from .interpose_plan import (
    COMMUNITY_PAYLOAD_REL,
    DYLIB_STEM,
    PLUGIN_STEM,
    community_payload_root,
)

EXTREME_DYLIB_SHA256: dict[str, str] = {}

SOURCE_FILES: tuple[str, ...] = (
    "README.md",
    "NOTICE.md",
    "SOURCE.md",
    "LICENSE.txt",
    "Makefile",
    "src/ExtremeCompositorInterpose.c",
    "src/ExtremeCompositorInterpose.h",
    "src/SkyLightPluginShim.c",
    "scripts/build.sh",
    "scripts/install-dyld-insert.sh",
    "launchd/com.26x86.extreme-interpose.plist.example",
    "docs/SYMBOLS.md",
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pinned_dylib_sha256() -> Optional[str]:
    return EXTREME_DYLIB_SHA256.get(f"{DYLIB_STEM}.dylib")


def resolve_built_dylib(repo_root: Optional[Path] = None) -> Optional[Path]:
    candidate = community_payload_root(repo_root) / "build" / f"{DYLIB_STEM}.dylib"
    try:
        if candidate.is_file() and candidate.stat().st_size > 0:
            return candidate
    except OSError:
        return None
    return None


def verify_built_dylib(repo_root: Optional[Path] = None) -> dict[str, Any]:
    path = resolve_built_dylib(repo_root)
    expected = pinned_dylib_sha256()
    result: dict[str, Any] = {
        "path": str(path) if path else None,
        "present": path is not None,
        "sha256_expected": expected,
        "sha256_actual": None,
        "pin_ok": False,
    }
    if path is None:
        return result
    try:
        actual = _sha256_file(path)
    except OSError:
        return result
    result["sha256_actual"] = actual
    if expected:
        result["pin_ok"] = actual.lower() == expected.lower()
    else:
        result["note"] = "no SHA-256 pin yet — research build only"
    return result


def enumerate_extreme_interpose_sources(
    repo_root: Optional[Path] = None,
) -> dict[str, bool]:
    root = community_payload_root(repo_root)
    out: dict[str, bool] = {}
    for rel in SOURCE_FILES:
        try:
            out[rel] = (root / rel).is_file()
        except OSError:
            out[rel] = False
    return out


def skylight_plugin_pair_paths(
    repo_root: Optional[Path] = None,
) -> Optional[tuple[Path, Path]]:
    root = community_payload_root(repo_root)
    dylib = root / "SkyLightPlugins" / f"{PLUGIN_STEM}.dylib"
    txt = root / "SkyLightPlugins" / f"{PLUGIN_STEM}.txt"
    try:
        if dylib.is_file() and txt.is_file():
            return dylib, txt
    except OSError:
        return None
    return None


def payload_status(repo_root: Optional[Path] = None) -> dict[str, Any]:
    root = community_payload_root(repo_root)
    sources = enumerate_extreme_interpose_sources(repo_root)
    missing = [name for name, ok in sources.items() if not ok]
    return {
        "payload_root": str(root),
        "payload_relative": COMMUNITY_PAYLOAD_REL.as_posix(),
        "sources_complete": not missing,
        "sources_missing": missing,
        "built_dylib": verify_built_dylib(repo_root),
        "plugin_pair_present": skylight_plugin_pair_paths(repo_root) is not None,
        "apple_blobs_vendored": False,
        "install_blocked_reason": gate_blocks_reason(require_install=True),
        "research_armed": extreme_opt_in(),
    }


def dyld_insert_command_preview(
    target_executable: str,
    *,
    repo_root: Optional[Path] = None,
) -> Optional[str]:
    if gate_blocks_reason(require_install=False):
        return None
    dylib = resolve_built_dylib(repo_root)
    if dylib is None:
        return None
    return f'X86_EXTREME=1 DYLD_INSERT_LIBRARIES="{dylib}" "{target_executable}"'


def sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int = 0,
    *args: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    """Optional Track G hook — empty unless pin + X86_EXTREME_INSTALL."""
    del xnu_major, xnu_minor, args, kwargs
    from .interpose_plan import root_volume_interpose_recipe

    return root_volume_interpose_recipe()
