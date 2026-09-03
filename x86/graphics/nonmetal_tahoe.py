"""
Track N — Non-Metal Tahoe opt-in unlock (OCLP-style generation unlock).

Default deployment keeps live ``non_metal*.py`` empty on Tahoe
(``xnu_major >= 25``) to avoid KP / yellow-screen regressions.

Experimental reactivation (must actually **refill** shared patch keys):
  * ``X86_TAHOE_NONMETAL=1`` — track-scoped opt-in
  * ``X86_EXTREME=1`` — mission-wide extreme gate
  Either flag alone unlocks (same pattern as Track M). Do not leave Tahoe
  permanently ``{}`` under opt-in.

Optional stage filter ``X86_TAHOE_NONMETAL_STAGE`` (cumulative):
  ``common`` | ``ioaccel`` | ``coredisplay`` | ``enforcement`` | ``all``
  Default when opted in: ``all`` (Common→IOAccel→CoreDisplay). Enforcement
  still needs ``X86_TAHOE_NONMETAL_ENFORCEMENT=1`` (useMetal=no risk).

Integration (file-monopoly ban):
  Do **not** edit live ``non_metal*.py`` from Track N.
  Opt-in ``patches()`` bodies live in ``*.py.stage-N``; MC integrate copies
  them over the shared files. ``filter_nonmetal_tahoe_patches`` is the refill
  gate (mirrors ``filter_tahoe_3802_patches``).

Software render is accepted. Never invents moraea binaries.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

TAHOE_XNU_MAJOR = 25

ENV_EXTREME = "X86_EXTREME"
ENV_NONMETAL = "X86_TAHOE_NONMETAL"
ENV_STAGE = "X86_TAHOE_NONMETAL_STAGE"
ENV_ENFORCEMENT = "X86_TAHOE_NONMETAL_ENFORCEMENT"

STAGE_COMMON = "common"
STAGE_IOACCEL = "ioaccel"
STAGE_COREDISPLAY = "coredisplay"
STAGE_ENFORCEMENT = "enforcement"

STAGE_ORDER: tuple[str, ...] = (
    STAGE_COMMON,
    STAGE_IOACCEL,
    STAGE_COREDISPLAY,
    STAGE_ENFORCEMENT,
)

PATCH_KEY_BY_STAGE: dict[str, str] = {
    STAGE_COMMON: "Non-Metal Common",
    STAGE_IOACCEL: "Non-Metal IOAccelerator Common",
    STAGE_COREDISPLAY: "Non-Metal CoreDisplay Common",
    STAGE_ENFORCEMENT: "Non-Metal Enforcement",
}
STAGE_BY_PATCH_KEY: dict[str, str] = {v: k for k, v in PATCH_KEY_BY_STAGE.items()}

MORAEA_NON_METAL_FRAMEWORKS = "https://github.com/moraea/non-metal-frameworks"
SKYLIGHT_OLD_MARKER = (
    "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLightOld.dylib"
)

STAGE_N_SHARED_PATCHES: tuple[str, ...] = (
    "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/non_metal.py.stage-N",
    "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/non_metal_ioaccel.py.stage-N",
    "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/non_metal_coredisplay.py.stage-N",
    "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/non_metal_enforcement.py.stage-N",
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_TRUTHY = frozenset({"1", "true", "yes", "on"})


def _env_truthy(key: str, environ: Optional[Mapping[str, str]] = None) -> bool:
    env = environ if environ is not None else os.environ
    raw = env.get(key)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUTHY


def tahoe_nonmetal_opt_in(
    environ: Optional[Mapping[str, str]] = None,
) -> bool:
    """True when experimental Tahoe Non-Metal shared patches may be emitted."""
    return _env_truthy(ENV_NONMETAL, environ) or _env_truthy(ENV_EXTREME, environ)


def _requested_stage_name(
    environ: Optional[Mapping[str, str]] = None,
) -> str:
    env = environ if environ is not None else os.environ
    # Default ALL when opted in — do not keep stages closed ("안 염 금지").
    raw = (env.get(ENV_STAGE) or "all").strip().lower()
    if raw in {"all", "max", "*"}:
        return "all"
    if raw in STAGE_ORDER:
        return raw
    return "all"


def enabled_nonmetal_stages(
    environ: Optional[Mapping[str, str]] = None,
) -> frozenset[str]:
    """
    Cumulative stages unlocked under the current env.

    Enforcement is withheld unless ``X86_TAHOE_NONMETAL_ENFORCEMENT=1``.
    """
    env = environ if environ is not None else os.environ
    if not tahoe_nonmetal_opt_in(env):
        return frozenset()

    name = _requested_stage_name(env)
    if name == "all":
        stages = set(STAGE_ORDER)
    else:
        idx = STAGE_ORDER.index(name)
        stages = set(STAGE_ORDER[: idx + 1])

    if STAGE_ENFORCEMENT in stages and not _env_truthy(ENV_ENFORCEMENT, env):
        stages.discard(STAGE_ENFORCEMENT)
    return frozenset(stages)


def enabled_patch_keys(
    environ: Optional[Mapping[str, str]] = None,
) -> frozenset[str]:
    return frozenset(
        PATCH_KEY_BY_STAGE[s]
        for s in enabled_nonmetal_stages(environ)
        if s in PATCH_KEY_BY_STAGE
    )


def allow_nonmetal_common_on_tahoe(
    environ: Optional[Mapping[str, str]] = None,
) -> bool:
    return STAGE_COMMON in enabled_nonmetal_stages(environ)


def allow_nonmetal_ioaccel_on_tahoe(
    environ: Optional[Mapping[str, str]] = None,
) -> bool:
    return STAGE_IOACCEL in enabled_nonmetal_stages(environ)


def allow_nonmetal_coredisplay_on_tahoe(
    environ: Optional[Mapping[str, str]] = None,
) -> bool:
    return STAGE_COREDISPLAY in enabled_nonmetal_stages(environ)


def allow_nonmetal_enforcement_on_tahoe(
    environ: Optional[Mapping[str, str]] = None,
) -> bool:
    return STAGE_ENFORCEMENT in enabled_nonmetal_stages(environ)


def filter_nonmetal_tahoe_patches(
    patches: Mapping[str, Any],
    *,
    xnu_major: int,
    environ: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    """
    Gate Non-Metal shared patch dict for Tahoe (Track N refill).

    Non-Tahoe: return patches unchanged.
    Tahoe without opt-in: ``{}``.
    Tahoe with opt-in: keep only enabled stage keys — **must be non-empty**
    when at least Common is enabled (no permanent closed gate under opt-in).
    """
    if xnu_major < TAHOE_XNU_MAJOR:
        return dict(patches)
    if not tahoe_nonmetal_opt_in(environ):
        return {}
    allow = enabled_patch_keys(environ)
    return {k: v for k, v in patches.items() if k in allow}


def stock_skylight_old_present(marker: Optional[str] = None) -> bool:
    path = Path(marker or SKYLIGHT_OLD_MARKER)
    try:
        return path.is_file()
    except OSError:
        return False


def stage_n_proposal_paths(
    repo_root: Optional[Path] = None,
) -> list[Path]:
    root = Path(repo_root) if repo_root is not None else REPO_ROOT
    return [root / rel for rel in STAGE_N_SHARED_PATCHES]


def stage_n_proposals_present(repo_root: Optional[Path] = None) -> bool:
    return all(p.is_file() for p in stage_n_proposal_paths(repo_root))


@dataclass(frozen=True)
class NonMetalTahoeGateReport:
    xnu_major: int
    tahoe: bool
    opt_in: bool
    stages_enabled: tuple[str, ...]
    common_allowed: bool
    ioaccel_allowed: bool
    coredisplay_allowed: bool
    enforcement_allowed: bool
    skylight_old_present: bool
    stage_n_proposals_present: bool = False
    software_render_accepted: bool = True
    usemetal_enforcement_blocked_by_default: bool = True
    moraea_non_metal_frameworks: str = MORAEA_NON_METAL_FRAMEWORKS
    notes: list[str] = field(default_factory=list)


def assess_nonmetal_tahoe_gate(
    xnu_major: int,
    *,
    environ: Optional[Mapping[str, str]] = None,
    skylight_old: Optional[bool] = None,
    repo_root: Optional[Path] = None,
) -> NonMetalTahoeGateReport:
    env = environ if environ is not None else os.environ
    tahoe = xnu_major >= TAHOE_XNU_MAJOR
    stages = tuple(s for s in STAGE_ORDER if s in enabled_nonmetal_stages(env))
    opt_in = tahoe_nonmetal_opt_in(env)
    stub = (
        bool(skylight_old)
        if skylight_old is not None
        else stock_skylight_old_present()
    )
    proposals_ok = stage_n_proposals_present(repo_root)
    notes: list[str] = []
    if tahoe and not opt_in:
        notes.append(
            "Tahoe Non-Metal live shared stays {}; set "
            f"{ENV_NONMETAL}=1 or {ENV_EXTREME}=1 then MC-integrate *.py.stage-N."
        )
    if tahoe and opt_in:
        notes.append(
            f"Opt-in active — filter_nonmetal_tahoe_patches will refill "
            f"{list(enabled_patch_keys(env))} from stage-N bodies."
        )
    if tahoe and opt_in and STAGE_ENFORCEMENT not in stages:
        notes.append(
            "useMetal=no Enforcement withheld — set "
            f"{ENV_ENFORCEMENT}=1 only after WS color is stable."
        )
    if not stub:
        notes.append(
            "SkyLightOld.dylib absent — stock Tahoe SkyLight ignores "
            "SkyLightPlugins; moraea Non-Metal stubs required for plugin loader."
        )
    if not proposals_ok:
        notes.append("Track N *.py.stage-N proposal files missing from tree.")
    return NonMetalTahoeGateReport(
        xnu_major=xnu_major,
        tahoe=tahoe,
        opt_in=opt_in and tahoe,
        stages_enabled=stages if (opt_in and tahoe) else (),
        common_allowed=tahoe and allow_nonmetal_common_on_tahoe(env),
        ioaccel_allowed=tahoe and allow_nonmetal_ioaccel_on_tahoe(env),
        coredisplay_allowed=tahoe and allow_nonmetal_coredisplay_on_tahoe(env),
        enforcement_allowed=tahoe and allow_nonmetal_enforcement_on_tahoe(env),
        skylight_old_present=stub,
        stage_n_proposals_present=proposals_ok,
        notes=notes,
    )


def serialize_nonmetal_tahoe_fields(
    model: str = "",
    *,
    xnu_major: Optional[int] = None,
    gpu_archs: Optional[Iterable[Any]] = None,
    environ: Optional[Mapping[str, str]] = None,
    assume_tahoe: bool = False,
    **_kwargs: Any,
) -> dict[str, Any]:
    major = TAHOE_XNU_MAJOR if assume_tahoe and xnu_major is None else (
        xnu_major if xnu_major is not None else TAHOE_XNU_MAJOR
    )
    report = assess_nonmetal_tahoe_gate(major, environ=environ)
    fixture = match_nonmetal_fixture(model, gpu_archs=gpu_archs)
    payload = {
        "nonmetal_track": "N",
        "nonmetal_tahoe_opt_in": report.opt_in,
        "nonmetal_tahoe_stages": list(report.stages_enabled),
        "nonmetal_enabled_patch_keys": (
            sorted(enabled_patch_keys(environ)) if report.opt_in else []
        ),
        "nonmetal_common_allowed_on_tahoe": report.common_allowed,
        "nonmetal_ioaccel_allowed_on_tahoe": report.ioaccel_allowed,
        "nonmetal_coredisplay_allowed_on_tahoe": report.coredisplay_allowed,
        "nonmetal_enforcement_allowed_on_tahoe": report.enforcement_allowed,
        "nonmetal_blocked_on_tahoe_default": report.tahoe and not report.opt_in,
        "nonmetal_stage_n_proposals_present": report.stage_n_proposals_present,
        "nonmetal_stage_sidecar": "non_metal.py.stage-N (+ ioaccel/coredisplay/enforcement)",
        "skylight_old_present": report.skylight_old_present,
        "nonmetal_software_render_accepted": report.software_render_accepted,
        "nonmetal_usemetal_enforcement_extra_opt_in": ENV_ENFORCEMENT,
        "moraea_non_metal_frameworks": report.moraea_non_metal_frameworks,
        "nonmetal_gate_notes": list(report.notes),
        "nonmetal_env": {
            "extreme": ENV_EXTREME,
            "nonmetal": ENV_NONMETAL,
            "stage": ENV_STAGE,
            "enforcement": ENV_ENFORCEMENT,
        },
    }
    if fixture is not None:
        payload["nonmetal_fixture"] = asdict(fixture)
    return payload


def sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int = 0,
    marketing_version: str = "",
) -> dict:
    """
    Emit Non-Metal shared patches under Tahoe opt-in by evaluating ``*.stage-N``.

    Live ``non_metal*.py`` stay ``{}`` until MC integrate; this hook lets Track G
    / yellow-screen merge inject the stage-N bodies when env unlocks.
    """
    del xnu_minor, marketing_version
    if xnu_major < TAHOE_XNU_MAJOR:
        return {}
    if not tahoe_nonmetal_opt_in():
        return {}

    merged: dict = {}
    for stem, cls_name in (
        ("non_metal", "NonMetal"),
        ("non_metal_ioaccel", "NonMetalIOAccelerator"),
        ("non_metal_coredisplay", "NonMetalCoreDisplay"),
        ("non_metal_enforcement", "NonMetalEnforcement"),
    ):
        mod = _load_stage_n_module(stem)
        if mod is None:
            continue
        cls = getattr(mod, cls_name, None)
        if cls is None:
            continue
        try:
            extra = cls(xnu_major, 0, "25A").patches() or {}
        except Exception:
            continue
        for key, value in extra.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
    return merged


def _load_stage_n_module(stem: str):
    """Load ``{stem}.py.stage-N`` (non-.py suffix → SourceFileLoader)."""
    import importlib
    import importlib.machinery
    import importlib.util
    import sys

    path = REPO_ROOT / (
        "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/"
        f"{stem}.py.stage-N"
    )
    if not path.is_file():
        return None
    pkg = "opencore_legacy_patcher.sys_patch.patchsets.shared_patches"
    name = f"{pkg}._stage_n_{stem}"
    if name in sys.modules:
        return sys.modules[name]
    if pkg not in sys.modules:
        importlib.import_module(pkg)
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg
    mod.__file__ = str(path)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(name, None)
        return None
    return mod


@dataclass(frozen=True)
class NonMetalHardwareFixture:
    id: str
    model: str
    gpu_arch: str
    graphics_subclass: str
    shared_patch_sets: tuple[str, ...]
    hardware_patch_module: str
    notes: tuple[str, ...] = ()


FIXTURE_MACPRO51_TERASCALE = NonMetalHardwareFixture(
    id="macpro51_terascale2",
    model="MacPro5,1",
    gpu_arch="TeraScale_2",
    graphics_subclass="NON_METAL_GRAPHICS",
    shared_patch_sets=(
        "Non-Metal Common",
        "Non-Metal IOAccelerator Common",
        "AMD TeraScale",
    ),
    hardware_patch_module=(
        "opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.amd_terascale_2"
    ),
    notes=(
        "Socket Mac Pro + aftermarket TeraScale; pre-AVX CPU separate track.",
        "Tahoe default: live Non-Metal {}; stage-N + opt-in refills Common/IOAccel.",
    ),
)

FIXTURE_NONMETAL_IGPU_SANDY = NonMetalHardwareFixture(
    id="nonmetal_igpu_sandy_bridge",
    model="MacBookPro8,2",
    gpu_arch="Sandy_Bridge",
    graphics_subclass="NON_METAL_GRAPHICS",
    shared_patch_sets=("Non-Metal Common",),
    hardware_patch_module=(
        "opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.intel_sandy_bridge"
    ),
    notes=(
        "Classic Non-Metal iGPU; software render accepted on Tahoe.",
        "Avoid Enforcement (useMetal=no) until compositor color is verified.",
    ),
)

FIXTURE_NONMETAL_IGPU_IRON_LAKE = NonMetalHardwareFixture(
    id="nonmetal_igpu_iron_lake",
    model="MacBookPro6,2",
    gpu_arch="Iron_Lake",
    graphics_subclass="NON_METAL_GRAPHICS",
    shared_patch_sets=("Non-Metal Common",),
    hardware_patch_module=(
        "opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.intel_iron_lake"
    ),
    notes=(
        "Iron Lake Non-Metal iGPU; Liquid Glass UI expected degraded.",
        "moraea non-metal-frameworks Tahoe payloads still incomplete.",
    ),
)

ALL_NONMETAL_FIXTURES: tuple[NonMetalHardwareFixture, ...] = (
    FIXTURE_MACPRO51_TERASCALE,
    FIXTURE_NONMETAL_IGPU_SANDY,
    FIXTURE_NONMETAL_IGPU_IRON_LAKE,
)


def _gpu_token(gpu: Any) -> str:
    if gpu is None:
        return ""
    if isinstance(gpu, str):
        return gpu
    arch = getattr(gpu, "arch", None)
    if arch is not None:
        return str(getattr(arch, "name", arch))
    name = getattr(gpu, "name", None)
    if name:
        return str(name)
    if isinstance(gpu, dict):
        return str(gpu.get("arch") or gpu.get("name") or "")
    return str(gpu)


def match_nonmetal_fixture(
    model: str,
    gpu_archs: Optional[Iterable[Any]] = None,
) -> Optional[NonMetalHardwareFixture]:
    tokens = " ".join(_gpu_token(g) for g in (gpu_archs or [])).lower()
    model_l = (model or "").strip()

    if model_l == "MacPro5,1" and (
        not tokens
        or "terascale" in tokens
        or "radeon hd 5" in tokens
        or "radeon hd 6" in tokens
    ):
        return FIXTURE_MACPRO51_TERASCALE
    if "terascale" in tokens:
        return FIXTURE_MACPRO51_TERASCALE
    if "sandy" in tokens or model_l.startswith("MacBookPro8"):
        return FIXTURE_NONMETAL_IGPU_SANDY
    if "iron" in tokens or model_l.startswith("MacBookPro6"):
        return FIXTURE_NONMETAL_IGPU_IRON_LAKE
    return None
