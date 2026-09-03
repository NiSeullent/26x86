# 면책 조항 (Disclaimer)

**26x86** — Better macOS 26 System for x86-Based Macintosh

> **위키:** 요약·주의사항 통합 문서는 [docs/wiki/Disclaimer.md](docs/wiki/Disclaimer.md) · [docs/wiki/Warnings.md](docs/wiki/Warnings.md) · [docs/wiki/Home.md](docs/wiki/Home.md)를 참고하세요.

---

## 실험적 소프트웨어

26x86은 **실험적(experimental) 알파 단계** 소프트웨어입니다. Apple이 공식적으로 지원하지 않는 x86 기반 Mac(특히 T2 칩 탑재 모델)에서 macOS 26 Tahoe를 실행하기 위한 커뮤니티 포크입니다.

본 소프트웨어는 다음을 **보장하지 않습니다**:

- 모든 Mac 모델에서의 정상 부팅 또는 설치
- 그래픽 가속, Wi-Fi, Bluetooth 등 하드웨어 기능의 완전한 동작
- macOS 업데이트 이후의 지속적인 호환성
- 데이터 무손실 또는 시스템 안정성

## 보증 없음 (No Warranty)

본 소프트웨어는 **「있는 그대로(AS IS)」** 제공됩니다. 저작권자 및 기여자는 명시적이거나 묵시적인 어떠한 보증도 하지 않으며, 상품성·특정 목적 적합성에 대한 보증을 포함하되 이에 국한되지 않습니다.

26x86 사용으로 인해 발생하는 **직접·간접·부수·특별·결과적 손해**(데이터 손실, 시스템 손상, 하드웨어 고장, 업무 중단 등)에 대해 개발자 및 기여자는 **법률이 허용하는 범위 내에서 책임을 지지 않습니다**.

## 데이터 백업 경고

**반드시 사용 전 전체 데이터를 백업하세요.**

- macOS 설치, 루트 패치, OpenCore EFI 구성 변경은 시스템을 복구 불가능한 상태로 만들 수 있습니다.
- Time Machine, 외장 드라이브, 클라우드 등 **신뢰할 수 있는 백업**을 준비한 뒤 진행하십시오.
- **주력(일상용) Mac이 아닌 여분의 테스트용 Mac**에서 먼저 시험하는 것을 강력히 권장합니다.

## T2 Mac — SIP(시스템 무결성 보호) 경고

**T2 칩이 탑재된 Mac에서는 SIP(System Integrity Protection)가 완전히 비활성화될 수 있습니다.**

- T2 Mac에서 OpenCorePkg를 통한 부팅 시 SIP가 0xFFF로 설정되어 **SIP가 사실상 꺼진 상태**가 될 수 있습니다.
- SIP는 macOS 핵심 시스템 파일을 악성코드로부터 보호하는 보안 기능입니다. SIP 비활성화 시 **시스템 보안 수준이 크게 낮아집니다**.
- 26x86 설정 UI의 SIP 관련 옵션은 T2 Mac에서 **대부분 효과가 없을 수 있습니다**.
- T1 Mac 또는 T2가 없는 x86 Mac에는 이 제한이 적용되지 않을 수 있습니다.

## macOS 26 (Tahoe) 제한 사항

- **macOS 26 Tahoe**가 본 프로젝트에서 지원하는 **마지막 주요 macOS 버전**입니다.
- **macOS 27 Golden Gate** 및 이후 버전은 Apple Silicon(arm64) 전용으로 예상되며, x86 Mac은 지원 대상에서 제외될 수 있습니다.
- 일부 구형 Mac(2008–2010년대 Core 2 Duo 등)은 AAAMouSSE·telemetrap 관련 커널 패닉으로 **macOS 26 부팅이 불가능**할 수 있습니다.
- 2011–2014년 Metal/non-Metal GPU Mac은 **그래픽 패치 미완료**로 커널 패닉 또는 가속 없이 동작할 수 있습니다.
- Hackintosh용 EFI 생성은 **지원되지 않습니다**. 본 패처는 **실제 Mac**용 OpenCore EFI를 생성합니다.

## 법적 고지

- Apple macOS EULA 및 관련 이용 약관을 준수할 책임은 **사용자에게** 있습니다.
- 본 프로젝트는 Apple Inc.와 **제휴·승인·후원 관계가 없습니다**.
- 상업적 재배포 또는 「26x86」 이름을 이용한 제3자 제품 홍보 시 `LICENSE.txt`의 BSD 3-Clause 조건을 준수해야 합니다.

## 문의 및 지원

본 프로젝트는 **「있는 그대로」** 제공되며 공식적인 기술 지원을 보장하지 않습니다. 문제 발생 시 GitHub Issues 또는 커뮤니티를 통해 자발적으로 도움을 구할 수 있습니다.

## 설정 파일 및 OCLP 분리

26x86은 Dortania OpenCore Legacy Patcher(OCLP)와 **런타임 설정·Launch Services·앱 설치 경로를 공유하지 않습니다.** OCLP 공유 plist를 **읽거나 쓰지 않으며**, OCLP plist 존재 여부와 **무관하게** 동작합니다.

- **26x86 설정:** `~/Library/Preferences/com.niseullent.26x86.plist`
- **로그:** `~/Library/Logs/26x86/`
- **앱 설치(PKG):** `/Library/Application Support/26x86/26x86.app`

OCLP에서 전환하거나 디스크 정리가 필요하면 [docs/wiki/Migration-from-OCLP.md](./docs/wiki/Migration-from-OCLP.md)를 참고하세요. 자세한 설정 경로는 [docs/wiki/Configuration.md](./docs/wiki/Configuration.md)를 참고하세요.

---

*Copyright © 2026 NiSeullent and 26x86 contributors. Portions copyright © 2020–2025 Dhinak G, Mykola Grymalyuk, and individual contributors.*
