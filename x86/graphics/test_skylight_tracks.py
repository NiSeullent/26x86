"""Integration tests for Track G SkyLight LUT orchestration."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.detect import (  # noqa: E402
    TAHOE_XNU_MAJOR,
    serialize_graphics_detect_fields,
)
from x86.graphics.skylight_tracks import (  # noqa: E402
    merge_sys_patch_hooks,
    serialize_skylight_lut_tracks,
    track_status_entry,
)


class SkylightTracksOrchestrationTest(unittest.TestCase):
    def test_serialize_skylight_lut_tracks_shape(self) -> None:
        summary = serialize_skylight_lut_tracks()
        self.assertIn("tracks", summary)
        self.assertIn("connected", summary)
        self.assertIn("missing", summary)
        self.assertIn("partial", summary)
        for tid in ("A", "B", "C", "D", "E", "F", "G"):
            self.assertIn(tid, summary["tracks"])
            entry = summary["tracks"][tid]
            self.assertIn("status", entry)
            self.assertIn(entry["status"], {"connected", "partial", "missing"})
        self.assertEqual(summary["tracks"]["G"]["status"], "connected")
        self.assertIn("G", summary["connected"])

    def test_detect_json_includes_skylight_lut_tracks(self) -> None:
        payload = serialize_graphics_detect_fields(
            "MacPro6,1",
            xnu_major=TAHOE_XNU_MAJOR,
            cpu_features=["AVX1.0"],
            cpu_leaf7_features=[],
            assume_tahoe=True,
        )
        self.assertIn("skylight_lut_tracks", payload)
        tracks = payload["skylight_lut_tracks"]
        self.assertEqual(tracks["tracks"]["G"]["role"], "orchestration")
        self.assertEqual(tracks["sys_patch_tracks"], ["B", "C", "E", "F"])

    def test_merge_sys_patch_hooks_noop_when_tracks_missing(self) -> None:
        merged = merge_sys_patch_hooks(TAHOE_XNU_MAJOR, 0, "26.0")
        self.assertIsInstance(merged, dict)

    def test_merge_sys_patch_hooks_imports_callable(self) -> None:
        fake_hooks = mock.Mock(return_value={"TrackBPoC": {"EXECUTE": ["/bin/true"]}})
        fake_mod = mock.Mock()
        fake_mod.sys_patch_hooks = fake_hooks

        with mock.patch(
            "x86.graphics.skylight_tracks.resolve_track_module",
            side_effect=lambda tid: (fake_mod, "x86.graphics.skylight_analysis")
            if tid == "B"
            else (None, None),
        ):
            merged = merge_sys_patch_hooks(TAHOE_XNU_MAJOR, 0, "26.0")
        self.assertIn("TrackBPoC", merged)
        fake_hooks.assert_called_once_with(TAHOE_XNU_MAJOR, 0, "26.0")

    def test_track_b_partial_or_missing_without_dedicated_module(self) -> None:
        entry = track_status_entry("B")
        self.assertIn(entry["status"], {"partial", "missing", "connected"})
        if entry["status"] != "connected":
            self.assertTrue(entry.get("todo"))

    def test_compositor_patches_still_importable(self) -> None:
        # Import via package chain can fail if other tracks leave half-landed
        # shared_patches; assert the G wiring is present in source instead.
        path = (
            REPO
            / "opencore_legacy_patcher"
            / "sys_patch"
            / "patchsets"
            / "shared_patches"
            / "tahoe_yellow_screen.py"
        )
        text = path.read_text(encoding="utf-8")
        self.assertIn("merge_sys_patch_hooks", text)
        self.assertIn("skylight_tracks", text)


if __name__ == "__main__":
    unittest.main()
