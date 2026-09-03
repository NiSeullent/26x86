# Mac Pro · macOS 26 Tahoe 노란 화면 (WindowServer)

Safari 크래시(AVX SIGILL)와 **전체 화면 노란/주황**은 별개입니다. Safari 경로는 [Pre-AVX-Mac-Pro.md](./Pre-AVX-Mac-Pro.md)를 보세요.

이 문서는 **WindowServer / CoreDisplay** 노란 화면, 커널 패닉, 가속 없음의 원인과 권장 조치입니다.

---

## 원인 요약

| 요인 | 설명 |
|------|------|
| **Metal 3802 / Non-Metal shared 패치 차단** | Tahoe에서 `Metal 3802 Common`, `Non-Metal Common` 등은 **의도적으로 비활성화**되어 있습니다. 강제 적용 시 KP·노란 화면·WS crash loop 위험이 있습니다. |
| **MacPro6,1 + GCN 7000** | Ivy Bridge Xeon(AVX1, AVX2 없음) + 듀얼 FirePro D300/D500/D700. 루트 Metal 3802/Non-Metal로는 가속을 기대할 수 없습니다. |
| **EFI DeviceProperties 미설정** | `agdpmod` / `shikigva` 없이 부팅하면 AGDCDiagnose solid yellow 또는 설치 99% 노란 화면이 발생할 수 있습니다. |
| **Pre-AVX2 CPU** | MacPro5,1(Westmere) 등은 AVX2가 없어 Polaris 자동 경로와 맞물리지 않습니다. |

26x86은 `x86/graphics/detect.py` → `HardwarePatchsetDetection`에서 Tahoe + Pre-AVX Mac Pro일 때 **3802/Non-Metal 하드웨어 변형을 패치 목록에서 제거**하고, **AMD Legacy GCN kext + EFI agdpmod** 경로를 안내합니다.

---

## 모델별 AVX · GPU 프로필

| 모델 | CPU | AVX1 | AVX2 | 기본 GPU | Tahoe 권장 정책 |
|------|-----|------|------|----------|-----------------|
| MacPro5,1 | Westmere Xeon | ✅(업그레이드 CPU) | ❌ | 소켓 GPU / TeraScale 2 | `tahoe_no_legacy_gpu_root_patch` |
| MacPro6,1 | Ivy Bridge Xeon | ✅ | ❌ | 듀얼 GCN 7000 (FirePro D) | `tahoe_gcn_efi_only` |

진단:

```bash
python3 -m x86 detect --json
```

확인 필드: `gpu_family`, `yellow_screen_risk`, `pre_avx_mac_pro`, `avx_available`, `avx2_available`, `recommended_tahoe_graphics_policy`, `tahoe_blocked_patches`

루트 패치 전 `sys_patch` preflight와 GUI `get_patch_status`에 `graphics_policy_warnings`가 포함됩니다.

---

## MacPro6,1 권장 조치 (GCN / 노란 화면)

1. **EFI 빌드·재설치** — `efi_builder/graphics_audio.py`가 MacPro6,1에 `agdpmod` / `shikigva`를 주입합니다.
2. **루트 패치** — **AMD Legacy GCN** kext 다운그레이드만 기대하세요. Metal 3802 / Non-Metal shared 패치는 Tahoe에서 차단됩니다 (`tahoe_blocked_patches`).
3. **WindowServer 캐시** — GCN 패치 후 WS 캐시 비활성화가 적용될 수 있습니다.
4. **진단** — `Tools/collect_graphics_diagnostics.command`로 WindowServer 로그를 수집하세요.

---

## MacPro5,1 권장 조치

1. **GPU 세대 확인** — TeraScale 2 / Kepler dGPU는 Non-Metal·3802 계열입니다. Tahoe에서 **루트 GPU 가속 패치는 적용되지 않습니다**.
2. **CPU 업그레이드(AVX2)** — Haswell/Broadwell Xeon 등 AVX2 CPU면 Polaris/Vega kext 경로(`tahoe_modern_mac_pro`)를 검토하세요. **3802/Non-Metal shared 패치는 여전히 Tahoe에서 차단**됩니다.
3. **Safari / AVX** — AVX1 미지원 5,1은 Safari SIGILL 가능. 조치는 [Pre-AVX-Mac-Pro.md](./Pre-AVX-Mac-Pro.md)입니다.

---

## Tahoe에서 차단되는 shared 패치 ID

- `Metal 3802 Common` / `Extended` / `.metallibs`
- `Non-Metal Common` / `IOAccelerator` / `CoreDisplay` / `Enforcement`

개발자 우회(`~/.26x86_developer`)는 model-specific 패치만 영향을 주며, **shared 가드는 유지**됩니다.

---

## 관련 문서

- [Pre-AVX-Mac-Pro.md](./Pre-AVX-Mac-Pro.md) — Safari AVX / RestrictEvents
- [GPU-Limitations.md](./GPU-Limitations.md)
- [Warnings.md](./Warnings.md)
