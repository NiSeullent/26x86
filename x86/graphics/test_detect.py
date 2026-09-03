"""Unit tests for Pre-AVX Mac Pro / Tahoe graphics detection."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.detect import (  # noqa: E402
    TAHOE_XNU_MAJOR,
    detect_pre_avx_mac_pro,
    serialize_graphics_detect_fields,
    should_strip_tahoe_legacy_gpu_patches,
    tahoe_blocked_patch_ids,
)


# Ivy Bridge Xeon (stock MacPro6,1): AVX1, no AVX2.
MACPRO61_CPU_FEATURES = ["MMX", "SSE", "SSE2", "SSE3", "SSSE3", "SSE4.1", "SSE4.2", "AVX1.0"]
MACPRO61_LEAF7: list[str] = []

# Westmere Xeon (typical MacPro5,1): AVX1, no AVX2.
MACPRO51_CPU_FEATURES = ["MMX", "SSE", "SSE2", "SSE3", "SSSE3", "SSE4.1", "SSE4.2", "AVX1.0"]
MACPRO51_LEAF7: list[str] = []


class PreAvxMacProDetectTest(unittest.TestCase):
    def test_macpro61_tahoe_gcn_efi_only(self) -> None:
        report = detect_pre_avx_mac_pro(
            "MacPro6,1",
            cpu_features=MACPRO61_CPU_FEATURES,
            cpu_leaf7_features=MACPRO61_LEAF7,
            xnu_major=TAHOE_XNU_MAJOR,
        )
        self.assertTrue(report.is_mac_pro)
        self.assertTrue(report.is_pre_avx2_mac_pro_like)
        self.assertTrue(report.has_avx1)
        self.assertFalse(report.has_avx2)
        self.assertEqual(report.recommended_tahoe_graphics_policy, "tahoe_gcn_efi_only")
        self.assertTrue(should_strip_tahoe_legacy_gpu_patches(report))
        self.assertIn("Metal 3802 Common", report.tahoe_blocked_patches)
        self.assertIn("Non-Metal Common", report.tahoe_blocked_patches)
        self.assertTrue(any("agdpmod" in note for note in report.notes))

    def test_macpro51_no_legacy_root_patch(self) -> None:
        report = detect_pre_avx_mac_pro(
            "MacPro5,1",
            cpu_features=MACPRO51_CPU_FEATURES,
            cpu_leaf7_features=MACPRO51_LEAF7,
            xnu_major=TAHOE_XNU_MAJOR,
        )
        self.assertTrue(report.is_pre_avx2_mac_pro_like)
        self.assertEqual(
            report.recommended_tahoe_graphics_policy,
            "tahoe_no_legacy_gpu_root_patch",
        )
        self.assertTrue(should_strip_tahoe_legacy_gpu_patches(report))
        self.assertGreater(len(report.tahoe_blocked_patches), 0)

    def test_macpro51_avx2_upgrade_modern_policy(self) -> None:
        report = detect_pre_avx_mac_pro(
            "MacPro5,1",
            cpu_features=MACPRO51_CPU_FEATURES,
            cpu_leaf7_features=["AVX2"],
            xnu_major=TAHOE_XNU_MAJOR,
        )
        self.assertFalse(report.is_pre_avx2_mac_pro_like)
        self.assertTrue(report.has_avx2)
        self.assertEqual(report.recommended_tahoe_graphics_policy, "tahoe_modern_mac_pro")

    def test_non_mac_pro_not_flagged(self) -> None:
        report = detect_pre_avx_mac_pro("iMac18,3", cpu_features=["AVX1.0"], cpu_leaf7_features=["AVX2"])
        self.assertFalse(report.is_mac_pro)
        self.assertEqual(report.recommended_tahoe_graphics_policy, "not_mac_pro")
        self.assertFalse(should_strip_tahoe_legacy_gpu_patches(report))

    def test_tahoe_blocked_empty_before_tahoe(self) -> None:
        report = detect_pre_avx_mac_pro(
            "MacPro6,1",
            cpu_features=MACPRO61_CPU_FEATURES,
            cpu_leaf7_features=MACPRO61_LEAF7,
            xnu_major=24,
        )
        self.assertEqual(report.tahoe_blocked_patches, ())
        self.assertEqual(tahoe_blocked_patch_ids(24), [])

    def test_serialize_graphics_detect_fields(self) -> None:
        payload = serialize_graphics_detect_fields(
            "MacPro6,1",
            xnu_major=TAHOE_XNU_MAJOR,
            cpu_features=MACPRO61_CPU_FEATURES,
            cpu_leaf7_features=MACPRO61_LEAF7,
        )
        self.assertTrue(payload["pre_avx_mac_pro"])
        self.assertTrue(payload["avx_available"])
        self.assertFalse(payload["avx2_available"])
        self.assertEqual(payload["recommended_tahoe_graphics_policy"], "tahoe_gcn_efi_only")
        self.assertIn("Metal 3802 Common", payload["tahoe_blocked_patches"])
        self.assertIsInstance(payload["graphics_policy_notes"], list)


if __name__ == "__main__":
    unittest.main()
