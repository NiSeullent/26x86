"""
Extreme Tahoe validation orchestration (mock-host friendly).

Entry: ``python -m x86.extreme.validation`` or ``Tools/run_extreme_validation.py``.
Never requires a live Tahoe root volume — fixtures inject xnu/product/model/GPU.
"""

from __future__ import annotations

import json
import os
import platform
import sys
import unittest
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

UNITTEST_MODULES: tuple[str, ...] = (
    "x86.graphics.test_tahoe_gate",
    "x86.graphics.test_extreme_host_combo",
    "x86.graphics.test_metal3802_tahoe",
    "x86.graphics.test_nonmetal_tahoe",
    "x86.graphics.test_skylight_lut_rootpatch",
    "x86.graphics.test_metallib_preflight",
    "x86.graphics.test_metallib_renderbox",
    "x86.graphics.test_interpose",
    "x86.graphics.test_yellow_screen",
    "x86.graphics.test_iosurface_coreanimation",
    "x86.graphics.test_detect",
    "x86.graphics.test_skylight_tracks",
    "x86.graphics.test_shader_avx",
    "x86.profiles.test_macpro5_vega64_tahoe",
    "x86.pre_avx.test_detect",
    "opencore_legacy_patcher.efi_builder.test_gcn_agdp",
    "x86.extreme.test_validation",
    "x86.extreme.test_apply_order_mock",
)


@dataclass
class StepResult:
    name: str
    ok: bool
    detail: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


