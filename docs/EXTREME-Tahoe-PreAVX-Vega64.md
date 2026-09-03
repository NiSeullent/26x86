# EXTREME — Tahoe Pre-AVX + Vega 64 (Mission Control)

> **Stage:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) · **Tracks:** [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md) · **WIP:** [WIP-STATUS.md](./WIP-STATUS.md)  
> **MC:** J detect `33e506a` · **Sweep:** `tahoe_gate` land

## 극한 정책

- `X86_EXTREME=1` (Tahoe에서) → 실험 허용. 영구 blocked 금지.
- **루트패치 / L5 OVERWRITE:** **`is_tahoe` / macOS 26만** (`xnu≥25`). Sequoia+extreme → 루트·L5 **no-op**.
- 단일 게이트: `x86/graphics/tahoe_gate.py` (`is_tahoe` · `root_patches_allowed`) — **Sweep 소유** · 배포는 앱 설치만.
- **K `--extreme` → I:** Tahoe 호스트에서만 실주입.

## 갭 / WIP

| 항목 | 상태 | 소유 |
|------|------|------|
| A/F/G/M/N | integrated | — |
| D Tools | live | — |
| B ↔ L5-R 역할 | landed · 마커 분리 | — |
| H iosurface | integrated `d1093ef` · N∥10.15.7 | — |
| I↔K | linked `cfd2458` | — |
| L5-R recipes | landed · G soft-import · **gate wired** | Sweep |
| **J detect** | **integrated** `33e506a` | MC |
| **`tahoe_gate.py`** | **landed** | **Sweep** |
| N ioaccel 10.14.6 vs H 10.15.7 | **prefer 10.15.7 when H latch** | landed |
| Validation matrix | `docs/EXTREME-TAHOE-VALIDATION.md` | validate |
| L5-patched Mach-O 실기 | deferred | 배포 |
| 앱/PKG | deferred | 배포 전담 |

### B ↔ L5-R

| 축 | 소유 | 마커 |
|----|------|------|
| B | BYTE_PATCH API | `26X86_SL_*` |
| L5-R | sys_patch OVERWRITE | `26X86_L5_*` · `L5-patched/` |

### H ∥ N

IOSurface/QC **10.15.7** 동일 → idempotent. H latch 시 N `IOSurface.kext=10.14.6`보다 **10.15.7 우선**.

## INTEGRATE 큐

1. ✅ A/M/N/F · D Tools · H · L5 soft-import (`d1093ef`)
2. ✅ **J** detect (`33e506a`)
3. ✅ **Sweep:** `tahoe_gate` + L5/M/N/I soft-import
4. deferred: 앱 배포 · L5 binary staging

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | Sweep tahoe_gate land |
| 2026-09-04 | J detect INTEGRATE · Sweep은 tahoe_gate만 |
| 2026-09-04 | WIP Sweep 라운드 — MC 갭만; J+tahoe_gate→Sweep |
| 2026-09-04 | H promote · L5 soft-import · I↔K · is_tahoe 메모 |
