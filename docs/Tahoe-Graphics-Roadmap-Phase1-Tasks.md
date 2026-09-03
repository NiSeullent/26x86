# Tahoe 그래픽 R&D — Phase 1 실행 태스크

> **기간:** 1–2주 (Layer A)  
> **선행 문서:** [Tahoe-Graphics-Roadmap.md](./Tahoe-Graphics-Roadmap.md)  
> **작성일:** 2026-09-04  
> **태스크 수:** 22

---

## 사용법

| 필드 | 설명 |
|------|------|
| **ID** | `A-XX` = Layer A, `X-XX` = 교차/인프라 |
| **우선순위** | P0 (차단) → P3 (개선) |
| **상태** | `todo` / `doing` / `done` / `blocked` |
| **의존성** | 선행 태스크 ID |
| **산출물** | PR·파일·로그 경로 |

**범례 — 구현 vs 문서:**

- 🟢 **코드** — 저장소 변경
- 📄 **문서** — 문서·wiki만
- 🧪 **실기** — spare Mac 필요

---

## Week 0 — 인프라·진단 (Day 1–3)

### A-01 🧪 Pre-AVX CPU 진단 스크립트 배포

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `done` |
| **의존성** | — |
| **설명** | Westmere 등 AVX 미지원 CPU 자동 식별 |
| **파일/도구** | `Tools/detect_cpu_avx.command` |
| **실행** | 더블클릭 또는 `bash Tools/detect_cpu_avx.command` |
| **완료 조건** | `~/Desktop/CPU-AVX-Report-*` 에 `PRE_AVX=1/0` 기록 |
| **Fallback** | 수동 `sysctl hw.optional.avx1_0` |

---

### A-02 📄 GPU 클래스 ↔ SMBIOS 매핑 테이블

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `todo` |
| **의존성** | — |
| **설명** | Metal 3802 / 31001 / 8302(Wiki) / Non-Metal 모델 매핑 고정 |
| **파일/도구** | `docs/wiki/GPU-Model-Matrix.md` (신규), [device_probe.py](../opencore_legacy_patcher/detections/device_probe.py) |
| **참고 URL** | [OCLP-T2 Wiki Metal 8302](https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/wiki), [RESEARCH_INVENTORY](./RESEARCH_INVENTORY.md) |
| **PoC** | MacPro5,1 + Kepler / MacBookPro11,1 + Iris → detect 로그 대조 |
| **완료 조건** | ≥30 SMBIOS 행, GPU subclass 열 포함 |
| **Fallback** | RESEARCH_SUMMARY 표만 인용 |

---

### A-03 🧪 그래픽 진단 확장 (Pre-AVX 필드)

| | |
|---|---|
| **우선순위** | P1 |
| **상태** | `todo` |
| **의존성** | A-01 |
| **설명** | `collect_graphics_diagnostics.command`에 AVX·revpatch·Metallib 경로 추가 |
| **파일/도구** | `Tools/collect_graphics_diagnostics.command` |
| **완료 조건** | 출력 zip에 `cpu_avx.txt`, `metallib_path.txt` 포함 |
| **Fallback** | A-01 리포트 별도 첨부 |

---

