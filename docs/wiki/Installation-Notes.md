# 설치·업그레이드 노트

---

## 공식 지원 경로

- **클린 설치** 및 **공식 업그레이드**만 공식 지원합니다.
- Patched Sur, bigmac 등으로 **이미 패치된 Big Sur** 설치본은 APFS 스냅샷·SIP 무결성 문제로 **사용할 수 없습니다**.

---

## 다른 패처에서 전환

- Mod·Plus·**공식 패처** 사용자는 **루트 패치를 되돌린 뒤** 26x86으로 업그레이드할 수 있습니다.
- 26x86으로 macOS를 **재설치**하면서 **기존 데이터를 유지**할 수 있습니다.

---

## OS 버전 범위

- 26x86은 **Monterey ~ Tahoe** 패치를 공식 지원합니다.
- 그 이전 OS는 OpenCore가 동작할 수 있으나 Albert Müller 포크 기준 **공식 지원은 제공하지 않습니다**.
- **Mojave·Catalina**는 [dosdude1 패처](http://dosdude1.com) 사용을 권장합니다.

---

## T2 Mac

- Releases에서 안정 빌드 다운로드 권장. [T2-Mac-Notes.md](./T2-Mac-Notes.md)
- Non-T2 Tahoe 설치 참고: [T2-Mac-Notes.md](./T2-Mac-Notes.md)

---

## 개발 환경 (개발자용)

| 항목 | 요구 |
|------|------|
| Python | **3.13+** (Xcode/CLT 내장 3.9 **비지원**) |
| macOS 호스트 | 15.x Sequoia 이상 권장 |
| VM 테스트 | **Intel Mac 호스트** 권장 (Apple Silicon에서는 x86 macOS VM 제한) |

상세 셋업: [docs/SETUP.md](../SETUP.md)

---

## 시작하기 (사용자)

```bash
python -m x86 wizard    # 권장 — 마법사 GUI
python -m x86 status    # 설정·패치 상태
```

- 이전 패처에서 전환: [Migration.md](./Migration.md)
- 소스 실행: [SOURCE.md](../../SOURCE.md)
- 영문 보조: [docs/README.en.md](../README.en.md)
