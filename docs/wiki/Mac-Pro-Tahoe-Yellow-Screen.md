# Mac Pro · macOS 26 Tahoe 노란 화면 (WindowServer)

Safari 크래시(AVX SIGILL)와 **전체 화면 노란/주황**은 별개입니다. Safari 경로는 [Pre-AVX-Mac-Pro.md](./Pre-AVX-Mac-Pro.md) · [Safari-PreAVX-Fix.md](./Safari-PreAVX-Fix.md)를 보세요.

이 문서는 **WindowServer / CoreDisplay compositor** 노란 화면의 원인과 권장 조치입니다.

---

## 원인 요약

전체 화면 노란/주황은 **AVX와 무관**하며, **GCN LUT만의 문제도 아닙니다.**

| 요인 | 설명 |
|------|------|
| **공통 compositor 실패 (본질)** | Tahoe **WindowServer / SkyLight / CoreDisplay / ColorSync(ICC)** 합성. **Vega 64에서도 재현** (unpublished / reporter: 내부). 공개: [OCLP-T2 #194](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194) — MacPro5,1/6,1 + RX570도 GPU와 무관하게 보고. |
| **PatcherSupportPkg kext 공백** | `GPUCompanionBundles` 없음, PSP #16/#18 Tahoe payload 미병합. |
| **EFI DeviceProperties (완화)** | `agdpmod` / `shikigva` 누락은 증상을 악화합니다. GCN·Polaris·**Vega 64 소켓** 모두 EFI에 넣습니다. |
| **Metal 3802 / Non-Metal shared 차단** | Tahoe에서 의도적 비활성화. Vega는 별도 **31001** (`amd_vega.py`) 경로이며, 그 kext만으로 compositor는 고쳐지지 않습니다. |

`python3 -m x86 detect --json` 필드: `gpu_family`, `yellow_screen_risk`, `recommended_efi_graphics_fixes`, `patcher_support_pkg_kexts_present`.

진단: `Tools/collect_graphics_diagnostics.command`

---

## 모델별 AVX · GPU 프로필

| 모델 | CPU | AVX1 | AVX2 | 기본 GPU | Tahoe 권장 정책 |
|------|-----|------|------|----------|-----------------|
| MacPro5,1 | Westmere Xeon | ✅(업그레이드 CPU) | ❌ | 소켓 GPU (TeraScale / **Vega 64** / Polaris) | `tahoe_no_legacy_gpu_root_patch` + EFI AGDP |
| MacPro6,1 | Ivy Bridge Xeon | ✅ | ❌ | 듀얼 GCN 7000 또는 소켓 Vega | `tahoe_gcn_efi_only` + EFI AGDP |

```bash
python3 -m x86 detect --json
```

확인 필드: `gpu_family`, `yellow_screen_risk`, `pre_avx_mac_pro`, `avx_available`, `avx2_available`, `recommended_tahoe_graphics_policy`, `tahoe_blocked_patches`

루트 패치 전 `sys_patch` preflight와 GUI `get_patch_status`에 `graphics_policy_warnings`가 포함됩니다.

---

## MacPro6,1 / MacPro5,1 + Vega 64 권장 조치

1. **EFI 재빌드** — `agdpmod` / `shikigva` (GCN·Polaris·Vega). Mac Pro 소켓은 **KDKlessWorkaround.kext**도 넣습니다 (MTL 번들 누락 시 WindowServer 루프).
2. **루트 패치** — Vega `amd_vega.py` (Metal 31001) + **Tahoe Yellow Screen Mitigations**: WindowServer 캐시 잠금, ColorSync sRGB 폴백, PatcherSupportPkg `12.5-25` / **`RenderBox-25` `default.metallib`가 있으면** OCLP와 동일 overwrite. **페이로드 없으면** 셰이더/LUT 본질은 여전히 미해결입니다 ([Tahoe-SkyLight-LUT-Research.md](../Tahoe-SkyLight-LUT-Research.md)).
3. **진단** — `Tools/collect_graphics_diagnostics.command` · `python3 -m x86 detect --json` (`yellow_screen_mitigations`)
4. **Safari** — 노란 화면과 별개.

오버레이 슬롯: `payloads/Kexts/Community/Tahoe-Yellow-Screen/` (`SOURCE.md`). Apple kext는 DMG에만 있으며 이 폴더에 재배포하지 않습니다.

Metal 3802 / Non-Metal Tahoe 가드는 **유지**합니다 (커널 패닉).

---

## Tahoe에서 차단되는 shared 패치 ID

- `Metal 3802 Common` / `Extended` / `.metallibs`
- `Non-Metal Common` / `IOAccelerator` / `CoreDisplay` / `Enforcement`

개발자 우회(`~/.26x86_developer`)는 model-specific 패치만 영향을 주며, **shared 가드는 유지**됩니다.

---

## SkyLight LUT 트랙 (극한도전 · A–L)

**Autopilot / 극한도전:** Tahoe + pre-AVX + Vega 64 → 정상 색 · Metal/OpenGL · Safari Pre-AVX · 재부팅 안정.  
소유권·Mission Control: [SkyLight-LUT-Tracks.md](../SkyLight-LUT-Tracks.md).  
`python3 -m x86 detect --json` 의 `skylight_lut_tracks` 필드(트랙 G)가 연결 상태를 요약할 수 있습니다.

| 트랙 | 역할 |
|------|------|
| **A** | 문서·Mission Control — Research · Tracks · Roadmap |
| **B–C** | SkyLight/WS 심볼 · CoreDisplay/ColorSync/ICC |
| **D** | AGDC 검증만 (EFI agdpmod **재작성 금지**) |
| **E–F** | RenderBox/31001 · PSP Tahoe 오버레이 |
| **G** | 루트패치 통합 · detect · 테스트 |
| **H–L** | Plugins 로더 · UI · #234 분리 · 3802(가드) · 재부팅/KDK |

Metal 3802 / Non-Metal Tahoe 가드는 **유지**합니다.

---

## 관련 문서

- [Pre-AVX-Mac-Pro.md](./Pre-AVX-Mac-Pro.md) — Safari AVX / RestrictEvents
- [GPU-Limitations.md](./GPU-Limitations.md)
- [Warnings.md](./Warnings.md)
- [docs/Tahoe-Yellow-Screen-Research.md](../Tahoe-Yellow-Screen-Research.md)
- [docs/Tahoe-SkyLight-LUT-Research.md](../Tahoe-SkyLight-LUT-Research.md) — SkyLight/LUT/RenderBox 심층·PoC
- [docs/SkyLight-LUT-Tracks.md](../SkyLight-LUT-Tracks.md) — 극한도전 Mission Control · A–L
- [docs/Tahoe-Graphics-Roadmap.md](../Tahoe-Graphics-Roadmap.md) — Layer B compositor
