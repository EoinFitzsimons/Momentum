"""Accessibility settings helpers for Momentum GUI."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional, Tuple

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QFont, QFontDatabase, QGuiApplication
from PyQt6.QtWidgets import QApplication, QWidget

DEFAULT_ACCESSIBILITY_SETTINGS: Dict[str, Any] = {
    "theme": "standard",
    "ui_scale": 100,
}

VALID_THEMES = ("standard", "high_contrast", "colorblind_safe")
VALID_UI_SCALES = (100, 125, 150)

# Unscaled application font size in points. Every scale is derived from this
# constant rather than from the current application font so that applying a
# scale repeatedly never compounds.
BASE_FONT_POINT_SIZE = 10.0

# Fallback desktop size used when no screen is available (offscreen tests).
FALLBACK_SCREEN_SIZE = (1600, 900)

# Name of the duck-typed hook a window may implement to react to a live
# accessibility change (theme or UI scale).
ACCESSIBILITY_HOOK = "refresh_accessibility"

_current_ui_scale: int = 100

PREFERRED_FONT_FILES = (
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\tahoma.ttf",
    r"C:\Windows\Fonts\verdana.ttf",
)

PREFERRED_FONT_FAMILIES = (
    "Segoe UI",
    "Arial",
    "Tahoma",
    "Verdana",
    "Liberation Sans",
    "DejaVu Sans",
)


def _settings_dir() -> str:
    path = os.path.join(os.path.expanduser("~"), ".momentum")
    os.makedirs(path, exist_ok=True)
    return path


def _settings_path() -> str:
    return os.path.join(_settings_dir(), "accessibility_settings.json")


def normalize_accessibility_settings(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    """Normalize user-supplied settings with defensive defaults."""
    settings = dict(DEFAULT_ACCESSIBILITY_SETTINGS)
    if not isinstance(raw, dict):
        return settings

    theme = str(raw.get("theme", "standard") or "standard").strip().lower()
    if theme not in VALID_THEMES:
        theme = "standard"

    scale_raw = raw.get("ui_scale", 100)
    try:
        ui_scale = int(scale_raw)
    except Exception:
        ui_scale = 100

    if ui_scale not in VALID_UI_SCALES:
        ui_scale = 100

    settings["theme"] = theme
    settings["ui_scale"] = ui_scale
    return settings


def default_ui_scale_for_screen(screen_height: int) -> int:
    """Recommend a UI scale from the desktop height when the player has not chosen one.

    At 100% the base font is about 13 px tall, which is under 2 mm on a
    1920-pixel-high desktop, so taller desktops default to a larger scale.
    """
    if screen_height >= 1800:
        return 150
    if screen_height >= 1300:
        return 125
    return 100


def default_accessibility_settings() -> Dict[str, Any]:
    """Defaults for a first run: standard theme, scale recommended for the screen."""
    settings = dict(DEFAULT_ACCESSIBILITY_SETTINGS)
    try:
        settings["ui_scale"] = default_ui_scale_for_screen(
            available_screen_geometry().height()
        )
    except Exception:
        settings["ui_scale"] = DEFAULT_ACCESSIBILITY_SETTINGS["ui_scale"]
    return settings


def load_accessibility_settings() -> Dict[str, Any]:
    """Load settings from disk; on a first run derive the UI scale from the screen."""
    path = _settings_path()
    try:
        if not os.path.exists(path):
            return default_accessibility_settings()
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        return normalize_accessibility_settings(loaded)
    except Exception:
        return dict(DEFAULT_ACCESSIBILITY_SETTINGS)


def save_accessibility_settings(settings: Dict[str, Any]) -> None:
    """Persist settings to disk."""
    normalized = normalize_accessibility_settings(settings)
    path = _settings_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2)


def current_ui_scale() -> int:
    """Return the UI scale (percentage) currently applied to the application."""
    return _current_ui_scale


def ui_scale_factor(ui_scale: Optional[int] = None) -> float:
    """Return the multiplier for the given (or current) UI scale percentage."""
    scale = _current_ui_scale if ui_scale is None else int(ui_scale)
    if scale not in VALID_UI_SCALES:
        scale = 100
    return float(scale) / 100.0


def scaled(value: float, ui_scale: Optional[int] = None) -> int:
    """Scale a pixel dimension designed at 100% to the current UI scale."""
    return max(0, int(round(float(value) * ui_scale_factor(ui_scale))))


def scaled_font(
    point_size: float,
    bold: bool = False,
    ui_scale: Optional[int] = None,
    base: Optional[QFont] = None,
) -> QFont:
    """Return a QFont whose point size follows the current UI scale."""
    font = QFont(base) if base is not None else QFont()
    app = QApplication.instance()
    if base is None and isinstance(app, QApplication):
        font = QFont(app.font())
    font.setPointSizeF(max(6.0, float(point_size) * ui_scale_factor(ui_scale)))
    font.setBold(bold)
    return font


def available_screen_geometry(widget: Optional[QWidget] = None) -> QRect:
    """Return the usable desktop area for the widget's screen (or the primary screen)."""
    screen = None
    if widget is not None:
        try:
            screen = widget.screen()
        except Exception:
            screen = None
    if screen is None:
        screen = QGuiApplication.primaryScreen()
    if screen is None:
        return QRect(0, 0, FALLBACK_SCREEN_SIZE[0], FALLBACK_SCREEN_SIZE[1])
    rect = screen.availableGeometry()
    if rect.width() <= 0 or rect.height() <= 0:
        return QRect(0, 0, FALLBACK_SCREEN_SIZE[0], FALLBACK_SCREEN_SIZE[1])
    return rect


