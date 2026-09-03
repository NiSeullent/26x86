"""Unit tests for Tahoe yellow-screen / compositor detect fields."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.detect import TAHOE_XNU_MAJOR, serialize_graphics_detect_fields  # noqa: E402
from x86.graphics.yellow_screen import (  # noqa: E402
    classify_gpu_family,
    recommended_efi_graphics_fixes,
    yellow_screen_risk,
)

from opencore_legacy_patcher.efi_builder.gcn_agdp import (  # noqa: E402
    SOCKET_AMD_AGDP_MODELS,
    apply_gcn_agdp_fallbacks,
    boot_args_need_gcn_agdp,
    config_has_agdpmod,
)


class YellowScreenDetectTest(unittest.TestCase):
    def test_macpro61_gcn_recommends_agdpmod(self) -> None:
        self.assertIn("agdpmod", recommended_efi_graphics_fixes("MacPro6,1"))
        self.assertTrue(
            yellow_screen_risk("MacPro6,1", xnu_major=TAHOE_XNU_MAJOR, agdpmod_present=False)
        )

    def test_macpro51_vega64_yellow_screen_risk(self) -> None:
        gpus = ["Vega", "RX Vega 64"]
        self.assertEqual(classify_gpu_family("MacPro5,1", gpus), "vega")
        self.assertIn("agdpmod", recommended_efi_graphics_fixes("MacPro5,1", gpus))
        self.assertIn("shikigva", recommended_efi_graphics_fixes("MacPro5,1", gpus))
        self.assertTrue(
            yellow_screen_risk(
                "MacPro5,1",
                gpu_archs=gpus,
                xnu_major=TAHOE_XNU_MAJOR,
                agdpmod_present=False,
            )
        )
        payload = serialize_graphics_detect_fields(
            "MacPro5,1",
            xnu_major=TAHOE_XNU_MAJOR,
            gpu_archs=gpus,
        )
        self.assertEqual(payload["gpu_family"], "vega")
        self.assertTrue(payload["yellow_screen_risk"])
        self.assertIn("agdpmod", payload["recommended_efi_graphics_fixes"])

    def test_polaris_rx570_also_flagged(self) -> None:
        self.assertTrue(
            yellow_screen_risk(
                "MacPro5,1",
                gpu_archs=["Polaris"],
                xnu_major=TAHOE_XNU_MAJOR,
            )
        )
        self.assertEqual(classify_gpu_family("MacPro5,1", ["Polaris"]), "polaris")

    def test_imac183_not_flagged_without_legacy_amd(self) -> None:
        self.assertFalse(
            yellow_screen_risk("iMac18,3", gpu_archs=["Intel"], xnu_major=TAHOE_XNU_MAJOR)
        )
        self.assertEqual(recommended_efi_graphics_fixes("iMac18,3", ["Intel"]), [])


class EfiAgdpFallbackTest(unittest.TestCase):
    def test_macpro51_in_socket_agdp_models(self) -> None:
        self.assertIn("MacPro5,1", SOCKET_AMD_AGDP_MODELS)
        self.assertIn("MacPro6,1", SOCKET_AMD_AGDP_MODELS)

    def test_apply_gcn_agdp_fallbacks_sets_agdpmod_and_shikigva(self) -> None:
        config: dict = {}
        apply_gcn_agdp_fallbacks(config)
        self.assertTrue(config_has_agdpmod(config))
        boot = config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]
        self.assertIn("agdpmod=", boot)
        self.assertIn("shikigva=", boot)
        props = next(iter(config["DeviceProperties"]["Add"].values()))
        self.assertEqual(props.get("agdpmod"), "pikera")
        self.assertEqual(props.get("shikigva"), 128)

    def test_boot_args_need_gcn_agdp_skips_when_present(self) -> None:
        self.assertEqual(boot_args_need_gcn_agdp("agdpmod=pikera shikigva=128"), [])


if __name__ == "__main__":
    unittest.main()
