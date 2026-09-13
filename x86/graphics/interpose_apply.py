"""
Track I — Apply Extreme-Interpose when ``X86_EXTREME=1``.

Build community dylib → copy plugin/staging artifacts → emit install guide.
No SHA-256 pin required. Does not vendor Apple blobs. Shared sys_patch modules
are not edited; callers import ``sys_patch_hooks`` / ``apply_extreme_interpose``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from .interpose_gate import (
    ENV_AVX_MODE,
    ENV_LUT_MODE,
    ENV_X86_EXTREME,
    ENV_X86_EXTREME_INSTALL,
    extreme_opt_in,
    gate_blocks_reason,
)
from .interpose_payload import _sha256_file, resolve_built_dylib
from .interpose_plan import DYLIB_STEM, PLUGIN_STEM, community_payload_root

SKYLIGHT_PLUGINS_DATA_VOLUME = Path(
    "/Library/Application Support/SkyLightPlugins"
)
STAGING_SUBDIR = "staging"
GUIDE_NAME = "APPLY-GUIDE.txt"


def build_extreme_interpose(repo_root: Optional[Path] = None) -> dict[str, Any]:
    """Run ``make all plugin`` under Extreme-Interpose. Returns status dict."""
    root = community_payload_root(repo_root)
    result: dict[str, Any] = {
        "ok": False,
        "cwd": str(root),
        "stdout": "",
        "stderr": "",
        "returncode": None,
        "dylib": None,
        "plugin": None,
    }
    if not (root / "Makefile").is_file():
        result["stderr"] = "Makefile missing"
        return result
    try:
        proc = subprocess.run(
            ["make", "all", "plugin"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["stderr"] = str(exc)
        return result
    result["returncode"] = proc.returncode
    result["stdout"] = proc.stdout or ""
    result["stderr"] = proc.stderr or ""
    if proc.returncode != 0:
        return result
    dylib = root / "build" / f"{DYLIB_STEM}.dylib"
    plugin = root / "build" / f"{PLUGIN_STEM}.dylib"
    result["ok"] = dylib.is_file()
    result["dylib"] = str(dylib) if dylib.is_file() else None
    result["plugin"] = str(plugin) if plugin.is_file() else None
    return result


def _ensure_built(repo_root: Optional[Path] = None) -> dict[str, Any]:
    existing = resolve_built_dylib(repo_root)
    if existing is not None:
        root = community_payload_root(repo_root)
        plugin = root / "build" / f"{PLUGIN_STEM}.dylib"
        return {
            "ok": True,
            "skipped_build": True,
            "dylib": str(existing),
            "plugin": str(plugin) if plugin.is_file() else None,
        }
    return build_extreme_interpose(repo_root)


def copy_interpose_artifacts(
    repo_root: Optional[Path] = None,
    *,
    dest_plugins: Optional[Path] = None,
    dest_staging: Optional[Path] = None,
) -> dict[str, Any]:
    """
    Copy built dylibs into staging + SkyLightPlugins overlay (repo-local by default).

    When ``dest_plugins`` is None, copies into
    ``Extreme-Interpose/SkyLightPlugins/``. Live ``/Library/.../SkyLightPlugins``
    is only used when explicitly passed (and extreme is on).
    """
    root = community_payload_root(repo_root)
    built = _ensure_built(repo_root)
    out: dict[str, Any] = {
        "ok": False,
        "build": built,
        "copied": [],
        "errors": [],
    }
    if not built.get("ok"):
        out["errors"].append("build failed or dylib missing")
        return out

    dylib = Path(built["dylib"])
    plugin_src = Path(built["plugin"]) if built.get("plugin") else None
    staging = Path(dest_staging) if dest_staging else (root / STAGING_SUBDIR)
    plugins = Path(dest_plugins) if dest_plugins else (root / "SkyLightPlugins")

    try:
        staging.mkdir(parents=True, exist_ok=True)
        plugins.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        out["errors"].append(str(exc))
        return out

    targets: list[tuple[Path, Path]] = [
        (dylib, staging / dylib.name),
    ]
    if plugin_src and plugin_src.is_file():
        targets.append((plugin_src, staging / plugin_src.name))
        targets.append((plugin_src, plugins / f"{PLUGIN_STEM}.dylib"))
    txt_src = root / "SkyLightPlugins" / f"{PLUGIN_STEM}.txt"
    if not txt_src.is_file():
        try:
            txt_src.parent.mkdir(parents=True, exist_ok=True)
            txt_src.write_text("WindowServer\n", encoding="utf-8")
        except OSError as exc:
            out["errors"].append(str(exc))
    if txt_src.is_file():
        targets.append((txt_src, plugins / f"{PLUGIN_STEM}.txt"))
        targets.append((txt_src, staging / f"{PLUGIN_STEM}.txt"))

    for src, dst in targets:
        try:
            if src.resolve() == dst.resolve():
                out["copied"].append({"src": str(src), "dst": str(dst), "skipped": "same_path"})
                continue
            shutil.copy2(src, dst)
            out["copied"].append({"src": str(src), "dst": str(dst)})
        except OSError as exc:
            out["errors"].append(f"{src} -> {dst}: {exc}")

    out["ok"] = not out["errors"] and any(
        not c.get("skipped") for c in out["copied"]
    )
    out["staging_dir"] = str(staging)
    out["plugins_dir"] = str(plugins)
    return out


def write_apply_guide(
    repo_root: Optional[Path] = None,
    *,
    staging_dir: Optional[Path] = None,
) -> Path:
    root = community_payload_root(repo_root)
    staging = Path(staging_dir) if staging_dir else (root / STAGING_SUBDIR)
    staging.mkdir(parents=True, exist_ok=True)
    dylib = staging / f"{DYLIB_STEM}.dylib"
    if not dylib.is_file():
        built = resolve_built_dylib(repo_root)
        dylib_path = str(built) if built else str(root / "build" / f"{DYLIB_STEM}.dylib")
    else:
        dylib_path = str(dylib)

    guide = staging / GUIDE_NAME
    text = f"""26x86 Track I — Extreme Interpose APPLY GUIDE
