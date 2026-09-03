# 26x86 연구 자료 인벤토리

> **프로젝트:** macOS 26 Tahoe on x86 Macs (26x86)  
> **작성일:** 2026년 9월 4일  
> **조사 범위:** OCLP 포크, T2 패치, GPU/Metal, 커널/Kext, 커뮤니티, macOS 26 Tahoe 공식 지원 현황

---

## 핵심 프로젝트 저장소

| 제목 | 출처 URL | 유형 | 26x86 관련성 | 요약 |
|------|----------|------|--------------|------|
| Dortania OpenCore Legacy Patcher (공식) | https://github.com/dortania/OpenCore-Legacy-Patcher | GitHub 저장소 | **핵심** — 비공식 Intel Mac 패치의 기준점 | 현재 안정 버전 2.4.1(Sequoia까지). Tahoe 26 지원은 Issue #1167에서 진행 중이나 공식 릴리스 미출시. 개발자 이탈로 진행 속도 둔화. |
| OCLP Tahoe 지원 트래커 (#1167) | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 | GitHub Issue | **핵심** — 공식 Tahoe 로드맵 | Tahoe가 Intel Mac 마지막 macOS임을 확인. T2 Mac, Metal 3802/8302, Non-Metal, Wi-Fi 등 패치 범위 정의. Liquid Glass UI 초기 스크린샷 공개. |
| OCLP Sequoia/T2 이슈 (#1136) | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1136 | GitHub Issue | **높음** — T2 차단의 근본 원인 문서화 | MacBookAir8,x에서 OpenCorePkg 부팅 시 AppleKeyStore SKS 타임아웃 패닉. 공식 OCLP가 T2를 지원하지 않는 기술적 근거. |
| hackdoc/OCLP-R | https://github.com/hackdoc/OCLP-R | GitHub 저장소 | **높음** — Tahoe 실험 빌드 | Dortania OCLP 포크. macOS 26 상수, USB-Map-Tahoe.kext, Solarium(Liquid Glass) Nightly 지원. CHANGELOG에 Tahoe 관련 변경 다수. |
| hackdoc/PatcherSupportPkg | https://github.com/hackdoc/PatcherSupportPkg | GitHub 저장소 | **높음** — 루트 패치 바이너리 | OCLP-R용 Apple 바이너리 패키지. 최신 v1.11.6(2026-08). C/Metal/Python 혼합. pyquick 기여. |
| pyquick/OCLP-R | https://github.com/pyquick/OCLP-R | GitHub 저장소 | **높음** — Metallib 26.x 패치 | hackdoc OCLP-R의 개인 포크. `metallib_handler.py`에서 Dortania manifest를 pyquick GitHub Pages로 리다이렉트하여 Tahoe Metallib 다운로드 문제 해결. |
| pyquick/MetallibSupportPkg | https://github.com/pyquick/MetallibSupportPkg | GitHub 저장소 | **높음** — Tahoe Metallib manifest | pyquick.github.io/MetallibSupportPkg/manifest.json 호스팅. OCLP-R의 macOS 26 Metallib 패치 다운로드 엔드포인트. |
| YBronst/OCLP-Plus (Tahoe Patch Set) | https://github.com/YBronst/OCLP-Plus | GitHub 저장소 | **높음** — Tahoe Wi-Fi/루트 패치 | macOS 26.0~26.4.1 Modern 루트 패치. Broadcom Wi-Fi(AWDL/AirDrop) 복원. 2026-06-28 아카이브(추가 업데이트 없음). MacPro7,1/MBP16,x 등 대상. |
| YBronst/PatcherSupportPkg | https://github.com/YBronst/PatcherSupportPkg | GitHub 저장소 | **중간** — OCLP-Plus 바이너리 의존성 | OCLP-Plus가 Tahoe 네이티브 바이너리를 가져오는 리소스. 저장소 삭제 시 루트 패치 실패 위험. |
| laobamac/OCLP-Mod | https://github.com/laobamac/OCLP-Mod | GitHub 저장소 | **높음** — 커뮤니티 Tahoe 포크 | 662 stars. Intel 구형 iGPU 패치는 Dortania 담당이라고 명시. MetallibSupportPkg Tahoe 호환 이슈(#86, #91) 논의. |
| albert-mueller/OpenCore-Legacy-Patcher-T2 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2 | GitHub 저장소 | **핵심** — T2 Mac 전용 실험 포크 | Sequoia/Tahoe T2 지원 목표. 최신 4.0.0 alpha 18.2.1(2026-09-03). 83 stars. macOS 27(Golden Gate) 미지원(arm64 전용). |
| albert-mueller/PatcherSupportPkg | https://github.com/albert-mueller/PatcherSupportPkg | GitHub 저장소 | **중간** — T2 포크 바이너리 | T2 포크 전용 PatcherSupportPkg. 레거시 하드웨어 패치 바이너리 호스팅. |
| albert-mueller/OpenCore-Legacy-Patcher-T2-Instructions | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2-Instructions-for-T2-Macs | GitHub 저장소 | **중간** — T2 설치 후 가이드 | T2 Mac에서 "Reboot to apply" 화면 이후 필요한 후속 작업 문서. |
| vytska69/OpenCore-Legacy-Patcher | https://github.com/vytska69/OpenCore-Legacy-Patcher | GitHub 저장소 | **높음** — T2 SEP/AppleKeyStore 연구 | T1 keystore 스택 대체로 SEP mailbox hang 우회. MacBookAir8,1/8,2 실험. T2 진단 도구(Save T2 boot diagnostics) 포함. |
| GUTY345/OpenCore-Legacy-Patcher-T2-Fork | https://github.com/GUTY345/OpenCore-Legacy-Patcher-T2-Fork | GitHub 저장소 | **중간** — T2 버그 수정 포크 | USB-Map.plist 구문 오류, SMBIOS 스푸핑 버그, UHD 630 그래픽, Unsupported Mantissa speed 패닉 등 T2 특화 수정. |
| albert-mueller/OpenCorePkg-add-T2-support | https://github.com/albert-mueller/OpenCorePkg-add-T2-support | GitHub 저장소 | **높음** — T2 OpenCore 부트로더 | Acidanthera OpenCorePkg T2 지원 포크. T2 Mac EFI 부팅·kext 주입 개선 목적. |
| dortania/MetallibSupportPkg | https://github.com/dortania/MetallibSupportPkg | GitHub 저장소 | **핵심** — Metal 3802 .metallib 패치 | Sequoia IPSW에서 .metallib 추출→AIR v26 다운그레이드→PKG 빌드. 최신 릴리스 15.7.8(Sequoia 기준). Tahoe 전용 릴리스 미확인. |
| dortania/KdkSupportPkg | https://github.com/dortania/KdkSupportPkg | GitHub 저장소 | **높음** — Kernel Debug Kit | Tahoe 루트 패치에 KDK 필수. 최신 26A5425a(2026-08-31). macOS 26.6+ KDK 미제공 시 설치 제한. |
| Moraea GitHub 조직 | https://github.com/moraea | GitHub 조직 | **높음** — Non-Metal/GPU 패치 생태계 | non-metal-frameworks, misc-patches, unsupported-wifi-patches, dsce 등. EduCovas/ASentientBot 계열 패치의 중심. |
| Moraea Non-Metal Wiki | https://moraea.github.io/ | Wiki/문서 | **중간** — Non-Metal 패치 문서 | TeraScale 2 지원, Non-Metal 패치 상세 문서. Tahoe Liquid Glass 비호환 명시적 언급은 제한적. |
| laobamac/non-metal-frameworks | https://github.com/laobamac/non-metal-frameworks | GitHub 저장소 | **중간** — Non-Metal 프레임워크 미러 | Moraea 삭제 저장소 기반 Non-Metal 패치. OCLP-Mod에서 참조. Tahoe 지원 미확인. |
| Dortania OCLP 공식 가이드 | https://dortania.github.io/OpenCore-Legacy-Patcher/ | 문서 | **기준** — 설치/패치 워크플로 | 모델 목록, POST-INSTALL, DEBUG, TROUBLESHOOT 가이드. T2 Mac은 "미지원" 상태. |
| OpenCore Legacy Patcher CHANGELOG | https://github.com/dortania/OpenCore-Legacy-Patcher/blob/main/CHANGELOG.md | CHANGELOG | **참고** — 패치 이력 | USB 1.1, T1, Metal 3802, Wi-Fi 등 과거 패치 타임라인. Tahoe 항목은 Nightly/미출시. |

---

## T2 Mac 지원

| 제목 | 출처 URL | 유형 | 26x86 관련성 | 요약 |
|------|----------|------|--------------|------|
| T2 지원 마스터 이슈 (#1) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/1 | GitHub Issue | **핵심** — T2 프로젝트 로드맵 | #1167, #1136, OCLP-Mod #81 연계. MBA 2018/2019 인스톨러 부팅 성공. OpenCore 1.0.7 업그레이드 필요. AppleT2Controller/AppleKeyStore/SMC 역공학 진행 중. |
| OCLP-T2 Wiki (T2 진행 상황) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki | GitHub Wiki | **핵심** — 현재 T2 상태 요약 | 체크리스트: 인스톨러 부팅 ✅, MBA8,x 인스톨러 ⬜, 내부 HDD 마운트 ⬜, 데스크톱 도달 ⬜. T2에서 SIP 완전 비활성화(0xFFF) 하드코딩. |
| corecrypto 커널 패닉 (#53) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/53 | GitHub Issue | **높음** — MBP15,4 등 부팅 차단 | MacBookPro15,4에서 corecrypto 패닉·파란 진행바 정지. FIPS 패치 제거로 alpha 15 pre-alpha 7에서 대부분 해결. Touch Bar 모델 잔여 패닉. |
| APFS 마운트/포맷 오류 (#69) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/69 | GitHub Issue | **핵심** — 설치 진행 블로커 | 인스톨러 부팅 후 파티션 마운트/지우기 시 -69624 오류. Container First Aid 가능하나 APFS 파티션 생성 불가. T2 exploit 불필요, 역공학 필요. |
| authenticate_root_hash 패닉 (#60) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/60 | GitHub Issue | **높음** — Tahoe 부팅 실패 | `apfs_extract_root_hash_and_manifest failed (22)` 커널 패닉. #69 APFS 이슈와 연관. 2026-09-01 종료. |
| AppleImage4/APFS 패닉 (#130) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/130 | GitHub Issue | **핵심** — 설치 후 부팅 차단 | Tahoe 설치 후 외부 SSD 부팅 시 AppleImage4.kext+apfs.kext "Needs authenticator (81)" 패닉. trustcache 오류 동반. |
| AppleKeyStore Lilu 플러그인 (#125) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/125 | GitHub Issue | **핵심** — SEP/KeyStore 해결 방향 | AppleSEPManager "sks request timeout" 해결에 새 Lilu 플러그인 필요. DrDonk·vytska69 연구와 연계. |
| AppleSEPManager 패치 실패 (#23) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/23 | GitHub Issue | **중간** — 패치 적용 버그(해결됨) | pre-alpha 1/2에서 AppleSEPManager 패치 템플릿 누락·`sys` 미정의 오류. pre-alpha 3에서 수정. |
| MetallibSupportPkg Tahoe 한계 (#27) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/27 | GitHub Issue | **높음** — T2+Metallib 교차 이슈 | MetallibSupportPkg 미지원 시 그래픽/Wi-Fi 드라이버 작동 불가. T2 부팅 우선으로 Metallib 수정은 후순위. albert-mueller/metal 포크 언급. |
| OCLP-T2 Releases (alpha 18.2.1) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/releases | GitHub Releases | **높음** — 최신 빌드 | Metal 3802/Non-Metal Tahoe 패치 안전 가드. T2 Mac SMBIOS 스푸핑 불필요화. Touch ID 작동(Apple Pay는 SIP 제약). OpenCorePkg #620 버그 협력 중. |
| Non-T2 Tahoe 설치 가이드 (#171) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/discussions/171 | GitHub Discussion | **중간** — 2017+ Non-T2 가이드 | KDK 매칭 설치, OCLP-T2로 Tahoe USB 생성, 루트 패치 워크플로. 26.6+ KDK 미제공 주의. |
| T2 Mac Tahoe 차단 분석 (ITECH4MAC) | https://www.itech4mac.net/2026/03/why-t2-macs-are-blocked-from-macos-tahoe-via-oclp-and-what-it-means-for-you/ | 블로그 | **높음** — T2 정책 요약 | Tahoe SIP 강화와 T2 secure boot 충돌로 공식 OCLP Tahoe 불가. Sequoia+OCLP 2.4.1 권장. Non-T2 Mac은 상대적으로 유리. |
| Acidanthera OpenCorePkg #620 | https://github.com/acidanthera/OpenCorePkg/issues/620 | GitHub Issue | **중간** — OpenCore T2 버그 | OCLP-T2 릴리스 노트에서 T2 Mac 부팅 관련 OpenCorePkg 버그로 인용. Acidanthera와 협력 중. |
| laobamac OCLP-Mod T2 이슈 (#81) | https://github.com/laobamac/OCLP-Mod/issues/81 | GitHub Issue | **중간** — OCLP-Mod T2 논의 | OCLP-T2 #1에서 참조. OCLP-Mod 커뮤니티의 T2 지원 요청·진행 상황. |

---

## GPU/Metal 패치

| 제목 | 출처 URL | 유형 | 26x86 관련성 | 요약 |
|------|----------|------|--------------|------|
| MetallibSupportPkg 패치 파이프라인 | https://github.com/dortania/MetallibSupportPkg/blob/main/README.md | README | **핵심** — Metal 3802 기술 | IPSW→DMG→.metallib 추출→AIR v27→v26 다운그레이드→PKG. Sequoia 기준 검증됨. Tahoe AIR 버전 변경 대응 필요. |
| pyquick Metallib 26.x 다운로드 수정 | https://github.com/hackdoc/OCLP-R/commit/167332042abac842f9c6d36a43ae3390d1d8ed6d | Git Commit | **높음** — Tahoe Metallib 엔드포인트 | `METALLIB_API_LINK_ORG`를 pyquick.github.io로 변경. `network_handler.py`에 재시도/프록시 로직 추가. |
| OCLP-Mod Metallib Tahoe 희망 (#86) | https://github.com/laobamac/OCLP-Mod/issues/86 | GitHub Issue | **중간** — Metallib 현황 논쟁 | Intel iGPU 재활성화는 Dortania 담당. laobamac: Tahoe MetalSupportPkg 컴파일은 쉬우나 PatcherSupportPkg 구형 프레임워크 이식이 어려움. |
| OCLP-Mod Metallib 호환 버그 (#91) | https://github.com/laobamac/OCLP-Mod/issues/91 | GitHub Issue | **중간** — MetallibSupportPkg 버그 | MetallibSupportPkg와 macOS 26 Tahoe 호환성 버그 리포트. #86, #27과 연계. |
| Metal 3802 패치셋 (metal_3802.py) | https://github.com/dortania/OpenCore-Legacy-Patcher/blob/main/opencore_legacy_patcher/sys_patch/patchsets/shared_patches/metal_3802.py | 소스코드 | **높음** — 3802 GPU 패치 로직 | Ivy Bridge/Haswell/Kepler 대상. Metal.framework, MTLCompiler, GPUCompiler 다운그레이드. 13.3+ extended 패치로 AMFI 영향. |
| moraea 3802-Metal-15 패치 | https://github.com/moraea/misc-patches/tree/main/3802-Metal-15 | GitHub 디렉터리 | **높음** — Metal 3802 레거시 | Kepler·Ivy/Haswell iGPU용 3802 Metal 패치셋. Sequoia 15 기준. Tahoe 26 미검증. |
| moraea Kepler 13+ Metal 번들 | https://github.com/moraea/misc-patches/tree/main/Kepler%2013%2B | GitHub 디렉터리 | **중간** — Kepler Metal 셔im | Kepler GPU Metal 번들 패치·shim. Tahoe Liquid Glass와 호환성 미확인. |
| moraea GCN/Vega Metal 번들 | https://github.com/moraea/misc-patches/tree/main/GCN%2013%2B | GitHub 디렉터리 | **중간** — AMD GCN Metal | GCN 1~4 Metal 번들 패치. Mac Pro 5,1 등 AMD GPU 업그레이드 Mac 관련. |
| moraea sequoia 31001 interposer | https://github.com/moraea/misc-patches/tree/main/sequoia%2031001%20interposer | GitHub 디렉터리 | **중간** — Broadwell/Skylake Metal | AMD GCN 1~5, Intel 5th/6th Gen Metal bundle interposer. Metal 31001 스택 보완. |
| Non-Metal 패치셋 (moraea) | https://github.com/moraea/non-metal-frameworks | GitHub 저장소 | **높음** — 2011 Mac GPU | Tesla/Fermi/Maxwell/Pascal, TeraScale, Iron/Sandy Bridge. Tahoe에서 Liquid Glass 비호환→UI 우회 필요(#1167). |
| OCLP-T2 Wiki: Metal 8302 경고 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki | GitHub Wiki | **핵심** — 2012~2014 Mac GPU | Metal 8302(2012~2014 Mac) 및 Non-Metal(2011 Mac) Tahoe 그래픽 패치 미완. 패치 주입 시 커널 패닉→안전 가드로 가속 없이 부팅만 허용. |
| OCLP PR #1137 Sequoia 그래픽 | https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1137 | GitHub PR | **참고** — Metal 3802 Sequoia 통합 | MetallibSupportPkg 통합으로 3802 GPU Sequoia 지원 확대. Tahoe 패치 기반으로 활용 가능. |
| MrMacintosh Metallib/KDK 상태 | https://mrmacintosh.com/macos-tahoe-26-5-1-update-everything-you-need-to-know/ | 블로그 | **높음** — Tahoe 업데이트 호환 | OCLP 2.4.1 + Tahoe 26.5.1 = **설치 금지**. KdkSupportPkg·MetallibSupportPkg Tahoe 릴리스 대기 중 명시. |
| OCLP-T2 Releases: Metal 가드 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/releases | GitHub Releases | **높음** — Tahoe GPU 안전장치 | Metal 3802/Non-Metal 패치가 macOS 26에서 황면·패닉 유발→Tahoe에서 해당 패치 주입 차단. gandolf243 수정 작업 중. |

---

## 커널/Kext 패치

| 제목 | 출처 URL | 유형 | 26x86 관련성 | 요약 |
|------|----------|------|--------------|------|
| AAAMouSSE SSE4.2 에뮬레이터 | https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/ | MacRumors 포럼 | **핵심** — Penryn/Core2 Duo | POPCNT, PCMPGTQ, CRC32만 에뮬. CPUID SSE4.2 스푸핑 불가. 2021 이후 업데이트 없음·폐쇄 소스. Tahoe에서 C2D Mac 부팅 불가. |
| telemetrap SSE4.2 체크 우회 | https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/post-28447707 | MacRumors 포스트 | **높음** — Mojave+ SSE4.1 Mac | com.apple.telemetry.plugin 차단으로 SSE4.2 부트 체크 우회. AAAMouSSE와 병용. Tahoe C2D에서 패닉. |
| DrDonk — AppleKeyStore 패치 기여 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2 (Credits) | 기여자 크레딧 | **높음** — T2 KeyStore | OCLP-T2 README에서 DrDonk가 AppleKeyStore 유효 패치 작성·테스트 기여로 명시. 별도 공개 저장소 없음. |
| vytska69 T1 keystore 스택 대체 | https://github.com/vytska69/OpenCore-Legacy-Patcher | GitHub README | **핵심** — SEP mailbox 우회 | AppleKeyStore/AppleSSE/AppleCredentialManager+corecrypto_T1+KernelRelayHost로 T2 keystore 대체. SEP MMIO+IOMMU+MSI mailbox hang 해결 시도. |
| stephandeutsch USB 1.1 호환 | https://github.com/stephandeutsch/OpenCore-Legacy-Patcher/ | GitHub 저장소 | **높음** — USB 1.1 Mac | OCLP-T2 크레딧: Sequoia/Tahoe USB 1.1 호환 수정. Penryn 이하 Mac 인스톨러 키보드/마우스 복원. |
| Legacy UHCI/OHCI 지원 (#1021) | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1021 | GitHub Issue | **높음** — Ventura+ USB 1.1 | AppleUSBUHCI/OHCI kext 제거. 루트 패치로 복원하나 인스톨러/클린설치/업데이트 후 USB 1.1 불가. USB 2.0 허브 필수. |
| OCLP TROUBLESHOOT-HARDWARE USB 1.1 | https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOT-HARDWARE.html | 문서 | **높음** — USB 1.1 모델 목록 | MacBook7,1, MacPro3,1~5,1 등 Ventura+ USB 1.1 복원 방법. Sonoma에서 일부 허브 비호환. SSH 원격 패치 대안. |
| hackdoc OCLP-R USB-Map-Tahoe.kext | https://github.com/hackdoc/OCLP-R/blob/3.0.1/CHANGELOG.md | CHANGELOG | **중간** — Tahoe USB 맵 | macOS 26 USB-Map-Tahoe.kext 추가. USB 1.1 Mac에 legacy USB map 주입. |
| YBronst OCLP-Plus Modern Wireless | https://github.com/YBronst/OCLP-Plus/blob/main/CHANGELOG.md | CHANGELOG | **높음** — Tahoe Broadcom Wi-Fi | Tahoe 26.x AWDL/Wi-Fi/AirDrop 복원. Legacy 패치 Tahoe에서 비활성화. Intel Wi-Fi(AirportItlwm) 미지원→OCLP-Mod 권장. |
| moraea unsupported-wifi-patches | https://github.com/moraea/unsupported-wifi-patches | GitHub 저장소 | **중간** — 레거시 Wi-Fi | 2007~2017 Mac BCM94328/94322/Atheros Wi-Fi 복원. Tahoe Modern Wireless와 별도 스택. |
| moraea T1-Patch | https://github.com/moraea/misc-patches/tree/main/T1-Patch | GitHub 디렉터리 | **중간** — T1 Mac (2016~17) | Touch ID, Apple Pay, T1 보안 기능 복원. MBP13,x/14,x. Tahoe T1 이슈 별도. |
| moraea IOUSBHostFamily-14.4 USB 패치 | https://github.com/moraea/misc-patches/tree/main/IOUSBHostFamily-14.4 | GitHub 디렉터리 | **중간** — USB 호스트 패밀리 | USB 1 패치. stephandeutsch/moraea USB 1.1 연구와 연계. |
| SurPlus (Syncretic) | https://github.com/reenigneorcim/SurPlus | GitHub 저장소 | **낮음** — Sequoia 서플라스 | Syncretic의 Sequoia 관련 kext. AAAMouSSE/telemetrap과 동일 개발자. Tahoe C2D 관련성. |
| GUTY345 Mantissa speed 패닉 수정 | https://github.com/GUTY345/OpenCore-Legacy-patcher-t2chip-fixBugs/tree/main | GitHub 디렉터리 | **높음** — T2 MacBook | UNSUPPORTED_MANTISSA_SPEED 커널 패닉, "Mac not supported by Tahoe" 메시지, UHD 630 그래픽 수정. |
| CryptexFixup / AMFIPass | https://github.com/acidanthera/CryptexFixup | GitHub 저장소 | **중간** — Ventura+ 설치 | Rosetta Cryptex 강제 설치, root hash 검증 비활성화. Tahoe T2/Non-T2 설치에 필수 kext. |

---

## 커뮤니티/포럼

| 제목 | 출처 URL | 유형 | 26x86 관련성 | 요약 |
|------|----------|------|--------------|------|
| macOS Tahoe 26 Unsupported Macs 토론 | https://forums.macrumors.com/threads/macos-tahoe-26-on-unsupported-macs-discussion.2458481/ | MacRumors 스레드 | **핵심** — 메인 커뮤니티 허브 | OCLP Tahoe 실험·성능·포기론 논의. albert-mueller T2 APFS 이슈 cross-post. 프로젝트 "사실상 abandoned" 우려도 존재. |
| T2 Mac Tahoe APFS 패닉 스레드 | https://forums.macrumors.com/threads/unsupported-t2-macs-oclp-when-trying-to-boot-macos-26-tahoe-on-an-ssd-where-it-is-fully-installed-it-fails-with-appleimage4-apfs-panic.2486563/ | MacRumors 스레드 | **핵심** — T2 디버깅 | albert-mueller가 T2 Tahoe APFS/AppleImage4 패닉 전용 스레드 개설. trustcache 오류 보고. |
| macOS Tahoe on Intel | https://forums.macrumors.com/threads/macos-tahoe-on-intel.2476282/ | MacRumors 스레드 | **중간** — 공식 Intel Mac | iMac 2020, MBP 2019 등 Apple 공식 지원 Intel Mac의 Tahoe 경험. OCLP와 별개. |
| macOS Tahoe Intel 성능 | https://forums.macrumors.com/threads/macos-tahoe-performance-on-intel.2474392/ | MacRumors 스레드 | **중간** — 성능 기대치 | Liquid Glass·WindowServer 메모리 누수·Intel 최적화 부족 보고. Mac Pro 2019에서 Sequoia 복귀 사례. |
| macOS Golden Gate 27 Unsupported | https://forums.macrumors.com/threads/macos-golden-gate-27-on-unsupported-macs-discussion.2483600/ | MacRumors 스레드 | **참고** — macOS 27 전망 | Tahoe도 OCLP 미지원 상태. macOS 27은 arm64-only로 OCLP 패치 불가능 논의. |
| SSE 4.2 에뮬레이션 스레드 (p.9) | https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/page-9 | MacRumors 스레드 | **높음** — C2D Tahoe | OCLP-T2 Wiki가 인용. AAAMouSSE/telemetrap Tahoe 재작성 필요성 논의. |
| r/OpenCoreLegacyPatcher | https://www.reddit.com/r/OpenCoreLegacyPatcher/ | Reddit | **중간** — Reddit 커뮤니티 | OCLP 실험·문제 해결·Tahoe Nightly 공유. ITECH4MAC 등에서 참조. |
| OpenCore Patcher Paradise Discord | https://discord.gg/rqdPgH8xSN | Discord | **중간** — 실시간 지원 | OCLP-T2 README에서 안내. T2 Mac 실험·패닉 로그 공유. |
| ITECH4MAC OCLP 3.0 Nightly 가이드 | https://www.itech4mac.net/2025/11/macos-tahoe-26-on-unsupported-macs-oclp3-nightly-full-guide/ | 블로그 | **높음** — Tahoe 설치 가이드 | Non-T2 Mac Tahoe Nightly 실험 절차. T2 Mac 설치 금지 명시. KDK/MetallibSupportPkg 재패치 필요. |
| ITECH4MAC OCLP 3.0 출시 예상 | https://www.itech4mac.net/2025/11/macos-tahoe-opencore-legacy-patcher-expected-release-date/ | 블로그 | **중간** — 일정 전망 | OCLP 3.0.0 미출시. T2/Non-T2 분류표. Sequoia+OCLP 2.4.1 일상 사용 권장. |
| The Register OCLP Intel Mac | https://www.theregister.com/software/2026/07/16/how-to-teach-an-old-intel-mac-new-tricks-with-opencore-legacy-patcher/5271880 | 언론 | **중간** — 일반 사용자 시각 | OCLP 2.4.1=Sequoia 한계. Tahoe 업그레이드 시 USB 불능 경고. OCLP Tahoe 지원 기대. |
| Gadget Hacks OCLP Tahoe 전망 | https://apple.gadgethacks.com/news/opencore-legacy-patcher-intel-mac-support-what-tahoe-26-means/ | 언론 | **중간** — 아키텍처 분석 | OCLP 3.0 겨울 2025 데드라인 미달. macOS 27에서 Universal Binary x86 코드 소멸→OCLP 구조적 한계. |
| OCLP typosquatting 경고 (#116) | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/discussions/116 | GitHub Discussion | **낮음** — 보안 | opencorelegacypatchert2.net 등 가짜 사이트·AsyncRAT 악성코드 경고. 공식 GitHub만 사용 권장. |
| MacGeneration Tahoe 불법 Mac | https://forums.macg.co/threads/installation-de-macos-tahoe-sur-les-mac-incompatibles.1401201/ | 프랑스 포럼 | **낮음** — 보안 | opencorelegacypatcher.org typosquatting·ClickFix 공격 문서화. albert-mueller #103 연계. |

---

## 알려진 제한사항

| 제목 | 출처 URL | 유형 | 26x86 관련성 | 요약 |
|------|----------|------|--------------|------|
| Core 2 Duo Mac Tahoe 부팅 불가 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki | Wiki | **핵심** — 2008~2010 Mac | AAAMouSSE+telemetrap이 Tahoe에서 패닉. 2021 이후 미업데이트·폐쇄 소스→재작성 필요. 가속 없이도 부팅 불가. |
| T2 Mac SIP 완전 비활성화 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki | Wiki | **핵심** — T2 보안 | T2 Mac은 SIP 0xFFF 하드코딩. Apple Pay 등 SIP 필수 기능 불가. OpenCorePkg 부팅 시 thermal throttling 유발. |
| Non-Metal Liquid Glass 비호환 | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 | GitHub Issue | **높음** — 2011 이하 GPU | Non-Metal 다운그레이드 방식으로 Liquid Glass UI 불가. 사용 가능한 UI 우회(workaround) 개발 예정. |
| Metal 8302 (2012~2014) 패치 부재 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/releases | GitHub Releases | **높음** — Mid-2012~2014 Mac | Metal 8302 패치 미완→Tahoe에서 주입 시 패닉. 안전 가드로 GPU 가속 없이 부팅만 허용. |
| OCLP 기부 중단·개발자 이탈 | https://opencollective.com/opencore-legacy-patcher/updates/closing-off-to-new-donations | OpenCollective | **높음** — 프로젝트 지속성 | 신규 기부 중단. dev departure로 Tahoe 릴리스 불확실. MacRumors "abandoned" 논의와 연결. |
| macOS 27 Golden Gate arm64-only | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki | Wiki | **핵심** — 프로젝트 범위 | macOS 27+는 Apple Silicon 전용. 26x86 프로젝트는 Tahoe(26)가 최종 목표. |
| KDK 미제공 빌드 설치 제한 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/discussions/171 | GitHub Discussion | **중간** — 업데이트 추적 | macOS 26.6+ KDK 미출시 시 OCLP-T2 루트 패치 불가. 26.5.2 이하 권장. |
| Tahoe 업데이트 시 루트 패치 소거 | https://dortania.github.io/OpenCore-Legacy-Patcher/POST-INSTALL.html | 문서 | **높음** — 유지보수 | macOS 업데이트마다 루트 패치 삭제→재적용 필수. OCLP 자체도 먼저 업데이트 필요. |
| Hackintosh EFI 빌드 미지원 | https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki | Wiki | **낮음** — 범위 제한 | OCLP-T2는 real Mac EFI만 생성. Hackintosh SMBIOS 스푸핑 취약점 수정(4.0.0.16050). |
| FileVault Tahoe 자동 활성화 | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 | GitHub Issue | **중간** — 암호화 | Tahoe 설치 시 FileVault 자동 ON→복호화 문제. Non-T2 Mac에서 apfs 관련 수정 필요. |
| Intel Wi-Fi OCLP-Plus 미지원 | https://github.com/YBronst/OCLP-Plus | GitHub README | **중간** — Wi-Fi 하드웨어 | OCLP-Plus는 Broadcom 전용. Intel Wi-Fi Mac은 OCLP-Mod 필요. |

---

## macOS 26 Tahoe 관련

| 제목 | 출처 URL | 유형 | 26x86 관련성 | 요약 |
|------|----------|------|--------------|------|
| macOS Tahoe Wikipedia | https://en.wikipedia.org/wiki/MacOS_Tahoe | Wikipedia | **기준** — 공식 OS 정보 | 2025-09-15 출시. Intel Mac 마지막 macOS. MAS 업그레이드 불가→System Settings만. |
| Apple 공식 Intel 지원 목록 (WWDC 2025) | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 | GitHub Issue | **핵심** — 지원 모델 | Mac Pro 2019, MBP 16" 2019, MBP 13" 2020(4TB), iMac 27" 2020만 공식 지원. MBA/Mini/iMac Pro Intel 탈락. |
| GSMArena Tahoe Intel 분석 | https://www.gsmarena.com/macos_tahoe_26_is_the_last_version_for_intelpowered_macs_and_only_some_are_supported-news-68188.php | 언론 | **중간** — 지원 범위 정리 | 2020 Intel MBA/Mini/iMac Pro 미지원. 2018~2019 T2 MBP 등 OCLP 대상. |
| MrMacintosh Tahoe 26.5.1 + OCLP | https://mrmacintosh.com/macos-tahoe-26-5-1-update-everything-you-need-to-know/ | 블로그 | **높음** — 업데이트 호환 | OCLP 2.4.1 + Tahoe 26.5.1 = 호환 불가. KDK/MetallibSupportPkg 테스트 진행 중. |
| OCLP 2.4.1 현재 안정 버전 | https://github.com/dortania/OpenCore-Legacy-Patcher/releases | GitHub Releases | **기준** — 현재 프로덕션 | Sequoia 15.x까지 공식 지원. Tahoe 26 설치 시 USB/패치 실패 보고. |
| OCLP Nightly Builds (GitHub Actions) | https://github.com/dortania/OpenCore-Legacy-Patcher/actions | CI/CD | **높음** — 실험 빌드 | Green build→Artifacts→OpenCore-Patcher.pkg.zip. Non-T2 Tahoe 실험용. 일상 사용 비권장. |
| hackdoc OCLP-R CHANGELOG 3.0.1 | https://github.com/hackdoc/OCLP-R/blob/3.0.1/CHANGELOG.md | CHANGELOG | **높음** — Tahoe 기능 목록 | macOS 26 상수, USB-Map-Tahoe, apfs_aligned.efi, Liquid Glass 아이콘, PatcherSupportPkg 1.9.5+. |
| Apple Intelligence Intel 미지원 | https://www.gsmarena.com/macos_tahoe_26_is_the_last_version_for_intelpowered_macs_and_only_some_are_supported-news-68188.php | 언론 | **낮음** — 기능 제한 | Tahoe의 Apple Intelligence는 Apple Silicon 전용. Intel Mac OCLP 목표와 무관. |
| macOS 26 Liquid Glass UI | https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167 | GitHub Issue | **중간** — UI 패치 | Metal 31001/3802/Non-Metal별 Liquid Glass 초기 결과 스크린샷. Non-Metal은 UI 우회 필요. |
| Tahoe x86 Rosetta 2 잔존 | https://forums.macrumors.com/threads/macos-golden-gate-27-on-unsupported-macs-discussion.2483600/ | MacRumors 스레드 | **참고** — macOS 27 | Tahoe=마지막 x86 macOS. macOS 27 Golden Gate는 arm64-only, Rosetta 2는 레거시 게임용으로만 잔존 예상. |

---

## 조사 통계

| 항목 | 수치 |
|------|------|
| 총 인벤토리 항목 | **78** |
| GitHub 저장소/Issue/PR | 52 |
| MacRumors/커뮤니티 | 10 |
| 문서/블로그/언론 | 16 |
| 조사일 | 2026-09-04 |

---

## 우선 추적 대상 (26x86 로드맵)

1. **albert-mueller/OpenCore-Legacy-Patcher-T2** — Issue #69, #130 (APFS/AppleImage4)
2. **dortania/OpenCore-Legacy-Patcher** — Issue #1167 (공식 Tahoe 릴리스)
3. **dortania/MetallibSupportPkg + KdkSupportPkg** — Tahoe 빌드별 PKG/KDK
4. **hackdoc/OCLP-R + pyquick Metallib** — Non-T2 Metal 3802/8302
5. **vytska69/DrDonk AppleKeyStore 연구** — T2 SEP/KeyStore 근본 해결

---

*이 문서는 26x86 프로젝트 연구용 living document입니다. 새로운 이슈·릴리스 발견 시 갱신하세요.*
