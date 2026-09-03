"""
about.py: 26x86 branded About dialog for the wizard UI.
"""

import wx
import logging
import webbrowser

from opencore_legacy_patcher import constants
from opencore_legacy_patcher.wx_gui import gui_support
from x86.gui.branding import about_description_lines, about_title
from x86.manifest import APP_NAME, BUNDLE_ID


def show_about(global_constants: constants.Constants) -> None:
    if wx.FindWindowByName("About"):
        return

    logging.info("26x86 정보 창 생성 (%s)", BUNDLE_ID)
    frame = wx.Frame(
        None,
        title=about_title(),
        size=(400, 400),
        style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX),
        name="About",
    )
    frame.constants = global_constants
    frame.Centre()

    title = wx.StaticText(frame, label=APP_NAME, pos=(-1, 12))
    title.SetFont(gui_support.font_factory(24, wx.FONTWEIGHT_BOLD))
    title.Centre(wx.HORIZONTAL)

    version = wx.StaticText(
        frame,
        label=f"버전 {global_constants.patcher_version}",
        pos=(-1, title.GetPosition()[1] + title.GetSize()[1] + 6),
    )
    version.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
    version.Centre(wx.HORIZONTAL)

    spacer = 0
    y = version.GetPosition()[1] + version.GetSize()[1] + 10
    for line in about_description_lines():
        desc = wx.StaticText(frame, label=line, pos=(-1, y + spacer))
        desc.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
        desc.Centre(wx.HORIZONTAL)
        spacer += 22

    icon_path = str(global_constants.app_icon_path)
    icon = wx.StaticBitmap(
        frame,
        bitmap=wx.Bitmap(icon_path, wx.BITMAP_TYPE_ICON),
        pos=(5, y + spacer + 8),
    )
    icon.SetSize((72, 72))
    icon.Centre(wx.HORIZONTAL)

    docs_btn = wx.Button(
        frame,
        label="사용 설명서 열기",
        pos=(-1, icon.GetPosition()[1] + icon.GetSize()[1] + 16),
        size=(180, 32),
    )
    docs_btn.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
    docs_btn.Centre(wx.HORIZONTAL)
    docs_btn.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open(global_constants.guide_link))

    repo_btn = wx.Button(
        frame,
        label="GitHub 프로젝트",
        pos=(-1, docs_btn.GetPosition()[1] + docs_btn.GetSize()[1] + 8),
        size=(180, 32),
    )
    repo_btn.SetFont(gui_support.font_factory(12, wx.FONTWEIGHT_NORMAL))
    repo_btn.Centre(wx.HORIZONTAL)
    repo_btn.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open(global_constants.repo_link))

    copy_label = wx.StaticText(
        frame,
        label=global_constants.copyright_date,
        pos=(-1, repo_btn.GetPosition()[1] + repo_btn.GetSize()[1] + 16),
    )
    copy_label.SetFont(gui_support.font_factory(10, wx.FONTWEIGHT_NORMAL))
    copy_label.Centre(wx.HORIZONTAL)

    frame.SetSize((-1, copy_label.GetPosition()[1] + copy_label.GetSize()[1] + 24))
    frame.Show()
