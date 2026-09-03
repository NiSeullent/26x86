# 26x86 연구 요약 (Executive Summary)

> **프로젝트:** macOS 26 Tahoe on x86 Macs  
> **작성일:** 2026年 9월 4일  
> **상태:** Alpha / 실험 단계 — 일상 사용 비권장

---

## 한 줄 요약

**macOS 26 Tahoe는 Apple이 공식 지원하는 마지막 Intel macOS이지만, OCLP 공식 릴리스는 아직 Sequoia(2.4.1)에 머물러 있으며 T2 Mac은 실험 포크(OCLP-T2 alpha 18)에서도 인스톨러 부팅까지만 가능하고 데스크톱/APFS 단계에서 차단된다.**

---

## macOS 26 Tahoe x86 지원 현황

### Apple 공식 지원 (OCLP 불필요)

| 모델 | SMBIOS | 비고 |
|------|--------|------|
| Mac Pro (2019) | MacPro7,1 | T2 탑재 |
| MacBook Pro 16" (2019) | MacBookPro16,x | T2 탑재 |
| MacBook Pro 13" (2020, 4 Thunderbolt) | MacBookPro16,2 등 | T2 탑재 |
| iMac 27" 5K (2020) | iMac20,x | T2 탑재 |

**탈락 모델:** Intel MacBook Air(2020), Intel Mac mini(2018), iMac Pro(2017), 2018~2019 T2 MacBook Air/Pro(Apple 미지원 목록) 등.

### OCLP 비공식 지원 매트릭스 (2026-09 기준)

| Mac 분류 | Sequoia (OCLP 2.4.1) | Tahoe 26 (실험) | 권장 조치 |
|----------|----------------------|-----------------|-----------|
| **Non-T2 Intel (2012~2017)** | ✅ 안정 | 🟡 실험 가능 (Nightly/OCLP-R/OCLP-Plus) | 실험용 spare Mac에서만 |
| **T2 Mac (2017~2020, Apple 탈락)** | ✅ 대부분 안정 | 🔴 인스톨러만 부분 성공, 데스크톱/APFS 차단 | **Sequoia 유지** |
| **Core 2 Duo (2008~2010)** | ✅ (SSE kext 필요) | 🔴 Tahoe 부팅 불가 (AAAMouSSE/telemetrap) | Sequoia 또는 하드웨어 교체 |
| **Metal 8302 (2012~2014)** | ✅ | 🟡 가속 없이 부팅만 (패치 미완) | 패치 대기 |
| **Non-Metal (2011 이하)** | ✅ (UI 제한) | 🟡 Liquid Glass 비호환, 패치 미완 | UI 우회 패치 대기 |

---

## 핵심 프로젝트별 역할

### 1. Dortania OpenCore Legacy Patcher (공식)
- **현재:** v2.4.1, Sequoia까지 안정 지원
- **Tahoe:** Issue #1167에서 개발 중이나 **공식 릴리스 미출시**
- **T2:** Issue #1136 — AppleKeyStore SKS timeout으로 **공식 미지원**
- **개발 현황:** 핵심 개발자 이탈, OpenCollective 신규 기부 중단, 릴리스 일정 불확실

### 2. albert-mueller/OpenCore-Legacy-Patcher-T2 (T2 실험 포크)
- **현재:** v4.0.0 alpha 18.2.1 (2026-09-03)
- **성과:** Tahoe 인스톨러 부팅, corecrypto 패닉 대부분 해결, SMBIOS 스푸핑 불필요화(T2)
- **미해결:** APFS 파티션 생성/마운트(-69624, -69845), AppleImage4 "Needs authenticator", 데스크톱 미도달
- **범위:** macOS 27 Golden Gate 미지원(arm64-only) — **Tahoe 26이 최종 목표**

### 3. hackdoc/OCLP-R + pyquick (Non-T2 Tahoe 실험)
- macOS 26 상수, USB-Map-Tahoe, PatcherSupportPkg 1.11.x
- pyquick: MetallibSupportPkg manifest를 자체 GitHub Pages로 리다이렉트
- **대상:** T2 없는 2012~2017 Intel Mac

### 4. YBronst/OCLP-Plus (Tahoe Patch Set)
- macOS 26.0~26.4.1 Modern 루트 패치, Broadcom Wi-Fi(AWDL/AirDrop)
- **2026-06-28 아카이브** — 추가 업데이트 없음, 기존 버전은 동작
- MacPro7,1, MBP16,x, iMac20,x 등 **공식 지원 모델** 중심

### 5. laobamac/OCLP-Mod (커뮤니티 포크)
- 662 stars, Intel 구형 iGPU는 Dortania 담당
- MetallibSupportPkg Tahoe 호환 논의 중

---

## 기술적 블로커 (우선순위)

### 🔴 P0 — T2 Mac 부팅/설치

