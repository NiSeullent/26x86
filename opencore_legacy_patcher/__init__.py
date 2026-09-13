"""
opencore_legacy_patcher package — lazy entry to avoid import cycles with x86.gui.
"""

__all__ = ["main"]


def main() -> None:
    from .application_entry import main as _run

    _run()
