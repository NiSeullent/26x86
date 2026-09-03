"""Headless smoke tests for the HTML wizard Python bridge."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class BridgeSmokeTest(unittest.TestCase):
    def test_bridge_roundtrip(self) -> None:
        from x86.gui.bridge import WizardBridge

        bridge = WizardBridge()
        info = bridge.get_app_info()
        self.assertEqual(info["bundle_id"], "com.niseullent.26x86")
        self.assertTrue(bridge.index_path().exists())
        self.assertFalse(bridge.index_uri().startswith("file://"))
        self.assertTrue((bridge.web_root() / "app.js").exists())
        self.assertTrue((bridge.web_root() / "index.html").exists())
        if info.get("logo_url"):
            self.assertTrue(
                info["logo_url"].startswith("data:image/"),
                "logo should be embedded for HTTP-served wizard UI",
            )

        steps = bridge.get_steps()
        self.assertEqual(len(steps), 5)

        detect = bridge.detect(refresh=False)
        self.assertTrue(detect["ok"])
        self.assertIn("model", detect["detect"])

        macos = bridge.get_macos_choices()
        self.assertIn("choices", macos)
        self.assertGreaterEqual(len(macos["choices"]), 1)

        status = bridge.get_status()
        self.assertTrue(status["ok"])

    def test_webview_smoke_helper(self) -> None:
        from x86.gui.webview_app import smoke_test_bridge
        from x86.platform import is_macos

        payload = smoke_test_bridge()
        self.assertTrue(payload["ok"], json.dumps(payload, ensure_ascii=False))
        self.assertIn("qt_chromium_available", payload)
        self.assertIn("pywebview_gui", payload)
        self.assertTrue(payload["qt_opt_in_only"])
        if is_macos():
            self.assertEqual(payload["pywebview_gui"], "cocoa")
            self.assertTrue(payload["macos_default_cocoa"])

    def test_macos_gui_defaults_to_cocoa(self) -> None:
        from x86.gui.webview_app import (
            _requested_backend,
            _should_try_qt_chromium,
            launch_webview_wizard,
        )
        from x86.platform import is_macos, resolve_pywebview_gui

        if not is_macos():
            self.skipTest("macOS-only backend preference")
        self.assertEqual(resolve_pywebview_gui(), "cocoa")
        self.assertEqual(_requested_backend(), "auto")
        self.assertFalse(_should_try_qt_chromium("auto"))
        self.assertFalse(_should_try_qt_chromium(_requested_backend()))
        self.assertTrue(_should_try_qt_chromium("qt"))
        # Cocoa+HTTP is the default entry; Chromium only via X86_GUI_BACKEND.
        self.assertIn("cocoa", (launch_webview_wizard.__doc__ or "").lower())

    def test_html_bootstraps_qt_or_pywebview_bridge(self) -> None:
        from x86.gui.bridge import WizardBridge

        index = WizardBridge().index_path().read_text(encoding="utf-8")
        js = (WizardBridge().web_root() / "app.js").read_text(encoding="utf-8")
        self.assertIn("qrc:", index)
        self.assertIn("connectQtWebChannel", js)
        self.assertIn("promisifyQtBridge", js)
    def test_frozen_webengine_lookup_is_safe(self) -> None:
        from x86.gui.qt_chromium import _frozen_webengine_process

        self.assertIsNone(_frozen_webengine_process())


if __name__ == "__main__":
    unittest.main()
