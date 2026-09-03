# EXTREME — Tahoe Pre-AVX + Vega 64 (Mission Control)

> **Stage:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) · **Tracks:** [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md)  
> **MC:** 문서/갭 + docs/Tools/H/L5 soft-import INTEGRATE · 앱 배포는 전담 에이전트

## 극한 정책

- `X86_EXTREME=1` (Tahoe에서) → 실험 허용. 영구 blocked 금지.
- **루트패치 / L5 OVERWRITE:** **`is_tahoe` / macOS 26만** (`xnu≥25`). Sequoia+extreme → 루트·L5 **no-op** (배포 `tahoe_gate`와 정합).
- **K `--extreme` → I `apply_extreme_interpose`:** 역시 **Tahoe 전제** (K extreme도 Tahoe 호스트에서만 실주입).

## 갭

| 트랙 | 상태 |
|------|------|
| A/F/G/M/N | integrated |
| **D** | Tools diagnostics **live** (`30203ab`) |
| **B** | extreme_unlocked · L5-R 역할 분담 (`9233fad`, `26X86_SL_*`) |
| **H** | **integrated** — `tahoe_iosurface_ca.py` + amd_* wire · N과 10.15.7 병행 |
| **I↔K** | **linked** (`cfd2458`) — profiles `--extreme`→`apply_extreme_interpose` |
| **J** | landed · stage-J **다음 패스** (resource_exhausted 재시작) |
| **L5-R** | **landed** (`a5c9d94`) · G soft-import **본 패스** · **L5 must use is_tahoe** |

### B ↔ L5-R

| 축 | 소유 | 마커 |
|----|------|------|
| B | BYTE_PATCH API | `26X86_SL_*` |
| L5-R | sys_patch OVERWRITE | `26X86_L5_*` · `L5-patched/` |

### H ∥ N

IOSurface/QuartzCore **10.15.7** 동일 페이로드 → idempotent 병행. N ioaccel `10.14.6`과 충돌 시 H latch 활성 시 **10.15.7 우선**.

## INTEGRATE 큐

1. ✅ A/M/N/F · A docs · D Tools  
2. ✅ **H** iosurface promote (본 패스)  
3. ✅ **L5** G soft-import (본 패스)  
4. next: **J** detect stage  
5. deferred: 앱 배포 / 추가 L5 binary staging  

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | H promote · L5-R landed+soft-import · I↔K linked · is_tahoe |
