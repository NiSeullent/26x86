"""
Track F — PatcherSupportPkg Tahoe kext overlay (12.5-25 / 12.5-26).

Owned by skylight-F. Mount-time injection is proposed in
``dmg_mount.py.stage-F`` (MC integrates). Missing payload → operator guidance.
Does not redistribute Apple proprietary binaries.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional

TAHOE_MTL_PAYLOAD_PREFERRED = "12.5-25"
TAHOE_MTL_PAYLOAD_FALLBACK = "12.5-24"
TAHOE_PSP_VERSION_DIRS: tuple[str, ...] = ("12.5-25", "12.5-26")

COMMUNITY_YELLOW_SCREEN_RELATIVE = (
    "payloads/Kexts/Community/Tahoe-Yellow-Screen/Universal-Binaries"
)

TAHOE_PSP_YELLOW_SCREEN_MTL_BUNDLES: tuple[str, ...] = (
    "AMDMTLBronzeDriver.bundle",
    "AMDRadeonX5000MTLDriver.bundle",
)

TAHOE_PSP_YELLOW_SCREEN_COMPANION_HINTS: tuple[str, ...] = (
    "AMDRadeonX4000.kext",
    "AMDRadeonX4000HWServices.kext",
    "AMDRadeonX5000.kext",
    "AMDRadeonX5000HWServices.kext",
    "AMDFramebuffer.kext",
    "AMDShared.bundle",
    "AMDRadeonX5000Shared.bundle",
)

PSP_PR_16_URL = "https://github.com/dortania/PatcherSupportPkg/pull/16"
PSP_PR_18_URL = "https://github.com/dortania/PatcherSupportPkg/pull/18"
PSP_OVERLAY_DOWNLOAD_DOC = (
    "payloads/Kexts/Community/Tahoe-Yellow-Screen/SOURCE.md"
)

OVERLAY_MISSING_GUIDANCE: tuple[str, ...] = (
    "Tahoe Yellow Screen 오버레이(12.5-25/12.5-26 MTL)가 없습니다. "
    "루트패치는 12.5-24 fallback을 쓰며 GPUCompanionBundles 공백(OCLP-T2 #194)이 남을 수 있습니다.",
    "필요 MTL: "
    + ", ".join(TAHOE_PSP_YELLOW_SCREEN_MTL_BUNDLES)
    + f" — 출처: PSP #16 ({PSP_PR_16_URL}), Tahoe 트리: PSP #18 ({PSP_PR_18_URL}).",
    "Apple 바이너리는 재배포하지 않습니다. 확보 후 "
    + f"{COMMUNITY_YELLOW_SCREEN_RELATIVE}/12.5-25/System/Library/Extensions/ "
    + "아래에 두거나 sibling 26x86-PatcherSupportPkg Universal-Binaries에 배치하세요. "
    + f"절차: {PSP_OVERLAY_DOWNLOAD_DOC}",
)


def community_yellow_screen_overlay() -> Path:
    from x86.paths import Paths
    return Paths.repo_root() / COMMUNITY_YELLOW_SCREEN_RELATIVE


def default_psp_binaries_roots() -> list[Path]:
    from x86.paths import Paths
    return [
        community_yellow_screen_overlay(),
        Paths.universal_binaries_mount(),
        Paths.repo_root().parent / "26x86-PatcherSupportPkg" / "Universal-Binaries",
    ]


def version_dir_has_injectable_payload(version_dir: Path) -> bool:
    try:
        if not version_dir.is_dir():
            return False
        for path in version_dir.rglob("*"):
            if not path.is_file():
                continue
            name = path.name.lower()
            if name in {".gitkeep", "readme.md", "readme.txt", ".ds_store"}:
                continue
            if name.endswith((".md", ".txt", ".gitignore")):
                continue
            return True
    except OSError:
        return False
    return False


def discover_tahoe_psp_overlay_versions(
    search_roots: Optional[Iterable[Path]] = None,
) -> list[str]:
    roots = [Path(p) for p in (search_roots if search_roots is not None else default_psp_binaries_roots())]
    found: list[str] = []
    for version in TAHOE_PSP_VERSION_DIRS:
        for root in roots:
            if version_dir_has_injectable_payload(root / version):
                found.append(version)
                break
    return found


def tahoe_psp_mtl_bundles_present(
    version: str,
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, bool]:
    roots = [Path(p) for p in (search_roots if search_roots is not None else default_psp_binaries_roots())]
    result: dict[str, bool] = {}
    for bundle in TAHOE_PSP_YELLOW_SCREEN_MTL_BUNDLES:
        present = False
        for root in roots:
            candidate = root / version / "System/Library/Extensions" / bundle
            try:
                if candidate.exists():
                    present = True
                    break
            except OSError:
                continue
        result[bundle] = present
    return result


def tahoe_psp_overlay_status(
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, Any]:
    roots = [Path(p) for p in (search_roots if search_roots is not None else default_psp_binaries_roots())]
    versions = discover_tahoe_psp_overlay_versions(roots)
    mtl_by_version = {v: tahoe_psp_mtl_bundles_present(v, roots) for v in versions}
    any_mtl = any(any(f.values()) for f in mtl_by_version.values()) if mtl_by_version else False
    present = bool(versions)
    guidance = [] if present and any_mtl else list(OVERLAY_MISSING_GUIDANCE)
    if present and not any_mtl:
        guidance = [
            "오버레이 폴더 " + ", ".join(versions)
            + "는 있으나 노란 화면 MTL 번들("
            + ", ".join(TAHOE_PSP_YELLOW_SCREEN_MTL_BUNDLES) + ")이 없습니다.",
            *OVERLAY_MISSING_GUIDANCE[1:],
        ]
    return {
        "present": present,
        "versions_found": versions,
        "mtl_bundles": mtl_by_version,
        "expected_mtl_bundles": list(TAHOE_PSP_YELLOW_SCREEN_MTL_BUNDLES),
        "companion_kext_hints": list(TAHOE_PSP_YELLOW_SCREEN_COMPANION_HINTS),
        "mtl_payload_preferred": TAHOE_MTL_PAYLOAD_PREFERRED,
        "mtl_payload_fallback": TAHOE_MTL_PAYLOAD_FALLBACK,
        "guidance": guidance,
        "psp_pr_16": PSP_PR_16_URL,
        "psp_pr_18": PSP_PR_18_URL,
        "download_doc": PSP_OVERLAY_DOWNLOAD_DOC,
    }


def format_tahoe_psp_overlay_missing_message(
    search_roots: Optional[Iterable[Path]] = None,
) -> str:
    status = tahoe_psp_overlay_status(search_roots)
    if status["present"] and not status["guidance"]:
        return ""
    return " | ".join(status["guidance"] or OVERLAY_MISSING_GUIDANCE)


def tahoe_psp_version_copy_pairs(
    dest_root: Path,
    search_roots: Optional[Iterable[Path]] = None,
) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    dest = Path(dest_root)
    roots = [Path(p) for p in (search_roots if search_roots is not None else default_psp_binaries_roots())]
    seen: set[str] = set()
    for root in roots:
        try:
            if dest.exists() and root.exists() and root.resolve() == dest.resolve():
                continue
        except OSError:
            continue
        for version in TAHOE_PSP_VERSION_DIRS:
            src = root / version
            key = str(src)
            if key in seen:
                continue
            try:
                if version_dir_has_injectable_payload(src):
                    seen.add(key)
                    pairs.append((src, dest / version))
            except OSError:
                continue
    return pairs


def merge_tahoe_psp_overlay_into_detect(
    payload: dict[str, Any],
    search_roots: Optional[Iterable[Path]] = None,
) -> dict[str, Any]:
    overlay = tahoe_psp_overlay_status(search_roots)
    payload["tahoe_psp_overlay"] = overlay
    notes = payload.get("yellow_screen_notes")
    if isinstance(notes, list):
        for line in overlay.get("guidance") or []:
            if line and line not in notes:
                notes.append(line)
    return payload


def sys_patch_hooks(xnu_major: int, xnu_minor: int, marketing_version: str) -> dict:
    del xnu_major, xnu_minor, marketing_version
    return {}


def serialize_track_detect_fields(model: str = "", **kwargs: Any) -> dict[str, Any]:
    search = kwargs.get("psp_search_paths") or kwargs.get("search_roots")
    return {"tahoe_psp_overlay": tahoe_psp_overlay_status(search)}
