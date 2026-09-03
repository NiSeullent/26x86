"""
Track D — Mac Pro + Vega 64 framebuffer / AGDP path diagnostic checklist.

Validates DeviceProperties path assumptions already implemented in
efi_builder/graphics_audio.py (d3a7b87 — do not rewrite). Wrong sibling PCI
path → solid yellow AGDCDiagnose screen.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Literal, Optional

from .yellow_screen import (
    SOCKET_AMD_YELLOW_SCREEN_MODELS,
    STOCK_GCN_AGDP_MODELS,
    classify_gpu_family,
    is_tahoe_os,
    socket_amd_needs_kdkless,
)

CheckStatus = Literal["pass", "fail", "warn", "unknown", "skip"]

VEGA64_DEVICE_HEX = "0x687F"
DEFAULT_MAC_PRO_GFX0_PATH = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"

AGDP_GAP_DOC = (
    "efi_builder/graphics_audio.py:_backlight_path_detection (gfx0_matched) — "
    "d3a7b87; do not rewrite. Diagnose only."
)


@dataclass(frozen=True)
class FramebufferCheckItem:
    id: str
    title: str
    status: CheckStatus
    detail: str = ""
    remediation: str = ""


@dataclass
class FramebufferChecklistResult:
    model: str
    gpu_family: str
    applicable: bool
    items: list[FramebufferCheckItem] = field(default_factory=list)
    failed_ids: list[str] = field(default_factory=list)
    warn_ids: list[str] = field(default_factory=list)
    gap_notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "gpu_family": self.gpu_family,
            "applicable": self.applicable,
            "items": [asdict(item) for item in self.items],
            "failed_ids": list(self.failed_ids),
            "warn_ids": list(self.warn_ids),
            "gap_notes": list(self.gap_notes),
            "all_critical_passed": bool(
                self.applicable
                and not self.failed_ids
                and not any(
                    i.status == "unknown" and i.id.startswith("agdp") for i in self.items
                )
            ),
        }


def _token_blob(gpu_archs: Optional[Iterable[Any]]) -> str:
    parts: list[str] = []
    for gpu in gpu_archs or []:
        if isinstance(gpu, dict):
            parts.append(str(gpu.get("arch") or gpu.get("name") or gpu.get("device") or ""))
            did = gpu.get("device_id")
            if isinstance(did, int):
                parts.append(hex(did))
            elif did is not None:
                parts.append(str(did))
        else:
            parts.append(str(gpu))
    return " ".join(parts).lower()


def is_vega64_gpu(gpu_archs: Optional[Iterable[Any]] = None) -> bool:
    blob = _token_blob(gpu_archs)
    if "687f" in blob or "vega 64" in blob or "rx vega 64" in blob:
        return True
    return "vega" in blob and "64" in blob


def is_mac_pro_framebuffer_target(model: str) -> bool:
    return model in SOCKET_AMD_YELLOW_SCREEN_MODELS or model in STOCK_GCN_AGDP_MODELS


def checklist_applicable(
    model: str,
    gpu_archs: Optional[Iterable[Any]] = None,
) -> bool:
    if not is_mac_pro_framebuffer_target(model):
        return False
    family = classify_gpu_family(model, gpu_archs)
    if family in {"vega", "polaris", "gcn", "socket_amd"}:
        return True
    return model in SOCKET_AMD_YELLOW_SCREEN_MODELS


def build_macpro_framebuffer_checklist(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    assume_tahoe: bool = False,
    agdpmod_present: Optional[bool] = None,
    shikigva_present: Optional[bool] = None,
    agdp_on_correct_gfx0: Optional[bool] = None,
    gfx0_pci_path: Optional[str] = None,
    deviceproperties_paths: Optional[Iterable[str]] = None,
    whatevergreen_loaded: Optional[bool] = None,
    amd_framebuffer_kext_loaded: Optional[bool] = None,
    cpu_generation: Optional[int] = None,
    kdkless_enabled: Optional[bool] = None,
) -> FramebufferChecklistResult:
    family = classify_gpu_family(model, gpu_archs)
    applicable = checklist_applicable(model, gpu_archs)
    items: list[FramebufferCheckItem] = []
    gaps: list[str] = [
        AGDP_GAP_DOC,
        "Wrong PCI path → solid yellow AGDCDiagnose; compositor tint is a separate layer.",
    ]

    if not applicable:
        return FramebufferChecklistResult(
            model=model,
            gpu_family=family,
            applicable=False,
            items=[
                FramebufferCheckItem(
                    id="scope",
                    title="Mac Pro / stock GCN AGDP scope",
                    status="skip",
                    detail=f"{model} is outside Mac Pro / stock GCN AGDP checklist",
                )
            ],
            gap_notes=gaps,
        )

    tahoe = is_tahoe_os(os_version, xnu_major) or assume_tahoe
    items.append(
        FramebufferCheckItem(
            id="tahoe_os",
            title="Target OS is Tahoe (XNU 25+)",
            status="pass" if tahoe else "warn",
            detail="Tahoe" if tahoe else "Not Tahoe — AGDC solid yellow is primarily Tahoe-era",
            remediation="" if tahoe else "Re-run after upgrade or set assume_tahoe",
        )
    )

    vega64 = is_vega64_gpu(gpu_archs)
    items.append(
        FramebufferCheckItem(
            id="gpu_identity",
            title="GPU identity (Vega 64 / GCN / Polaris / socket)",
            status="pass"
            if (vega64 or family in {"vega", "polaris", "gcn", "socket_amd"})
            else "warn",
            detail=(
                f"family={family}"
                + (f", Vega64 marker ({VEGA64_DEVICE_HEX})" if vega64 else "")
            ),
            remediation="Confirm system_profiler / ioreg device-id for aftermarket cards",
        )
    )

    if agdpmod_present is True:
        agdp_status: CheckStatus = "pass"
        agdp_detail = "agdpmod visible"
    elif agdpmod_present is False:
        agdp_status = "fail"
        agdp_detail = "agdpmod not detected in boot-args (DeviceProperties-only possible)"
    else:
        agdp_status = "unknown"
        agdp_detail = "agdpmod presence not probed"
    items.append(
        FramebufferCheckItem(
            id="agdpmod_present",
            title="WhateverGreen agdpmod present",
            status=agdp_status,
            detail=agdp_detail,
            remediation="Rebuild EFI with agdpmod=vit9696|pikera (efi_builder — do not hand-rewrite)",
        )
    )

    if shikigva_present is True:
        shi_status: CheckStatus = "pass"
        shi_detail = "shikigva present"
    elif shikigva_present is False:
        shi_status = "fail"
        shi_detail = "shikigva missing"
    else:
        shi_status = "unknown"
        shi_detail = "shikigva not probed"
    items.append(
        FramebufferCheckItem(
            id="shikigva_present",
            title="shikigva DRM/GVA property present",
            status=shi_status,
            detail=shi_detail,
            remediation="Ensure shikigva on the dGPU DeviceProperties path",
        )
    )

    paths = [p for p in (deviceproperties_paths or []) if p]
    if agdp_on_correct_gfx0 is True:
        path_status: CheckStatus = "pass"
        path_detail = f"GFX0 path confirmed ({gfx0_pci_path or 'caller-verified'})"
    elif agdp_on_correct_gfx0 is False:
        path_status = "fail"
        path_detail = (
            f"agdpmod not on real GFX0 (gfx0={gfx0_pci_path or 'unknown'}; "
            f"DeviceProperties paths={paths or ['none']})"
        )
    elif paths and gfx0_pci_path:
        if gfx0_pci_path in paths:
            path_status = "pass"
            path_detail = f"DeviceProperties includes GFX0 {gfx0_pci_path}"
        else:
            path_status = "fail"
            path_detail = (
                f"GFX0 {gfx0_pci_path} missing from DeviceProperties {paths} — "
                "classic MacPro dual-GPU wrong-path solid yellow"
            )
    elif model == "MacPro6,1":
        path_status = "warn"
        path_detail = (
            "MacPro6,1 dual GCN: verify gfx0_matched so sibling GPU does not steal "
            f"agdpmod (default fallback {DEFAULT_MAC_PRO_GFX0_PATH})"
        )
    else:
        path_status = "unknown"
        path_detail = "GFX0 PCI path not probed"
    items.append(
        FramebufferCheckItem(
            id="agdp_gfx0_pci_path",
            title="agdpmod on correct GFX0 PCI path",
            status=path_status,
            detail=path_detail,
            remediation="Rebuild EFI on live hardware so gfx0_matched sticks; do not hand-edit sibling paths",
        )
    )

    if whatevergreen_loaded is True:
        weg_status: CheckStatus = "pass"
    elif whatevergreen_loaded is False:
        weg_status = "fail"
    else:
        weg_status = "unknown"
    items.append(
        FramebufferCheckItem(
            id="whatevergreen_loaded",
            title="WhateverGreen.kext loaded",
            status=weg_status,
            detail=str(whatevergreen_loaded),
            remediation="Enable WhateverGreen and confirm kextstat",
        )
    )

    if amd_framebuffer_kext_loaded is True:
        fb_status: CheckStatus = "pass"
    elif amd_framebuffer_kext_loaded is False:
        fb_status = "fail"
    else:
        fb_status = "unknown"
    items.append(
        FramebufferCheckItem(
            id="amd_framebuffer_kext",
            title="AMD framebuffer / MTL companion kext loaded",
            status=fb_status,
            detail="AMDRadeonX5000 / X4000 / companion bundles",
            remediation="Root-patch AMD Vega/Polaris/GCN kexts; check PatcherSupportPkg",
        )
    )

    needs_kdkless = socket_amd_needs_kdkless(model, cpu_generation)
    if not needs_kdkless:
        kdk_status: CheckStatus = "skip"
        kdk_detail = "KDKlessWorkaround not required for this model/CPU gen"
    elif kdkless_enabled is True:
        kdk_status = "pass"
        kdk_detail = "KDKlessWorkaround enabled"
    elif kdkless_enabled is False:
        kdk_status = "fail"
        kdk_detail = "KDKlessWorkaround missing on Mac Pro socket"
    else:
        kdk_status = "unknown"
        kdk_detail = "KDKlessWorkaround not probed"
    items.append(
        FramebufferCheckItem(
            id="kdkless_workaround",
            title="KDKlessWorkaround for Mac Pro socket MTL gaps",
            status=kdk_status,
            detail=kdk_detail,
            remediation="Enable KDKlessWorkaround.kext when MTL bundles are missing",
        )
    )

    failed = [i.id for i in items if i.status == "fail"]
    warns = [i.id for i in items if i.status == "warn"]
    if "agdp_gfx0_pci_path" in failed or path_status == "warn":
        gaps.append(
            "Gap: dual-GPU enumeration can mis-attribute DeviceProperties — "
            "compare ioreg PCI paths to config.plist DeviceProperties.Add keys."
        )
    if agdpmod_present is False:
        gaps.append("Gap: missing agdpmod in boot-args — rebuild EFI or inspect DeviceProperties.")

    return FramebufferChecklistResult(
        model=model,
        gpu_family=family,
        applicable=True,
        items=items,
        failed_ids=failed,
        warn_ids=warns,
        gap_notes=gaps,
    )


def serialize_agdc_framebuffer_fields(
    model: str,
    *,
    gpu_archs: Optional[Iterable[Any]] = None,
    os_version: Optional[str] = None,
    xnu_major: Optional[int] = None,
    assume_tahoe: bool = False,
    agdpmod_present: Optional[bool] = None,
    shikigva_present: Optional[bool] = None,
    agdp_on_correct_gfx0: Optional[bool] = None,
    gfx0_pci_path: Optional[str] = None,
    deviceproperties_paths: Optional[Iterable[str]] = None,
    whatevergreen_loaded: Optional[bool] = None,
    amd_framebuffer_kext_loaded: Optional[bool] = None,
    cpu_generation: Optional[int] = None,
    kdkless_enabled: Optional[bool] = None,
    **_kwargs: Any,
) -> dict[str, Any]:
    """Detect JSON checklist fields (never overwrites yellow_screen_risk)."""
    result = build_macpro_framebuffer_checklist(
        model,
        gpu_archs=gpu_archs,
        os_version=os_version,
        xnu_major=xnu_major,
        assume_tahoe=assume_tahoe,
        agdpmod_present=agdpmod_present,
        shikigva_present=shikigva_present,
        agdp_on_correct_gfx0=agdp_on_correct_gfx0,
        gfx0_pci_path=gfx0_pci_path,
        deviceproperties_paths=deviceproperties_paths,
        whatevergreen_loaded=whatevergreen_loaded,
        amd_framebuffer_kext_loaded=amd_framebuffer_kext_loaded,
        cpu_generation=cpu_generation,
        kdkless_enabled=kdkless_enabled,
    )
    return {
        "agdc_framebuffer_checklist": result.as_dict(),
        "agdc_framebuffer_checklist_applicable": result.applicable,
        "agdc_framebuffer_failed_ids": list(result.failed_ids),
        "agdc_vega64_detected": is_vega64_gpu(gpu_archs),
        "agdc_default_mac_pro_gfx0_path": DEFAULT_MAC_PRO_GFX0_PATH,
        "agdc_gap_doc": AGDP_GAP_DOC,
    }


def serialize_agdc_fields(
    model: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Alias used by optional __init__ imports."""
    return serialize_agdc_framebuffer_fields(model, **kwargs)
