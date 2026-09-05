"""Read-only preparation for the Surface Pro 6 i5 Tahoe target.

An EFI validation is never evidence that macOS booted. This module deliberately
does not use OCLP's Mac EFI builder: Surface ACPI and USB maps belong to its EFI.
"""

from __future__ import annotations

import hashlib
import plistlib
from pathlib import Path
from typing import Any

PROFILE_ID = "surface-pro6-i5-tahoe"
APPLE_NVRAM_GUID = "7C436110-AB2A-4BBB-A880-FE41995C9F82"


def profile_info() -> dict[str, Any]:
    return {
        "id": PROFILE_ID,
        "title": "Surface Pro 6 · i5-8250U · macOS Tahoe",
        "cpu": "Intel Core i5-8250U", "gpu": "Intel UHD 620",
        "target_darwin": 25, "network": "Android USB tethering; Marvell Wi-Fi unsupported",
        "graphics_policy": "Use the native Kaby Lake driver with WhateverGreen; no legacy GPU root patches.",
        "root_patch": "Modern Audio (AppleHDA), when detected on installed Tahoe; KDK required.",
        "hardware_verified": False,
        "instructions": "Preserve the Surface EFI. Run root preflight on the installed macOS before patching.",
    }


def validate_efi(path: str | Path) -> dict[str, Any]:
    """Validate a complete EFI directory without writing it or mounting disks."""
    root = Path(path).expanduser().resolve()
    if (root / "EFI" / "OC" / "config.plist").is_file():
        root /= "EFI"
    errors, warnings = [], []
    config_path = root / "OC" / "config.plist"
    report = {"profile": profile_info(), "efi_path": str(root), "errors": errors,
              "warnings": warnings, "hardware_verified": False, "root_patch_ready": False}
    try:
        raw = config_path.read_bytes()
        config = plistlib.loads(raw)
        if not isinstance(config, dict):
            raise ValueError("config.plist must contain a dictionary")
    except (OSError, ValueError, plistlib.InvalidFileException) as exc:
        errors.append(f"Cannot read OpenCore config: {exc}")
        return {**report, "ok": False}
    report["config_sha256"] = hashlib.sha256(raw).hexdigest()

    def required_file(relative: str) -> None:
        target = (root / relative).resolve()
        if not target.is_relative_to(root):
            errors.append(f"Path escapes EFI directory: {relative}")
        elif not target.is_file():
            errors.append(f"Missing EFI file: {relative}")

    required_file("BOOT/BOOTx64.efi")
    required_file("OC/OpenCore.efi")
    try:
        additions = [row for row in config["Kernel"]["Add"] if row.get("Enabled")]
        names = [row["BundlePath"] for row in additions]
        for row in additions:
            base = "OC/Kexts/" + row["BundlePath"] + "/"
            required_file(base + row["PlistPath"])
            if row.get("ExecutablePath"):
                required_file(base + row["ExecutablePath"])
        for row in config["ACPI"]["Add"]:
            if row.get("Enabled"):
                required_file("OC/ACPI/" + row["Path"])
        for row in config["UEFI"]["Drivers"]:
            if row.get("Enabled"):
                required_file("OC/Drivers/" + row["Path"])
        for required in ("Lilu.kext", "WhateverGreen.kext", "VirtualSMC.kext", "AppleALC.kext"):
            if required not in names:
                errors.append(f"Required enabled kext missing: {required}")
        if "Lilu.kext" in names:
            for plugin in ("WhateverGreen.kext", "AppleALC.kext"):
                if plugin in names and names.index(plugin) < names.index("Lilu.kext"):
                    errors.append(f"Lilu must load before {plugin}")
        if "HoRNDIS.kext" not in names:
            warnings.append("HoRNDIS is not enabled; Android RNDIS tethering may be unavailable.")
        if any("itlwm" in name.lower() or "airportbrcm" in name.lower() for name in names):
            warnings.append("Intel/Broadcom wireless drivers cannot drive the stock Marvell adapter.")
        gpu = config["DeviceProperties"]["Add"].get("PciRoot(0x0)/Pci(0x2,0x0)", {})
        if gpu.get("AAPL,ig-platform-id") != bytes.fromhex("00001659"):
            warnings.append("Expected Surface Kaby Lake framebuffer 0x59160000 (data 00001659); verify display mapping.")
        if gpu.get("device-id") != bytes.fromhex("16590000"):
            warnings.append("Expected UHD 620 device spoof 0x5916 (data 16590000).")
        nvram = config["NVRAM"]["Add"].get(APPLE_NVRAM_GUID, {})
        csr = nvram.get("csr-active-config", b"\0\0\0\0")
        sip = int.from_bytes(csr, "little") if isinstance(csr, bytes) else 0
        secure_boot = config["Misc"]["Security"].get("SecureBootModel")
        report["root_patch_ready"] = (sip & 0x803) == 0x803 and secure_boot == "Disabled" and "AMFIPass.kext" in names
        if not report["root_patch_ready"]:
            warnings.append("Root patch profile needs SIP bits 0x803, SecureBootModel Disabled and AMFIPass. Runtime validation is still required.")
        report["smbios"] = config["PlatformInfo"]["Generic"].get("SystemProductName")
        report["enabled_kexts"] = names
    except (KeyError, TypeError, AttributeError) as exc:
        errors.append(f"Invalid or incomplete OpenCore structure: {exc}")
    return {**report, "ok": not errors}


def configure_surface_constants(constants) -> None:
    """Require live CPU/GPU evidence before applying a manually selected target."""
    computer = constants.computer
    cpu_name = str(getattr(getattr(computer, "cpu", None), "name", ""))
    if "i5-8250U" not in cpu_name:
        raise ValueError("Surface target requires a live i5-8250U CPU probe; SMBIOS alone is insufficient.")
    if not any(getattr(gpu, "vendor_id", None) == 0x8086 and getattr(gpu, "device_id", None) in (0x5916, 0x5917, 0x591E)
               for gpu in (getattr(computer, "gpus", None) or [])):
        raise ValueError("Surface target requires an Intel UHD 620/Kaby Lake GPU probe.")
    constants.host_is_hackintosh = True
    constants.allow_vmware_root_patching = False
    constants.allow_modern_audio = True
    # MacBookPro15,2 SMBIOS is not evidence of Apple's physical T2 hardware.
    computer.t2_chip = False
