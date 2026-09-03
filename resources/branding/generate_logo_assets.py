#!/usr/bin/env python3
"""Generate PNG and .icns assets from the 26x86 master icon image."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

BRANDING_DIR = Path(__file__).resolve().parent
REPO_ROOT = BRANDING_DIR.parent.parent
APP_ICONS_DIR = REPO_ROOT / "payloads" / "Resources" / "AppIcons"
SOURCE_IMAGE = BRANDING_DIR / "26x86-logo-source.jpg"


def load_master() -> Image.Image:
    if not SOURCE_IMAGE.exists():
        raise SystemExit(f"Master image not found: {SOURCE_IMAGE}")
    img = Image.open(SOURCE_IMAGE).convert("RGBA")
    width, height = img.size
    if width != height:
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        img = img.crop((left, top, left + side, top + side))
    return img


def resize(size: int) -> Image.Image:
    return load_master().resize((size, size), resample=Image.LANCZOS)


def write_png(size: int) -> Path:
    out = BRANDING_DIR / f"26x86-logo-{size}.png"
    resize(size).save(out, "PNG")
    return out


def write_icns() -> Path:
    iconset = BRANDING_DIR / "26x86.iconset"
    iconset.mkdir(exist_ok=True)
    sizes = [16, 32, 64, 128, 256, 512]
    for dim in sizes:
        resize(dim).save(iconset / f"icon_{dim}x{dim}.png", "PNG")
        if dim <= 256:
            resize(dim * 2).save(iconset / f"icon_{dim}x{dim}@2x.png", "PNG")

    icns_path = APP_ICONS_DIR / "26x86.icns"
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)],
        check=True,
    )
    return icns_path


def main() -> int:
    for size in (256, 512):
        path = write_png(size)
        print(f"wrote {path}")

    icns = write_icns()
    print(f"wrote {icns}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
