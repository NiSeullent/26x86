"""
Track B — SkyLight / WindowServer binary·symbol analysis & evidence-backed hooks.

Registers dylib / framework *candidates* only when community or in-tree OCLP
code documents them. Never emits guessed CoreDisplay/SkyLight byte patches.

G contract exports: ``sys_patch_hooks``, ``serialize_track_detect_fields``.
Integration/wiring of shared modules is Mission Control — this file is B-only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional

TAHOE_XNU_MAJOR = 25

PATH_SKYLIGHT = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLight"
)
PATH_SKYLIGHT_OLD = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLightOld.dylib"
)
PATH_FAKE_LIBSYSTEM = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/FakeLibSystem.dylib"
)
PATH_LIBSYSTEM_WRAPPER = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/LibSystemWrapper.dylib"
)
PATH_WINDOWSERVER = "/System/Library/CoreServices/WindowServer"
PATH_SKYLIGHT_PLUGINS = "/Library/Application Support/SkyLightPlugins"
PATH_SKYLIGHT_SHADERS_METALLIB = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/Resources/"
    "SkyLightShaders.air64.metallib"
)
PATH_WINDOWSERVER_CACHE_GLOB = (
    "/private/var/folders/*/*/*/WindowServer/com.apple.WindowServer"
)

HOST_SKYLIGHT_BINARIES: tuple[str, ...] = (
    PATH_SKYLIGHT,
    PATH_SKYLIGHT_OLD,
    PATH_WINDOWSERVER,
)

NON_METAL_SKYLIGHT_PAYLOAD_PREFIX = "10.14.6-"
NON_METAL_SKYLIGHT_RELATIVE = (
    "System/Library/PrivateFrameworks/SkyLight.framework"
)

SYMBOL_SKYLIGHT_PLUGIN_ENTRY = "SkyLightPluginEntry"

PUBLIC_COMPOSITOR_SYMBOL_NEEDLES: tuple[str, ...] = (
    SYMBOL_SKYLIGHT_PLUGIN_ENTRY,
    "CGDisplayGammaTable",
    "CGColorSpaceCreateWithICCData",
    "CGColorSpaceCreateWithName",
    "ColorSyncProfileCreateWithURL",
    "ColorSyncTransformCreate",
)

EVIDENCE_ASENTIENTBOT = "https://github.com/ASentientBot/monterey"
EVIDENCE_MORAEA = "https://github.com/moraea/non-metal-frameworks"
EVIDENCE_OCLP_1167 = (
    "https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167"
)
EVIDENCE_OCLP_T2_194 = (
    "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194"
)
EVIDENCE_PSP_MERGE_MORAEA = (
    "https://github.com/dortania/PatcherSupportPkg/commit/0d04b8078fb1ef00d898611adea7988b089d2b35"
)
EVIDENCE_RESEARCH_A = "docs/Tahoe-SkyLight-LUT-Research.md"
EVIDENCE_NON_METAL_PY = (
    "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/non_metal.py"
)
EVIDENCE_WS_CACHE_HELPER = (
    "opencore_legacy_patcher/sys_patch/sys_patch_helpers.py"
    "#disable_window_server_caching"
)
EVIDENCE_METAL_3802_SHADERS = (
    "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/metal_3802.py"
)


class HookStatus(str, Enum):
    ACTIVE = "active"
    SCAFFOLD = "scaffold"
    BLOCKED = "blocked"
    REJECTED = "rejected"
    CROSS_REF = "cross_ref"


class HookAction(str, Enum):
    WINDOW_SERVER_CACHE = "window_server_cache"
    DATA_VOLUME_PLUGIN = "data_volume_plugin"
    MERGE_FRAMEWORK = "merge_framework"
    DETECT_STUB = "detect_stub"
    METALLIB_RESOURCE = "metallib_resource"
    BYTE_PATCH = "byte_patch"


@dataclass(frozen=True)
class SkylightHookCandidate:
    hook_id: str
    title: str
    action: HookAction
    status: HookStatus
    target_paths: tuple[str, ...]
    evidence: tuple[str, ...]
    tahoe_allowed: bool
    requires_payload: bool
    notes: str
    owner_track: str = "B"


SKYLIGHT_HOOK_REGISTRY: tuple[SkylightHookCandidate, ...] = (
    SkylightHookCandidate(
        hook_id="SL-WS-CACHE",
        title="Disable WindowServer Opaque shader cache (uchg)",
        action=HookAction.WINDOW_SERVER_CACHE,
        status=HookStatus.ACTIVE,
        target_paths=(PATH_WINDOWSERVER_CACHE_GLOB,),
        evidence=(EVIDENCE_WS_CACHE_HELPER, EVIDENCE_RESEARCH_A),
        tahoe_allowed=True,
        requires_payload=False,
        notes=(
            "OCLP sys_patch_helpers.disable_window_server_caching — documented "
            "for legacy GCN/Polaris/Vega opaque-shader corruption. Mitigation "
            "only; does not fix RenderBox/SkyLight ABI."
        ),
    ),
    SkylightHookCandidate(
        hook_id="SL-PLUGIN-PROTOCOL",
        title="SkyLightPlugins dylib+txt (moraea / ASentientBot v2)",
        action=HookAction.DATA_VOLUME_PLUGIN,
        status=HookStatus.SCAFFOLD,
        target_paths=(PATH_SKYLIGHT_PLUGINS,),
        evidence=(EVIDENCE_ASENTIENTBOT, EVIDENCE_MORAEA, EVIDENCE_RESEARCH_A),
        tahoe_allowed=True,
        requires_payload=True,
        notes=(
            "Stock Tahoe SkyLight does not load this folder. Requires patched "
            "Non-Metal SkyLight that calls SkyLightPluginEntry, plus SHA-256 "
            "pin in skylight_lut.COMPOSITOR_PLUGIN_SHA256. DropboxHack is never "
            "a Metal LUT fix."
        ),
    ),
    SkylightHookCandidate(
        hook_id="SL-FRAMEWORK-MERGE",
        title="Merge Non-Metal SkyLight.framework 10.14.6-<xnu>",
        action=HookAction.MERGE_FRAMEWORK,
        status=HookStatus.BLOCKED,
        target_paths=(PATH_SKYLIGHT, PATH_SKYLIGHT_OLD),
        evidence=(EVIDENCE_NON_METAL_PY, EVIDENCE_OCLP_1167, EVIDENCE_PSP_MERGE_MORAEA),
        tahoe_allowed=False,
        requires_payload=True,
        notes=(
            "non_metal.py returns {} on Tahoe (XNU>=25) — kernel panic with "
            "IOGPU removal bundle. Sequoia payload capped at 10.14.6-24. Do not "
            "lift the guard from Track B."
        ),
    ),
    SkylightHookCandidate(
        hook_id="SL-STUB-MARKER",
        title="Detect SkyLightOld.dylib Non-Metal stub marker",
        action=HookAction.DETECT_STUB,
        status=HookStatus.ACTIVE,
        target_paths=(PATH_SKYLIGHT_OLD,),
        evidence=(
            "opencore_legacy_patcher/wx_gui/gui_support.py",
            EVIDENCE_PSP_MERGE_MORAEA,
        ),
        tahoe_allowed=True,
        requires_payload=False,
        notes=(
            "Presence of SkyLightOld.dylib indicates moraea injector stubs. "
            "Used as stock_skylight_loads_plugins() gate."
        ),
    ),
    SkylightHookCandidate(
        hook_id="SL-SHADERS-AIR64",
        title="SkyLightShaders.air64.metallib (Metal 3802 MetallibSupportPkg)",
        action=HookAction.METALLIB_RESOURCE,
        status=HookStatus.CROSS_REF,
        target_paths=(PATH_SKYLIGHT_SHADERS_METALLIB,),
        evidence=(EVIDENCE_METAL_3802_SHADERS,),
        tahoe_allowed=False,
        requires_payload=True,
        notes="Owned by Track E (metallib_*). Catalog only — Metal 3802 path.",
        owner_track="E",
    ),
    SkylightHookCandidate(
        hook_id="SL-BYTEPATCH-LUT",
        title="Guessed CoreDisplay/SkyLight LUT byte patch",
        action=HookAction.BYTE_PATCH,
        status=HookStatus.REJECTED,
        target_paths=(PATH_SKYLIGHT,),
        evidence=(EVIDENCE_OCLP_T2_194, EVIDENCE_RESEARCH_A),
        tahoe_allowed=False,
        requires_payload=False,
        notes=(
            "OCLP-T2 #194 hypothesizes private color-management hooks but does "
            "not publish symbol names. Track B never emits byte patches."
        ),
    ),
)


def hook_by_id(hook_id: str) -> Optional[SkylightHookCandidate]:
    for candidate in SKYLIGHT_HOOK_REGISTRY:
        if candidate.hook_id == hook_id:
            return candidate
    return None


def poc_registration_table(
    *,
    include_rejected: bool = False,
    include_cross_ref: bool = True,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in SKYLIGHT_HOOK_REGISTRY:
        if candidate.status is HookStatus.REJECTED and not include_rejected:
            continue
        if candidate.status is HookStatus.CROSS_REF and not include_cross_ref:
            continue
        row = asdict(candidate)
        row["action"] = candidate.action.value
        row["status"] = candidate.status.value
        row["target_paths"] = list(candidate.target_paths)
        row["evidence"] = list(candidate.evidence)
        rows.append(row)
    return rows


def non_metal_skylight_payload_folder(xnu_major: int) -> str:
    major = min(xnu_major, 24)
    return f"{NON_METAL_SKYLIGHT_PAYLOAD_PREFIX}{major}"


def resolve_non_metal_skylight_payload(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> Optional[str]:
    folder = non_metal_skylight_payload_folder(xnu_major)
    roots = [Path(p) for p in search_roots] if search_roots is not None else []
    for root in roots:
        binary = (
            Path(root) / folder / NON_METAL_SKYLIGHT_RELATIVE / "Versions/A/SkyLight"
        )
        try:
            if binary.is_file() and binary.stat().st_size > 0:
                return folder
        except OSError:
            continue
    return None


def stock_skylight_loads_plugins(marker: Optional[Path] = None) -> bool:
    path = Path(marker) if marker is not None else Path(PATH_SKYLIGHT_OLD)
    try:
        return path.is_file()
    except OSError:
        return False


def parse_nm_symbol_fixture(
    nm_text: str,
    *,
    needles: Optional[Iterable[str]] = None,
) -> dict[str, Any]:
    search = tuple(needles) if needles is not None else PUBLIC_COMPOSITOR_SYMBOL_NEEDLES
    lines = [line.strip() for line in nm_text.splitlines() if line.strip()]
    found = sorted({needle for needle in search if needle in nm_text})
    return {
        "line_count": len(lines),
        "needles_found": found,
        "has_skylight_plugin_entry": SYMBOL_SKYLIGHT_PLUGIN_ENTRY in found,
        "sample": lines[:40],
    }


def emit_hook_scaffold(
    hook_id: str,
    *,
    xnu_major: int = TAHOE_XNU_MAJOR,
    plugin_overlay_dir: Optional[Path] = None,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, Any]:
    candidate = hook_by_id(hook_id)
    if candidate is None:
        return {"hook_id": hook_id, "status": "unknown", "patches": {}}

    if candidate.hook_id == "SL-FRAMEWORK-MERGE":
        folder = resolve_non_metal_skylight_payload(
            xnu_major, search_roots=search_roots
        )
        return {
            "hook_id": hook_id,
            "status": HookStatus.BLOCKED.value,
            "patches": {},
            "payload_folder": folder,
            "reason": candidate.notes,
        }

    if candidate.status in (HookStatus.REJECTED, HookStatus.BLOCKED):
        return {
            "hook_id": hook_id,
            "status": candidate.status.value,
            "patches": {},
            "reason": candidate.notes,
        }

    if candidate.status is HookStatus.CROSS_REF:
        return {
            "hook_id": hook_id,
            "status": candidate.status.value,
            "patches": {},
            "owner_track": candidate.owner_track,
            "reason": candidate.notes,
        }

    if candidate.hook_id == "SL-PLUGIN-PROTOCOL":
        files: dict[str, str] = {}
        if plugin_overlay_dir is not None:
            try:
                from x86.graphics.skylight_lut import enumerate_evidence_skylight_plugins
            except Exception:
                enumerate_evidence_skylight_plugins = None  # type: ignore
            if enumerate_evidence_skylight_plugins is not None:
                files = enumerate_evidence_skylight_plugins(Path(plugin_overlay_dir))
        if not files:
            return {
                "hook_id": hook_id,
                "status": candidate.status.value,
                "patches": {},
                "reason": "no SHA-pinned compositor plugin pair in overlay",
            }
        return {
            "hook_id": hook_id,
            "status": candidate.status.value,
            "patches": {
                "Overwrite Data Volume": {
                    PATH_SKYLIGHT_PLUGINS: files,
                },
            },
            "stock_skylight_loads_plugins": stock_skylight_loads_plugins(),
        }

    if candidate.hook_id in ("SL-WS-CACHE", "SL-STUB-MARKER"):
        return {
            "hook_id": hook_id,
            "status": candidate.status.value,
            "patches": {},
            "runtime": True,
            "notes": candidate.notes,
        }

    return {
        "hook_id": hook_id,
        "status": candidate.status.value,
        "patches": {},
    }


def inventory_skylight_paths(
    *,
    path_exists: Optional[Any] = None,
) -> dict[str, Any]:
    exists = path_exists or (lambda p: Path(p).is_file() or Path(p).is_dir())
    entries: dict[str, bool] = {}
    for path in (
        PATH_SKYLIGHT,
        PATH_SKYLIGHT_OLD,
        PATH_FAKE_LIBSYSTEM,
        PATH_LIBSYSTEM_WRAPPER,
        PATH_WINDOWSERVER,
        PATH_SKYLIGHT_PLUGINS,
        PATH_SKYLIGHT_SHADERS_METALLIB,
    ):
        try:
            entries[path] = bool(exists(path))
        except OSError:
            entries[path] = False
    return {
        "paths": entries,
        "stock_skylight_loads_plugins": bool(entries.get(PATH_SKYLIGHT_OLD)),
    }


def serialize_skylight_analysis_fields(
    xnu_major: Optional[int] = None,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    include_rejected: bool = False,
) -> dict[str, Any]:
    major = TAHOE_XNU_MAJOR if xnu_major is None else xnu_major
    return {
        "skylight_track": "B",
        "xnu_major": major,
        "non_metal_skylight_payload": resolve_non_metal_skylight_payload(
            major, search_roots=search_roots
        ),
        "non_metal_skylight_payload_folder_name": non_metal_skylight_payload_folder(
            major
        ),
        "stock_skylight_loads_plugins": stock_skylight_loads_plugins(),
        "plugin_entry_symbol": SYMBOL_SKYLIGHT_PLUGIN_ENTRY,
        "public_compositor_symbol_needles": list(PUBLIC_COMPOSITOR_SYMBOL_NEEDLES),
        "poc_hooks": poc_registration_table(include_rejected=include_rejected),
        "blocked_on_tahoe": [
            c.hook_id
            for c in SKYLIGHT_HOOK_REGISTRY
            if not c.tahoe_allowed or c.status is HookStatus.BLOCKED
        ],
        "rejected_byte_patches": [
            c.hook_id
            for c in SKYLIGHT_HOOK_REGISTRY
            if c.status is HookStatus.REJECTED
        ],
        "evidence_asentientbot": EVIDENCE_ASENTIENTBOT,
        "evidence_oclp_1167": EVIDENCE_OCLP_1167,
        "research_doc": EVIDENCE_RESEARCH_A,
        "symbol_appendix": "docs/SkyLight-Symbol-Appendix.md",
    }


def serialize_track_detect_fields(
    xnu_major: Optional[int] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Track G discoverable detect serializer."""
    return serialize_skylight_analysis_fields(xnu_major, **kwargs)


