import math
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

repo_root = Path(__file__).resolve().parents[3]
py_pkg = repo_root / "Momentum" / "Python"
sys.path.insert(0, str(py_pkg))
sys.path.insert(0, str(repo_root))

from database.database_manager import DatabaseManager
from tools.validate_track_routes import _build_field_based_circuit_instructions


def gap(routes):
    points = (routes or {}).get("main") or []
    if len(points) < 2:
        return float("inf")
    s, e = points[0], points[-1]
    return math.hypot(float(e.x) - float(s.x), float(e.y) - float(s.y))


if __name__ == "__main__":
    _ = QApplication.instance() or QApplication([])
    from GUI.gui_race_visual import CircuitGenerator

    db = DatabaseManager()
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, length_km, turns, tightest_corner_radius_m FROM tracks WHERE id = 2"
        ).fetchone()
    r = dict(row)
    length_m = float(r["length_km"] or 3.2) * 1000.0
    instr = _build_field_based_circuit_instructions(
        length_m, int(r["turns"] or 10), float(r["tightest_corner_radius_m"] or 30.0)
    )

    solved = CircuitGenerator.generate_with_routes(
        {"solve_closure": True, "instructions": instr}, options={}
    )
    unsolved = CircuitGenerator.generate_with_routes(
        {"solve_closure": False, "instructions": instr}, options={}
    )

    print("id", r["id"], r["name"])
    print("solved_gap", gap(solved))
    print("unsolved_gap", gap(unsolved))
