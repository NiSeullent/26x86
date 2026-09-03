"""
Tahoe-inspired neumorphic theme helpers for 26x86 wxPython GUI.

Soft elevated/depressed surfaces, generous spacing, and light/dark adaptive
colours where wx supports them. Buttons on macOS use panel-based controls so
custom styling is not overridden by native NSButton rendering.
"""

from __future__ import annotations

import wx

from opencore_legacy_patcher.wx_gui import gui_support

# Spacing scale (SF-like rhythm)
SPACE_XS = 6
SPACE_SM = 10
SPACE_MD = 16
SPACE_LG = 20
SPACE_XL = 28

RADIUS = 12
CONTENT_WRAP = 520
WIZARD_MIN_SIZE = (860, 640)
DIALOG_MIN_WIDTH = 440


class Palette:
    """Colour tokens for one appearance mode (lazy wx.Colour resolution)."""

    def __init__(self, tokens: dict[str, str]) -> None:
        self._tokens = tokens
        self._cache: dict[str, wx.Colour] = {}

    def _colour(self, name: str) -> wx.Colour:
        if name not in self._cache:
            self._cache[name] = wx.Colour(self._tokens[name])
        return self._cache[name]

    @property
    def page_bg(self) -> wx.Colour:
        return self._colour("page_bg")

    @property
    def surface(self) -> wx.Colour:
        return self._colour("surface")

    @property
    def elevated(self) -> wx.Colour:
        return self._colour("elevated")

    @property
    def inset(self) -> wx.Colour:
        return self._colour("inset")

    @property
    def accent(self) -> wx.Colour:
        return self._colour("accent")

    @property
    def accent_soft(self) -> wx.Colour:
        return self._colour("accent_soft")

    @property
    def accent_text(self) -> wx.Colour:
        return self._colour("accent_text")

    @property
    def text_primary(self) -> wx.Colour:
        return self._colour("text_primary")

    @property
    def text_secondary(self) -> wx.Colour:
        return self._colour("text_secondary")

    @property
    def text_muted(self) -> wx.Colour:
        return self._colour("text_muted")

    @property
    def border_light(self) -> wx.Colour:
        return self._colour("border_light")

    @property
    def border_dark(self) -> wx.Colour:
        return self._colour("border_dark")

    @property
    def warning(self) -> wx.Colour:
        return self._colour("warning")

    @property
    def success(self) -> wx.Colour:
        return self._colour("success")

    @property
    def step_active(self) -> wx.Colour:
        return self._colour("step_active")

    @property
    def step_idle(self) -> wx.Colour:
        return self._colour("step_idle")


_LIGHT_TOKENS = {
    "page_bg": "#E3E8EF",
    "surface": "#EEF2F7",
    "elevated": "#F7F9FC",
    "inset": "#D5DCE6",
    "accent": "#0A84FF",
    "accent_soft": "#D9EBFF",
    "accent_text": "#FFFFFF",
    "text_primary": "#1D1D1F",
    "text_secondary": "#48484A",
    "text_muted": "#8E8E93",
    "border_light": "#FFFFFF",
    "border_dark": "#B8C2D0",
    "warning": "#C45C00",
    "success": "#248A3D",
    "step_active": "#D9EBFF",
    "step_idle": "#EEF2F7",
}

_DARK_TOKENS = {
    "page_bg": "#1C1C1E",
    "surface": "#2C2C2E",
    "elevated": "#3A3A3C",
    "inset": "#1A1A1C",
    "accent": "#0A84FF",
    "accent_soft": "#1B3A5C",
    "accent_text": "#FFFFFF",
    "text_primary": "#F5F5F7",
    "text_secondary": "#C7C7CC",
    "text_muted": "#8E8E93",
    "border_light": "#4A4A4E",
    "border_dark": "#121214",
    "warning": "#FF9F0A",
    "success": "#30D158",
    "step_active": "#1B3A5C",
    "step_idle": "#2C2C2E",
}

_palette: Palette | None = None


def is_dark_mode() -> bool:
    try:
        appearance = wx.SystemSettings.GetAppearance()
        return appearance.IsDark()
    except Exception:
        return False


def colors() -> Palette:
    global _palette
    if _palette is None:
        _palette = Palette(_DARK_TOKENS if is_dark_mode() else _LIGHT_TOKENS)
    return _palette


def refresh_palette() -> Palette:
    global _palette
    _palette = Palette(_DARK_TOKENS if is_dark_mode() else _LIGHT_TOKENS)
    return _palette


def font(size: int, weight=wx.FONTWEIGHT_NORMAL) -> wx.Font:
    return gui_support.font_factory(size, weight)


def font_title() -> wx.Font:
    return font(24, wx.FONTWEIGHT_BOLD)


def font_heading() -> wx.Font:
    return font(18, wx.FONTWEIGHT_BOLD)


def font_subheading() -> wx.Font:
    weight = getattr(wx, "FONTWEIGHT_SEMIBOLD", wx.FONTWEIGHT_BOLD)
    return font(14, weight)


