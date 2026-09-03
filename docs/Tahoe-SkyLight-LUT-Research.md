# Tahoe SkyLight / WindowServer LUT·셰이더 합성 — 심층 Research

> **프로젝트:** 26x86 (`NiSeullent/26x86`)  
> **작성일:** 2026-09-04  
> **미션:** Autopilot / **극한도전** — Tahoe + pre-AVX + Vega 64 **및** Metal 3802 · Non-Metal도 **쓸 수 있는** 환경 (**중단 없음**)  
> **Mission Control:** [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md) · [STAGE-WORKFLOW.md](./STAGE-WORKFLOW.md)  
> **마지막 INTEGRATE:** `52f7298` — A docs · M 3802 · N Non-Metal · F PSP **live**  
> **다음 큐:** H → J → L5-R/B → I↔K (D Tools diagnostics 승격됨)  
> **로드맵:** [Tahoe-Graphics-Roadmap.md](./Tahoe-Graphics-Roadmap.md) Layer B  
> **관련:** [Tahoe-Yellow-Screen-Research.md](./Tahoe-Yellow-Screen-Research.md) · [wiki/Mac-Pro-Tahoe-Yellow-Screen.md](./wiki/Mac-Pro-Tahoe-Yellow-Screen.md)

트랙 **A**는 문서 `.stage-A`만. 3802/Non-Metal **코드는 M/N 라이브** (재구현 금지).  
루트패치는 **Tahoe (`is_tahoe`)만** — Sequoia에서 `X86_EXTREME`이어도 루트 no-op.

---

## INTEGRATE 스냅샷

| 축 | 상태 |
|----|------|
| STAGE-WORKFLOW | **정식화** (`52f7298` + `9e896f3` touch-up) |
| A 문서 | INTEGRATE |
| M / N / F | Tahoe 옵트인 **live** |
| D Tools diagnostics | **live** (`30203ab` promote) |

### 다음 큐

**H → J → L5-R/B → I↔K** (배포/루트 에이전트와 코드 충돌 시 문서만 선행)

---

## 0. 극한도전 — 성공 기준

| # | 기준 | 상태 (문서 시점) |
|---|------|------------------|
| 1 | WindowServer **정상 색** | 미달 — compositor 본질 미해결 |
| 2 | **가속** (31001 / **3802** / **Non-Metal**) | 31001 부분; **3802/NM = 기본 `{}` + 옵트인 live** (`52f7298`) — 실기 스모크 대기 |
| 3 | **Safari** Pre-AVX Fix | 경로 존재 (cf7f26f) |
| 4 | **재부팅 안정** | 실기 ≥2 cold boot 필요 (Tahoe) |

### 가드 정책 — 기본 경로 안전 / 옵트인 해금

| 항목 | 기본 | 옵트인 |
|------|------|--------|
| **Metal 3802** Tahoe shared | **`return {}`** | `X86_EXTREME` + `X86_TAHOE_3802` |
| **Non-Metal** Tahoe shared | **`return {}`** | `X86_EXTREME` + `X86_TAHOE_NONMETAL` |
| SkyLight/CoreDisplay 바이트패치 | 기본 비활성 | extreme 옵트인 허용 (영구 절대금지 아님) |
| EFI agdpmod 재구현 | D=검증만 | d3a7b87 유지 |

OCLP 세대 해금: [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md).  
트랙 ID(A–N)와 복구 후보(R\*)는 다른 네임스페이스.

---

## 1. Executive Summary

전체 화면 노란/주황은 **GPU 세대(GCN LUT만) 문제가 아니다.** Vega 64(unpublished / reporter: 내부)와 OCLP-T2 #194(RX570)가 동일 증상을 보이며, 본질은 **Tahoe WindowServer ↔ SkyLight ↔ CoreDisplay ↔ ColorSync(ICC) ↔ RenderBox/Opaque metallib** 합성 파이프라인이다. pre-AVX는 **Safari/APFS**와 겹칠 수 있으나 노란 화면의 직접 원인이 아니다.

