"""
Cross-platform helpers for 26x86 (macOS / Windows / Linux).
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

MACOS_ONLY_MESSAGE = (
    "이 기능은 macOS에서만 사용할 수 있습니다. "
    "OpenCore EFI 빌드, 루트 볼륨 패치, LaunchAgent 설치 등은 macOS 전용입니다."
)

NON_MAC_HOST_MODEL = "NonMacHost"


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_windows() -> bool:
    return sys.platform == "win32"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def platform_label() -> str:
    if is_macos():
        return "macOS"
    if is_windows():
        return "Windows"
    if is_linux():
        return "Linux"
    return sys.platform


def macos_only_message(feature: str = "") -> str:
    if feature:
        return f"{feature}: {MACOS_ONLY_MESSAGE}"
    return MACOS_ONLY_MESSAGE


def qt_webengine_available() -> bool:
    """True when a Qt Chromium binding is installed (does not import WebEngine)."""
    import importlib.util

    for module in (
        "PySide6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineWidgets",
        "PyQt5.QtWebEngineWidgets",
    ):
        try:
            if importlib.util.find_spec(module) is not None:
                return True
        except (ImportError, ValueError, AttributeError):
            # find_spec('PyQt6.child') raises if the optional parent package
            # is absent. A minimal Linux preparation install need not have Qt.
            continue
    return False


def resolve_pywebview_gui() -> Optional[str]:
    """Preferred pywebview backend. macOS default is Cocoa WebKit, not Chromium."""
    override = (os.environ.get("X86_WEBVIEW_GUI") or "").strip().lower()
    if override:
        return override

    if is_macos():
        return "cocoa"
    if is_windows():
        return "edgechromium"
    if is_linux():
        if qt_webengine_available():
            return "qt"
        return "gtk"
    return None


def reveal_in_file_manager(path: str | Path) -> bool:
    """Reveal a file or folder in the platform file manager."""
    target = Path(path)
    if not target.exists():
        return False

    try:
        if is_macos():
            subprocess.run(["/usr/bin/open", "--reveal", str(target)], check=False)
            return True
        if is_windows():
            subprocess.run(["explorer", "/select,", str(target.resolve())], check=False)
            return True
        if is_linux():
            folder = target if target.is_dir() else target.parent
            for cmd in (
                ["xdg-open", str(folder)],
                ["gio", "open", str(folder)],
            ):
                try:
                    subprocess.run(cmd, check=False)
                    return True
                except OSError:
                    continue
    except OSError:
        return False
    return False


def host_os_version() -> str:
    if is_macos():
        try:
            result = subprocess.run(
                ["/usr/bin/sw_vers", "-productVersion"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return platform.version() or platform.release()


def host_os_build() -> str:
    if is_macos():
        try:
            result = subprocess.run(
                ["/usr/bin/sw_vers", "-buildVersion"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return "N/A"


def non_mac_detect_payload() -> dict[str, object]:
    """Minimal detect payload when Mac hardware probing is unavailable."""
    return {
        "platform": platform_label(),
        "host_is_mac": False,
        "model": NON_MAC_HOST_MODEL,
        "marketing_name": f"{platform_label()} 호스트 (Mac 하드웨어 감지 불가)",
        "build_model": NON_MAC_HOST_MODEL,
        "real_model": NON_MAC_HOST_MODEL,
        "cpu": platform.processor() or platform.machine(),
        "gpus": [],
        "os_version": host_os_version(),
        "os_build": host_os_build(),
        "host_is_hackintosh": True,
        "macos_only_note": MACOS_ONLY_MESSAGE,
    }
