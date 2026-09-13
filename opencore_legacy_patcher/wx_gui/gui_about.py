"""
gui_about.py: About frame (26x86 branding)
"""

import wx
import logging
import webbrowser

from .. import constants

from ..wx_gui import gui_support


class AboutFrame(wx.Frame):

    def __init__(self, global_constants: constants.Constants) -> None:
        if wx.FindWindowByName("About"):
            return

        logging.info("26x86 정보 창 생성")
        super(AboutFrame, self).__init__(None, title="26x86 정보", size=(380, 380), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.constants: constants.Constants = global_constants
        self.SetName("About")
        self.Centre()

        self._generate_elements(self)

        self.Show()

    def _generate_elements(self, frame: wx.Frame) -> None:
        title = wx.StaticText(frame, label="26x86", pos=(-1, 12))
        title.SetFont(gui_support.font_factory(24, wx.FONTWEIGHT_BOLD))
        title.Centre(wx.HORIZONTAL)

        version = wx.StaticText(
            frame,
            label=f"버전 {self.constants.patcher_version}",
            pos=(-1, title.GetPosition()[1] + title.GetSize()[1] + 6),
        )
        version.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        version.Centre(wx.HORIZONTAL)

        description = [
            "오래된 Mac에서 Apple이 공식 지원하지 않는",
            "최신 macOS를 사용할 수 있도록 돕는 도구입니다.",
            "",
            "OpenCore Legacy Patcher T2 포크",
        ]
        spacer = 0
        y = version.GetPosition()[1] + version.GetSize()[1] + 10
        for line in description:
            desc = wx.StaticText(frame, label=line, pos=(-1, y + spacer))
            desc.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
            desc.Centre(wx.HORIZONTAL)
            spacer += 22

        icon_path = str(self.constants.app_icon_path)
        icon = wx.StaticBitmap(frame, bitmap=wx.Bitmap(icon_path, wx.BITMAP_TYPE_ICON), pos=(5, y + spacer + 8))
        icon.SetSize((72, 72))
        icon.Centre(wx.HORIZONTAL)

        docs_btn = wx.Button(frame, label="사용 설명서 열기", pos=(-1, icon.GetPosition()[1] + icon.GetSize()[1] + 16), size=(180, 32))
        docs_btn.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        docs_btn.Centre(wx.HORIZONTAL)
        docs_btn.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open(self.constants.guide_link))

        repo_btn = wx.Button(frame, label="GitHub 프로젝트", pos=(-1, docs_btn.GetPosition()[1] + docs_btn.GetSize()[1] + 8), size=(180, 32))
        repo_btn.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        repo_btn.Centre(wx.HORIZONTAL)
        repo_btn.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open(self.constants.repo_link))

        copy_label = wx.StaticText(frame, label=self.constants.copyright_date, pos=(-1, repo_btn.GetPosition()[1] + repo_btn.GetSize()[1] + 16))
        copy_label.SetFont(gui_support.font_factory(10, wx.FONTWEIGHT_NORMAL))
        copy_label.Centre(wx.HORIZONTAL)

        frame.SetSize((-1, copy_label.GetPosition()[1] + copy_label.GetSize()[1] + 24))
