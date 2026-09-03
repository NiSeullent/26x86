"""Sequoia vs Tahoe host-gate fixtures for ``x86.graphics.tahoe_gate``."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.tahoe_gate import (  # noqa: E402
    ENV_EXTREME,
    ENV_TAHOE_3802,
    ENV_TAHOE_NONMETAL,
    SEQUOIA_PRODUCT_MAJOR,
    SEQUOIA_XNU_MAJOR,
    TAHOE_PRODUCT_MAJOR,
    TAHOE_XNU_MAJOR,
    HostOsInfo,
    detect_flashed_mac_pro,
    is_tahoe,
    metal3802_root_unlocked,
    nonmetal_root_unlocked,
    probe_host_os,
    root_patches_allowed,
    serialize_root_patch_gates,
)

# Compact per-test fixtures (no shared mega-dicts).
_SEQUOIA = {"xnu_major": SEQUOIA_XNU_MAJOR, "product_version": "15.5"}
_TAHOE = {"xnu_major": TAHOE_XNU_MAJOR, "product_version": "26.0"}


class IsTahoeFixtureTest(unittest.TestCase):
    def test_sequoia_xnu_and_product(self) -> None:
        self.assertFalse(is_tahoe(**_SEQUOIA))
        self.assertFalse(is_tahoe(xnu_major=SEQUOIA_XNU_MAJOR))
        self.assertFalse(is_tahoe(product_version="15.7.1"))
        self.assertEqual(SEQUOIA_PRODUCT_MAJOR, 15)

    def test_tahoe_xnu_and_product(self) -> None:
        self.assertTrue(is_tahoe(**_TAHOE))
        self.assertTrue(is_tahoe(xnu_major=TAHOE_XNU_MAJOR))
        self.assertTrue(is_tahoe(product_version="26.0"))
        self.assertTrue(is_tahoe(os_version="26.1"))
        self.assertEqual(TAHOE_PRODUCT_MAJOR, 26)

    def test_assume_tahoe_overrides(self) -> None:
        self.assertTrue(is_tahoe(assume_tahoe=True, **_SEQUOIA))

    def test_root_patches_mirror_is_tahoe(self) -> None:
        self.assertFalse(root_patches_allowed(**_SEQUOIA))
        self.assertTrue(root_patches_allowed(**_TAHOE))


class ExtremeOptInGateTest(unittest.TestCase):
    def test_sequoia_extreme_does_not_unlock_root(self) -> None:
        env = {ENV_EXTREME: "1"}
        self.assertFalse(
            metal3802_root_unlocked(**_SEQUOIA, environ=env)
        )
        self.assertFalse(
            nonmetal_root_unlocked(**_SEQUOIA, environ=env)
        )

    def test_tahoe_extreme_unlocks(self) -> None:
        env = {ENV_EXTREME: "1"}
        self.assertTrue(metal3802_root_unlocked(**_TAHOE, environ=env))
        self.assertTrue(nonmetal_root_unlocked(**_TAHOE, environ=env))

    def test_tahoe_track_flags(self) -> None:
        self.assertTrue(
            metal3802_root_unlocked(
                **_TAHOE, environ={ENV_TAHOE_3802: "1"}
            )
        )
        self.assertTrue(
            nonmetal_root_unlocked(
                **_TAHOE, environ={ENV_TAHOE_NONMETAL: "1"}
            )
        )
        self.assertFalse(
            metal3802_root_unlocked(**_TAHOE, environ={})
        )


class SerializeAndProbeTest(unittest.TestCase):
    def test_serialize_sequoia_reason(self) -> None:
        fields = serialize_root_patch_gates(
            **_SEQUOIA, environ={ENV_EXTREME: "1"}
        )
        self.assertFalse(fields["is_tahoe"])
        self.assertFalse(fields["root_patches_allowed"])
        self.assertTrue(fields["extreme_env"])
        self.assertFalse(fields["metal3802_root_unlocked"])
        self.assertIn("not Tahoe", fields["reason"])

    def test_serialize_tahoe_reason(self) -> None:
        fields = serialize_root_patch_gates(
            **_TAHOE, environ={ENV_EXTREME: "1"}
        )
        self.assertTrue(fields["is_tahoe"])
        self.assertTrue(fields["root_patches_allowed"])
        self.assertTrue(fields["metal3802_root_unlocked"])

    def test_probe_explicit_args(self) -> None:
        info = probe_host_os(
            xnu_major=SEQUOIA_XNU_MAJOR, product_version="15.5"
        )
        self.assertIsInstance(info, HostOsInfo)
        self.assertFalse(info.is_tahoe)
        info_t = probe_host_os(
            xnu_major=TAHOE_XNU_MAJOR, product_version="26.0"
        )
        self.assertTrue(info_t.is_tahoe)


class FlashedMacProFixtureTest(unittest.TestCase):
    def test_macpro71_westmere_flash(self) -> None:
        hit = detect_flashed_mac_pro(
            reported_model="MacPro7,1",
            real_model="MacPro5,1",
            cpu_brand="Intel(R) Xeon(R) CPU X5675 @ 3.07GHz",
            smc_version="1.39f11",
        )
        self.assertTrue(hit["flashed_mac_pro"])
        self.assertTrue(hit["classic_macpro_smc"])
        self.assertTrue(hit["westmere_class_cpu"])

    def test_native_imac_not_flash(self) -> None:
        miss = detect_flashed_mac_pro(
            reported_model="iMac18,3",
            real_model="iMac18,3",
            cpu_brand="Intel(R) Core(TM) i5-7500 CPU @ 3.40GHz",
            smc_version="2.41f2",
        )
        self.assertFalse(miss["flashed_mac_pro"])


if __name__ == "__main__":
    unittest.main()
