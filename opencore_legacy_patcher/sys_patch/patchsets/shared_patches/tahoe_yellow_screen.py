"""
tahoe_yellow_screen.py: Tahoe WindowServer / ColorSync compositor mitigations.

Does not lift Metal 3802 / Non-Metal shared guards (those panic on Tahoe).
Does not inject guessed CoreDisplay/SkyLight bytes. SkyLightPlugins installs
only SHA-pinned compositor stems (stock Tahoe SkyLight ignores the folder).
Optional overlay kexts / RenderBox-25 from PatcherSupportPkg are merged at
DMG mount time.
"""

from pathlib import Path

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data

from x86.graphics.skylight_lut import enumerate_evidence_skylight_plugins
from x86.graphics.yellow_screen import (
    TAHOE_YELLOW_SCREEN_PATCH_NAME,
    community_yellow_screen_overlay,
)


class TahoeYellowScreen(BaseSharedPatchSet):
    """Root-patch marker + optional overlay files for compositor yellow screen."""

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)

    def _os_requires_patches(self) -> bool:
        return self._xnu_major >= os_data.tahoe.value

    def patches(self) -> dict:
        if self._os_requires_patches() is False:
            return {}

        body: dict = {}
        overlay_merge = self._optional_overlay_payloads()
        if overlay_merge:
            body.update(overlay_merge)

        # Track G: merge B/C/E/F sys_patch_hooks (missing → no-op).
        from x86.graphics.skylight_tracks import merge_sys_patch_hooks

        track_hooks = merge_sys_patch_hooks(
            self._xnu_major,
            self._xnu_minor,
            self._marketing_version,
        )
        result: dict = {TAHOE_YELLOW_SCREEN_PATCH_NAME: body}
        for key, value in track_hooks.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = {**result[key], **value}
            else:
                result[key] = value
        return result

    def _optional_overlay_payloads(self) -> dict:
        """
        Install files only when the community overlay actually contains them.

        Expected PSP layout under Universal-Binaries/<version>/...
        SkyLight dylibs (SHA-pinned compositor stems only):
        SkyLightPlugins/Library/Application Support/SkyLightPlugins/*.dylib
        """
        overlay = community_yellow_screen_overlay()
        merge: dict = {}

        skylight_src = (
            overlay
            / "SkyLightPlugins"
            / "Library"
            / "Application Support"
            / "SkyLightPlugins"
        )
        if skylight_src.is_dir():
            files = enumerate_evidence_skylight_plugins(skylight_src)
            if files:
                merge[PatchType.OVERWRITE_DATA_VOLUME] = {
                    "/Library/Application Support/SkyLightPlugins": files,
                }

        return merge


def compositor_patches(xnu_major: int, xnu_minor: int, marketing_version: str) -> dict:
    return TahoeYellowScreen(xnu_major, xnu_minor, marketing_version).patches()
