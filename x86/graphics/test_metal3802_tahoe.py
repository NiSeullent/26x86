"""Track M — Metal 3802 Tahoe opt-in / slice KP matrix fixtures."""

from __future__ import annotations

import ast
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.metal3802_tahoe import (  # noqa: E402
    ALL_SLICES,
    ENV_EXTREME,
    ENV_SLICES,
    ENV_TAHOE_3802,
    KP_HYPOTHESES,
    METAL_3802_FIXTURES,
    PATCH_KEY_BY_SLICE,
    SLICE_COMMON,
    TAHOE_XNU_MAJOR,
    assess_metallib_tahoe_manifest,
    enabled_patch_keys,
    filter_tahoe_3802_patches,
    fixture_for_model,
    fixtures_by_family,
    is_tahoe_3802_opt_in,
    parse_enabled_slices,
    recommended_probe_sequence,
    serialize_metal3802_tahoe_fields,
)

STAGE_M = (
    REPO
    / "opencore_legacy_patcher"
    / "sys_patch"
    / "patchsets"
    / "shared_patches"
    / "metal_3802.py.stage-M"
)
SHARED_METAL = STAGE_M.with_name("metal_3802.py")


class OptInGateTest(unittest.TestCase):
    def test_default_off(self) -> None:
        self.assertFalse(is_tahoe_3802_opt_in({}))

    def test_tahoe_3802_flag(self) -> None:
        self.assertTrue(is_tahoe_3802_opt_in({ENV_TAHOE_3802: "1"}))

    def test_extreme_flag(self) -> None:
        self.assertTrue(is_tahoe_3802_opt_in({ENV_EXTREME: "yes"}))

    def test_filter_blocks_without_opt_in(self) -> None:
        patches = {PATCH_KEY_BY_SLICE[s]: {"n": s} for s in ALL_SLICES}
        self.assertEqual(
            filter_tahoe_3802_patches(
                patches, xnu_major=TAHOE_XNU_MAJOR, environ={}
            ),
            {},
        )

    def test_filter_noop_pre_tahoe(self) -> None:
        patches = {"Metal 3802 Common": {"ok": True}}
        # Sequoia + filter call → {} (stock patches() returns base before filter).
        self.assertEqual(
            filter_tahoe_3802_patches(patches, xnu_major=24, environ={ENV_EXTREME: "1"}),
            {},
        )

    def test_slice_common_only(self) -> None:
        patches = {PATCH_KEY_BY_SLICE[s]: {"n": s} for s in ALL_SLICES}
        env = {ENV_TAHOE_3802: "1", ENV_SLICES: "common"}
        out = filter_tahoe_3802_patches(
            patches, xnu_major=TAHOE_XNU_MAJOR, environ=env
        )
        self.assertEqual(list(out.keys()), ["Metal 3802 Common"])
        self.assertEqual(parse_enabled_slices(env), frozenset({SLICE_COMMON}))

    def test_default_slices_all_when_opt_in(self) -> None:
        env = {ENV_EXTREME: "1"}
        self.assertEqual(parse_enabled_slices(env), frozenset(ALL_SLICES))
        self.assertEqual(
            enabled_patch_keys(env),
            frozenset(PATCH_KEY_BY_SLICE.values()),
        )


class KpHypothesisTest(unittest.TestCase):
    def test_hypotheses_cover_slices(self) -> None:
        self.assertGreaterEqual(len(KP_HYPOTHESES), 4)
        ids = {h.combo_id for h in KP_HYPOTHESES}
        self.assertIn("common_only", ids)
        self.assertIn("all_three", ids)

    def test_probe_sequence_ordered(self) -> None:
        seq = recommended_probe_sequence()
        orders = [
            next(
                h.recommended_probe_order
                for h in KP_HYPOTHESES
                if h.combo_id == s["combo_id"]
            )
            for s in seq
        ]
        self.assertEqual(orders, sorted(orders))
        self.assertEqual(seq[0]["env"][ENV_SLICES], "common")


class FixtureTest(unittest.TestCase):
    def test_ivy_haswell_kepler_present(self) -> None:
        families = {f.family for f in METAL_3802_FIXTURES}
        self.assertEqual(families, {"ivy_bridge", "haswell", "kepler"})

    def test_model_lookup(self) -> None:
        ivy = fixture_for_model("MacBookPro10,1")
        self.assertIsNotNone(ivy)
        assert ivy is not None
        self.assertEqual(ivy.family, "ivy_bridge")
        self.assertEqual(ivy.hardware_patch_class, "IntelIvyBridge")

        haswell = fixture_for_model("MacBookAir6,1")
        self.assertIsNotNone(haswell)
        assert haswell is not None
        self.assertEqual(haswell.family, "haswell")

        self.assertTrue(any(f.family == "kepler" for f in fixtures_by_family("kepler")))


