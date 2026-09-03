# Tahoe 그래픽 R&D 로드맵

> **미션 승격:** Autopilot / **극한도전** — Tahoe + pre-AVX + Vega 64에서 **가속·쓸 만한** 환경 (중단 없음)  
> **Mission Control:** [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md)  
> **합성 Research:** [Tahoe-SkyLight-LUT-Research.md](./Tahoe-SkyLight-LUT-Research.md)  
> **Phase 1 태스크:** [Tahoe-Graphics-Roadmap-Phase1-Tasks.md](./Tahoe-Graphics-Roadmap-Phase1-Tasks.md)  
> **노란 화면 조사:** [Tahoe-Yellow-Screen-Research.md](./Tahoe-Yellow-Screen-Research.md)

---

## 0. 성공 기준 (극한도전)

| # | 기준 | 비고 |
|---|------|------|
| 1 | WindowServer **정상 색** | solid yellow/orange 제거 |
| 2 | **Metal / OpenGL 가속** | Vega 31001; 3802/Non-Metal 가드 **유지** |
| 3 | **Safari** Pre-AVX Fix | RestrictEvents / cf7f26f — WS와 별개 |
| 4 | **재부팅 안정** | cold boot ≥2, KP/WS 루프 없음 |

---

## 1. 하드 가드

| 항목 | 정책 |
|------|------|
| Metal 3802 Tahoe shared | **`return {}` 유지 — 해제 금지** |
| Non-Metal Tahoe shared | **해제 금지** |
| `useMetal=no` | Tahoe에서 **적용 금지** |
| 추측 SkyLight/CoreDisplay 바이트패치 | **금지** |
| EFI agdpmod | d3a7b87 유지 — 트랙 D는 검증만 |

---

## 2. 레이어

| Layer | 초점 | 상태 |
|-------|------|------|
| **A** | Pre-AVX / Safari / 진단 / 보안 | Phase 1 — 일부 done |
| **B** | compositor / LUT / 가속 복구 (**극한도전 핵심**) | 트랙 A–L active |
| **C** | Non-Metal·Liquid Glass (가드 존중) | long-term |
| **D** | T2 / SEP | Known-Issues — 본 미션 외 |

---

## 3. Layer B ↔ 트랙 매핑

| Roadmap | 트랙 | 산출 |
|---------|------|------|
| B-0 문제 정의 | A | Research + Mission Control |
| B-1 SkyLight/WS 심볼 | B | nm/otool 목록, 실패 모드 |
| B-2 ColorSync/ICC | C | tint vs solid |
| B-3 AGDC | D | 검증만 |
| B-4 RenderBox/31001 | E | 페이로드 게이트 (368ff72) |
| B-5 PSP 오버레이 | F | 12.5-25 / RenderBox-25 실장 |
| B-6 통합/detect | G | 훅·테스트 |
| B-7 Plugins 로더 | H | moraea Tahoe |
| B-8 재부팅/KDK | L | 기준 4 |
| B-9 UI/3802 보조 | I / K | 가드 유지 |

상세 소유권·금지 파일: [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md).

---

## 4. Layer A (요약)

Safari Pre-AVX ≠ 노란 화면. Phase1 A-05/A-06 done (cf7f26f).  
문서화된 AMD 완화 boot-arg: `agdpmod`, `shikigva`. **없음:** WS Metal compositor off 공식 플래그.

---

## 5. Autopilot

중단 조건 없음. 미달 기준 → 트랙 재배분 → 근거 있는 최소 패치 → 재측정 → Tracks 갱신(A).  
코드는 B–L이 소유; A는 문서만.

---

## 6. wiki

- [Mac-Pro-Tahoe-Yellow-Screen.md](./wiki/Mac-Pro-Tahoe-Yellow-Screen.md)  
- [Pre-AVX-Mac-Pro.md](./wiki/Pre-AVX-Mac-Pro.md) · [Safari-PreAVX-Fix.md](./wiki/Safari-PreAVX-Fix.md)  
- [GPU-Limitations.md](./wiki/GPU-Limitations.md)

---

## 7. 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 파일 복구 · Layer A/B · 가드 |
| 2026-09-04 | 극한도전 성공 기준 · 트랙 A–L 매핑 · Autopilot |
