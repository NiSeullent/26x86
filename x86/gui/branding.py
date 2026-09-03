"""
Window titles and branding helpers for 26x86 GUI.
"""

import os

from x86.manifest import APP_NAME, BUNDLE_ID


def window_title(version: str = "") -> str:
    """Primary window title: ``26x86 (com.sharhene777.26x86)``."""
    base = f"{APP_NAME} ({BUNDLE_ID})"
    if version:
        return f"{base} {version}"
    return base


def about_title() -> str:
    return f"{APP_NAME} 정보"


def about_description_lines() -> list[str]:
    return [
        "오래된 Mac에서 Apple이 공식 지원하지 않는",
        "최신 macOS를 사용할 수 있도록 돕는 도구입니다.",
        "",
        BUNDLE_ID,
    ]


def is_advanced_gui_enabled() -> bool:
    """Legacy wx MainFrame is available only when ``X86_ADVANCED=1``."""
    return os.environ.get("X86_ADVANCED") == "1"
