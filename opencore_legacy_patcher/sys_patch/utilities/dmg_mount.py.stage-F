"""
dmg_mount.py: PatcherSupportPkg DMG Mounting. Handles Universal-Binaries and DortaniaInternalResources DMGs.

New code should use ``x86.patch.PayloadManager`` for explicit mount/unmount;
this module is wrapped by PayloadManager and kept for backward compatibility.
"""

import logging
import subprocess
import shutil
import applescript
import sys
from pathlib import Path
from ... import constants
from ...support import subprocess_wrapper

class PatcherSupportPkgMount:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants
        self.icon_path = str(self.constants.app_icon_path).replace("/", ":")[1:]

    def _request_admin_password(self) -> str:
        """Prompt for the local administrator password via a plain dialog.

        Deliberately NOT routed through "do shell script ... with administrator
        privileges": that mechanism runs the elevated command via
        /usr/libexec/security_authtrampoline, a process detached from the
        current login/Aqua session. hdiutil's own internal authentication
        (DIHelperAgentMaster) appears to depend on that session being present,
        so a hdiutil invocation elevated via the trampoline can fail with
        "hdiutil: attach failed - Authentication error" even though the same
        command run under sudo from a session-bound process succeeds. A plain
        "display dialog" only needs a WindowServer session to render, not the
        trampoline's separate authorization session, so we use it purely to
        collect the password and feed it to sudo ourselves.
        """
        try:
            return applescript.AppleScript(
                f'set theResult to display dialog "26x86 requires administrator access to mount patch resources." default answer "" with hidden answer with title "26x86" with icon file "{self.icon_path}"\nreturn the text returned of theResult'
            ).run()
        except Exception:
            return ""

    def _run_hdiutil(self, dmg_path: Path, mount_point: Path, shadow_path: Path = None, password: str = None, retry_on_auth_error: bool = False) -> subprocess.CompletedProcess:
        """Helper to standardize hdiutil execution using -stdinpass, with elevation on failure"""
        return subprocess_wrapper.mount_dmg(
            dmg_path, mount_point, shadow_path=shadow_path, password=password,
            admin_password_prompt=self._request_admin_password,
            retry_on_auth_error=retry_on_auth_error
        )

    def _mount_universal_binaries_dmg(self) -> bool:
        """Mount PatcherSupportPkg's Universal-Binaries.dmg"""
        dmg_path = Path(self.constants.payload_local_binaries_root_path_dmg)
        if not dmg_path.exists():
            logging.error("- PatcherSupportPkg resources missing, Patcher likely corrupted!!!")
            logging.exception("Stack Trace:")
            return False

        output = self._run_hdiutil(
            dmg_path,
            Path(self.constants.payload_path / "Universal-Binaries"),
            shadow_path=Path(self.constants.payload_path / "Universal-Binaries_overlay"),
            password="password",
            # Fixed, known-correct password: "Authentication error" here can only mean
            # the privilege gate/quarantine issue, never a wrong password (see mount_dmg)
            retry_on_auth_error=True
        )

        if output.returncode != 0:
            logging.info("- Failed to mount Universal-Binaries.dmg")
            subprocess_wrapper.log(output)
            return False

        logging.info("- Mounted Universal-Binaries.dmg")
        return True

    def _mount_26x86_internal_resources_dmg(self) -> bool:
        """Mount PatcherSupportPkg's DortaniaInternalResources.dmg"""
        if not Path(self.constants.overlay_psp_path_dmg).exists() or \
           not Path("~/.26x86_developer").expanduser().exists() or \
           self.constants.cli_mode is True:
            return True

        logging.info("- Found 26x86 internal resources, mounting...")

        for i in range(3):
            key = self._request_decryption_key(i)
            output = self._run_hdiutil(
                Path(self.constants.overlay_psp_path_dmg),
                Path(self.constants.payload_path / "DortaniaInternal"),
                password=key
            )

            if output.returncode != 0:
                logging.info("- Failed to mount DortaniaInternal resources")
                subprocess_wrapper.log(output)
                if "Authentication error" not in output.stdout.decode():
                    self._display_authentication_error()
                if i == 2:
                    self._display_too_many_attempts()
                    sys.exit(3)
                continue
            break

        logging.info("- Mounted 26x86 internal resources")
        return self._merge_26x86_internal_resources()

    def _merge_26x86_internal_resources(self) -> bool:
        """Merge DortaniaInternal resources with Universal-Binaries"""
        result = subprocess.run(
            ["/usr/bin/ditto", str(self.constants.payload_path / "DortaniaInternal"), str(self.constants.payload_path / "Universal-Binaries")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        return result.returncode == 0

    def _request_decryption_key(self, attempt: int) -> str:
        if attempt == 0 and Path("~/.26x86_developer_key").expanduser().exists():
            return Path("~/.26x86_developer_key").expanduser().read_text().strip()

        msg = "Welcome to the 26x86 internal program, please provide the decryption key." if attempt == 0 else f"Decryption failed. {2 - attempt} attempts remaining."
        try:
            return applescript.AppleScript(
                f'set theResult to display dialog "{msg}" default answer "" with hidden answer with title "26x86" with icon file "{self.icon_path}"\nreturn the text returned of theResult'
            ).run()
        except Exception:
            return ""

    def _display_authentication_error(self) -> None:
        applescript.AppleScript(f'display dialog "Failed to mount 26x86 internal resources, please file an internal radar." with title "26x86" with icon file "{self.icon_path}"').run()

    def _display_too_many_attempts(self) -> None:
        applescript.AppleScript(f'display dialog "Failed to mount 26x86 internal resources, too many incorrect passwords." with title "26x86" with icon file "{self.icon_path}"').run()

    def _merge_tahoe_yellow_screen_overlay(self) -> None:
        """Ditto PatcherSupportPkg 12.5-25+ overlay into the mounted Universal-Binaries tree."""
        # Track F: prefer psp_overlay (MC integrates this .stage-F file).
        from x86.graphics.skylight_lut import renderbox_overlay_copy_pairs
        from x86.graphics.psp_overlay import (
            format_tahoe_psp_overlay_missing_message,
            tahoe_psp_version_copy_pairs,
        )

        dest = Path(self.constants.payload_local_binaries_root_path)
        if not dest.exists():
            return
        pairs = tahoe_psp_version_copy_pairs(dest)
        pairs.extend(renderbox_overlay_copy_pairs(dest))
        if not pairs:
            message = format_tahoe_psp_overlay_missing_message()
            logging.warning(
                "yellow_screen_mitigations: no Tahoe PSP overlay (12.5-25/26) to inject. %s",
                message or "See payloads/Kexts/Community/Tahoe-Yellow-Screen/SOURCE.md",
            )
            return
        ditto = Path("/usr/bin/ditto")
        for src, target in pairs:
            logging.info(
                "yellow_screen_mitigations: injecting PatcherSupportPkg Tahoe payload %s -> %s",
                src,
                target,
            )
            try:
                if ditto.exists():
                    subprocess.run(
                        [str(ditto), str(src), str(target)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                else:
                    shutil.copytree(src, target, dirs_exist_ok=True)
            except OSError as exc:
                logging.warning("yellow_screen_mitigations: overlay copy failed: %s", exc)

    def mount(self) -> bool:
        if not Path(self.constants.payload_local_binaries_root_path).exists():
            if not (self._mount_universal_binaries_dmg() and self._mount_26x86_internal_resources_dmg()):
                return False
        self._merge_tahoe_yellow_screen_overlay()
        return True
