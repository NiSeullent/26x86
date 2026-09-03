"""
tahoe_yellow_screen.py: Tahoe WindowServer / ColorSync compositor mitigations.

Does not lift Metal 3802 / Non-Metal shared guards (those panic on Tahoe).
Does not inject guessed CoreDisplay/SkyLight bytes. Optional overlay kexts
from PatcherSupportPkg 12.5-25+ are merged at DMG mount time.
"""

from pathlib import Path

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data

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
        return {TAHOE_YELLOW_SCREEN_PATCH_NAME: body}

    def _optional_overlay_payloads(self) -> dict:
        """
        Install files only when the community overlay actually contains them.

        Expected PSP layout under Universal-Binaries/<version>/...
        SkyLight dylibs (if a future evidence-based plugin is dropped in):
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
            files = {
                path.name: "SkyLightPlugins"
                for path in skylight_src.iterdir()
                if path.is_file() and path.suffix in {".dylib", ".txt"}
            }
            if files:
                merge[PatchType.OVERWRITE_DATA_VOLUME] = {
                    "/Library/Application Support/SkyLightPlugins": files,
                }

        return merge


def compositor_patches(xnu_major: int, xnu_minor: int, marketing_version: str) -> dict:
    return TahoeYellowScreen(xnu_major, xnu_minor, marketing_version).patches()
