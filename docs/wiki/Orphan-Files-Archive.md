# 제거·정리된 파일 목록

2026-09-04 찌꺼기 정리로 저장소에서 **삭제**한 항목입니다. Git 히스토리에서 복구 가능합니다.

## 삭제된 문서

| 파일 | 사유 |
|------|------|
| `docs/ARCHITECTURE-26x86.md` | 내부 설계서 → [Developer.md](./Developer.md) |
| `docs/DEPENDENCY-AUDIT.md` | 개발자 감사 로그 |
| `docs/CLEANROOM-ARCHITECTURE.md` | Developer.md로 통합 |
| `docs/wiki/Migration-from-OCLP.md` | [Migration.md](./Migration.md)와 중복 |

## 삭제된 빌드·진입점

| 파일 | 사유 |
|------|------|
| `OpenCore-Patcher-GUI.spec` | `26x86-GUI.spec`과 중복 |
| `OpenCore-Patcher-GUI.command` | `26x86.command`로 통일 |

## 삭제된 CI·로컬 아카이브

| 파일 | 사유 |
|------|------|
| `ci_tooling/.../com.dortania...privileged-helper` | 구 helper 바이너리 |
| `archive/legacy-oclp/` | EFI 비교 로그, `NEW_EFI_*`, 일회성 스크립트 |

`archive/`는 `.gitignore` (로컬 전용).

## 이전에 삭제

- `payloads/Kexts/**/*.dSYM`
- `rebrand_to_26x86.py`

개발자: [Developer.md](./Developer.md)
