# Extreme-Interpose (Track I)

Symbol-based Metal/SkyLight/CoreDisplay dylib interpose PoC for 26x86 Tahoe
(pre-AVX + Vega 64 research). Commit prefix: `feat(skylight-I):`.

## Gates

```bash
export X86_EXTREME=1                 # arms recipe + build→copy→guide (no SHA pin gate)
export X86_EXTREME_INSTALL=1         # optional: live /Library SkyLightPlugins
export X86_INTERPOSE_AVX=passthrough # or report0 | report1
export X86_INTERPOSE_LUT=off         # or log | identity
```

## Apply

```bash
chmod +x scripts/*.sh
./scripts/apply.sh
# → staging/ + SkyLightPlugins/ExtremeCompositor.{dylib,txt} + APPLY-GUIDE.txt
# or: X86_EXTREME=1 python3 -m x86.graphics.interpose_apply
```

## Build only

```bash
./scripts/build.sh
```

## License

BSD-3-Clause. See `NOTICE.md` — no Apple blob redistribution.
