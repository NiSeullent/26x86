"""
Bootstrap and launch the default 26x86 wizard GUI.
"""

import sys
from pathlib import Path


def _ensure_repo_root() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _strip_x86_subcommand() -> None:
    """Remove ``python -m x86 <subcommand>`` tokens so legacy CLI parsing succeeds."""
    filtered: list[str] = []
    skip_next = False
    for i, arg in enumerate(sys.argv):
        if skip_next:
            skip_next = False
            continue
        if i == 0:
            filtered.append(arg)
            continue
        if arg in ("-m", "x86"):
            continue
        if arg in ("wizard", "detect", "build", "patch", "status"):
            continue
        if arg == "--json":
            continue
        if arg.startswith("--model="):
            continue
        if arg == "--model":
            skip_next = True
            continue
        filtered.append(arg)
    sys.argv = filtered


def launch_wizard(advanced: bool = False) -> None:
    """Start the wx wizard as the default end-user GUI."""
    import os

    _ensure_repo_root()
    _strip_x86_subcommand()
    if advanced:
        if os.environ.get("X86_ADVANCED") != "1":
            os.environ["X86_ADVANCED"] = "1"
        if "--advanced_gui" not in sys.argv:
            sys.argv.append("--advanced_gui")
    from opencore_legacy_patcher.application_entry import main

    main()


def launch_advanced_gui() -> None:
    """Start the legacy wx MainFrame (requires ``X86_ADVANCED=1``)."""
    from x86.gui.branding import is_advanced_gui_enabled

    if not is_advanced_gui_enabled():
        raise RuntimeError(
            "Advanced GUI requires X86_ADVANCED=1. "
            "Normal users should use: python -m x86 wizard"
        )
    _ensure_repo_root()
    _strip_x86_subcommand()
    if "--advanced_gui" not in sys.argv:
        sys.argv.append("--advanced_gui")
    from opencore_legacy_patcher.application_entry import main

    main()
