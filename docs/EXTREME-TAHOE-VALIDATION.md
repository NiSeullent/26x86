# EXTREME — Tahoe Pre-AVX + Vega 64 Validation Matrix

> **Entry:** `python Tools/run_extreme_validation.py`  
> **Module:** `python -m x86.extreme.validation`  
> **Alt:** `python tests/extreme/run_extreme_validation.py`  
> **venv:** `/Users/nyase/Desktop/26x86/.venv` · **profile:** `macpro5-vega64-tahoe`

## 한 줄

Sequoia 개발기에서는 **mock host**로 게이트/패치 dict를 검증하고, Tahoe+Vega 실기에서는 EFI → root → yellow → extreme 순으로 적용한다. UTM/qemu/Docker가 없으면 VM smoke는 문서만.

## 검증 매트릭스

| 축 | Sequoia 15 + `X86_EXTREME=1` | Tahoe 26 + flags | 테스트 |
|----|------------------------------|------------------|--------|
| `is_tahoe` / `root_patches_allowed` | false / false | true / true | `test_tahoe_gate` |
| Metal 3802 filter | `{}` | dict 충전 | `test_metal3802_tahoe` · combo |
| Non-Metal N | `{}` | dict 충전 | `test_nonmetal_tahoe` · combo |
| L5 OVERWRITE | `{}` | SkyLight/CoreDisplay OW | `test_skylight_lut_rootpatch` |
| Yellow mitigations | `[]` | list (WS/ColorSync/EFI) | `test_yellow_screen` · combo |
| Interpose recipe | `{}` (non-Tahoe) | recipe when EXTREME | `test_interpose` |
| H latch → N IOSurface | n/a | `10.14.6`→`10.15.7` | `test_extreme_host_combo` |
| Track E RenderBox-25 | n/a | mock MTLB → 31001; missing → `{}` | `test_metallib_renderbox` |
| L5 Mach-O probe | acquire notes | MH_MAGIC_64 SkyLight+CD | `test_apply_order_mock` |
| Apply order dry-run | EFI→root→yellow→extreme | same | `apply_order` |
| Mock guest matrix | Sequoia control | MacPro5/flash/26.x | `mock_guest` |
| Profile `--extreme` dry-run | order + planned | same (mock) | `test_macpro5_vega64_tahoe` |
| EFI agdpmod / revpatch=jsc | config mutate | same | `test_gcn_agdp` · combo |
| Flashed MacPro5 + Vega ID | fixture | fixture | combo · `fixtures.py` |

## 엔트리포인트 단계

1. **detect_fixture** — MacPro5,1 + Vega `0x687F` + pre-AVX + flash 신호  
2. **patchset_emptiness** — Sequoia empty / Tahoe charged  
3. **profile_dry_run** — `macpro5-vega64-tahoe --extreme` order  
4. **efi_bridge** — agdpmod + RestrictEvents + `revpatch=jsc`  
5. **h_n_iosurface_prefer** — H latch lifts IOAccel IOSurface to 10.15.7  
6. **track_e_renderbox** — Track E soft-import + RenderBox mock path  
7. **l5_macho_probe** — SkyLight/CoreDisplay MH_MAGIC_64 (or acquire notes)  
8. **apply_order_dry_run** — EFI→root→yellow→extreme matches profile  
9. **mock_guest_matrix** — MacPro5 / flash 7,1 / 26.x / Sequoia control  
10. **unittest suite** — 위 모듈 일괄 (`--gates-only`로 게이트만)

```bash
source /Users/nyase/Desktop/26x86/.venv/bin/activate
cd /Users/nyase/Desktop/26x86/26x86
export PYTHONPATH="$PWD"
python Tools/run_extreme_validation.py
python Tools/run_extreme_validation.py --gates-only
python Tools/check_extreme_payloads.py --allow-renderbox-gap
python Tools/run_apply_order_dry_run.py
```

**주의:** `python -m unittest discover -s x86` 는 `x86/logging.py` 가 stdlib `logging` 을 가려 실패한다. 반드시 모듈명으로 로드하거나 이 엔트리포인트를 쓴다.

