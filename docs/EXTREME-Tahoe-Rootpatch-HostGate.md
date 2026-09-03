# EXTREME — Tahoe-only root-patch + WIP 큐

> **정식:** `docs/EXTREME-Tahoe-Rootpatch-HostGate.md`  
> **갭:** `docs/EXTREME-Tahoe-PreAVX-Vega64.md` · Tracks: `docs/SkyLight-LUT-Tracks.md` · WIP: `docs/WIP-STATUS.md`

## 한 줄

루트패치·L5 OVERWRITE·K extreme 실주입은 **macOS 26 Tahoe (`is_tahoe`)에서만**.  
Sequoia + `X86_EXTREME=1` → 루트 **no-op**. 구현: `x86/graphics/tahoe_gate.py` (**Sweep 소유**).

## 소유 분리

| 소유 | 범위 |
|------|------|
| **Sweep** | `tahoe_gate` 모듈 · L5/M/N/I soft-import · detect `root_patch_gates` |
| **MC** | 갭/큐 문서 · J detect INTEGRATE (`33e506a`) |
| **배포 전담** | 앱·PKG · 실기 L5-patched 스테이징 (게이트 모듈 중복 금지) |

## 체크리스트

- [x] `tahoe_gate.py` tracked + push
- [x] `skylight_lut_rootpatch.py` → `is_tahoe` / `root_patches_allowed`
- [x] `metal3802_tahoe.py` / `nonmetal_tahoe.py` → gate import
- [x] **J** detect stage → live (`33e506a`)
- [ ] (선택) N IOSurface 10.15.7 prefer when H latch

## 이미 landed (재 INTEGRATE 금지)

`d1093ef` H+L5 soft-import · `a5c9d94` L5 recipes · `cfd2458` I↔K · D Tools · **J** `33e506a` · **tahoe_gate** Sweep

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | Sweep: tahoe_gate land + soft-import |
| 2026-09-04 | J detect INTEGRATE · MC race 회피 |
| 2026-09-04 | WIP Sweep: MC=docs only; H 완료 → J+gate가 Sweep 메인 |
