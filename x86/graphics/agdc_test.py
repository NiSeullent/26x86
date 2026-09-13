"""Unit tests for Track D AGDC modules (agdc_*.py only — no shared-file edits)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.agdc_diagnose import (  # noqa: E402
    agdc_yellow_risk,
    classify_yellow_mode,
    serialize_agdc_diagnose_fields,
    serialize_track_detect_fields,
    sys_patch_hooks,
    ui_tint_yellow_risk,
)
from x86.graphics.agdc_framebuffer import (  # noqa: E402
    build_macpro_framebuffer_checklist,
    is_vega64_gpu,
)
from x86.graphics.detect import TAHOE_XNU_MAJOR  # noqa: E402
from x86.graphics.skylight_tracks import track_status_entry  # noqa: E402


class ContractTest(unittest.TestCase):
    def test_sys_patch_hooks_empty(self) -> None:
        self.assertEqual(sys_patch_hooks(25, 0, "26.0"), {})

    def test_track_d_connected(self) -> None:
        entry = track_status_entry("D")
        self.assertEqual(entry["status"], "connected")
        self.assertTrue(entry["detect_fields"])
        self.assertTrue(any("agdc_" in m for m in entry["modules"]))

    def test_serialize_track_detect_fields(self) -> None:
        fields = serialize_track_detect_fields(
            "MacPro5,1",
            gpu_archs=["Vega", "0x687F"],
            xnu_major=TAHOE_XNU_MAJOR,
            agdpmod_present=False,
        )
        self.assertNotIn("yellow_screen_risk", fields)
        self.assertTrue(fields["agdc_yellow_risk"])
        self.assertIn("agdc_framebuffer_checklist", fields)


class YellowModeTest(unittest.TestCase):
    def test_solid_vs_tint(self) -> None:
        self.assertEqual(
            classify_yellow_mode(full_screen_solid=True, ui_interactive=False),
            "solid_agdc",
        )
        self.assertEqual(
            classify_yellow_mode(ui_interactive=True, ui_tint_only=True),
            "ui_tint_compositor",
        )


class RiskChecklistTest(unittest.TestCase):
    def test_vega64_macpro(self) -> None:
        gpus = ["Vega", "0x687F"]
        self.assertTrue(is_vega64_gpu(gpus))
        self.assertTrue(
            agdc_yellow_risk(
                "MacPro5,1",
                gpu_archs=gpus,
                xnu_major=TAHOE_XNU_MAJOR,
                agdpmod_present=False,
            )
        )
        self.assertTrue(
            ui_tint_yellow_risk(
                "MacPro5,1", gpu_archs=gpus, xnu_major=TAHOE_XNU_MAJOR
            )
        )
        result = build_macpro_framebuffer_checklist(
            "MacPro5,1",
            gpu_archs=gpus,
            xnu_major=TAHOE_XNU_MAJOR,
            agdpmod_present=False,
            agdp_on_correct_gfx0=False,
        )
        self.assertIn("agdpmod_present", result.failed_ids)

    def test_diagnose_no_yellow_screen_risk_key(self) -> None:
        fields = serialize_agdc_diagnose_fields(
            "MacPro6,1", xnu_major=TAHOE_XNU_MAJOR, agdpmod_present=True
        )
        self.assertNotIn("yellow_screen_risk", fields)
        self.assertIn("agdc_yellow_risk", fields)


if __name__ == "__main__":
    unittest.main()
