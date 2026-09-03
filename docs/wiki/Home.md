# 26x86 위키

**26x86** — x86 기반 Mac을 위한 더 나은 macOS 26 시스템

> **한국어가 기본 문서 언어입니다.** 영문 보조: [docs/README.en.md](../README.en.md) · [wiki/README.en.md](./README.en.md)

---

## 빠른 시작

| 방법 | 명령 |
|------|------|
| **권장 (마법사 GUI)** | `python -m x86 wizard` |
| macOS 더블클릭 | `26x86.command` |
| CLI 도움말 | `python -m x86 --help` |

```bash
python -m x86 detect [--json]   # 하드웨어 탐지
python -m x86 build [--model ...] # OpenCore EFI 빌드
python -m x86 patch [--auto]      # 루트 패치
python -m x86 status              # 설정·패치·EFI 상태
python -m x86 wizard              # 기본 GUI (마법사)
```

고급 레거시 메뉴: `X86_ADVANCED=1 python -m x86 wizard` (점진 폐기 예정)

아키텍처 상세: [CLEANROOM-ARCHITECTURE.md](../CLEANROOM-ARCHITECTURE.md)

---

## 목차

| 문서 | 설명 |
|------|------|
| [Warnings.md](./Warnings.md) | ⚠️ 모든 주의사항 통합 (C2D, GPU, T2 SIP, Hackintosh, macOS 27) |
| [Known-Issues.md](./Known-Issues.md) | 알려진 이슈 및 T2 진행 상황 |
| [Disclaimer.md](./Disclaimer.md) | 면책 조항 요약 및 [DISCLAIMER.md](../../DISCLAIMER.md) 링크 |
| [GPU-Limitations.md](./GPU-Limitations.md) | Metal 8302·Non-Metal GPU 제한 |
| [T2-Mac-Notes.md](./T2-Mac-Notes.md) | T2 Mac 전용 주의 (SIP, APFS, 다운로드) |
| [Installation-Notes.md](./Installation-Notes.md) | 클린 설치, 업그레이드, 개발 환경 |
| [Configuration.md](./Configuration.md) | 설정 경로, App Support, launchd, `26x86.*` 키 |
| [Migration-from-OCLP.md](./Migration-from-OCLP.md) | OCLP 1회 자동 마이그레이션, 공존 주의 |
| [Orphan-Files-Archive.md](./Orphan-Files-Archive.md) | 제거·보관된 고아 파일 목록 |
| [Upstream-Repositories.md](./Upstream-Repositories.md) | **원본 저장소 전체** — OCLP, OCLP-T2, Acidanthera, moraea 등 |
| [README.en.md](./README.en.md) | English wiki index |

## 개발자·아키텍처

| 문서 | 설명 |
|------|------|
| [ARCHITECTURE-26x86.md](../ARCHITECTURE-26x86.md) | 26x86 독립 런타임 설계 |
| [DEPENDENCY-AUDIT.md](../DEPENDENCY-AUDIT.md) | OCLP 의존성 감사 |

---

## 법적·라이선스

| 문서 | 경로 |
|------|------|
| 면책 조항 (전문) | [DISCLAIMER.md](../../DISCLAIMER.md) |
| BSD 3-Clause | [LICENSE.txt](../../LICENSE.txt) |
| 업스트림 고지 | [NOTICE.md](../../NOTICE.md) |
| 원본 저장소 전체 | [Upstream-Repositories.md](./Upstream-Repositories.md) |
| 서드파티 라이선스 | [THIRD_PARTY_LICENSES.md](../../THIRD_PARTY_LICENSES.md) |
| 기여자 | [CREDITS.md](../../CREDITS.md) |

## 외부 링크

- [Releases](https://github.com/NiSeullent/26x86/releases)
- [보안 정책](https://github.com/NiSeullent/26x86/security/policy)
- [Dortania OCLP 가이드](https://dortania.github.io/OpenCore-Legacy-Patcher/) (영문)
- [OpenCore Patcher Paradise Discord](https://discord.gg/rqdPgH8xSN)
