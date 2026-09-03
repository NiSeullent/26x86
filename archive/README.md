# 보관 파일 (Archive)

레포 정리 시 **목적이 불명확하거나 일회성**으로 판단된 파일을 이 디렉터리에 보관합니다. **삭제하지 않았으며**, Git 히스토리에도 이전 커밋이 남아 있습니다.

애플리케이션·`payloads/`·`ci_tooling/` 등 **핵심 경로는 유지**했습니다.

위키 상세: [docs/wiki/Orphan-Files-Archive.md](../docs/wiki/Orphan-Files-Archive.md)

---

## `legacy-oclp/` 보관 목록

2026-09-04 정리로 루트에 있던 OCLP 일회성 산출물이 `legacy-oclp/`로 이동되었습니다.

| 파일 / 디렉터리 | 사유 |
|-----------------|------|
| `EFI_COMPARISON_16048_vs_16903.txt` | OpenCore 빌드 4.0.0.16048 vs 4.0.0.16903 EFI 설정 비교 일회성 로그 |
| `NEW_EFI_REPORT.txt` | EFI 빌드 테스트 리포트 |
| `PREVIOUS_BUILD_STATE.txt` | 이전 빌드 상태 스냅샷 |
| `NEW_EFI_4.0.0.16903/` | 테스트용 EFI 트리 (`EFI/OC/config.plist` 등) |
| `verify_efi.py` | 루트 EFI 검증 Python 스크립트; 운영 도구는 `Tools/verify_efi.command` |
| `update_verify.py`, `update_verify2.py`, `update_verify3.py` | `verify_efi.py` 수정용 일회성 스크립트 |
| `update_config.py` | `config.plist` 일회성 수정 스크립트 |
| `sim_builds.py` | 로컬 MBP14,3 빌드 프로필 테스트 |
| `replace_gui.py` | GUI 일회성 치환 스크립트 |
| `replace_gui_sys_patch_display.py` | sys_patch GUI 표시 일회성 치환 |
| `Install-OCLP-T1-MBP143-to-USB.command` / `.sh` | 레거시 OCLP 이름 USB 설치 스크립트 |
| `install-OpenCore-T1.command` | 구 T1 설치 헬퍼 (현재 루트의 `install-OpenCore-T1.command`는 별도 유지) |

---

## 유지된 관련 파일 (archive 밖)

| 파일 | 사유 |
|------|------|
| `Tools/verify_efi.command` | READ-ONLY EFI 감사 도구 |
| `install-OpenCore-T1.command` (루트) | `26x86.pkg` 설치 헬퍼 |
| `payloads/Kexts/*.dSYM` | kext 디버그 심볼; 릴리스 빌드에 영향 없음 |

---

## 복원 방법

필요 시 `legacy-oclp/`에서 프로젝트 루트로 파일을 되돌릴 수 있습니다. 권장하지는 않으며, 참고·비교 목적으로만 보관합니다.
