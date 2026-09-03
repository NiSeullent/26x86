"""
26x86 GUI package. Default UI is the Cocoa+HTTP HTML wizard (``x86.gui.webview_app``).
Qt Chromium (``x86.gui.qt_chromium``) is opt-in via ``X86_GUI_BACKEND=qt``.
"""

__all__ = ["wizard", "theme", "branding", "webview_app", "qt_chromium", "bridge", "launch"]
