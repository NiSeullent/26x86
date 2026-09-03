# 원본 저장소 (Upstream Repositories)

**26x86** — x86 기반 Mac을 위한 더 나은 macOS 26 시스템

---

## 개요

**26x86**은 [OpenCore Legacy Patcher T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2)에서 파생된 **2차(derivative) 작업**입니다. T2 프로젝트는 Dortania [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher)를 기반으로 하며, 두 프로젝트 모두 BSD 3-Clause 라이선스를 따릅니다.

본 문서는 26x86이 직접·간접으로 사용·참조·포크하는 **모든 주요 원본 GitHub 저장소**를 범주별로 나열합니다. 각 항목의 저작권은 원저작자에게 유지되며, 26x86은 해당 코드를 수정·통합·재배포할 수 있는 라이선스 조건을 준수합니다.

**관련 법적 문서:** [NOTICE.md](../../NOTICE.md) · [THIRD_PARTY_LICENSES.md](../../THIRD_PARTY_LICENSES.md) · [CREDITS.md](../../CREDITS.md) · [LICENSE.txt](../../LICENSE.txt)

> **면책:** 26x86은 Apple Inc., Dortania, Acidanthera 또는 기타 업스트림 프로젝트와 **제휴·승인·후원 관계가 없습니다**. **macOS**, **Apple**, **OpenCore**, **OpenCorePkg**, **Lilu** 등은 각 소유자의 상표 또는 등록 상표입니다.

---

## English Summary

**26x86** is a community fork of **OpenCore Legacy Patcher T2** (Albert Müller), which extends **Dortania OpenCore Legacy Patcher**. This page catalogs every major upstream repository—patchers, bootloader forks, payload packages, Acidanthera kexts, moraea GPU patches, and community research forks—that 26x86 builds upon or redistributes under their respective licenses. Original copyrights remain with upstream authors; 26x86 modifications are Copyright (c) 2026 NiSeullent and 26x86 contributors. See [NOTICE.md](../../NOTICE.md) for the BSD 3-Clause attribution statement.

---

## 포크 계보 (Fork Lineage)

```
dortania/OpenCore-Legacy-Patcher
    └── albert-mueller/OpenCore-Legacy-Patcher-T2
            └── NiSeullent/26x86  ← 본 프로젝트
```

