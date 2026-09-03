#!/usr/bin/env python3
"""
Fetch / stage ``RenderBox-25/.../default.metallib`` for Track E.

Public PatcherSupportPkg trees (Dortania, YBronst 2.0.0, hackdoc, NiSeullent)
currently ship RenderBox-22..24 only — no authentic Tahoe RenderBox-25.

Strategy (no invented metallib bytes):
  1. Probe GitHub raw / Contents API mirrors for ``RenderBox-25``.
  2. Optionally mount known Universal-Binaries.dmg releases and search.
  3. ``--provisional-from-24``: copy local ``RenderBox-24`` MTLB into the
     Community overlay slot with SOURCE provenance (Sequoia-era ABI —
     research / path-validation only until a real Tahoe payload appears).

Never commits Apple binaries (overlay ``Universal-Binaries/.gitignore``).
Never touches ESP / sudo EFI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from x86.graphics.skylight_lut import RENDERBOX_METALLIB_RELATIVE  # noqa: E402

METALLIB_MAGIC = b"MTLB"
REL = Path(RENDERBOX_METALLIB_RELATIVE)
DEST_DIR_NAME = "RenderBox-25"

# Ordered mirrors — authentic Tahoe payload first if/when published.
GITHUB_RAW_CANDIDATES: tuple[str, ...] = (
    "https://raw.githubusercontent.com/NiSeullent/26x86-PatcherSupportPkg/main/"
    f"Universal-Binaries/{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}",
    "https://raw.githubusercontent.com/hackdoc/PatcherSupportPkg/main/"
    f"Universal-Binaries/{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}",
    "https://raw.githubusercontent.com/dortania/PatcherSupportPkg/main/"
    f"Universal-Binaries/{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}",
    "https://raw.githubusercontent.com/YBronst/PatcherSupportPkg/main/"
    f"Universal-Binaries/{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}",
    "https://raw.githubusercontent.com/albert-mueller/PatcherSupportPkg/main/"
    f"Universal-Binaries/{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}",
    "https://raw.githubusercontent.com/laobamac/PatcherSupportPkg/main/"
    f"Universal-Binaries/{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}",
    "https://raw.githubusercontent.com/kgp-macPro/PatcherSupportPkg-laobamac/main/"
    f"Universal-Binaries/{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}",
    "https://raw.githubusercontent.com/dortania/PatcherSupportPkg/macos-next/"
    f"Universal-Binaries/{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}",
)

DMG_CANDIDATES: tuple[tuple[str, str], ...] = (
    (
        "YBronst/PatcherSupportPkg@2.0.0",
        "https://github.com/YBronst/PatcherSupportPkg/releases/download/2.0.0/Universal-Binaries.dmg",
    ),
    (
        "laobamac/PatcherSupportPkg@2.0.0",
        "https://github.com/laobamac/PatcherSupportPkg/releases/download/2.0.0/Universal-Binaries.dmg",
    ),
    (
        "hackdoc/PatcherSupportPkg@1.11.6",
        "https://github.com/hackdoc/PatcherSupportPkg/releases/download/1.11.6/Universal-Binaries.dmg",
    ),
    (
        "dortania/PatcherSupportPkg@1.9.7",
        "https://github.com/dortania/PatcherSupportPkg/releases/download/1.9.7/Universal-Binaries.dmg",
    ),
)

SOURCE_DOC = """# RenderBox-25 payload slot (Track E)

## License / provenance

