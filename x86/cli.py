"""
cli.py: argparse subcommands — detect, build, patch, status, wizard
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from . import __version__
from .logging import setup_logging
from .manifest import APP_NAME
from .settings import SettingsStore


def _ensure_repo_on_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    repo_str = str(repo_root)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)
    return repo_root


def _sw_vers(key: str) -> Optional[str]:
    flag = key if key.startswith("-") else f"-{key}"
    try:
        result = subprocess.run(
            ["/usr/bin/sw_vers", flag],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _emit_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _serialize_detect_payload(computer: Any) -> dict[str, Any]:
    from opencore_legacy_patcher.datasets import smbios_data

    model = computer.real_model
    marketing = smbios_data.smbios_dictionary.get(model, {}).get("Marketing Name", model)
    cpu_name = getattr(computer.cpu, "name", None) if computer.cpu else None

    gpus = []
    for gpu in computer.gpus or []:
        gpus.append(
            {
                "name": getattr(gpu, "name", "Unknown"),
                "vendor": hex(getattr(gpu, "vendor_id", 0)),
                "device": hex(getattr(gpu, "device_id", 0)),
            }
        )

    return {
        "model": model,
        "marketing_name": marketing,
        "build_model": computer.build_model,
        "real_model": computer.real_model,
        "cpu": cpu_name,
        "gpus": gpus,
        "os_version": _sw_vers("productVersion"),
        "os_build": _sw_vers("buildVersion"),
        "host_is_hackintosh": getattr(computer, "firmware_vendor", None) not in (None, "Apple"),
    }


def cmd_detect(args: argparse.Namespace) -> int:
    _ensure_repo_on_path()
    from opencore_legacy_patcher.detections.device_probe import Computer

    computer = Computer.probe()
    payload = _serialize_detect_payload(computer)

    store = SettingsStore()
    store.record_detect(payload["model"])

    if args.json:
        _emit_json(payload)
    else:
        logging.info("Mac 모델 감지 결과:")
        logging.info("  모델: %s", payload["model"])
        logging.info("  제품명: %s", payload["marketing_name"])
        logging.info("  CPU: %s", payload["cpu"] or "N/A")
        logging.info(
            "  macOS: %s (%s)",
            payload["os_version"] or "N/A",
            payload["os_build"] or "N/A",
        )
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    model = args.model or "(auto-detect)"
    message = (
        f"{APP_NAME} build is not yet implemented in the x86 CLI. "
        f"Requested model: {model}. "
        "Use `python -m x86 wizard` for the guided EFI build flow."
    )
    if args.json:
        _emit_json({"status": "not_implemented", "message": message, "model": model})
    else:
        logging.warning(message)
    return 2


def cmd_patch(args: argparse.Namespace) -> int:
    message = (
        f"{APP_NAME} patch is not yet implemented in the x86 CLI. "
        "Use `python -m x86 wizard` or the legacy `opencore_legacy_patcher` entry for now."
    )
    if args.auto:
        message += " (--auto requested)"
    if args.json:
        _emit_json({"status": "not_implemented", "message": message, "auto": args.auto})
    else:
        logging.warning(message)
    return 2


def cmd_status(args: argparse.Namespace) -> int:
    store = SettingsStore()
    settings = store.load()
    payload = {
        "status": "partial",
        "message": (
            f"{APP_NAME} status summary (settings only; full patch detection pending x86/patch migration)."
        ),
        "settings": settings,
        "config_path": str(store.config_path),
    }
    if args.json:
        _emit_json(payload)
    else:
        logging.info(payload["message"])
        logging.info("  설정 파일: %s", store.config_path)
        last_detect = settings.get("last_detect")
        if last_detect:
            logging.info("  마지막 감지: %s", last_detect)
    return 0


def cmd_wizard(args: argparse.Namespace) -> int:
    _ensure_repo_on_path()

    try:
        from x86.gui.wizard import launch_wizard  # type: ignore[import-not-found]
    except ImportError:
        launch_wizard = None

    if launch_wizard is not None:
        launch_wizard(advanced=args.advanced)
        return 0

    from opencore_legacy_patcher.application_entry import main as oclp_main

    argv = [sys.argv[0]]
    if args.advanced or os.environ.get("X86_ADVANCED") == "1":
        argv.append("--advanced_gui")
    sys.argv = argv
    oclp_main()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="x86",
        description=f"{APP_NAME} — x86 Mac OpenCore EFI build and root patch tooling",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    detect = subparsers.add_parser("detect", help="Mac 모델 및 하드웨어 정보 확인")
    detect.add_argument("--json", action="store_true", help="JSON 형식으로 결과 출력")
    detect.set_defaults(handler=cmd_detect)

    build = subparsers.add_parser("build", help="OpenCore EFI 빌드")
    build.add_argument("--model", help="대상 Mac 모델 (예: iMac18,3)")
    build.add_argument("--json", action="store_true", help="JSON 형식으로 결과 출력")
    build.set_defaults(handler=cmd_build)

    patch = subparsers.add_parser("patch", help="루트 볼륨 패치 적용")
    patch.add_argument("--auto", action="store_true", help="자동 패치 모드")
    patch.add_argument("--json", action="store_true", help="JSON 형식으로 결과 출력")
    patch.set_defaults(handler=cmd_patch)

    status = subparsers.add_parser("status", help="설정·패치·EFI 상태 요약")
    status.add_argument("--json", action="store_true", help="JSON 형식으로 결과 출력")
    status.set_defaults(handler=cmd_status)

    wizard = subparsers.add_parser("wizard", help="기본 GUI 마법사 실행")
    wizard.add_argument(
        "--advanced",
        action="store_true",
        help="고급 GUI (X86_ADVANCED=1 과 동일)",
    )
    wizard.set_defaults(handler=cmd_wizard)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    setup_logging(verbose=os.environ.get("X86_VERBOSE") == "1")
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
