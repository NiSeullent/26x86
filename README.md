# 26x86

<div align="center">
<img src="https://github.com/dortania/OpenCore-Legacy-Patcher/blob/macos-next/docs/images/OC-Patcher.png" alt="26x86 로고" width="256" />
<h1>26x86</h1>
<h3>x86 기반 Mac을 위한 더 나은 macOS 26 시스템</h3>
<p><strong>Better macOS 26 System for x86-Based Macintosh</strong> — T2 칩 탑재 Mac을 포함한 Intel Mac에서 macOS 26 Tahoe 지원을 목표로 하는 실험적 커뮤니티 포크입니다.</p>
</div>

> **실험적 알파** — [위키 주의사항](docs/wiki/Warnings.md)을 읽고 **전체 백업** 후 여분의 Mac에서 테스트하세요.

**한국어가 기본 문서 언어입니다.** 영문: [docs/README.en.md](docs/README.en.md)

---

## 시작하기

```bash
python -m x86 wizard    # 권장 — 마법사 GUI
python -m x86 --help    # CLI: detect · build · patch · status · wizard
```

macOS: `26x86.command` 더블클릭 · PKG: [Releases](https://github.com/NiSeullent/26x86/releases)

---

## 문서

| 문서 | 설명 |
|------|------|
| **[위키 홈](docs/wiki/Home.md)** | 주의사항, 설치, 설정, OCLP 전환, CLI |
| **[클린룸 아키텍처](docs/CLEANROOM-ARCHITECTURE.md)** | `x86/` 패키지, JSON 설정, wizard-first 설계 |
| [소스 실행](SOURCE.md) | 개발자용 |
| [보안 정책](https://github.com/NiSeullent/26x86/security/policy) | 취약점 보고 |

---

## 지원

본 프로젝트는 **「있는 그대로(AS IS)」** 제공됩니다.

- [OpenCore Patcher Paradise Discord](https://discord.gg/rqdPgH8xSN)
- [Dortania OCLP 가이드](https://dortania.github.io/OpenCore-Legacy-Patcher/) (영문, 업스트림 참고)

## 법적·라이선스

[DISCLAIMER.md](DISCLAIMER.md) · [LICENSE.txt](LICENSE.txt) · [NOTICE.md](NOTICE.md) · [**원본 저장소 전체**](docs/wiki/Upstream-Repositories.md) · [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) · [CREDITS.md](CREDITS.md)
