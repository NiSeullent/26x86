# 소스에서 빌드 및 실행

26x86의 핵심은 Python 기반 GUI/CLI 애플리케이션입니다. 소스에서 실행하려면 `OpenCore-Patcher-GUI.command`를 Python으로 실행하세요.

검증된 빌드는 [26x86 Releases](https://github.com/NiSeullent/26x86/releases)를 참고하세요.

* **경고:** 태그 없는 최신 커밋 빌드는 활발히 개발 중인 빌드입니다. 테스트·안전·동작이 보장되지 않습니다. 주력 Mac에서 사용하지 마세요. [CHANGELOG](./CHANGELOG.md)를 먼저 읽으세요.
* **포럼 등에 해당 바이너리 링크를 공유하지 마세요.** 이 문서 또는 공식 Releases만 링크하세요.
* 신뢰할 수 없는 출처의 재업로드 바이너리는 보안 위험이 있습니다.

## 시작하기

**Python 3.13.13 이상**이 필요합니다. [python.org](https://www.python.org/downloads/macos/)에서 받은 공식 빌드를 사용하세요.

* Xcode·Command Line Tools에 포함된 Python은 신뢰성 문제로 **지원하지 않습니다**.

터미널에서:

```sh
cd ~/Developer
git clone https://github.com/NiSeullent/26x86
cd ./26x86
pip3 install -r requirements.txt
```

설치 오류 시:

* Python 3.13 사용 (본 프로젝트는 3.13 기준으로 테스트)
* 의존성 `.whl` 스냅샷 사용

## 26x86 실행

```sh
# GUI 실행
python3 OpenCore-Patcher-GUI.command
```

인자 없이 실행하면 GUI가, 핵심 CLI 인자를 넘기면 CLI가 시작합니다. 한글 도움말 기본:

```sh
python3 OpenCore-Patcher-GUI.command --lang ko --build --model iMac12,2 --verbose
```

`-h` / `--help` 또는 `--lang ko --help`로 옵션을 확인하세요.

## 사전 빌드 바이너리 생성

일반 사용자에게 로컬 Python 없이 쓰게 하려는 목적입니다. 개발 중에는 `OpenCore-Patcher-GUI.command`로 충분합니다.

```sh
pip3 install pyinstaller
cd ~/Developer/26x86/
python3 Build-Project.command
open ./dist/
```

완료 후 `./dist/26x86.app` 및 pkg 설치 프로그램이 생성됩니다.

워크스페이스 전체 개발환경은 [./docs/SETUP.en.md](./docs/SETUP.en.md)를 참고하세요. 영문: [./docs/SETUP.en.md](./docs/SETUP.en.md).
