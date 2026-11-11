"""Capture screenshots for all accessibility themes and UI scales.

This wrapper writes the accessibility settings to the user's .momentum settings
file, runs the existing capture_all_screens.py (offscreen), and moves the
generated images into a per-variant folder under saves/accessibility_screenshots/.
"""

import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAPTURE_SCRIPT = os.path.join(ROOT, "tools", "capture_all_screens.py")
OUT_ROOT = os.path.join(os.path.dirname(ROOT), "saves", "accessibility_screenshots")
ALL_SCREENS_DIR = os.path.join(OUT_ROOT, "all_screens")

VARIANTS = [
    ("standard", 100),
    ("standard", 125),
    ("standard", 150),
    ("high_contrast", 100),
    ("high_contrast", 125),
    ("high_contrast", 150),
    ("colorblind_safe", 100),
    ("colorblind_safe", 125),
    ("colorblind_safe", 150),
]


def _write_settings(theme: str, ui_scale: int) -> str:
    cfg_dir = os.path.join(os.path.expanduser("~"), ".momentum")
    os.makedirs(cfg_dir, exist_ok=True)
    path = os.path.join(cfg_dir, "accessibility_settings.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"theme": theme, "ui_scale": ui_scale}, f, indent=2)
    return path


def _ensure_all_screens_dir():
    os.makedirs(ALL_SCREENS_DIR, exist_ok=True)


def _move_generated_to_variant(theme: str, ui_scale: int):
    dest = os.path.join(OUT_ROOT, f"{theme}_{ui_scale}")
    os.makedirs(dest, exist_ok=True)
    if not os.path.isdir(ALL_SCREENS_DIR):
        return
    for fname in os.listdir(ALL_SCREENS_DIR):
        src = os.path.join(ALL_SCREENS_DIR, fname)
        if os.path.isfile(src):
            shutil.move(src, os.path.join(dest, fname))


def main():
    _ensure_all_screens_dir()
    for theme, scale in VARIANTS:
        print(f"\n--- Capturing variant: theme={theme}, ui_scale={scale} ---")
        _write_settings(theme, scale)
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["PYTHONPATH"] = ROOT
        # Run capture script in a fresh process to ensure a new QApplication
        cmd = [sys.executable, CAPTURE_SCRIPT]
        try:
            subprocess.run(cmd, env=env, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Capture failed for {theme} {scale}: {e}")
            continue
        # Move outputs into variant folder
        _move_generated_to_variant(theme, scale)
        # Small pause between runs
        time.sleep(0.2)


if __name__ == "__main__":
    main()
