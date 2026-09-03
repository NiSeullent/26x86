"""
Track N stage sidecar (``non_metal_ioaccel.py.stage-N``).
MC integrate copies this over shared ``non_metal_ioaccel.py`` — do not edit the
in-tree shared file from Track N (file-monopoly ban).

Tahoe default remains ``{}`` without opt-in; opt-in via
``X86_TAHOE_NONMETAL=1`` or ``X86_EXTREME=1`` refills ``Non-Metal IOAccelerator Common``
through ``filter_nonmetal_tahoe_patches`` (stage=ioaccel).
See ``x86.graphics.nonmetal_tahoe``.
"""
from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetalIOAccelerator(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        TeraScale 2 and Nvidia Web Drivers broke in Mojave due to mismatched structs in
        the IOAccelerator stack
        """
        if self._os_requires_patches() is False:
            return {}

        base = {
            "Non-Metal IOAccelerator Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "IOAcceleratorFamily2.kext":     "10.13.6",
                        "IOSurface.kext":                "10.14.6",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        # Note: PatcherSupportPkg only ships 10.14.6-<xnu_major> / 10.13.6-<xnu_major> payloads up to
                        # xnu_major 24 (Sequoia), cap the lookup there for Sequoia+ hosts (e.g. Tahoe) instead of
                        # requesting a non-existent folder.
                        "IOSurface.framework": f"10.14.6-{self._xnu_major}" if self._xnu_major < os_data.sequoia.value else "10.14.6-24",
                        "OpenCL.framework":     "10.13.6",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "GPUSupport.framework":     "10.13.6",
                        "IOAccelerator.framework": f"10.13.6-{self._xnu_major}" if self._xnu_major < os_data.sequoia.value else "10.13.6-24",
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        "AppleCameraInterface.kext"
                    ],
                },
            },
        }

        if self._xnu_major < os_data.tahoe.value:
            return base

        # Track N — opt-in refill (X86_TAHOE_NONMETAL / X86_EXTREME). Default stays {}.
        from x86.graphics.nonmetal_tahoe import filter_nonmetal_tahoe_patches

        return filter_nonmetal_tahoe_patches(base, xnu_major=self._xnu_major)
