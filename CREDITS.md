# 기여자 (Credits)

## 26x86

**26x86** — x86 기반 Mac을 위한 더 나은 macOS 26 시스템

26x86은 Apple T2를 포함한 x86 Mac에서 macOS 26 (Tahoe) 지원에 초점을 맞춘 커뮤니티 포크입니다. OpenCore Legacy Patcher 생태계의 많은 기여자 작업 위에 구축되었습니다.

- **메인테이너:** [NiSeullent](https://github.com/NiSeullent)
- **저장소:** https://github.com/NiSeullent/26x86
- **업스트림 포크:** [OpenCore Legacy Patcher T2](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2) — [Albert Müller](https://github.com/albert-mueller/)
- **원본 프로젝트:** [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher) — [Dortania](https://github.com/dortania)
- **원본 저장소 전체 목록:** [docs/wiki/Upstream-Repositories.md](docs/wiki/Upstream-Repositories.md) (56개 GitHub 저장소 + 비-GitHub 출처)

### 26x86 의존성 포크

| 26x86 포크 | 업스트림 |
|------------|----------|
| [NiSeullent/26x86-OpenCorePkg](https://github.com/NiSeullent/26x86-OpenCorePkg) | [albert-mueller/OpenCorePkg-add-T2-support](https://github.com/albert-mueller/OpenCorePkg-add-T2-support) → [acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) |
| [NiSeullent/26x86-PatcherSupportPkg](https://github.com/NiSeullent/26x86-PatcherSupportPkg) | [hackdoc/PatcherSupportPkg](https://github.com/hackdoc/PatcherSupportPkg) |
| [NiSeullent/26x86-MetallibSupportPkg](https://github.com/NiSeullent/26x86-MetallibSupportPkg) | [dortania/MetallibSupportPkg](https://github.com/dortania/MetallibSupportPkg) |

---

## 포크 및 T2 지원

* [Albert Müller](https://github.com/albert-mueller/) — OCLP-T2 주 저자; T2 지원·보안 수정·패치
* [vytska69](https://github.com/vytska69) — [T2 칩 패치](https://github.com/vytska69/OpenCore-Legacy-Patcher), [SEP 타임아웃 패치](https://github.com/vytska69/OpenCore-Legacy-Patcher)
* [nxvid](https://github.com/nxvid/OpenCore-Legacy-Patcher-T2/) — T2 Mac sbvmm 주입 이슈 문서화·수정
* [GUTY345](https://github.com/GUTY345) — USB-Map.plist, SMBIOS 스푸핑, [UHD 630 그래픽](https://github.com/GUTY345/OpenCore-Legacy-patcher-t2chip-fixBugs/tree/main), [macOS 26 호환 수정](https://github.com/GUTY345/OpenCore-Legacy-patcher-t2chip-fixBugs/tree/main)
* [kodeaqua](https://github.com/kodeaqua) — MacBook Air 2018–2019 부팅 이슈 하드웨어 조사
* [peltorio](https://github.com/peltorio/) — GitHub Actions macOS runner 수정

---

## OpenCore Legacy Patcher (Dortania) — 핵심 저자

* [Acidanthera](https://github.com/Acidanthera) — OpenCorePkg 및 핵심 kext·도구
* [DhinakG](https://github.com/DhinakG) — 공동 주 저자
* [Khronokernel](https://github.com/Khronokernel) — 공동 주 저자; 디버깅·코드 기여
* [gandolf243](https://github.com/gandolf243) — UI 재설계; 버그 수정·테스트
* [DrDonk](https://github.com/DrDonk) — AppleKeyStore 패치; 테스트
* [TheRaddish1313](https://github.com/TheRaddish1313) — Framebuffer·boot args 수정
* [vit9696](https://github.com/vit9696)
* [Jazzzny](https://github.com/Jazzzny) — Vaulting, GUI/백엔드, UEFI 연구, 문서
* [Mr.Macintosh](https://mrmacintosh.com) — 아키텍처·트러블슈팅
* [mario_bros_tech](https://github.com/mariobrostech) 및 Unsupported Mac Discord — OCLP 시작 계기

---

## macOS 26 / Metal / 그래픽

* [EduCovas](https://github.com/covasedu) — [non-Metal](https://github.com/moraea/non-metal-frameworks), [3802 Metal](https://github.com/moraea/misc-patches/tree/main/3802-Metal-15), [MetallibSupportPkg](https://github.com/dortania/MetallibSupportPkg), IOSurface·Wi-Fi·T1·USB 1 패치
* [ASentientBot](https://github.com/ASentientBot) / [ASentientHedgehog](https://github.com/moosethegoose2213) — non-Metal·Metal bundle interposer
* [pyquick](https://github.com/pyquick), [hackdoc](https://github.com/hackdoc) — [macOS 26 Metallib](https://github.com/hackdoc/OCLP-R)
* [YBronst](https://github.com/YBronst/OCLP-Plus) — Tahoe 모던 무선
* [stephandeutsch](https://github.com/stephandeutsch/OpenCore-Legacy-Patcher/) — USB 1.1 (Sequoia/Tahoe)
* [Ausdauersportler](https://github.com/Ausdauersportler) — iMac Metal GPU 업그레이드
* [flagers](https://github.com/flagersgit) — Nvidia Web Driver·non-Metal

---

## 하드웨어·레거시·유틸리티

* [cdf](https://github.com/cdf) — Mac Pro 패치; [Innie](https://github.com/cdf/Innie)
* [Syncretic](https://forums.macrumors.com/members/syncretic.1173816/) — [AAAMouSSE](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/), [telemetrap](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/post-28447707), [SurPlus](https://github.com/reenigneorcim/SurPlus)
* [dosdude1](https://github.com/dosdude1) — [원 GUI](https://github.com/dortania/OCLP-GUI)
* [parrotgeek1](https://github.com/parrotgeek1) — [VMM Patch Set](https://github.com/dortania/OpenCore-Legacy-Patcher/blob/4a8f61a01da72b38a4b2250386cc4b497a31a839/payloads/Config/config.plist#L1222-L1281)
* [BarryKN](https://github.com/BarryKN), [arter97](https://github.com/arter97/) — [SimpleMSR](https://github.com/arter97/SimpleMSR/)
* [joevt](https://github.com/joevt) — [FixPCIeLinkrate](https://github.com/joevt/joevtApps)

---

## 커뮤니티·하드웨어 기증

* MacRumors·Unsupported Mac 커뮤니티 — 테스트·이슈 보고
* [JohnD](https://forums.macrumors.com/members/johnd.53633/), [SpiGAndromeda](https://github.com/SpiGAndromeda), [turbomacs](https://github.com/turbomacs), [vinaypundith](https://forums.macrumors.com/members/vinaypundith.1212357/), [ThatStella7922](https://github.com/ThatStella7922), zephar, jazo97 등 하드웨어 기증
* **Apple** — macOS 및 kext·프레임워크

---

## 라이선스·원본 고지

This product includes software developed by Dortania, OpenCore Legacy Patcher contributors, and the 26x86 project.

| 문서 | 설명 |
|------|------|
| [Upstream-Repositories.md](docs/wiki/Upstream-Repositories.md) | OCLP, OCLP-T2, Acidanthera, moraea 등 **원본 저장소 전체** (56개) |
| [NOTICE.md](./NOTICE.md) | 법적 고지·저작권 표 |
| [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) | 서드파티 라이선스 전문·링크 |
| [LICENSE.txt](./LICENSE.txt) | 26x86 BSD 3-Clause |
