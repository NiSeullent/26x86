"""Track I Extreme-Interpose unit tests (owned module only)."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.interpose_gate import (  # noqa: E402
    ENV_X86_EXTREME,
    ENV_X86_EXTREME_INSTALL,
    extreme_install_opt_in,
    extreme_opt_in,
    gate_blocks_reason,
)
from x86.graphics.interpose_payload import (  # noqa: E402
    enumerate_extreme_interpose_sources,
    payload_status,
)
from x86.graphics.interpose_plan import (  # noqa: E402
    PLUGIN_STEM,
    plan_summary,
    root_volume_interpose_recipe,
    serialize_interpose_fields,
)
from x86.graphics.interpose_symbols import INTERPOSE_SYMBOLS  # noqa: E402


class GateTest(unittest.TestCase):
    def test_default_blocked(self) -> None:
        env = {k: v for k, v in os.environ.items() if not k.startswith("X86_")}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(extreme_opt_in())
            self.assertIsNotNone(gate_blocks_reason())

    def test_extreme_arms_research(self) -> None:
        with mock.patch.dict(os.environ, {ENV_X86_EXTREME: "1"}, clear=False):
            self.assertTrue(extreme_opt_in())
            self.assertIsNone(gate_blocks_reason(require_install=False))
            self.assertFalse(extreme_install_opt_in())
            self.assertIsNotNone(gate_blocks_reason(require_install=True))

    def test_install_requires_both(self) -> None:
        with mock.patch.dict(
            os.environ,
            {ENV_X86_EXTREME: "1", ENV_X86_EXTREME_INSTALL: "1"},
            clear=False,
        ):
            self.assertTrue(extreme_install_opt_in())
            self.assertIsNone(gate_blocks_reason(require_install=True))


class PlanTest(unittest.TestCase):
    def test_symbols_include_avx_and_lut(self) -> None:
        groups = {s.mode_group for s in INTERPOSE_SYMBOLS}
        self.assertIn("avx", groups)
        self.assertIn("lut", groups)
        self.assertIn("loader", groups)

    def test_recipe_empty_without_pin(self) -> None:
        with mock.patch.dict(
            os.environ,
            {ENV_X86_EXTREME: "1", ENV_X86_EXTREME_INSTALL: "1"},
            clear=False,
        ):
            self.assertEqual(root_volume_interpose_recipe(), {})

    def test_serialize_fields(self) -> None:
        fields = serialize_interpose_fields(repo_root=REPO)
        self.assertEqual(fields["skylight_track_I"]["track"], "I")
        self.assertFalse(fields["extreme_interpose"]["apple_blobs_vendored"])
        self.assertIn(
            "src/ExtremeCompositorInterpose.c",
            fields["extreme_interpose"]["sources"],
        )

    def test_payload_sources_present(self) -> None:
        sources = enumerate_extreme_interpose_sources(repo_root=REPO)
        missing = [k for k, v in sources.items() if not v]
        self.assertEqual(missing, [], msg=f"missing Track I sources: {missing}")
        status = payload_status(repo_root=REPO)
        self.assertTrue(status["sources_complete"])
        self.assertEqual(PLUGIN_STEM, "ExtremeCompositor")

    def test_plan_forbidden_mentions_byte_patches(self) -> None:
        summary = plan_summary(extreme=False)
        self.assertTrue(any("byte patch" in f.lower() for f in summary["forbidden"]))


if __name__ == "__main__":
    unittest.main()
