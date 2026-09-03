# T2 Mac 주의사항

Apple **T2** 칩이 탑재된 Intel Mac에서 26x86을 사용할 때의 전용 노트입니다.

---

## SIP(시스템 무결성 보호)

- T2 Mac에서 OpenCorePkg 부팅 시 SIP가 **0xFFF(사실상 전체 비활성화)** 로 설정될 수 있습니다.
- 열·스로틀링 등 이슈로 SIP 비활성화가 하드코딩되어 있을 수 있습니다.
- 26x86 설정 UI의 SIP 관련 옵션은 T2 Mac에서 **대부분 효과가 없을 수 있습니다**.
- **T1 Mac 또는 T2가 없는 x86 Mac**에는 이 제한이 적용되지 않을 수 있습니다.

SIP 비활성화 시 macOS 핵심 파일 보호가 약해져 **보안 수준이 크게 낮아집니다**.

---

## 다운로드 안내

GitHub **Code → Download ZIP**은 개발 중 커밋으로 인해 **불안정**할 수 있습니다.

**[Releases](https://github.com/NiSeullent/26x86/releases)**에서 검증된 빌드를 받는 것을 권장합니다.

---

## APFS·내부 디스크

- T2 **내부 디스크 마운트**는 아직 해결되지 않은 이슈가 있습니다. [OCLP-T2 #69](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/69)
- 클린 설치·공식 업그레이드 경로만 권장합니다. [Installation-Notes.md](./Installation-Notes.md)

---

## 실험적 상태

- macOS 15 Sequoia·macOS 26 Tahoe T2 지원은 **알파** 단계입니다.
- 백업 후 **여분의 T2 Mac**에서만 시험하세요.

---

## 진행 상황

[T2 진행 상황 표](./Known-Issues.md#t2-진행-상황-요약) 및 [Known-Issues.md](./Known-Issues.md)를 참고하세요.
