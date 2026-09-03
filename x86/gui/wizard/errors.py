"""
errors.py: 기술 오류를 일반 사용자용 한국어 메시지로 변환
"""

import logging

from . import strings


def user_message(exc: BaseException) -> str:
    """
    예외를 사용자에게 보여줄 평이한 한국어 메시지로 변환합니다.
    기술적 세부사항은 로그에만 남깁니다.
    """
    logging.exception("작업 오류 (사용자 메시지로 변환): %s", exc)

    text = str(exc).lower() if exc else ""

    if "permission" in text or "denied" in text or "eacces" in text:
        return strings.ERR_PERMISSION
    if "unsupported" in text or "not supported" in text:
        return strings.ERR_UNSUPPORTED
    if "build" in text or "opencore" in text:
        return strings.ERR_BUILD_FAILED
    if "install" in text or "disk" in text or "usb" in text:
        return strings.ERR_INSTALL_FAILED
    if "patch" in text or "sip" in text or "amfi" in text:
        return strings.ERR_PATCH_FAILED

    return strings.ERR_GENERIC


def show_error_dialog(parent, exc: BaseException, title: str = "오류") -> None:
    """wx 대화상자로 평이한 오류 메시지를 표시합니다."""
    import wx

    message = user_message(exc)
    dlg = wx.MessageDialog(parent, message, title, style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()
