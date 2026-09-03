# Tahoe SkyLight / WindowServer LUT·셰이더 합성 — 심층 Research

> **프로젝트:** 26x86 (`NiSeullent/26x86`)  
> **작성일:** 2026-09-04  
> **목표:** LUT/Opaque 셰이더 합성 **복구**를 위한 근거·실패 모드·PoC  
> **관련:** [Tahoe-Yellow-Screen-Research.md](./Tahoe-Yellow-Screen-Research.md) · [wiki/Mac-Pro-Tahoe-Yellow-Screen.md](./wiki/Mac-Pro-Tahoe-Yellow-Screen.md)

---

## 1. Executive Summary

전체 화면 노란/주황은 **GPU 세대(GCN LUT만) 문제가 아니다.** Vega 64(unpublished / reporter: 내부)와 OCLP-T2 #194(RX570)가 동일 증상을 보이며, 본질은 **Tahoe WindowServer ↔ SkyLight ↔ CoreDisplay ↔ ColorSync(ICC) ↔ RenderBox/Opaque metallib** 합성 파이프라인이다.

| 이미 된 완화 (재구현 금지) | 역할 | LUT/셰이더 복구? |
|---------------------------|------|------------------|
| WindowServer cache `uchg` | 손상 Opaque 셰이더 캐시 재생성 유도 | **부분** — 원인은 남음 |
| ColorSync sRGB 링크 | ICC 폴백 | tint만; solid yellow에는 UI 불가 |
| KDKlessWorkaround | MTL 누락 시 WS 루프 | 합성 자체 아님 |
| EFI `agdpmod`/`shikigva` | AGDC yellow 완화 | framebuffer 경로 |
| Metal 3802 / Non-Metal Tahoe 가드 | KP 방지 | **유지 필수** |

**이번에 코드로 넣은 것:** OCLP PR #1176과 동일한 **RenderBox `default.metallib` overwrite**를 **페이로드가 디스크에 있을 때만** 활성화. SkyLightPlugins는 **SHA-256 핀 + 스템 허용목록**만 설치(추정 바이트 금지). 스톡 Tahoe SkyLight는 플러그인 폴더를 **로드하지 않음**.

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
        AMD MTLDriver.bundle / IOKit framebuffer (AGDC)
