"""
modern_audio.py: Modern Audio patch set for macOS 26
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants import Constants

from .....datasets.os_data import os_data


class ModernAudio(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Modern Audio"


    def present(self) -> bool:
        """
        AppleHDA was outright removed in macOS Tahoe, so this patch set is always present if OS requires it
        """
        if self._constants.allow_modern_audio is False:
            return False
        return True


    def native_os(self) -> bool:
        """
        - Everything before macOS Tahoe 26 is considered native
        - T2 Macs retain native (digital) audio routing under macOS Tahoe;
          Apple only removed AppleHDA-based analog audio routing for non-T2 Macs
        """
        if self._xnu_major < os_data.tahoe.value:
            return True

        # Technically, macOS Tahoe Beta 1 is also native, so return True
        if self._os_build == "25A5279m":
            return True

        # Non-T2 models (including T1 models like MacBookPro13,x and MacBookPro14,x)
        # require AppleHDA on macOS Tahoe even if spoofed to a T2 model.
        real_model = getattr(self._computer, "real_model", "")
        if self._computer.t2_chip is True and real_model not in ["MacBookPro14,3", "MacBookPro14,2", "MacBookPro14,1", "MacBookPro13,3", "MacBookPro13,2", "MacBookPro13,1"]:
            return True

        return False

    def requires_kernel_debug_kit(self) -> bool:
        """
        Apple no longer provides standalone kexts in the base OS
        """
        return True


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.MISCELLANEOUS


    def _modern_audio_patches(self) -> dict:
        """
        Patches for Modern Audio
        """
        return {
            "Modern Audio": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext":      "26.0 Beta 1",
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for modern audio
        """
        if self.native_os() is True:
            return {}

        return self._modern_audio_patches()
