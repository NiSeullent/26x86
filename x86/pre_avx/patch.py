"""
Safari26-PreAVX-Fix EFI bundle helpers — delegates to x86.patch.safari26_preavx.
"""

from x86.patch.safari26_preavx import (
    KEXT_VERSION as SAFARI26_PRE_AVX_FIX_VERSION,
    UPSTREAM_URL as SAFARI26_PRE_AVX_FIX_SOURCE,
    evaluate_for_efi_build,
    kext_zip_path,
    merge_jsc_tokens,
    setting_allows_auto,
)

SAFARI26_PRE_AVX_FIX_NOTICE = (
    "Safari26-PreAVX-Fix RestrictEvents 1.1.8 — BSD 3-Clause, "
    "derived from Acidanthera RestrictEvents. "
    "See payloads/Kexts/Community/Safari26-PreAVX-Fix/LICENSE.txt"
)


def should_apply_safari26_pre_avx_fix(*args, **kwargs):
    from x86.patch.safari26_preavx import evaluate

    decision = evaluate(*args, **kwargs)
    return decision.should_apply


def resolve_restrict_events_bundle(constants, model, *, computer=None, auto_pre_avx_patch=True):
    from x86.patch.safari26_preavx import evaluate_for_efi_build
    from dataclasses import dataclass
    from pathlib import Path

    @dataclass(frozen=True)
    class RestrictEventsBundle:
        kext_path: Path
        version: str
        community_build: bool
        source_url: str

    decision = evaluate_for_efi_build(
        model,
        computer=computer,
        settings={"auto_pre_avx_patch": auto_pre_avx_patch, "safari26_preavx_fix": auto_pre_avx_patch},
    )
    if decision.should_apply and decision.kext_path:
        return RestrictEventsBundle(
            kext_path=decision.kext_path,
            version=decision.kext_version,
            community_build=True,
            source_url=SAFARI26_PRE_AVX_FIX_SOURCE,
        )
    return RestrictEventsBundle(
        kext_path=constants.restrictevents_path,
        version=constants.restrictevents_version,
        community_build=False,
        source_url="https://github.com/acidanthera/RestrictEvents",
    )


__all__ = [
    "SAFARI26_PRE_AVX_FIX_NOTICE",
    "SAFARI26_PRE_AVX_FIX_SOURCE",
    "SAFARI26_PRE_AVX_FIX_VERSION",
    "evaluate_for_efi_build",
    "kext_zip_path",
    "merge_jsc_tokens",
    "resolve_restrict_events_bundle",
    "setting_allows_auto",
    "should_apply_safari26_pre_avx_fix",
]
