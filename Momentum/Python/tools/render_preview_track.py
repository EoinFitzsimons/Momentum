"""Render a single preview PNG for the current solved track using TrackWidget.

Saves to Momentum/Python/tools/preview_solved_track.png
"""
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root / 'Momentum' / 'Python'))
sys.path.insert(0, str(repo_root))

from database.database_manager import DatabaseManager
from GUI.gui_race_visual import CircuitGenerator, TrackWidget, VehicleAppearanceManager
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter

OUT = Path(__file__).parent / 'preview_solved_track.png'


def render_preview(out_path: Path):
    app = QApplication([])
    db = DatabaseManager()
    st = db.get_simple_track()
    if not st:
        print('No simple track available in DB')
        return 1

    # Use closure-solved generator like the GUI does
    wrapper = {'solve_closure': True, 'instructions': [
        ('S', int(600 * (st.length_km / 6.0))),
        ('C', 45, 170, 60, 0.00008),
        ('S', int(400 * (st.length_km / 6.0))),
        ('C', 65, 95, 50, 0.0001),
        ('S', int(220 * (st.length_km / 6.0))),
        ('C', -55, 100, 52, 0.0001),
        ('S', int(350 * (st.length_km / 6.0))),
        ('C', 155, 48, 42, 0.00014),
        ('S', int(550 * (st.length_km / 6.0))),
        ('C', -65, 145, 58, 0.00009),
        ('S', int(380 * (st.length_km / 6.0))),
        ('C', 55, 115, 54, 0.00009),
        ('S', int(180 * (st.length_km / 6.0))),
        ('C', 60, 90, 50, 0.0001),
        ('S', int(300 * (st.length_km / 6.0))),
        ('C', -50, 135, 56, 0.00009),
        ('S', int(160 * (st.length_km / 6.0))),
        ('C', 50, 135, 56, 0.00009),
        ('S', int(320 * (st.length_km / 6.0))),
    ]}

    routes = CircuitGenerator.generate_with_routes(wrapper, options={})
    track_points = routes.get('main')
    if not track_points:
        print('Generator returned no points')
        return 2

    track_length = st.length_km * 1000
    appearance = VehicleAppearanceManager()

    widget = TrackWidget(track_points, track_length, appearance, track_surface=getattr(st, 'surface', 'asphalt'), surface_grip=getattr(st, 'surface_grip', None))
    widget.resize(1024, 720)
    w = widget.width()
    h = widget.height()

    pix = QPixmap(w, h)
    pix.fill()
    painter = QPainter(pix)
    widget.render(painter)
    painter.end()

    pix.save(str(out_path))
    print(f'Saved preview to {out_path}')
    app.quit()
    return 0


if __name__ == '__main__':
    rc = render_preview(OUT)
    sys.exit(rc)
