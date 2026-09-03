# SkyLight / LUT — 트랙 맵 + Mission Control

> **미션:** Autopilot / **극한도전** — Tahoe + pre-AVX + Vega 64 **및** Metal 3802 / Non-Metal 쓸 만함  
> **마지막 INTEGRATE:** `52f7298` (A·M·N·F live) · **본 패스:** stage-A `9e896f3` + D diagnostics `30203ab`  
> **STAGE-WORKFLOW:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md)  
> **EXTREME:** [EXTREME-Tahoe-PreAVX-Vega64.md](./EXTREME-Tahoe-PreAVX-Vega64.md)  
> **조율:** MC · 영구 차단 문구 없음 · 루트패치는 **Tahoe only**

후보 ID는 Research **R\***; 본 문서 **트랙 A–Z** 만 소유권.

---

## Stage 규칙

| 규칙 | 내용 |
|------|------|
| 공유 파일 | 트랙 **직접 수정 금지** → `*.stage-<TRACK>` |
| 통합 | **MC만** → `feat(extreme-INTEGRATE):` |
| 상세 | [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) |
| docs/Tools | 배포 에이전트와 분리 — 본 INTEGRATE 범위 |

---

## 성공 기준

| # | 기준 | 검증 |
|---|------|------|
| 1 | WindowServer 정상 색 | Tahoe |
| 2 | Metal/OpenGL 가속 | 31001 / 3802(M) / Non-Metal(N) — Tahoe 루트 후 |
| 3 | Safari Pre-AVX | ≠ 그래픽 AVX (J) |
| 4 | 재부팅 안정 | Tahoe cold boot ≥2 |
| 5 | 루트패치 호스트 | `is_tahoe` / macOS 26만 (Sequoia+extreme → 루트 no-op) |

---

## 가드 정책

| 경로 | 동작 |
|------|------|
| **기본** | 3802 / Non-Metal Tahoe ≈ `return {}` |
| **옵트인** | `X86_EXTREME` ± `X86_TAHOE_3802` / `X86_TAHOE_NONMETAL` |

---

## 갭 표

| 트랙 | 상태 |
|------|------|
| **A** | connected · **INTEGRATE done** (`52f7298`/`9e896f3`) · 이후 `.stage-A`만 |
| **B** | extreme_unlocked — L5-R 조율 (코드는 배포 에이전트 후) |
| **C** | connected |
| **D** | connected · **diagnostics INTEGRATE done** (Tools `.command` live) |
| **E** | partial (RenderBox-25) |
| **F** | landed · **INTEGRATE done** `52f7298` |
| **G** | connected |
| **H** | extreme_open — **다음 큐** (N과 extreme 병행) |
| **I** | apply_live — K 연계 TODO |
| **J** | landed — **다음 큐** detect stage |
| **K** | landed |
| **L** | L5-R 재배정 |
| **M** | **INTEGRATE done** live |
| **N** | **INTEGRATE done** live · H와 병행 |

### INTEGRATE 완료 (1–4 + D Tools)

| 순 | 트랙 | 상태 |
|----|------|------|
| 1–4 | A / M / N / F | `52f7298` |
| — | D Tools diagnostics | `30203ab` → live `.command` |
| — | A docs touch-up | `9e896f3` → 원본 |

### 다음 큐

| 순 | 항목 |
|----|------|
| 5 | **H** IOSurface/CA stage |
| 6 | **J** shader AVX detect |
| 7 | **L5-R / B** (배포/루트 에이전트 조율 후) |
| 8 | **I ↔ K** |

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 극한도전 · stage · A/M/N/F INTEGRATE |
| 2026-09-04 | post-`52f7298` 큐 H→J→D→L5-R/B→I↔K (stage-A) |
| 2026-09-04 | **D diagnostics + stage-A 문서 merge** · Tahoe-only 루트 게이트 |
