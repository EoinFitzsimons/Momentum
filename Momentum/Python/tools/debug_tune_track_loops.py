import math
import sqlite3
import sys
import io
from contextlib import redirect_stdout
from pathlib import Path
from PyQt6.QtWidgets import QApplication

repo_root = Path(__file__).resolve().parents[3]
py_pkg = repo_root / "Momentum" / "Python"
sys.path.insert(0, str(py_pkg))
sys.path.insert(0, str(repo_root))

FAILED_IDS = [
    151,
    152,
    156,
    157,
    159,
    160,
    161,
    163,
    164,
    166,
    167,
    168,
    169,
    170,
    171,
    172,
    173,
    175,
]


def mk_instr(length_m: float, turns: int, radius: float):
    angle_deg = 360.0 / float(turns)
    corner_arc = max(8.0, radius * math.radians(angle_deg))
    total_corner_len = corner_arc * turns
    remaining = max(120.0, float(length_m) - total_corner_len)
    straight_each = max(30.0, remaining / turns)
    clothoid_len = max(6.0, min(30.0, radius * 0.35))

    ins = []
    for _ in range(turns):
        ins.append({"type": "S", "length_m": int(straight_each)})
        ins.append(
            {
                "type": "C",
                "angle_deg": float(angle_deg),
                "radius_m": float(radius),
                "clothoid_len": float(clothoid_len),
                "k": 0.00011,
            }
        )
    return ins


def gap_of(points):
    if not points or len(points) < 2:
        return float("inf")
    s, e = points[0], points[-1]
    return math.hypot(float(e.x) - float(s.x), float(e.y) - float(s.y))


def best_gap(length_m: float, circuit_generator):
    best = (float("inf"), None, None)
    for turns in range(4, 11):
        for radius in (18, 22, 26, 30, 36, 44, 56):
            ins = mk_instr(length_m, turns, radius)
            with redirect_stdout(io.StringIO()):
                routes = circuit_generator.generate_with_routes(ins, options={})
            g = gap_of((routes or {}).get("main"))
            if g < best[0]:
                best = (g, turns, radius)
    return best


def main():
    _ = QApplication.instance() or QApplication([])
    from GUI.gui_race_visual import CircuitGenerator

    db = sqlite3.connect(py_pkg / "database" / "momentum.db")
    db.row_factory = sqlite3.Row

    for tid in FAILED_IDS:
        r = db.execute(
            "SELECT id, name, length_km FROM tracks WHERE id = ?", (tid,)
        ).fetchone()
        if not r:
            continue
        length_m = float(r["length_km"] or 1.0) * 1000.0
        g, t, rad = best_gap(length_m, CircuitGenerator)
        print(f"{tid}: {r['name']} -> best_gap={g:.1f}m turns={t} radius={rad}")

    db.close()


if __name__ == "__main__":
    main()
