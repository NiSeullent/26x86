"""
Track M — Metal 3802 Tahoe opt-in unlock (OCLP-style generation unlock).

Default deployment keeps ``LegacyMetal3802.patches()`` empty on Tahoe
(``xnu_major >= 25``) to avoid the Sequoia→Tahoe yellow/KP regressions.

Experimental reactivation (OCLP generation-unlock pattern):
  * ``X86_TAHOE_3802=1`` — track-scoped opt-in
  * ``X86_EXTREME=1`` — mission-wide extreme gate

Optional slice filter ``X86_TAHOE_3802_SLICES`` (comma-separated):
  ``common`` | ``extended`` | ``metallibs`` | ``all`` (default when opt-in).

Integration note (file-monopoly ban):
  Do **not** edit shared ``metal_3802.py`` in-tree from Track M.
  Apply the opt-in ``patches()`` body from
  ``opencore_legacy_patcher/.../metal_3802.py.stage-M`` via MC integrate.

This module never invents .metallib bytes. MetallibSupportPkg Tahoe coverage
is probed from the published manifest / install trees only.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Sequence

TAHOE_XNU_MAJOR = 25
SEQUOIA_XNU_MAJOR = 24

ENV_TAHOE_3802 = "X86_TAHOE_3802"
ENV_EXTREME = "X86_EXTREME"
ENV_SLICES = "X86_TAHOE_3802_SLICES"

SLICE_COMMON = "common"
SLICE_EXTENDED = "extended"
SLICE_METALLIBS = "metallibs"
ALL_SLICES: tuple[str, ...] = (SLICE_COMMON, SLICE_EXTENDED, SLICE_METALLIBS)

PATCH_KEY_BY_SLICE: dict[str, str] = {
    SLICE_COMMON: "Metal 3802 Common",
    SLICE_EXTENDED: "Metal 3802 Common Extended",
    SLICE_METALLIBS: "Metal 3802 .metallibs",
}
SLICE_BY_PATCH_KEY: dict[str, str] = {v: k for k, v in PATCH_KEY_BY_SLICE.items()}

METALLIB_SUPPORT_PKG_INSTALL_PATHS: tuple[str, ...] = (
    "/Library/Application Support/26x86/MetallibSupportPkg",
    "/Library/Application Support/Dortania/MetallibSupportPkg",
    "/Library/Application Support/Pyquick/MetallibSupportPkg",
)

METALLIB_MANIFEST_URLS: tuple[str, ...] = (
    "https://raw.githubusercontent.com/NiSeullent/26x86-MetallibSupportPkg/main/manifest.json",
    "https://dortania.github.io/MetallibSupportPkg/manifest.json",
)

_TRUTHY = frozenset({"1", "true", "yes", "on"})


@dataclass(frozen=True)
class SliceComboHypothesis:
    """Which Common / Extended / .metallibs combo is suspected to KP on Tahoe."""

    combo_id: str
    slices: tuple[str, ...]
    suspected_failure: str
    rationale: str
    recommended_probe_order: int


KP_HYPOTHESES: tuple[SliceComboHypothesis, ...] = (
    SliceComboHypothesis(
        combo_id="common_only",
        slices=(SLICE_COMMON,),
        suspected_failure="compiler/sandbox mismatch; yellow tint possible, KP less likely",
        rationale=(
            "Re-adds Monterey-era Metal/MTLCompiler/GPUCompiler + sandbox profile. "
            "Lowest surface; mirrors OCLP Ventura-era 3802 bootstrap before Extended."
        ),
        recommended_probe_order=1,
    ),
    SliceComboHypothesis(
        combo_id="common_plus_extended",
        slices=(SLICE_COMMON, SLICE_EXTENDED),
        suspected_failure="RenderBox/CoreImage ABI clash → WindowServer abort or KP",
        rationale=(
            "Extended downgrades Metal to 13.2.1-24 and swaps RenderBox 14.0-3802. "
            "Tahoe compositor (Liquid Glass) expects newer RenderBox/metallib ABI."
        ),
        recommended_probe_order=2,
    ),
    SliceComboHypothesis(
        combo_id="metallibs_only",
        slices=(SLICE_METALLIBS,),
        suspected_failure="V27→legacy AIR rewrite without compiler stack → shader load KP",
        rationale=(
            "Sequoia MetallibSupportPkg rewrites .metallib containers. On Tahoe, "
            "manifest often lacks 25xxx/26.x builds; applying Sequoia metallibs alone "
            "is the highest-risk isolation probe."
        ),
        recommended_probe_order=3,
    ),
    SliceComboHypothesis(
        combo_id="all_three",
        slices=ALL_SLICES,
        suspected_failure="full 3802 stack on Tahoe — historically yellow screen / KP",
        rationale=(
            "Pre-guard behavior (Sequoia path unchanged). Kept as last resort after "
            "slice isolation proves which layer panics."
        ),
        recommended_probe_order=4,
    ),
)


@dataclass(frozen=True)
class Metal3802ModelFixture:
    """Representative Metal 3802 Mac for Tahoe unlock experiments."""

    fixture_id: str
    family: str  # ivy_bridge | haswell | kepler
    smbios_models: tuple[str, ...]
    gpu_arch: str
    hardware_patch_class: str
    notes: str


METAL_3802_FIXTURES: tuple[Metal3802ModelFixture, ...] = (
    Metal3802ModelFixture(
        fixture_id="ivy_mbp10",
        family="ivy_bridge",
        smbios_models=("MacBookPro10,1", "MacBookPro10,2"),
        gpu_arch="Intel Ivy Bridge (HD 4000)",
        hardware_patch_class="IntelIvyBridge",
        notes="Capri framebuffer + HD4000 MTL; requires LegacyMetal3802 shared stack.",
    ),
    Metal3802ModelFixture(
        fixture_id="ivy_macpro61",
        family="ivy_bridge",
        smbios_models=("MacPro6,1",),
        gpu_arch="Intel Ivy Bridge Xeon + dual GCN 7000 (dGPU path separate)",
        hardware_patch_class="IntelIvyBridge",
        notes=(
            "iGPU is 3802; stock dual FirePro is GCN/31001. Tahoe default policy "
            "strips 3802 shared patches — opt-in only for iGPU experiments."
        ),
    ),
    Metal3802ModelFixture(
        fixture_id="haswell_mba6",
        family="haswell",
        smbios_models=("MacBookAir6,1", "MacBookAir6,2"),
        gpu_arch="Intel Haswell (HD 5000)",
        hardware_patch_class="IntelHaswell",
        notes="Haswell iGPU Metal 3802; primary laptop fixture for Common-only probes.",
    ),
    Metal3802ModelFixture(
        fixture_id="haswell_mbp11",
        family="haswell",
        smbios_models=("MacBookPro11,1", "MacBookPro11,2", "MacBookPro11,3"),
        gpu_arch="Intel Haswell (Iris / HD 4xxx)",
        hardware_patch_class="IntelHaswell",
        notes="Includes dual-GPU MBP11,3 (Kepler dGPU may also present).",
    ),
    Metal3802ModelFixture(
        fixture_id="haswell_imac14",
        family="haswell",
        smbios_models=("iMac14,1", "iMac14,2", "iMac14,3", "iMac14,4"),
        gpu_arch="Intel Haswell iGPU (± Kepler dGPU on some SKUs)",
        hardware_patch_class="IntelHaswell",
        notes="Desktop Haswell; good for metallib rewrite soak without laptop lid GPU quirks.",
    ),
    Metal3802ModelFixture(
        fixture_id="kepler_mbp113",
        family="kepler",
        smbios_models=("MacBookPro11,3",),
        gpu_arch="NVIDIA Kepler (GT 750M) + Haswell iGPU",
        hardware_patch_class="NvidiaKepler",
        notes="Kepler dGPU uses same LegacyMetal3802 shared patches as Ivy/Haswell.",
    ),
    Metal3802ModelFixture(
        fixture_id="kepler_imac14_dual",
        family="kepler",
        smbios_models=("iMac14,2", "iMac14,3"),
        gpu_arch="NVIDIA Kepler dGPU (selected SKUs)",
        hardware_patch_class="NvidiaKepler",
        notes="Confirm device_probe Kepler arch before applying NvidiaKepler kext set.",
    ),
)


def _env_truthy(name: str, environ: Optional[Mapping[str, str]] = None) -> bool:
    env = environ if environ is not None else os.environ
    raw = env.get(name, "")
    return raw.strip().lower() in _TRUTHY


def is_tahoe_3802_opt_in(environ: Optional[Mapping[str, str]] = None) -> bool:
    """True when experimental Tahoe 3802 shared patches may be emitted."""
    return _env_truthy(ENV_TAHOE_3802, environ) or _env_truthy(ENV_EXTREME, environ)


def parse_enabled_slices(
    environ: Optional[Mapping[str, str]] = None,
) -> frozenset[str]:
    """
    Resolve which patch slices to emit under opt-in.

    Default (empty / ``all``): all three slices — full shared-patch reactivation.
    Narrow with ``X86_TAHOE_3802_SLICES=common`` (etc.) for KP isolation.
    """
    env = environ if environ is not None else os.environ
    raw = env.get(ENV_SLICES, "").strip().lower()
    if not raw or raw in {"all", "*"}:
        return frozenset(ALL_SLICES)

    aliases = {
        "common": SLICE_COMMON,
        "c": SLICE_COMMON,
        "extended": SLICE_EXTENDED,
        "ext": SLICE_EXTENDED,
        "e": SLICE_EXTENDED,
        "metallibs": SLICE_METALLIBS,
        "metallib": SLICE_METALLIBS,
        "m": SLICE_METALLIBS,
        "libs": SLICE_METALLIBS,
    }
    out: set[str] = set()
    for token in raw.replace(";", ",").replace(" ", ",").split(","):
        token = token.strip()
        if not token:
            continue
        if token in {"all", "*"}:
            return frozenset(ALL_SLICES)
        mapped = aliases.get(token)
        if mapped:
            out.add(mapped)
    return frozenset(out) if out else frozenset(ALL_SLICES)


def enabled_patch_keys(
    environ: Optional[Mapping[str, str]] = None,
) -> frozenset[str]:
    """Patch dict keys allowed under the current slice filter."""
    return frozenset(
        PATCH_KEY_BY_SLICE[s]
        for s in parse_enabled_slices(environ)
        if s in PATCH_KEY_BY_SLICE
    )


def filter_tahoe_3802_patches(
    patches: Mapping[str, Any],
    *,
    xnu_major: int,
    environ: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    """
    Gate LegacyMetal3802 patch dict for Tahoe.

    Non-Tahoe: return patches unchanged.
    Tahoe without opt-in: ``{}``.
    Tahoe with opt-in: keep only enabled slice keys.
    """
    if xnu_major < TAHOE_XNU_MAJOR:
        return dict(patches)
    if not is_tahoe_3802_opt_in(environ):
        return {}
    allow = enabled_patch_keys(environ)
    return {k: v for k, v in patches.items() if k in allow}


def recommended_probe_sequence() -> list[dict[str, Any]]:
    """Ordered KP isolation steps (OCLP generation-unlock style)."""
    ordered = sorted(KP_HYPOTHESES, key=lambda h: h.recommended_probe_order)
    return [
        {
            "combo_id": h.combo_id,
            "slices": list(h.slices),
            "env": {
                ENV_TAHOE_3802: "1",
                ENV_SLICES: ",".join(h.slices),
            },
            "suspected_failure": h.suspected_failure,
            "rationale": h.rationale,
        }
        for h in ordered
    ]


def fixture_for_model(model: str) -> Optional[Metal3802ModelFixture]:
    """Return the first fixture that lists ``model`` in smbios_models."""
    for fix in METAL_3802_FIXTURES:
        if model in fix.smbios_models:
            return fix
    return None


def fixtures_by_family(family: str) -> list[Metal3802ModelFixture]:
    return [f for f in METAL_3802_FIXTURES if f.family == family]


@dataclass(frozen=True)
class MetallibManifestEntry:
    build: str
    version: str
    url: str = ""
    name: str = ""
    date: str = ""
    sha1sum: str = ""

    @property
    def is_tahoe(self) -> bool:
        """Tahoe = macOS 26 / XNU 25 build prefixes (25A… / 25B…) or version 26.x."""
        build = (self.build or "").upper()
        if build.startswith("25"):
            return True
        version = (self.version or "").strip()
        return version.startswith("26.") or version == "26"


@dataclass(frozen=True)
class MetallibTahoeManifestReport:
    """Coverage of MetallibSupportPkg for Tahoe 3802 .metallibs."""

    manifest_url: Optional[str]
    entries_total: int
    tahoe_entries: list[MetallibManifestEntry] = field(default_factory=list)
    sequoia_entries_sample: list[MetallibManifestEntry] = field(default_factory=list)
    install_paths_present: list[str] = field(default_factory=list)
    tahoe_metallib_ready: bool = False
    gaps: list[str] = field(default_factory=list)
    source: str = "none"  # remote | fixture | none | skipped


def _parse_manifest_items(raw: Any) -> list[MetallibManifestEntry]:
    if not isinstance(raw, list):
        return []
    out: list[MetallibManifestEntry] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        build = str(item.get("build") or "")
        version = str(item.get("version") or "")
        if not build and not version:
            continue
        out.append(
            MetallibManifestEntry(
                build=build,
                version=version,
                url=str(item.get("url") or ""),
                name=str(item.get("name") or ""),
                date=str(item.get("date") or ""),
                sha1sum=str(item.get("sha1sum") or ""),
            )
        )
    return out


def load_metallib_manifest(
    *,
    urls: Optional[Sequence[str]] = None,
    fixture_json: Optional[Any] = None,
    timeout_sec: float = 5.0,
) -> tuple[list[MetallibManifestEntry], Optional[str], str]:
    """
    Load MetallibSupportPkg manifest entries.

    ``fixture_json`` short-circuits network (unit tests). Returns
    ``(entries, url_used, source)``.
    """
    if fixture_json is not None:
        return _parse_manifest_items(fixture_json), None, "fixture"

    for url in urls or METALLIB_MANIFEST_URLS:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "26x86-TrackM/metal3802_tahoe"},
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            entries = _parse_manifest_items(payload)
            if entries:
                return entries, url, "remote"
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            json.JSONDecodeError,
            OSError,
        ):
            continue
    return [], None, "none"


def probe_install_trees(
    install_paths: Optional[Iterable[str]] = None,
) -> list[str]:
    present: list[str] = []
    for raw in install_paths or METALLIB_SUPPORT_PKG_INSTALL_PATHS:
        path = Path(raw)
        try:
            if path.is_dir() and any(path.iterdir()):
                present.append(str(path))
        except OSError:
            continue
    return present


def assess_metallib_tahoe_manifest(
    *,
    urls: Optional[Sequence[str]] = None,
    fixture_json: Optional[Any] = None,
    install_paths: Optional[Iterable[str]] = None,
    timeout_sec: float = 5.0,
) -> MetallibTahoeManifestReport:
    """
    Decide whether MetallibSupportPkg can back Tahoe ``Metal 3802 .metallibs``.

    Ready when at least one Tahoe-tagged manifest entry exists **or** a local
    install tree is present (operator-supplied PKG). Missing Tahoe remote
    entries are recorded as gaps — never invented.
    """
    entries, url, source = load_metallib_manifest(
        urls=urls, fixture_json=fixture_json, timeout_sec=timeout_sec
    )
    tahoe = [e for e in entries if e.is_tahoe]
    sequoia = [e for e in entries if (e.build or "").upper().startswith("24")][:3]
    installed = probe_install_trees(install_paths)
    gaps: list[str] = []

    if source == "none" and not installed:
        gaps.append(
            "MetallibSupportPkg manifest unreachable and no local install tree "
            f"under {list(METALLIB_SUPPORT_PKG_INSTALL_PATHS)}"
        )
    if entries and not tahoe:
        gaps.append(
            "Manifest has Sequoia (24xxx) metallibs but no Tahoe (25xxx / 26.x) "
            "entry — .metallibs slice needs a Tahoe MetallibSupportPkg build"
        )
    if not installed and tahoe:
        gaps.append(
            "Tahoe manifest entry present but MetallibSupportPkg not installed locally"
        )

    ready = bool(tahoe) or bool(installed)
    return MetallibTahoeManifestReport(
        manifest_url=url,
        entries_total=len(entries),
        tahoe_entries=tahoe,
        sequoia_entries_sample=sequoia,
        install_paths_present=installed,
        tahoe_metallib_ready=ready,
        gaps=gaps,
        source=source,
    )


def metallibs_slice_advised(
    report: Optional[MetallibTahoeManifestReport] = None,
    *,
    environ: Optional[Mapping[str, str]] = None,
) -> bool:
    """Advisory: emit .metallibs slice only when opt-in + Tahoe metallib ready."""
    if report is None:
        report = assess_metallib_tahoe_manifest()
    if not is_tahoe_3802_opt_in(environ):
        return False
    if SLICE_METALLIBS not in parse_enabled_slices(environ):
        return False
    return report.tahoe_metallib_ready


def serialize_metal3802_tahoe_fields(
    xnu_major: Optional[int] = None,
    *,
    model: Optional[str] = None,
    environ: Optional[Mapping[str, str]] = None,
    manifest_fixture: Optional[Any] = None,
    install_paths: Optional[Iterable[str]] = None,
    skip_network: bool = True,
) -> dict[str, Any]:
    """
    Fields for detect JSON / research (Track M).

    ``skip_network=True`` (default) avoids live manifest fetch in detect paths;
    pass ``skip_network=False`` or ``manifest_fixture=...`` for explicit probes.
    """
    major = TAHOE_XNU_MAJOR if xnu_major is None else xnu_major
    opt_in = is_tahoe_3802_opt_in(environ)
    slices = sorted(parse_enabled_slices(environ)) if opt_in else []
    fixture = fixture_for_model(model) if model else None

    if skip_network and manifest_fixture is None:
        installed = probe_install_trees(install_paths)
        gaps = [
            "manifest network probe skipped (pass skip_network=False or fixture)",
        ]
        if not installed:
            gaps.append("no local MetallibSupportPkg install tree")
        manifest = MetallibTahoeManifestReport(
            manifest_url=None,
            entries_total=0,
            tahoe_entries=[],
            sequoia_entries_sample=[],
            install_paths_present=installed,
            tahoe_metallib_ready=bool(installed),
            gaps=gaps,
            source="skipped",
        )
    else:
        manifest = assess_metallib_tahoe_manifest(
            fixture_json=manifest_fixture,
            install_paths=install_paths,
        )

    return {
        "metal3802_track": "M",
        "metal3802_tahoe_opt_in": opt_in,
        "metal3802_tahoe_default_blocked": major >= TAHOE_XNU_MAJOR and not opt_in,
        "metal3802_enabled_slices": slices,
        "metal3802_enabled_patch_keys": (
            sorted(enabled_patch_keys(environ)) if opt_in else []
        ),
        "metal3802_kp_hypotheses": [asdict(h) for h in KP_HYPOTHESES],
        "metal3802_probe_sequence": recommended_probe_sequence(),
        "metal3802_fixture": asdict(fixture) if fixture else None,
        "metal3802_fixtures": [asdict(f) for f in METAL_3802_FIXTURES],
        "metallib_support_pkg_tahoe": {
            "manifest_url": manifest.manifest_url,
            "source": manifest.source,
            "entries_total": manifest.entries_total,
            "tahoe_entry_count": len(manifest.tahoe_entries),
            "tahoe_builds": [e.build for e in manifest.tahoe_entries],
            "install_paths_present": list(manifest.install_paths_present),
            "tahoe_metallib_ready": manifest.tahoe_metallib_ready,
            "gaps": list(manifest.gaps),
            "metallibs_slice_advised": metallibs_slice_advised(
                manifest, environ=environ
            ),
        },
        "metal3802_env": {
            ENV_TAHOE_3802: ENV_TAHOE_3802,
            ENV_EXTREME: ENV_EXTREME,
            ENV_SLICES: ENV_SLICES,
        },
        "metal3802_stage_sidecar": (
            "opencore_legacy_patcher/sys_patch/patchsets/shared_patches/"
            "metal_3802.py.stage-M"
        ),
    }


def merge_detect_fields(
    payload: MutableMapping[str, Any],
    **kwargs: Any,
) -> MutableMapping[str, Any]:
    """In-place merge of Track M fields into a detect JSON payload."""
    payload.update(serialize_metal3802_tahoe_fields(**kwargs))
    return payload