### A-04 📄 Known-good SIP/AMFI/boot-args 시트

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `todo` |
| **의존성** | — |
| **설명** | Non-T2 Pre-AVX / T2 / 3802 Extended 시나리오별 NVRAM·csr 값 문서화 |
| **파일/도구** | `docs/wiki/Tahoe-Known-Good-Security.md` (신규), [detect.py](../opencore_legacy_patcher/sys_patch/patchsets/detect.py), [sip_data](../opencore_legacy_patcher/datasets/sip_data.py) |
| **참고** | [Roadmap § A-4](./Tahoe-Graphics-Roadmap.md#a-4-boot-args--amfi--sip-known-good-조합) |
| **PoC** | 각 시나리오 1회 루트패치 성공 스크린샷 + `csrutil status` |
| **완료 조건** | 4 시나리오 × 검증 체크리스트 |
| **Fallback** | Dortania POST-INSTALL 링크 |

---

## Week 1 — Safari26 Pre-AVX (Day 4–7)

### A-05 🟢 RestrictEvents 1.1.7+ vendoring

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `done` — [cf7f26f](https://github.com/NiSeullent/26x86/commit/cf7f26f) |
| **의존성** | A-04 |
| **설명** | JavaScriptCore pre-AVX 패치 포함 RestrictEvents 번들 |
| **파일/도구** | `payloads/Kexts/Update-Kexts.command`, [constants.py](../opencore_legacy_patcher/constants.py) `restrictevents_version`, [config.plist](../payloads/Config/config.plist) |
| **참고 URL** | [RestrictEvents Actions](https://github.com/acidanthera/RestrictEvents/actions) — "JavaScriptCore patches for pre-AVX CPUs" artifact; [Safari26-PreAVX-Fix](https://ptrix01.github.io/) |
| **PoC** | MacPro5,1 EFI 빌드 → `kextstat RestrictEvents` ≥1.1.7 |
| **완료 조건** | CI kext zip checksum pinned in CHANGELOG |
| **Fallback** | 사용자 수동 nightly 다운로드 가이드 (문서) |

---

### A-06 🟢 Pre-AVX `revpatch=jsc` 자동 주입

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `done` — [cf7f26f](https://github.com/NiSeullent/26x86/commit/cf7f26f) |
| **의존성** | A-05, A-01 |
| **설명** | `hw.optional.avx1_0=0` 시 `revpatch`에 `jsc` 추가 |
| **파일/도구** | [efi_builder/misc.py](../opencore_legacy_patcher/efi_builder/misc.py) `_re_generate_patch_arguments()`, [device_probe.py](../opencore_legacy_patcher/detections/device_probe.py) CPU flags |
| **PoC** | MacPro5,1 `nvram 4D1FDA02-...:revpatch` → `sbvmm,jsc` (또는 `jsc` 단독 테스트) |
| **완료 조건** | Safari 26 — 10 페이지 연속 로드 |
| **Fallback** | A-07 JIT LaunchDaemon |

---

### A-07 🟢 JSC JIT disable LaunchDaemon (2차 방어)

| | |
|---|---|
| **우선순위** | P1 |
| **상태** | `todo` |
| **의존성** | A-06 |
| **설명** | `JSC_useJIT` / `__XPC_JSC_useJIT` false 영구 설정 |
| **파일/도구** | `payloads/Plists/com.26x86.disable-jsc-jit.plist` (신규), 루트패치 `PatchType` plist 설치 |
| **참고 URL** | [MacRumors 2445415](https://forums.macrumors.com/threads/opencore-legacy-patcher-2-2-0-on-mac-pro-5-1-issue-with-safari-and-app-store-after-upgrading-on-macos-15-2.2445415/) |
| **PoC** | `launchctl getenv JSC_useJIT` → `false` after login |
| **완료 조건** | A-06 실패 시에도 Safari usable (성능 저하 허용) |
| **Fallback** | 사용자 수동 `launchctl setenv` |

---

### A-08 📄 Safari26-PreAVX-Fix 통합 가이드 (한국어)

| | |
|---|---|
| **우선순위** | P1 |
| **상태** | `todo` |
| **의존성** | A-05, A-06 |
| **설명** | End-user troubleshooting — Safari "a problem repeatedly occurred" |
| **파일/도구** | `docs/wiki/Safari-PreAVX-Tahoe.md` (신규) |
| **완료 조건** | 증상·원인·3단계 fix·fallback 브라우저 |
| **Fallback** | ptrix01.github.io 링크 |

---

## Week 1 — Metallib & GPU 분기 (Day 5–10)

### A-09 🟢 MetallibSupportPkg manifest 빌드 검증

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `todo` |
| **의존성** | A-04 |
| **설명** | Tahoe 빌드별 `.metallib` PKG 다운로드·설치 E2E |
| **파일/도구** | [metallib_handler.py](../opencore_legacy_patcher/support/metallib_handler.py), [manifest.py](../x86/manifest.py) `URL_METALLIB_SUPPORT_PKG`, 외부 `26x86-MetallibSupportPkg` |
| **PoC** | `26A5425a` host → PKG 설치 → `/Library/Application Support/26x86/MetallibSupportPkg` |
| **완료 조건** | `MetalLibraryObject.success == True` 로그 |
| **Fallback** | pyquick manifest mirror |

---

### A-10 🧪 Metal 3802 패치셋 Tahoe 스모크 테스트

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `todo` |
| **의존성** | A-09, A-02 |
| **설명** | Kepler/Ivy/Haswell 1대 이상 — 루트패치 + 재부팅 |
| **파일/도구** | [metal_3802.py](../opencore_legacy_patcher/sys_patch/patchsets/shared_patches/metal_3802.py), KDK [KdkSupportPkg](https://github.com/dortania/KdkSupportPkg) |
| **PoC** | `OpenCore-Legacy-Patcher.plist`에 `Metal 3802 Common` |
| **완료 조건** | WindowServer 120s 내 기동, 패닉 0 |
| **Fallback** | 3802 패치 skip + safe boot |

---

### A-11 🧪 Metal 31001 분기 검증 (GCN/Skylake)

| | |
|---|---|
| **우선순위** | P1 |
| **상태** | `todo` |
| **의존성** | A-02, A-10 |
| **설명** | 31001 vs 3802 동시 GPU strip 로직 확인 |
| **파일/도구** | [detect.py](../opencore_legacy_patcher/sys_patch/patchsets/detect.py) `_strip_incompatible_hardware()`, [metal_31001.py](../opencore_legacy_patcher/sys_patch/patchsets/shared_patches/metal_31001.py) |
| **PoC** | MacPro6,1 dual GPU 또는 Skylake iMac |
| **완료 조건** | 로그에 strip 메시지 + 단일 subclass 패치 |
| **Fallback** | 수동 GPU 선택 (developer mode) |

---

### A-12 🧪 Non-Metal Tahoe 가드 회귀 테스트

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `todo` |
| **의존성** | A-02 |
| **설명** | Non-Metal 패치 **미주입** 확인 — 패닉 방지 |
| **파일/도구** | [non_metal.py](../opencore_legacy_patcher/sys_patch/patchsets/shared_patches/non_metal.py) L29–34 |
| **PoC** | MacBookPro8,2 / Tesla GPU — detect → patches `{}` |
| **완료 조건** | 부팅 성공 + plist에 Non-Metal 항목 없음 |
| **Fallback** | — (가드 유지 필수) |

---

### A-13 📄 GPU 패치 분기 decision tree

| | |
|---|---|
| **우선순위** | P2 |
| **상태** | `todo` |
| **의존성** | A-10, A-11, A-12 |
| **설명** | detect → patchset 흐름 mermaid + FAQ |
| **파일/도구** | `docs/wiki/GPU-Patch-Decision-Tree.md` (신규) |
| **완료 조건** | 4 GPU 클래스 × Tahoe/Sequoia 열 |
| **Fallback** | Roadmap mermaid 인용 |

---

## Week 2 — 자동화 & EFI (Day 8–14)

### A-14 🟢 `settings.py` Pre-AVX 프로파일 키

| | |
|---|---|
| **우선순위** | P1 |
| **상태** | `todo` |
| **의존성** | A-01 |
| **설명** | JSON 설정에 pre-AVX 관련 플래그 추가 |
| **파일/도구** | [x86/settings.py](../x86/settings.py) `DEFAULT_SETTINGS` |
| **제안 키** | `pre_avx_profile: "auto"`, `safari_jit_disable: false`, `force_revpatch_jsc: true` |
| **완료 조건** | SettingsStore read/write 단위 테스트 (수동) |
| **Fallback** | 하드코드 detect |

---

### A-15 🟢 auto-patcher Pre-AVX 분기

| | |
|---|---|
| **우선순위** | P1 |
| **상태** | `todo` |
| **의존성** | A-14, A-06 |
| **설명** | 자동 루트패치 시 Pre-AVX 경고 + 권장 패치셋 |
| **파일/도구** | [auto_patcher/start.py](../opencore_legacy_patcher/sys_patch/auto_patcher/start.py), [HardwarePatchsetDetection](../opencore_legacy_patcher/sys_patch/patchsets/detect.py) |
| **PoC** | OS 업데이트 후 스냅샷 intact → GUI auto-patch 프롬프트 |
| **완료 조건** | Pre-AVX Mac에서 Metallib+3802+RestrictEvents 체크리스트 표시 |
| **Fallback** | 수동 Root Patcher |

---

### A-16 🟢 NoAVX APFS kext EFI 검증 (Mac Pro)

| | |
|---|---|
| **우선순위** | P1 |
| **상태** | `todo` |
| **의존성** | A-04 |
| **설명** | Westmere Mac Pro APFS 부팅용 NoAVX zlib kext |
| **파일/도구** | [firmware.py](../opencore_legacy_patcher/efi_builder/firmware.py), `payloads/Kexts/Misc/NoAVXFSCompressionTypeZlib-*`, [config.plist](../payloads/Config/config.plist) |
| **PoC** | `ioreg | grep NoAVXCompressionTypeZlib` |
| **완료 조건** | APFS root mount 성공 (Pre-AVX CPU) |
| **Fallback** | HFS+ 테스트 볼륨 (비권장) |

---

### A-17 🧪 PatcherSupportPkg 2.0.0 DMG E2E

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `todo` |
| **의존성** | — |
| **설명** | Universal-Binaries.dmg 마운트 → kext resolve |
| **파일/도구** | [payload_manager.py](../x86/patch/payload_manager.py), [dmg_mount.py](../opencore_legacy_patcher/sys_patch/utilities/dmg_mount.py) |
| **PoC** | `PayloadManager().mount_support_pkg()` → `resolve_kext("WhateverGreen.kext")` |
| **완료 조건** | 오프라인 bundled DMG + 온라인 download dual path |
| **Fallback** | 수동 hdiutil mount |

---

### A-18 🟢 developer mode GPU unlock 문서화

| | |
|---|---|
| **우선순위** | P2 |
| **상태** | `todo` |
| **의존성** | A-12 |
| **설명** | `~/.26x86_developer` — Non-Metal Tahoe 실험 패치 (위험) |
| **파일/도구** | [base.py](../opencore_legacy_patcher/sys_patch/patchsets/hardware/base.py) `_26x86_internal_check()` |
| **완료 조건** | wiki 경고 + enable/disable 절차 |
| **Fallback** | — |

---

## Week 2 — QA & 릴리스 (Day 12–14)

### A-19 🧪 Phase 1 통합 테스트 매트릭스

| | |
|---|---|
| **우선순위** | P0 |
| **상태** | `todo` |
| **의존성** | A-05–A-17 |
| **설명** | 최소 3 spare Mac × 시나리오 실행 |
| **매트릭스** | |

| # | Mac | CPU AVX | GPU | 테스트 |
|---|-----|---------|-----|--------|
| 1 | MacPro5,1 | ❌ | Kepler 3802 | A-05–07, A-10, A-16 |
| 2 | MacPro6,1 | ✅ | GCN 31001 | A-09, A-11 |
| 3 | MacBookPro8,2 | ✅ | Non-Metal | A-12 |

| **산출물** | `docs/test-reports/Phase1-YYYY-MM-DD.md` |
| **완료 조건** | 3/3 시나리오 결과表 + known failures |
| **Fallback** | 1/3 + VM 문서 |

---

### A-20 📄 CHANGELOG Phase 1 섹션

| | |
|---|---|
| **우선순위** | P1 |
| **상태** | `todo` |
| **의존성** | A-19 |
| **설명** | 사용자 facing 변경 요약 |
| **파일/도구** | [CHANGELOG.md](../CHANGELOG.md) |
| **완료 조건** | RestrictEvents·Pre-AVX·Metallib 항목 |
| **Fallback** | GitHub Release notes only |

---

### A-21 📄 wiki Known-Issues / GPU-Limitations 갱신

| | |
|---|---|
| **우선순위** | P2 |
| **상태** | `todo` |
| **의존성** | A-19 |
| **설명** | Phase 1 결과 반영 |
| **파일/도구** | [Known-Issues.md](./wiki/Known-Issues.md), [GPU-Limitations.md](./wiki/GPU-Limitations.md) |
| **완료 조건** | Pre-AVX Safari ✅ / Non-Metal Tahoe ⏳ 상태 |
| **Fallback** | — |

---

### A-22 📄 Layer B 킥오프 — WindowServer AVX 스캔 계획

| | |
|---|---|
| **우선순위** | P2 |
| **상태** | `todo` |
| **의존성** | A-19 |
| **설명** | Phase 2 진입 조건·첫 PoC 태스크 정의 |
| **파일/도구** | Roadmap Layer B-1, `otool`/Hopper on Tahoe WindowServer |
| **완료 조건** | `docs/Tahoe-Graphics-Roadmap-Phase2-Tasks.md` outline (5+ tasks) |
| **Fallback** | Roadmap Layer B만 유지 |

---

## 교차 태스크 (인프라)

### X-01 🟢 CI: kext checksum pin

| | |
|---|---|
| **우선순위** | P2 |
| **상태** | `todo` |
| **의존성** | A-05 |
| **파일** | `.github/workflows/` 또는 `payloads/Kexts/Update-Kexts.command` |
| **완료 조건** | RestrictEvents SHA256 in repo metadata |

---

### X-02 📄 RESEARCH_INVENTORY Safari26 항목 추가

| | |
|---|---|
| **우선순위** | P3 |
| **상태** | `todo` |
| **의존성** | A-08 |
| **파일** | [RESEARCH_INVENTORY.md](./RESEARCH_INVENTORY.md) |
| **완료 조건** | ptrix01, RestrictEvents jsc, WebKit#292 행 |

---

## Phase 1 Gantt (요약)

```
Day:  1  2  3  4  5  6  7  8  9 10 11 12 13 14
      A01 A02 A03 A04
          A05 A06 A07 A08
              A09 A10 A11 A12 A13
                      A14 A15 A16 A17 A18
                              A19 A20 A21 A22
```

---

## 완료 정의 (Phase 1 Exit Criteria)

- [ ] **P0 태스크 전부** `done` 또는 documented `blocked` + fallback
- [ ] MacPro5,1: Safari 26 usable (A-06 or A-07)
- [ ] Metal 3802: 1+ 실기 스모크 (A-10)
- [ ] Non-Metal: Tahoe 가드 유지 확인 (A-12)
- [ ] Known-good security sheet published (A-04)
- [ ] 통합 테스트 리포트 (A-19)

---

## 이미 완료된 항목

| ID | 산출물 | 비고 |
|----|--------|------|
| A-01 | `Tools/detect_cpu_avx.command` | Phase 1 trivial 구현 |
| A-05 | `payloads/Kexts/Community/Safari26-PreAVX-Fix/` RestrictEvents 1.1.8 | [cf7f26f](https://github.com/NiSeullent/26x86/commit/cf7f26f) |
| A-06 | `x86/patch/safari26_preavx.py`, `efi_builder/misc.py` `revpatch=jsc` | [cf7f26f](https://github.com/NiSeullent/26x86/commit/cf7f26f) |
| — | `docs/Tahoe-Graphics-Roadmap.md` | 본 로드맵 |
| — | `docs/Tahoe-Graphics-Roadmap-Phase1-Tasks.md` | 본 문서 |

---

*태스크 상태는 GitHub Project / Issue #TBD 와 동기화 예정.*