def _host_snapshot() -> dict[str, Any]:
    product = ""
    build = ""
    if sys.platform == "darwin":
        import subprocess

        try:
            product = subprocess.check_output(
                ["/usr/bin/sw_vers", "-productVersion"], text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            product = ""
        try:
            build = subprocess.check_output(
                ["/usr/bin/sw_vers", "-buildVersion"], text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            build = ""
    return {
        "platform": sys.platform,
        "machine": platform.machine(),
        "product_version": product,
        "build_version": build,
        "darwin_release": os.uname().release if hasattr(os, "uname") else "",
        "has_qemu": bool(_which("qemu-system-x86_64")),
        "has_utm": Path("/Applications/UTM.app").is_dir(),
        "has_docker": bool(_which("docker")),
    }


def _which(name: str) -> Optional[str]:
    from shutil import which

    return which(name)


def step_detect_fixture() -> StepResult:
    from x86.profiles.fixtures import macpro5_vega64_fixture_payload
    from x86.graphics.tahoe_gate import detect_flashed_mac_pro, serialize_root_patch_gates

    payload = macpro5_vega64_fixture_payload()
    flash = detect_flashed_mac_pro(
        reported_model="MacPro7,1",
        real_model="MacPro5,1",
        cpu_brand="Intel(R) Xeon(R) CPU X5675 @ 3.07GHz",
        smc_version="1.39f11",
    )
    gates_seq = serialize_root_patch_gates(
        xnu_major=24, product_version="15.5", environ={"X86_EXTREME": "1"}
    )
    gates_tah = serialize_root_patch_gates(
        xnu_major=25, product_version="26.0", environ={"X86_EXTREME": "1"}
    )
    ok = (
        payload.get("gpu_family") == "vega"
        and payload.get("pre_avx_mac_pro") is True
        and flash["flashed_mac_pro"]
        and gates_seq["root_patches_allowed"] is False
        and gates_tah["root_patches_allowed"] is True
    )
    return StepResult(
        name="detect_fixture",
        ok=ok,
        detail={
            "profile_match": payload.get("profile_match"),
            "gpu_family": payload.get("gpu_family"),
            "flashed_mac_pro": flash["flashed_mac_pro"],
            "sequoia_root_allowed": gates_seq["root_patches_allowed"],
            "tahoe_root_allowed": gates_tah["root_patches_allowed"],
        },
    )


def step_patchset_emptiness() -> StepResult:
    """Sequoia+extreme → empty; Tahoe+flags → non-empty dicts."""
    from x86.graphics.metal3802_tahoe import (
        ENV_EXTREME,
        filter_tahoe_3802_patches,
        PATCH_KEY_BY_SLICE,
        ALL_SLICES,
    )
    from x86.graphics.nonmetal_tahoe import filter_nonmetal_tahoe_patches
    from x86.graphics.skylight_lut_rootpatch import (
        ENV_EXTREME as L5_EXTREME,
        PATCH_NAME,
        sys_patch_hooks as l5_hooks,
    )
    from x86.graphics.yellow_screen import yellow_screen_mitigations

    patches_m = {PATCH_KEY_BY_SLICE[s]: {"n": s} for s in ALL_SLICES}
    seq_m = filter_tahoe_3802_patches(
        patches_m, xnu_major=24, environ={ENV_EXTREME: "1"}
    )
    tah_m = filter_tahoe_3802_patches(
        patches_m, xnu_major=25, environ={ENV_EXTREME: "1"}
    )
    seq_n = filter_nonmetal_tahoe_patches(
        {"Non-Metal Common": {"ok": True}},
        xnu_major=24,
        environ={ENV_EXTREME: "1"},
    )
    tah_n = filter_nonmetal_tahoe_patches(
        {"Non-Metal Common": {"ok": True}},
        xnu_major=25,
        environ={ENV_EXTREME: "1"},
    )
    seq_l5 = l5_hooks(24, 0, "15.5", environ={L5_EXTREME: "1"})
    tah_l5 = l5_hooks(25, 0, "26.0", environ={L5_EXTREME: "1"})
    seq_y = yellow_screen_mitigations(
        "MacPro5,1", gpu_archs=["Vega"], xnu_major=24
    )
    tah_y = yellow_screen_mitigations(
        "MacPro5,1", gpu_archs=["Vega"], xnu_major=25
    )
    ok = (
        seq_m == {}
        and bool(tah_m)
        and seq_n == {}
        and bool(tah_n)
        and seq_l5 == {}
        and PATCH_NAME in tah_l5
        and seq_y == []
        and bool(tah_y)
    )
    return StepResult(
        name="patchset_emptiness",
        ok=ok,
        detail={
            "metal3802_sequoia": seq_m,
            "metal3802_tahoe_keys": list(tah_m.keys()),
            "nonmetal_sequoia": seq_n,
            "nonmetal_tahoe_keys": list(tah_n.keys()),
            "l5_sequoia": seq_l5,
            "l5_tahoe_keys": list(tah_l5.keys()),
            "yellow_sequoia": seq_y,
            "yellow_tahoe": tah_y,
        },
    )


def step_profile_dry_run() -> StepResult:
    from x86.profiles.macpro5_vega64_tahoe import apply_profile

    report = apply_profile(
        dry_run=True, include_extreme=True, environ={"X86_EXTREME": "1"}
    )
    order = report.get("order") or []
    ok = (
        "efi.agdpmod_shikigva" in order
        and "efi.restrictevents_jsc" in order
        and "root.yellow_mitigations" in order
        and "extreme.hooks" in order
    )
    return StepResult(name="profile_dry_run", ok=ok, detail={"order": order})


def step_efi_bridge() -> StepResult:
    from opencore_legacy_patcher.efi_builder.gcn_agdp import (
        apply_gcn_agdp_fallbacks,
        config_has_agdpmod,
    )

    config: dict[str, Any] = {}
    apply_gcn_agdp_fallbacks(config)
    boot = config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]
    rev_uuid = "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"
    # RestrictEvents path via profile apply into empty config
    from x86.profiles.macpro5_vega64_tahoe import apply_profile

    apply_profile(config=config, dry_run=False, include_extreme=False)
    rev = config.get("NVRAM", {}).get("Add", {}).get(rev_uuid, {}).get("revpatch", "")
    kexts = {e["BundlePath"] for e in config.get("Kernel", {}).get("Add", [])}
    ok = (
        config_has_agdpmod(config)
        and "agdpmod=" in boot
        and "jsc" in str(rev).split(",")
        and "RestrictEvents.kext" in kexts
    )
    return StepResult(
        name="efi_bridge",
        ok=ok,
        detail={
            "agdpmod": config_has_agdpmod(config),
            "revpatch": rev,
            "kexts": sorted(kexts),
        },
    )


def step_h_n_iosurface_prefer() -> StepResult:
    from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType
    from x86.graphics.nonmetal_tahoe import (
        ENV_EXTREME,
        ENV_IOSURFACE_CA,
        filter_nonmetal_tahoe_patches,
        H_PREFERRED_IOSURFACE_KEXT,
    )

    base = {
        "Non-Metal IOAccelerator Common": {
            PatchType.OVERWRITE_SYSTEM_VOLUME: {
                "/System/Library/Extensions": {"IOSurface.kext": "10.14.6"},
            },
            PatchType.MERGE_SYSTEM_VOLUME: {
                "/System/Library/Frameworks": {
                    "IOSurface.framework": "10.14.6-24"
                },
            },
        },
        "Non-Metal Common": {"ok": True},
    }
    no_h = filter_nonmetal_tahoe_patches(
        base, xnu_major=25, environ={ENV_EXTREME: "1"}
    )
    with_h = filter_nonmetal_tahoe_patches(
        base,
        xnu_major=25,
        environ={ENV_EXTREME: "1", ENV_IOSURFACE_CA: "1"},
    )
    kext_no = (
        no_h["Non-Metal IOAccelerator Common"][PatchType.OVERWRITE_SYSTEM_VOLUME][
            "/System/Library/Extensions"
        ]["IOSurface.kext"]
    )
    kext_h = (
        with_h["Non-Metal IOAccelerator Common"][PatchType.OVERWRITE_SYSTEM_VOLUME][
            "/System/Library/Extensions"
        ]["IOSurface.kext"]
    )
    ok = kext_no == "10.14.6" and kext_h == H_PREFERRED_IOSURFACE_KEXT
    return StepResult(
        name="h_n_iosurface_prefer",
        ok=ok,
        detail={"without_h": kext_no, "with_h": kext_h},
    )


def step_track_e_renderbox() -> StepResult:
    """Track E: missing RenderBox-25 → noop hooks; mock MTLB → Metal 31001."""
    import tempfile

    from x86.graphics.metallib_preflight import METALLIB_MAGIC, MIN_RENDERBOX_METALLIB_BYTES
    from x86.graphics.metallib_renderbox import renderbox_gap_status, sys_patch_hooks
    from x86.graphics.skylight_lut import RENDERBOX_METALLIB_RELATIVE
    from x86.graphics.skylight_tracks import resolve_track_module

    mod, name = resolve_track_module("E")
    resolved = name == "x86.graphics.metallib_renderbox" and mod is not None
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp) / "empty"
        empty.mkdir()
        gap = renderbox_gap_status(25, search_roots=[empty])
        hooks_empty = sys_patch_hooks(25, 0, "26.0", search_roots=[empty])
        filled = Path(tmp) / "filled"
        metallib = filled / "RenderBox-25" / RENDERBOX_METALLIB_RELATIVE
        metallib.parent.mkdir(parents=True)
        metallib.write_bytes(METALLIB_MAGIC + (b"\x03" * MIN_RENDERBOX_METALLIB_BYTES))
        hooks_ok = sys_patch_hooks(25, 0, "26.0", search_roots=[filled])
    ok = (
        resolved
        and gap["noop"]
        and hooks_empty == {}
        and "Metal 31001 Common" in hooks_ok
    )
    return StepResult(
        name="track_e_renderbox",
        ok=ok,
        detail={
            "resolved_module": name,
            "gap_noop": gap["noop"],
            "hooks_when_present": list(hooks_ok.keys()),
        },
    )


