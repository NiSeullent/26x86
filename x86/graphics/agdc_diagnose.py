"""
Track D — AGDCDiagnose solid yellow vs UI-tint yellow.

Layer split (do not conflate):
- solid_agdc: framebuffer / AppleGraphicsDevicePolicy — UI often unusable;
  mitigated by WhateverGreen agdpmod/shikigva on the *correct* GFX0 PCI path
  (already in efi_builder/graphics_audio.py d3a7b87 — do not rewrite).
- ui_tint_compositor: ColorSync/SkyLight tint with interactive UI;
  sRGB fallback helps tint only.

skylight_tracks contract:
- serialize_track_detect_fields / serialize_agdc_diagnose_fields
- sys_patch_hooks → {} (detect/docs only; not in SYS_PATCH_TRACKS)
"""

from __future__ import annotations

from typing import Any, Iterable, Literal, Optional

from .yellow_screen import (
    SOCKET_AMD_YELLOW_SCREEN_MODELS,
    STOCK_GCN_AGDP_MODELS,
    classify_gpu_family,
    is_compositor_yellow_screen_hardware,
    is_tahoe_os,
)

YellowMode = Literal[
    "none",
    "solid_agdc",
    "ui_tint_compositor",
    "ambiguous",
    "unknown",
]

SYMPTOM_FULL_SCREEN_SOLID = "full_screen_solid_yellow"
SYMPTOM_UI_INTERACTIVE = "ui_interactive"
SYMPTOM_UI_TINT_ONLY = "ui_tint_only"
SYMPTOM_AGDCDIAGNOSE_YELLOW = "agdc_diagnose_yellow"

OCLP_T2_YELLOW_SCREEN_ISSUE = (
    "https://github.com/albert-mueller/OpenCore-Legacy-Patcher-T2/issues/194"
)
WEG_AGDPMOD_DOC = (
    "https://github.com/acidanthera/WhateverGreen/blob/master/Manual/FAQ.Chart.md"
)


def sys_patch_hooks(
    xnu_major: int,
    xnu_minor: int = 0,
    marketing_version: str = "",
) -> dict:
    """Detect-only track — no root-patch dict (EFI agdpmod stays in efi_builder)."""
    del xnu_major, xnu_minor, marketing_version
    return {}


def is_agdc_framebuffer_hardware(
    model: str,
    gpu_archs: Optional[Iterable[Any]] = None,
) -> bool:
    if model in STOCK_GCN_AGDP_MODELS or model in SOCKET_AMD_YELLOW_SCREEN_MODELS:
        return True
    return classify_gpu_family(model, gpu_archs) in {
        "vega",
        "polaris",
        "gcn",
        "socket_amd",
    }


def classify_yellow_mode(
    *,
    full_screen_solid: Optional[bool] = None,
    ui_interactive: Optional[bool] = None,
    ui_tint_only: Optional[bool] = None,
    agdc_diagnose_yellow: Optional[bool] = None,
    symptoms: Optional[dict[str, Any]] = None,
) -> YellowMode:
    bag = dict(symptoms or {})
    if full_screen_solid is None and SYMPTOM_FULL_SCREEN_SOLID in bag:
        full_screen_solid = bool(bag[SYMPTOM_FULL_SCREEN_SOLID])
    if ui_interactive is None and SYMPTOM_UI_INTERACTIVE in bag:
        ui_interactive = bool(bag[SYMPTOM_UI_INTERACTIVE])
    if ui_tint_only is None and SYMPTOM_UI_TINT_ONLY in bag:
        ui_tint_only = bool(bag[SYMPTOM_UI_TINT_ONLY])
    if agdc_diagnose_yellow is None and SYMPTOM_AGDCDIAGNOSE_YELLOW in bag:
        agdc_diagnose_yellow = bool(bag[SYMPTOM_AGDCDIAGNOSE_YELLOW])

    if not any(
        v is not None
        for v in (full_screen_solid, ui_interactive, ui_tint_only, agdc_diagnose_yellow)
    ):
        return "unknown"

    if agdc_diagnose_yellow is True or (
        full_screen_solid is True and ui_interactive is False
    ):
        return "solid_agdc"

    if ui_tint_only is True or (
        ui_interactive is True and full_screen_solid is not True
    ):
        if full_screen_solid is True and ui_interactive is True:
            return "ambiguous"
        return "ui_tint_compositor"

    if full_screen_solid is True and ui_interactive is True:
        return "ambiguous"

    if (
        full_screen_solid is False
        and ui_tint_only is False
        and agdc_diagnose_yellow is False
    ):
        return "none"

    return "ambiguous"


def agdc_yellow_risk(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    agdpmod_present: Optional[bool] = None,
    agdp_on_correct_gfx0: Optional[bool] = None,
    assume_tahoe: bool = False,
) -> bool:
    """True on Tahoe when AGDC/framebuffer solid-yellow is plausible."""
    if not is_agdc_framebuffer_hardware(model, gpu_archs):
        return False
    if not (is_tahoe_os(os_version, xnu_major) or assume_tahoe):
        return False
    if agdp_on_correct_gfx0 is False:
        return True
    if agdpmod_present is not True:
        return True
    return agdp_on_correct_gfx0 is None


def ui_tint_yellow_risk(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    assume_tahoe: bool = False,
) -> bool:
    if not is_compositor_yellow_screen_hardware(model, gpu_archs):
        return False
    return is_tahoe_os(os_version, xnu_major) or assume_tahoe


