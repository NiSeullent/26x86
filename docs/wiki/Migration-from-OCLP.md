# OCLP에서 26x86으로 전환

26x86은 OpenCore Legacy Patcher(OCLP)와 **런타임 설정·Launch Services·앱 경로를 공유하지 않습니다.** OCLP를 제거하지 않아도 26x86은 독립적으로 동작합니다.

## 핵심 차이

| OCLP | 26x86 |
|------|--------|
| `/Users/Shared/.com.dortania.opencore-legacy-patcher.plist` | `~/Library/Preferences/com.sharhene777.26x86.plist` |
| `com.dortania.opencore-legacy-patcher.*` | `com.sharhene777.26x86.*` |
| OpenCore-Patcher.app | 26x86.app |

26x86은 **OCLP 공유 plist를 읽거나 쓰지 않습니다.** root 소유 OCLP plist가 남아 있어도 26x86 동작에 영향을 주지 않습니다.

## 전환 절차

1. **데이터 백업** — Time Machine 또는 전체 디스크 백업
2. **26x86 설치** — [Releases](https://github.com/NiSeullent/26x86/releases) 또는 소스 실행
3. **OCLP 자동 패치 비활성화** (선택) — OCLP LaunchAgent가 있다면 제거:

```bash
launchctl bootout gui/$(id -u) /Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist 2>/dev/null
sudo launchctl bootout system /Library/LaunchDaemons/com.dortania.opencore-legacy-patcher.* 2>/dev/null
```

4. **26x86으로 EFI 재빌드** — 마법사 또는 `python -m x86 build --model YOUR_MODEL`
5. **루트 패치** — 26x86 전용 패치 적용

## OCLP plist 정리 (선택)

OCLP plist 삭제는 **26x86 사용에 필수가 아닙니다.** 디스크 정리 목적으로만 선택적으로 진행하세요:

```bash
# root 소유인 경우에만 sudo 필요
sudo rm -f '/Users/Shared/.com.dortania.opencore-legacy-patcher.plist'
```

## 설정 마이그레이션

26x86은 OCLP 설정을 **자동으로 가져오지 않습니다.** GUI 설정·모델 선택 등은 26x86에서 다시 구성하세요.

자세한 설정 경로: [Configuration.md](./Configuration.md)
