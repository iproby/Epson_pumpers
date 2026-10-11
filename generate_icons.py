#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate high-resolution application icons for macOS (.icns) and Windows (.ico)."""

import os
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw


def create_base_icon(size: int = 1024) -> Image.Image:
    """Render a modern 1024x1024 printer icon with CMYK accents."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background Squircle / Rounded Rectangle
    pad = int(size * 0.08)  # 80px pad
    corner_radius = int(size * 0.22)  # 225px corner radius
    bg_box = [pad, pad, size - pad, size - pad]

    # Draw soft shadow
    shadow_offset = int(size * 0.02)
    shadow_box = [pad, pad + shadow_offset, size - pad, size - pad + shadow_offset]
    draw.rounded_rectangle(shadow_box, radius=corner_radius, fill=(15, 20, 25, 120))

    # Base gradient fill (approx with rounded rectangle)
    draw.rounded_rectangle(bg_box, radius=corner_radius, fill=(28, 37, 48, 255), outline=(52, 73, 94, 255), width=int(size * 0.008))

    # 2. Printer Body (White / Metallic silver)
    pr_left = int(size * 0.22)
    pr_top = int(size * 0.40)
    pr_right = int(size * 0.78)
    pr_bottom = int(size * 0.74)
    pr_radius = int(size * 0.04)

    # Printer base shadow
    draw.rounded_rectangle(
        [pr_left, pr_top + int(size * 0.01), pr_right, pr_bottom + int(size * 0.01)],
        radius=pr_radius,
        fill=(10, 15, 20, 100),
    )
    # Printer main body
    draw.rounded_rectangle(
        [pr_left, pr_top, pr_right, pr_bottom],
        radius=pr_radius,
        fill=(245, 246, 250, 255),
        outline=(210, 218, 226, 255),
        width=int(size * 0.005),
    )

    # 3. Paper Output Slot
    slot_left = int(size * 0.30)
    slot_top = int(size * 0.52)
    slot_right = int(size * 0.70)
    slot_bottom = int(size * 0.56)
    draw.rounded_rectangle([slot_left, slot_top, slot_right, slot_bottom], radius=int(size * 0.01), fill=(47, 53, 66, 255))

    # 4. Printed Page coming out of slot
    page_left = int(size * 0.34)
    page_top = int(size * 0.54)
    page_right = int(size * 0.66)
    page_bottom = int(size * 0.68)
    draw.rectangle([page_left, page_top, page_right, page_bottom], fill=(255, 255, 255, 255), outline=(220, 221, 225, 255), width=2)

    # Text lines on page
    for offset_y in [0.57, 0.60, 0.63]:
        ly = int(size * offset_y)
        draw.line([(int(size * 0.37), ly), (int(size * 0.63), ly)], fill=(180, 190, 200, 255), width=int(size * 0.006))

    # 5. Top Paper Feed Tray & Paper Input
    tray_left = int(size * 0.32)
    tray_top = int(size * 0.24)
    tray_right = int(size * 0.68)
    tray_bottom = pr_top + int(size * 0.02)
    draw.rounded_rectangle([tray_left, tray_top, tray_right, tray_bottom], radius=int(size * 0.02), fill=(220, 225, 235, 255))

    # 6. CMYK Indicator Dots (Cyan, Magenta, Yellow, Key/Black)
    cmyk_colors = [
        (0, 168, 255),   # Cyan
        (232, 67, 147),  # Magenta
        (241, 196, 15),  # Yellow
        (44, 62, 80),    # Black
    ]
    dot_radius = int(size * 0.022)
    dot_y = int(size * 0.46)
    spacing = int(size * 0.065)
    start_x = int(size * 0.40)

    for i, color in enumerate(cmyk_colors):
        cx = start_x + (i * spacing)
        draw.ellipse([cx - dot_radius, dot_y - dot_radius, cx + dot_radius, dot_y + dot_radius], fill=color + (255,))

    # 7. Status LED (Green glowing dot)
    led_x = int(size * 0.27)
    led_y = int(size * 0.46)
    led_radius = int(size * 0.014)
    # Glow
    draw.ellipse([led_x - led_radius * 2, led_y - led_radius * 2, led_x + led_radius * 2, led_y + led_radius * 2], fill=(46, 204, 113, 60))
    # Core
    draw.ellipse([led_x - led_radius, led_y - led_radius, led_x + led_radius, led_y + led_radius], fill=(46, 204, 113, 255))

    return img


def generate_icons():
    project_root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(project_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    print("Generating base 1024x1024 icon image...")
    base_img = create_base_icon(1024)
    base_png = os.path.join(assets_dir, "icon_1024.png")
    base_img.save(base_png, "PNG")

    # Save Windows .ico with multi-resolution
    ico_path = os.path.join(assets_dir, "app_icon.ico")
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base_img.save(ico_path, format="ICO", sizes=ico_sizes)
    print(f"✓ Created Windows icon: {ico_path}")

    # Generate macOS .icns if on macOS and iconutil is available
    icns_path = os.path.join(assets_dir, "app_icon.icns")
    if sys.platform == "darwin" and shutil.which("iconutil"):
        print("Generating macOS .icns using iconutil...")
        iconset_dir = os.path.join(assets_dir, "app_icon.iconset")
        if os.path.exists(iconset_dir):
            shutil.rmtree(iconset_dir)
        os.makedirs(iconset_dir)

        sizes_mapping = [
            ("icon_16x16.png", 16),
            ("icon_16x16@2x.png", 32),
            ("icon_32x32.png", 32),
            ("icon_32x32@2x.png", 64),
            ("icon_128x128.png", 128),
            ("icon_128x128@2x.png", 256),
            ("icon_256x256.png", 256),
            ("icon_256x256@2x.png", 512),
            ("icon_512x512.png", 512),
            ("icon_512x512@2x.png", 1024),
        ]

        for filename, px in sizes_mapping:
            resized = base_img.resize((px, px), Image.Resampling.LANCZOS)
            resized.save(os.path.join(iconset_dir, filename), "PNG")

        subprocess.check_call(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path])
        shutil.rmtree(iconset_dir)
        print(f"✓ Created macOS icon: {icns_path}")
    else:
        # Fallback copy base png
        base_img.resize((512, 512)).save(icns_path, "PNG")


if __name__ == "__main__":
    generate_icons()
