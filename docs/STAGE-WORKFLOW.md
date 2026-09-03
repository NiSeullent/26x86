# STAGE WORKFLOW — 파일 독재 금지

> **파일:** `docs/STAGE-WORKFLOW.md` (정식)  
> **승격:** `52f7298` · H/L5 `d1093ef` · J `33e506a` · Sweep `tahoe_gate`  
> **WIP:** [WIP-STATUS.md](./WIP-STATUS.md)  
> **추가 변경:** 트랙은 `*.stage-<TRACK>` 만; live 원본은 INTEGRATE/Sweep 담당만

## 목적

공유 원본을 트랙이 직접 고치지 않는다. MC/Sweep이 `feat(extreme-INTEGRATE):` 로 승격.

## 명명

`원본경로.stage-<TRACK>` (예: `tahoe_iosurface_ca.py.stage-H`, `*.command.stage-D`).

## 루트 / L5 / K extreme

- **Tahoe only** (`x86.graphics.tahoe_gate.is_tahoe` / macOS 26). Sequoia+`X86_EXTREME` → 루트·L5 OVERWRITE **no-op**.
- L5-R: `26X86_L5_*` · B: `26X86_SL_*`.
- **Sweep** owns `tahoe_gate.py`; deploy agent owns app/PKG only.

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | Sweep tahoe_gate land |
| 2026-09-04 | WIP Sweep: MC docs-only; J+gate → Sweep |
| 2026-09-04 | 정식화 · H promote · L5 soft-import · Tahoe gate |
