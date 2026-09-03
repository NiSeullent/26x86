# Tahoe / Pre-AVX — Metal shader compiler & compositor AVX 게이트 (Track J)

**미션:** Safari26-PreAVX와 **유사하게** 그래픽 스택에서 AVX `SIGILL`/기능 비트 게이트를 찾고 우회한다.  
**소유:** `x86/graphics/shader_avx_*.py`, `shader_avx_detect.stage-J.py`, 이 문서  
**공유 merge:** MC `feat(extreme-INTEGRATE): promote J` — `detect.py` + `skylight_tracks.py` (detect-only; J ∉ SYS_PATCH).  
**게이트:** 변이 PoC는 `X86_EXTREME=1` 만.

## 핵심 결론 (Sequoia 15.5 / MacPro5,1 / Xeon X5675)

| 대상 | Safari형 `vmovaps` 트램폴린 | `hw.optional.avx*` | 해석 |
|------|---------------------------|-------------------|------|
| SkyLight `__TEXT` | **0** | `avx2_0` | 쿼리만; 무조건 VEX 블록 없음 |
| RenderBox / Metal / QuartzCore / MTLCompiler | **0** | — | AVX SIGILL 후보 아님 |
| CoreDisplay | **0** | `avx1_0`, `avx2_0` | 기능 비트 분기 가능 |
| `libGPUCompilerImplLazy` | dense run **0** | LLVM `__AVX__` / `+avx` | 호스트 codegen 플래그 |
| `default.metallib` | host VEX **0** | — | AIR/GPU IR |

**판정:** 이 빌드에서 WindowServer 노란 화면 ≠ AVX SIGILL. RestrictEvents `revpatch=jsc`는 JavaScriptCore 전용.

## Safari26 대응

- `c5 f8 29` = VEX `vmovaps` → pre-AVX `#UD` / `SIGILL`
- 동일 길이 SSE 치환 테이블: `shader_avx_opcodes.py`
- 가칭 `revpatch=gfx` — 문서만 (업스트림 미구현, `jsc` 재사용 금지)

## 모듈

| 파일 | 역할 |
|------|------|
| `shader_avx_opcodes.py` | VEX/SSE 서명·치환 |
| `shader_avx_scan.py` | standalone + dyld cache 스캔 |
| `shader_avx_gate.py` | `X86_EXTREME` 게이트·detect JSON 조각 |
| `shader_avx_detect.stage-J.py` | G/detect merge 훅 (공유 파일 미수정) |

```python
# Track G / detect 측 (다른 트랙이 적용):
from importlib.util import spec_from_file_location, module_from_spec
# 또는: merge_into_graphics_payload(payload)
```

## PoC (`X86_EXTREME=1`)

1. `scan_graphics_avx_surface(probe_host=True, include_shared_cache=True)`
2. `dense_trampoline_hints > 0` → SSE 치환 후보 — **자동 루트패치 없음**
3. pre-AVX에서 `hw.optional.avx*=1` 스푸핑 **금지**


## MC INTEGRATE — J detect · **done**

`integrate_queue`: ~~`next:J-detect-stage`~~ → **promoted** (base `d1093ef` / stages `3800bf8`·`393192d`).

- Live: `detect.py` inserts `shader_avx` after `payload.update(yellow)`.
- Live: `skylight_tracks` registers J detect-only; tid includes H,J,L5; **J not in SYS_PATCH_TRACKS**.

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | Track J 전용 파일만 추가 (공유 파일 무수정) |
| 2026-09-04 | INTEGRATE 52f7298 — stage-J mc_merge_plan + detect/tracks stage snippets |
| 2026-09-04 | stage-J를 `d1093ef` (H+L5) 기준으로 재정렬 — 다음 INTEGRATE = J detect |
| 2026-09-04 | **INTEGRATE** J detect → live detect/skylight_tracks |
