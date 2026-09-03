# Safari 26 Pre-AVX Fix (Mac Pro 5,1)

Safari 26.6.1 WebContent가 pre-AVX Intel CPU에서 AVX 명령(`vmovaps`)을 실행해 `EXC_BAD_INSTRUCTION` / `SIGILL`로 죽는 문제를 완화합니다. 패치는 [Safari26-PreAVX-Fix](https://github.com/kilinccagatay/Safari26-PreAVX-Fix)의 RestrictEvents 1.1.8입니다.

## 무엇을 하는가

- 기존 RestrictEvents `revpatch=jsc`가 JavaScriptCore AVX 기능 비트를 숨기더라도, Safari 26.6.1의 `ctiMasmProbeTrampoline`에는 길이 고정 AVX `vmovaps` 블록이 남아 있습니다.
- 이 kext는 해당 바이트 시퀀스를 같은 길이의 레거시 SSE `movaps`로 바꿉니다.
- **시스템 볼륨·루트 패치·`config.plist`를 직접 고치지 않습니다.** 26x86은 EFI 빌드 때 `RestrictEvents.kext`를 이 빌드로 교체하고 `revpatch`에 `jsc`를 넣습니다.

출처·면책: [kilinccagatay/Safari26-PreAVX-Fix](https://github.com/kilinccagatay/Safari26-PreAVX-Fix) (BSD 3-Clause, Acidanthera RestrictEvents 포크). 업스트림은 **MacPro5,1 + Xeon E5620(Westmere, AVX 없음) + Safari 26.6.1**에서만 종단 검증했습니다.

## 언제 자동 적용되는가

| 조건 | 동작 |
|------|------|
| 대상 모델이 **MacPro5,1**이고 CPU가 AVX를 보고하지 않음 | EFI 빌드 시 자동 ON |
| MacPro4,1 / 3,1 / 6,1 / 7,1 및 그 외 Mac | **적용하지 않음** (과잉 적용 방지). 4,1을 5,1로 플래시한 기기는 모델이 5,1로 감지됩니다. |
| MacPro5,1이지만 CPU가 AVX를 보고함 (업그레이드 Xeon 등) | 적용하지 않음 |
| Windows / Linux 호스트 | EFI를 바꾸지 않고 안내만 |
| 사용자 설정으로 끔 | 적용하지 않음 |

기본값은 감지 시 자동 적용입니다. 끄려면 `~/Library/Application Support/26x86/config.json`에서:

```json
"safari26_preavx_fix": false,
"auto_pre_avx_patch": false
```

어느 한쪽을 `false`로 두면 자동 적용이 중단됩니다.

## 사용 방법

1. MacPro5,1에서 `26x86.command` 또는 `python3 -m x86 wizard`로 EFI를 만듭니다.
2. 빌드 로그에 `Safari 26 Pre-AVX Fix: RestrictEvents 1.1.8`이 보이면 교체가 포함된 것입니다.
3. 해당 EFI로 부팅한 뒤 `kmutil showloaded | grep -i RestrictEvents`에서 버전 **1.1.8**을 확인합니다.

`python3 -m x86 detect --json`의 `safari26_preavx` 필드로 적용 여부(`should_apply`)와 이유(`reason`)를 볼 수 있습니다.

관련: [Pre-AVX-Mac-Pro.md](./Pre-AVX-Mac-Pro.md)
