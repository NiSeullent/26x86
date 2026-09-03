# OCLP T1 MBP14,3 — Tools

Diagnostic and recovery tools for 26x86 T1 on MacBookPro14,3.

## Safety Classification

| Tool | Safety | Description |
|------|--------|-------------|
| `kdk_status.command` | ✅ READ-ONLY | Inspects KDK installation status and kernel compatibility |
| `verify_efi.command` | ✅ READ-ONLY | Audits EFI partition contents without modification |
| `collect_graphics_diagnostics.command` | ✅ READ-ONLY | Collects GPU/display/WindowServer logs for troubleshooting |
| `revert_snapshot.command` | ⚠️ POTENTIALLY DESTRUCTIVE | Reverts to sealed APFS snapshot (requires explicit `YES` confirmation + `sudo`) |

## Usage

All tools can be run by double-clicking the `.command` file or from Terminal:

```bash
bash Tools/kdk_status.command
bash Tools/verify_efi.command
bash Tools/collect_graphics_diagnostics.command
bash Tools/revert_snapshot.command   # ⚠️ requires sudo + explicit YES
```

## Important Notes

- **No tool in this directory will modify Ventura, NVRAM, or internal EFI automatically.**
- `revert_snapshot.command` requires the user to type `YES` (exact match) before any `sudo` operation.
- `collect_graphics_diagnostics.command` outputs to `~/Desktop/GPU-Diagnostics-{timestamp}/`.
- All tools are designed for MacBookPro14,3 with T1 chip running macOS Tahoe via OpenCore.