def screen_relative_size(
    width_fraction: float,
    height_fraction: float,
    min_width: int = 0,
    min_height: int = 0,
    widget: Optional[QWidget] = None,
    screen: Optional[QRect] = None,
) -> Tuple[int, int]:
    """Size a window as a fraction of the available screen.

    ``width_fraction``/``height_fraction`` and ``min_width``/``min_height`` are
    100%-scale design values and grow with the UI scale; the result never
    exceeds the available screen area so a dialog always fits on the desktop
    it opens on.
    """
    rect = screen if screen is not None else available_screen_geometry(widget)
    # Fractions are design values at 100%; a larger UI scale needs
    # proportionally more of the screen to show the same content.
    factor = ui_scale_factor()
    target_w = int(rect.width() * max(0.0, min(1.0, width_fraction * factor)))
    target_h = int(rect.height() * max(0.0, min(1.0, height_fraction * factor)))
    width = max(target_w, scaled(min_width))
    height = max(target_h, scaled(min_height))
    width = min(width, rect.width())
    height = min(height, rect.height())
    return width, height


def size_dialog_to_screen(
    widget: QWidget,
    width_fraction: float,
    height_fraction: float,
    min_width: int = 0,
    min_height: int = 0,
) -> Tuple[int, int]:
    """Resize ``widget`` relative to its screen and apply a scaled, screen-capped minimum.

    The cap leaves room for the native window frame so a framed dialog's
    client area never forces the window off the work area.
    """
    rect = available_screen_geometry(widget)
    frame_w, frame_h = window_frame_allowance(widget)
    usable = QRect(rect.x(), rect.y(), rect.width() - frame_w, rect.height() - frame_h)
    width, height = screen_relative_size(
        width_fraction, height_fraction, min_width, min_height, screen=usable
    )
    min_w = min(scaled(min_width), usable.width())
    min_h = min(scaled(min_height), usable.height())
    widget.setMinimumSize(min_w, min_h)
    widget.resize(width, height)
    return width, height


# Space reserved for native window decorations (title bar and borders) in
# device-independent pixels; decorations do not follow the UI scale.
WINDOW_FRAME_ALLOWANCE = (16, 48)


