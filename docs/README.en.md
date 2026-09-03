# 26x86 — Project Overview (English)

> **Korean-Optimized Edition / 한글판 최적화**
>
> This repository is maintained primarily for Korean-speaking users. User-facing documentation, the setup wizard, and CLI help default to **Korean**. These English pages are **supplementary**.

## What is 26x86?

**26x86** is an experimental community fork focused on **macOS 26 Tahoe** (and related releases) on **x86-based Macs**, including Apple **T2** models. It builds on [OpenCore Legacy Patcher T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2) and Dortania’s [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher).

- **Main repo:** https://github.com/NiSeullent/26x86
- **Maintainer:** NiSeullent
- **Status:** Experimental alpha — read [DISCLAIMER](../DISCLAIMER.md) before use

## Documentation map

| Document | Language | Path |
|----------|----------|------|
| Main README | Korean | [README.md](../README.md) |
| **Wiki home** | Korean | [wiki/Home.md](./wiki/Home.md) |
| **Architecture** | Korean + EN summary | [ARCHITECTURE-26x86.md](./ARCHITECTURE-26x86.md) |
| Configuration | Korean + EN summary | [wiki/Configuration.md](./wiki/Configuration.md) |
| OCLP migration | Korean + EN summary | [wiki/Migration-from-OCLP.md](./wiki/Migration-from-OCLP.md) |
| Build from source | Korean | [SOURCE.md](../SOURCE.md) |
| Dev environment | Korean | [SETUP.md](./SETUP.md) |
| This overview | English | README.en.md |
| Setup guide | English | [SETUP.en.md](./SETUP.en.md) |
| Edition notes | EN + KO | [KOREAN_EDITION.md](./KOREAN_EDITION.md) |
| English wiki index | English | [wiki/README.en.md](./wiki/README.en.md) |

## Quick links

- Releases: https://github.com/NiSeullent/26x86/releases
- Security: https://github.com/NiSeullent/26x86/security/policy
- Dortania OCLP guide (upstream, English): https://dortania.github.io/OpenCore-Legacy-Patcher/

## Workspace layout

The parent folder `26x86/` (Desktop workspace) may contain forked support packages (`26x86-OpenCorePkg`, `26x86-PatcherSupportPkg`, `26x86-MetallibSupportPkg`), scripts, and VM templates. See [SETUP.en.md](./SETUP.en.md).
