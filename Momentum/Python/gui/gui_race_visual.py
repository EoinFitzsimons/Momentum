"""
Combined GUI: Race simulation with visual track display.

Integrates:
- Circuit generation from circuit_with_grid.py
- Race simulation engine from gui_game.py
- Real-time car position updates based on simulation events
"""

import sys
import os
import math
import time
import threading
import traceback
from typing import Any, List, Dict, Optional, cast
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt, QPointF, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QKeyEvent, QPaintEvent

from database.database_manager import DatabaseManager
from services.race_simulation_api import simulate_race
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline
from database.models import Team


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
    color: QColor
    dnf: bool = False
    # Use 1-based lap counting for UI (show lap 1 as first racing lap)
    lap: int = 1
    total_time: float = 0.0  # Total race time from simulation
    avg_lap_time: float = 60.0  # Average lap time in seconds
    last_lap: int = 0  # Last completed lap number
    velocity_mps: float = 0.0
    movement_direction: float = 0.0
    prev_s: Optional[float] = None


class EventEmitter(QObject):
    """Signal emitter for race events."""
    position_update = pyqtSignal(dict)  # {driver_id: {lap, position, total_time}}
    race_finished = pyqtSignal(list)
    event_signal = pyqtSignal(str)


class CircuitGenerator:
    """Generates racing circuit with clothoid transitions."""
    
    @staticmethod
    def generate(track_length_km: float = 5.0):
        """Generate circuit based on track length."""
        segments = []
        state = {
            'segments': segments,
            'current_s': 0,
            'current_x': 0,
            'current_y': 0,
            'current_theta': 0,
            'total_angle': 0,
            'target_length_m': track_length_km * 1000  # Store target for post-scaling
        }
        
        # Scale circuit instructions based on track length
        # Note: This is approximate - final track will be rescaled to exact length
        scale = track_length_km / 6.0  # Base is ~6km
        
        # Interesting varied circuit - closure will be calculated dynamically
        circuit_instructions = [
            ('S', int(600 * scale)),
            ('C', 45, 170, 60, 0.00008),
            ('S', int(400 * scale)),
            ('C', 65, 95, 50, 0.0001),
            ('S', int(220 * scale)),
            ('C', -55, 100, 52, 0.0001),
            ('S', int(350 * scale)),
            ('C', 155, 48, 42, 0.00014),
            ('S', int(550 * scale)),
            ('C', -65, 145, 58, 0.00009),
            ('S', int(380 * scale)),
            ('C', 55, 115, 54, 0.00009),
            ('S', int(180 * scale)),
            ('C', 60, 90, 50, 0.0001),
            ('S', int(300 * scale)),
            ('C', -50, 135, 56, 0.00009),
            ('S', int(160 * scale)),
            ('C', 50, 135, 56, 0.00009),
            ('S', int(320 * scale)),
            # Closure corners will be added automatically by _process_instructions
        ]
        
        CircuitGenerator._process_instructions(circuit_instructions, state)
        CircuitGenerator._rescale_to_target_length(segments, state)
        CircuitGenerator._finalize_circuit(segments)
        
        return segments
    
    @staticmethod
    def _process_instructions(instructions, state):
        start_x, start_y = 0, 0  # Track starts at origin
        
        # Process all instructions
        for instruction in instructions:
            if instruction[0] == 'S':
                CircuitGenerator._add_straight(instruction[1], state)
            elif instruction[0] == 'C':
                angle_deg, radius, clothoid_len, k = instruction[1:5]
                CircuitGenerator._add_corner(angle_deg * math.pi / 180, radius, clothoid_len, k, state)
        
        # NOW: Calculate what we need to close the loop
        dx = start_x - state['current_x']
        dy = start_y - state['current_y']
        distance_to_start = math.hypot(dx, dy)
        angle_to_start = math.atan2(dy, dx)
        
        # Calculate heading error
        heading_error = angle_to_start - state['current_theta']
        while heading_error > math.pi:
            heading_error -= 2 * math.pi
        while heading_error < -math.pi:
            heading_error += 2 * math.pi
        
        # Calculate angle deficit (how much we need to turn to complete 360 degrees)
        angle_deficit = 2 * math.pi - state['total_angle']
        
        print(f"  [CLOSURE] Distance to start: {distance_to_start:.1f}m, Heading error: {math.degrees(heading_error):.1f}deg, Angle deficit: {math.degrees(angle_deficit):.1f}deg")
        
        # Strategy: Add corners and straights to navigate back to start
        # We need to balance: 1) Turn to complete 360 degrees, 2) Turn to point at start, 3) Cover remaining distance
        
        if abs(angle_deficit) > 0.1 or distance_to_start > 50:
            # Split the angular deficit into interesting corners
            if abs(angle_deficit) > math.radians(120):
                # Large angle: Create S-bend with 3 alternating corners
                CircuitGenerator._add_straight(int(distance_to_start * 0.15), state)
                CircuitGenerator._add_corner(angle_deficit * 0.35, 110, 50, 0.00009, state)
                
                CircuitGenerator._add_straight(int(distance_to_start * 0.15), state)
                CircuitGenerator._add_corner(angle_deficit * -0.15, 120, 52, 0.00009, state)
                
                CircuitGenerator._add_straight(int(distance_to_start * 0.15), state)
                CircuitGenerator._add_corner(angle_deficit * 0.80, 100, 48, 0.00009, state)
            elif abs(angle_deficit) > math.radians(60):
                # Medium angle: 2-corner S-bend
                CircuitGenerator._add_straight(int(distance_to_start * 0.2), state)
                CircuitGenerator._add_corner(angle_deficit * 0.6, 115, 52, 0.00009, state)
                
                CircuitGenerator._add_straight(int(distance_to_start * 0.2), state)
                CircuitGenerator._add_corner(angle_deficit * 0.4, 125, 54, 0.00009, state)
            else:
                # Small angle: Single corner
                CircuitGenerator._add_straight(int(distance_to_start * 0.3), state)
                CircuitGenerator._add_corner(angle_deficit, 130, 55, 0.00008, state)
            
            # Recalculate position after closure corners
            final_dx = start_x - state['current_x']
            final_dy = start_y - state['current_y']
            final_angle = math.atan2(final_dy, final_dx)
            final_heading_error = final_angle - state['current_theta']
            
            while final_heading_error > math.pi:
                final_heading_error -= 2 * math.pi
            while final_heading_error < -math.pi:
                final_heading_error += 2 * math.pi
            
            # Iteratively refine closure - CORNERS ONLY to avoid overshooting
            # Stop if gap starts increasing (diverging)
            max_iterations = 12
            prev_gap = float('inf')
            for iteration in range(max_iterations):
                # Recalculate where we are relative to start
                gap_dx = start_x - state['current_x']
                gap_dy = start_y - state['current_y']
                gap_dist = math.hypot(gap_dx, gap_dy)
                gap_angle = math.atan2(gap_dy, gap_dx)
                gap_heading_error = gap_angle - state['current_theta']
                
                while gap_heading_error > math.pi:
                    gap_heading_error -= 2 * math.pi
                while gap_heading_error < -math.pi:
                    gap_heading_error += 2 * math.pi
                
                print(f"  [CLOSURE ITER {iteration}] Gap: {gap_dist:.1f}m, Heading error: {math.degrees(gap_heading_error):.1f}deg")
                
                # STOP if gap is increasing (diverging)
                if gap_dist > prev_gap * 1.2:
                    print(f"  [CLOSURE ITER {iteration}] DIVERGING - stopping iterations (gap increased from {prev_gap:.1f}m to {gap_dist:.1f}m)")
                    break
                
                # Convergence check: if gap is small AND heading is reasonable, stop
                # Combined condition prevents risky corrections that could flip heading
                # Tighter thresholds when gap is very small to avoid heading flips
                heading_error_deg = abs(math.degrees(gap_heading_error))
                if gap_dist < 100 and heading_error_deg < 20:
                    print(f"  [CLOSURE ITER {iteration}] GOOD ENOUGH - gap={gap_dist:.1f}m, heading={heading_error_deg:.1f}deg - final straight will handle it")
                    break
                if gap_dist < 200 and heading_error_deg < 25:
                    print(f"  [CLOSURE ITER {iteration}] GOOD ENOUGH - gap={gap_dist:.1f}m, heading={heading_error_deg:.1f}deg - final straight will handle it")
                    break
                
                # PROPORTIONAL CORRECTION based on BOTH gap distance AND heading error
                # Key insight: if heading is already good, be MORE conservative with corrections
                
                # Base correction factor on gap distance
                if gap_dist > 300:
                    base_factor = 0.6
                elif gap_dist > 150:
                    base_factor = 0.45
                elif gap_dist > 75:
                    base_factor = 0.3
                else:
                    base_factor = 0.2
                
                # REDUCE correction if heading error is small (already pointing the right way)
                if heading_error_deg < 5:
                    correction_factor = base_factor * 0.3  # Very gentle - heading is good
                elif heading_error_deg < 15:
                    correction_factor = base_factor * 0.5  # Gentle - heading is decent
                elif heading_error_deg < 30:
                    correction_factor = base_factor * 0.7  # Moderate
                else:
                    correction_factor = base_factor  # Full correction - heading is bad
                
                # Add corner to correct heading
                if abs(gap_heading_error) > math.radians(1):
                    CircuitGenerator._add_corner(gap_heading_error * correction_factor, 180, 60, 0.00006, state)
                
                prev_gap = gap_dist
            
            # Final straight to close remaining gap (NO FINAL CORNER - that made it worse)
            final_gap_dist = math.hypot(start_x - state['current_x'], start_y - state['current_y'])
            print(f"  [CLOSURE FINAL] Gap before final straight: {final_gap_dist:.1f}m")
            
            if final_gap_dist > 2:
                # Add slightly more than the gap to ensure closure
                CircuitGenerator._add_straight(int(final_gap_dist) + 5, state)
        
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
            segments.append(TrackPoint(s, state['current_x'], state['current_y'], state['current_theta'], 0))
        state['current_s'] += length
    
    @staticmethod
    def _add_corner(target_angle, radius, clothoid_len, k_clothoid, state):
        entry_start = state['current_theta']
        sign = 1 if target_angle > 0 else -1
        
        CircuitGenerator._add_clothoid(clothoid_len, k_clothoid, sign, state, reverse=False)
        arc_angle = target_angle - 2 * (state['current_theta'] - entry_start)
        CircuitGenerator._add_arc(arc_angle, radius, sign, state)
        CircuitGenerator._add_clothoid(clothoid_len, k_clothoid, sign, state, reverse=True)
        
        state['total_angle'] += target_angle
    
    @staticmethod
    def _add_clothoid(clothoid_len, k_clothoid, sign, state, reverse):
        segments = state['segments']
        for i in range(clothoid_len):
            curvature = k_clothoid * (clothoid_len - i if reverse else i) * sign
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
        if not segments or 'target_length_m' not in state:
            return
        
        target_length = state['target_length_m']
        actual_length = state['current_s']
        
        if actual_length == 0:
            return
        
        scale_factor = target_length / actual_length
        print(f"  [RESCALE] Adjusting track length from {actual_length:.0f}m to {target_length:.0f}m (scale: {scale_factor:.3f})")
        
        # Rescale all arc-length values
        for segment in segments:
            segment.s = segment.s * scale_factor
        
        # Update state to reflect new length
        state['current_s'] = target_length
    
    @staticmethod
    def _finalize_circuit(segments):
        """Scale and center the circuit."""
        if not segments:
            return
        
        # Verify closure
        start_x, start_y = segments[0].x, segments[0].y
        end_x, end_y = segments[-1].x, segments[-1].y
        gap = math.hypot(end_x - start_x, end_y - start_y)
        print(f"  [FINALIZE] Track closure gap: {gap:.1f}m (should be near 0)")
        
        # Scale and center for display
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
        
        print(f"  [FINALIZE] Track scaled and centered: {len(segments)} points")


