#!/usr/bin/env python3
"""Generate PNG and .icns assets from the 26x86 M→N logo geometry."""

from __future__ import annotations

import subprocess
import sys
import math
from pathlib import Path

from PIL import Image, ImageDraw

BRANDING_DIR = Path(__file__).resolve().parent
REPO_ROOT = BRANDING_DIR.parent.parent
APP_ICONS_DIR = REPO_ROOT / "payloads" / "Resources" / "AppIcons"

FILL = (26, 29, 38, 255)  # #1A1D26
BG_C0 = (242, 243, 247)  # very light gray
BG_C1 = (222, 233, 252)  # softer pale blue
BG_C2 = (226, 212, 252)  # softer pale lavender


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
    """
    Render the 26x86 M→N logo at a given square size.

    The foreground arrow geometry stays identical to the original logo,
    while the symbol background is a soft radial gradient clipped to a circle.
    """
    # Small sizes need supersampling to keep M/N joins and caps crisp.
    supersample = 4 if size <= 64 else 1
    render_size = size * supersample

    img = Image.new("RGBA", (render_size, render_size), (0, 0, 0, 0))
    px = img.load()

    # Keep consistent with 26x86-logo.svg: circle r=60 in viewBox 0..128.
    cx = cy = (render_size / 2.0)
    r = render_size * (60.0 / 128.0)

    # Gentle edge smoothing (sub-pixel-ish) to avoid harsh aliasing.
    edge = max(1.0, render_size * (2.0 / 128.0))

    # Gradient focal point (cx/cy = 35%/30% in svg).
    gx = render_size * 0.35
    gy = render_size * 0.30

    def lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def mix_rgb(c0: tuple[int, int, int], c1: tuple[int, int, int], t: float) -> tuple[int, int, int]:
        return (
            int(round(lerp(c0[0], c1[0], t))),
            int(round(lerp(c0[1], c1[1], t))),
            int(round(lerp(c0[2], c1[2], t))),
        )

    for y in range(render_size):
        y0 = y + 0.5
        for x in range(render_size):
            x0 = x + 0.5

            # Circle mask with smooth alpha.
            dc = math.hypot(x0 - cx, y0 - cy)
            if dc > r + edge:
                continue
            a = (r + edge - dc) / edge
            a = max(0.0, min(1.0, a))
            alpha = int(round(255.0 * a))

            # Radial gradient value 0..1, normalized by circle radius.
            dg = math.hypot(x0 - gx, y0 - gy)
            t = min(1.0, dg / r)

            # 3-stop blend: gray -> blue -> lavender.
            if t < 0.55:
                u = t / 0.55
                rgb = mix_rgb(BG_C0, BG_C1, u)
            else:
                u = (t - 0.55) / 0.45
                rgb = mix_rgb(BG_C1, BG_C2, u)

            px[x, y] = (rgb[0], rgb[1], rgb[2], alpha)

    # Foreground: keep arrow geometry unchanged.
    draw = ImageDraw.Draw(img)
    m_pts, n_pts = letter_points(float(render_size))
    draw.polygon(m_pts, fill=FILL)
    draw.polygon(n_pts, fill=FILL)

    if supersample != 1:
        img = img.resize((size, size), resample=Image.LANCZOS)
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
