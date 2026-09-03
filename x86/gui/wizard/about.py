"""
about.py: 26x86 branded About dialog for the wizard UI.
"""

import wx
import logging
import webbrowser

from opencore_legacy_patcher import constants
from x86.gui.branding import about_description_lines, about_title, resolve_gui_logo_path
from x86.gui import theme
from x86.manifest import APP_NAME, BUNDLE_ID


def show_about(global_constants: constants.Constants) -> None:
    if wx.FindWindowByName("About"):
        return

    logging.info("26x86 정보 창 생성 (%s)", BUNDLE_ID)
    frame = wx.Frame(
        None,
        title=about_title(),
        size=(420, 460),
        style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX),
        name="About",
    )
    theme.style_frame(frame)
    frame.SetMinSize((400, 400))
    frame.constants = global_constants
    frame.Centre()

    root = wx.Panel(frame)
    theme.style_panel(root, "page")
    outer = wx.BoxSizer(wx.VERTICAL)

    card, inner = theme.create_card(root, variant="elevated")
    content = wx.BoxSizer(wx.VERTICAL)

    title = wx.StaticText(card, label=APP_NAME)
    title.SetFont(theme.font_title())
    title.SetForegroundColour(theme.colors().text_primary)
    content.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, theme.SPACE_SM)

    version = wx.StaticText(card, label=f"버전 {global_constants.patcher_version}")
    theme.style_static_body(version)
    content.Add(version, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, theme.SPACE_MD)

    for line in about_description_lines():
        desc = wx.StaticText(card, label=line)
        theme.style_static_body(desc)
        content.Add(desc, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)

    logo_path = resolve_gui_logo_path(global_constants.icns_resource_path)
    if logo_path is not None:
        if logo_path.suffix.lower() == ".png":
            logo_bitmap = wx.Bitmap(str(logo_path), wx.BITMAP_TYPE_PNG)
        else:
            logo_bitmap = wx.Bitmap(str(logo_path), wx.BITMAP_TYPE_ICON)
        icon = wx.StaticBitmap(card, bitmap=logo_bitmap, size=(72, 72))
        content.Add(icon, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, theme.SPACE_MD)

    docs_btn = theme.NeumoButton(
        card,
        "사용 설명서 열기",
        variant=theme.NeumoButton.VARIANT_SECONDARY,
        size=(-1, 38),
        min_width=200,
    )
    docs_btn.BindClick(lambda e: webbrowser.open(global_constants.guide_link))
    content.Add(docs_btn, 0, wx.EXPAND | wx.TOP, theme.SPACE_SM)

    repo_btn = theme.NeumoButton(
        card,
        "GitHub 프로젝트",
        variant=theme.NeumoButton.VARIANT_GHOST,
        size=(-1, 38),
        min_width=200,
    )
    repo_btn.BindClick(lambda e: webbrowser.open(global_constants.repo_link))
    content.Add(repo_btn, 0, wx.EXPAND | wx.TOP, theme.SPACE_SM)

    copy_label = wx.StaticText(card, label=global_constants.copyright_date)
    theme.style_static_muted(copy_label)
    content.Add(copy_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, theme.SPACE_LG)

    inner.Add(content, 1, wx.EXPAND | wx.ALL, theme.SPACE_LG)
    outer.Add(card, 1, wx.EXPAND | wx.ALL, theme.SPACE_MD)
    root.SetSizer(outer)

    frame_sizer = wx.BoxSizer(wx.VERTICAL)
    frame_sizer.Add(root, 1, wx.EXPAND)
    frame.SetSizer(frame_sizer)
    frame.Show()
