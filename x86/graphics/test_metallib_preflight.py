"""Track E — metallib preflight / opaque↔WS cache fixtures."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.detect import TAHOE_XNU_MAJOR  # noqa: E402
from x86.graphics.metallib_opaque import (  # noqa: E402
    opaque_shader_windowserver_relationship,
    serialize_opaque_shader_fields,
)
from x86.graphics.metallib_preflight import (  # noqa: E402
    METALLIB_MAGIC,
    MIN_RENDERBOX_METALLIB_BYTES,
    assess_metallib_gaps,
    gated_metal_31001_common_patches,
    probe_renderbox_metallib,
    serialize_metallib_preflight_fields,
)
from x86.graphics.skylight_lut import RENDERBOX_METALLIB_RELATIVE  # noqa: E402


def _write_renderbox(root: Path, xnu_major: int, payload: bytes) -> Path:
    metallib = root / f"RenderBox-{xnu_major}" / RENDERBOX_METALLIB_RELATIVE
    metallib.parent.mkdir(parents=True)
    metallib.write_bytes(payload)
    return metallib


class LegacyMetal31001NoOpTest(unittest.TestCase):
    def test_missing_payload_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = assess_metallib_gaps(TAHOE_XNU_MAJOR, search_roots=[Path(tmp)])
            self.assertTrue(report.legacy_metal_31001_noop)
            self.assertIn("absent", report.legacy_metal_31001_reason)
            self.assertEqual(
                gated_metal_31001_common_patches(
                    TAHOE_XNU_MAJOR, search_roots=[Path(tmp)]
                ),
                {},
            )
            self.assertTrue(report.metallib_support_pkg_blocked_on_tahoe)

    def test_tiny_fixture_allows_31001_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_renderbox(root, TAHOE_XNU_MAJOR, b"RB")
            patches = gated_metal_31001_common_patches(
                TAHOE_XNU_MAJOR, search_roots=[root]
            )
            self.assertEqual(list(patches.keys()), ["Metal 31001 Common"])
            self.assertNotIn("Metal 3802", str(patches))

    def test_large_non_mtlb_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            junk = b"NOTM" + (b"\0" * MIN_RENDERBOX_METALLIB_BYTES)
            _write_renderbox(root, TAHOE_XNU_MAJOR, junk)
            probe = probe_renderbox_metallib(TAHOE_XNU_MAJOR, search_roots=[root])
            self.assertFalse(probe.valid_for_overwrite)
            self.assertEqual(probe.no_op_reason, "payload_bad_magic")
            self.assertEqual(
                gated_metal_31001_common_patches(
                    TAHOE_XNU_MAJOR, search_roots=[root]
                ),
                {},
            )

    def test_mtlb_magic_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blob = METALLIB_MAGIC + (b"\x01" * MIN_RENDERBOX_METALLIB_BYTES)
            _write_renderbox(root, TAHOE_XNU_MAJOR, blob)
            report = assess_metallib_gaps(TAHOE_XNU_MAJOR, search_roots=[root])
            self.assertFalse(report.legacy_metal_31001_noop)
            self.assertTrue(report.safe_injection_allowed)

    def test_legacy_class_uses_gate(self) -> None:
        from opencore_legacy_patcher.sys_patch.patchsets.shared_patches.metal_31001 import (
            LegacyMetal31001,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty = LegacyMetal31001(TAHOE_XNU_MAJOR, 0, "25A", search_roots=[root])
            self.assertEqual(empty.patches(), {})
            _write_renderbox(root, TAHOE_XNU_MAJOR, b"RB")
            filled = LegacyMetal31001(TAHOE_XNU_MAJOR, 0, "25A", search_roots=[root])
            self.assertIn("Metal 31001 Common", filled.patches())


class OpaqueWindowServerRelationTest(unittest.TestCase):
    def test_relationship_warns_when_noop(self) -> None:
        rel = opaque_shader_windowserver_relationship(
            renderbox_metallib_present=False,
            legacy_metal_31001_noop=True,
        )
        self.assertEqual(
            rel["recommended_combo"],
            "apply_ws_cache_uchg_and_await_renderbox_payload",
        )
        self.assertIn("RenderBox-25", rel["warning"])

    def test_relationship_warns_when_provisional(self) -> None:
        rel = opaque_shader_windowserver_relationship(
            renderbox_metallib_present=True,
            legacy_metal_31001_noop=False,
            provisional_renderbox=True,
        )
        self.assertTrue(rel["provisional_renderbox"])
        self.assertIn("provisional", rel["recommended_combo"])
        self.assertIn("Liquid Glass", rel["warning"])

    def test_serialize_fields(self) -> None:
        fields = serialize_metallib_preflight_fields(
            TAHOE_XNU_MAJOR, search_roots=[Path("/nope")]
        )
        self.assertEqual(fields["metallib_track"], "E")
        self.assertTrue(fields["legacy_metal_31001_noop"])
        self.assertTrue(fields["metallib_support_pkg_blocked_on_tahoe"])
        opaque = serialize_opaque_shader_fields(
            renderbox_metallib_present=False,
            legacy_metal_31001_noop=True,
        )
        self.assertIn("opaque_shader_ws_cache", opaque)


if __name__ == "__main__":
    unittest.main()
