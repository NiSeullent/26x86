# Extreme-Interpose — sources

| Path | Role |
|------|------|
| `src/ExtremeCompositorInterpose.c` | DYLD_INTERPOSE: sysctl AVX, CG gamma, ColorSync |
| `src/ExtremeCompositorInterpose.h` | Env key constants |
| `src/SkyLightPluginShim.c` | `SkyLightPluginEntry` no-op |
| `Makefile` | Builds dylib + optional plugin |
| `scripts/build.sh` | Clean build |
| `scripts/install-dyld-insert.sh` | Gated DYLD_INSERT helper |
| `launchd/*.plist.example` | Disabled example |
| `docs/SYMBOLS.md` | Symbol map |

Python: `x86/graphics/interpose_*.py`
