# 26x86 OCLP 의존성 감사 (Dependency Audit)

> **감사 일시:** 2026-09-04  
> **범위:** `*.py`, `*.plist`, `*.command`, `*.spec` (CREDITS / NOTICE / THIRD_PARTY 제외)  
> **검색 패턴:** `dortania|opencore-legacy-patcher|OpenCore-Patcher|Users/Shared|YBronst|albert-mueller`

## 요약

| 지표 | 값 |
|------|-----|
| **총 매치 수 (Before)** | **115** |
| **총 매치 수 (After)** | **27** |
| **영향 파일 수 (Before)** | **52** |
| **이미 26x86-native로 전환된 항목** | bundle ID, preferences domain, NiSeullent fork URLs (constants.py), `global_settings.py` 26x86 plist, 신규 Launch Services plist 3종 |
| **런타임 차단 필요** | **~45** (설정/launchd/업데이트/경로 하드코딩) |
| **빌드/패키징 전용** | **~35** (ci_tooling, spec, Build-Project.command) |
| **페이로드 정적 자산** | **~15** (kext plists, config.plist, Tools stub app) |
| **주석/참조 URL만** | **~20** (GitHub issue 링크, docstring) |

---

## 도메인별 분류

### 1. 설정 / Shared State (CRITICAL — 런타임 금지)

| 파일 | 매치 | 상태 | 조치 |
|------|------|------|------|
| `opencore_legacy_patcher/constants.py` | `legacy_oclp_shared_settings`, `legacy_oclp_preferences_domain` | 상수만 존재 (마이그레이션용) | 마이그레이션 완료 후 read-only 참조로 축소 |
| `opencore_legacy_patcher/support/global_settings.py` | OCLP plist import, `sudo rm` 안내 | **읽기 전용 1회 마이그레이션** | Worker A: settings_store 분리 |
| `opencore_legacy_patcher/wx_gui/gui_build.py:384` | OCLP 경로 error log | 런타임 | 26x86 경로로 교체 |
| `ci_tooling/build_modules/package_scripts.py` | `/Users/Shared/.com.dortania...`, domain | 패키지 postinstall | 26x86 domain/plist |
| `opencore_legacy_patcher/support/logging_handler.py` | `/Users/Shared`, `OpenCore-Patcher_*` log | 런타임 | `~/Library/Logs/26x86/` |

### 2. Bundle ID / Launchd (CRITICAL)

| 파일 | 매치 | 상태 |
|------|------|------|
| `payloads/Launch Services/com.dortania.*.plist` (×4) | bundle ID, label | **구버전 — 삭제 대상** |
| `payloads/Launch Services/com.sharhene777.26x86.*.plist` (×3) | 26x86 ID | **신규 — rsr-monitor 누락** |
| `opencore_legacy_patcher/sys_patch/auto_patcher/install.py` | 하드코oded `/Library/LaunchAgents/com.dortania...` | **미전환** |
| `opencore_legacy_patcher/support/subprocess_wrapper.py` | `OCLP_PRIVILEGED_HELPER` dortania path | **미전환** |
| `OpenCore-Patcher-GUI.spec` | `com.sharhene777.26x86` | **전환 완료** |
| `ci_tooling/build_modules/package.py` | dortania bundle IDs, helper paths | **미전환** |
| `Build-Project.command` | dortania privileged helper | **미전환** |
| `payloads/Tools/OpenCore-Patcher.app/Contents/Info.plist` | dortania bundle ID | **→ 26x86.app** |

### 3. 업데이트 / Analytics / API 엔드포인트 (CRITICAL)

| 파일 | URL / 참조 | 조치 |
|------|-----------|------|
| `sys_patch/auto_patcher/start.py` | `albert-mueller/OpenCore-Legacy-Patcher-T2` API | → `NiSeullent/26x86` |
| `wx_gui/gui_main_menu.py:342` | albert-mueller releases API | → NiSeullent/26x86 |
| `wx_gui/gui_update.py` | OpenCore-Patcher.pkg, Dortania App Support path | → 26x86.pkg, `/Library/Application Support/26x86/` |
| `wx_gui/gui_macos_configeration.py` | dortania/OCLP branches, nightly.link | 제거 또는 26x86 전용 |
| `wx_gui/gui_help.py`, `gui_build.py`, `gui_install_oc.py` | albert-mueller issues/discussions | → NiSeullent/26x86 |
| `support/metallib_handler.py` | `albert-mueller.github.io/MetallibSupportPkg` | → NiSeullent/26x86-MetallibSupportPkg |
| `support/kdk_handler.py` | `dortania.github.io/KdkSupportPkg` | 유지 가능 (upstream KDK) 또는 fork |
| `support/validation.py` | `YBronst/PatcherSupportPkg` | → NiSeullent/26x86-PatcherSupportPkg |
| `ci_tooling/build_modules/disk_images.py` | YBronst download URL | → NiSeullent fork |

### 4. 앱 바이너리 / 경로 (HIGH)

| 파일 | 참조 | 조치 |
|------|------|------|
| `constants.py:796` | `Tools/OpenCore-Patcher.app/.../OpenCore-Patcher` | → `Tools/26x86.app/.../26x86` |
| `application_entry.py:224` | `OpenCore-Patcher-GUI.command` | → `26x86-GUI.command` (또는 alias) |
| `support/cli.py:78` | prog=`OpenCore-Patcher-GUI.command` | → `26x86` |
| `support/arguments.py:246` | `OpenCore-Patcher --cache_os` | → `26x86 --cache_os` |
| `ci_tooling/build_modules/application.py` | OpenCore-Patcher.app 생성 | → 26x86.app |
| `wx_gui/gui_update.py:302` | `/Library/Application Support/Dortania/` | → `/Library/Application Support/26x86/` |

