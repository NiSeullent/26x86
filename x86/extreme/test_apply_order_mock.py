"""Tests for L5 Mach-O probe, apply-order planner, mock guest matrix."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.extreme.apply_order import (  # noqa: E402
    dry_run_profile_apply,
    plan_apply_order,
)
from x86.extreme.mock_guest import GUESTS, run_mock_guest_matrix  # noqa: E402
from x86.graphics.skylight_lut_rootpatch import (  # noqa: E402
    MH_MAGIC_64,
    COREDISPLAY_REL,
    SKYLIGHT_REL,
    probe_l5_macho_payloads,
)


class L5MachOProbeTest(unittest.TestCase):
    def test_missing_reports_acquire(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = probe_l5_macho_payloads(25, search_roots=[Path(tmp)])
            self.assertFalse(report["ready_for_overwrite"])
            self.assertTrue(any("MISSING" in n for n in report["acquire_notes"]))

    def test_macho_magic_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sk = root / "10.14.6-24" / SKYLIGHT_REL
            cd = root / "10.14.4-24" / COREDISPLAY_REL
            sk.parent.mkdir(parents=True)
            cd.parent.mkdir(parents=True)
            sk.write_bytes(MH_MAGIC_64 + b"\0" * 32)
            cd.write_bytes(MH_MAGIC_64 + b"\0" * 32)
            report = probe_l5_macho_payloads(25, search_roots=[root])
            self.assertTrue(report["ready_for_overwrite"])
            self.assertTrue(report["skylight_macho"])
            self.assertTrue(report["coredisplay_macho"])

    def test_psp_sibling_ready_if_present(self) -> None:
        psp = REPO.parent / "26x86-PatcherSupportPkg" / "Universal-Binaries"
        if not psp.is_dir():
            self.skipTest("PSP Universal-Binaries missing")
        report = probe_l5_macho_payloads(25, search_roots=[psp])
        self.assertTrue(
            report["ready_for_overwrite"],
            msg=report.get("acquire_notes"),
        )


class ApplyOrderTest(unittest.TestCase):
    def test_phase_order_extreme(self) -> None:
        plan = plan_apply_order(include_extreme=True, dry_run=True)
        self.assertEqual(
            list(plan.flat_order),
            [
                "efi.agdpmod_shikigva",
                "efi.kdkless",
                "efi.restrictevents_jsc",
                "root.amd_vega",
                "root.yellow_mitigations",
                "extreme.hooks",
            ],
        )
        self.assertEqual(plan.phases[-1].status, "planned")

    def test_extreme_skipped_without_flag(self) -> None:
        plan = plan_apply_order(include_extreme=False, environ={}, dry_run=True)
        self.assertEqual(plan.phases[-1].status, "skipped")
        self.assertNotIn("extreme.hooks", plan.flat_order)

    def test_dry_run_matches_profile(self) -> None:
        payload = dry_run_profile_apply(include_extreme=True)
        self.assertTrue(payload["order_matches_phases"])


class MockGuestMatrixTest(unittest.TestCase):
    def test_matrix_green(self) -> None:
        self.assertGreaterEqual(len(GUESTS), 4)
        payload = run_mock_guest_matrix()
        self.assertTrue(payload["ok"], msg=payload)


if __name__ == "__main__":
    unittest.main()