def font_body() -> wx.Font:
    return font(12, wx.FONTWEIGHT_NORMAL)


def font_caption() -> wx.Font:
    return font(11, wx.FONTWEIGHT_NORMAL)


def font_button() -> wx.Font:
    weight = getattr(wx, "FONTWEIGHT_MEDIUM", wx.FONTWEIGHT_NORMAL)
    return font(13, weight)


def style_frame(frame: wx.Frame | wx.Dialog) -> None:
    c = colors()
    frame.SetBackgroundColour(c.page_bg)
    try:
        frame.SetMinSize(WIZARD_MIN_SIZE if isinstance(frame, wx.Frame) else (DIALOG_MIN_WIDTH, 280))
    except Exception:
        pass


def style_panel(panel: wx.Panel, variant: str = "surface") -> None:
    c = colors()
    mapping = {
        "page": c.page_bg,
        "surface": c.surface,
        "elevated": c.elevated,
        "inset": c.inset,
        "transparent": c.page_bg,
    }
    panel.SetBackgroundColour(mapping.get(variant, c.surface))


def style_static_heading(text: wx.StaticText) -> wx.StaticText:
    c = colors()
    text.SetFont(font_heading())
    text.SetForegroundColour(c.text_primary)
    return text


def style_static_body(text: wx.StaticText) -> wx.StaticText:
    c = colors()
    text.SetFont(font_body())
    text.SetForegroundColour(c.text_secondary)
    return text


def style_static_muted(text: wx.StaticText) -> wx.StaticText:
    c = colors()
    text.SetFont(font_caption())
    text.SetForegroundColour(c.text_muted)
    return text


def style_static_label(text: wx.StaticText, bold: bool = True) -> wx.StaticText:
    c = colors()
    text.SetFont(font(12, wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL))
    text.SetForegroundColour(c.text_primary if bold else c.text_secondary)
    return text


def wrap_static_text(text: wx.StaticText, width: int = CONTENT_WRAP) -> None:
    text.Wrap(width)


def style_status_bar(status_bar: wx.StatusBar) -> None:
    c = colors()
    status_bar.SetBackgroundColour(c.surface)
    status_bar.SetForegroundColour(c.text_secondary)


def style_choice(choice: wx.Choice) -> None:
    choice.SetFont(font_body())
    style_panel(choice, "elevated")


def style_gauge(gauge: wx.Gauge) -> None:
    gauge.SetBackgroundColour(colors().inset)


def apply_app_theme(app: wx.App) -> None:
    refresh_palette()
    c = colors()
    app.SetAppName(app.GetAppName())
    try:
        wx.SystemOptions.SetOption("mac.tab-focusable", 0)
    except Exception:
        pass
    # Global hint for child windows; individual frames still call style_frame.
    wx.ArtProvider.SetColour(wx.ART_BUTTON, wx.ART_OTHER, c.elevated)


class NeumoPanel(wx.Panel):
    """Panel with soft raised or inset border (neumorphic card)."""

    def __init__(
        self,
        parent: wx.Window,
        variant: str = "elevated",
        radius: int = RADIUS,
        border: int = 1,
    ) -> None:
        super().__init__(parent)
        self._variant = variant
        self._radius = radius
        self._border = border
        style_panel(self, variant)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, lambda e: self.Refresh())

    def _on_paint(self, event: wx.Event) -> None:
        dc = wx.PaintDC(self)
        rect = self.GetClientRect()
        c = colors()
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            event.Skip()
            return

        gc.SetBrush(wx.Brush(self.GetBackgroundColour()))
        if self._variant == "inset":
            pen_top = wx.Pen(c.border_dark, self._border)
            pen_bottom = wx.Pen(c.border_light, self._border)
        else:
            pen_top = wx.Pen(c.border_light, self._border)
            pen_bottom = wx.Pen(c.border_dark, self._border)

        path = gc.CreatePath()
        r = float(self._radius)
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        path.AddRoundedRectangle(x, y, w, h, r)
        gc.FillPath(path)

        gc.SetPen(pen_top)
        gc.StrokePath(path)
        event.Skip()