def window_frame_allowance(widget: Optional[QWidget]) -> Tuple[int, int]:
    """Return the (width, height) a framed top-level window needs for decorations."""
    if widget is None:
        return WINDOW_FRAME_ALLOWANCE
    flags = widget.windowFlags()
    if flags & Qt.WindowType.FramelessWindowHint:
        return (0, 0)
    try:
        frame = widget.frameGeometry()
        inner = widget.geometry()
        if widget.isVisible() and frame.height() > inner.height():
            return (
                max(0, frame.width() - inner.width()),
                max(0, frame.height() - inner.height()),
            )
    except Exception:
        pass
    return WINDOW_FRAME_ALLOWANCE


def centred_window_geometry(
    width_fraction: float,
    height_fraction: float,
    min_width: int = 0,
    min_height: int = 0,
    widget: Optional[QWidget] = None,
) -> QRect:
    """Return a screen-relative window rectangle centred on the available screen."""
    rect = available_screen_geometry(widget)
    width, height = screen_relative_size(
        width_fraction, height_fraction, min_width, min_height, screen=rect
    )
    x = rect.x() + max(0, (rect.width() - width) // 2)
    y = rect.y() + max(0, (rect.height() - height) // 2)
    return QRect(x, y, width, height)


_PX_FONT_SIZE = re.compile(r"font-size:\s*(\d+)px")


def scale_px_stylesheet(css: str, ui_scale: Optional[int] = None) -> str:
    """Scale every ``font-size: Npx`` declaration in a 100%-design stylesheet."""
    return _PX_FONT_SIZE.sub(
        lambda match: f"font-size: {scaled(int(match.group(1)), ui_scale)}px", css
    )


def get_focus_stylesheet() -> str:
    """Visible keyboard focus styling for core interactive controls."""
    return """
QPushButton:focus, QComboBox:focus, QRadioButton:focus, QListWidget:focus,
QLineEdit:focus, QTableWidget:focus, QTreeWidget:focus {
    border: 2px solid #FFD54F;
    outline: none;
}
"""


def get_theme_stylesheet(theme: str, ui_scale: Optional[int] = None) -> str:
    """Return stylesheet overrides for selected accessibility theme.

    Every theme declares ``alternate-background-color`` on tables, trees and
    lists so alternating rows never fall back to the platform palette (which
    paints white rows under a white-text theme). Item colours are deliberately
    not styled so per-cell highlights set in code (player rows, DNF cells)
    still show.
    """
    theme = str(theme or "standard").strip().lower()
    structure = structure_stylesheet(ui_scale)
    if theme == "high_contrast":
        return """
QWidget { background-color: #000000; color: #FFFFFF; }
QMainWindow { background-color: #000000; }
QGroupBox { border: 2px solid #FFFFFF; }
QPushButton { background-color: #000000; color: #FFFFFF; border: 2px solid #FFFFFF; }
QPushButton:hover { background-color: #222222; }
QComboBox, QLineEdit, QListWidget, QTableWidget, QTreeWidget {
    background-color: #000000;
    alternate-background-color: #1E1E1E;
    color: #FFFFFF;
    border: 2px solid #FFFFFF;
}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #FFFFFF;
    color: #000000;
}
QGroupBox::title { color: #FFFFFF; background-color: #000000; }
QHeaderView::section { background-color: #000000; color: #FFFFFF; border: 1px solid #FFFFFF; }
""" + structure

    if theme == "colorblind_safe":
        return """
QWidget { background-color: #1F2430; color: #E6E6E6; }
QMainWindow { background-color: #1F2430; }
QGroupBox { border: 1px solid #5DA5DA; }
QPushButton { background-color: #2A3142; color: #E6E6E6; border: 1px solid #5DA5DA; }
QPushButton:hover { background-color: #3A4560; }
QComboBox, QLineEdit, QListWidget, QTableWidget, QTreeWidget {
    background-color: #2A3142;
    alternate-background-color: #343C50;
    color: #E6E6E6;
    border: 1px solid #5DA5DA;
}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #F0AD4E;
    color: #1F2430;
}
QGroupBox::title { color: #5DA5DA; background-color: #1F2430; }
QHeaderView::section { background-color: #2A3142; color: #E6E6E6; border: none; }
""" + structure

    # Default 'standard' theme: a dark, high-contrast friendly palette used by Momentum.
    return STANDARD_THEME_BASE + structure


# Shared structural rules so group titles sit above their panel instead of over
# the first row, tables read as cards and controls have consistent spacing.
# Pixel sizes are written at 100% and scaled with the UI scale.
_STRUCTURE_STYLESHEET_TEMPLATE = """
QGroupBox {
    border-radius: 10px;
    margin-top: __GROUP_MARGIN__px;
    padding: __GROUP_PAD_TOP__px 12px 12px 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 4px;
    padding: 2px 8px;
    font-size: __TITLE_PX__px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
QTableWidget, QTreeWidget, QListWidget {
    border-radius: 8px;
    gridline-color: transparent;
    outline: none;
}
QTableWidget::item, QTreeWidget::item { padding: __ITEM_PAD_V__px __ITEM_PAD_H__px; }
QHeaderView::section { padding: __HEADER_PAD_V__px __ITEM_PAD_H__px; font-weight: 600; }
QHeaderView::section:first { border-top-left-radius: 8px; }
QHeaderView::section:last { border-top-right-radius: 8px; }
QTableCornerButton::section { border: none; }
QPushButton { border-radius: 8px; padding: 8px 14px; font-weight: 600; }
QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QTextEdit {
    border-radius: 6px;
    padding: 6px 10px;
    min-height: __FIELD_MIN_H__px;
}
QComboBox::drop-down { border: none; width: __DROPDOWN_W__px; }
QScrollBar:vertical { width: 10px; margin: 0; }
QScrollBar:horizontal { height: 10px; margin: 0; }
QScrollBar::handle { border-radius: 5px; min-height: 24px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {
    background: none; border: none; height: 0; width: 0;
}
QTabBar::tab { padding: 8px 16px; border-top-left-radius: 8px; border-top-right-radius: 8px; }
"""


def structure_stylesheet(ui_scale: Optional[int] = None) -> str:
    """Return the shared structural stylesheet with pixel sizes at the given UI scale."""
    sizes = {
        "__GROUP_MARGIN__": 26,
        "__GROUP_PAD_TOP__": 14,
        "__TITLE_PX__": 12,
        "__ITEM_PAD_V__": 6,
        "__ITEM_PAD_H__": 10,
        "__HEADER_PAD_V__": 8,
        "__FIELD_MIN_H__": 20,
        "__DROPDOWN_W__": 24,
    }
    css = _STRUCTURE_STYLESHEET_TEMPLATE
    for placeholder, base_px in sizes.items():
        css = css.replace(placeholder, str(scaled(base_px, ui_scale)))
    return css


STANDARD_THEME_BASE = (
    """
QWidget { background-color: #272B2D; color: #E3F6F9; }
QMainWindow, QDialog { background-color: #272B2D; }
QLabel { color: #E3F6F9; background-color: transparent; }
QGroupBox { background-color: #30363A; border: 1px solid #3E474D; }
QGroupBox::title { color: #7EE6E0; background-color: #272B2D; }
QPushButton { background-color: #38424A; color: #E3F6F9; border: 1px solid #4B5A63; }
QPushButton:hover { background-color: #43515A; border-color: #7EE6E0; }
QPushButton:pressed { background-color: #2E373D; }
QPushButton:disabled { background-color: #2E3438; color: #7A8A91; border-color: #3A4348; }
QPushButton[primary="true"] { background-color: #7EE6E0; color: #16211F; border-color: #7EE6E0; }
QPushButton[primary="true"]:hover { background-color: #9AEFEA; }
QPushButton[secondary="true"] { background-color: #DD2D4A; color: #FFFFFF; border-color: #DD2D4A; }
QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QTextEdit {
    background-color: #1F2426;
    color: #E3F6F9;
    border: 1px solid #3E474D;
    selection-background-color: #7EE6E0;
    selection-color: #16211F;
}
QComboBox:hover, QLineEdit:hover { border-color: #7EE6E0; }
QComboBox QAbstractItemView {
    background-color: #1F2426;
    color: #E3F6F9;
    border: 1px solid #3E474D;
    selection-background-color: #38424A;
    selection-color: #E3F6F9;
}
QTableWidget, QTreeWidget, QListWidget {
    background-color: #1F2426;
    alternate-background-color: #2A3134;
    color: #E3F6F9;
    border: 1px solid #3E474D;
}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #35504F;
    color: #FFFFFF;
}
QHeaderView::section { background-color: #30363A; color: #9ED8DB; border: none; }
QHeaderView { background-color: #30363A; }
QTableCornerButton::section { background-color: #30363A; }
QScrollBar:vertical, QScrollBar:horizontal { background: #1F2426; }
QScrollBar::handle { background: #4B5A63; }
QScrollBar::handle:hover { background: #7EE6E0; }
QTabBar::tab { background-color: #30363A; color: #9ED8DB; }
QTabBar::tab:selected { background-color: #38424A; color: #E3F6F9; }
QToolTip { background-color: #1F2426; color: #E3F6F9; border: 1px solid #4B5A63; }
QMenu { background-color: #1F2426; color: #E3F6F9; border: 1px solid #3E474D; }
QMenu::item:selected { background-color: #35504F; }
"""
)

STANDARD_THEME_STYLESHEET = STANDARD_THEME_BASE + structure_stylesheet(100)


def _resolve_readable_font_family() -> str:
    """Return a UI font family that is likely to render text in headless Qt."""
    family = _load_font_family_from_paths(PREFERRED_FONT_FILES)
    if family:
        return family
    family = _find_available_preferred_family()
    if family:
        return family
    family = _load_matplotlib_font_family()
    if family:
        return family
    return _first_available_font_family()


def _load_font_family_from_paths(font_paths: tuple[str, ...]) -> str:
    for font_path in font_paths:
        if not os.path.exists(font_path):
            continue
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            continue
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            return families[0]
    return ""


def _find_available_preferred_family() -> str:
    available = set(QFontDatabase.families())
    return next((family for family in PREFERRED_FONT_FAMILIES if family in available), "")


def _load_matplotlib_font_family() -> str:
    try:
        import matplotlib

        font_path = os.path.join(
            matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans.ttf"
        )
        return _load_font_family_from_paths((font_path,))
    except Exception:
        return ""


def _first_available_font_family() -> str:
    try:
        families = list(QFontDatabase.families())
        return families[0] if families else ""
    except Exception:
        return ""


def apply_accessibility_to_app(app: QApplication, settings: Dict[str, Any]) -> None:
    """Apply theme and UI scale to the application and every open window.

    The font size is always derived from ``BASE_FONT_POINT_SIZE`` so repeated
    calls are idempotent. After the global font and stylesheet are updated,
    every top-level window implementing ``refresh_accessibility(settings)`` is
    asked to refresh its own fonts, stylesheets and scaled dimensions so the
    change is visible live rather than only in windows opened afterwards.
    """
    global _current_ui_scale
    normalized = normalize_accessibility_settings(settings)
    _current_ui_scale = int(normalized["ui_scale"])

    readable_family = _resolve_readable_font_family()

    font = QFont(app.font())
    if readable_family:
        font.setFamily(readable_family)
    font.setPointSizeF(max(8.0, BASE_FONT_POINT_SIZE * ui_scale_factor()))
    app.setFont(font)

    app.setStyleSheet(
        get_focus_stylesheet()
        + "\n"
        + get_theme_stylesheet(str(normalized["theme"]), _current_ui_scale)
    )

    refresh_open_windows(app, normalized)


def refresh_open_windows(app: QApplication, settings: Dict[str, Any]) -> int:
    """Notify every open top-level window of an accessibility change.

    Returns the number of windows that implemented the refresh hook.
    """
    refreshed = 0
    for window in app.topLevelWidgets():
        hook = getattr(window, ACCESSIBILITY_HOOK, None)
        if callable(hook):
            hook(dict(settings))
            refreshed += 1
    return refreshed
