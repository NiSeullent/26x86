# OCLP → 26x86 마이그레이션

Dortania **OpenCore Legacy Patcher(OCLP)**, **OCLP-T2**, **OCLP-Mod**, **OCLP-Plus** 등에서 **26x86**으로 옮길 때의 정책과 절차입니다.

> 설정 경로: [Configuration.md](./Configuration.md)  
> 아키텍처: [ARCHITECTURE-26x86.md](../ARCHITECTURE-26x86.md)

---

## English Summary

On first run, 26x86 **reads** legacy OCLP (and optionally old 26x86 plist) settings **once**, writes them to `~/Library/Application Support/26x86/config.json`, and never writes back to OCLP paths. Use `python -m x86 wizard` or subcommands (`detect`, `build`, `patch`, `status`). Do not run OCLP and 26x86 auto-patch launchd jobs together.

---

## 무엇이 바뀌는가

| 영역 | OCLP (구) | 26x86 (신) |
|------|-----------|-------------------|
| 사용자 설정 | `/Users/Shared/`·plist | `~/Library/Application Support/26x86/config.json` |
| 진입점 | `OpenCore-Patcher-GUI.command` | `python -m x86 wizard` / `26x86.command` |
| CLI | 없음(또는 간접) | `detect` · `build` · `patch` · `status` · `wizard` |
| LaunchAgents | `com.dortania.*` | `com.niseullent.26x86.*` |
| 번들 ID | `com.dortania.opencore-legacy-patcher` | `com.niseullent.26x86` |

---

## 권장 전환 순서

1. **백업** — Time Machine 또는 전체 디스크 이미지 ([Warnings.md](./Warnings.md))
2. OCLP에서 **루트 패치 되돌리기** (Revert Root Patches)
3. 26x86 저장소 또는 PKG 설치
4. **마법사 실행** (권장):

   ```bash
   python -m x86 wizard
   ```

5. 마법사 또는 CLI로 하드웨어 확인:

   ```bash
   python -m x86 detect --json
   ```

6. EFI 빌드·루트 패치는 마법사 안내 또는:

   ```bash
   python -m x86 build
   python -m x86 patch
   python -m x86 status    # 결과 확인
   ```

7. (선택) OCLP 앱·레거시 plist 정리 — 아래 「선택 정리」 참고

---

## 자동 마이그레이션 (1회)

26x86 **첫 실행** 시, 읽을 수 있는 레거시 설정이 있으면 **한 번만** `config.json`으로 가져옵니다.

**읽기 소스 (우선순위):**

1. `~/Library/Preferences/com.dortania.opencore-legacy-patcher.plist` (OCLP 사용자 Preferences)
2. `/Users/Shared/.com.dortania.opencore-legacy-patcher.plist` (OCLP 공유 plist, **읽기 가능한 경우만**)
3. `~/Library/Preferences/com.niseullent.26x86.plist` (구 26x86 plist, 있을 경우)

| 조건 | 26x86 동작 |
|------|-----------|
| `config.json` 없음 + 레거시 plist 읽기 가능 | 키 매핑 후 `migrated_from_oclp: true` 기록 |
| OCLP plist가 **root 소유** 등으로 읽기 불가 | 마이그레이션 **건너뜀**, 기본 JSON 사용 (크래시 없음) |
| 이미 `migrated_from_oclp: true` | 재실행하지 않음 (idempotent) |

가져온 뒤 **모든 읽기·쓰기는 `config.json`만** 사용합니다. OCLP·구 plist에는 **쓰지 않습니다.**

```bash
# 마이그레이션 결과 확인
python -m x86 status
cat ~/Library/Application\ Support/26x86/config.json
```

---

## 신규 CLI 요약

```bash
python -m x86 --help
python -m x86 detect [--json]      # device_probe 래핑
python -m x86 build [--model ...]  # EFI 빌드
python -m x86 patch [--auto]       # 루트 패치
python -m x86 status               # 설정·패치·EFI 상태
python -m x86 wizard               # 기본 GUI
```

| 환경 변수 | 효과 |
|-----------|------|
| `X86_ADVANCED=1` | 레거시 고급 wx 메뉴 (점진 폐기) |
| `X86_VERBOSE=1` | 상세 로깅 |

구 진입점 `OpenCore-Patcher-GUI.command`는 deprecated — `26x86.command` 또는 `python -m x86 wizard`를 사용하세요.

---

## OCLP와 26x86 동시 실행 — **지원 안 함**

| 구성 | 결과 |
|------|------|
| OCLP launchd + 26x86 launchd 동시 활성 | **지원 안 함** — 패치·업데이트 경쟁 |
| 26x86 PKG 설치 | `com.dortania.opencore-legacy-patcher.*` launchd 제거 포함 |
| OCLP만 제거하고 26x86 사용 | `com.niseullent.26x86.*`만 유지 |

---

## 선택 정리 (OCLP 완전 제거 시)

다음은 **필수가 아닙니다.** 26x86은 자체 `config.json`만 사용합니다.

```bash
# 선택 — OCLP 공유 plist (26x86 config.json과 무관)
sudo rm '/Users/Shared/.com.dortania.opencore-legacy-patcher.plist'

# 선택 — OCLP 사용자 Preferences
rm ~/Library/Preferences/com.dortania.opencore-legacy-patcher.plist

# 선택 — 구 26x86 plist (이미 config.json으로 이전된 경우)
rm ~/Library/Preferences/com.niseullent.26x86.plist
```

---

## 다른 포크·설치본

- **OCLP-Mod**, **OCLP-Plus**, **Dortania OCLP**: 루트 패치 되돌린 뒤 위 순서로 전환
- 26x86으로 macOS **재설치**하면서 사용자 데이터 유지 가능
- Patched Sur, bigmac 등 **타사 Big Sur 패치** 설치본은 APFS·SIP 문제로 공식 지원 경로가 아님 → [Installation-Notes.md](./Installation-Notes.md)

---

## 시나리오별 요약

| 시나리오 | 26x86 동작 |
|----------|-----------|
| OCLP 미설치 | `config.json` 기본값 |
| OCLP + readable plist | 1회 JSON 마이그레이션 |
| OCLP + root-owned shared plist | skip, 기본값; plist 삭제는 선택 |
| OCLP + 26x86 동시 auto-patch | **하지 말 것** |
| 구 `com.niseullent.26x86.plist`만 있음 | plist → `config.json` 1회 이전 |

---

## 관련 문서

- [Configuration.md](./Configuration.md) — `config.json`·launchd·번들 ID
- [Installation-Notes.md](./Installation-Notes.md) — 클린 설치·OS 버전
- [T2-Mac-Notes.md](./T2-Mac-Notes.md) — T2 전용 주의
- [Migration-from-OCLP.md](./Migration-from-OCLP.md) — 구 문서 (본 페이지로 통합됨)
