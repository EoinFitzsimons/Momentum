"""Render track previews using the GUI rendering pipeline (TrackWidget).

For each track in the database this script:
- loads the track via DatabaseManager.get_simple_track(track_id)
- generates visual `track_points` using `CircuitGenerator.generate(length_km)`
- creates a `TrackWidget` and renders it offscreen to a PNG

Run:
    python Momentum/Python/tools/gui_tracks_to_png.py

Output:
    Momentum/Python/tools/gui_track_{track_id}.png
"""

import sys
from pathlib import Path
import re

repo_root = Path(__file__).resolve().parents[3]
py_pkg = repo_root / "Momentum" / "Python"
sys.path.insert(0, str(py_pkg))
sys.path.insert(0, str(repo_root))

from database.database_manager import DatabaseManager
from GUI.gui_race_visual import CircuitGenerator, TrackWidget, VehicleAppearanceManager
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter


def render_all(output_dir: Path):
    app = QApplication([])
    db = DatabaseManager()

    # Collect track ids
    with db.get_connection() as conn:
        rows = conn.execute("SELECT id FROM tracks ORDER BY id").fetchall()
    if not rows:
        print("No tracks found in DB.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    appearance = VehicleAppearanceManager()

    for (row,) in rows:
        track_id = int(row)
        print(f"Rendering track id={track_id}...")
        st = db.get_simple_track(track_id)
        # Generate visual track points using GUI's generator
        track_points = CircuitGenerator.generate(st.length_km)
        track_length = st.length_km * 1000

        widget = TrackWidget(
            track_points,
            track_length,
            appearance,
            track_surface=getattr(st, "surface", "asphalt"),
            surface_grip=getattr(st, "surface_grip", None),
        )
        # ensure proper sizing
        widget.resize(widget.minimumSize())
        w = widget.width()
        h = widget.height()

        pix = QPixmap(w, h)
        pix.fill()
        painter = QPainter(pix)
        widget.render(painter)
        painter.end()
        # build racetrack-style filename: {id:03d}-{Country}-{Name}-{LengthKm}km.png
        country = getattr(st, "country", "") or ""
        length = getattr(st, "length_km", None)
        length_str = f"{length:.2f}km" if isinstance(length, (int, float)) else ""
        parts = [f"{track_id:03d}"]
        if country:
            parts.append(country)
        parts.append(getattr(st, "name", f"track_{track_id}"))
        if length_str:
            parts.append(length_str)
        raw = "-".join(parts)
        safe = re.sub(r"[^A-Za-z0-9 _\-]", "", raw).strip()
        safe = safe.replace(" ", "_")
        if not safe:
            safe = f"{track_id:03d}"
        safe = safe[:140]
        out = output_dir / f"{safe}.png"
        pix.save(str(out))
        print(f"Saved {out}")

    app.quit()


if __name__ == "__main__":
    outdir = Path(__file__).parent
    render_all(outdir)
