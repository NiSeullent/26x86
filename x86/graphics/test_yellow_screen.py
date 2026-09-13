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
    TAHOE_YELLOW_SCREEN_PATCH_NAME,
    classify_gpu_family,
    recommended_efi_graphics_fixes,
    resolve_legacy_amd_mtl_payload,
    should_disable_window_server_caching,
    socket_amd_needs_kdkless,
    yellow_screen_mitigations,
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


class CompositorMitigationTest(unittest.TestCase):
    def test_window_server_cache_keys_include_vega_and_polaris(self) -> None:
        self.assertTrue(should_disable_window_server_caching({"AMD Vega": {}}))
        self.assertTrue(should_disable_window_server_caching({"AMD Polaris": {}}))
        self.assertTrue(should_disable_window_server_caching({"AMD Legacy GCN": {}}))
        self.assertTrue(
            should_disable_window_server_caching({TAHOE_YELLOW_SCREEN_PATCH_NAME: {}})
        )
        self.assertFalse(should_disable_window_server_caching({"Modern Wireless": {}}))

    def test_kdkless_mac_pro_socket_not_imac_pro(self) -> None:
        self.assertTrue(socket_amd_needs_kdkless("MacPro5,1", cpu_generation=4))
        self.assertTrue(socket_amd_needs_kdkless("MacPro6,1", cpu_generation=6))
        self.assertFalse(socket_amd_needs_kdkless("iMacPro1,1", cpu_generation=9))
        self.assertFalse(socket_amd_needs_kdkless("iMac18,3", cpu_generation=6))

    def test_mitigations_listed_for_vega64_tahoe(self) -> None:
        items = yellow_screen_mitigations(
            "MacPro5,1",
            gpu_archs=["Vega", "0x687F"],
            xnu_major=TAHOE_XNU_MAJOR,
            cpu_generation=4,
        )
        self.assertIn("window_server_cache_disable", items)
        self.assertIn("colorsync_srgb_fallback", items)
        self.assertIn("kdkless_workaround", items)
        self.assertIn("agdpmod", items)

    def test_psp_prefers_12_5_25_when_overlay_has_bundle(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = (
                root
                / "12.5-25"
                / "System"
                / "Library"
                / "Extensions"
                / "AMDRadeonX5000MTLDriver.bundle"
            )
            bundle.mkdir(parents=True)
            (bundle / "Contents").mkdir()
            self.assertEqual(
                resolve_legacy_amd_mtl_payload(
                    TAHOE_XNU_MAJOR,
                    bundle_name="AMDRadeonX5000MTLDriver.bundle",
                    search_roots=[root],
                ),
                "12.5-25",
            )
            self.assertEqual(
                resolve_legacy_amd_mtl_payload(
                    TAHOE_XNU_MAJOR,
                    bundle_name="AMDRadeonX5000MTLDriver.bundle",
                    search_roots=[root / "missing"],
                ),
                "12.5-24",
            )


class RootPatchDictFixtureTest(unittest.TestCase):
    """Tahoe patch dicts include compositor mitigations for Vega / Polaris / GCN."""

    def _constants(self, model: str, gpu):
        from opencore_legacy_patcher.constants import Constants
        from opencore_legacy_patcher.detections.device_probe import CPU, Computer

        constants = Constants()
        computer = Computer()
        computer.real_model = model
        computer.rosetta_active = False
        computer.cpu = CPU(name="Xeon", flags=["AVX1.0"], leafs=[])
        computer.gpus = [gpu]
        constants.computer = computer
        constants.detected_os_version = "26.0"
        constants.detected_os = TAHOE_XNU_MAJOR
        return constants

    def _amd(self, device_id: int):
        from opencore_legacy_patcher.detections.device_probe import AMD

        return AMD(
            vendor_id=0x1002,
            device_id=device_id,
            class_code=0x030000,
            name="fixture",
        )

    def test_vega64_macpro51_patch_dict_has_compositor_key(self) -> None:
        from opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.amd_vega import (
            AMDVega,
        )

        gpu = self._amd(0x687F)
        self.assertEqual(gpu.arch.name, "Vega")
        patcher = AMDVega(TAHOE_XNU_MAJOR, 0, "25A", self._constants("MacPro5,1", gpu))
        patches = patcher.patches()
        self.assertIn("AMD Vega", patches)
        self.assertIn(TAHOE_YELLOW_SCREEN_PATCH_NAME, patches)
        mtl = patches["AMD Vega"]["Overwrite System Volume"]["/System/Library/Extensions"][
            "AMDRadeonX5000MTLDriver.bundle"
        ]
        self.assertIn(mtl, {"12.5-24", "12.5-25", f"12.5-{TAHOE_XNU_MAJOR}"})

    def test_polaris_macpro51_patch_dict_has_compositor_key(self) -> None:
        from opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.amd_polaris import (
            AMDPolaris,
        )

        gpu = self._amd(0x67FF)
        self.assertEqual(gpu.arch.name, "Polaris")
        patcher = AMDPolaris(TAHOE_XNU_MAJOR, 0, "25A", self._constants("MacPro5,1", gpu))
        patches = patcher.patches()
        self.assertIn("AMD Polaris", patches)
        self.assertIn(TAHOE_YELLOW_SCREEN_PATCH_NAME, patches)

    def test_gcn_macpro61_patch_dict_has_compositor_key(self) -> None:
        from opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.amd_legacy_gcn import (
            AMDLegacyGCN,
        )

        gpu = self._amd(0x6800)
        self.assertTrue(gpu.arch.name.startswith("Legacy_GCN") or "GCN" in gpu.arch.value)
        patcher = AMDLegacyGCN(TAHOE_XNU_MAJOR, 0, "25A", self._constants("MacPro6,1", gpu))
        patches = patcher.patches()
        self.assertIn("AMD Legacy GCN", patches)
        self.assertIn(TAHOE_YELLOW_SCREEN_PATCH_NAME, patches)

    def test_sequoia_does_not_add_tahoe_compositor_key(self) -> None:
        from opencore_legacy_patcher.sys_patch.patchsets.hardware.graphics.amd_vega import (
            AMDVega,
        )

        gpu = self._amd(0x687F)
        patcher = AMDVega(24, 0, "24A", self._constants("MacPro5,1", gpu))
        self.assertNotIn(TAHOE_YELLOW_SCREEN_PATCH_NAME, patcher.patches())


if __name__ == "__main__":
    unittest.main()