| 이미 된 완화 (재구현 금지) | 역할 | 성공 기준 기여 | 커밋 |
|---------------------------|------|----------------|------|
| WindowServer cache `uchg` | Opaque 셰이더 캐시 재생성 | 1 부분 | edf958f |
| ColorSync sRGB 링크 | ICC 폴백 | 1 tint만 | edf958f |
| KDKlessWorkaround | MTL 누락 시 WS 루프 | 4 | edf958f |
| EFI `agdpmod`/`shikigva` | AGDC yellow 완화 | 1·4 부분 | d3a7b87 |
| Safari RestrictEvents | WebContent SIGILL | **3** | cf7f26f |
| Metal 3802 / Non-Metal Tahoe 가드 | 기본=안전 부팅; **옵트인만** 해금 | 2 (M/N) | shared + `X86_*` |
| RenderBox `default.metallib` 게이트 | OCLP #1176 iff payload | 2 조건부 | 368ff72 |

**코드 PoC (E/G):** RenderBox overwrite는 `RenderBox-<xnu>` 있을 때만. SkyLightPlugins는 SHA 핀만. 스톡 Tahoe SkyLight는 플러그인 폴더를 **로드하지 않음**.

---

## 2. 합성 파이프라인 (Tahoe XNU 25)

```
앱 / CA / Metal
        │  IOSurface / drawable
        ▼
WindowServer  ── Opaque shader cache ──► /private/var/folders/.../WindowServer/
        │
        ├─ SkyLight.framework   (private compositor)
        ├─ CoreDisplay.framework (디스플레이·색·AGDC 브리지)
        ├─ ColorSync.framework  (.icc / LUT / transform)
        └─ RenderBox.framework  (UI/Liquid Glass metallib: default.metallib)
                │
                ▼
        AMD MTLDriver.bundle / IOKit framebuffer (AGDC)  ← Vega 64 31001
```

### Sequoia (XNU 24) vs Tahoe (XNU 25)

| 계층 | Sequoia | Tahoe |
|------|---------|-------|
| Liquid Glass / RenderBox | 기존 metallib | **새 셰이더** — `RenderBox-25` 필요 |
| Metal 31001 shared | Ventura+ 일부 | PR #1176 overwrite; PSP에 폴더 없으면 no-op |
| Non-Metal SkyLight 10.14.6-N | 동작(제한 UI) | **기본 shared 가드**; `X86_TAHOE_NONMETAL` 옵트인(N) |
| PatcherSupportPkg | 12.5-24 | #16/#18 DRAFT — `12.5-25`·`RenderBox-25` 공백 |

### `disable_window_server_caching`

1. WS 캐시 디렉터리 삭제  
2. `chflags uchg`로 재기록 차단  

**부족:** 소스 metallib/ABI가 Tahoe와 안 맞으면 재생성이 다시 깨짐; solid yellow ICC 실패와는 별개; `default.metallib` 부재는 미해결.

---

## 3. 심볼·파일 경로

| 경로 | 역할 | 트랙 |
|------|------|------|
| `/System/Library/CoreServices/WindowServer` | 합성 | B |
| `SkyLight.framework` / `SkyLightOld.dylib` | compositor / Non-Metal stub 마커 | B / H |
| `CoreDisplay.framework` | 디스플레이·색 | C |
| `ColorSync.framework` + sRGB ICC | LUT/ICC | C |
| `RenderBox.../default.metallib` | Opaque/Liquid Glass | E |
| `/Library/Application Support/SkyLightPlugins/` | moraea 슬롯 | H |
| AMD Vega MTL/kext | 가속 | E / F / G |

**공개 심볼 바늘:** `ColorSyncProfileCreateWithURL`, `ColorSyncTransformCreate`, `CGColorSpaceCreateWithICCData`, `CGColorSpaceCreateWithName`, `CGDisplayGammaTable`  
#194 사설 CoreDisplay 훅 이름 **미공개** → 추측 바이트패치 금지.

---

## 4. 커뮤니티 근거

| 소스 | URL | 요지 |
|------|-----|------|
| OCLP-T2 #194 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194 | 노란 화면; ICC/LUT; PSP 공백 |
| OCLP-T2 #234 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/234 | 검은+커서 (J — 분리) |
| OCLP #1167 | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 | Tahoe 로드맵 |
| OCLP PR #1176 | https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1176 | RenderBox metallib |
| PSP #16/#18 | dortania/PatcherSupportPkg | Tahoe DRAFT |
| MetallibSupportPkg | dortania / NiSeullent | **3802** — Vega 31001과 별개 (K) |
| moraea non-metal-frameworks | github.com/moraea/non-metal-frameworks | Tahoe **미완** |
| ASentientBot monterey | github.com/ASentientBot/monterey | SkyLightPlugins v2 |
| Safari26-PreAVX-Fix | kilinccagatay | 기준 3 |
| Vega 64 | unpublished / reporter: 내부 | GPU 무관 compositor |

