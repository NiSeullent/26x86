# 26x86 Tauri GUI shell

Native WebView shell for the HTML wizard in `x86/gui/web/`.

| Platform | Engine |
|----------|--------|
| macOS | **WKWebView** (Safari WebKit) |
| Windows | **WebView2** (Edge) |
| Linux | WebKitGTK |

This is **not** Qt WebEngine / Chromium.

## Architecture

1. Python starts a local HTTP server (`x86.gui.http_bridge`) that serves static UI + `/api/*` JSON bridge.
2. This Tauri app opens a window pointed at `http://127.0.0.1:<port>/index.html`.
3. `app.js` talks to the Python bridge over HTTP when `window.pywebview` is absent.

```
python -m x86 wizard          # prefers Tauri when binary exists
X86_GUI_BACKEND=cocoa …       # force pywebview Cocoa fallback
X86_GUI_BACKEND=qt …          # opt-in Qt WebEngine (Chromium)
```

## Prerequisites

- Rust stable (`rustup`)
- Tauri CLI 2: `cargo install tauri-cli --version "^2"`
- macOS: Xcode CLT; Windows: WebView2 Runtime

Node.js is **not** required (frontend is plain HTML/CSS/JS).

## Build

```sh
cd gui-tauri
cargo build --release
# or with bundler:
cargo tauri build
```

Outputs:

- Binary: `target/release/x86-gui`
- macOS app (with `cargo tauri build`): `target/release/bundle/macos/26x86.app`

## Windows / CI plan

1. Install Rust + WebView2 on the Windows runner.
2. `cargo tauri build --target x86_64-pc-windows-msvc`
3. Ship `26x86.exe` / `x86-gui.exe` alongside the Python entrypoint that launches it (same as macOS).
4. Do **not** bundle Qt WebEngine for the default GUI path.

PyInstaller (`26x86-Windows.spec`) remains a fallback until the Tauri Windows artifact is wired into CI.
