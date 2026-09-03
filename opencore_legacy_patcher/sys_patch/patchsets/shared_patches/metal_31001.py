"""
metal_31001.py: Metal 31001 patches
"""

from pathlib import Path
from typing import Iterable, Optional

from .base import BaseSharedPatchSet

from ....datasets.os_data import os_data

from x86.graphics.skylight_lut import metal_31001_common_patches


class LegacyMetal31001(BaseSharedPatchSet):

    def __init__(
        self,
        xnu_major: int,
        xnu_minor: int,
        marketing_version: str,
        search_roots: Optional[Iterable[Path]] = None,
    ) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)
        self._search_roots = search_roots

    def _os_requires_patches(self) -> bool:
        """
        Check if the current OS requires
        """
        return self._xnu_major >= os_data.ventura.value

    def _patches_metal_31001_common(self) -> dict:
        """
        Intel Broadwell, Skylake, and AMD GCN/Polaris/Vega are Metal 31001.

        Upstream OCLP (PR #1176 / RenderBox metallib) overwrites
        RenderBox.framework ``default.metallib`` from ``RenderBox-<xnu>``.
        PatcherSupportPkg still often lacks ``RenderBox-25``; emitting the
        dict anyway fails preflight. Gate on file presence — no guessed bytes,
        and no Metal 3802 / Non-Metal Tahoe guard lift.
        """
        if self._os_requires_patches() is False:
            return {}
        return metal_31001_common_patches(
            self._xnu_major,
            search_roots=self._search_roots,
        )

    def patches(self) -> dict:
        """
        Dictionary of patches
        """
        return {
            **self._patches_metal_31001_common(),
        }
