# 26x86

<div align="center">
<img src="https://github.com/dortania/OpenCore-Legacy-Patcher/blob/macos-next/docs/images/OC-Patcher.png" alt="26x86 로고" width="256" />
<h1>26x86</h1>
<h3>x86 기반 Mac을 위한 더 나은 macOS 26 시스템</h3>
<p><strong>Better macOS 26 System for x86-Based Macintosh</strong> — T2 칩 탑재 Mac을 포함한 Intel Mac에서 macOS 26 Tahoe 지원을 목표로 하는 실험적 커뮤니티 포크입니다.</p>
</div>

> **면책 조항:** 본 소프트웨어는 실험적 알파 단계입니다. 사용 전 [DISCLAIMER.md](./DISCLAIMER.md)를 반드시 읽고, **전체 데이터를 백업**한 뒤 여분의 Mac에서 테스트하세요.

[Acidanthera OpenCorePkg](https://github.com/acidanthera/OpenCorePkg)와 [Lilu](https://github.com/acidanthera/Lilu)를 기반으로, 공식·비공식 지원 Mac에서 macOS를 실행하고 기능을 잠금 해제하는 Python 프로젝트입니다.

26x86은 [OpenCore Legacy Patcher T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2)를 포크했으며, 해당 프로젝트는 Dortania의 [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher)를 확장합니다.

**한글판 최적화:** 사용자 문서·GUI 마법사·CLI 도움말의 기본 언어는 한국어입니다. 영문 보조 문서: [docs/README.en.md](./docs/README.en.md) · [docs/KOREAN_EDITION.md](./docs/KOREAN_EDITION.md)

보안 연구자는 [GitHub 보안 정책](https://github.com/NiSeullent/26x86/security/policy)을 확인한 뒤 취약점을 보고할 수 있습니다.

---

## ⚠️ Intel Core 2 Duo Mac 주의

다음 모델 등은 AAAMouSSE·telemetrap 한계로 **현재 macOS 26 Tahoe 부팅이 불가능**할 수 있습니다.

- 2008–2010 MacBook / MacBook Pro / MacBook Air
- 2009–2010 Mac mini
- 2008 Mac Pro

자세한 논의: [MacRumors 스레드](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/page-9). macOS 26에서 동작하려면 해당 kext의 역공학·재작성이 필요할 수 있으며, 두 kext는 2021년 이후 업데이트가 없고 **폐쇄 소스**입니다.

## ⚠️ 그래픽 패치 미완료 모델

macOS 26에서 다음 GPU 클래스는 **그래픽 패치가 없어 커널 패닉**이 발생할 수 있습니다.

- **Metal 8302** — 2012–2014년 Mac 전반
- **Non-Metal** — 2011년 Mac 전반

작업 진행 중이며, 해당 환경에서는 패치 주입을 막아 **가속 없이 사용**할 수 있도록 안전 장치를 두고 있습니다.

## ⚠️ T2 Mac — SIP(시스템 무결성 보호)

**T2 Mac에서는 SIP가 완전히 비활성화(0xFFF)될 수 있습니다.** OpenCorePkg 부팅 시 열·스로틀링 등 이슈로 SIP 비활성화가 하드코딩되어 있을 수 있습니다. T2가 아닌 Mac(T1·비-T Mac)에는 적용되지 않을 수 있습니다.

## ⚠️ Hackintosh EFI 빌드 미지원

본 패처는 **실제 Mac**용 OpenCore EFI를 생성합니다. Hackintosh용 BOOTx64.efi 워크플로와는 다릅니다. Hackintosh에서 EFI를 빌드하는 것은 지원하지 않습니다.

## ⚠️ macOS 27 Golden Gate 이후 미지원

macOS 27 Golden Gate 및 이후 버전은 **Apple Silicon(arm64) 전용**으로 예상됩니다. **macOS 26 Tahoe**가 본 프로젝트의 마지막 주요 지원 대상입니다.

## 실험적 T2 포크

Dortania 공식 OCLP가 아직 T2 Mac을 지원하지 않는 가운데, **macOS 15 Sequoia·macOS 26 Tahoe T2 지원**을 실험적으로 추가합니다. 알파 단계이므로 백업 후 여분의 T2 Mac에서만 시험하세요.

### T2 Mac — 다운로드 안내

GitHub **Code → Download ZIP**은 개발 중 커밋으로 인해 불안정할 수 있습니다. **Releases**에서 받는 것을 권장합니다.

### T2 진행 상황 (요약)

- [x] 인스톨러 부팅
- [ ] MacBookAir8,1 / 8,2 인스톨러 부팅
- [ ] T2 내부 디스크 마운트 — [이슈 #69](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/69)
- [ ] 데스크톱 도달
- [ ] 설치 후 2단계 이슈
- [ ] GPU 가속 / Wi-Fi (일부 T2는 기본 가속 가능)

T2·비-T2 x86 Mac 모두에서 macOS 26 Tahoe 호환성 개선을 목표로 합니다.

---

## 주요 기능

- macOS Monterey, Ventura, Sonoma, Sequoia 및 Tahoe 지원(목표)
- OTA(무선) 시스템 업데이트
- Penryn 이후 Mac 지원
- BCM943224 이후 무선 칩셋 WPA Wi-Fi·Personal Hotspot
- SIP, FileVault 2, .im4m Secure Boot, Vaulting(모델·구성에 따라 다름)
- 비네이티브 OS에서 Recovery / Safe Mode / Single-user Mode
- Sidecar, AirPlay to Mac 등 기능 잠금 해제
- 비-Apple 저장장치 SATA·NVMe 전력 관리
- APFS ROM 등 **펌웨어 패치 불필요**
- Metal·Non-Metal GPU 그래픽 가속(지원 모델 한정)

---

## 설치·업그레이드 참고

- **클린 설치·업그레이드**만 공식 지원합니다. Patched Sur, bigmac 등으로 이미 패치된 Big Sur 설치본은 APFS 스냅샷·SIP 무결성 문제로 사용할 수 없습니다.
- OCLP-Mod, OCLP-Plus, Dortania OCLP 사용자는 루트 패치를 되돌린 뒤 본 패처로 업그레이드할 수 있습니다.
- 본 패처로 macOS를 재설치하면서 **기존 데이터를 유지**할 수 있습니다.
- 26x86은 Monterey~Tahoe 패치를 공식 지원합니다. 그 이전 OS는 OpenCore가 동작할 수 있으나 Albert Müller 포크 기준 공식 지원은 제공하지 않습니다.
- Mojave·Catalina는 [dosdude1 패처](http://dosdude1.com) 사용을 권장합니다.

## 시작하기

- Dortania 가이드(영문): [OpenCore Legacy Patcher Guide](https://dortania.github.io/OpenCore-Legacy-Patcher/)
- 소스 실행: [SOURCE.md](./SOURCE.md) (한국어)
- 개발환경(한국어): [docs/SETUP.md](./docs/SETUP.md)
- 영문 개요: [docs/README.en.md](./docs/README.en.md)
- 한글판 최적화 안내: [docs/KOREAN_EDITION.md](./docs/KOREAN_EDITION.md)

## 지원

본 프로젝트는 **「있는 그대로(AS IS)」** 제공되며 공식 기술 지원을 보장하지 않습니다. 커뮤니티 Discord 등에서 도움을 받을 수 있습니다.

- [OpenCore Patcher Paradise Discord](https://discord.gg/rqdPgH8xSN)
- 문제 해결 시 [OpenCore 디버그 문서](https://dortania.github.io/OpenCore-Legacy-Patcher/DEBUG.html)를 참고해 로그를 준비하세요.

## 법적·라이선스

| 문서 | 설명 |
|------|------|
| [DISCLAIMER.md](./DISCLAIMER.md) | 면책 조항 (한국어) |
| [LICENSE.txt](./LICENSE.txt) | BSD 3-Clause |
| [NOTICE.md](./NOTICE.md) | 업스트림 고지 |
| [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) | 서드파티 라이선스 |
| [CREDITS.md](./CREDITS.md) | 기여자 목록 |

## 기여자

전체 목록은 [CREDITS.md](./CREDITS.md)를 참고하세요. OpenCorePkg·Lilu, Dortania OCLP, OCLP-T2, NiSeullent 및 커뮤니티 기여자에게 감사드립니다.
