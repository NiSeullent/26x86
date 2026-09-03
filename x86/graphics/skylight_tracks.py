"""
Track G — SkyLight LUT root-patch / detect orchestration.

Connects B/C/E/F (and optional D detect) modules via import only.
Does **not** duplicate domain logic. Missing tracks → no-op + TODO.
Never lifts Metal 3802 / Non-Metal Tahoe guards.
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

SYS_PATCH_HOOKS = "sys_patch_hooks"
DETECT_FIELDS = "serialize_track_detect_fields"

# First successful import wins. Keep in sync with Track A map.
TRACK_MODULE_CANDIDATES: dict[str, tuple[str, ...]] = {
    "B": (
        "x86.graphics.skylight_analysis",
        "x86.graphics.windowserver_hook_gate",
        "x86.graphics.interpose_gate",
        "x86.graphics.skylight_symbols",
        "x86.graphics.skylight_hooks",
    ),
    "C": (
        "x86.graphics.colorsync_icc",
        "x86.graphics.coredisplay_prefs",
        "x86.graphics.colorsync_lut",
        "x86.graphics.coredisplay_lut",
    ),
    "D": (
        "x86.graphics.agdc_diagnose",
        "x86.graphics.agdc_framebuffer",
        "x86.graphics.agdc_yellow",
    ),
    "E": (
        "x86.graphics.metallib_preflight",
        "x86.graphics.metallib_opaque",
        "x86.graphics.metallib_renderbox",
    ),
    "F": (
        "x86.graphics.yellow_screen",
        "x86.graphics.psp_overlay",
    ),
    "H": (
        "x86.graphics.iosurface_ca_hooks",
        "x86.graphics.iosurface_extreme",
    ),
    "L5": (
        "x86.graphics.skylight_lut_rootpatch",
    ),
    "J": (
        "x86.graphics.shader_avx_gate",
    ),
}

SYS_PATCH_TRACKS: tuple[str, ...] = ("B", "C", "E", "F", "L5")

TRACK_ROLES: dict[str, str] = {
    "A": "docs",
    "B": "skylight_windowserver",
    "C": "coredisplay_colorsync",
    "D": "agdc_framebuffer",
    "E": "metallib_renderbox",
    "F": "psp_overlay",
    "G": "orchestration",
    "H": "iosurface_ca",
    "J": "shader_compiler_avx",
    "L5": "skylight_coredisplay_rootpatch",
}

TRACK_DOCS: dict[str, tuple[str, ...]] = {
    "A": (
        "docs/Tahoe-SkyLight-LUT-Research.md",
        "docs/SkyLight-LUT-Tracks.md",
        "docs/Tahoe-Graphics-Roadmap.md",
    ),
}

# Provisional wiring already on main (dedicated track modules may still be missing).
PROVISIONAL_CONNECTIONS: dict[str, dict[str, Any]] = {
    "B": {
        "via": "x86.graphics.skylight_lut",
        "note": "SkyLightPlugins SHA gate imported by tahoe_yellow_screen",
    },
    "E": {
        "via": "x86.graphics.skylight_lut",
        "note": "metal_31001_common_patches imported by LegacyMetal31001",
    },
    "F": {
        "via": "x86.graphics.yellow_screen",
        "note": "community overlay + dmg_mount + compositor_patches already wired",
    },
}

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _try_import(module_name: str) -> Optional[Any]:
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None
    except Exception as exc:  # noqa: BLE001
        logger.debug("skylight_tracks: import %s failed: %s", module_name, exc)
        return None


def resolve_track_module(track_id: str) -> tuple[Optional[Any], Optional[str]]:
    for name in TRACK_MODULE_CANDIDATES.get(track_id, ()):
        mod = _try_import(name)
        if mod is not None:
            return mod, name
    return None, None


def _doc_present(rel_path: str) -> bool:
    return (REPO_ROOT / rel_path).is_file()


def _callable_attr(mod: Any, attr: str) -> Optional[Callable[..., Any]]:
    fn = getattr(mod, attr, None)
    return fn if callable(fn) else None


def _adapt_c_sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int,
    marketing_version: str,
) -> dict:
    """
    Track C may export EXECUTE helpers without a unified sys_patch_hooks yet.
    Compose them here — domain logic stays in C modules.
    """
    del xnu_minor, marketing_version
    if xnu_major < 25:
        return {}
    execute: dict = {}
    colorsync = _try_import("x86.graphics.colorsync_icc")
    coredisplay = _try_import("x86.graphics.coredisplay_prefs")
    if colorsync is not None:
        fn = _callable_attr(colorsync, "colorsync_lut_execute_patches")
        if fn is not None:
            try:
                execute.update(fn() or {})
            except Exception as exc:  # noqa: BLE001
                logger.debug("skylight_tracks: C colorsync execute skipped: %s", exc)
    if coredisplay is not None:
        fn = _callable_attr(coredisplay, "coredisplay_cleanup_execute_patches")
        if fn is not None:
            try:
                execute.update(fn() or {})
            except Exception as exc:  # noqa: BLE001
                logger.debug("skylight_tracks: C coredisplay execute skipped: %s", exc)
    if not execute:
        return {}
    from x86.graphics.yellow_screen import TAHOE_YELLOW_SCREEN_PATCH_NAME

    try:
        from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType
    except Exception:  # noqa: BLE001
        return {}
    return {TAHOE_YELLOW_SCREEN_PATCH_NAME: {PatchType.EXECUTE: execute}}


def track_status_entry(track_id: str) -> dict[str, Any]:
    role = TRACK_ROLES.get(track_id, "unknown")
    entry: dict[str, Any] = {
        "track": track_id,
        "role": role,
        "status": "missing",
        "modules": [],
        "sys_patch_hooks": False,
        "detect_fields": False,
        "todo": None,
    }

    if track_id == "A":
        docs = list(TRACK_DOCS.get("A", ()))
        present = [p for p in docs if _doc_present(p)]
        entry["modules"] = present
        if not present:
            entry["todo"] = "TODO(skylight-A): land Research / Tracks docs"
        elif len(present) < len(docs):
            entry["status"] = "partial"
            entry["todo"] = f"TODO(skylight-A): missing {sorted(set(docs) - set(present))}"
        else:
            entry["status"] = "connected"
        return entry

    if track_id == "G":
        entry["status"] = "connected"
        entry["modules"] = ["x86.graphics.skylight_tracks"]
        entry["sys_patch_hooks"] = True
        entry["detect_fields"] = True
        return entry

    mod, name = resolve_track_module(track_id)
    provisional = PROVISIONAL_CONNECTIONS.get(track_id)

    if mod is None:
        if provisional:
            entry["status"] = "partial"
            entry["modules"] = [provisional["via"]]
            entry["todo"] = (
                f"TODO(skylight-{track_id}): dedicated module not landed; "
                f"provisional via {provisional['via']} — {provisional['note']}"
            )
            if track_id in SYS_PATCH_TRACKS:
                entry["sys_patch_hooks"] = True
        else:
            entry["todo"] = (
                f"TODO(skylight-{track_id}): no module among "
                f"{list(TRACK_MODULE_CANDIDATES.get(track_id, ()))}; sys_patch no-op"
            )
        return entry

    entry["modules"] = [name]
    hooks = _callable_attr(mod, SYS_PATCH_HOOKS)
    detect_fn = _callable_attr(mod, DETECT_FIELDS)
    if detect_fn is None and track_id == "D":
        detect_fn = (
            _callable_attr(mod, "serialize_agdc_diagnose_fields")
            or _callable_attr(mod, "serialize_agdc_framebuffer_fields")
        )
    if detect_fn is None and track_id == "B":
        detect_fn = _callable_attr(mod, "serialize_skylight_analysis_fields")
    if detect_fn is None and track_id == "C":
        detect_fn = _callable_attr(mod, "serialize_colorsync_fields") or _callable_attr(
            mod, "serialize_coredisplay_fields"
        )
    if detect_fn is None and track_id == "E":
        detect_fn = _callable_attr(mod, "serialize_opaque_shader_fields") or _callable_attr(
            mod, "serialize_metallib_fields"
        )
    if detect_fn is None and track_id == "F":
        detect_fn = _callable_attr(mod, "serialize_yellow_screen_fields")
    if detect_fn is None and track_id == "J":
        detect_fn = _callable_attr(mod, "serialize_shader_avx_fields")

    entry["sys_patch_hooks"] = hooks is not None or (
        track_id == "C"
        and (
            _callable_attr(mod, "colorsync_lut_execute_patches") is not None
            or _callable_attr(
                _try_import("x86.graphics.coredisplay_prefs"),
                "coredisplay_cleanup_execute_patches",
            )
            is not None
        )
    ) or (track_id in PROVISIONAL_CONNECTIONS and track_id in SYS_PATCH_TRACKS)
    entry["detect_fields"] = detect_fn is not None

    if hooks is not None or detect_fn is not None or entry["sys_patch_hooks"]:
        entry["status"] = "connected" if (hooks or detect_fn) else "partial"
        if entry["status"] == "partial" and provisional:
            entry["todo"] = (
                f"TODO(skylight-{track_id}): module {name} lacks unified hooks; "
                f"provisional: {provisional['note']}"
            )
    elif provisional:
        entry["status"] = "partial"
        entry["todo"] = (
            f"TODO(skylight-{track_id}): module {name} lacks {SYS_PATCH_HOOKS}/"
            f"{DETECT_FIELDS}; provisional: {provisional['note']}"
        )
    else:
        entry["status"] = "partial"
        entry["todo"] = (
            f"TODO(skylight-{track_id}): imported {name} but no hook/detect export"
        )
    return entry


def serialize_skylight_lut_tracks() -> dict[str, Any]:
    """Summary for ``python -m x86 detect --json`` → ``skylight_lut_tracks``."""
    tracks = {
        tid: track_status_entry(tid)
        for tid in ("A", "B", "C", "D", "E", "F", "G", "H", "J", "L5")
    }
    connected = [t for t, e in tracks.items() if e["status"] == "connected"]
    partial = [t for t, e in tracks.items() if e["status"] == "partial"]
    missing = [t for t, e in tracks.items() if e["status"] == "missing"]
    return {
        "tracks": tracks,
        "connected": connected,
        "partial": partial,
        "missing": missing,
        "sys_patch_tracks": list(SYS_PATCH_TRACKS),
        "map_doc": "docs/SkyLight-LUT-Tracks.md",
        "research_doc": "docs/Tahoe-SkyLight-LUT-Research.md",
    }


def _call_hooks(hooks, xnu_major: int, xnu_minor: int, marketing_version: str):
    try:
        return hooks(xnu_major, xnu_minor, marketing_version)
    except TypeError:
        try:
            return hooks(xnu_major)
        except TypeError:
            return hooks()


def merge_sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int,
    marketing_version: str,
) -> dict:
    """
    Import B/C/E/F ``sys_patch_hooks`` and shallow-merge patch dicts.
    Missing modules → no-op. Track C EXECUTE helpers are adapted if present.
    """
    merged: dict = {}

    def _merge_into(extra: dict) -> None:
        for key, value in extra.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value

    for track_id in SYS_PATCH_TRACKS:
        mod, name = resolve_track_module(track_id)
        if mod is None:
            logger.debug(
                "skylight_tracks: track %s missing — TODO no-op for sys_patch",
                track_id,
            )
            continue
        hooks = _callable_attr(mod, SYS_PATCH_HOOKS)
        if hooks is None:
            logger.debug(
                "skylight_tracks: %s (%s) has no %s — no-op",
                track_id,
                name,
                SYS_PATCH_HOOKS,
            )
            continue
        try:
            # Track B uses keyword-only after xnu_major; use adaptive caller.
            extra = _call_hooks(hooks, xnu_major, xnu_minor, marketing_version) or {}
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "skylight_tracks: track %s sys_patch_hooks failed: %s",
                track_id,
                exc,
            )
            continue
        if not isinstance(extra, dict):
            logger.warning(
                "skylight_tracks: track %s sys_patch_hooks returned non-dict",
                track_id,
            )
            continue
        _merge_into(extra)

    # C soft path when modules exist but lack unified sys_patch_hooks.
    try:
        _merge_into(_adapt_c_sys_patch_hooks(xnu_major, xnu_minor, marketing_version))
    except Exception as exc:  # noqa: BLE001
        logger.debug("skylight_tracks: C adapt skipped: %s", exc)

    return merged


def merge_optional_detect_fields(
    model: str,
    *,
    gpu_archs: Optional[Any] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    agdpmod_present: Optional[bool] = None,
    assume_tahoe: bool = False,
    agdp_on_correct_gfx0: Optional[bool] = None,
    yellow_symptoms: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Optional detect extras from landed track modules (e.g. D agdc_*)."""
    extras: dict[str, Any] = {}
    kwargs = {
        "gpu_archs": gpu_archs,
        "os_version": os_version,
        "xnu_major": xnu_major,
        "agdpmod_present": agdpmod_present,
        "assume_tahoe": assume_tahoe,
        "agdp_on_correct_gfx0": agdp_on_correct_gfx0,
        "symptoms": yellow_symptoms,
    }

    mod_d, _ = resolve_track_module("D")
    if mod_d is not None:
        for attr in (
            "serialize_agdc_diagnose_fields",
            "serialize_agdc_framebuffer_fields",
            DETECT_FIELDS,
        ):
            fn = _callable_attr(mod_d, attr)
            if fn is None:
                continue
            try:
                extras.update(fn(model, **kwargs) or {})
                break
            except TypeError:
                try:
                    extras.update(fn(model) or {})
                    break
                except Exception as exc:  # noqa: BLE001
                    logger.debug("skylight_tracks: D detect merge skipped: %s", exc)
            except Exception as exc:  # noqa: BLE001
                logger.debug("skylight_tracks: D detect merge skipped: %s", exc)

    detect_attrs = {
        "B": ("serialize_skylight_analysis_fields", DETECT_FIELDS),
        "C": (
            "serialize_colorsync_fields",
            "serialize_coredisplay_fields",
            DETECT_FIELDS,
        ),
        "E": (
            "serialize_metallib_preflight_fields",
            "serialize_opaque_shader_fields",
            "serialize_metallib_fields",
            DETECT_FIELDS,
        ),
        "H": ("serialize_iosurface_ca_fields", DETECT_FIELDS),
        "J": (
            "serialize_track_detect_fields",
            "serialize_shader_avx_fields",
        ),
        "L5": (DETECT_FIELDS,),
    }
    for track_id, attrs in detect_attrs.items():
        mod, _ = resolve_track_module(track_id)
        if mod is None:
            continue
        for attr in attrs:
            fn = _callable_attr(mod, attr)
            if fn is None:
                continue
            try:
                extras.update(fn(model, **kwargs) or {})
                break
            except TypeError:
                try:
                    extras.update(fn() or {})
                    break
                except Exception as exc:  # noqa: BLE001
                    logger.debug(
                        "skylight_tracks: %s detect merge skipped: %s",
                        track_id,
                        exc,
                    )
            except Exception as exc:  # noqa: BLE001
                logger.debug(
                    "skylight_tracks: %s detect merge skipped: %s",
                    track_id,
                    exc,
                )
    return extras
