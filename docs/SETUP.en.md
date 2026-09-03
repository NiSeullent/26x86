# 26x86 Development Setup (English)

> **Korean-Optimized Edition / 한글판 최적화** — The canonical setup guide is in Korean: [SETUP (workspace)](../../docs/SETUP.md) — Korean canonical guide in monorepo. This file is an English summary for international contributors.

## Directory layout

```
~/Desktop/26x86/
├── 26x86/                      # Main patcher (Python GUI/CLI)
├── 26x86-MetallibSupportPkg/
├── 26x86-PatcherSupportPkg/
├── 26x86-OpenCorePkg/
├── .venv/                      # Local Python venv (not committed)
├── scripts/
├── docs/
└── vm/
```

## Quick start

```bash
cd ~/Desktop/26x86
bash scripts/setup-dev.sh
source .venv/bin/activate
cd 26x86
python3 OpenCore-Patcher-GUI.command
```

## Requirements

| Item | Notes |
|------|--------|
| macOS | 15.x (Sequoia) or newer recommended |
| Python | **3.13+** from python.org or `uv python install 3.13` |
| Xcode CLT | `xcode-select --install` |
| Git | required |
| gh CLI | optional, for GitHub |

## Korean UI default

- The **GUI wizard** uses Korean strings (`opencore_legacy_patcher/wizard/strings.py`).
- **CLI** help defaults to Korean; use `--lang en` for English help:
  ```bash
  python3 OpenCore-Patcher-GUI.command --lang en --help
  ```

## Building OpenCore / support forks

Use workspace scripts under `scripts/` (see Korean [SETUP (workspace)](../../docs/SETUP.md) — Korean canonical guide in monorepo for full commands): `setup-dev.sh`, `build-opencore.sh`.

## VM testing

See [../vm/README.md](../vm/README.md) (Korean) or UTM docs. Real hardware validation is still required for T2 and GPU patches.

## Secrets

Copy `.env.example` to `.env` locally; **never commit `.env`**.
