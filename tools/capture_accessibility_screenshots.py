"""Capture accessibility theme and scale screenshots for Main Menu.

Saves PNGs under `saves/accessibility_screenshots/`.
"""

import os
import sys
import time

# Put the repository root on sys.path so the momentum package imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap

from momentum.gui.gui_main_menu import MainMenuWindow
from momentum.gui.accessibility_settings import (
    apply_accessibility_to_app,
    normalize_accessibility_settings,
)

OUT_DIR = os.path.join(os.path.dirname(ROOT), "saves", "accessibility_screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

THEMES = ["standard", "high_contrast", "colorblind_safe"]
SCALES = [100, 125, 150]


def capture_one(app, theme, scale, filename):
    settings = normalize_accessibility_settings({"theme": theme, "ui_scale": scale})
    apply_accessibility_to_app(app, settings)

    win = MainMenuWindow()
    win.show()
    # Allow the event loop to settle styles and layout
    app.processEvents()
    time.sleep(0.25)
    app.processEvents()

    pix = QPixmap(win.size())
    pix = win.grab()
    path = os.path.join(OUT_DIR, filename)
    pix.save(path)
    win.close()
    return path


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    generated = []
    for theme in THEMES:
        for scale in SCALES:
            name = f"menu_{theme}_{scale}pct.png"
            print(f"Capturing {name}...")
            path = capture_one(app, theme, scale, name)
            generated.append(path)
            print("Saved:", path)
    print("\nAll screenshots saved:")
    for p in generated:
        print(" -", p)


if __name__ == "__main__":
    main()
