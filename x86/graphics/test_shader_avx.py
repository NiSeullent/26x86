"""Track J — shader / compositor AVX opcode gate tests (owned files only)."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.shader_avx_gate import (  # noqa: E402
    EXTREME_ENV,
    evaluate_shader_avx_gate,
    serialize_shader_avx_fields,
    sys_patch_hooks,
)
from x86.graphics.shader_avx_opcodes import (  # noqa: E402
    VMOVAPS_STORE_LO,
    count_opcode_hits,
    dense_vmovaps_windows,
    propose_sse_rewrites,
)
from x86.graphics.shader_avx_scan import (  # noqa: E402
    SEQUOIA_155_BASELINE,
    scan_standalone_file,
)

STAGE_PATH = Path(__file__).resolve().parent / "shader_avx_detect.stage-J.py"


def _load_stage():
    spec = importlib.util.spec_from_file_location(
        "shader_avx_detect_stage_J",
        STAGE_PATH,
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class OpcodeTableTest(unittest.TestCase):
    def test_sse_rewrite_preserves_length(self) -> None:
        blob = bytearray(VMOVAPS_STORE_LO + b"\x00\x00" + b"\x90" * 8)
        out = propose_sse_rewrites(bytes(blob), [0], "vmovaps_store_lo")
        self.assertEqual(len(out), len(blob))
        self.assertEqual(bytes(out[0:3]), bytes([0x90, 0x0F, 0x29]))

    def test_dense_window_detects_cluster(self) -> None:
        chunk = (VMOVAPS_STORE_LO + b"\x00\x00") * 10
        self.assertTrue(dense_vmovaps_windows(chunk, min_hits=8))
        sparse = VMOVAPS_STORE_LO + (b"\x00" * 200) + VMOVAPS_STORE_LO
        self.assertEqual(dense_vmovaps_windows(sparse, min_hits=8), [])


class GateDecisionTest(unittest.TestCase):
    def test_pre_avx_without_trampoline_demotes(self) -> None:
        d = evaluate_shader_avx_gate(
            cpu_has_avx1=False,
            cpu_has_avx2=False,
            probe_host=False,
            environ={EXTREME_ENV: "0"},
        )
        self.assertEqual(d.recommended_action, "monitor_demote_j_priority")
        self.assertFalse(d.sse_poc_armed)

    def test_extreme_sys_patch_empty(self) -> None:
        self.assertEqual(sys_patch_hooks(25, 0, "26.0"), {})

    def test_serialize_nested(self) -> None:
        payload = serialize_shader_avx_fields(
            cpu_has_avx1=False,
            cpu_has_avx2=False,
            environ={},
        )
        self.assertEqual(payload["shader_avx"]["track"], "J")
        self.assertIn("SIGILL", payload["shader_avx"]["scan_summary"]["baseline_verdict"])

    def test_baseline_zero_dense(self) -> None:
        self.assertEqual(
            SEQUOIA_155_BASELINE["findings"]["safari_style_dense_runs"],
            0,
        )


class StageJHookTest(unittest.TestCase):
    def test_stage_merge_does_not_overwrite(self) -> None:
        stage = _load_stage()
        base = {"shader_avx": {"track": "keep"}, "avx_available": False}
        merged = stage.merge_into_graphics_payload(base)
        self.assertEqual(merged["shader_avx"]["track"], "keep")

    def test_stage_merge_adds_when_absent(self) -> None:
        stage = _load_stage()
        merged = stage.merge_into_graphics_payload(
            {"avx_available": False, "avx2_available": False},
            environ={},
        )
        self.assertIn("shader_avx", merged)
        self.assertEqual(merged["shader_avx"]["track"], "J")
        self.assertEqual(stage.STAGE_ID, "J")
        self.assertIn("x86.graphics.shader_avx_gate", stage.TRACK_CANDIDATES)

    def test_mc_merge_plan_targets_shared_detect(self) -> None:
        stage = _load_stage()
        plan = stage.mc_merge_plan()
        self.assertEqual(plan["integrate_after"], "52f7298")
        self.assertEqual(plan["queue_id"], "next:J-detect-stage")
        paths = {t["path"] for t in plan["shared_targets"]}
        self.assertIn("x86/graphics/detect.py", paths)
        self.assertIn("x86/graphics/skylight_tracks.py", paths)
        self.assertIn("serialize_shader_avx_fields", plan["snippets"]["detect.py"])
        self.assertIn('"J"', plan["snippets"]["skylight_tracks.py"])


class StandaloneScanSmokeTest(unittest.TestCase):
    def test_missing_path(self) -> None:
        r = scan_standalone_file("/nonexistent/shader_avx_test.bin")
        self.assertFalse(r.present)
        self.assertEqual(count_opcode_hits(b"")["vmovaps_store_lo"], 0)


if __name__ == "__main__":
    unittest.main()
