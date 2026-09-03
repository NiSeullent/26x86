# Tahoe Yellow Screen — PatcherSupportPkg overlay

**Does not vendor Apple proprietary kexts.** Those stay in `Universal-Binaries.dmg`
(`NiSeullent/26x86-PatcherSupportPkg`, Apple license).

This directory is a **conditional injection slot**:

| Path | Purpose |
|------|---------|
| `Universal-Binaries/12.5-25/` | Drop Tahoe MTL / GPU companion trees from [PatcherSupportPkg #16](https://github.com/dortania/PatcherSupportPkg/pull/16) / [#18](https://github.com/dortania/PatcherSupportPkg/pull/18) when they exist. `dmg_mount` dittos `12.5-25` and `12.5-26` onto the mounted DMG. |
| `Universal-Binaries/RenderBox-25/` | OCLP Metal 31001 `default.metallib` ([PR #1176](https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1176)). Layout: `System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources/default.metallib`. Installed **only if the file exists** (`metal_31001.py` gate). |
| `SkyLightPlugins/Library/Application Support/SkyLightPlugins/` | Compositor interpose `.dylib`+`.txt` **only** when stem is allowlisted **and** SHA-256 is pinned in `x86/graphics/skylight_lut.py`. Stock Tahoe SkyLight does **not** load this folder (moraea `Plugins.m` / `SkyLightOld.dylib` required). DropboxHack/CoreWLAN are never used as LUT fixes. |
| `ColorSync/` | Optional ICC; runtime already links system `sRGB Profile.icc` (OCLP-T2 #194 ICC/LUT reports). |

EFI `KDKlessWorkaround.kext` is the existing open-source payload
(`payloads/Kexts/Misc/KDKlessWorkaround-*.zip`, [flagersgit/KDKlessWorkaround](https://github.com/flagersgit/KDKlessWorkaround)).
Mac Pro sockets enable it so WindowServer does not loop when MTL bundles are missing.

Metal 3802 / Non-Metal shared Tahoe guards stay closed (kernel panic).

Research: [docs/Tahoe-SkyLight-LUT-Research.md](../../../../docs/Tahoe-SkyLight-LUT-Research.md)
