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

        payload = smoke_test_bridge()
        self.assertTrue(payload["ok"], json.dumps(payload, ensure_ascii=False))
        self.assertIn("qt_chromium_available", payload)
        self.assertIn("pywebview_gui", payload)

    def test_macos_gui_prefers_qt_not_cocoa(self) -> None:
        from x86.platform import is_macos, qt_webengine_available, resolve_pywebview_gui

        if not is_macos():
            self.skipTest("macOS-only backend preference")
        gui = resolve_pywebview_gui()
        if qt_webengine_available():
            self.assertEqual(gui, "qt")
        else:
            self.assertEqual(gui, "cocoa")

    def test_html_bootstraps_qt_or_pywebview_bridge(self) -> None:
        from x86.gui.bridge import WizardBridge

        index = WizardBridge().index_path().read_text(encoding="utf-8")
        js = (WizardBridge().web_root() / "app.js").read_text(encoding="utf-8")
        self.assertIn("qrc:", index)
        self.assertIn("connectQtWebChannel", js)
        self.assertIn("promisifyQtBridge", js)
        self.assertIn("pywebviewready", js)


if __name__ == "__main__":
    unittest.main()
