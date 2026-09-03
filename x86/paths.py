"""
paths.py: Filesystem paths for 26x86 (bundle ID com.sharhene777.26x86).
"""

from __future__ import annotations

from pathlib import Path

BUNDLE_ID: str = "com.sharhene777.26x86"
APP_NAME: str = "26x86"
APP_BUNDLE_NAME: str = "26x86.app"

BUNDLE_ID_PRIVILEGED_HELPER: str = f"{BUNDLE_ID}.privileged-helper"
BUNDLE_ID_UNINSTALLER: str = f"{BUNDLE_ID}-uninstaller"
BUNDLE_ID_INSTALLER: str = BUNDLE_ID
BUNDLE_ID_AUTOPKG: str = f"{BUNDLE_ID}.pkg.AutoPkg-Assets"

LAUNCH_AGENT_SUFFIXES: tuple[str, ...] = (
    "auto-patch",
    "macos-update",
    "rsr-monitor",
    "os-caching",
)


class Paths:
    """Canonical filesystem locations for 26x86."""

    @staticmethod
    def repo_root() -> Path:
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def user_config_dir() -> Path:
        return Path.home() / "Library/Application Support/26x86"

    @staticmethod
    def user_config() -> Path:
        return Paths.user_config_dir() / "config.json"

    @staticmethod
    def user_preferences_plist() -> Path:
        return Path.home() / "Library/Preferences/com.niseullent.26x86.plist"

    @staticmethod
    def user_cache_dir() -> Path:
        return Paths.user_config_dir() / "cache"

    @staticmethod
    def user_logs_dir() -> Path:
        return Path.home() / "Library/Logs/26x86"

    @staticmethod
    def user_launch_agents_dir() -> Path:
        return Path.home() / "Library/LaunchAgents"

    @staticmethod
    def system_app_support() -> Path:
        return Path("/Library/Application Support/26x86")

    @staticmethod
    def developer_mode_marker() -> Path:
        return Path.home() / ".26x86_developer"

    @staticmethod
    def payloads_dir() -> Path:
        return Paths.repo_root() / "payloads"

    @staticmethod
    def resources_dir() -> Path:
        return Paths.repo_root() / "resources"

    @staticmethod
    def launch_agents_templates_dir() -> Path:
        return Paths.resources_dir() / "launchagents"

    @staticmethod
    def launch_agent_label(suffix: str) -> str:
        return f"{BUNDLE_ID}.{suffix}"

    @staticmethod
    def launch_agent_plist_name(suffix: str) -> str:
        return f"{Paths.launch_agent_label(suffix)}.plist"

    @staticmethod
    def launch_agent_user_path(suffix: str) -> Path:
        return Paths.user_launch_agents_dir() / Paths.launch_agent_plist_name(suffix)

