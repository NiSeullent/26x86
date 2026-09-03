# 26x86 클린룸 아키텍처

> **「이름만 바꾼 포크」가 아닌, 오늘 처음부터 26x86을 설계했다면 이렇게 만들었을 것**  
> Bundle ID: `com.sharhene777.26x86`  
> 핵심 역량 유지: x86 Mac에서 macOS 26용 OpenCore EFI 빌드 + 루트 패치 적용

> **문서 언어:** 사용자 대면 문서의 **기본 언어는 한국어**입니다. 영문 보조: [README.en.md](README.en.md)

### 관련 문서

| 문서 | 설명 |
|------|------|
| [wiki/Home.md](wiki/Home.md) | 위키 목차·빠른 링크 |
| [wiki/Configuration.md](wiki/Configuration.md) | `config.json`·번들 ID·launchd |
| [wiki/Migration.md](wiki/Migration.md) | OCLP → 26x86 전환 (JSON·CLI) |
| [wiki/Warnings.md](wiki/Warnings.md) | 주의사항 통합 |
| [ARCHITECTURE-26x86.md](ARCHITECTURE-26x86.md) | 선행 마이그레이션 설계 (점진 이전) |

---

## 1. 설계 철학

### 1.1 클린룸이란

OCLP(OpenCore Legacy Patcher)의 **런타임 관행·디렉터리 구조·진입점·설정 저장 방식**을 그대로 끌고 오지 않는다.  
패치 로직·EFI 빌더·하드웨어 탐지(device_probe) 등 **핵심 가치**는 `x86/` 패키지로 리팩터링하여 보존한다.

| 원칙 | 설명 |
|------|------|
| **단일 진실 원천** | 경로·버전·URL은 `x86/paths.py` + `x86/manifest.py` |
| **사용자 설정 분리** | JSON, 사용자 홈, 쓰기 가능 — `/Users/Shared/` 금지 |
| **마법사 우선 UI** | 일반 사용자는 wizard만; 고급 UI는 `X86_ADVANCED=1` |
| **명시적 CLI** | `python -m x86 {detect,build,patch,status,wizard}` |
| **얇은 호환 층** | `opencore_legacy_patcher/`는 import shim으로만 유지(점진 이전) |

### 1.2 금지 (완전 제거)

| 레거시 패턴 | 이유 |
|-------------|------|
| `/Users/Shared/` plist 설정 | root 소유·다중 사용자 오염·보안 취약점 |
| `com.dortania.*` LaunchDaemons/LaunchAgents 페이로드 | OCLP 자동 패치와 충돌 |
| 일회성 개발 스크립트: `replace_gui.py`, `rebrand_to_26x86.py`, `update_verify*.py`, `verify_efi.py`, `sim_builds.py` | 저장소 오염, CI/아카이브로 이전 |
| 고아 리포트: `EFI_COMPARISON_*`, `NEW_EFI_*`, `PREVIOUS_BUILD_STATE.txt` | 런타임 무관 |
| `Install-OCLP-T1*.command` (T1 비범위 시) | 제품 범위 밖 |
| `payloads/Kexts/**/*.dSYM` | 패처 배포에 디버그 심볼 불필요 |
| `OpenCore-Patcher-GUI.command` 진입명 | → `26x86.command` / `bin/26x86` |
| `utilities.py` god-module | 도메인별 모듈로 분해 |
| Dortania analytics/telemetry 엔드포인트 | 26x86 독립 또는 비활성 |
| `PatcherSupportPkg` 버전 등 plist 전역 상태 | `SettingsStore` JSON으로 대체 |

---

## 2. 패키지 레이아웃 (목표 구조)

