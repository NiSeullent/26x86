"""
Safari 26 Pre-AVX Fix — RestrictEvents 1.1.8 trampoline patch for MacPro5,1.

Source: https://github.com/kilinccagatay/Safari26-PreAVX-Fix
License: BSD 3-Clause (Acidanthera RestrictEvents fork)

Applied only during macOS EFI build when a verified pre-AVX Mac Pro is the
target. Windows/Linux hosts never mutate EFI; they only receive a notice.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

from x86.platform import MACOS_ONLY_MESSAGE, is_macos

# README verified machine only. Do not apply to MacPro3,1 / 6,1 / 7,1.
# MacPro4,1 flashed to 5,1 reports as MacPro5,1 and is covered that way.
ELIGIBLE_MODELS = frozenset({"MacPro5,1"})
VERIFIED_MODEL = "MacPro5,1"
SETTING_KEY_ALIAS = "auto_pre_avx_patch"

UPSTREAM_URL = "https://github.com/kilinccagatay/Safari26-PreAVX-Fix"
UPSTREAM_RELEASE = "v1.1.8"
KEXT_VERSION = "1.1.8"
KEXT_ZIP_NAME = f"RestrictEvents-v{KEXT_VERSION}-RELEASE.zip"
EXECUTABLE_SHA256 = "5862fd1c5415fa94b6d0165e70200eae80ef9e3b1dd4d89220c669507d79f7ef"
SETTING_KEY = "safari26_preavx_fix"
SOURCE_RELATIVE = Path("payloads/Kexts/Community/Safari26-PreAVX-Fix")

# Upstream installer refuses any CPU that reports AVX (sysctl token).
_AVX_TOKENS = frozenset({"AVX", "AVX2", "AVX512F", "AVX512"})


@dataclass
class Safari26PreAvxDecision:
    eligible_model: bool
    cpu_has_avx: Optional[bool]
    setting_enabled: bool
    payload_present: bool
    host_is_macos: bool
    should_apply: bool
    reason: str
    model: str
    kext_version: str = KEXT_VERSION
    kext_path: Optional[Path] = None
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "eligible_model": self.eligible_model,
            "cpu_has_avx": self.cpu_has_avx,
            "setting_enabled": self.setting_enabled,
            "payload_present": self.payload_present,
            "host_is_macos": self.host_is_macos,
            "should_apply": self.should_apply,
            "reason": self.reason,
            "model": self.model,
            "kext_version": self.kext_version,
            "upstream": UPSTREAM_URL,
            "verified_model": VERIFIED_MODEL,
            "notes": list(self.notes),
        }


def payload_dir(repo_root: Optional[Path] = None) -> Path:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
    return repo_root / SOURCE_RELATIVE


def kext_zip_path(repo_root: Optional[Path] = None) -> Path:
    return payload_dir(repo_root) / KEXT_ZIP_NAME


def payload_available(repo_root: Optional[Path] = None) -> bool:
    path = kext_zip_path(repo_root)
    return path.is_file() and path.stat().st_size > 0


def normalize_model(model: Optional[str]) -> str:
    return (model or "").strip()


def is_eligible_mac_pro(model: Optional[str]) -> bool:
    return normalize_model(model) in ELIGIBLE_MODELS


def cpu_reports_avx(flags: Optional[Iterable[str]]) -> bool:
    """True when sysctl-style CPU feature tokens include AVX (installer logic)."""
    if not flags:
        return False
    tokens = {str(flag).strip().upper() for flag in flags if str(flag).strip()}
    if "AVX" in tokens:
        return True
    return any(token.startswith("AVX") for token in tokens)


def _cpu_flags_from_computer(computer: Any) -> Optional[list[str]]:
    cpu = getattr(computer, "cpu", None) if computer is not None else None
    if cpu is None:
        return None
    flags = list(getattr(cpu, "flags", None) or [])
    leafs = list(getattr(cpu, "leafs", None) or [])
    combined = flags + leafs
    return combined or None


def _truthy_setting(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "off", "no", "disabled"}
    return bool(value)


def setting_allows_auto(settings: Optional[dict[str, Any]] = None) -> bool:
    """Default ON. safari26_preavx_fix or auto_pre_avx_patch set False disables."""
    if settings is None:
        try:
            from x86.settings import SettingsStore

            settings = SettingsStore().load()
        except Exception:
            return True
    primary = settings.get(SETTING_KEY, True)
    alias = settings.get(SETTING_KEY_ALIAS, True)
    return _truthy_setting(primary, True) and _truthy_setting(alias, True)


def merge_jsc_tokens(tokens: Iterable[str]) -> list[str]:
    """Ensure revpatch includes jsc (required by the upstream installer)."""
    merged = [token for token in tokens if token and token != "none"]
    if "jsc" not in merged:
        merged.append("jsc")
    return merged


def evaluate(
    model: Optional[str],
    *,
    cpu_flags: Optional[Iterable[str]] = None,
    settings: Optional[dict[str, Any]] = None,
    host_is_macos: Optional[bool] = None,
    repo_root: Optional[Path] = None,
    respect_host_avx: bool = True,
) -> Safari26PreAvxDecision:
    """
    Decide whether the Safari 26 Pre-AVX RestrictEvents swap should run.

    Model matching follows the upstream README verified machine (MacPro5,1).
    Other Mac Pros and all non-Mac-Pro models are never selected.
    """
    resolved_model = normalize_model(model)
    macos = is_macos() if host_is_macos is None else host_is_macos
    eligible = is_eligible_mac_pro(resolved_model)
    enabled = setting_allows_auto(settings)
    present = payload_available(repo_root)
    has_avx: Optional[bool] = None
    if cpu_flags is not None:
        has_avx = cpu_reports_avx(cpu_flags)

    notes: list[str] = []
    if not macos:
        notes.append(MACOS_ONLY_MESSAGE)

    reason = "not_eligible"
    should = False

    if not eligible:
        reason = "model_not_preavx_mac_pro"
    elif not enabled:
        reason = "disabled_by_user"
    elif not macos:
        reason = "macos_only"
    elif respect_host_avx and has_avx is True:
        reason = "cpu_reports_avx"
    elif not present:
        reason = "payload_missing"
    else:
        should = True
        reason = "auto_apply_preavx_mac_pro"

    return Safari26PreAvxDecision(
        eligible_model=eligible,
        cpu_has_avx=has_avx,
        setting_enabled=enabled,
        payload_present=present,
        host_is_macos=macos,
        should_apply=should,
        reason=reason,
        model=resolved_model,
        kext_path=kext_zip_path(repo_root) if present else None,
        notes=notes,
    )


def evaluate_for_efi_build(
    model: str,
    computer: Any = None,
    custom_model: Optional[str] = None,
    settings: Optional[dict[str, Any]] = None,
    repo_root: Optional[Path] = None,
) -> Safari26PreAvxDecision:
    """
    EFI-build evaluation. Host AVX flags are used only when the target model
    is the probed machine (no custom SMBIOS override).
    """
    flags = _cpu_flags_from_computer(computer)
    host_model = ""
    if computer is not None:
        host_model = normalize_model(getattr(computer, "real_model", None))
    target = normalize_model(model)
    building_for_host = not normalize_model(custom_model) or target == host_model
    return evaluate(
        target,
        cpu_flags=flags if building_for_host else None,
        settings=settings,
        repo_root=repo_root,
        respect_host_avx=building_for_host,
    )


def apply_to_misc_builder(builder: Any) -> Safari26PreAvxDecision:
    """
    Hook for efi_builder.misc.BuildMiscellaneous.

    Returns the decision. Caller uses kext path / version and merge_jsc_tokens.
    """
    decision = evaluate_for_efi_build(
        model=builder.model,
        computer=getattr(builder, "computer", None),
        custom_model=getattr(getattr(builder, "constants", None), "custom_model", None),
    )
    if decision.should_apply:
        logging.info(
            "- Safari 26 Pre-AVX Fix: RestrictEvents %s for %s (%s)",
            decision.kext_version,
            decision.model,
            UPSTREAM_URL,
        )
    elif decision.eligible_model:
        logging.info("- Safari 26 Pre-AVX Fix skipped: %s", decision.reason)
    return decision
