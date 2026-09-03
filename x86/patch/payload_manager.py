"""
payload_manager.py: Explicit mount/unmount for PatcherSupportPkg DMG resources.

Wraps ``opencore_legacy_patcher.sys_patch.utilities.dmg_mount.PatcherSupportPkgMount``
while sourcing version/URL configuration from ``x86.manifest`` and ``x86.settings``.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from x86 import manifest
from x86.paths import Paths
from x86.settings import SettingsStore

if TYPE_CHECKING:
    from opencore_legacy_patcher import constants


class PayloadManager:
    """
    Capsulates PatcherSupportPkg DMG lifecycle for root patching.

    Does not read OCLP plist for PatcherSupportPkg version — uses manifest.py
    and optional 26x86 JSON settings instead.
    """

    def __init__(
        self,
        global_constants: constants.Constants | None = None,
        settings: SettingsStore | None = None,
    ) -> None:
        if global_constants is None:
            from opencore_legacy_patcher import constants as constants_module

            global_constants = constants_module.Constants()

        self._constants = global_constants
        self._settings = settings or SettingsStore()

        from opencore_legacy_patcher.sys_patch.utilities.dmg_mount import PatcherSupportPkgMount

        self._mount_helper = PatcherSupportPkgMount(self._constants)
        self._mounted = False

    @property
    def constants(self):
        return self._constants

    @property
    def settings(self) -> SettingsStore:
        return self._settings

    def patcher_support_pkg_version(self) -> str:
        """
        Resolve PSP version from manifest / 26x86 JSON — never from OCLP plist keys.
        """
        if self._settings.read("force_latest_psp", False):
            return manifest.PATCHER_SUPPORT_PKG_VERSION

        override = self._settings.read("patcher_support_pkg_version")
        if override:
            return str(override)

        return manifest.PATCHER_SUPPORT_PKG_VERSION

    def universal_binaries_dmg_path(self) -> Path:
        """Return the DMG path to mount: bundled copy first, then user cache."""
        bundled = Paths.universal_binaries_dmg()
        if bundled.exists():
            return bundled

        cached = Paths.cached_universal_binaries_dmg(self.patcher_support_pkg_version())
        if cached.exists():
            return cached

        return bundled

    def universal_binaries_url(self) -> str:
        return manifest.patcher_support_pkg_dmg_url(self.patcher_support_pkg_version())

    def is_mounted(self) -> bool:
        return Paths.universal_binaries_mount().exists()

    def mount_support_pkg(self) -> Path:
        """
        Mount PatcherSupportPkg Universal-Binaries (and internal overlay when applicable).

        Returns the mount point path on success.
        """
        mount_point = Paths.universal_binaries_mount()
        if self.is_mounted():
            self._mounted = True
            return mount_point

        if not self._mount_helper.mount():
            raise RuntimeError(
                "Failed to mount PatcherSupportPkg resources "
                f"(expected DMG at {self.universal_binaries_dmg_path()})"
            )

        self._mounted = True
        logging.info("- PayloadManager mounted PatcherSupportPkg at %s", mount_point)
        return mount_point

    def unmount(self) -> None:
        """Detach Universal-Binaries DMG and remove overlay shadow file."""
        overlay_path = Paths.universal_binaries_overlay()
        mount_path = Paths.universal_binaries_mount()

        if overlay_path.exists():
            overlay_path.unlink(missing_ok=True)

        if mount_path.exists():
            result = subprocess.run(
                ["/usr/bin/hdiutil", "detach", str(mount_path), "-force"],
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                logging.debug(
                    "hdiutil detach returned %s for %s",
                    result.returncode,
                    mount_path,
                )

        internal_mount = Paths.internal_resources_mount()
        if internal_mount.exists():
            subprocess.run(
                ["/usr/bin/hdiutil", "detach", str(internal_mount), "-force"],
                capture_output=True,
                check=False,
            )

        self._mounted = False
        logging.info("- PayloadManager unmounted PatcherSupportPkg resources")

    def resolve_kext(self, name: str) -> Path:
        """
        Resolve a payload file or directory under the mounted Universal-Binaries tree.

        ``name`` may be a bare filename (e.g. ``AppleHDA.kext``) or a relative path.
        """
        root = Paths.universal_binaries_mount()
        if not root.exists():
            raise RuntimeError("PatcherSupportPkg is not mounted; call mount_support_pkg() first")

        candidate = root / name
        if candidate.exists():
            return candidate

        matches = sorted(root.rglob(name))
        if matches:
            return matches[0]

        raise FileNotFoundError(f"Payload resource not found under Universal-Binaries: {name}")

    def mount(self) -> bool:
        """
        Backward-compatible mount API (returns bool like PatcherSupportPkgMount.mount).

        Prefer ``mount_support_pkg()`` for new code.
        """
        try:
            self.mount_support_pkg()
            return True
        except RuntimeError:
            return False