```
26x86/
├── 26x86.py                    # 루트 진입점 → x86.cli
├── bin/26x86                   # 셸 shim
├── 26x86.command               # macOS 더블클릭 진입 (구 OpenCore-Patcher-GUI.command 대체)
├── x86/                        # ★ 신규 최상위 패키지
│   ├── __init__.py
│   ├── __main__.py             # python -m x86
│   ├── paths.py                # 모든 파일시스템 경로
│   ├── manifest.py             # 버전, NiSeullent fork URL
│   ├── settings.py             # SettingsStore (JSON)
│   ├── logging.py              # ~/Library/Logs/26x86/
│   ├── cli.py                  # argparse: detect|build|patch|status|wizard
│   ├── efi/                    # EFI 빌더 (opencore_legacy_patcher/efi_builder 이전)
│   ├── patch/                  # sys_patch + PayloadManager
│   │   ├── __init__.py
│   │   ├── payload_manager.py
│   │   └── ...
│   └── gui/
│       └── wizard/             # 기본 UI (유일한 일반 사용자 GUI)
├── opencore_legacy_patcher/    # 얇은 shim — from x86 import … 위임
├── payloads/                   # kexts, OpenCore zip, LaunchAgents 템플릿
├── resources/
│   └── launchagents/           # com.sharhene777.26x86.*.plist 템플릿
├── archive/legacy-oclp/        # 제거된 OCLP 스크립트·리포트
└── docs/
    ├── CLEANROOM-ARCHITECTURE.md  # (본 문서)
    └── wiki/
```

---

## 3. 재구현 매핑

| 필요 | OCLP (구) | 26x86 클린룸 (신) |
|------|-----------|-------------------|
| **사용자 설정** | `/Users/Shared/` plist | `~/Library/Application Support/26x86/config.json` |
| **CLI 진입** | `OpenCore-Patcher-GUI.command` | `26x86.py` + `bin/26x86`; 서브커맨드: `detect`, `build`, `patch`, `status`, `wizard` |
| **GUI** | wx MainFrame + 볼트온 wizard | **Wizard 전용** 기본; `26x86 wizard` / `--wizard`; 고급은 `X86_ADVANCED=1` |
| **설정 API** | 분산 plist 읽기 | `x86/settings.py` — `SettingsStore` 단일 클래스 |
| **경로·상수** | `constants.py` ~900줄 | `x86/paths.py` + `x86/manifest.py` |
| **LaunchAgents** | 시스템 전역 dortania plist | `~/Library/LaunchAgents/com.sharhene777.26x86.*.plist` (필요 시 설치) |
| **로깅** | 혼재 (`/Users/Shared/` 등) | `~/Library/Logs/26x86/` 구조화 로그 |
| **패치 페이로드** | PatcherSupportPkg DMG 마운트 마법 | `PayloadManager` 클래스로 mount/unmount 명시 |
| **패키지명** | `opencore_legacy_patcher/` | `x86/` + shim |

---

## 4. 네임스페이스

| 도메인 | 값 |
|--------|-----|
| **Bundle ID** | `com.sharhene777.26x86` |
| **Privileged Helper** | `com.sharhene777.26x86.privileged-helper` |
| **LaunchAgents** | `com.sharhene777.26x86.{auto-patch,macos-update,rsr-monitor,os-caching}` |
| **설정** | `~/Library/Application Support/26x86/config.json` |
| **로그** | `~/Library/Logs/26x86/` |
| **앱 지원** | `/Library/Application Support/26x86/` |
| **개발자 모드** | `~/.26x86_developer` |
| **OpenCorePkg** | NiSeullent/26x86-OpenCorePkg |
| **PatcherSupportPkg** | NiSeullent/26x86-PatcherSupportPkg |
| **MetallibSupportPkg** | NiSeullent/26x86-MetallibSupportPkg |
| **릴리스 API** | `api.github.com/repos/NiSeullent/26x86` |

---

## 5. CLI 설계

```bash
python -m x86 --help
python -m x86 detect [--json]      # device_probe 래핑
python -m x86 build [--model ...]  # EFI 빌드
python -m x86 patch [--auto]       # 루트 패치
python -m x86 status               # 설정·패치·EFI 상태 요약
python -m x86 wizard               # 기본 GUI (wx wizard)
```

환경 변수:

| 변수 | 효과 |
|------|------|
| `X86_ADVANCED=1` | 레거시 wx MainFrame 메뉴 노출 (점진 제거 예정) |
| `X86_VERBOSE=1` | 디버그 로깅 |

---

## 6. SettingsStore (JSON)

```json
{
  "version": 1,
  "auto_patch": false,
  "verbose_logging": false,
  "migrated_from_oclp": false,
  "last_detect": { "model": "iMac18,3", "timestamp": "2026-09-04T00:00:00Z" }
}
```

- 경로: `~/Library/Application Support/26x86/config.json`
- 권한: `0600`, 심볼릭 링크 거부
- OCLP 마이그레이션: 기존 plist 읽기 **1회** 후 JSON에 기록; OCLP plist에는 **쓰기 금지**

---

## 7. PayloadManager

