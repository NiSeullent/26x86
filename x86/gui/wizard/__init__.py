"""
wizard: 단계별 마법사 GUI (일반 사용자용 기본 UI)
"""

from x86.gui.launch import launch_wizard
def __getattr__(name):
    if name == "WizardFrame":
        from .wizard_frame import WizardFrame
        return WizardFrame
    raise AttributeError(name)

__all__ = ["WizardFrame", "launch_wizard"]
