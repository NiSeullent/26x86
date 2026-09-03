# Third-Party Licenses

This document lists the licenses of major third-party components used by 26x86.
Full copyright notices from upstream projects are retained in `LICENSE.txt` and `NOTICE.md`.

---

## Project Lineage

### 26x86 (this repository)

- **License:** BSD 3-Clause
- **Copyright:** Copyright (c) 2026 NiSeullent and 26x86 contributors.
- **Upstream:** Derived from OpenCore Legacy Patcher T2 and OpenCore Legacy Patcher.

### OpenCore Legacy Patcher T2

- **Repository:** https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2
- **License:** BSD 3-Clause
- **Copyright:** Copyright (c) 2020–2025 Dhinak G, Mykola Grymalyuk, and individual contributors.

### OpenCore Legacy Patcher (Dortania)

- **Repository:** https://github.com/dortania/OpenCore-Legacy-Patcher
- **License:** BSD 3-Clause (4-clause variant in upstream; 3-clause core terms apply)
- **Copyright:** Copyright (c) 2020–2025 Dhinak G, Mykola Grymalyuk, and individual contributors.

### OpenCorePkg-add-T2-support

- **Repository:** https://github.com/albert-mueller/OpenCorePkg-add-T2-support
- **License:** BSD 3-Clause
- **Copyright:**
  - Copyright (c) 2016–2017, The HermitCrabs Lab
  - Copyright (c) 2016–2020, Download-Fritz
  - Copyright (c) 2017–2020, savvas
  - Copyright (c) 2016–2020, vit9696

### PatcherSupportPkg

- **Repository:** https://github.com/hackdoc/PatcherSupportPkg
- **License:** All rights reserved to respective authors (no redistribution license file)
- **Copyright:**
  - Copyright (c) 2017–2021, Apple.inc
  - Copyright (c) 2020–2021, ASentientBot
  - Copyright (c) 2019–2021, dosdude1
  - Copyright (c) 2021, Khronokernel

### MetallibSupportPkg

- **Repository:** https://github.com/dortania/MetallibSupportPkg
- **License:** No explicit LICENSE file in the repository at time of fork; treat as all-rights-reserved unless otherwise stated by Dortania.
- **Purpose:** Metal Library (`.metallib`) patching utilities for legacy GPU support.

---

## Bootloader and Kexts (Acidanthera)

| Component | License | URL |
|-----------|---------|-----|
| OpenCorePkg | BSD 3-Clause | https://github.com/acidanthera/OpenCorePkg |
| Lilu | BSD 3-Clause | https://github.com/acidanthera/Lilu |
| WhateverGreen | BSD 3-Clause | https://github.com/acidanthera/WhateverGreen |
| AirportBrcmFixup | BSD 3-Clause | https://github.com/acidanthera/AirportBrcmFixup |
| CPUFriend | BSD 3-Clause | https://github.com/acidanthera/CPUFriend |
| RestrictEvents | BSD 3-Clause | https://github.com/acidanthera/RestrictEvents |
| FeatureUnlock | BSD 3-Clause | https://github.com/acidanthera/FeatureUnlock |
| DebugEnhancer | BSD 3-Clause | https://github.com/acidanthera/DebugEnhancer |
| CryptexFixup | BSD 3-Clause | https://github.com/acidanthera/CryptexFixup |
| NVMeFix | GPL 2.0 | https://github.com/acidanthera/NVMeFix |

---

## Other Bundled Components

| Component | License | Notes |
|-----------|---------|-------|
| Innie | BSD 3-Clause | https://github.com/cdf/Innie |
| AAAMouSSE | All rights reserved | Syncretic — closed source |
| telemetrap | All rights reserved | Syncretic — closed source |
| SurPlus | See repository | https://github.com/reenigneorcim/SurPlus |
| AMFIPass | See author | Dhinak G |
| Apple binaries (kexts, frameworks) | Apple Proprietary | Apple Inc. |
| Non-Metal / 3802 Metal patch sets | See respective authors | moraea and contributors |

For a detailed component list, see also [docs/LICENSE.md](./docs/LICENSE.md).

---

## BSD 3-Clause Summary

Redistribution and use in source and binary forms, with or without modification, are permitted provided that:

1. Redistributions of source code retain the copyright notice, conditions, and disclaimer.
2. Redistributions in binary form reproduce the copyright notice, conditions, and disclaimer in documentation.
3. Advertising materials acknowledge Dortania, OpenCore Legacy Patcher contributors, and the 26x86 project (where applicable).
4. Neither project names nor contributor names may be used for endorsement without permission.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.**

See `LICENSE.txt` for the full legal text.
