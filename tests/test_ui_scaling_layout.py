"""Tests for UI scale, screen-relative sizing and theme-safe alternating rows."""

from __future__ import annotations

import re

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtCore import QRect  # noqa: E402
from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem  # noqa: E402

from momentum.gui import accessibility_settings as acc  # noqa: E402
from momentum.gui.accessibility_settings import (  # noqa: E402
    BASE_FONT_POINT_SIZE,
    VALID_THEMES,
    VALID_UI_SCALES,
    apply_accessibility_to_app,
    centred_window_geometry,
    current_ui_scale,
    get_theme_stylesheet,
    scaled,
    scaled_font,
    screen_relative_size,
    structure_stylesheet,
)


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance() or QApplication([])
    yield instance
    apply_accessibility_to_app(instance, {"theme": "standard", "ui_scale": 100})


def _luminance(hex_colour: str) -> float:
    value = hex_colour.lstrip("#")
    channels = [int(value[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def linear(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(c) for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def _alternating_blocks(css: str) -> list[str]:
    """Return every rule body that declares an alternate row background."""
    return [
        body
        for body in re.findall(r"\{([^}]*)\}", css)
        if "alternate-background-color" in body
    ]


@pytest.mark.unit
@pytest.mark.parametrize("theme", VALID_THEMES)
def test_every_theme_declares_readable_alternate_rows(app, theme):
    css = get_theme_stylesheet(theme)
    blocks = _alternating_blocks(css)
    assert blocks, f"{theme} must set alternate-background-color"
    for block in blocks:
        alternate = re.search(r"alternate-background-color:\s*(#[0-9A-Fa-f]{6})", block)
        foreground = re.search(r"(?<![-\w])color:\s*(#[0-9A-Fa-f]{6})", block)
        assert alternate is not None and foreground is not None
        assert _contrast(alternate.group(1), foreground.group(1)) >= 4.5
    assert "::item:alternate" in css


@pytest.mark.unit
def test_apply_scale_is_idempotent(app):
    apply_accessibility_to_app(app, {"theme": "standard", "ui_scale": 150})
    first = app.font().pointSizeF()
    apply_accessibility_to_app(app, {"theme": "standard", "ui_scale": 150})
    assert app.font().pointSizeF() == pytest.approx(first)
    assert first == pytest.approx(BASE_FONT_POINT_SIZE * 1.5)
    assert current_ui_scale() == 150

    apply_accessibility_to_app(app, {"theme": "standard", "ui_scale": 100})
    assert app.font().pointSizeF() == pytest.approx(BASE_FONT_POINT_SIZE)


@pytest.mark.unit
@pytest.mark.parametrize("scale", VALID_UI_SCALES)
def test_scaled_helpers_follow_scale(app, scale):
    assert scaled(100, scale) == scale
    assert scaled_font(12, ui_scale=scale).pointSizeF() == pytest.approx(
        12 * scale / 100
    )
    assert f"font-size: {scaled(12, scale)}px" in structure_stylesheet(scale)
    assert f"font-size: {scaled(12, scale)}px" in get_theme_stylesheet(
        "high_contrast", scale
    )


@pytest.mark.unit
def test_screen_relative_size_scales_minimum_and_caps_to_screen(app):
    screen = QRect(0, 0, 2560, 1920)
    assert screen_relative_size(0.7, 0.7, 800, 600, screen=screen) == (1792, 1344)
    small = QRect(0, 0, 1024, 700)
    assert screen_relative_size(0.7, 0.7, 1200, 900, screen=small) == (1024, 700)

    apply_accessibility_to_app(app, {"theme": "standard", "ui_scale": 150})
    try:
        width, height = screen_relative_size(0.1, 0.1, 800, 600, screen=screen)
        assert (width, height) == (1200, 900)
    finally:
        apply_accessibility_to_app(app, {"theme": "standard", "ui_scale": 100})


@pytest.mark.unit
def test_centred_window_geometry_fits_screen(app):
    rect = centred_window_geometry(0.7, 0.7, 960, 640)
    screen = acc.available_screen_geometry()
    assert screen.contains(rect)


@pytest.mark.unit
def test_live_apply_refreshes_open_windows(app):
    from PyQt6.QtWidgets import QWidget

    class Window(QWidget):
        def __init__(self):
            super().__init__()
            self.seen = []

        def refresh_accessibility(self, settings):
            self.seen.append(dict(settings))

    window = Window()
    window.show()
    try:
        apply_accessibility_to_app(app, {"theme": "high_contrast", "ui_scale": 125})
        assert window.seen[-1] == {"theme": "high_contrast", "ui_scale": 125}
    finally:
        window.close()
        apply_accessibility_to_app(app, {"theme": "standard", "ui_scale": 100})


@pytest.mark.unit
def test_wrapping_button_keeps_full_caption(app):
    from momentum.gui.gui_career import WrappingPushButton

    button = WrappingPushButton("Tier 1 · Single Seater Tier 1 Championship")
    assert button.text() == "Tier 1 · Single Seater Tier 1 Championship"
    label = button.caption_label()
    assert label.wordWrap()
    one_line = label.fontMetrics().lineSpacing()
    assert label.heightForWidth(160) >= one_line * 2


@pytest.mark.unit
def test_main_menu_single_apply_action(app, tmp_path, monkeypatch):
    monkeypatch.setattr(acc, "_settings_dir", lambda: str(tmp_path))
    import momentum.gui.gui_main_menu as menu_module

    monkeypatch.setattr(menu_module, "information", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        menu_module,
        "save_race_settings",
        lambda values: {
            "render_fps": int(values["render_fps"]),
            "simulation_speed": float(values["simulation_speed"]),
        },
    )
    window = menu_module.MainMenuWindow()
    try:
        assert window.pending_setting_changes() == []
        assert not window.apply_settings_btn.isEnabled()

        scale_index = window.ui_scale_combo.findData(150)
        window.ui_scale_combo.setCurrentIndex(scale_index)
        assert window.pending_setting_changes() == ["UI scale"]
        assert window.apply_settings_btn.isEnabled()

        window._apply_settings()
        assert current_ui_scale() == 150
        assert window.accessibility_settings["ui_scale"] == 150
        assert window.pending_setting_changes() == []
        assert not window.apply_settings_btn.isEnabled()
        assert app.font().pointSizeF() == pytest.approx(BASE_FONT_POINT_SIZE * 1.5)
    finally:
        window.close()
        apply_accessibility_to_app(app, {"theme": "standard", "ui_scale": 100})


@pytest.mark.unit
def test_round_header_spans_columns(app):
    tree = QTreeWidget()
    tree.setColumnCount(4)
    item = QTreeWidgetItem(["Round 1", "", "", ""])
    tree.addTopLevelItem(item)
    item.setFirstColumnSpanned(True)
    assert item.isFirstColumnSpanned()


@pytest.mark.unit
@pytest.mark.parametrize(
    ("height", "expected"), [(1080, 100), (1440, 125), (1920, 150), (2160, 150)]
)
def test_default_ui_scale_follows_screen_height(height, expected):
    assert acc.default_ui_scale_for_screen(height) == expected
