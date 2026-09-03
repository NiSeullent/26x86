"""
subprocess_wrapper.py: Wrapper for subprocess module to better handle errors and output
                       Additionally handles our Privileged Helper Tool
"""

import enum
import stat
import shlex
import logging
import subprocess
import Security
import os

from pathlib import Path
from typing import Callable, Optional


OCLP_PRIVILEGED_HELPER = "/Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper"
OCLP_PRIVILEGED_HELPER_EXPECTED_MODE = 0o4755


class PrivilegedHelperErrorCodes(enum.IntEnum):
    """
    Error codes for Privileged Helper Tool.

    Reference:
        payloads/Tools/PrivilegedHelperTool/main.m
    """
    OCLP_PHT_ERROR_MISSING_ARGUMENTS           = 160
    OCLP_PHT_ERROR_SET_UID_MISSING             = 161
    OCLP_PHT_ERROR_SET_UID_FAILED              = 162
    OCLP_PHT_ERROR_SELF_PATH_MISSING           = 163
    OCLP_PHT_ERROR_PARENT_PATH_MISSING         = 164
    OCLP_PHT_ERROR_SIGNING_INFORMATION_MISSING = 165
    OCLP_PHT_ERROR_INVALID_TEAM_ID             = 166
    OCLP_PHT_ERROR_INVALID_CERTIFICATES        = 167
    OCLP_PHT_ERROR_COMMAND_MISSING             = 168
    OCLP_PHT_ERROR_COMMAND_FAILED              = 169
    OCLP_PHT_ERROR_CATCH_ALL                   = 170


def privileged_helper_needs_setuid_repair() -> bool:
    """
    Check whether the Privileged Helper Tool is missing its expected
    permission bits (4755: setuid root, rwxr-xr-x).

    This can drift after certain OS updates or re-signing steps, and
    manifests as OCLP_PHT_ERROR_SET_UID_MISSING/FAILED when the helper
    is invoked.

    Returns:
        bool: True if the helper tool exists but its permissions need to be
              repaired. False if it's already correct, or the helper tool
              isn't installed yet (nothing to repair here).
    """
    helper_path = Path(OCLP_PRIVILEGED_HELPER)
    if not helper_path.exists():
        return False

    current_mode = stat.S_IMODE(helper_path.stat().st_mode)
    if current_mode == OCLP_PRIVILEGED_HELPER_EXPECTED_MODE:
        return False

    logging.info(f"Privileged Helper Tool has unexpected permissions: {oct(current_mode)} (expected {oct(OCLP_PRIVILEGED_HELPER_EXPECTED_MODE)})")
    return True