### 5. 개발자 / 내부 DMG (MEDIUM)

| 파일 | 참조 | 조치 |
|------|------|------|
| `support/defaults.py`, `wx_gui/gui_settings.py` | `~/.dortania_developer` | → `~/.26x86_developer` |
| `sys_patch/utilities/dmg_mount.py` | `_mount_dortania_internal_resources_dmg`, `~/.dortania_developer_key` | 26x86 namespace 리네임 |
| `sys_patch/patchsets/detect.py`, `hardware/base.py` | `_dortania_internal_check()` | → `_26x86_internal_check()` |
| `sys_patch/patchsets/hardware/graphics/*.py` | `_dortania_internal_check()` 호출 | 메서드명만 변경 |

### 6. 페이로드 정적 plist (LOW — kext 번들 ID)

| 파일 | bundle ID |
|------|-----------|
| `payloads/Kexts/Plists/AppleUSBMaps/Info*.plist` | `com.dortania.USB-Map` |
| `payloads/Kexts/Plists/AppleMuxControl/Info.plist` | `com.dortania.AMC-Override` |
| `payloads/Kexts/Plists/AppleGraphicsPowerManagement/Info.plist` | `com.dortania.AGPM-Override` |
| `payloads/Kexts/Plists/AppleGraphicsDevicePolicy/Info.plist` | `com.dortania.AGDP-Override` |
| `payloads/Config/config.plist` | "Chainload OpenCore-Patcher installation" 문자열 |

> Kext bundle ID는 EFI/OpenCore 로드에 영향 — 변경 시 기존 설치와 호환성 검토 필요. 1차 마이그레이션에서는 **유지**, 2차에서 `com.niseullent.*` 전환 검토.

### 7. 주석 / 문서 참조만 (ALLOWED)

- `sys_patch/sys_patch.py`, `sys_patch_helpers.py`, `macos_installer_handler.py`, `gmux.py`, `metal_3802.py`, `datasets/example_data.py` — GitHub issue/commit URL
- `constants.py:107` — Dortania kext 버전 주석
- `wx_gui/gui_main_menu.py:188` — OpenCore Install Guide (Dortania) — 외부 가이드 링크 OK

---

## 파일별 전체 목록 (52 files)

```
ci_tooling/build_modules/package.py (7)
ci_tooling/build_modules/package_scripts.py (6)
ci_tooling/build_modules/application.py (5)
ci_tooling/build_modules/disk_images.py (1)
Build-Project.command (3)
OpenCore-Patcher-GUI.spec (2)
payloads/Launch Services/com.dortania.* (4)
payloads/Tools/OpenCore-Patcher.app/Contents/Info.plist (6)
payloads/Kexts/Plists/* (5)
payloads/Config/config.plist (1)
opencore_legacy_patcher/constants.py (4)
opencore_legacy_patcher/support/global_settings.py (3)
opencore_legacy_patcher/support/subprocess_wrapper.py (1)
opencore_legacy_patcher/support/logging_handler.py (4)
opencore_legacy_patcher/support/validation.py (1)
opencore_legacy_patcher/support/metallib_handler.py (1)
opencore_legacy_patcher/support/kdk_handler.py (1)
opencore_legacy_patcher/support/defaults.py (1)
opencore_legacy_patcher/support/utilities.py (1)
opencore_legacy_patcher/support/arguments.py (1)
opencore_legacy_patcher/support/cli.py (1)
opencore_legacy_patcher/application_entry.py (1)
opencore_legacy_patcher/wx_gui/* (15 across 8 files)
opencore_legacy_patcher/sys_patch/* (20 across 12 files)
opencore_legacy_patcher/datasets/example_data.py (1)
```

---

## 검증 명령 (마이그레이션 후)

```bash
cd /Users/nyase/Desktop/26x86/26x86

# Before count (baseline): 115 → After: 27 (2026-09-04)
grep -rn "dortania\|opencore-legacy-patcher\|OpenCore-Patcher\|Users/Shared\|YBronst\|albert-mueller" \
  --include="*.py" --include="*.plist" --include="*.command" --include="*.spec" . \
  | grep -v CREDITS | grep -v NOTICE | grep -v THIRD_PARTY | wc -l

# Runtime-only check (must be 0 except migration module + comments):
grep -rn "legacy_oclp\|/Users/Shared/.com.dortania\|com.dortania.opencore" \
  --include="*.py" opencore_legacy_patcher/ \
  | grep -v settings_store | grep -v global_settings | grep -v "#"

# Functional smoke test
python3 -m opencore_legacy_patcher.support.cli --help
python3 -m opencore_legacy_patcher.support.cli --detect --json
```

---

## 우선순위 매트릭스

| P | 영역 | Worker |
|---|------|--------|
| P0 | settings API, launchd paths, privileged helper | A + B |
| P0 | update URLs, auto-patcher API | C |
| P1 | build/package rename (26x86.app) | B + C |
| P1 | logging, analytics paths | A |
| P2 | docs/wiki, orphan archive | D |
| P3 | kext bundle ID rename | deferred |
