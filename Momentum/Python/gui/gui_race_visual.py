"""
Combined GUI: Race simulation with visual track display.

Integrates:
- Circuit generation from circuit_with_grid.py
- Race simulation engine from gui_game.py
- Real-time car position updates based on simulation events
"""

from services.race_simulation_api import simulate_race
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline
from database.database_manager import DatabaseManager
from vehicles.appearance_integration import VehicleAppearanceManager
from vehicles.vehicle_appearance import (
    Livery,
    VehicleRenderer,
    create_team_livery,
)

from PyQt6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QBrush,
    QPainterPath,
    QKeyEvent,
    QPaintEvent,
    QPixmap,
    QImage,
    QLinearGradient,
    QPolygonF,
)

from PyQt6.QtCore import (
    Qt,
    QPointF,
    QTimer,
    pyqtSignal,
    QObject,
)

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QListWidget,
    QListWidgetItem,
)
import random
from PyQt6.QtWidgets import QHeaderView, QSizePolicy
import sys
import os
import math
import re
import time
import threading
import traceback as _traceback
from typing import Any, List, Dict, Optional, Tuple, cast
from dataclasses import dataclass
from config import RACE_GRID_SIZE, RENDER_FPS
from services.driver_attributes import get_preferred_window_size
from .infield_presets import select_preset
from .props_placer import place_props, draw_props

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CONTROL_LABEL_STYLE = "font-size: 16px; font-weight: bold; color: #FFFFFF;"


def compute_canonical_starting_grid(starting_grid, track_widget) -> list:
    """
    Return a canonical starting grid list where index 0 == start pos 1.

    If the visual `track_widget` provides a cars list and the set of driver
    ids matches `starting_grid` but the order differs, prefer the visual
    ordering (sorted by `s`) which reflects the actual on-track layout.
    Otherwise return `starting_grid` unchanged.
    """
    if not starting_grid:
        return starting_grid
    try:
        tw_cars = getattr(track_widget, 'cars', None)
        if tw_cars:
            # Some track representations use larger `s` for the front
            # of the grid (cars nearer the line). Sort by `s` DESC so
            # that the highest `s` maps to P1. This is robust across
            # different track widget coordinate conventions.
            tw_ids = [getattr(c, 'driver_id', None) for c in sorted(tw_cars, key=lambda c: getattr(c, 's', 0.0), reverse=True)]
            # Force using the track widget ordering as authoritative when
            # the set of drivers matches the recorded starting grid.
            if set(tw_ids) == set(starting_grid):
                return tw_ids
    except Exception:
        pass
    return starting_grid


@dataclass
class TrackPoint:
    s: float  # Arc-length
    x: float
    y: float
    theta: float  # Heading
    curvature: float


@dataclass
class Car:
    """Car with position on track."""
    driver_id: int
    driver_name: str
    s: float  # Current arc-length position (meters)
    colour: QColor
    dnf: bool = False
    # Use 1-based lap counting for UI (show lap 1 as first racing lap)
    lap: int = 1
    total_time: float = 0.0  # Total race time from simulation
    avg_lap_time: float = 60.0  # Average lap time in seconds
    last_lap: int = 0  # Last completed lap number
    velocity_mps: float = 0.0
    movement_direction: float = 0.0
    prev_s: Optional[float] = None
    # Display/interpolation helpers (GUI-only)
    display_s: float = 0.0
    target_s: Optional[float] = None
    prev_update_time: float = 0.0
    target_update_time: float = 0.0


class EventEmitter(QObject):
    """Signal emitter for race events."""
    position_update = pyqtSignal(
        dict)  # {driver_id: {lap, position, total_time}}
    race_finished = pyqtSignal(list)
    event_signal = pyqtSignal(str)


