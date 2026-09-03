# SkyLight / WindowServer 심볼·경로 부록 (Track B)

> **소유:** Track B (`x86/graphics/skylight_analysis.py`)  
> **메인 연구 문서 (Track A):** [Tahoe-SkyLight-LUT-Research.md](./Tahoe-SkyLight-LUT-Research.md)  
> **조율:** INTEGRATE `52f7298` · B extreme bytepatch `55c3802` ↔ L5-R rootpatch

이 문서는 **바이너리 경로·심볼·PoC 훅**만 정리합니다. 공유 모듈 통합은 Mission Control.

---

## 0. Track B vs L5-R 역할 분담

| 트랙 | 모듈 | 역할 |
|------|------|------|
| **B** | `skylight_analysis.py` | 분석·nm 픽스처·`BYTE_PATCH_CANDIDATES`·`dry_run_byte_patch` / `apply_byte_patch` API |
| **L5-R** | `skylight_lut_rootpatch.py` | sys_patch **MERGE / OVERWRITE** 루트볼륨 레시피 (`BINARY_PATCH_CANDIDATES` → `L5-patched/`) |

마커 prefix: B=`26X86_SL_*` · L5=`26X86_L5_*` (충돌 방지).

---

## 1. 호스트 경로

| 경로 | 역할 |
|------|------|
| `.../SkyLight` | 합성기 |
| `.../SkyLightOld.dylib` | Non-Metal stub 마커 |
| `/Library/Application Support/SkyLightPlugins/` | `.dylib`+`.txt` |
| `/System/Library/CoreServices/WindowServer` | 합성 프로세스 |

---

## 2. PoC 훅 (blocked/rejected 없음)

| hook_id | status | 비고 |
|---------|--------|------|
| SL-WS-CACHE | active | WS 캐시 완화 |
| SL-PLUGIN-PROTOCOL | scaffold | SHA 핀 dylib |
| SL-FRAMEWORK-MERGE | **extreme** | scaffold만; 본문 MERGE는 L5-R |
| SL-STUB-MARKER | active | SkyLightOld detect |
| SL-SHADERS-AIR64 | cross_ref | Track E |
| SL-BYTEPATCH-LUT | **extreme** | B API dry-run→apply |

게이트: `X86_EXTREME=1` 또는 `extreme=True`.

---

## 3. 바이트패치 dry-run → apply (B API)

```python
from x86.graphics.skylight_analysis import dry_run_byte_patch, apply_byte_patch

dry_run_byte_patch(Path("SkyLight"))
apply_byte_patch(Path("SkyLight"), dry_run=False, extreme=True)
```

루트볼륨 OVERWRITE 스테이징은 L5-R 문서:
`docs/EXTREME-SkyLight-LUT-Rootpatch.stage-L5.md`.

---

## 4. 테스트

```bash
python3 -m unittest x86.graphics.test_skylight_analysis
```
