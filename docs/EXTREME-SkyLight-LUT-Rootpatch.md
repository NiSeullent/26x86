# EXTREME — SkyLight / CoreDisplay 루트 볼륨 OVERWRITE (L5-R)

> **트랙:** **L5-R** (`feat(skylight-L5):`)  
> **조율:** Track B `55c3802` (bytepatch API) · INTEGRATE `52f7298`  
> **소유:** `skylight_lut_rootpatch.py`, `*.stage-L5`  
> **공유 금지:** `metal_3802` / `sys_patch` / `non_metal*` / `skylight_analysis` 본문  
> **게이트:** `X86_EXTREME=1` → 패치 dict 충전 (blocked 없음)  
> **금지:** 런타임 pid inject / `task_for_pid` (L 프로세스주입 교체)

## B ↔ L5-R 역할

| 트랙 | 역할 |
|------|------|
| **B** | 심볼 분석, `BYTE_PATCH_CANDIDATES` (`26X86_SL_*`), dry-run→apply API |
| **L5-R** | sys_patch **OVERWRITE**/MERGE 레시피, `BINARY_PATCH_CANDIDATES` → `L5-patched/` |

## 기본 레시피 (`X86_EXTREME=1`)

```text
Overwrite System Volume
  /System/Library/PrivateFrameworks/SkyLight.framework  ← 10.14.6-24
  /System/Library/Frameworks/CoreDisplay.framework      ← 10.14.4-24
```

`X86_EXTREME_SKYLIGHT_ROOTPATCH_MODE=merge` 이면 Non-Metal Common식 MERGE.

## 사용

```bash
X86_EXTREME=1 python3 -m x86.graphics.skylight_lut_rootpatch
python3 x86/graphics/test_skylight_lut_rootpatch.stage-L5.py
```

## G 계약

`sys_patch_hooks(xnu, minor, marketing) -> dict` — extreme+Tahoe에서 non-empty.