class CircuitGenerator:
    """Generates racing circuit with clothoid transitions."""

    @staticmethod
    def generate(track_length_km: float = 5.0):
        """Generate circuit based on track length."""
        # Backwards-compatible generator: create main route from built-in instructions
        circuit_instructions = [
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

        routes = CircuitGenerator.generate_with_routes(circuit_instructions, {'is_point_to_point': False})
        # preserve backward compatibility: return main route list
        return routes['main']

    @staticmethod
    def generate_with_routes(instructions, options: Optional[Dict] = None):
        """Generate route(s) from an instruction list.

        Returns a dict: {'main': [TrackPoint], 'joker': [TrackPoint] or None, 'pit': [TrackPoint] or None}
        Supported instruction formats: tuple-format (legacy) or dict-format:
          {'type':'S', 'length_m':...}, {'type':'C','radius_m':...,'angle_deg':...},
          {'type':'JOKER', 'instructions':[...]} , {'type':'PIT','instructions':[...]}.
        Options: {'is_point_to_point': bool}
        """
        if options is None:
            options = {}
        is_point_to_point = bool(options.get('is_point_to_point', False))

        # main segments state
        main_segments: List[TrackPoint] = []
        state = {
            'segments': main_segments,
            'current_s': 0,
            'current_x': 0,
            'current_y': 0,
            'current_theta': 0,
            'total_angle': 0,
            'target_length_m': None
        }

        # storage for alternate routes
        routes = {'main': main_segments, 'joker': None, 'pit': None}

        # Internal: process instructions and collect alternate routes when present
        CircuitGenerator._process_instructions(instructions, state, routes, is_point_to_point)

        # Rescale / finalize only for main route unless point-to-point
        if state.get('target_length_m') is None:
            # no explicit target length: leave as-is
            pass
        if not is_point_to_point:
            CircuitGenerator._rescale_to_target_length(main_segments, state)
            CircuitGenerator._finalize_circuit(main_segments)

        return routes

        # (legacy/generated-instructions block removed - generation now returns
        # 'routes' above. This dead code caused undefined-name mypy errors.)

    @staticmethod
    def _process_subinstructions(sub_instructions: List[Any]) -> List[TrackPoint]:
        """Process nested route instructions (e.g., pit/joker) into standalone segments."""
        sub_segments: List[TrackPoint] = []
        sub_state = {
            'segments': sub_segments,
            'current_s': 0,
            'current_x': 0,
            'current_y': 0,
            'current_theta': 0,
            'total_angle': 0,
            'target_length_m': None,
        }
        for instr in sub_instructions:
            CircuitGenerator._process_instructions(
                [instr],
                sub_state,
                {'main': sub_segments, 'joker': None, 'pit': None},
                False,
            )
        if sub_segments:
            CircuitGenerator._finalize_circuit(sub_segments)
        return sub_segments

    @staticmethod
    def _extract_instruction_list(instructions: Any) -> Tuple[List[Any], bool]:
        """Normalize instruction container and extract optional solve-closure flag."""
        solve_requested = False
        instruction_list: List[Any] = []

        if isinstance(instructions, dict) and instructions.get('solve_closure'):
            wrapped_instructions = instructions.get('instructions', [])
            instruction_list = cast(List[Any], wrapped_instructions) if isinstance(wrapped_instructions, list) else []
            solve_requested = True
        elif isinstance(instructions, list) and len(instructions) > 0:
            instruction_list = cast(List[Any], instructions)
            if isinstance(instructions[0], dict) and instructions[0].get('solve_closure'):
                solve_requested = True
        elif isinstance(instructions, list):
            instruction_list = cast(List[Any], instructions)

        return instruction_list, solve_requested

    @staticmethod
    def _maybe_solve_closure(instruction_list: List[Any], solve_requested: bool, is_point_to_point: bool) -> bool:
        """Run analytic closure solver when requested for circuit-style tracks."""
        if not solve_requested or is_point_to_point:
            return False

        from RaceLogic import closure_solver

        try:
            success, multipliers, diag = closure_solver.solve_closure(instruction_list)
            if success:
                closure_solver.apply_multipliers_to_instructions(instruction_list, multipliers)
                return True
            print(f"Closure solver failed: {diag}")
        except Exception as e:
            print(f"Error running closure solver: {e}")
        return False

    @staticmethod
    def _process_instruction_item(instruction: Any, state: Dict[str, Any], routes: Dict[str, Any]) -> None:
        """Dispatch one normalized instruction item."""
        if isinstance(instruction, tuple) or isinstance(instruction, list):
            CircuitGenerator._process_legacy_instruction(instruction, state)
            return
        if isinstance(instruction, dict):
            CircuitGenerator._process_dict_instruction(instruction, state, routes)

    @staticmethod
    def _process_legacy_instruction(instruction: Any, state: Dict[str, Any]) -> None:
        """Handle legacy tuple/list instructions."""
        if not instruction:
            return
        if instruction[0] == 'S':
            CircuitGenerator._add_straight(instruction[1], state)
            return
        if instruction[0] == 'C':
            angle_deg, radius, clothoid_len, k = instruction[1:5]
            CircuitGenerator._add_corner(angle_deg * math.pi / 180, radius, clothoid_len, k, state)

    @staticmethod
    def _process_dict_instruction(instruction: Dict[str, Any], state: Dict[str, Any], routes: Dict[str, Any]) -> None:
        """Handle dict-based instructions including nested route blocks."""
        typ = instruction.get('type')
        if not typ:
            return
        typ = str(typ).upper()

        if typ == 'S':
            CircuitGenerator._add_straight(int(instruction.get('length_m', 50)), state)
            return
        if typ == 'C':
            angle = float(instruction.get('angle_deg', 45))
            radius = float(instruction.get('radius_m', 80))
            clothoid = int(instruction.get('clothoid_len', 50))
            k = float(instruction.get('k', 0.00009))
            CircuitGenerator._add_corner(angle * math.pi / 180, radius, clothoid, k, state)
            return
        if typ in ('PIT', 'PIT_ENTRY', 'PIT_EXIT'):
            pit_instr = instruction.get('instructions')
            if pit_instr:
                routes['pit'] = CircuitGenerator._process_subinstructions(cast(List[Any], pit_instr))
            else:
                pit_len = int(instruction.get('length_m', 60))
                pit_state = {
                    'segments': [],
                    'current_s': 0,
                    'current_x': 0,
                    'current_y': 0,
                    'current_theta': state['current_theta'],
                    'total_angle': 0,
                    'target_length_m': None,
                }
                CircuitGenerator._add_straight(pit_len, pit_state)
                routes['pit'] = pit_state['segments']
            return
        if typ == 'JOKER':
            joker_instr = instruction.get('instructions')
            if joker_instr:
                routes['joker'] = CircuitGenerator._process_subinstructions(cast(List[Any], joker_instr))

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize radians to [-pi, pi] for stable closure math."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    @staticmethod
    def _compute_closure_metrics(state: Dict[str, Any], start_x: float, start_y: float) -> Tuple[float, float, float]:
        """Return (distance_to_start, heading_error, angle_deficit)."""
        dx = start_x - state['current_x']
        dy = start_y - state['current_y']
        distance_to_start = math.hypot(dx, dy)
        angle_to_start = math.atan2(dy, dx)
        heading_error = CircuitGenerator._normalize_angle(angle_to_start - state['current_theta'])
        angle_deficit = 2 * math.pi - state['total_angle']
        return distance_to_start, heading_error, angle_deficit

    @staticmethod
    def _add_initial_closure_shape(state: Dict[str, Any], distance_to_start: float, angle_deficit: float) -> None:
        """Add a coarse closure shape before iterative refinement."""
        if abs(angle_deficit) > math.radians(120):
            CircuitGenerator._add_straight(int(distance_to_start * 0.15), state)
            CircuitGenerator._add_corner(angle_deficit * 0.35, 110, 50, 0.00009, state)
            CircuitGenerator._add_straight(int(distance_to_start * 0.15), state)
            CircuitGenerator._add_corner(angle_deficit * -0.15, 120, 52, 0.00009, state)
            CircuitGenerator._add_straight(int(distance_to_start * 0.15), state)
            CircuitGenerator._add_corner(angle_deficit * 0.80, 100, 48, 0.00009, state)
            return
        if abs(angle_deficit) > math.radians(60):
            CircuitGenerator._add_straight(int(distance_to_start * 0.2), state)
            CircuitGenerator._add_corner(angle_deficit * 0.6, 115, 52, 0.00009, state)
            CircuitGenerator._add_straight(int(distance_to_start * 0.2), state)
            CircuitGenerator._add_corner(angle_deficit * 0.4, 125, 54, 0.00009, state)
            return
        CircuitGenerator._add_straight(int(distance_to_start * 0.3), state)
        CircuitGenerator._add_corner(angle_deficit, 130, 55, 0.00008, state)

    @staticmethod
    def _closure_iteration_metrics(state: Dict[str, Any], start_x: float, start_y: float) -> Tuple[float, float, float]:
        """Return per-iteration closure metrics (gap distance, heading error rad/deg)."""
        gap_dx = start_x - state['current_x']
        gap_dy = start_y - state['current_y']
        gap_dist = math.hypot(gap_dx, gap_dy)
        gap_angle = math.atan2(gap_dy, gap_dx)
        gap_heading_error = CircuitGenerator._normalize_angle(gap_angle - state['current_theta'])
        heading_error_deg = abs(math.degrees(gap_heading_error))
        return gap_dist, gap_heading_error, heading_error_deg

    @staticmethod
    def _should_stop_closure_iteration(iteration: int, gap_dist: float, prev_gap: float, heading_error_deg: float) -> bool:
        """Return True if closure iteration should stop due to divergence or convergence."""
        if gap_dist > prev_gap * 1.2:
            print(
                f"  [CLOSURE ITER {iteration}] DIVERGING - stopping iterations (gap increased from {prev_gap:.1f}m to {gap_dist:.1f}m)")
            return True

        if gap_dist < 100 and heading_error_deg < 20:
            print(
                f"  [CLOSURE ITER {iteration}] GOOD ENOUGH - gap={gap_dist:.1f}m, heading={heading_error_deg:.1f}deg - final straight will handle it")
            return True

        if gap_dist < 200 and heading_error_deg < 25:
            print(
                f"  [CLOSURE ITER {iteration}] GOOD ENOUGH - gap={gap_dist:.1f}m, heading={heading_error_deg:.1f}deg - final straight will handle it")
            return True

        return False

    @staticmethod
    def _closure_correction_factor(gap_dist: float, heading_error_deg: float) -> float:
        """Compute proportional closure correction factor from distance and heading quality."""
        if gap_dist > 300:
            base_factor = 0.6
        elif gap_dist > 150:
            base_factor = 0.45
        elif gap_dist > 75:
            base_factor = 0.3
        else:
            base_factor = 0.2

        if heading_error_deg < 5:
            return base_factor * 0.3
        if heading_error_deg < 15:
            return base_factor * 0.5
        if heading_error_deg < 30:
            return base_factor * 0.7
        return base_factor

    @staticmethod
    def _iterative_closure_refinement(state: Dict[str, Any], start_x: float, start_y: float) -> None:
        """Refine closure with small heading corrections while avoiding divergence."""
        prev_gap = float('inf')
        for iteration in range(12):
            gap_dist, gap_heading_error, heading_error_deg = CircuitGenerator._closure_iteration_metrics(
                state,
                start_x,
                start_y,
            )

            print(
                f"  [CLOSURE ITER {iteration}] Gap: {gap_dist:.1f}m, Heading error: {math.degrees(gap_heading_error):.1f}deg")

            if CircuitGenerator._should_stop_closure_iteration(iteration, gap_dist, prev_gap, heading_error_deg):
                break

            correction_factor = CircuitGenerator._closure_correction_factor(gap_dist, heading_error_deg)

            if abs(gap_heading_error) > math.radians(1):
                CircuitGenerator._add_corner(gap_heading_error * correction_factor, 180, 60, 0.00006, state)

            prev_gap = gap_dist

    @staticmethod
    def _apply_heuristic_closure(state: Dict[str, Any], start_x: float, start_y: float, distance_to_start: float, angle_deficit: float) -> None:
        """Apply non-analytic closure correction for looped circuits."""
        if abs(angle_deficit) <= 0.1 and distance_to_start <= 50:
            return

        CircuitGenerator._add_initial_closure_shape(state, distance_to_start, angle_deficit)
        CircuitGenerator._iterative_closure_refinement(state, start_x, start_y)

        final_gap_dist = math.hypot(start_x - state['current_x'], start_y - state['current_y'])
        print(f"  [CLOSURE FINAL] Gap before final straight: {final_gap_dist:.1f}m")
        if final_gap_dist > 2:
            CircuitGenerator._add_straight(int(final_gap_dist) + 5, state)

    @staticmethod
    def _process_instructions(instructions: Any, state: Dict[str, Any], routes: Dict[str, Any], is_point_to_point: bool = False):
        start_x, start_y = 0, 0
        instruction_list, solve_requested = CircuitGenerator._extract_instruction_list(instructions)
        closure_solved = CircuitGenerator._maybe_solve_closure(instruction_list, solve_requested, is_point_to_point)

        for instruction in instruction_list:
            CircuitGenerator._process_instruction_item(instruction, state, routes)

        distance_to_start, heading_error, angle_deficit = CircuitGenerator._compute_closure_metrics(state, start_x, start_y)

        if closure_solved:
            print(
                f"  [CLOSURE solver] Distance to start: {distance_to_start:.1f}m, Heading error: {math.degrees(heading_error):.1f}deg, Angle deficit: {math.degrees(angle_deficit):.1f}deg")

        if not is_point_to_point:
            print(
                f"  [CLOSURE] Distance to start: {distance_to_start:.1f}m, Heading error: {math.degrees(heading_error):.1f}deg, Angle deficit: {math.degrees(angle_deficit):.1f}deg")

        if not closure_solved and not is_point_to_point:
            CircuitGenerator._apply_heuristic_closure(state, start_x, start_y, distance_to_start, angle_deficit)

        if not is_point_to_point:
            final_gap = math.hypot(start_x - state['current_x'], start_y - state['current_y'])
            print(f"  [CLOSURE] Final gap after closure: {final_gap:.1f}m")

    @staticmethod
    def _add_straight(length, state):
        length = int(length)
        segments = state['segments']
        for i in range(length):
            s = state['current_s'] + i
            state['current_x'] += math.cos(state['current_theta'])
            state['current_y'] += math.sin(state['current_theta'])
            segments.append(
                TrackPoint(
                    s,
                    state['current_x'],
                    state['current_y'],
                    state['current_theta'],
                    0))
        state['current_s'] += length

    @staticmethod
    def _add_corner(target_angle, radius, clothoid_len, k_clothoid, state):
        entry_start = state['current_theta']
        sign = 1 if target_angle > 0 else -1

        CircuitGenerator._add_clothoid(
            clothoid_len, k_clothoid, sign, state, reverse=False)
        arc_angle = target_angle - 2 * (state['current_theta'] - entry_start)
        CircuitGenerator._add_arc(arc_angle, radius, sign, state)
        CircuitGenerator._add_clothoid(
            clothoid_len, k_clothoid, sign, state, reverse=True)

        state['total_angle'] += target_angle

    @staticmethod
    def _add_clothoid(clothoid_len, k_clothoid, sign, state, reverse):
        segments = state['segments']
        for i in range(clothoid_len):
            curvature = k_clothoid * \
                (clothoid_len - i if reverse else i) * sign
            state['current_theta'] += curvature
            state['current_x'] += math.cos(state['current_theta'])
            state['current_y'] += math.sin(state['current_theta'])
            segments.append(TrackPoint(state['current_s'] + i, state['current_x'], state['current_y'],
                                       state['current_theta'], curvature))
        state['current_s'] += clothoid_len

    @staticmethod
    def _add_arc(arc_angle, radius, sign, state):
        segments = state['segments']
        arc_curvature = sign / radius
        arc_length = int(abs(radius * arc_angle))
        for i in range(arc_length):
            state['current_theta'] += arc_curvature
            state['current_x'] += math.cos(state['current_theta'])
            state['current_y'] += math.sin(state['current_theta'])
            segments.append(TrackPoint(state['current_s'] + i, state['current_x'], state['current_y'],
                                       state['current_theta'], arc_curvature))
        state['current_s'] += arc_length

    @staticmethod
    def _rescale_to_target_length(segments, state):
        """Rescale all arc-length values to match target track length exactly."""
        if not segments or 'target_length_m' not in state or state.get('target_length_m') is None:
            return

        target_length = state['target_length_m']
        actual_length = state['current_s']

        if actual_length == 0:
            return

        scale_factor = target_length / actual_length
        print(
            f"  [RESCALE] Adjusting track length from {
                actual_length:.0f}m to {
                target_length:.0f}m (scale: {
                scale_factor:.3f})")

        # Rescale all arc-length values
        for segment in segments:
            segment.s = segment.s * scale_factor

        # Update state to reflect new length
        state['current_s'] = target_length

    @staticmethod
    def _finalize_circuit(segments):
        """Scale and centre the circuit."""
        if not segments:
            return

        # Verify closure
        start_x, start_y = segments[0].x, segments[0].y
        end_x, end_y = segments[-1].x, segments[-1].y
        gap = math.hypot(end_x - start_x, end_y - start_y)
        print(f"  [FINALIZE] Track closure gap: {gap:.1f}m (should be near 0)")

        # Scale and centre for display
        min_x = min(seg.x for seg in segments)
        max_x = max(seg.x for seg in segments)
        min_y = min(seg.y for seg in segments)
        max_y = max(seg.y for seg in segments)

        width = max_x - min_x
        height = max_y - min_y
        scale = min(1000 / width, 700 / height)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        for seg in segments:
            seg.x = (seg.x - center_x) * scale
            seg.y = (seg.y - center_y) * scale

        print(
            f"  [FINALIZE] Track scaled and centred: {
                len(segments)} points")


class TrackWidget(QWidget):
    """Widget displaying the racing circuit and cars."""

    def __init__(self, track_points: List[TrackPoint], track_length: float,
                 appearance_manager: VehicleAppearanceManager,
                 track_surface: str = "asphalt", surface_grip: Optional[float] = None,
                 pit_points: Optional[List[TrackPoint]] = None,
                 joker_points: Optional[List[TrackPoint]] = None):
        super().__init__()
        self.track_points = track_points
        self.track_length = track_length
        self.track_surface = track_surface
        self.surface_grip = surface_grip
        # Optional alternate routes (pit lane, joker lap)
        self.pit_points = pit_points
        self.joker_points = joker_points
        self.cars: List[Car] = []
        # Remove fixed minimum size - let layout determine size
        # self.setMinimumSize(1400, 900)
        self.race_active = False
        self.start_time = 0.0

        # Use shared appearance manager so liveries created in RaceWindow are visible here
        self.appearance_manager = appearance_manager

        # Camera settings
        self.camera_mode = 'full'
        self.follow_car_id: Optional[int] = None
        self.camera_zoom = 1.0
        self.camera_x = 0
        self.camera_y = 0
        self.camera_rotation = 0
        self._init_visual_caches()
        self._init_grass_tile_cache()
        self._init_animation_timer()
        # Cache for generated infield pixmaps keyed by (w,h,seed,palette)
        self._infield_cache: Dict[tuple, QPixmap] = {}
        # Cache for placed props keyed by same key as pixmap
        self._infield_props_cache: Dict[tuple, list] = {}
        self._normalize_track_arc_lengths()
        # Diagnostic: recent large-jump history per car (time, prev_display, normalized_pos, delta)
        self._telemetry_jumps: Dict[int, List[tuple]] = {}

    def _init_visual_caches(self) -> None:
        """Initialize cached rendering resources and asset paths."""
        self._cached_track_bounds = None
        self._cached_track_zoom = 1.0
        self._cached_forest_pixmap = None
        self._cached_inner_infield_polygon = None
        self._cached_assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        self._cached_forest_tile_path = os.path.join(self._cached_assets_dir, 'forest_tile.png')
        self._forest_tile_exists = os.path.exists(self._cached_forest_tile_path)
        self._grass_tile_pixmap: Optional[QPixmap] = None
        self._grass_tile_mtime: Optional[int] = None

    def _init_grass_tile_cache(self) -> None:
        """Load optional grass tile texture and mtime metadata."""
        try:
            grass_path = os.path.join(self._cached_assets_dir, 'grass_tile.png')
            if not os.path.exists(grass_path):
                return
            gp = QPixmap(grass_path)
            if gp.isNull():
                return
            self._grass_tile_pixmap = gp
            try:
                self._grass_tile_mtime = int(os.path.getmtime(grass_path))
            except Exception:
                self._grass_tile_mtime = None
        except Exception:
            self._grass_tile_pixmap = None
            self._grass_tile_mtime = None

    def _init_animation_timer(self) -> None:
        """Create animation timer with capped render frequency."""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_cars)
        try:
            effective_fps = max(1, min(RENDER_FPS, 60))
            interval_ms = max(1, int(1000 / effective_fps))
        except Exception:
            interval_ms = 16
        self.animation_timer.setInterval(interval_ms)

    def _normalize_track_arc_lengths(self) -> None:
        """Rescale generated arc-length coordinates to authoritative track length."""
        try:
            if not (self.track_points and self.track_length and len(self.track_points) > 1):
                return
            gen_length = float(self.track_points[-1].s)
            if gen_length <= 0.0 or abs(gen_length - float(self.track_length)) <= 1.0:
                return
            scale = float(self.track_length) / gen_length
            for pt in self.track_points:
                pt.s = float(pt.s) * scale
        except Exception:
            pass

    def set_camera_mode(self, mode: str, follow_car_id: Optional[int] = None):
        """Set camera mode and target car.
        
        Args:
            mode: 'full' for full track view or 'follow' for car-follow view
            follow_car_id: Driver ID to follow (only used when mode='follow')
        """
        self.camera_mode = mode
        if mode == 'follow' and follow_car_id is not None:
            self.follow_car_id = int(follow_car_id)
            self.camera_zoom = 3.0  # 3x zoom for follow camera
            print(f"[CAMERA] Set follow_car_id to {self.follow_car_id} (zoom: 3.0x)")
        else:
            self.follow_car_id = None
            if mode == 'full':
                self.camera_zoom = 1.0
                self.camera_rotation = 0
        self.update()

    def _point_at_s(self, s: float) -> Optional[TrackPoint]:
        """Return an interpolated TrackPoint at arc-length s (meters).

        Handles wrap-around and non-uniform sampling by binary-searching the
        nearest segment and linearly interpolating between samples. Returns
        a new TrackPoint (s,x,y,theta,curvature).
        """
        if not getattr(self, 'track_points', None) or not self.track_length or self.track_length <= 0:
            return None

        target = float(s) % float(self.track_length)
        pts = self.track_points
        # Binary search for first index with s >= target
        left, right = 0, len(pts) - 1
        while left < right:
            mid = (left + right) // 2
            if pts[mid].s < target:
                left = mid + 1
            else:
                right = mid
        idx = max(0, min(left, len(pts) - 1))
        next_pt = pts[idx]
        prev_idx = idx - 1 if idx > 0 else len(pts) - 1
        prev_pt = pts[prev_idx]

        prev_s = float(prev_pt.s)
        next_s = float(next_pt.s)

        # Handle wrap-around between last and first point
        if next_s <= prev_s:
            next_s += float(self.track_length)
        adj_target = float(target)
        if adj_target < prev_s:
            adj_target += float(self.track_length)

        span = next_s - prev_s
        if span == 0:
            t = 0.0
        else:
            t = max(0.0, min(1.0, (adj_target - prev_s) / span))

        # Linear interpolation for position
        x = prev_pt.x + (next_pt.x - prev_pt.x) * t
        y = prev_pt.y + (next_pt.y - prev_pt.y) * t

        # Angular interpolation (shortest path)
        a0 = prev_pt.theta
        a1 = next_pt.theta
        diff = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        theta = a0 + diff * t

        # Curvature interpolation
        curvature = prev_pt.curvature + (next_pt.curvature - prev_pt.curvature) * t

        interp_s = prev_s + span * t
        interp_s = interp_s % float(self.track_length)

        return TrackPoint(interp_s, x, y, theta, curvature)

    def set_cars(self, cars: List[Car]):
        """Update car list."""
        self.cars = cars
        self.update()

    def start_animation(self):
        """Start smooth animation."""
        self.race_active = True
        self.race_start_time = time.time()
        for car in self.cars:
            car.total_time = 0.0
            # Start lap counting at 1 (first racing lap)
            car.lap = 1
            car.s = 0.0
            # initialize interpolation state
            car.display_s = car.s
            car.target_s = car.s
            now = time.time()
            car.prev_update_time = now
            car.target_update_time = now
        self.animation_timer.start()

    def stop_animation(self):
        """Stop animation."""
        self.race_active = False
        self.animation_timer.stop()

    def update_car_position(self, driver_id: int, lap: int,
                            position: int, total_time: float):
        """Update specific car position based on simulation data (legacy method)."""
        for car in self.cars:
            if car.driver_id == driver_id:
                # Engine reports laps completed (0 = none). Convert to
                # 1-based current lap for UI (current lap = laps_completed + 1)
                car.lap = max(1, int(lap) + 1)
                car.total_time = total_time

                # Calculate average lap time
                if lap > 0:
                    car.avg_lap_time = total_time / lap

                # Calculate position based on total time and track length
                if car.avg_lap_time > 0 and self.track_length > 0:
                    laps_completed = total_time / car.avg_lap_time
                    sim_pos = (laps_completed * self.track_length) % self.track_length
                else:
                    sim_pos = 0.0

                # Update authoritative simulation position and set interpolation
                # targets so the GUI animates smoothly between legacy position updates.
                prev_display = getattr(car, 'display_s', None)
                now = time.time()
                car.prev_s = prev_display if prev_display is not None else getattr(car, 's', sim_pos)
                car.prev_update_time = getattr(car, 'target_update_time', now) or now
                car.target_s = sim_pos
                car.target_update_time = now
                car.s = sim_pos

                car.last_lap = lap
                break

    def update_car_realtime(self, driver_id: int,
                            position_m: float, lap: int, velocity_mps: float):
        """
        *** CRITICAL FUNCTION: Real-time car position updates from race engine ***

        This function is called 30 times per second (30 FPS) by the race engine.
        It updates the visual position of each car on the track.

        Args:
            driver_id: Unique driver identifier (1-10)
            position_m: Absolute position in meters from race start (can exceed track length)
            lap: Current lap number (0 = formation lap, 1+ = racing)
            velocity_mps: Current velocity in meters per second

        HOW IT WORKS:
        1. Receives position from physics engine (meters from race start)
        2. Maps to visual track using modulo (wraps position to track length)
        3. Updates car object with new position and lap
        4. Triggers repaint so car appears in new location

        THREADING:
        - Called from race simulation thread (NOT main GUI thread)
        - Must be thread-safe (check widget validity before accessing)
        - Uses Qt signals to ensure thread safety
        """
        if not self._can_accept_realtime_updates():
            return

        if velocity_mps < 0.1:
            print(
                f"WARNING: Car {driver_id} has near-zero velocity: {
                    velocity_mps:.2f} m/s at pos={
                    position_m:.1f}m, lap={lap}")

        car = self._find_car_by_driver_id(driver_id)
        if car is None:
            print(f"  [ERROR] update_car_realtime: Unknown driver_id={driver_id}")
            self.update()
            return

        self._apply_realtime_position(car, position_m)
        self._update_realtime_car_state(car, lap, velocity_mps)
        self._record_realtime_update(driver_id, car, lap)

        # Trigger repaint
        self.update()

    def _can_accept_realtime_updates(self) -> bool:
        """Return whether this widget is still valid/visible for realtime updates."""
        try:
            if not self.isVisible():
                return False
        except RuntimeError:
            return False

        if not hasattr(self, 'cars') or not self.cars or not hasattr(self, 'track_points'):
            return False
        return True

    def _find_car_by_driver_id(self, driver_id: int) -> Optional[Car]:
        """Find a car by driver id from the active grid list."""
        for car in self.cars:
            if car.driver_id == driver_id:
                return car
        return None

    def _apply_realtime_position(self, car: Car, position_m: float) -> None:
        """Map engine position to visual track position and update interpolation state."""
        if self.track_length <= 0 or len(self.track_points) <= 0:
            car.s = position_m
            return

        normalized_pos = position_m % self.track_length
        if not hasattr(car, 'prev_s') or car.prev_s is None:
            car.prev_s = normalized_pos

        prev_display = car.display_s if hasattr(car, 'display_s') and car.display_s is not None else getattr(car, 's', normalized_pos)

        # Preserve previous display position; animation timer interpolates from prev -> target.
        car.prev_s = prev_display
        car.prev_update_time = getattr(car, 'target_update_time', time.time()) or time.time()
        car.target_s = normalized_pos
        car.target_update_time = time.time()
        car.s = normalized_pos

        # Keep heading smooth when crossing lap boundary by applying shortest wrap delta.
        prev_s_val = car.prev_s if car.prev_s is not None else normalized_pos
        movement = normalized_pos - prev_s_val
        if self.track_length and movement < -self.track_length / 2:
            movement += self.track_length
        elif self.track_length and movement > self.track_length / 2:
            movement -= self.track_length
        car.movement_direction = movement

    def _update_realtime_car_state(self, car: Car, lap: int, velocity_mps: float) -> None:
        """Update non-positional realtime fields from the race engine."""
        car.lap = max(1, int(lap) + 1)
        car.velocity_mps = velocity_mps

    def _record_realtime_update(self, driver_id: int, car: Car, lap: int) -> None:
        """Track update frequency for coarse diagnostics without flooding logs."""
        if not hasattr(self, '_update_count'):
            self._update_count: Dict[int, int] = {}
        self._update_count[driver_id] = self._update_count.get(driver_id, 0) + 1

        if self._update_count[driver_id] % 60 == 0:
            print(f"  [CAR UPDATE] {car.driver_name} (ID:{driver_id}): "
                  f"{self._update_count[driver_id]} updates received, "
                  f"position={car.s:.1f}m, lap={lap}")

    def _animate_cars(self):
        """Smoothly update car positions based on simulation time - just trigger repaint."""
        if not self.race_active:
            return
        now = time.time()
        for car in self.cars:
            car.display_s = self._interpolate_display_s(car, now)

        self.update()

    def _interpolate_display_s(self, car: Car, now: float) -> float:
        """Compute displayed position using shortest-path interpolation on looped track."""
        try:
            if not self._has_interpolation_window(car):
                return car.s
            t = self._compute_interpolation_factor(car, now)
            prev = car.prev_s if car.prev_s is not None else car.s
            target = car.target_s if car.target_s is not None else car.s
            if self.track_length and self.track_length > 0:
                return self._interpolate_circular(prev, target, t)
            return prev + (target - prev) * t
        except Exception:
            return car.s

    def _has_interpolation_window(self, car: Car) -> bool:
        return bool(
            car.target_update_time
            and car.prev_update_time
            and car.target_update_time > car.prev_update_time
        )

    def _compute_interpolation_factor(self, car: Car, now: float) -> float:
        span = car.target_update_time - car.prev_update_time
        if span <= 0:
            return 1.0
        return min(1.0, max(0.0, (now - car.prev_update_time) / span))

    def _interpolate_circular(self, prev: float, target: float, t: float) -> float:
        delta = target - prev
        if delta > self.track_length / 2:
            delta -= self.track_length
        elif delta < -self.track_length / 2:
            delta += self.track_length
        return (prev + delta * t) % self.track_length

    def mark_dnf(self, driver_id: int):
        """Mark car as DNF."""
        # Thread safety: check if widget is still valid
        if not hasattr(self, 'cars') or not self.cars:
            return
        for car in self.cars:
            if car.driver_id == driver_id:
                car.dnf = True
                break
        self.update()

    def paintEvent(self, a0: Optional[QPaintEvent]):
        if a0 is None:
            return
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor(28, 90, 36))
            center_x = self.width() // 2
            center_y = self.height() // 2
            painter.save()
            self._apply_camera_transform(painter, center_x, center_y)
            self._draw_world_forest_layers(painter)

            self._draw_runoff_areas(painter)  # Layer 2
            self._draw_grandstands(painter)    # Layer 3
            self._draw_garages(painter)        # Layer 4
            # Draw joker/pit if present
            self._draw_joker(painter)          # optional joker route
            self._draw_pit_lane(painter)       # Layer 5
            self._draw_track(painter)          # Layers 6-12
            self._draw_cars(painter)           # Layer 13

            painter.restore()
            painter.end()
        except Exception as e:
            print(f"ERROR in paintEvent: {e}")
            _traceback.print_exc()

    def _apply_camera_transform(self, painter, center_x: int, center_y: int) -> None:
        """Apply follow/full camera transform before world-space drawing."""
        if self.camera_mode == 'follow' and self.follow_car_id is not None:
            if self._try_apply_follow_camera(painter, center_x, center_y):
                return
            self._apply_full_view_fallback(painter, center_x, center_y)
            return
        self._apply_full_track_camera(painter, center_x, center_y)

    def _try_apply_follow_camera(self, painter, center_x: int, center_y: int) -> bool:
        followed_car = next((car for car in self.cars if car.driver_id == self.follow_car_id), None)
        if followed_car is None or len(self.track_points) <= 0 or self.track_length <= 0:
            if self.follow_car_id is not None:
                print(f"[CAMERA] Followed car {self.follow_car_id} not found or no track data - falling back to full view")
            return False
        try:
            normalized_s = float(followed_car.s) % float(self.track_length)
            pt = self._point_at_s(normalized_s) or self.track_points[0]
            painter.translate(center_x, center_y)
            painter.rotate(math.degrees(pt.theta))
            painter.scale(self.camera_zoom, -self.camera_zoom)
            painter.translate(-pt.x, -pt.y)
            return True
        except Exception as e:
            print(f"[CAMERA] Follow camera error: {e} - falling back to full view")
            return False

    def _apply_full_view_fallback(self, painter, center_x: int, center_y: int) -> None:
        painter.translate(center_x, center_y)
        painter.scale(1, -1)
        self.camera_mode = 'full'

    def _apply_full_track_camera(self, painter, center_x: int, center_y: int) -> None:
        painter.translate(center_x, center_y)
        base_zoom = self._compute_full_view_zoom()
        painter.scale(base_zoom, -base_zoom)

    def _compute_full_view_zoom(self) -> float:
        """Compute fit-to-viewport zoom for full-track mode."""
        if self._cached_track_bounds is None and self.track_points:
            track_min_x = min(pt.x for pt in self.track_points)
            track_max_x = max(pt.x for pt in self.track_points)
            track_min_y = min(pt.y for pt in self.track_points)
            track_max_y = max(pt.y for pt in self.track_points)
            self._cached_track_bounds = (track_max_x - track_min_x, track_max_y - track_min_y)

        if not self._cached_track_bounds:
            return 1.0

        track_width, track_height = self._cached_track_bounds
        padding_factor = 1.15
        zoom_x = (self.width() * 0.95) / (track_width * padding_factor) if track_width > 0 else 1.0
        zoom_y = (self.height() * 0.95) / (track_height * padding_factor) if track_height > 0 else 1.0
        return max(0.5, min(min(zoom_x, zoom_y), 2.5))

    def _draw_world_forest_layers(self, painter) -> None:
        """Draw cached large forest and infield forest overlays in world space."""
        self._draw_world_forest_tile(painter)
        self._draw_world_inner_forest_band(painter)

    def _draw_world_forest_tile(self, painter) -> None:
        try:
            painter.save()
            if self._forest_tile_exists:
                ft_pix = QPixmap(self._cached_forest_tile_path)
                if not ft_pix.isNull():
                    painter.drawTiledPixmap(int(-5000), int(-5000), int(10000), int(10000), ft_pix)
            painter.restore()
        except Exception:
            pass

    def _draw_world_inner_forest_band(self, painter) -> None:
        try:
            if self._cached_inner_infield_polygon is None and self.track_points:
                track_width = 14
                inner_infield_points = []
                inner_shrink = max(48, int(min(self.width(), self.height()) * 0.14))
                for pt in self.track_points:
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    iix = pt.x - normal_x * (track_width - 2 + inner_shrink)
                    iiy = pt.y - normal_y * (track_width - 2 + inner_shrink)
                    inner_infield_points.append(QPointF(iix, iiy))
                if inner_infield_points:
                    self._cached_inner_infield_polygon = QPolygonF(inner_infield_points)

            if not self._cached_inner_infield_polygon:
                return

            band_path = QPainterPath()
            band_path.addPolygon(self._cached_inner_infield_polygon)
            painter.save()
            painter.setClipPath(band_path)
            if self._forest_tile_exists:
                ft_pix = QPixmap(self._cached_forest_tile_path)
                if not ft_pix.isNull():
                    painter.drawTiledPixmap(int(-2000), int(-2000), int(self.width() * 4), int(self.height() * 4), ft_pix)
            painter.restore()
        except Exception:
            pass

    def _draw_runoff_areas(self, painter):
        """Draw red asphalt runoff zones on outside of fast corners."""
        try:
            if not self.track_points:
                return
            TRACK_WIDTH = 14
            for i in range(0, len(self.track_points) - 1):
                pt = self.track_points[i]
                next_pt = self.track_points[i + 1]

                # Fast corners only (high curvature)
                if abs(pt.curvature) > 0.004:
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    next_normal_x = -math.sin(next_pt.theta)
                    next_normal_y = math.cos(next_pt.theta)

                    # Draw runoff on outside of corner (8m wide)
                    runoff_inner = TRACK_WIDTH + 1
                    runoff_outer = TRACK_WIDTH + 9

                    painter.setPen(QPen(QColor(220, 90, 90), 8))  # Red asphalt
                    if pt.curvature > 0:  # Left turn - runoff on right
                        mid_offset = (runoff_inner + runoff_outer) / 2
                        painter.drawLine(
                            int(pt.x + normal_x * mid_offset),
                            int(pt.y + normal_y * mid_offset),
                            int(next_pt.x + next_normal_x * mid_offset),
                            int(next_pt.y + next_normal_y * mid_offset)
                        )
                    else:  # Right turn - runoff on left
                        mid_offset = (runoff_inner + runoff_outer) / 2
                        painter.drawLine(
                            int(pt.x - normal_x * mid_offset),
                            int(pt.y - normal_y * mid_offset),
                            int(next_pt.x - next_normal_x * mid_offset),
                            int(next_pt.y - next_normal_y * mid_offset)
                        )
        except Exception:
            pass

    def _generate_infield_pixmap(self, bbox, w: int, h: int, seed: int) -> QPixmap:
        """Generate a procedural blended turf pixmap for the given bbox.

        bbox: QRectF in world coords (top-left origin)
        w,h: integer pixel dimensions for the pixmap
        seed: integer seed to vary output per-track
        Uses `select_preset` to pick a color palette based on `track_surface`
        and `surface_grip` so biomes vary by track parameters.
        """
        try:
            pix = QPixmap(w, h)
            pix.fill(QColor(0, 0, 0, 0))
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)

            palette = select_preset(getattr(self, 'track_surface', ''), getattr(self, 'surface_grip', None), seed)
            muted_base = self._compute_muted_base_color(palette)
            highlight = palette.get('highlight', QColor(95, 180, 85))
            rnd = random.Random(seed)

            self._paint_infield_base_layers(p, w, h, muted_base)
            self._paint_infield_texture_overlay(p, w, h, palette)
            self._paint_infield_noise(p, rnd, w, h, muted_base, palette)
            self._paint_infield_molehills(p, rnd, w, h, muted_base, palette)
            self._paint_infield_streaks(p, rnd, w, h, palette)
            self._paint_infield_mowing_stripes(p, w, h, muted_base, highlight, palette)

            p.end()
            return pix
        except Exception:
            # Return a tiny fallback pixmap
            p = QPixmap(max(2, w), max(2, h))
            p.fill(QColor(34, 139, 34))
            return p

    def _compute_muted_base_color(self, palette: Dict[str, Any]) -> QColor:
        """Return desaturated base color for infield painting."""
        base = palette.get('base', QColor(80, 160, 70))
        try:
            return QColor(
                max(0, int(base.red() * 0.45)),
                max(0, int(base.green() * 0.5)),
                max(0, int(base.blue() * 0.45)),
            )
        except Exception:
            return base

    def _paint_infield_base_layers(self, painter: QPainter, w: int, h: int, muted_base: QColor) -> None:
        """Paint solid base and soft vertical gradient."""
        painter.fillRect(0, 0, w, h, muted_base)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(80, 150, 70, 70))
        grad.setColorAt(1.0, QColor(55, 120, 50, 70))
        painter.fillRect(0, 0, w, h, grad)

    def _paint_infield_texture_overlay(self, painter: QPainter, w: int, h: int, palette: Dict[str, Any]) -> None:
        """Overlay grass tile and tint/occlusion when texture exists."""
        try:
            tile_pix = self._grass_tile_pixmap
            if tile_pix is None or tile_pix.isNull():
                return
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            painter.drawTiledPixmap(0, 0, w, h, tile_pix)
            painter.restore()

            tint = palette.get('texture_tint')
            if tint is not None:
                painter.fillRect(0, 0, w, h, QColor(tint.red(), tint.green(), tint.blue(), 50))

            occ = float(palette.get('occlusion', 0.08))
            if occ <= 0:
                return
            try:
                occ_grad = QLinearGradient(w / 2, 0, w / 2, h)
                occ_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
                occ_grad.setColorAt(0.5, QColor(0, 0, 0, int(occ * 180)))
                occ_grad.setColorAt(1.0, QColor(0, 0, 0, int(occ * 240)))
                painter.fillRect(0, 0, w, h, occ_grad)
            except Exception:
                painter.fillRect(0, 0, w, h, QColor(0, 0, 0, int(occ * 255)))
        except Exception:
            pass

    def _paint_infield_noise(self, painter: QPainter, rnd: random.Random, w: int, h: int, muted_base: QColor, palette: Dict[str, Any]) -> None:
        """Paint translucent ellipse noise layer for turf variation."""
        base_count = int(max(40, (w * h) // 8000))
        count = int(base_count * max(0.6, palette.get('density_mult', 1.0)))
        for _ in range(count):
            cx = rnd.uniform(0, w)
            cy = rnd.uniform(0, h)
            rw = rnd.uniform(w * 0.02, w * 0.12)
            rh = rnd.uniform(h * 0.02, h * 0.12)
            shade = rnd.randint(-20, 20)
            col = QColor(
                max(30, min(255, muted_base.red() + shade)),
                max(30, min(255, muted_base.green() + shade)),
                max(30, min(255, muted_base.blue() + shade)),
                rnd.randint(18, 48),
            )
            painter.setBrush(QBrush(col))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(cx - rw / 2), int(cy - rh / 2), int(rw), int(rh))

    def _paint_infield_molehills(self, painter: QPainter, rnd: random.Random, w: int, h: int, muted_base: QColor, palette: Dict[str, Any]) -> None:
        """Paint darker speckle dots/molehills."""
        mole_col = palette.get('mole', QColor(40, 100, 30))
        mole_count = int(max(30, (w * h) // 20000) * palette.get('molehills_mult', 1.0))
        for _ in range(mole_count):
            cx = rnd.uniform(0, w)
            cy = rnd.uniform(0, h)
            r0 = rnd.uniform(1, max(2, min(w, h) * 0.02))
            col = mole_col if mole_col is not None else QColor(
                max(0, muted_base.red() - 40),
                max(0, muted_base.green() - 60),
                max(0, muted_base.blue() - 40),
                rnd.randint(80, 160),
            )
            painter.setBrush(QBrush(col))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(cx - r0), int(cy - r0), int(r0 * 2), int(r0 * 2))

    def _paint_infield_streaks(self, painter: QPainter, rnd: random.Random, w: int, h: int, palette: Dict[str, Any]) -> None:
        """Paint thin random dirt streaks."""
        streak_col = palette.get('streak', QColor(70, 50, 30, 100))
        painter.setPen(QPen(streak_col, 1))
        streak_count = int(max(20, (w * h) // 25000) * max(0.5, palette.get('density_mult', 1.0)))
        for _ in range(streak_count):
            x1 = rnd.uniform(0, w)
            y1 = rnd.uniform(0, h)
            x2 = x1 + rnd.uniform(-w * 0.06, w * 0.06)
            y2 = y1 + rnd.uniform(-h * 0.06, h * 0.06)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def _paint_infield_mowing_stripes(
        self,
        painter: QPainter,
        w: int,
        h: int,
        muted_base: QColor,
        highlight: QColor,
        palette: Dict[str, Any],
    ) -> None:
        """Paint diagonal mowing stripes for readability at race zoom."""
        try:
            stripe_w = max(8, int(min(w, h) * 0.08))
            stripe_alpha = 40 if palette.get('name') != 'dry' else 35
            stripe_col_light = QColor(
                min(255, highlight.red()),
                min(255, highlight.green()),
                min(255, highlight.blue()),
                stripe_alpha,
            )
            stripe_col_dark = QColor(
                max(0, muted_base.red() - 18),
                max(0, muted_base.green() - 18),
                max(0, muted_base.blue() - 18),
                stripe_alpha,
            )
            angle = -18 * math.pi / 180
            dx = math.cos(angle) * stripe_w * 0.6
            dy = math.sin(angle) * stripe_w * 0.6
            x0 = -w
            toggle = True
            while x0 < w * 2:
                col = stripe_col_light if toggle else stripe_col_dark
                painter.setBrush(QBrush(col))
                painter.setPen(Qt.PenStyle.NoPen)
                band = [
                    QPointF(x0, 0),
                    QPointF(x0 + dx * 200, dy * 200),
                    QPointF(x0 + dx * 200 + stripe_w * -math.sin(angle), dy * 200 + stripe_w * math.cos(angle)),
                    QPointF(x0 + stripe_w * -math.sin(angle), stripe_w * math.cos(angle)),
                ]
                path = QPainterPath()
                path.moveTo(band[0])
                for bp in band[1:]:
                    path.lineTo(bp)
                path.closeSubpath()
                painter.drawPath(path)
                toggle = not toggle
                x0 += stripe_w * 0.7
        except Exception:
            pass

    def _draw_joker(self, painter):
        """Draw an alternate 'joker' route if provided by the track data."""
        try:
            if not getattr(self, 'joker_points', None):
                return
            pts = self.joker_points
            if not pts:
                return
            painter.save()
            pen = QPen(QColor(255, 140, 0), 3, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            path = QPainterPath()
            path.moveTo(pts[0].x, pts[0].y)
            for pt in pts[1:]:
                path.lineTo(pt.x, pt.y)
            painter.drawPath(path)
            painter.restore()
        except Exception:
            pass

    def _draw_pit_lane(self, painter):
        """Draw professional pit lane with boxes, entry/exit zones."""
        try:
            points = self.pit_points if getattr(self, 'pit_points', None) else self.track_points
            if not points:
                return
            pit_inner_points, pit_outer_points = self._build_pit_lane_offsets(points)
            self._draw_pit_lane_polygon(painter, pit_inner_points, pit_outer_points)
            self._draw_pit_wall(painter, pit_inner_points)
            self._draw_pit_boxes(painter)
            self._draw_pit_entry_chevrons(painter)
            self._draw_pit_exit_marker(painter)

        except Exception:
            pass

    def _build_pit_lane_offsets(self, points: List[TrackPoint]) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        pit_inner_points: List[Tuple[float, float]] = []
        pit_outer_points: List[Tuple[float, float]] = []
        for pt in points:
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            pit_inner_points.append((pt.x + normal_x * 22, pt.y + normal_y * 22))
            pit_outer_points.append((pt.x + normal_x * 40, pt.y + normal_y * 40))
        return pit_inner_points, pit_outer_points

    def _draw_pit_lane_polygon(self, painter, pit_inner_points: List[Tuple[float, float]], pit_outer_points: List[Tuple[float, float]]) -> None:
        polygon = QPolygonF()
        for x, y in pit_inner_points:
            polygon.append(QPointF(x, y))
        for x, y in reversed(pit_outer_points):
            polygon.append(QPointF(x, y))
        painter.setBrush(QBrush(QColor(110, 110, 110)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(polygon)

    def _draw_pit_wall(self, painter, pit_inner_points: List[Tuple[float, float]]) -> None:
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        for i in range(len(pit_inner_points) - 1):
            painter.drawLine(
                int(pit_inner_points[i][0]),
                int(pit_inner_points[i][1]),
                int(pit_inner_points[i + 1][0]),
                int(pit_inner_points[i + 1][1]),
            )

    def _draw_pit_boxes(self, painter) -> None:
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for box_idx in range(10):
            box_s = 50 + box_idx * 20
            pt = self._find_track_point_near_s(box_s, tolerance=2)
            if pt is None:
                continue
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            painter.save()
            painter.translate(pt.x + normal_x * 31, pt.y + normal_y * 31)
            painter.rotate(math.degrees(pt.theta))
            painter.drawRect(-10, -8, 20, 16)
            painter.restore()

    def _draw_pit_entry_chevrons(self, painter) -> None:
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        for stripe_idx in range(8):
            stripe_s = 250 + stripe_idx * 2.5
            pt = self._find_track_point_near_s(stripe_s, tolerance=1)
            if pt is None:
                continue
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            painter.drawLine(
                int(pt.x + normal_x * 14),
                int(pt.y + normal_y * 14),
                int(pt.x + normal_x * 26),
                int(pt.y + normal_y * 26),
            )

    def _draw_pit_exit_marker(self, painter) -> None:
        if getattr(self, 'pit_points', None):
            return
        pt = self._find_track_point_near_s(285, tolerance=2)
        if pt is None:
            return
        normal_x = -math.sin(pt.theta)
        normal_y = math.cos(pt.theta)
        painter.save()
        painter.setBrush(QBrush(QColor(0, 255, 0)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(pt.x + normal_x * 31, pt.y + normal_y * 31), 3, 3)
        painter.restore()

    def _find_track_point_near_s(self, s_value: float, tolerance: float) -> Optional[TrackPoint]:
        if not self.track_points:
            return None
        for pt in self.track_points:
            if abs(pt.s - s_value) < tolerance:
                return pt
        return None

    def _draw_grandstands(self, painter):
        """Draw professional 3D grandstands facing the track."""
        try:
            if not self.track_points:
                return
            self._draw_main_straight_grandstands(painter)
            self._draw_corner_grandstands(painter)

        except Exception:
            pass

    def _draw_main_straight_grandstands(self, painter) -> None:
        for gs_s in [320, 380, 440]:
            pt = self._find_track_point_near_s(gs_s, tolerance=2)
            if pt is None:
                continue
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            self._draw_main_grandstand_block(painter, pt.x - normal_x * 40, pt.y - normal_y * 40, pt.theta)

    def _draw_main_grandstand_block(self, painter, gs_x: float, gs_y: float, theta: float) -> None:
        painter.save()
        painter.translate(gs_x, gs_y)
        painter.rotate(math.degrees(theta) + 90)

        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawRect(-20, 0, 40, 10)

        painter.setBrush(QBrush(QColor(60, 100, 180)))
        painter.setPen(QPen(QColor(50, 80, 150), 1))
        painter.drawRect(-19, -5, 38, 8)

        painter.setBrush(QBrush(QColor(80, 120, 200)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(-18, -10, 36, 8)

        painter.setBrush(QBrush(QColor(100, 140, 220)))
        painter.drawRect(-17, -15, 34, 6)

        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawRect(-22, -20, 44, 3)

        painter.setPen(QPen(QColor(90, 90, 90), 3))
        for pillar_x in [-18, -6, 6, 18]:
            painter.drawLine(pillar_x, -17, pillar_x, 10)

        painter.setPen(QPen(QColor(40, 70, 140), 1))
        for row_offset in [-13, -11, -9, -7, -3, -1, 1, 3]:
            painter.drawLine(-18, row_offset, 18, row_offset)

        painter.restore()

    def _draw_corner_grandstands(self, painter) -> None:
        for i, pt in enumerate(self.track_points):
            if abs(pt.curvature) <= 0.006 or i % 50 != 0:
                continue
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            if pt.curvature > 0:
                gs_x = pt.x - normal_x * 35
                gs_y = pt.y - normal_y * 35
            else:
                gs_x = pt.x + normal_x * 35
                gs_y = pt.y + normal_y * 35
            self._draw_corner_grandstand_block(painter, gs_x, gs_y, pt.theta)

    def _draw_corner_grandstand_block(self, painter, gs_x: float, gs_y: float, theta: float) -> None:
        painter.save()
        painter.translate(gs_x, gs_y)
        painter.rotate(math.degrees(theta) + 90)

        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(-12, 0, 24, 8)

        painter.setBrush(QBrush(QColor(70, 110, 190)))
        painter.drawRect(-11, -4, 22, 6)

        painter.setBrush(QBrush(QColor(90, 130, 210)))
        painter.drawRect(-10, -8, 20, 6)

        painter.setBrush(QBrush(QColor(190, 190, 190)))
        painter.drawRect(-13, -11, 26, 2)
        painter.restore()

    def _draw_garages(self, painter):
        """Draw continuous professional paddock garage building."""
        try:
            if not self.track_points:
                return
            self._draw_garage_base_segments(painter)
            self._draw_garage_bays(painter)

        except Exception:
            pass

    def _draw_garage_base_segments(self, painter) -> None:
        painter.setBrush(QBrush(QColor(140, 140, 140)))
        painter.setPen(QPen(QColor(120, 120, 120), 1))
        for i, pt in enumerate(self.track_points):
            if not (10 < pt.s < 280 and i % 3 == 0):
                continue
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            painter.save()
            painter.translate(pt.x + normal_x * 50, pt.y + normal_y * 50)
            painter.rotate(math.degrees(pt.theta))
            painter.drawRect(-6, 0, 12, 25)
            painter.restore()

    def _draw_garage_bays(self, painter) -> None:
        team_colors = [
            QColor(6, 0, 239),
            QColor(0, 210, 190),
            QColor(220, 0, 0),
            QColor(245, 150, 0),
            QColor(0, 144, 255),
            QColor(182, 186, 189),
            QColor(53, 140, 117),
            QColor(201, 45, 75),
            QColor(255, 220, 0),
            QColor(100, 100, 100),
        ]
        for bay_idx in range(10):
            pt = self._find_track_point_near_s(20 + bay_idx * 26, tolerance=2)
            if pt is None:
                continue
            self._draw_single_garage_bay(painter, pt, team_colors[bay_idx])

    def _draw_single_garage_bay(self, painter, pt: TrackPoint, team_color: QColor) -> None:
        normal_x = -math.sin(pt.theta)
        normal_y = math.cos(pt.theta)

        painter.save()
        painter.translate(pt.x + normal_x * 50, pt.y + normal_y * 50)
        painter.rotate(math.degrees(pt.theta))

        painter.setBrush(QBrush(QColor(180, 180, 180)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(-15, -2, 30, 29)

        painter.setBrush(QBrush(QColor(40, 40, 40)))
        for door in range(3):
            painter.drawRect(-11 + door * 7, 5, 6, 18)

        painter.setBrush(QBrush(team_color))
        painter.drawRect(-12, 1, 24, 3)
        painter.restore()

    def _draw_track(self, painter):
        """Draw track with professional surface, smooth kerbs, checkered start/finish."""
        try:
            centerline = self._build_centerline_path()
            if centerline is None:
                return

            track_width = 14
            self._draw_track_infield(painter, track_width)
            self._draw_track_surface_and_racing_line(painter, centerline, track_width)
            self._draw_track_edges(painter, track_width)
            self._draw_corner_kerbs(painter)
            self._draw_track_centerline_overlay(painter, centerline)
            self._draw_start_finish_line(painter, track_width)

        except Exception as e:
            print(f"ERROR in _draw_track: {e}")

        # Cached props are already drawn within the infield pixmap block
        # to ensure correct orientation and clipping. Avoid duplicate drawing here.

    def _build_centerline_path(self) -> Optional[QPainterPath]:
        """Return closed centerline path for the current track."""
        if not self.track_points or len(self.track_points) < 2:
            return None
        centerline = QPainterPath()
        centerline.moveTo(self.track_points[0].x, self.track_points[0].y)
        for pt in self.track_points[1:]:
            centerline.lineTo(pt.x, pt.y)
        centerline.lineTo(self.track_points[0].x, self.track_points[0].y)
        return centerline

    def _build_infield_points(self, track_width: int) -> Tuple[List[QPointF], List[QPointF], List[QPointF]]:
        """Build visible infield, inner infield and outer band point lists."""
        infield_points: List[QPointF] = []
        inner_infield_points: List[QPointF] = []
        outer_points: List[QPointF] = []

        inner_shrink = max(48, int(min(self.width(), self.height()) * 0.14))
        forest_margin = max(20, int(min(self.width(), self.height()) * 0.06))
        for pt in self.track_points:
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            infield_points.append(QPointF(pt.x - normal_x * (track_width - 2), pt.y - normal_y * (track_width - 2)))
            inner_infield_points.append(
                QPointF(
                    pt.x - normal_x * (track_width - 2 + inner_shrink),
                    pt.y - normal_y * (track_width - 2 + inner_shrink),
                )
            )
            outer_points.append(
                QPointF(
                    pt.x + normal_x * (track_width + forest_margin),
                    pt.y + normal_y * (track_width + forest_margin),
                )
            )
        return infield_points, inner_infield_points, outer_points

    def _build_infield_cache_key(self, w: int, h: int, seed: int) -> Tuple[Any, ...]:
        """Return infield cache key including palette and texture revision."""
        try:
            preset = select_preset(getattr(self, 'track_surface', ''), getattr(self, 'surface_grip', None), seed)
            palette_name = preset.get('name', '')
        except Exception:
            palette_name = ''
        tile_mtime = self._grass_tile_mtime
        return (w, h, seed, palette_name, tile_mtime)

    def _ensure_infield_assets(self, key: Tuple[Any, ...], bbox: Any, w: int, h: int, seed: int, inner_infield_points: List[QPointF]) -> None:
        """Populate cached infield pixmap and props for a cache key."""
        if self._infield_cache.get(key) is None:
            try:
                pix = self._generate_infield_pixmap(bbox, w, h, seed)
            except Exception:
                pix = QPixmap(max(1, w), max(1, h))
                pix.fill(QColor(100, 160, 100))
            self._infield_cache[key] = pix

        if self._infield_props_cache.get(key) is None:
            try:
                world_pts = [(pt.x(), pt.y()) for pt in inner_infield_points]
                props = place_props(world_pts, seed=seed, density=0.00035)
            except Exception:
                props = []
            self._infield_props_cache[key] = props

    def _draw_infield_props_clipped(
        self,
        painter,
        bbox: Any,
        h: int,
        inner_infield_points: List[QPointF],
        key: Tuple[Any, ...],
    ) -> None:
        """Draw cached infield props clipped to the inner infield polygon."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.translate(bbox.x(), bbox.y())
        painter.save()
        painter.scale(1, -1)
        painter.translate(0, -h)

        local_poly = QPolygonF()
        for p in inner_infield_points:
            local_poly.append(QPointF(p.x() - bbox.x(), p.y() - bbox.y()))
        clip_path = QPainterPath()
        clip_path.addPolygon(local_poly)
        painter.setClipPath(clip_path)

        props = self._infield_props_cache.get(key, [])
        if props:
            try:
                draw_props(painter, props, offset_x=bbox.x(), offset_y=bbox.y())
            except Exception:
                self._draw_fallback_props(painter, props, bbox)

        painter.restore()
        painter.restore()

    def _draw_fallback_props(self, painter, props: List[Dict[str, Any]], bbox: Any) -> None:
        """Fallback prop renderer if shared prop drawing fails."""
        for prop in props:
            x = prop.get('x', 0) - bbox.x()
            y = prop.get('y', 0) - bbox.y()
            s = prop.get('size', 8.0)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(34, 120, 34)))
            painter.drawEllipse(int(x - s / 2), int(y - s / 2), int(s), int(s))

    def _draw_outer_forest_band(self, painter, outer_poly: Optional[QPolygonF], inner_poly: QPolygonF, bbox: Any, w: int, h: int) -> None:
        """Draw outer vegetation band between outer and inner polygons."""
        if outer_poly is None:
            return

        band_path = QPainterPath()
        band_path.addPolygon(outer_poly)
        inner_path = QPainterPath()
        inner_path.addPolygon(inner_poly)
        band_path = band_path.subtracted(inner_path)

        painter.save()
        painter.setClipPath(band_path)
        try:
            tile_pix = self._grass_tile_pixmap
            if tile_pix is not None and not tile_pix.isNull():
                painter.drawTiledPixmap(
                    int(bbox.x()) - w,
                    int(bbox.y()) - h,
                    int(bbox.width()) + w * 2,
                    int(bbox.height()) + h * 2,
                    tile_pix,
                )
                painter.fillRect(
                    int(bbox.x()) - w,
                    int(bbox.y()) - h,
                    int(bbox.width()) + w * 2,
                    int(bbox.height()) + h * 2,
                    QColor(60, 120, 60, 40),
                )
            else:
                painter.fillPath(band_path, QBrush(QColor(70, 120, 70)))
        except Exception:
            painter.fillPath(band_path, QBrush(QColor(70, 120, 70)))
        painter.restore()

    def _draw_track_infield(self, painter, track_width: int) -> None:
        """Render infield props and outer vegetation band."""
        try:
            infield_points, inner_infield_points, outer_points = self._build_infield_points(track_width)
            if not infield_points:
                return

            inner_poly = QPolygonF(inner_infield_points)
            outer_poly = QPolygonF(outer_points) if outer_points else None
            bbox = inner_poly.boundingRect()
            w = max(2, int(math.ceil(bbox.width())))
            h = max(2, int(math.ceil(bbox.height())))
            seed = int(self.track_length) if getattr(self, 'track_length', None) is not None else 0
            key = self._build_infield_cache_key(w, h, seed)

            self._ensure_infield_assets(key, bbox, w, h, seed, inner_infield_points)
            self._draw_infield_props_clipped(painter, bbox, h, inner_infield_points, key)
            self._draw_outer_forest_band(painter, outer_poly, inner_poly, bbox, w, h)
        except Exception:
            pass

    def _resolve_track_surface_color(self) -> Tuple[int, int, int]:
        """Resolve track base color, adjusted by grip where available."""
        surface = getattr(self, 'track_surface', '') or ''
        base_colors = {
            'asphalt': (85, 85, 85),
            'tarmac': (85, 85, 85),
            'concrete': (100, 100, 100),
            'gravel': (120, 90, 50),
            'mixed': (80, 75, 70),
            'dirt': (110, 80, 45),
        }
        r, g, b = base_colors.get(surface.lower(), (85, 85, 85))
        grip_val = getattr(self, 'surface_grip', None)
        try:
            if grip_val is not None:
                gv = float(grip_val)
                if gv > 1.0:
                    gv = min(1.0, gv / 20.0)
                factor = 0.75 + 0.25 * gv
                r = int(max(0, min(255, r * factor)))
                g = int(max(0, min(255, g * factor)))
                b = int(max(0, min(255, b * factor)))
        except Exception:
            pass
        return r, g, b

    def _draw_track_surface_and_racing_line(self, painter, centerline: QPainterPath, track_width: int) -> None:
        """Draw surface base and darker racing line."""
        r, g, b = self._resolve_track_surface_color()
        painter.setPen(
            QPen(
                QColor(r, g, b),
                track_width * 2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawPath(centerline)

        painter.setPen(
            QPen(
                QColor(45, 45, 45),
                track_width * 1.2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawPath(centerline)

    def _draw_track_edges(self, painter, track_width: int) -> None:
        """Draw left and right white edge lines."""
        painter.setPen(QPen(QColor(240, 240, 240), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(0, len(self.track_points) - 1):
            pt = self.track_points[i]
            next_pt = self.track_points[i + 1]
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            next_normal_x = -math.sin(next_pt.theta)
            next_normal_y = math.cos(next_pt.theta)
            painter.drawLine(
                int(pt.x - normal_x * track_width),
                int(pt.y - normal_y * track_width),
                int(next_pt.x - next_normal_x * track_width),
                int(next_pt.y - next_normal_y * track_width),
            )
            painter.drawLine(
                int(pt.x + normal_x * track_width),
                int(pt.y + normal_y * track_width),
                int(next_pt.x + next_normal_x * track_width),
                int(next_pt.y + next_normal_y * track_width),
            )

    def _draw_single_corner_kerb(self, painter, corner_points: List[TrackPoint], kerb_offset: int) -> None:
        """Draw striped kerb for one detected corner segment."""
        first_curv = corner_points[0].curvature
        segment_length = 0.0
        stripe_toggle = True

        for j in range(len(corner_points) - 1):
            pt = corner_points[j]
            next_pt = corner_points[j + 1]
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            next_normal_x = -math.sin(next_pt.theta)
            next_normal_y = math.cos(next_pt.theta)

            dist = math.sqrt((next_pt.x - pt.x) ** 2 + (next_pt.y - pt.y) ** 2)
            segment_length += dist
            if segment_length > 5:
                stripe_toggle = not stripe_toggle
                segment_length = 0.0

            colour = QColor(221, 45, 74) if stripe_toggle else QColor(255, 255, 255)
            painter.setPen(QPen(colour, 4))

            if first_curv > 0:
                painter.drawLine(
                    int(pt.x - normal_x * kerb_offset),
                    int(pt.y - normal_y * kerb_offset),
                    int(next_pt.x - next_normal_x * kerb_offset),
                    int(next_pt.y - next_normal_y * kerb_offset),
                )
            else:
                painter.drawLine(
                    int(pt.x + normal_x * kerb_offset),
                    int(pt.y + normal_y * kerb_offset),
                    int(next_pt.x + next_normal_x * kerb_offset),
                    int(next_pt.y + next_normal_y * kerb_offset),
                )

    def _draw_corner_kerbs(self, painter) -> None:
        """Detect corner runs and draw inside apex kerbs."""
        current_corner: List[TrackPoint] = []
        kerb_offset = 12
        for pt in self.track_points:
            if abs(pt.curvature) > 0.003:
                current_corner.append(pt)
                continue
            if len(current_corner) > 5:
                self._draw_single_corner_kerb(painter, current_corner, kerb_offset)
            current_corner = []

        if len(current_corner) > 5:
            self._draw_single_corner_kerb(painter, current_corner, kerb_offset)

    def _draw_track_centerline_overlay(self, painter, centerline: QPainterPath) -> None:
        """Draw subtle dashed centerline overlay."""
        painter.setPen(QPen(QColor(200, 200, 200), 0.5, Qt.PenStyle.DashLine))
        painter.drawPath(centerline)

    def _draw_start_finish_line(self, painter, track_width: int) -> None:
        """Draw checkered start/finish marker near s=0."""
        for pt in self.track_points:
            if pt.s >= 5:
                continue
            painter.save()
            painter.translate(pt.x + 200, pt.y)
            painter.rotate(math.degrees(pt.theta) + 90)
            painter.setPen(Qt.PenStyle.NoPen)
            square_size = 3.5
            for col in range(8):
                painter.setBrush(QBrush(QColor(255, 255, 255) if col % 2 == 0 else QColor(0, 0, 0)))
                painter.drawRect(
                    int(col * square_size - track_width),
                    int(-square_size),
                    int(square_size),
                    int(square_size * 2),
                )
            painter.restore()
            break

    def _draw_cars(self, painter):
        """Draw cars at current positions."""
        try:
            if not self.track_points or self.track_length <= 0:
                return

            cars_drawn = 0
            for car in self.cars:
                try:
                    if car.dnf:
                        continue
                    if self._draw_single_car(painter, car):
                        cars_drawn += 1
                except Exception as e:
                    print(
                        f"ERROR drawing car {
                            car.driver_id} (s={
                            car.s:.1f}): {e}")

            # Debug: Print if not all cars are being drawn
            if cars_drawn < len([c for c in self.cars if not c.dnf]):
                active_cars = len([c for c in self.cars if not c.dnf])
                print(
                    f"WARNING: Only drew {cars_drawn}/{active_cars} active cars")
        except Exception as e:
            print(f"ERROR in _draw_cars: {e}")

    def _draw_single_car(self, painter, car: Car) -> bool:
        """Draw one active car and return whether it was rendered."""
        state = self._resolve_car_draw_state(car)
        if state is None:
            return False
        offset_x, offset_y, movement_angle, steering_angle = state

        painter.save()
        painter.translate(offset_x, offset_y)
        painter.rotate(math.degrees(movement_angle) + 90)
        livery = self._resolve_car_livery(car)
        VehicleRenderer.render_single_seater_car(painter, livery, scale=1.5, steering_angle=steering_angle)
        painter.restore()
        self._draw_player_halo_if_needed(painter, car, offset_x, offset_y)
        return True

    def _resolve_car_draw_state(self, car: Car) -> Optional[Tuple[float, float, float, float]]:
        """Resolve world-space draw coordinates and orientation for a car."""
        display_pos = getattr(car, 'display_s', None)
        normalized_s = (display_pos if display_pos is not None else car.s) % self.track_length
        pt = self._point_at_s(normalized_s)
        if pt is None:
            return None

        grid_position = car.driver_id % 2
        base_offset = (grid_position - 0.5) * 6
        lap_progress = normalized_s / self.track_length
        dynamic_offset = math.sin(lap_progress * 6 * math.pi + car.driver_id * 0.7) * 2
        total_lateral_offset = base_offset + dynamic_offset

        track_angle = pt.theta
        offset_x = pt.x + total_lateral_offset * math.cos(track_angle + math.pi / 2)
        offset_y = pt.y + total_lateral_offset * math.sin(track_angle + math.pi / 2)
        movement_angle = self._resolve_car_movement_angle(car, track_angle)
        steering_angle = dynamic_offset * 2.5
        return offset_x, offset_y, movement_angle, steering_angle

    def _resolve_car_movement_angle(self, car: Car, track_angle: float) -> float:
        """Use movement direction when available to orient rendered car."""
        if hasattr(car, 'movement_direction') and abs(car.movement_direction) > 0.1:
            return track_angle if car.movement_direction > 0 else track_angle + math.pi
        return track_angle

    def _resolve_car_livery(self, car: Car) -> Livery:
        """Return cached livery or build a simple fallback from driver color."""
        livery = self.appearance_manager.get_livery(car.driver_id)
        if livery:
            return livery
        primary = car.colour
        secondary = QColor(
            min(255, primary.red() + 30),
            min(255, primary.green() + 30),
            min(255, primary.blue() + 30),
        )
        return Livery(primary, secondary, QColor(255, 255, 255), f"Driver {car.driver_id}", car.driver_id)

    def _draw_player_halo_if_needed(self, painter, car: Car, offset_x: float, offset_y: float) -> None:
        """Highlight the player-controlled car with a halo ring."""
        try:
            if getattr(self, 'player_driver_id', None) is None:
                return
            if car.driver_id != getattr(self, 'player_driver_id', None):
                return
            painter.save()
            halo_pen = QPen(QColor(255, 215, 0, 200))
            halo_pen.setWidth(4)
            painter.setPen(halo_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(int(offset_x) - 14, int(offset_y) - 14, 28, 28)
            painter.restore()
        except Exception:
            pass


class RaceWindow(QMainWindow):
    """Main race window with track display and controls."""

    # Signals
    return_to_menu = pyqtSignal()  # Signal to return to main menu
    next_race = pyqtSignal(dict)  # Signal to start next race in championship with config

    def __init__(self, track_id: Optional[int] = None, discipline: Optional[str] = None, championship_id: Optional[int] = None, race_id: Optional[int] = None):
        try:
            super().__init__()
            self.setWindowTitle("Momentum - Race Visualisation")
            # Display mode (default: borderless)
            self.display_mode = "borderless"
            # Borderless windowed fullscreen (use setWindowFlag to toggle)
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            screen_obj = QApplication.primaryScreen()
            available = screen_obj.availableGeometry() if screen_obj else None
            if available is not None:
                # Ensure widget minimums don't force a larger geometry than the screen
                try:
                    self.setMinimumSize(0, 0)
                except Exception:
                    pass
                # Also clear minimums on child widgets to avoid min>max issues
                try:
                    for w in self.findChildren(QWidget):
                        try:
                            w.setMinimumSize(0, 0)
                        except Exception:
                            pass
                except Exception:
                    pass
                # Constrain maximum size to available screen area
                try:
                    self.setMaximumSize(available.width(), available.height())
                except Exception:
                    pass
                # Use available geometry (accounts for taskbar/docked panels)
                self.setGeometry(available)
            self.showMaximized()
            # Race state
            self.db: Optional[DatabaseManager] = None
            self.drivers = []
            self.track = None
            self._initial_track_id = track_id
            self._initial_discipline = discipline or "SINGLE_SEATER"
            self._championship_id = championship_id  # Championship this race belongs to
            self._race_id = race_id  # Current race ID in championship
            self.race_thread: Optional[threading.Thread] = None
            self.stop_event: Optional[threading.Event] = None
            # Track last lap time per driver
            self.driver_lap_times: Dict[int, float] = {}
            self.race_start_time: float = 0.0
            # Mapping of driver IDs to car colours
            self.driver_colours: Dict[int, QColor] = {}
            # Mapping of driver IDs to push intensity
            self._driver_push_intensity: Dict[int, float] = {}

            # Player control
            self.player_driver_id: Optional[int] = None
            self.player_team_id: Optional[int] = None
            self.player_team_driver_ids: List[int] = []
            self.player_overrides: Dict[str, float] = {
                'pace': 0.7, 'overtake': 0.5}  # pace: 0.5-1.0, overtake: 0.0-1.0
            self.tuning_preset: str = 'balanced'  # Simulation tuning preset

            # Player telemetry tracking
            self.player_telemetry = {
                'speed_kph': 0.0,
                'push_intensity': 0.7,
                'push_fatigue': 0.0,
                'tire_condition': 1.0
            }

            # Collision tracking
            self._collision_log: List[Dict[str, Any]] = []

            # Race state tracking for live standings
            self._race_state: Dict[int, Dict[str, Any]] = {}

            # Camera mode
            self.camera_mode = 'full'  # 'full' or 'follow'

            # Event emitter
            self.emitter = EventEmitter()
            self.emitter.position_update.connect(self._on_position_update)
            self.emitter.race_finished.connect(self._on_race_finished)
            self.emitter.event_signal.connect(self._on_event)

            # Vehicle appearance manager for rendering detailed cars
            self.appearance_manager = VehicleAppearanceManager()

            self._setup_ui()
            self._load_data()
            # No auto-start: user must click Start Race manually
            print("[INFO] GUI ready - click Start Race when ready")
        except Exception as e:
            print("[ERROR] Exception in RaceWindow.__init__:", e)
            _traceback.print_exc()
            raise

    # Auto-start logic removed: user must click Start Race manually

    def _setup_ui(self):
        """Setup user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Left: Track display (MUCH BIGGER)
        # Annotate type so static checkers know this will be a TrackWidget
        self.track_widget: Optional["TrackWidget"] = None  # Will be created after track loads
        left_container = QWidget()
        self.left_layout = QVBoxLayout(left_container)
        self.left_layout.addWidget(QLabel("Loading track..."))
        layout.addWidget(left_container, 1)  # Track gets all remaining space

        # Right: Controls and standings - fixed width to avoid layout churn
        right_container = QWidget()
        right_container.setFixedWidth(430)
        right_panel = QVBoxLayout(right_container)
        right_panel.setContentsMargins(10, 10, 10, 10)  # Compact margins
        layout.addWidget(right_container)

        # Title
        title = QLabel("<h1>Race Control</h1>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(title)

        # Controls
        controls = QHBoxLayout()
        self.start_btn = QPushButton("Start Race")
        self.start_btn.clicked.connect(self._start_race)
        self.start_btn.setMinimumHeight(50)
        controls.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Race")
        self.stop_btn.clicked.connect(self._stop_race)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(50)
        controls.addWidget(self.stop_btn)

        right_panel.addLayout(controls)

        # Race info
        self.info_label = QLabel("Ready to race")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self.info_label)

        # Player controls section
        from PyQt6.QtWidgets import QSlider, QGroupBox
        player_controls = QGroupBox("Your Controls")
        player_controls.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #B9F2FF;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        player_layout = QVBoxLayout(player_controls)

        # Pace control
        pace_label_top = QLabel("Race Pace: Balanced (50%)")
        pace_label_top.setStyleSheet(CONTROL_LABEL_STYLE)
        pace_label_top.setMinimumHeight(22)
        self.pace_value_label = pace_label_top
        player_layout.addWidget(pace_label_top)

        self.pace_slider = QSlider(Qt.Orientation.Horizontal)
        self.pace_slider.setMinimum(0)
        self.pace_slider.setMaximum(100)
        self.pace_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pace_slider.setTickInterval(10)
        self.pace_slider.valueChanged.connect(self._on_pace_changed)
        player_layout.addWidget(self.pace_slider)
        # Set value AFTER connecting signal to trigger initial styling
        self.pace_slider.setValue(50)

        pace_hint = QLabel("Conservative ← → Aggressive")
        pace_hint.setStyleSheet("font-size: 10px;")
        pace_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_layout.addWidget(pace_hint)

        player_layout.addSpacing(10)

        # Overtake aggressiveness
        overtake_label_top = QLabel("Overtaking: Moderate (50%)")
        overtake_label_top.setStyleSheet(CONTROL_LABEL_STYLE)
        overtake_label_top.setMinimumHeight(22)
        self.overtake_value_label = overtake_label_top
        player_layout.addWidget(overtake_label_top)

        self.overtake_slider = QSlider(Qt.Orientation.Horizontal)
        self.overtake_slider.setMinimum(0)
        self.overtake_slider.setMaximum(100)
        self.overtake_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.overtake_slider.setTickInterval(10)
        self.overtake_slider.valueChanged.connect(self._on_overtake_changed)
        player_layout.addWidget(self.overtake_slider)
        # Set value AFTER connecting signal to trigger initial styling
        self.overtake_slider.setValue(50)

        overtake_hint = QLabel("Cautious ← → Aggressive")
        overtake_hint.setStyleSheet("font-size: 10px;")
        overtake_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_layout.addWidget(overtake_hint)

        right_panel.addWidget(player_controls)

        # Player telemetry display
        telemetry_group = QGroupBox("Your Telemetry")
        telemetry_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #B9F2FF;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        telemetry_layout = QVBoxLayout(telemetry_group)

        # Speed display
        self.speed_label = QLabel("Speed: --- km/h")
        self.speed_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #FFFFFF;")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        telemetry_layout.addWidget(self.speed_label)

        # Push intensity gauge (horizontal bar)
        push_label = QLabel("Push Intensity")
        push_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        telemetry_layout.addWidget(push_label)

        from PyQt6.QtWidgets import QProgressBar
        self.push_gauge = QProgressBar()
        self.push_gauge.setMinimum(0)
        self.push_gauge.setMaximum(100)
        self.push_gauge.setValue(70)
        self.push_gauge.setTextVisible(True)
        self.push_gauge.setFormat("%p%")
        self.push_gauge.setStyleSheet("""
            QProgressBar {
                border: 3px solid #B9F2FF;
                border-radius: 8px;
                text-align: center;
                background-color: #353839;
                height: 35px;
                font-size: 16px;
                font-weight: bold;
                color: #F5F5F5;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4FC3F7, stop:0.3 #26C6DA, stop:0.6 #FFB74D, stop:0.8 #FF7043, stop:1.0 #E53935);
                border-radius: 5px;
            }
        """)
        telemetry_layout.addWidget(self.push_gauge)

        # Fatigue warning
        self.fatigue_label = QLabel("Fatigue: 0%")
        self.fatigue_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fatigue_label.setStyleSheet("font-size: 12px; color: #FFD700;")
        telemetry_layout.addWidget(self.fatigue_label)

        # Tire condition
        self.tire_label = QLabel("Tire: 100%")
        self.tire_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tire_label.setStyleSheet("font-size: 12px; color: #00BFFF;")
        telemetry_layout.addWidget(self.tire_label)
        # Player status (e.g., RETIRED) — visible but does not disable controls
        self.player_status_label = QLabel("")
        self.player_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_status_label.setStyleSheet(
            "font-size: 18px; color: #FF4444; font-weight: 900;")
        self.player_status_label.hide()
        telemetry_layout.addWidget(self.player_status_label)

        right_panel.addWidget(telemetry_group)

        # Camera controls
        camera_group = QGroupBox("Camera")
        camera_layout = QHBoxLayout(camera_group)
        self.camera_full_btn = QPushButton("Full Track")
        self.camera_full_btn.clicked.connect(
            lambda: self._set_camera_mode('full'))
        self.camera_follow_btn = QPushButton("Follow Car")
        self.camera_follow_btn.clicked.connect(
            lambda: self._set_camera_mode('follow'))
        camera_layout.addWidget(self.camera_full_btn)
        camera_layout.addWidget(self.camera_follow_btn)
        right_panel.addWidget(camera_group)

        # Menu/Exit controls
        menu_layout = QHBoxLayout()
        
        self.next_race_btn = QPushButton("Next Race")
        self.next_race_btn.clicked.connect(self._next_race)
        self.next_race_btn.setMinimumHeight(40)
        self.next_race_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a6b1a;
                color: #FFFFFF;
                border: 2px solid #00FF00;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2a8a2a;
                border: 2px solid #00FF00;
            }
            QPushButton:pressed {
                background-color: #0a4a0a;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #555555;
                border: 2px solid #555555;
            }
        """)
        self.next_race_btn.setEnabled(False)  # Only enabled in championship mode after race
        menu_layout.addWidget(self.next_race_btn)
        
        self.menu_btn = QPushButton("Return to Menu")
        self.menu_btn.clicked.connect(self._return_to_menu)
        self.menu_btn.setMinimumHeight(40)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
                border: 2px solid #FFED4E;
            }
            QPushButton:pressed {
                background-color: #0a0a0a;
            }
        """)
        menu_layout.addWidget(self.menu_btn)
        right_panel.addLayout(menu_layout)

        # Standings table (fixed widths to avoid reflow and scrolling)
        right_panel.addWidget(QLabel("<h2>Live Standings</h2>"))
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(4)
        self.standings_table.setHorizontalHeaderLabels(["", "Driver", "Lap", "Gap"])
        self.standings_table.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding
        )
        # Match right panel width (430) minus margins for stable layout
        self.standings_table.setFixedWidth(410)
        header = self.standings_table.horizontalHeader()
        if header is not None:
            self.standings_table.setColumnWidth(0, 32)   # color chip
            self.standings_table.setColumnWidth(1, 240)  # driver name width budget
            self.standings_table.setColumnWidth(2, 48)   # lap number
            self.standings_table.setColumnWidth(3, 88)   # gap like "+888:888"
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            header.setStretchLastSection(False)
        
        self.standings_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.standings_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.standings_table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        # Use fixed row height for performance (avoid resizeRowsToContents each frame)
        self._standings_row_height = 26
        standings_vheader = self.standings_table.verticalHeader()
        if isinstance(standings_vheader, QHeaderView):
            standings_vheader.setDefaultSectionSize(self._standings_row_height)
            standings_vheader.setVisible(False)
        self._last_standings_row_count = 0
        right_panel.addWidget(self.standings_table, 1)  # Stretch factor 1 - grows to fill space

        # Apply dark Momentum palette for race HUD and visuals (restoring
        # darker theme)
        self.setStyleSheet("""
            /* Window and global */
            QMainWindow { background-color: #353839; }
            QWidget { background-color: #353839; color: #B9F2FF; font-family: 'Inter', 'Segoe UI', sans-serif; }

            /* HUD / monospace */
            QLabel { color: #B9F2FF; }
            QLabel.hud { font-family: 'Roboto Mono', 'Courier New', monospace; color: #F5F5F5; }

            /* Buttons */
            QPushButton { border: none; border-radius: 6px; padding: 8px; font-weight: 700; }
            QPushButton.primary { background-color: #B9F2FF; color: #353839; }
            QPushButton.secondary { background-color: #DD2D4A; color: #ffffff; }
            QPushButton:disabled { background-color: #2E2E2E; color: #777777; }

            /* Progress bars */
            QProgressBar { border: 2px solid rgba(185,242,255,0.06); border-radius: 6px; background-color: #2E2E2E; color: #FFFFFF; }
            QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B9F2FF, stop:0.6 #B9F2FF, stop:1.0 #DD2D4A); }

            /* Standings table */
            QTableWidget { background-color: #252627; color: #B9F2FF; gridline-color: #353839; }
            QHeaderView::section { background-color: #353839; color: #B9F2FF; padding: 6px; border: none; }
            QTableWidget::item:selected { background-color: #FFB000; color: #000000; font-weight: 700; }

            /* Track widget */
            QWidget#TrackWidget { background-color: #1A1A1A; border: 1px solid rgba(185,242,255,0.04); }
        """)

    def _load_data(self):
        """Load drivers and track from database."""
        try:
            if not self._init_database():
                return
            if not self._load_and_prepare_drivers():
                return
            self._load_track_with_fallback()
            track_points, track_length = self._generate_circuit_geometry()
            if track_points is None or track_length is None:
                return
            if not self._create_and_mount_track_widget(track_points, track_length):
                return
            if not self._create_cars_and_start_grid():
                return
            self._init_standings_table_safe()
            self._set_load_data_ready_message()

        except Exception as e:
            self.info_label.setText(f"Unexpected error: {e}")
            self.start_btn.setEnabled(False)
            print(f"ERROR: Unexpected error in _load_data: {e}")
            _traceback.print_exc()

    def _init_database(self) -> bool:
        """Initialize database manager for race data loading."""
        try:
            from database.database_manager import DatabaseManager
            self.db = DatabaseManager()
            return True
        except Exception as e:
            self.info_label.setText(f"Database connection failed: {e}")
            self.start_btn.setEnabled(False)
            print(f"ERROR: Database initialisation failed: {e}")
            _traceback.print_exc()
            return False

    def _load_and_prepare_drivers(self) -> bool:
        """Load race drivers and initialize colours/liveries."""
        try:
            loaded_drivers = self._load_race_drivers()
            if not loaded_drivers:
                self.info_label.setText("Error: No drivers in database")
                self.start_btn.setEnabled(False)
                print("ERROR: No drivers found in database")
                return False

            self.drivers = loaded_drivers[:RACE_GRID_SIZE] if len(loaded_drivers) >= RACE_GRID_SIZE else loaded_drivers
            print(f"Loaded {len(self.drivers)} drivers")
            if self.drivers:
                print(f"First driver: id={self.drivers[0].id}, name={self.drivers[0].name}")
            self._log_placeholder_driver_warning()
            self._prepare_driver_colours()
            self._init_driver_liveries_safe()
            return True
        except Exception as e:
            self.info_label.setText(f"Failed to load drivers: {e}")
            self.start_btn.setEnabled(False)
            print(f"ERROR: Failed to load drivers: {e}")
            _traceback.print_exc()
            return False

    def _log_placeholder_driver_warning(self) -> None:
        """Log warning if placeholder names are present in active grid."""
        placeholder_count = sum(
            1 for d in self.drivers
            if re.match(r"^(Driver|Seed Driver)\\s+\\d+", str(getattr(d, 'name', '')).strip())
        )
        if placeholder_count <= 0:
            return
        print(
            f"[DATA WARNING] {placeholder_count}/{len(self.drivers)} active drivers use placeholder names. "
            "Run scripts/seed_career_mode.py for realistic Faker data."
        )

    def _prepare_driver_colours(self) -> None:
        """Create deterministic per-driver colour map for visuals."""
        palette = [
            QColor(255, 50, 50), QColor(50, 150, 255), QColor(50, 255, 50),
            QColor(255, 255, 50), QColor(255, 150, 50), QColor(200, 50, 255),
            QColor(50, 255, 255), QColor(255, 150, 150), QColor(150, 255, 150),
            QColor(200, 200, 255), QColor(180, 120, 60), QColor(120, 60, 180),
            QColor(60, 180, 120), QColor(255, 200, 100), QColor(100, 200, 255),
            QColor(200, 100, 255),
        ]
        if RACE_GRID_SIZE > len(palette):
            repeat = (RACE_GRID_SIZE // len(palette)) + 1
            palette = (palette * repeat)[:RACE_GRID_SIZE]
        self.driver_colours = {}
        for i, driver in enumerate(self.drivers):
            self.driver_colours[driver.id] = palette[i % len(palette)]

    def _init_driver_liveries_safe(self) -> None:
        """Initialize driver liveries; non-fatal on failure."""
        try:
            db = self.db
            if db is None:
                return
            teams_dict: Dict[int, Any] = {}
            for driver in self.drivers:
                if driver.current_team_id and driver.current_team_id not in teams_dict:
                    team = db.get_team(driver.current_team_id)
                    if team:
                        teams_dict[driver.current_team_id] = team

            for driver in self.drivers:
                primary = self.driver_colours.get(driver.id, QColor(200, 200, 200))
                secondary = QColor(
                    min(255, primary.red() + 30),
                    min(255, primary.green() + 30),
                    min(255, primary.blue() + 30),
                )
                livery = create_team_livery(driver.id, f"Driver {driver.id}", driver.id)
                livery.primary_color = primary
                livery.secondary_color = secondary
                livery.trim_color = QColor(255, 255, 255)
                self.appearance_manager.driver_liveries[driver.id] = livery
            print(f"[LIVERY] Initialized {len(self.appearance_manager.driver_liveries)} liveries for {len(self.drivers)} drivers")
        except Exception as e:
            print(f"ERROR: Livery initialisation failed: {e}")
            _traceback.print_exc()

    def _load_track_with_fallback(self) -> None:
        """Load track from database, falling back to a local simple track."""
        db = self.db
        if db is None:
            self.track = self._make_fallback_track()
            print(f"Loaded fallback track: {self.track.name} ({self.track.length_km:.2f}km)")
            return
        try:
            try:
                req_id = getattr(self, '_initial_track_id', None)
                self.track = db.get_simple_track(req_id)
            except Exception:
                self.track = db.get_simple_track()
            print(f"Loaded track: {self.track.name} ({self.track.length_km:.2f}km)")
        except Exception:
            self.track = self._make_fallback_track()
            print(f"Loaded fallback track: {self.track.name} ({self.track.length_km:.2f}km)")

    def _make_fallback_track(self) -> Any:
        """Construct fallback track model compatible with visual/sim code."""
        from dataclasses import dataclass

        @dataclass
        class SimpleTrack:
            name: str
            length_km: float
            turns: int = 12
            left_turns: int = 6
            right_turns: int = 6
            elevation_change_m: float = 15.0
            avg_corner_radius_m: float = 40.0
            min_corner_radius_m: float = 20.0
            max_corner_radius_m: float = 80.0
            tightest_corner_radius_m: float = 20.0
            longest_straight_m: float = 800.0
            shortest_straight_m: float = 150.0
            avg_speed_kmh: float = 180.0
            top_speed_kmh: float = 280.0
            surface: str = "asphalt"
            surface_type: str = "asphalt"
            surface_grip: float = 12.0
            surface_abrasiveness: float = 8.0
            climate: str = "temperate"
            drs_zones: int = 2

        return SimpleTrack(name="Test Circuit", length_km=4.5)

    def _build_legacy_circuit_instructions(self) -> List[Tuple[Any, ...]]:
        """Build legacy instruction pattern scaled by loaded track length."""
        track = self.track
        length_km = getattr(track, 'length_km', 4.5)
        return [
            ('S', int(600 * (length_km / 6.0))),
            ('C', 45, 170, 60, 0.00008),
            ('S', int(400 * (length_km / 6.0))),
            ('C', 65, 95, 50, 0.0001),
            ('S', int(220 * (length_km / 6.0))),
            ('C', -55, 100, 52, 0.0001),
            ('S', int(350 * (length_km / 6.0))),
            ('C', 155, 48, 42, 0.00014),
            ('S', int(550 * (length_km / 6.0))),
            ('C', -65, 145, 58, 0.00009),
            ('S', int(380 * (length_km / 6.0))),
            ('C', 55, 115, 54, 0.00009),
            ('S', int(180 * (length_km / 6.0))),
            ('C', 60, 90, 50, 0.0001),
            ('S', int(300 * (length_km / 6.0))),
            ('C', -50, 135, 56, 0.00009),
            ('S', int(160 * (length_km / 6.0))),
            ('C', 50, 135, 56, 0.00009),
            ('S', int(320 * (length_km / 6.0))),
        ]

    def _generate_circuit_geometry(self) -> Tuple[Optional[List[TrackPoint]], Optional[float]]:
        """Generate circuit geometry and return points with authoritative track length."""
        try:
            track = self.track
            track_km = getattr(track, 'length_km', 4.5)
            print(f"Generating circuit for {track_km}km track (closure solver enabled)...")
            wrapper = {'solve_closure': True, 'instructions': self._build_legacy_circuit_instructions()}
            routes = CircuitGenerator.generate_with_routes(wrapper, options={})
            track_points = routes.get('main')
            if not track_points:
                self.info_label.setText("Error: Failed to generate circuit")
                self.start_btn.setEnabled(False)
                print("ERROR: Circuit generation returned empty list")
                return None, None
            track_length = track_km * 1000
            print(f"Generated circuit with {len(track_points)} points, using database length: {track_length:.0f}m")
            self.track_points = track_points
            return track_points, track_length
        except Exception as e:
            self.info_label.setText(f"Circuit generation failed: {e}")
            self.start_btn.setEnabled(False)
            print(f"ERROR: Circuit generation failed: {e}")
            _traceback.print_exc()
            return None, None

    def _create_and_mount_track_widget(self, track_points: List[TrackPoint], track_length: float) -> bool:
        """Create TrackWidget and replace loading placeholder in left panel."""
        try:
            self.track_widget = TrackWidget(
                track_points,
                track_length,
                self.appearance_manager,
                track_surface=getattr(self.track, 'surface', 'asphalt'),
                surface_grip=getattr(self.track, 'surface_grip', None),
            )
            while self.left_layout.count():
                item = self.left_layout.takeAt(0)
                if item is None:
                    continue
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.left_layout.addWidget(self.track_widget)
            print("Track widget created and added to layout")
            return True
        except Exception as e:
            self.info_label.setText(f"Failed to create track display: {e}")
            self.start_btn.setEnabled(False)
            print(f"ERROR: Track widget creation failed: {e}")
            _traceback.print_exc()
            return False

    def _build_starting_cars(self, ascending: bool = False) -> Tuple[List[Car], Dict[int, Any]]:
        """Create grid cars and map from grid position to driver id."""
        cars: List[Car] = []
        gridpos_map: Dict[int, Any] = {}
        total_drivers = len(self.drivers)
        grid_spacing = 15.0
        for i, driver in enumerate(self.drivers):
            grid_number = (i + 1) if ascending else (total_drivers - i)
            row = (grid_number - 1) // 2
            start_position = row * grid_spacing
            car_colour = self.driver_colours.get(driver.id, QColor(200, 200, 200))
            cars.append(Car(
                driver_id=driver.id,
                driver_name=driver.name,
                s=start_position,
                colour=car_colour,
                total_time=0.0,
                avg_lap_time=60.0,
                last_lap=0,
            ))
            try:
                gridpos_map[int(grid_number)] = int(driver.id)
            except Exception:
                gridpos_map[int(grid_number)] = getattr(driver, 'id', None)
        return cars, gridpos_map

    def _record_starting_grid_from_map(self, gridpos_map: Dict[int, Any], total_drivers: int) -> None:
        """Build canonical starting grid list where index 0 corresponds to P1."""
        try:
            self._starting_grid = [gridpos_map.get(pos) for pos in range(1, total_drivers + 1)]
            print(f"Starting grid recorded (pos1..posN): {self._starting_grid}")
        except Exception:
            try:
                self._starting_grid = [getattr(d, 'id', None) for d in self.drivers]
            except Exception:
                self._starting_grid = []

    def _maybe_fix_reversed_grid_order(self) -> None:
        """Flip grid assignment if canonical grid is reverse of driver ordering."""
        try:
            ordered_ids = [getattr(d, 'id', None) for d in self.drivers]
            if self._starting_grid != ordered_ids[::-1]:
                return
            total_drivers = len(self.drivers)
            cars, gridpos_map = self._build_starting_cars(ascending=True)
            tw = self.track_widget
            if tw is None:
                return
            try:
                tw.set_cars(cars)
            except Exception:
                pass
            try:
                self._starting_grid = [gridpos_map.get(pos) for pos in range(1, total_drivers + 1)]
            except Exception:
                self._starting_grid = ordered_ids
            print("Detected reversed grid order; flipped to ascending start positions")
            self._recompute_grid_from_track_widget_positions()
        except Exception:
            pass

    def _recompute_grid_from_track_widget_positions(self) -> None:
        """Derive starting grid from visual car placement to keep UI/engine aligned."""
        try:
            tw_cars = getattr(self.track_widget, 'cars', None)
            if not tw_cars:
                return
            sorted_by_s = sorted(tw_cars, key=lambda c: getattr(c, 's', 0.0), reverse=True)
            self._starting_grid = [getattr(c, 'driver_id', None) for c in sorted_by_s]
            print(f"Computed starting grid from car positions (P1..PN): {self._starting_grid}")
        except Exception:
            pass

    def _create_cars_and_start_grid(self) -> bool:
        """Create race cars and initialize canonical starting grid."""
        try:
            tw = self.track_widget
            if tw is None:
                self.info_label.setText("Failed to create cars: Track widget unavailable")
                self.start_btn.setEnabled(False)
                print("ERROR: Car creation failed: Track widget unavailable")
                return False
            total_drivers = len(self.drivers)
            cars, gridpos_map = self._build_starting_cars(ascending=False)
            tw.set_cars(cars)
            print(f"Created {len(cars)} cars at start line")
            print(f"Car details: {[(c.driver_name, c.driver_id) for c in cars]}")
            self._record_starting_grid_from_map(gridpos_map, total_drivers)
            self._maybe_fix_reversed_grid_order()
            return True
        except Exception as e:
            self.info_label.setText(f"Failed to create cars: {e}")
            self.start_btn.setEnabled(False)
            print(f"ERROR: Car creation failed: {e}")
            _traceback.print_exc()
            return False

    def _init_standings_row(self, row: int, driver_name: str, driver_id: Any, extra: str = "") -> None:
        """Initialize one standings row with default lap/gap values."""
        print(f"[STANDINGS INIT] Row {row}: Setting driver name to '{driver_name}'{extra}")
        self._set_standings_item(row, 0, QTableWidgetItem(""), driver_id)
        self._set_standings_item(row, 1, QTableWidgetItem(driver_name), driver_id)
        self._set_standings_item(row, 2, QTableWidgetItem("1"), driver_id)
        self._set_standings_item(row, 3, QTableWidgetItem("-"), driver_id)

    def _init_standings_table_safe(self) -> None:
        """Initialize standings table rows; non-fatal on failure."""
        try:
            self.standings_table.setRowCount(len(self.drivers))
            if hasattr(self, '_starting_grid') and self._starting_grid:
                for i, did in enumerate(self._starting_grid):
                    driver = next((d for d in self.drivers if getattr(d, 'id', None) == did), None)
                    driver_name = driver.name if driver is not None else f"Driver {did}"
                    driver_id = getattr(driver, 'id', None) if driver else did
                    self._init_standings_row(i, driver_name, driver_id, f" (start pos {i + 1})")
                print("Standings table initialized from starting grid")
                return

            for i, driver in enumerate(self.drivers):
                self._init_standings_row(i, driver.name, getattr(driver, 'id', None))
            print("Standings table initialized")
        except Exception as e:
            print(f"WARNING: Standings table initialisation failed: {e}")

    def _set_load_data_ready_message(self) -> None:
        """Set final ready message after successful data load."""
        track = self.track
        track_name = getattr(track, 'name', 'Unknown Track')
        track_km = float(getattr(track, 'length_km', 0.0))
        self.info_label.setText(f"{len(self.drivers)} drivers | {track_name} ({track_km:.2f}km)")
        print("Data loading complete - ready to race")

    # _auto_start_race method removed: user must click Start Race manually

    def _load_race_drivers(self):
        """Load race entrants with championship discipline/team constraints."""
        if self.db is None:
            return []

        # Use existing contracted drivers only; do not mutate contracts here.
        contracted = self._get_contracted_discipline_drivers(self._initial_discipline, RACE_GRID_SIZE)
        if contracted:
            return contracted

        # Last-resort fallback if discipline data is unavailable.
        all_drivers = self.db.get_all_drivers()
        return all_drivers[:RACE_GRID_SIZE] if len(all_drivers) >= RACE_GRID_SIZE else all_drivers

    def _get_contracted_discipline_drivers(self, discipline: str, limit: int):
        """Return contracted drivers for teams in selected discipline."""
        if self.db is None:
            return []

        norm = (discipline or "").lower().replace(" ", "_")
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT d.id
                FROM drivers d
                JOIN teams t ON t.id = d.current_team_id
                WHERE LOWER(REPLACE(t.discipline, ' ', '_')) = ?
                ORDER BY d.speed DESC, d.id ASC
                LIMIT ?
                """,
                (norm, int(limit))
            ).fetchall()

        out = []
        for row in rows:
            drv = self.db.get_driver(int(row[0]))
            if drv:
                out.append(drv)
        return out

    def _ensure_contracted_grid_for_discipline(self, discipline: str, target_grid_size: int):
        """Assign available drivers to discipline teams so race grid is playable."""
        if self.db is None:
            return

        norm = (discipline or "").lower().replace(" ", "_")
        with self.db.get_connection() as conn:
            team_rows = conn.execute(
                """
                SELECT id
                FROM teams
                WHERE LOWER(REPLACE(discipline, ' ', '_')) = ?
                ORDER BY operations_rating DESC, id ASC
                """,
                (norm,)
            ).fetchall()
            team_ids = [int(r[0]) for r in team_rows]
            if not team_ids:
                return

            assigned_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM drivers d
                JOIN teams t ON t.id = d.current_team_id
                WHERE LOWER(REPLACE(t.discipline, ' ', '_')) = ?
                """,
                (norm,)
            ).fetchone()[0]

            needed = max(0, int(target_grid_size) - int(assigned_count))
            if needed == 0:
                return

            preferred_pool = conn.execute(
                """
                SELECT id
                FROM drivers
                WHERE current_team_id IS NULL
                  AND LOWER(REPLACE(preferred_discipline, ' ', '_')) = ?
                ORDER BY speed DESC, id ASC
                LIMIT ?
                """,
                (norm, needed)
            ).fetchall()
            selected_ids = [int(r[0]) for r in preferred_pool]

            if len(selected_ids) < needed:
                remaining = needed - len(selected_ids)
                fallback_pool = conn.execute(
                    """
                    SELECT id
                    FROM drivers
                    WHERE current_team_id IS NULL
                    ORDER BY speed DESC, id ASC
                    LIMIT ?
                    """,
                    (remaining,)
                ).fetchall()
                selected_ids.extend(int(r[0]) for r in fallback_pool)

            if not selected_ids:
                return

            for idx, driver_id in enumerate(selected_ids):
                team_id = team_ids[idx % len(team_ids)]
                conn.execute(
                    """
                    UPDATE drivers
                    SET current_team_id = ?,
                        contract_length = COALESCE(contract_length, 2),
                        salary = COALESCE(salary, 800000)
                    WHERE id = ?
                    """,
                    (team_id, driver_id)
                )
            conn.commit()

            print(
                f"[GRID FIX] Assigned {len(selected_ids)} drivers to {discipline} teams "
                f"to reach a playable grid"
            )

    def _start_race(self):
        """Start the race simulation."""
        self._start_race_impl()

    def _start_race_impl(self):
        """Race-start implementation split from entrypoint to keep orchestration clear."""
        if not self.drivers or not self.track:
            self.info_label.setText("Error: No drivers or track loaded")
            print("ERROR: Cannot start race - no drivers or track")
            return

        if not self.track_widget:
            self.info_label.setText("Error: Track display not ready")
            print("ERROR: Cannot start race - track widget not initialized")
            return

        print(
            f"Starting race with {len(self.drivers)} drivers on {self.track.name}")

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.info_label.setText("Race starting... waiting for data")
        # Clear any player RETIRED status from a previous run
        try:
            if hasattr(self, 'player_status_label'):
                self.player_status_label.hide()
        except Exception:
            pass

        # Ensure player controls are enabled at race start (in case they were
        # disabled by a prior DNF)
        try:
            if hasattr(self, 'pace_slider'):
                self.pace_slider.setEnabled(True)
            if hasattr(self, 'overtake_slider'):
                self.overtake_slider.setEnabled(True)
            if hasattr(self, 'camera_full_btn'):
                self.camera_full_btn.setEnabled(True)
            if hasattr(self, 'camera_follow_btn'):
                self.camera_follow_btn.setEnabled(True)
            if hasattr(self, 'push_gauge'):
                self.push_gauge.setEnabled(True)
        except Exception:
            pass

        # === CRITICAL FIX: Don't start animation yet! ===
        # Starting animation before first data arrives causes freeze
        # Animation will auto-start when first position update arrives
        if not hasattr(self, '_animation_started'):
            self._animation_started = False
        print("[RACE START] Waiting for simulation to send first position data...")

        self._launch_race_thread()

    def _launch_race_thread(self) -> None:
        """Launch simulation thread and attach event callback bridge."""

        self.race_thread = threading.Thread(target=self._race_runner, daemon=True)
        self.race_thread.start()
        print("Race thread launched")

    def _race_runner(self) -> None:
        """Worker-thread entrypoint for race simulation."""
        try:
            self.stop_event = threading.Event()
            print("Race thread started")
            self._run_simulation_with_callback()
        except Exception as e:
            error_msg = f"Race error: {e}"
            print(f"ERROR in race_runner: {e}")
            _traceback.print_exc()
            try:
                self.emitter.event_signal.emit(error_msg)
            except Exception:
                pass

    def _run_simulation_with_callback(self) -> None:
        """Build context and execute simulation using thread event bridge."""
        print("Starting simulate_race with comprehensive engine via RaceContext...")
        track_pts = getattr(self, 'track_points', None)
        teams = self._build_race_teams_map()
        context = self._build_race_context(self._event_callback_from_race_thread, track_pts, teams)
        results = simulate_race(context=context, verbose=True, db=cast(Any, self.db))
        print(f"Race simulation complete, {len(results) if results else 0} results")

    def _build_race_teams_map(self) -> Dict[int, Any]:
        """Resolve team objects for current race entrants."""
        teams: Dict[int, Any] = {}
        try:
            db_any = cast(Any, self.db)
            get_team_fn = getattr(db_any, 'get_team', None)
            if not callable(get_team_fn):
                return teams
            team_ids = {d.current_team_id for d in self.drivers if d.current_team_id}
            for team_id in team_ids:
                team = get_team_fn(team_id)
                if team:
                    teams[team_id] = team
        except Exception:
            return {}
        return teams

    def _build_race_context(self, event_callback: Any, track_pts: Any, teams: Dict[int, Any]) -> RaceContext:
        """Construct race context and populate adapter-specific conditions."""
        context = RaceContext(
            discipline=RacingDiscipline[self._initial_discipline],
            track=self.track,
            drivers=self.drivers,
            teams=teams,
            total_laps=3,
            event_callback=event_callback,
        )
        tc = context.track_conditions
        tc['player_driver_id'] = self.player_driver_id
        tc['player_team_driver_ids'] = list(self.player_team_driver_ids)
        tc['player_overrides'] = self.player_overrides
        tc['track_points'] = track_pts
        tc['realtime_speed'] = 5.0
        tc['stop_event'] = self.stop_event
        tc['tuning_preset'] = self.tuning_preset
        return context

    def _event_callback_from_race_thread(self, event: dict) -> None:
        """Bridge simulation events to GUI-thread-safe signals."""
        try:
            event_type = event.get("type")
            if event_type == "position_update":
                self._handle_thread_position_update_event(event)
                return
            if event_type == "dnf":
                self._handle_thread_dnf_event(event)
                return
            if event_type == "race_finished":
                self._handle_thread_race_finished_event(event)
                return
        except Exception as e:
            print(f"ERROR in event_callback: {e}")
            _traceback.print_exc()

    def _handle_thread_position_update_event(self, event: dict) -> None:
        """Process realtime position payload in worker thread."""
        self._maybe_start_animation_from_thread()
        frame = int(event.get("frame", 0))
        race_time = float(event.get("time", 0.0))
        positions = event.get("positions", [])
        self._log_position_frame_snapshot(frame, race_time, positions)
        for pos_data in positions:
            self._process_single_thread_position_update(pos_data, frame, race_time)

    def _maybe_start_animation_from_thread(self) -> None:
        """Request animation start once, when first position packet arrives."""
        if self._animation_started:
            return
        print("[ANIMATION] First position data received - requesting animation start on main thread")
        try:
            self.emitter.event_signal.emit("start_animation")
            self.emitter.event_signal.emit("Race in progress...")
        except Exception as e:
            print(f"[ERROR] Failed to request animation start: {e}")
        self._animation_started = True

    def _log_position_frame_snapshot(self, frame: int, race_time: float, positions: Any) -> None:
        """Log top-3 snapshot once per second for runtime visibility."""
        if frame % 30 != 0 or not positions:
            return
        print(f"[{race_time:.1f}s] ", end="")
        for p in positions[:3]:
            print(
                f"P{p['position']}: {p['driver_name']} (L{p['lap']}, {p['racing_mode']}) ",
                end="",
            )
        print()

    def _process_single_thread_position_update(self, pos_data: Any, frame: int, race_time: float) -> None:
        """Apply one driver's realtime update and emit table/telemetry signals."""
        if not isinstance(pos_data, dict):
            return
        driver_id = pos_data.get("driver_id")
        if driver_id is None:
            return
        try:
            self._emit_player_telemetry_if_needed(driver_id, pos_data)
            self._update_track_widget_realtime(driver_id, pos_data, race_time)
            self._emit_standings_update_if_due(driver_id, pos_data, frame, race_time)
        except Exception as e:
            print(f"ERROR updating position for driver {driver_id}: {e}")

    def _emit_player_telemetry_if_needed(self, driver_id: int, pos_data: Dict[str, Any]) -> None:
        """Store player telemetry and emit formatted telemetry update signal."""
        if driver_id != self.player_driver_id:
            return
        velocity_mps = float(pos_data.get("velocity_mps", 0.0))
        push_intensity = float(pos_data.get("push_intensity", 0.7))
        push_fatigue = float(pos_data.get("push_fatigue", 0.0))
        tire_condition = float(pos_data.get("tire_condition", 1.0))
        self.player_telemetry['speed_kph'] = velocity_mps * 3.6
        self.player_telemetry['push_intensity'] = push_intensity
        self.player_telemetry['push_fatigue'] = push_fatigue
        self.player_telemetry['tire_condition'] = tire_condition
        self.emitter.event_signal.emit(
            f"telemetry_update|{velocity_mps * 3.6:.1f}|{push_intensity:.2f}|{push_fatigue:.2f}|{tire_condition:.2f}"
        )

    def _update_track_widget_realtime(self, driver_id: int, pos_data: Dict[str, Any], race_time: float) -> None:
        """Update track widget position for a running car."""
        if not self.track_widget or not pos_data.get("running", True):
            return
        position_m = float(pos_data.get("position_m", 0.0))
        lap = int(pos_data.get("lap", 0))
        velocity_mps = float(pos_data.get("velocity_mps", 0.0))
        if hasattr(self.track_widget, 'update_car_realtime'):
            self.track_widget.update_car_realtime(
                driver_id=driver_id,
                position_m=position_m,
                lap=lap,
                velocity_mps=velocity_mps,
            )
            return
        self.track_widget.update_car_position(
            driver_id=driver_id,
            lap=lap,
            position=pos_data.get("position", 1),
            total_time=race_time,
        )

    def _emit_standings_update_if_due(self, driver_id: int, pos_data: Dict[str, Any], frame: int, race_time: float) -> None:
        """Emit live standings payload at 1Hz to reduce GUI churn."""
        if frame % 30 != 0:
            return
        position = int(pos_data.get("position", 0))
        lap = int(pos_data.get("lap", 0))
        push_intensity = float(pos_data.get("push_intensity", 0.7))
        gap_ahead = float(pos_data.get("gap_ahead", 0.0))
        position_m = float(pos_data.get("position_m", 0.0))
        self.emitter.event_signal.emit(
            f"standings_update|{driver_id}|{position}|{lap}|{push_intensity:.2f}|{gap_ahead:.2f}|{position_m:.2f}|{race_time:.2f}"
        )

    def _handle_thread_dnf_event(self, event: dict) -> None:
        """Handle DNF updates from simulation worker thread."""
        driver_id = event.get("driver_id")
        driver_name = event.get("driver_name", f"Driver {driver_id}")
        reason = event.get("reason", "unknown")
        laps_completed = int(event.get("lap", 0))
        lap = max(1, laps_completed + 1)
        print(f"[DNF] {driver_name} DNF on lap {lap}: {reason}")
        self._emit_mark_dnf_signal(driver_id)
        self._emit_player_dnf_if_controlled(driver_id, lap, reason)
        self._update_race_state_dnf_snapshot(driver_id, driver_name, lap, event)

    def _emit_mark_dnf_signal(self, driver_id: Any) -> None:
        """Signal GUI thread to mark DNF on track/standings."""
        try:
            if driver_id is not None:
                self.emitter.event_signal.emit(f"mark_dnf|{driver_id}")
        except Exception:
            pass

    def _emit_player_dnf_if_controlled(self, driver_id: Any, lap: int, reason: str) -> None:
        """Emit player_dnf event for selected driver or teammate control group."""
        try:
            controlled_ids = set(getattr(self, 'player_team_driver_ids', []) or [])
            player_id = getattr(self, 'player_driver_id', None)
            if player_id is not None:
                controlled_ids.add(player_id)
            if driver_id in controlled_ids:
                self.emitter.event_signal.emit(f"player_dnf|{driver_id}|{lap}|{reason}")
        except Exception:
            pass

    def _update_race_state_dnf_snapshot(self, driver_id: Any, driver_name: str, lap: int, event: dict) -> None:
        """Keep race-state DNF flag in sync for subsequent table rebuilds."""
        if driver_id is None:
            return
        existing = self._race_state.get(driver_id, {
            'name': driver_name,
            'position': event.get('position', 0),
            'lap': lap,
            'time': event.get('race_time', 0.0),
            'distance': 0.0,
            'gap_ahead': 0.0,
        })
        existing['dnf'] = True
        existing['lap'] = lap
        self._race_state[driver_id] = existing

    def _handle_thread_race_finished_event(self, event: dict) -> None:
        """Store completion diagnostics and emit race-finished payload."""
        total_laps = int(event.get("total_laps", 0))
        race_time = float(event.get("race_time", 0.0))
        print(f"\nRace finished! {total_laps} laps in {race_time:.1f}s")
        collision_log = event.get('collision_log', [])
        self._collision_log = collision_log
        result_count = len(event.get('results', []))
        if collision_log:
            print(f"Race simulation complete, {result_count} results, {len(collision_log)} collisions")
        else:
            print(f"Race simulation complete, {result_count} results")
        self._emit_race_finished_results(event)

    def _emit_race_finished_results(self, event: dict) -> None:
        """Emit race_finished signal with robust fallback behavior."""
        try:
            results_payload = event.get('results', []) if isinstance(event, dict) else []
            try:
                self.emitter.race_finished.emit(results_payload)
            except Exception as ex:
                print(f"ERROR: failed to emit race_finished: {ex}")
                try:
                    _traceback.print_exc()
                except Exception:
                    pass
                try:
                    self.emitter.race_finished.emit([])
                except Exception:
                    pass
        except Exception as e:
            print(f"ERROR preparing results payload for emit: {e}")
            try:
                _traceback.print_exc()
            except Exception:
                pass

    def _stop_race(self):
        """Stop the race simulation."""
        print("[STOP RACE] User requested race stop")

        # Signal the race thread to stop
        if self.stop_event:
            self.stop_event.set()
            print("[STOP RACE] Stop event set")

        # Stop animation
        if self.track_widget:
            self.track_widget.stop_animation()
            print("[STOP RACE] Animation stopped")

        # Wait for race thread to finish (with timeout)
        if self.race_thread and self.race_thread.is_alive():
            print("[STOP RACE] Waiting for race thread to terminate...")
            self.race_thread.join(timeout=2.0)
            if self.race_thread.is_alive():
                print("[STOP RACE] WARNING: Race thread did not stop cleanly")
            else:
                print("[STOP RACE] Race thread terminated")

        # Re-enable start button
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.info_label.setText("Race stopped")
        print("[STOP RACE] Stop complete")

    def _next_race(self):
        """Proceed to next race in championship."""
        print("[NEXT RACE] User requested next race in championship")
        
        if not self._championship_id:
            print("[NEXT RACE] Not in championship mode, ignoring")
            return
        
        # Stop race if running
        if self.stop_event and not self.stop_event.is_set():
            print("[NEXT RACE] Stopping active race...")
            self._stop_race()
        
        # Emit signal with championship and race info
        config = {
            'championship_id': self._championship_id,
            'race_id': self._race_id,
            'mode': getattr(self, '_game_mode', 'championship'),
        }
        self.next_race.emit(config)
        print(f"[NEXT RACE] Emitted next_race signal with config: {config}")

    def _return_to_menu(self):
        """Return to main menu."""
        print("[MENU] User requested return to menu")
        
        # Stop race if running
        if self.stop_event and not self.stop_event.is_set():
            print("[MENU] Stopping active race...")
            self._stop_race()
        
        # Emit signal to return to menu
        self.return_to_menu.emit()
        print("[MENU] Emitted return_to_menu signal")

    def _on_position_update(self, data: dict):
        """Handle position update from simulation."""
        try:
            if not self.track_widget:
                return
            self._apply_track_widget_position_update(data)
            self._apply_standings_position_update(data)
        except Exception as e:
            print(f"ERROR in _on_position_update: {e}")

    def _apply_track_widget_position_update(self, data: dict) -> None:
        """Apply one position update to track widget."""
        tw = self.track_widget
        if tw is None:
            return
        tw.update_car_position(
            data['driver_id'],
            data['lap'],
            data['position'],
            data['total_time'],
        )

    def _find_standings_row_for_driver(self, driver_id: int) -> Optional[int]:
        """Find standings row index that corresponds to driver id."""
        for row in range(self.standings_table.rowCount()):
            name_item = self.standings_table.item(row, 1)
            if not name_item:
                continue
            driver_name = name_item.text()
            driver = next((d for d in self.drivers if d.name == driver_name), None)
            if driver and driver.id == driver_id:
                return row
        return None

    def _apply_dnf_row_state(self, row: int, driver_id: int) -> None:
        """Set standings cells for a retired driver."""
        try:
            self._set_standings_item(row, 0, QTableWidgetItem("-"), driver_id)
            self._set_standings_item(row, 2, QTableWidgetItem("-"), driver_id)
            self._set_standings_item(row, 3, QTableWidgetItem("DNF"), driver_id)
        except Exception:
            pass

    def _style_standings_name_cell(self, row: int, driver_id: int) -> None:
        """Apply player/highlight styling for standings name cell."""
        name_cell = self.standings_table.item(row, 1)
        if name_cell is None:
            return
        if driver_id == self.player_driver_id:
            name_cell.setBackground(QColor(255, 215, 0))
            name_cell.setForeground(QColor(0, 0, 0))
            return
        name_cell.setBackground(QColor(37, 38, 39))

    def _apply_standings_position_update(self, data: dict) -> None:
        """Update standings row for a single realtime position update."""
        driver_id = data['driver_id']
        row = self._find_standings_row_for_driver(driver_id)
        if row is None:
            return

        race_entry = self._race_state.get(driver_id, {})
        if race_entry.get('dnf', False):
            self._apply_dnf_row_state(row, driver_id)
            return

        self._set_standings_item(row, 0, QTableWidgetItem(str(data['position'])), driver_id)
        self._set_standings_item(row, 2, QTableWidgetItem(str(data['lap'])), driver_id)
        self._style_standings_name_cell(row, driver_id)

    def _on_race_finished(self, results: list):
        """Handle race finish."""
        results_sorted: list = []
        try:
            print(f"Race finished event received with {len(results)} results")
            self._log_collision_summary_if_available()
            self._reset_ui_for_race_finished()
            if not results:
                print("WARNING: No results to display")
                return
            results_sorted = self._sorted_results_by_position(results)
            self._render_final_standings(results_sorted)
        except Exception as e:
            print(f"ERROR in _on_race_finished: {e}")
            _traceback.print_exc()

        self._save_race_results_if_needed(results_sorted)
        self._show_position_change_summary_safe(results_sorted)
        self._enable_next_race_if_championship_mode()

    def _log_collision_summary_if_available(self) -> None:
        """Print collision summary block when incidents were recorded."""
        if not hasattr(self, '_collision_log') or not self._collision_log:
            return
        print(f"\n*** COLLISION SUMMARY ({len(self._collision_log)} incidents) ***")
        for i, collision in enumerate(self._collision_log, 1):
            lap = collision.get('lap', '?')
            description = collision.get('description', 'Unknown incident')
            print(f"  {i}. Lap {lap}: {description}")
        print("")

    def _reset_ui_for_race_finished(self) -> None:
        """Reset race controls and stop animation once race completes."""
        self.info_label.setText("Race finished!")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        try:
            if hasattr(self, 'player_status_label'):
                self.player_status_label.hide()
        except Exception:
            pass
        self._set_player_controls_enabled(True)
        if self.track_widget:
            self.track_widget.stop_animation()

    def _set_player_controls_enabled(self, enabled: bool) -> None:
        """Enable or disable player interaction controls as a group."""
        try:
            if hasattr(self, 'pace_slider'):
                self.pace_slider.setEnabled(enabled)
            if hasattr(self, 'overtake_slider'):
                self.overtake_slider.setEnabled(enabled)
            if hasattr(self, 'camera_full_btn'):
                self.camera_full_btn.setEnabled(enabled)
            if hasattr(self, 'camera_follow_btn'):
                self.camera_follow_btn.setEnabled(enabled)
            if hasattr(self, 'push_gauge'):
                self.push_gauge.setEnabled(enabled)
        except Exception:
            pass

    def _sorted_results_by_position(self, results: list) -> list:
        """Return race results sorted by finishing position."""
        return sorted(results, key=lambda r: r.get('position', 999))

    def _render_final_standings(self, results_sorted: list) -> None:
        """Render final leaderboard rows and timing/gap values."""
        leader_time = results_sorted[0].get('time_seconds', 0) if results_sorted else 0
        for i, result in enumerate(results_sorted):
            self._render_final_standings_row(i, result, leader_time)

    def _render_final_standings_row(self, row_index: int, result: dict, leader_time: float) -> None:
        """Render one final standings row with player highlighting."""
        try:
            driver_id = result.get('driver_id')
            driver = next((d for d in self.drivers if d.id == driver_id), None)
            if not driver:
                return

            self._set_standings_item(row_index, 0, QTableWidgetItem(str(row_index + 1)), driver.id)
            self._set_standings_item(row_index, 1, QTableWidgetItem(driver.name), driver.id)
            self._set_standings_item(
                row_index,
                3,
                QTableWidgetItem(self._build_final_time_display(row_index, result, leader_time)),
                driver.id,
            )
            self._style_standings_name_cell(row_index, driver.id)
        except Exception as e:
            print(f"ERROR updating standings row {row_index}: {e}")

    def _build_final_time_display(self, row_index: int, result: dict, leader_time: float) -> str:
        """Format leader total time or follower gap display string."""
        if row_index == 0:
            minutes = int(leader_time // 60)
            seconds = leader_time % 60
            return f"{minutes}:{seconds:06.3f}"
        time_seconds = result.get('time_seconds', 0)
        gap = time_seconds - leader_time
        return f"+{gap:.2f}s" if gap > 0 else "-"

    def _save_race_results_if_needed(self, results_sorted: list) -> None:
        """Persist race results in championship mode."""
        if not (self._championship_id and self._race_id and results_sorted):
            return
        try:
            saved_count = 0
            for result in results_sorted:
                if self._save_single_race_result(result):
                    saved_count += 1
            print(f"[RACE FINISHED] Saved {saved_count} race results to database")
        except Exception as e:
            print(f"WARNING: Error saving race results: {e}")

    def _save_single_race_result(self, result: dict) -> bool:
        """Save one race result record; return True on success."""
        from database.models import RaceResult
        from services.championship_service import ChampionshipService

        driver_id = result.get('driver_id')
        driver = next((d for d in self.drivers if d.id == driver_id), None)
        team_id = driver.current_team_id if driver and hasattr(driver, 'current_team_id') else None
        if team_id is None:
            print(f"WARNING: Skipping result for driver {driver_id} - no team assigned")
            return False

        discipline = str(getattr(self, '_initial_discipline', 'SINGLE_SEATER') or 'SINGLE_SEATER')
        position = int(result.get('position', 0) or 0)
        fastest_lap = bool(result.get('fastest_lap', False))
        dnf_reason = result.get('dnf_reason')

        points = 0
        if dnf_reason is None and position > 0:
            points = ChampionshipService(self.db).calculate_points(
                position=position,
                discipline=discipline,
                fastest_lap=fastest_lap,
            )

        race_result = RaceResult(
            id=None,
            race_id=self._race_id,
            driver_id=driver_id,
            team_id=team_id,
            position=position,
            points=points,
            fastest_lap=fastest_lap,
            dnf_reason=dnf_reason,
            grid_position=result.get('grid_position', result.get('position')),
        )
        try:
            if self.db is not None:
                self.db.save_race_result(race_result)
                return True
        except Exception as e:
            print(f"WARNING: Could not save result for driver {driver_id}: {e}")
        return False

    def _show_position_change_summary_safe(self, results_sorted: list) -> None:
        """Display post-race position summary while keeping flow fail-safe."""
        try:
            self._show_position_change_summary(results_sorted)
        except Exception as e:
            print(f"ERROR showing position change summary: {e}")

    def _enable_next_race_if_championship_mode(self) -> None:
        """Enable next-race navigation in championship mode."""
        if not self._championship_id:
            return
        self.next_race_btn.setEnabled(True)
        print("[RACE FINISHED] Next Race button enabled (championship mode)")

    def _show_position_change_summary(self, results_sorted: list):
        """Display a post-race start-vs-finish summary dialog."""
        try:
            self._show_position_change_summary_impl(results_sorted)
        except Exception as e:
            print(f"Error building position change summary: {e}")

    def _show_position_change_summary_impl(self, results_sorted: list):
        """Display a modal dialog that compares starting grid to final positions.

        Columns: StartPos, FinishPos, Driver, Change, Status
        """
        if not hasattr(self, '_starting_grid') or not self._starting_grid:
            print("No starting grid recorded; skipping position-change summary")
            return
        start_pos = self._build_summary_start_positions(results_sorted)
        rows = self._build_summary_rows(results_sorted, start_pos)
        self._show_summary_table_dialog(rows)

    def _normalize_driver_id(self, driver_id: Any) -> Any:
        """Normalize driver id keys to int when possible."""
        try:
            return int(driver_id)
        except Exception:
            return driver_id

    def _build_summary_start_positions(self, results_sorted: list) -> Dict[Any, int]:
        """Build start-position mapping from recorded grid and engine hints."""
        start_pos: Dict[Any, int] = {}

        for idx, did in enumerate(getattr(self, '_starting_grid', []) or []):
            if did is None:
                continue
            start_pos[self._normalize_driver_id(did)] = idx + 1

        for res in results_sorted:
            did = res.get('driver_id')
            if did is None:
                continue
            gp = res.get('grid_position') or res.get('grid')
            if gp is None:
                continue
            try:
                start_pos[self._normalize_driver_id(did)] = int(gp)
            except Exception:
                try:
                    start_pos[self._normalize_driver_id(did)] = int(float(gp))
                except Exception:
                    pass

        return start_pos

    def _build_summary_rows(self, results_sorted: list, start_pos: Dict[Any, int]) -> List[Tuple[Optional[int], int, str, int, str]]:
        """Build start-vs-finish rows sorted by race finish order."""
        rows: List[Tuple[Optional[int], int, str, int, str]] = []
        for res in results_sorted:
            did = res.get('driver_id')
            did_key = self._normalize_driver_id(did)
            finish = int(res.get('position') or 999)
            name = res.get('driver_name') or next((d.name for d in self.drivers if d.id == did), str(did))
            status = 'DNF' if res.get('dnf_reason') else 'FINISHED'
            start = start_pos.get(did_key)
            change = (start - finish) if start is not None else 0
            rows.append((start, finish, name, change, status))

        # Default to result order (finish position) so the table reads like race standings.
        rows.sort(key=lambda r: (r[1], r[0] if r[0] is not None else 9999))
        return rows

    def _show_summary_table_dialog(self, rows: List[Tuple[Optional[int], int, str, int, str]]) -> None:
        """Show a compact position-change dialog with table-only content."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Race Position Changes")
        dlg_layout = QVBoxLayout()

        info = QLabel("<h2>Start -> Finish</h2><p>Positive = gained positions. DNFs are highlighted.</p>")
        info.setTextFormat(Qt.TextFormat.RichText)
        dlg_layout.addWidget(info)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Start", "Finish", "Driver", "Change", "Status"])
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            start, finish, name, change, status = row
            table.setItem(r, 0, QTableWidgetItem(str(start) if start is not None else "-"))
            table.setItem(r, 1, QTableWidgetItem(str(finish)))
            table.setItem(r, 2, QTableWidgetItem(name))
            table.setItem(r, 3, QTableWidgetItem(f"{change:+d}"))
            status_item = QTableWidgetItem(status)
            if status == 'DNF':
                status_item.setBackground(QColor(220, 40, 40))
                status_item.setForeground(QColor(255, 255, 255))
            table.setItem(r, 4, status_item)

        table.resizeColumnsToContents()
        hdr = table.horizontalHeader()
        if isinstance(hdr, QHeaderView):
            hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.setAlternatingRowColors(True)
        dlg_layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        dlg_layout.addWidget(close_btn)

        try:
            pref_w, pref_h = get_preferred_window_size()
            dlg_w = int(pref_w * 0.65)
            dlg_h = int(pref_h * 0.5)
            dlg.setMinimumSize(dlg_w, dlg_h)
            dlg.resize(dlg_w, dlg_h)
        except Exception:
            pass

        dlg.setLayout(dlg_layout)
        dlg.setModal(True)
        dlg.exec()

    def _on_event(self, message: str):
        """
        *** Handle general race events from simulation ***

        This receives string messages from the race engine containing:
        - telemetry_update: Player driver telemetry (speed, push, fatigue, tires)
        - standings_update: Position changes during race
        - General info messages

        TELEMETRY UPDATE FORMAT:
        "telemetry_update|speed_kph|push_intensity|push_fatigue|tire_condition"

        STANDINGS UPDATE FORMAT (live gaps):
        "standings_update|driver_id|position|lap|push|gap_ahead|position_m|race_time"

        Example: "standings_update|5|1|3|0.72|0.45|19234.5|185.4"
        Means: Driver 5 is P1, lap 3, push 0.72, 0.45s gap to car ahead,
        at position 19,234.5m and race time 185.4s.
        """
        if message == "start_animation":
            self._handle_start_animation_event()
            return

        if message.startswith("telemetry_update|"):
            self._handle_telemetry_event(message)
            return

        if message.startswith("mark_dnf|"):
            self._handle_mark_dnf_event(message)
            return

        if message.startswith("player_dnf|"):
            self._handle_player_dnf_event(message)
            return

        if message.startswith("standings_update|"):
            self._handle_standings_update_event(message)
            return

        self.info_label.setText(message)

    def _handle_start_animation_event(self) -> None:
        """Start track animation when first simulation data is ready."""
        try:
            if self.track_widget:
                self.track_widget.start_animation()
                print("[ANIMATION] Animation timer started (main thread)")
        except Exception as e:
            print(f"ERROR starting animation in GUI thread: {e}")

    def _set_fatigue_label_style(self, push_fatigue: float) -> None:
        """Apply fatigue color/warning style by fatigue threshold."""
        if push_fatigue > 0.7:
            self.fatigue_label.setStyleSheet("font-size: 14px; color: #DD2D4A; font-weight: bold;")
        elif push_fatigue > 0.4:
            self.fatigue_label.setStyleSheet("font-size: 14px; color: #DD2D4A; font-weight: normal;")
        else:
            self.fatigue_label.setStyleSheet("font-size: 14px; color: #B9F2FF;")

    def _set_tire_label_style(self, tire_condition: float) -> None:
        """Apply tire condition style by wear threshold."""
        if tire_condition < 0.3:
            self.tire_label.setStyleSheet("font-size: 14px; color: #DD2D4A; font-weight: bold;")
        elif tire_condition < 0.6:
            self.tire_label.setStyleSheet("font-size: 14px; color: #DD2D4A;")
        else:
            self.tire_label.setStyleSheet("font-size: 14px; color: #B9F2FF;")

    def _handle_telemetry_event(self, message: str) -> None:
        """Update player telemetry panel from event payload."""
        try:
            parts = message.split("|")
            if len(parts) < 5:
                return

            speed_kph = float(parts[1])
            push_intensity = float(parts[2])
            push_fatigue = float(parts[3])
            tire_condition = float(parts[4])

            self.speed_label.setText(f"Speed: {speed_kph:.0f} km/h")
            self.push_gauge.setValue(int(push_intensity * 100))

            fatigue_percent = int(push_fatigue * 100)
            self.fatigue_label.setText(f"Fatigue: {fatigue_percent}%")
            self._set_fatigue_label_style(push_fatigue)

            tire_percent = int(tire_condition * 100)
            self.tire_label.setText(f"Tire: {tire_percent}%")
            self._set_tire_label_style(tire_condition)
        except Exception as e:
            print(f"Error updating telemetry display: {e}")
            _traceback.print_exc()

    def _ensure_race_state(self) -> None:
        """Ensure race-state container exists before state updates."""
        if not hasattr(self, '_race_state'):
            self._race_state = {}

    def _driver_name_by_id(self, driver_id: int) -> str:
        """Resolve driver display name from current race entrants."""
        return next((d.name for d in self.drivers if getattr(d, 'id', None) == driver_id), f"Driver {driver_id}")

    def _mark_driver_dnf_in_state(self, driver_id: int) -> None:
        """Mark a driver as DNF in race state, creating minimal row when missing."""
        self._ensure_race_state()
        entry = self._race_state.get(driver_id)
        if entry is not None:
            entry['dnf'] = True
            return

        self._race_state[driver_id] = {
            'name': self._driver_name_by_id(driver_id),
            'position': None,
            'lap': None,
            'time': 0.0,
            'distance': 0.0,
            'gap_ahead': 0.0,
            'dnf': True,
            'total_progress': 0.0,
        }

    def _refresh_standings_safe(self) -> None:
        """Rebuild standings while keeping event handlers fail-safe."""
        try:
            self._rebuild_standings_table()
        except Exception:
            pass

    def _handle_mark_dnf_event(self, message: str) -> None:
        """Process generic DNF command emitted from simulation thread."""
        try:
            parts = message.split("|")
            if len(parts) < 2:
                return
            did = int(parts[1])
            tw = getattr(self, 'track_widget', None)
            if tw is None or not hasattr(tw, 'mark_dnf'):
                return

            print(f"[GUI EVENT] Received mark_dnf for driver {did}")
            tw.mark_dnf(did)
            try:
                if getattr(tw, 'camera_mode', None) == 'follow' and getattr(tw, 'follow_car_id', None) == did:
                    tw.set_camera_mode('full')
                    print(f"[CAMERA] Followed car {did} DNF'd — switching to full track view")
            except Exception:
                pass

            self._mark_driver_dnf_in_state(did)
            self._refresh_standings_safe()
        except Exception:
            pass

    def _controlled_driver_ids(self) -> set:
        """Return the set of drivers controlled by player team/selection."""
        controlled = set(getattr(self, 'player_team_driver_ids', []) or [])
        player_id = getattr(self, 'player_driver_id', None)
        if player_id is not None:
            controlled.add(player_id)
        return controlled

    def _has_active_controlled_driver(self, controlled_ids: set) -> bool:
        """Return True if at least one controlled driver is still not DNF."""
        self._ensure_race_state()
        for cid in controlled_ids:
            c_entry = self._race_state.get(cid)
            if c_entry is None:
                return True
            if not bool(c_entry.get('dnf', False)):
                return True
        return False

    def _disable_player_controls(self) -> None:
        """Disable player-control widgets once whole controlled team retires."""
        try:
            if hasattr(self, 'player_status_label'):
                self.player_status_label.setText("TEAM RETIRED")
            if hasattr(self, 'pace_slider'):
                self.pace_slider.setEnabled(False)
            if hasattr(self, 'overtake_slider'):
                self.overtake_slider.setEnabled(False)
            if hasattr(self, 'camera_full_btn'):
                self.camera_full_btn.setEnabled(False)
            if hasattr(self, 'camera_follow_btn'):
                self.camera_follow_btn.setEnabled(False)
            if hasattr(self, 'push_gauge'):
                self.push_gauge.setEnabled(False)
        except Exception:
            pass

    def _handle_player_dnf_event(self, message: str) -> None:
        """Process DNF updates for controlled cars and reflect UI state."""
        try:
            parts = message.split("|")
            if len(parts) < 2:
                return
            did = int(parts[1])
            controlled_ids = self._controlled_driver_ids()
            player_id = getattr(self, 'player_driver_id', None)
            if did not in controlled_ids:
                return

            print(f"[GUI EVENT] Received player_dnf for controlled driver {did}")
            try:
                if hasattr(self, 'player_status_label'):
                    self.player_status_label.setText("PRIMARY CAR RETIRED" if did == player_id else "TEAM CAR RETIRED")
                    self.player_status_label.show()
            except Exception:
                pass

            self._mark_driver_dnf_in_state(did)
            if not self._has_active_controlled_driver(controlled_ids):
                self._disable_player_controls()
            self._refresh_standings_safe()
        except Exception:
            pass

    def _update_race_state_from_standings(
        self,
        driver_id: int,
        race_position: int,
        lap: int,
        race_time: float,
        position_m: float,
        gap_ahead: float,
        push_intensity: float,
    ) -> None:
        """Merge standings payload into race state and push-intensity cache."""
        if not hasattr(self, '_driver_push_intensity'):
            self._driver_push_intensity = {}

        driver = next((d for d in self.drivers if d.id == driver_id), None)
        if not driver:
            return

        existing = self._race_state.get(driver_id, {}) if hasattr(self, '_race_state') else {}
        dnf_flag = existing.get('dnf', False)
        self._ensure_race_state()
        self._race_state[driver_id] = {
            'name': driver.name,
            'position': race_position,
            'lap': lap,
            'time': race_time,
            'distance': position_m,
            'gap_ahead': gap_ahead,
            'dnf': dnf_flag,
        }
        self._driver_push_intensity[driver_id] = push_intensity

    def _record_position_history(self, driver_id: int, lap: int, position_m: float, race_position: int, race_time: float) -> None:
        """Append race position history for post-race plotting."""
        try:
            if not hasattr(self, '_position_history'):
                self._position_history = {}
            hist = self._position_history.get(driver_id)
            if hist is None:
                hist = []
                self._position_history[driver_id] = hist

            try:
                track_obj = getattr(self, 'track', None)
                track_length_m = (track_obj.length_km * 1000.0) if track_obj is not None else 6350.0
            except Exception:
                track_length_m = 6350.0

            try:
                total_distance = (max(1, int(lap)) - 1) * track_length_m + position_m
            except Exception:
                total_distance = race_time
            hist.append((total_distance, race_position))
        except Exception:
            pass

    def _handle_standings_update_event(self, message: str) -> None:
        """Process live standings payload and refresh table."""
        try:
            parts = message.split("|")
            driver_id = int(parts[1])
            race_position = int(parts[2])
            lap = max(1, int(parts[3]) + 1)
            push_intensity = float(parts[4]) if len(parts) > 4 else 0.7
            gap_ahead = float(parts[5]) if len(parts) > 5 else 0.0
            position_m = float(parts[6]) if len(parts) > 6 else 0.0
            race_time = float(parts[7]) if len(parts) > 7 else 0.0

            self._update_race_state_from_standings(
                driver_id,
                race_position,
                lap,
                race_time,
                position_m,
                gap_ahead,
                push_intensity,
            )
            self._record_position_history(driver_id, lap, position_m, race_position, race_time)
            self._rebuild_standings_table()
        except Exception:
            pass

    def _rebuild_standings_table(self):
        """Rebuild the standings table with live gaps and proper lapped classification."""
        self._rebuild_standings_table_impl()

    def _rebuild_standings_table_impl(self) -> None:
        """Implementation body extracted to keep entrypoint complexity low."""
        if not hasattr(self, '_race_state'):
            return

        track_length = self._current_track_length_m()
        standings_list = self._build_standings_entries(track_length)
        if not standings_list:
            return

        standings_list.sort(key=lambda x: (x['dnf'], -x['total_progress']))

        finished_drivers, lapped_drivers, dnf_drivers, leader_lap = self._classify_standings_entries(standings_list)
        all_classified = finished_drivers + lapped_drivers + dnf_drivers

        self._ensure_standings_row_count(len(all_classified))
        cumulative_gap = 0.0
        for row, entry in enumerate(all_classified):
            cumulative_gap = self._render_standings_row(
                row,
                entry,
                cumulative_gap,
                leader_lap,
                lapped_drivers,
                dnf_drivers,
            )

        self._maybe_log_standings_debug(finished_drivers, lapped_drivers, leader_lap)
        self._resize_standings_height()

    def _current_track_length_m(self) -> float:
        """Return current track length in meters with fallback."""
        track_obj = getattr(self, 'track', None)
        return (track_obj.length_km * 1000.0) if track_obj is not None else 6350.0

    def _build_standings_entries(self, track_length: float) -> List[Dict[str, Any]]:
        """Build standings list enriched with total progress and race metadata."""
        standings_list: List[Dict[str, Any]] = []
        for did, data in self._race_state.items():
            lap_for_progress = max(0, int(data.get('lap', 1)) - 1)
            total_progress = lap_for_progress * track_length + (data.get('distance', 0.0) % track_length)
            standings_list.append({
                'driver_id': did,
                'name': data['name'],
                'position': data['position'],
                'lap': data['lap'],
                'time': data.get('time', 0.0),
                'distance': data.get('distance', 0.0),
                'gap_ahead': data.get('gap_ahead', 0.0),
                'dnf': data.get('dnf', False),
                'total_progress': total_progress,
            })
        return standings_list

    def _classify_standings_entries(self, standings_list: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], int]:
        """Split standings into finished, lapped, and DNF buckets."""
        leader_lap = int(standings_list[0]['lap']) if standings_list else 0
        finished_drivers: List[Dict[str, Any]] = []
        lapped_drivers: List[Dict[str, Any]] = []
        dnf_drivers: List[Dict[str, Any]] = []
        for entry in standings_list:
            if entry['dnf']:
                dnf_drivers.append(entry)
                continue
            if entry['lap'] < leader_lap:
                lapped_drivers.append(entry)
                continue
            finished_drivers.append(entry)
        return finished_drivers, lapped_drivers, dnf_drivers, leader_lap

    def _ensure_standings_row_count(self, row_count: int) -> None:
        """Resize standings table rows only when row count changes."""
        if row_count == getattr(self, '_last_standings_row_count', 0):
            return
        self.standings_table.setRowCount(row_count)
        self._last_standings_row_count = row_count

    def _render_standings_row(
        self,
        row: int,
        entry: Dict[str, Any],
        cumulative_gap: float,
        leader_lap: int,
        lapped_drivers: List[Dict[str, Any]],
        dnf_drivers: List[Dict[str, Any]],
    ) -> float:
        """Render one row and return updated cumulative time gap."""
        driver_id = entry['driver_id']
        self._set_standings_item(row, 0, self._build_colour_item(driver_id), driver_id)
        self._set_standings_item(row, 1, self._build_driver_name_item(entry), driver_id)
        self._style_standings_name_cell(row, driver_id)
        self._set_standings_item(row, 2, QTableWidgetItem(str(entry['lap'])), driver_id)
        gap_text, new_cumulative = self._compute_gap_text(
            row,
            entry,
            cumulative_gap,
            leader_lap,
            lapped_drivers,
            dnf_drivers,
        )
        self._set_standings_item(row, 3, QTableWidgetItem(gap_text), driver_id)
        return new_cumulative

    def _build_colour_item(self, driver_id: int) -> QTableWidgetItem:
        """Create leading colour-cell item for a standings row."""
        colour_item = QTableWidgetItem()
        if driver_id in self.driver_colours:
            colour_item.setBackground(self.driver_colours[driver_id])
            colour_item.setText("  ")
        return colour_item

    def _build_driver_name_item(self, entry: Dict[str, Any]) -> QTableWidgetItem:
        """Build display name with aggression symbol."""
        push_int = self._driver_push_intensity.get(entry['driver_id'], 0.7)
        if push_int < 0.25:
            symbol = "(-)"
        elif push_int < 0.75:
            symbol = "(=)"
        else:
            symbol = "(+)"
        return QTableWidgetItem(f"{symbol} {entry['name']}")

    def _compute_gap_text(
        self,
        row: int,
        entry: Dict[str, Any],
        cumulative_gap: float,
        leader_lap: int,
        lapped_drivers: List[Dict[str, Any]],
        dnf_drivers: List[Dict[str, Any]],
    ) -> Tuple[str, float]:
        """Return formatted gap text and updated cumulative gap value."""
        if entry.get('dnf', False) or entry in dnf_drivers:
            return "DNF", cumulative_gap
        if row == 0:
            return "LEADER", cumulative_gap
        if entry in lapped_drivers:
            lap_deficit = leader_lap - entry['lap']
            return f"+{lap_deficit}L", cumulative_gap

        raw_gap = entry.get('gap_ahead', 0.0)
        if raw_gap >= 1000.0:
            laps_behind = int(raw_gap - 999.0)
            if laps_behind > 0:
                return f"+{laps_behind}L", cumulative_gap
            cumulative_gap += max(raw_gap - 999.0, 0.0)
        else:
            cumulative_gap += max(raw_gap, 0.0)

        if cumulative_gap < 0.1:
            return "-", cumulative_gap
        return f"+{cumulative_gap:.1f}s", cumulative_gap

    def _maybe_log_standings_debug(
        self,
        finished_drivers: List[Dict[str, Any]],
        lapped_drivers: List[Dict[str, Any]],
        leader_lap: int,
    ) -> None:
        """Print compact periodic standings debug output."""
        if not hasattr(self, '_last_standings_log'):
            self._last_standings_log = 0.0
        now = time.time()
        if now - self._last_standings_log <= 3.0:
            return
        self._last_standings_log = now
        print("\n  [STANDINGS] Current order (CORRECTED CLASSIFICATION):")
        self._log_finished_drivers_debug(finished_drivers)
        self._log_lapped_drivers_debug(lapped_drivers, leader_lap)

    def _log_finished_drivers_debug(self, finished_drivers: List[Dict[str, Any]]) -> None:
        """Log top finished drivers with live gap metadata."""
        for i, entry in enumerate(finished_drivers[:5]):
            print(f"    P{i + 1}: {entry['name']} (L{entry['lap']}, gap={entry.get('gap_ahead', 0.0):.1f}s)")

    def _log_lapped_drivers_debug(self, lapped_drivers: List[Dict[str, Any]], leader_lap: int) -> None:
        """Log top lapped drivers with lap deficit markers."""
        if not lapped_drivers:
            return
        print("    --- LAPPED ---")
        for entry in lapped_drivers[:3]:
            lap_deficit = leader_lap - entry['lap']
            print(f"    +{lap_deficit}L: {entry['name']} (L{entry['lap']})")


    def _set_standings_item(self, row: int, col: int, item: QTableWidgetItem, driver_id: Optional[int] = None):
        """Set an item in the standings table but respect DNF state.

        If `driver_id` is provided and that driver is marked DNF in
        `self._race_state`, this will write a stable DNF/placeholder
        instead of allowing other code to overwrite the cell.
        """
        try:
            if self._is_dnf_driver(driver_id):
                self._set_dnf_standings_item(row, col, item)
                return
            self.standings_table.setItem(row, col, item)
        except Exception:
            try:
                # Best-effort fallback
                self.standings_table.setItem(row, col, item)
            except Exception:
                pass

    def _is_dnf_driver(self, driver_id: Optional[int]) -> bool:
        """Return True when the target row belongs to a DNF driver."""
        if driver_id is None or not hasattr(self, '_race_state'):
            return False
        entry = self._race_state.get(driver_id, {})
        return bool(entry.get('dnf', False))

    def _set_dnf_standings_item(self, row: int, col: int, item: QTableWidgetItem) -> None:
        """Write DNF-safe placeholders and muted styling."""
        if col == 3:
            self.standings_table.setItem(row, col, QTableWidgetItem("DNF"))
        elif col in (0, 2):
            self.standings_table.setItem(row, col, QTableWidgetItem("-"))
        else:
            self.standings_table.setItem(row, col, item)
        self._apply_dnf_name_cell_style(row)

    def _apply_dnf_name_cell_style(self, row: int) -> None:
        """Apply greyed-out style to DNF name cell."""
        try:
            name_cell = self.standings_table.item(row, 1)
            if name_cell is None:
                return
            name_cell.setBackground(QColor(80, 80, 80))
            name_cell.setForeground(QColor(200, 200, 200))
        except Exception:
            pass

    def _resize_standings_height(self):
        """Resize standings table to its contents to avoid scrollbars."""
        try:
            rows = self.standings_table.rowCount()
            header = self.standings_table.horizontalHeader()
            header_h = header.height() if header else 0
            row_heights = rows * getattr(self, '_standings_row_height', 26)
            margins = self.standings_table.contentsMargins()
            frame = self.standings_table.frameWidth() * 2
            total = header_h + row_heights + margins.top() + margins.bottom() + frame + 4
            self.standings_table.setMinimumHeight(total)
            self.standings_table.setMaximumHeight(total)
        except Exception:
            pass

    def _on_pace_changed(self, value):
        """Handle pace slider change - update label and colour gradient."""
        if value < 33:
            pace_text = "CONSERVATIVE"
        elif value < 67:
            pace_text = "BALANCED"
        else:
            pace_text = "AGGRESSIVE"

        # Store raw slider value (0-100)
        self.player_overrides['pace'] = value / 100.0
        # Recompute combined push from both sliders
        self._update_combined_push()
        self.pace_value_label.setText(f"Race Pace: {pace_text} ({value}%)")

        # Mix colour from blue -> red based on value
        try:
            t = max(0.0, min(1.0, value / 100.0))
            low = (0x00, 0xBF, 0xFF)  # blue
            high = (0xDD, 0x2D, 0x4A)  # red
            r = int(low[0] + (high[0] - low[0]) * t)
            g = int(low[1] + (high[1] - low[1]) * t)
            b = int(low[2] + (high[2] - low[2]) * t)
            colour = f"#{r:02X}{g:02X}{b:02X}"
            self.pace_value_label.setStyleSheet(CONTROL_LABEL_STYLE)
            # Update slider styling: sub-page shows selected colour
            self.pace_slider.setStyleSheet(
                "QSlider::groove:horizontal { height: 8px; background: #2E2E2E; border-radius: 4px; }"
                f"QSlider::sub-page:horizontal {{ background: {colour}; border-radius: 4px; }}"
                "QSlider::handle:horizontal { background: #F5F5F5; width: 14px; margin: -4px 0; border-radius: 7px; }"
            )
        except Exception:
            # Fallback: keep readable style
            self.pace_value_label.setStyleSheet(
                "font-size:16px; font-weight:bold; color: #DD2D4A;")

    def _on_overtake_changed(self, value):
        """Handle overtake aggressiveness slider change with dynamic colour."""
        if value < 33:
            aggr_text = "CAUTIOUS"
        elif value < 67:
            aggr_text = "MODERATE"
        else:
            aggr_text = "AGGRESSIVE"

        # Store raw slider value (0-100)
        self.player_overrides['overtake'] = value / 100.0
        # Recompute combined push from both sliders
        self._update_combined_push()
        self.overtake_value_label.setText(
            f"Overtaking: {aggr_text} ({value}%)")

        try:
            t = max(0.0, min(1.0, value / 100.0))
            low = (0x00, 0xBF, 0xFF)
            high = (0xDD, 0x2D, 0x4A)
            r = int(low[0] + (high[0] - low[0]) * t)
            g = int(low[1] + (high[1] - low[1]) * t)
            b = int(low[2] + (high[2] - low[2]) * t)
            colour = f"#{r:02X}{g:02X}{b:02X}"
            self.overtake_value_label.setStyleSheet(CONTROL_LABEL_STYLE)
            style = (
                "QSlider::groove:horizontal { "
                "height: 8px; background: #2E2E2E; "
                "border-radius: 4px; }"
                f"QSlider::sub-page:horizontal {{ "
                f"background: {colour}; border-radius: 4px; }}"
            )
            self.overtake_slider.setStyleSheet(
                style +
                "QSlider::handle:horizontal { background: #F5F5F5; "
                "width: 14px; margin: -4px 0; border-radius: 7px; }"
            )
        except Exception:
            self.overtake_value_label.setStyleSheet(
                "font-size:16px; font-weight:bold; color: #FFFFFF;")

    def _update_combined_push(self):
        """Compute combined push intensity as average of pace and overtake sliders."""
        pace_norm = self.player_overrides.get('pace', 0.5)
        overtake_norm = self.player_overrides.get('overtake', 0.5)
        # Average both sliders: 100% push only when both at 100%
        avg = (pace_norm + overtake_norm) / 2.0
        # Map to 0.3-1.0 range
        self.player_overrides['push'] = 0.3 + avg * 0.7
        print(
            f"[PLAYER PUSH] pace={
                pace_norm *
                100:.0f}%, overtake={
                overtake_norm *
                100:.0f}% → combined push={
                self.player_overrides['push']:.2f}")

    def set_player_driver(self, driver):
        """Set the player-controlled driver."""
        if driver:
            self.player_driver_id = driver.id
            inferred_team_id = getattr(driver, 'current_team_id', None)
            if inferred_team_id:
                self.player_team_id = int(inferred_team_id)
            print(
                f"[RACE WINDOW] Player driver set: {
                    driver.name} (ID: {
                    driver.id})")
        else:
            self.player_driver_id = None

        # Keep entrant list and visuals consistent when player selection changes.
        self._ensure_player_driver_in_grid(driver)

        # Refresh team-controlled driver ids after driver assignment.
        try:
            self._rebuild_player_team_driver_ids()
        except Exception:
            pass

    def _build_cars_from_drivers(self) -> List[Car]:
        """Create grid cars from current entrant list using stable grid spacing."""
        cars: List[Car] = []
        for i, drv in enumerate(getattr(self, 'drivers', []) or []):
            row = i // 2
            grid_spacing = 15.0
            start_position = row * grid_spacing
            drv_id_raw = getattr(drv, 'id', 0)
            try:
                drv_id = int(drv_id_raw) if drv_id_raw is not None else 0
            except Exception:
                drv_id = 0
            car_colour = self.driver_colours.get(drv_id, QColor(200, 200, 200))
            cars.append(Car(
                driver_id=drv_id,
                driver_name=getattr(drv, 'name', ''),
                s=start_position,
                colour=car_colour,
                total_time=0.0,
                avg_lap_time=60.0,
                last_lap=0
            ))
        return cars

    def _refresh_standings_names(self) -> None:
        """Refresh standings names to match current entrant order."""
        self.standings_table.setRowCount(len(getattr(self, 'drivers', []) or []))
        for i, drv in enumerate(self.drivers):
            self.standings_table.setItem(i, 1, QTableWidgetItem(getattr(drv, 'name', '')))

    def _refresh_grid_visuals(self) -> bool:
        """Rebuild cars + table rows after entrant list changes.

        Returns True when cars are pushed to the track widget.
        """
        tw = getattr(self, 'track_widget', None)
        if tw is None:
            return False

        cars = self._build_cars_from_drivers()
        tw.set_cars(cars)
        self._refresh_standings_names()
        return True

    def _ensure_player_driver_in_grid(self, driver) -> None:
        """Ensure selected player driver is present in entrants, then refresh visuals."""
        try:
            existing = getattr(self, 'drivers', None)
            if not driver or existing is None:
                return

            present = any(getattr(d, 'id', None) == driver.id for d in existing)
            if not present:
                if len(existing) >= RACE_GRID_SIZE:
                    existing[-1] = driver
                else:
                    existing.append(driver)

            if self._refresh_grid_visuals():
                print(f"[RACE WINDOW] Rebuilt cars to include player: {driver.name} (ID: {driver.id})")
                print("[RACE WINDOW] Standings updated to include player driver")
        except Exception:
            print("[RACE WINDOW] Warning: couldn't ensure player driver in driver list")

    def set_player_team(self, team):
        """Set the player team so strategy controls apply to all team cars."""
        if team is None:
            self.player_team_id = None
            self.player_team_driver_ids = []
            return

        try:
            self.player_team_id = int(getattr(team, 'id'))
            print(f"[RACE WINDOW] Player team set: {getattr(team, 'name', 'Unknown Team')} (ID: {self.player_team_id})")
        except Exception:
            self.player_team_id = None

        # Ensure all cars from the selected team are present on the race grid.
        self._ensure_team_drivers_in_grid()

        self._rebuild_player_team_driver_ids()

    def _ensure_team_drivers_in_grid(self) -> None:
        """Ensure all contracted drivers for player team are present in entrants."""
        try:
            if self.player_team_id is None or self.db is None or getattr(self, 'drivers', None) is None:
                return

            team_drivers = self.db.get_drivers_by_team(self.player_team_id)
            present_ids = {int(getattr(d, 'id')) for d in self.drivers if getattr(d, 'id', None) is not None}
            changed = False
            replace_idx = max(0, len(self.drivers) - 1)

            for team_driver in team_drivers:
                td_id = getattr(team_driver, 'id', None)
                if td_id is None or int(td_id) in present_ids:
                    continue
                if len(self.drivers) < RACE_GRID_SIZE:
                    self.drivers.append(team_driver)
                else:
                    self.drivers[replace_idx] = team_driver
                    replace_idx = max(0, replace_idx - 1)
                present_ids.add(int(td_id))
                changed = True

            if changed and self._refresh_grid_visuals():
                print("[RACE WINDOW] Rebuilt grid to include all team cars")
        except Exception:
            print("[RACE WINDOW] Warning: couldn't ensure team cars in driver list")

    def _rebuild_player_team_driver_ids(self):
        """Recompute controlled team-car IDs from current entrants."""
        controlled = set()
        for drv in getattr(self, 'drivers', []) or []:
            did = getattr(drv, 'id', None)
            if did is None:
                continue
            team_id = getattr(drv, 'current_team_id', None)
            if self.player_team_id is not None and team_id is not None and int(team_id) == int(self.player_team_id):
                controlled.add(int(did))

        if self.player_driver_id is not None:
            controlled.add(int(self.player_driver_id))

        self.player_team_driver_ids = sorted(controlled)
        if self.player_team_driver_ids:
            print(f"[RACE WINDOW] Team-control drivers: {self.player_team_driver_ids}")

    def set_tuning_preset(self, preset: str):
        """Set the simulation tuning preset."""
        self.tuning_preset = preset or 'balanced'
        print(f"[RACE WINDOW] Tuning preset set: {self.tuning_preset}")

    def _set_camera_mode(self, mode: str):
        """Set camera mode: 'full' or 'follow'."""
        self.camera_mode = mode
        follow_id = None
        if mode == 'follow':
            follow_id = self._resolve_follow_driver_id()
            if follow_id is None:
                print("[CAMERA] No player driver set - cannot follow")
                self.camera_mode = 'full'
                mode = 'full'

        tw = getattr(self, 'track_widget', None)
        if tw is not None:
            tw.set_camera_mode(mode, follow_id)

        # Update button styles
        if mode == 'full':
            self.camera_full_btn.setStyleSheet(
                "background-color: #B9F2FF; color: #353839;")
            self.camera_follow_btn.setStyleSheet("")
        else:
            self.camera_follow_btn.setStyleSheet(
                "background-color: #B9F2FF; color: #353839;")
            self.camera_full_btn.setStyleSheet("")

        print(f"[CAMERA] Switched to {mode} mode (follow_id: {follow_id})")

    def _resolve_follow_driver_id(self) -> Optional[int]:
        """Resolve which driver to follow in camera mode.

        Priority: explicit player driver, then any controlled team car.
        """
        if hasattr(self, 'player_driver_id') and self.player_driver_id is not None:
            return self.player_driver_id
        if hasattr(self, 'player_team_driver_ids') and self.player_team_driver_ids:
            return self.player_team_driver_ids[0]
        return None

    def set_display_mode(self, mode: str):
        """Set display mode: 'windowed', 'borderless', or 'fullscreen'."""
        self.display_mode = mode
        screen_obj = QApplication.primaryScreen()
        available = screen_obj.availableGeometry() if screen_obj else None

        if mode == "windowed":
            self._apply_windowed_mode()
        elif mode == "borderless":
            self._apply_borderless_mode(available)
        elif mode == "fullscreen":
            self._apply_fullscreen_mode(available)

        self.show()

    def _reset_child_min_sizes(self) -> None:
        """Clear size constraints so window mode switches don't fight widget minimums."""
        try:
            for w in self.findChildren(QWidget):
                try:
                    w.setMinimumSize(0, 0)
                except Exception:
                    pass
        except Exception:
            pass

    def _apply_max_size_from_rect(self, rect) -> None:
        """Clamp window max size to the provided screen rectangle."""
        if rect is None:
            return
        try:
            self.setMaximumSize(rect.width(), rect.height())
        except Exception:
            pass

    def _apply_windowed_mode(self) -> None:
        """Switch to standard resizable windowed mode."""
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
        self.showNormal()
        self.setGeometry(100, 100, 1600, 900)
        print("[INFO] Race window: windowed mode (1600x900)")

    def _apply_borderless_mode(self, available) -> None:
        """Switch to borderless-windowed fullscreen mode."""
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        if available is not None:
            try:
                self.setMinimumSize(0, 0)
            except Exception:
                pass
            self._reset_child_min_sizes()
            self._apply_max_size_from_rect(available)
            self.setGeometry(available)
        self.showMaximized()
        print("[INFO] Race window: borderless windowed fullscreen")

    def _apply_fullscreen_mode(self, available) -> None:
        """Switch to native exclusive fullscreen mode."""
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
        if available is not None:
            self._reset_child_min_sizes()
            self._apply_max_size_from_rect(available)
        self.showFullScreen()
        print("[INFO] Race window: exclusive fullscreen")

    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        """Handle keyboard events."""
        if a0 is None:
            return
        if a0.key() == Qt.Key.Key_Escape:
            # ESC key: Stop race and return to menu
            print("[INFO] ESC pressed - returning to main menu")
            self._stop_race()
            self.return_to_menu.emit()
            self.close()
        else:
            super().keyPressEvent(a0)


def main():
    # Use top-level imports; no local imports needed here
    app = QApplication(sys.argv)
    try:
        window = RaceWindow()
        window.show()
        print("[DEBUG] RaceWindow created and shown.")
        # Show a message box to confirm GUI launch
    except Exception as e:
        print("[ERROR] Exception during GUI launch:", e)
        _traceback.print_exc()
        raise
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
