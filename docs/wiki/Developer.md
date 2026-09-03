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
# macOS
python3 26x86.command
python3 -m x86 detect --json
python3 Build-Project.command

# Windows
python -m x86 wizard
26x86.bat

# Linux
python3 -m x86 wizard
./26x86.sh
```

**macOS 전용:** EFI 빌드, 루트 패치, PKG/LaunchAgent. Windows/Linux에서는 CLI·마법사 GUI·설정 JSON만 지원합니다. 자세한 실행 방법은 [SETUP.md](../SETUP.md#windows--linux에서-실행-소스)를 참고하세요.

상세: [SETUP.md](../SETUP.md), [SOURCE.md](../../SOURCE.md)

## 그래픽·compositor Research

- [SkyLight-LUT-Tracks.md](../SkyLight-LUT-Tracks.md) — Autopilot/극한도전 Mission Control · 트랙 A–L
- [Tahoe-SkyLight-LUT-Research.md](../Tahoe-SkyLight-LUT-Research.md) — 합성 파이프라인 · 성공 기준
- [Tahoe-Graphics-Roadmap.md](../Tahoe-Graphics-Roadmap.md) — Layer B compositor
- [Mac-Pro-Tahoe-Yellow-Screen.md](./Mac-Pro-Tahoe-Yellow-Screen.md)

## 설정

- **macOS:** `~/Library/Preferences/com.niseullent.26x86.plist` 또는 `~/Library/Application Support/26x86/config.json`
- **Windows:** `%APPDATA%\26x86\config.json`
- **Linux:** `~/.config/26x86/config.json`
- 이전 패처와 자동 패치 **동시 사용 금지** — [Migration.md](./Migration.md)

## 원본·라이선스

[Upstream-Repositories.md](./Upstream-Repositories.md) · [CREDITS.md](../../CREDITS.md) · [NOTICE.md](../../NOTICE.md)
