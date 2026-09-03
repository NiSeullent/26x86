# EXTREME — Metal 3802 & Non-Metal Tahoe

> **영구 차단 없음.** `X86_EXTREME` / `X86_TAHOE_3802` / `X86_TAHOE_NONMETAL` (+ `X86_TAHOE_NONMETAL_ENFORCEMENT`)

## M — integrated

라이브 `metal_3802.py` ← stage-M. `filter_tahoe_3802_patches` · `metal3802_tahoe.py`.

## N — integrated

라이브 `non_metal*.py` ← stage-N ×4. `filter_nonmetal_tahoe_patches` · `nonmetal_tahoe.py`.  
Enforcement는 `X86_TAHOE_NONMETAL_ENFORCEMENT=1` 추가 필요.

## H ∥ N

extreme에서 **병행 허용** (상호 차단 없음). H=IOSurface/CA·QuartzCore 실험, N=Non-Metal shared 재주입. MC는 키 충돌 시 병합만.

## CHANGELOG

OCLP-T2 4.0.0.17001.1: yellow/KP → 기본 `{}`. 26x86은 옵트인 재충전.
