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
"""

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
"""

    # Default 'standard' theme: a dark, high-contrast friendly palette used by Momentum.
    return """
QWidget { background-color: #353839; color: #B9F2FF; }
QMainWindow { background-color: #353839; }
QGroupBox { border: 1px solid rgba(185,242,255,0.12); }
QLabel { color: #B9F2FF; }
QPushButton { background-color: #2b2f30; color: #B9F2FF; border: 1px solid rgba(185,242,255,0.12); padding: 6px; }
QPushButton:hover { background-color: #3a3f40; }
QComboBox, QLineEdit, QListWidget, QTableWidget, QTreeWidget {
    background-color: #2f3233;
    color: #B9F2FF;
    border: 1px solid rgba(185,242,255,0.06);
}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: rgba(185,242,255,0.12);
    color: #FFFFFF;
}
"""



def _resolve_readable_font_family() -> str:
    """Return a UI font family that is likely to render text in headless Qt."""
    for font_path in PREFERRED_FONT_FILES:
        if not os.path.exists(font_path):
            continue
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            continue
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            return families[0]

    database = QFontDatabase()
    available = set(database.families())
    for family in PREFERRED_FONT_FAMILIES:
        if family in available:
            return family
    # Try to load DejaVu Sans from matplotlib as a reliable bundled fallback
    try:
        import matplotlib
        dv_path = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf', 'DejaVuSans.ttf')
        if os.path.exists(dv_path):
            font_id = QFontDatabase.addApplicationFont(dv_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    return families[0]
    except Exception:
        pass

    # Final fallback: return first available family or empty string
    try:
        fams = list(set(QFontDatabase().families()))
        return fams[0] if fams else ""
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

    app.setStyleSheet(get_focus_stylesheet() + "\n" + get_theme_stylesheet(str(normalized["theme"])))