| 저장소 | 소유자 | 라이선스 | 포크 관계 | 26x86에서의 사용 |
|--------|--------|----------|-----------|------------------|
| [dortania/OpenCore-Legacy-Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher) | Dortania | BSD 3-Clause | 루트 계보 | Python 패처 아키텍처, 패치셋, GUI, 문서 구조의 원본 |
| [albert-mueller/OpenCore-Legacy-Patcher-T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2) | Albert Müller | BSD 3-Clause | Dortania OCLP 포크 | **직접 업스트림** — T2 지원, macOS 26 실험 코드, 대부분의 소스 기반 |
| [NiSeullent/26x86](https://github.com/NiSeullent/26x86) | NiSeullent | BSD 3-Clause | OCLP-T2 포크 | 본 저장소 — 한국어 UI, macOS 26 Tahoe 초점, 브랜딩·릴리스 독립화 |

**저작권 고지 (BSD 3-Clause):**

- Copyright (c) 2020–2025 Dhinak G, Mykola Grymalyuk, and individual contributors. (Dortania OCLP / OCLP-T2 계보)
- Copyright (c) 2026 NiSeullent and 26x86 contributors. (26x86 수정분)

---

## 26x86 의존성 포크 (Dependency Forks)

26x86은 런타임·빌드 시 아래 NiSeullent 포크 저장소에서 바이너리·manifest를 가져옵니다 (`constants.py` URL 참조).

| 26x86 포크 | 원본 저장소 | 라이선스 | 26x86에서의 역할 |
|------------|-------------|----------|------------------|
| [NiSeullent/26x86-OpenCorePkg](https://github.com/NiSeullent/26x86-OpenCorePkg) | [albert-mueller/OpenCorePkg-add-T2-support](https://github.com/albert-mueller/OpenCorePkg-add-T2-support) | BSD 3-Clause | T2 지원 OpenCore EFI 부트로더 ZIP (`url_opencore_pkg`) |
| [NiSeullent/26x86-PatcherSupportPkg](https://github.com/NiSeullent/26x86-PatcherSupportPkg) | [hackdoc/PatcherSupportPkg](https://github.com/hackdoc/PatcherSupportPkg) | 저장소 정책 | 루트 패치 Apple 바이너리·Universal-Binaries DMG (`url_patcher_support_pkg`) |
| [NiSeullent/26x86-MetallibSupportPkg](https://github.com/NiSeullent/26x86-MetallibSupportPkg) | [dortania/MetallibSupportPkg](https://github.com/dortania/MetallibSupportPkg) | 저장소 정책 | Metal 3802 `.metallib` PKG manifest (`url_metallib_support_pkg`, `metallib_handler.py`) |

**원본 OpenCorePkg (Acidanthera):** [acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) — T2 포크 및 26x86-OpenCorePkg의 궁극적 기반. Copyright Acidanthera and contributors.

---

## 부트로더·지원 패키지 (Bootloader & Support Packages)

| 저장소 | 소유자 | 라이선스 | 26x86에서의 사용 |
|--------|--------|----------|------------------|
| [acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) | Acidanthera | BSD 3-Clause | OpenCore 부트로더 기준; `opencore_version` 2.0.3; macserial, ocvalidate |
| [albert-mueller/OpenCorePkg-add-T2-support](https://github.com/albert-mueller/OpenCorePkg-add-T2-support) | Albert Müller | BSD 3-Clause | T2 Mac EFI 부팅·kext 주입 개선 포크 |
| [hackdoc/PatcherSupportPkg](https://github.com/hackdoc/PatcherSupportPkg) | hackdoc / pyquick 등 | 저장소 정책 | OCLP-R 계열 루트 패치 바이너리 원본 |
| [albert-mueller/PatcherSupportPkg](https://github.com/albert-mueller/PatcherSupportPkg) | Albert Müller | 저장소 정책 | OCLP-T2 전용 PatcherSupportPkg 변형 |
| [YBronst/PatcherSupportPkg](https://github.com/YBronst/PatcherSupportPkg) | YBronst | 저장소 정책 | OCLP-Plus Tahoe 네이티브 바이너리 (참조·연구) |
| [dortania/MetallibSupportPkg](https://github.com/dortania/MetallibSupportPkg) | Dortania / EduCovas 등 | 저장소 정책 | Sequoia 기준 Metal 3802 `.metallib` 패치 파이프라인 |
| [pyquick/MetallibSupportPkg](https://github.com/pyquick/MetallibSupportPkg) | pyquick | 저장소 정책 | macOS 26 Tahoe Metallib manifest (OCLP-R 연계) |
| [dortania/KdkSupportPkg](https://github.com/dortania/KdkSupportPkg) | Dortania | 저장소 정책 | Kernel Debug Kit 다운로드·루트 패치 빌드 지원 |

---

## 커뮤니티 패처·연구 포크 (Community Patcher Forks)

아래 저장소는 26x86의 직접 포크는 아니나, 패치 로직·연구·CHANGELOG에서 코드·아이디어를 차용하거나 참조합니다.

| 저장소 | 소유자 | 라이선스 | 26x86에서의 관계 |
|--------|--------|----------|------------------|
| [hackdoc/OCLP-R](https://github.com/hackdoc/OCLP-R) | hackdoc | BSD 3-Clause (OCLP 계보) | macOS 26 상수, USB-Map-Tahoe.kext, Solarium UI 연구 |
| [pyquick/OCLP-R](https://github.com/pyquick/OCLP-R) | pyquick | BSD 3-Clause (OCLP 계보) | Tahoe Metallib 다운로드 엔드포인트 수정 |
| [YBronst/OCLP-Plus](https://github.com/YBronst/OCLP-Plus) | YBronst | BSD 3-Clause (OCLP 계보) | Tahoe Modern Wireless·Broadcom AWDL/AirDrop 패치 참조 |
| [vytska69/OpenCore-Legacy-Patcher](https://github.com/vytska69/OpenCore-Legacy-Patcher) | vytska69 | BSD 3-Clause | T2 SEP/AppleKeyStore 연구, T1 keystore 스택 대체 |
| [laobamac/OCLP-Mod](https://github.com/laobamac/OCLP-Mod) | laobamac | BSD 3-Clause | 커뮤니티 Tahoe 포크; Metallib 호환 논의 |
| [stephandeutsch/OpenCore-Legacy-Patcher](https://github.com/stephandeutsch/OpenCore-Legacy-Patcher) | stephandeutsch | BSD 3-Clause | USB 1.1 (Sequoia/Tahoe) 호환 수정 |
| [GUTY345/OpenCore-Legacy-patcher-t2chip-fixBugs](https://github.com/GUTY345/OpenCore-Legacy-patcher-t2chip-fixBugs) | GUTY345 | BSD 3-Clause | T2 USB-Map, SMBIOS, UHD 630, macOS 26 수정 |
| [GUTY345/OpenCore-Legacy-Patcher-T2-Fork](https://github.com/GUTY345/OpenCore-Legacy-Patcher-T2-Fork) | GUTY345 | BSD 3-Clause | T2 버그 수정 포크 |
| [nxvid/OpenCore-Legacy-Patcher-T2](https://github.com/nxvid/OpenCore-Legacy-Patcher-T2) | nxvid | BSD 3-Clause | T2 sbvmm 주입 이슈 문서화·수정 |
| [albert-mueller/OpenCore-Legacy-Patcher-T2-Instructions-for-T2-Macs](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2-Instructions-for-T2-Macs) | Albert Müller | — | T2 Mac 설치 후 가이드 문서 |
| [dortania/OCLP-GUI](https://github.com/dortania/OCLP-GUI) | dosdude1 / Dortania | BSD 3-Clause | 초기 GUI 레거시 (크레딧) |

---

## GPU·Metal·패치 페이로드 (moraea 및 관련)

| 저장소 | 소유자 | 라이선스 | 26x86에서의 사용 |
|--------|--------|----------|------------------|
| [moraea/non-metal-frameworks](https://github.com/moraea/non-metal-frameworks) | moraea / EduCovas 등 | 각 파일 LICENSE | Non-Metal GPU 프레임워크 다운그레이드 패치 |
| [moraea/misc-patches](https://github.com/moraea/misc-patches) | moraea | 각 파일 LICENSE | 3802-Metal-15, Kepler/GCN Metal 번들, T1-Patch, IOUSBHostFamily 등 |
| [moraea/unsupported-wifi-patches](https://github.com/moraea/unsupported-wifi-patches) | moraea | 각 파일 LICENSE | 레거시 Broadcom/Atheros Wi-Fi 복원 |
| [laobamac/non-metal-frameworks](https://github.com/laobamac/non-metal-frameworks) | laobamac | 각 파일 LICENSE | moraea Non-Metal 미러 (OCLP-Mod 참조) |

**moraea 조직:** https://github.com/moraea — Non-Metal·Metal interposer 생태계 중심.

---

## Acidanthera Kext 및 도구

`payloads/Kexts/Update-Kexts.command` 및 `opencore_legacy_patcher/constants.py`에서 버전 관리·번들되는 구성 요소입니다.

| 구성 요소 | 저장소 | 라이선스 | 26x86 역할 |
|-----------|--------|----------|------------|
| Lilu | [acidanthera/Lilu](https://github.com/acidanthera/Lilu) | BSD 3-Clause | 커널 패치 인프라 (필수) |
| WhateverGreen | [acidanthera/WhateverGreen](https://github.com/acidanthera/WhateverGreen) | BSD 3-Clause | GPU 패치; Navi 백라이트 커스텀 빌드 |
| AirportBrcmFixup | [acidanthera/AirportBrcmFixup](https://github.com/acidanthera/AirportBrcmFixup) | BSD 3-Clause | Broadcom Wi-Fi/Bluetooth |
| BlueToolFixup | [acidanthera/BrcmPatchRAM](https://github.com/acidanthera/BrcmPatchRAM) | BSD 3-Clause | Bluetooth 펌웨어 (BrcmPatchRAM에서 빌드) |
| CPUFriend | [acidanthera/CPUFriend](https://github.com/acidanthera/CPUFriend) | BSD 3-Clause | CPU 전력 관리 |
| CryptexFixup | [acidanthera/CryptexFixup](https://github.com/acidanthera/CryptexFixup) | BSD 3-Clause | Rosetta Cryptex·root hash |
| DebugEnhancer | [acidanthera/DebugEnhancer](https://github.com/acidanthera/DebugEnhancer) | BSD 3-Clause | 커널 디버그 |
| FeatureUnlock | [acidanthera/FeatureUnlock](https://github.com/acidanthera/FeatureUnlock) | BSD 3-Clause | Sidecar 등 기능 잠금 해제 |
| NVMeFix | [acidanthera/NVMeFix](https://github.com/acidanthera/NVMeFix) | **GPL 2.0** | NVMe 커널 패치 |
| RestrictEvents | [acidanthera/RestrictEvents](https://github.com/acidanthera/RestrictEvents) | BSD 3-Clause | SIP/이벤트 제한 |
| AppleALC | [acidanthera/AppleALC](https://github.com/acidanthera/AppleALC) | BSD 3-Clause | 오디오 (레거시 Mac — 자동 업데이트 비활성) |
| AutoPkgInstaller | [acidanthera/AutoPkgInstaller](https://github.com/acidanthera/AutoPkgInstaller) | BSD 3-Clause | PKG 자동 설치 Lilu 플러그인 |
| CSLVFixup | [acidanthera/CSLVFixup](https://github.com/acidanthera/CSLVFixup) | BSD 3-Clause | Library Validation |
| AMFIPass | (Dhinak G / Acidanthera 배포) | BSD 3-Clause | AMFI 우회 Lilu 플러그인 |
| MacKernelSDK | [acidanthera/MacKernelSDK](https://github.com/acidanthera/MacKernelSDK) | BSD 3-Clause | kext 빌드 SDK (WEG Navi 빌드 시) |
| RSRHelper | [khronokernel/RSRHelper](https://github.com/khronokernel/RSRHelper) | BSD 3-Clause | Rapid Security Response 복구 |

**Acidanthera 저작권 (일반):** Copyright (c) 2018–2026 vit9696 and contributors. 각 저장소 `LICENSE` 파일 참조.

---

## 기타 Kext·UEFI·유틸리티

| 구성 요소 | 저장소 | 라이선스 | 26x86 역할 |
|-----------|--------|----------|------------|
| Innie | [cdf/Innie](https://github.com/cdf/Innie) | BSD 3-Clause | 내부 SATA/NVMe 인식 |
| SimpleMSR | [arter97/SimpleMSR](https://github.com/arter97/SimpleMSR) | BSD 3-Clause | MSR 레지스터 접근 |
| AMDGPUWakeHandler | [blackgate/AMDGPUWakeHandler](https://github.com/blackgate/AMDGPUWakeHandler) | 저장소 참조 | AMD GPU 웨이크 |
| KDKlessWorkaround | [flagersgit/KDKlessWorkaround](https://github.com/flagersgit/KDKlessWorkaround) | 저장소 참조 | KDK 없이 패치 |
| FixPCIeLinkrate | [joevt/joevtApps](https://github.com/joevt/joevtApps) | 저장소 참조 | PCIe 링크 레이트 UEFI 드라이버 |
| SurPlus | [reenigneorcim/SurPlus](https://github.com/reenigneorcim/SurPlus) | Syncretic 정책 | Sequoia 서플라스 kext |
| latebloom | [reenigneorcim/latebloom](https://github.com/reenigneorcim/latebloom) | Syncretic 정책 | MouSSE 관련 |
| AAAMouSSE | [MacRumors 스레드](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/) | **All rights reserved** (Syncretic) | SSE4.2 에뮬레이션 (Penryn Mac) |
| telemetrap | [MacRumors 포스트](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/post-28447707) | **All rights reserved** (Syncretic) | SSE4.2 부트 체크 우회 |
| VMM Patch Set | [OCLP config.plist](https://github.com/dortania/OpenCore-Legacy-Patcher/blob/4a8f61a01da72b38a4b2250386cc4b497a31a839/payloads/Config/config.plist#L1222-L1281) | parrotgeek1 | VMM 부트 패치 |
| Apple kext·프레임워크 | Apple Inc. | **Apple Proprietary** | Dortania/OCLP 수정·다운그레이드 바이너리 (PatcherSupportPkg) |

---

## 26x86 수정 사항 (Modifications)

NiSeullent 및 26x86 기여자가 본 포크에서 수행한 주요 변경(비포괄):

- 프로젝트 브랜딩·번들 ID·Application Support 경로를 `26x86` 네임스페이스로 분리
- 한국어 GUI·CLI·위키 문서 기본화
- macOS 26 Tahoe 지원에 초점을 맞춘 릴리스·업데이트 API (`NiSeullent/26x86`)
- 의존성 포크 3종 (`26x86-OpenCorePkg`, `26x86-PatcherSupportPkg`, `26x86-MetallibSupportPkg`) 운영
- OCLP/Dortania와 독립된 보안 정책·면책·라이선스 고지 체계

업스트림에 병합되지 않은 수정분에 대한 저작권은 **Copyright (c) 2026 NiSeullent and 26x86 contributors** 에 귀속됩니다.

---

## 법적 고지 요약

### BSD 3-Clause 필수 표기

> This product includes software developed by Dortania, OpenCore Legacy Patcher contributors, and the 26x86 project.

(본 제품에는 Dortania, OpenCore Legacy Patcher 기여자 및 26x86 프로젝트가 개발한 소프트웨어가 포함됩니다.)

### 상표 면책

- **macOS**, **Apple**, Apple 로고 및 관련 제품명은 **Apple Inc.** 의 상표입니다.
- **OpenCore**, **OpenCorePkg**, **Lilu** 및 Acidanthera 프로젝트명은 각 저자·커뮤니티의 프로젝트입니다.
- **26x86**은 NiSeullent의 커뮤니티 포크 브랜드이며, 위 주체들의 승인을 받지 않았습니다.

### GPL 2.0 (NVMeFix)

NVMeFix는 GPL 2.0입니다. 소스 제공 의무가 적용될 수 있으므로 [acidanthera/NVMeFix](https://github.com/acidanthera/NVMeFix) 원본을 참조하세요.

---

## 문서 통계

| 범주 | 문서화된 저장소 수 |
|------|-------------------|
| 패처 계보 | 3 |
| 26x86 의존성 포크 | 3 (+ 원본 3) |
| 부트로더·지원 패키지 | 8 |
| 커뮤니티 패처 포크 | 11 |
| moraea·GPU 패치 | 4 |
| Acidanthera kext·도구 | 16 |
| 기타 kext·유틸리티 | 11 |
| **합계 (고유 GitHub 저장소)** | **56** |

*AAAMouSSE·telemetrap·Apple 바이너리 등 GitHub 외 출처는 별도 행으로 [NOTICE.md](../../NOTICE.md)에 기재됩니다.*

---

*최종 갱신: 2026년 9월 — 저장소 목록은 `constants.py`, `Update-Kexts.command`, `CREDITS.md`, GitHub fork 메타데이터를 기준으로 작성되었습니다.*
