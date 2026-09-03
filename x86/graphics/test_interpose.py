"""Track I Extreme-Interpose unit tests (owned module only)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.interpose_apply import (  # noqa: E402
    apply_extreme_interpose,
    copy_interpose_artifacts,
    interpose_install_manifest,
)
from x86.graphics.interpose_gate import (  # noqa: E402
    ENV_X86_EXTREME,
    ENV_X86_EXTREME_INSTALL,
    extreme_install_opt_in,
    extreme_opt_in,
    gate_blocks_reason,
)
from x86.graphics.interpose_payload import (  # noqa: E402
    enumerate_extreme_interpose_sources,
    payload_status,
)
from x86.graphics.interpose_plan import (  # noqa: E402
    PLUGIN_STEM,
    plan_summary,
    root_volume_interpose_recipe,
    serialize_interpose_fields,
)
from x86.graphics.interpose_symbols import INTERPOSE_SYMBOLS  # noqa: E402


class GateTest(unittest.TestCase):
    def test_default_blocked(self) -> None:
        env = {k: v for k, v in os.environ.items() if not k.startswith("X86_")}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(extreme_opt_in())
            self.assertIsNotNone(gate_blocks_reason())

    def test_extreme_arms_recipe_without_install_flag(self) -> None:
        with mock.patch.dict(os.environ, {ENV_X86_EXTREME: "1"}, clear=False):
            os.environ.pop(ENV_X86_EXTREME_INSTALL, None)
            self.assertTrue(extreme_opt_in())
            self.assertIsNone(gate_blocks_reason(require_install=False))
            self.assertFalse(extreme_install_opt_in())
            self.assertIsNotNone(gate_blocks_reason(require_install=True))

    def test_live_library_needs_install_flag(self) -> None:
        with mock.patch.dict(
            os.environ,
            {ENV_X86_EXTREME: "1", ENV_X86_EXTREME_INSTALL: "1"},
            clear=False,
        ):
            self.assertTrue(extreme_install_opt_in())
            self.assertIsNone(gate_blocks_reason(require_install=True))


class PlanTest(unittest.TestCase):
    def test_symbols_include_avx_and_lut(self) -> None:
        groups = {s.mode_group for s in INTERPOSE_SYMBOLS}
        self.assertIn("avx", groups)
        self.assertIn("lut", groups)
        self.assertIn("loader", groups)

    def test_recipe_armed_without_sha_pin(self) -> None:
        with mock.patch.dict(os.environ, {ENV_X86_EXTREME: "1"}, clear=False):
            recipe = root_volume_interpose_recipe(repo_root=REPO)
            self.assertIn("Extreme Interpose Compositor", recipe)
            entry = recipe["Extreme Interpose Compositor"]
            self.assertIn(entry.get("status"), {"ready", "build_failed"})
            if entry.get("status") == "ready":
                self.assertTrue(entry.get("dylib"))
                self.assertTrue(entry.get("sha256"))
                self.assertFalse(
                    plan_summary(extreme=True).get("sha_pin_required", True)
                )

    def test_recipe_empty_without_extreme(self) -> None:
        env = {k: v for k, v in os.environ.items() if not k.startswith("X86_")}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(root_volume_interpose_recipe(repo_root=REPO), {})

    def test_serialize_fields(self) -> None:
        fields = serialize_interpose_fields(repo_root=REPO)
        self.assertEqual(fields["skylight_track_I"]["track"], "I")
        self.assertFalse(fields["extreme_interpose"]["apple_blobs_vendored"])
        self.assertFalse(fields["extreme_interpose"]["sha_pin_required"])
        self.assertIn(
            "src/ExtremeCompositorInterpose.c",
            fields["extreme_interpose"]["sources"],
        )

    def test_payload_sources_present(self) -> None:
        sources = enumerate_extreme_interpose_sources(repo_root=REPO)
        missing = [k for k, v in sources.items() if not v]
        self.assertEqual(missing, [], msg=f"missing Track I sources: {missing}")
        status = payload_status(repo_root=REPO)
        self.assertTrue(status["sources_complete"])
        self.assertEqual(PLUGIN_STEM, "ExtremeCompositor")

    def test_plan_forbidden_mentions_byte_patches(self) -> None:
        summary = plan_summary(extreme=False)
        self.assertTrue(any("byte patch" in f.lower() for f in summary["forbidden"]))


@unittest.skipUnless(sys.platform == "darwin", "dylib build needs macOS clang")
class ApplyTest(unittest.TestCase):
    def test_apply_builds_copies_and_guides(self) -> None:
        with mock.patch.dict(os.environ, {ENV_X86_EXTREME: "1"}, clear=False):
            with tempfile.TemporaryDirectory() as tmp:
                plugins = Path(tmp) / "plugins"
                result = apply_extreme_interpose(
                    REPO,
                    dest_plugins=plugins,
                    live_library_plugins=False,
                )
                self.assertTrue(result["applied"], msg=result)
                self.assertIn("Extreme Interpose Compositor", result["recipe"])
                self.assertTrue((plugins / f"{PLUGIN_STEM}.dylib").is_file())
                self.assertTrue((plugins / f"{PLUGIN_STEM}.txt").is_file())
                guide = Path(result["steps"]["guide"])
                self.assertTrue(guide.is_file())
                self.assertIn("DYLD_INSERT_LIBRARIES", guide.read_text(encoding="utf-8"))

    def test_manifest_ok(self) -> None:
        with mock.patch.dict(os.environ, {ENV_X86_EXTREME: "1"}, clear=False):
            man = interpose_install_manifest(REPO)
            self.assertTrue(man.get("ok"), msg=man)
            self.assertTrue(Path(man["dylib"]).is_file())


if __name__ == "__main__":
    unittest.main()
