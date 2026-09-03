# 26x86 Wiki (English Index)

> **Korean is the primary documentation language.** Wiki pages are written in **Korean**. This page is an English navigation index only.

## Wiki home (Korean)

[Home.md](./Home.md) — full table of contents, CLI quick start

## Key pages

| Page | Topic |
|------|--------|
| [Warnings.md](./Warnings.md) | All cautions: C2D, GPU, T2 SIP, Hackintosh, 26x86 settings notes |
| [Configuration.md](./Configuration.md) | `config.json`, `com.niseullent.26x86`, launchd |
| [Migration-from-OCLP.md](./Migration-from-OCLP.md) | 이전 패처에서 26x86으로 전환 |
| [Known-Issues.md](./Known-Issues.md) | T2 progress, known bugs |
| [Disclaimer.md](./Disclaimer.md) | Disclaimer summary → [DISCLAIMER.md](../../DISCLAIMER.md) |
| [GPU-Limitations.md](./GPU-Limitations.md) | Metal 8302, Non-Metal |
| [T2-Mac-Notes.md](./T2-Mac-Notes.md) | T2-specific notes |
| [Installation-Notes.md](./Installation-Notes.md) | Clean install |
| [Orphan-Files-Archive.md](./Orphan-Files-Archive.md) | Archived orphan files |

## Architecture

- [ARCHITECTURE-26x86.md](../ARCHITECTURE-26x86.md) — `x86/` package, JSON settings, wizard-first CLI (Korean)

## Project docs (English supplements)

- [docs/README.en.md](../README.en.md) — project overview
- [docs/SETUP.en.md](../SETUP.en.md) — dev setup
- [docs/KOREAN_EDITION.md](../KOREAN_EDITION.md) — edition notes (EN + KO)

## CLI (reference)

```bash
python -m x86 wizard    # recommended entry
python -m x86 detect --json
python -m x86 build
python -m x86 patch
python -m x86 status
```

## Status

Experimental alpha — read warnings before use. Last major target: **macOS 26 Tahoe** on x86 Macs (including T2).
