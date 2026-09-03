#!/usr/bin/env python3
"""
This-Mac EFI optimize helper (MacPro5,1 flashed → MacPro7,1 SMBIOS).

Mutates an OpenCore config.plist / staging tree:
  - Track K: agdpmod/shikigva, RestrictEvents + revpatch=jsc (Safari26-PreAVX)
  - Flashed Mac Pro: -no_compat_check (efi_builder/smbios.py convention)
  - Performance: serverperfmode=1, CFG locks, ForceBoost, TscSync, SimpleMSR
  - Debug: Misc.Debug Target=0x43 file+console logging

Does not mount disks or reboot. See docs/EFI-OPTIMIZE-THIS-MAC.md.
"""

from __future__ import annotations

import argparse
import plistlib
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

APPLE_NVRAM = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
OCLP_NVRAM = "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"

PERF_ARGS = (
    "keepsyms=1",
    "debug=0x100",
    "serverperfmode=1",
    "npci=0x2000",
    "-v",
    "-no_compat_check",  # smbios.py when model == override_smbios (flashed 7,1)
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        data = plistlib.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} root must be dict")
    return data


def _save(path: Path, config: dict[str, Any]) -> None:
    with path.open("wb") as handle:
        plistlib.dump(config, handle)


def _ensure_boot_args(boot: str, required: tuple[str, ...]) -> str:
    tokens = list(boot.split()) if boot else []
    for arg in required:
        key = arg.split("=", 1)[0]
        if arg.startswith("-") and "=" not in arg:
            # normalize no_compat_check → -no_compat_check
            tokens = [t for t in tokens if t.lstrip("-") != arg.lstrip("-")]
            tokens.append(arg)
            continue
        out: list[str] = []
        replaced = False
        for t in tokens:
            if t.split("=", 1)[0] == key:
                if not replaced:
                    out.append(arg)
                    replaced = True
                continue
            out.append(t)
        if not replaced:
            out.append(arg)
        tokens = out
    # de-dupe -no_compat_check
    cleaned: list[str] = []
    seen_ncc = False
    for t in tokens:
        if t.lstrip("-") == "no_compat_check":
            if seen_ncc:
                continue
            cleaned.append("-no_compat_check")
            seen_ncc = True
        else:
            cleaned.append(t)
    if not seen_ncc:
        cleaned.append("-no_compat_check")
    return " ".join(cleaned)


def _ensure_kext(
    config: dict[str, Any],
    bundle: str,
    *,
    comment: str,
    arch: str = "Any",
    min_kernel: str = "8.0.0",
) -> None:
    add = config.setdefault("Kernel", {}).setdefault("Add", [])
    if not isinstance(add, list):
        raise TypeError("Kernel.Add must be list")
    exe = bundle[: -len(".kext")] if bundle.endswith(".kext") else bundle
    for entry in add:
        if isinstance(entry, dict) and entry.get("BundlePath") == bundle:
            entry["Enabled"] = True
            entry.setdefault("Arch", arch)
            entry.setdefault("MaxKernel", "")
            entry.setdefault("MinKernel", min_kernel)
            entry.setdefault("ExecutablePath", f"Contents/MacOS/{exe}")
            entry.setdefault("PlistPath", "Contents/Info.plist")
            return
    add.append(
        {
            "Arch": arch,
            "BundlePath": bundle,
            "Comment": comment,
            "Enabled": True,
            "ExecutablePath": f"Contents/MacOS/{exe}",
            "MaxKernel": "",
            "MinKernel": min_kernel,
            "PlistPath": "Contents/Info.plist",
        }
    )


def _replace_tree(src: Path, dest: Path) -> None:
    """Replace dest with src; tolerate root-owned ESP copies via rename fallback."""
    if dest.exists():
        try:
            shutil.rmtree(dest)
        except PermissionError:
            bak = dest.with_name(dest.name + ".bak-old")
            if bak.exists():
                shutil.rmtree(bak, ignore_errors=True)
            dest.rename(bak)
            try:
                shutil.rmtree(bak)
            except OSError:
                pass
    shutil.copytree(src, dest)


def _install_restrictevents(kexts_dir: Path) -> str:
    from x86.patch.safari26_preavx import KEXT_VERSION, kext_zip_path, payload_dir

    src_tree = payload_dir() / "RestrictEvents.kext"
    dest = kexts_dir / "RestrictEvents.kext"
    if src_tree.is_dir():
        _replace_tree(src_tree, dest)
        return KEXT_VERSION
    zip_path = kext_zip_path()
    if not zip_path.is_file():
        return "missing"
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)
        found = next(Path(tmp).rglob("RestrictEvents.kext"), None)
        if found is None:
            return "missing"
        _replace_tree(found, dest)
    return KEXT_VERSION


def _install_simplemsr(kexts_dir: Path) -> bool:
    zip_path = REPO / "payloads" / "Kexts" / "Misc" / "SimpleMSR-v1.0.0.zip"
    if not zip_path.is_file():
        return False
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)
        found = next(Path(tmp).rglob("SimpleMSR.kext"), None)
        if found is None:
            return False
        _replace_tree(found, kexts_dir / "SimpleMSR.kext")
    return True


