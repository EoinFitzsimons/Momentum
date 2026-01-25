"""
Render the TrackWidget to a PNG for visual inspection of the infield + forest band.
Run this with Python while in the repo root:

python Momentum/Python/tools/render_infield_test.py

This script creates a QApplication, constructs a sample circuit using the
CircuitGenerator defined in gui_race_visual, instantiates TrackWidget and
renders it to debug_infield_render.png in the repo root.
"""
import os
import sys

# Ensure package root on path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# Add the Momentum/Python folder to sys.path so we can import GUI modules
python_pkg = os.path.join(root, 'Python')
if python_pkg not in sys.path:
    sys.path.insert(0, python_pkg)


from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QColor, QImage, QPainter

# Delay importing GUI that may create QPixmaps until after QApplication exists
def import_gui():
    from GUI.gui_race_visual import TrackWidget, CircuitGenerator
    return TrackWidget, CircuitGenerator


def main():
    app = QApplication(sys.argv)
    # Use the actual MomentumLauncher so the same track loading path is used
    # and the RaceWindow/TrackWidget are constructed exactly as in the app.
    from GUI.launcher import MomentumLauncher
    # Create launcher (this will create a QApplication internally but we're already inside one)
    launcher = MomentumLauncher()

    # Start race using default config so RaceWindow is created and loaded
    try:
        launcher.start_race({})
        race_win = launcher.race_window
        # Ensure track_widget exists (RaceWindow._load_data runs synchronously)
        widget = getattr(race_win, 'track_widget', None)
        if widget is None:
            print('RaceWindow did not create track_widget — falling back to direct TrackWidget')
            track_widget, circuit_generator = import_gui()
            # fallback: generate a circuit from default length
            try:
                from database.database_manager import DatabaseManager
                db = DatabaseManager()
                simple_track = db.get_simple_track()
                length_km = getattr(simple_track, 'length_km', 4.5) if simple_track else 4.5
            except Exception:
                length_km = 4.5
            try:
                pts = circuit_generator.generate(length_km)
            except Exception:
                pts = []
            track_length = pts[-1].s if pts else 2000
            widget = track_widget(pts, track_length, appearance_manager=None)
    except Exception as e:
        print('Failed to use MomentumLauncher:', e)
        # fallback to direct construction
        track_widget, circuit_generator = import_gui()
        try:
            from database.database_manager import DatabaseManager
            db = DatabaseManager()
            simple_track = db.get_simple_track()
            length_km = getattr(simple_track, 'length_km', 4.5) if simple_track else 4.5
        except Exception:
            length_km = 4.5
        try:
            pts = circuit_generator.generate(length_km)
        except Exception:
            pts = []
        track_length = pts[-1].s if pts else 2000
        widget = track_widget(pts, track_length, appearance_manager=None)

    widget.resize(1400, 900)
    widget.show()
    app.processEvents()

    # Render widget to pixmap
    # Render into a QImage (ARGB32) to avoid platform-specific QPixmap
    # compositing differences. Fill transparent, paint the widget, then
    # save the image as PNG preserving alpha/transparency.
    size = widget.size()
    img = QImage(size.width(), size.height(), QImage.Format.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))
    painter = QPainter(img)
    widget.render(painter)
    painter.end()

    out = os.path.join(os.getcwd(), 'debug_infield_render.png')
    img.save(out, 'PNG')
    print('Saved debug render to', out)

    # Clean exit
    widget.close()
    if getattr(launcher, 'race_window', None):
        launcher.race_window.close()
    app.quit()


if __name__ == '__main__':
    main()
