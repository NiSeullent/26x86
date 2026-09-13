"""
Track N stage sidecar (``non_metal.py.stage-N``).
MC integrate copies this over shared ``non_metal.py`` — do not edit the
in-tree shared file from Track N (file-monopoly ban).

Tahoe default remains ``{}`` without opt-in; opt-in via
``X86_TAHOE_NONMETAL=1`` or ``X86_EXTREME=1`` refills ``Non-Metal Common``
through ``filter_nonmetal_tahoe_patches`` (stage=common).
See ``x86.graphics.nonmetal_tahoe``.
"""
from .base import BaseSharedPatchSet

from ..base import PatchType

from ....datasets.os_data import os_data


class NonMetal(BaseSharedPatchSet):

    def __init__(self, xnu_major: int, xnu_minor: int, marketing_version: str) -> None:
        super().__init__(xnu_major, xnu_minor, marketing_version)


    def _os_requires_patches(self) -> bool:
        """
        Dropped support with macOS 10.14, Mojave
        """
        return self._xnu_major >= os_data.mojave.value


    def patches(self) -> dict:
        """
        General non-Metal GPU patches
        """
        if self._os_requires_patches() is False:
            return {}

        base = {
            "Non-Metal Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "IOSurface.kext": "10.15.7",
                    },
                    "/System/Applications": {
                        **({ "Photo Booth.app": "11.7.9"} if self._xnu_major >= os_data.monterey else {}),
                    },
                    "/usr/sbin": {
                        **({ "screencapture": "14.7"} if self._xnu_major >= os_data.sequoia else {}),
                    },
                    "/System/Library/CoreServices/RemoteManagement": {
                        **({"ScreensharingAgent.bundle": "14.7.2"} if self._xnu_major >= os_data.sequoia else {}),
                        **({"screensharingd.bundle":     "14.7.2"} if self._xnu_major >= os_data.sequoia else {}),
                        **({"SSMenuAgent.app":           "14.7.2"} if self._xnu_major >= os_data.sequoia else {}),
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        "AMDRadeonX4000.kext",
                        "AMDRadeonX4000HWServices.kext",
                        "AMDRadeonX5000.kext",
                        "AMDRadeonX5000HWServices.kext",
                        "AMDRadeonX6000.kext",
                        "AMDRadeonX6000Framebuffer.kext",
                        "AMDRadeonX6000HWServices.kext",
                        "AppleIntelBDWGraphics.kext",
                        "AppleIntelBDWGraphicsFramebuffer.kext",
                        "AppleIntelCFLGraphicsFramebuffer.kext",
                        "AppleIntelHD4000Graphics.kext",
                        "AppleIntelHD5000Graphics.kext",
                        "AppleIntelICLGraphics.kext",
                        "AppleIntelICLLPGraphicsFramebuffer.kext",
                        "AppleIntelKBLGraphics.kext",
                        "AppleIntelKBLGraphicsFramebuffer.kext",
                        "AppleIntelSKLGraphics.kext",
                        "AppleIntelSKLGraphicsFramebuffer.kext",
                        "AppleIntelFramebufferAzul.kext",
                        "AppleIntelFramebufferCapri.kext",
                        "AppleParavirtGPU.kext",
                        "GeForce.kext",
                        "IOAcceleratorFamily2.kext",
                        "IOGPUFamily.kext",
                        "AppleAfterburner.kext",
                    ],
                    "/System/Library/ExtensionKit/Extensions/": [
                        "WallpaperMacintoshExtension.appex"
                    ],
                },
                PatchType.OVERWRITE_DATA_VOLUME: {
                    "/Library/Application Support/SkyLightPlugins": {
                        **({ "DropboxHack.dylib": "SkyLightPlugins" } if self._xnu_major >= os_data.monterey else {}),
                        **({ "DropboxHack.txt":   "SkyLightPlugins" } if self._xnu_major >= os_data.monterey else {}),
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    # Note: PatcherSupportPkg only ships payloads up to xnu_major 24 (Sequoia)
                    # for these four folders; there is no "-25" (Tahoe) variant yet, so
                    # anything on Tahoe or newer is capped to the last known-good "-24"
                    # payload instead of looking up a folder that doesn't exist. Mirrors the
                    # existing "12.5-24" capping in intel_broadwell.py/intel_skylake.py.
                    "/System/Library/Frameworks": {
                        "OpenGL.framework":       "10.14.3",
                        "CoreDisplay.framework": "10.14.4-24" if self._xnu_major >= os_data.tahoe.value else f"10.14.4-{self._xnu_major}",
                        "IOSurface.framework":   "10.15.7-24" if self._xnu_major >= os_data.tahoe.value else f"10.15.7-{self._xnu_major}",
                        "QuartzCore.framework":  "10.15.7-24" if self._xnu_major >= os_data.tahoe.value else f"10.15.7-{self._xnu_major}",
                    },
                    "/System/Library/PrivateFrameworks": {
                        "GPUSupport.framework": "10.14.3",
                        "SkyLight.framework":  "10.14.6-24" if self._xnu_major >= os_data.tahoe.value else f"10.14.6-{self._xnu_major}",
                        **({"FaceCore.framework":  f"13.5"} if self._xnu_major >= os_data.sonoma else {}),
                    },
                },
                PatchType.EXECUTE: {
                    # 'When Space Allows' option introduced in 12.4 (XNU 21.5)
                    **({"/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist ShowDate -int 1": True } if self._xnu_float >= self.macOS_12_4 else {}),
                    "/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist InternalDebugUseGPUProcessForCanvasRenderingEnabled -bool false": True,
                    "/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist WebKitExperimentalUseGPUProcessForCanvasRenderingEnabled -bool false": True,
                    **({"/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist WebKitPreferences.acceleratedDrawingEnabled -bool false": True} if self._xnu_major >= os_data.sonoma else {}),
                    **({"/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist NSEnableAppKitMenus -bool false": True} if self._xnu_major >= os_data.sonoma else {}),
                    **({"/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist NSZoomButtonShowMenu -bool false": True} if self._xnu_major == os_data.sonoma else {}),
                },
            },
        }

        if self._xnu_major < os_data.tahoe.value:
            return base

        # Track N — opt-in refill (X86_TAHOE_NONMETAL / X86_EXTREME). Default stays {}.
        from x86.graphics.nonmetal_tahoe import filter_nonmetal_tahoe_patches

        return filter_nonmetal_tahoe_patches(base, xnu_major=self._xnu_major)
