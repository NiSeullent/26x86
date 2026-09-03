# Tahoe Metallib / Opaque shader / WindowServer cache — Track E

> **프로젝트:** 26x86 (`NiSeullent/26x86`)  
> **트랙:** E — MetallibSupportPkg · LegacyMetal31001 · RenderBox · Opaque  
> **작성일:** 2026-09-04  
> **관련:** [Tahoe-SkyLight-LUT-Research.md](./Tahoe-SkyLight-LUT-Research.md) · [wiki/Mac-Pro-Tahoe-Yellow-Screen.md](./wiki/Mac-Pro-Tahoe-Yellow-Screen.md)

---

## 1. LegacyMetal31001 no-op 원인

`LegacyMetal31001.patches()` → `Metal 31001 Common` 은 **RenderBox `default.metallib` overwrite 한 줄**이다 (OCLP [PR #1176](https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1176)).

| 조건 | 결과 |
|------|------|
| `xnu < Ventura` | 빈 dict (대상 OS 아님) |
| `RenderBox-<xnu>/.../default.metallib` 없음 | **의도적 no-op** — 사전에 OVERWRITE를내면 preflight가 `Failed to find .../default.metallib` 로 실패 |
| 파일 크기 0 / 대형 파일인데 `MTLB` 매직 없음 | no-op (안전 게이트) |
| 페이로드 유효 | `Metal 31001 Common`만 방출 |

**핵심:** no-op은 버그가 아니라 **페이로드 공백에 대한 가드**다. Tahoe에서 PatcherSupportPkg DRAFT(`RenderBox-25`)가 비어 있으면 항상 no-op이다.

코드: `x86/graphics/metallib_preflight.py` · `sys_patch/.../metal_31001.py`

---

## 2. Tahoe metallib 갭 (31001 vs 3802)

두 경로는 **섞으면 안 된다.**

| 경로 | 대상 GPU | 페이로드 | Tahoe |
|------|----------|----------|-------|
| **RenderBox-25 `default.metallib`** | Metal **31001** (GCN/Polaris/Vega, BDW/SKL) | PSP / OCLP nightly `RenderBox-<xnu>` | **필요** — Liquid Glass Opaque 소스 |
| **MetallibSupportPkg** | Metal **3802** (IVB/HSW/Kepler) | `/Library/Application Support/*/MetallibSupportPkg` | **shared 가드 유지** — `metal_3802.py`가 XNU≥25에서 `{}` |

Sequoia에서 도입된 metallib 포맷(V27) 재작성은 3802 전용이다. 31001 RenderBox 공백을 MetallibSupportPkg로 “대체”하면 ABI/셰이더 세대가 어긋난다.

---

## 3. Opaque shader corruption ↔ WindowServer cache

```
RenderBox.default.metallib  (소스 Opaque / Liquid Glass 프로그램)
        │
        ▼
WindowServer ── compile / cache ──► /private/var/folders/.../WindowServer/
                                        com.apple.WindowServer   ← 손상 시 노란 화면 고정
```

| 조치 | 하는 일 | 한계 |
|------|---------|------|
| 캐시 삭제 + `chflags uchg` | 손상 Opaque 재기록 차단 → 재생성 유도 | **소스 metallib/ABI가 틀리면 또 깨짐** |
| RenderBox overwrite (페이로드 있을 때) | 소스 교체 | 페이로드 없으면 no-op |
| MetallibSupportPkg 3802 | 무관 | Tahoe에서 잠금 |

완화 코드: `sys_patch_helpers.disable_window_server_caching`  
관계 직렬화: `x86/graphics/metallib_opaque.py`  
읽기 전용 프로브: `probe_window_server_opaque_cache()` (삭제/uchg **안 함**)

---

## 4. 안전한 preflight 훅 (전면 주입 금지)

허용:

- 페이로드 **존재·크기·MTLB 매직** 검사
- `Metal 31001 Common` **조건부** OVERWRITE만
- detect JSON: `legacy_metal_31001_noop`, `metallib_gaps`, `opaque_shader_ws_cache`

금지 (이 트랙):

- Tahoe에서 `Metal 3802 *` / Non-Metal shared 가드 해제
- 추정 metallib 바이트 생성·전 시스템 metallib 일괄 주입
- SkyLight / ColorSync / AGDC / PSP 바이너리 복사 (B/C/D/F)

```bash
cd 26x86 && python3 -m unittest x86.graphics.test_metallib_preflight
```

---

## 5. 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | Track E — gap 정리, Opaque↔WS 문서, `metallib_preflight` / `metallib_opaque` |
