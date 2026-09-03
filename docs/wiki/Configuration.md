# 26x86 설정 (Configuration)

26x86은 Dortania **OpenCore Legacy Patcher(OCLP)** 및 OCLP-T2와 **런타임 설정·Launch Services·앱 경로를 공유하지 않습니다.** 모든 사용자 대면 경로와 식별자는 `com.niseullent.26x86` / `26x86.*` 네임스페이스를 사용합니다.

> OCLP에서 전환하는 경우: [Migration-from-OCLP.md](./Migration-from-OCLP.md)  
> 아키텍처 상세: [ARCHITECTURE-26x86.md](../ARCHITECTURE-26x86.md)

---

## English Summary

26x86 stores settings in `~/Library/Preferences/com.niseullent.26x86.plist`, uses `~/Library/Application Support/26x86/` and `/Library/Application Support/26x86/` for app data, registers launchd jobs under `com.niseullent.26x86.*`, and namespaces preference keys as `26x86.*`. It never writes to OCLP shared paths at runtime.

---

## 설정 파일 (Preferences)

| 항목 | 경로 |
|------|------|
| **사용자 설정 (단일 진실 원천)** | `~/Library/Preferences/com.niseullent.26x86.plist` |
| Preferences 도메인 | `com.niseullent.26x86` |
| 로그 | `~/Library/Logs/26x86/` |
| 개발자 모드 마커 | `~/.26x86_developer` |

설정은 **`/Users/Shared/`에 쓰지 않습니다.** 사용자 홈의 `Library/Preferences`에 저장되며, 일반적으로 `sudo`로 패처를 실행해도 root 소유 공유 plist가 생기지 않습니다.

### 설정 파일 직접 확인

```bash
# plist 내용 보기
plutil -p ~/Library/Preferences/com.niseullent.26x86.plist

# defaults로 키 읽기/쓰기 (도메인 = com.niseullent.26x86)
defaults read com.niseullent.26x86
```

---

## 앱 지원 경로 (Application Support)

| 범위 | 경로 | 용도 |
|------|------|------|
| **시스템 (PKG 설치)** | `/Library/Application Support/26x86/` | `26x86.app`, 자동 패치 바이너리, 업데이트 페이로드 |
| **사용자** | `~/Library/Application Support/26x86/` | 사용자별 캐시·보조 데이터 |
| Applications 바로가기 | `/Applications/26x86.app` | PKG 설치 시 생성되는 심볼릭 링크/복사본 |
| Privileged Helper | `/Library/PrivilegedHelperTools/com.niseullent.26x86.privileged-helper` | 권한 상승 작업 |

**OCLP 레거시 경로** `/Library/Application Support/Dortania/`는 26x86 런타임에서 **사용하지 않습니다.**

---

## Launch Services (launchd)

PKG 설치 또는 루트 패치 활성화 시 등록되는 레이블은 모두 `com.niseullent.26x86.*` 접두사를 사용합니다.

| 레이블 | 유형 | 역할 |
|--------|------|------|
| `com.niseullent.26x86.auto-patch` | LaunchAgent | 부팅 시 자동 루트 패치 확인·적용 |
| `com.niseullent.26x86.macos-update` | LaunchDaemon | macOS 업데이트 후 패치 재적용 |
| `com.niseullent.26x86.os-caching` | LaunchDaemon | OS 캐싱(KDK 등) |
| `com.niseullent.26x86.rsr-monitor` | LaunchDaemon | RSR(보안 응답) 모니터링 |

설치된 plist 위치 예:

- LaunchAgent: `/Library/LaunchAgents/com.niseullent.26x86.auto-patch.plist`
- LaunchDaemon: `/Library/LaunchDaemons/com.niseullent.26x86.{macos-update,os-caching,rsr-monitor}.plist`

페이로드 원본: `payloads/Launch Services/com.niseullent.26x86.*.plist`

**OCLP 레이블** `com.dortania.opencore-legacy-patcher.*`와 **동시에 자동 패치를 실행할 수 없습니다.** 26x86 PKG 설치 시 레거시 dortania launchd 항목은 제거 대상에 포함됩니다.

---

## 설정 키 네임스페이스 (`26x86.*`)

신규·제품 전용 설정 키는 `26x86.` 접두사를 사용합니다.

| 키 (예) | 설명 |
|---------|------|
| `26x86` | 마커 키 (plist 초기화 시 `true`) |
| `26x86.migrated_from_oclp` | OCLP 설정 1회 마이그레이션 완료 플래그 |
| `26x86.auto_patch` | 자동 패치 관련 설정 |
| `26x86.verbose_logging` | 상세 로깅 |

### 레거시·GUI 키 (업스트림 호환)

마이그레이션 및 GUI 상태는 OCLP 시절 키 이름을 그대로 쓰는 경우가 있습니다 (예: `EnableCrashAndAnalyticsReporting`, `GUI:oc_build`, `AutoPatch_Notify_Mismatched_Disks`). 새 기능은 가능한 한 `26x86.*`로 추가합니다.

### 분석·크래시 보고 옵트아웃

```bash
defaults write com.niseullent.26x86 DisableCrashAndAnalyticsReporting -bool true
```

또는 26x86 앱 **설정(Settings)** 화면에서 비활성화할 수 있습니다.

---

## OCLP와의 경로 대조

| OCLP (레거시) | 26x86 |
|---------------|--------|
| `/Users/Shared/.com.dortania.opencore-legacy-patcher.plist` | `~/Library/Preferences/com.niseullent.26x86.plist` |
| `/Library/Application Support/Dortania/` | `/Library/Application Support/26x86/` |
| `com.dortania.opencore-legacy-patcher.*` | `com.niseullent.26x86.*` |
| OCLP defaults 키 | `26x86.*` (신규) + 레거시 GUI 키 (호환) |

OCLP에서의 전환 절차는 [Migration-from-OCLP.md](./Migration-from-OCLP.md)를 참고하세요.

---

## 내부 패키지 이름

Python 소스 패키지명 `opencore_legacy_patcher`는 업스트림 호환을 위해 유지됩니다. 사용자에게 보이는 이름·경로·번들 ID는 **26x86** / `com.niseullent.26x86` 입니다.
