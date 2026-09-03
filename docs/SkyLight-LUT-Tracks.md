# SkyLight / LUT — 트랙 맵 + Mission Control

> **마지막 INTEGRATE:** H iosurface promote + L5 G soft-import + D Tools · base `52f7298`  
> **STAGE:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) · **EXTREME:** [EXTREME-Tahoe-PreAVX-Vega64.md](./EXTREME-Tahoe-PreAVX-Vega64.md)  
> 루트패치·L5·K extreme: **Tahoe (`is_tahoe`) only**

## 갭 표

| 트랙 | 상태 |
|------|------|
| **A/F/G/M/N** | INTEGRATE done |
| **B** | extreme_unlocked · `26X86_SL_*` vs L5 `26X86_L5_*` |
| **D** | diagnostics **live** |
| **H** | **INTEGRATE done** · N과 10.15.7 병행 |
| **I↔K** | **linked** (`cfd2458`) · Tahoe 전제 |
| **J** | 다음 패스 |
| **L5-R** | **landed** · soft-import · **must use is_tahoe** |

## 다음 큐

1. **J** detect stage  
2. L5-patched Mach-O 스테이징 (실기)  
3. 배포 에이전트 앱/PKG  

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | H promote · L5 soft-import · I↔K linked |
