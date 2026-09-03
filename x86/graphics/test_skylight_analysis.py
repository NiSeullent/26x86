"""Track B fixtures — load skylight_analysis by path (no shared __init__ edits)."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
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

    def test_no_byte_patch_is_active_or_scaffold(self) -> None:
        for candidate in self.m.SKYLIGHT_HOOK_REGISTRY:
            if candidate.action.value == "byte_patch":
                self.assertEqual(candidate.status, self.m.HookStatus.REJECTED)
                self.assertFalse(candidate.tahoe_allowed)

    def test_framework_merge_blocked_on_tahoe(self) -> None:
        candidate = self.m.hook_by_id("SL-FRAMEWORK-MERGE")
        assert candidate is not None
        self.assertEqual(candidate.status, self.m.HookStatus.BLOCKED)
        self.assertFalse(candidate.tahoe_allowed)

    def test_poc_table_hides_rejected_by_default(self) -> None:
        ids = {row["hook_id"] for row in self.m.poc_registration_table()}
        self.assertNotIn("SL-BYTEPATCH-LUT", ids)
        self.assertIn("SL-PLUGIN-PROTOCOL", ids)

    def test_g_contract_exports(self) -> None:
        self.assertTrue(callable(self.m.sys_patch_hooks))
        self.assertTrue(callable(self.m.serialize_track_detect_fields))
        payload = self.m.sys_patch_hooks(25)
        self.assertEqual(payload["track"], "B")
        fields = self.m.serialize_track_detect_fields(25, search_roots=[Path("/nope")])
        self.assertEqual(fields["skylight_track"], "B")


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


class PayloadAndScaffoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = _load_analysis()

    def test_tahoe_payload_folder_capped_at_24(self) -> None:
        self.assertEqual(self.m.non_metal_skylight_payload_folder(25), "10.14.6-24")

    def test_framework_merge_scaffold_empty_even_with_payload(self) -> None:
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
            )
            self.assertEqual(scaffold["status"], "blocked")
            self.assertEqual(scaffold["patches"], {})
            self.assertEqual(scaffold["payload_folder"], folder)

    def test_bytepatch_scaffold_empty(self) -> None:
        scaffold = self.m.emit_hook_scaffold("SL-BYTEPATCH-LUT")
        self.assertEqual(scaffold["status"], "rejected")
        self.assertEqual(scaffold["patches"], {})

    def test_plugin_scaffold_requires_sha_pin(self) -> None:
        # Optional dependency on skylight_lut — skip soft if package init broken.
        try:
            import x86.graphics.skylight_lut as lut
        except Exception:
            self.skipTest("skylight_lut unavailable via package import")
            return
        stem = "CompositorLUT"
        blob = b"track-b-compositor-lut"
        digest = hashlib.sha256(blob).hexdigest()
        original = dict(lut.COMPOSITOR_PLUGIN_SHA256)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                (directory / f"{stem}.dylib").write_bytes(blob)
                (directory / f"{stem}.txt").write_text("WindowServer\n", encoding="utf-8")
                empty = self.m.emit_hook_scaffold(
                    "SL-PLUGIN-PROTOCOL", plugin_overlay_dir=directory
                )
                self.assertEqual(empty["patches"], {})
                lut.COMPOSITOR_PLUGIN_SHA256[stem] = digest
                filled = self.m.emit_hook_scaffold(
                    "SL-PLUGIN-PROTOCOL", plugin_overlay_dir=directory
                )
                self.assertIn("Overwrite Data Volume", filled["patches"])
        finally:
            lut.COMPOSITOR_PLUGIN_SHA256.clear()
            lut.COMPOSITOR_PLUGIN_SHA256.update(original)


if __name__ == "__main__":
    unittest.main()
