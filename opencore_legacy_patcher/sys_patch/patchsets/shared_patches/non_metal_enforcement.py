"""
Track N stage sidecar (``non_metal_enforcement.py.stage-N``).
MC integrate copies this over shared ``non_metal_enforcement.py`` — do not edit the
in-tree shared file from Track N (file-monopoly ban).

Tahoe default remains ``{}`` without opt-in; opt-in via
``X86_TAHOE_NONMETAL=1`` or ``X86_EXTREME=1`` plus
``X86_TAHOE_NONMETAL_ENFORCEMENT=1`` refills ``Non-Metal Enforcement``
through ``filter_nonmetal_tahoe_patches`` (stage=enforcement).
See ``x86.graphics.nonmetal_tahoe``.
"""

from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetalEnforcement(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        Forces Metal kexts from High Sierra to run in the fallback non-Metal mode
        Verified functional with HD4000 and Iris Plus 655
        Only used for internal development purposes, not suitable for end users

        Note: Metal kexts in High Sierra rely on IOAccelerator, thus 'Non-Metal IOAccelerator Common'
        is needed for proper linking

        Tahoe: default ``{}``. Track N opt-in + ENFORCEMENT flag reactivates via filter.
        """
        if self._os_requires_patches() is False:
            return {}

        base = {
            "Non-Metal Enforcement": {
                PatchType.EXECUTE: {
                    "/usr/bin/defaults write /Library/Preferences/com.apple.CoreDisplay useMetal -boolean no": True,
                    "/usr/bin/defaults write /Library/Preferences/com.apple.CoreDisplay useIOP -boolean no":   True,
                },
            },
        }

        if self._xnu_major < os_data.tahoe.value:
            return base

        # Track N — opt-in refill (X86_TAHOE_NONMETAL / X86_EXTREME + ENFORCEMENT).
        from x86.graphics.nonmetal_tahoe import filter_nonmetal_tahoe_patches

        return filter_nonmetal_tahoe_patches(base, xnu_major=self._xnu_major)
