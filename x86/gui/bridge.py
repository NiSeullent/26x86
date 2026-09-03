"""
Python ↔ JS bridge backend for the HTML hybrid wizard.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any, Optional

from opencore_legacy_patcher.datasets import smbios_data
from opencore_legacy_patcher.datasets.os_data import os_conversion
from opencore_legacy_patcher.datasets import os_data as os_data_module
from opencore_legacy_patcher.sys_patch.patchsets import (
    HardwarePatchsetDetection,
    HardwarePatchsetValidation,
)
from opencore_legacy_patcher.wx_gui import gui_support

from x86.cli import _patch_status_payload, _serialize_detect_payload, _sw_vers
from x86.gui import bootstrap
from x86.gui.branding import (
    is_advanced_gui_enabled,
    logo_png_path,
    logo_svg_path,
    resolve_gui_logo_path,
    window_title,
)
from x86.gui.wizard import errors, strings
from x86.manifest import APP_NAME, BUNDLE_ID, COPYRIGHT, PATCHER_VERSION, URL_GUIDE
from x86.settings import SettingsStore


MACOS_CHOICES: list[dict[str, Any]] = [
    {"label": "macOS Ventura (13)", "kernel": os_data_module.os_data.ventura},
    {"label": "macOS Sonoma (14)", "kernel": os_data_module.os_data.sonoma},
    {"label": "macOS Sequoia (15)", "kernel": os_data_module.os_data.sequoia},
    {"label": "macOS Tahoe (26)", "kernel": os_data_module.os_data.tahoe},
]

WEB_STEPS: list[dict[str, str]] = [
    {
        "id": "welcome",
        "title": "시작",
        "heading": "26x86에 오신 것을 환영합니다",
        "desc": "오래된 Mac에서 최신 macOS를 사용할 수 있도록 단계별로 안내합니다.",
    },
    {
        "id": "detect",
        "title": "1. 내 Mac 확인",
        "heading": strings.STEP_DETECT_HEADING,
        "desc": strings.STEP_DETECT_DESC,
    },
    {
        "id": "build",
        "title": "2. 패치 생성",
        "heading": strings.STEP_BUILD_HEADING,
        "desc": strings.STEP_BUILD_DESC,
    },
    {
        "id": "patch",
        "title": "3. 설치·패치",
        "heading": strings.STEP_ROOT_HEADING,
        "desc": f"{strings.STEP_INSTALL_DESC}\n{strings.STEP_ROOT_DESC}",
    },
    {
        "id": "done",
        "title": "4. 완료",
        "heading": "설정이 완료되었습니다",
        "desc": "EFI를 설치하고 macOS를 부팅한 뒤, 필요하면 루트 패치를 적용하세요.",
    },
]


class WizardBridge:
    """Backend API consumed by pywebview and headless smoke tests."""

    def __init__(self) -> None:
        self._settings = SettingsStore()
        self._selected_target_os: Optional[int] = None
        self._build_completed = False

    def _constants(self):
        return bootstrap.get_constants(start_unpack=True)

    def get_app_info(self) -> dict[str, Any]:
        c = self._constants()
        logo = resolve_gui_logo_path(c.icns_resource_path)
        logo_url = None
        if logo and logo.exists():
            logo_url = logo.as_uri()
        elif logo_svg_path().exists():
            logo_url = logo_svg_path().as_uri()

        return {
            "app_name": APP_NAME,
            "bundle_id": BUNDLE_ID,
            "version": PATCHER_VERSION,
            "copyright": COPYRIGHT,
            "title": window_title(PATCHER_VERSION),
            "guide_link": URL_GUIDE,
            "logo_url": logo_url,
            "advanced_enabled": is_advanced_gui_enabled(),
            "status_ready": strings.STATUS_READY,
        }

    def get_steps(self) -> list[dict[str, str]]:
        return WEB_STEPS

    def get_macos_choices(self) -> list[dict[str, Any]]:
        c = self._constants()
        current_kernel = c.detected_os
        choices = []
        default_idx = 2
        for i, item in enumerate(MACOS_CHOICES):
            if item["kernel"] == current_kernel:
                default_idx = i
            choices.append(
                {
                    "label": item["label"],
                    "kernel": item["kernel"],
                    "marketing": os_conversion.convert_kernel_to_marketing_name(item["kernel"]),
                }
            )

        if self._selected_target_os is None:
            self._selected_target_os = MACOS_CHOICES[default_idx]["kernel"]

        model = c.custom_model or c.computer.real_model
        max_os = smbios_data.smbios_dictionary.get(model, {}).get("Max OS Supported")
        recommended = None
        if max_os is not None:
            recommended = os_conversion.convert_kernel_to_marketing_name(max_os)

        return {
            "choices": choices,
            "default_index": default_idx,
            "selected_kernel": self._selected_target_os,
            "current_marketing": os_conversion.convert_kernel_to_marketing_name(current_kernel),
            "recommended": recommended,
        }

    def set_target_os(self, kernel: int) -> dict[str, Any]:
        self._selected_target_os = int(kernel)
        label = next(
            (item["label"] for item in MACOS_CHOICES if item["kernel"] == kernel),
            str(kernel),
        )
        return {"ok": True, "selected_kernel": kernel, "label": label}

    def detect(self, refresh: bool = False) -> dict[str, Any]:
        c = self._constants()
        if refresh:
            from opencore_legacy_patcher.detections import device_probe

            c.computer = device_probe.Computer.probe()
            if c.computer.build_model is None:
                c.computer.build_model = c.computer.real_model

        payload = _serialize_detect_payload(c.computer)
        payload["os_version"] = payload.get("os_version") or c.detected_os_version or _sw_vers("productVersion")
        payload["os_build"] = payload.get("os_build") or c.detected_os_build or _sw_vers("buildVersion")
        payload["marketing_name"] = smbios_data.smbios_dictionary.get(
            payload["model"], {}
        ).get("Marketing Name", payload["model"])

        self._settings.record_detect(payload["model"])
        return {"ok": True, "detect": payload}

    def get_patch_status(self) -> dict[str, Any]:
        try:
            patch = _patch_status_payload()
            active = patch.get("patches_available") or []
            lines = []
            if patch.get("last_patched_version"):
                lines.append(f"{strings.STEP_ROOT_LAST}: {patch['last_patched_version']}")
            if active:
                lines.append("적용 가능한 패치:")
                lines.extend(f"• {name}" for name in active[:8])
                if len(active) > 8:
                    lines.append(f"… 외 {len(active) - 8}개")
            else:
                lines.append(strings.STEP_ROOT_NONE)

            if not patch.get("can_patch"):
                lines.append("현재 상태에서는 패치를 적용할 수 없습니다 (SIP 등 확인 필요).")

            return {"ok": True, "patch": patch, "summary": "\n".join(lines)}
        except Exception as exc:
            logging.exception("patch status failed")
            return {"ok": False, "error": errors.user_message(exc), "summary": errors.user_message(exc)}

    def get_status(self) -> dict[str, Any]:
        settings = self._settings.load()
        patch_result = self.get_patch_status()
        return {
            "ok": True,
            "settings": settings,
            "config_path": str(self._settings.config_path),
            "patch": patch_result.get("patch"),
            "build_completed": self._build_completed,
        }

    def get_settings(self) -> dict[str, Any]:
        from opencore_legacy_patcher.support import global_settings

        gs = global_settings.GlobalEnviromentSettings()
        analytics = gs.read_property("EnableCrashAndAnalyticsReporting")
        if analytics is None:
            analytics = True
        data = self._settings.load()
        data["analytics"] = bool(analytics)
        return {"ok": True, "settings": data, "config_path": str(self._settings.config_path)}

    def save_settings(self, data: dict[str, Any]) -> dict[str, Any]:
        from opencore_legacy_patcher.support import global_settings

        try:
            store_data = {k: v for k, v in data.items() if k != "analytics"}
            if store_data:
                current = self._settings.load()
                current.update(store_data)
                self._settings.save(current)

            if "analytics" in data:
                gs = global_settings.GlobalEnviromentSettings()
                gs.write_property("EnableCrashAndAnalyticsReporting", bool(data["analytics"]))

            return {"ok": True}
        except Exception as exc:
            logging.exception("save_settings failed")
            return {"ok": False, "error": errors.user_message(exc)}

    def host_can_build(self) -> dict[str, Any]:
        c = self._constants()
        can_build = gui_support.CheckProperties(c).host_can_build()
        return {"ok": True, "can_build": bool(can_build), "build_completed": self._build_completed}

    def mark_build_completed(self) -> dict[str, Any]:
        self._build_completed = True
        return {"ok": True, "build_completed": True}

    def launch_wx_action(self, action: str) -> dict[str, Any]:
        """Spawn legacy wx UI for build/install/patch flows (separate process)."""
        allowed = {
            "build",
            "install",
            "patch",
            "unpatch",
            "model_change",
            "advanced",
            "help",
        }
        if action not in allowed:
            return {"ok": False, "error": f"Unknown action: {action}"}

        if action == "advanced" and not is_advanced_gui_enabled():
            return {"ok": False, "error": strings.ERR_ADVANCED_DISABLED}

        if action == "build":
            check = self.host_can_build()
            if not check["can_build"]:
                return {
                    "ok": False,
                    "error": "이 Mac에서는 EFI를 만들 수 없습니다. 다른 지원 Mac에서 실행해 주세요.",
                }

        repo = bootstrap.ensure_repo_on_path()
        env = os.environ.copy()
        env.setdefault("X86_LEGACY_GUI", "1")
        if action == "advanced":
            env["X86_ADVANCED"] = "1"

        cmd = [sys.executable, "-m", "x86.gui.wx_runner", action]
        try:
            subprocess.Popen(
                cmd,
                cwd=str(repo),
                env=env,
                start_new_session=True,
            )
            if action == "build":
                self._build_completed = True
            return {"ok": True, "action": action, "spawned": True}
        except OSError as exc:
            logging.exception("wx_runner spawn failed")
            return {"ok": False, "error": errors.user_message(exc)}

    def reveal_log(self) -> dict[str, Any]:
        c = self._constants()
        try:
            subprocess.run(["/usr/bin/open", "--reveal", c.log_filepath], check=False)
            return {"ok": True, "path": c.log_filepath}
        except OSError as exc:
            return {"ok": False, "error": errors.user_message(exc)}

    def open_guide(self) -> dict[str, Any]:
        c = self._constants()
        webbrowser.open(c.guide_link)
        return {"ok": True, "url": c.guide_link}

    def web_root(self) -> Path:
        import sys

        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            if meipass:
                candidate = Path(meipass) / "x86" / "gui" / "web"
                if candidate.exists():
                    return candidate
        return Path(__file__).resolve().parent / "web"

    def index_uri(self) -> str:
        index = self.web_root() / "index.html"
        return index.resolve().as_uri()