class MetallibManifestTest(unittest.TestCase):
    def test_sequoia_only_reports_gap(self) -> None:
        fixture = [
            {
                "build": "24G830",
                "version": "15.7.9",
                "url": "https://example.invalid/seq.pkg",
                "name": "MetallibSupportPkg Sequoia",
            }
        ]
        report = assess_metallib_tahoe_manifest(
            fixture_json=fixture, install_paths=["/nope/missing"]
        )
        self.assertEqual(report.entries_total, 1)
        self.assertEqual(report.tahoe_entries, [])
        self.assertFalse(report.tahoe_metallib_ready)
        self.assertTrue(any("no Tahoe" in g for g in report.gaps))

    def test_tahoe_entry_ready(self) -> None:
        fixture = [
            {
                "build": "25A353",
                "version": "26.0",
                "url": "https://example.invalid/tahoe.pkg",
                "name": "MetallibSupportPkg Tahoe",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "25A353-tree").mkdir()
            (root / "25A353-tree" / "dummy").write_text("x", encoding="utf-8")
            report = assess_metallib_tahoe_manifest(
                fixture_json=fixture, install_paths=[str(root)]
            )
        self.assertTrue(report.tahoe_metallib_ready)
        self.assertEqual(report.tahoe_entries[0].build, "25A353")

    def test_local_install_alone_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pkg").mkdir()
            (root / "pkg" / "f").write_text("1", encoding="utf-8")
            report = assess_metallib_tahoe_manifest(
                fixture_json=[], install_paths=[str(root)]
            )
        self.assertTrue(report.tahoe_metallib_ready)


class SerializeTest(unittest.TestCase):
    def test_serialize_default_blocked(self) -> None:
        fields = serialize_metal3802_tahoe_fields(
            TAHOE_XNU_MAJOR, model="MacBookPro10,1", environ={}
        )
        self.assertEqual(fields["metal3802_track"], "M")
        self.assertTrue(fields["metal3802_tahoe_default_blocked"])
        self.assertFalse(fields["metal3802_tahoe_opt_in"])
        self.assertEqual(fields["metal3802_fixture"]["family"], "ivy_bridge")
        self.assertIn("metal_3802.py.stage-M", fields["metal3802_stage_sidecar"])




class LivePatchFillTest(unittest.TestCase):
    """Prove Tahoe opt-in re-fills shared patch keys (not permanent {})."""

    def _tahoe_base(self):
        from opencore_legacy_patcher.sys_patch.patchsets.shared_patches.metal_3802 import (
            LegacyMetal3802,
        )

        obj = LegacyMetal3802(TAHOE_XNU_MAJOR, 0, "26.0")
        # Shared in-tree patches() still returns {}; build the same base the stage uses.
        return {
            **obj._patches_metal_3802_common(),
            **obj._patches_metal_3802_common_extended(),
            **obj._patches_metal_3802_metallibs(),
        }

    def test_tahoe_base_slices_nonempty(self) -> None:
        base = self._tahoe_base()
        self.assertIn("Metal 3802 Common", base)
        self.assertIn("Metal 3802 Common Extended", base)
        self.assertIn("Metal 3802 .metallibs", base)

    def test_opt_in_refills_all_slices(self) -> None:
        base = self._tahoe_base()
        filled = filter_tahoe_3802_patches(
            base, xnu_major=TAHOE_XNU_MAJOR, environ={ENV_TAHOE_3802: "1"}
        )
        self.assertEqual(set(filled.keys()), set(base.keys()))
        self.assertGreater(len(filled), 0)

    def test_extreme_opt_in_refills(self) -> None:
        base = self._tahoe_base()
        filled = filter_tahoe_3802_patches(
            base, xnu_major=TAHOE_XNU_MAJOR, environ={ENV_EXTREME: "1"}
        )
        self.assertIn("Metal 3802 Common", filled)
        self.assertFalse(filled == {})

    def test_stage_patches_method_has_no_permanent_empty(self) -> None:
        stage = STAGE_M.read_text(encoding="utf-8")
        # Must route through filter (opt-in refill), not bare Tahoe return {}.
        self.assertIn("filter_tahoe_3802_patches", stage)
        self.assertIn("X86_TAHOE_3802", stage)
        # The old permanent-guard comment must not remain as the only path.
        self.assertNotIn(
            "Safety guard: skip this patchset entirely until a working fix is found.",
            stage,
        )


class StageSidecarTest(unittest.TestCase):
    def test_stage_exists_and_shared_untouched_marker(self) -> None:
        self.assertTrue(STAGE_M.is_file(), "missing metal_3802.py.stage-M")
        self.assertTrue(SHARED_METAL.is_file())
        stage = STAGE_M.read_text(encoding="utf-8")
        shared = SHARED_METAL.read_text(encoding="utf-8")
        self.assertIn("filter_tahoe_3802_patches", stage)
        self.assertIn("X86_TAHOE_3802", stage)
        # Live shared already MC-integrated — filter wired for Tahoe opt-in.
        self.assertIn("filter_tahoe_3802_patches", shared)
        self.assertIn("os_data.tahoe", shared)

    def test_stage_parses_as_python(self) -> None:
        tree = ast.parse(STAGE_M.read_text(encoding="utf-8"))
        self.assertTrue(
            any(
                isinstance(n, ast.ClassDef) and n.name == "LegacyMetal3802"
                for n in tree.body
            )
        )


if __name__ == "__main__":
    unittest.main()
