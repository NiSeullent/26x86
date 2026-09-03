# This-Mac EFI Optimize (MacPro5,1 / Vega 64 / Sequoia)

한국어 + English. 실기: Fusion Drive (HDD + SSD), 플래시 MacPro7,1 SMBIOS / 실체 MacPro5,1급, Xeon X5675 pre-AVX, RX Vega 64.

## Disk map / 디스크 맵

| Role | Media (stable) | Typical BSD (can change!) | ESP |
|------|----------------|---------------------------|-----|
| Fusion HDD | ST1000DM003 1TB SATA | often `disk0` | `…s1` |
| Fusion SSD | INTEL SSDSA2M080G2GC 80GB | often `disk1`, or `disk2` if USB present | `…s1` ← **active OpenCore** |
| Fusion APFS | virtual (HDD+SSD slices) | synthesized | — |
| External USB | SanDisk / Passport / etc. | steals low `diskN` | **do not confuse with Fusion SSD** |

**Always match by Media Name**, never by bare `diskN` — plugging USB renumbers disks.

Live OpenCore is on the **Intel 80GB SSD ESP**; HDD ESP holds a recovery OpenCore copy after this optimize.

## Backup paths / 백업 경로 (absolute)

Original EFI (pre-optimize), timestamp `20260904-024355`:

- `/Volumes/Time Machine/EFI-BACKUP-20260904-024355/`
- `/Users/nyase/Desktop/EFI-BACKUP-20260904-024355/`

Optimized staging used for install:

- `/Users/nyase/Desktop/EFI-OPTIMIZED-STAGING/`

**New EFI installed to:** Intel SSD ESP (`EFI/OC`, `EFI/BOOT/BOOTx64.efi`, `System/Library/CoreServices/boot.efi`)

**Recovery copy also on HDD ESP:** same OpenCore tree so the firmware picker can boot either disk.

## What was applied / 적용 내용

### Compat (flashed Mac Pro / 원형 슬래시 방지)

- `boot-args` **반드시** `-no_compat_check` 포함  
  - 레포: `opencore_legacy_patcher/efi_builder/smbios.py` — `model == override_smbios`일 때 주입  
  - 플래시 MacPro5,1→7,1에서 누락 시 펌웨어/부팅 화면에 금지(원형 슬래시) 표시 가능  
- 현재 SSD/HDD EFI 모두 `-no_compat_check` 적용됨

### Performance / 성능

- `boot-args`: `serverperfmode=1` (→ `kern.serverperfmode`), `keepsyms=1`, `npci=0x2000`, `-no_compat_check`, existing Vega/AMFI args kept
- `Kernel.Quirks`: `AppleCpuPmCfgLock=True`, `AppleXcpmCfgLock=True`, `AppleXcpmForceBoost=True`, `ProvideCurrentCpuInfo=True`
- `UEFI.Quirks.TscSyncTimeout=500000` (dual-socket Xeon)
- `SimpleMSR.kext` (OCLP `disable_fw_throttle` path — MSR firmware throttle off)
- Existing `CPUFriend` + `ASPP-Override` + `AppleIntelCPUPowerManagement*` retained (Westmere AICPUPM)

### Pre-AVX Safari / AVX patch

- `RestrictEvents.kext` **1.1.8** from `payloads/Kexts/Community/Safari26-PreAVX-Fix/`
- NVRAM `revpatch=sbvmm,jsc`
- EFI build auto path: `efi_builder/misc.py` → `x86.patch.safari26_preavx.apply_to_misc_builder` (MacPro5,1 + `auto_pre_avx_patch`)
- Profile: `python -m x86.profiles apply macpro5-vega64-tahoe --config …`

### Vega / yellow

- `agdpmod=pikera` + `shikigva` DeviceProperties/boot-args via Track K / `gcn_agdp`

### Logging / 복구용 로그

- `Misc.Debug.Target=0x43` (Enable | Console | **File**)
- `DisplayLevel=0x80000042`, `AppleDebug=True`, `ApplePanic=True`
- File log on ESP: `opencore-YYYY-MM-DD-*.txt`
- `boot-args` keep `-v` + `debug=0x100` + `keepsyms=1`
- Picker: `ShowPicker=True`, `Timeout≥8`

## Reboot / 재부팅 (do not force)

1. Save work. Reboot only when ready: Apple menu → Restart.
2. At OpenCore picker, confirm the SSD OpenCore entry (or HDD recovery if testing).
3. After boot, verify:
   - `sysctl kern.serverperfmode` → `1`
   - `nvram boot-args` includes `serverperfmode=1` and graphics args
   - Safari JSC no longer SIGILL on pre-AVX (RestrictEvents `jsc`)

### Boot picker: choose SSD EFI

- Hold **Option (Alt)** at power-on for firmware boot menu, or use OpenCore picker.
- Select the volume that corresponds to the **80GB SSD** / OpenCore on `disk1s1`.
- Mac Pro also blesses `System/Library/CoreServices/boot.efi` on the ESP (not only `EFI/BOOT`).

### NVRAM reset 주의

- NVRAM reset clears runtime `boot-args` overrides; OpenCore **Add** NVRAM from `config.plist` is re-applied on next OC boot.
- After reset, boot **OpenCore from SSD or HDD ESP** again (do not boot stock `boot.efi` only).

## Recovery / 실패 시 복구

1. Firmware Option-ROM picker → boot **HDD ESP** OpenCore (`disk0s1`), or
2. Mount backup and restore:

```bash
# mount SSD ESP
sudo diskutil mount -mountPoint /Volumes/EFI-SSD disk1s1
# restore original
sudo ditto "/Volumes/Time Machine/EFI-BACKUP-20260904-024355/EFI" /Volumes/EFI-SSD/EFI
sudo ditto "/Volumes/Time Machine/EFI-BACKUP-20260904-024355/System" /Volumes/EFI-SSD/System
sync
sudo diskutil unmount disk1s1
```

Desktop mirror: `/Users/nyase/Desktop/EFI-BACKUP-20260904-024355/`.

3. Read ESP log: mount ESP, open `opencore-*.txt` on the volume root.

## Rebuild commands / 재적용

```bash
source /Users/nyase/Desktop/26x86/.venv/bin/activate
cd /Users/nyase/Desktop/26x86/26x86

# Track K mutations on a config.plist
python -m x86.profiles apply macpro5-vega64-tahoe --config /path/to/EFI/OC/config.plist

# Power / debug / SimpleMSR / -no_compat_check / Safari26 RE staging helper
python Tools/this_mac_efi_optimize.py --stage /path/to/staging --from-backup /path/to/EFI-BACKUP-…
python Tools/this_mac_efi_optimize.py --config /Volumes/EFI-SSD/EFI/OC/config.plist
```

Do **not** modify GitHub Actions workflows for this path.
