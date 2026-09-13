# 26x86 — Meta Repository

This repository assembles the public 26x86 (NextCore) project from independently versioned submodules.

## Repository Structure

```text
26x86/
├── README.md               # This file
├── LICENSE.txt             # Primary license
├── .gitignore
├── .gitmodules
├── docs/                  # Public documentation (mkdocs)
│   └── wiki/              # Wiki source
├── x86/                   # Core patcher engine
├── gui-tauri/             # GUI client (Tauri)
├── payload/               # OpenCore payloads (generated, ignored)
├── Tools/                 # Build and validation tools
├── vendor/               # Vendored dependencies
├── tests/                # Test suite
├── ci_tooling/           # [REMOVED - private/internal] → zuzunza private repo
└── research/             # [REMOVED - private/research] → zuzunza private repo
```

## Submodules

Currently included as submodules:
- `nextcore/crates/nextcore-core`     → [26x86/Nextcore-Core](https://github.com/26x86/Nextcore-Core)
- `nextcore/crates/nextcore-efi`      → [26x86/Nextcore-EFI](https://github.com/26x86/Nextcore-EFI)
- `nextcore/crates/nextcore-ise`      → [26x86/Nextcore-ISE](https://github.com/26x86/Nextcore-ISE)
- `nextcore/crates/nextcore-gpu`      → [26x86/Nextcore-GPU](https://github.com/26x86/Nextcore-GPU)
- `nextcore/crates/nextcore-hal`      → [26x86/Nextcore-HAL](https://github.com/26x86/Nextcore-HAL)
- `nextcore/crates/nextcore-apls`     → [26x86/Nextcore-APLS](https://github.com/26x86/Nextcore-APLS)
- `nextcore/crates/nextcore-tool`     → [26x86/Nextcore-Tool](https://github.com/26x86/Nextcore-Tool)

### Cloning with submodules

```bash
git clone --recurse-submodules https://github.com/26x86/26x86.git
```

## Private Content

Sensitive research, reverse-engineering evidence, internal build tooling, and CI signing credentials are stored in **private repositories** hosted on `zuzunza` (SSH-only, no HTTP/HTTPS access):

```text
ssh zuzunza
/srv/git/
├── 26x86-research.git     # research/, _isolated/
├── 26x86-internal.git     # ci_tooling/, Build-Project.command
└── 26x86-artifacts.git    # nextcore/artifacts/, validation receipts
```

## License

See [LICENSE.txt](LICENSE.txt) and [NOTICE.md](NOTICE.md).