def repair_privileged_helper_permissions() -> bool:
    """
    Reset the Privileged Helper Tool back to 4755 using the Security framework,
    which is supported on macOS 10.0+, that easily fits with 10.10!

    Note: Deliberately does NOT go through run_as_root() (i.e. the helper
    tool itself), since a helper tool missing its setuid bit can't elevate
    itself - that's precisely the problem being repaired here.
    """
    # Authorize the privileged operation using macOS Authorization Services.
    # This causes macOS to present its native authorization UI rather than
    # requiring OCLP to collect an administrator password.
    # MARK: IMPORTANT

    # If this doesn't work make sure that you have pyObjC 12.1, as that was version that has been tested.
    status, auth_ref = Security.AuthorizationCreate(
        None,
        None,
        Security.kAuthorizationFlagDefaults,
        None
    )

    if status != Security.errAuthorizationSuccess:
        raise RuntimeError(
            f"AuthorizationCreate failed with status {status}"
        )

    try:
        # Request the right to execute a privileged tool.
        rights = (
            Security.AuthorizationItem(
                Security.kAuthorizationRightExecute,
                0,
                None,
                0
            ),
        )
        prompt = b"26x86 needs administrator permission to repair the permissions of its privileged helper tool."

        environment = (
            Security.AuthorizationItem(
                Security.kAuthorizationEnvironmentPrompt,
                len(prompt),
                prompt,
                0
            ),
        )

        status, authorized_rights = Security.AuthorizationCopyRights(
            auth_ref,
            rights,
            environment,
            (
                Security.kAuthorizationFlagInteractionAllowed
                | Security.kAuthorizationFlagExtendRights
            ),
            None,
        )

        if status == Security.errAuthorizationCanceled:
            logging.info("User canceled the request")
            return False

        if status != Security.errAuthorizationSuccess:
            raise RuntimeError(
                f"AuthorizationCopyRights failed with status {status}"
            )


        chmod_arguments = (
            oct(OCLP_PRIVILEGED_HELPER_EXPECTED_MODE)[2:].encode("utf-8"),
            OCLP_PRIVILEGED_HELPER.encode("utf-8"),
        )

        status, _ = Security.AuthorizationExecuteWithPrivileges(
            auth_ref,
            b"/bin/chmod",
            Security.kAuthorizationFlagDefaults,
            chmod_arguments,
            None,
        )

        if status == Security.errAuthorizationCanceled:
            logging.info("User canceled the request")
            return False

        if status != Security.errAuthorizationSuccess:
            raise RuntimeError(
                f"AuthorizationExecuteWithPrivileges failed with status {status}"
            )

        logging.info("Privileged Helper Tool permissions repaired (4755)")
        return True
    # behebt einen Bug, indem falls die Operation nicht erfolgreich ist, zeigt es nicht einen Fehler
    except Exception as e:
        logging.error("Running the Priveleged Helper Tool operation failed.")
        logging.exception("Stack Trace:")
        sys.exit(3)

    finally:
        Security.AuthorizationFree(
           auth_ref,
           Security.kAuthorizationFlagDefaults
        )
