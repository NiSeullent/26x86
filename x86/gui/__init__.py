"""
26x86 GUI package.

Default UI shell is **Tauri** (WKWebView / WebView2) over the local HTTP
bridge (``x86.gui.tauri_app`` + ``x86.gui.http_bridge``).

Fallbacks: Cocoa pywebview (``x86.gui.webview_app``). Qt Chromium
(``x86.gui.qt_chromium``) is opt-in via ``X86_GUI_BACKEND=qt``.
"""

__all__ = [
    "wizard",
    "theme",
    "branding",
    "webview_app",
    "tauri_app",
    "http_bridge",
    "qt_chromium",
    "bridge",
    "launch",
]
