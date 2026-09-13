"""Track L5-R — SkyLight/CoreDisplay OVERWRITE rootpatch tests (*.stage-L5)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

_MOD_PATH = REPO / "x86" / "graphics" / "skylight_lut_rootpatch.py"
_SPEC = importlib.util.spec_from_file_location(
    "x86.graphics.skylight_lut_rootpatch", _MOD_PATH
)
assert _SPEC and _SPEC.loader
m = importlib.util.module_from_spec(_SPEC)
sys.modules["x86.graphics.skylight_lut_rootpatch"] = m
_SPEC.loader.exec_module(m)

from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType  # noqa: E402


class ExtremeOverwriteTest(unittest.TestCase):
    def test_default_empty(self) -> None:
        self.assertEqual(m.sys_patch_hooks(25, 0, "26.0", environ={}), {})

    def test_pre_tahoe_empty(self) -> None:
        self.assertEqual(
            m.sys_patch_hooks(24, 0, "15.0", environ={m.ENV_EXTREME: "1"}),
            {},
        )

    def test_extreme_fills_overwrite(self) -> None:
        hooks = m.sys_patch_hooks(25, 0, "26.0", environ={m.ENV_EXTREME: "1"})
        self.assertIn(m.PATCH_NAME, hooks)
        body = hooks[m.PATCH_NAME]
        self.assertIn(PatchType.OVERWRITE_SYSTEM_VOLUME, body)
        ow = body[PatchType.OVERWRITE_SYSTEM_VOLUME]
        self.assertEqual(
            ow["/System/Library/PrivateFrameworks"]["SkyLight.framework"],
            "10.14.6-24",
        )
        self.assertEqual(
            ow["/System/Library/Frameworks"]["CoreDisplay.framework"],
            "10.14.4-24",
        )
        self.assertNotIn(PatchType.MERGE_SYSTEM_VOLUME, body)

    def test_merge_mode(self) -> None:
        env = {m.ENV_EXTREME: "1", m.ENV_MODE: "merge", m.ENV_SLICES: "skylight"}
        hooks = m.sys_patch_hooks(25, 0, "26.0", environ=env)
        body = hooks[m.PATCH_NAME]
        self.assertIn(PatchType.MERGE_SYSTEM_VOLUME, body)
        self.assertNotIn(PatchType.OVERWRITE_SYSTEM_VOLUME, body)

    def test_coredisplay_hs(self) -> None:
        env = {
            m.ENV_EXTREME: "1",
            m.ENV_SLICES: "coredisplay",
            m.ENV_COREDISPLAY_VARIANT: "hs",
        }
        hooks = m.sys_patch_hooks(25, 0, "26.0", environ=env)
        ow = hooks[m.PATCH_NAME][PatchType.OVERWRITE_SYSTEM_VOLUME]
        self.assertEqual(
            ow["/System/Library/Frameworks"]["CoreDisplay.framework"],
            "10.13.6-24",
        )


class PayloadAndBinaryTest(unittest.TestCase):
    def test_resolve_psp(self) -> None:
        psp = REPO.parent / "26x86-PatcherSupportPkg" / "Universal-Binaries"
        if not psp.is_dir():
            self.skipTest("PSP Universal-Binaries missing")
        self.assertEqual(
            m.resolve_skylight_payload(25, search_roots=[psp]), "10.14.6-24"
        )
        self.assertEqual(
            m.resolve_coredisplay_payload(25, search_roots=[psp]), "10.14.4-24"
        )

    def test_l5_patched_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staged = (
                root
                / "L5-patched"
                / "System/Library/PrivateFrameworks/SkyLight.framework/Versions/A"
            )
            staged.mkdir(parents=True)
            (staged / "SkyLight").write_bytes(b"\x00L5\x00")
            hooks = m.build_rootpatch_dict(
                25,
                search_roots=[root],
                environ={m.ENV_EXTREME: "1", m.ENV_SLICES: "binary"},
            )
            ow = hooks[m.PATCH_NAME][PatchType.OVERWRITE_SYSTEM_VOLUME]
            dest = (
                "/System/Library/PrivateFrameworks/SkyLight.framework/Versions/A"
            )
            self.assertEqual(ow[dest]["SkyLight"], "L5-patched")


class ContractAndBCoordinationTest(unittest.TestCase):
    def test_detect_fields(self) -> None:
        fields = m.serialize_track_detect_fields(
            environ={m.ENV_EXTREME: "1"}, assume_tahoe=True
        )
        block = fields["skylight_lut_rootpatch"]
        self.assertEqual(block["track"], "L5")
        self.assertEqual(block["track_b_commit"], "55c3802")
        self.assertEqual(block["integrate_commit"], "52f7298")
        self.assertFalse(block["runtime_inject"])
        self.assertTrue(block["would_emit_patches"])

    def test_b_sibling_markers(self) -> None:
        ids = {c["patch_id"] for c in m.BINARY_PATCH_CANDIDATES}
        self.assertIn("L5-SL-LUT-MARKER-V1", ids)
        self.assertIn("L5-CD-GAMMA-PROBE-V1", ids)
        siblings = {c.get("b_sibling") for c in m.BINARY_PATCH_CANDIDATES}
        self.assertIn("SL-LUT-MARKER-V1", siblings)

    def test_b_cross_link_exists(self) -> None:
        b = REPO / "x86" / "graphics" / "skylight_analysis.py"
        text = b.read_text(encoding="utf-8")
        self.assertIn("skylight_lut_rootpatch", text)
        self.assertIn("EVIDENCE_L5R_ROOTPATCH", text)

    def test_no_inject_apis(self) -> None:
        src = _MOD_PATH.read_text(encoding="utf-8")
        self.assertNotIn("mach_inject", src)
        self.assertNotIn("DYLD_INSERT_LIBRARIES", src)


if __name__ == "__main__":
    unittest.main()
