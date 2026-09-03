"""
wizard_frame.py: 5단계 마법사 메인 프레임
"""

import wx
import logging
import threading
import webbrowser
from pathlib import Path

from opencore_legacy_patcher import constants
from opencore_legacy_patcher.datasets import smbios_data, os_data
from opencore_legacy_patcher.datasets.os_data import os_conversion
from opencore_legacy_patcher.sys_patch.patchsets import HardwarePatchsetDetection, HardwarePatchsetValidation
from opencore_legacy_patcher.wx_gui import gui_support
from x86.gui.branding import is_advanced_gui_enabled
from x86.manifest import BUNDLE_ID

from . import strings, errors
from .settings_panel import SimplifiedSettingsDialog


class WizardFrame(wx.Frame):
    """
    일반 사용자용 단계별 마법사 UI.
    고급 기능은 X86_ADVANCED=1 환경에서 gui_main_menu.MainFrame으로 전환합니다.
    """

    STEP_COUNT = 5

    MACOS_CHOICES = [
        ("macOS Ventura (13)", os_data.os_data.ventura),
        ("macOS Sonoma (14)", os_data.os_data.sonoma),
        ("macOS Sequoia (15)", os_data.os_data.sequoia),
        ("macOS Tahoe (26)", os_data.os_data.tahoe),
    ]

    def __init__(
        self,
        parent: wx.Frame,
        title: str,
        global_constants: constants.Constants,
        screen_location: tuple = None,
    ) -> None:
        logging.info("26x86 마법사 프레임 초기화 (%s)", BUNDLE_ID)
        super().__init__(
            parent,
            title=title,
            size=(820, 620),
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.MAXIMIZE_BOX),
        )
        self.constants = global_constants
        self.title = title
        self.current_step = 0
        self.build_completed = False
        self.selected_target_os = os_data.os_data.sequoia

        self._generate_menubar()
        self._build_layout()
        self._show_step(0)

        self.Centre()
        self.Show()
        self._preflight_checks()

    def _generate_menubar(self) -> None:
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        about_item = file_menu.Append(wx.ID_ABOUT, "&정보\tCtrl+I")
        file_menu.AppendSeparator()
        log_item = file_menu.Append(wx.ID_ANY, "로그 파일 &보기")
        file_menu.AppendSeparator()
        quit_item = file_menu.Append(wx.ID_EXIT, "종&료\tCtrl+Q")
        menubar.Append(file_menu, "파일")

        tools_menu = wx.Menu()
        settings_item = tools_menu.Append(wx.ID_PREFERENCES, "설&정…")
        if is_advanced_gui_enabled():
            advanced_item = tools_menu.Append(wx.ID_ANY, "고급 &모드…")
        else:
            advanced_item = None
        menubar.Append(tools_menu, "도구")

        help_menu = wx.Menu()
        docs_item = help_menu.Append(wx.ID_HELP, "사용 &설명서")
        menubar.Append(help_menu, "도움말")

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self._on_about, about_item)
        self.Bind(wx.EVT_MENU, self._on_reveal_log, log_item)
        self.Bind(wx.EVT_MENU, lambda e: gui_support.quit_app(), quit_item)
        self.Bind(wx.EVT_MENU, self._on_settings, settings_item)
        if advanced_item is not None:
            self.Bind(wx.EVT_MENU, self._on_advanced_mode, advanced_item)
        self.Bind(wx.EVT_MENU, self._on_help, docs_item)

    def _build_layout(self) -> None:
        root = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.Panel(root)
        header.SetBackgroundColour(wx.Colour(245, 247, 250))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        logo_path = str(self.constants.icns_resource_path / "OC-Patcher.icns")
        if Path(logo_path).exists():
            logo = wx.StaticBitmap(header, bitmap=wx.Bitmap(logo_path, wx.BITMAP_TYPE_ICON))
            logo.SetSize((48, 48))
            header_sizer.Add(logo, 0, wx.ALL, 10)

        title_col = wx.BoxSizer(wx.VERTICAL)
        app_title = wx.StaticText(header, label=strings.APP_NAME)
        app_title.SetFont(gui_support.font_factory(22, wx.FONTWEIGHT_BOLD))
        subtitle = wx.StaticText(header, label=BUNDLE_ID)
        subtitle.SetFont(gui_support.font_factory(11, wx.FONTWEIGHT_NORMAL))
        subtitle.SetForegroundColour(wx.Colour(90, 90, 90))
        tagline = wx.StaticText(header, label="오래된 Mac, 새 macOS")
        tagline.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        tagline.SetForegroundColour(wx.Colour(90, 90, 90))
        title_col.Add(app_title, 0, wx.TOP, 12)
        title_col.Add(subtitle, 0)
        title_col.Add(tagline, 0)
        header_sizer.Add(title_col, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 8)
        header.SetSizer(header_sizer)
        main_sizer.Add(header, 0, wx.EXPAND)

        body = wx.Panel(root)
        body_sizer = wx.BoxSizer(wx.HORIZONTAL)

        sidebar = wx.Panel(body, size=(220, -1))
        sidebar.SetBackgroundColour(wx.Colour(250, 250, 252))
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        self.step_buttons: list = []
        for i, step in enumerate(strings.STEPS):
            btn = wx.Button(sidebar, label=step["title"], size=(200, 44))
            btn.SetFont(gui_support.font_factory(11, wx.FONTWEIGHT_NORMAL))
            btn.SetToolTip(step["tooltip"])
            btn.Bind(wx.EVT_BUTTON, lambda e, idx=i: self._show_step(idx))
            sidebar_sizer.Add(btn, 0, wx.ALL, 8)
            self.step_buttons.append(btn)
        sidebar.SetSizer(sidebar_sizer)
        body_sizer.Add(sidebar, 0, wx.EXPAND | wx.ALL, 8)

        self.content_panel = wx.ScrolledWindow(body, style=wx.VSCROLL)
        self.content_panel.SetScrollRate(0, 16)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        body_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 8)
        body.SetSizer(body_sizer)
        main_sizer.Add(body, 1, wx.EXPAND)

        nav = wx.Panel(root)
        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.prev_btn = wx.Button(nav, label=strings.BTN_PREV, size=(120, 36))
        self.next_btn = wx.Button(nav, label=strings.BTN_NEXT, size=(120, 36))
        self.next_btn.SetDefault()
        self.prev_btn.Bind(wx.EVT_BUTTON, lambda e: self._show_step(max(0, self.current_step - 1)))
        self.next_btn.Bind(wx.EVT_BUTTON, lambda e: self._show_step(min(self.STEP_COUNT - 1, self.current_step + 1)))
        nav_sizer.AddStretchSpacer()
        nav_sizer.Add(self.prev_btn, 0, wx.ALL, 8)
        nav_sizer.Add(self.next_btn, 0, wx.ALL, 8)
        nav.SetSizer(nav_sizer)
        main_sizer.Add(nav, 0, wx.EXPAND)

        self.status_bar = self.CreateStatusBar(1)
        self.set_status(strings.STATUS_READY)

        root.SetSizer(main_sizer)

    def set_status(self, message: str) -> None:
        self.status_bar.SetStatusText(message)

    def _clear_content(self) -> None:
        self.content_sizer.Clear(True)

    def _add_heading(self, title: str, desc: str) -> None:
        h = wx.StaticText(self.content_panel, label=title)
        h.SetFont(gui_support.font_factory(18, wx.FONTWEIGHT_BOLD))
        self.content_sizer.Add(h, 0, wx.ALL, 12)
        d = wx.StaticText(self.content_panel, label=desc)
        d.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        d.Wrap(520)
        self.content_sizer.Add(d, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

    def _add_info_row(self, label: str, value: str) -> None:
        row = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(self.content_panel, label=f"{label}:")
        lbl.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_BOLD))
        lbl.SetMinSize((120, -1))
        val = wx.StaticText(self.content_panel, label=value or "—")
        val.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        row.Add(lbl, 0, wx.RIGHT, 8)
        row.Add(val, 1)
        self.content_sizer.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

    def _add_large_button(self, label: str, handler, tooltip: str = "") -> wx.Button:
        btn = wx.Button(self.content_panel, label=label, size=(280, 48))
        btn.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
        if tooltip:
            btn.SetToolTip(tooltip)
        btn.Bind(wx.EVT_BUTTON, handler)
        self.content_sizer.Add(btn, 0, wx.ALL, 12)
        return btn

    def _add_progress(self) -> wx.Gauge:
        gauge = wx.Gauge(self.content_panel, range=100, size=(400, 24))
        self.content_sizer.Add(gauge, 0, wx.ALL, 12)
        return gauge

    def _show_step(self, index: int) -> None:
        self.current_step = index
        self._clear_content()

        builders = [
            self._build_step_detect,
            self._build_step_macos,
            self._build_step_build,
            self._build_step_install,
            self._build_step_root_patch,
        ]
        builders[index]()

        self.content_panel.Layout()
        self.content_panel.FitInside()

        for i, btn in enumerate(self.step_buttons):
            if i == index:
                btn.SetBackgroundColour(wx.Colour(220, 235, 255))
            else:
                btn.SetBackgroundColour(wx.NullColour)

        self.prev_btn.Enable(index > 0)
        self.next_btn.Enable(index < self.STEP_COUNT - 1)
        self.set_status(strings.STEPS[index]["title"])

    def _model_marketing_name(self, model: str) -> str:
        data = smbios_data.smbios_dictionary.get(model, {})
        return data.get("Marketing Name", model)

    def _build_step_detect(self) -> None:
        self._add_heading(strings.STEP_DETECT_HEADING, strings.STEP_DETECT_DESC)
        model = self.constants.custom_model or self.constants.computer.real_model
        self._add_info_row(strings.STEP_DETECT_MODEL_LABEL, model)
        self._add_info_row(strings.STEP_DETECT_NAME_LABEL, self._model_marketing_name(model))
        cpu_name = getattr(self.constants.computer.cpu, "name", None) if self.constants.computer.cpu else None
        self._add_info_row(strings.STEP_DETECT_CPU_LABEL, cpu_name or "확인됨")
        self._add_info_row(
            strings.STEP_DETECT_OS_LABEL,
            f"{self.constants.detected_os_version} ({self.constants.detected_os_build})",
        )
        self._add_large_button(strings.STEP_DETECT_BUTTON, lambda e: self._refresh_detection(), "Mac 정보를 다시 읽습니다.")
        self._add_large_button(strings.STEP_DETECT_CHANGE_MODEL, self._on_change_model, "다른 Mac 모델용으로 EFI를 만들 때 사용합니다.")

    def _build_step_macos(self) -> None:
        self._add_heading(strings.STEP_MACOS_HEADING, strings.STEP_MACOS_DESC)
        choices = [label for label, _ in self.MACOS_CHOICES]
        self.macos_choice = wx.Choice(self.content_panel, choices=choices, size=(320, -1))
        self.macos_choice.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        default_idx = 2
        for i, (_, kernel) in enumerate(self.MACOS_CHOICES):
            if kernel == self.constants.detected_os:
                default_idx = i
        self.macos_choice.SetSelection(default_idx)
        self.macos_choice.Bind(wx.EVT_CHOICE, self._on_macos_selected)
        self.content_sizer.Add(self.macos_choice, 0, wx.ALL, 12)

        current = os_conversion.convert_kernel_to_marketing_name(self.constants.detected_os)
        self._add_info_row(strings.STEP_MACOS_CURRENT, current)

        model = self.constants.custom_model or self.constants.computer.real_model
        max_os = smbios_data.smbios_dictionary.get(model, {}).get("Max OS Supported")
        if max_os is not None:
            native = os_conversion.convert_kernel_to_marketing_name(max_os)
            self._add_info_row(strings.STEP_MACOS_RECOMMENDED, f"Apple 공식 지원: {native} → 26x86로 더 높은 버전 가능")

    def _build_step_build(self) -> None:
        self._add_heading(strings.STEP_BUILD_HEADING, strings.STEP_BUILD_DESC)
        model = self.constants.custom_model or self.constants.computer.real_model
        target_label = "macOS Sequoia (15)"
        if hasattr(self, "macos_choice") and self.macos_choice:
            target_label = self.MACOS_CHOICES[self.macos_choice.GetSelection()][0]
        self._add_info_row("대상 Mac", f"{self._model_marketing_name(model)} ({model})")
        self._add_info_row("대상 macOS", target_label)
        self.build_status = wx.StaticText(self.content_panel, label="")
        self.build_status.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        self.content_sizer.Add(self.build_status, 0, wx.ALL, 8)
        self.build_gauge = self._add_progress()
        self.build_gauge.Hide()
        self._add_large_button(strings.STEP_BUILD_BUTTON, self._on_start_build, strings.STEPS[2]["tooltip"])

    def _build_step_install(self) -> None:
        self._add_heading(strings.STEP_INSTALL_HEADING, strings.STEP_INSTALL_DESC)
        if not self.build_completed and not gui_support.CheckProperties(self.constants).host_can_build():
            warn = wx.StaticText(self.content_panel, label=strings.STEP_INSTALL_NEED_BUILD)
            warn.SetForegroundColour(wx.Colour(180, 80, 0))
            warn.Wrap(520)
            self.content_sizer.Add(warn, 0, wx.ALL, 12)
        self._add_large_button(strings.STEP_INSTALL_BUTTON, self._on_start_install, strings.STEPS[3]["tooltip"])

    def _build_step_root_patch(self) -> None:
        self._add_heading(strings.STEP_ROOT_HEADING, strings.STEP_ROOT_DESC)
        self.root_status_label = wx.StaticText(self.content_panel, label="패치 정보를 불러오는 중…")
        self.root_status_label.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        self.root_status_label.Wrap(520)
        self.content_sizer.Add(self.root_status_label, 0, wx.ALL, 12)
        self.root_gauge = self._add_progress()
        self.root_pulse = gui_support.GaugePulseCallback(self.constants, self.root_gauge)
        self.root_pulse.start_pulse()
        threading.Thread(target=self._fetch_patch_status, daemon=True).start()
        self._add_large_button(strings.STEP_ROOT_APPLY, self._on_root_patch, strings.STEPS[4]["tooltip"])
        self._add_large_button(strings.STEP_ROOT_REVERT, self._on_root_unpatch, "적용한 루트 패치를 되돌립니다.")

    def _refresh_detection(self) -> None:
        self.set_status("Mac 정보를 확인하는 중…")
        try:
            from opencore_legacy_patcher.detections import device_probe
            self.constants.computer = device_probe.Computer.probe()
            self._show_step(0)
            self.set_status("Mac 정보 확인 완료")
        except Exception as exc:
            errors.show_error_dialog(self, exc)
            self.set_status(strings.STATUS_READY)

    def _on_change_model(self, event: wx.Event = None) -> None:
        try:
            from opencore_legacy_patcher.wx_gui import gui_model_change

            self.Disable()
            gui_model_change.ModelPickerFrame(parent=self, title=self.title, global_constants=self.constants)
            self.Enable()
            self._show_step(0)
        except Exception as exc:
            self.Enable()
            errors.show_error_dialog(self, exc)

    def _on_macos_selected(self, event: wx.Event = None) -> None:
        idx = self.macos_choice.GetSelection()
        if idx >= 0:
            self.selected_target_os = self.MACOS_CHOICES[idx][1]
            self.set_status(f"대상 macOS: {self.MACOS_CHOICES[idx][0]}")

    def _on_start_build(self, event: wx.Event = None) -> None:
        if not gui_support.CheckProperties(self.constants).host_can_build():
            wx.MessageBox(
                "이 Mac에서는 EFI를 만들 수 없습니다.\n다른 지원 Mac에서 실행하거나, 고급 모드에서 설정을 확인해 주세요.",
                "안내",
                wx.OK | wx.ICON_INFORMATION,
            )
            return
        self.set_status(strings.STEP_BUILD_RUNNING)
        self.build_gauge.Show()
        self.build_status.SetLabel(strings.STEP_BUILD_RUNNING)
        self.Hide()
        try:
            from opencore_legacy_patcher.wx_gui import gui_build

            gui_build.BuildFrame(
                parent=None,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition(),
            )
            self.build_completed = True
            self.set_status(strings.STEP_BUILD_DONE)
        except Exception as exc:
            errors.show_error_dialog(self, exc)
            self.set_status(strings.STATUS_READY)
        finally:
            self.Show()
            self._show_step(2)

    def _on_start_install(self, event: wx.Event = None) -> None:
        self.set_status("EFI 설치 화면을 여는 중…")
        self.Hide()
        try:
            from opencore_legacy_patcher.wx_gui import gui_install_oc

            gui_install_oc.InstallOCFrame(
                parent=None,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition(),
            )
        except Exception as exc:
            errors.show_error_dialog(self, exc)
        finally:
            self.Show()
            self.set_status(strings.STATUS_READY)

    def _fetch_patch_status(self) -> None:
        try:
            patches = HardwarePatchsetDetection(constants=self.constants, validation=True).device_properties
            lines = []
            active = [
                p.split(": ", 1)[1]
                for p in patches
                if patches[p] is True and not p.startswith("Validation") and not p.startswith("Settings")
            ]
            if self.constants.computer.oclp_sys_version:
                lines.append(f"{strings.STEP_ROOT_LAST}: {self.constants.computer.oclp_sys_version}")
            if active:
                lines.append("적용 가능한 패치:")
                lines.extend(f"  • {p}" for p in active[:8])
                if len(active) > 8:
                    lines.append(f"  … 외 {len(active) - 8}개")
            else:
                lines.append(strings.STEP_ROOT_NONE)
            if patches.get(HardwarePatchsetValidation.PATCHING_NOT_POSSIBLE):
                lines.append("\n현재 상태에서는 패치를 적용할 수 없습니다 (SIP 등 확인 필요).")
            text = "\n".join(lines)
        except Exception as exc:
            text = errors.user_message(exc)

        wx.CallAfter(self._update_root_status, text)

    def _update_root_status(self, text: str) -> None:
        if hasattr(self, "root_pulse"):
            self.root_pulse.stop_pulse()
        if hasattr(self, "root_gauge"):
            self.root_gauge.Hide()
        if hasattr(self, "root_status_label"):
            self.root_status_label.SetLabel(text)

    def _on_root_patch(self, event: wx.Event = None) -> None:
        self.Hide()
        try:
            from opencore_legacy_patcher.wx_gui import gui_sys_patch_display

            gui_sys_patch_display.SysPatchDisplayFrame(
                parent=None,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition(),
            )
        except Exception as exc:
            errors.show_error_dialog(self, exc)
        finally:
            self.Show()

    def _on_root_unpatch(self, event: wx.Event = None) -> None:
        self.Hide()
        try:
            from opencore_legacy_patcher.wx_gui import gui_sys_patch_start
            frame = gui_sys_patch_start.SysPatchStartFrame(
                None,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition(),
                patches=HardwarePatchsetDetection(constants=self.constants).device_properties,
            )
            frame.revert_root_patching()
        except Exception as exc:
            errors.show_error_dialog(self, exc)
        finally:
            self.Show()

    def _on_about(self, event: wx.Event = None) -> None:
        from .about import show_about
        show_about(self.constants)

    def _on_reveal_log(self, event: wx.Event = None) -> None:
        import subprocess
        subprocess.run(["/usr/bin/open", "--reveal", self.constants.log_filepath])

    def _on_settings(self, event: wx.Event = None) -> None:
        dlg = SimplifiedSettingsDialog(self, self.constants)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_advanced_mode(self, event: wx.Event = None) -> None:
        if not is_advanced_gui_enabled():
            wx.MessageBox(
                strings.ERR_ADVANCED_DISABLED,
                "고급 모드",
                wx.OK | wx.ICON_INFORMATION,
            )
            return
        confirm = wx.MessageDialog(
            self,
            "고급 모드는 26x86의 전체 메뉴를 표시합니다.\n"
            "일반 사용자라면 마법사 모드를 계속 사용하는 것을 권장합니다.\n\n"
            "고급 모드로 전환할까요?",
            "고급 모드",
            wx.YES_NO | wx.ICON_QUESTION,
        )
        if confirm.ShowModal() != wx.ID_YES:
            confirm.Destroy()
            return
        confirm.Destroy()
        self.Hide()
        from opencore_legacy_patcher.wx_gui import gui_main_menu

        gui_main_menu.MainFrame(
            None,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.GetPosition(),
        )
        wx.CallAfter(self.Destroy)

    def _on_help(self, event: wx.Event = None) -> None:
        try:
            from opencore_legacy_patcher.wx_gui import gui_help

            gui_help.HelpFrame(
                parent=self,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition(),
            )
        except Exception:
            webbrowser.open(self.constants.guide_link)

    def _preflight_checks(self) -> None:
        try:
            if self.constants.computer.build_model is None:
                self.constants.computer.build_model = self.constants.computer.real_model
        except Exception as exc:
            logging.warning("사전 검사 중 오류: %s", exc)
