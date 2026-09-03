# Tahoe 노란 화면 / AVX / Metal 패치 조사 보고서

> **프로젝트:** 26x86 (`NiSeullent/26x86`)  
> **작성일:** 2026-09-04  
> **범위:** GitHub 이슈·외부 저장소·코드베이스 grep — 코드 대규모 수정 없음  
> **관련 문서:** [Tahoe-Graphics-Patch-Inventory.md](./Tahoe-Graphics-Patch-Inventory.md), [RESEARCH_SUMMARY.md](./RESEARCH_SUMMARY.md)

---

## 1. Executive Summary

macOS 26 Tahoe 업그레이드 후 **WindowServer/데스크톱 출력이 망가지는 현상**은 단일 원인이 아니라 **여러 독립 실패 경로**가 겹친 결과다.

| 증상 계열 | 대표 원인 | AVX와의 관계 |
|-----------|-----------|--------------|
| **전체 화면 단색 노란/주황** | **Tahoe WindowServer/SkyLight/CoreDisplay/ColorSync 합성 실패** (GPU 세대 무관). EFI `agdpmod` 미적용·PatcherSupportPkg kext 공백은 악화 요인. **Vega 64에서도 재현** (unpublished / reporter: 내부). OCLP-T2 #194는 MacPro5,1/6,1 + RX570도 GPU와 무관하게 보고 | **직접 인과 아님** |
| **검은 화면 + 커서만** | Broadwell iGPU + WindowServer 합성 실패 (`SkyLight`/`CoreDisplay`) | AVX2 부재 Mac에서 31001 패치 불완 | 
| **Safari/WebContent SIGILL** | JavaScriptCore `ctiMasmProbeTrampoline`의 무조건 AVX `vmovaps` | **직접 인과** (pre-AVX CPU) |
| **루트패치 후 KP / 가속 없음** | Metal 3802 / Non-Metal shared 패치 Tahoe 미완 | APFS `NoAVXFSCompressionTypeZlib` 등 **별도** AVX 이슈 |

**26x86 현재 정책:** Tahoe에서 `metal_3802.py`, `non_metal*.py` shared 패치를 **의도적으로 차단** → 패닉/노란 화면 대신 **GPU 가속 없이 부팅**만 허용.

---

## 2. Safari26-PreAVX-Fix (kilinccagatay) 분석

**저장소:** https://github.com/kilinccagatay/Safari26-PreAVX-Fix

### 2.1 목적·범위

- Acidanthera **RestrictEvents** 포크 — Safari **26.6.1** WebContent의 `EXC_BAD_INSTRUCTION (SIGILL)` 해결
- **WindowServer/데스크톱 노란 화면과 무관** — README가 명시적으로 구분
- 검증 환경: MacPro5,1, 2×Xeon E5620 (Westmere, **AVX 없음**), Quadro K5000, macOS 15.7.9, OCLP 2.5.0 nightly

### 2.2 기술 메커니즘

| 항목 | 내용 |
|------|------|
| 기존 `revpatch=jsc` | JavaScriptCore AVX **기능 플래그** 숨김 (RestrictEvents b70aaa4) |
| 미해결 문제 | Safari 26.6.1 `ctiMasmProbeTrampoline`에 **조건 분기 없는** AVX `vmovaps` 32개 (XMM0–15 save/restore) |
| 패치 (v1.1.8) | 두 개의 **바이트 정확** 시그니처 블록을 legacy SSE `movaps`로 1:1 길이 치환 |
| 수정 파일 | `RestrictEvents/JavaScriptCore.hpp`, `RestrictEvents/RestrictEvents.cpp` |

핵심 인용 (TECHNICAL.md):

> Hiding AVX capability cannot protect a path whose generated machine code does not branch on that capability.

### 2.3 설치·스크립트

| 스크립트 | 역할 |
|----------|------|
| `Install Safari AVX Fix.command` | `scripts/install.sh` 래퍼 |
| `Verify Safari AVX Fix.command` | 로드된 RestrictEvents 1.1.8 확인 |
| `Restore Original RestrictEvents.command` | Desktop 백업에서 복원 |

