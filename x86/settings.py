"""
settings.py: JSON-backed user settings for 26x86.

Settings live at ~/Library/Application Support/26x86/config.json.
OCLP plist values are never read for PatcherSupportPkg version or URLs.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from .manifest import PATCHER_SUPPORT_PKG_VERSION
from .paths import Paths

_DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "auto_patch": False,
    "verbose_logging": False,
    "migrated_from_oclp": False,
    "patcher_support_pkg_version": PATCHER_SUPPORT_PKG_VERSION,
    "force_latest_psp": False,
}


class SettingsStore:
    """
    Single JSON settings file for 26x86 user preferences.
    """

    def __init__(self, paths: Paths | None = None) -> None:
        self._paths = paths or Paths()
        self._config_path = self._paths.user_config

    @property
    def config_path(self) -> Path:
        return self._config_path

    def _ensure_parent(self) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        path = self._config_path
        if path.is_symlink():
            logging.warning("Security: refusing to read symlinked config at %s", path)
            return dict(_DEFAULT_CONFIG)

        if not path.exists():
            return dict(_DEFAULT_CONFIG)

        try:
            with path.open(encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict):
                return dict(_DEFAULT_CONFIG)
            merged = dict(_DEFAULT_CONFIG)
            merged.update(data)
            return merged
        except (OSError, json.JSONDecodeError) as error:
            logging.warning("Unable to read settings at %s: %s", path, error)
            return dict(_DEFAULT_CONFIG)

    def save(self, config: dict[str, Any]) -> None:
        path = self._config_path
        if path.is_symlink():
            logging.warning("Security: refusing to write symlinked config at %s", path)
            return

        self._ensure_parent()
        try:
            with path.open("w", encoding="utf-8") as handle:
                json.dump(config, handle, indent=2)
                handle.write("\n")
            os.chmod(path, 0o600)
        except OSError as error:
            logging.error("Failed to write settings to %s: %s", path, error)

    def get(self, key: str, default: Any = None) -> Any:
        return self.load().get(key, default)

    def set(self, key: str, value: Any) -> None:
        config = self.load()
        config[key] = value
        self.save(config)

    def patcher_support_pkg_version(self) -> str:
        """
        PatcherSupportPkg version from manifest defaults, overridable in JSON.

        Never reads OCLP plist keys.
        """
        return str(self.get("patcher_support_pkg_version", PATCHER_SUPPORT_PKG_VERSION))

    def force_latest_psp(self) -> bool:
        return bool(self.get("force_latest_psp", False))
