# 26x86 설정 (Configuration)

26x86은 Dortania **OpenCore Legacy Patcher(OCLP)** 및 OCLP-T2와 **런타임 설정·Launch Services·앱 경로를 공유하지 않습니다.**  
클린룸 아키텍처 기준으로 사용자 설정은 **JSON**(`config.json`)에 저장하며, 식별자는 `com.sharhene777.26x86` 네임스페이스를 사용합니다.

> OCLP에서 전환: [Migration-from-OCLP.md](./Migration-from-OCLP.md)  
> 아키텍처: [CLEANROOM-ARCHITECTURE.md](../CLEANROOM-ARCHITECTURE.md)

---

## English Summary

26x86 stores settings in `~/Library/Application Support/26x86/config.json` (mode `0600`, no symlinks). App support uses `/Library/Application Support/26x86/` and `~/Library/Application Support/26x86/cache/`. Launchd labels use `com.sharhene777.26x86.*`. Legacy `/Users/Shared/` OCLP plists are never written at runtime.

---

## 설정 파일 (`config.json`)

| 항목 | 경로 |
|------|------|
| **사용자 설정 (단일 진실 원천)** | `~/Library/Application Support/26x86/config.json` |
| 로컬 캐시 (PatcherSupportPkg 등) | `~/Library/Application Support/26x86/cache/` |
| 로그 | `~/Library/Logs/26x86/` |
| 개발자 모드 마커 | `~/.26x86_developer` |

설정은 **`/Users/Shared/`에 쓰지 않습니다.** JSON 파일 권한은 `0600`이며, 심볼릭 링크 경로는 거부합니다.

### 예시 (`config.json`)

```json
{
  "version": 1,
  "auto_patch": false,
  "verbose_logging": false,
  "last_detect": {
    "model": "iMac18,3",
    "timestamp": "2026-09-04T00:00:00Z"
  }
}
```

### 설정 확인·편집

```bash
# 내용 보기
python3 -m json.tool ~/Library/Application\ Support/26x86/config.json

# CLI로 상태 요약
python -m x86 status
```

`SettingsStore`(`x86/settings.py`)가 읽기·쓰기를 담당합니다. 신규 코드는 plist/`defaults`가 아닌 이 API를 사용합니다.

---

## 번들 ID·식별자

| 도메인 | 값 |
|--------|-----|
| **Bundle ID** | `com.sharhene777.26x86` |
| **Privileged Helper** | `com.sharhene777.26x86.privileged-helper` |
| **LaunchAgents** | `com.sharhene777.26x86.{auto-patch,macos-update,rsr-monitor,os-caching}` |

---

## 앱 지원 경로 (Application Support)

| 범위 | 경로 | 용도 |
|------|------|------|
| **시스템 (PKG 설치)** | `/Library/Application Support/26x86/` | `26x86.app`, 자동 패치 바이너리, 업데이트 페이로드 |
| **사용자** | `~/Library/Application Support/26x86/` | `config.json`, 캐시, 보조 데이터 |
| Applications 바로가기 | `/Applications/26x86.app` | PKG 설치 시 생성 |
| Privileged Helper | `/Library/PrivilegedHelperTools/com.sharhene777.26x86.privileged-helper` | 권한 상승 작업 |

**OCLP 레거시 경로** `/Library/Application Support/Dortania/`는 26x86 런타임에서 **사용하지 않습니다.**

---

## Launch Services (launchd)

필요 시 설치되는 레이블은 모두 `com.sharhene777.26x86.*` 접두사를 사용합니다.

| 레이블 | 유형 | 역할 |
|--------|------|------|
| `com.sharhene777.26x86.auto-patch` | LaunchAgent | 부팅 시 자동 루트 패치 확인·적용 |
| `com.sharhene777.26x86.macos-update` | LaunchDaemon | macOS 업데이트 후 패치 재적용 |
| `com.sharhene777.26x86.os-caching` | LaunchDaemon | OS 캐싱(KDK 등) |
| `com.sharhene777.26x86.rsr-monitor` | LaunchDaemon | RSR(보안 응답) 모니터링 |

설치된 plist 위치 예:

- LaunchAgent: `~/Library/LaunchAgents/com.sharhene777.26x86.auto-patch.plist` 또는 `/Library/LaunchAgents/…`
- LaunchDaemon: `/Library/LaunchDaemons/com.sharhene777.26x86.{macos-update,os-caching,rsr-monitor}.plist`

페이로드 템플릿: `resources/launchagents/com.sharhene777.26x86.*.plist`

**OCLP 레이블** `com.dortania.opencore-legacy-patcher.*`와 **동시에 자동 패치를 실행할 수 없습니다.**

---

## 환경 변수

| 변수 | 효과 |
|------|------|
| `X86_ADVANCED=1` | 레거시 wx MainFrame 메뉴 노출 (점진 제거 예정) |
| `X86_VERBOSE=1` | 디버그 로깅 (`verbose_logging`과 병행 가능) |

---

## OCLP·레거시 plist와의 대조

| OCLP / 구 26x86 (레거시) | 클린룸 26x86 |
|--------------------------|--------------|
| `/Users/Shared/.com.dortania.opencore-legacy-patcher.plist` | **쓰기 금지** — 1회 읽기 후 JSON으로만 운영 |
| `~/Library/Preferences/com.dortania.opencore-legacy-patcher.plist` | 마이그레이션 소스 (읽기만) |
| `~/Library/Preferences/com.niseullent.26x86.plist` (구) | → `config.json`으로 이전 |
| `com.dortania.opencore-legacy-patcher.*` | `com.sharhene777.26x86.*` |
| 분산 plist 키 | `config.json` + `SettingsStore` |

전환 절차: [Migration.md](./Migration.md)

---

## 내부 패키지 이름

| 계층 | 이름 | 비고 |
|------|------|------|
| 신규 코드 | `x86/` | paths, settings, CLI, patch, wizard |
| 호환 shim | `opencore_legacy_patcher/` | `from x86 import …` 위임, 점진 이전 |

사용자에게 보이는 이름·경로·번들 ID는 **26x86** / `com.sharhene777.26x86` 입니다.
