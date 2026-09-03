# EXTREME — WindowServer / SkyLight process injection & LUT 복구

> **트랙:** **L-WS** (`feat(skylight-L):`)  
> **소유(전용 신규만):** `x86/graphics/windowserver_hook_*.py`, `test_windowserver_hook.py`, `windowserver_hook.stage-L`, 본 문서  
> **공유 파일 수정 금지:** `__init__.py`, `yellow_screen.py`, Tracks/Research 등  
> **게이트:** `X86_EXTREME=1` + (`X86_EXTREME_WINDOWSERVER_HOOK=1` | `I_ACCEPT_WINDOWSERVER_HOOK_RISK=1`)

## SIP / EULA

SIP가 WindowServer `DYLD_INSERT`를 거부 → plist는 `Disabled=true` 연구 아티팩트만.  
Non-Metal/3802 가드 유지. 사설 LUT 바이트패치(L5) blocked. Apple blob 무단 커밋 금지.

## 단계 L0–L5

| ID | 내용 | 상태 |
|----|------|------|
| L0 | cache/sRGB/agdpmod/RenderBox/KDKless | 출시됨 |
| L1 | 공개 LUT API | dry-run |
| L2 | SkyLightPlugins SHA 핀 | 스톡 Tahoe 무효 |
| L3 | DYLD launchd | SIP 차단 |
| L4 | software compositor | Apple 플래그 없음 |
| L5 | 사설 함수 후킹 | blocked |

## 사용

```bash
python3 -m x86.graphics.windowserver_hook
X86_EXTREME=1 X86_EXTREME_WINDOWSERVER_HOOK=1 python3 -m x86.graphics.windowserver_hook --run
python3 -m unittest x86.graphics.test_windowserver_hook
```

근거: OCLP-T2 #194, PR #1176, ASentientBot, moraea, WhateverGreen.