class TrackWidget(QWidget):
    """Widget displaying the racing circuit and cars."""
    
    def __init__(self, track_points: List[TrackPoint], track_length: float):
        super().__init__()
        self.track_points = track_points
        self.track_length = track_length
        self.cars: List[Car] = []
        self.setMinimumSize(1400, 900)
        self.race_active = False
        self.start_time = 0.0
        
        
        # Camera settings
        self.camera_mode = 'full'
        self.follow_car_id = None
        self.camera_zoom = 1.0
        self.camera_x = 0
        self.camera_y = 0
        self.camera_rotation = 0
        
        # Animation timer for smooth movement
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_cars)
        self.animation_timer.setInterval(16)  # ~60 FPS
    
    def set_camera_mode(self, mode: str, follow_car_id: Optional[int] = None):
        """Set camera mode and target car."""
        self.camera_mode = mode
        self.follow_car_id = follow_car_id
        if mode == 'full':
            self.camera_zoom = 1.0
            self.camera_rotation = 0
        else:
            self.camera_zoom = 3.0
        self.update()
    
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
        self.animation_timer.start()
    
    def stop_animation(self):
        """Stop animation."""
        self.race_active = False
        self.animation_timer.stop()
    
    def update_car_position(self, driver_id: int, lap: int, position: int, total_time: float):
        """Update specific car position based on simulation data (legacy method)."""
        for car in self.cars:
            if car.driver_id == driver_id:
                # Ensure lap is 1-based for UI consistency
                car.lap = max(1, int(lap))
                car.total_time = total_time
                
                # Calculate average lap time
                if lap > 0:
                    car.avg_lap_time = total_time / lap
                
                # Calculate position based on total time and track length
                if car.avg_lap_time > 0:
                    laps_completed = total_time / car.avg_lap_time
                    car.s = (laps_completed * self.track_length) % self.track_length
                
                car.last_lap = lap
                break
    
    def update_car_realtime(self, driver_id: int, position_m: float, lap: int, velocity_mps: float):
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
        # === SAFETY CHECK 1: Widget may have been deleted/closed ===
        try:
            if not self.isVisible():
                return  # Window was closed, stop updating
        except RuntimeError:
            # Widget has been deleted from memory
            return
        
        # === DEBUG: Track zero velocity (cars stopping) ===
        if velocity_mps < 0.1:
            print(f"WARNING: Car {driver_id} has near-zero velocity: {velocity_mps:.2f} m/s at pos={position_m:.1f}m, lap={lap}")
        
        # === SAFETY CHECK 2: Required attributes exist ===
        if not hasattr(self, 'cars') or not self.cars or not hasattr(self, 'track_points'):
            return
        
        # === FIND AND UPDATE THE MATCHING CAR ===
        car_found = False
        for car in self.cars:
            if car.driver_id == driver_id:
                car_found = True
                
                # === POSITION MAPPING: Engine -> Visual Track ===
                # The engine uses absolute position (meters from race start)
                # The visual track is circular (0 to track_length)
                # Arc-length directly maps to track point index (1m = 1 point)
                if self.track_length > 0 and len(self.track_points) > 0:
                    # Wrap position to track length (NO TELEPORTATION)
                    normalized_pos = position_m % self.track_length
                    
                    # Direct arc-length to index mapping
                    idx = int(normalized_pos)
                    idx = max(0, min(idx, len(self.track_points) - 1))
                    
                    # Store previous position to calculate actual movement direction
                    if not hasattr(car, 'prev_s') or car.prev_s is None:
                        car.prev_s = normalized_pos
                    
                    # Update position
                    car.s = normalized_pos
                    
                    # Track movement direction for rotation
                    prev_s = car.prev_s if car.prev_s is not None else normalized_pos
                    car.movement_direction = normalized_pos - prev_s
                    # Handle wrap-around
                    if car.movement_direction < -self.track_length / 2:
                        car.movement_direction += self.track_length
                    elif car.movement_direction > self.track_length / 2:
                        car.movement_direction -= self.track_length
                    
                    car.prev_s = normalized_pos
                else:
                    # Fallback if track not loaded
                    car.s = position_m
                
                # Update car state
                # Ensure lap is 1-based for UI consistency
                car.lap = max(1, int(lap))
                car.velocity_mps = velocity_mps
                
                # === DEBUG TRACKING: Monitor which cars are updating ===
                if not hasattr(self, '_update_count'):
                    self._update_count = {}
                self._update_count[driver_id] = self._update_count.get(driver_id, 0) + 1
                
                # Log every 60 frames (2 seconds at 30 FPS)
                if self._update_count[driver_id] % 60 == 0:
                    print(f"  [CAR UPDATE] {car.driver_name} (ID:{driver_id}): "
                          f"{self._update_count[driver_id]} updates received, "
                          f"position={car.s:.1f}m, lap={lap}")
                break
        
        if not car_found:
            print(f"  [ERROR] update_car_realtime: Unknown driver_id={driver_id}")
        
        # Trigger repaint
        self.update()
    
    def _animate_cars(self):
        """Smoothly update car positions based on simulation time - just trigger repaint."""
        if not self.race_active:
            return
        
        self.update()
    
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
            
            # GRASS BACKGROUND
            painter.fillRect(self.rect(), QColor(34, 139, 34))  # Forest green
            
            # Center point for transformations
            center_x = self.width() // 2
            center_y = self.height() // 2
            
            # Save painter state
            painter.save()
            
            # Camera transform
            if self.camera_mode == 'follow' and self.follow_car_id:
                # Find followed car
                followed_car = None
                for car in self.cars:
                    if car.driver_id == self.follow_car_id:
                        followed_car = car
                        break
                
                if followed_car and len(self.track_points) > 0:
                    # Get car position - use binary search like _draw_cars does
                    normalized_s = followed_car.s % self.track_length
                    left, right = 0, len(self.track_points) - 1
                    while left < right:
                        mid = (left + right) // 2
                        if self.track_points[mid].s < normalized_s:
                            left = mid + 1
                        else:
                            right = mid
                    idx = max(0, min(left, len(self.track_points) - 1))
                    pt = self.track_points[idx]
                    
                    # CORRECT TRANSFORM ORDER FOR FOLLOW CAMERA:
                    # 1. Translate viewport center to canvas origin
                    # 2. Rotate based on car heading direction (track angle)
                    # 3. Scale (flip Y for screen coords)
                    # 4. Translate world so car is at origin
                    painter.translate(center_x, center_y)
                    painter.rotate(math.degrees(pt.theta))  # Rotate track ahead to "up" on screen
                    painter.scale(self.camera_zoom, -self.camera_zoom)  # Zoom and flip Y
                    painter.translate(-pt.x, -pt.y)  # Center on car position
                else:
                    # Fallback to full view
                    painter.translate(center_x, center_y)
                    painter.scale(1, -1)
            else:
                # Full track view with increased zoom
                painter.translate(center_x, center_y)
                painter.scale(1.5, -1.5)  # Reduced to 1.5x for better overview
            
            # CORRECT LAYER ORDER for visibility
            self._draw_runoff_areas(painter)  # Layer 2
            self._draw_grandstands(painter)    # Layer 3
            self._draw_garages(painter)        # Layer 4
            self._draw_pit_lane(painter)       # Layer 5
            self._draw_track(painter)          # Layers 6-12
            self._draw_cars(painter)           # Layer 13
            
            painter.restore()
            painter.end()
        except Exception as e:
            print(f"ERROR in paintEvent: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def _draw_pit_lane(self, painter):
        """Draw professional pit lane with boxes, entry/exit zones."""
        try:
            if not self.track_points:
                return
            
            from PyQt6.QtGui import QPolygonF
            
            # Build pit lane as filled polygon (s=0 to 300m)
            pit_inner_points = []  # 22m offset from centerline
            pit_outer_points = []  # 40m offset (18m wide pit lane)
            
            for pt in self.track_points:
                if pt.s < 300:
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    
                    inner_x = pt.x + normal_x * 22
                    inner_y = pt.y + normal_y * 22
                    outer_x = pt.x + normal_x * 40
                    outer_y = pt.y + normal_y * 40
                    
                    pit_inner_points.append((inner_x, inner_y))
                    pit_outer_points.append((outer_x, outer_y))
            
            # Draw filled polygon
            polygon = QPolygonF()
            for pt in pit_inner_points:
                polygon.append(QPointF(pt[0], pt[1]))
            for pt in reversed(pit_outer_points):
                polygon.append(QPointF(pt[0], pt[1]))
            
            painter.setBrush(QBrush(QColor(110, 110, 110)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(polygon)
            
            # Pit wall (inner edge)
            painter.setPen(QPen(QColor(80, 80, 80), 2))
            for i in range(len(pit_inner_points) - 1):
                painter.drawLine(
                    int(pit_inner_points[i][0]), int(pit_inner_points[i][1]),
                    int(pit_inner_points[i+1][0]), int(pit_inner_points[i+1][1])
                )
            
            # Pit boxes (10 boxes, 20m each, s=50 to 250)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            for box_idx in range(10):
                box_s = 50 + box_idx * 20
                # Find points at box start and end
                for i, pt in enumerate(self.track_points):
                    if abs(pt.s - box_s) < 2:
                        normal_x = -math.sin(pt.theta)
                        normal_y = math.cos(pt.theta)
                        
                        # Draw box rectangle rotated to track angle
                        painter.save()
                        painter.translate(pt.x + normal_x * 31, pt.y + normal_y * 31)
                        painter.rotate(math.degrees(pt.theta))
                        painter.drawRect(-10, -8, 20, 16)
                        painter.restore()
                        break
            
            # Pit entry chevrons (s=250-270)
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            for stripe_idx in range(8):
                stripe_s = 250 + stripe_idx * 2.5
                for pt in self.track_points:
                    if abs(pt.s - stripe_s) < 1:
                        normal_x = -math.sin(pt.theta)
                        normal_y = math.cos(pt.theta)
                        # Diagonal stripe from track edge to pit lane
                        painter.drawLine(
                            int(pt.x + normal_x * 14), int(pt.y + normal_y * 14),
                            int(pt.x + normal_x * 26), int(pt.y + normal_y * 26)
                        )
                        break
            
            # Pit exit green light marker (s=285)
            for pt in self.track_points:
                if abs(pt.s - 285) < 2:
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    painter.setBrush(QBrush(QColor(0, 255, 0)))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(QPointF(pt.x + normal_x * 31, pt.y + normal_y * 31), 3, 3)
                    break
            
        except Exception:
            pass

    def _draw_grandstands(self, painter):
        """Draw professional 3D grandstands facing the track."""
        try:
            if not self.track_points:
                return
            
            # Main straight grandstands (s=320, 380, 440 - left side)
            grandstand_positions = [320, 380, 440]
            
            for gs_s in grandstand_positions:
                for pt in self.track_points:
                    if abs(pt.s - gs_s) < 2:
                        normal_x = -math.sin(pt.theta)
                        normal_y = math.cos(pt.theta)
                        
                        gs_x = pt.x - normal_x * 40  # LEFT side of track
                        gs_y = pt.y - normal_y * 40
                        
                        painter.save()
                        painter.translate(gs_x, gs_y)
                        painter.rotate(math.degrees(pt.theta) + 90)  # Face track
                        
                        # Tier 1: Ground level (concrete base)
                        painter.setBrush(QBrush(QColor(100, 100, 100)))
                        painter.setPen(QPen(QColor(80, 80, 80), 1))
                        painter.drawRect(-20, 0, 40, 10)
                        
                        # Tier 2: Lower seating (blue)
                        painter.setBrush(QBrush(QColor(60, 100, 180)))
                        painter.setPen(QPen(QColor(50, 80, 150), 1))
                        painter.drawRect(-19, -5, 38, 8)
                        
                        # Tier 3: Middle seating (lighter blue)
                        painter.setBrush(QBrush(QColor(80, 120, 200)))
                        painter.setPen(Qt.PenStyle.NoPen)
                        painter.drawRect(-18, -10, 36, 8)
                        
                        # Tier 4: Upper seating (lightest blue)
                        painter.setBrush(QBrush(QColor(100, 140, 220)))
                        painter.drawRect(-17, -15, 34, 6)
                        
                        # Roof structure (overhangs)
                        painter.setBrush(QBrush(QColor(200, 200, 200)))
                        painter.setPen(QPen(QColor(180, 180, 180), 1))
                        painter.drawRect(-22, -20, 44, 3)
                        
                        # Support columns (4 pillars)
                        painter.setPen(QPen(QColor(90, 90, 90), 3))
                        for pillar_x in [-18, -6, 6, 18]:
                            painter.drawLine(pillar_x, -17, pillar_x, 10)
                        
                        # Seating rows (horizontal detail lines)
                        painter.setPen(QPen(QColor(40, 70, 140), 1))
                        for row_offset in [-13, -11, -9, -7, -3, -1, 1, 3]:
                            painter.drawLine(-18, row_offset, 18, row_offset)
                        
                        painter.restore()
                        break
            
            # Corner grandstands (smaller, at high curvature points)
            for i, pt in enumerate(self.track_points):
                if abs(pt.curvature) > 0.006 and i % 50 == 0:
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    
                    # Position on inside of corner
                    if pt.curvature > 0:
                        gs_x = pt.x - normal_x * 35
                        gs_y = pt.y - normal_y * 35
                    else:
                        gs_x = pt.x + normal_x * 35
                        gs_y = pt.y + normal_y * 35
                    
                    painter.save()
                    painter.translate(gs_x, gs_y)
                    painter.rotate(math.degrees(pt.theta) + 90)
                    
                    # Smaller 3-tier grandstand
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
            
        except Exception:
            pass

    def _draw_garages(self, painter):
        """Draw continuous professional paddock garage building."""
        try:
            if not self.track_points:
                return
            
            # Continuous building structure (s=10 to 280m)
            # Layer 1: Building base segments
            painter.setBrush(QBrush(QColor(140, 140, 140)))
            painter.setPen(QPen(QColor(120, 120, 120), 1))
            
            for i, pt in enumerate(self.track_points):
                if 10 < pt.s < 280 and i % 3 == 0:
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    
                    painter.save()
                    painter.translate(pt.x + normal_x * 50, pt.y + normal_y * 50)
                    painter.rotate(math.degrees(pt.theta))
                    painter.drawRect(-6, 0, 12, 25)
                    painter.restore()
            
            # Layer 2: Team garage bays (10 bays)
            team_colors = [
                QColor(6, 0, 239),    # Blue
                QColor(0, 210, 190),  # Teal
                QColor(220, 0, 0),    # Red
                QColor(245, 150, 0),  # Orange
                QColor(0, 144, 255),  # Light Blue
                QColor(182, 186, 189),# Silver
                QColor(53, 140, 117), # Green
                QColor(201, 45, 75),  # Pink
                QColor(255, 220, 0),  # Yellow
                QColor(100, 100, 100) # Grey
            ]
            
            for bay_idx in range(10):
                bay_s = 20 + bay_idx * 26
                for pt in self.track_points:
                    if abs(pt.s - bay_s) < 2:
                        normal_x = -math.sin(pt.theta)
                        normal_y = math.cos(pt.theta)
                        
                        painter.save()
                        painter.translate(pt.x + normal_x * 50, pt.y + normal_y * 50)
                        painter.rotate(math.degrees(pt.theta))
                        
                        # Roof (light grey overhang)
                        painter.setBrush(QBrush(QColor(180, 180, 180)))
                        painter.setPen(Qt.PenStyle.NoPen)
                        painter.drawRect(-15, -2, 30, 29)
                        
                        # Three garage door openings
                        painter.setBrush(QBrush(QColor(40, 40, 40)))
                        for door in range(3):
                            painter.drawRect(-11 + door * 7, 5, 6, 18)
                        
                        # Team color panel above doors
                        painter.setBrush(QBrush(team_colors[bay_idx]))
                        painter.drawRect(-12, 1, 24, 3)
                        
                        painter.restore()
                        break
            
        except Exception:
            pass

    def _draw_track(self, painter):
        """Draw track with professional surface, smooth kerbs, checkered start/finish."""
        try:
            if not self.track_points or len(self.track_points) < 2:
                return
            
            TRACK_WIDTH = 14  # Half-width of track surface
            
            # Build centerline path
            centerline = QPainterPath()
            centerline.moveTo(self.track_points[0].x, self.track_points[0].y)
            
            for i in range(1, len(self.track_points)):
                pt = self.track_points[i]
                centerline.lineTo(pt.x, pt.y)
            
            centerline.lineTo(self.track_points[0].x, self.track_points[0].y)

            # === Infield fill: match outer grass and add water pool ===
            try:
                from PyQt6.QtGui import QPolygonF
                infield_points = []
                for pt in self.track_points:
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    # Move inward from centerline towards infield by TRACK_WIDTH - 2
                    ix = pt.x - normal_x * (TRACK_WIDTH - 2)
                    iy = pt.y - normal_y * (TRACK_WIDTH - 2)
                    infield_points.append(QPointF(ix, iy))

                if infield_points:
                    poly = QPolygonF(infield_points)
                    # Fill with same forest green as background
                    painter.setBrush(QBrush(QColor(34, 139, 34)))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawPolygon(poly)

                    # Add a water pool matching the infield shape (scaled down), rotated clockwise 20°
                    cx = sum(p.x() for p in infield_points) / len(infield_points)
                    cy = sum(p.y() for p in infield_points) / len(infield_points)
                    scale = 0.6  # scale down the infield polygon to make the pool
                    raw_poly = []
                    for p in infield_points:
                        sx = cx + (p.x() - cx) * scale
                        sy = cy + (p.y() - cy) * scale
                        raw_poly.append((sx, sy))

                    # Rotate polygon clockwise by 20 degrees (clockwise -> negative angle)
                    rot_rad = math.radians(-20)
                    cos_t = math.cos(rot_rad)
                    sin_t = math.sin(rot_rad)
                    pool_poly = QPolygonF()
                    for (sx, sy) in raw_poly:
                        dx = sx - cx
                        dy = sy - cy
                        rx = cx + (dx * cos_t - dy * sin_t)
                        ry = cy + (dx * sin_t + dy * cos_t)
                        pool_poly.append(QPointF(rx, ry))

                    # Use requested water color #006994 (deeper, realistic) and darker edge
                    water_color = QColor("#006994")
                    water_edge = QColor("#004A66")
                    painter.setBrush(QBrush(water_color))
                    painter.setPen(QPen(water_edge, 2))
                    painter.drawPolygon(pool_poly)

                    # Small specular highlight near upper-left of pool (relative)
                    if len(pool_poly) > 0:
                        hp = pool_poly[int(len(pool_poly) * 0.22)]
                        painter.setBrush(QBrush(QColor(255, 255, 255, 140)))
                        painter.setPen(Qt.PenStyle.NoPen)
                        painter.drawEllipse(QPointF(hp.x() + 8, hp.y() + 6), 14, 7)
            except Exception:
                pass

            # LAYER 6: Base track surface (lighter grey off-line)
            painter.setPen(QPen(QColor(85, 85, 85), TRACK_WIDTH * 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(centerline)
            
            # LAYER 7: Racing line (darker worn surface)
            painter.setPen(QPen(QColor(45, 45, 45), TRACK_WIDTH * 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(centerline)
            
            # LAYER 9: Track edges (clean white lines)
            painter.setPen(QPen(QColor(240, 240, 240), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for i in range(0, len(self.track_points) - 1):
                pt = self.track_points[i]
                next_pt = self.track_points[i + 1]
                normal_x = -math.sin(pt.theta)
                normal_y = math.cos(pt.theta)
                next_normal_x = -math.sin(next_pt.theta)
                next_normal_y = math.cos(next_pt.theta)
                # Left edge
                painter.drawLine(
                    int(pt.x - normal_x * TRACK_WIDTH), int(pt.y - normal_y * TRACK_WIDTH),
                    int(next_pt.x - next_normal_x * TRACK_WIDTH), int(next_pt.y - next_normal_y * TRACK_WIDTH)
                )
                # Right edge
                painter.drawLine(
                    int(pt.x + normal_x * TRACK_WIDTH), int(pt.y + normal_y * TRACK_WIDTH),
                    int(next_pt.x + next_normal_x * TRACK_WIDTH), int(next_pt.y + next_normal_y * TRACK_WIDTH)
                )
            
            # LAYER 10: SMOOTH STRIPED KERBS on INSIDE (apex)
            # Build continuous kerb paths for each corner
            current_corner = []
            in_corner = False
            
            for i, pt in enumerate(self.track_points):
                if abs(pt.curvature) > 0.003:
                    current_corner.append(pt)
                    in_corner = True
                elif in_corner and len(current_corner) > 5:
                    # Draw smooth kerb for this corner
                    first_curv = current_corner[0].curvature
                    kerb_offset = 12  # Inside edge
                    
                    segment_length = 0
                    stripe_toggle = True
                    
                    for j in range(len(current_corner) - 1):
                        pt = current_corner[j]
                        next_pt = current_corner[j + 1]
                        
                        normal_x = -math.sin(pt.theta)
                        normal_y = math.cos(pt.theta)
                        next_normal_x = -math.sin(next_pt.theta)
                        next_normal_y = math.cos(next_pt.theta)
                        
                        # Calculate segment distance
                        dx = next_pt.x - pt.x
                        dy = next_pt.y - pt.y
                        dist = math.sqrt(dx*dx + dy*dy)
                        segment_length += dist
                        
                        # Toggle stripe every 5m
                        if segment_length > 5:
                            stripe_toggle = not stripe_toggle
                            segment_length = 0
                        
                        color = QColor(221, 45, 74) if stripe_toggle else QColor(255, 255, 255)
                        painter.setPen(QPen(color, 4))
                        
                        if first_curv > 0:  # Left turn - kerb on LEFT
                            painter.drawLine(
                                int(pt.x - normal_x * kerb_offset),
                                int(pt.y - normal_y * kerb_offset),
                                int(next_pt.x - next_normal_x * kerb_offset),
                                int(next_pt.y - next_normal_y * kerb_offset)
                            )
                        else:  # Right turn - kerb on RIGHT
                            painter.drawLine(
                                int(pt.x + normal_x * kerb_offset),
                                int(pt.y + normal_y * kerb_offset),
                                int(next_pt.x + next_normal_x * kerb_offset),
                                int(next_pt.y + next_normal_y * kerb_offset)
                            )
                    
                    current_corner = []
                    in_corner = False
            
            # LAYER 11: Centerline (subtle dashed)
            painter.setPen(QPen(QColor(200, 200, 200), 0.5, Qt.PenStyle.DashLine))
            painter.drawPath(centerline)
            
            # LAYER 12: START/FINISH LINE at s=0 (proper checkered flag)
            for pt in self.track_points:
                if pt.s < 5:  # At start of lap
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    
                    painter.save()
                    # Move the finish line to the right of the screen (world +X) by 200 units
                    # and rotate it 90 degrees relative to the track heading so it appears perpendicular
                    painter.translate(pt.x + 200, pt.y)
                    painter.rotate(math.degrees(pt.theta) + 90)
                    painter.setPen(Qt.PenStyle.NoPen)
                    
                    # Bold checkered pattern - 8 squares across track width
                    square_size = 3.5
                    for col in range(8):
                        if col % 2 == 0:
                            painter.setBrush(QBrush(QColor(255, 255, 255)))
                        else:
                            painter.setBrush(QBrush(QColor(0, 0, 0)))
                        painter.drawRect(
                            int(col * square_size - TRACK_WIDTH), 
                            int(-square_size), 
                            int(square_size), 
                            int(square_size * 2)
                        )
                    
                    painter.restore()
                    break
            
        except Exception as e:
            print(f"ERROR in _draw_track: {e}")
    
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
                    
                    # Find track point at car's arc-length
                    if self.track_length > 0 and len(self.track_points) > 0:
                        # === STEP 1: MODULO WRAPPING ===
                        # This is CRITICAL for preventing teleportation!
                        # When car.s exceeds track_length, it wraps back to 0
                        # Example: If track is 6000m and car.s = 6100m, normalized_s = 100m
                        normalized_s = car.s % self.track_length
                        
                        # === STEP 2: FIND MATCHING TRACK POINT ===
                        # CRITICAL FIX: Track points were rescaled, so their .s values
                        # don't match array indices. Must search for closest .s value!
                        # Binary search for the track point with .s closest to normalized_s
                        left, right = 0, len(self.track_points) - 1
                        while left < right:
                            mid = (left + right) // 2
                            if self.track_points[mid].s < normalized_s:
                                left = mid + 1
                            else:
                                right = mid
                        
                        idx = left
                        # Safety clamp
                        idx = max(0, min(idx, len(self.track_points) - 1))
                        pt = self.track_points[idx]
                        
                        # === STEP 3: LATERAL POSITIONING (SIDE-BY-SIDE RACING) ===
                        # Spread cars across track width to simulate racing lines
                        # Grid position determines if car is on left or right side of track
                        
                        # Base offset: Grid position (odd = left, even = right)
                        # This creates pairs of cars side-by-side at the start
                        grid_position = car.driver_id % 2  # 0 or 1
                        base_offset = (grid_position - 0.5) * 6  # -3 or +3 pixels
                        
                        # Dynamic offset: Small variation during racing
                        # Much smaller than before to keep cars ON the track
                        lap_progress = (normalized_s / self.track_length)
                        dynamic_offset = math.sin(lap_progress * 6 * math.pi + car.driver_id * 0.7) * 2
                        
                        total_lateral_offset = base_offset + dynamic_offset
                        
                        # === STEP 4: CALCULATE PERPENDICULAR OFFSET ===
                        # Track angle (theta) points along the track direction
                        # To move sideways, we rotate 90 degrees (pi/2 radians)
                        track_angle = pt.theta
                        offset_x = pt.x + total_lateral_offset * math.cos(track_angle + math.pi/2)
                        offset_y = pt.y + total_lateral_offset * math.sin(track_angle + math.pi/2)
                        
                        # === STEP 5: DRAW CAR (actual 5m length) ===
                        # Calculate rotation based on ACTUAL MOVEMENT, not just track angle
                        if hasattr(car, 'movement_direction') and abs(car.movement_direction) > 0.1:
                            # Car is moving - use direction of motion
                            # Positive movement = forward, negative = backward (shouldn't happen)
                            movement_angle = track_angle if car.movement_direction > 0 else track_angle + math.pi
                        else:
                            # Car stationary - use track direction
                            movement_angle = track_angle
                        
                        car_length = 5.0  # 5 meters
                        car_width = 2.0   # 2 meters
                        
                        painter.setBrush(QBrush(car.color))
                        painter.setPen(QPen(Qt.GlobalColor.white, 1))
                        
                        # Draw rectangle oriented to movement direction
                        painter.save()
                        painter.translate(offset_x, offset_y)
                        painter.rotate(math.degrees(movement_angle))  # Rotate to MOVEMENT direction (reversed)
                        painter.drawRect(int(-car_length/2), int(-car_width/2), 
                                        int(car_length), int(car_width))
                        painter.restore()
                        cars_drawn += 1
                except Exception as e:
                    print(f"ERROR drawing car {car.driver_id} (s={car.s:.1f}): {e}")
            
            # Debug: Print if not all cars are being drawn
            if cars_drawn < len([c for c in self.cars if not c.dnf]):
                active_cars = len([c for c in self.cars if not c.dnf])
                print(f"WARNING: Only drew {cars_drawn}/{active_cars} active cars")
        except Exception as e:
            print(f"ERROR in _draw_cars: {e}")


class RaceWindow(QMainWindow):
    """Main race window with track display and controls."""
    
    # Signals
    return_to_menu = pyqtSignal()  # Signal to return to main menu
    
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Momentum - Race Visualization")
            # Display mode (default: borderless)
            self.display_mode = "borderless"
            # Borderless windowed fullscreen
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            screen_obj = QApplication.primaryScreen()
            screen = screen_obj.geometry() if screen_obj else None
            if screen is not None:
                self.setGeometry(screen)
            self.showMaximized()
            # Race state
            self.db: Optional[DatabaseManager] = None
            self.drivers = []
            self.track = None
            self.race_thread: Optional[threading.Thread] = None
            self.stop_event: Optional[threading.Event] = None
            self.driver_lap_times: Dict[int, float] = {}  # Track last lap time per driver
            self.race_start_time: float = 0.0
            self.driver_colours: Dict[int, QColor] = {}  # Mapping of driver IDs to car colours
            self._driver_push_intensity: Dict[int, float] = {}  # Mapping of driver IDs to push intensity
            
            # Player control
            self.player_driver_id: Optional[int] = None
            self.player_overrides: Dict[str, float] = {'pace': 0.7, 'overtake': 0.5}  # pace: 0.5-1.0, overtake: 0.0-1.0
            self.tuning_preset: str = 'balanced'  # Simulation tuning preset
            
            # Player telemetry tracking
            self.player_telemetry = {
                'speed_kph': 0.0,
                'push_intensity': 0.7,
                'push_fatigue': 0.0,
                'tire_condition': 1.0
            }
            
            # Camera mode
            self.camera_mode = 'full'  # 'full' or 'follow'
            
            # Event emitter
            self.emitter = EventEmitter()
            self.emitter.position_update.connect(self._on_position_update)
            self.emitter.race_finished.connect(self._on_race_finished)
            self.emitter.event_signal.connect(self._on_event)
            self._setup_ui()
            self._load_data()
            # No auto-start: user must click Start Race manually
            print("[INFO] GUI ready - click Start Race when ready")
        except Exception as e:
            import traceback
            print("[ERROR] Exception in RaceWindow.__init__:", e)
            traceback.print_exc()
            raise

    # Auto-start logic removed: user must click Start Race manually
    
    def _setup_ui(self):
        """Setup user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Left: Track display (MUCH BIGGER)
        self.track_widget = None  # Will be created after track loads
        left_container = QWidget()
        self.left_layout = QVBoxLayout(left_container)
        self.left_layout.addWidget(QLabel("Loading track..."))
        layout.addWidget(left_container, 5)  # Was 3, now 5 for bigger track
        
        # Right: Controls and standings
        right_panel = QVBoxLayout()
        
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
        pace_label_top.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
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
        self.pace_slider.setValue(50)  # Set value AFTER connecting signal to trigger initial styling
        
        pace_hint = QLabel("Conservative ← → Aggressive")
        pace_hint.setStyleSheet("font-size: 10px;")
        pace_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_layout.addWidget(pace_hint)
        
        player_layout.addSpacing(10)
        
        # Overtake aggressiveness
        overtake_label_top = QLabel("Overtaking: Moderate (50%)")
        overtake_label_top.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
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
        self.overtake_slider.setValue(50)  # Set value AFTER connecting signal to trigger initial styling
        
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
        self.speed_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
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
        self.player_status_label.setStyleSheet("font-size: 18px; color: #FF4444; font-weight: 900;")
        self.player_status_label.hide()
        telemetry_layout.addWidget(self.player_status_label)
        
        right_panel.addWidget(telemetry_group)
        
        # Camera controls
        camera_group = QGroupBox("Camera")
        camera_layout = QHBoxLayout(camera_group)
        self.camera_full_btn = QPushButton("Full Track")
        self.camera_full_btn.clicked.connect(lambda: self._set_camera_mode('full'))
        self.camera_follow_btn = QPushButton("Follow Car")
        self.camera_follow_btn.clicked.connect(lambda: self._set_camera_mode('follow'))
        camera_layout.addWidget(self.camera_full_btn)
        camera_layout.addWidget(self.camera_follow_btn)
        right_panel.addWidget(camera_group)
        
        # Standings table (MUCH BIGGER)
        right_panel.addWidget(QLabel("<h2>Live Standings</h2>"))
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(4)
        self.standings_table.setHorizontalHeaderLabels(["", "Driver", "Lap", "Gap"])
        self.standings_table.setMinimumWidth(500)
        self.standings_table.setMinimumHeight(400)
        self.standings_table.setColumnWidth(0, 40)  # Color indicator
        self.standings_table.setColumnWidth(1, 210)  # Driver name
        self.standings_table.setColumnWidth(2, 60)   # Lap
        self.standings_table.setColumnWidth(3, 100)  # Gap
        right_panel.addWidget(self.standings_table, 1)  # Stretch factor 1
        
        layout.addLayout(right_panel, 1)
        
        # Apply dark Momentum palette for race HUD and visuals (restoring darker theme)
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
            # Initialize database
            try:
                from database.database_manager import DatabaseManager
                self.db = DatabaseManager()
            except Exception as e:
                self.info_label.setText(f"Database connection failed: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Database initialization failed: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Load drivers
            try:
                all_drivers = self.db.get_all_drivers()
                if not all_drivers:
                    self.info_label.setText("Error: No drivers in database")
                    self.start_btn.setEnabled(False)
                    print("ERROR: No drivers found in database")
                    return
                
                self.drivers = all_drivers[:10] if len(all_drivers) >= 10 else all_drivers
                
                print(f"Loaded {len(self.drivers)} drivers")
                if self.drivers:
                    print(f"First driver: id={self.drivers[0].id}, name={self.drivers[0].name}")
            except Exception as e:
                self.info_label.setText(f"Failed to load drivers: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Failed to load drivers: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Load track - HARDCODED for now (database track system needs redesign)
            try:
                # Create a simple track object with fields needed by race simulation
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
                
                self.track = SimpleTrack(
                    name="Test Circuit",
                    length_km=4.5
                )
                
                print(f"Loaded track: {self.track.name} ({self.track.length_km:.2f}km)")
            except Exception as e:
                self.info_label.setText(f"Failed to create track: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Failed to create track: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Generate circuit
            try:
                print(f"Generating circuit for {self.track.length_km}km track...")
                track_points = CircuitGenerator.generate(self.track.length_km)
                if not track_points:
                    self.info_label.setText("Error: Failed to generate circuit")
                    self.start_btn.setEnabled(False)
                    print("ERROR: Circuit generation returned empty list")
                    return
                
                # USE DATABASE TRACK LENGTH - this is the authoritative value
                # The generated track points should wrap around this length using modulo
                track_length = self.track.length_km * 1000  # Convert km to meters
                print(f"Generated circuit with {len(track_points)} points, using database length: {track_length:.0f}m")
                
                # Store track_points for passing to engine
                self.track_points = track_points
            except Exception as e:
                self.info_label.setText(f"Circuit generation failed: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Circuit generation failed: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Create track widget
            try:
                self.track_widget = TrackWidget(track_points, track_length)
                
                # Clear loading message and add track widget
                while self.left_layout.count():
                    item = self.left_layout.takeAt(0)
                    if item is None:
                        continue
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                self.left_layout.addWidget(self.track_widget)
                print("Track widget created and added to layout")
            except Exception as e:
                self.info_label.setText(f"Failed to create track display: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Track widget creation failed: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Create cars with grid alignment
            try:
                colours = [
                    QColor(255, 50, 50), QColor(50, 150, 255), QColor(50, 255, 50),
                    QColor(255, 255, 50), QColor(255, 150, 50), QColor(200, 50, 255),
                    QColor(50, 255, 255), QColor(255, 150, 150), QColor(150, 255, 150),
                    QColor(200, 200, 255)
                ]
                
                cars = []
                # Create a mapping of driver IDs to colours for standings table
                self.driver_colours = {}
                
                # Starting grid: Stagger cars along track direction (not side-to-side)
                # Formation: 2 cars per row, 10m spacing between rows
                # Row 1: positions 0, 0 (side by side via lateral offset)
                # Row 2: positions 15, 15
                # Row 3: positions 30, 30, etc.
                for i, driver in enumerate(self.drivers):
                    row = i // 2  # 0,1 -> row 0; 2,3 -> row 1; etc.
                    grid_spacing = 15.0  # meters between rows
                    start_position = row * grid_spacing
                    
                    # Assign colour to this driver
                    car_colour = colours[i % len(colours)]
                    self.driver_colours[driver.id] = car_colour
                    
                    cars.append(Car(
                        driver_id=driver.id,
                        driver_name=driver.name,
                        s=start_position,  # Staggered start positions
                        color=car_colour,
                        total_time=0.0,
                        avg_lap_time=60.0,
                        last_lap=0
                    ))
                
                self.track_widget.set_cars(cars)
                print(f"Created {len(cars)} cars at start line")
                print(f"Car details: {[(c.driver_name, c.driver_id) for c in cars]}")
            except Exception as e:
                self.info_label.setText(f"Failed to create cars: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Car creation failed: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Initialize standings table (row order = position)
            try:
                self.standings_table.setRowCount(len(self.drivers))
                for i, driver in enumerate(self.drivers):
                    driver_name = driver.name
                    print(f"[STANDINGS INIT] Row {i}: Setting driver name to '{driver_name}'")
                    # Column 0: color/position indicator (empty for now)
                    self.standings_table.setItem(i, 0, QTableWidgetItem(""))
                    # Column 1: Driver name
                    self.standings_table.setItem(i, 1, QTableWidgetItem(driver_name))
                    # Column 2: Lap (1-based)
                    self.standings_table.setItem(i, 2, QTableWidgetItem("1"))
                    # Column 3: Gap
                    self.standings_table.setItem(i, 3, QTableWidgetItem("-"))
                print("Standings table initialized")
            except Exception as e:
                print(f"WARNING: Standings table initialization failed: {e}")
                # Non-critical, continue
            
            self.info_label.setText(f"{len(self.drivers)} drivers | {self.track.name} ({self.track.length_km:.2f}km)")
            print("Data loading complete - ready to race")
            
        except Exception as e:
            self.info_label.setText(f"Unexpected error: {e}")
            self.start_btn.setEnabled(False)
            print(f"ERROR: Unexpected error in _load_data: {e}")
            import traceback
            traceback.print_exc()
    
    # _auto_start_race method removed: user must click Start Race manually
    
    def _start_race(self):
        """Start the race simulation."""
        if not self.drivers or not self.track:
            self.info_label.setText("Error: No drivers or track loaded")
            print("ERROR: Cannot start race - no drivers or track")
            return
        
        if not self.track_widget:
            self.info_label.setText("Error: Track display not ready")
            print("ERROR: Cannot start race - track widget not initialized")
            return
        
        print(f"Starting race with {len(self.drivers)} drivers on {self.track.name}")
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.info_label.setText("Race starting... waiting for data")
        # Clear any player RETIRED status from a previous run
        try:
            if hasattr(self, 'player_status_label'):
                self.player_status_label.hide()
        except Exception:
            pass

        # Ensure player controls are enabled at race start (in case they were disabled by a prior DNF)
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
        
        def race_runner():
            try:
                self.stop_event = threading.Event()
                print("Race thread started")
                
                def event_callback(event: dict):
                    try:
                        event_type = event.get("type")
                        
                        if event_type == "position_update":
                            # === AUTO-START ANIMATION ON FIRST DATA ===
                            # Prevents freeze where animation waits for data
                            if not self._animation_started:
                                # Request animation start on the GUI thread via event_signal
                                print("[ANIMATION] First position data received - requesting animation start on main thread")
                                try:
                                    # Emit a simple string command handled by _on_event
                                    self.emitter.event_signal.emit("start_animation")
                                except Exception as e:
                                    print(f"[ERROR] Failed to request animation start: {e}")
                                self._animation_started = True
                                self.info_label.setText("Race in progress...")
                            
                            # Real-time position updates at 30 FPS
                            frame = event.get("frame", 0)
                            race_time = event.get("time", 0.0)
                            positions = event.get("positions", [])
                            
                            # Print status every 30 frames (once per second)
                            if frame % 30 == 0 and positions:
                                print(f"[{race_time:.1f}s] ", end="")
                                for p in positions[:3]:  # Top 3
                                    print(f"P{p['position']}: {p['driver_name']} (L{p['lap']}, {p['racing_mode']}) ", end="")
                                print()
                            
                            # Update all car positions on track AND standings table
                            for pos_data in positions:
                                driver_id = pos_data.get("driver_id") if isinstance(pos_data, dict) else None
                                try:
                                    if driver_id is None:
                                        continue
                                    
                                    # Update player telemetry if this is the player's driver
                                    if driver_id == self.player_driver_id:
                                        velocity_mps = pos_data.get("velocity_mps", 0.0)
                                        push_intensity = pos_data.get("push_intensity", 0.7)
                                        push_fatigue = pos_data.get("push_fatigue", 0.0)
                                        tire_condition = pos_data.get("tire_condition", 1.0)
                                        
                                        self.player_telemetry['speed_kph'] = velocity_mps * 3.6
                                        self.player_telemetry['push_intensity'] = push_intensity
                                        self.player_telemetry['push_fatigue'] = push_fatigue
                                        self.player_telemetry['tire_condition'] = tire_condition
                                        
                                        # Update telemetry display (thread-safe via signal)
                                        self.emitter.event_signal.emit(f"telemetry_update|{velocity_mps * 3.6:.1f}|{push_intensity:.2f}|{push_fatigue:.2f}|{tire_condition:.2f}")
                                    
                                    # Update track widget with position
                                    if self.track_widget and pos_data.get("running", True):
                                        # position_m from engine is already lap-relative (0 to track_length)
                                        # DO NOT subtract lap * track_length (causes negative positions!)
                                        position_m = pos_data.get("position_m", 0.0)
                                        lap = pos_data.get("lap", 0)
                                        velocity_mps = pos_data.get("velocity_mps", 0.0)
                                        
                                        # Update car position
                                        if hasattr(self.track_widget, 'update_car_realtime'):
                                            self.track_widget.update_car_realtime(
                                                driver_id=driver_id,
                                                position_m=position_m,
                                                lap=lap,
                                                velocity_mps=velocity_mps
                                            )
                                        else:
                                            # Fallback to old method
                                            self.track_widget.update_car_position(
                                                driver_id=driver_id,
                                                lap=lap,
                                                position=pos_data.get("position", 1),
                                                total_time=race_time
                                            )
                                    
                                    # Update standings table via signal (thread-safe)
                                    position = pos_data.get("position", 0)
                                    lap = pos_data.get("lap", 0)
                                    push_intensity = pos_data.get("push_intensity", 0.7)
                                    gap_ahead = pos_data.get("gap_ahead", 0.0)
                                    position_m = pos_data.get("position_m", 0.0)
                                    if frame % 30 == 0:  # Update table once per second
                                        # Include timing + position for live gaps and ordering
                                        self.emitter.event_signal.emit(
                                            f"standings_update|{driver_id}|{position}|{lap}|{push_intensity:.2f}|{gap_ahead:.2f}|{position_m:.2f}|{race_time:.2f}"
                                        )
                                        
                                except Exception as e:
                                    print(f"ERROR updating position for driver {driver_id}: {e}")
                        
                        elif event_type == "dnf":
                            driver_id = event.get("driver_id")
                            driver_name = event.get("driver_name", f"Driver {driver_id}")
                            reason = event.get("reason", "unknown")
                            lap = event.get("lap", 0)
                            print(f"[DNF] {driver_name} DNF on lap {lap}: {reason}")
                            
                            # Ask GUI thread to mark DNF (avoid touching widgets from race thread)
                            try:
                                if driver_id is not None:
                                    self.emitter.event_signal.emit(f"mark_dnf|{driver_id}")
                            except Exception:
                                pass

                            # Request GUI thread to show player RETIRED and disable controls
                            try:
                                if driver_id == getattr(self, 'player_driver_id', None):
                                    self.emitter.event_signal.emit(f"player_dnf|{driver_id}|{lap}|{reason}")
                            except Exception:
                                pass
                            # Mark in standings and rebuild table so DNF appears immediately
                            if driver_id is not None:
                                if not hasattr(self, '_race_state'):
                                    self._race_state = {}
                                existing = self._race_state.get(driver_id, {
                                    'name': driver_name,
                                    'position': event.get('position', 0),
                                    'lap': lap,
                                    'time': event.get('race_time', 0.0),
                                    'distance': 0.0,
                                    'gap_ahead': 0.0
                                })
                                existing['dnf'] = True
                                existing['lap'] = lap
                                self._race_state[driver_id] = existing
                                self._rebuild_standings_table()
                        
                        elif event_type == "race_finished":
                            total_laps = event.get("total_laps", 0)
                            race_time = event.get("race_time", 0.0)
                            print(f"\nRace finished! {total_laps} laps in {race_time:.1f}s")
                            
                            # Store collision log for display
                            collision_log = event.get('collision_log', [])
                            self._collision_log = collision_log
                            if collision_log:
                                print(f"Race simulation complete, {len(event.get('results', []))} results, {len(collision_log)} collisions")
                            else:
                                print(f"Race simulation complete, {len(event.get('results', []))} results")

                            # Emit actual results to the GUI if provided by the engine.
                            # Previously this emitted an empty list which left the
                            # standings unpopulated. Use the `results` field from
                            # the event if available, otherwise fall back to an
                            # empty list to avoid exceptions.
                            results_payload = event.get('results') if isinstance(event, dict) else None
                            if results_payload is None:
                                # If the engine didn't include results in the event,
                                # try to use a `results` variable in outer scope if set.
                                results_payload = event.get('results', []) if isinstance(event, dict) else []

                            if hasattr(self.emitter, 'race_finished'):
                                try:
                                    self.emitter.race_finished.emit(results_payload)
                                except Exception as ex:
                                    # Log exception to help debug malformed payloads
                                    print(f"ERROR: failed to emit race_finished with payload type={type(results_payload)}: {ex}")
                                    try:
                                        traceback.print_exc()
                                    except Exception:
                                        pass
                                    # Fallback to empty list to avoid GUI crash
                                    self.emitter.race_finished.emit([])
                    
                    except Exception as e:
                        print(f"ERROR in event_callback: {e}")
                        traceback.print_exc()
                
                print("Starting simulate_race with comprehensive engine via RaceContext...")
                # Get track_points safely
                track_pts = getattr(self, 'track_points', None)

                # Build a minimal teams dictionary if possible (empty dict is acceptable)
                teams = {}
                try:
                    db_any = cast(Any, self.db)
                    get_team_fn = getattr(db_any, 'get_team', None)
                    if callable(get_team_fn):
                        team_ids = {d.current_team_id for d in self.drivers if d.current_team_id}
                        for team_id in team_ids:
                            team = get_team_fn(team_id)
                            if team:
                                teams[team_id] = team
                except Exception:
                    teams = {}

                # Create RaceContext and populate track_conditions for discipline adapter
                context = RaceContext(
                    discipline=RacingDiscipline.SINGLE_SEATER,
                    track=self.track,
                    drivers=self.drivers,
                    teams=teams,
                    total_laps=3,
                    event_callback=event_callback
                )

                # Populate track_conditions keys expected by SingleSeaterEngine
                tc = context.track_conditions
                tc['player_driver_id'] = self.player_driver_id
                tc['player_overrides'] = self.player_overrides
                tc['track_points'] = track_pts
                tc['realtime_speed'] = 5.0
                tc['stop_event'] = self.stop_event
                tc['tuning_preset'] = self.tuning_preset

                results = simulate_race(context=context, verbose=True, db=cast(Any, self.db))
                
                print(f"Race simulation complete, {len(results) if results else 0} results")
                
                # Don't save from race thread - database is in main thread
                # Results will be saved via race_finished event if needed
            
            except Exception as e:
                error_msg = f"Race error: {e}"
                print(f"ERROR in race_runner: {e}")
                import traceback
                traceback.print_exc()
                self.emitter.event_signal.emit(error_msg)
        
        self.race_thread = threading.Thread(target=race_runner, daemon=True)
        self.race_thread.start()
        print("Race thread launched")
    
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
    
    def _on_position_update(self, data: dict):
        """Handle position update from simulation."""
        try:
            if not self.track_widget:
                return
            
            self.track_widget.update_car_position(
                data['driver_id'],
                data['lap'],
                data['position'],
                data['total_time']
            )
            
            # Update standings table: find row by driver id
            for row in range(self.standings_table.rowCount()):
                name_item = self.standings_table.item(row, 1)
                if not name_item:
                    continue
                driver_name = name_item.text()
                driver = next((d for d in self.drivers if d.name == driver_name), None)
                if driver and driver.id == data['driver_id']:
                    # Column 0 = position
                    self.standings_table.setItem(row, 0, QTableWidgetItem(str(data['position'])))
                    # Column 2 = lap
                    self.standings_table.setItem(row, 2, QTableWidgetItem(str(data['lap'])))

                    # Highlight player-controlled driver cell background
                    try:
                        name_cell = self.standings_table.item(row, 1)
                        if driver.id == self.player_driver_id:
                            name_cell.setBackground(QColor(255, 215, 0))  # Gold
                            name_cell.setForeground(QColor(0, 0, 0))  # Dark text on gold
                        else:
                            name_cell.setBackground(QColor(37, 38, 39))  # normal background (dark)
                    except Exception:
                        pass
                    break
        except Exception as e:
            print(f"ERROR in _on_position_update: {e}")
    
    def _on_race_finished(self, results: list):
        """Handle race finish."""
        try:
            print(f"Race finished event received with {len(results)} results")
            
            # Display collision summary if available
            if hasattr(self, '_collision_log') and self._collision_log:
                print(f"\n*** COLLISION SUMMARY ({len(self._collision_log)} incidents) ***")
                for i, collision in enumerate(self._collision_log, 1):
                    print(f"  {i}. Lap {collision.get('lap', '?')}: {collision.get('description', 'Unknown incident')}")
                print("")
            
            self.info_label.setText("Race finished!")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            try:
                if hasattr(self, 'player_status_label'):
                    self.player_status_label.hide()
                    # Re-enable player controls on race finish
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
            except Exception:
                pass
            
            # Stop animation
            if self.track_widget:
                self.track_widget.stop_animation()
            
            # Update final standings
            if not results:
                print("WARNING: No results to display")
                return
            
            results_sorted = sorted(results, key=lambda r: r.get('position', 999))
            leader_time = results_sorted[0].get('time_seconds', 0) if results_sorted else 0
            
            for i, result in enumerate(results_sorted):
                try:
                    driver_id = result.get('driver_id')
                    driver = next((d for d in self.drivers if d.id == driver_id), None)
                    if driver:
                        time_seconds = result.get('time_seconds', 0)
                        gap = time_seconds - leader_time if i > 0 else 0
                        
                        self.standings_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                        self.standings_table.setItem(i, 1, QTableWidgetItem(driver.name))
                        self.standings_table.setItem(i, 3, QTableWidgetItem(f"+{gap:.2f}s" if gap > 0 else "-"))

                        # Highlight player-controlled driver in leaderboard
                        try:
                            name_cell = self.standings_table.item(i, 1)
                            if driver.id == self.player_driver_id:
                                name_cell.setBackground(QColor(255, 215, 0))  # Gold
                                name_cell.setForeground(QColor(0, 0, 0))  # Dark text on gold
                            else:
                                name_cell.setBackground(QColor(37, 38, 39))
                        except Exception:
                            pass
                except Exception as e:
                    print(f"ERROR updating standings row {i}: {e}")
        
        except Exception as e:
            print(f"ERROR in _on_race_finished: {e}")
            import traceback
            traceback.print_exc()
    
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
        # Handle explicit GUI commands first
        if message == "start_animation":
            try:
                if self.track_widget:
                    self.track_widget.start_animation()
                    print("[ANIMATION] Animation timer started (main thread)")
            except Exception as e:
                print(f"ERROR starting animation in GUI thread: {e}")
            return

        # Handle telemetry update
        if message.startswith("telemetry_update|"):
            try:
                parts = message.split("|")
                if len(parts) >= 5:
                    speed_kph = float(parts[1])
                    push_intensity = float(parts[2])
                    push_fatigue = float(parts[3])
                    tire_condition = float(parts[4])
                    
                    # Update speed label
                    self.speed_label.setText(f"Speed: {speed_kph:.0f} km/h")
                    
                    # Update push gauge
                    push_percent = int(push_intensity * 100)
                    self.push_gauge.setValue(push_percent)
                    
                    # Update fatigue label with color warning
                    fatigue_percent = int(push_fatigue * 100)
                    self.fatigue_label.setText(f"Fatigue: {fatigue_percent}%")
                    if push_fatigue > 0.7:
                        self.fatigue_label.setStyleSheet("font-size: 14px; color: #DD2D4A; font-weight: bold;")
                    elif push_fatigue > 0.4:
                        self.fatigue_label.setStyleSheet("font-size: 14px; color: #DD2D4A; font-weight: normal;")
                    else:
                        self.fatigue_label.setStyleSheet("font-size: 14px; color: #B9F2FF;")
                    
                    # Update tire label with color coding
                    tire_percent = int(tire_condition * 100)
                    self.tire_label.setText(f"Tire: {tire_percent}%")
                    if tire_condition < 0.3:
                        self.tire_label.setStyleSheet("font-size: 14px; color: #DD2D4A; font-weight: bold;")
                    elif tire_condition < 0.6:
                        self.tire_label.setStyleSheet("font-size: 14px; color: #DD2D4A;")
                    else:
                        self.tire_label.setStyleSheet("font-size: 14px; color: #B9F2FF;")
                        
            except Exception as e:
                print(f"Error updating telemetry display: {e}")
                import traceback
                traceback.print_exc()
            return

        # Handle mark_dnf command emitted from simulation thread (run on GUI thread)
        if message.startswith("mark_dnf|"):
            try:
                parts = message.split("|")
                if len(parts) >= 2:
                    did = int(parts[1])
                    if hasattr(self, 'track_widget') and hasattr(self.track_widget, 'mark_dnf'):
                        try:
                            self.track_widget.mark_dnf(did)
                        except Exception:
                            pass
            except Exception:
                pass
            return

        # Handle player DNF UI request (show RETIRED and disable controls)
        if message.startswith("player_dnf|"):
            try:
                parts = message.split("|")
                if len(parts) >= 2:
                    did = int(parts[1])
                    # Only act if it's the player's driver
                    if did == getattr(self, 'player_driver_id', None):
                        try:
                            if hasattr(self, 'player_status_label'):
                                self.player_status_label.setText("RETIRED")
                                self.player_status_label.show()
                        except Exception:
                            pass
                        # Disable a set of interactive widgets so the player cannot change strategy
                        try:
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
            except Exception:
                pass
            return
        
        # Check if this is a standings update
        if message.startswith("standings_update|"):
            try:
                parts = message.split("|")
                driver_id = int(parts[1])
                race_position = int(parts[2])
                # Normalize to 1-based lap counting for display
                lap = max(1, int(parts[3]))
                push_intensity = float(parts[4]) if len(parts) > 4 else 0.7
                gap_ahead = float(parts[5]) if len(parts) > 5 else 0.0
                position_m = float(parts[6]) if len(parts) > 6 else 0.0
                race_time = float(parts[7]) if len(parts) > 7 else 0.0

                if not hasattr(self, '_race_state'):
                    self._race_state = {}
                if not hasattr(self, '_driver_push_intensity'):
                    self._driver_push_intensity = {}

                driver = next((d for d in self.drivers if d.id == driver_id), None)
                if driver:
                    self._race_state[driver_id] = {
                        'name': driver.name,
                        'position': race_position,
                        'lap': lap,
                        'time': race_time,
                        'distance': position_m,
                        'gap_ahead': gap_ahead,
                        'dnf': False
                    }
                    self._driver_push_intensity[driver_id] = push_intensity

                self._rebuild_standings_table()

            except Exception:
                pass
        else:
            self.info_label.setText(message)

    def _rebuild_standings_table(self):
        """Rebuild the standings table with live gaps and aggression symbols."""
        if not hasattr(self, '_race_state'):
            return

        track_obj = getattr(self, 'track', None)
        track_length = (track_obj.length_km * 1000.0) if track_obj is not None else 6350.0
        standings_list = []
        for did, data in self._race_state.items():
            # Use (lap - 1) so that lap=1 (first racing lap) corresponds to progress starting at 0
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
                'total_progress': total_progress
            })

        if not standings_list:
            return

        standings_list.sort(key=lambda x: (x['dnf'], -x['total_progress']))

        leader = standings_list[0]
        leader_lap = leader['lap']
        cumulative_gap = 0.0

        for row, entry in enumerate(standings_list):
            colour_item = QTableWidgetItem()
            if entry['driver_id'] in self.driver_colours:
                colour = self.driver_colours[entry['driver_id']]
                colour_item.setBackground(colour)
                colour_item.setText("  ")
            self.standings_table.setItem(row, 0, colour_item)

            driver_name = entry['name']
            push_int = self._driver_push_intensity.get(entry['driver_id'], 0.7)
            if push_int < 0.25:
                symbol = "(-)"
            elif push_int < 0.75:
                symbol = "(=)"
            else:
                symbol = "(+)"
            self.standings_table.setItem(row, 1, QTableWidgetItem(f"{symbol} {driver_name}"))
            # Highlight the player-controlled driver row/cell
            try:
                name_item = self.standings_table.item(row, 1)
                if entry['driver_id'] == getattr(self, 'player_driver_id', None):
                    name_item.setBackground(QColor(255, 215, 0))  # Gold for player
                    name_item.setForeground(QColor(0, 0, 0))  # Dark text on gold
                else:
                    name_item.setBackground(QColor(37, 38, 39))
            except Exception:
                pass

            self.standings_table.setItem(row, 2, QTableWidgetItem(str(entry['lap'])))

            if entry.get('dnf', False):
                gap_text = "DNF"
            elif row == 0:
                gap_text = "LEADER"
            else:
                lap_diff = leader_lap - entry['lap']
                raw_gap = entry.get('gap_ahead', 0.0)
                
                if lap_diff > 0:
                    # Car is behind on laps
                    gap_text = f"+{lap_diff}L"
                elif raw_gap >= 1000.0:
                    # Gap encoded as 999+N means N laps (from engine)
                    laps_behind = int(raw_gap - 999.0)
                    if laps_behind > 0:
                        gap_text = f"+{laps_behind}L"
                    else:
                        gap_text = f"+{raw_gap:.1f}s"  # Fallback if just large gap
                else:
                    # Normal time gap accumulation
                    cumulative_gap += max(raw_gap, 0.0)
                    if cumulative_gap < 0.1:
                        gap_text = "-"
                    else:
                        gap_text = f"+{cumulative_gap:.1f}s"

            self.standings_table.setItem(row, 3, QTableWidgetItem(gap_text))

        # Debug log every few seconds
        if not hasattr(self, '_last_standings_log'):
            self._last_standings_log = 0
        import time
        if time.time() - self._last_standings_log > 3.0:
            self._last_standings_log = time.time()
            print("\n  [STANDINGS] Current order:")
            for i, entry in enumerate(standings_list[:5]):
                print(f"    P{i+1}: {entry['name']} (L{entry['lap']}, gap={entry.get('gap_ahead', 0.0):.1f}s)")
    
    def _on_pace_changed(self, value):
        """Handle pace slider change - update label and color gradient."""
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

        # Mix color from blue -> red based on value
        try:
            t = max(0.0, min(1.0, value / 100.0))
            low = (0x00, 0xBF, 0xFF)  # blue
            high = (0xDD, 0x2D, 0x4A)  # red
            r = int(low[0] + (high[0] - low[0]) * t)
            g = int(low[1] + (high[1] - low[1]) * t)
            b = int(low[2] + (high[2] - low[2]) * t)
            color = f"#{r:02X}{g:02X}{b:02X}"
            self.pace_value_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: #FFFFFF;")
            # Update slider styling: sub-page shows selected color
            self.pace_slider.setStyleSheet(
                "QSlider::groove:horizontal { height: 8px; background: #2E2E2E; border-radius: 4px; }"
                f"QSlider::sub-page:horizontal {{ background: {color}; border-radius: 4px; }}"
                "QSlider::handle:horizontal { background: #F5F5F5; width: 14px; margin: -4px 0; border-radius: 7px; }"
            )
        except Exception:
            # Fallback: keep readable style
            self.pace_value_label.setStyleSheet("font-size:16px; font-weight:bold; color: #DD2D4A;")
    
    def _on_overtake_changed(self, value):
        """Handle overtake aggressiveness slider change with dynamic color."""
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
        self.overtake_value_label.setText(f"Overtaking: {aggr_text} ({value}%)")

        try:
            t = max(0.0, min(1.0, value / 100.0))
            low = (0x00, 0xBF, 0xFF)
            high = (0xDD, 0x2D, 0x4A)
            r = int(low[0] + (high[0] - low[0]) * t)
            g = int(low[1] + (high[1] - low[1]) * t)
            b = int(low[2] + (high[2] - low[2]) * t)
            color = f"#{r:02X}{g:02X}{b:02X}"
            self.overtake_value_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: #FFFFFF;")
            self.overtake_slider.setStyleSheet(
                "QSlider::groove:horizontal { height: 8px; background: #2E2E2E; border-radius: 4px; }"
                f"QSlider::sub-page:horizontal {{ background: {color}; border-radius: 4px; }}"
                "QSlider::handle:horizontal { background: #F5F5F5; width: 14px; margin: -4px 0; border-radius: 7px; }"
            )
        except Exception:
            self.overtake_value_label.setStyleSheet("font-size:16px; font-weight:bold; color: #FFFFFF;")
    
    def _update_combined_push(self):
        """Compute combined push intensity as average of pace and overtake sliders."""
        pace_norm = self.player_overrides.get('pace', 0.5)
        overtake_norm = self.player_overrides.get('overtake', 0.5)
        # Average both sliders: 100% push only when both at 100%
        avg = (pace_norm + overtake_norm) / 2.0
        # Map to 0.3-1.0 range
        self.player_overrides['push'] = 0.3 + avg * 0.7
        print(f"[PLAYER PUSH] pace={pace_norm*100:.0f}%, overtake={overtake_norm*100:.0f}% → combined push={self.player_overrides['push']:.2f}")

    def set_player_driver(self, driver):
        """Set the player-controlled driver."""
        if driver:
            self.player_driver_id = driver.id
            print(f"[RACE WINDOW] Player driver set: {driver.name} (ID: {driver.id})")
        else:
            self.player_driver_id = None
    
    def set_tuning_preset(self, preset: str):
        """Set the simulation tuning preset."""
        self.tuning_preset = preset or 'balanced'
        print(f"[RACE WINDOW] Tuning preset set: {self.tuning_preset}")
    
    def _set_camera_mode(self, mode: str):
        """Set camera mode: 'full' or 'follow'."""
        self.camera_mode = mode
        if self.track_widget:
            self.track_widget.set_camera_mode(mode, self.player_driver_id)
        
        # Update button styles
        if mode == 'full':
            self.camera_full_btn.setStyleSheet("background-color: #B9F2FF; color: #353839;")
            self.camera_follow_btn.setStyleSheet("")
        else:
            self.camera_follow_btn.setStyleSheet("background-color: #B9F2FF; color: #353839;")
            self.camera_full_btn.setStyleSheet("")
        
        print(f"[CAMERA] Switched to {mode} mode")
    
    def set_display_mode(self, mode: str):
        """Set display mode: 'windowed', 'borderless', or 'fullscreen'."""
        self.display_mode = mode
        screen_obj = QApplication.primaryScreen()
        screen = screen_obj.geometry() if screen_obj else None
        
        if mode == "windowed":
            self.setWindowFlags(Qt.WindowType.Window)
            self.showNormal()
            self.setGeometry(100, 100, 1600, 900)
            print("[INFO] Race window: windowed mode (1600x900)")
        
        elif mode == "borderless":
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            if screen is not None:
                self.setGeometry(screen)
            self.showMaximized()
            print("[INFO] Race window: borderless windowed fullscreen")
        
        elif mode == "fullscreen":
            self.setWindowFlags(Qt.WindowType.Window)
            self.showFullScreen()
            print("[INFO] Race window: exclusive fullscreen")
        
        self.show()
    
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
    import traceback
    from PyQt6.QtWidgets import QMessageBox
    app = QApplication(sys.argv)
    try:
        window = RaceWindow()
        window.show()
        print("[DEBUG] RaceWindow created and shown.")
        # Show a message box to confirm GUI launch
    except Exception as e:
        print("[ERROR] Exception during GUI launch:", e)
        traceback.print_exc()
        raise
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
