"""
Track K owned CLI — equivalent to ``python -m x86 profile ...`` without touching x86/cli.py.

Usage:
  python -m x86.profiles list
  python -m x86.profiles show macpro5-vega64-tahoe
  python -m x86.profiles apply macpro5-vega64-tahoe [--dry-run] [--config PATH] [--extreme] [--json]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any, Optional


def _emit_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="python -m x86.profiles",
        description="Track K E2E hardware profiles (EFI→root order)",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    p_list = sub.add_parser("list", help="List profiles")
    p_list.add_argument("--json", action="store_true")

    p_show = sub.add_parser("show", help="Show profile steps")
    p_show.add_argument("profile_id")
    p_show.add_argument("--extreme", action="store_true")
    p_show.add_argument("--json", action="store_true")

    p_apply = sub.add_parser("apply", help="Apply profile (EFI mutate / root plan)")
    p_apply.add_argument("profile_id")
    p_apply.add_argument("--config", help="OpenCore config.plist path")
    p_apply.add_argument("--dry-run", action="store_true")
    p_apply.add_argument("--extreme", action="store_true")
    p_apply.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    from x86.profiles import apply, get_profile, list_profiles

    if args.action == "list":
        rows = [
            {"id": p.id, "title": p.title, "model": p.model, "gpu_family": p.gpu_family, "docs": p.docs}
            for p in list_profiles()
        ]
        if args.json:
            _emit_json({"profiles": rows})
        else:
            for row in rows:
                logging.info("%s — %s (%s / %s)", row["id"], row["title"], row["model"], row["gpu_family"])
        return 0

    if args.action == "show":
        try:
            profile = get_profile(args.profile_id)
        except KeyError as error:
            logging.error("%s", error)
            return 2
        extreme = bool(args.extreme) or os.environ.get("X86_EXTREME", "").lower() in {"1", "true", "yes", "on"}
        payload = profile.as_dict(include_extreme=extreme)
        if args.json:
            _emit_json(payload)
        else:
            logging.info("%s — %s", payload["id"], payload["title"])
            for step in payload["steps"]:
                logging.info("[%s] %s — %s", step["phase"], step["id"], step["title"])
        return 0

    if args.action == "apply":
        try:
            get_profile(args.profile_id)
        except KeyError as error:
            logging.error("%s", error)
            return 2
        report = apply(
            args.profile_id,
            config_path=args.config,
            dry_run=bool(args.dry_run),
            include_extreme=bool(args.extreme),
        )
        if args.json:
            _emit_json(report)
        else:
            logging.info("apply %s", report["profile_id"])
            logging.info("order: %s", " → ".join(report.get("order") or []))
            for result in report.get("results") or []:
                logging.info("[%s] %s — %s", result["status"], result["step_id"], result["detail"])
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
