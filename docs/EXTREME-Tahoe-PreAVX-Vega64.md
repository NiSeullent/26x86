# EXTREME — Tahoe Pre-AVX + Vega 64 (Mission Control)

> **Stage:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) · **Tracks:** [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md)  
> **MC (본 라운드):** 갭/큐 문서만 · **Sweep:** 메인 INTEGRATE (race 금지)

## 극한 정책

- `X86_EXTREME=1` (Tahoe에서) → 실험 허용. 영구 blocked 금지.
- **루트패치 / L5 OVERWRITE:** **`is_tahoe` / macOS 26만** (`xnu≥25`). Sequoia+extreme → 루트·L5 **no-op**.
- 단일 게이트: `x86/graphics/tahoe_gate.py` (`is_tahoe` · `root_patches_allowed`) — 배포 에이전트와 정합.
- **K `--extreme` → I:** Tahoe 호스트에서만 실주입.

## 갭 / WIP (Sweep 전수)

| 항목 | 상태 | 소유 |
|------|------|------|
| A/F/G/M/N | integrated | — |
| D Tools | live | — |
| B ↔ L5-R 역할 | landed · 마커 분리 | — |
| H iosurface | integrated `d1093ef` · N∥10.15.7 | — |
| I↔K | linked `cfd2458` | — |
| L5-R recipes | landed `a5c9d94` · G soft-import `d1093ef` | — |
| **J detect stage** | stage ready (`3800bf8` rebase on H+L5) · **INTEGRATE 대기** | **Sweep** |
| **`tahoe_gate.py`** | 워킹트리 untracked · L5/M dirty가 import 중 | **Sweep** |
| **L5 → `is_tahoe`** | live `skylight_lut_rootpatch.py` WIP (gate wire) | **Sweep** |
| **M → `tahoe_gate`** | `metal3802_tahoe.py` WIP | **Sweep** |
| N ioaccel 10.14.6 vs H 10.15.7 | prefer 10.15.7 when H latch | docs / later |
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
2. **Sweep 메인:** `tahoe_gate` land + L5/M gate wire + **J** detect promote  
3. MC: Sweep 커밋 후 갭 표만 재맞춤 (본 문서 / stage-MC)  
4. deferred: 앱 배포 · L5 binary staging

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | WIP Sweep 라운드 — MC 갭만; J+tahoe_gate→Sweep |
| 2026-09-04 | H promote · L5 soft-import · I↔K · is_tahoe 메모 |
