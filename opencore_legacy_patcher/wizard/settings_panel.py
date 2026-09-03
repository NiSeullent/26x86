"""
settings_panel.py: 간소화된 설정 대화상자
"""

import wx
import logging

from .. import constants
from ..wx_gui import gui_support
from ..support import global_settings, analytics_handler
from . import strings


class SimplifiedSettingsDialog(wx.Dialog):
    """
    일반 사용자용 간소화 설정 패널.
    고급 설정은 기존 SettingsFrame(고급 모드)에서 접근합니다.
    """

    def __init__(self, parent: wx.Frame, global_constants: constants.Constants) -> None:
        super().__init__(parent, title=strings.SETTINGS_TITLE, size=(420, 280))
        self.constants = global_constants
        self._build_ui()
        self.Centre()

    def _build_ui(self) -> None:
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        heading = wx.StaticText(panel, label=strings.SETTINGS_GENERAL)
        heading.SetFont(gui_support.font_factory(14, wx.FONTWEIGHT_BOLD))
        sizer.Add(heading, 0, wx.ALL, 12)

        gs = global_settings.GlobalEnviromentSettings()
        analytics_default = gs.read_property("EnableCrashAndAnalyticsReporting")
        if analytics_default is None:
            analytics_default = True

        self.check_analytics = wx.CheckBox(panel, label=strings.SETTINGS_ANALYTICS)
        self.check_analytics.SetValue(bool(analytics_default))
        self.check_analytics.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        if analytics_handler.ANALYTICS_SERVER or analytics_handler.SITE_KEY is not None:
            sizer.Add(self.check_analytics, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        note = wx.StaticText(
            panel,
            label="고급 OpenCore·개발자 설정은 메뉴의 「고급 모드」에서 변경할 수 있습니다.",
        )
        note.SetFont(gui_support.font_factory(10, wx.FONTWEIGHT_NORMAL))
        note.Wrap(380)
        note.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(note, 0, wx.ALL, 12)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cancel_btn = wx.Button(panel, label=strings.SETTINGS_CANCEL)
        save_btn = wx.Button(panel, label=strings.SETTINGS_SAVE)
        save_btn.SetDefault()
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        save_btn.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(cancel_btn, 0, wx.RIGHT, 8)
        btn_sizer.Add(save_btn, 0)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 12)

        panel.SetSizer(sizer)

    def _on_save(self, event: wx.Event = None) -> None:
        try:
            gs = global_settings.GlobalEnviromentSettings()
            if hasattr(self, "check_analytics"):
                gs.write_property(
                    "EnableCrashAndAnalyticsReporting",
                    self.check_analytics.GetValue(),
                )
            self.EndModal(wx.ID_OK)
        except Exception as exc:
            logging.error("설정 저장 실패: %s", exc)
            wx.MessageBox(
                "설정을 저장하지 못했습니다.",
                "오류",
                wx.OK | wx.ICON_ERROR,
            )
