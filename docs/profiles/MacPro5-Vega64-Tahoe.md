# MacPro5,1 pre-AVX + RX Vega 64 → macOS Tahoe E2E 프로파일 (Track K)

실기: 플래시 Mac Pro(5,1급), AVX 없음, RX Vega 64, Tahoe 목표.

## CLI (공유 `x86/cli.py` 미수정)

```bash
python -m x86.profiles list
python -m x86.profiles show macpro5-vega64-tahoe
python -m x86.profiles apply macpro5-vega64-tahoe --dry-run
python -m x86.profiles apply macpro5-vega64-tahoe --config /Volumes/EFI/EFI/OC/config.plist
python -m x86.profiles apply macpro5-vega64-tahoe --extreme   # 또는 X86_EXTREME=1
```

동등: `python -m x86.profiles.macpro5_vega64_tahoe apply …`

## 고정 순서 (역전 금지)

1. `efi.agdpmod_shikigva` — agdpmod / shikigva
2. `efi.kdkless` — KDKlessWorkaround.kext
3. `efi.restrictevents_jsc` — RestrictEvents + revpatch=jsc
4. `root.amd_vega` — AMD Vega Metal 31001
5. `root.yellow_mitigations` — Tahoe Yellow Screen Mitigations
6. `extreme.hooks` — H/I/J/L (opt-in)

## 소유 (Track K 전용 신규)

| 경로 | 역할 |
|------|------|
| `x86/profiles/macpro5_vega64_tahoe.py` | 프로파일·EFI 뮤테이션 |
| `x86/profiles/fixtures.py` | detect 픽스처 |
| `x86/profiles/__main__.py` | 전용 CLI |
| `docs/profiles/MacPro5-Vega64-Tahoe.md` | 이 문서 |
| `x86/cli.profile.stage-K.md` | 공유 CLI 병합 제안(비적용) |

공유 파일(`x86/cli.py` 등)은 직접 수정하지 않습니다.
