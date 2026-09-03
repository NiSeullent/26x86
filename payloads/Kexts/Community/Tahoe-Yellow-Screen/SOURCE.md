# Tahoe Yellow Screen — PatcherSupportPkg overlay

**Does not vendor Apple proprietary kexts.**

Conditional injection slot for Tahoe MTL. MC integrates `*.stage-F`.

## Required MTL (PSP #16/#18 · OCLP-T2 #194)

| Bundle | GPU |
|--------|-----|
| `AMDMTLBronzeDriver.bundle` | GCN / Polaris |
| `AMDRadeonX5000MTLDriver.bundle` | Vega |

Companion hints: `AMDRadeonX4000*.kext`, `AMDRadeonX5000*.kext`, `AMDFramebuffer.kext`, `AMDShared.bundle`, `AMDRadeonX5000Shared.bundle`.

PSP #18 today is AppleHDA-only (not graphics).

## Placement

Copy licensed trees into `Universal-Binaries/12.5-25/...`, `RenderBox-25/...`, or sibling `26x86-PatcherSupportPkg`. Never commit Apple binaries.

RenderBox-25: see `Universal-Binaries/RenderBox-25/SOURCE.md` and `Tools/fetch_renderbox25.py`.

## Stage-F

- `x86/graphics/psp_overlay.py` (landed)
- `dmg_mount.py.stage-F` — inject + missing guidance
- `yellow_screen.py.stage-F` — detect `tahoe_psp_overlay`
- `sys_patch.py.stage-F` — no body change