def sys_patch_hooks(
    xnu_major: int = TAHOE_XNU_MAJOR,
    *,
    plugin_overlay_dir: Optional[Path] = None,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, Any]:
    """Track G discoverable hook export (SHA-pinned plugins only; never byte patches)."""
    merged: dict[str, Any] = {}
    for hook_id in ("SL-PLUGIN-PROTOCOL",):
        scaffold = emit_hook_scaffold(
            hook_id,
            xnu_major=xnu_major,
            plugin_overlay_dir=plugin_overlay_dir,
            search_roots=search_roots,
        )
        patches = scaffold.get("patches") or {}
        for method, body in patches.items():
            bucket = merged.setdefault(method, {})
            if isinstance(body, dict):
                for path, files in body.items():
                    bucket.setdefault(path, {}).update(files)
    return {
        "track": "B",
        "hooks": ["SL-PLUGIN-PROTOCOL"],
        "patches": merged,
        "poc_table": poc_registration_table(),
        "notes": (
            "Stock Tahoe ignores SkyLightPlugins until Non-Metal stubs exist. "
            "SL-FRAMEWORK-MERGE stays blocked."
        ),
    }


FIXTURE_NM_STOCK_COMPOSITOR = """\
0000000000010000 T _CGColorSpaceCreateWithName
0000000000010100 T _CGDisplayGammaTable
0000000000020000 T _ColorSyncProfileCreateWithURL
0000000000020100 T _ColorSyncTransformCreate
0000000000030000 T _SLWindowCreate
"""

FIXTURE_NM_PATCHED_SKYLIGHT_WITH_PLUGIN_LOADER = """\
0000000000010000 T _SLWindowCreate
0000000000040000 T _SkyLightPluginEntry
0000000000040100 T _ASBLoadSkyLightPlugins
"""
