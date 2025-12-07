"""
Simple rendering test for VehicleRenderer that saves a PNG so you don't need to
launch the full GUI.

Usage:
  # Run as a simple script
  python Momentum/Python/tests/test_vehicle_appearance_render.py

  # Or run with pytest (will assert output file exists)
  pytest Momentum/Python/tests/test_vehicle_appearance_render.py

The test will create the output PNG at `Momentum/Python/tests/output/vehicle_topdown.png`
"""

import os
import sys

# Ensure Momentum/Python is on sys.path so `vehicles` can be imported when running
# the test from repo root.
HERE = os.path.dirname(os.path.abspath(__file__))
PY_DIR = os.path.abspath(os.path.join(HERE, '..'))
if PY_DIR not in sys.path:
    sys.path.insert(0, PY_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor
from vehicles.vehicle_appearance import VehicleRenderer, Livery


def render_and_save(path: str, *, size=(240, 120), scale=6.0):
    """Render a single seater at center of a QPixmap and save to `path`.

    Returns the path saved.
    """
    # Create (or reuse) a QApplication instance - required for QPixmap/QPainter
    app = QApplication.instance() or QApplication([])

    w, h = size
    pix = QPixmap(w, h)
    # Transparent background to make inspection easier
    pix.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pix)
    # Turn OFF antialiasing for the flat, polygonal look
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    except Exception:
        # Older PyQt versions may not accept enum form - ignore if it fails
        pass

    # Translate so the car is centred in the pixmap
    painter.translate(w / 2, h / 2)

    # Create a test livery: red primary, white accent, white trim
    livery = Livery(QColor(220, 40, 40), QColor(255, 255, 255), QColor(255, 255, 255), "TestTeam", 1)

    # Render with optional steering angle (0 for straight, can test with -15 or +15)
    steering = 0.0  # Change to -12 or +12 to test steering
    VehicleRenderer.render_single_seater_car(painter, livery, scale=scale, steering_angle=steering)

    painter.end()

    os.makedirs(os.path.dirname(path), exist_ok=True)
    pix.save(path)

    return path


def test_render_creates_file(tmp_path):
    out = tmp_path / "vehicle_topdown.png"
    path = render_and_save(str(out))
    assert os.path.exists(path)


if __name__ == "__main__":
    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)

    # Save raw sprite (no rotation) for inspection
    raw_path = os.path.join(out_dir, "vehicle_topdown.png")
    render_and_save(raw_path)

    # Save rotated sprite (+90 degrees) to mirror in-game rotation
    rotated_path = os.path.join(out_dir, "vehicle_topdown_rotated.png")
    # Create a pixmap and painter, rotate before rendering
    app = QApplication.instance() or QApplication([])
    w, h = (240, 120)
    pix = QPixmap(w, h)
    pix.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pix)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    except Exception:
        pass
    painter.translate(w / 2, h / 2)
    painter.rotate(90)  # match +90° rotation used in track renderer
    livery = Livery(QColor(220, 40, 40), QColor(255, 255, 255), QColor(255, 255, 255), "TestTeam", 1)
    VehicleRenderer.render_single_seater_car(painter, livery, scale=6.0)
    painter.end()
    pix.save(rotated_path)
    print("Saved:", raw_path, rotated_path)
