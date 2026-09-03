# SkyLight / LUT — 트랙 맵 + Mission Control

> **마지막 INTEGRATE:** J `33e506a` + Sweep `tahoe_gate`  
> **STAGE:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) · **EXTREME:** [EXTREME-Tahoe-PreAVX-Vega64.md](./EXTREME-Tahoe-PreAVX-Vega64.md) · **WIP:** [WIP-STATUS.md](./WIP-STATUS.md)  
> 루트·L5·K extreme: **Tahoe (`is_tahoe`) only** · `x86/graphics/tahoe_gate.py`

## 갭 표

| 트랙 | 상태 |
|------|------|
| **A/F/G/M/N** | INTEGRATE done |
| **B** | extreme_unlocked · `26X86_SL_*` vs L5 `26X86_L5_*` |
| **D** | diagnostics live |
| **H** | INTEGRATE done `d1093ef` · N∥10.15.7 |
| **I↔K** | linked · I root Tahoe-gated |
| **J** | **INTEGRATE done** `33e506a` · detect-only · ∉ SYS_PATCH |
| **L5-R** | recipes + soft-import + **is_tahoe wire done** |

## 다음 큐

1. deferred: L5-patched 실기 · 앱/PKG (배포 전담)  
2. ✅ N IOSurface 10.15.7 prefer when H latch  
3. ✅ Validation: `Tools/run_extreme_validation.py` · `docs/EXTREME-TAHOE-VALIDATION.md`  

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | Sweep tahoe_gate + L5/M/N/I wire |
| 2026-09-04 | J detect INTEGRATE |
| 2026-09-04 | WIP Sweep — J+gate 미결; H/L5 soft-import done |
| 2026-09-04 | H promote · L5 soft-import · I↔K |
