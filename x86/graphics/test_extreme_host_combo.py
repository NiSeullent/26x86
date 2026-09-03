"""Combo fixtures: Sequoia no-op vs Tahoe+flags dict charge (mock host)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType  # noqa: E402
from x86.graphics.metal3802_tahoe import (  # noqa: E402
    ALL_SLICES,
    ENV_EXTREME,
    ENV_TAHOE_3802,
    PATCH_KEY_BY_SLICE,
    filter_tahoe_3802_patches,
)
from x86.graphics.nonmetal_tahoe import (  # noqa: E402
    ENV_IOSURFACE_CA,
    ENV_NONMETAL,
    H_PREFERRED_IOSURFACE_FRAMEWORK,
    H_PREFERRED_IOSURFACE_KEXT,
    filter_nonmetal_tahoe_patches,
    h_iosurface_latch_on,
    prefer_h_iosurface_versions,
)
from x86.graphics.skylight_lut_rootpatch import (  # noqa: E402
    ENV_EXTREME as L5_EXTREME,
    PATCH_NAME as L5_PATCH,
    sys_patch_hooks as l5_hooks,
)
from x86.graphics.interpose_plan import root_volume_interpose_recipe  # noqa: E402
from x86.graphics.yellow_screen import yellow_screen_mitigations  # noqa: E402
from x86.graphics.tahoe_gate import (  # noqa: E402
    detect_flashed_mac_pro,
    is_tahoe,
    serialize_root_patch_gates,
)
from x86.profiles.fixtures import (  # noqa: E402
    VEGA64_DEVICE_ID,
    macpro5_vega64_detect_kwargs,
    matches_macpro5_vega64_profile,
)


_SEQUOIA = {"xnu_major": 24, "product_version": "15.5"}
_TAHOE = {"xnu_major": 25, "product_version": "26.0"}


class PreAvxMacProVegaComboTest(unittest.TestCase):
    def test_fixture_kwargs_pre_avx_vega(self) -> None:
        kw = macpro5_vega64_detect_kwargs()
        self.assertEqual(kw["model"], "MacPro5,1")
        self.assertEqual(kw["xnu_major"], 25)
        self.assertFalse(any(f.upper() == "AVX" for f in kw["cpu_features"]))
        gpu = kw["gpus"][0]
        self.assertEqual(gpu.device_id, VEGA64_DEVICE_ID)

    def test_flashed_macpro71_plus_vega_match(self) -> None:
        flash = detect_flashed_mac_pro(
            reported_model="MacPro7,1",
            real_model="MacPro5,1",
            cpu_brand="Intel(R) Xeon(R) CPU X5675 @ 3.07GHz",
            smc_version="1.39f11",
        )
        self.assertTrue(flash["flashed_mac_pro"])
        self.assertTrue(
            matches_macpro5_vega64_profile(
                model="MacPro5,1",
                gpu_family="vega",
                avx_available=False,
                pre_avx_mac_pro=True,
            )
        )


class SequoiaNoOpVsTahoeChargeTest(unittest.TestCase):
    def test_metal3802(self) -> None:
        patches = {PATCH_KEY_BY_SLICE[s]: {"n": s} for s in ALL_SLICES}
        self.assertEqual(
            filter_tahoe_3802_patches(
                patches, xnu_major=24, environ={ENV_EXTREME: "1"}
            ),
            {},
        )
        out = filter_tahoe_3802_patches(
            patches, xnu_major=25, environ={ENV_TAHOE_3802: "1"}
        )
        self.assertTrue(out)

    def test_nonmetal(self) -> None:
        base = {"Non-Metal Common": {"body": True}}
        self.assertEqual(
            filter_nonmetal_tahoe_patches(
                base, xnu_major=24, environ={ENV_NONMETAL: "1"}
            ),
            {},
        )
        self.assertIn(
            "Non-Metal Common",
            filter_nonmetal_tahoe_patches(
                base, xnu_major=25, environ={ENV_NONMETAL: "1"}
            ),
        )

    def test_l5_overwrite(self) -> None:
        self.assertEqual(l5_hooks(24, 0, "15.5", environ={L5_EXTREME: "1"}), {})
        hooks = l5_hooks(25, 0, "26.0", environ={L5_EXTREME: "1"})
        self.assertIn(L5_PATCH, hooks)
        self.assertIn(PatchType.OVERWRITE_SYSTEM_VOLUME, hooks[L5_PATCH])

    def test_yellow_mitigations(self) -> None:
        self.assertEqual(
            yellow_screen_mitigations(
                "MacPro5,1", gpu_archs=["Vega"], xnu_major=24
            ),
            [],
        )
        items = yellow_screen_mitigations(
            "MacPro5,1", gpu_archs=["Vega"], xnu_major=25
        )
        self.assertIn("window_server_cache_disable", items)
        self.assertIn("agdpmod", items)

    def test_interpose_sequoia_blocked(self) -> None:
        with mock.patch.dict("os.environ", {ENV_EXTREME: "1"}, clear=False):
            with mock.patch(
                "x86.graphics.interpose_gate.host_is_tahoe_for_root",
                return_value=False,
            ):
                self.assertEqual(root_volume_interpose_recipe(repo_root=REPO), {})

    def test_gates_serialize(self) -> None:
        seq = serialize_root_patch_gates(**_SEQUOIA, environ={ENV_EXTREME: "1"})
        tah = serialize_root_patch_gates(**_TAHOE, environ={ENV_EXTREME: "1"})
        self.assertFalse(seq["root_patches_allowed"])
        self.assertTrue(tah["metal3802_root_unlocked"])
        self.assertTrue(is_tahoe(**_TAHOE))


class HnIosurfacePreferTest(unittest.TestCase):
    def _ioaccel_base(self) -> dict:
        return {
            "Non-Metal IOAccelerator Common": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {"IOSurface.kext": "10.14.6"},
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/Frameworks": {
                        "IOSurface.framework": "10.14.6-24"
                    },
                },
            },
            "Non-Metal Common": {"ok": True},
        }

    def test_latch_detect(self) -> None:
        self.assertFalse(h_iosurface_latch_on({ENV_EXTREME: "1"}))
        self.assertTrue(
            h_iosurface_latch_on({ENV_EXTREME: "1", ENV_IOSURFACE_CA: "1"})
        )

    def test_prefer_rewrite(self) -> None:
        rewritten = prefer_h_iosurface_versions(
            self._ioaccel_base(),
            environ={ENV_EXTREME: "1", ENV_IOSURFACE_CA: "1"},
        )
        ow = rewritten["Non-Metal IOAccelerator Common"][
            PatchType.OVERWRITE_SYSTEM_VOLUME
        ]
        self.assertEqual(
            ow["/System/Library/Extensions"]["IOSurface.kext"],
            H_PREFERRED_IOSURFACE_KEXT,
        )
        mg = rewritten["Non-Metal IOAccelerator Common"][
            PatchType.MERGE_SYSTEM_VOLUME
        ]
        self.assertEqual(
            mg["/System/Library/Frameworks"]["IOSurface.framework"],
            H_PREFERRED_IOSURFACE_FRAMEWORK,
        )

    def test_filter_applies_prefer(self) -> None:
        out = filter_nonmetal_tahoe_patches(
            self._ioaccel_base(),
            xnu_major=25,
            environ={ENV_EXTREME: "1", ENV_IOSURFACE_CA: "1"},
        )
        kext = out["Non-Metal IOAccelerator Common"][
            PatchType.OVERWRITE_SYSTEM_VOLUME
        ]["/System/Library/Extensions"]["IOSurface.kext"]
        self.assertEqual(kext, "10.15.7")


class ProfileExtremeDryRunTest(unittest.TestCase):
    def test_macpro5_vega64_tahoe_extreme(self) -> None:
        from x86.profiles.macpro5_vega64_tahoe import apply_profile

        report = apply_profile(
            dry_run=True,
            include_extreme=True,
            environ={"X86_EXTREME": "1"},
        )
        self.assertIn("extreme.hooks", report["order"])
        self.assertIn("efi.agdpmod_shikigva", report["order"])
        self.assertIn("efi.restrictevents_jsc", report["order"])


class EfiRestrictEventsPathTest(unittest.TestCase):
    def test_agdpmod_and_revpatch_jsc(self) -> None:
        from x86.profiles.macpro5_vega64_tahoe import apply_profile

        config: dict = {}
        apply_profile(config=config, dry_run=False, include_extreme=False)
        boot = config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"][
            "boot-args"
        ]
        self.assertIn("agdpmod=", boot)
        rev = config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"][
            "revpatch"
        ]
        self.assertIn("jsc", rev.split(","))
        bundles = {e["BundlePath"] for e in config["Kernel"]["Add"]}
        self.assertIn("RestrictEvents.kext", bundles)
        self.assertIn("KDKlessWorkaround.kext", bundles)


if __name__ == "__main__":
    unittest.main()
