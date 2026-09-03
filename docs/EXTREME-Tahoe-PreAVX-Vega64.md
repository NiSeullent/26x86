# EXTREME — Tahoe Pre-AVX + Vega 64 (Mission Control)

> **Stage:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) · **Tracks:** [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md)  
> **3802/Non-Metal:** [EXTREME-Metal3802-NonMetal-Tahoe.md](./EXTREME-Metal3802-NonMetal-Tahoe.md) · **L:** [EXTREME-WindowServer-Hook.md](./EXTREME-WindowServer-Hook.md)  
> **코드:** `x86/extreme/`

## 극한 정책 (영구 차단 없음)

- 기본 배포는 안전 기본값(`return {}`) 가능.
- **`X86_EXTREME=1`이면** L5-R 루트볼륨 패치 · 3802 · Non-Metal · interpose · bytepatch · IOSurface/CA **전부 허용**.
- MC 문서/INTEGRATE에 blocked-forever 플래그 **금지**.

## 성공 기준

| # | 기준 |
|---|------|
| 1 | WindowServer 정상 색 |
| 2 | Metal/OpenGL (31001 / 3802 / Non-Metal 축) |
| 3 | Safari Pre-AVX — **≠ 그래픽 AVX** (J: 노란화면 ≠ SIGILL) |
| 4 | 재부팅 안정 |

## A–N 갭

| 트랙 | 상태 | 메모 |
|------|------|------|
| **A** | integrated | STAGE-WORKFLOW / Tracks |
| **B** | extreme_unlocked (`55c3802`) | SL-BYTEPATCH-LUT; **L5-R과 조율** |
| **C** | connected | colorsync/coredisplay |
| **D** | connected | agdc; `.stage-D` 후보 |
| **E** | partial | RenderBox-25 → 31001 no-op |
| **F** | **integrated** | psp overlay live |
| **G** | connected | soft-import |
| **H** | extreme_open (`a02908b`) | IOSurface/CA; **N과 extreme 병행 허용** |
| **I** | **apply_live** (`98e2528`) | EXTREME→interpose_apply staging; INSTALL→`/Library`. **TODO:** K `--extreme` 연계 |
| **J** | landed | stage-J detect 큐; Tahoe 스캔↔K E2E TODO |
| **K** | landed | E2E 프로파일; `application_entry.py` 혼입 주의 |
| **L** | landed | L5=`refused_by_agent` → **L5-R** 루트볼륨 패치셋 |
| **M** | **integrated** | `metal_3802.py` live opt-in |
| **N** | **integrated** (`7360f93`) | `non_metal*.py` live; Enforcement 별도 env; H와 병행 |

## INTEGRATE 큐

1. ✅ A docs  
2. ✅ M 3802  
3. ✅ N Non-Metal  
4. ✅ F PSP  
5. next: H stage-H  
6. next: J detect  
7. next: D diagnostics  
8. next: L5-R / B coord  
9. next: I↔K extreme profile  

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | A/M/N/F INTEGRATE · I=apply_live · H∥N · L5-R · 영구차단 삭제 |
