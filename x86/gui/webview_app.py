"""
HTML hybrid 26x86 wizard shell.

Default: PySide6 Qt WebEngine (Chromium).
Fallback: pywebview (Qt / Edge WebView2), then Cocoa WebKit on macOS only.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Optional

from x86.gui import bootstrap
from x86.gui.bridge import WizardBridge
from x86.platform import is_macos, resolve_pywebview_gui, qt_webengine_available


class WebviewApi:
    """JS-callable API surface (pywebview js_api / Qt QWebChannel)."""

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


def _ensure_stdio_for_frozen_gui() -> None:
    """PyInstaller windowed apps may have no stdout/stderr; bottle needs them."""
    if not getattr(sys, "frozen", False):
        return
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")


def _requested_backend() -> str:
    return (os.environ.get("X86_GUI_BACKEND") or "auto").strip().lower()


def _should_try_qt_chromium(requested: str) -> bool:
    if requested in ("cocoa", "webkit", "pywebview", "edge", "edgechromium"):
        return False
    if requested in ("auto", "", "chromium", "qt", "webengine"):
        return True
    return requested == "chromium"


def launch_webview_wizard(*, advanced: bool = False) -> None:
    """Open the HTML hybrid wizard. Chromium is preferred; Cocoa is last-resort."""
    _ensure_stdio_for_frozen_gui()
    bootstrap.ensure_repo_on_path()
    requested = _requested_backend()

    if _should_try_qt_chromium(requested) and qt_webengine_available():
        try:
            from x86.gui.qt_chromium import launch_qt_chromium_wizard

            logging.info("Launching HTML wizard with Qt WebEngine (Chromium)")
            launch_qt_chromium_wizard(advanced=advanced)
            return
        except Exception:
            logging.exception("Qt WebEngine (Chromium) failed; trying pywebview")
            if requested in ("chromium", "qt", "webengine"):
                raise

    _launch_pywebview_wizard(advanced=advanced, requested=requested)


def _launch_pywebview_wizard(*, advanced: bool, requested: str) -> None:
    import webview

    bridge = WizardBridge()
    api = WebviewApi(bridge)

    if advanced:
        result = bridge.launch_wx_action("advanced")
        if result.get("ok"):
            logging.info("Advanced GUI requested; spawned wx runner.")
            return
        logging.warning("Advanced GUI unavailable: %s", result.get("error"))

    title = bridge.get_app_info()["title"]
    index_path = bridge.index_uri()
    logging.info("pywebview wizard url=%s exists=%s", index_path, os.path.exists(index_path))

    gui = resolve_pywebview_gui()
    if requested in ("cocoa", "webkit"):
        gui = "cocoa"
    elif requested in ("edge", "edgechromium"):
        gui = "edgechromium"
    elif requested == "qt":
        gui = "qt"

    if requested in ("cocoa", "webkit"):
        backends = ["cocoa"]
    elif gui == "cocoa":
        backends = ["qt", "cocoa"] if is_macos() else ["qt"]
    else:
        backends = [gui]
        if is_macos() and gui != "cocoa":
            backends.append("cocoa")

    last_error: Optional[BaseException] = None
    for index, backend in enumerate(backends):
        try:
            logging.info("Starting pywebview with gui=%s http_server=True", backend)
            os.environ.setdefault("QT_API", "pyside6")
            webview.create_window(
                title,
                url=index_path,
                js_api=api,
                width=960,
                height=720,
                min_size=(760, 560),
                resizable=True,
                text_select=True,
                background_color="#e8edf3",
            )
            webview.start(debug=False, gui=backend, http_server=True)
            return
        except Exception as exc:
            last_error = exc
            logging.warning("pywebview gui=%s failed: %s", backend, exc)
            if index == len(backends) - 1:
                raise
            continue

    if last_error:
        raise last_error


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

    index_path = bridge.index_path()
    results["web_index"] = str(index_path)
    results["index_is_file_uri"] = bridge.index_uri().startswith("file://")
    results["qt_chromium_available"] = qt_webengine_available()
    results["pywebview_gui"] = resolve_pywebview_gui()
    results["gui_backend_env"] = _requested_backend()
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
