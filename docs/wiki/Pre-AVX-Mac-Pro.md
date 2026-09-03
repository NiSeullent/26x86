# Pre-AVX Mac Pro (Phase 1)

**26x86 Phase 1** — Mac Pro 5,1 / 6,1 Pre-AVX 감지, Metal 분기 힌트, Safari26 Pre-AVX RestrictEvents 자동 적용.

Safari SIGILL(AVX)과 WindowServer 노란 화면은 **원인·조치가 다릅니다.** 이 문서는 Safari/AVX 경로입니다. 노란 화면은 [Mac-Pro-Tahoe-Yellow-Screen.md](./Mac-Pro-Tahoe-Yellow-Screen.md)를 보세요.

---

## 빠른 확인

```bash
python3 -m x86 detect --json
```

다음 필드가 포함됩니다:

| 필드 | 설명 |
|------|------|
| `pre_avx_mac_pro` | MacPro5,1 / MacPro6,1 Pre-AVX(또는 Pre-AVX2) 프로파일 여부 |
| `recommended_metal_patch` | `3802` / `31001` / `non_metal` / `unknown` |
| `avx_available` | AVX1.0 (`machdep.cpu.features`) 존재 여부 |
| `avx2_available` / `has_avx2` | AVX2 (`machdep.cpu.leaf7_features`) 존재 여부 |
| `safari_pre_avx_fix_recommended` | Safari26 RestrictEvents 교체 권장 여부 |
| `auto_pre_avx_patch` | 사용자 설정 (기본 `true`) |
| `recommended_tahoe_graphics_policy` | Tahoe 루트 GPU 패치 정책 (`tahoe_gcn_efi_only` 등) |
| `tahoe_blocked_patches` | Tahoe에서 차단된 3802 / Non-Metal shared 패치 ID |
| `safari26_preavx` | EFI RestrictEvents 교체 판단 상세 |

---

## 두 가지 증상 (이원화)

| 경로 | 증상 | 원인 | 조치 |
|------|------|------|------|
| **Safari AVX** | Safari 크래시 / SIGILL | Pre-AVX CPU + Safari 18.2+/26 JIT | RestrictEvents 1.1.8 + `revpatch=jsc` (아래). [Safari-PreAVX-Fix.md](./Safari-PreAVX-Fix.md) |
| **WindowServer 노란 화면** | 전체 화면 노란/주황, WS 재시작, KP | Tahoe에서 Metal 3802/Non-Metal 차단 + GCN EFI `agdpmod` 누락 | GCN kext + EFI DeviceProperties. [Mac-Pro-Tahoe-Yellow-Screen.md](./Mac-Pro-Tahoe-Yellow-Screen.md) |

`detect --json`의 `safari26_preavx`는 Safari 경로, `recommended_tahoe_graphics_policy` / `tahoe_blocked_patches`는 그래픽 경로입니다.

---

## 적용 조건

### Safari26-PreAVX-Fix (RestrictEvents 1.1.8)

| 조건 | 값 |
|------|-----|
| 모델 | **MacPro5,1** (upstream 검증 기준) |
| CPU | AVX **미지원** (Westmere Xeon 등) |
| 설정 | `auto_pre_avx_patch: true` (기본) |
| 페이로드 | `payloads/Kexts/Community/Safari26-PreAVX-Fix/RestrictEvents-v1.1.8-RELEASE.zip` |
| 적용 시점 | **OpenCore EFI 빌드** (`efi_builder/misc.py`) |
| NVRAM | `revpatch`에 `jsc` 자동 추가 |

**출처·라이선스:** [kilinccagatay/Safari26-PreAVX-Fix](https://github.com/kilinccagatay/Safari26-PreAVX-Fix) — BSD 3-Clause (Acidanthera RestrictEvents 파생). 저장소 내 `LICENSE.txt`, `NOTICE.md` 참고.

### MacPro6,1 (Pre-AVX2)

- AVX1 있음, AVX2 없음 → `pre_avx_mac_pro: true`
- Safari26 kext는 **적용하지 않음** (CPU에 AVX1 존재)
- Tahoe에서 Metal **3802 / Non-Metal** 루트 패치는 안전 가드로 **차단** — AMD Legacy GCN + EFI `agdpmod` 경로 사용

### Metal variant 힌트

| 값 | OCLP 내부 | 대표 GPU |
|----|-----------|----------|
| `3802` | METAL_3802 | Kepler, Ivy/Haswell iGPU |
| `31001` | METAL_31001 | GCN/FirePro D, Polaris, Skylake |
| `non_metal` | NON_METAL | Sandy Bridge 이하, Tesla |

커뮤니티 문서의 **31002** 표기는 OCLP **31001** 스택에 해당합니다.

---

## 설정

`~/Library/Application Support/26x86/config.json`:

```json
{
  "auto_pre_avx_patch": true
}
```

`false`로 설정하면 Safari26 RestrictEvents 자동 교체 및 `revpatch=jsc` 주입을 건너뜁니다.  
레거시 키 `safari26_preavx_fix`도 동일하게 인식됩니다.

---

## Phase 1 한계

- **WindowServer 노란 화면 완전 해결**은 이 문서 범위 밖 — 정책 안내·패치 차단은 [Mac-Pro-Tahoe-Yellow-Screen.md](./Mac-Pro-Tahoe-Yellow-Screen.md)
- Safari26 kext는 **EFI 빌드 시**만 자동 적용; PKG post-install에서 EFI를 덮어쓰지 않음
- Safari **버전별** 바이트 시그니처 — 26.6.1 검증, 업데이트 시 재검증 필요
- MacPro6,1 Safari 크래시는 AVX1 있으면 **별도** 대응 (JIT 비활성 등 Phase 1 후속)

---

## 관련 문서

- [Mac-Pro-Tahoe-Yellow-Screen.md](./Mac-Pro-Tahoe-Yellow-Screen.md) — WindowServer 노란 화면
- [Safari-PreAVX-Fix.md](./Safari-PreAVX-Fix.md) — Safari RestrictEvents 상세
- [GPU-Limitations.md](./GPU-Limitations.md)
- [Configuration.md](./Configuration.md)
- [Tahoe-Graphics-Roadmap.md](../Tahoe-Graphics-Roadmap.md)
