# ⚠️ 주의사항 (Warnings)

본 페이지는 README 및 관련 문서에 흩어져 있던 **모든 주의·경고**를 통합합니다. 사용 전 반드시 읽으세요.

> **면책:** 실험적 알파 단계 소프트웨어입니다. 전체 데이터를 **백업**한 뒤 **여분의 Mac**에서 테스트하세요. 전문: [Disclaimer.md](./Disclaimer.md)

---

## Intel Core 2 Duo Mac

다음 모델 등은 AAAMouSSE·telemetrap 한계로 **현재 macOS 26 Tahoe 부팅이 불가능**할 수 있습니다.

- 2008–2010 MacBook / MacBook Pro / MacBook Air
- 2009–2010 Mac mini
- 2008 Mac Pro

자세한 논의: [MacRumors 스레드](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/page-9).

macOS 26에서 동작하려면 해당 kext의 역공학·재작성이 필요할 수 있으며, 두 kext는 2021년 이후 업데이트가 없고 **폐쇄 소스**입니다.

---

## 그래픽 패치 미완료 모델

macOS 26에서 다음 GPU 클래스는 **그래픽 패치가 없어 커널 패닉**이 발생할 수 있습니다.

- **Metal 8302** — 2012–2014년 Mac 전반
- **Non-Metal** — 2011년 Mac 전반

작업 진행 중이며, 해당 환경에서는 패치 주입을 막아 **가속 없이 사용**할 수 있도록 안전 장치를 두고 있습니다.

상세: [GPU-Limitations.md](./GPU-Limitations.md)

---

## T2 Mac — SIP(시스템 무결성 보호)

**T2 Mac에서는 SIP가 완전히 비활성화(0xFFF)될 수 있습니다.**

OpenCorePkg 부팅 시 열·스로틀링 등 이슈로 SIP 비활성화가 하드코딩되어 있을 수 있습니다. T2가 아닌 Mac(T1·비-T Mac)에는 적용되지 않을 수 있습니다.

상세: [T2-Mac-Notes.md](./T2-Mac-Notes.md)

---

## Hackintosh EFI 빌드 미지원

본 패처는 **실제 Mac**용 OpenCore EFI를 생성합니다. Hackintosh용 BOOTx64.efi 워크플로와는 다릅니다. Hackintosh에서 EFI를 빌드하는 것은 **지원하지 않습니다**.

---

## macOS 27 Golden Gate 이후 미지원

macOS 27 Golden Gate 및 이후 버전은 **Apple Silicon(arm64) 전용**으로 예상됩니다. **macOS 26 Tahoe**가 본 프로젝트의 마지막 주요 지원 대상입니다.

---

## 소스·빌드 관련

- **태그 없는 최신 커밋** 빌드는 개발 중입니다. 테스트·안전·동작이 보장되지 않습니다. **주력 Mac에서 사용하지 마세요.** [CHANGELOG](../../CHANGELOG.md)를 먼저 읽으세요.
- 포럼 등에 **비공식 바이너리 링크를 공유하지 마세요.** 본 문서 또는 [공식 Releases](https://github.com/NiSeullent/26x86/releases)만 링크하세요.
- 신뢰할 수 없는 출처의 재업로드 바이너리는 **보안 위험**이 있습니다.
- Xcode/CLT에 포함된 **Python 3.9는 지원하지 않습니다.** Python **3.13+** (python.org 또는 uv)를 사용하세요.
- Apple Silicon Mac 호스트에서는 x86 macOS VM이 제한됩니다. **Intel Mac 호스트**에서 VM 테스트를 권장합니다.

---

## 설치·업그레이드

- **클린 설치·업그레이드**만 공식 지원합니다. Patched Sur, bigmac 등으로 이미 패치된 Big Sur 설치본은 APFS 스냅샷·SIP 무결성 문제로 사용할 수 없습니다.
- Mojave·Catalina는 [dosdude1 패처](http://dosdude1.com) 사용을 권장합니다.

상세: [Installation-Notes.md](./Installation-Notes.md)

---

## 보안·사칭 사이트

공식 GitHub 저장소([NiSeullent/26x86](https://github.com/NiSeullent/26x86))만 사용하세요. typosquatting·가짜 사이트에서 악성코드가 유포된 사례가 있습니다.

---

## 26x86 설정·실행

- **설정:** `~/Library/Application Support/26x86/config.json` — 공유 plist에 **쓰지 않습니다.**
- **권장 실행:** `26x86.command` 또는 `python3 -m x86 wizard`
- **이전 패처와 자동 패치 동시 사용 금지** — 충돌할 수 있습니다.
- 이전 패처에서 전환: [Migration-from-OCLP.md](./Migration-from-OCLP.md)
