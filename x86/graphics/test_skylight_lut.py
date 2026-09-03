"""Fixtures for SkyLight / RenderBox compositor hooks (no guessed bytes)."""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.detect import TAHOE_XNU_MAJOR  # noqa: E402
from x86.graphics.skylight_lut import (  # noqa: E402
    COMPOSITOR_PLUGIN_STEM_ALLOWLIST,
    RENDERBOX_METALLIB_RELATIVE,
    enumerate_evidence_skylight_plugins,
    metal_31001_common_patches,
    resolve_renderbox_metallib_payload,
    serialize_skylight_lut_fields,
)
from x86.graphics.yellow_screen import (  # noqa: E402
    TAHOE_YELLOW_SCREEN_PATCH_NAME,
    yellow_screen_mitigations,
)


def _write_renderbox_tree(root: Path, xnu_major: int, payload: bytes = b"RB") -> Path:
    metallib = root / f"RenderBox-{xnu_major}" / RENDERBOX_METALLIB_RELATIVE
    metallib.parent.mkdir(parents=True)
    metallib.write_bytes(payload)
    return metallib


class RenderBoxPayloadGateTest(unittest.TestCase):
    def test_missing_payload_is_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(
                resolve_renderbox_metallib_payload(
                    TAHOE_XNU_MAJOR,
                    search_roots=[Path(tmp)],
                )
            )
            self.assertEqual(
                metal_31001_common_patches(
                    TAHOE_XNU_MAJOR,
                    search_roots=[Path(tmp)],
                ),
                {},
            )

    def test_present_payload_emits_oclp_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_renderbox_tree(root, TAHOE_XNU_MAJOR)
            folder = resolve_renderbox_metallib_payload(
                TAHOE_XNU_MAJOR,
                search_roots=[root],
            )
            self.assertEqual(folder, f"RenderBox-{TAHOE_XNU_MAJOR}")
            patches = metal_31001_common_patches(
                TAHOE_XNU_MAJOR,
                search_roots=[root],
            )
            self.assertIn("Metal 31001 Common", patches)
            resources = patches["Metal 31001 Common"]["Overwrite System Volume"][
                "/System/Library/PrivateFrameworks/RenderBox.framework/Versions/A/Resources"
            ]
            self.assertEqual(resources["default.metallib"], folder)

    def test_legacy_metal_31001_class_uses_gate(self) -> None:
        from opencore_legacy_patcher.sys_patch.patchsets.shared_patches.metal_31001 import (
            LegacyMetal31001,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty = LegacyMetal31001(
                TAHOE_XNU_MAJOR,
                0,
                "25A",
                search_roots=[root],
            )
            self.assertEqual(empty.patches(), {})
            _write_renderbox_tree(root, TAHOE_XNU_MAJOR)
            filled = LegacyMetal31001(
                TAHOE_XNU_MAJOR,
                0,
                "25A",
                search_roots=[root],
            )
            self.assertIn("Metal 31001 Common", filled.patches())

    def test_detect_json_fields(self) -> None:
        fields = serialize_skylight_lut_fields(TAHOE_XNU_MAJOR, search_roots=[Path("/nope")])
        self.assertFalse(fields["renderbox_metallib_present"])
        self.assertTrue(fields["skylight_plugins_require_nonmetal_stubs"])
        self.assertIn("agdpmod=pikera", fields["documented_graphics_boot_args"])
        self.assertIn("ngfxgl=1", fields["documented_graphics_boot_args"])
        self.assertNotIn("disable_metal_compositor", fields["documented_graphics_boot_args"])


class SkyLightPluginAllowlistTest(unittest.TestCase):
    def test_dropboxhack_never_selected_for_compositor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "DropboxHack.dylib").write_bytes(b"fake")
            (directory / "DropboxHack.txt").write_text("WindowServer\n", encoding="utf-8")
            self.assertEqual(enumerate_evidence_skylight_plugins(directory), {})

    def test_allowlisted_stem_without_sha_pin_is_skipped(self) -> None:
        stem = next(iter(COMPOSITOR_PLUGIN_STEM_ALLOWLIST))
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / f"{stem}.dylib").write_bytes(b"unpinned")
            (directory / f"{stem}.txt").write_text("WindowServer\n", encoding="utf-8")
            self.assertEqual(enumerate_evidence_skylight_plugins(directory), {})

    def test_allowlisted_stem_with_matching_sha_is_selected(self) -> None:
        import x86.graphics.skylight_lut as module

        stem = "CompositorLUT"
        blob = b"pinned-compositor-lut"
        digest = hashlib.sha256(blob).hexdigest()
        original = dict(module.COMPOSITOR_PLUGIN_SHA256)
        try:
            module.COMPOSITOR_PLUGIN_SHA256[stem] = digest
            with tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                (directory / f"{stem}.dylib").write_bytes(blob)
                (directory / f"{stem}.txt").write_text("WindowServer\n", encoding="utf-8")
                files = enumerate_evidence_skylight_plugins(directory)
                self.assertEqual(files[f"{stem}.dylib"], "SkyLightPlugins")
                self.assertEqual(files[f"{stem}.txt"], "SkyLightPlugins")
        finally:
            module.COMPOSITOR_PLUGIN_SHA256.clear()
            module.COMPOSITOR_PLUGIN_SHA256.update(original)


class MitigationListTest(unittest.TestCase):
    def test_renderbox_mitigation_when_payload_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_renderbox_tree(root, TAHOE_XNU_MAJOR)
            items = yellow_screen_mitigations(
                "MacPro5,1",
                gpu_archs=["Vega", "0x687F"],
                xnu_major=TAHOE_XNU_MAJOR,
                cpu_generation=4,
                search_roots=[root],
            )
            self.assertIn("renderbox_metallib_if_payload", items)
            self.assertIn("window_server_cache_disable", items)

    def test_patch_name_constant_unchanged(self) -> None:
        self.assertEqual(TAHOE_YELLOW_SCREEN_PATCH_NAME, "Tahoe Yellow Screen Mitigations")


if __name__ == "__main__":
    unittest.main()
