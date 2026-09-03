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


if __name__ == "__main__":
    unittest.main()
