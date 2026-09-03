# Track I — Metal/SkyLight dylib interpose (극한)

> **소유:** `x86/graphics/interpose_*.py`, `payloads/Kexts/Community/Extreme-Interpose/`  
> **커밋 prefix:** `feat(skylight-I):`  
> **공유 파일 수정 금지** — detect / yellow_screen / skylight_lut / sys_patch는 다른 트랙.

## 게이트

| Env | 역할 |
|-----|------|
| `X86_EXTREME=1` | 연구 훅 / 비패스스루 활성 |
| `X86_EXTREME_INSTALL=1` | LaunchDaemon·루트 래퍼 설치 허용 |
| `X86_INTERPOSE_AVX` | `passthrough` \| `report0` \| `report1` |
| `X86_INTERPOSE_LUT` | `off` \| `log` \| `identity` |

## PoC

- 심볼 기반 `DYLD_INTERPOSE` (sysctl AVX 스푸핑, CG gamma, ColorSync 프로브)
- SkyLightPlugins 스템 `ExtremeCompositor` + `SkyLightPluginEntry` 심 (스톡 Tahoe 미로드)
- Apple blob 재배포 없음; SHA 핀 전 루트 레시피는 빈 dict

## 빌드

```bash
cd payloads/Kexts/Community/Extreme-Interpose && ./scripts/build.sh
python3 -m unittest x86.graphics.test_interpose
```