```

### Sequoia (XNU 24) vs Tahoe (XNU 25)

| 계층 | Sequoia | Tahoe |
|------|---------|-------|
| Liquid Glass / RenderBox | 기존 metallib | **새 셰이더·API** — 31001용 `RenderBox-25` 필요 |
| Metal 31001 shared | Ventura+ 일부 | OCLP PR #1176이 RenderBox overwrite 추가; PSP에 폴더 없으면 no-op |
| Non-Metal SkyLight 10.14.6-N | 동작(제한 UI) | **shared 가드** — IOGPU 제거 등과 함께 KP |
| PatcherSupportPkg | 12.5-24 | #16/#18 DRAFT — `12.5-25`·`RenderBox-25` 공백이 흔함 |

### `disable_window_server_caching`이 하는 일 vs 부족한 점

**코드:** `sys_patch_helpers.disable_window_server_caching`

1. `/private/var/folders/*/*/*/WindowServer/com.apple.WindowServer` 삭제  
2. 상위 `WindowServer` 디렉터리에 `chflags uchg` → 캐시 재기록 차단  

**의도:** 레거시 AMD에서 **손상된 Opaque 셰이더**가 캐시에 고정되는 것을 막고 재생성.

**부족:**

- RenderBox / SkyLight **소스 metallib·프레임워크 ABI**가 Tahoe와 안 맞으면 재생성이 또 깨짐  
- ColorSync/ICC LUT 실패(solid yellow)와는 별개  
- Metal 31001 `default.metallib` 부재는 건드리지 않음  

---

## 3. 심볼·파일 경로

| 경로 | 역할 |
|------|------|
| `/System/Library/CoreServices/WindowServer` | 합성 프로세스 |
| `/System/Library/PrivateFrameworks/SkyLight.framework/.../SkyLight` | 윈도 합성 |
| `.../SkyLightOld.dylib` | **Non-Metal stub 마커** (`gui_support.py`) |
| `/System/Library/Frameworks/CoreDisplay.framework/.../CoreDisplay` | 디스플레이/색 |
| `/System/Library/Frameworks/ColorSync.framework/.../ColorSync` | ICC/LUT |
| `/System/Library/PrivateFrameworks/RenderBox.framework/.../Resources/default.metallib` | UI Opaque/Liquid Glass 셰이더 |
| `/Library/Application Support/SkyLightPlugins/` | moraea 플러그인 슬롯 (패치된 SkyLight만) |
| `/System/Library/ColorSync/Profiles/sRGB Profile.icc` | 런타임 sRGB 폴백 원본 |
| `/Library/ColorSync/Profiles/Displays/sRGB Profile.icc` | 26x86 심볼릭 링크 대상 |

**공개 심볼 바늘 (nm 픽스처):** `ColorSyncProfileCreateWithURL`, `ColorSyncTransformCreate`, `CGColorSpaceCreateWithICCData`, `CGColorSpaceCreateWithName`, `CGDisplayGammaTable`  
#194의 “CoreDisplay color management hooks” **사설 심볼 이름은 공개되지 않음** → 추측 바이트패치 금지.

**호스트 인벤토리:** `serialize_skylight_lut_fields(..., probe_host_symbols=True)` → `inventory_host_compositor_symbols()`.

---

## 4. 커뮤니티 근거

| 소스 | URL | 요지 |
|------|-----|------|
| OCLP-T2 #194 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194 | MacPro5,1/6,1 노란 화면; ICC/LUT 가설; PSP 미병합; GPUCompanionBundles 없음 |
| OCLP #1167 | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 | Tahoe 로드맵 — 31001/3802/Non-Metal; Liquid Glass |
| OCLP PR #1176 | https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1176 | **RenderBox metallib** → `metal_31001` / `renderbox.py` |
| PSP #16 / #18 | https://github.com/dortania/PatcherSupportPkg/pull/16 · [/18](https://github.com/dortania/PatcherSupportPkg/pull/18) | Tahoe 바이너리 DRAFT |
| MetallibSupportPkg | https://github.com/dortania/MetallibSupportPkg · NiSeullent/26x86-MetallibSupportPkg | **3802** metallib — 31001 RenderBox와 별개 |
| LegacyMetal31001 no-op | 26x86 `metal_31001.py` (구) | 페이로드 없으면 preflight 실패 → 의도적 빈 dict |
| moraea non-metal-frameworks | https://github.com/moraea/non-metal-frameworks | Tahoe **미완** (OCLP #1167 Non-Metal UI 다운그레이드) |
| ASentientBot monterey | https://github.com/ASentientBot/monterey | SkyLightPlugins v2 — **패치된 SkyLight**가 `.dylib`+`.txt` 로드 |
| AGDCDiagnose yellow | WhateverGreen `agdpmod=vit9696`/`pikera` | framebuffer board-id — compositor LUT와 별층 |

**Vega 64 (unpublished / reporter: 내부):** Mac Pro 소켓 `0x687F` + Tahoe에서 동일 solid yellow → GCN 전용 LUT 가설 기각 → **공통 SkyLight compositor**.

---

## 5. 복구 후보 평가 (난이도순)

| ID | 후보 | 난이도 | 근거 | 26x86 조치 |
|----|------|--------|------|------------|
| **E** | IOKit AGDC / `agdpmod` | 낮음 | WEG 문서화; yellow 완화 | **이미 EFI** — 유지 |
| **C** | software compositor boot-arg | — | Apple **문서화된 WS Metal 합성 off 플래그 없음**. `useMetal=no`는 Non-Metal Enforcement → Tahoe 차단. `ngfxgl`/`-igfxvesa`는 벤더 한정 | **구현 안 함** (문서만) |
| **D** | RenderBox / metallib | 중 | OCLP PR #1176; `RenderBox-<xnu>/.../default.metallib` | **페이로드 게이트 PoC 활성화** |
| **B** | CoreDisplay/SkyLight LUT 바이트패치 | 높음 | #194 가설만; 사설 심볼 미공개 | **금지** |
| **A** | SkyLight.framework 10.14.6 다운 | 매우 높음 | Non-Metal 묶음(IOSurface/IOGPU 제거) → Tahoe KP | **가드 유지** |
| SkyLightPlugins dylib | 중·조건부 | moraea 프로토콜 | SHA 핀만 설치; 스톡 Tahoe에선 **무효** |

---

## 6. PoC 단계 (실행)

1. **페이로드 확보:** `RenderBox-25/.../default.metallib`를 PSP 포크 또는 OCLP nightly에서 받아  
   `payloads/Kexts/Community/Tahoe-Yellow-Screen/Universal-Binaries/RenderBox-25/` 에 배치 (Apple 바이너리 재배포 라이선스 준수).  
2. `dmg_mount`가 Universal-Binaries에 ditto (`tahoe_psp_overlay_copy_pairs` + `renderbox_overlay_copy_pairs`).  
3. 루트패치: `LegacyMetal31001` → `Metal 31001 Common` overwrite.  
4. 기존 mitigations: WS cache + ColorSync sRGB + EFI agdpmod.  
5. 재부팅 후 `Tools/collect_graphics_diagnostics.command` · `python3 -m x86 detect --json` (`renderbox_metallib_present`).  

**SkyLightPlugins PoC (장기):** Tahoe용 패치 SkyLight(또는 별도 로더) + `COMPOSITOR_PLUGIN_SHA256`에 핀 등록 후에만 dylib 설치.

### 단위 테스트

```bash
cd 26x86 && python3 -m unittest x86.graphics.test_skylight_lut x86.graphics.test_yellow_screen
```

픽스처: tempfile `RenderBox-25` 트리; DropboxHack 거부; SHA 미핀 거부.

---

## 7. 실패 모드

| 모드 | 증상 | 대응 |
|------|------|------|
| `RenderBox-25` 없음 | `Metal 31001 Common` 미주입 (정상 no-op) | 오버레이에 metallib 추가 |
| 잘못된 metallib | 노란 화면/WS crash | 해시·빌드 검증 후 롤백 |
| Non-Metal SkyLight 강제 | **커널 패닉** | 가드 유지 |
| SkyLightPlugins만 넣고 기대 | 변화 없음 (스톡 SkyLight) | 문서대로 Non-Metal stub 필요 |
| 3802 MetallibSupportPkg로 31001 대체 | ABI/셰이더 세대 불일치 | 3802 가드 유지 |
| 추측 CoreDisplay 바이트패치 | SIP/서명/WS 크래시 | 금지 |

---

## 8. 코드 맵

| 파일 | 역할 |
|------|------|
| `x86/graphics/skylight_lut.py` | RenderBox resolve, 플러그인 허용목록, 심볼 인벤토리 |
| `x86/graphics/test_skylight_lut.py` | 게이트·허용목록 단위 테스트 |
| `sys_patch/.../metal_31001.py` | 페이로드 있을 때만 OCLP overwrite |
| `sys_patch/.../tahoe_yellow_screen.py` | SHA 핀 플러그인만 설치 |
| `x86/graphics/yellow_screen.py` | mitigations + overlay ditto에 RenderBox 포함 |

---

## 9. 이번에 넣은 것 vs 장기 R&D

**이번에:**

- RenderBox metallib **조건부** 훅 (근거: OCLP PR #1176)  
- SkyLightPlugins **안전 게이트** (DropboxHack을 LUT 해결책으로 쓰지 않음)  
- detect JSON: `renderbox_metallib_present` 등  
- 본 Research 문서 + wiki 링크  

**장기:**

- PatcherSupportPkg `RenderBox-25` / Tahoe MTL 병합  
- Tahoe 호환 SkyLight 플러그인 로더 (moraea Tahoe)  
- 사설 CoreDisplay LUT 심볼 RE (공개 심볼 확보 전 패치 금지)  
- Liquid Glass Non-Metal UI 우회  

---

## 10. 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 초안 — 파이프라인·후보 A–E·RenderBox 게이트 PoC |
