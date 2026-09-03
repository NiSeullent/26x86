"""Unit tests for Track L-WS dedicated modules."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.windowserver_hook import serialize_windowserver_hook_fields  # noqa: E402
from x86.graphics.windowserver_hook_compositor import plan_software_compositor  # noqa: E402
from x86.graphics.windowserver_hook_gate import (  # noqa: E402
    ENV_ACCEPT, ENV_EXTREME, ENV_HOOK, extreme_windowserver_hooks_allowed, require_extreme_windowserver_hooks,
)
from x86.graphics.windowserver_hook_inject import plan_process_injection, render_dyld_insert_launchd_plist  # noqa: E402
from x86.graphics.windowserver_hook_lut import PRIVATE_LUT_BYTE_PATCH_STATUS, build_gamma_identity_table, plan_public_lut_recovery  # noqa: E402
from x86.graphics.windowserver_hook_plan import STAGE_L0_SHIPPED, build_windowserver_hook_plan, run_extreme_windowserver_plan  # noqa: E402


class TrackLWSTest(unittest.TestCase):
    def test_gate(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            for k in (ENV_EXTREME, ENV_HOOK, ENV_ACCEPT):
                os.environ.pop(k, None)
            self.assertFalse(extreme_windowserver_hooks_allowed())
            with self.assertRaises(PermissionError):
                require_extreme_windowserver_hooks()
        with mock.patch.dict(os.environ, {ENV_EXTREME: "1", ENV_HOOK: "1"}, clear=False):
            self.assertTrue(extreme_windowserver_hooks_allowed())

    def test_plans(self) -> None:
        self.assertEqual(build_gamma_identity_table(5)["red"][-1], 1.0)
        self.assertEqual(plan_public_lut_recovery(require_gate=False)["private_lut_byte_patch"], PRIVATE_LUT_BYTE_PATCH_STATUS)
        with mock.patch.dict(os.environ, {ENV_EXTREME: "1", ENV_ACCEPT: "1"}, clear=False):
            self.assertIn("Disabled", render_dyld_insert_launchd_plist("/tmp/CompositorLUT.dylib"))
        mach = next(p for p in plan_process_injection(require_gate=False)["paths"] if p["id"] == "mach_task_inject_function_hook")
        self.assertEqual(mach["status"], "not_implemented")
        self.assertIsNone(plan_software_compositor(require_gate=False)["apple_metal_windowserver_off_flag"])
        self.assertIn("window_server_cache_disable", STAGE_L0_SHIPPED)
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(next(s for s in build_windowserver_hook_plan()["stages"] if s["id"] == "L1")["status"], "locked")
        with mock.patch.dict(os.environ, {ENV_EXTREME: "1", ENV_HOOK: "1"}, clear=False):
            self.assertFalse(run_extreme_windowserver_plan()["mutated_host"])
        self.assertEqual(serialize_windowserver_hook_fields()["windowserver_hook_track"], "L-WS")


if __name__ == "__main__":
    unittest.main()
