import sys
import math
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from database.database_manager import DatabaseManager

# We must ensure QApplication is initialized BEFORE any CircuitGenerator might be imported if it
# triggers some pixmap operations on import. But usually it's certain operations within the methods.
app = QApplication(sys.argv)

from GUI.gui_race_visual import CircuitGenerator


def _build_field_based_circuit_instructions(length_m, turns_raw, tightest_radius_m):
    turns = max(4, min(16, int(turns_raw or 10)))
    radius = max(22.0, min(120.0, float(tightest_radius_m or 30.0) * 1.6))
    angle_deg = 360.0 / float(turns)
    corner_arc = max(8.0, radius * math.radians(angle_deg))
    total_corner_len = corner_arc * turns
    remaining = max(120.0, float(length_m) - total_corner_len)
    straight_each = max(35.0, remaining / turns)
    clothoid_len = max(8.0, min(40.0, radius * 0.45))

    instructions = []
    for _ in range(turns):
        instructions.append({"type": "S", "length_m": int(straight_each)})
        instructions.append(
            {
                "type": "C",
                "angle_deg": float(angle_deg),
                "radius_m": float(radius),
                "clothoid_len": float(clothoid_len),
                "k": 0.00011,
            }
        )
    return instructions


def main():
    db_path = "database/momentum.db"
    if not Path(db_path).exists():
        print(f"Database not found at {db_path}")
        return

    db = DatabaseManager(db_path)
    track_ids = [2, 3, 151]

    for tid in track_ids:
        track = db.get_track(tid)
        if not track:
            print(f"Track {tid} not found.")
            continue

        # Accessing sqlite3.Row or simple object attributes
        if isinstance(track, dict):
            name = track.get("name")
            length_km = track.get("length_km")
            turns = track.get("turns")
            tightest_radius = track.get("tightest_corner_radius_m")
        else:
            # Try attribute access for Track object
            name = getattr(track, "name", f"ID {tid}")
            length_km = getattr(track, "length_km", 3.2)
            turns = getattr(track, "turns", 12)
            tightest_radius = getattr(track, "tightest_corner_radius_m", 30.0)

        print(f"Track {tid}: {name}")
        length_m = length_km * 1000.0

        instructions = _build_field_based_circuit_instructions(
            length_m, turns, tightest_radius
        )

        for solve_closure in [True, False]:
            options = {"solve_closure": solve_closure, "is_point_to_point": False}
            routes = CircuitGenerator.generate_with_routes(instructions, options)
            main_route = routes.get("main", [])

            if main_route:
                start = main_route[0]
                end = main_route[-1]

                try:
                    # check if it's a dict or object with x,y
                    if isinstance(start, dict):
                        sx, sy = start["x"], start["y"]
                        ex, ey = end["x"], end["y"]
                    else:
                        sx, sy = start.x, start.y
                        ex, ey = end.x, end.y

                    gap = math.sqrt((ex - sx) ** 2 + (ey - sy) ** 2)
                    print(f"  solve_closure={solve_closure}: gap={gap:.4f}m")
                except Exception as e:
                    print(
                        f"  solve_closure={solve_closure}: error accessing coordinates: {e}"
                    )
            else:
                print(f"  solve_closure={solve_closure}: No route generated.")


if __name__ == "__main__":
    main()
