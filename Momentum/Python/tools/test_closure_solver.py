import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from RaceLogic import closure_solver


def build_template_instructions(track_length_km=5.0):
    return [
        ("S", int(600 * (track_length_km / 6.0))),
        ("C", 45, 170, 60, 0.00008),
        ("S", int(400 * (track_length_km / 6.0))),
        ("C", 65, 95, 50, 0.0001),
        ("S", int(220 * (track_length_km / 6.0))),
        ("C", -55, 100, 52, 0.0001),
        ("S", int(350 * (track_length_km / 6.0))),
        ("C", 155, 48, 42, 0.00014),
        ("S", int(550 * (track_length_km / 6.0))),
        ("C", -65, 145, 58, 0.00009),
        ("S", int(380 * (track_length_km / 6.0))),
        ("C", 55, 115, 54, 0.00009),
        ("S", int(180 * (track_length_km / 6.0))),
        ("C", 60, 90, 50, 0.0001),
        ("S", int(300 * (track_length_km / 6.0))),
        ("C", -50, 135, 56, 0.00009),
        ("S", int(160 * (track_length_km / 6.0))),
        ("C", 50, 135, 56, 0.00009),
        ("S", int(320 * (track_length_km / 6.0))),
    ]


def main():
    instr = build_template_instructions(5.0)
    success, multipliers, diag = closure_solver.solve_closure(instr, max_nfev=1000)
    print("success:", success)
    print("multipliers:", multipliers)
    print("diag:", diag)
    # simulate final pose
    x, y, th = closure_solver._simulate_primitives(
        instr, multipliers if multipliers else [1.0] * len(multipliers)
    )
    print("final pose:", x, y, th)


if __name__ == "__main__":
    main()
