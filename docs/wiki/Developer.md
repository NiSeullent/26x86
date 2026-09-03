# 개발자 안내

일반 사용자는 [Home.md](./Home.md)와 [SETUP.md](../SETUP.md)만 참고하면 됩니다.

---

## 저장소 구조 (요약)

| 경로 | 역할 |
|------|------|
| `x86/` | CLI·마법사 GUI·설정·패치 관리 |
| `opencore_legacy_patcher/` | 패치·EFI 빌드 로직 (내부 호환 층) |
| `payloads/` | kext, OpenCore, Launch Services |
| `ci_tooling/` | PKG·PyInstaller 빌드 |

## 실행·빌드

```bash
python3 26x86.command
python3 -m x86 detect --json
python3 Build-Project.command
```

상세: [SETUP.md](../SETUP.md), [SOURCE.md](../../SOURCE.md)

## 설정

- `~/Library/Preferences/com.niseullent.26x86.plist` 또는 `~/Library/Application Support/26x86/config.json`
- 이전 패처와 자동 패치 **동시 사용 금지** — [Migration-from-OCLP.md](./Migration-from-OCLP.md)

## 원본·라이선스

[Upstream-Repositories.md](./Upstream-Repositories.md) · [CREDITS.md](../../CREDITS.md) · [NOTICE.md](../../NOTICE.md)
