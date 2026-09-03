#!/usr/bin/env python3
"""Generate PNG and .icns assets from the 26x86 M→N logo geometry."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

BRANDING_DIR = Path(__file__).resolve().parent
REPO_ROOT = BRANDING_DIR.parent.parent
APP_ICONS_DIR = REPO_ROOT / "payloads" / "Resources" / "AppIcons"

FILL = (26, 29, 38, 255)  # #1A1D26


def baseline_y(x: float) -> float:
    return 76.0 + (x - 8.0) * (18.0 / 104.0)


def letter_points(scale: float) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    m = [
        (10, baseline_y(10)),
        (10, 22),
        (30, 22),
        (40, baseline_y(40)),
        (50, 22),
        (70, 22),
        (70, baseline_y(70)),
    ]
    n = [
        (70, baseline_y(70)),
        (70, 22),
        (104, baseline_y(104)),
        (104, 22),
        (118, 8),
        (108, 30),
        (104, 30),
        (104, baseline_y(104)),
    ]
    s = scale / 128.0
    return (
        [(x * s, y * s) for x, y in m],
        [(x * s, y * s) for x, y in n],
    )


def render_png(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    m_pts, n_pts = letter_points(float(size))
    draw.polygon(m_pts, fill=FILL)
    draw.polygon(n_pts, fill=FILL)
    return img


def write_png(size: int) -> Path:
    out = BRANDING_DIR / f"26x86-logo-{size}.png"
    render_png(size).save(out, "PNG")
    return out


def write_icns() -> Path:
    iconset = BRANDING_DIR / "26x86.iconset"
    iconset.mkdir(exist_ok=True)
    sizes = [16, 32, 64, 128, 256, 512]
    for dim in sizes:
        img = render_png(dim)
        img.save(iconset / f"icon_{dim}x{dim}.png", "PNG")
        if dim <= 256:
            img2x = render_png(dim * 2)
            img2x.save(iconset / f"icon_{dim}x{dim}@2x.png", "PNG")

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
