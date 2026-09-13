"""Track E — ``metallib_renderbox`` soft-import + Tahoe RenderBox-25 gap fixtures."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.metallib_preflight import METALLIB_MAGIC, MIN_RENDERBOX_METALLIB_BYTES  # noqa: E402
from x86.graphics.metallib_renderbox import (  # noqa: E402
    renderbox_gap_status,
    serialize_track_detect_fields,
    sys_patch_hooks,
)
from x86.graphics.skylight_lut import RENDERBOX_METALLIB_RELATIVE  # noqa: E402
from x86.graphics.skylight_tracks import resolve_track_module  # noqa: E402


class TrackEResolveTest(unittest.TestCase):
    def test_g_resolves_metallib_renderbox(self) -> None:
        mod, name = resolve_track_module("E")
        self.assertIsNotNone(mod)
        self.assertEqual(name, "x86.graphics.metallib_renderbox")
        self.assertTrue(callable(getattr(mod, "sys_patch_hooks")))


class RenderBox25GapTest(unittest.TestCase):
    def test_missing_payload_noop_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status = renderbox_gap_status(25, search_roots=[Path(tmp)])
            self.assertTrue(status["noop"])
            self.assertFalse(status["present"])
            self.assertEqual(sys_patch_hooks(25, 0, "26.0", search_roots=[Path(tmp)]), {})

    def test_mock_tahoe_path_with_mtlb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metallib = root / "RenderBox-25" / RENDERBOX_METALLIB_RELATIVE
            metallib.parent.mkdir(parents=True)
            metallib.write_bytes(METALLIB_MAGIC + (b"\x02" * MIN_RENDERBOX_METALLIB_BYTES))
            status = renderbox_gap_status(25, search_roots=[root])
            self.assertTrue(status["valid_for_overwrite"])
            hooks = sys_patch_hooks(25, 0, "26.0", search_roots=[root])
            self.assertIn("Metal 31001 Common", hooks)

    def test_detect_fields_include_track_e(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fields = serialize_track_detect_fields(25, search_roots=[Path(tmp)])
            self.assertEqual(fields["metallib_track"], "E")
            self.assertIn("renderbox_track_e", fields)
            self.assertTrue(fields["legacy_metal_31001_noop"])


class ProvisionalRootPatchPlanTest(unittest.TestCase):
    def test_provisional_emits_31001_with_warning(self) -> None:
        from x86.graphics.metallib_preflight import (
            METALLIB_MAGIC,
            MIN_RENDERBOX_METALLIB_BYTES,
            PROVISIONAL_MARKER_NAME,
            metal_31001_root_patch_plan,
        )
        from x86.graphics.skylight_lut import RENDERBOX_METALLIB_RELATIVE
        from opencore_legacy_patcher.sys_patch.patchsets.shared_patches.metal_31001 import (
            LegacyMetal31001,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metallib = root / "RenderBox-25" / RENDERBOX_METALLIB_RELATIVE
            metallib.parent.mkdir(parents=True)
            metallib.write_bytes(METALLIB_MAGIC + (b"\x04" * MIN_RENDERBOX_METALLIB_BYTES))
            (root / "RenderBox-25" / PROVISIONAL_MARKER_NAME).write_text(
                "from-24\n", encoding="utf-8"
            )
            plan = metal_31001_root_patch_plan(25, search_roots=[root], dry_run=True)
            self.assertTrue(plan["would_emit"])
            self.assertTrue(plan["provisional"])
            self.assertFalse(plan["authentic"])
            self.assertTrue(plan["warnings"])
            self.assertIn("Liquid Glass", plan["warnings"][0])
            self.assertIn("Metal 31001 Common", plan["patches"])
            live = LegacyMetal31001(25, 0, "26.0", search_roots=[root]).patches()
            self.assertEqual(list(live.keys()), list(plan["patches"].keys()))

    def test_authentic_no_provisional_flag(self) -> None:
        from x86.graphics.metallib_preflight import (
            METALLIB_MAGIC,
            MIN_RENDERBOX_METALLIB_BYTES,
            metal_31001_root_patch_plan,
        )
        from x86.graphics.skylight_lut import RENDERBOX_METALLIB_RELATIVE

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metallib = root / "RenderBox-25" / RENDERBOX_METALLIB_RELATIVE
            metallib.parent.mkdir(parents=True)
            metallib.write_bytes(METALLIB_MAGIC + (b"\x05" * MIN_RENDERBOX_METALLIB_BYTES))
            plan = metal_31001_root_patch_plan(25, search_roots=[root], dry_run=True)
            self.assertTrue(plan["would_emit"])
            self.assertFalse(plan["provisional"])
            self.assertTrue(plan["authentic"])
            self.assertEqual(plan["warnings"], [])


if __name__ == "__main__":
    unittest.main()
