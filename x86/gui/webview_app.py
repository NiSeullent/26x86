"""
pywebview shell for the HTML hybrid 26x86 wizard.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Optional

from x86.gui import bootstrap
from x86.gui.bridge import WizardBridge
from x86.platform import resolve_pywebview_gui


class WebviewApi:
    """JS-callable API surface (pywebview js_api)."""

    def __init__(self, bridge: Optional[WizardBridge] = None) -> None:
        self._bridge = bridge or WizardBridge()

    def get_app_info(self) -> dict[str, Any]:
        return self._bridge.get_app_info()

    def get_steps(self) -> list[dict[str, str]]:
        return self._bridge.get_steps()

    def detect(self, refresh: bool = False) -> dict[str, Any]:
        return self._bridge.detect(refresh=refresh)

    def get_macos_choices(self) -> dict[str, Any]:
        return self._bridge.get_macos_choices()

    def set_target_os(self, kernel: int) -> dict[str, Any]:
        return self._bridge.set_target_os(kernel)

    def get_patch_status(self) -> dict[str, Any]:
        return self._bridge.get_patch_status()

    def get_status(self) -> dict[str, Any]:
        return self._bridge.get_status()

    def get_settings(self) -> dict[str, Any]:
        return self._bridge.get_settings()

    def save_settings(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._bridge.save_settings(data)

    def host_can_build(self) -> dict[str, Any]:
        return self._bridge.host_can_build()

    def launch_wx_action(self, action: str) -> dict[str, Any]:
        return self._bridge.launch_wx_action(action)

    def reveal_log(self) -> dict[str, Any]:
        return self._bridge.reveal_log()

    def open_guide(self) -> dict[str, Any]:
        return self._bridge.open_guide()


def launch_webview_wizard(*, advanced: bool = False) -> None:
    """Open the HTML hybrid wizard in a native pywebview window."""
    import webview

    bootstrap.ensure_repo_on_path()
    bridge = WizardBridge()
    api = WebviewApi(bridge)

    if advanced:
        result = bridge.launch_wx_action("advanced")
        if result.get("ok"):
            logging.info("Advanced GUI requested; spawned wx runner.")
            return
        logging.warning("Advanced GUI unavailable: %s", result.get("error"))

    title = bridge.get_app_info()["title"]
    window = webview.create_window(
        title,
        url=bridge.index_uri(),
        js_api=api,
        width=960,
        height=720,
        min_size=(760, 560),
        resizable=True,
        text_select=True,
        background_color="#e8edf3",
    )
    webview.start(debug=False, gui=resolve_pywebview_gui())


def smoke_test_bridge() -> dict[str, Any]:
    """Headless bridge checks (no GUI)."""
    bootstrap.ensure_repo_on_path()
    bridge = WizardBridge()
    results: dict[str, Any] = {"ok": True, "checks": {}}

    for name, fn in (
        ("app_info", bridge.get_app_info),
        ("steps", bridge.get_steps),
        ("detect", lambda: bridge.detect(refresh=False)),
        ("macos", bridge.get_macos_choices),
        ("status", bridge.get_status),
        ("host_can_build", bridge.host_can_build),
    ):
        try:
            payload = fn()
            results["checks"][name] = {"ok": True, "keys": list(payload.keys()) if isinstance(payload, dict) else len(payload)}
        except Exception as exc:
            results["ok"] = False
            results["checks"][name] = {"ok": False, "error": str(exc)}

    results["web_index"] = str(bridge.web_root() / "index.html")
    return results


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if argv and argv[0] == "--smoke":
        import json

        payload = smoke_test_bridge()
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    launch_webview_wizard(advanced="--advanced" in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
