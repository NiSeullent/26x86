"""
Track B — SkyLight / WindowServer binary·symbol analysis & extreme-gated hooks.

G contract: ``sys_patch_hooks``, ``serialize_track_detect_fields``.
Extreme-enabled (``X86_EXTREME=1`` / ``extreme=True``): Non-Metal SkyLight merge
scaffold + experimental LUT bytepatch dry-run → apply API.

Role split vs Track L5-R (``x86.graphics.skylight_lut_rootpatch``, INTEGRATE
``52f7298`` + L5 stage):
  * **B** — analysis, nm fixtures, ``BYTE_PATCH_CANDIDATES``, dry-run/apply API
  * **L5-R** — sys_patch ``MERGE`` / ``OVERWRITE`` root-volume recipes
    (``BINARY_PATCH_CANDIDATES`` staging under ``L5-patched/``)

Do not duplicate L5 OVERWRITE dicts here. Mission Control wires shared modules.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

TAHOE_XNU_MAJOR = 25
ENV_EXTREME = "X86_EXTREME"
_TRUTHY = frozenset({"1", "true", "yes", "on"})

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
# L5-R module (root-volume OVERWRITE/MERGE) — documentation cross-link only.
EVIDENCE_L5R_ROOTPATCH = "x86/graphics/skylight_lut_rootpatch.py"
EVIDENCE_L5R_STAGE_DOC = "docs/EXTREME-SkyLight-LUT-Rootpatch.stage-L5.md"

# INTEGRATE 52f7298 coordination: B owns API; L5-R owns sys_patch recipes.
ROLE_SPLIT_WITH_L5R = (
    "B=analysis/bytepatch API (dry_run_byte_patch/apply_byte_patch); "
    "L5-R=sys_patch MERGE/OVERWRITE root-volume recipes "
    "(skylight_lut_rootpatch.BINARY_PATCH_CANDIDATES → L5-patched/)"
)


def extreme_enabled(
    environ: Optional[Mapping[str, str]] = None,
    *,
    flag: bool = False,
) -> bool:
    """Mission-wide extreme gate (``X86_EXTREME=1`` or explicit flag)."""
    if flag:
        return True
    env = environ if environ is not None else os.environ
    return str(env.get(ENV_EXTREME, "")).strip().lower() in _TRUTHY


class HookStatus(str, Enum):
    ACTIVE = "active"
    SCAFFOLD = "scaffold"
    EXTREME = "extreme"  # enabled under X86_EXTREME / extreme=True
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
    requires_extreme: bool = False


@dataclass(frozen=True)
class BytePatchCandidate:
    """Same-length find/replace experiment for SkyLight/WindowServer binaries."""

    patch_id: str
    title: str
    target_path_hint: str
    find: bytes
    replace: bytes
    evidence: tuple[str, ...]
    notes: str
    hook_id: str = "SL-BYTEPATCH-LUT"

    def __post_init__(self) -> None:
        if len(self.find) != len(self.replace):
            raise ValueError(
                f"{self.patch_id}: find/replace length mismatch "
                f"{len(self.find)} != {len(self.replace)}"
            )
        if not self.find:
            raise ValueError(f"{self.patch_id}: empty find pattern")


# ---------------------------------------------------------------------------
# BYTE_PATCH_CANDIDATES — Track B analysis / bytepatch API (55c3802)
#
# Role split with L5-R (``skylight_lut_rootpatch.BINARY_PATCH_CANDIDATES``):
#   * B   = scan + dry-run→apply helpers on a given Mach-O path (this table).
#           Markers use prefix ``26X86_SL_*`` / public-string probes.
#   * L5-R = sys_patch OVERWRITE/MERGE recipes that stage patched Mach-Os under
#           ``L5-patched/`` (markers ``26X86_L5_*``). Do not emit PatchType
#           OVERWRITE dicts from Track B — hand off needles to L5-R / MC.
# Coordinated under INTEGRATE 52f7298 extreme mission; both require X86_EXTREME.
# ---------------------------------------------------------------------------
BYTE_PATCH_CANDIDATES: tuple[BytePatchCandidate, ...] = (
    BytePatchCandidate(
        patch_id="SL-LUT-MARKER-V1",
        title="Experimental compositor LUT marker swap (fixture / RE fill)",
        target_path_hint=PATH_SKYLIGHT,
        find=b"26X86_SL_LUT_MARK_A",
        replace=b"26X86_SL_LUT_MARK_B",
        evidence=(EVIDENCE_OCLP_T2_194, EVIDENCE_RESEARCH_A, EVIDENCE_L5R_ROOTPATCH),
        notes=(
            "B API dry-run→apply validation marker (not an L5 OVERWRITE recipe). "
            "L5-R sibling marker is L5-SL-LUT-MARKER-V1 under L5-patched/. "
            "Replace find/replace with RE-confirmed Tahoe needles before host apply."
        ),
    ),
    BytePatchCandidate(
        patch_id="SL-GAMMA-PROBE-V1",
        title="Public CGDisplayGammaTable UTF-8 tag probe (experimental)",
        target_path_hint=PATH_SKYLIGHT,
        find=b"CGDisplayGammaTable\x00",
        replace=b"CGDisplayGammaTable\x00",  # identity — dry-run locates; apply is no-op
        evidence=(EVIDENCE_RESEARCH_A, EVIDENCE_L5R_STAGE_DOC),
        notes=(
            "B locate-only probe (identity apply). L5-R owns CoreDisplay "
            "L5-CD-GAMMA-PROBE-V1 as root-volume OVERWRITE staging, not this API."
        ),
    ),
)


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
            "for legacy GCN/Polaris/Vega opaque-shader corruption."
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
            "Stock Tahoe SkyLight does not load this folder without Non-Metal "
            "stubs that call SkyLightPluginEntry; SHA pin still required."
        ),
    ),
    SkylightHookCandidate(
        hook_id="SL-FRAMEWORK-MERGE",
        title="Merge Non-Metal SkyLight.framework 10.14.6-<xnu>",
        action=HookAction.MERGE_FRAMEWORK,
        status=HookStatus.EXTREME,
        target_paths=(PATH_SKYLIGHT, PATH_SKYLIGHT_OLD),
        evidence=(EVIDENCE_NON_METAL_PY, EVIDENCE_OCLP_1167, EVIDENCE_PSP_MERGE_MORAEA),
        tahoe_allowed=True,
        requires_payload=True,
        requires_extreme=True,
        notes=(
            "Extreme-only scaffold hint when 10.14.6-<xnu> payload exists. "
            "Production MERGE/OVERWRITE recipes live in L5-R "
            "(skylight_lut_rootpatch); B does not own sys_patch PatchType bodies."
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
        notes="Presence of SkyLightOld.dylib indicates moraea injector stubs.",
    ),
    SkylightHookCandidate(
        hook_id="SL-SHADERS-AIR64",
        title="SkyLightShaders.air64.metallib (Metal 3802 MetallibSupportPkg)",
        action=HookAction.METALLIB_RESOURCE,
        status=HookStatus.CROSS_REF,
        target_paths=(PATH_SKYLIGHT_SHADERS_METALLIB,),
        evidence=(EVIDENCE_METAL_3802_SHADERS,),
        tahoe_allowed=True,
        requires_payload=True,
        notes="Owned by Track E (metallib_*). Catalog only — Metal 3802 path.",
        owner_track="E",
    ),
    SkylightHookCandidate(
        hook_id="SL-BYTEPATCH-LUT",
        title="Experimental SkyLight LUT byte patch (extreme)",
        action=HookAction.BYTE_PATCH,
        status=HookStatus.EXTREME,
        target_paths=(PATH_SKYLIGHT,),
        evidence=(EVIDENCE_OCLP_T2_194, EVIDENCE_RESEARCH_A),
        tahoe_allowed=True,
        requires_payload=False,
        requires_extreme=True,
        notes=(
            "Extreme-enabled dry-run→apply via BYTE_PATCH_CANDIDATES (B API). "
            "Root-volume sys_patch OVERWRITE of staged Mach-Os is L5-R "
            "(BINARY_PATCH_CANDIDATES → L5-patched/). Fill RE needles before host apply."
        ),
    ),
)


def hook_by_id(hook_id: str) -> Optional[SkylightHookCandidate]:
    for candidate in SKYLIGHT_HOOK_REGISTRY:
        if candidate.hook_id == hook_id:
            return candidate
    return None


def byte_patch_by_id(patch_id: str) -> Optional[BytePatchCandidate]:
    for candidate in BYTE_PATCH_CANDIDATES:
        if candidate.patch_id == patch_id:
            return candidate
    return None


def poc_registration_table(
    *,
    include_cross_ref: bool = True,
    include_extreme: bool = True,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in SKYLIGHT_HOOK_REGISTRY:
        if candidate.status is HookStatus.CROSS_REF and not include_cross_ref:
            continue
        if candidate.status is HookStatus.EXTREME and not include_extreme:
            continue
        row = asdict(candidate)
        row["action"] = candidate.action.value
        row["status"] = candidate.status.value
        row["target_paths"] = list(candidate.target_paths)
        row["evidence"] = list(candidate.evidence)
        rows.append(row)
    return rows


def byte_patch_candidate_table() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in BYTE_PATCH_CANDIDATES:
        rows.append(
            {
                "patch_id": candidate.patch_id,
                "title": candidate.title,
                "hook_id": candidate.hook_id,
                "target_path_hint": candidate.target_path_hint,
                "find_hex": candidate.find.hex(),
                "replace_hex": candidate.replace.hex(),
                "find_len": len(candidate.find),
                "evidence": list(candidate.evidence),
                "notes": candidate.notes,
                "requires_extreme": True,
            }
        )
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


def _scan_occurrences(blob: bytes, needle: bytes) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        idx = blob.find(needle, start)
        if idx < 0:
            break
        offsets.append(idx)
        start = idx + 1
    return offsets


def dry_run_byte_patch(
    target: Path,
    *,
    patch_id: Optional[str] = None,
    candidates: Optional[Iterable[BytePatchCandidate]] = None,
) -> dict[str, Any]:
    """Report match offsets without writing. No extreme gate required for dry-run."""
    path = Path(target)
    report: dict[str, Any] = {
        "target": str(path),
        "exists": False,
        "dry_run": True,
        "candidates": [],
    }
    try:
        if not path.is_file():
            return report
        blob = path.read_bytes()
    except OSError as exc:
        report["error"] = str(exc)
        return report
    report["exists"] = True
    report["size"] = len(blob)
    selected = list(candidates) if candidates is not None else list(BYTE_PATCH_CANDIDATES)
    if patch_id:
        selected = [c for c in selected if c.patch_id == patch_id]
    for candidate in selected:
        offsets = _scan_occurrences(blob, candidate.find)
        report["candidates"].append(
            {
                "patch_id": candidate.patch_id,
                "matches": len(offsets),
                "offsets": offsets[:32],
                "would_apply": len(offsets) > 0 and candidate.find != candidate.replace,
                "identity": candidate.find == candidate.replace,
            }
        )
    return report


def apply_byte_patch(
    target: Path,
    *,
    patch_id: Optional[str] = None,
    dry_run: bool = True,
    extreme: bool = False,
    environ: Optional[Mapping[str, str]] = None,
    destination: Optional[Path] = None,
    backup_suffix: str = ".pre-skylight-B",
) -> dict[str, Any]:
    """
    Dry-run → apply path for BYTE_PATCH_CANDIDATES.

    - ``dry_run=True`` (default): scan only.
    - ``dry_run=False``: requires extreme gate; writes ``destination`` or in-place
      with ``backup_suffix`` copy first.
    """
    plan = dry_run_byte_patch(target, patch_id=patch_id)
    plan["applied"] = False
    plan["extreme"] = extreme_enabled(environ, flag=extreme)
    if dry_run:
        plan["status"] = "dry_run"
        return plan
    if not plan["extreme"]:
        plan["status"] = "skipped_needs_extreme"
        plan["reason"] = f"Set {ENV_EXTREME}=1 or pass extreme=True to apply"
        return plan
    if not plan.get("exists"):
        plan["status"] = "missing_target"
        return plan

    path = Path(target)
    blob = path.read_bytes()
    selected = list(BYTE_PATCH_CANDIDATES)
    if patch_id:
        selected = [c for c in selected if c.patch_id == patch_id]
    mutated = bytearray(blob)
    applied_ids: list[str] = []
    for candidate in selected:
        offsets = _scan_occurrences(bytes(mutated), candidate.find)
        if not offsets:
            continue
        if candidate.find == candidate.replace:
            continue
        for off in offsets:
            mutated[off : off + len(candidate.replace)] = candidate.replace
        applied_ids.append(candidate.patch_id)

    out = Path(destination) if destination is not None else path
    plan["destination"] = str(out)
    plan["patch_ids_applied"] = applied_ids
    if not applied_ids:
        plan["status"] = "no_op"
        return plan

    try:
        if destination is None and backup_suffix:
            backup = path.with_name(path.name + backup_suffix)
            if not backup.exists():
                shutil.copy2(path, backup)
                plan["backup"] = str(backup)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(bytes(mutated))
        plan["applied"] = True
        plan["status"] = "applied"
        plan["bytes_written"] = len(mutated)
    except OSError as exc:
        plan["status"] = "write_error"
        plan["error"] = str(exc)
    return plan


def emit_hook_scaffold(
    hook_id: str,
    *,
    xnu_major: int = TAHOE_XNU_MAJOR,
    plugin_overlay_dir: Optional[Path] = None,
    search_roots: Optional[Iterable[Path]] = None,
    extreme: bool = False,
    environ: Optional[Mapping[str, str]] = None,
    byte_patch_target: Optional[Path] = None,
) -> dict[str, Any]:
    candidate = hook_by_id(hook_id)
    if candidate is None:
        return {"hook_id": hook_id, "status": "unknown", "patches": {}}

    extreme_on = extreme_enabled(environ, flag=extreme)

    if candidate.status is HookStatus.CROSS_REF:
        return {
            "hook_id": hook_id,
            "status": candidate.status.value,
            "patches": {},
            "owner_track": candidate.owner_track,
            "reason": candidate.notes,
        }

    if candidate.requires_extreme and not extreme_on:
        return {
            "hook_id": hook_id,
            "status": HookStatus.EXTREME.value,
            "patches": {},
            "extreme": False,
            "reason": f"Enable with {ENV_EXTREME}=1 or extreme=True — {candidate.notes}",
        }

    if candidate.hook_id == "SL-FRAMEWORK-MERGE":
        folder = resolve_non_metal_skylight_payload(
            xnu_major, search_roots=search_roots
        )
        if not folder:
            return {
                "hook_id": hook_id,
                "status": HookStatus.EXTREME.value,
                "patches": {},
                "extreme": True,
                "payload_folder": None,
                "reason": "Non-Metal SkyLight payload not found under search_roots",
            }
        return {
            "hook_id": hook_id,
            "status": HookStatus.EXTREME.value,
            "extreme": True,
            "payload_folder": folder,
            "patches": {
                "Merge System Volume": {
                    "/System/Library/PrivateFrameworks": {
                        "SkyLight.framework": folder,
                    },
                },
            },
            "notes": candidate.notes,
        }

    if candidate.hook_id == "SL-BYTEPATCH-LUT":
        target = Path(byte_patch_target) if byte_patch_target else Path(PATH_SKYLIGHT)
        dry = dry_run_byte_patch(target)
        return {
            "hook_id": hook_id,
            "status": HookStatus.EXTREME.value,
            "extreme": True,
            "patches": {},
            "byte_patch_dry_run": dry,
            "byte_patch_candidates": byte_patch_candidate_table(),
            "apply": (
                "apply_byte_patch(target, dry_run=False, extreme=True) "
                "after reviewing dry-run offsets"
            ),
            "notes": candidate.notes,
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
    extreme: bool = False,
    environ: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    major = TAHOE_XNU_MAJOR if xnu_major is None else xnu_major
    extreme_on = extreme_enabled(environ, flag=extreme)
    return {
        "skylight_track": "B",
        "xnu_major": major,
        "extreme_enabled": extreme_on,
        "extreme_env": ENV_EXTREME,
        "non_metal_skylight_payload": resolve_non_metal_skylight_payload(
            major, search_roots=search_roots
        ),
        "non_metal_skylight_payload_folder_name": non_metal_skylight_payload_folder(
            major
        ),
        "stock_skylight_loads_plugins": stock_skylight_loads_plugins(),
        "plugin_entry_symbol": SYMBOL_SKYLIGHT_PLUGIN_ENTRY,
        "public_compositor_symbol_needles": list(PUBLIC_COMPOSITOR_SYMBOL_NEEDLES),
        "poc_hooks": poc_registration_table(),
        "extreme_hooks": [
            c.hook_id
            for c in SKYLIGHT_HOOK_REGISTRY
            if c.status is HookStatus.EXTREME or c.requires_extreme
        ],
        "byte_patch_candidates": byte_patch_candidate_table(),
        "role_split_with_l5r": ROLE_SPLIT_WITH_L5R,
        "l5r_rootpatch_module": EVIDENCE_L5R_ROOTPATCH,
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
    extreme: bool = False,
    environ: Optional[Mapping[str, str]] = None,
    byte_patch_target: Optional[Path] = None,
) -> dict[str, Any]:
    """Track G hook export — plugins always; extreme merge/bytepatch when gated."""
    extreme_on = extreme_enabled(environ, flag=extreme)
    merged: dict[str, Any] = {}
    hook_ids = ["SL-PLUGIN-PROTOCOL"]
    if extreme_on:
        hook_ids.extend(["SL-FRAMEWORK-MERGE", "SL-BYTEPATCH-LUT"])

    byte_reports: list[dict[str, Any]] = []
    for hook_id in hook_ids:
        scaffold = emit_hook_scaffold(
            hook_id,
            xnu_major=xnu_major,
            plugin_overlay_dir=plugin_overlay_dir,
            search_roots=search_roots,
            extreme=extreme_on,
            environ=environ,
            byte_patch_target=byte_patch_target,
        )
        if hook_id == "SL-BYTEPATCH-LUT":
            byte_reports.append(scaffold)
        patches = scaffold.get("patches") or {}
        for method, body in patches.items():
            bucket = merged.setdefault(method, {})
            if isinstance(body, dict):
                for path, files in body.items():
                    if isinstance(files, dict):
                        bucket.setdefault(path, {}).update(files)
                    else:
                        bucket[path] = files
    return {
        "track": "B",
        "hooks": hook_ids,
        "extreme": extreme_on,
        "patches": merged,
        "poc_table": poc_registration_table(),
        "byte_patch": byte_reports,
        "notes": (
            f"Extreme hooks ({ENV_EXTREME}=1): SL-FRAMEWORK-MERGE merge scaffold + "
            "SL-BYTEPATCH-LUT dry-run table; call apply_byte_patch(..., dry_run=False) "
            "explicitly to write. Root-volume OVERWRITE recipes: Track L5-R "
            f"({EVIDENCE_L5R_ROOTPATCH}). Role: {ROLE_SPLIT_WITH_L5R}"
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
