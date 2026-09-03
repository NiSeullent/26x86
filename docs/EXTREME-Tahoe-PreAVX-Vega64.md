# EXTREME — Tahoe Pre-AVX + Vega 64 (Mission Control)

> **Stage:** [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md) · **Tracks:** [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md)  
> **3802/Non-Metal:** [EXTREME-Metal3802-NonMetal-Tahoe.md](./EXTREME-Metal3802-NonMetal-Tahoe.md) · **L:** [EXTREME-WindowServer-Hook.md](./EXTREME-WindowServer-Hook.md)  
> **코드 요약:** `x86/extreme/` (런타임 배선·앱 배포는 **Tahoe 루트패치/배포 전담 에이전트** 소유)

## 극한 정책 (영구 차단 없음)

- 기본 배포는 안전 기본값(`return {}`) 가능.
- **`X86_EXTREME=1`이면** (대상 OS가 Tahoe일 때) L5-R · 3802 · Non-Metal · interpose · bytepatch · IOSurface/CA 실험 **허용**.
- MC 문서에 blocked-forever 플래그 **금지**.

### 루트패치 OS 게이트 (성공 조건 · 필수)

| 조건 | 의미 |
|------|------|
| **`is_tahoe` / macOS 26 (XNU ≥ 25)** | 루트볼륨 패치·extreme 루트 슬라이스가 **실제로 적용**되는 유일한 타깃 |
| **Sequoia(및 그 외 non-Tahoe) 호스트** | `X86_EXTREME=1`이어도 **루트패치 no-op** — 플래그는 연구/스테이징·문서·detect 요약만 |
| **이 Mac 앱/PKG 설치** | 배포 전담 에이전트 소유 — MC는 문서/갭만 |

검증: 루트패치 성공 판정은 Tahoe 부팅 환경에서만. Sequoia에서 extreme 실험 “성공”을 루트 적용으로 주장하지 말 것.

## 성공 기준

| # | 기준 |
|---|------|
| 1 | WindowServer 정상 색 (**Tahoe**) |
| 2 | Metal/OpenGL (31001 / 3802 / Non-Metal 축) — **Tahoe 루트패치 후** |
| 3 | Safari Pre-AVX — **≠ 그래픽 AVX** (J) |
| 4 | 재부팅 안정 (**Tahoe** cold boot ≥2) |
| 5 | 루트패치 경로 = **Tahoe only** (`is_tahoe`) |

## A–N 갭 (요약)

| 트랙 | 상태 | 메모 |
|------|------|------|
| **A/F/G/M/N** | integrated / connected | `52f7298` 등 |
| **B** | extreme_unlocked | L5-R 조율 — 코드 merge는 배포 에이전트 후 |
| **C/D** | connected | D `.stage-D` — 배포 에이전트와 충돌 시 대기 |
| **E** | partial | RenderBox-25 |
| **H** | extreme_open | **INTEGRATE 대기:** stage-H only |
| **I** | apply_live | K `--extreme` 연계 TODO (배포 에이전트와 조율) |
| **J** | landed | **INTEGRATE 대기:** stage-J detect only |
| **K** | landed | E2E; Tahoe 실기 |
| **L** | landed | L5-R — 배포/루트 에이전트 후 MC 문서만 |

## INTEGRATE 큐 (현재 · 충돌 회피)

배포/Tahoe-루트패치 전담 에이전트와 **겹치지 않게** MC는 다음만 대기:

1. **H** — `tahoe_iosurface_ca.py.stage-H` 등 (문서·stage 승격만, 대량 sys_patch 재작성 금지)  
2. **J** — `shader_avx_detect.stage-J.py` → detect soft-import  

**보류 (배포 에이전트 소유 구간):** D diagnostics 라이브 치환, L5-R/B 코드 merge, I↔K 프로파일 실행 배선, 앱/PKG 빌드.

재명령 시점: 배포 에이전트가 Tahoe-only 루트게이트 + 이 Mac 설치 경로를 main에 올린 뒤 → 부모 재명령 → MC가 H/J stage INTEGRATE.

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | A/M/N/F INTEGRATE · I=apply_live · H∥N · L5-R |
| 2026-09-04 | **Tahoe-only 루트패치** · Sequoia extreme no-op · INTEGRATE=H/J만 대기 |