def apply_optimize(config: dict[str, Any], *, kexts_dir: Optional[Path] = None) -> dict[str, Any]:
    from x86.profiles.macpro5_vega64_tahoe import (
        apply_efi_agdpmod,
        apply_efi_kdkless,
        apply_efi_restrictevents,
    )

    agdp = apply_efi_agdpmod(config)
    kdk = apply_efi_kdkless(config)
    re_step = apply_efi_restrictevents(config)

    apple = config.setdefault("NVRAM", {}).setdefault("Add", {}).setdefault(APPLE_NVRAM, {})
    apple["boot-args"] = _ensure_boot_args(str(apple.get("boot-args") or ""), PERF_ARGS)

    kq = config.setdefault("Kernel", {}).setdefault("Quirks", {})
    kq["AppleCpuPmCfgLock"] = True
    kq["AppleXcpmCfgLock"] = True
    kq["AppleXcpmForceBoost"] = True
    kq["ProvideCurrentCpuInfo"] = True
    kq["PanicNoKextDump"] = True

    uefi_q = config.setdefault("UEFI", {}).setdefault("Quirks", {})
    if int(uefi_q.get("TscSyncTimeout") or 0) == 0:
        uefi_q["TscSyncTimeout"] = 500000

    dbg = config.setdefault("Misc", {}).setdefault("Debug", {})
    dbg["AppleDebug"] = True
    dbg["ApplePanic"] = True
    dbg["Target"] = 0x43
    dbg["DisplayLevel"] = 0x80000042
    dbg["LogModules"] = "*"

    boot_misc = config.setdefault("Misc", {}).setdefault("Boot", {})
    boot_misc["ShowPicker"] = True
    boot_misc["Timeout"] = max(int(boot_misc.get("Timeout") or 0), 8)
    boot_misc["PollAppleHotKeys"] = True

    re_ver = None
    simplemsr = False
    if kexts_dir is not None:
        kexts_dir.mkdir(parents=True, exist_ok=True)
        re_ver = _install_restrictevents(kexts_dir)
        simplemsr = _install_simplemsr(kexts_dir)
        if simplemsr:
            _ensure_kext(
                config,
                "SimpleMSR.kext",
                comment="this-mac: disable firmware MSR throttling (SimpleMSR)",
            )

    oclp = config.setdefault("NVRAM", {}).setdefault("Add", {}).setdefault(OCLP_NVRAM, {})
    return {
        "boot-args": apple.get("boot-args"),
        "revpatch": oclp.get("revpatch"),
        "no_compat_check": "-no_compat_check" in str(apple.get("boot-args") or ""),
        "restrictevents": re_ver,
        "simplemsr": simplemsr,
        "steps": {
            "agdp": agdp.status,
            "kdkless": kdk.status,
            "restrictevents": re_step.status,
            "restrictevents_detail": re_step.detail,
        },
        "debug_target": dbg.get("Target"),
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Path to config.plist to mutate in place")
    parser.add_argument("--stage", type=Path, help="Staging root containing EFI/OC/")
    parser.add_argument(
        "--from-backup",
        type=Path,
        help="Copy EFI (+System) from backup into --stage before mutate",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    stage = args.stage
    if args.from_backup:
        if stage is None:
            parser.error("--from-backup requires --stage")
        stage.mkdir(parents=True, exist_ok=True)
        src_efi = args.from_backup / "EFI"
        if not src_efi.is_dir():
            print(f"missing {src_efi}", file=sys.stderr)
            return 2
        if (stage / "EFI").exists():
            shutil.rmtree(stage / "EFI")
        shutil.copytree(src_efi, stage / "EFI")
        src_sys = args.from_backup / "System"
        if src_sys.is_dir():
            if (stage / "System").exists():
                shutil.rmtree(stage / "System")
            shutil.copytree(src_sys, stage / "System")
        boot_dir = stage / "EFI" / "BOOT"
        boot_dir.mkdir(parents=True, exist_ok=True)
        oc = stage / "EFI" / "OC" / "OpenCore.efi"
        if oc.is_file():
            shutil.copy2(oc, boot_dir / "BOOTx64.efi")

    cfg = args.config
    if cfg is None and stage is not None:
        cfg = stage / "EFI" / "OC" / "config.plist"
    if cfg is None or not cfg.is_file():
        parser.error("need --config or --stage with EFI/OC/config.plist")

    config = _load(cfg)
    kexts = cfg.parent / "Kexts"
    report = apply_optimize(config, kexts_dir=kexts if kexts.is_dir() or stage else None)
    _save(cfg, config)

    if args.json:
        import json

        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Wrote", cfg)
        for key, value in report.items():
            print(f"  {key}: {value}")
    return 0 if report.get("no_compat_check") else 3


if __name__ == "__main__":
    raise SystemExit(main())
