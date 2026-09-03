"""
Mock guest harness — Sequoia host simulates Tahoe + pre-AVX + Vega fixtures.

No UTM/qemu required. Combinations cover MacPro5+Vega, flashed MacPro7,1,
no-AVX, and product 26.x / xnu 25.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from x86.profiles.fixtures import (
    MACPRO51_WESTMERE_FEATURES,
    MACPRO51_WESTMERE_LEAF7,
    VEGA64_DEVICE_ID,
    macpro5_vega64_detect_kwargs,
    matches_macpro5_vega64_profile,
    vega64_gpu,
)


@dataclass(frozen=True)
class MockGuest:
    """One synthetic guest identity for gate/detect tests."""

    guest_id: str
    reported_model: str
    real_model: str
    product_version: str
    xnu_major: int
    cpu_brand: str
    smc_version: str
    gpu_device_id: int = VEGA64_DEVICE_ID
    gpu_archs: tuple[str, ...] = ("Vega", "RX Vega 64")
    avx_available: bool = False
    pre_avx_mac_pro: bool = True
    notes: tuple[str, ...] = ()

    def detect_kwargs(self) -> dict[str, Any]:
        base = macpro5_vega64_detect_kwargs()
        base.update(
            {
                "model": self.real_model,
                "xnu_major": self.xnu_major,
                "cpu_features": list(MACPRO51_WESTMERE_FEATURES),
                "cpu_leaf7_features": list(MACPRO51_WESTMERE_LEAF7),
                "gpus": [vega64_gpu()],
            }
        )
        return base

    def flash_kwargs(self) -> dict[str, Any]:
        return {
            "reported_model": self.reported_model,
            "real_model": self.real_model,
            "cpu_brand": self.cpu_brand,
            "smc_version": self.smc_version,
        }


GUESTS: tuple[MockGuest, ...] = (
    MockGuest(
        guest_id="macpro5-vega-tahoe26",
        reported_model="MacPro5,1",
        real_model="MacPro5,1",
        product_version="26.0",
        xnu_major=25,
        cpu_brand="Intel(R) Xeon(R) CPU X5675 @ 3.07GHz",
        smc_version="1.39f11",
        notes=("native SMBIOS MacPro5,1 + Vega 64 + Tahoe",),
    ),
    MockGuest(
        guest_id="flash-macpro71-westmere-vega",
        reported_model="MacPro7,1",
        real_model="MacPro5,1",
        product_version="26.1",
        xnu_major=25,
        cpu_brand="Intel(R) Xeon(R) CPU X5675 @ 3.07GHz",
        smc_version="1.39f11",
        notes=("flashed cMP under MacPro7,1 SMBIOS",),
    ),
    MockGuest(
        guest_id="macpro5-vega-tahoe26-0-1",
        reported_model="MacPro5,1",
        real_model="MacPro5,1",
        product_version="26.0.1",
        xnu_major=25,
        cpu_brand="Intel(R) Xeon(R) CPU E5620 @ 2.40GHz",
        smc_version="1.39f11",
        notes=("product 26.0.1 string parse",),
    ),
    MockGuest(
        guest_id="macpro5-noavx-sequoia-control",
        reported_model="MacPro5,1",
        real_model="MacPro5,1",
        product_version="15.5",
        xnu_major=24,
        cpu_brand="Intel(R) Xeon(R) CPU X5675 @ 3.07GHz",
        smc_version="1.39f11",
        notes=("Sequoia control — root patches must stay empty",),
    ),
)


@dataclass
class GuestEval:
    guest_id: str
    is_tahoe: bool
    root_allowed: bool
    flashed: bool
    profile_match: bool
    yellow_risk: bool
    ok: bool
    detail: dict[str, Any] = field(default_factory=dict)


def evaluate_guest(guest: MockGuest) -> GuestEval:
    from x86.graphics.tahoe_gate import (
        detect_flashed_mac_pro,
        is_tahoe,
        root_patches_allowed,
    )
    from x86.graphics.yellow_screen import yellow_screen_risk

    tahoe = is_tahoe(xnu_major=guest.xnu_major, product_version=guest.product_version)
    allowed = root_patches_allowed(
        xnu_major=guest.xnu_major, product_version=guest.product_version
    )
    flash = detect_flashed_mac_pro(**guest.flash_kwargs())
    match = matches_macpro5_vega64_profile(
        model=guest.real_model,
        gpu_family="vega",
        avx_available=guest.avx_available,
        pre_avx_mac_pro=guest.pre_avx_mac_pro,
    )
    risk = yellow_screen_risk(
        guest.real_model,
        gpu_archs=list(guest.gpu_archs),
        xnu_major=guest.xnu_major,
        os_version=guest.product_version,
        agdpmod_present=False,
    )
    # Expectations
    expect_tahoe = guest.xnu_major >= 25 or guest.product_version.startswith("26")
    expect_flash = guest.reported_model != guest.real_model or (
        guest.reported_model.startswith("MacPro7,1")
    )
    ok = (
        tahoe == expect_tahoe
        and allowed == expect_tahoe
        and match is True
        and guest.avx_available is False
        and (risk is True if expect_tahoe else risk is False)
    )
    if expect_flash and not flash["flashed_mac_pro"] and guest.guest_id.startswith("flash"):
        ok = False

    return GuestEval(
        guest_id=guest.guest_id,
        is_tahoe=tahoe,
        root_allowed=allowed,
        flashed=bool(flash.get("flashed_mac_pro")),
        profile_match=match,
        yellow_risk=risk,
        ok=ok,
        detail={
            "product_version": guest.product_version,
            "xnu_major": guest.xnu_major,
            "flash": flash,
            "guest": asdict(guest),
        },
    )


def run_mock_guest_matrix() -> dict[str, Any]:
    results = [evaluate_guest(g) for g in GUESTS]
    return {
        "guests": len(results),
        "ok": all(r.ok for r in results),
        "results": [
            {
                "guest_id": r.guest_id,
                "ok": r.ok,
                "is_tahoe": r.is_tahoe,
                "root_allowed": r.root_allowed,
                "flashed": r.flashed,
                "profile_match": r.profile_match,
                "yellow_risk": r.yellow_risk,
            }
            for r in results
        ],
    }


def main(argv: Optional[list[str]] = None) -> int:
    import json
    import sys

    del argv
    payload = run_mock_guest_matrix()
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