def yellow_layer_summary(mode: YellowMode) -> str:
    return {
        "none": "yellow 증상 없음 (보고된 범위)",
        "solid_agdc": "AGDCDiagnose / framebuffer solid yellow — agdpmod·GFX0 PCI path 확인",
        "ui_tint_compositor": "UI-tint yellow — ColorSync/SkyLight; sRGB는 tint만 완화",
        "ambiguous": "solid AGDC와 UI-tint 신호 혼재 — 두 계층 모두 점검",
        "unknown": "증상 미입력 — agdc_yellow_risk / ui_tint_yellow_risk 참고",
    }.get(mode, "unknown")


def mitigation_hints_for_mode(mode: YellowMode) -> list[str]:
    if mode == "solid_agdc":
        return [
            "efi_rebuild_agdpmod_shikigva",
            "verify_deviceproperties_on_gfx0_pci_path",
            "avoid_wrong_sibling_gpu_path_macpro_dual",
            "collect_graphics_diagnostics_agdc_section",
        ]
    if mode == "ui_tint_compositor":
        return [
            "colorsync_srgb_fallback",
            "window_server_cache_disable",
            "renderbox_metallib_if_payload",
            "not_fixed_by_agdpmod_alone",
        ]
    if mode == "ambiguous":
        return [
            "run_agdc_and_compositor_checklists",
            "efi_rebuild_agdpmod_shikigva",
            "colorsync_srgb_fallback",
        ]
    return []


def serialize_agdc_diagnose_fields(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    agdpmod_present: Optional[bool] = None,
    agdp_on_correct_gfx0: Optional[bool] = None,
    assume_tahoe: bool = False,
    symptoms: Optional[dict[str, Any]] = None,
    include_framebuffer_checklist: bool = True,
    **_kwargs: Any,
) -> dict[str, Any]:
    """Detect JSON for Track D. Never emits yellow_screen_risk."""
    mode = classify_yellow_mode(symptoms=symptoms)
    agdc_risk = agdc_yellow_risk(
        model,
        gpu_archs=gpu_archs,
        os_version=os_version,
        xnu_major=xnu_major,
        agdpmod_present=agdpmod_present,
        agdp_on_correct_gfx0=agdp_on_correct_gfx0,
        assume_tahoe=assume_tahoe,
    )
    tint_risk = ui_tint_yellow_risk(
        model,
        gpu_archs=gpu_archs,
        os_version=os_version,
        xnu_major=xnu_major,
        assume_tahoe=assume_tahoe,
    )
    payload: dict[str, Any] = {
        "agdc_yellow_risk": agdc_risk,
        "ui_tint_yellow_risk": tint_risk,
        "agdc_yellow_mode": mode,
        "agdc_yellow_layer_summary": yellow_layer_summary(mode),
        "agdc_mitigation_hints": mitigation_hints_for_mode(mode),
        "agdc_framebuffer_hardware": is_agdc_framebuffer_hardware(model, gpu_archs),
        "agdc_issue_url": OCLP_T2_YELLOW_SCREEN_ISSUE,
        "agdc_weg_agdpmod_doc": WEG_AGDPMOD_DOC,
        "agdc_notes": _notes(model, mode, agdc_risk, tint_risk, agdpmod_present),
    }
    if include_framebuffer_checklist:
        from .agdc_framebuffer import serialize_agdc_framebuffer_fields

        payload.update(
            serialize_agdc_framebuffer_fields(
                model,
                gpu_archs=gpu_archs,
                os_version=os_version,
                xnu_major=xnu_major,
                assume_tahoe=assume_tahoe,
                agdpmod_present=agdpmod_present,
                agdp_on_correct_gfx0=agdp_on_correct_gfx0,
            )
        )
    return payload


def serialize_track_detect_fields(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    agdpmod_present: Optional[bool] = None,
    assume_tahoe: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """skylight_tracks DETECT_FIELDS hook."""
    return serialize_agdc_diagnose_fields(
        model,
        gpu_archs=gpu_archs,
        os_version=os_version,
        xnu_major=xnu_major,
        agdpmod_present=agdpmod_present,
        assume_tahoe=assume_tahoe,
        **kwargs,
    )


def _notes(
    model: str,
    mode: YellowMode,
    agdc_risk: bool,
    tint_risk: bool,
    agdpmod_present: Optional[bool],
) -> list[str]:
    notes = [
        "solid AGDC yellow ≠ UI-tint yellow — 계층을 섞지 마세요.",
        "ColorSync sRGB는 tint만 완화; solid yellow(UI 불가)에는 효과가 없습니다.",
        "agdpmod 로직은 efi_builder/graphics_audio.py (d3a7b87) — 재작성 금지.",
        yellow_layer_summary(mode),
    ]
    if agdc_risk:
        notes.append(
            f"{model}: Tahoe AGDC/framebuffer 위험 — agdpmod가 실제 GFX0 PCI path에 있는지 확인."
        )
    if tint_risk:
        notes.append(
            f"{model}: Tahoe UI-tint/compositor 위험 — Track B/C·RenderBox를 별도 점검."
        )
    if agdpmod_present is True:
        notes.append("boot-args에 agdpmod 보임 — Mac Pro 듀얼 GPU sibling path를 체크리스트로 확인.")
    elif agdpmod_present is False:
        notes.append("boot-args에 agdpmod 없음 (DeviceProperties-only일 수 있음).")
    return notes
