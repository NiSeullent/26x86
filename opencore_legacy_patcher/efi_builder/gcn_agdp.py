"""
EFI agdpmod/shikigva helpers for Tahoe yellow-screen mitigation.

Not GCN-only: Polaris and Vega 64 (Mac Pro aftermarket) hit the same
WindowServer compositor failure. These DeviceProperties/boot-args are
mitigations, not a complete compositor fix.
"""

from __future__ import annotations

STOCK_GCN_AGDP_MODELS = ("iMac15,1", "iMac17,1", "MacPro6,1")
SOCKET_AMD_AGDP_MODELS = ("MacPro3,1", "MacPro4,1", "MacPro5,1", "MacPro6,1", "iMacPro1,1")
APPLE_NVRAM_UUID = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
DEFAULT_GCN_GFX0_PATH = "PciRoot(0x0)/Pci(0x1,0x0)/Pci(0x0,0x0)"


def model_needs_legacy_amd_agdp(model: str) -> bool:
    return model in STOCK_GCN_AGDP_MODELS or model in SOCKET_AMD_AGDP_MODELS


def boot_args_need_gcn_agdp(boot_args: str) -> list[str]:
    extra: list[str] = []
    args = boot_args or ""
    if "agdpmod=" not in args:
        extra.append("agdpmod=vit9696")
    if "shikigva=" not in args:
        extra.append("shikigva=128")
    return extra


def config_has_agdpmod(config: dict) -> bool:
    boot = (
        config.get("NVRAM", {})
        .get("Add", {})
        .get(APPLE_NVRAM_UUID, {})
        .get("boot-args", "")
    )
    if "agdpmod=" in str(boot):
        return True
    for props in config.get("DeviceProperties", {}).get("Add", {}).values():
        if isinstance(props, dict) and "agdpmod" in props:
            return True
    return False


def apply_gcn_agdp_fallbacks(config: dict, gfx0_path: str | None = None) -> dict:
    path = gfx0_path or DEFAULT_GCN_GFX0_PATH
    add_props = config.setdefault("DeviceProperties", {}).setdefault("Add", {})
    entry = add_props.setdefault(path, {})
    entry.setdefault("shikigva", 128)
    entry.setdefault("unfairgva", 1)
    entry.setdefault("agdpmod", "pikera")
    entry.setdefault("rebuild-device-tree", 1)
    entry.setdefault("enable-gva-support", 1)

    nvram_add = config.setdefault("NVRAM", {}).setdefault("Add", {})
    apple = nvram_add.setdefault(APPLE_NVRAM_UUID, {})
    current = str(apple.get("boot-args", "") or "")
    extra = boot_args_need_gcn_agdp(current)
    if extra:
        apple["boot-args"] = (current + " " + " ".join(extra)).strip()
    return config
