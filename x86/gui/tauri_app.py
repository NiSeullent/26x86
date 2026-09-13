"""
Tauri shell launcher for the HTML hybrid wizard.

Default GUI path: Tauri (WKWebView on macOS, WebView2 on Windows) + local
HTTP bridge. Not Qt WebEngine / Chromium.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

from x86.gui import bootstrap
from x86.gui.bridge import WizardBridge
from x86.gui.http_bridge import start_bridge_http_server, wizard_base_url
from x86.manifest import APP_NAME, BUNDLE_ID
from x86.platform import is_macos, is_windows


def _repo_root() -> Path:
    return bootstrap.ensure_repo_on_path()


def _tauri_project_dir() -> Path:
    return _repo_root() / "gui-tauri"


def candidate_tauri_binaries() -> list[Path]:
    """Ordered list of places the Tauri shell binary / .app may live."""
    root = _repo_root()
    env = (os.environ.get("X86_TAURI_BIN") or "").strip()
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env).expanduser())

    if is_macos():
        candidates.extend(
            [
                Path("/Applications/26x86.app/Contents/MacOS/26x86"),
                Path("/Applications/26x86-GUI.app/Contents/MacOS/26x86"),
                Path.home() / "Applications" / "26x86.app" / "Contents" / "MacOS" / APP_NAME,
            ]
        )

    tauri = _tauri_project_dir()
    for profile in ("release", "debug"):
        target = tauri / "target" / profile
        if is_macos():
            candidates.append(
                target / "bundle" / "macos" / f"{APP_NAME}.app" / "Contents" / "MacOS" / APP_NAME
            )
            candidates.append(target / APP_NAME)
            candidates.append(target / "x86-gui")
            candidates.append(target / "app")
        elif is_windows():
            candidates.append(target / f"{APP_NAME}.exe")
            candidates.append(target / "x86-gui.exe")
            candidates.append(target / "app.exe")
        else:
            candidates.append(target / APP_NAME)
            candidates.append(target / "x86-gui")
            candidates.append(target / "app")

    seen: set[str] = set()
    ordered: list[Path] = []
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(path)
    return ordered


def resolve_tauri_binary() -> Optional[Path]:
    for path in candidate_tauri_binaries():
        if path.is_file() and os.access(path, os.X_OK):
            return path
        if is_macos() and path.suffix == ".app" and path.is_dir():
            exe = path / "Contents" / "MacOS" / APP_NAME
            if exe.is_file() and os.access(exe, os.X_OK):
                return exe
    which = shutil.which("26x86-gui") or shutil.which("x86-gui")
    if which:
        return Path(which)
    return None


def tauri_available() -> bool:
    return resolve_tauri_binary() is not None


def _ensure_stdio_for_frozen_gui() -> None:
    if not getattr(sys, "frozen", False):
        return
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")


def launch_tauri_wizard(*, advanced: bool = False) -> None:
    """
    Start the Python HTTP bridge, then open the Tauri WebView shell.

    Raises ``FileNotFoundError`` when no Tauri binary is present (caller falls back).
    """
    _ensure_stdio_for_frozen_gui()
    bootstrap.ensure_repo_on_path()

    binary = resolve_tauri_binary()
    if binary is None:
        raise FileNotFoundError(
            "Tauri GUI binary not found. Build with: cd gui-tauri && cargo tauri build"
        )

    bridge = WizardBridge()
    if advanced:
        result = bridge.launch_wx_action("advanced")
        if result.get("ok"):
            logging.info("Advanced GUI requested; spawned wx runner.")
            return
        logging.warning("Advanced GUI unavailable: %s", result.get("error"))

    web_root = bridge.web_root()
    index_path = bridge.index_path()
    if not index_path.exists():
        raise FileNotFoundError(f"Wizard HTML missing: {index_path}")

    httpd, _ = start_bridge_http_server(web_root, bridge=bridge)
    base = wizard_base_url(httpd)
    url = f"{base}/index.html"
    logging.info("Tauri wizard url=%s binary=%s", url, binary)

    env = os.environ.copy()
    env["X86_WIZARD_URL"] = url
    env["X86_WIZARD_API"] = base
    env.setdefault("X86_APP_NAME", APP_NAME)
    env.setdefault("X86_BUNDLE_ID", BUNDLE_ID)

    title = bridge.get_app_info().get("title") or APP_NAME
    cmd = [str(binary), "--url", url, "--title", title]

    try:
        proc = subprocess.Popen(cmd, env=env, cwd=str(_repo_root()))
    except OSError:
        try:
            httpd.shutdown()
        except Exception:
            logging.debug("wizard http shutdown failed", exc_info=True)
        raise

    try:
        returncode = proc.wait()
        if returncode not in (0, None):
            logging.warning("Tauri shell exited with code %s", returncode)
    finally:
        try:
            httpd.shutdown()
        except Exception:
            logging.debug("wizard http shutdown failed", exc_info=True)
        time.sleep(0.05)


def smoke_tauri_paths() -> dict[str, Any]:
    binary = resolve_tauri_binary()
    return {
        "ok": True,
        "tauri_available": binary is not None,
        "tauri_binary": str(binary) if binary else None,
        "tauri_project": str(_tauri_project_dir()),
        "candidates": [str(p) for p in candidate_tauri_binaries()[:12]],
    }
