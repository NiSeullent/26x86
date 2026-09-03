# OCLP에서 26x86으로 전환 (Migration from OCLP)

Dortania **OpenCore Legacy Patcher(OCLP)**, **OCLP-T2**, **OCLP-Mod**, **OCLP-Plus** 등에서 26x86으로 옮길 때의 정책과 주의사항입니다.

> 설정 경로 상세: [Configuration.md](./Configuration.md)

---

## English Summary

26x86 uses only its own settings (`~/Library/Application Support/26x86/config.json` and `~/Library/Preferences/com.niseullent.26x86.plist`). It **never reads or writes** OCLP legacy plists under `/Users/Shared/` or `com.dortania.*`. **Do not** run OCLP and 26x86 auto-patch launchd jobs at the same time.

---

## 26x86은 OCLP 설정을 사용하지 않습니다

26x86은 OCLP의 공유 plist·Preferences plist를 **읽거나 쓰지 않습니다.**

| OCLP 경로 | 26x86 동작 |
|-----------|-----------|
| `/Users/Shared/.com.dortania.opencore-legacy-patcher.plist` | **무시** — 읽기·쓰기 없음 |
| `~/Library/Preferences/com.dortania.opencore-legacy-patcher.plist` | **무시** |

OCLP plist 삭제는 **필수가 아닙니다.** 26x86은 자체 설정만 사용합니다.

---

## OCLP와 26x86 동시 실행 — **지원 안 함**

OCLP와 26x86의 **자동 패치(launchd)** 를 동시에 켜 두면 충돌할 수 있습니다.

| 구성 | 결과 |
|------|------|
| OCLP launchd + 26x86 launchd 동시 활성 | **지원 안 함** — 패치·업데이트 경쟁 가능 |
| 26x86 PKG 설치 | `com.dortania.opencore-legacy-patcher.*` launchd 제거 포함 |
| OCLP만 제거하고 26x86 사용 | 26x86 launchd만 유지 |

권장 순서:

1. OCLP에서 **루트 패치 되돌리기** (Revert Root Patches) — [Installation-Notes.md](./Installation-Notes.md)
2. 26x86 설치 및 루트 패치 활성화
3. (선택) OCLP 앱·레거시 plist 정리

---

## 다른 포크에서 업그레이드

- **OCLP-Mod**, **OCLP-Plus**, **Dortania OCLP** 사용자는 루트 패치를 되돌린 뒤 26x86으로 업그레이드할 수 있습니다.
- 26x86으로 macOS를 **재설치**하면서 **기존 사용자 데이터를 유지**할 수 있습니다.
- Patched Sur, bigmac 등 **타사 Big Sur 패치** 설치본은 APFS 스냅샷·SIP 문제로 공식 지원 경로가 아닙니다.

---

## 시나리오별 요약

| 시나리오 | 26x86 동작 |
|----------|-----------|
| OCLP 미설치 | 26x86 기본 설정으로 시작 |
| OCLP 설치 + shared plist 존재 | OCLP plist **무시**, 26x86 자체 설정만 사용 |
| OCLP + 26x86 동시 auto-patch | **하지 말 것** — 26x86 설치 시 dortania launchd 정리 |

---

## 관련 문서

- [Configuration.md](./Configuration.md) — 경로·launchd·키 네임스페이스
- [Installation-Notes.md](./Installation-Notes.md) — 클린 설치·OS 버전 범위
- [T2-Mac-Notes.md](./T2-Mac-Notes.md) — T2 전용 주의
