# OCLP에서 26x86으로 전환 (Migration from OCLP)

Dortania **OpenCore Legacy Patcher(OCLP)**, **OCLP-T2**, **OCLP-Mod**, **OCLP-Plus** 등에서 26x86으로 옮길 때의 정책과 주의사항입니다.

> 설정 경로 상세: [Configuration.md](./Configuration.md)  
> 아키텍처: [ARCHITECTURE-26x86.md](../ARCHITECTURE-26x86.md)

---

## English Summary

26x86 **reads** legacy OCLP settings **once** on first launch when the files are readable, then uses only `~/Library/Preferences/com.niseullent.26x86.plist`. Removing the OCLP shared plist is **optional** (for a clean OCLP uninstall only). **Do not** run OCLP and 26x86 auto-patch launchd jobs at the same time.

---

## 자동 마이그레이션 (1회)

26x86 **첫 실행** 시, 읽을 수 있는 OCLP 설정이 있으면 **한 번만** 가져옵니다.

1. `~/Library/Preferences/com.dortania.opencore-legacy-patcher.plist` (사용자 Preferences)
2. `/Users/Shared/.com.dortania.opencore-legacy-patcher.plist` (공유 plist, **읽기 가능한 경우만**)

동작 요약:

| 조건 | 26x86 동작 |
|------|-----------|
| 26x86 plist 없음 + OCLP plist 읽기 가능 | 키 복사 후 `26x86.migrated_from_oclp` 설정 |
| OCLP plist가 **root 소유** 등으로 읽기 불가 | 마이그레이션 **건너뜀**, 26x86 기본값 사용 (크래시 없음) |
| 이미 마이그레이션 완료 | 재실행하지 않음 (idempotent) |

가져온 뒤 로그에 안내가 표시됩니다. 이후 모든 읽기·쓰기는 **26x86 plist만** 사용하며, OCLP 공유 plist에는 **쓰지 않습니다.**

---

## OCLP 공유 plist 삭제 — **선택 사항**

`/Users/Shared/.com.dortania.opencore-legacy-patcher.plist` 제거는 **필수 단계가 아닙니다.**

| 목적 | 삭제 필요? |
|------|-----------|
| 26x86 정상 사용 | **아니오** — 26x86은 자체 plist만 사용 |
| OCLP 설정을 읽을 수 없어 마이그레이션을 건너뛴 경우 | **아니오** — 26x86 기본값으로 동작 가능 |
| OCLP를 **완전히 제거**하고 디스크를 정리하고 싶을 때 | **선택** — 원하면 수동 삭제 |

OCLP를 깨끗이 지우려는 경우에만, 관리자 권한으로 레거시 파일을 제거할 수 있습니다:

```bash
# 선택 사항 — OCLP 완전 제거·정리 시에만
sudo rm '/Users/Shared/.com.dortania.opencore-legacy-patcher.plist'
```

**26x86 설정 파일** `~/Library/Preferences/com.niseullent.26x86.plist`와는 **무관**합니다. 위 명령은 OCLP 레거시만 대상으로 합니다.

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
| OCLP 미설치 | 26x86 plist만 사용 |
| OCLP 설치 + shared plist 읽기 가능 | 1회 마이그레이션 |
| OCLP 설치 + root-owned shared plist | 마이그레이션 skip, 기본값; plist 삭제는 선택 |
| OCLP + 26x86 동시 auto-patch | **하지 말 것** — 26x86 설치 시 dortania launchd 정리 |

---

## 관련 문서

- [Configuration.md](./Configuration.md) — 경로·launchd·키 네임스페이스
- [Installation-Notes.md](./Installation-Notes.md) — 클린 설치·OS 버전 범위
- [T2-Mac-Notes.md](./T2-Mac-Notes.md) — T2 전용 주의
