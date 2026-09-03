# 제거·정리된 파일 목록

2026-09-04 찌꺼기 정리로 **저장소에서 삭제**한 항목입니다. 필요 시 Git 히스토리에서 복구할 수 있습니다.

---

## Git 추적 (`archive/`)

`archive/`는 **로컬 전용**입니다 (`.gitignore` 대상).

- `git clone`만으로는 `archive/` 내용이 **없습니다.**
- 과거 EFI·icns 등은 Git **히스토리**(`d03718f` 이전 커밋)에만 남아 있습니다.
- 로컬에서 `archive/legacy-oclp/` 등을 유지하려면 **커밋하지 마세요.**

---

## 삭제된 문서 (중복·내부용)

| 파일 | 사유 |
|------|------|
| `docs/ARCHITECTURE-26x86.md` | 내부 설계서, 사용자 문서 아님 |
| `docs/DEPENDENCY-AUDIT.md` | 개발자 감사 로그 |
| `docs/CLEANROOM-ARCHITECTURE.md` | 내부 설계 초안, 공개 문서 아님 |
| `docs/wiki/Migration.md` | [Migration-from-OCLP.md](./Migration-from-OCLP.md)와 중복 |

---

## 삭제된 빌드·진입점

| 파일 | 사유 |
|------|------|
| `OpenCore-Patcher-GUI.spec` | `26x86-GUI.spec`과 중복 |
| `OpenCore-Patcher-GUI.command` | `26x86.command`로 통일 (호환 래퍼는 별도 유지 가능) |

---

## 삭제된 CI·아카이브

| 파일 | 사유 |
|------|------|
| `ci_tooling/privileged_helper_tool/com.dortania.opencore-legacy-patcher.privileged-helper` | 구 privileged helper 바이너리 |
| `archive/` (Git 추적) | EFI 비교 로그, `NEW_EFI_*`, 일회성 스크립트 등 — **로컬만 유지** |

---

## 이전에 삭제된 항목

- `payloads/Kexts/**/*.dSYM` — kext 디버그 심볼
- `rebrand_to_26x86.py` — 일회성 리브랜드 스크립트

---

## 유지

| 항목 | 사유 |
|------|------|
| `payloads/kexts`, OpenCore zip | 런타임 필수 |
| `26x86-GUI.spec` / `26x86-GUI.command` | PyInstaller 빌드 |
| `26x86.command`, `26x86.py` | 사용자 진입점 |
| NOTICE, LICENSE, CREDITS, 위키 핵심 | 법적·사용자 문서 |

개발자 안내: [Developer.md](./Developer.md)
