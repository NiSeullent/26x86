"""
cli.py: 명령줄 인터페이스 파싱 및 한국어 도움말
"""

import argparse
import json
import sys

CLI_ACTION_ARGS = (
    "build",
    "patch_sys_vol",
    "patch",
    "unpatch_sys_vol",
    "unpatch",
    "validate",
    "auto_patch",
    "prepare_for_update",
    "cache_os",
    "detect",
    "status",
)


def _help_text(lang: str) -> dict:
    if lang == "ko":
        return {
            "description": "26x86 — 오래된 Mac에서 최신 macOS를 사용하기 위한 도구",
            "epilog": (
                "예시:\n"
                "  %(prog)s --detect\n"
                "  %(prog)s --detect --json\n"
                "  %(prog)s --build --model iMac11,2\n"
                "  %(prog)s --patch\n"
                "  %(prog)s --status --json\n"
                "  %(prog)s --unpatch\n"
                "  %(prog)s --lang ko --help"
            ),
            "build": "OpenCore EFI 패치 생성",
            "detect": "Mac 모델 및 하드웨어 정보 확인",
            "patch": "루트 볼륨 패치 적용 (--patch_sys_vol 와 동일)",
            "patch_sys_vol": "루트 볼륨 패치 적용",
            "unpatch": "루트 볼륨 패치 되돌리기 (--unpatch_sys_vol 와 동일)",
            "unpatch_sys_vol": "루트 볼륨 패치 되돌리기 (실험적)",
            "status": "현재 패치 상태 표시",
            "json": "JSON 형식으로 결과 출력",
            "lang": "도움말 언어 (ko 또는 en)",
            "model": "대상 Mac 모델 (예: iMac11,2)",
            "verbose": "자세한 부팅 로그 사용",
            "advanced_gui": "고급 GUI(기존 메인 메뉴) 실행",
        }
    return {
        "description": "26x86 — Run unsupported macOS on older Macs",
        "epilog": (
            "Examples:\n"
            "  %(prog)s --detect\n"
            "  %(prog)s --build --model iMac11,2\n"
            "  %(prog)s --patch\n"
            "  %(prog)s --status --json"
        ),
        "build": "Build OpenCore EFI",
        "detect": "Detect Mac model and hardware",
        "patch": "Apply root volume patches (alias for --patch_sys_vol)",
        "patch_sys_vol": "Apply root volume patches",
        "unpatch": "Revert root volume patches (alias for --unpatch_sys_vol)",
        "unpatch_sys_vol": "Revert root volume patches (experimental)",
        "status": "Show patch status",
        "json": "Emit machine-readable JSON output",
        "lang": "Help language (ko or en)",
        "model": "Target Mac model (e.g. iMac11,2)",
        "verbose": "Enable verbose boot",
        "advanced_gui": "Launch advanced GUI (legacy main menu)",
    }


def build_parser(lang: str = "ko") -> argparse.ArgumentParser:
    h = _help_text(lang)
    parser = argparse.ArgumentParser(
        prog="26x86",
        description=h["description"],
        epilog=h["epilog"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Primary actions
    parser.add_argument("--detect", help=h["detect"], action="store_true")
    parser.add_argument("--status", help=h["status"], action="store_true")
    parser.add_argument("--build", help=h["build"], action="store_true")
    parser.add_argument("--patch", help=h["patch"], action="store_true")
    parser.add_argument("--patch_sys_vol", help=h["patch_sys_vol"], action="store_true")
    parser.add_argument("--unpatch", help=h["unpatch"], action="store_true")
    parser.add_argument("--unpatch_sys_vol", help=h["unpatch_sys_vol"], action="store_true")

    # Output / locale
    parser.add_argument("--json", help=h["json"], action="store_true")
    parser.add_argument("--lang", choices=["ko", "en"], default=lang, help=h["lang"])

    # GUI mode flags
    parser.add_argument("--advanced_gui", help=h["advanced_gui"], action="store_true")
    parser.add_argument("--gui_patch", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--gui_unpatch", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--update_installed", help=argparse.SUPPRESS, action="store_true")

    # Build options (existing)
    parser.add_argument("--verbose", help=h["verbose"], action="store_true")
    parser.add_argument("--debug_oc", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--debug_kext", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--hide_picker", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--disable_sip", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--disable_smb", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--vault", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--support_all", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--firewire", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--nvme", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--wlan", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--moderate_smbios", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--disable_tb", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--force_surplus", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--model", action="store", help=h["model"])
    parser.add_argument("--disk", action="store", help=argparse.SUPPRESS)
    parser.add_argument("--smbios_spoof", action="store", help=argparse.SUPPRESS)

    # Other existing actions
    parser.add_argument("--prepare_for_update", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--cache_os", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--validate", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--auto_patch", help=argparse.SUPPRESS, action="store_true")

    return parser


def _normalize_args(args: argparse.Namespace) -> argparse.Namespace:
    """Alias flags to existing handlers without breaking legacy args."""
    if args.patch:
        args.patch_sys_vol = True
    if args.unpatch:
        args.unpatch_sys_vol = True
    return args


def _has_cli_action(args: argparse.Namespace) -> bool:
    return any(getattr(args, name, False) for name in CLI_ACTION_ARGS)


def parse_cli_args(argv=None):
    """
    Parse CLI arguments. Returns None when GUI should launch.
    Handles --help and --lang ko --help with localized help text.
    """
    argv = argv if argv is not None else sys.argv[1:]

    # Pre-scan for language before building parser help text
    lang = "ko"
    for i, arg in enumerate(argv):
        if arg == "--lang" and i + 1 < len(argv):
            lang = argv[i + 1]
            break
        if arg.startswith("--lang="):
            lang = arg.split("=", 1)[1]
            break

    if lang not in ("ko", "en"):
        lang = "ko"

    if "--help" in argv or "-h" in argv:
        build_parser(lang).print_help()
        sys.exit(0)

    parser = build_parser(lang)
    args = parser.parse_args(argv)
    args = _normalize_args(args)

    # --advanced_gui alone should still open GUI (handled in gui_entry)
    if args.advanced_gui and not _has_cli_action(args):
        return args

    if not _has_cli_action(args):
        return None

    return args


def is_cli_mode(args) -> bool:
    """True when args request a non-GUI CLI action."""
    if args is None:
        return False
    return _has_cli_action(args)


def emit_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
