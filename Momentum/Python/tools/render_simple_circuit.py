"""Render a single simple circuit using the GUI generator with closure solving
and save an offscreen PNG for quick visual verification.
"""
import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from GUI.gui_race_visual import CircuitGenerator, TrackWidget
from RaceLogic import closure_solver
from vehicles.appearance_integration import initialize_appearance_manager


def build_template_instructions(track_length_km=5.0):
    return [
        ('S', int(600 * (track_length_km / 6.0))),
        ('C', 45, 170, 60, 0.00008),
        ('S', int(400 * (track_length_km / 6.0))),
        ('C', 65, 95, 50, 0.0001),
        ('S', int(220 * (track_length_km / 6.0))),
        ('C', -55, 100, 52, 0.0001),
        ('S', int(350 * (track_length_km / 6.0))),
        ('C', 155, 48, 42, 0.00014),
        ('S', int(550 * (track_length_km / 6.0))),
        ('C', -65, 145, 58, 0.00009),
        ('S', int(380 * (track_length_km / 6.0))),
        ('C', 55, 115, 54, 0.00009),
        ('S', int(180 * (track_length_km / 6.0))),
        ('C', 60, 90, 50, 0.0001),
        ('S', int(300 * (track_length_km / 6.0))),
        ('C', -50, 135, 56, 0.00009),
        ('S', int(160 * (track_length_km / 6.0))),
        ('C', 50, 135, 56, 0.00009),
        ('S', int(320 * (track_length_km / 6.0))),
    ]


def render_and_save(track_points, pit_points, joker_points, out_path):
    app = QApplication.instance() or QApplication([])
    appearance = initialize_appearance_manager()
    # estimate track_length from last point.s if present
    track_length = track_points[-1].s if track_points else 0.0

    widget = TrackWidget(track_points, track_length, appearance,
                         track_surface='asphalt', surface_grip=12.0,
                         pit_points=pit_points, joker_points=joker_points)
    widget.resize(1400, 900)

    img = QImage(widget.width(), widget.height(), QImage.Format.Format_ARGB32)
    img.fill(0xFFFFFFFF)
    painter = QPainter(img)
    widget.render(painter)
    painter.end()
    img.save(out_path)
    print(f"Saved {out_path}")


def main():
    instr = build_template_instructions(5.0)
    out_dir = os.path.join(os.path.dirname(__file__), '')

    # 1) Run solver and then generate without rescaling (point-to-point)
    instr_solved = [tuple(x) if isinstance(x, (list, tuple)) else dict(x) for x in instr]
    success, multipliers, diag = closure_solver.solve_closure(instr_solved)
    print(f"Solver success: {success}, diag: {diag}")
    if success:
        closure_solver.apply_multipliers_to_instructions(instr_solved, multipliers)
    wrapper_solved = {'solve_closure': False, 'instructions': instr_solved}
    routes_solved = CircuitGenerator.generate_with_routes(wrapper_solved, options={'is_point_to_point': True})
    main_route_solved = routes_solved.get('main')
    pit_solved = routes_solved.get('pit')
    joker_solved = routes_solved.get('joker')
    out_path_solved = os.path.join(out_dir, 'simple_circuit_solved_no_rescale.png')
    render_and_save(main_route_solved, pit_solved, joker_solved, out_path_solved)
    if main_route_solved:
        last = main_route_solved[-1]
        gap = (last.x ** 2 + last.y ** 2) ** 0.5
        print(f"Solved (no rescale) final gap: {gap:.3f} m, final theta: {getattr(last, 'theta', 0):.3f}")

    # 2) Run generator with its own solve flag (normal path, may rescale)
    # 2) Run generator with its own solve flag (normal path, may rescale)
    # Try iterative append-of-final-straight strategy to close residual gap
    instr_iter = [tuple(x) if isinstance(x, (list, tuple)) else dict(x) for x in instr]
    max_iters = 6
    final_gap = None
    for iteration in range(max_iters):
        wrapper = {'solve_closure': True, 'instructions': instr_iter}
        # use point-to-point mode to avoid display rescaling so gaps are in world coords
        routes = CircuitGenerator.generate_with_routes(wrapper, options={'is_point_to_point': True})
        main_route = routes.get('main')
        pit = routes.get('pit')
        joker = routes.get('joker')
        if not main_route:
            break
        last2 = main_route[-1]
        gap2 = (last2.x ** 2 + last2.y ** 2) ** 0.5
        print(f"Iteration {iteration}: generator gap={gap2:.3f} m")
        if gap2 <= 2.5:
            final_gap = gap2
            break
        # Append a straight roughly equal to remaining gap and retry
        append_len = int(gap2 + 0.5)
        print(f"  Appending straight of length {append_len}m to instructions and retrying")
        instr_iter.append(('S', append_len))

    out_path = os.path.join(out_dir, 'simple_circuit_generator.png')
    render_and_save(main_route, pit, joker, out_path)
    if main_route:
        print(f"Generator final gap after iterations: {final_gap if final_gap is not None else gap2:.3f} m")


if __name__ == '__main__':
    main()
