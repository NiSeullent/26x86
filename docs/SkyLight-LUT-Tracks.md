# SkyLight / LUT — 트랙 맵 + Mission Control

> **마지막 INTEGRATE:** **J** detect soft-merge · base H+L5 `d1093ef` · stages `3800bf8`/`393192d`  
> **STAGE:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) · **EXTREME:** [EXTREME-Tahoe-PreAVX-Vega64.md](./EXTREME-Tahoe-PreAVX-Vega64.md)  
> 루트·L5·K extreme: **Tahoe (`is_tahoe`) only** · gate land → Sweep

## 갭 표

| 트랙 | 상태 |
|------|------|
| **A/F/G/M/N** | INTEGRATE done |
| **B** | extreme_unlocked · `26X86_SL_*` vs L5 `26X86_L5_*` |
| **D** | diagnostics live |
| **H** | INTEGRATE done `d1093ef` · N∥10.15.7 |
| **I↔K** | linked `cfd2458` |
| **J** | **INTEGRATE done** · detect-only (`shader_avx`) · ∉ SYS_PATCH |
| **L5-R** | recipes + soft-import done · **is_tahoe wire → Sweep** |

## 다음 큐

1. **Sweep:** `tahoe_gate` + L5/M is_tahoe  
2. deferred: L5-patched 실기 · 앱/PKG  

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | J detect INTEGRATE |
| 2026-09-04 | WIP Sweep — J+gate 미결; H/L5 soft-import done |
| 2026-09-04 | H promote · L5 soft-import · I↔K |