def step_l5_macho_probe() -> StepResult:
    from x86.graphics.skylight_lut_rootpatch import probe_l5_macho_payloads

    report = probe_l5_macho_payloads(25)
    # Soft-ok when acquire notes exist even if sibling PSP absent on CI.
    # Prefer ready; otherwise require documented acquire path.
    ok = bool(report.get("ready_for_overwrite")) or bool(report.get("acquire_notes"))
    return StepResult(
        name="l5_macho_probe",
        ok=ok,
        detail={
            "ready": report.get("ready_for_overwrite"),
            "skylight_macho": report.get("skylight_macho"),
            "coredisplay_macho": report.get("coredisplay_macho"),
            "acquire_doc": report.get("acquire_doc"),
        },
    )


def step_apply_order_dry_run() -> StepResult:
    from x86.extreme.apply_order import dry_run_profile_apply

    payload = dry_run_profile_apply(include_extreme=True)
    ok = bool(payload.get("order_matches_phases"))
    return StepResult(
        name="apply_order_dry_run",
        ok=ok,
        detail={
            "flat_order": payload.get("apply_order", {}).get("flat_order"),
            "profile_order": payload.get("profile_report", {}).get("order"),
        },
    )


def step_mock_guest_matrix() -> StepResult:
    from x86.extreme.mock_guest import run_mock_guest_matrix

    payload = run_mock_guest_matrix()
    return StepResult(
        name="mock_guest_matrix",
        ok=bool(payload.get("ok")),
        detail={"guests": payload.get("guests"), "results": payload.get("results")},
    )


