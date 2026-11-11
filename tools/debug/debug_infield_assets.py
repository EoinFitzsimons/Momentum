"""Generate debug images for infield pixmap and props for the current solved track.

Saves:
 - tools/debug_infield_pixmap.png
 - tools/debug_infield_props.png
"""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from momentum.database.database_manager import DatabaseManager
from momentum.gui.gui_race_visual import CircuitGenerator, TrackWidget, VehicleAppearanceManager
from momentum.gui.props_placer import place_props, draw_props
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor
import math

OUT_PIX = Path(__file__).parent / "debug_infield_pixmap.png"
OUT_PROPS = Path(__file__).parent / "debug_infield_props.png"


def main():
    app = QApplication([])
    db = DatabaseManager()
    st = db.get_simple_track()
    if not st:
        print("No simple track found")
        return 1

    wrapper = {
        "solve_closure": True,
        "instructions": [
            ("S", int(600 * (st.length_km / 6.0))),
            ("C", 45, 170, 60, 0.00008),
            ("S", int(400 * (st.length_km / 6.0))),
            ("C", 65, 95, 50, 0.0001),
            ("S", int(220 * (st.length_km / 6.0))),
            ("C", -55, 100, 52, 0.0001),
            ("S", int(350 * (st.length_km / 6.0))),
            ("C", 155, 48, 42, 0.00014),
            ("S", int(550 * (st.length_km / 6.0))),
            ("C", -65, 145, 58, 0.00009),
            ("S", int(380 * (st.length_km / 6.0))),
            ("C", 55, 115, 54, 0.00009),
            ("S", int(180 * (st.length_km / 6.0))),
            ("C", 60, 90, 50, 0.0001),
            ("S", int(300 * (st.length_km / 6.0))),
            ("C", -50, 135, 56, 0.00009),
            ("S", int(160 * (st.length_km / 6.0))),
            ("C", 50, 135, 56, 0.00009),
            ("S", int(320 * (st.length_km / 6.0))),
        ],
    }

    routes = CircuitGenerator.generate_with_routes(wrapper, options={})
    tp = routes.get("main")
    if not tp:
        print("No track points")
        return 2

    track_length = st.length_km * 1000
    appearance = VehicleAppearanceManager()
    widget = TrackWidget(
        tp,
        track_length,
        appearance,
        track_surface=getattr(st, "surface", "asphalt"),
        surface_grip=getattr(st, "surface_grip", None),
    )

    # Recompute infield polygon and bbox similarly to _draw_track
    TRACK_WIDTH = 14
    infield_pts = []
    for pt in tp:
        normal_x = -math.sin(pt.theta)
        normal_y = math.cos(pt.theta)
        ix = pt.x - normal_x * (TRACK_WIDTH - 2)
        iy = pt.y - normal_y * (TRACK_WIDTH - 2)
        infield_pts.append((ix, iy))

    # Compute bbox
    xs = [p[0] for p in infield_pts]
    ys = [p[1] for p in infield_pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = max(2, int(math.ceil(maxx - minx)))
    h = max(2, int(math.ceil(maxy - miny)))
    from PyQt6.QtCore import QRectF

    bbox = QRectF(minx, miny, maxx - minx, maxy - miny)
    seed = int(track_length) if track_length is not None else 0

    print(
        f"Infield bbox: {bbox}, size: {w}x{h}, seed={seed}, points={len(infield_pts)}"
    )

    # Generate pixmap using widget helper
    try:
        pix = widget._generate_infield_pixmap(bbox, w, h, seed)
        pix.save(str(OUT_PIX))
        print("Saved pixmap to", OUT_PIX)
    except Exception as e:
        print("Failed to generate pixmap:", e)

    # Place props in world coords and draw onto a transparent image matching bbox
    painter = None
    try:
        props = place_props(infield_pts, seed=seed, density=0.00035)
        canvas = QPixmap(w, h)
        canvas.fill(QColor(0, 0, 0, 0))
        painter = QPainter(canvas)
        # translate so world -> local bbox coords
        painter.translate(-minx, -miny)
        draw_props(painter, props, offset_x=0.0, offset_y=0.0)
        canvas.save(str(OUT_PROPS))
        print("Saved props overlay to", OUT_PROPS, "count=", len(props))
    except Exception as e:
        print("Failed to generate props overlay:", e)
    finally:
        try:
            if painter is not None:
                painter.end()
        except Exception:
            pass

    app.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
