# GPU 제한 사항

macOS 26 Tahoe에서 **그래픽 패치가 미완료**된 GPU 클래스와 대응 방침입니다.

---

## Metal 8302

- **대상:** 2012–2014년 Mac 전반
- **상태:** Tahoe용 그래픽 패치 **작업 중**
- **위험:** 패치 주입 시 **커널 패닉** 가능
- **현재 대응:** 패치 주입을 막고 **가속 없이 부팅만** 허용하는 안전 장치

---

## Non-Metal

- **대상:** 2011년 Mac 전반
- **상태:** Metal 8302와 유사하게 패치 **미완**
- **위험:** 커널 패닉 또는 그래픽 가속 없음

---

## Mac Pro 5,1 / 6,1 (Tahoe 노란 화면)

Safari 크래시(AVX)와 WindowServer 노란 화면은 다릅니다.

- **Safari SIGILL:** [Pre-AVX-Mac-Pro.md](./Pre-AVX-Mac-Pro.md)
- **노란 화면 / 3802·Non-Metal:** 기본은 Tahoe shared **차단**. 옵트인 해금은 [SkyLight-LUT-Tracks.md](../SkyLight-LUT-Tracks.md) (`X86_TAHOE_3802` / `X86_TAHOE_NONMETAL`). Vega 31001은 별도 — [Mac-Pro-Tahoe-Yellow-Screen.md](./Mac-Pro-Tahoe-Yellow-Screen.md)

---

## 노란 화면 vs Safari AVX (이원화)

- **전체 화면 노란/주황:** Tahoe **WindowServer compositor** 실패. GCN만이 아니라 **Polaris·Vega 64**(Mac Pro 소켓 애프터마켓 포함)에서도 발생. 공개: [OCLP-T2 #194](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194). Vega 64 재현은 **unpublished / reporter: 내부**.
- **Safari만 크래시:** Pre-AVX JavaScriptCore — WindowServer와 무관.
- 진단: `Tools/collect_graphics_diagnostics.command`, `python3 -m x86 detect --json` (`gpu_family`, `yellow_screen_risk`).
- 상세: [Mac-Pro-Tahoe-Yellow-Screen.md](./Mac-Pro-Tahoe-Yellow-Screen.md) · [Tahoe-SkyLight-LUT-Research.md](../Tahoe-SkyLight-LUT-Research.md)

---

## 지원 모델 (참고)

README의 주요 기능에 따르면, **지원 모델 한정**으로 Metal·Non-Metal GPU 그래픽 가속이 가능합니다. 본 페이지의 제한 대상 Mac은 해당 범위에 포함되지 않을 수 있습니다.

---

## 진단 도구

MacBookPro14,3 T1 등 특정 구성에서는 `Tools/collect_graphics_diagnostics.command`로 GPU·WindowServer 로그를 수집할 수 있습니다. [Tools/README.md](../../Tools/README.md) 참고.

---

## 관련 링크

- [Warnings.md](./Warnings.md) — 그래픽 주의사항 요약
- [Known-Issues.md](./Known-Issues.md) — T2 GPU/Wi-Fi 진행 상황
- [OCLP-T2 Wiki — Metal 8302](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki) (업스트림)
