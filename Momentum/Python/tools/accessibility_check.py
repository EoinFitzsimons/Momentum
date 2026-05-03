"""Small CLI to print contrast ratios for accessibility themes."""

import os
import sys
import re

# Ensure Momentum/Python is on sys.path when run as a script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from GUI.accessibility_settings import get_theme_stylesheet


def _extract_first_bg_fg(css: str):
    bg_match = re.search(r"background-color:\s*#([0-9A-Fa-f]{6})", css)
    fg_match = re.search(r"color:\s*#([0-9A-Fa-f]{6})", css)
    bg = f"#{bg_match.group(1)}" if bg_match else None
    fg = f"#{fg_match.group(1)}" if fg_match else None
    return bg, fg


def _hex_to_linear_luminance(hexcol: str) -> float:
    h = hexcol.lstrip("#")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0

    def to_lin(c):
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    R = to_lin(r)
    G = to_lin(g)
    B = to_lin(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def _contrast_ratio(hex1: str, hex2: str) -> float:
    L1 = _hex_to_linear_luminance(hex1)
    L2 = _hex_to_linear_luminance(hex2)
    lighter = max(L1, L2)
    darker = min(L1, L2)
    return (lighter + 0.05) / (darker + 0.05)


def main():
    for theme in ("standard", "high_contrast", "colorblind_safe"):
        css = get_theme_stylesheet(theme)
        bg, fg = _extract_first_bg_fg(css)
        print(f"Theme: {theme}")
        print(f"  background: {bg}, foreground: {fg}")
        if bg and fg:
            print(f"  contrast ratio: {_contrast_ratio(bg, fg):.2f}")
        else:
            print("  Could not parse bg/fg for this theme")


if __name__ == "__main__":
    main()
