"""
26x86 application package.

Runtime entry: ``python -m x86 <command>``
"""

from .manifest import (
    APP_NAME,
    BUNDLE_ID,
    COPYRIGHT,
    PATCHER_SUPPORT_PKG_VERSION,
    PATCHER_VERSION,
)
from .paths import Paths

__version__ = PATCHER_VERSION

__all__ = [
    "APP_NAME",
    "BUNDLE_ID",
    "COPYRIGHT",
    "PATCHER_SUPPORT_PKG_VERSION",
    "PATCHER_VERSION",
    "Paths",
    "__version__",
]
