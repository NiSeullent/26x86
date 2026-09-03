# 26x86 개발환경 셋업 가이드

macOS 26 Tahoe x86 Mac 지원 프로젝트 **26x86**의 로컬 개발·빌드·테스트 환경 구성 방법입니다.

## 디렉터리 구조

```
~/Desktop/26x86/
├── 26x86/                      # 메인 패처 (Python GUI/CLI)
├── 26x86-MetallibSupportPkg/   # Metal 라이브러리 패치
├── 26x86-PatcherSupportPkg/    # 유니버설 바이너리·패치 DMG
├── 26x86-OpenCorePkg/          # OpenCore 부트로더 (T2 지원 포크)
├── .venv/                      # Python 3.13 가상환경
├── scripts/                    # 셋업·빌드 스크립트
├── docs/                       # 문서
└── vm/                         # UTM 가상머신 템플릿
```

## 빠른 시작 (원클릭)

```bash
cd ~/Desktop/26x86
bash scripts/setup-dev.sh
source .venv/bin/activate
cd 26x86
python3 26x86.command
```

## 수동 설치

### 1. 사전 요구사항

| 항목 | 버전/설명 |
|------|-----------|
| macOS | 15.x (Sequoia) 이상 권장 |
| Python | **3.13+** (python.org 또는 `uv python install 3.13`) |
| Xcode CLT | `xcode-select --install` |
| Git | `git --version` |
| gh CLI | GitHub 인증 (선택) |

> 개발 환경 주의사항(Python 3.9 비지원, VM 호스트 등): [wiki/Installation-Notes.md](./wiki/Installation-Notes.md) · [wiki/Warnings.md](./wiki/Warnings.md)

### 2. 저장소 클론

```bash
mkdir -p ~/Desktop/26x86 && cd ~/Desktop/26x86

git clone https://github.com/NiSeullent/26x86.git
git clone https://github.com/NiSeullent/26x86-MetallibSupportPkg.git
git clone https://github.com/NiSeullent/26x86-PatcherSupportPkg.git
git clone https://github.com/NiSeullent/26x86-OpenCorePkg.git
```

### 3. Python 가상환경

```bash
# uv 사용 (권장)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.13
~/.local/bin/python3.13 -m venv .venv
source .venv/bin/activate

# 종속성 설치 (PyInstaller 부트로더 재컴파일 포함)
PYINSTALLER_COMPILE_BOOTLOADER=1 pip install --no-binary pyinstaller -r 26x86/requirements.txt
```

### 4. 실행 확인

```bash
cd 26x86
python3 26x86.command --help     # CLI
python3 26x86.command              # GUI (마법사 모드)
python3 26x86.command --detect     # Mac 모델 감지
python3 26x86.command --build --model iMac11,2 --verbose
```

## 빌드 환경

### OpenCorePkg 빌드

```bash
bash scripts/build-opencore.sh
```

**방법 A — 네이티브 (Xcode CLT 필요):**
```bash
cd 26x86-OpenCorePkg
./build_oc.tool
```

**방법 B — Docker:**
```bash
brew install --cask docker   # Docker Desktop 설치 후
cd 26x86-OpenCorePkg
docker compose up --build
```

빌드 결과(`OpenCore-RELEASE.zip`, `OpenCore-DEBUG.zip`)를 `26x86/payloads/OpenCore/`에 배치하거나:

```bash
cd 26x86/payloads/OpenCore
python3 Update-OpenCore.command
```

### PatcherSupportPkg DMG 생성

```bash
cd 26x86-PatcherSupportPkg
python3 ci.py
# 또는 Generate-DMG.command 실행
```

### MetallibSupportPkg

```bash
cd 26x86-MetallibSupportPkg
pip install -r requirements.txt
python3 metallib.py --help
```

### 앱 번들 빌드 (PyInstaller)

```bash
source .venv/bin/activate
cd 26x86
python3 Build-Project.command
open ./dist/
```

## UTM 가상머신 (테스트용)

실제 Mac 하드웨어 없이 EFI/부트 설정을 검증하려면 UTM을 사용합니다.

### UTM 설치

```bash
# Homebrew (Intel Mac 권한 문제 시 수동 설치)
brew install --cask utm

# 또는 https://mac.getutm.app 에서 직접 다운로드
```

### VM 템플릿 사용

1. UTM 실행 → **파일 → 가져오기**
2. `vm/26x86-test.utm` 선택
3. 디스크 이미지: macOS Recovery 또는 설치 ISO 마운트
4. EFI 파티션에 26x86으로 생성한 OpenCore EFI 복사

자세한 VM 설정은 [vm/README.md](../vm/README.md)를 참고하세요. VM 호스트 제한은 [wiki/Installation-Notes.md](./wiki/Installation-Notes.md)를 참고하세요.

## 환경 변수

`.env.example`을 `.env`로 복사하여 경로를 커스터마이즈할 수 있습니다:

```bash
cp .env.example .env
```

## 종속 GitHub 포크

| 포크 | 원본 |
|------|------|
| [NiSeullent/26x86](https://github.com/NiSeullent/26x86) | albert-mueller/OpenCore-Legacy-Patcher-T2 |
| [NiSeullent/26x86-OpenCorePkg](https://github.com/NiSeullent/26x86-OpenCorePkg) | albert-mueller/OpenCorePkg-add-T2-support |
| [NiSeullent/26x86-PatcherSupportPkg](https://github.com/NiSeullent/26x86-PatcherSupportPkg) | hackdoc/PatcherSupportPkg |
| [NiSeullent/26x86-MetallibSupportPkg](https://github.com/NiSeullent/26x86-MetallibSupportPkg) | dortania/MetallibSupportPkg |

Acidanthera kext (Lilu, WhateverGreen 등)는 `payloads/Kexts/Update-Kexts.command`로 upstream에서 가져옵니다.

## 문제 해결

| 증상 | 해결 |
|------|------|
| `Python 3.9` 오류 | `.venv` 재생성, python3.13 사용 확인 |
| PyInstaller codesign 오류 | `PYINSTALLER_COMPILE_BOOTLOADER=1` 로 재설치 |
| wxPython import 실패 | `pip install 'wxpython<4.2.5'` |
| Homebrew 권한 오류 | `sudo chown -R $(whoami) /usr/local/share/man/man8` 또는 [MacPorts](https://www.macports.org) 사용 |
| OpenCore 빌드 실패 | Xcode CLT 설치 확인, `./build_oc.tool --help` |

## 관련 문서

- [wiki/Home.md](./wiki/Home.md) — 위키 목차 (주의사항·이슈·설치)
- [SOURCE.md](../SOURCE.md) — 소스에서 실행
- [DISCLAIMER.md](../DISCLAIMER.md) — 면책사항
- [RESEARCH_INVENTORY.md](./RESEARCH_INVENTORY.md) — 연구 자료 목록
