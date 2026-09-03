# 26x86

<div align="center">
<img src="https://github.com/dortania/OpenCore-Legacy-Patcher/blob/macos-next/docs/images/OC-Patcher.png" alt="26x86 로고" width="256" />
<h1>26x86</h1>
<h3>x86 기반 Mac을 위한 더 나은 macOS 26 시스템</h3>
<p><strong>Better macOS 26 System for x86-Based Macintosh</strong> — T2 칩 탑재 Mac을 포함한 Intel Mac에서 macOS 26 Tahoe 지원을 목표로 하는 실험적 커뮤니티 포크입니다.</p>
</div>

> **실험적 알파** — 사용 전 [위키 주의사항](docs/wiki/Warnings.md)과 [면책 조항](DISCLAIMER.md)을 읽고, **전체 백업** 후 여분의 Mac에서 테스트하세요.

[Acidanthera OpenCorePkg](https://github.com/acidanthera/OpenCorePkg)와 [Lilu](https://github.com/acidanthera/Lilu)를 기반으로, 공식·비공식 지원 Mac에서 macOS를 실행하고 기능을 잠금 해제하는 Python 프로젝트입니다.

26x86은 [OpenCore Legacy Patcher T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2)를 포크했으며, 해당 프로젝트는 Dortania의 [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher)를 확장합니다.

**한글판 최적화:** 사용자 문서·GUI 마법사·CLI 도움말의 기본 언어는 한국어입니다. 영문 보조: [docs/README.en.md](docs/README.en.md) · [docs/KOREAN_EDITION.md](docs/KOREAN_EDITION.md)

보안 연구자는 [GitHub 보안 정책](https://github.com/NiSeullent/26x86/security/policy)을 확인한 뒤 취약점을 보고할 수 있습니다.

---

## 위키

상세 주의사항·이슈·설치 노트는 **위키**에 모았습니다.

| 문서 | 설명 |
|------|------|
| [위키 홈](docs/wiki/Home.md) | 목차 및 링크 |
| [⚠️ 주의사항](docs/wiki/Warnings.md) | C2D, GPU, T2 SIP, Hackintosh, macOS 27 |
| [알려진 이슈](docs/wiki/Known-Issues.md) | T2 진행 상황 |
| [GPU 제한](docs/wiki/GPU-Limitations.md) | Metal 8302, Non-Metal |
| [T2 Mac 노트](docs/wiki/T2-Mac-Notes.md) | SIP, 다운로드, APFS |
| [설치·업그레이드](docs/wiki/Installation-Notes.md) | 클린 설치, OCLP 마이그레이션 |
| [면책 요약](docs/wiki/Disclaimer.md) | [DISCLAIMER.md](DISCLAIMER.md) 링크 |
| [English index](docs/wiki/README.en.md) | 영문 위키 목차 |

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

## 시작하기

- Dortania 가이드(영문): [OpenCore Legacy Patcher Guide](https://dortania.github.io/OpenCore-Legacy-Patcher/)
- 소스 실행: [SOURCE.md](SOURCE.md)
- 개발 셋업: [docs/SETUP.md](docs/SETUP.md)
- 영문 보조: [docs/README.en.md](docs/README.en.md) · [docs/SETUP.en.md](docs/SETUP.en.md)
- Releases: https://github.com/NiSeullent/26x86/releases

## 지원

본 프로젝트는 **「있는 그대로(AS IS)」** 제공되며 공식 기술 지원을 보장하지 않습니다.

- [OpenCore Patcher Paradise Discord](https://discord.gg/rqdPgH8xSN)
- 문제 해결 시 [OpenCore 디버그 문서](https://dortania.github.io/OpenCore-Legacy-Patcher/DEBUG.html)를 참고해 로그를 준비하세요.

## 법적·라이선스

| 문서 | 설명 |
|------|------|
| [DISCLAIMER.md](DISCLAIMER.md) | 면책 조항 (한국어) |
| [LICENSE.txt](LICENSE.txt) | BSD 3-Clause |
| [NOTICE.md](NOTICE.md) | 업스트림 고지 |
| [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) | 서드파티 라이선스 |
| [CREDITS.md](CREDITS.md) | 기여자 목록 |

## 기여자

전체 목록은 [CREDITS.md](CREDITS.md)를 참고하세요. OpenCorePkg·Lilu, Dortania OCLP, OCLP-T2, NiSeullent 및 커뮤니티 기여자에게 감사드립니다.
