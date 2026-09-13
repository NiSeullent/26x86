"""
Track N stage sidecar (``non_metal_coredisplay.py.stage-N``).
MC integrate copies this over shared ``non_metal_coredisplay.py`` — do not edit the
in-tree shared file from Track N (file-monopoly ban).

Tahoe default remains ``{}`` without opt-in; opt-in via
``X86_TAHOE_NONMETAL=1`` or ``X86_EXTREME=1`` refills ``Non-Metal CoreDisplay Common``
through ``filter_nonmetal_tahoe_patches`` (stage=coredisplay).
See ``x86.graphics.nonmetal_tahoe``.
"""
from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetalCoreDisplay(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        Nvidia Web Drivers require an older build of CoreDisplay
        """
        if self._os_requires_patches() is False:
            return {}

        base = {
            "Non-Metal CoreDisplay Common": {
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        # Note: PatcherSupportPkg only ships 10.13.6-<xnu_major> payloads up to xnu_major 24 (Sequoia),
                        # cap the lookup there for Sequoia+ hosts (e.g. Tahoe) instead of requesting a non-existent folder.
                        "CoreDisplay.framework": f"10.13.6-{self._xnu_major}" if self._xnu_major < os_data.sequoia.value else "10.13.6-24",
                    },
                },
            },
        }

        if self._xnu_major < os_data.tahoe.value:
            return base

        # Track N — opt-in refill (X86_TAHOE_NONMETAL / X86_EXTREME). Default stays {}.
        from x86.graphics.nonmetal_tahoe import filter_nonmetal_tahoe_patches

        return filter_nonmetal_tahoe_patches(base, xnu_major=self._xnu_major)
