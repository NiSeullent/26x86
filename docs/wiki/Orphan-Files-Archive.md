# 고아 파일 보관 목록

레포 정리 시 **목적이 불명확하거나 일회성**으로 판단된 파일을 `archive/`로 이동했습니다. 애플리케이션·payloads·CI 핵심 경로는 유지했습니다.

---

## `archive/`로 이동된 파일

| 파일 | 사유 |
|------|------|
| `EFI_COMPARISON_16048_vs_16903.txt` | OpenCore 빌드 번호 비교 일회성 로그 |
| `NEW_EFI_REPORT.txt` | EFI 빌드 테스트 리포트 |
| `PREVIOUS_BUILD_STATE.txt` | 이전 빌드 상태 스냅샷 |
| `NEW_EFI_4.0.0.16903/` | 테스트용 EFI 트리 (약 10MB) |
| `replace_gui.py` | GUI 일회성 치환 스크립트 (작업 완료) |
| `replace_gui_sys_patch_display.py` | 동일 |
| `update_verify.py`, `update_verify2.py`, `update_verify3.py` | `verify_efi.py` 수정용 일회성 스크립트 |
| `verify_efi.py` | 루트 EFI 검증 스크립트; `Tools/verify_efi.command`는 별도 bash 구현 사용 |
| `sim_builds.py` | 로컬 MBP14,3 빌드 프로필 테스트 |
| `update_config.py` | config.plist 일회성 수정 |
| `Install-OCLP-T1-MBP143-to-USB.command` | 레거시 OCLP 이름·이탈리아어 USB 설치 스크립트 |
| `Install-OCLP-T1-MBP143-to-USB.sh` | 동일 |

---

## 유지된 관련 파일

| 파일 | 사유 |
|------|------|
| `Tools/verify_efi.command` | READ-ONLY EFI 감사 도구 ([Tools/README.md](../../Tools/README.md)) |
| `install-OpenCore-T1.command` | `26x86.pkg` 설치 헬퍼 |
| `payloads/Kexts/*.dSYM` | kext 디버그 심볼; 릴리스 빌드에 영향 없음, upstream 구조 유지 |

---

## 복원 방법

필요 시 `archive/`에서 루트로 파일을 되돌릴 수 있습니다. Git 히스토리에도 이전 커밋이 보존됩니다.
