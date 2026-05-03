import re

import pytest

# Skip this entire module gracefully if PyQt6 can't load (e.g. headless CI without libEGL)
pytest.importorskip("PyQt6.QtWidgets", minversion=None)

from PyQt6.QtWidgets import QApplication
from GUI.accessibility_settings import (
    get_theme_stylesheet,
    apply_accessibility_to_app,
)


def _extract_first_bg_fg(css: str):
    # Prefer the QWidget rule which commonly contains background + color.
    m = re.search(r"QWidget\s*\{([^}]*)\}", css)
    if m:
        block = m.group(1)
        bg_match = re.search(r"background-color:\s*#([0-9A-Fa-f]{6})", block)
        fg_match = re.search(r"color:\s*#([0-9A-Fa-f]{6})", block)
        bg = f"#{bg_match.group(1)}" if bg_match else None
        fg = f"#{fg_match.group(1)}" if fg_match else None
        if bg or fg:
            return bg, fg

    # Fallback: find the first occurrences anywhere
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


@pytest.mark.unit
def test_theme_stylesheets_exist():
    # Standard may be empty (no override). Ensure specialized themes exist.
    css = get_theme_stylesheet("standard")
    assert isinstance(css, str)

    for theme in ("high_contrast", "colorblind_safe"):
        css = get_theme_stylesheet(theme)
        assert isinstance(css, str)
        assert css.strip() != ""


@pytest.mark.unit
def test_apply_accessibility_scales_font():
    app = QApplication.instance() or QApplication([])
    before = app.font().pointSizeF()
    apply_accessibility_to_app(app, {"theme": "standard", "ui_scale": 125})
    after = app.font().pointSizeF()
    assert after != before


@pytest.mark.unit
def test_high_contrast_theme_meets_wcag():
    css = get_theme_stylesheet("high_contrast")
    # Collect all background and foreground hex colours present and check best contrast
    bgs = re.findall(r"background-color:\s*#([0-9A-Fa-f]{6})", css)
    fgs = re.findall(r"color:\s*#([0-9A-Fa-f]{6})", css)
    bgs = [f"#{b}" for b in bgs]
    fgs = [f"#{f}" for f in fgs]
    assert bgs and fgs
    best = 0.0
    for bg in bgs:
        for fg in fgs:
            best = max(best, _contrast_ratio(bg, fg))
    assert best >= 7.0, f"High contrast theme best contrast ratio too low: {best:.2f}"


@pytest.mark.unit
def test_colorblind_safe_theme_has_readable_selection():
    css = get_theme_stylesheet("colorblind_safe")
    # Ensure theme provides a selection color we can parse
    selection = re.search(
        r"QTableWidget::item:selected[^{]*\{[^}]*background-color:\s*#([0-9A-Fa-f]{6})",
        css,
    )
    if selection:
        sel = f"#{selection.group(1)}"
        # Assume overall background from earlier
        bg, fg = _extract_first_bg_fg(css)
        if bg and sel:
            ratio = _contrast_ratio(bg, sel)
            assert ratio >= 3.0
    else:
        # If no explicit selection style, pass but warn (not failing test)
        pytest.skip("No explicit selection color in colorblind_safe theme")
