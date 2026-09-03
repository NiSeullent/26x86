# 제거·정리된 파일 목록

2026-09-04 찌꺼기 정리로 **저장소에서 삭제**한 항목입니다. 필요 시 Git 히스토리에서 복구할 수 있습니다.

---

## 삭제된 문서 (중복·내부용)

| 파일 | 사유 |
|------|------|
| `docs/ARCHITECTURE-26x86.md` | 내부 설계서 → [Developer.md](./Developer.md)로 통합 |
| `docs/DEPENDENCY-AUDIT.md` | 개발자 감사 로그, 사용자 불필요 |
| `docs/CLEANROOM-ARCHITECTURE.md` | Developer.md로 통합 |
| `docs/wiki/Migration-from-OCLP.md` | [Migration.md](./Migration.md)와 중복 |

---

## 삭제된 빌드·진입점

| 파일 | 사유 |
|------|------|
| `OpenCore-Patcher-GUI.spec` | `26x86-GUI.spec`과 중복 |
| `OpenCore-Patcher-GUI.command` | `26x86.command`로 통일 |

---

## 삭제된 CI·아카이브

| 파일 | 사유 |
|------|------|
| `ci_tooling/privileged_helper_tool/com.dortania.opencore-legacy-patcher.privileged-helper` | 구 privileged helper 바이너리 |
| `archive/legacy-oclp/` 전체 | EFI 비교 로그, `NEW_EFI_*`, 일회성 스크립트 등 |

`archive/`는 `.gitignore` 대상(로컬 전용). `archive/README.md`만 안내용.

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
