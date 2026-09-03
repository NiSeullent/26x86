"""
Track L5-R — OCLP-style root-volume SkyLight / CoreDisplay OVERWRITE recipes.

Coordinates with Track B (``55c3802`` / ``skylight_analysis``):
  * **B** — analysis, ``BYTE_PATCH_CANDIDATES``, dry-run→apply API
  * **L5-R** — sys_patch ``OVERWRITE`` / ``MERGE`` root-volume patch dicts

INTEGRATE ``52f7298`` + post-queue L5-R. Replaces refused WindowServer process
inject. No ``task_for_pid`` / runtime pid inject.

Gate: ``X86_EXTREME=1`` → non-empty patch dict **only on Tahoe**
(``tahoe_gate.root_patches_allowed`` / xnu ≥ 25). Sequoia + extreme → ``{}``.
Default → ``{}``. No permanent blocked path.

Primary recipe (OCLP Non-Metal Sequoia-capped folders):
  * OVERWRITE ``SkyLight.framework`` ← ``10.14.6-24``
  * OVERWRITE ``CoreDisplay.framework`` ← ``10.14.4-24`` (alt ``10.13.6-24``)

Optional: MERGE (softer), binary OVERWRITE from ``L5-patched/`` (B needle handoff).

File monopoly: this module + ``*.stage-L5`` only.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

TAHOE_XNU_MAJOR = 25
SEQUOIA_XNU_MAJOR = 24

ENV_EXTREME = "X86_EXTREME"
ENV_SLICES = "X86_EXTREME_SKYLIGHT_ROOTPATCH_SLICES"
ENV_COREDISPLAY_VARIANT = "X86_EXTREME_COREDISPLAY_VARIANT"
ENV_MODE = "X86_EXTREME_SKYLIGHT_ROOTPATCH_MODE"  # overwrite (default) | merge

SLICE_SKYLIGHT = "skylight"
SLICE_COREDISPLAY = "coredisplay"
SLICE_BINARY = "binary"
ALL_SLICES: tuple[str, ...] = (SLICE_SKYLIGHT, SLICE_COREDISPLAY, SLICE_BINARY)

PATCH_NAME = "Track L5 Extreme SkyLight/CoreDisplay Root Volume (opt-in)"

# B cross-link (do not import B for patch emission — avoid cycles / monopoly).
TRACK_B_MODULE = "x86.graphics.skylight_analysis"
TRACK_B_COMMIT = "55c3802"
INTEGRATE_COMMIT = "52f7298"

SKYLIGHT_PAYLOAD_PREFIX = "10.14.6-"
COREDISPLAY_PAYLOAD_PREFIX_MOJAVE = "10.14.4-"
COREDISPLAY_PAYLOAD_PREFIX_HS = "10.13.6-"

SKYLIGHT_REL = Path(
    "System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLight"
)
COREDISPLAY_REL = Path(
    "System/Library/Frameworks/CoreDisplay.framework/Versions/A/CoreDisplay"
)

PATH_SKYLIGHT = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLight"
)
PATH_COREDISPLAY = (
    "/System/Library/Frameworks/CoreDisplay.framework/Versions/A/CoreDisplay"
)

DEST_PRIVATE_FRAMEWORKS = "/System/Library/PrivateFrameworks"
DEST_FRAMEWORKS = "/System/Library/Frameworks"

EVIDENCE: tuple[str, ...] = (
    "https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167",
    "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194",
    "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/non_metal.py",
    TRACK_B_MODULE,
    f"git:{TRACK_B_COMMIT}",
    f"git:{INTEGRATE_COMMIT}",
)

# Sibling markers to B's ``26X86_SL_*`` — L5 stages under L5-patched/ for OVERWRITE.
BINARY_PATCH_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "patch_id": "L5-SL-LUT-MARKER-V1",
        "b_sibling": "SL-LUT-MARKER-V1",
        "target": PATH_SKYLIGHT,
        "find": b"26X86_L5_SL_LUT_A",
        "replace": b"26X86_L5_SL_LUT_B",
        "notes": (
            "L5 OVERWRITE staging marker (sibling of B SL-LUT-MARKER-V1). "
            "Stage patched Mach-O under L5-patched/ then emit OVERWRITE."
        ),
    },
    {
        "patch_id": "L5-CD-GAMMA-PROBE-V1",
        "b_sibling": "SL-GAMMA-PROBE-V1",
        "target": PATH_COREDISPLAY,
        "find": b"CGDisplayGammaTable\x00",
        "replace": b"CGDisplayGammaTable\x00",
        "notes": (
            "Locate-only CoreDisplay probe for root-volume OVERWRITE staging; "
            "identity replace is apply no-op until RE delta lands."
        ),
    },
)

_TRUTHY = frozenset({"1", "true", "yes", "on"})
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

TRACK_CANDIDATES: tuple[str, ...] = ("x86.graphics.skylight_lut_rootpatch",)


def extreme_enabled(
    environ: Optional[Mapping[str, str]] = None,
    *,
    flag: bool = False,
) -> bool:
    if flag:
        return True
    env = environ if environ is not None else os.environ
    return str(env.get(ENV_EXTREME, "")).strip().lower() in _TRUTHY


def sequoia_capped_folder(prefix: str, xnu_major: int) -> str:
    return f"{prefix}{min(int(xnu_major), SEQUOIA_XNU_MAJOR)}"


def skylight_payload_folder(xnu_major: int) -> str:
    return sequoia_capped_folder(SKYLIGHT_PAYLOAD_PREFIX, xnu_major)


def coredisplay_payload_folder(
    xnu_major: int,
    *,
    environ: Optional[Mapping[str, str]] = None,
) -> str:
    env = environ if environ is not None else os.environ
    variant = str(env.get(ENV_COREDISPLAY_VARIANT, "mojave")).strip().lower()
    if variant in {"hs", "highsierra", "10.13.6", "webdriver"}:
        return sequoia_capped_folder(COREDISPLAY_PAYLOAD_PREFIX_HS, xnu_major)
    return sequoia_capped_folder(COREDISPLAY_PAYLOAD_PREFIX_MOJAVE, xnu_major)


def parse_enabled_slices(
    environ: Optional[Mapping[str, str]] = None,
) -> frozenset[str]:
    env = environ if environ is not None else os.environ
    raw = str(env.get(ENV_SLICES, "")).strip().lower()
    if not raw or raw in {"all", "*", "max"}:
        return frozenset(ALL_SLICES)
    parts = {p.strip() for p in raw.replace(";", ",").split(",") if p.strip()}
    return frozenset(p for p in parts if p in ALL_SLICES) or frozenset(ALL_SLICES)


def patch_install_mode(
    environ: Optional[Mapping[str, str]] = None,
) -> str:
    """Default OVERWRITE (user L5-R mandate); ``merge`` softens to Non-Metal Common style."""
    env = environ if environ is not None else os.environ
    raw = str(env.get(ENV_MODE, "overwrite")).strip().lower()
    if raw in {"merge", "merge_system_volume"}:
        return "merge"
    return "overwrite"


def _default_psp_roots() -> list[Path]:
    candidates = [
        REPO_ROOT / "payloads" / "Kexts" / "Universal-Binaries",
        REPO_ROOT.parent / "26x86-PatcherSupportPkg" / "Universal-Binaries",
        REPO_ROOT
        / "payloads"
        / "Kexts"
        / "Community"
        / "Tahoe-Yellow-Screen"
        / "Universal-Binaries",
    ]
    try:
        from x86.graphics.yellow_screen import default_psp_binaries_roots

        for root in default_psp_binaries_roots():
            p = Path(root)
            if p not in candidates:
                candidates.append(p)
    except Exception:  # noqa: BLE001
        pass
    return [p for p in candidates if p.is_dir()] or candidates


def _search_roots(search_roots: Optional[Iterable[Path]] = None) -> list[Path]:
    if search_roots is not None:
        return [Path(p) for p in search_roots]
    return _default_psp_roots()


def resolve_payload_folder(
    folder: str,
    relative: Path,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> Optional[str]:
    for root in _search_roots(search_roots):
        candidate = root / folder / relative
        if candidate.is_file() and candidate.stat().st_size > 0:
            return folder
        parent = candidate.parent
        try:
            if parent.is_dir() and any(parent.iterdir()):
                return folder
        except OSError:
            continue
    return None


def resolve_skylight_payload(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> Optional[str]:
    return resolve_payload_folder(
        skylight_payload_folder(xnu_major), SKYLIGHT_REL, search_roots=search_roots
    )


def resolve_coredisplay_payload(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> Optional[str]:
    return resolve_payload_folder(
        coredisplay_payload_folder(xnu_major, environ=environ),
        COREDISPLAY_REL,
        search_roots=search_roots,
    )


@dataclass(frozen=True)
class RootPatchPlan:
    xnu_major: int
    extreme: bool
    mode: str
    slices: tuple[str, ...]
    skylight_folder: Optional[str]
    coredisplay_folder: Optional[str]
    skylight_present: bool
    coredisplay_present: bool
    would_emit: bool
    notes: list[str] = field(default_factory=list)


def assess_rootpatch_plan(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[Mapping[str, str]] = None,
    extreme: bool = False,
    product_version: Optional[str] = None,
    marketing_version: Optional[str] = None,
) -> RootPatchPlan:
    from .tahoe_gate import is_tahoe, root_patches_allowed

    env = environ if environ is not None else os.environ
    version = product_version if product_version is not None else marketing_version
    tahoe = is_tahoe(xnu_major=xnu_major, product_version=version)
    on = extreme_enabled(env, flag=extreme)
    mode = patch_install_mode(env)
    slices = tuple(s for s in ALL_SLICES if s in parse_enabled_slices(env))
    notes: list[str] = []
    if not tahoe:
        notes.append(
            "Non-Tahoe host: L5 OVERWRITE/MERGE returns {} "
            f"(even with {ENV_EXTREME}=1)."
        )
    if not on:
        notes.append(f"Set {ENV_EXTREME}=1 to emit OVERWRITE/MERGE patch dict.")
    elif tahoe:
        notes.append(
            f"Mode={mode} (set {ENV_MODE}=merge for softer MERGE). "
            f"B={TRACK_B_COMMIT} owns bytepatch API; L5-R owns sys_patch recipes."
        )

    sk_folder = skylight_payload_folder(xnu_major)
    cd_folder = coredisplay_payload_folder(xnu_major, environ=env)
    sk_res = resolve_skylight_payload(xnu_major, search_roots=search_roots)
    cd_res = resolve_coredisplay_payload(
        xnu_major, search_roots=search_roots, environ=env
    )
    if on and tahoe:
        if SLICE_SKYLIGHT in slices and not sk_res:
            notes.append(f"SkyLight PSP {sk_folder} missing — folder name still emitted.")
        if SLICE_COREDISPLAY in slices and not cd_res:
            notes.append(
                f"CoreDisplay PSP {cd_folder} missing — folder name still emitted."
            )

    would = bool(
        on
        and root_patches_allowed(xnu_major=xnu_major, product_version=version)
        and slices
    )
    return RootPatchPlan(
        xnu_major=xnu_major,
        extreme=on,
        mode=mode,
        slices=slices if (on and tahoe) else (),
        skylight_folder=sk_folder if (on and tahoe) else None,
        coredisplay_folder=cd_folder if (on and tahoe) else None,
        skylight_present=bool(sk_res),
        coredisplay_present=bool(cd_res),
        would_emit=would,
        notes=notes,
    )


def _framework_method(mode: str):
    from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType

    if mode == "merge":
        return PatchType.MERGE_SYSTEM_VOLUME
    return PatchType.OVERWRITE_SYSTEM_VOLUME


def _staged_binary_overwrites(
    *,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, dict[str, str]]:
    """OVERWRITE map for B-handed-off patched Mach-Os under ``L5-patched/``."""
    rel_map = {
        "SkyLight": (
            "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A",
            "SkyLight",
            Path(
                "System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLight"
            ),
        ),
        "CoreDisplay": (
            "/System/Library/Frameworks/CoreDisplay.framework/Versions/A",
            "CoreDisplay",
            Path(
                "System/Library/Frameworks/CoreDisplay.framework/Versions/A/CoreDisplay"
            ),
        ),
    }
    out: dict[str, dict[str, str]] = {}
    for root in _search_roots(search_roots):
        stage = root / "L5-patched"
        if not stage.is_dir():
            continue
        for _name, (dest_dir, file_name, rel) in rel_map.items():
            src = stage / rel
            if src.is_file() and src.stat().st_size > 0:
                out.setdefault(dest_dir, {})[file_name] = "L5-patched"
    return out


def build_rootpatch_dict(
    xnu_major: int,
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[Mapping[str, str]] = None,
    extreme: bool = False,
    require_payload_on_disk: bool = False,
    product_version: Optional[str] = None,
    marketing_version: Optional[str] = None,
) -> dict[str, Any]:
    """
    Build OCLP-shaped patch dict.

    ``X86_EXTREME=1`` on Tahoe fills OVERWRITE (default) entries for SkyLight +
    CoreDisplay with Sequoia-capped PSP folder names. Sequoia + EXTREME → ``{}``.
    """
    plan = assess_rootpatch_plan(
        xnu_major,
        search_roots=search_roots,
        environ=environ,
        extreme=extreme,
        product_version=product_version,
        marketing_version=marketing_version,
    )
    if not plan.would_emit:
        return {}

    from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType

    body: dict[str, Any] = {}
    slices = set(plan.slices)
    method = _framework_method(plan.mode)

    if SLICE_SKYLIGHT in slices:
        folder = plan.skylight_folder
        if folder and (not require_payload_on_disk or plan.skylight_present):
            body.setdefault(method, {})
            body[method].setdefault(DEST_PRIVATE_FRAMEWORKS, {})
            body[method][DEST_PRIVATE_FRAMEWORKS]["SkyLight.framework"] = folder

    if SLICE_COREDISPLAY in slices:
        folder = plan.coredisplay_folder
        if folder and (not require_payload_on_disk or plan.coredisplay_present):
            body.setdefault(method, {})
            body[method].setdefault(DEST_FRAMEWORKS, {})
            body[method][DEST_FRAMEWORKS]["CoreDisplay.framework"] = folder

    if SLICE_BINARY in slices:
        overwrites = _staged_binary_overwrites(search_roots=search_roots)
        if overwrites:
            body.setdefault(PatchType.OVERWRITE_SYSTEM_VOLUME, {})
            for dest, files in overwrites.items():
                body[PatchType.OVERWRITE_SYSTEM_VOLUME].setdefault(dest, {}).update(
                    files
                )

    if not body:
        return {}
    return {PATCH_NAME: body}


def binary_patch_candidate_table() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for c in BINARY_PATCH_CANDIDATES:
        find_b: bytes = c["find"]
        replace_b: bytes = c["replace"]
        rows.append(
            {
                "patch_id": c["patch_id"],
                "b_sibling": c.get("b_sibling"),
                "target": c["target"],
                "find_len": len(find_b),
                "replace_len": len(replace_b),
                "identity": find_b == replace_b,
                "find_hex": find_b.hex(),
                "replace_hex": replace_b.hex(),
                "notes": c["notes"],
            }
        )
    return rows


def serialize_track_detect_fields(
    model: str = "",
    *,
    xnu_major: Optional[int] = None,
    environ: Optional[Mapping[str, str]] = None,
    search_roots: Optional[Iterable[Path]] = None,
    assume_tahoe: bool = False,
    **_kwargs: Any,
) -> dict[str, Any]:
    del model
    major = (
        TAHOE_XNU_MAJOR
        if assume_tahoe and xnu_major is None
        else (xnu_major if xnu_major is not None else TAHOE_XNU_MAJOR)
    )
    plan = assess_rootpatch_plan(
        major, search_roots=search_roots, environ=environ
    )
    patches = build_rootpatch_dict(
        major, search_roots=search_roots, environ=environ
    )
    return {
        "skylight_lut_rootpatch": {
            "track": "L5",
            "commit_prefix": "feat(skylight-L5):",
            "role_split_with_b": (
                "B=analysis/bytepatch API; L5-R=sys_patch OVERWRITE/MERGE recipes"
            ),
            "track_b_module": TRACK_B_MODULE,
            "track_b_commit": TRACK_B_COMMIT,
            "integrate_commit": INTEGRATE_COMMIT,
            "extreme_env": ENV_EXTREME,
            "slices_env": ENV_SLICES,
            "mode_env": ENV_MODE,
            "coredisplay_variant_env": ENV_COREDISPLAY_VARIANT,
            "plan": asdict(plan),
            "would_emit_patches": bool(patches),
            "patch_name": PATCH_NAME if patches else None,
            "binary_patch_candidates": binary_patch_candidate_table(),
            "runtime_inject": False,
            "task_for_pid": False,
            "evidence": list(EVIDENCE),
        }
    }


def sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int = 0,
    marketing_version: str = "",
    *,
    search_roots: Optional[Iterable[Path]] = None,
    environ: Optional[Mapping[str, str]] = None,
    extreme: bool = False,
) -> dict:
    """
    Track G contract: ``sys_patch_hooks(xnu_major, xnu_minor, marketing_version)``.

    ``X86_EXTREME=1`` → OVERWRITE SkyLight + CoreDisplay **only on Tahoe**.
    Sequoia (or any non-Tahoe) → ``{}`` even when extreme is set.
    """
    del xnu_minor
    return build_rootpatch_dict(
        xnu_major,
        search_roots=search_roots,
        environ=environ,
        extreme=extreme,
        marketing_version=marketing_version or None,
        product_version=marketing_version or None,
    )


def merge_into_yellow_screen_patches(
    existing: dict,
    xnu_major: int,
    xnu_minor: int = 0,
    marketing_version: str = "",
    *,
    environ: Optional[Mapping[str, str]] = None,
) -> dict:
    """MC INTEGRATE helper — does not edit shared tahoe_yellow_screen.py."""
    extra = sys_patch_hooks(
        xnu_major, xnu_minor, marketing_version, environ=environ
    )
    if not extra:
        return existing
    out = dict(existing)
    for key, value in extra.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = {**out[key], **value}
        else:
            out[key] = value
    return out


__all__ = [
    "ALL_SLICES",
    "BINARY_PATCH_CANDIDATES",
    "ENV_COREDISPLAY_VARIANT",
    "ENV_EXTREME",
    "ENV_MODE",
    "ENV_SLICES",
    "PATCH_NAME",
    "SLICE_BINARY",
    "SLICE_COREDISPLAY",
    "SLICE_SKYLIGHT",
    "TAHOE_XNU_MAJOR",
    "TRACK_CANDIDATES",
    "assess_rootpatch_plan",
    "binary_patch_candidate_table",
    "build_rootpatch_dict",
    "coredisplay_payload_folder",
    "extreme_enabled",
    "merge_into_yellow_screen_patches",
    "parse_enabled_slices",
    "patch_install_mode",
    "resolve_coredisplay_payload",
    "resolve_skylight_payload",
    "serialize_track_detect_fields",
    "skylight_payload_folder",
    "sys_patch_hooks",
]


def _stringify_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _stringify_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_stringify_keys(v) for v in obj]
    return obj


def _main(argv: Optional[Sequence[str]] = None) -> int:
    import json
    import sys as _sys

    args = list(argv if argv is not None else _sys.argv[1:])
    extreme = "--extreme" in args or extreme_enabled()
    env = dict(os.environ)
    if extreme:
        env[ENV_EXTREME] = "1"
    fields = serialize_track_detect_fields(environ=env, assume_tahoe=True)
    hooks = sys_patch_hooks(TAHOE_XNU_MAJOR, 0, "26.0", environ=env)
    print(
        json.dumps(
            {"detect": fields, "sys_patch_hooks": _stringify_keys(hooks)},
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
