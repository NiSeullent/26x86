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
from .platform import (
    MACOS_ONLY_MESSAGE,
    is_macos,
    non_mac_detect_payload,
    platform_label,
)
from .settings import SettingsStore


def _ensure_repo_on_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    repo_str = str(repo_root)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)
    return repo_root


def _sw_vers(key: str) -> Optional[str]:
    if not is_macos():
        return None
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


def _serialize_detect_payload(computer: Any, model_override: Optional[str] = None) -> dict[str, Any]:
    from opencore_legacy_patcher.datasets import smbios_data
    from x86.pre_avx.detect import build_detect_fields, serialize_detect_fields
    from x86.settings import SettingsStore, read_auto_pre_avx_patch

    if not is_macos():
        payload = non_mac_detect_payload()
        model = model_override or payload.get("model") or "unknown"
        payload["model"] = model
        payload["real_model"] = model
        payload["build_model"] = model
        auto_pre_avx_patch = read_auto_pre_avx_patch(SettingsStore().load())
        fields = build_detect_fields(model, auto_pre_avx_patch=auto_pre_avx_patch, xnu_major=25)
        payload.update(serialize_detect_fields(fields))
        return payload

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

    xnu_major = None
    try:
        from opencore_legacy_patcher.detections import os_probe

        xnu_major = os_probe.OSProbe().detect_kernel_major()
    except Exception:
        pass

    auto_pre_avx_patch = read_auto_pre_avx_patch(SettingsStore().load())
    cpu_features = None
    cpu_leaf7_features = None
    if getattr(computer, "cpu", None) is not None:
        cpu_features = getattr(computer.cpu, "flags", None)
        cpu_leaf7_features = getattr(computer.cpu, "leafs", None)

    fields = build_detect_fields(
        model,
        gpus=getattr(computer, "gpus", None),
        cpu_features=cpu_features,
        cpu_leaf7_features=cpu_leaf7_features,
        auto_pre_avx_patch=auto_pre_avx_patch,
        xnu_major=xnu_major,
    )

    payload = {
        "platform": "macOS",
        "host_is_mac": True,
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
    payload.update(serialize_detect_fields(fields))
    return payload


def cmd_detect(args: argparse.Namespace) -> int:
    _ensure_repo_on_path()

    if is_macos():
        from opencore_legacy_patcher.detections.device_probe import Computer

        computer = Computer.probe()
        payload = _serialize_detect_payload(computer)
    else:
        payload = _serialize_detect_payload(None, model_override=args.model)

    store = SettingsStore()
    detect_extra = {
        key: payload[key]
        for key in (
            "pre_avx_mac_pro",
            "recommended_metal_patch",
            "recommended_tahoe_graphics_policy",
            "avx_available",
            "avx2_available",
            "has_avx2",
            "tahoe_blocked_patches",
            "safari_pre_avx_fix_recommended",
            "auto_pre_avx_patch",
        )
        if key in payload
    }
    store.record_detect(str(payload["model"]), extra=detect_extra)

    if args.json:
        _emit_json(payload)
    else:
        if is_macos():
            logging.info("Mac 모델 감지 결과:")
            logging.info("  모델: %s", payload["model"])
            logging.info("  제품명: %s", payload["marketing_name"])
            logging.info("  CPU: %s", payload["cpu"] or "N/A")
            if payload.get("pre_avx_mac_pro"):
                logging.info("  Pre-AVX Mac Pro: 예 (Metal 힌트: %s)", payload.get("recommended_metal_patch"))
                logging.info("  AVX 사용 가능: %s", "예" if payload.get("avx_available") else "아니오")
                logging.info("  AVX2 사용 가능: %s", "예" if payload.get("avx2_available") else "아니오")
                if payload.get("recommended_tahoe_graphics_policy"):
                    logging.info("  Tahoe 그래픽 정책: %s", payload["recommended_tahoe_graphics_policy"])
                blocked = payload.get("tahoe_blocked_patches") or []
                if blocked:
                    logging.info("  Tahoe 차단 패치: %s", ", ".join(blocked[:4]) + ("…" if len(blocked) > 4 else ""))
        else:
            logging.info("%s 호스트 정보:", platform_label())
            logging.info("  플랫폼: %s", payload.get("platform"))
            logging.info("  Mac 하드웨어 감지: 불가")
            logging.info("  CPU: %s", payload.get("cpu") or "N/A")
            logging.info("  안내: %s", MACOS_ONLY_MESSAGE)
            safari = payload.get("safari26_preavx") or {}
            if safari.get("eligible_model"):
                logging.info(
                    "  Safari 26 Pre-AVX Fix: 이 호스트에서는 적용하지 않습니다. "
                    "MacPro5,1에서 EFI 빌드 시 자동 적용됩니다."
                )
        safari = payload.get("safari26_preavx") or {}
        if safari:
            logging.info(
                "  Safari 26 Pre-AVX Fix: %s (%s)",
                "적용 예정" if safari.get("should_apply") else "건너뜀",
                safari.get("reason"),
            )
        logging.info(
            "  OS: %s (%s)",
            payload["os_version"] or "N/A",
            payload["os_build"] or "N/A",
        )
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    if not is_macos():
        message = MACOS_ONLY_MESSAGE
        if args.json:
            _emit_json({"status": "unsupported_platform", "message": message, "platform": platform_label()})
        else:
            logging.error(message)
        return 2

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
    if not is_macos():
        message = MACOS_ONLY_MESSAGE
        if args.json:
            _emit_json({"status": "unsupported_platform", "message": message, "platform": platform_label(), "auto": args.auto})
        else:
            logging.error(message)
        return 2

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


def _patch_status_payload() -> dict[str, Any]:
    if not is_macos():
        return {
            "platform": platform_label(),
            "host_is_mac": False,
            "error": MACOS_ONLY_MESSAGE,
            "can_patch": False,
            "can_unpatch": False,
            "patches_available": [],
        }

    from opencore_legacy_patcher import constants as constants_module
    from opencore_legacy_patcher.detections import device_probe, os_probe
    from opencore_legacy_patcher.sys_patch.patchsets import (
        HardwarePatchsetDetection,
        HardwarePatchsetValidation,
    )
    from x86.pre_avx.detect import build_detect_fields, serialize_detect_fields
    from x86.settings import SettingsStore

    global_constants = constants_module.Constants()
    os_data = os_probe.OSProbe()
    global_constants.detected_os = os_data.detect_kernel_major()
    global_constants.detected_os_build = os_data.detect_os_build()
    global_constants.detected_os_version = os_data.detect_os_version()
    global_constants.computer = device_probe.Computer.probe()

    patchset = HardwarePatchsetDetection(
        constants=global_constants,
        validation=True,
    )
    patches = patchset.device_properties

    active = [
        patch_name.split(": ", 1)[1]
        for patch_name in patches
        if patches[patch_name] is True
        and not patch_name.startswith("Validation")
        and not patch_name.startswith("Settings")
        and not patch_name.startswith("Graphics Policy")
    ]
    validations = {
        key.split("Validation: ", 1)[1]: value
        for key, value in patches.items()
        if key.startswith("Validation:")
    }

    model = global_constants.custom_model or global_constants.computer.real_model
    auto_pre_avx_patch = SettingsStore().read("auto_pre_avx_patch", True)
    cpu_features = None
    cpu_leaf7_features = None
    if getattr(global_constants.computer, "cpu", None) is not None:
        cpu_features = getattr(global_constants.computer.cpu, "flags", None)
        cpu_leaf7_features = getattr(global_constants.computer.cpu, "leafs", None)

    detect_fields = serialize_detect_fields(
        build_detect_fields(
            model,
            gpus=getattr(global_constants.computer, "gpus", None),
            cpu_features=cpu_features,
            cpu_leaf7_features=cpu_leaf7_features,
            auto_pre_avx_patch=bool(auto_pre_avx_patch),
            xnu_major=global_constants.detected_os,
        )
    )

    return {
        "model": model,
        "os_version": global_constants.detected_os_version,
        "os_build": global_constants.detected_os_build,
        "last_patched_version": global_constants.computer.oclp_sys_version,
        "last_patched_date": global_constants.computer.oclp_sys_date,
        "patches_available": active,
        "can_patch": not patches.get(HardwarePatchsetValidation.PATCHING_NOT_POSSIBLE, False),
        "can_unpatch": not patches.get(HardwarePatchsetValidation.UNPATCHING_NOT_POSSIBLE, False),
        "validations": validations,
        "graphics_policy_warnings": patchset.graphics_policy_warnings,
        **detect_fields,
    }


def cmd_status(args: argparse.Namespace) -> int:
    store = SettingsStore()
    settings = store.load()
    payload: dict[str, Any] = {
        "platform": platform_label(),
        "host_is_mac": is_macos(),
        "settings": settings,
        "config_path": str(store.config_path),
    }

    try:
        payload["patch"] = _patch_status_payload()
    except Exception as error:
        logging.debug("Patch status unavailable: %s", error)
        payload["patch"] = {"error": str(error)}

    if args.json:
        _emit_json(payload)
    else:
        logging.info("26x86 상태 요약")
        logging.info("  플랫폼: %s", platform_label())
        logging.info("  설정 파일: %s", store.config_path)
        last_detect = settings.get("last_detect")
        if last_detect:
            logging.info("  마지막 감지: %s", last_detect)
        patch = payload.get("patch") or {}
        if patch.get("model"):
            logging.info("  모델: %s", patch["model"])
            logging.info(
                "  macOS: %s (%s)",
                patch.get("os_version") or "N/A",
                patch.get("os_build") or "N/A",
            )
            if patch.get("last_patched_version"):
                logging.info(
                    "  마지막 패치: %s (%s)",
                    patch["last_patched_version"],
                    patch.get("last_patched_date") or "N/A",
                )
            if "can_patch" in patch:
                logging.info("  패치 가능: %s", "예" if patch.get("can_patch") else "아니오")
        elif not is_macos():
            logging.info("  패치 상태: macOS 전용 (현재 호스트에서는 사용 불가)")
    return 0


def cmd_wizard(args: argparse.Namespace) -> int:
    _ensure_repo_on_path()

    try:
        from x86.gui.launch import launch_wizard
    except ImportError:
        launch_wizard = None

    if launch_wizard is not None:
        launch_wizard(advanced=args.advanced)
        return 0

    if not is_macos():
        logging.error("GUI를 시작할 수 없습니다. `pip install PySide6 pywebview wxpython` 설치를 확인하세요.")
        return 1

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
    detect.add_argument("--model", help="(비-macOS) 대상 Mac 모델을 수동 지정 (예: iMac18,3)")
    detect.set_defaults(handler=cmd_detect)

    build = subparsers.add_parser("build", help="OpenCore EFI 빌드 (macOS 전용)")
    build.add_argument("--model", help="대상 Mac 모델 (예: iMac18,3)")
    build.add_argument("--json", action="store_true", help="JSON 형식으로 결과 출력")
    build.set_defaults(handler=cmd_build)

    patch = subparsers.add_parser("patch", help="루트 볼륨 패치 적용 (macOS 전용)")
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
        help="고급 GUI (X86_ADVANCED=1 과 동일, macOS 전용)",
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
