"""Track N — Non-Metal Tahoe opt-in refill via *.py.stage-N (M-style)."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from opencore_legacy_patcher.sys_patch.patchsets.shared_patches.non_metal import (  # noqa: E402
    NonMetal,
)
from x86.graphics.nonmetal_tahoe import (  # noqa: E402
    ENV_ENFORCEMENT,
    ENV_EXTREME,
    ENV_NONMETAL,
    ENV_STAGE,
    FIXTURE_MACPRO51_TERASCALE,
    FIXTURE_NONMETAL_IGPU_SANDY,
    STAGE_N_SHARED_PATCHES,
    TAHOE_XNU_MAJOR,
    enabled_patch_keys,
    filter_nonmetal_tahoe_patches,
    match_nonmetal_fixture,
    serialize_nonmetal_tahoe_fields,
    stage_n_proposals_present,
    sys_patch_hooks,
    tahoe_nonmetal_opt_in,
)

SP = (
    REPO
    / "opencore_legacy_patcher/sys_patch/patchsets/shared_patches"
)
STAGE_COMMON = SP / "non_metal.py.stage-N"
SHARED_COMMON = SP / "non_metal.py"


class OptInGateTest(unittest.TestCase):
    def test_or_opt_in(self) -> None:
        self.assertTrue(tahoe_nonmetal_opt_in({ENV_NONMETAL: "1"}))
        self.assertTrue(tahoe_nonmetal_opt_in({ENV_EXTREME: "1"}))
        self.assertFalse(tahoe_nonmetal_opt_in({}))

    def test_default_stage_all_refills_common_ioaccel_coredisplay(self) -> None:
        keys = enabled_patch_keys({ENV_NONMETAL: "1"})
        self.assertIn("Non-Metal Common", keys)
        self.assertIn("Non-Metal IOAccelerator Common", keys)
        self.assertIn("Non-Metal CoreDisplay Common", keys)
        self.assertNotIn("Non-Metal Enforcement", keys)

    def test_enforcement_extra(self) -> None:
        keys = enabled_patch_keys(
            {
                ENV_NONMETAL: "1",
                ENV_STAGE: "all",
                ENV_ENFORCEMENT: "1",
            }
        )
        self.assertIn("Non-Metal Enforcement", keys)


class FilterRefillTest(unittest.TestCase):
    """Prove Tahoe opt-in re-fills shared patch keys (not permanent {})."""

    def _base(self) -> dict:
        return {
            "Non-Metal Common": {"ok": True},
            "Non-Metal IOAccelerator Common": {"ok": True},
            "Non-Metal CoreDisplay Common": {"ok": True},
            "Non-Metal Enforcement": {"ok": True},
        }

    def test_tahoe_default_empty(self) -> None:
        self.assertEqual(
            filter_nonmetal_tahoe_patches(
                self._base(), xnu_major=TAHOE_XNU_MAJOR, environ={}
            ),
            {},
        )

    def test_opt_in_refills_default_all(self) -> None:
        filled = filter_nonmetal_tahoe_patches(
            self._base(),
            xnu_major=TAHOE_XNU_MAJOR,
            environ={ENV_NONMETAL: "1"},
        )
        self.assertIn("Non-Metal Common", filled)
        self.assertIn("Non-Metal IOAccelerator Common", filled)
        self.assertIn("Non-Metal CoreDisplay Common", filled)
        self.assertNotIn("Non-Metal Enforcement", filled)
        self.assertGreater(len(filled), 0)

    def test_extreme_opt_in_refills(self) -> None:
        filled = filter_nonmetal_tahoe_patches(
            self._base(),
            xnu_major=TAHOE_XNU_MAJOR,
            environ={ENV_EXTREME: "1"},
        )
        self.assertIn("Non-Metal Common", filled)
        self.assertFalse(filled == {})

    def test_sequoia_unchanged(self) -> None:
        base = self._base()
        self.assertEqual(
            filter_nonmetal_tahoe_patches(base, xnu_major=24, environ={}),
            base,
        )


class StageSidecarTest(unittest.TestCase):
    def test_all_stage_n_present(self) -> None:
        self.assertTrue(stage_n_proposals_present(REPO))
        for rel in STAGE_N_SHARED_PATCHES:
            self.assertTrue((REPO / rel).is_file(), rel)

    def test_stage_uses_filter_not_permanent_empty(self) -> None:
        stage = STAGE_COMMON.read_text(encoding="utf-8")
        self.assertIn("filter_nonmetal_tahoe_patches", stage)
        self.assertIn("X86_TAHOE_NONMETAL", stage)
        self.assertNotIn(
            "Safety guard: skip this patchset entirely until a working fix is found.",
            stage,
        )

    def test_live_shared_untouched(self) -> None:
        shared = SHARED_COMMON.read_text(encoding="utf-8")
        self.assertNotIn("filter_nonmetal_tahoe_patches", shared)
        self.assertIn("return {}", shared)

    def test_stage_parses(self) -> None:
        tree = ast.parse(STAGE_COMMON.read_text(encoding="utf-8"))
        self.assertTrue(
            any(
                isinstance(n, ast.ClassDef) and n.name == "NonMetal"
                for n in tree.body
            )
        )


class StageNInjectionTest(unittest.TestCase):
    """stage-N patches() must emit Non-Metal keys under opt-in."""

    def test_stage_common_injects(self) -> None:
        mod = __import__(
            "x86.graphics.nonmetal_tahoe", fromlist=["_load_stage_n_module"]
        )
        stage_mod = mod._load_stage_n_module("non_metal")
        self.assertIsNotNone(stage_mod)
        with mock.patch.dict(
            "os.environ",
            {ENV_NONMETAL: "1", ENV_STAGE: "all"},
            clear=False,
        ):
            patches = stage_mod.NonMetal(TAHOE_XNU_MAJOR, 0, "25A").patches()
        self.assertIn("Non-Metal Common", patches)
        self.assertGreater(len(patches["Non-Metal Common"]), 0)

    def test_stage_default_env_empty(self) -> None:
        mod = __import__(
            "x86.graphics.nonmetal_tahoe", fromlist=["_load_stage_n_module"]
        )
        stage_mod = mod._load_stage_n_module("non_metal")
        self.assertIsNotNone(stage_mod)
        with mock.patch.dict("os.environ", {}, clear=True):
            patches = stage_mod.NonMetal(TAHOE_XNU_MAJOR, 0, "25A").patches()
        self.assertEqual(patches, {})

    def test_sys_patch_hooks_inject(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {ENV_NONMETAL: "1", ENV_STAGE: "all"},
            clear=False,
        ):
            hooks = sys_patch_hooks(TAHOE_XNU_MAJOR, 0, "26.0")
        self.assertIn("Non-Metal Common", hooks)
        self.assertIn("Non-Metal IOAccelerator Common", hooks)
        self.assertIn("Non-Metal CoreDisplay Common", hooks)

    def test_live_still_empty_on_tahoe(self) -> None:
        with mock.patch.dict(
            "os.environ", {ENV_NONMETAL: "1"}, clear=False
        ):
            self.assertEqual(
                NonMetal(TAHOE_XNU_MAJOR, 0, "25A").patches(), {}
            )


class FixtureTest(unittest.TestCase):
    def test_macpro51(self) -> None:
        self.assertEqual(
            match_nonmetal_fixture("MacPro5,1", ["TeraScale_2"]),
            FIXTURE_MACPRO51_TERASCALE,
        )

    def test_sandy(self) -> None:
        self.assertEqual(
            match_nonmetal_fixture("MacBookPro8,2", ["Sandy_Bridge"]),
            FIXTURE_NONMETAL_IGPU_SANDY,
        )

    def test_serialize(self) -> None:
        fields = serialize_nonmetal_tahoe_fields(
            "MacPro5,1",
            xnu_major=TAHOE_XNU_MAJOR,
            gpu_archs=["TeraScale_2"],
            environ={ENV_NONMETAL: "1"},
        )
        self.assertTrue(fields["nonmetal_tahoe_opt_in"])
        self.assertIn("Non-Metal Common", fields["nonmetal_enabled_patch_keys"])
        self.assertIn("stage-N", fields["nonmetal_stage_sidecar"])


if __name__ == "__main__":
    unittest.main()
