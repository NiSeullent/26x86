# Extreme-Interpose (Track I)

Symbol-based Metal/SkyLight/CoreDisplay dylib interpose PoC for 26x86 Tahoe
(pre-AVX + Vega 64 research). Commit prefix: `feat(skylight-I):`.

## Gates

```bash
export X86_EXTREME=1
export X86_EXTREME_INSTALL=1   # install helpers only
export X86_INTERPOSE_AVX=passthrough   # or report0 | report1
export X86_INTERPOSE_LUT=off           # or log | identity
```

## Build

```bash
chmod +x scripts/*.sh && ./scripts/build.sh
```

## License

BSD-3-Clause. See `NOTICE.md` — no Apple blob redistribution.
