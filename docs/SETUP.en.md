# 26x86 Development Setup (English)

> **Korean-Optimized Edition** — GUI and primary docs default to Korean. Use `--lang en` for English CLI help.

## Workspace Layout

```
26x86/                      # Main patcher (this repo)
26x86-MetallibSupportPkg/   # Metal library patches
26x86-PatcherSupportPkg/    # Universal binaries
26x86-OpenCorePkg/          # OpenCore bootloader fork
```

## Requirements

| Item | Version |
|------|---------|
| macOS host | 15.x+ recommended |
| Python | **3.13+** (not Xcode bundled 3.9) |
| Xcode CLT | For native OpenCore builds |

## One-Shot Setup

```bash
git clone https://github.com/NiSeullent/26x86.git
cd ..   # parent workspace
bash scripts/setup-dev.sh   # if using full workspace clone
```

## Manual Setup

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.13
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r 26x86/requirements.txt
```

With PyInstaller bootloader rebuild:

```bash
PYINSTALLER_COMPILE_BOOTLOADER=1 pip install --no-binary pyinstaller -r 26x86/requirements.txt
```

## Run

```bash
cd 26x86
python3 OpenCore-Patcher-GUI.command              # Korean wizard GUI (default)
python3 OpenCore-Patcher-GUI.command --advanced_gui
python3 OpenCore-Patcher-GUI.command --lang en --help
python3 OpenCore-Patcher-GUI.command --detect --json
python3 OpenCore-Patcher-GUI.command --build --model iMac11,2
```

## Build OpenCore

```bash
cd 26x86-OpenCorePkg
./build_oc.tool
# Copy OpenCore-RELEASE.zip to 26x86/payloads/OpenCore/
```

## Korean Documentation

- [SETUP.md](./SETUP.md) — Full Korean setup guide
- [KOREAN_EDITION.md](./KOREAN_EDITION.md) — What “Korean-optimized” means