=============================================
Env: {ENV_X86_EXTREME}=1 (required)
Optional: {ENV_X86_EXTREME_INSTALL}=1 for live LaunchDaemon /Library writes
AVX: {ENV_AVX_MODE}=passthrough|report0|report1
LUT: {ENV_LUT_MODE}=off|log|identity

1) User-process DYLD_INSERT (safest probe):
   {ENV_X86_EXTREME}=1 {ENV_LUT_MODE}=log \\
     DYLD_INSERT_LIBRARIES="{dylib_path}" /path/to/MetalApp

2) SkyLightPlugins pair (needs patched SkyLight / SkyLightOld.dylib):
   Copy staging/{PLUGIN_STEM}.dylib + .txt → {SKYLIGHT_PLUGINS_DATA_VOLUME}/
   Stock Tahoe SkyLight does NOT load this folder.

3) Log file:
   /tmp/26x86-extreme-interpose.log

4) Python apply (this module):
   {ENV_X86_EXTREME}=1 python3 -m x86.graphics.interpose_apply

No Apple proprietary frameworks are copied by this track.
"""
    guide.write_text(text, encoding="utf-8")
    return guide


def install_guidance_commands(
    *,
    dylib: Path,
    live_library: bool = False,
) -> list[str]:
    cmds = [
        (
            f'{ENV_X86_EXTREME}=1 {ENV_LUT_MODE}=log '
            f'DYLD_INSERT_LIBRARIES="{dylib}" /path/to/MetalApp'
        ),
        f"tail -f /tmp/26x86-extreme-interpose.log",
    ]
    if live_library:
        cmds.append(
            f"sudo mkdir -p '{SKYLIGHT_PLUGINS_DATA_VOLUME}' && "
            f"sudo cp '{dylib.parent / (PLUGIN_STEM + '.dylib')}' "
            f"'{dylib.parent / (PLUGIN_STEM + '.txt')}' "
            f"'{SKYLIGHT_PLUGINS_DATA_VOLUME}/'"
        )
    return cmds


def apply_extreme_interpose(
    repo_root: Optional[Path] = None,
    *,
    dest_plugins: Optional[Path] = None,
    live_library_plugins: bool = False,
) -> dict[str, Any]:
    """
    Full apply path when ``X86_EXTREME=1``: build → copy → guide.

    ``live_library_plugins=True`` also copies into
    ``/Library/Application Support/SkyLightPlugins`` (may need sudo; best-effort).
    """
    blocked = gate_blocks_reason(require_install=False)
    result: dict[str, Any] = {
        "applied": False,
        "blocked_reason": blocked,
        "steps": {},
        "recipe": {},
        "guidance": [],
    }
    if blocked:
        return result

    copy_dest = dest_plugins
    if live_library_plugins and dest_plugins is None:
        copy_dest = SKYLIGHT_PLUGINS_DATA_VOLUME

    copied = copy_interpose_artifacts(repo_root, dest_plugins=copy_dest)
    result["steps"]["copy"] = copied
    guide = write_apply_guide(
        repo_root,
        staging_dir=Path(copied["staging_dir"]) if copied.get("staging_dir") else None,
    )
    result["steps"]["guide"] = str(guide)

    dylib = resolve_built_dylib(repo_root)
    if dylib is None and copied.get("staging_dir"):
        candidate = Path(copied["staging_dir"]) / f"{DYLIB_STEM}.dylib"
        if candidate.is_file():
            dylib = candidate

    from .interpose_plan import root_volume_interpose_recipe

    result["recipe"] = root_volume_interpose_recipe(repo_root=repo_root)
    if dylib is not None:
        result["guidance"] = install_guidance_commands(
            dylib=dylib,
            live_library=live_library_plugins,
        )
    result["applied"] = bool(copied.get("ok")) and bool(result["recipe"])
    result["x86_extreme"] = extreme_opt_in()
    return result


def interpose_install_manifest(repo_root: Optional[Path] = None) -> dict[str, Any]:
    """
    Concrete install manifest for extreme mode (no empty dict, no SHA pin gate).

    Paths are community-built dylibs only.
    """
    root = community_payload_root(repo_root)
    built = _ensure_built(repo_root)
    if not built.get("ok") or not built.get("dylib"):
        return {
            "ok": False,
            "error": "dylib build failed",
            "build": built,
        }
    dylib = Path(built["dylib"])
    plugin = Path(built["plugin"]) if built.get("plugin") else None
    try:
        digest = _sha256_file(dylib)
    except OSError as exc:
        return {"ok": False, "error": str(exc)}

    staging = root / STAGING_SUBDIR
    plugins = root / "SkyLightPlugins"
    return {
        "ok": True,
        "name": "Extreme Interpose Compositor",
        "dylib": str(dylib),
        "dylib_sha256": digest,
        "plugin_dylib": str(plugin) if plugin and plugin.is_file() else None,
        "plugin_txt": str(plugins / f"{PLUGIN_STEM}.txt"),
        "staging_dir": str(staging),
        "skylight_plugins_overlay": str(plugins),
        "live_skylight_plugins": str(SKYLIGHT_PLUGINS_DATA_VOLUME),
        "env": {
            ENV_X86_EXTREME: os.environ.get(ENV_X86_EXTREME),
            ENV_AVX_MODE: os.environ.get(ENV_AVX_MODE, "passthrough"),
            ENV_LUT_MODE: os.environ.get(ENV_LUT_MODE, "off"),
        },
        "install_actions": [
            "build make all plugin",
            f"copy {DYLIB_STEM}.dylib → staging/",
            f"copy {PLUGIN_STEM}.dylib+.txt → Extreme-Interpose/SkyLightPlugins/",
            "write APPLY-GUIDE.txt",
            "optional: copy plugins to /Library/Application Support/SkyLightPlugins",
        ],
    }


def main(argv: Optional[list[str]] = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    live = "--live-library" in args
    if not extreme_opt_in():
        print(f"Set {ENV_X86_EXTREME}=1 to apply Track I interpose.", file=sys.stderr)
        return 2
    result = apply_extreme_interpose(live_library_plugins=live)
    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("applied") else 1


if __name__ == "__main__":
    raise SystemExit(main())
