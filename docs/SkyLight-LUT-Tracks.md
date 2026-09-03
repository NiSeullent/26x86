# SkyLight / LUT — 트랙 맵 + Mission Control

> **미션:** Autopilot / **극한도전** — Tahoe + pre-AVX + Vega 64 **및** Metal 3802 / Non-Metal 쓸 만함  
> **Stage:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md)  
> **EXTREME:** [EXTREME-Tahoe-PreAVX-Vega64.md](./EXTREME-Tahoe-PreAVX-Vega64.md) · [EXTREME-Metal3802-NonMetal-Tahoe.md](./EXTREME-Metal3802-NonMetal-Tahoe.md)  
> **조율:** MC · **영구 차단 문구 없음** (`X86_EXTREME=1`이면 전 실험 허용)

후보 ID는 Research **R\***; 본 문서 **트랙 A–Z** 만 소유권.

---

## Stage 규칙

| 규칙 | 내용 |
|------|------|
| 공유 파일 | 트랙 **직접 수정 금지** → `*.stage-<TRACK>` |
| 통합 | **MC만** → `feat(extreme-INTEGRATE):` |
| 상세 | [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) |

---

## 성공 기준

| # | 기준 | 검증 |
|---|------|------|
| 1 | WindowServer 정상 색 | solid yellow/orange 없음 |
| 2 | Metal/OpenGL 가속 | 31001 / 3802(M) / Non-Metal(N) 축 |
| 3 | Safari Pre-AVX | RestrictEvents; **≠ 그래픽 AVX** (J) |
| 4 | 재부팅 안정 | cold boot ≥2 |

---

## 가드 정책 — 기본 안전 / 극한 옵트인 (절대 금지 아님)

| 경로 | 동작 |
|------|------|
| **기본** | 3802 / Non-Metal Tahoe shared ≈ `return {}` |
| **옵트인** | `X86_EXTREME=1` 및/또는 `X86_TAHOE_3802` / `X86_TAHOE_NONMETAL` (+ Enforcement 별도) |

**여전히 파일 독재만 금지** (stage 워크플로). extreme 실험·bytepatch·루트볼륨 패치셋은 허용.

---

## 갭 표 (실행 상태)

| 트랙 | 역할 | 상태 |
|------|------|------|
| **A** | 문서·MC | connected · stage-A **INTEGRATE** |
| **B** | SkyLight 분석 | **extreme_unlocked** (`55c3802`) — L5-R과 bytepatch 조율 |
| **C** | ColorSync/CoreDisplay | connected |
| **D** | AGDC | connected · `.stage-D` 후보 |
| **E** | Metallib 31001 | partial (RenderBox-25) |
| **F** | PSP overlay | landed · **INTEGRATE** (본 패스) |
| **G** | detect/sys_patch 연결 | connected |
| **H** | IOSurface/CA | **extreme_open** — N과 **extreme 병행 허용** |
| **I** | dylib interpose | **apply_live** (`98e2528`) — K `--extreme`↔`interpose_apply` TODO |
| **J** | 셰이더 AVX | landed — 노란화면≠AVX SIGILL; stage-J detect 큐 |
| **K** | MacPro5+Vega E2E | landed — `application_entry.py` 혼입 주의 |
| **L** | WS hook | landed · L5=`refused_by_agent` → **L5-R** 루트볼륨 패치셋 재배정 |
| **M** | Metal 3802 | landed · **INTEGRATE** 라이브 (`metal_3802.py`) |
| **N** | Non-Metal | **stage_ready→INTEGRATE** 라이브 (`non_metal*.py`) |

### H ↔ N

extreme에서 **병행 허용**: H=IOSurface/CA·QuartzCore 실험 더블래치, N=Non-Metal shared 재주입. 충돌 키는 INTEGRATE 시 MC가 병합·문서화만 (상호 차단하지 않음).

### INTEGRATE 우선순위 (현재)

1. ✅ A docs · M · N · F (`52f7298`)  
2. **대기 (MC):** **H** stage-H · **J** stage-J detect만  
3. **보류:** D / L5-R·B / I↔K 코드 — **Tahoe 루트패치·이 Mac 배포 전담 에이전트**와 충돌 방지  

**루트패치:** `is_tahoe` / macOS 26에서만 적용. Sequoia + `X86_EXTREME`이어도 루트 **no-op** ([EXTREME](./EXTREME-Tahoe-PreAVX-Vega64.md)).
---

## OCLP 세대 해금

차단(기본 {}) → 페이로드 → 옵트인 스모크 → 증거 후 기본 승격. 지금은 옵트인 스모크.

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 극한도전 A–L · M–Z |
| 2026-09-04 | stage · 옵트인 · **A/M/N/F INTEGRATE** · B/H/I/L5-R 갭 · 영구차단 삭제 |
