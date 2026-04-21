"""Validate imported tracks for physical sanity and drawable route coherence.

Checks performed:
- Record-level physical constraints (length, turns, straights, grip, name)
- Route generation viability using GUI circuit generator
- Closed-loop sanity for circuit disciplines
- Point-to-point sanity for drag/point-to-point tracks

Run from Momentum/Python:
    python tools/validate_track_routes.py
"""

import json
import math
import sys
import io
from contextlib import redirect_stdout
from pathlib import Path

from PyQt6.QtWidgets import QApplication

repo_root = Path(__file__).resolve().parents[3]
py_pkg = repo_root / "Momentum" / "Python"
sys.path.insert(0, str(py_pkg))
sys.path.insert(0, str(repo_root))

from database.database_manager import DatabaseManager


def _build_field_based_circuit_instructions(length_m: float, turns_raw: int, tightest_radius_m: float):
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


def _is_point_to_point(row: dict) -> bool:
    discipline = str(row.get("primary_discipline") or "").upper()
    return bool(row.get("is_point_to_point")) or discipline == "DRAG_ACCELERATION"


def _parse_instructions(raw):
    if not raw:
        return None
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
        if isinstance(parsed, list) and parsed:
            return parsed
    except Exception:
        return None
    return None


def _record_errors(row: dict) -> list:
    errs = []
    if not str(row.get("name") or "").strip():
        errs.append("blank name")
    if float(row.get("length_km") or 0) <= 0:
        errs.append("length_km <= 0")
    if int(row.get("turns") or 0) <= 0:
        errs.append("turns <= 0")
    if float(row.get("longest_straight_m") or 0) <= 0:
        errs.append("longest_straight_m <= 0")
    if float(row.get("tightest_corner_radius_m") or 0) <= 0:
        errs.append("tightest_corner_radius_m <= 0")
    grip = float(row.get("surface_grip") or 0)
    if grip < 0.0 or grip > 1.5:
        errs.append("surface_grip out of [0, 1.5]")
    return errs


def _route_errors(row: dict, circuit_generator) -> list:
    errs = []
    length_m = max(100.0, float(row.get("length_km") or 3.2) * 1000.0)
    is_ptp = _is_point_to_point(row)
    instructions = _parse_instructions(row.get("instructions_json"))

    with redirect_stdout(io.StringIO()):
        if instructions:
            wrapper = {"solve_closure": not is_ptp, "instructions": instructions}
            routes = circuit_generator.generate_with_routes(wrapper, options={"is_point_to_point": is_ptp})
            points = routes.get("main") or []
        elif is_ptp:
            points = circuit_generator.generate_with_routes(
                {"instructions": [{"type": "S", "length_m": int(max(350.0, length_m))}]},
                options={"is_point_to_point": True},
            ).get("main") or []
        else:
            field_based = _build_field_based_circuit_instructions(
                length_m=length_m,
                turns_raw=int(row.get("turns") or 10),
                tightest_radius_m=float(row.get("tightest_corner_radius_m") or 30.0),
            )
            routes = circuit_generator.generate_with_routes(
                {"solve_closure": True, "instructions": field_based},
                options={},
            )
            points = routes.get("main") or []

    if len(points) < 20:
        errs.append("too few generated points")
        return errs

    start = points[0]
    end = points[-1]
    gap = math.hypot(float(end.x) - float(start.x), float(end.y) - float(start.y))

    if is_ptp:
        # P2P tracks should not collapse into tiny loops.
        if gap < max(80.0, 0.15 * length_m):
            errs.append(f"point-to-point gap too small ({gap:.1f}m)")
    else:
        # Closed circuits should end near start after closure solve/finalization.
        if gap > max(120.0, 0.12 * length_m):
            errs.append(f"closed-loop gap too large ({gap:.1f}m)")

    return errs


def main() -> int:
    _app = QApplication.instance() or QApplication([])
    from GUI.gui_race_visual import CircuitGenerator

    db = DatabaseManager()

    with db.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, primary_discipline, is_point_to_point,
                   instructions_json, length_km, turns, longest_straight_m,
                   tightest_corner_radius_m, surface_grip
            FROM tracks
            ORDER BY id
            """
        ).fetchall()

    if not rows:
        print("No tracks found in DB.")
        return 1

    failed = []
    for r in rows:
        row = dict(r)
        errs = _record_errors(row)
        errs.extend(_route_errors(row, CircuitGenerator))
        if errs:
            failed.append((row["id"], row["name"], errs))

    total = len(rows)
    ok = total - len(failed)
    print(f"Track route validation: {ok}/{total} passed")

    if failed:
        print("Failures:")
        for tid, name, errs in failed:
            print(f"- id={tid} name={name}: {'; '.join(errs)}")
        return 2

    print("All tracks passed record and route validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
