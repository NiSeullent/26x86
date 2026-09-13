"""Unit tests for Track C ColorSync / CoreDisplay modules (no shared-file edits)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.colorsync_icc import (  # noqa: E402
    SYSTEM_SRGB_ICC,
    colorsync_lut_execute_patches,
    colorsync_lut_mitigation_marker,
    purge_non_srgb_display_icc_overrides,
    serialize_colorsync_fields,
    serialize_track_detect_fields,
    sys_patch_hooks,
)
from x86.graphics.coredisplay_prefs import (  # noqa: E402
    FORBIDDEN_TAHOE_COREDISPLAY_WRITES,
    apply_coredisplay_pref_cleanup,
    coredisplay_cleanup_execute_patches,
    is_forbidden_tahoe_coredisplay_write,
)
from x86.graphics.detect import TAHOE_XNU_MAJOR  # noqa: E402
from x86.graphics.skylight_tracks import track_status_entry  # noqa: E402
from x86.graphics.yellow_screen import TAHOE_YELLOW_SCREEN_PATCH_NAME  # noqa: E402


class ColorSyncContractTest(unittest.TestCase):
    def test_execute_no_srgb_ln_duplicate(self) -> None:
        patches = colorsync_lut_execute_patches()
        joined = " ".join(patches)
        self.assertIn("com.apple.colorsyncd", joined)
        self.assertIn("Profiles/Displays", joined)
        self.assertNotIn("ln -sf", joined)
        self.assertNotIn(SYSTEM_SRGB_ICC, joined)

    def test_purge_keeps_srgb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sRGB Profile.icc").write_text("keep", encoding="utf-8")
            (root / "Broken.icc").write_text("bad", encoding="utf-8")
            removed = purge_non_srgb_display_icc_overrides(root)
            self.assertEqual(len(removed), 1)
            self.assertTrue((root / "sRGB Profile.icc").is_file())

    def test_sys_patch_hooks_tahoe(self) -> None:
        self.assertEqual(sys_patch_hooks(24, 0, "15.0"), {})
        hooks = sys_patch_hooks(TAHOE_XNU_MAJOR, 0, "26.0")
        self.assertIn(TAHOE_YELLOW_SCREEN_PATCH_NAME, hooks)
        execute = hooks[TAHOE_YELLOW_SCREEN_PATCH_NAME]["Execute"]
        self.assertTrue(any("colorsyncd" in cmd for cmd in execute))
        for cmd in execute:
            self.assertFalse(is_forbidden_tahoe_coredisplay_write(cmd))

    def test_detect_fields(self) -> None:
        fields = serialize_track_detect_fields()
        self.assertTrue(fields["colorsync_gpu_agnostic"])
        self.assertTrue(fields["colorsync_never_usemetal_no"])
        self.assertTrue(fields.get("coredisplay_tahoe_forbids_usemetal_no"))
        self.assertEqual(colorsync_lut_mitigation_marker(), "colorsync_lut_deep")
        self.assertTrue(serialize_colorsync_fields()["colorsync_extreme_does_not_unlock_nonmetal"])


class CoreDisplayContractTest(unittest.TestCase):
    def test_forbid_usemetal_no(self) -> None:
        for cmd in FORBIDDEN_TAHOE_COREDISPLAY_WRITES:
            self.assertTrue(is_forbidden_tahoe_coredisplay_write(cmd))
        self.assertEqual(coredisplay_cleanup_execute_patches(), {})

    def test_cleanup(self) -> None:
        result = apply_coredisplay_pref_cleanup(
            run_root=lambda argv: 0 if argv[-1] == "useMetal" else 1
        )
        self.assertEqual(result["deleted"], ["useMetal"])
        self.assertEqual(result["absent"], ["useIOP"])


class TrackGStatusTest(unittest.TestCase):
    def test_track_c_connected(self) -> None:
        entry = track_status_entry("C")
        self.assertEqual(entry["status"], "connected")
        self.assertTrue(entry["sys_patch_hooks"])
        self.assertTrue(entry["detect_fields"])
        self.assertIn("x86.graphics.colorsync_icc", entry["modules"])


if __name__ == "__main__":
    unittest.main()
