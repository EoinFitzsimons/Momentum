"""Accessibility settings helpers for Momentum GUI."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication

DEFAULT_ACCESSIBILITY_SETTINGS: Dict[str, Any] = {
    "theme": "standard",
    "ui_scale": 100,
}

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
    if theme not in {"standard", "high_contrast", "colorblind_safe"}:
        theme = "standard"

    scale_raw = raw.get("ui_scale", 100)
    try:
        ui_scale = int(scale_raw)
    except Exception:
        ui_scale = 100

    if ui_scale not in {100, 125, 150}:
        ui_scale = 100

    settings["theme"] = theme
    settings["ui_scale"] = ui_scale
    return settings


def load_accessibility_settings() -> Dict[str, Any]:
    """Load settings from disk with defaults on failure."""
    path = _settings_path()
    try:
        if not os.path.exists(path):
            return dict(DEFAULT_ACCESSIBILITY_SETTINGS)
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


def get_focus_stylesheet() -> str:
    """Visible keyboard focus styling for core interactive controls."""
    return """
QPushButton:focus, QComboBox:focus, QRadioButton:focus, QListWidget:focus,
QLineEdit:focus, QTableWidget:focus, QTreeWidget:focus {
    border: 2px solid #FFD54F;
    outline: none;
}
"""


def get_theme_stylesheet(theme: str) -> str:
    """Return stylesheet overrides for selected accessibility theme."""
    theme = str(theme or "standard").strip().lower()
    if theme == "high_contrast":
        return """
QWidget { background-color: #000000; color: #FFFFFF; }
QMainWindow { background-color: #000000; }
QGroupBox { border: 2px solid #FFFFFF; }
QPushButton { background-color: #000000; color: #FFFFFF; border: 2px solid #FFFFFF; }
QPushButton:hover { background-color: #222222; }
QComboBox, QLineEdit, QListWidget, QTableWidget, QTreeWidget {
    background-color: #000000;
    color: #FFFFFF;
    border: 2px solid #FFFFFF;
}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #FFFFFF;
    color: #000000;
}
QGroupBox::title { color: #FFFFFF; background-color: #000000; }
QHeaderView::section { background-color: #000000; color: #FFFFFF; border: 1px solid #FFFFFF; }
""" + _STRUCTURE_STYLESHEET

    if theme == "colorblind_safe":
        return """
QWidget { background-color: #1F2430; color: #E6E6E6; }
QMainWindow { background-color: #1F2430; }
QGroupBox { border: 1px solid #5DA5DA; }
QPushButton { background-color: #2A3142; color: #E6E6E6; border: 1px solid #5DA5DA; }
QPushButton:hover { background-color: #3A4560; }
QComboBox, QLineEdit, QListWidget, QTableWidget, QTreeWidget {
    background-color: #2A3142;
    color: #E6E6E6;
    border: 1px solid #5DA5DA;
}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #F0AD4E;
    color: #1F2430;
}
QGroupBox::title { color: #5DA5DA; background-color: #1F2430; }
QHeaderView::section { background-color: #2A3142; color: #E6E6E6; }
""" + _STRUCTURE_STYLESHEET

    # Default 'standard' theme: a dark, high-contrast friendly palette used by Momentum.
    return STANDARD_THEME_STYLESHEET


# Shared structural rules so group titles sit above their panel instead of over
# the first row, tables read as cards and controls have consistent spacing.
_STRUCTURE_STYLESHEET = """
QGroupBox {
    border-radius: 10px;
    margin-top: 26px;
    padding: 14px 12px 12px 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 4px;
    padding: 2px 8px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
QTableWidget, QTreeWidget, QListWidget {
    border-radius: 8px;
    gridline-color: transparent;
    outline: none;
}
QTableWidget::item, QTreeWidget::item { padding: 6px 10px; }
QHeaderView::section { padding: 8px 10px; border: none; font-weight: 600; }
QHeaderView::section:first { border-top-left-radius: 8px; }
QHeaderView::section:last { border-top-right-radius: 8px; }
QTableCornerButton::section { border: none; }
QPushButton { border-radius: 8px; padding: 8px 14px; font-weight: 600; }
QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QTextEdit {
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 20px;
}
QComboBox::drop-down { border: none; width: 24px; }
QScrollBar:vertical { width: 10px; margin: 0; }
QScrollBar:horizontal { height: 10px; margin: 0; }
QScrollBar::handle { border-radius: 5px; min-height: 24px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {
    background: none; border: none; height: 0; width: 0;
}
QTabBar::tab { padding: 8px 16px; border-top-left-radius: 8px; border-top-right-radius: 8px; }
"""

STANDARD_THEME_STYLESHEET = (
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
    alternate-background-color: #242A2D;
    color: #E3F6F9;
    border: 1px solid #3E474D;
}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #35504F;
    color: #FFFFFF;
}
QHeaderView::section { background-color: #30363A; color: #9ED8DB; }
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
    + _STRUCTURE_STYLESHEET
)


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
    """Apply global scale and base accessibility stylesheet to QApplication."""
    normalized = normalize_accessibility_settings(settings)

    readable_family = _resolve_readable_font_family()

    # Global font scaling (kept simple and deterministic).
    font = app.font()
    if readable_family:
        font.setFamily(readable_family)
    base_size = font.pointSizeF()
    if base_size <= 0:
        base_size = 10.0
    scaled_size = max(8.0, base_size * (float(normalized["ui_scale"]) / 100.0))
    font.setPointSizeF(scaled_size)
    app.setFont(font)

    app.setStyleSheet(
        get_focus_stylesheet() + "\n" + get_theme_stylesheet(str(normalized["theme"]))
    )
