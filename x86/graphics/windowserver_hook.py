"""Track L-WS facade — dedicated module; not wired into shared __init__."""

from __future__ import annotations

from typing import Any

from x86.graphics.windowserver_hook_gate import ENV_ACCEPT, ENV_EXTREME, ENV_HOOK, TRACK_DOC, TRACK_ID, TRACK_TITLE
from x86.graphics.windowserver_hook_plan import build_windowserver_hook_plan, run_extreme_windowserver_plan


def serialize_windowserver_hook_fields(*, include_extreme_detail: bool = False) -> dict[str, Any]:
    plan = build_windowserver_hook_plan(include_extreme_detail=include_extreme_detail)
    return {
        "windowserver_hook_track": TRACK_ID,
        "windowserver_hook_title": TRACK_TITLE,
        "windowserver_hook_doc": TRACK_DOC,
        "windowserver_hook_gate": plan["gate"],
        "windowserver_hook_beyond_cache_lock": True,
        "windowserver_hook_stages": [{"id": s["id"], "title": s["title"], "gated": s["gated"], "status": s["status"]} for s in plan["stages"]],
        "windowserver_hook_env": {"extreme": ENV_EXTREME, "hook": ENV_HOOK, "accept": ENV_ACCEPT},
    }


def main() -> int:
    import json
    import sys

    if "--run" in sys.argv:
        try:
            payload = run_extreme_windowserver_plan()
        except PermissionError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    else:
        payload = serialize_windowserver_hook_fields(include_extreme_detail="--detail" in sys.argv)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
