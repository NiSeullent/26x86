# SkyLight / WindowServer 심볼·경로 부록 (Track B)

> **소유:** Track B (`x86/graphics/skylight_analysis.py`)  
> **메인 연구 문서 (Track A):** [Tahoe-SkyLight-LUT-Research.md](./Tahoe-SkyLight-LUT-Research.md)  
> **작성일:** 2026-09-04 · **갱신:** extreme unlock

이 문서는 **바이너리 경로·심볼·PoC 훅**만 정리합니다. 공유 모듈 통합은 Mission Control.

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
| SL-FRAMEWORK-MERGE | **extreme** | `X86_EXTREME=1` 시 merge scaffold |
| SL-STUB-MARKER | active | SkyLightOld detect |
| SL-SHADERS-AIR64 | cross_ref | Track E |
| SL-BYTEPATCH-LUT | **extreme** | dry-run→`apply_byte_patch` |

게이트: `X86_EXTREME=1` 또는 `extreme=True`.

---

## 3. 바이트패치 dry-run → apply

```python
from x86.graphics.skylight_analysis import dry_run_byte_patch, apply_byte_patch

dry_run_byte_patch(Path("SkyLight"))
apply_byte_patch(Path("SkyLight"), dry_run=False, extreme=True)
```

`BYTE_PATCH_CANDIDATES` — 동일 길이 find/replace. 기본값은 마커/아이덴티티 프로브; 호스트 적용 전 RE 바늘로 교체.

---

## 4. 테스트

```bash
python3 -m unittest x86.graphics.test_skylight_analysis
```