| 블로커 | 증상 | 연구 방향 |
|--------|------|-----------|
| **AppleKeyStore SEP timeout** | `sks request timeout` → AppleSEPManager 패닉 | vytska69: T1 keystore 스택 대체; DrDonk: AppleKeyStore 패치; Lilu 플러그인 (#125) |
| **APFS/AppleImage4 인증** | `Needs authenticator (81)`, trustcache 오류 | Issue #130 — T2 secure boot + APFS root hash 상호작용 |
| **APFS 파티션 관리** | -69624, -69845, Container만 마운트 | Issue #69 — T2 역공학, OpenCorePkg 협력 |

### 🟠 P1 — GPU/Metal (Non-T2)

| 블로커 | 영향 Mac | 상태 |
|--------|----------|------|
| **MetallibSupportPkg Tahoe 미완** | Metal 3802 (Ivy/Haswell/Kepler) | Dortania Sequoia PKG만; pyquick/albert-mueller 포크 진행 |
| **Metal 8302 패치 부재** | 2012~2014 Mac (rMBP, Late 2012 iMac 등) | OCLP-T2 안전 가드로 패닉 방지, 가속 없음 |
| **Non-Metal + Liquid Glass** | 2011 이하 GPU | UI downgrade 우회 필요, 패치 미완 |

### 🟡 P2 — 레거시 CPU/주변기기

| 블로커 | 영향 Mac | 상태 |
|--------|----------|------|
| **AAAMouSSE/telemetrap** | Core 2 Duo (Penryn 이하) | 2021 이후 미업데이트, 폐쇄 소스 → Tahoe용 재작성 필요 |
| **USB 1.1** | 2010 이하 Mac, Mac Pro 3,1~5,1 | stephandeutsch/moraea 패치; 인스톨러에서 USB 2.0 허브 필수 |
| **Intel Wi-Fi** | Atheros/BCM94328 등 | OCLP-Plus는 Broadcom만; OCLP-Mod 또는 moraea 패치 |

---

## 권장 전략 (Mac 유형별)

### T2 Mac 사용자 (2017~2020, Apple Tahoe 탈락)
```
✅ macOS Sequoia + OCLP 2.4.1 (일상 사용)
❌ Tahoe 실험 — 데이터 백업 후 spare Mac에서만
📡 albert-mueller/OpenCore-Legacy-Patcher-T2 Issue #69, #130 추적
```

### Non-T2 Intel Mac (2012~2017)
```
🟡 Tahoe 실험: OCLP Nightly / hackdoc OCLP-R / OCLP-T2 (Non-T2 가이드 #171)
⚠️ KDK(26A5425a) + MetallibSupportPkg + 루트 패치 재적용 필수
⚠️ macOS 업데이트마다 패치 소거
```

### Core 2 Duo / 2011 Non-Metal Mac
```
✅ Sequoia 유지 (OCLP 2.4.1)
❌ Tahoe — AAAMouSSE/telemetrap 재작성 전까지 부팅 불가
```

### Apple 공식 Tahoe 지원 Intel Mac
```
✅ System Settings에서 정상 업그레이드 (OCLP 불필요)
🟡 Wi-Fi/Continuity 문제 시 YBronst OCLP-Plus 고려 (Broadcom)
```

---

## macOS 27 (Golden Gate) 전망

- **arm64-only** — Intel Mac 부팅 불가
- OCLP는 Universal Binary에서 x86 코드가 제거되면 **구조적으로 패치 불가**
- **26x86 프로젝트 범위 = macOS 26 Tahoe가 최종**
- MacRumors 커뮤니티: Tahoe도 OCLP 미완 상태에서 macOS 27 논의는 "너무 이르다"는 의견 우세

---

## 연구 갭 (추가 조사 필요)

1. **albert-mueller/metal** 포크 — Issue #27에서 "최초 Tahoe MetallibSupportPkg"로 언급되나 공개 저장소 미확인(404)
2. **DrDonk AppleKeyStore 패치** — OCLP-T2 크레딧에만 존재, 독립 공개 코드 없음
3. **stephandeutsch USB 1.1** — 저장소 존재(0 stars)하나 Tahoe 패치 diff 미분석
4. **Metal 8302 vs 3802** — Wiki는 8302(2012~2014) 미지원, Dortania는 3802(Ivy/Haswell) 중심 — 모델별 GPU 세대 매핑 문서화 필요
5. **OpenCorePkg T2 포크** — albert-mueller/OpenCorePkg-add-T2-support와 Acidanthera upstream 머지 가능성

---

## 결론

macOS 26 Tahoe on x86는 **기술적으로 가능한 마지막 Intel macOS**이지만, 2026년 9월 현재 **프로덕션 준비 상태는 아니다**.

| 영역 | 성숙도 | 비고 |
|------|--------|------|
| Apple 공식 Intel Tahoe | ✅ Production | 4개 모델만 |
| OCLP Sequoia (Non-T2/T2) | ✅ Production | 2.4.1 |
| OCLP Tahoe (Non-T2) | 🟡 Alpha | Nightly/OCLP-R/OCLP-Plus 실험 |
| OCLP Tahoe (T2) | 🔴 Pre-Alpha | 인스톨러만, APFS/데스크톱 차단 |
| GPU Metal 3802 Tahoe | 🟡 Beta | MetallibSupportPkg/pyquick 진행 |
| GPU Metal 8302 / Non-Metal Tahoe | 🔴 Not Ready | 패치 미완, 안전 가드만 |
| Core 2 Duo Tahoe | 🔴 Blocked | SSE kext 재작성 필요 |

**26x86 프로젝트의 실질적 초점:** T2 Mac APFS/AppleKeyStore 블로커 해결, MetallibSupportPkg Tahoe 완성, Non-T2 Mac의 실용적 Tahoe 패치셋 통합.

---

*상세 출처 및 78개 항목 전체 목록: [RESEARCH_INVENTORY.md](./RESEARCH_INVENTORY.md)*
