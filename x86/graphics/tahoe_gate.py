"""
Single Tahoe (macOS 26) host gate for root-patch / extreme unlocks.

Root patches (3802 / Non-Metal / yellow mitigations / H / I / L5, etc.) may
emit live payloads only when the **target host OS** is Tahoe:

  * XNU major ≥ 25 (``os_data.tahoe``), or
  * Product version 26.x

Sequoia 15.x (XNU 24) with ``X86_EXTREME=1`` stays research/staging only —
filters and hooks return ``{}`` / no-op.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Mapping, Optional

# Matches opencore_legacy_patcher.datasets.os_data.tahoe / yellow_screen.
TAHOE_XNU_MAJOR = 25
TAHOE_PRODUCT_MAJOR = 26
SEQUOIA_XNU_MAJOR = 24
SEQUOIA_PRODUCT_MAJOR = 15

ENV_EXTREME = "X86_EXTREME"
ENV_TAHOE_3802 = "X86_TAHOE_3802"
ENV_TAHOE_NONMETAL = "X86_TAHOE_NONMETAL"

_TRUTHY = frozenset({"1", "true", "yes", "on"})

# Classic Mac Pro 4,1/5,1 SMC family (flashed SMBIOS often reports MacPro7,1).
_CLASSIC_MACPRO_SMC_PREFIXES: tuple[str, ...] = (
    "1.39f",  # MacPro5,1
    "1.74f",  # MacPro4,1
    "1.70f",
)


@dataclass(frozen=True)
class HostOsInfo:
    """Resolved host OS identity for gating."""

    product_version: str
    macos_major: Optional[int]
    xnu_major: Optional[int]
    build_version: str = ""
    is_tahoe: bool = False


def _env_truthy(name: str, environ: Optional[Mapping[str, str]] = None) -> bool:
    env = environ if environ is not None else os.environ
    raw = env.get(name, "")
    return str(raw).strip().lower() in _TRUTHY


def macos_major_from_version(product_version: Optional[str]) -> Optional[int]:
    """Parse major from ``sw_vers`` product version (e.g. ``15.5`` → 15, ``26.0`` → 26)."""
    if not product_version:
        return None
    text = str(product_version).strip()
    match = re.match(r"^(\d+)", text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def is_tahoe(
    *,
    xnu_major: Optional[int] = None,
    product_version: Optional[str] = None,
    os_version: Optional[str] = None,
    assume_tahoe: bool = False,
) -> bool:
    """
    True when the OS target is macOS 26 Tahoe.

    Accepts XNU major ≥ 25 and/or product version 26.x. ``os_version`` is an
    alias for ``product_version`` (yellow_screen / detect call sites).
    """
    if assume_tahoe:
        return True
    if xnu_major is not None and int(xnu_major) >= TAHOE_XNU_MAJOR:
        return True
    version = product_version if product_version is not None else os_version
    major = macos_major_from_version(version)
    if major is not None and major >= TAHOE_PRODUCT_MAJOR:
        return True
    if version:
        text = str(version).strip()
        if text.startswith("26.") or text == "26":
            return True
    return False


def root_patches_allowed(
    *,
    xnu_major: Optional[int] = None,
    product_version: Optional[str] = None,
    os_version: Optional[str] = None,
    assume_tahoe: bool = False,
) -> bool:
    """Root-volume patch emission is allowed only on Tahoe hosts."""
    return is_tahoe(
        xnu_major=xnu_major,
        product_version=product_version,
        os_version=os_version,
        assume_tahoe=assume_tahoe,
    )


def probe_host_os(
    *,
    xnu_major: Optional[int] = None,
    product_version: Optional[str] = None,
    build_version: Optional[str] = None,
) -> HostOsInfo:
    """
    Resolve host OS info. Prefers explicit args; otherwise probes macOS via
    ``sw_vers`` / Darwin release (``24.5.0`` → XNU major 24).
    """
    version = (product_version or "").strip()
    build = (build_version or "").strip()
    major_xnu = xnu_major

    if sys.platform == "darwin":
        if not version:
            try:
                result = subprocess.run(
                    ["/usr/bin/sw_vers", "-productVersion"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
            except OSError:
                pass
        if not build:
            try:
                result = subprocess.run(
                    ["/usr/bin/sw_vers", "-buildVersion"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    build = result.stdout.strip()
            except OSError:
                pass
        if major_xnu is None:
            # Darwin kernel version major == XNU major (e.g. 24.5.0 → 24).
            release = os.uname().release if hasattr(os, "uname") else ""
            match = re.match(r"^(\d+)", release or "")
            if match:
                try:
                    major_xnu = int(match.group(1))
                except ValueError:
                    major_xnu = None

    macos_major = macos_major_from_version(version)
    tahoe = is_tahoe(xnu_major=major_xnu, product_version=version)
    return HostOsInfo(
        product_version=version,
        macos_major=macos_major,
        xnu_major=major_xnu,
        build_version=build,
        is_tahoe=tahoe,
    )


def extreme_env_opt_in(environ: Optional[Mapping[str, str]] = None) -> bool:
    return _env_truthy(ENV_EXTREME, environ)


def metal3802_env_opt_in(environ: Optional[Mapping[str, str]] = None) -> bool:
    return _env_truthy(ENV_TAHOE_3802, environ) or extreme_env_opt_in(environ)


def nonmetal_env_opt_in(environ: Optional[Mapping[str, str]] = None) -> bool:
    return _env_truthy(ENV_TAHOE_NONMETAL, environ) or extreme_env_opt_in(environ)


def metal3802_root_unlocked(
    *,
    xnu_major: Optional[int] = None,
    product_version: Optional[str] = None,
    os_version: Optional[str] = None,
    environ: Optional[Mapping[str, str]] = None,
    assume_tahoe: bool = False,
) -> bool:
    """Env opt-in is effective only on Tahoe."""
    return root_patches_allowed(
        xnu_major=xnu_major,
        product_version=product_version,
        os_version=os_version,
        assume_tahoe=assume_tahoe,
    ) and metal3802_env_opt_in(environ)


def nonmetal_root_unlocked(
    *,
    xnu_major: Optional[int] = None,
    product_version: Optional[str] = None,
    os_version: Optional[str] = None,
    environ: Optional[Mapping[str, str]] = None,
    assume_tahoe: bool = False,
) -> bool:
    return root_patches_allowed(
        xnu_major=xnu_major,
        product_version=product_version,
        os_version=os_version,
        assume_tahoe=assume_tahoe,
    ) and nonmetal_env_opt_in(environ)


def serialize_root_patch_gates(
    *,
    xnu_major: Optional[int] = None,
    product_version: Optional[str] = None,
    os_version: Optional[str] = None,
    environ: Optional[Mapping[str, str]] = None,
    assume_tahoe: bool = False,
) -> dict[str, Any]:
    """Fields for ``detect --json`` → ``root_patch_gates`` (+ top-level mirrors)."""
    version = product_version if product_version is not None else os_version
    tahoe = is_tahoe(
        xnu_major=xnu_major,
        product_version=version,
        assume_tahoe=assume_tahoe,
    )
    macos_major = macos_major_from_version(version)
    extreme = extreme_env_opt_in(environ)
    m3802_env = metal3802_env_opt_in(environ)
    nm_env = nonmetal_env_opt_in(environ)
    allowed = tahoe
    reason: str
    if tahoe:
        reason = "host is Tahoe (macOS 26 / XNU ≥ 25); root patches may emit under opt-in"
    else:
        reason = (
            "host is not Tahoe; X86_EXTREME / Tahoe opt-in flags do not inject "
            "root patches on Sequoia or other non-26 hosts"
        )
    return {
        "macos_major": macos_major,
        "xnu_major": xnu_major,
        "is_tahoe": tahoe,
        "root_patches_allowed": allowed,
        "extreme_env": extreme,
        "metal3802_env_opt_in": m3802_env,
        "nonmetal_env_opt_in": nm_env,
        "metal3802_root_unlocked": allowed and m3802_env,
        "nonmetal_root_unlocked": allowed and nm_env,
        "reason": reason,
    }


# --- Flashed Mac Pro (MacPro5,1-class under MacPro7,1 SMBIOS) -----------------


def _sysctl_str(key: str) -> str:
    if sys.platform != "darwin":
        return ""
    try:
        result = subprocess.run(
            ["/usr/sbin/sysctl", "-n", key],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except OSError:
        return ""


def read_smc_system_version() -> str:
    """Best-effort SMC Version (system) from system_profiler."""
    if sys.platform != "darwin":
        return ""
    try:
        result = subprocess.run(
            ["/usr/sbin/system_profiler", "SPHardwareDataType"],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        if result.returncode != 0:
            return ""
        for line in result.stdout.splitlines():
            if "SMC Version (system)" in line or "SMC 버전(시스템)" in line:
                return line.split(":", 1)[-1].strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return ""


def detect_flashed_mac_pro(
    *,
    real_model: Optional[str] = None,
    reported_model: Optional[str] = None,
    cpu_brand: Optional[str] = None,
    smc_version: Optional[str] = None,
    probe_host: bool = False,
) -> dict[str, Any]:
    """
    MacPro5,1-class hardware under a newer reported SMBIOS (e.g. MacPro7,1).

    Signals: reported ≠ real, classic SMC (1.39f…), Westmere/Xeon X56xx, DDR3 era.
    """
    reported = (reported_model or "").strip()
    real = (real_model or "").strip()
    smc = (smc_version or "").strip()
    brand = (cpu_brand or "").strip()

    if probe_host:
        if not reported:
            reported = _sysctl_str("hw.model")
        if not smc:
            smc = read_smc_system_version()
        if not brand:
            brand = _sysctl_str("machdep.cpu.brand_string")

    classic_smc = any(smc.startswith(p) for p in _CLASSIC_MACPRO_SMC_PREFIXES if smc)
    westmere = bool(
        re.search(r"X56\d{2}|W36\d{2}|E56\d{2}|Westmere", brand, re.I)
    )
    model_mismatch = bool(reported and real and reported != real)
    flashed = bool(
        (real.startswith("MacPro5,1") or real.startswith("MacPro4,1"))
        and (
            model_mismatch
            or classic_smc
            or (reported.startswith("MacPro7,1") and (westmere or classic_smc))
        )
    )
    if not flashed and reported.startswith("MacPro7,1") and (westmere or classic_smc):
        # Native boot with firmware spoof but oem-product absent → still flash-class.
        flashed = True
        if not real:
            real = "MacPro5,1"

    return {
        "reported_model": reported or None,
        "real_model_hint": real or None,
        "smc_version": smc or None,
        "classic_macpro_smc": classic_smc,
        "westmere_class_cpu": westmere,
        "flashed_mac_pro": flashed,
        "flash_notes": (
            [
                "Reported SMBIOS (e.g. MacPro7,1) with MacPro5,1-class SMC/CPU — "
                "treat as flashed cMP for Pre-AVX / Vega policy."
            ]
            if flashed
            else []
        ),
    }