---

## 5. 복구 후보 (R\*) — 트랙 A–N과 별개

| ID | 후보 | 난이도 | 조치 | 트랙 |
|----|------|--------|------|------|
| **R1** | AGDC / agdpmod | 낮음 | EFI 유지 | D |
| **R2** | software compositor boot-arg | — | 문서화된 플래그 없음 | A |
| **R3** | RenderBox metallib | 중 | 페이로드 게이트 | E/F |
| **R4** | LUT 바이트패치 | 높음 | **금지** | B/C 심볼만 |
| **R5** | SkyLight 10.14.6 / Non-Metal shared | 매우 높음 | **기본 가드**; `X86_TAHOE_NONMETAL` | **N** |
| **R6** | SkyLightPlugins | 중 | SHA 핀; 스톡 Tahoe 무효 | H |
| **R7** | Metal 3802 Tahoe shared | 높음 | **기본 가드**; `X86_TAHOE_3802` + Metallib | **M** / K |

→ [SkyLight-LUT-Tracks.md](./SkyLight-LUT-Tracks.md)

---

## 6. PoC · Autopilot 단계

1. EFI: agdpmod/shikigva + RestrictEvents (pre-AVX) — **재구현 말고 검증**  
2. `RenderBox-25` / `12.5-25` 오버레이 실장 (F)  
3. 루트패치: Vega 31001 + compositor mitigations + RenderBox iff present (E/G)  
4. WS cache + ColorSync sRGB (이미 있음)  
5. 재부팅 ×2 · `detect --json` · diagnostics (L/G)  
6. 기준 1–4 미달 시 Tracks에 블로커 기록 → 해당 트랙 재배분 (A)

```bash
python3 -m unittest x86.graphics.test_skylight_lut x86.graphics.test_yellow_screen
python3 -m x86 detect --json
```

---

## 7. 실패 모드

| 모드 | 대응 |
|------|------|
| RenderBox-25 없음 | no-op 정상 → F가 페이로드 확보 |
| Non-Metal SkyLight **기본** 강제 | **KP** — 기본 가드; N 옵트인만 |
| Plugins만 설치 | 스톡 SkyLight 무시 → H |
| 3802 metallib→31001 | ABI 불일치 — K/M과 E 분리 |
| env 없이 3802/NM 해금 | 정책 위반 — PR 거부 |
| 추측 바이트패치 | 금지 |

---

## 8. 코드 맵 (소유는 트랙 B–N)

| 파일 | 역할 | 트랙 |
|------|------|------|
| `x86/graphics/skylight_lut.py` | RenderBox·플러그인 게이트 | E/G |
| `sys_patch/.../metal_31001.py` | 조건부 overwrite | E |
| `sys_patch/.../metal_3802.py` | Tahoe 가드 / **옵트인 해금** | **M** |
| `sys_patch/.../non_metal*.py` | Tahoe 가드 / **옵트인 해금** | **N** |
| `sys_patch/.../tahoe_yellow_screen.py` | compositor 마커 | G |
| `x86/graphics/yellow_screen.py` | mitigations·detect | G |
| `efi_builder` agdp | EFI | D 읽기만 |

---

## 9. 트랙 A vs 코드 vs 장기

**A (문서):** Mission Control · Research · Roadmap · **기본 가드 / `X86_*` 옵트인** 정책.  
**이미 코드 (E/G 등):** edf958f · d3a7b87 · cf7f26f · 368ff72.  
**M/N (코드 담당):** `X86_TAHOE_3802` / `X86_TAHOE_NONMETAL` 해금 — A는 구현하지 않음.  
**장기:** F 실장 · H 로더 · B/C 심볼 · L 재부팅 · I UI (N 연계).

---

## 10. 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 초안 — 파이프라인·RenderBox 게이트 |
| 2026-09-04 | 극한도전 Mission · 성공 기준 4항 · R\* · Tracks A–L 링크 |
| 2026-09-04 | 3802/Non-Metal **옵트인 해금** · 트랙 M·N · OCLP 세대 서사 |


---

**Track E:** [Tahoe-Metallib-Opaque-Shader.md](./Tahoe-Metallib-Opaque-Shader.md) — LegacyMetal31001 no-op, Opaque↔WS cache, safe metallib preflight.
