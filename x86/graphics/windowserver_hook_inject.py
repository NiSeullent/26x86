"""Track L-WS — SkyLightPlugins + DYLD plist orchestration; no Mach injector."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from x86.graphics.skylight_lut import (
    ASENTIENTBOT_SKYLIGHT_PLUGINS,
    COMPOSITOR_PLUGIN_SHA256,
    COMPOSITOR_PLUGIN_STEM_ALLOWLIST,
    MORAEA_NON_METAL_FRAMEWORKS,
    SKYLIGHT_PLUGINS_INSTALL_DIR,
    SKYLIGHT_STUB_MARKER,
    enumerate_evidence_skylight_plugins,
    stock_skylight_loads_plugins,
)
from x86.graphics.windowserver_hook_gate import (
    extreme_windowserver_hooks_allowed,
    require_extreme_windowserver_hooks,
)

WINDOWSERVER_BIN = "/System/Library/CoreServices/WindowServer"
LAUNCHD_LABEL = "local.26x86.extreme.windowserver-hook"
LAUNCHD_PLIST_PATH = f"/Library/LaunchDaemons/{LAUNCHD_LABEL}.plist"


def plan_skylight_plugin_injection(overlay_plugins_dir: Optional[Path] = None, *, require_gate: bool = True) -> dict[str, Any]:
    if require_gate:
        require_extreme_windowserver_hooks()
    files: dict[str, str] = {}
    if overlay_plugins_dir is not None:
        files = enumerate_evidence_skylight_plugins(Path(overlay_plugins_dir))
    return {
        "gated": extreme_windowserver_hooks_allowed(),
        "method": "SkyLightPlugins",
        "install_dir": SKYLIGHT_PLUGINS_INSTALL_DIR,
        "stub_marker": SKYLIGHT_STUB_MARKER,
        "stock_skylight_loads_plugins": stock_skylight_loads_plugins(),
        "effective_on_stock_tahoe": False,
        "allowlisted_stems": sorted(COMPOSITOR_PLUGIN_STEM_ALLOWLIST),
        "sha256_pinned_stems": sorted(COMPOSITOR_PLUGIN_SHA256),
        "selected_files": files,
        "evidence": {"asentientbot": ASENTIENTBOT_SKYLIGHT_PLUGINS, "moraea": MORAEA_NON_METAL_FRAMEWORKS},
        "notes_ko": ["스톡 Tahoe는 Plugins 미로드.", "SHA 미핀/DropboxHack 거부."],
    }


def render_dyld_insert_launchd_plist(dylib_path: str, *, require_gate: bool = True) -> str:
    if require_gate:
        require_extreme_windowserver_hooks()
    dylib = Path(dylib_path)
    if dylib.suffix != ".dylib":
        raise ValueError("dylib_path must end with .dylib")
    path_xml = str(dylib).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<!-- 26x86 Track L-WS RESEARCH ONLY -->
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{LAUNCHD_LABEL}</string>
  <key>Disabled</key>
  <true/>
  <key>ProgramArguments</key>
  <array>
    <string>{WINDOWSERVER_BIN}</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>DYLD_INSERT_LIBRARIES</key>
    <string>{path_xml}</string>
  </dict>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
"""


def plan_process_injection(*, require_gate: bool = True) -> dict[str, Any]:
    if require_gate:
        require_extreme_windowserver_hooks()
    return {
        "gated": extreme_windowserver_hooks_allowed(),
        "windowserver_bin": WINDOWSERVER_BIN,
        "paths": [
            {"id": "skylight_plugins", "status": "orchestrated", "sip_impact": "data_volume_ok_with_root_patch", "detail": plan_skylight_plugin_injection(require_gate=False)},
            {"id": "dyld_insert_launchd", "status": "plist_generator_only", "sip_impact": "blocked_when_sip_enabled", "launchd_label": LAUNCHD_LABEL, "launchd_plist_path": LAUNCHD_PLIST_PATH, "detail": "SIP rejects DYLD_INSERT into WindowServer; Disabled=true."},
            {"id": "mach_task_inject_function_hook", "status": "not_implemented", "sip_impact": "requires_sip_off_and_symbols", "detail": "No public SkyLight LUT symbol map — Research R4 forbidden."},
        ],
        "notes_ko": ["일반 process injector 미제공.", "사설 심볼 후킹 미구현."],
    }
