"""
Opaque shader corruption ↔ WindowServer cache (Track E).

On legacy AMD (GCN / Polaris / Vega) under Ventura+, WindowServer caches
compiled **Opaque** shaders under::

    /private/var/folders/*/*/*/WindowServer/com.apple.WindowServer

Corrupted cache entries present as full-screen yellow/orange desktops on Tahoe.
``sys_patch_helpers.disable_window_server_caching`` deletes that cache and sets
``chflags uchg`` on the parent ``WindowServer`` directory so the broken blob
cannot be rewritten.

Relationship to RenderBox metallib (this track):

- **WS cache uchg** = symptom mitigation. Forces regeneration of Opaque shaders.
- **RenderBox ``default.metallib``** = source library for UI / Liquid Glass Opaque
  programs (OCLP PR #1176). If the source ABI/metallib is wrong or missing,
  regeneration after uchg still produces a broken desktop.
- Clearing the cache alone never installs ``RenderBox-25``; missing payload keeps
  ``LegacyMetal31001`` as a no-op (see ``metallib_preflight``).

Never: invent metallib bytes, unlock Metal 3802 on Tahoe, or touch ColorSync /
SkyLight byte patches (other tracks).
"""

from __future__ import annotations

import glob
import os
import stat
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

# Documented in sys_patch_helpers.disable_window_server_caching
WINDOW_SERVER_CACHE_GLOB = "/private/var/folders/*/*/*/WindowServer/com.apple.WindowServer"
WINDOW_SERVER_DIR_GLOB = "/private/var/folders/*/*/*/WindowServer"

OPAQUE_WS_CACHE_EVIDENCE = (
    "Legacy GCN/Polaris/Vega: WindowServer asset cache can pin corrupted Opaque "
    "shaders → yellow/orange desktop; delete cache + chflags uchg on WindowServer dir"
)


@dataclass(frozen=True)
class WindowServerCacheProbe:
    """Read-only snapshot of WindowServer shader-cache directories."""

    platform: str
    cache_paths_found: list[str] = field(default_factory=list)
    dir_paths_found: list[str] = field(default_factory=list)
    uchg_dirs: list[str] = field(default_factory=list)
    writable_dirs: list[str] = field(default_factory=list)
    probe_ok: bool = False
    notes: list[str] = field(default_factory=list)


def _dir_has_uchg(path: str) -> Optional[bool]:
    """Best-effort immutable-flag check (Darwin ``UF_IMMUTABLE`` / ls -ldO uchg)."""
    try:
        st = os.stat(path)
    except OSError:
        return None
    uf_immutable = getattr(stat, "UF_IMMUTABLE", 0x2)
    flags = getattr(st, "st_flags", 0)
    if flags & uf_immutable:
        return True
    if sys.platform != "darwin":
        return bool(flags & uf_immutable)
    try:
        proc = subprocess.run(
            ["/bin/ls", "-ldO", path],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return bool(flags & uf_immutable)
    if proc.returncode != 0:
        return bool(flags & uf_immutable)
    return "uchg" in (proc.stdout or "").split()


def probe_window_server_opaque_cache() -> WindowServerCacheProbe:
    """
    Read-only probe. Does **not** delete caches or set uchg
    (that remains ``sys_patch_helpers.disable_window_server_caching``).
    """
    notes: list[str] = []
    if sys.platform != "darwin":
        return WindowServerCacheProbe(
            platform=sys.platform,
            notes=["WindowServer cache probe is Darwin-only"],
        )

    cache_paths = sorted(glob.glob(WINDOW_SERVER_CACHE_GLOB))
    dir_paths = sorted(glob.glob(WINDOW_SERVER_DIR_GLOB))
    uchg_dirs: list[str] = []
    writable_dirs: list[str] = []
    for path in dir_paths:
        flag = _dir_has_uchg(path)
        if flag is True:
            uchg_dirs.append(path)
        elif flag is False:
            writable_dirs.append(path)
        else:
            notes.append(f"could not read flags: {path}")

    if not dir_paths:
        notes.append("no WindowServer cache directories matched glob (user not logged in?)")
    if cache_paths and not uchg_dirs:
        notes.append(
            "Opaque cache present without uchg — disable_window_server_caching not applied"
        )
    if uchg_dirs and not cache_paths:
        notes.append(
            "uchg set and cache cleared — regeneration forced; RenderBox source still matters"
        )

    return WindowServerCacheProbe(
        platform=sys.platform,
        cache_paths_found=cache_paths,
        dir_paths_found=dir_paths,
        uchg_dirs=uchg_dirs,
        writable_dirs=writable_dirs,
        probe_ok=True,
        notes=notes,
    )


def opaque_shader_windowserver_relationship(
    *,
    renderbox_metallib_present: bool,
    legacy_metal_31001_noop: bool,
) -> dict[str, Any]:
    """
    Structured explanation of Opaque corruption vs WS cache vs RenderBox.

    Pure data — safe to embed in detect JSON / research docs.
    """
    layers = [
        {
            "layer": "window_server_opaque_cache",
            "path_glob": WINDOW_SERVER_CACHE_GLOB,
            "mitigation": "delete cache + chflags uchg on parent WindowServer dir",
            "restores_compositor": "partial",
            "notes": OPAQUE_WS_CACHE_EVIDENCE,
        },
        {
            "layer": "renderbox_default_metallib",
            "path": (
                "/System/Library/PrivateFrameworks/RenderBox.framework/"
                "Versions/A/Resources/default.metallib"
            ),
            "mitigation": "OVERWRITE from RenderBox-<xnu> when payload validates",
            "restores_compositor": "conditional",
            "present": renderbox_metallib_present,
            "legacy_metal_31001_noop": legacy_metal_31001_noop,
            "notes": (
                "Source Opaque/Liquid Glass programs. Missing ⇒ uchg alone cannot "
                "fix ABI mismatch; LegacyMetal31001 stays no-op."
            ),
        },
        {
            "layer": "metallib_support_pkg_3802",
            "mitigation": "never unlock on Tahoe from this track",
            "restores_compositor": "n/a",
            "notes": "Different GPU generation (3802) and Sequoia+ metallib format",
        },
    ]
    verdict = (
        "apply_ws_cache_uchg_and_await_renderbox_payload"
        if legacy_metal_31001_noop
        else "ws_cache_uchg_plus_renderbox_overwrite_when_root_patching"
    )
    return {
        "opaque_shader_pipeline": layers,
        "recommended_combo": verdict,
        "warning": (
            "WindowServer cache disable without a valid RenderBox-25 metallib "
            "only forces recompile from a still-broken or stock Tahoe source"
        ),
    }


def serialize_opaque_shader_fields(
    *,
    renderbox_metallib_present: bool = False,
    legacy_metal_31001_noop: bool = True,
    probe_host_cache: bool = False,
) -> dict[str, Any]:
    """Detect JSON fragment for Opaque ↔ WindowServer caching."""
    payload: dict[str, Any] = {
        "opaque_shader_ws_cache": opaque_shader_windowserver_relationship(
            renderbox_metallib_present=renderbox_metallib_present,
            legacy_metal_31001_noop=legacy_metal_31001_noop,
        ),
    }
    if probe_host_cache:
        payload["window_server_opaque_cache_probe"] = asdict(
            probe_window_server_opaque_cache()
        )
    return payload