## VM / 격리

| 환경 | 이 Sequoia 개발기 (2026-09) | 조치 |
|------|---------------------------|------|
| UTM | 없음 | Tahoe guest 생기면 아래 guest smoke |
| qemu | 없음 | 동일 |
| Docker | 없음 | macOS guest 불가에 가깝 → mock 유지 |
| Mock | **기본** | `xnu_major=25`, `product_version=26.0`, ModelIdentifier=`MacPro5,1`, Vega PCI `0x687F` |

### Guest smoke (Tahoe VM이 있을 때)

```bash
# guest 안에서 repo + venv 마운트/클론 후
export PYTHONPATH="$PWD"
export X86_EXTREME=1
python -m x86.extreme.validation --gates-only
python -m x86.profiles apply macpro5-vega64-tahoe --dry-run --extreme
python -m x86 detect --json 2>/dev/null | head -c 4000
```

스크립트: `tests/extreme/guest_smoke.sh` (있을 때).

## 실기 체크리스트

### A. Sequoia 개발기 (지금)

- [x] `tahoe_gate` live + unit green  
- [x] Sequoia+EXTREME → root/L5/3802/N yellow **no-op** 증명  
- [x] extreme validation 엔트리포인트  
- [ ] (선택) UTM Tahoe guest 설치 후 guest smoke  

### B. Tahoe + Vega 목표 Mac (플래시 cMP)

순서 (재부팅 포함):

1. **EFI rebuild** — profile `macpro5-vega64-tahoe` (agdpmod/shikigva, KDKless, RestrictEvents+`revpatch=jsc`)  
2. 재부팅 → OpenCore 확인  
3. **Root patch** — AMD Vega (Metal 31001)  
4. **Yellow mitigations** — WS cache / ColorSync / PSP prefer  
5. **Extreme flags** (필요 시만):  
   - `X86_EXTREME=1`  
   - Metal 3802: `X86_TAHOE_3802=1`  
   - Non-Metal: `X86_TAHOE_NONMETAL=1`  
   - H IOSurface/CA: `X86_EXTREME_IOSURFACE_CA=1` (N과 병행 시 IOSurface **10.15.7** prefer)  
   - L5 OVERWRITE: extreme + Tahoe only  
   - Interpose: EXTREME; live `/Library` 는 `X86_EXTREME_INSTALL=1`  
6. `Tools/collect_graphics_diagnostics.command`  
7. 앱/PKG 설치는 **배포 에이전트**와 조율 (GUI Tauri race 시 pull만)

## 트랙 랜딩 vs 실기 갭

| 트랙 | 코드 랜딩 | 실기 갭 |
|------|-----------|---------|
| A–N / L5-R / M/N/H/I/J/F | 대부분 INTEGRATE + `tahoe_gate` | L5-patched Mach-O 스테이징, 앱/PKG |
| E RenderBox-25 | soft-import `metallib_renderbox` | PSP에 RenderBox-25 없음 → nightly/획득 |
| N∥H IOSurface | **prefer 10.15.7 landed** | 실기 KP 관측 |
| B bytepatch | extreme_unlocked | 배포 조율 |
| GUI Tauri | 별 에이전트 | 이 트랙에서 대규모 재작성 금지 |

## RenderBox-25 / L5 획득

| 페이로드 | 이 개발기 상태 | 획득 |
|----------|----------------|------|
| `RenderBox-25/.../default.metallib` | **없음** (22–24만) | OCLP/PSP nightly · `Tools/check_extreme_payloads.py` |
| `10.14.6-24` SkyLight Mach-O | PSP sibling 있으면 ✅ | `26x86-PatcherSupportPkg` |
| `10.14.4-24` CoreDisplay | PSP sibling 있으면 ✅ | 동일 |
| `L5-patched/` binary | optional | B needle handoff |

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | Track E soft-import · L5 Mach-O probe · apply-order · mock guest |
| 2026-09-04 | 검증 매트릭스 · entrypoint · H→N IOSurface prefer · combo tests |
