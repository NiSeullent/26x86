"""
Track I — Extreme dylib interpose safety gate.

Dangerous Metal/SkyLight/CoreDisplay interpose paths stay inert unless the
operator explicitly opts in with ``X86_EXTREME=1`` (and, for install scripts,
``X86_EXTREME_INSTALL=1``).
"""

from __future__ import annotations

import os
from typing import Any

ENV_X86_EXTREME = "X86_EXTREME"
ENV_X86_EXTREME_INSTALL = "X86_EXTREME_INSTALL"
ENV_AVX_MODE = "X86_INTERPOSE_AVX"
ENV_LUT_MODE = "X86_INTERPOSE_LUT"

AVX_MODE_PASSTHROUGH = "passthrough"
AVX_MODE_REPORT0 = "report0"
AVX_MODE_REPORT1 = "report1"

LUT_MODE_OFF = "off"
LUT_MODE_LOG = "log"
LUT_MODE_IDENTITY = "identity"


def _truthy(raw: str | None) -> bool:
    if raw is None:
        return False
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def extreme_opt_in() -> bool:
    return _truthy(os.environ.get(ENV_X86_EXTREME))


def extreme_install_opt_in() -> bool:
    return extreme_opt_in() and _truthy(os.environ.get(ENV_X86_EXTREME_INSTALL))


def avx_interpose_mode() -> str:
    raw = (os.environ.get(ENV_AVX_MODE) or AVX_MODE_PASSTHROUGH).strip().lower()
    if raw in {AVX_MODE_PASSTHROUGH, AVX_MODE_REPORT0, AVX_MODE_REPORT1}:
        return raw
    return AVX_MODE_PASSTHROUGH


def lut_interpose_mode() -> str:
    raw = (os.environ.get(ENV_LUT_MODE) or LUT_MODE_OFF).strip().lower()
    if raw in {LUT_MODE_OFF, LUT_MODE_LOG, LUT_MODE_IDENTITY}:
        return raw
    return LUT_MODE_OFF


def gate_blocks_reason(*, require_install: bool = False) -> str | None:
    if not extreme_opt_in():
        return f"{ENV_X86_EXTREME}=1 required for Track I extreme interpose"
    if require_install and not extreme_install_opt_in():
        return (
            f"{ENV_X86_EXTREME}=1 and {ENV_X86_EXTREME_INSTALL}=1 required "
            "to install LaunchDaemons / root-volume wrappers"
        )
    return None


def serialize_interpose_gate_fields() -> dict[str, Any]:
    return {
        "x86_extreme": extreme_opt_in(),
        "x86_extreme_install": extreme_install_opt_in(),
        "interpose_avx_mode": avx_interpose_mode(),
        "interpose_lut_mode": lut_interpose_mode(),
        "extreme_env_keys": [
            ENV_X86_EXTREME,
            ENV_X86_EXTREME_INSTALL,
            ENV_AVX_MODE,
            ENV_LUT_MODE,
        ],
    }


def serialize_track_detect_fields(**_kwargs: Any) -> dict[str, Any]:
    """Optional Track G import hook — does not mutate shared detect modules."""
    from .interpose_plan import serialize_interpose_fields

    return serialize_interpose_fields()
