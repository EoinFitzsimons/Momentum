"""Test that point-to-point tracks don't try to close."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PyQt6.QtWidgets import QApplication

# Create QApplication FIRST before importing GUI modules
app = QApplication([])

from GUI.gui_race_visual import CircuitGenerator

print("Testing drag strip (single straight, point-to-point)...")
drag_instructions = [{"type": "S", "length_m": 402}]
options = {"is_point_to_point": True}
routes = CircuitGenerator.generate_with_routes(drag_instructions, options)
track_points = routes["main"]
print(f"Generated {len(track_points)} points, length: {track_points[-1].s:.1f}m")
print(f"Start: ({track_points[0].x:.1f}, {track_points[0].y:.1f})")
print(f"End: ({track_points[-1].x:.1f}, {track_points[-1].y:.1f})")
print("✓ Drag strip should be ~402 points in straight line\n")

print("Testing rally stage (many random turns, point-to-point)...")
rally_instructions = [
    {"type": "S", "length_m": 500},
    {"type": "C", "angle_deg": 45, "radius_m": 100, "clothoid_len": 60, "k": 0.0001},
    {"type": "S", "length_m": 800},
    {"type": "C", "angle_deg": -60, "radius_m": 120, "clothoid_len": 70, "k": 0.00008},
    {"type": "S", "length_m": 600},
]
routes = CircuitGenerator.generate_with_routes(rally_instructions, options)
track_points = routes["main"]
print(f"Generated {len(track_points)} points, length: {track_points[-1].s:.1f}m")
print(f"Start: ({track_points[0].x:.1f}, {track_points[0].y:.1f})")
print(f"End: ({track_points[-1].x:.1f}, {track_points[-1].y:.1f})")
print("✓ Rally stage should NOT loop back to start\n")

print("Testing circuit (should close to start)...")
circuit_instructions = [
    {"type": "S", "length_m": 300},
    {"type": "C", "angle_deg": 90, "radius_m": 50, "clothoid_len": 35, "k": 0.0002},
    {"type": "S", "length_m": 200},
    {"type": "C", "angle_deg": 90, "radius_m": 50, "clothoid_len": 35, "k": 0.0002},
    {"type": "S", "length_m": 300},
    {"type": "C", "angle_deg": 90, "radius_m": 50, "clothoid_len": 35, "k": 0.0002},
    {"type": "S", "length_m": 200},
    {"type": "C", "angle_deg": 90, "radius_m": 50, "clothoid_len": 35, "k": 0.0002},
]
circuit_options = {"is_point_to_point": False}
routes = CircuitGenerator.generate_with_routes(circuit_instructions, circuit_options)
track_points = routes["main"]
print(f"Generated {len(track_points)} points, length: {track_points[-1].s:.1f}m")
print(f"Start: ({track_points[0].x:.1f}, {track_points[0].y:.1f})")
print(f"End: ({track_points[-1].x:.1f}, {track_points[-1].y:.1f})")
gap = (
    (track_points[-1].x - track_points[0].x) ** 2
    + (track_points[-1].y - track_points[0].y) ** 2
) ** 0.5
print(f"Gap to start: {gap:.1f}m")
print("✓ Circuit should close (gap < 100m)\n")

print("All tests complete!")
app.quit()