**install.sh 안전 장치:**
- AVX CPU 거부 (`machdep.cpu.features`에 AVX 있으면 exit)
- Safari ≠ 26.6.1 거부
- 기존 OpenCore EFI + RestrictEvents + `revpatch`에 `jsc` 필수
- `EFI/OC/Kexts/RestrictEvents.kext`만 교체 — config.plist/NVRAM/루트패치 **미수정**
- SHA-256 검증: executable `5862fd1c5415fa94b6d0165e70200eae80ef9e3b1dd4d89220c669507d79f7ef`

### 2.4 26x86 적용 가능성

| 항목 | 판정 |
|------|------|
| MacPro5,1 + Safari 26.6.1 + pre-AVX | ✅ **즉시 시험 가능** (USB EFI, 루트패치 무관) |
| Tahoe 노란 화면 | ❌ **해당 없음** — GPU/CoreDisplay/WindowServer 경로 |
| upstream 통합 | 🟡 RestrictEvents PR 또는 26x86 EFI 번들 문서화 수준 |

---

## 3. GitHub 이슈·PR 수집

### 3.1 핵심 이슈 URL

| # | URL | 요약 |
|---|-----|------|
| OCLP #1167 | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 | **공식 Tahoe 로드맵** — Metal 31001/3802/Non-Metal, Liquid Glass 스크린샷, T2·Wi-Fi·USB 블로커 |
| OCLP-T2 #194 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194 | **Mac Pro 6,1 / iMac 2015 루트패치 후 노란 화면** — `GPUCompanionBundles` kext 없음, PatcherSupportPkg 미병합 |
| OCLP-T2 #234 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/234 | MacBookPro12,1 Broadwell — **검은 화면 + 커서**, WindowServer UI 합성 실패 |
| OCLP-T2 #161 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/161 | Metallib API → albert-mueller pyquick 포크, **Metal 3802 Metallib 부재** (OCLP-R) |
| hackdoc/OCLP-R #15 | https://github.com/hackdoc/OCLP-R/issues/15 | Tahoe Metallib 지원 — **3802 패치 없음** |
| PSP #16 | https://github.com/dortania/PatcherSupportPkg/pull/16 | Nov 2025 패치 바이너리 (31001 fixes, DRAFT) |
| PSP #18 | https://github.com/dortania/PatcherSupportPkg/pull/18 | Tahoe patchset (Modern Audio 등, DRAFT) |
| OCLP #1004 | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1004 | (과거) Kepler + **WindowServer crash** — Monterey 12.5 |
| TechPrototyper/OCLP #1 | https://github.com/TechPrototyper/OpenCore-Legacy-Patcher/issues/1 | Metal 31001 / Legacy GCN Tahoe 작업 로그 |
| Acidanthera #2499 | https://github.com/acidanthera/bugtracker/issues/2499 | Tahoe FileVault 자동 활성화 (T2 전용 OS 가정) |

### 3.2 OCLP-T2 #194 핵심 인용·증거