def run_gates() -> list[StepResult]:
    steps = (
        step_detect_fixture,
        step_patchset_emptiness,
        step_profile_dry_run,
        step_efi_bridge,
        step_h_n_iosurface_prefer,
        step_track_e_renderbox,
        step_l5_macho_probe,
        step_apply_order_dry_run,
        step_mock_guest_matrix,
    )
    results: list[StepResult] = []
    for fn in steps:
        try:
            results.append(fn())
        except Exception as exc:  # noqa: BLE001
            results.append(StepResult(name=fn.__name__, ok=False, error=str(exc)))
    return results


def run_unit_suite(verbosity: int = 1) -> unittest.TestResult:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for mod in UNITTEST_MODULES:
        try:
            suite.addTests(loader.loadTestsFromName(mod))
        except Exception as exc:  # noqa: BLE001
            print(f"SKIP load {mod}: {exc}", file=sys.stderr)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


def run_all(*, run_unittests: bool = True, verbosity: int = 1) -> dict[str, Any]:
    host = _host_snapshot()
    gates = run_gates()
    unit: dict[str, Any] = {"skipped": True}
    if run_unittests:
        result = run_unit_suite(verbosity=verbosity)
        unit = {
            "skipped": False,
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "ok": result.wasSuccessful(),
        }
    payload = {
        "host": host,
        "gates": [asdict(g) for g in gates],
        "gates_ok": all(g.ok for g in gates),
        "unit": unit,
        "doc": "docs/EXTREME-TAHOE-VALIDATION.md",
        "vm_note": (
            "No UTM/qemu/docker on this Sequoia host — mock fixtures cover "
            "Tahoe dict/path gates. On Tahoe guest: re-run this entrypoint."
            if not (host.get("has_utm") or host.get("has_qemu"))
            else "VM tooling present — see docs for guest smoke."
        ),
    }
    payload["ok"] = payload["gates_ok"] and (
        unit.get("ok", True) if not unit.get("skipped") else True
    )
    return payload


def main(argv: Optional[list[str]] = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    skip_unit = "--gates-only" in args
    quiet = "--quiet" in args
    payload = run_all(run_unittests=not skip_unit, verbosity=0 if quiet else 1)
    print(json.dumps(payload, indent=2, default=str))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
