"""
gui_main_menu.py: Generate GUI for main menu
"""

import wx
import wx.html2

import sys
import logging
import subprocess
import requests
import markdown2
import threading
import webbrowser
import shutil
import os
from pathlib import Path
from packaging import version

from .. import constants
from x86.gui.branding import resolve_gui_logo_path
from x86.gui import theme

from ..support import (
    global_settings,
    updates
)
from ..datasets import (
    os_data,
    css_data
)
from ..wx_gui import (
    gui_build,
    gui_macos_installer_download,
    gui_support,
    gui_help,
    gui_settings,
    gui_sys_patch_display,
    gui_test_info,
    gui_update,
    gui_oc_settings,
    gui_macos_configeration,
    gui_model_change,
)

class MainFrame(wx.Frame):
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        logging.info("Initializing Main Menu Frame")
        super(MainFrame, self).__init__(parent, title=title, size=(740, 820), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        theme.style_frame(self)
        self.SetMinSize((680, 640))
        gui_support.GenerateMenubar(self, global_constants).generate()

        self.constants: constants.Constants = global_constants
        self.title: str = title

        self.model_button: wx.Button = None
        self.build_button: wx.Button = None
        
        # FIX: Absicherung gegen Thread-Races & Verwaiste Fenster-Referenzen
        self.exiting_app: bool = False  
        self.active_gemini_frame: wx.Frame = None

        self.constants.update_stage = gui_support.AutoUpdateStages.INACTIVE

        self._generate_elements()

        self.Centre()
        self.Show()

        self._preflight_checks()

    def _generate_elements(self) -> None:
        """
        Generate UI elements for the main menu (sizer-based, Tahoe neumorphic).
        """
        root = wx.Panel(self)
        theme.style_panel(root, "page")
        outer = wx.BoxSizer(wx.VERTICAL)

        header_card, header_inner = theme.create_card(root, variant="elevated")
        header = wx.BoxSizer(wx.VERTICAL)

        logo_path = resolve_gui_logo_path(self.constants.icns_resource_path)
        if logo_path is not None:
            if logo_path.suffix.lower() == ".png":
                logo_bitmap = wx.Bitmap(str(logo_path), wx.BITMAP_TYPE_PNG)
            else:
                logo_bitmap = wx.Bitmap(str(logo_path), wx.BITMAP_TYPE_ICON)
            logo = wx.StaticBitmap(header_card, bitmap=logo_bitmap, size=(96, 96))
            header.Add(logo, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, theme.SPACE_SM)

        title_label = wx.StaticText(header_card, label=self.constants.patcher_name)
        title_label.SetFont(theme.font_title())
        title_label.SetForegroundColour(theme.colors().text_primary)
        header.Add(title_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        is_matteo = getattr(self.constants, "app_mode", "albert") == "matteo"
        display_version = self.constants.experimental_version if is_matteo else self.constants.patcher_version_label
        version_label = wx.StaticText(header_card, label=f"Version {display_version}")
        theme.style_static_muted(version_label)
        header.Add(version_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, theme.SPACE_XS)

        try:
            if self.constants.Experimental_Features:
                dev_label = wx.StaticText(header_card, label="Developer Mode is ON")
                dev_label.SetFont(theme.font_body())
                dev_label.SetForegroundColour(theme.colors().success)
                header.Add(dev_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, theme.SPACE_SM)
        except Exception as e:
            logging.error("Developer Mode status check failed: %s", e)

        model_label = self.constants.custom_model or self.constants.computer.real_model
        model_button = theme.NeumoButton(
            header_card,
            f"Model: {model_label}",
            variant=theme.NeumoButton.VARIANT_SECONDARY,
            size=(-1, 38),
            min_width=260,
        )
        model_button.SetToolTip("Edit the Target Model OpenCore will build for")
        model_button.BindClick(self.on_edit_model)
        header.Add(model_button, 0, wx.EXPAND | wx.TOP, theme.SPACE_MD)
        self.model_button = model_button

        header_inner.Add(header, 1, wx.EXPAND | wx.ALL, theme.SPACE_LG)
        outer.Add(header_card, 0, wx.EXPAND | wx.ALL, theme.SPACE_MD)

        menu_card, menu_inner = theme.create_card(root, variant="surface")
        grid = wx.FlexGridSizer(cols=2, hgap=theme.SPACE_MD, vgap=theme.SPACE_MD)
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        menu_buttons = {
            "OpenCore": {
                "function": self.on_oc_settings,
                "description": ["Settings to prepares provided drives to be", "able to boot unsupported macOSes."],
                "icon": str(self.constants.icns_resource_path / "OC-Build.icns"),
            },
            "Settings": {
                "function": self.on_settings,
                "description": ["App settings"],
                "icon": str(self.constants.icns_resource_path / "Settings.icns"),
            },
            "Create macOS Installer": {
                "function": self.on_create_macos_installer,
                "description": ["Download and flash a macOS", "Installer for your system."],
                "icon": str(self.constants.icns_resource_path / "OC-Installer.icns"),
            },
            "macOS Configuration": {
                "function": self.on_macos_config,
                "description": ["Settings, drivers and", "patches for your system."],
                "icon": str(self.constants.patch_icon_path),
            },
            "Help": {
                "function": self.on_help,
                "description": ["26x86 도움말", "및 리소스."],
                "icon": str(self.constants.icns_resource_path / "OC-Support.icns"),
            },
        }

        for button_name, button_function in menu_buttons.items():
            cell = wx.BoxSizer(wx.HORIZONTAL)
            if "icon" in button_function and Path(button_function["icon"]).exists():
                icon = wx.StaticBitmap(
                    menu_card,
                    bitmap=wx.Bitmap(button_function["icon"], wx.BITMAP_TYPE_ICON),
                    size=(56, 56),
                )
                cell.Add(icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, theme.SPACE_SM)

            text_col = wx.BoxSizer(wx.VERTICAL)
            button = theme.NeumoButton(
                menu_card,
                button_name,
                variant=theme.NeumoButton.VARIANT_SECONDARY,
                size=(-1, 34),
                min_width=180,
            )
            button.BindClick(lambda event, f=button_function["function"]: f(event))

            if "OpenCore" in button_name:
                self.build_button = button
                if not gui_support.CheckProperties(self.constants).host_can_build():
                    button.SetToolTip(
                        "Opens OpenCore settings.\n\n"
                        "Building and installing OpenCore is not supported on this host, so "
                        "\"Save OpenCore\" and \"Install OpenCore\" stay disabled inside. To unlock them, "
                        "enable \"Allow native models\" in these settings, or pick a real, supported Mac "
                        "as the target model.\n\n"
                        "For installing OpenCore on Hackintoshes, follow Dortania's guide here: "
                        "https://dortania.github.io/OpenCore-Install-Guide/"
                    )
                    logging.info("Host cannot build OpenCore: settings stay accessible, Save/Install stay disabled.")
                else:
                    button.SetToolTip("Opens OpenCore settings, where OpenCore can be built and installed")
                    logging.info("Building OpenCore is supported on this host.")

            text_col.Add(button, 0, wx.EXPAND)
            description_label = wx.StaticText(menu_card, label="\n".join(button_function["description"]))
            theme.style_static_muted(description_label)
            text_col.Add(description_label, 0, wx.TOP, theme.SPACE_XS)
            cell.Add(text_col, 1, wx.EXPAND)
            grid.Add(cell, 1, wx.EXPAND)

        menu_inner.Add(grid, 1, wx.EXPAND | wx.ALL, theme.SPACE_MD)
        outer.Add(menu_card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, theme.SPACE_MD)

        copy_label = wx.StaticText(root, label=self.constants.copyright_date)
        theme.style_static_muted(copy_label)
        outer.Add(copy_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, theme.SPACE_MD)

        root.SetSizer(outer)

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(root, 1, wx.EXPAND)
        self.SetSizer(frame_sizer)

    def on_return_to_mode_selector(self, event: wx.Event = None):
        try:
            self.Hide()
            from ..wx_gui import gui_mode_selector
            new_frame = gui_mode_selector.ModeSelectorFrame(parent=None, title=self.title, global_constants=self.constants, screen_location=self.GetPosition())
            app = wx.GetApp()
            if hasattr(app, 'frame'):
                app.frame = new_frame
                new_frame.Bind(wx.EVT_CLOSE, app.OnCloseFrame)
            wx.CallAfter(self.Destroy)
        except Exception as e:
            logging.error(f"Failed to return to mode selector: {e}")
            logging.exception("Stack Trace:") # <- Angreifern könnten davon ausnutzen, dass Benutzer nicht das exakte Fehler weißen, um ClickFix-Angriffe zu starten

    def _preflight_checks(self):
        try:
            if self.constants.computer.build_model is None:
                logging.info("No build model detected. Defaulting to current host hardware.")
                self.constants.computer.build_model = self.constants.computer.real_model
            
            real_model = str(self.constants.computer.real_model).strip()
            build_model = str(self.constants.computer.build_model).strip() if self.constants.computer.build_model else None
            
            print(f"DEBUG: Real: '{real_model}' | Build: '{build_model}'")

            if (
                build_model is not None and
                build_model != real_model and
                self.constants.host_is_hackintosh is False
            ):
                pop_up = wx.MessageDialog(
                    self,
                    f"We found you are currently booting OpenCore built for a different unit: {build_model}\n\nPlease Build and Install a new OpenCore config.",
                    "Unsupported Configuration Detected!",
                    style=wx.OK | wx.ICON_EXCLAMATION
                )
                pop_up.ShowModal()
                self.Hide()
                gui_build.BuildFrame(
                    self,
                    self.title,
                    self.constants,
                    self.GetPosition(),
                    install=True,
                )
                return

        except Exception as e:
            print(f"DEBUG: Preflight error: {e}")

        self.update_thread = threading.Thread(target=self._check_for_updates)
        self.update_thread.daemon = True
        self.update_thread.start()
        # Also tracked on constants (not just this frame) so PatcherApp.OnExit()
        # can join it at quit the same way it already does for unpack_thread/
        # analytics_thread - this frame instance itself may already be gone by
        # then (the app keeps destroying and recreating MainFrame as the user
        # navigates), but constants persists for the whole process lifetime.
        self.constants.update_thread = self.update_thread

        if "--update_installed" in sys.argv and self.constants.has_checked_updates is False and gui_support.CheckProperties(self.constants).host_can_build():
            self.constants.has_checked_updates = True
            pop_up = wx.MessageDialog(
                self,
                f"{self.constants.patcher_name} has been updated to the latest available version: {self.constants.patcher_version_label}\n\nWould you like to update OpenCore and your root volume patches?",
                "Update successful!",
                style=wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
            )
            pop_up.ShowModal()

            if pop_up.GetReturnCode() != wx.ID_YES:
                logging.info("Skipping OpenCore and root volume patch updates...")
                return

            logging.info("Updating OpenCore and root volume patches...")
            self.constants.update_stage = gui_support.AutoUpdateStages.CHECKING
            self.Hide()
            pos = self.GetPosition()
            gui_build.BuildFrame(
                parent=None,
                title=self.title,
                global_constants=self.constants,
                screen_location=pos,
                install=True
            )
            wx.CallAfter(self.Destroy)

    def _check_for_updates(self):
        if self.constants.has_checked_updates is True:
            logging.info("We have already checked for updates.")
            return
        self.constants.has_checked_updates = True
        
        update_dict = updates.CheckBinaryUpdates(self.constants).check_binary_updates()
        if not update_dict:
            return
    
        remote_version_str = update_dict["Version"]
        local_version_str = self.constants.patcher_version
    
        try:
            remote_v = version.parse(str(remote_version_str))
            local_v = version.parse(local_version_str)
    
            if remote_v <= local_v:
                logging.info(f"{self.constants.patcher_name} is up to date. (Local: {local_v} >= Remote: {remote_v})")
                return
    
        except version.InvalidVersion:
            logging.info("The version is invalid, you'll not receive any further updates.")
            if remote_version_str == local_version_str:
                return
    
        if getattr(self, 'exiting_app', False) or gui_support.is_app_exiting():
            return
        
        logging.info(f"Newer version detected: {remote_version_str}")
        
        url = "https://api.github.com/repos/NiSeullent/26x86/releases/latest"
        changelog = """## Unable to fetch changelog\n\nPlease check the Github page for more information."""
        # User-Agent auf Edge gesetzt statt einfach OpenCore-Legacy-Patcher-T2, um die API sicher zu laden und MitM-Angriffe zu vermeiden
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/152.0.4191.53/26x86"}, timeout=10).json()
            if "body" in response:
                changelog = response["body"].split("## Asset Information")[0]
        except Exception as e:
            logging.error(f"Failed to fetch changelog text: {e}")
            logging.error(f"Es hat fehlgeschlagen, den Changelog-Text anzuzeigen: {e}")

        if not getattr(self, 'exiting_app', False) and not gui_support.is_app_exiting():
            wx.CallAfter(self.on_update, update_dict["Link"], remote_version_str, update_dict["Github Link"], changelog)
        
    def on_update(self, oclp_url: str, oclp_version: str, oclp_github_url: str, changelog_text: str):
        if not self or gui_support.is_app_exiting():
            return

        ID_GITHUB = wx.NewIdRef() if hasattr(wx, "NewIdRef") else wx.NewId()
        ID_UPDATE = wx.NewIdRef() if hasattr(wx, "NewIdRef") else wx.NewId()

        html_markdown = markdown2.markdown(changelog_text, extras=["tables"])
        html_css = css_data.updater_css
        
        # Parent auf self gesetzt zur sauberen Speicherhierarchie
        frame = wx.Dialog(self, -1, title="", size=(650, 500))
        frame.SetMinSize((650, 500))
        frame.SetWindowStyle(wx.STAY_ON_TOP)
        panel = wx.Panel(frame)
        
        self.title_text = wx.StaticText(panel, label=f"A new version of {self.constants.patcher_name} is available!")
        self.description = wx.StaticText(panel, label=f"{self.constants.patcher_name} {oclp_version} is now available - You have {self.constants.patcher_version_label}. Would you like to update?")
        self.title_text.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        self.description.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        
        self.web_view = wx.html2.WebView.New(panel, style=wx.BORDER_SUNKEN)
        html_code = f'''
<html>
    <head>
        <style>
            {html_css}
        </style>
    </head>
    <body class="markdown-body">
        {html_markdown.replace("<a href=", "<a target='_blank' href=")}
    </body>
</html>
'''
        self.web_view.SetPage(html_code, "")
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_NEWWINDOW, self._onWebviewNav)
        self.web_view.EnableContextMenu(False)
        
        self.close_button = wx.Button(panel, label="Update Later")
        self.close_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(wx.ID_CANCEL))
        self.view_button = wx.Button(panel, ID_GITHUB, label="View on GitHub")
        self.view_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(ID_GITHUB))
        self.install_button = wx.Button(panel, label="Update Now")
        self.install_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(ID_UPDATE))
        self.install_button.SetDefault()

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(self.close_button, 0, wx.ALIGN_CENTRE | wx.RIGHT, 5)
        buttonsizer.Add(self.view_button, 0, wx.ALIGN_CENTRE | wx.LEFT|wx.RIGHT, 5)
        buttonsizer.Add(self.install_button, 0, wx.ALIGN_CENTRE | wx.LEFT, 5)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.title_text, 0, wx.ALIGN_CENTRE | wx.TOP, 20)
        sizer.Add(self.description, 0, wx.ALIGN_CENTRE | wx.BOTTOM, 20)
        sizer.Add(self.web_view, 1, wx.EXPAND | wx.LEFT|wx.RIGHT, 10)
        sizer.Add(buttonsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 20)
        panel.SetSizer(sizer)
        frame.Centre()

        result = frame.ShowModal()

        if result == ID_GITHUB:
            webbrowser.open(oclp_github_url)
        elif result == ID_UPDATE:
            gui_update.UpdateFrame(
                parent=self,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition(),
                url=oclp_url,
                version_label=oclp_version
            )

        frame.Destroy()

    def _onWebviewNav(self, event):
        url = event.GetURL()
        webbrowser.open(url)

    def on_show_test_info(self, event: wx.Event = None, initial_tab: int = 0):
        try:
            dialog = gui_test_info.TestExplanationDialog(self, self.constants, initial_tab=initial_tab)
            dialog.ShowModal()
            dialog.Destroy()
        except Exception as e:
            logging.error(f"Failed to open Test Explanation dialog: {e}")
            logging.exception("Stack Trace:")

    def on_build_and_install_standard(self, event: wx.Event = None):
        self.constants.build_profile = "standard"
        self.on_build_and_install(event)

    def on_build_opencore_menu(self, event: wx.Event = None):
        choices = [
            "🟢 Standard / Safe Build",
            "🧪 [LEVEL-B] Experimental GPU",
            "🧪 [LEVEL-C] Experimental Tahoe (Native SMBIOS)",
            "🧪 [LEVEL-C] Experimental Spoof T2 (MacBookPro16,1)",
            "🧪 [LEVEL-D] All-In-One Tahoe (Wi-Fi + Audio + GPU + T1)"
        ]
        dialog = wx.SingleChoiceDialog(
            self,
            "Select the OpenCore build profile you wish to generate:",
            "Build OpenCore",
            choices
        )
        
        if dialog.ShowModal() == wx.ID_OK:
            selection = dialog.GetSelection()
            if selection == 0:
                self.constants.build_profile = "standard"
            elif selection == 1:
                self.constants.build_profile = "test_b"
            elif selection == 2:
                self.constants.build_profile = "test_c"
            elif selection == 3:
                self.constants.build_profile = "test_c_spoofed"
            elif selection == 4:
                self.constants.build_profile = "test_d"
            # behebt eine Sicherheitslücke, die erlaubt Angreifern, selection zu manipulieren und beispielsweise zu behaupten, es wäre Option 5 ausgewählt, die erst gar nicht existiert, um die Anwendung zum Absturz zu bringen.
            else:
                logging.error("You haven't selected a valid testing OpenCore option.")
                logging.info("Please try again later.")
            
            self.on_build_and_install(event)
        
        dialog.Destroy()

    def on_build_and_install_testd(self, event: wx.Event = None):
        self.constants.build_profile = "test_d"
        self.on_build_and_install(event)

    def on_build_and_install(self, event: wx.Event = None):
        try:
            self.Hide()
            gui_build.BuildFrame(parent=None, title=self.title, global_constants=self.constants, screen_location=self.GetPosition())
            wx.CallAfter(self.Destroy)
        except Exception as e:
            logging.error(f"We failed to open up Build and Install OpenCore: {e}")
            logging.exception("Stack Trace:")

    def on_root_patches(self, event: wx.Event = None):
        try:
            self.Hide()
            gui_sys_patch_display.SysPatchDisplayFrame(parent=None, title=self.title, global_constants=self.constants, screen_location=self.GetPosition())
            wx.CallAfter(self.Destroy)
        except Exception as e:
            logging.error(f"We failed to open up Root Patches: {e}")
            logging.exception("Stack Trace:")
            return

    def on_macos_config(self, event: wx.Event = None):
        try:
            gui_macos_configeration.MacosConfigFrame(
                parent=self,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition()
            )
        except Exception as e:
            logging.error(f"We failed to open MacOS Configuration: {e}")
            logging.exception("Stack Trace:")
            return
    def on_edit_model(self, event: wx.Event = None):
        # behebt eine Sicherheitslücke, die erlaubt Angreifern, wenn Fehlern in on_edit_model gibt, die Anwendung zum Absturz zu bringen oder beliebiges Code auszuführen
        try:
            self.Disable()
            gui_model_change.ModelPickerFrame(
                parent=self,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition(),
            )
        except Exception as e:
            logging.error(f"We failed to call the function on_edit_model: {e}")
            logging.exception("Stack Trace:")

    def on_oc_settings(self, event: wx.Event = None):
        try:
            gui_oc_settings.OCSettingsFrame(
                parent=self,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition()
            )
        except Exception as e:
            logging.error(f"We failed to open OpenCore Settings: {e}")
            logging.exception("Stack Trace:")
            return

    def on_create_macos_installer(self, event: wx.Event = None):
        try:
            gui_macos_installer_download.macOSInstallerDownloadFrame(parent=self, title=self.title, global_constants=self.constants, screen_location=self.GetPosition())
        except Exception as e:
            logging.error(f"We failed to open up Download macOS: {e}")
            logging.exception("Stack Trace:")
            return # <- da fehlte das return-Funktion, also der App könnte trotzdem der fehlerhafte Code auszuführen, auch wenn es schlug fehl. Angreifern könnten davon ausnutzen, um die Anwendung zum Absturz zu bringen oder beliebiges Code auszuführen

    def on_settings(self, event: wx.Event = None):
        try:
            gui_settings.SettingsFrame(parent=self, title=self.title, global_constants=self.constants, screen_location=self.GetPosition())
        except Exception as e:
            logging.error(f"We failed to open up Settings: {e}")
            logging.exception("Stack Trace:")
            return # <- da fehlte das return-Funktion, also der App könnte trotzdem der fehlerhafte Code auszuführen, auch wenn es schlug fehl. Angreifern könnten davon ausnutzen, um die Anwendung zum Absturz zu bringen oder beliebiges Code auszuführen

    def on_help(self, event: wx.Event = None):
        try:
            gui_help.HelpFrame(parent=self, title=self.title, global_constants=self.constants, screen_location=self.GetPosition())
        except Exception as e:
            logging.error(f"We failed to open up Help: {e}")
            logging.exception("Stack Trace:")
            return # <- da fehlte das return-Funktion, also der App könnte trotzdem der fehlerhafte Code auszuführen, auch wenn es schlug fehl. Angreifern könnten davon ausnutzen, um die Anwendung zum Absturz zu bringen oder beliebiges Code auszuführen

