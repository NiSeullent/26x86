"""Track B fixtures — path-load skylight_analysis (no shared __init__ edits)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYSIS_PATH = HERE / "skylight_analysis.py"


def _load_analysis():
    spec = importlib.util.spec_from_file_location(
        "skylight_analysis_track_b", ANALYSIS_PATH
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class RegistryIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = _load_analysis()

    def test_no_blocked_or_rejected_status(self) -> None:
        for candidate in self.m.SKYLIGHT_HOOK_REGISTRY:
            self.assertNotEqual(candidate.status.value, "blocked")
            self.assertNotEqual(candidate.status.value, "rejected")
            self.assertNotIn(candidate.status.value, {"blocked", "rejected"})

    def test_framework_merge_is_extreme(self) -> None:
        candidate = self.m.hook_by_id("SL-FRAMEWORK-MERGE")
        assert candidate is not None
        self.assertEqual(candidate.status, self.m.HookStatus.EXTREME)
        self.assertTrue(candidate.requires_extreme)
        self.assertTrue(candidate.tahoe_allowed)

    def test_bytepatch_is_extreme(self) -> None:
        candidate = self.m.hook_by_id("SL-BYTEPATCH-LUT")
        assert candidate is not None
        self.assertEqual(candidate.status, self.m.HookStatus.EXTREME)
        self.assertTrue(candidate.requires_extreme)

    def test_poc_table_includes_extreme_hooks(self) -> None:
        ids = {row["hook_id"] for row in self.m.poc_registration_table()}
        self.assertIn("SL-BYTEPATCH-LUT", ids)
        self.assertIn("SL-FRAMEWORK-MERGE", ids)

    def test_role_split_with_l5r_documented(self) -> None:
        split = self.m.ROLE_SPLIT_WITH_L5R
        self.assertIn("B=analysis/bytepatch API", split)
        self.assertIn("L5-R=sys_patch MERGE/OVERWRITE", split)
        fields = self.m.serialize_skylight_analysis_fields(25)
        self.assertEqual(fields["role_split_with_l5r"], split)
        blob = ANALYSIS_PATH.read_text(encoding="utf-8")
        self.assertIn("Role split with L5-R", blob)
        self.assertIn("L5-patched/", blob)

    def test_g_contract_exports(self) -> None:
        self.assertTrue(callable(self.m.sys_patch_hooks))
        self.assertTrue(callable(self.m.serialize_track_detect_fields))
        payload = self.m.sys_patch_hooks(25, environ={})
        self.assertEqual(payload["track"], "B")
        self.assertFalse(payload["extreme"])
        fields = self.m.serialize_track_detect_fields(25, search_roots=[Path("/nope")])
        self.assertEqual(fields["skylight_track"], "B")
        self.assertIn("SL-BYTEPATCH-LUT", fields["extreme_hooks"])
        self.assertNotIn("blocked_on_tahoe", fields)
        self.assertNotIn("rejected_byte_patches", fields)


class ExtremeScaffoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = _load_analysis()

    def test_framework_merge_gated_without_extreme(self) -> None:
        scaffold = self.m.emit_hook_scaffold(
            "SL-FRAMEWORK-MERGE", xnu_major=25, environ={}
        )
        self.assertEqual(scaffold["status"], "extreme")
        self.assertEqual(scaffold["patches"], {})
        self.assertFalse(scaffold.get("extreme"))

    def test_framework_merge_emits_under_extreme_with_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = "10.14.6-24"
            binary = (
                root
                / folder
                / "System/Library/PrivateFrameworks/SkyLight.framework"
                / "Versions/A/SkyLight"
            )
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"fake-skylight")
            scaffold = self.m.emit_hook_scaffold(
                "SL-FRAMEWORK-MERGE",
                xnu_major=25,
                search_roots=[root],
                extreme=True,
            )
            self.assertTrue(scaffold["extreme"])
            self.assertEqual(scaffold["payload_folder"], folder)
            self.assertIn("Merge System Volume", scaffold["patches"])

    def test_bytepatch_dry_run_apply_path(self) -> None:
        marker = self.m.BYTE_PATCH_CANDIDATES[0]
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "SkyLight"
            target.write_bytes(b"HDR" + marker.find + b"TAIL")
            dry = self.m.dry_run_byte_patch(target, patch_id=marker.patch_id)
            self.assertTrue(dry["exists"])
            self.assertEqual(dry["candidates"][0]["matches"], 1)

            skipped = self.m.apply_byte_patch(
                target, patch_id=marker.patch_id, dry_run=False, environ={}
            )
            self.assertEqual(skipped["status"], "skipped_needs_extreme")

            applied = self.m.apply_byte_patch(
                target,
                patch_id=marker.patch_id,
                dry_run=False,
                extreme=True,
            )
            self.assertEqual(applied["status"], "applied")
            self.assertIn(marker.patch_id, applied["patch_ids_applied"])
            self.assertEqual(target.read_bytes(), b"HDR" + marker.replace + b"TAIL")
            self.assertTrue(Path(str(target) + ".pre-skylight-B").is_file())

    def test_sys_patch_hooks_includes_extreme_when_gated(self) -> None:
        cold = self.m.sys_patch_hooks(25, environ={})
        self.assertEqual(cold["hooks"], ["SL-PLUGIN-PROTOCOL"])
        hot = self.m.sys_patch_hooks(25, extreme=True)
        self.assertIn("SL-FRAMEWORK-MERGE", hot["hooks"])
        self.assertIn("SL-BYTEPATCH-LUT", hot["hooks"])
        self.assertTrue(hot["extreme"])


class NmFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = _load_analysis()

    def test_stock_fixture_lacks_plugin_entry(self) -> None:
        result = self.m.parse_nm_symbol_fixture(self.m.FIXTURE_NM_STOCK_COMPOSITOR)
        self.assertFalse(result["has_skylight_plugin_entry"])

    def test_patched_fixture_has_plugin_entry(self) -> None:
        result = self.m.parse_nm_symbol_fixture(
            self.m.FIXTURE_NM_PATCHED_SKYLIGHT_WITH_PLUGIN_LOADER
        )
        self.assertTrue(result["has_skylight_plugin_entry"])


if __name__ == "__main__":
    unittest.main()
