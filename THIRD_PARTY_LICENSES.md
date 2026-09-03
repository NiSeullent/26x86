# 서드파티 라이선스 (Third-Party Licenses)

26x86이 사용하는 주요 서드파티 구성 요소의 라이선스 목록입니다. 업스트림 전체 저작권 고지는 `LICENSE.txt`, `NOTICE.md`에 유지됩니다.

---

## 프로젝트 계보

### 26x86 (본 저장소)

- **라이선스:** BSD 3-Clause
- **저작권:** Copyright (c) 2026 NiSeullent and 26x86 contributors.
- **업스트림:** OpenCore Legacy Patcher T2 및 OpenCore Legacy Patcher에서 파생

### OpenCore Legacy Patcher T2

- **저장소:** https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2
- **라이선스:** BSD 3-Clause
- **저작권:** Copyright (c) 2020–2025 Dhinak G, Mykola Grymalyuk, and individual contributors.

### OpenCore Legacy Patcher (Dortania)

- **저장소:** https://github.com/dortania/OpenCore-Legacy-Patcher
- **라이선스:** BSD 3-Clause
- **저작권:** Copyright (c) 2020–2025 Dhinak G, Mykola Grymalyuk, and individual contributors.

### OpenCorePkg-add-T2-support

- **저장소:** https://github.com/albert-mueller/OpenCorePkg-add-T2-support
- **라이선스:** BSD 3-Clause
- **저작권:** HermitCrabs Lab, Download-Fritz, savvas, vit9696 등 (저장소 참조)

### PatcherSupportPkg

- **저장소:** https://github.com/hackdoc/PatcherSupportPkg
- **라이선스:** 각 저자 권리 (별도 LICENSE 파일 없음 — 저장소 정책 준수)

### MetallibSupportPkg

- **저장소:** https://github.com/dortania/MetallibSupportPkg
- **라이선스:** 포크 시점 LICENSE 미확인 시 Dortania 저장소 정책 따름
- **용도:** 레거시 GPU `.metallib` 패치

---

## 부트로더 및 Kext (Acidanthera)

| 구성 요소 | 라이선스 | URL |
|-----------|----------|-----|
| OpenCorePkg | BSD 3-Clause | https://github.com/acidanthera/OpenCorePkg |
| Lilu | BSD 3-Clause | https://github.com/acidanthera/Lilu |
| WhateverGreen | BSD 3-Clause | https://github.com/acidanthera/WhateverGreen |
| AirportBrcmFixup | BSD 3-Clause | https://github.com/acidanthera/AirportBrcmFixup |
| CPUFriend | BSD 3-Clause | https://github.com/acidanthera/CPUFriend |
| RestrictEvents | BSD 3-Clause | https://github.com/acidanthera/RestrictEvents |
| FeatureUnlock | BSD 3-Clause | https://github.com/acidanthera/FeatureUnlock |
| DebugEnhancer | BSD 3-Clause | https://github.com/acidanthera/DebugEnhancer |
| CryptexFixup | BSD 3-Clause | https://github.com/acidanthera/CryptexFixup |
| NVMeFix | GPL 2.0 | https://github.com/acidanthera/NVMeFix |

---

## 기타 번들 구성 요소

| 구성 요소 | 라이선스 | 비고 |
|-----------|----------|------|
| Innie | BSD 3-Clause | https://github.com/cdf/Innie |
| AAAMouSSE | All rights reserved | Syncretic — 폐쇄 소스 |
| telemetrap | All rights reserved | Syncretic — 폐쇄 소스 |
| SurPlus | 저장소 참조 | https://github.com/reenigneorcim/SurPlus |
| AMFIPass | 저자 참조 | Dhinak G |
| Apple 바이너리 | Apple Proprietary | Apple Inc. |
| Non-Metal / 3802 Metal 패치 | 각 저자 | moraea 등 |

상세 목록: [docs/LICENSE.md](./docs/LICENSE.md)

---

## BSD 3-Clause 요약

소스·바이너리 형태로 재배포·사용 가능하나, (1) 저작권·조건·면책 유지, (2) 바이너리 배포 시 문서에 동일 고지, (3) 해당 시 Dortania·OCLP·26x86 표기, (4) 무단 보증·승인 금지.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.**

전문: `LICENSE.txt`
