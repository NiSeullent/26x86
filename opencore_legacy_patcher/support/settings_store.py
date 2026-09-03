"""
settings_store.py: Legacy shim during x86 migration.

New code should use ``x86.settings.SettingsStore`` (JSON at
``~/Library/Application Support/26x86/config.json``).

This module keeps the plist-based API for existing opencore_legacy_patcher imports.
"""

import logging
import os
import plistlib
import subprocess
from pathlib import Path
from typing import Any

from ..constants import Constants


def _resolve_preferences_path(domain: str) -> Path:
    """
    Resolve ~/Library/Preferences/<domain>.plist, using the console user when
    running as root (eg. LaunchDaemon).
    """
    home = Path.home()
    if home == Path("/var/root"):
        try:
            result = subprocess.run(
                ["/usr/bin/stat", "-f", "%Su", "/dev/console"],
                capture_output=True,
                text=True,
                check=True,
            )
            console_user = result.stdout.strip()
            if console_user and console_user != "root":
                user_home = Path(f"/Users/{console_user}")
                if user_home.is_dir():
                    return user_home / "Library" / "Preferences" / f"{domain}.plist"
        except (OSError, subprocess.CalledProcessError):
            pass
    return home / "Library" / "Preferences" / f"{domain}.plist"


class SettingsStore:
    """
    26x86-native settings storage.
    """

    def __init__(self, global_constants: Constants = None) -> None:
        self.constants: Constants = global_constants or Constants()
        self.preferences_path: Path = _resolve_preferences_path(self.constants.preferences_domain)

        self._ensure_settings_file()

    def _ensure_settings_file(self) -> None:
        path = self.preferences_path
        if path.is_symlink():
            try:
                path.unlink()
            except (PermissionError, OSError):
                return

        if path.exists():
            return

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as handle:
                plistlib.dump({"26x86": True}, handle)
            os.chmod(path, 0o600)
        except (PermissionError, OSError) as error:
            logging.debug(f"Unable to initialize settings file: {error}")

    def _read_plist(self) -> dict:
        path = self.preferences_path
        if path.is_symlink():
            logging.warning("Security Alert: Symlink detected during read. Ignoring.")
            return {}

        if not path.exists():
            return {}

        try:
            with path.open("rb") as handle:
                return plistlib.load(handle)
        except PermissionError:
            return {}
        except Exception as error:
            logging.error("Error: Unable to read settings file")
            logging.error(error)
            return {}

    def _write_plist(self, plist: dict) -> None:
        path = self.preferences_path
        if path.is_symlink():
            try:
                path.unlink()
            except (PermissionError, OSError):
                return

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as handle:
                plistlib.dump(plist, handle)
            os.chmod(path, 0o600)
        except PermissionError:
            pass
        except Exception as error:
            logging.error("Failed to write settings file")
            logging.error(error)

    def read(self, key: str) -> Any:
        """
        Read a property from the 26x86 settings plist.
        """
        return self._read_plist().get(key)

    def write(self, key: str, value: Any) -> None:
        """
        Write a property to the 26x86 settings plist.
        """
        plist = self._read_plist()
        plist[key] = value
        self._write_plist(plist)

    def delete(self, key: str) -> None:
        """
        Delete a property from the 26x86 settings plist.
        """
        plist = self._read_plist()
        if key not in plist:
            return
        del plist[key]
        self._write_plist(plist)
