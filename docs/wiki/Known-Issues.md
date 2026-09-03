# 알려진 이슈 (Known Issues)

## 실험적 T2 포크

Dortania 공식 OCLP가 아직 T2 Mac을 지원하지 않는 가운데, **macOS 15 Sequoia·macOS 26 Tahoe T2 지원**을 실험적으로 추가합니다. 알파 단계이므로 백업 후 **여분의 T2 Mac**에서만 시험하세요.

T2·비-T2 x86 Mac 모두에서 macOS 26 Tahoe 호환성 개선을 목표로 합니다.

---

## T2 진행 상황 (요약)

| 항목 | 상태 |
|------|------|
| 인스톨러 부팅 | ✅ |
| MacBookAir8,1 / 8,2 인스톨러 부팅 | ❌ |
| T2 내부 디스크 마운트 | ❌ — [OCLP-T2 이슈 #69](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/69) |
| 데스크톱 도달 | ❌ |
| 설치 후 2단계 이슈 | ❌ |
| GPU 가속 / Wi-Fi | ⚠️ 일부 T2는 기본 가속 가능 |

---

## 그래픽·GPU

- Metal 8302 (2012–2014 Mac): Tahoe 그래픽 패치 **미완** → 커널 패닉 또는 가속 없이 부팅만 허용
- Non-Metal (2011 Mac): 동일
- 상세: [GPU-Limitations.md](./GPU-Limitations.md)

---

## Core 2 Duo / Penryn 이전

AAAMouSSE·telemetrap 관련으로 **macOS 26 부팅 불가** 가능. 상세: [Warnings.md](./Warnings.md)

---

## Safari 26 / MacPro5,1 Pre-AVX

Safari 26.6.1 WebContent SIGILL은 [Safari-PreAVX-Fix.md](./Safari-PreAVX-Fix.md)를 참고하세요. EFI 빌드 시 MacPro5,1에만 자동 적용됩니다.

---

## macOS 업데이트 후

- KDK + MetallibSupportPkg + **루트 패치 재적용**이 필요할 수 있습니다.
- macOS 업데이트마다 패치가 **소거**될 수 있습니다.

---

## 기타

- Hackintosh EFI 생성: **미지원**
- macOS 27 Golden Gate 이후 x86: **지원 대상 아님** (예상)
