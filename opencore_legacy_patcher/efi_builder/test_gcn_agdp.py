"""
opencore_legacy_patcher/efi_builder/test_gcn_agdp.py
"""

from __future__ import annotations

import unittest

from opencore_legacy_patcher.efi_builder.gcn_agdp import (
    SOCKET_AMD_AGDP_MODELS,
    apply_gcn_agdp_fallbacks,
    boot_args_need_gcn_agdp,
    config_has_agdpmod,
    model_needs_legacy_amd_agdp,
)


class GcnAgdpHelperTest(unittest.TestCase):
    def test_mac_pro_socket_models_need_agdp(self) -> None:
        self.assertTrue(model_needs_legacy_amd_agdp("MacPro5,1"))
        self.assertTrue(model_needs_legacy_amd_agdp("MacPro6,1"))
        self.assertIn("MacPro5,1", SOCKET_AMD_AGDP_MODELS)

    def test_apply_sets_agdpmod_and_shikigva(self) -> None:
        config: dict = {}
        apply_gcn_agdp_fallbacks(config)
        self.assertTrue(config_has_agdpmod(config))
        boot = config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]
        self.assertIn("agdpmod=", boot)
        self.assertIn("shikigva=", boot)

    def test_boot_args_idempotent(self) -> None:
        self.assertEqual(boot_args_need_gcn_agdp("agdpmod=pikera shikigva=128"), [])


if __name__ == "__main__":
    unittest.main()
