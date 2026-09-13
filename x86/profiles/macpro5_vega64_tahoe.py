"""
MacPro5,1 pre-AVX + RX Vega 64 → macOS Tahoe E2E profile (Track K).

Fixed order:
  1) EFI — agdpmod / shikigva / KDKlessWorkaround / RestrictEvents + revpatch=jsc
  2) Root — AMD Vega + Tahoe Yellow Screen Mitigations
  3) Extreme (opt-in) — H/I/J/L hooks when present

CLI (Track K owned, does not patch x86/cli.py):
  python -m x86.profiles apply macpro5-vega64-tahoe
  python -m x86.profiles.macpro5_vega64_tahoe apply
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

from x86.graphics.yellow_screen import (
    TAHOE_YELLOW_SCREEN_PATCH_NAME,
    yellow_screen_mitigations,
)
from x86.patch.safari26_preavx import (
    KEXT_VERSION as SAFARI26_RE_VERSION,
    merge_jsc_tokens,
    payload_available as safari26_payload_available,
)
from x86.profiles.base import (
    HardwareProfile,
    Phase,
    ProfileStep,
    StepResult,
    extreme_enabled,
)

PROFILE_ID = "macpro5-vega64-tahoe"
PROFILE_MODEL = "MacPro5,1"
PROFILE_GPU_FAMILY = "vega"
VEGA64_DEVICE_ID = 0x687F
TAHOE_XNU_MAJOR = 25
OCLP_NVRAM_UUID = "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"
DOCS_RELATIVE = "docs/profiles/MacPro5-Vega64-Tahoe.md"

_logger = logging.getLogger(__name__)


def _steps() -> tuple[ProfileStep, ...]:
    return (
        ProfileStep(
            id="efi.agdpmod_shikigva",
            phase=Phase.EFI,
            title="WhateverGreen agdpmod/shikigva",
            description="DeviceProperties + boot-args fallback for Tahoe AGDC yellow mitigation.",
            owns=("opencore_legacy_patcher/efi_builder/gcn_agdp.py",),
        ),
        ProfileStep(
            id="efi.kdkless",
            phase=Phase.EFI,
            title="KDKlessWorkaround.kext",
            description="MTL gap WindowServer spin workaround for Mac Pro sockets.",
            owns=("opencore_legacy_patcher/efi_builder/graphics_audio.py",),
        ),
        ProfileStep(
            id="efi.restrictevents_jsc",
            phase=Phase.EFI,
            title="RestrictEvents + revpatch=jsc",
            description=(
                f"Safari26-PreAVX RestrictEvents {SAFARI26_RE_VERSION} + revpatch jsc."
            ),
            owns=("x86/patch/safari26_preavx.py",),
        ),
        ProfileStep(
            id="root.amd_vega",
            phase=Phase.ROOT,
            title="AMD Vega root kexts (Metal 31001)",
            description="amd_vega.py overwrite set after EFI reboot.",
            owns=("opencore_legacy_patcher/sys_patch/patchsets/hardware/graphics/amd_vega.py",),
        ),
        ProfileStep(
            id="root.yellow_mitigations",
            phase=Phase.ROOT,
            title=TAHOE_YELLOW_SCREEN_PATCH_NAME,
            description="WS cache / ColorSync / PSP prefer / optional RenderBox.",
            owns=("x86/graphics/yellow_screen.py",),
        ),
        ProfileStep(
            id="extreme.hooks",
            phase=Phase.EXTREME,
            title="Extreme compositor / AVX graphics hooks",
            description="Track H/I/J/L hooks; requires X86_EXTREME=1 or --extreme.",
            required=False,
            extreme_only=True,
            owns=("x86/profiles/extreme_interpose_link.py", "x86/graphics/interpose_apply.py"),
        ),
    )


def build_profile() -> HardwareProfile:
    mitigations = yellow_screen_mitigations(
        PROFILE_MODEL,
        gpu_archs=["Vega", "RX Vega 64", "0x687F"],
        xnu_major=TAHOE_XNU_MAJOR,
        cpu_generation=4,
    )
    return HardwareProfile(
        id=PROFILE_ID,
        title="MacPro5,1 pre-AVX + Vega 64 → Tahoe",
        model=PROFILE_MODEL,
        gpu_family=PROFILE_GPU_FAMILY,
        gpu_device_ids=(VEGA64_DEVICE_ID,),
        target_xnu_major=TAHOE_XNU_MAJOR,
        requires_pre_avx=True,
        steps=_steps(),
        docs=DOCS_RELATIVE,
        notes=(
            "실기: 플래시 MacPro(5,1급), AVX 없음, RX Vega 64, Tahoe 목표.",
            "EFI 완료 후 루트패치 — 순서 역전 금지.",
            "Metal 3802 / Non-Metal Tahoe shared 가드는 기본 유지 (극한 옵트인만).",
            f"yellow_screen_mitigations: {', '.join(mitigations)}",
        ),
    )


PROFILE = build_profile()


def _ensure_kext_entry(
    config: dict[str, Any],
    *,
    bundle_path: str,
    enabled: bool = True,
    comment: str = "",
) -> bool:
    kernel = config.setdefault("Kernel", {})
    add = kernel.setdefault("Add", [])
    if not isinstance(add, list):
        raise TypeError("Kernel.Add must be a list")
    for entry in add:
        if isinstance(entry, dict) and entry.get("BundlePath") == bundle_path:
            if entry.get("Enabled") is not True and enabled:
                entry["Enabled"] = True
                return True
            return False
    executable = bundle_path[: -len(".kext")] if bundle_path.endswith(".kext") else bundle_path
    add.append(
        {
            "BundlePath": bundle_path,
            "Enabled": enabled,
            "Comment": comment or bundle_path,
            "ExecutablePath": f"Contents/MacOS/{executable}",
            "PlistPath": "Contents/Info.plist",
        }
    )
    return True


def apply_efi_agdpmod(config: dict[str, Any]) -> StepResult:
    from opencore_legacy_patcher.efi_builder.gcn_agdp import (
        apply_gcn_agdp_fallbacks,
        config_has_agdpmod,
    )

    before = config_has_agdpmod(config)
    apply_gcn_agdp_fallbacks(config)
    return StepResult(
        step_id="efi.agdpmod_shikigva",
        status="applied" if (not before or config_has_agdpmod(config)) else "error",
        detail="agdpmod/shikigva DeviceProperties + boot-args fallback",
        mutations={"agdpmod": True, "shikigva": True},
    )


def apply_efi_kdkless(config: dict[str, Any]) -> StepResult:
    changed = _ensure_kext_entry(
        config,
        bundle_path="KDKlessWorkaround.kext",
        comment="Track K: Mac Pro socket MTL-gap WindowServer workaround",
    )
    return StepResult(
        step_id="efi.kdkless",
        status="applied" if changed else "planned",
        detail="KDKlessWorkaround.kext enabled in Kernel.Add",
        mutations={"KDKlessWorkaround.kext": True},
    )


def apply_efi_restrictevents(config: dict[str, Any]) -> StepResult:
    present = safari26_payload_available()
    changed = _ensure_kext_entry(
        config,
        bundle_path="RestrictEvents.kext",
        comment=f"Safari26-PreAVX-Fix RestrictEvents {SAFARI26_RE_VERSION}",
    )
    nvram = config.setdefault("NVRAM", {}).setdefault("Add", {})
    oclp = nvram.setdefault(OCLP_NVRAM_UUID, {})
    existing = str(oclp.get("revpatch", "") or "")
    tokens = [t for t in existing.split(",") if t]
    merged = merge_jsc_tokens(tokens if tokens else ["sbvmm"])
    new_value = ",".join(merged)
    rev_changed = oclp.get("revpatch") != new_value
    oclp["revpatch"] = new_value
    status = "applied" if (changed or rev_changed) else ("planned" if present else "blocked")
    detail = f"RestrictEvents {SAFARI26_RE_VERSION} + revpatch={new_value}"
    if not present:
        detail += "; Safari26 payload zip missing"
    return StepResult(
        step_id="efi.restrictevents_jsc",
        status=status,
        detail=detail,
        mutations={
            "RestrictEvents.kext": True,
            "revpatch": new_value,
            "safari26_payload_present": present,
            "kext_version": SAFARI26_RE_VERSION,
        },
    )


def plan_root_vega() -> StepResult:
    return StepResult(
        step_id="root.amd_vega",
        status="planned",
        detail="Root patchset 'AMD Vega' (Metal 31001) after EFI reboot",
        mutations={"patch_name": "AMD Vega"},
    )


def plan_root_yellow() -> StepResult:
    items = yellow_screen_mitigations(
        PROFILE_MODEL,
        gpu_archs=["Vega", "0x687F"],
        xnu_major=TAHOE_XNU_MAJOR,
        cpu_generation=4,
    )
    return StepResult(
        step_id="root.yellow_mitigations",
        status="planned",
        detail=f"{TAHOE_YELLOW_SCREEN_PATCH_NAME}: {', '.join(items)}",
        mutations={"patch_name": TAHOE_YELLOW_SCREEN_PATCH_NAME, "mitigations": items},
    )



ENV_X86_EXTREME = "X86_EXTREME"
ENV_X86_EXTREME_INSTALL = "X86_EXTREME_INSTALL"


@contextmanager
def _ensure_extreme_env(*, enabled: bool):
    """inject X86_EXTREME for interpose_apply gate when --extreme only."""
    if not enabled:
        yield
        return
    previous = os.environ.get(ENV_X86_EXTREME)
    os.environ[ENV_X86_EXTREME] = "1"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(ENV_X86_EXTREME, None)
        else:
            os.environ[ENV_X86_EXTREME] = previous


def _live_library_requested(environ: Optional[dict[str, str]] = None) -> bool:
    env = environ if environ is not None else os.environ
    value = str(env.get(ENV_X86_EXTREME_INSTALL, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def run_interpose_apply(
    *,
    enabled: bool,
    dry_run: bool = False,
    environ: Optional[dict[str, str]] = None,
    repo_root: Optional[Path] = None,
) -> StepResult:
    """Track K extreme → Track I apply_live (98e2528 / INTEGRATE 52f7298)."""
    if not enabled:
        return StepResult(
            step_id="extreme.hooks",
            status="skipped",
            detail="X86_EXTREME / --extreme not set — interpose_apply not called",
            mutations={"interpose_apply": False},
        )
    live = _live_library_requested(environ)
    if dry_run:
        return StepResult(
            step_id="extreme.hooks",
            status="planned",
            detail=(
                "[dry-run] would call interpose_apply.apply_extreme_interpose "
                f"(live_library_plugins={live})"
            ),
            mutations={
                "interpose_apply": True,
                "dry_run": True,
                "live_library_plugins": live,
                "integrate": "52f7298+98e2528",
            },
        )
    try:
        from x86.graphics.interpose_apply import apply_extreme_interpose
    except ImportError as exc:
        return StepResult(
            step_id="extreme.hooks",
            status="blocked",
            detail=f"interpose_apply import failed: {exc}",
            mutations={"interpose_apply": False},
        )
    with _ensure_extreme_env(enabled=True):
        report = apply_extreme_interpose(
            repo_root=repo_root,
            live_library_plugins=live,
        )
    applied = bool(report.get("applied"))
    blocked = report.get("blocked_reason")
    if blocked and not applied:
        status, detail = "blocked", f"interpose_apply blocked: {blocked}"
    elif applied:
        status = "applied"
        detail = (
            "interpose_apply: build→staging/SkyLightPlugins→APPLY-GUIDE "
            f"(live_library={live})"
        )
    else:
        status, detail = "planned", "interpose_apply ran but applied=False"
    return StepResult(
        step_id="extreme.hooks",
        status=status,
        detail=detail,
        mutations={
            "interpose_apply": True,
            "live_library_plugins": live,
            "report": {
                "applied": report.get("applied"),
                "blocked_reason": report.get("blocked_reason"),
                "guidance": report.get("guidance") or [],
                "steps_keys": list((report.get("steps") or {}).keys()),
                "recipe_keys": list((report.get("recipe") or {}).keys()),
            },
            "integrate": "52f7298+98e2528",
            "source": "x86.graphics.interpose_apply.apply_extreme_interpose",
        },
    )


def apply_extreme_hooks(
    *,
    enabled: bool,
    dry_run: bool = False,
    environ: Optional[dict[str, str]] = None,
) -> StepResult:
    """Extreme phase → Track I interpose_apply (profiles bridge)."""
    return run_interpose_apply(
        enabled=enabled,
        dry_run=dry_run,
        environ=environ,
    )


def apply_profile(
    *,
    config: Optional[dict[str, Any]] = None,
    dry_run: bool = False,
    include_extreme: bool = False,
    environ: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    extreme = extreme_enabled(environ=environ, flag=include_extreme)
    working = deepcopy(config) if config is not None else {}
    results: list[StepResult] = []

    for step in PROFILE.ordered_steps(include_extreme=extreme):
        if dry_run and step.phase == Phase.EFI:
            results.append(StepResult(step_id=step.id, status="planned", detail=f"[dry-run] {step.title}"))
            continue
        if step.id == "efi.agdpmod_shikigva":
            if config is None:
                results.append(StepResult(step_id=step.id, status="planned", detail="No config.plist — plan only"))
            else:
                results.append(apply_efi_agdpmod(working))
        elif step.id == "efi.kdkless":
            if config is None:
                results.append(StepResult(step_id=step.id, status="planned", detail="No config.plist — plan only"))
            else:
                results.append(apply_efi_kdkless(working))
        elif step.id == "efi.restrictevents_jsc":
            if config is None:
                results.append(StepResult(step_id=step.id, status="planned", detail="No config.plist — plan only"))
            else:
                results.append(apply_efi_restrictevents(working))
        elif step.id == "root.amd_vega":
            results.append(plan_root_vega())
        elif step.id == "root.yellow_mitigations":
            results.append(plan_root_yellow())
        elif step.id == "extreme.hooks":
            results.append(
                apply_extreme_hooks(
                    enabled=extreme,
                    dry_run=dry_run,
                    environ=environ,
                )
            )
        else:
            results.append(StepResult(step_id=step.id, status="error", detail="unknown step"))

    if config is not None and not dry_run:
        config.clear()
        config.update(working)

    return {
        "profile_id": PROFILE_ID,
        "model": PROFILE_MODEL,
        "gpu_family": PROFILE_GPU_FAMILY,
        "dry_run": dry_run,
        "extreme": extreme,
        "order": [r.step_id for r in results],
        "phases": ["efi", "root"] + (["extreme"] if extreme else []),
        "results": [r.as_dict() for r in results],
        "config_mutated": bool(config is not None and not dry_run),
        "docs": DOCS_RELATIVE,
        "profile": PROFILE.as_dict(include_extreme=extreme),
        "cli": "python -m x86.profiles apply macpro5-vega64-tahoe",
    }


def load_plist(path: Path) -> dict[str, Any]:
    import plistlib

    with path.open("rb") as handle:
        data = plistlib.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} root must be a dict")
    return data


def save_plist(path: Path, config: dict[str, Any]) -> None:
    import plistlib

    with path.open("wb") as handle:
        plistlib.dump(config, handle)


def apply_to_config_path(
    path: Path,
    *,
    dry_run: bool = False,
    include_extreme: bool = False,
) -> dict[str, Any]:
    config = load_plist(path)
    report = apply_profile(config=config, dry_run=dry_run, include_extreme=include_extreme)
    if not dry_run and report.get("config_mutated"):
        save_plist(path, config)
        _logger.info("Wrote Track K EFI mutations to %s", path)
    report["config_path"] = str(path)
    return report


def main(argv: Optional[list[str]] = None) -> int:
    """Thin alias — prefer ``python -m x86.profiles``."""
    from x86.profiles.__main__ import main as profiles_main

    return profiles_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
