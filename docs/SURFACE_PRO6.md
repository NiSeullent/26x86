# Surface Pro 6 (i5-8250U) / macOS Tahoe

This target prepares and validates a Surface-specific EFI on Windows, macOS or
Linux. Root patching runs on the installed macOS only. A successful static check
or GUI test is not proof of boot, graphics acceleration, sleep, touch or audio on
the physical Surface.

Select **Surface Pro 6 · Tahoe** on the wizard's first page. The preparation page
accepts the complete EFI directory and checks enabled file references, required
kexts, Lilu plugin ordering, framebuffer configuration and root patch settings.
The GUI deliberately blocks the generic Mac EFI builder and installer for this
target; keep the Surface ACPI and USB map supplied with the dedicated EFI.

```sh
python -m x86 wizard
python -m x86 surface --efi /path/to/EFI --json
```

Windows: use `26x86.exe` from the Windows build, or install `requests packaging
markdown2 pywebview` and run the source command. Microsoft Edge WebView2 Runtime
is required. Linux: install the same Python packages plus GTK/WebKitGTK and
PyGObject for pywebview's GTK backend, or `PySide6 qtpy` for its Qt backend.
macOS: install the repository's `requirements.txt` for native hardware probes and
the existing wx root patch interface; Cocoa WebKit is the default fallback.
Python 3.13 is used by CI. The Windows GUI was additionally exercised on 3.10.

## Graphics, network and audio policy

The i5-8250U supports AVX2. UHD 620 uses the Kaby Lake driver path with Lilu and
WhateverGreen (Surface framebuffer `0x59160000`, plist data `00001659`, device
spoof `0x5916`, data `16590000`). This profile does not apply legacy GPU,
pre-AVX, Metal 3802, RenderBox or metallib root patches. Validate actual Metal
acceleration after boot; do not select unrelated old-Mac graphics patches.

The stock Marvell wireless adapter is not supported by Intel/Broadcom kexts.
Android RNDIS USB tethering uses HoRNDIS in the supplied EFI. Enable USB tethering
on the phone after attaching it; Ethernet-like service creation and actual
connectivity still require hardware testing.

Tahoe removed AppleHDA after its first beta. 26x86's existing **Modern Audio**
patchset restores `26.0 Beta 1/System/Library/Extensions/AppleHDA.kext` and requires
a compatible Kernel Debug Kit. AppleALC and the Surface codec layout remain EFI
configuration. Restoring AppleHDA alone does not prove the speakers/microphone
work. A spoofed MacBookPro15,2 SMBIOS is not evidence of a physical T2 chip.

## Prepare the root patch payload

The NiSeullent support-package fork has source but no published release assets as
of the synchronization. The pinned published upstream fallback is
[hackdoc/PatcherSupportPkg 1.11.6](https://github.com/hackdoc/PatcherSupportPkg/releases/tag/1.11.6).
Place its `Universal-Binaries.dmg` inside this repository's `payloads` directory,
or supply `--payload-dir` pointing at a copy of the complete payloads directory.
Do not point `--payload-dir` at only an AppleHDA extraction: the engine also uses
the repository's supporting tools and resources.

- DMG size: 757652992 bytes.
- SHA-256: `2e99fb8db4ce21924c1a04669efd32954adba0df7eaa27cc6f8b9a31f7022943`.
- The download was verified against the upstream release's `sha256sum.txt`.
- Source payload inspection confirms AppleHDA version 600.2. The encrypted DMG
  itself requires macOS hdiutil; its mounted contents were not inspected on Windows.

The KDK must match the installed Tahoe build as selected/validated by the existing
patch engine. Keep tethering available for its KDK download. No Tahoe metallib
package is required for this Surface graphics path.

## Apply on the installed Tahoe

Boot the Surface EFI first. The root patch configuration needs SIP bits `0x803`,
`SecureBootModel=Disabled`, AMFIPass and AppleALC. A file check cannot establish the
live SIP/AMFI state: changing config.plist does not itself change an already
running macOS environment.

```sh
python -m x86 patch --profile surface-pro6-i5-tahoe --preflight --json
sudo .venv/bin/python -m x86 patch --profile surface-pro6-i5-tahoe --apply --json
```

The default `patch` command only checks prerequisites. `--auto` alone does not
authorize writes; `--apply` is explicit. The live CPU must report i5-8250U and the
GPU must report the expected Intel Kaby Lake identifiers. The profile stops if
the installed OS is not Darwin 25 or if anything beyond Modern Audio is detected.
SIP, AMFI, FileVault, network and security checks come from the real patch engine;
there is no VMware bypass. Missing payloads, incompatible security settings and
pending OS updates fail rather than report success.

The GUI's patch button opens the existing native root patch workflow on macOS.
It never patches an offline APFS volume from Windows/Linux. The CLI calls
`PatchSysVolume.start_patch`, mounts APFS through the engine, rebuilds kernel
collections and creates the new boot snapshot. `patched_reboot_required` is
returned only on explicit engine completion. Reboot and verify audio/Metal on the
device. The GUI's revert action uses the engine's APFS snapshot rollback.

## Verification scope

Automated checks cover preparation imports, HTTP bridge isolation, missing EFI
files, path escapes, CPU/GPU target mismatch, and root engine failure reporting.
The three-OS CI matrix does not apply root patches. No physical Surface boot or
APFS patch operation was performed in the Windows development environment.

Upstream references: [WhateverGreen Intel FAQ](https://github.com/acidanthera/WhateverGreen/blob/master/Manual/FAQ.IntelHD.en.md),
[26x86 Modern Audio implementation](../opencore_legacy_patcher/sys_patch/patchsets/hardware/misc/modern_audio.py),
[upstream OCLP-T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2).
