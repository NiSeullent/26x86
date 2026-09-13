"""
Track L-WS — WindowServer / SkyLight hook opt-in gate (dedicated file only).

Requires ``X86_EXTREME=1`` and explicit hook opt-in. Does not touch shared modules.
"""

from __future__ import annotations

import os
from typing import Any

ENV_EXTREME = "X86_EXTREME"
ENV_HOOK = "X86_EXTREME_WINDOWSERVER_HOOK"
ENV_ACCEPT = "I_ACCEPT_WINDOWSERVER_HOOK_RISK"
ACCEPT_TOKEN = "1"

TRACK_ID = "L-WS"
TRACK_TITLE = "WindowServer / SkyLight process injection & LUT recovery"
TRACK_DOC = "docs/EXTREME-WindowServer-Hook.md"

RISK_SUMMARY_KO = (
    "SIP 우회·WindowServer 주입·Apple EULA/보안 정책 위반 가능. "
    "로그인 루프·WS 크래시·데이터 손실 위험. 기본 배포 경로에서는 비활성."
)


def _truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip() == ACCEPT_TOKEN


def extreme_env_enabled() -> bool:
    return _truthy(ENV_EXTREME)


def windowserver_hook_opt_in() -> bool:
    return _truthy(ENV_HOOK) or _truthy(ENV_ACCEPT)


def extreme_windowserver_hooks_allowed() -> bool:
    return extreme_env_enabled() and windowserver_hook_opt_in()


def require_extreme_windowserver_hooks() -> None:
    if not extreme_windowserver_hooks_allowed():
        raise PermissionError(
            f"Track L-WS blocked: set {ENV_EXTREME}=1 and "
            f"({ENV_HOOK}=1 or {ENV_ACCEPT}=1). {RISK_SUMMARY_KO}"
        )


def serialize_windowserver_hook_gate() -> dict[str, Any]:
    allowed = extreme_windowserver_hooks_allowed()
    return {
        "track": TRACK_ID,
        "track_title": TRACK_TITLE,
        "track_doc": TRACK_DOC,
        "x86_extreme": extreme_env_enabled(),
        "windowserver_hook_opt_in": windowserver_hook_opt_in(),
        "extreme_windowserver_hooks_allowed": allowed,
        "env_extreme": ENV_EXTREME,
        "env_hook": ENV_HOOK,
        "env_accept": ENV_ACCEPT,
        "risk_summary_ko": RISK_SUMMARY_KO,
        "default_path_safe": not allowed,
    }
