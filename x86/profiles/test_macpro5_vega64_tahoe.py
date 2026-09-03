"""Unit tests for Track K MacPro5,1 + Vega 64 Tahoe E2E profile."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.profiles import (  # noqa: E402
    MACPRO5_VEGA64_TAHOE_ID,
    apply,
    get_profile,
    list_profiles,
    serialize_profile_match_fields,
)
from x86.profiles.fixtures import (  # noqa: E402
    macpro5_vega64_detect_kwargs,
    macpro5_vega64_fixture_payload,
    matches_macpro5_vega64_profile,
)
from x86.profiles.macpro5_vega64_tahoe import PROFILE, apply_profile  # noqa: E402
from x86.pre_avx.detect import build_detect_fields, serialize_detect_fields  # noqa: E402


class ProfileRegistryTest(unittest.TestCase):
    def test_registered(self) -> None:
        self.assertIn(MACPRO5_VEGA64_TAHOE_ID, [p.id for p in list_profiles()])
        self.assertEqual(get_profile("macpro5-vega64-tahoe").model, "MacPro5,1")

    def test_fixed_order(self) -> None:
        ids = [s.id for s in PROFILE.ordered_steps(include_extreme=True)]
        self.assertEqual(
            ids,
            [
                "efi.agdpmod_shikigva",
                "efi.kdkless",
                "efi.restrictevents_jsc",
                "root.amd_vega",
                "root.yellow_mitigations",
                "extreme.hooks",
            ],
        )


class DetectFixtureTest(unittest.TestCase):
    def test_fixture_payload(self) -> None:
        payload = macpro5_vega64_fixture_payload()
        self.assertEqual(payload["model"], "MacPro5,1")
        self.assertEqual(payload["gpu_family"], "vega")
        self.assertTrue(payload["pre_avx_mac_pro"])
        self.assertFalse(payload["avx_available"])
        self.assertIn("agdpmod", payload["recommended_efi_graphics_fixes"])
        self.assertTrue(payload["profile_match"])

    def test_detect_kwargs(self) -> None:
        serialized = serialize_detect_fields(build_detect_fields(**macpro5_vega64_detect_kwargs()))
        self.assertEqual(serialized["gpu_family"], "vega")

    def test_match_helper(self) -> None:
        self.assertTrue(
            matches_macpro5_vega64_profile(
                model="MacPro5,1", gpu_family="vega", avx_available=False, pre_avx_mac_pro=True
            )
        )
        self.assertFalse(matches_macpro5_vega64_profile(model="MacPro5,1", gpu_family="vega", avx_available=True))

    def test_serialize_match(self) -> None:
        hit = serialize_profile_match_fields(
            model="MacPro5,1", gpu_family="vega", avx_available=False, pre_avx_mac_pro=True
        )
        self.assertEqual(hit["recommended_profile"], MACPRO5_VEGA64_TAHOE_ID)


class ApplyOrderTest(unittest.TestCase):
    def test_dry_run_order(self) -> None:
        report = apply_profile(dry_run=True, include_extreme=True)
        self.assertEqual(
            report["order"],
            [
                "efi.agdpmod_shikigva",
                "efi.kdkless",
                "efi.restrictevents_jsc",
                "root.amd_vega",
                "root.yellow_mitigations",
                "extreme.hooks",
            ],
        )

    def test_apply_mutates_config(self) -> None:
        config: dict = {}
        report = apply_profile(config=config, dry_run=False, include_extreme=False)
        self.assertTrue(report["config_mutated"])
        boot = config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]
        self.assertIn("agdpmod=", boot)
        self.assertIn("shikigva=", boot)
        kexts = {e["BundlePath"] for e in config["Kernel"]["Add"]}
        self.assertIn("KDKlessWorkaround.kext", kexts)
        self.assertIn("RestrictEvents.kext", kexts)
        rev = config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["revpatch"]
        self.assertIn("jsc", rev.split(","))

    def test_plist_roundtrip(self) -> None:
        import plistlib

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.plist"
            with path.open("wb") as handle:
                plistlib.dump({}, handle)
            report = apply(MACPRO5_VEGA64_TAHOE_ID, config_path=path, dry_run=False)
            self.assertEqual(report["profile_id"], MACPRO5_VEGA64_TAHOE_ID)
            with path.open("rb") as handle:
                saved = plistlib.load(handle)
            self.assertIn("agdpmod=", saved["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"])

    def test_extreme_env(self) -> None:
        self.assertNotIn("extreme.hooks", apply_profile(dry_run=True, environ={})["order"])
        report = apply_profile(dry_run=True, environ={"X86_EXTREME": "1"})
        self.assertIn("extreme.hooks", report["order"])
        extreme = next(r for r in report["results"] if r["step_id"] == "extreme.hooks")
        self.assertEqual(extreme["status"], "planned")
        self.assertTrue(extreme["mutations"].get("interpose_apply"))

    def test_extreme_flag_calls_bridge_dry_run(self) -> None:
        report = apply_profile(dry_run=True, include_extreme=True, environ={})
        extreme = next(r for r in report["results"] if r["step_id"] == "extreme.hooks")
        self.assertIn("interpose_apply", extreme["detail"])
        self.assertEqual(extreme["mutations"].get("integrate"), "52f7298+98e2528")


class InterposeLinkTest(unittest.TestCase):
    def test_skipped_when_disabled(self) -> None:
        from x86.profiles.macpro5_vega64_tahoe import run_interpose_apply

        result = run_interpose_apply(enabled=False)
        self.assertEqual(result.status, "skipped")
        self.assertFalse(result.mutations.get("interpose_apply"))

    def test_dry_run_plans_apply(self) -> None:
        from x86.profiles.macpro5_vega64_tahoe import run_interpose_apply

        result = run_interpose_apply(enabled=True, dry_run=True, environ={"X86_EXTREME": "1"})
        self.assertEqual(result.status, "planned")
        self.assertTrue(result.mutations.get("interpose_apply"))


if __name__ == "__main__":
    unittest.main()