| 항목 | 내용 |
|------|------|
| Binary | Apple proprietary ``default.metallib`` (RenderBox.framework) |
| Redistribution | **Do not commit** the metallib — gitignored under this tree |
| Upstream pattern | OCLP Metal 31001 / [PR #1176](https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1176) |
| Authentic Tahoe | *Not published* on Dortania/YBronst/hackdoc/NiSeullent as of 2026-09-04 |

## Staging modes

1. **Authentic** — drop a real ``RenderBox-25`` tree from future PSP DRAFT / OCLP nightly.
2. **Provisional** — ``Tools/fetch_renderbox25.py --provisional-from-24`` copies
   Sequoia ``RenderBox-24`` MTLB here for **path / gate validation only**.
   Liquid Glass ABI may still be wrong on Tahoe; treat as research.

## Acquire

```bash
python Tools/fetch_renderbox25.py            # try public mirrors + DMGs
python Tools/fetch_renderbox25.py --provisional-from-24
python Tools/check_extreme_payloads.py
```
"""


def overlay_root() -> Path:
    return (
        REPO
        / "payloads"
        / "Kexts"
        / "Community"
        / "Tahoe-Yellow-Screen"
        / "Universal-Binaries"
    )


def sibling_psp() -> Path:
    return REPO.parent / "26x86-PatcherSupportPkg" / "Universal-Binaries"


def dest_metallib(root: Path) -> Path:
    return root / DEST_DIR_NAME / REL


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_metallib(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, "missing"
    size = path.stat().st_size
    if size <= 0:
        return False, "empty"
    with path.open("rb") as handle:
        magic = handle.read(4)
    if magic != METALLIB_MAGIC:
        return False, f"bad_magic={magic!r}"
    return True, f"ok size={size} sha256={sha256_file(path)[:16]}…"


def http_get(url: str, dest: Path, timeout: int = 60) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "26x86-fetch-renderbox25"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if not data:
            return {"url": url, "ok": False, "error": "empty body"}
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        ok, detail = validate_metallib(dest)
        return {"url": url, "ok": ok, "detail": detail, "bytes": len(data)}
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"url": url, "ok": False, "error": str(exc)}


def try_raw_mirrors(dest: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for url in GITHUB_RAW_CANDIDATES:
        print(f"try raw: {url}", file=sys.stderr)
        hit = http_get(url, dest)
        results.append(hit)
        if hit.get("ok"):
            break
        if dest.exists():
            dest.unlink(missing_ok=True)
    return results


def _hdiutil_attach(dmg: Path) -> Optional[Path]:
    try:
        out = subprocess.check_output(
            ["/usr/bin/hdiutil", "attach", "-nobrowse", "-readonly", str(dmg)],
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"hdiutil attach failed: {exc}", file=sys.stderr)
        return None
    vol: Optional[Path] = None
    for line in out.splitlines():
        if "/Volumes/" in line:
            vol = Path(line[line.index("/Volumes/") :].strip())
    return vol


def _hdiutil_detach(vol: Path) -> None:
    try:
        subprocess.run(
            ["/usr/bin/hdiutil", "detach", str(vol), "-quiet"],
            check=False,
            capture_output=True,
        )
    except OSError:
        pass


def try_dmg_mirrors(
    dest: Path, *, cache_dir: Path, skip_dmg: bool = False
) -> list[dict[str, Any]]:
    if skip_dmg:
        return [{"skipped": True, "reason": "--skip-dmg"}]
    results: list[dict[str, Any]] = []
    cache_dir.mkdir(parents=True, exist_ok=True)
    for label, url in DMG_CANDIDATES:
        print(f"try dmg: {label}", file=sys.stderr)
        dmg_path = cache_dir / f"{label.replace('/', '_')}.dmg"
        entry: dict[str, Any] = {"label": label, "url": url}
        if not dmg_path.is_file() or dmg_path.stat().st_size < 1_000_000:
            try:
                # Large downloads — use curl for progress / resume.
                subprocess.check_call(
                    [
                        "/usr/bin/curl",
                        "-L",
                        "--fail",
                        "--retry",
                        "2",
                        "-o",
                        str(dmg_path),
                        url,
                    ]
                )
            except (OSError, subprocess.CalledProcessError) as exc:
                entry["ok"] = False
                entry["error"] = f"download failed: {exc}"
                results.append(entry)
                continue
        vol = _hdiutil_attach(dmg_path)
        if vol is None:
            entry["ok"] = False
            entry["error"] = "attach failed"
            results.append(entry)
            continue
        try:
            found = vol / DEST_DIR_NAME / REL
            if not found.is_file():
                # Some images nest under Universal-Binaries/
                alt = list(vol.rglob(f"{DEST_DIR_NAME}/{RENDERBOX_METALLIB_RELATIVE}"))
                found = alt[0] if alt else found
            if found.is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(found, dest)
                ok, detail = validate_metallib(dest)
                entry["ok"] = ok
                entry["detail"] = detail
                entry["source"] = str(found)
                results.append(entry)
                if ok:
                    return results
            else:
                entry["ok"] = False
                entry["error"] = f"{DEST_DIR_NAME} absent in DMG"
                # Note nearby RenderBox-* for operators
                nearby = sorted(
                    {p.name for p in vol.glob("RenderBox-*") if p.is_dir()}
                )
                entry["nearby_renderbox"] = nearby
                results.append(entry)
        finally:
            _hdiutil_detach(vol)
    return results


def find_local_renderbox24() -> Optional[Path]:
    candidates = [
        sibling_psp() / "RenderBox-24" / REL,
        overlay_root() / "RenderBox-24" / REL,
        REPO / "payloads" / "Kexts" / "Universal-Binaries" / "RenderBox-24" / REL,
    ]
    for path in candidates:
        ok, _ = validate_metallib(path)
        if ok:
            return path
    return None


def provisional_from_24(dest: Path) -> dict[str, Any]:
    src = find_local_renderbox24()
    if src is None:
        return {
            "ok": False,
            "error": "no local RenderBox-24 metallib (need sibling PSP)",
        }
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    tree_root = dest
    while tree_root.name != DEST_DIR_NAME and tree_root != tree_root.parent:
        tree_root = tree_root.parent
    marker = tree_root / "PROVISIONAL_FROM_RENDERBOX_24"
    marker.write_text(
        "Staged from RenderBox-24 (Sequoia). Not an authentic Tahoe metallib.\n"
        f"source={src}\n"
        f"sha256={sha256_file(dest)}\n",
        encoding="utf-8",
    )
    ok, detail = validate_metallib(dest)
    return {
        "ok": ok,
        "detail": detail,
        "source": str(src),
        "provisional": True,
        "marker": str(marker),
    }


def write_source_readme(root: Path) -> None:
    tree = root / DEST_DIR_NAME
    tree.mkdir(parents=True, exist_ok=True)
    (tree / "SOURCE.md").write_text(SOURCE_DOC, encoding="utf-8")
    (tree / "README.md").write_text(
        "Slot for RenderBox-25 default.metallib. See SOURCE.md. Binary gitignored.\n",
        encoding="utf-8",
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provisional-from-24",
        action="store_true",
        help="Copy local RenderBox-24 MTLB into RenderBox-25 slot (research)",
    )
    parser.add_argument(
        "--skip-dmg",
        action="store_true",
        help="Skip large Universal-Binaries.dmg downloads",
    )
    parser.add_argument(
        "--also-sibling-psp",
        action="store_true",
        help="Also stage into ../26x86-PatcherSupportPkg/Universal-Binaries",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "26x86-psp-cache",
    )
    args = parser.parse_args(argv)

    overlay = overlay_root()
    dest = dest_metallib(overlay)
    write_source_readme(overlay)

    report: dict[str, Any] = {
        "dest": str(dest),
        "attempts": {},
        "final_ok": False,
        "provisional": False,
    }

    raw = try_raw_mirrors(dest)
    report["attempts"]["raw"] = raw
    if any(x.get("ok") for x in raw):
        report["final_ok"] = True
        report["mode"] = "authentic_raw"
    else:
        dmg = try_dmg_mirrors(dest, cache_dir=args.cache_dir, skip_dmg=args.skip_dmg)
        report["attempts"]["dmg"] = dmg
        if any(x.get("ok") for x in dmg):
            report["final_ok"] = True
            report["mode"] = "authentic_dmg"

    if not report["final_ok"] and args.provisional_from_24:
        prov = provisional_from_24(dest)
        report["attempts"]["provisional_from_24"] = prov
        report["final_ok"] = bool(prov.get("ok"))
        report["provisional"] = bool(prov.get("provisional"))
        report["mode"] = "provisional_from_24" if report["final_ok"] else "failed"

    if report["final_ok"] and args.also_sibling_psp and sibling_psp().is_dir():
        sib = dest_metallib(sibling_psp())
        sib.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, sib)
        write_source_readme(sibling_psp())
        report["sibling_psp"] = str(sib)

    ok, detail = validate_metallib(dest) if dest.is_file() else (False, "missing")
    report["validate"] = detail
    report["final_ok"] = ok
    print(json.dumps(report, indent=2, default=str))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
