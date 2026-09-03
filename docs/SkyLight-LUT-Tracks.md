# SkyLight / LUT — 트랙 맵 + Mission Control

> **미션:** Autopilot / **극한도전**  
> **목표 환경:** macOS **Tahoe** + **pre-AVX** CPU + **Vega 64** (Mac Pro 소켓)  
> **수단:** EFI · 루트패치 · 시스템패치 → **가속되고 쓸 만한** 데스크톱  
> **중단 조건:** 없음 (실패해도 트랙 재배분·재시도)  
> **조율:** 트랙 **A** = 문서·Mission Control만 (코드 독식 금지)  
> **근거:** [Tahoe-SkyLight-LUT-Research.md](./Tahoe-SkyLight-LUT-Research.md) · [Tahoe-Graphics-Roadmap.md](./Tahoe-Graphics-Roadmap.md)

복구 후보 난이도표의 옛 `A/B/C…` 라벨과 **트랙 ID가 겹친다.** 후보 ID는 Research의 **R\*** 를 쓰고, 본 문서의 **트랙 A–Z** 만 파일 소유권에 쓴다.

---

## Mission Control

### 성공 기준 (전부 충족)

| # | 기준 | 검증 |
|---|------|------|
| 1 | **WindowServer 정상 색** | 전체 화면 노란/주황 없음; Display 프로필·스크린샷 정상 |
| 2 | **Metal / OpenGL 가속** | Vega 31001 경로; `AMDRadeonX5000*` 로드; 단순 Metal/GL 스모크 |
| 3 | **Safari (Pre-AVX Fix)** | RestrictEvents + `revpatch=jsc`; WebContent SIGILL 없음 (cf7f26f) |
| 4 | **재부팅 안정** | ≥2회 cold boot; WS 루프/KP 없음; 루트패치 스냅샷 유지 |

### 목표 스택 (참조)

```
pre-AVX MacPro5,1 (또는 동급) + Vega 64 (0x687F)
        │
        ├─ EFI: OpenCore + WhateverGreen agdpmod/shikigva + RestrictEvents (Safari)
        ├─ 루트패치: amd_vega 31001 + compositor mitigations + RenderBox-25(있으면)
        └─ 시스템: WindowServer/SkyLight/CoreDisplay/ColorSync 정상 합성
```

### 이미 된 것 (재구현 금지)

