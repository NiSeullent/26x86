"""
x86.patch: Root volume patching payload management.
"""

from .payload_manager import PayloadManager
from .safari26_preavx import evaluate as evaluate_safari26_preavx

__all__ = ["PayloadManager", "evaluate_safari26_preavx"]
