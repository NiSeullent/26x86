# Credits

## 26x86

**26x86** — Better macOS 26 System for x86-Based Macintosh

26x86 is a community fork focused on macOS 26 (Tahoe) support for x86-based Macs, including Apple T2-equipped models. This project builds upon the work of many contributors across the OpenCore Legacy Patcher ecosystem.

- **Maintainer:** [NiSeullent](https://github.com/NiSeullent)
- **Repository:** https://github.com/NiSeullent/26x86
- **Upstream fork:** [OpenCore Legacy Patcher T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2) by [Albert Müller](https://github.com/albert-mueller/)
- **Original project:** [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher) by [Dortania](https://github.com/dortania)

---

## Fork and T2 Support

* [Albert Müller](https://github.com/albert-mueller/)
  * Main author of OpenCore Legacy Patcher T2; T2 Mac support, security fixes, and patches
* [vytska69](https://github.com/vytska69)
  * [T2 chip patches](https://github.com/vytska69/OpenCore-Legacy-Patcher)
  * [Secure Enclave Processor (SEP) timeout patches](https://github.com/vytska69/OpenCore-Legacy-Patcher)
* [nxvid](https://github.com/nxvid/OpenCore-Legacy-Patcher-T2/)
  * Documenting and fixing sbvmm injection issues on T2 Macs
* [GUTY345](https://github.com/GUTY345)
  * USB-Map.plist syntax and SMBIOS spoofing fixes on T2 Macs
  * [Graphics acceleration on Intel UHD 630](https://github.com/GUTY345/OpenCore-Legacy-patcher-t2chip-fixBugs/tree/main)
  * [macOS 26 Tahoe compatibility fixes](https://github.com/GUTY345/OpenCore-Legacy-patcher-t2chip-fixBugs/tree/main)
* [kodeaqua](https://github.com/kodeaqua)
  * MacBook Air 2018–2019 hardware research for boot issues
* [peltorio](https://github.com/peltorio/)
  * GitHub Actions macOS runner fix

---

## OpenCore Legacy Patcher (Dortania) — Core Authors

* [Acidanthera](https://github.com/Acidanthera)
  * OpenCorePkg and core kexts and tools
* [DhinakG](https://github.com/DhinakG) — Main co-author
* [Khronokernel](https://github.com/Khronokernel) — Main co-author; debugging and code contributions
* [gandolf243](https://github.com/gandolf243) — UI redesign; bug fixes and testing
* [DrDonk](https://github.com/DrDonk) — AppleKeyStore patch; testing
* [TheRaddish1313](https://github.com/TheRaddish1313) — Framebuffer and boot args fixes
* [vit9696](https://github.com/vit9696)
* [Jazzzny](https://github.com/Jazzzny) — Vaulting, GUI/backend, UEFI research, documentation
* [Mr.Macintosh](https://mrmacintosh.com) — Architecture and troubleshooting
* [mario_bros_tech](https://github.com/mariobrostech) and the Unsupported Mac Discord
  * Catalyst that started OpenCore Legacy Patcher

---

## macOS 26 / Metal / Graphics

* [EduCovas](https://github.com/covasedu)
  * [non-Metal patch set](https://github.com/moraea/non-metal-frameworks)
  * [3802 Metal patch set](https://github.com/moraea/misc-patches/tree/main/3802-Metal-15) and [MetallibSupportPkg](https://github.com/dortania/MetallibSupportPkg)
  * Metal bundle patches, IOSurface patches, legacy Wi-Fi, T1 patch set, USB 1 patch
* [ASentientBot](https://github.com/ASentientBot) / [ASentientHedgehog](https://github.com/moosethegoose2213)
  * non-Metal and Metal bundle interposer work
* [pyquick](https://github.com/pyquick) and [hackdoc](https://github.com/hackdoc)
  * [Metallib support on macOS 26](https://github.com/hackdoc/OCLP-R)
* [YBronst](https://github.com/YBronst/OCLP-Plus) — Modern wireless on macOS 26 Tahoe
* [stephandeutsch](https://github.com/stephandeutsch/OpenCore-Legacy-Patcher/) — USB 1.1 compatibility with Sequoia and Tahoe
* [Ausdauersportler](https://github.com/Ausdauersportler) — iMac Metal GPU upgrade patch set
* [flagers](https://github.com/flagersgit) — Nvidia Web Driver research; non-Metal patches

---

## Hardware, Legacy, and Utilities

* [cdf](https://github.com/cdf) — Mac Pro OpenCore patch set; [Innie](https://github.com/cdf/Innie)
* [Syncretic](https://forums.macrumors.com/members/syncretic.1173816/) — [AAAMouSSE](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/), [telemetrap](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/post-28447707), [SurPlus](https://github.com/reenigneorcim/SurPlus)
* [dosdude1](https://github.com/dosdude1) — [Original GUI](https://github.com/dortania/OCLP-GUI); legacy patcher groundwork
* [parrotgeek1](https://github.com/parrotgeek1) — [VMM Patch Set](https://github.com/dortania/OpenCore-Legacy-Patcher/blob/4a8f61a01da72b38a4b2250386cc4b497a31a839/payloads/Config/config.plist#L1222-L1281)
* [BarryKN](https://github.com/BarryKN) — Legacy patcher groundwork
* [arter97](https://github.com/arter97/) — [SimpleMSR](https://github.com/arter97/SimpleMSR/)
* [joevt](https://github.com/joevt) — [FixPCIeLinkrate](https://github.com/joevt/joevtApps)

---

## Community and Hardware Donors

* MacRumors and Unsupported Mac Communities — Testing and issue reporting
* [JohnD](https://forums.macrumors.com/members/johnd.53633/), [SpiGAndromeda](https://github.com/SpiGAndromeda), [turbomacs](https://github.com/turbomacs), [vinaypundith](https://forums.macrumors.com/members/vinaypundith.1212357/), [ThatStella7922](https://github.com/ThatStella7922), zephar, jazo97, and others who donated hardware for testing
* **Apple** — macOS and many kexts, frameworks, and binaries reimplemented into newer OSes

---

## License Acknowledgement

This product includes software developed by Dortania, OpenCore Legacy Patcher contributors, and the 26x86 project. See [LICENSE.txt](./LICENSE.txt), [NOTICE.md](./NOTICE.md), and [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md).
