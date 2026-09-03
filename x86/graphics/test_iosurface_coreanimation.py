"""Unit tests for Track H IOSurface / CoreAnimation gates and extreme PoC."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.coreanimation_analysis import (  # noqa: E402
    analyze_coreanimation_gates,
    metal_vega_boot_args,
)
from x86.graphics.coreanimation_extreme import (  # noqa: E402
    EXTREME_COREANIMATION_PATCH_NAME,
    extreme_coreanimation_merge_patches,
)
from x86.graphics.iosurface_analysis import (  # noqa: E402
    TAHOE_XNU_MAJOR,
    analyze_iosurface_gates,
    is_extreme_iosurface_ca_opt_in,
)
from x86.graphics.iosurface_ca_hooks import (  # noqa: E402
    iosurface_ca_extreme_patches,
    serialize_iosurface_ca_fields,
)
from x86.graphics.iosurface_extreme import (  # noqa: E402
    EXTREME_IOSURFACE_PATCH_NAME,
)


def _psp_root() -> Path:
    return REPO.parent / "26x86-PatcherSupportPkg" / "Universal-Binaries"


class GateAnalysisTest(unittest.TestCase):
    def test_tahoe_blocks_non_metal_iosurface(self) -> None:
        report = analyze_iosurface_gates(TAHOE_XNU_MAJOR, has_metal_amd=True)
        self.assertTrue(report.non_metal_iosurface_blocked_on_tahoe)
        self.assertTrue(report.metal_path_recommended)

    def test_payload_present_from_psp_fork(self) -> None:
        root = _psp_root()
        if not root.is_dir():
            self.skipTest("26x86-PatcherSupportPkg not checked out")
        report = analyze_iosurface_gates(TAHOE_XNU_MAJOR, search_roots=[root])
        self.assertTrue(report.payload_framework_present)
        self.assertEqual(report.framework_payload, "10.15.7-24")
        self.assertEqual(report.avx_markers_in_payload.get("AVX", 0), 0)

    def test_quartzcore_cametal_and_boot_args(self) -> None:
        root = _psp_root()
        if not root.is_dir():
            self.skipTest("26x86-PatcherSupportPkg not checked out")
        report = analyze_coreanimation_gates(TAHOE_XNU_MAJOR, search_roots=[root])
        self.assertTrue(report.payload_framework_present)
        self.assertGreater(report.cametal_string_hits, 0)
        self.assertIn("agdpmod=pikera", metal_vega_boot_args())


class ExtremeLatchTest(unittest.TestCase):
    def test_default_env_emits_nothing(self) -> None:
        self.assertFalse(is_extreme_iosurface_ca_opt_in({}))
        self.assertEqual(iosurface_ca_extreme_patches(TAHOE_XNU_MAJOR, environ={}), {})

    def test_extreme_alone_still_no_merge(self) -> None:
        env = {"X86_EXTREME": "1"}
        self.assertFalse(is_extreme_iosurface_ca_opt_in(env))
        self.assertEqual(iosurface_ca_extreme_patches(TAHOE_XNU_MAJOR, environ=env), {})

    def test_double_latch_with_payload_emits_merges(self) -> None:
        root = _psp_root()
        if not root.is_dir():
            self.skipTest("26x86-PatcherSupportPkg not checked out")
        env = {"X86_EXTREME": "1", "X86_EXTREME_IOSURFACE_CA": "1"}
        patches = iosurface_ca_extreme_patches(
            TAHOE_XNU_MAJOR, search_roots=[root], environ=env
        )
        self.assertIn(EXTREME_IOSURFACE_PATCH_NAME, patches)
        self.assertIn(EXTREME_COREANIMATION_PATCH_NAME, patches)
        blob = repr(patches)
        self.assertNotIn("useMetal", blob)
        self.assertNotIn("IOGPUFamily", blob)
        self.assertNotIn("IOSurface.kext", blob)

    def test_missing_payload_no_emit(self) -> None:
        env = {"X86_EXTREME": "1", "X86_EXTREME_IOSURFACE_CA": "1"}
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                iosurface_ca_extreme_patches(
                    TAHOE_XNU_MAJOR, search_roots=[Path(tmp)], environ=env
                ),
                {},
            )

    def test_pre_tahoe_no_emit(self) -> None:
        env = {"X86_EXTREME": "1", "X86_EXTREME_IOSURFACE_CA": "1"}
        self.assertEqual(extreme_coreanimation_merge_patches(24, environ=env), {})


class SerializeTest(unittest.TestCase):
    def test_serialize_combined(self) -> None:
        fields = serialize_iosurface_ca_fields(TAHOE_XNU_MAJOR, environ={})
        self.assertTrue(fields["iosurface_non_metal_blocked_on_tahoe"])
        self.assertTrue(fields["coreanimation_non_metal_blocked_on_tahoe"])
        self.assertFalse(fields["iosurface_ca_extreme"]["would_emit_root_patches"])
        self.assertIn("agdpmod=pikera", fields["coreanimation_boot_args_metal_vega"])


if __name__ == "__main__":
    unittest.main()
