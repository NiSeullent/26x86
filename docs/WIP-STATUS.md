# WIP STATUS — Sweep INTEGRATE

> **기준:** `33e506a` (J promote) + 본 Sweep `tahoe_gate` land  
> **소유:** Sweep=`tahoe_gate` 모듈 · 배포 에이전트=`앱/PKG` 설치 (중복 금지)

## Before (pull `33e506a`)

| 항목 | 상태 |
|------|------|
| J detect | ✅ MC INTEGRATE `33e506a` — live `detect.py` / `skylight_tracks` |
| `tahoe_gate.py` | ❌ 미존재 → yellow/detect soft-import ImportError 위험 |
| L5 / M / N root | xnu≥25 로컬 가드만 · Sequoia+EXTREME 정책 미통일 |
| L5 unit test | `*.stage-L5.py` 만 |
| stage-* 잔여 | H/J/L5/M/N/F/D/I/K/B/L/MC 다수 |

## After (본 Sweep)

| 항목 | 상태 |
|------|------|
| **`x86/graphics/tahoe_gate.py`** | ✅ live — `is_tahoe` · `root_patches_allowed` · M/N unlock helpers |
| yellow / detect | soft-import gate · `root_patch_gates` in detect JSON |
| L5 / M / N / I | soft-import Tahoe-only (Sequoia+EXTREME → `{}` / block) |
| L5 tests + docs | live `test_skylight_lut_rootpatch.py` · `EXTREME-SkyLight-LUT-Rootpatch.md` |
| I docs | live `EXTREME-Interpose-Track-I.md` |
| HostGate docs | live `EXTREME-Tahoe-Rootpatch-HostGate.md` |
| M/N unit tests | post-INTEGRATE 기대값으로 갱신 |

## 남은 stage-* (archive / 보류)

| stage | 처리 |
|-------|------|
| `*.stage-J` | archive (live 승격됨 `33e506a`) |
| `*.stage-H` / `MC-PROMOTE-H` | archive (live `d1093ef`) |
| `*.stage-L5` | archive (recipes live; test/docs 승격) |
| `*.stage-M` / `*.stage-N` | archive (live opt-in 이미 통합) |
| `*.stage-F` / `*.stage-D` | archive (live) |
| `*.stage-K` / `extreme_interpose_link.stage-K` | mirror only |
| `*.stage-I` | archive (doc 승격) |
| `*.stage-B` / `windowserver_hook.stage-L` | research / refused L |
| `*.stage-MC` | archive after HostGate doc promote |

## 남은 실무 (비-Sweep 또는 deferred)

- N IOSurface 10.15.7 prefer when H latch — ✅ code (`prefer_h_iosurface_versions`)
- 검증 엔트리 — `Tools/run_extreme_validation.py` · `docs/EXTREME-TAHOE-VALIDATION.md`
- Track E `metallib_renderbox` soft-import + RenderBox-25 probe/acquire docs
- L5 Mach-O probe + `Tools/check_extreme_payloads.py`
- Apply-order dry-run + mock guest matrix
- L5-patched Mach-O 실기 · 앱/PKG — **배포 에이전트**
- Track E RenderBox-25 **바이너리** — 공개 미러 없음 → `fetch_renderbox25.py --provisional-from-24` (path gate ✅, ABI research)
- Track B bytepatch 실기 조율 — deploy
- Tahoe VM guest smoke — UTM/qemu 없음 → mock guest harness

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | Track E soft-import + L5 probe + apply-order + mock guest |
| 2026-09-04 | Validate: extreme suite + H→N IOSurface prefer + docs matrix |
| 2026-09-04 | MC J INTEGRATE `33e506a` |
| 2026-09-04 | Sweep: `tahoe_gate` land + L5/M/N/I soft-import + WIP-STATUS |
