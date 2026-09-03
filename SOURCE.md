# 소스에서 빌드 및 실행

26x86은 Python GUI/CLI 애플리케이션입니다.

검증된 빌드: [Releases](https://github.com/NiSeullent/26x86/releases)

> 주의: [docs/wiki/Warnings.md](docs/wiki/Warnings.md)

## 시작하기

**Python 3.13+** 필요. [python.org](https://www.python.org/downloads/macos/) 공식 빌드 사용.

Xcode/CLT 내장 Python은 **지원하지 않습니다**.

```sh
git clone https://github.com/NiSeullent/26x86
cd 26x86
pip3 install -r requirements.txt
```

## 실행

```sh
python3 26x86.command              # 마법사 GUI (Tauri 우선)
python3 -m x86 wizard              # 동일
python3 -m x86 detect --json       # CLI
python3 -m x86 build --model iMac12,2 --verbose
python3 -m x86 --help
```

기본 GUI는 **Tauri** (macOS: WKWebView, Windows: WebView2) + 로컬 HTTP 브릿지입니다.
Qt WebEngine/Chromium은 `X86_GUI_BACKEND=qt`로만 선택합니다. Tauri 바이너리가 없으면
pywebview Cocoa로 폴백합니다. 셸 빌드: [gui-tauri/README.md](gui-tauri/README.md).

## 앱 번들 빌드

```sh
pip3 install pyinstaller
python3 Build-Project.command
open ./dist/
```

개발환경 전체: [docs/SETUP.md](docs/SETUP.md)
