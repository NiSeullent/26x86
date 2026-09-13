"""Unit tests for ``x86.extreme.validation`` gate steps."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.extreme.validation import (  # noqa: E402
    run_all,
    run_gates,
    step_apply_order_dry_run,
    step_detect_fixture,
    step_efi_bridge,
    step_h_n_iosurface_prefer,
    step_l5_macho_probe,
    step_mock_guest_matrix,
    step_patchset_emptiness,
    step_profile_dry_run,
    step_renderbox_payload_ready,
    step_track_e_renderbox,
)


class ValidationStepsTest(unittest.TestCase):
    def test_each_gate_ok(self) -> None:
        for fn in (
            step_detect_fixture,
            step_patchset_emptiness,
            step_profile_dry_run,
            step_efi_bridge,
            step_h_n_iosurface_prefer,
            step_track_e_renderbox,
            step_renderbox_payload_ready,
            step_l5_macho_probe,
            step_apply_order_dry_run,
            step_mock_guest_matrix,
        ):
            with self.subTest(step=fn.__name__):
                result = fn()
                self.assertTrue(result.ok, msg=f"{result.name}: {result.error or result.detail}")

    def test_run_gates_all(self) -> None:
        results = run_gates()
        self.assertEqual(len(results), 10)
        self.assertTrue(all(r.ok for r in results))

    def test_run_all_gates_only_shape(self) -> None:
        payload = run_all(run_unittests=False)
        self.assertTrue(payload["gates_ok"])
        self.assertIn("host", payload)
        self.assertIn("vm_note", payload)


if __name__ == "__main__":
    unittest.main()
