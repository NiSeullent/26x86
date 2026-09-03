# 26x86 — Korean-Optimized Edition

> **This is the Korean-optimized edition (*한글판 최적화*) of 26x86.**  
> Primary documentation is in Korean. This page is an English overview for international users and contributors.

## What is 26x86?

**26x86** — *Better macOS 26 System for x86-Based Macintosh*

A community fork focused on running **macOS 26 Tahoe** on Intel (x86) Macs, including experimental **T2 Mac** support. Built on [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) and [Lilu](https://github.com/acidanthera/Lilu).

Fork lineage:
- [OpenCore Legacy Patcher T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2) (Albert Müller)
- Rebranded and maintained as [NiSeullent/26x86](https://github.com/NiSeullent/26x86)

## Korean-Optimized Features

- **Wizard GUI** — 5-step Korean UI for non-technical users
- **CLI** — Full terminal control with `--lang ko` / `--lang en`
- **Docs** — Korean-first (`README.md`, `DISCLAIMER.md`, `docs/SETUP.md`)

See [KOREAN_EDITION.md](./KOREAN_EDITION.md) for details.

## Quick Start (English)

```bash
git clone https://github.com/NiSeullent/26x86.git
cd 26x86
pip3 install -r requirements.txt   # Python 3.13+ required
python3 OpenCore-Patcher-GUI.command --help
python3 OpenCore-Patcher-GUI.command --detect
```

Full dev setup: [SETUP.en.md](./SETUP.en.md)  
Korean setup guide: [SETUP.md](./SETUP.md)

## ⚠️ Disclaimer

Experimental alpha software. Read [DISCLAIMER.md](../26x86/DISCLAIMER.md) (Korean) before use. Backup all data. Test on spare hardware only.

Known limits on macOS 26:
- Core 2 Duo Macs: cannot boot (AAAMouSSE / telemetrap)
- Metal 8302 (2012–2014) / Non-Metal (2011): GPU patches incomplete
- T2 Macs: SIP disabled; desktop not yet reachable in alpha

## Related Repos (NiSeullent forks)

| Repo | Purpose |
|------|---------|
| [26x86-OpenCorePkg](https://github.com/NiSeullent/26x86-OpenCorePkg) | OpenCore with T2 support |
| [26x86-PatcherSupportPkg](https://github.com/NiSeullent/26x86-PatcherSupportPkg) | Patch binaries / DMGs |
| [26x86-MetallibSupportPkg](https://github.com/NiSeullent/26x86-MetallibSupportPkg) | Metal library patches |

## License

BSD 3-Clause — see [LICENSE.txt](../26x86/LICENSE.txt), [NOTICE.md](../26x86/NOTICE.md), [THIRD_PARTY_LICENSES.md](../26x86/THIRD_PARTY_LICENSES.md).
