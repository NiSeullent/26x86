# Track I — Metal/SkyLight dylib interpose (극한)

> **소유:** `x86/graphics/interpose_*.py`, `payloads/Kexts/Community/Extreme-Interpose/`  
> **커밋 prefix:** `feat(skylight-I):`  
> **공유 파일 수정 금지** — detect / yellow_screen / skylight_lut / sys_patch는 다른 트랙.

## 게이트

| Env | 역할 |
|-----|------|
| `X86_EXTREME=1` | **레시피·빌드·staging 복사·가이드 적용** (SHA 핀 불필요) |
| `X86_EXTREME_INSTALL=1` | 라이브 `/Library/.../SkyLightPlugins` 등 호스트 쓰기 |
| `X86_INTERPOSE_AVX` | `passthrough` \| `report0` \| `report1` |
| `X86_INTERPOSE_LUT` | `off` \| `log` \| `identity` |

## PoC / Apply

- 심볼 기반 `DYLD_INTERPOSE` (sysctl AVX, CG gamma, ColorSync)
- `X86_EXTREME=1` → `interpose_apply`: **make → staging/SkyLightPlugins 복사 → APPLY-GUIDE.txt**
- 레시피는 로컬 빌드 digest를 기록하며, 사전 SHA 핀으로 빈 dict를 내지 않음
- Apple blob 재배포 없음

## 실행

```bash
export X86_EXTREME=1
python3 -m x86.graphics.interpose_apply
# 또는
./payloads/Kexts/Community/Extreme-Interpose/scripts/apply.sh
python3 -m unittest x86.graphics.test_interpose
```

## Track K 연계 (INTEGRATE)

K `--extreme` → `macpro5_vega64_tahoe.run_interpose_apply` → `apply_extreme_interpose` (`98e2528`).
