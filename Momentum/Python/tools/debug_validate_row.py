import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

repo_root = Path(__file__).resolve().parents[3]
py_pkg = repo_root / "Momentum" / "Python"
sys.path.insert(0, str(py_pkg))
sys.path.insert(0, str(repo_root))

from database.database_manager import DatabaseManager
from tools.validate_track_routes import _route_errors

if __name__ == "__main__":
    _ = QApplication.instance() or QApplication([])
    from GUI.gui_race_visual import CircuitGenerator

    db = DatabaseManager()
    with db.get_connection() as conn:
        row = conn.execute("SELECT id, name, primary_discipline, is_point_to_point, instructions_json, length_km, turns, longest_straight_m, tightest_corner_radius_m, surface_grip FROM tracks WHERE id = 2").fetchone()
    r = dict(row)
    print(_route_errors(r, CircuitGenerator))
