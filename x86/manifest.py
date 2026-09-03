"""
manifest.py: Versioning and NiSeullent fork URLs for 26x86.
"""

from __future__ import annotations

from .paths import APP_NAME, BUNDLE_ID

PATCHER_VERSION: str = "4.0.0.18002.1"
PATCHER_SUPPORT_PKG_VERSION: str = "2.0.0"
OPENCORE_VERSION: str = "2.0.3"
COPYRIGHT: str = "Copyright © 2026 NiSeullent and 26x86 contributors"

GITHUB_ORG: str = "NiSeullent"
GITHUB_REPO: str = "26x86"

URL_PATCHER_SUPPORT_PKG: str = "https://github.com/NiSeullent/26x86-PatcherSupportPkg/download/"
URL_METALLIB_SUPPORT_PKG: str = "https://github.com/NiSeullent/26x86-MetallibSupportPkg"
URL_OPENCORE_PKG: str = "https://github.com/NiSeullent/26x86-OpenCorePkg"
URL_REPO: str = "https://github.com/NiSeullent/26x86/"
URL_GUIDE: str = "https://github.com/NiSeullent/26x86/wiki"
URL_ISSUES: str = "https://github.com/NiSeullent/26x86/issues"
URL_DISCUSSIONS: str = "https://github.com/NiSeullent/26x86/discussions"
URL_RELEASES_API: str = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}"

INSTALLER_PKG_URL: str = (
    f"{URL_REPO}releases/download/{PATCHER_VERSION}/AutoPkg-Assets-T2.pkg"
)


def patcher_support_pkg_dmg_url(version: str | None = None) -> str:
    """Download URL for Universal-Binaries.dmg."""
    ver = version or PATCHER_SUPPORT_PKG_VERSION
    return f"{URL_PATCHER_SUPPORT_PKG}{ver}/Universal-Binaries.dmg"


def patcher_support_pkg_internal_dmg_url(version: str | None = None) -> str:
    """Download URL for DortaniaInternalResources.dmg (developer builds)."""
    ver = version or PATCHER_SUPPORT_PKG_VERSION
    return f"{URL_PATCHER_SUPPORT_PKG}{ver}/DortaniaInternalResources.dmg"


__all__ = [
    "APP_NAME",
    "BUNDLE_ID",
    "COPYRIGHT",
    "GITHUB_ORG",
    "GITHUB_REPO",
    "INSTALLER_PKG_URL",
    "OPENCORE_VERSION",
    "PATCHER_SUPPORT_PKG_VERSION",
    "PATCHER_VERSION",
    "patcher_support_pkg_dmg_url",
    "patcher_support_pkg_internal_dmg_url",
    "URL_DISCUSSIONS",
    "URL_GUIDE",
    "URL_ISSUES",
    "URL_METALLIB_SUPPORT_PKG",
    "URL_OPENCORE_PKG",
    "URL_PATCHER_SUPPORT_PKG",
    "URL_RELEASES_API",
    "URL_REPO",
]