PatcherSupportPkg DMG 마운트/언마운트를 캡슐화:

```python
class PayloadManager:
    def mount_support_pkg(self) -> Path: ...
    def unmount(self) -> None: ...
    def resolve_kext(self, name: str) -> Path: ...
```

- OCLP plist에서 `PatcherSupportPkg` 버전을 읽지 않음
- `manifest.py`의 고정 URL + 로컬 캐시 (`~/Library/Application Support/26x86/cache/`)

---

## 8. GUI: Wizard-First

```
일반 사용자 흐름:
  26x86.command / python -m x86 wizard
    → x86/gui/wizard/WizardFrame
    → detect → build EFI → patch 안내

고급 사용자 (X86_ADVANCED=1):
  → 기존 wx_gui 메뉴 (shim, 점진 폐기)
```

브랜딩: 창 제목·About·아이콘에 `26x86` / `com.sharhene777.26x86` 통일.

---

## 9. 보존 (핵심 가치)

| 모듈 | 처리 |
|------|------|
| `efi_builder/` | → `x86/efi/` 리팩터 (로직 유지) |
| `sys_patch/` | → `x86/patch/` + PayloadManager |
| `device_probe.py` | `x86`에서 import, CLI `detect`에 연결 |
| `payloads/` kexts·OpenCore zip | 그대로 사용, 경로만 `paths.py` 참조 |
| NiSeullent fork URL | `manifest.py` 단일 정의 |

---

## 10. 호환 층

### 10.1 `opencore_legacy_patcher/` shim

```python
# opencore_legacy_patcher/constants.py (예시)
from x86.manifest import *  # noqa
from x86.paths import Paths
```

기존 import 경로가 깨지지 않도록 위임. 신규 코드는 `x86`만 import.

### 10.2 `OpenCore-Patcher-GUI.command`

```bash
echo "[경고] OpenCore-Patcher-GUI.command는 deprecated. 26x86.command를 사용하세요." >&2
exec "$(dirname "$0")/26x86.py" wizard "$@"
```

---

## 11. 아카이브 정책

`archive/legacy-oclp/`로 이동:

- `replace_gui.py`, `rebrand_to_26x86.py`, `update_verify*.py`, `verify_efi.py`, `sim_builds.py`
- `EFI_COMPARISON_*`, `NEW_EFI_*`, `PREVIOUS_BUILD_STATE.txt`
- `payloads/Kexts/**/*.dSYM`
- 미사용 `com.dortania.*` plist

문서: `docs/wiki/Orphan-Files-Archive.md`

---

## 12. 검증 체크리스트

- [ ] `python -m x86 --help` 성공
- [ ] `python -m x86 detect --json` 성공
- [ ] `python -m x86 wizard` GUI 기동
- [ ] `.py`/`.plist` 런타임 코드에 `Users/Shared`, `com.dortania` 참조 **0건** (kext plist·CHANGELOG·아카이브 제외)
- [ ] 설정이 `config.json`에만 기록됨
- [ ] LaunchAgent label = `com.sharhene777.26x86.*`

---

## 13. 워커 분할 (구현 단계)

| 워커 | 담당 |
|------|------|
| **x86-core-foundation** | `x86/` 패키지 골격, CLI, settings, paths, manifest |
| **x86-gui-wizard** | `x86/gui/wizard/`, wizard-first, 브랜딩 |
| **x86-patch-payload** | `x86/patch/`, PayloadManager, dmg_mount |
| **x86-cleanup-archive** | legacy 삭제/아카이브, dSYM, launchagent 템플릿 |
| **x86-docs-wiki** | wiki, README 슬림화, Migration.md |

---

## 14. OCLP 공존

| 시나리오 | 26x86 동작 |
|----------|-----------|
| OCLP 미설치 | `config.json`만 사용 |
| OCLP plist 읽기 가능 | 1회 마이그레이션 → JSON |
| OCLP + 26x86 launchd 동시 | **비지원** — 26x86 설치 시 dortania 에이전트 제거 안내 |
| root 소유 shared plist | 마이그레이션 skip, 기본값 사용 |

---

## 15. 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 클린룸 아키텍처 초안 — `x86/` 패키지, JSON 설정, wizard-first CLI |

---

*이 문서는 [ARCHITECTURE-26x86.md](ARCHITECTURE-26x86.md)의 점진 마이그레이션 설계를 **구조적 재작성** 수준으로 확장한 것입니다.*
