"""Unit tests for Safari 26 Pre-AVX Mac Pro matching (no real hardware)."""

from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.patch.safari26_preavx import (  # noqa: E402
    ELIGIBLE_MODELS,
    VERIFIED_MODEL,
    cpu_reports_avx,
    evaluate,
    evaluate_for_efi_build,
    is_eligible_mac_pro,
    merge_jsc_tokens,
)


class Safari26PreAvxDetectionTests(unittest.TestCase):
    def test_eligible_models_match_upstream_mac_pro_class(self) -> None:
        self.assertIn(VERIFIED_MODEL, ELIGIBLE_MODELS)
        self.assertTrue(is_eligible_mac_pro("MacPro5,1"))
        self.assertFalse(is_eligible_mac_pro("MacPro4,1"))
        self.assertFalse(is_eligible_mac_pro("MacPro3,1"))
        self.assertFalse(is_eligible_mac_pro("MacPro6,1"))
        self.assertFalse(is_eligible_mac_pro("MacPro7,1"))
        self.assertFalse(is_eligible_mac_pro("iMac18,3"))
        self.assertFalse(is_eligible_mac_pro("MacBookPro15,1"))
        self.assertFalse(is_eligible_mac_pro(""))
        self.assertFalse(is_eligible_mac_pro(None))

    def test_cpu_avx_tokens_match_installer(self) -> None:
        self.assertFalse(cpu_reports_avx(["FPU", "SSE", "SSE2", "SSE4.2"]))
        self.assertFalse(cpu_reports_avx([]))
        self.assertFalse(cpu_reports_avx(None))
        self.assertTrue(cpu_reports_avx(["FPU", "SSE", "AVX1.0", "AES"]))
        self.assertTrue(cpu_reports_avx(["avx"]))
        self.assertTrue(cpu_reports_avx(["AVX2"]))
        self.assertFalse(cpu_reports_avx(["PAE"]))  # substring must not match

    def test_merge_jsc_replaces_none(self) -> None:
        self.assertEqual(merge_jsc_tokens([]), ["jsc"])
        self.assertEqual(merge_jsc_tokens(["sbvmm"]), ["sbvmm", "jsc"])
        self.assertEqual(merge_jsc_tokens(["sbvmm", "jsc"]), ["sbvmm", "jsc"])
        self.assertEqual(merge_jsc_tokens(["none"]), ["jsc"])

    def test_macpro51_auto_on_when_payload_and_no_avx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dummy_zip(Path(tmp))
            decision = evaluate(
                "MacPro5,1",
                cpu_flags=["FPU", "SSE", "SSE4.2"],
                settings={"safari26_preavx_fix": True},
                host_is_macos=True,
                repo_root=Path(tmp),
            )
            self.assertTrue(decision.should_apply)
            self.assertEqual(decision.reason, "auto_apply_preavx_mac_pro")

    def test_user_can_disable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dummy_zip(Path(tmp))
            decision = evaluate(
                "MacPro5,1",
                cpu_flags=["SSE"],
                settings={"safari26_preavx_fix": False},
                host_is_macos=True,
                repo_root=Path(tmp),
            )
            self.assertFalse(decision.should_apply)
            self.assertEqual(decision.reason, "disabled_by_user")

    def test_avx_cpu_on_macpro51_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dummy_zip(Path(tmp))
            decision = evaluate(
                "MacPro5,1",
                cpu_flags=["SSE", "AVX"],
                settings={},
                host_is_macos=True,
                repo_root=Path(tmp),
            )
            self.assertFalse(decision.should_apply)
            self.assertEqual(decision.reason, "cpu_reports_avx")

    def test_other_mac_pros_never_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dummy_zip(Path(tmp))
            for model in ("MacPro3,1", "MacPro4,1", "MacPro6,1", "MacPro7,1"):
                decision = evaluate(
                    model,
                    cpu_flags=["SSE"],
                    settings={},
                    host_is_macos=True,
                    repo_root=Path(tmp),
                )
                self.assertFalse(decision.should_apply, model)
                self.assertEqual(decision.reason, "model_not_preavx_mac_pro")

    def test_windows_and_linux_never_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dummy_zip(Path(tmp))
            decision = evaluate(
                "MacPro5,1",
                cpu_flags=["SSE"],
                settings={},
                host_is_macos=False,
                repo_root=Path(tmp),
            )
            self.assertFalse(decision.should_apply)
            self.assertEqual(decision.reason, "macos_only")
            self.assertTrue(decision.notes)

    def test_custom_model_build_ignores_host_avx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dummy_zip(Path(tmp))
            host = SimpleNamespace(
                real_model="iMac18,3",
                cpu=SimpleNamespace(flags=["AVX", "SSE"], leafs=[]),
            )
            decision = evaluate_for_efi_build(
                "MacPro5,1",
                computer=host,
                custom_model="MacPro5,1",
                settings={"safari26_preavx_fix": True},
                repo_root=Path(tmp),
            )
            self.assertTrue(decision.should_apply)

    def test_payload_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decision = evaluate(
                "MacPro5,1",
                cpu_flags=["SSE"],
                settings={},
                host_is_macos=True,
                repo_root=Path(tmp),
            )
            self.assertFalse(decision.should_apply)
            self.assertEqual(decision.reason, "payload_missing")

    def test_vendored_payload_exists_in_repo(self) -> None:
        zip_path = (
            REPO
            / "payloads"
            / "Kexts"
            / "Community"
            / "Safari26-PreAVX-Fix"
            / "RestrictEvents-v1.1.8-RELEASE.zip"
        )
        self.assertTrue(zip_path.is_file(), f"missing vendored kext: {zip_path}")
        with zipfile.ZipFile(zip_path) as archive:
            names = archive.namelist()
        self.assertTrue(any(name.endswith("Contents/MacOS/RestrictEvents") for name in names))

    @staticmethod
    def _write_dummy_zip(repo_root: Path) -> None:
        dest = (
            repo_root
            / "payloads"
            / "Kexts"
            / "Community"
            / "Safari26-PreAVX-Fix"
            / "RestrictEvents-v1.1.8-RELEASE.zip"
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"PK\x03\x04dummy")


if __name__ == "__main__":
    unittest.main()