class NeumoButton(wx.Panel):
    """Soft raised button; works consistently on macOS unlike wx.Button."""

    VARIANT_PRIMARY = "primary"
    VARIANT_SECONDARY = "secondary"
    VARIANT_GHOST = "ghost"
    VARIANT_STEP = "step"

    def __init__(
        self,
        parent: wx.Window,
        label: str,
        *,
        variant: str = VARIANT_SECONDARY,
        size: tuple[int, int] = (-1, 40),
        min_width: int = 120,
    ) -> None:
        super().__init__(parent, size=size)
        self._label = label
        self._variant = variant
        self._hover = False
        self._pressed = False
        self._active = False
        self._handler = None
        self._default = False

        if size[0] > 0:
            self.SetMinSize(size)
        else:
            self.SetMinSize((min_width, size[1] if size[1] > 0 else 40))

        self._text = wx.StaticText(self, label=label)
        self._text.SetFont(font_button())
        self._sync_colours()

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_up)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def SetToolTip(self, tip: str) -> None:
        super().SetToolTip(tip)
        self._text.SetToolTip(tip)

    def SetActive(self, active: bool) -> None:
        self._active = active
        self._sync_colours()
        self.Refresh()

    def SetDefault(self, is_default: bool = True) -> None:
        self._default = is_default

    def Enable(self, enable: bool = True) -> None:
        super().Enable(enable)
        self._sync_colours()
        self.Refresh()

    def BindClick(self, handler) -> None:
        self._handler = handler

    def _on_size(self, event: wx.Event) -> None:
        self._layout_label()
        self.Refresh()
        event.Skip()

    def _layout_label(self) -> None:
        rect = self.GetClientRect()
        self._text.SetPosition(((rect.width - self._text.GetSize().width) // 2, (rect.height - self._text.GetSize().height) // 2))

    def _sync_colours(self) -> None:
        c = colors()
        if not self.IsEnabled():
            fg = c.text_muted
            bg = c.inset
        elif self._active or self._variant == self.VARIANT_PRIMARY:
            fg = c.accent_text if self._variant == self.VARIANT_PRIMARY else c.accent
            bg = c.accent if self._variant == self.VARIANT_PRIMARY else c.step_active
        elif self._variant == self.VARIANT_GHOST:
            fg = c.text_secondary
            bg = c.surface
        elif self._variant == self.VARIANT_STEP:
            fg = c.text_primary
            bg = c.step_active if self._active else c.step_idle
        else:
            fg = c.text_primary
            bg = c.elevated
        self.SetBackgroundColour(bg)
        self._text.SetForegroundColour(fg)

    def _on_paint(self, event: wx.Event) -> None:
        dc = wx.PaintDC(self)
        rect = self.GetClientRect()
        c = colors()
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            event.Skip()
            return

        bg = self.GetBackgroundColour()
        if self._pressed:
            bg = c.inset
        elif self._hover and self.IsEnabled():
            if self._variant == self.VARIANT_PRIMARY:
                bg = wx.Colour(
                    max(0, c.accent.Red() - 12),
                    max(0, c.accent.Green() - 12),
                    max(0, c.accent.Blue() - 12),
                )
            else:
                bg = c.accent_soft if not self._active else c.step_active

        gc.SetBrush(wx.Brush(bg))
        if self._pressed or self._variant == self.VARIANT_GHOST:
            pen = wx.Pen(c.border_dark, 1)
        else:
            pen = wx.Pen(c.border_light, 1)
        gc.SetPen(pen)

        path = gc.CreatePath()
        path.AddRoundedRectangle(rect.x + 0.5, rect.y + 0.5, rect.width - 1, rect.height - 1, float(RADIUS - 2))
        gc.FillPath(path)
        gc.StrokePath(path)

        if self._default and self.IsEnabled():
            gc.SetPen(wx.Pen(c.accent, 2))
            gc.StrokePath(path)

        self._layout_label()
        event.Skip()

    def _on_enter(self, event: wx.Event) -> None:
        self._hover = True
        self.Refresh()

    def _on_leave(self, event: wx.Event) -> None:
        self._hover = False
        self._pressed = False
        self.Refresh()

    def _on_down(self, event: wx.Event) -> None:
        if not self.IsEnabled():
            return
        self._pressed = True
        self.CaptureMouse()
        self.Refresh()

    def _on_up(self, event: wx.Event) -> None:
        if not self.IsEnabled():
            return
        if self._pressed:
            self._pressed = False
            if self.HasCapture():
                self.ReleaseMouse()
            if self.GetClientRect().Contains(event.GetPosition()) and self._handler:
                self._handler(event)
        self.Refresh()


def create_card(
    parent: wx.Window,
    variant: str = "elevated",
    border: int = SPACE_MD,
) -> tuple[NeumoPanel, wx.BoxSizer]:
    """Return a neumorphic card panel and its inner vertical sizer."""
    card = NeumoPanel(parent, variant=variant)
    inner = wx.BoxSizer(wx.VERTICAL)
    card.SetSizer(inner)
    return card, inner


def add_card_row(
    parent_sizer: wx.BoxSizer,
    parent: wx.Window,
    proportion: int = 0,
    flag: int = wx.EXPAND,
    border: int = SPACE_MD,
) -> tuple[NeumoPanel, wx.BoxSizer]:
    card, inner = create_card(parent)
    parent_sizer.Add(card, proportion, flag, border)
    return card, inner


def style_message_dialog(parent: wx.Window | None = None) -> None:
    refresh_palette()


def content_wrap_for(panel: wx.Window) -> int:
    w = panel.GetClientSize().width
    if w < 200:
        return CONTENT_WRAP
    return max(320, w - SPACE_XL * 2)