**DrDonk:**
> there are no compatible KEXTs present … ton of unmerged files for Tahoe [PatcherSupportPkg#18] and [#16]. Also probably need a MetallibSupportPkg update.

**WhiteLighter78 (MacPro5,1/6,1, RX570):**
> patcher recognizes the proper GPU and patches accordingly … same yellow screen after patches … `no kexts found in GPUCompanionBundles`

**Medelcartelinc (색상 LUT 가설):**
> legacy AMD Metal drivers failing to parse Tahoe's updated CoreDisplay.framework color management hooks … Color Lookup Table (LUT) fails to load default .icc … permanent yellow/orange tint

**대응 시도:** Display 프로필 → Generic RGB — **전체 노란 화면에서는 UI 접근 불가**로 실패 보고 다수

**albert-mueller:**
> PatcherSupportPkg from OCLP-Plus is still the only one that fully works with Tahoe at least on some GPUs … missing patches for MacPro5,1-6,1

### 3.3 OCLP #1167 Graphics 분류 (Dortania 공식)

| Metal 세대 | GPU / CPU |
|------------|-----------|
| **Metal 31001** | Intel Broadwell/Skylake, AMD Legacy GCN, non-AVX2 modern GCN |
| **Metal 3802** | Intel Ivy Bridge/Haswell, Nvidia Kepler |
| **Non-Metal** | Intel Iron Lake/Sandy Bridge, AMD TeraScale, Nvidia Tesla/Web Drivers |

---

## 4. 용어 정리: 3802 vs 31001 vs 8302 vs 31002

| 명칭 | 출처 | 26x86 코드 매핑 |
|------|------|-----------------|
| **Metal 3802** | OCLP `METAL_3802_GRAPHICS` | Ivy/Haswell iGPU, Kepler dGPU |
| **Metal 31001** | OCLP `METAL_31001_GRAPHICS` | Broadwell/Skylake, GCN, Polaris*, Vega |
| **Metal 8302** | OCLP-T2 Wiki, 26x86 wiki | **커뮤니티 버킷** — “2012–2014 Mac 그래픽 미완” (3802+31001 혼재) |
| **31002** | 사용자/포럼 언급 | **코드베이스에 상수 없음** — 31001 또는 Apple 내부 compiler 빌드 번호 혼동 가능 |

`HardwareVariantGraphicsSubclass` (`hardware/base.py`):

```python
NON_METAL_GRAPHICS   = "Non-Metal Graphics"
METAL_3802_GRAPHICS  = "Metal 3802 Graphics"
METAL_31001_GRAPHICS = "Metal 31001 Graphics"
```

---

## 5. 패치 매트릭스 (GPU/기기 → 필요 패치)

### 5.1 Metal 3802

| GPU | 대표 Mac | Sequoia (OCLP 2.4) | Tahoe 26 (26x86) | 필요 패치 |
|-----|----------|--------------------|------------------|-----------|
| Intel Ivy Bridge iGPU | MacBookPro10,x, iMac13,x | ✅ shared 3802 + metallib | ❌ **shared 가드** | `LegacyMetal3802` 3단계 + `MetallibSupportPkg` |
| Intel Haswell iGPU | MacBookPro11,x, iMac14,x | ✅ | ❌ 가드 | ↑ |
| Nvidia Kepler | MacBookPro11,3, cMP+Kepler | ✅ + KDK | ❌ 가드, KDK metallib 요구 | ↑ + GeForce.kext downgrade |

**Tahoe shared 패치 (가드 해제 시):** Metal.framework 12.5-3802, 13.2.1 downgrade, 80+ `.metallib` → NiSeullent/26x86-MetallibSupportPkg

### 5.2 Metal 31001 (“8302” 클래스)

| GPU | 대표 Mac | Sequoia | Tahoe 26 | 필요 패치 |
|-----|----------|---------|----------|-----------|
| Intel Broadwell | MacBookPro12,1 | ✅ kext | 🟡 kext만, **shared no-op** | AMD7000Controller 등 + WindowServer/CoreDisplay (미완) |
| Intel Skylake | MacBookPro13,x | ✅ | 🟡 | ↑ |
| AMD Legacy GCN (7000–9000) | MacPro6,1 D300/D500/D700, iMac15,1 | ✅ | 🟡 kext + **EFI agdpmod** | `_amd_mxm_patch`, CoreDisplay LUT |
| AMD Polaris | MacBookPro14,3 (AVX2 없을 때) | ✅ | 🟡 | Polaris kext + interposer |
| AMD Vega | iMac Pro, **cMP 소켓 Vega 64** | ✅ | 🟡 kext + **EFI agdpmod** — **노란 화면 재현됨** (unpublished / reporter: 내부) | `amd_vega.py` 31001 kext; compositor는 루트패치로 미해결 |

**Tahoe 한계:** `LegacyMetal31001._patches_metal_31001_common()` = **의도적 no-op** (RenderBox Tahoe payload 부재)

### 5.3 Non-Metal

| GPU | 대표 Mac | Sequoia | Tahoe 26 | 필요 패치 |
|-----|----------|---------|----------|-----------|
| Intel Sandy/Iron Lake | 2011 iMac/MBP | ✅ (UI 제한) | ❌ **전체 shared 가드** | SkyLight/CoreDisplay/IOSurface downgrade |
| AMD TeraScale | 2011 iMac | ✅ | ❌ | non-metal-frameworks (moraea) |
| Nvidia Tesla/Web | cMP GTX 계열 | ✅ | ❌ | WebDriver + IOAccel |

Liquid Glass: Non-Metal은 **UI 다운그레이드**만 가능 (OCLP #1167)

### 5.4 Mac Pro 특수 (사용자 시나리오)

| 모델 | CPU | GPU | Tahoe 증상 | 권장 패치 경로 |
|------|-----|-----|------------|----------------|
| MacPro5,1 | Westmere (**no AVX**) | Kepler / GCN / **Vega 64 애프터마켓** / Polaris | 노란 화면 + (별도) Safari SIGILL | **분리:** EFI agdpmod/shikigva + Vega/GCN kext; Safari는 RestrictEvents. 노란 화면은 **GPU 무관 compositor** |
| MacPro6,1 | Ivy Bridge (**no AVX2**) | D700 (GCN) 또는 소켓 Vega | #194 + Vega 64 동일 증상 | EFI `agdpmod` + 31001 kext; PatcherSupportPkg Tahoe payload |

---

## 6. AVX 부재 ↔ WindowServer/Metal 실패 인과관계

### 6.1 직접 인과 (커뮤니티·코드 증거)

| 계층 | 메커니즘 | 증거 |
|------|----------|------|
| **Safari/WebKit** | pre-AVX CPU에서 AVX opcode 실행 → SIGILL | Safari26-PreAVX-Fix TECHNICAL.md, `c5 f8 29` = VEX vmovaps |
| **APFS** | `FSCompressionTypeZlib` AVX 경로 | `NoAVXFSCompressionTypeZlib` kext (`constants.py`) |
| **Polaris 31001** | AVX2 없는 CPU에서 Polaris Metal | `amd_polaris.py` AVX2 게이트 |

### 6.2 간접/혼동 (AVX와 무관하지만 “가속 불가”로 묶임)

| 계층 | 메커니즘 | 증거 |
|------|----------|------|
| **WindowServer** | legacy kext + Tahoe CoreDisplay/SkyLight 불일치 → UI surface 미합성 | OCLP-T2 #234 Medelcartelinc: `-igfxvesa` 진단 제안 |
| **색상/LUT** | CoreDisplay ICC/LUT 파싱 실패 → **노란/주황 전체 화면** | OCLP-T2 #194 Medelcartelinc |
| **EFI GPU 경로** | `agdpmod`/`shikigva`가 wrong PCI path → AGDCDiagnose yellow | `efi_builder/graphics_audio.py:533–539`, `:167–172` |
| **PatcherSupportPkg** | Tahoe용 kext 바이너리 미병합 → companion bundle 없음 | DrDonk #194, PSP #16/#18 DRAFT |

### 6.3 WhiteLighter78 가설 (AVX2 / Ivy Bridge)

> due to the CPU being Ivy Bridge and lacking AVX2, no matter what GPU is there

**평가:** WhiteLighter78의 “GPU가 뭐든 Ivy Bridge라서”는 **부분적으로 맞음** — 다만 원인은 AVX2 부재가 아니라 **Tahoe compositor**. **Vega 64(unpublished / reporter: 내부)** 와 #194 RX570이 GCN LUT 가설을 기각한다. AVX2는 Polaris 등 **일부 31001 kext 게이트**에만 해당. Safari/APFS는 **별도** AVX 경로.

### 6.3.1 Vega 64 재현 (미공개)

| 항목 | 내용 |
|------|------|
| **상태** | unpublished / reporter: 내부 (공개 GitHub URL 없음) |
| **구성** | Mac Pro 소켓 **Vega 64** (`pci_data.vega_ids` `0x687F`) + Tahoe |
| **증상** | 전체 화면 노란/주황 — GCN 전용 LUT 가설과 불일치 |
| **26x86 경로** | `amd_vega.py` (Metal 31001 kext+OpenCL). EFI는 `graphics_audio.py` agdpmod/shikigva. **루트 Vega 패치만으로는 compositor를 고치지 못함** |

### 6.4 인과 관계 다이어그램

```
[Tahoe 업그레이드]
        │
        ├─► 공통 compositor 실패 (WindowServer / SkyLight / CoreDisplay / ColorSync·ICC)
        │         ▲ GCN · Polaris(RX570) · Vega 64 모두 재현
        │         ▲ PatcherSupportPkg kext 공백이 악화
        │
        ├─► EFI agdpmod/shikigva 누락 또는 잘못된 PCI path ──► AGDCDiagnose yellow (완화 가능)
        │
        ├─► Metal 3802/Non-Metal shared (Tahoe) ──► 26x86 가드 ──► 가속 없음 (의도)
        │
        └─► [별도] pre-AVX CPU + Safari 26.6.1 ──► JSC SIGILL (Safari26-PreAVX-Fix)
                    │
                    └─► WindowServer와 무관 — WebContent 프로세스만
```

---

## 7. 26x86 코드베이스 grep 결과

### 7.1 그래픽/Metal 핵심 파일

| 경로 | 역할 |
|------|------|
| `sys_patch/patchsets/shared_patches/metal_3802.py` | 3802 shared — **Tahoe `return {}` 가드** |
| `sys_patch/patchsets/shared_patches/metal_31001.py` | 31001 shared — **no-op** |
| `sys_patch/patchsets/shared_patches/non_metal.py` | Non-Metal — **Tahoe 가드** |
| `sys_patch/patchsets/shared_patches/non_metal_*.py` | IOAccel, CoreDisplay, Enforcement — **Tahoe 가드** |
| `sys_patch/patchsets/hardware/graphics/*.py` | GPU별 kext downgrade (14 파일) |
| `sys_patch/patchsets/detect.py` | Metal/Non-Metal 혼합 GPU strip, metallib 요구 |
| `support/metallib_handler.py` | NiSeullent/26x86-MetallibSupportPkg manifest |
| `efi_builder/graphics_audio.py` | **노란 화면 EFI 완화** — MacPro5,1/6,1 + GCN/Polaris/Vega `agdpmod`/`shikigva` |
| `constants.py` | `NoAVXFSCompressionTypeZlib`, `tahoe_ui_render`, USB-Map-Tahoe |
| `Tools/collect_graphics_diagnostics.command` | WindowServer/CoreDisplay 로그 수집 |

### 7.2 Tahoe 안전 가드 (코드 인용)

`metal_3802.py` / `non_metal.py`:

```python
if self._xnu_major >= os_data.tahoe.value:
    # ... cause kernel panics on macOS 26, Tahoe.
    return {}
```

### 7.3 노란 화면 EFI 완화 (코드 인용)

`efi_builder/graphics_audio.py` — MacPro6,1 등:

> without it, any boot needing GPU compositing … renders a solid yellow/garbled screen instead of finishing.

---

## 8. 즉시 적용 vs 장기 R&D

### 8.1 즉시 적용 가능 (사용자/운영)

| # | 조치 | 대상 | 리스크 |
|---|------|------|--------|
| 1 | **Tahoe 루트패치 전** EFI 재빌드 — MacPro6,1/iMac15,x GCN `agdpmod` 확인 | #194 노란 화면 | 낮음 |
| 2 | `Tools/collect_graphics_diagnostics.command` 실행 후 WindowServer/CoreDisplay 로그 공유 | 모든 그래픽 이슈 | 없음 (read-only) |
| 3 | MacPro5,1 + Safari 26.6.1: [Safari26-PreAVX-Fix](https://github.com/kilinccagatay/Safari26-PreAVX-Fix) USB EFI | Safari SIGILL | 중간 — 실험 kext |
| 4 | **MetallibSupportPkg** manifest 최신 확인 (`NiSeullent/26x86-MetallibSupportPkg`) | 3802 Mac Sequoia→Tahoe | 네트워크 |
| 5 | macOS 업데이트 후 **KDK + Metallib + 루트패치 재적용** | 전체 | Known-Issues.md |
| 6 | Metal 3802/Non-Metal Mac: Tahoe에서 **가속 없이 부팅** 기대 (가드 존중) | 2011–2014 | UX 제한 |

### 8.2 단기 R&D (26x86 포크)

| # | 작업 | 의존성 |
|---|------|--------|
| 1 | PatcherSupportPkg Tahoe fork 통합 (OCLP-Plus + PSP #16/#18) | DrDonk/gandolf243 협력 |
| 2 | `LegacyMetal31001` Tahoe RenderBox/metallib 파이프라인 | PatcherSupportPkg payload |
| 3 | `metal_3802.py` Tahoe 가드 해제 전 **KP/yellow 회귀 테스트** | Metallib 26.x 완성 |
| 4 | OCLP-T2 #194 재현 — `GPUCompanionBundles` 로그 + kext 목록 diff | 실제 MacPro6,1 |
| 5 | Safari26-PreAVX-Fix → 26x86 docs/EFI optional bundle 문서화 | upstream RestrictEvents |

### 8.3 장기 R&D

| # | 작업 | 비고 |
|---|------|------|
| 1 | Non-Metal + Liquid Glass UI 우회 (moraea non-metal-frameworks Tahoe) | OCLP #1167 |
| 2 | Core 2 Duo: AAAMouSSE/telemetrap 재작성 | Tahoe 부팅 불가 |
| 3 | T2 Mac: AppleKeyStore SEP + APFS (#69, #130) | 데스크톱 미도달 |
| 4 | RestrictEvents `jsc` trampoline 패치 upstream (Acidanthera) | Safari 버전별 시그니처 유지 |
| 5 | CoreDisplay LUT 바이너리 패치 (GCN yellow) | 역공학 |

---

## 9. 권장 진단 순서 (MacPro5,1 / 6,1 + Tahoe)

1. **증상 분류:** 전체 노란 vs 검은+커서 vs Safari만 crash vs KP
2. **EFI:** OpenCore에서 `agdpmod`/`shikigva`가 **실제 dGPU PCI path**에 있는지 (`graphics_audio.py` 로직)
3. **루트패치 로그:** `GPUCompanionBundles`, 적용된 patchset 이름 (3802/31001/Non-Metal)
4. **WindowServer:** `log show --predicate 'process == "WindowServer"' --last 30m`
5. **CPU:** `sysctl machdep.cpu.features` — AVX 유무 → Safari/APFS 분기
6. **Metallib:** `/Library/Application Support/26x86/MetallibSupportPkg` 설치 여부
7. **Safari crash:** DiagnosticReports에서 `ctiMasmProbeTrampoline` + `SIGILL` 확인

---

## 10. 참고 링크

| 리소스 | URL |
|--------|-----|
| Safari26-PreAVX-Fix | https://github.com/kilinccagatay/Safari26-PreAVX-Fix |
| 26x86-MetallibSupportPkg | https://github.com/NiSeullent/26x86-MetallibSupportPkg |
| moraea 3802-Metal-15 | https://github.com/moraea/misc-patches/tree/main/3802-Metal-15 |
| moraea non-metal-frameworks | https://github.com/moraea/non-metal-frameworks |
| OCLP-T2 Wiki (8302 경고) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki |
| pyquick Metallib (Tahoe) | https://github.com/pyquick/MetallibSupportPkg |
| albert-mueller Metallib API | https://albert-mueller.github.io/ |

---

## 11. 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 초안 — GitHub 이슈·Safari26-PreAVX-Fix·26x86 코드 grep 종합 |
| 2026-09-04 | Vega 64 재현(unpublished / reporter: 내부) — 본질을 GPU 세대 무관 compositor 실패로 격상 |