def run(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Basic subprocess.run wrapper.
    """
    return subprocess.run(*args, **kwargs)


def run_as_root(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Run subprocess as root.

    Note: Full path to first argument is required.
    Helper tool does not resolve PATH.
    """
    # Check if first argument exists
    if not Path(args[0][0]).exists():
        raise FileNotFoundError(f"File not found: {args[0][0]}")

    # If we are already running as root (e.g. launched via sudo), bypass the Helper Tool
    if os.geteuid() == 0:
        return subprocess.run(args[0], **kwargs)

    if Path(OCLP_PRIVILEGED_HELPER).exists():
        if privileged_helper_needs_setuid_repair():
            fixed = repair_privileged_helper_permissions()
            if not fixed:
                logging.error("User did not allow us to fix the privileged helper. cannot compete request.")
                return
        result = subprocess.run([OCLP_PRIVILEGED_HELPER] + [args[0][0]] + args[0][1:], **kwargs)
        # Any of our own PrivilegedHelperErrorCodes sentinel values (160-170) means the helper
        # tool itself couldn't do its job - an escalation failure (eg. missing/invalid setuid bit)
        # or another internal precondition (signing/certificates/command validation) - as opposed
        # to the wrapped command failing on its own merits with an ordinary low exit code, which is
        # just returned as-is: retrying that via osascript wouldn't fix a genuine command failure,
        # and would only cost an extra administrator-password prompt for nothing.
        _helper_error = __resolve_privileged_helper_errors(result.returncode)
        if _helper_error is not None:
            logging.error(f"Privileged Helper Tool failed ({_helper_error}). Falling back to osascript.")
            return osascript(args[0], **kwargs)
        return result
    else:
        logging.warning(f"Privileged Helper Tool not found at {OCLP_PRIVILEGED_HELPER}. Falling back to osascript.")
        return osascript(args[0], **kwargs)

# behebt eine Sicherheitslücke, indem osascript ohne Bedingung angerufen geworden. Einen Angreifer könnte dazu erzwingen, osascript abzurufen, um beliebiges Code auszuführen und Priveleged Helper Tool umzugehen
def osascript(cmd_args, **kwargs): # <- behebt einen Fehler, die zu Fehler NameError: name 'args' is not defined verursacht, die nur ins Repository https://github.com/Medelcartelinc/OpenCore-Legacy-Patcher-T2 existierte
    import shlex
    cmd_string = shlex.join(str(arg) for arg in cmd_args)
    as_safe_string = cmd_string.replace('\\', '\\\\').replace('"', '\\"')
    apple_script = f'do shell script "{as_safe_string}" with administrator privileges'
    return subprocess.run(["osascript", "-e", apple_script], **kwargs)


def mount_dmg(
    dmg_path: Path,
    mount_point: Path,
    shadow_path: Path = None,
    password: str = None,
    admin_password_prompt: Optional[Callable[[], str]] = None,
    retry_on_auth_error: bool = False
) -> subprocess.CompletedProcess:
    """
    Attach a disk image via 'hdiutil attach', using '-stdinpass' rather than
    the deprecated (and, on some systems, less reliable) '-passphrase' flag.

    Some systems (observed starting with macOS 26.4) require elevated
    privileges to mount disk images, a regression from prior unprivileged
    mounts succeeding, which manifests as "Permission denied". If
    'admin_password_prompt' is supplied and the unprivileged attempt fails
    with "Permission denied", this clears com.apple.quarantine (which can
    independently trip hdiutil's own Gatekeeper-style authentication gate)
    and retries once, elevated via 'sudo'.

    'retry_on_auth_error' additionally treats "Authentication error" as a
    retry trigger. Only pass this for a fixed, known-correct 'password' (e.g.
    PatcherSupportPkg's convention of a hardcoded passphrase): with a
    user-supplied password, "Authentication error" more likely means a wrong
    password than a privilege gate, and would otherwise wrongly prompt for an
    administrator password on every incorrect attempt.

    Deliberately not routed through "do shell script ... with administrator
    privileges" (security_authtrampoline): that mechanism runs detached from
    the current login/Aqua session, and hdiutil's own internal authentication
    appears to depend on that session being present. 'admin_password_prompt'
    is expected to only collect a password (e.g. via a plain AppleScript
    "display dialog"), not to perform the elevation itself.
    """
    mount_point.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["/usr/bin/hdiutil", "attach", "-noverify", str(dmg_path), "-mountpoint", str(mount_point), "-nobrowse"]
    if shadow_path:
        shadow_path.parent.mkdir(parents=True, exist_ok=True)
        cmd.extend(["-shadow", str(shadow_path)])
    cmd.append("-stdinpass")

    # Force hdiutil to output in English so we can reliably match "Permission denied"
    env = os.environ.copy()
    env["LC_ALL"] = "C"

    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    stdout, _ = process.communicate(input=password.encode() if password else None)

    if process.returncode == 0 or admin_password_prompt is None:
        return subprocess.CompletedProcess(args=cmd, returncode=process.returncode, stdout=stdout)

    _should_retry = b"Permission denied" in stdout or (retry_on_auth_error and b"Authentication error" in stdout)
    if not _should_retry:
        return subprocess.CompletedProcess(args=cmd, returncode=process.returncode, stdout=stdout)

    logging.info("- Unprivileged hdiutil attach denied, retrying with administrator privileges")

    admin_password = admin_password_prompt()
    if not admin_password:
        logging.info("- Elevated hdiutil attach cancelled (no administrator password provided)")
        return subprocess.CompletedProcess(args=cmd, returncode=process.returncode, stdout=stdout)

    # Clear com.apple.quarantine before attaching: a quarantined disk image (e.g. a
    # freshly rebuilt/re-extracted payload) can trip hdiutil's authentication gate
    # even when run as root - elevating privileges alone does not clear it. Run it
    # in the same elevated shell as the actual attach so it always has the rights to.
    elevated_shell = (
        f"xattr -d com.apple.quarantine {shlex.quote(str(dmg_path))} 2>/dev/null; "
        + " ".join(shlex.quote(str(arg)) for arg in cmd)
    )
    elevated_cmd = ["/usr/bin/sudo", "-S", "/bin/sh", "-c", elevated_shell]

    elevated_process = subprocess.Popen(elevated_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    # sudo -S reads exactly one line from stdin for its own password, then hands the
    # remaining, still-open stdin through to the shell (and on to hdiutil's -stdinpass)
    stdin_payload = admin_password + "\n" + (password or "")
    elevated_stdout, _ = elevated_process.communicate(input=stdin_payload.encode())

    if elevated_process.returncode == 0:
        logging.info("- Mounted (elevated)")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=elevated_stdout)
    # behebt einen Fehler, indem Elevated hdiutil attach failed druckt bedingungslos und eine Sicherheitslücke, die Angreifern ausnutzen können, um dieses Mount-Fehler zu zeigen, um DoS-Angriffe zu starten.
    else:
      logging.error(f"- Elevated hdiutil attach failed: {elevated_stdout.decode(errors='replace').strip()}")
      return subprocess.CompletedProcess(args=cmd, returncode=elevated_process.returncode, stdout=elevated_stdout)


def verify(process_result: subprocess.CompletedProcess) -> None:
    """
    Verify process result and raise exception if failed.
    """
    if process_result.returncode == 0:
        return
    # behebt 2 Sicherheitslücken: 1. Falls ein Fehler passiert, druckte es nicht ins Terminal, also ein Benutzer, der nicht das GUI verwendet, weißt nicht, es gäbe ein Fehler und Angreifern könnten davon ausnutzen. 2. Angreifern könnten die Bedingung if process_result.returncode == 0: löschen, um der Fehler Process failed with exit code zu forcieren, um ClickFix-Angriffe zu starten.
    else:
        logging.error(f"Process failed with exit code {process_result.returncode}")
        log(process_result)
        raise Exception(f"Process failed with exit code {process_result.returncode}")


def run_and_verify(*args, **kwargs) -> None:
    """
    Run subprocess and verify result.

    Asserts on failure.
    """
    verify(run(*args, **kwargs))


def run_as_root_and_verify(*args, **kwargs) -> None:
    """
    Run subprocess as root and verify result.

    Asserts on failure.
    """
    verify(run_as_root(*args, **kwargs))


def log(process: subprocess.CompletedProcess) -> None:
    """
    Display subprocess error output in formatted string.
    """
    for line in generate_log(process).split("\n"):
        logging.error(line)


def generate_log(process: subprocess.CompletedProcess) -> str:
    """
    Display subprocess error output in formatted string.
    Note this function is still used for zero return code errors, since
    some software don't ever return non-zero regardless of success.

    Format:

        Command: <command>
        Return Code: <return code>
        Standard Output:
            <standard output line 1>
            <standard output line 2>
            ...
        Standard Error:
            <standard error line 1>
            <standard error line 2>
            ...
    """
    output = "Subprocess failed.\n"
    output += f"    Command: {process.args}\n"
    output += f"    Return Code: {process.returncode}\n"
    _returned_error = __resolve_privileged_helper_errors(process.returncode)
    if _returned_error:
        output += f"        Likely Enum: {_returned_error}\n"
    output += f"    Standard Output:\n"
    if process.stdout:
        output += __format_output(process.stdout.decode("utf-8"))
    else:
        output += "        None\n"
    output += f"    Standard Error:\n"
    if process.stderr:
        output += __format_output(process.stderr.decode("utf-8"))
    else:
        output += "        None\n"

    return output


def __resolve_privileged_helper_errors(return_code: int) -> str:
    """
    Attempt to resolve Privileged Helper Tool error codes.
    """
    if return_code not in [error_code.value for error_code in PrivilegedHelperErrorCodes]:
        return None
    # behebt einen Fehler, indem den Priveleged Helper Tool Fehler bedingungslos zeigt und eine kritische Sicherheitslücke, die Angreifern ausnutzen können, um der Priveleged Helper Tool zum Absturz zu bringen, und auf osascript zurückzufallen
    else:
        return PrivilegedHelperErrorCodes(return_code).name


def __format_output(output: str) -> str:
    """
    Format output.
    """
    if not output:
        # Shouldn't happen, but just in case
        return "        None\n"

    _result = "\n".join([f"        {line}" for line in output.split("\n") if line not in ["", "\n"]])
    if not _result.endswith("\n"):
        _result += "\n"

    return _result
