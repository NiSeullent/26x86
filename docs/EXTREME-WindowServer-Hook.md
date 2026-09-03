# EXTREME — WindowServer / SkyLight (Track L)

> **게이트:** `X86_EXTREME=1` + (`X86_EXTREME_WINDOWSERVER_HOOK=1` \| `I_ACCEPT_WINDOWSERVER_HOOK_RISK=1`)  
> **영구 차단 없음.** L5 런타임 process inject PoC는 에이전트가 거부 → **L5-R** 재배정.

## SIP / 설치

SIP가 WindowServer `DYLD_INSERT`를 거부할 수 있음 → plist는 연구 아티팩트.  
Apple blob 무단 커밋 지양(페이로드 정책은 F/PSP).

## 단계 L0–L5-R

| ID | 내용 | 상태 |
|----|------|------|
| L0 | cache/sRGB/agdpmod/RenderBox/KDKless | 출시됨 |
| L1 | 공개 LUT API | dry-run |
| L2 | SkyLightPlugins | extreme / I 연계 |
| L3 | DYLD launchd | extreme dry-run |
| L4 | software compositor 탐색 | 조사 |
| L5 | 사설 함수 **런타임 inject** | **`refused_by_agent`** |
| **L5-R** | **루트볼륨 패치셋** (OCLP OVERWRITE/바이너리, inject 아님) | 부모 재배정 · MC 통합만 · B `SL-BYTEPATCH-LUT`와 조율 |

## 사용

```bash
python3 -m x86.graphics.windowserver_hook
X86_EXTREME=1 X86_EXTREME_WINDOWSERVER_HOOK=1 python3 -m x86.graphics.windowserver_hook --run
```

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | L5 refused → L5-R 루트볼륨 · 영구 blocked 문구 삭제 |
