"""
Shared constants bootstrap for HTML wizard bridge and wx subprocess runner.
"""

from __future__ import annotations

import logging
import sys
import threading
from pathlib import Path
from typing import Optional

from opencore_legacy_patcher import constants
from opencore_legacy_patcher.detections import device_probe, os_probe
from opencore_legacy_patcher.support import defaults, reroute_payloads, utilities
from x86.platform import is_linux, is_macos, is_windows


_constants: Optional[constants.Constants] = None
_init_lock = threading.Lock()


def ensure_repo_on_path() -> Path:
    root = Path(__file__).resolve().parent.parent.parent
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root


def get_constants(*, start_unpack: bool = True) -> constants.Constants:
    """Return a process-wide Constants instance (lazy, thread-safe)."""
    global _constants
    if _constants is not None:
        return _constants

    with _init_lock:
        if _constants is not None:
            return _constants

        ensure_repo_on_path()
        c = constants.Constants()
        c.wxpython_variant = True
        c.gui_mode = True
        c.cli_mode = False

        os_data = os_probe.OSProbe()
        c.detected_os = os_data.detect_kernel_major()
        c.detected_os_minor = os_data.detect_kernel_minor()
        c.detected_os_build = os_data.detect_os_build()
        c.detected_os_version = os_data.detect_os_version()

        c.computer = device_probe.Computer.probe()
        if not is_macos():
            c.host_is_hackintosh = True
        elif c.computer.firmware_vendor != "Apple":
            c.host_is_hackintosh = True
        if c.computer.real_model and c.computer.real_model.startswith("VMware"):
            c.host_is_hackintosh = True
            c.host_is_vmware_vm = True

        if c.computer.build_model is None:
            c.computer.build_model = c.computer.real_model

        defaults.GenerateDefaults(c.computer.real_model, True, c)

        if start_unpack and is_macos():
            c.unpack_thread = threading.Thread(
                target=reroute_payloads.RoutePayloadDiskImage,
                args=(c,),
                daemon=True,
            )
            c.unpack_thread.start()

        launcher_binary = sys.executable
        repo = ensure_repo_on_path()
        if is_macos() and "python" in launcher_binary.lower():
            c.launcher_script = str(repo / "26x86-GUI.command")
        elif is_windows():
            c.launcher_script = str(repo / "26x86.bat")
        elif is_linux():
            c.launcher_script = str(repo / "26x86.sh")
        c.launcher_binary = launcher_binary

        if is_macos():
            try:
                c.booted_oc_disk = utilities.find_disk_off_uuid(
                    utilities.clean_device_path(c.computer.opencore_path)
                )
            except Exception as exc:
                logging.debug("booted_oc_disk unavailable: %s", exc)

        _constants = c
        return c


def reset_constants() -> None:
    """Clear cached constants (tests)."""
    global _constants
    with _init_lock:
        _constants = None
