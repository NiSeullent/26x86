# 고아 파일 보관 목록

클린룸 아키텍처 정리(`docs/CLEANROOM-ARCHITECTURE.md`)에 따라 **일회성 OCLP 개발 산출물·T1 범위 밖 설치 스크립트·디버그 심볼**을 제거하거나 `archive/legacy-oclp/`로 이동했습니다. 애플리케이션·`payloads/` 핵심·CI 경로는 유지했습니다.

---

## `archive/legacy-oclp/`로 이동 (2026-09-04)

기존 `archive/` 루트에 있던 항목을 `archive/legacy-oclp/`로 통합했습니다.

| 파일 / 디렉터리 | 이전 위치 | 사유 |
|-----------------|-----------|------|
| `replace_gui.py` | `archive/` | GUI 일회성 치환 스크립트 (작업 완료) |
| `replace_gui_sys_patch_display.py` | `archive/` | 동일 |
| `update_verify.py`, `update_verify2.py`, `update_verify3.py` | `archive/` | `verify_efi.py` 수정용 일회성 스크립트 |
| `verify_efi.py` | `archive/` | 루트 EFI 검증 Python 스크립트; 운영 도구는 `Tools/verify_efi.command` |
| `sim_builds.py` | `archive/` | 로컬 MBP14,3 빌드 프로필 테스트 |
| `update_config.py` | `archive/` | `config.plist` 일회성 수정 |
| `EFI_COMPARISON_16048_vs_16903.txt` | `archive/` | OpenCore 빌드 번호 비교 일회성 로그 |
| `NEW_EFI_REPORT.txt` | `archive/` | EFI 빌드 테스트 리포트 |
| `PREVIOUS_BUILD_STATE.txt` | `archive/` | 이전 빌드 상태 스냅샷 |
| `NEW_EFI_4.0.0.16903/` | `archive/` | 테스트용 EFI 트리 (약 10MB) |
| `Install-OCLP-T1-MBP143-to-USB.command` | `archive/` | 레거시 OCLP T1 USB 설치 (제품 범위 밖) |
| `Install-OCLP-T1-MBP143-to-USB.sh` | `archive/` | 동일 |
| `install-OpenCore-T1.command` | **루트** | T1 설치 헬퍼; 26x86 제품 범위 밖 |

**루트에 없었던 항목 (이미 제거됨):** `rebrand_to_26x86.py`

---

## 삭제 (2026-09-04)

### kext 디버그 심볼 (`payloads/Kexts/**/*.dSYM`)

패처 배포에 불필요한 디버그 심볼 폴더를 삭제했습니다.

| 삭제된 경로 |
|-------------|
| `payloads/Kexts/AirportBrcmFixup.kext.dSYM/` |
| `payloads/Kexts/CPUFriend.kext.dSYM/` |
| `payloads/Kexts/Lilu.kext.dSYM/` |
| `payloads/Kexts/RestrictEvents.kext.dSYM/` |
| `payloads/Kexts/WhateverGreen.kext.dSYM/` |

### `com.dortania.*` LaunchAgents

`payloads/Launch Services/`에 `com.dortania.*` launchd plist **잔존 없음** (이전 정리 완료). kext plist의 `com.dortania.*` 번들 ID(예: USB-Map)는 kext 메타데이터로 유지.

---

## 신규 LaunchAgent 템플릿

클린룸 번들 ID `com.niseullent.26x86`용 템플릿을 추가했습니다 (`payloads/Launch Services/com.niseullent.26x86.*` 기반):

| 파일 |
|------|
| `resources/launchagents/com.niseullent.26x86.auto-patch.plist` |
| `resources/launchagents/com.niseullent.26x86.macos-update.plist` |
| `resources/launchagents/com.niseullent.26x86.rsr-monitor.plist` |
| `resources/launchagents/com.niseullent.26x86.os-caching.plist` |

설치 시 대상: `~/Library/LaunchAgents/com.niseullent.26x86.*.plist`

---

## 유지된 관련 파일

| 파일 | 사유 |
|------|------|
| `Tools/verify_efi.command` | READ-ONLY EFI 감사 도구 ([Tools/README.md](../../Tools/README.md)) |
| `payloads/Launch Services/com.niseullent.26x86.*.plist` | 기존 NiSeullent 페이로드; 점진 이전 예정 |
| `archive/README.md` | 아카이브 디렉터리 안내 |

---

## 복원 방법

필요 시 `archive/legacy-oclp/`에서 참고용으로 복사할 수 있습니다. Git 히스토리에도 이전 커밋이 보존됩니다. 운영 경로로 되돌리는 것은 권장하지 않습니다.
