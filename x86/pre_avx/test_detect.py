"""Unit tests for x86.pre_avx Phase 1 detect fields."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.pre_avx.detect import (  # noqa: E402
    MetalPatchVariant,
    build_detect_fields,
    is_pre_avx_mac_pro,
    recommend_metal_patch,
    serialize_detect_fields,
)

MACPRO61_FEATURES = ["MMX", "SSE", "SSE2", "SSE3", "SSSE3", "SSE4.1", "SSE4.2", "AVX1.0"]
MACPRO51_NO_AVX = ["MMX", "SSE", "SSE2", "SSE3", "SSSE3", "SSE4.1", "SSE4.2"]
MACPRO51_AVX1 = MACPRO61_FEATURES


class PreAvxPhase1DetectTest(unittest.TestCase):
    def test_macpro61_pre_avx_without_avx2(self) -> None:
        self.assertTrue(is_pre_avx_mac_pro("MacPro6,1", avx_available=True, has_avx2=False))
        fields = build_detect_fields(
            "MacPro6,1",
            cpu_features=MACPRO61_FEATURES,
            cpu_leaf7_features=[],
            gpus=[SimpleNamespace(name="AMD FirePro D700")],
        )
        self.assertTrue(fields.pre_avx_mac_pro)
        self.assertEqual(fields.recommended_metal_patch, MetalPatchVariant.METAL_31001.value)
        self.assertTrue(fields.avx_available)
        self.assertFalse(fields.has_avx2)

    def test_macpro51_westmere_no_avx(self) -> None:
        self.assertTrue(is_pre_avx_mac_pro("MacPro5,1", avx_available=False, has_avx2=False))
        fields = build_detect_fields(
            "MacPro5,1",
            cpu_features=MACPRO51_NO_AVX,
            cpu_leaf7_features=[],
            gpus=[SimpleNamespace(name="NVIDIA Quadro K5000")],
        )
        self.assertTrue(fields.pre_avx_mac_pro)
        self.assertFalse(fields.avx_available)
        self.assertEqual(fields.recommended_metal_patch, MetalPatchVariant.METAL_3802.value)

    def test_macpro51_avx2_upgrade_not_pre_avx(self) -> None:
        self.assertFalse(is_pre_avx_mac_pro("MacPro5,1", avx_available=True, has_avx2=True))
        fields = build_detect_fields(
            "MacPro5,1",
            cpu_features=MACPRO51_AVX1,
            cpu_leaf7_features=["AVX2"],
        )
        self.assertFalse(fields.pre_avx_mac_pro)

    def test_imac_not_pre_avx_mac_pro(self) -> None:
        fields = build_detect_fields("iMac18,3", cpu_features=MACPRO61_FEATURES, cpu_leaf7_features=["AVX2"])
        self.assertFalse(fields.pre_avx_mac_pro)
        self.assertEqual(fields.recommended_metal_patch, MetalPatchVariant.UNKNOWN.value)

    def test_serialize_detect_json_keys(self) -> None:
        fields = build_detect_fields(
            "MacPro6,1",
            cpu_features=MACPRO61_FEATURES,
            cpu_leaf7_features=[],
            xnu_major=25,
        )
        payload = serialize_detect_fields(fields)
        for key in (
            "pre_avx_mac_pro",
            "recommended_metal_patch",
            "avx_available",
            "has_avx2",
            "safari_pre_avx_fix_recommended",
            "auto_pre_avx_patch",
            "recommended_tahoe_graphics_policy",
            "safari26_preavx",
        ):
            self.assertIn(key, payload)

    def test_recommend_metal_from_gpu_name(self) -> None:
        self.assertEqual(
            recommend_metal_patch("MacPro5,1", [SimpleNamespace(name="NVIDIA GeForce GTX 680")]),
            MetalPatchVariant.METAL_3802,
        )
        self.assertEqual(
            recommend_metal_patch("MacPro6,1", [SimpleNamespace(name="AMD FirePro D500")]),
            MetalPatchVariant.METAL_31001,
        )


if __name__ == "__main__":
    unittest.main()
