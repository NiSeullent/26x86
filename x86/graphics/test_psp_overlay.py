"""Track F psp_overlay unit tests (loads module by path; no package __init__)."""
from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
MODULE = REPO / "x86" / "graphics" / "psp_overlay.py"

def _load():
    spec = importlib.util.spec_from_file_location("psp_overlay_under_test", MODULE)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

class InventoryTest(unittest.TestCase):
    def test_expected_mtl_bundles(self):
        mod = _load()
        self.assertEqual(set(mod.TAHOE_PSP_YELLOW_SCREEN_MTL_BUNDLES), {
            "AMDMTLBronzeDriver.bundle", "AMDRadeonX5000MTLDriver.bundle",
        })

class PresenceTest(unittest.TestCase):
    def test_readme_only_not_injectable(self):
        mod = _load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "12.5-25").mkdir()
            (root / "12.5-25" / "README.md").write_text("x\n", encoding="utf-8")
            self.assertEqual(mod.discover_tahoe_psp_overlay_versions([root]), [])
            self.assertFalse(mod.tahoe_psp_overlay_status([root])["present"])
            self.assertIn("AMDMTLBronzeDriver.bundle", mod.format_tahoe_psp_overlay_missing_message([root]))

    def test_injects_when_bundle_present(self):
        mod = _load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            b = root / "12.5-25/System/Library/Extensions/AMDRadeonX5000MTLDriver.bundle/Contents"
            b.mkdir(parents=True)
            (b / "Info.plist").write_text("<plist/>", encoding="utf-8")
            dest = root / "mounted"; dest.mkdir()
            self.assertEqual(len(mod.tahoe_psp_version_copy_pairs(dest, [root])), 1)
            self.assertEqual(mod.tahoe_psp_overlay_status([root])["guidance"], [])

class DetectMergeTest(unittest.TestCase):
    def test_merge(self):
        mod = _load()
        with tempfile.TemporaryDirectory() as tmp:
            out = mod.merge_tahoe_psp_overlay_into_detect({"yellow_screen_notes": ["base"]}, [Path(tmp)])
            self.assertIn("tahoe_psp_overlay", out)
            self.assertGreater(len(out["yellow_screen_notes"]), 1)

class StageSidecarTest(unittest.TestCase):
    def test_stage_f_exist(self):
        self.assertTrue((REPO / "x86/graphics/yellow_screen.py.stage-F").is_file())
        self.assertTrue((REPO / "opencore_legacy_patcher/sys_patch/utilities/dmg_mount.py.stage-F").is_file())
        self.assertTrue((REPO / "opencore_legacy_patcher/sys_patch/sys_patch.py.stage-F").is_file())
        self.assertTrue(MODULE.is_file())

if __name__ == "__main__":
    unittest.main()