| 커밋 | 내용 |
|------|------|
| [edf958f](https://github.com/NiSeullent/26x86/commit/edf958f) | WS cache, ColorSync sRGB, KDKless, PSP overlay 슬롯 |
| [d3a7b87](https://github.com/NiSeullent/26x86/commit/d3a7b87) | EFI agdpmod / yellow_screen_risk |
| [cf7f26f](https://github.com/NiSeullent/26x86/commit/cf7f26f) | Safari Pre-AVX |
| [368ff72](https://github.com/NiSeullent/26x86/commit/368ff72) | RenderBox metallib **페이로드 게이트** |

### 전역 하드 가드

| 금지 | 이유 |
|------|------|
| **Metal 3802** Tahoe shared 가드 해제 | KP |
| **Non-Metal** Tahoe shared 가드 해제 | KP |
| CoreDisplay/SkyLight **추측 바이트패치** | 사설 심볼 미공개 |
| EFI agdpmod **재작성** | d3a7b87 — 트랙 D는 검증만 |
| `x86/gui/**`, `.github/workflows/**` | 본 미션 트랙 범위 밖 (별도) |

**GPU 무관:** Vega 64 (unpublished / reporter: 내부) + [OCLP-T2 #194](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194) → 공통 compositor.

### Autopilot 루프 (중단 없음)

1. Mission Control에서 미달 성공 기준 식별  
2. 담당 트랙(B–L)에 작업 배분 — **한 파일 한 작성자**  
3. 근거 있는 최소 변경만 머지; 가드 위반 PR 거부  
4. 실기/픽스처로 기준 1–4 재측정  
5. Research·본 Tracks 상태열 갱신 (트랙 A) → 1로  

---

## 활성 트랙 A–L

| 트랙 | 역할 | 소유 (쓰기 OK) | 금지 | 성공 기여 | 상태 |
|------|------|----------------|------|-----------|------|
| **A** | Mission Control · Research · Roadmap | `docs/SkyLight-LUT-Tracks.md`, `docs/Tahoe-SkyLight-LUT-Research.md`, `docs/Tahoe-Graphics-Roadmap.md`, wiki **링크** | `x86/**`·`sys_patch/**`·`efi_builder/**`·`payloads/**` 코드 | 조율·가드·기준 문서 | **active** |
| **B** | SkyLight / WindowServer 심볼·분석 | `x86/graphics/skylight_analysis.py` 등 B 전용, Tools 진단 | 3802/Non-Metal 가드, 추측 바이트패치 | 기준 1 (색/합성 원인) | pending |
| **C** | CoreDisplay / ColorSync / ICC / LUT | `colorsync_*` / ICC 진단·문서 | `useMetal=no` Tahoe 활성화 | 기준 1 (tint vs solid) | pending |
| **D** | AGDC / framebuffer / solid yellow | 문서·진단 필드만 | **`efi_builder/**` 수정** | 기준 1·4 (AGDC vs compositor) | pending |
| **E** | Metallib / RenderBox / Opaque / 31001 | `metal_31001.py` 게이트, RenderBox resolve, `metallib_*` | 3802 metallib로 31001 대체 | 기준 2 (셰이더/가속) | **부분** (368ff72) |
| **F** | PatcherSupportPkg Tahoe 오버레이 실장 | `payloads/.../Tahoe-Yellow-Screen/Universal-Binaries/**` | 무단 Apple 바이너리 커밋 | 기준 2 (MTL/companion) | pending |
| **G** | 루트패치 통합 + detect + 테스트 | `sys_patch` **연결**, `yellow_screen`/`skylight_tracks` detect, tests | EFI 재작성, 가드 해제, GUI | 기준 1–4 자동화 필드 | **부분** |
| **H** | SkyLightPlugins / moraea Tahoe 로더 | 플러그인 슬롯·SHA 핀·로더 연구 | 스톡 SkyLight에 dylib만 넣고 성공 주장 | 기준 1 (조건부) | reserved→active when B ready |
| **I** | Liquid Glass / UI 우회 (가드 존중) | developer-only 실험 문서 | Non-Metal shared **해제** | UX (가속 후) | long-term |
| **J** | Broadwell 검은화면+#234 분리 | 증상 매트릭스 문서 | 노란 화면 패치에 iGPU 가설 혼입 | 오진 방지 | pending |
| **K** | MetallibSupportPkg **3802** Tahoe | 3802 PKG/빌드 (Vega와 **별개**) | KP 없이 가드 해제 | 비-Vega 기기; 본 미션 보조 | blocked/guard |
| **L** | KDK / KDKless / RSR / 재부팅 안정 | KDKless 회귀, RSRRepair, boot 체크리스트 | agdpmod EFI 재구현 | **기준 4** | pending |

---

## 예약 슬롯 M–Z

| 트랙 | 예정 |
|------|------|
| **M** | OpenCL / GVA / 미디어 |
| **N** | eGPU / 다중 GPU strip |
| **O** | Polaris/GCN 실기 매트릭스 (Vega와 병렬 재현) |
| **P** | SIP/AMFI/boot-args known-good 시트 |
| **Q** | 업스트림 OCLP/PSP PR 동기화 |
| **R** | 릴리스 노트 / 사용자 체크리스트 |
| **S–Z** | 실기 팜, 자동화, 외부 협력 |

---

## 파일 충돌 규칙

1. **한 파일 = 한 활성 작성자.** 충돌 시 A가 Tracks에 “대기” 표기.  
2. G는 B/C/E/F **연결만** — 새 가설 패치 금지.  
3. A는 **코드 패치 금지** (본 Mission Control·Research·Roadmap만).  
4. D는 EFI **읽기/검증**만.  
5. K는 본 미션(Vega/pre-AVX)의 가속 경로가 아님 — 3802 가드 유지.

---

## 이슈·심볼 빠른 참조

| 항목 | URL / 값 |
|------|----------|
| OCLP-T2 #194 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194 |
| OCLP #1167 | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 |
| OCLP PR #1176 | https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1176 |
| PSP #16/#18 | PatcherSupportPkg DRAFT |
| Vega 64 | unpublished / reporter: 내부 |
| 공개 심볼 바늘 | `ColorSyncProfileCreateWithURL`, `CGColorSpaceCreateWithICCData`, `CGDisplayGammaTable`, … |

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 초안 A–G |
| 2026-09-04 | **극한도전** Mission Control · A–L · M–Z · 성공 기준 4항 |
