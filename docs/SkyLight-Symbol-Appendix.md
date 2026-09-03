# SkyLight / WindowServer 심볼·경로 부록 (Track B)

> **소유:** Track B (`x86/graphics/skylight_analysis.py`)  
> **메인 연구 문서 (Track A):** [Tahoe-SkyLight-LUT-Research.md](./Tahoe-SkyLight-LUT-Research.md)  
> **작성일:** 2026-09-04

이 문서는 **바이너리 경로·공개/문서화 심볼·OCLP 패치 근거**만 정리합니다. LUT 파이프라인·복구 로드맵은 A 문서를 보세요. 공유 모듈 통합은 Mission Control.

---

## 1. 호스트 경로

| 경로 | 역할 | Tahoe 비고 |
|------|------|-----------|
| `/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A/SkyLight` | 합성기 | 스톡은 SkyLightPlugins **미로드** |
| `.../SkyLightOld.dylib` | Non-Metal stub 마커 | moraea injector |
| `/Library/Application Support/SkyLightPlugins/` | `.dylib`+`.txt` | 패치된 SkyLight만 |
| `/System/Library/CoreServices/WindowServer` | 합성 프로세스 | Opaque cache |
| `.../SkyLightShaders.air64.metallib` | Metal 3802 | Track E |

PSP: `10.14.6-<xnu>` (Tahoe 캡 `-24`). `non_metal.py`는 XNU≥25에서 `{}` (KP 가드).

---

## 2. 심볼

| 심볼 | 근거 | 용도 |
|------|------|------|
| `SkyLightPluginEntry` | ASentientBot/monterey 2022-1-16 | 플러그인 엔트리 |
| Plugins v2 경로 | monterey 2021-12-9 | data-volume 슬롯 |
| 공개 ColorSync/CG 바늘 | 헤더 | 인벤토리만 |

**금지:** OCLP-T2 #194 사설 심볼 미공개 → `SL-BYTEPATCH-LUT` rejected.

---

## 3. PoC 훅 (`SKYLIGHT_HOOK_REGISTRY`)

| hook_id | status | Tahoe |
|---------|--------|-------|
| SL-WS-CACHE | active | ✅ |
| SL-PLUGIN-PROTOCOL | scaffold | ✅* 스톡 무효 |
| SL-FRAMEWORK-MERGE | blocked | ❌ |
| SL-STUB-MARKER | active | ✅ |
| SL-SHADERS-AIR64 | cross_ref | E |
| SL-BYTEPATCH-LUT | rejected | ❌ |

G: `sys_patch_hooks` / `serialize_track_detect_fields`.

```bash
python3 -m unittest x86.graphics.test_skylight_analysis
```
