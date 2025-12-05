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
from typing import List, Dict, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt, QPointF, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QKeyEvent

from database.database_manager import DatabaseManager
from services.race_simulation_api import simulate_race


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
    lap: int = 0
    total_time: float = 0.0  # Total race time from simulation
    avg_lap_time: float = 60.0  # Average lap time in seconds
    last_lap: int = 0  # Last completed lap number


class EventEmitter(QObject):
    """Signal emitter for race events."""
    position_update = pyqtSignal(dict)  # {driver_id: {lap, position, total_time}}
    race_finished = pyqtSignal(list)
    event = pyqtSignal(str)


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
        segments = state['segments']
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
            final_distance = math.hypot(final_dx, final_dy)
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
        self.setMinimumSize(1200, 800)
        self.race_active = False
        self.start_time = 0.0
        
        # Animation timer for smooth movement
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_cars)
        self.animation_timer.setInterval(16)  # ~60 FPS
    
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
            car.lap = 0
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
                car.lap = lap
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
                    if not hasattr(car, 'prev_s'):
                        car.prev_s = normalized_pos
                    
                    # Update position
                    car.s = normalized_pos
                    
                    # Track movement direction for rotation
                    car.movement_direction = normalized_pos - car.prev_s
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
                car.lap = lap
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
    
    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Background
            painter.fillRect(self.rect(), QColor(15, 20, 25))
            
            # Transform: center view
            painter.translate(600, 400)
            painter.scale(1, -1)
            
            self._draw_track(painter)
            self._draw_cars(painter)
            
            painter.end()
        except Exception as e:
            print(f"ERROR in paintEvent: {e}")
            import traceback
            traceback.print_exc()
    
    def _draw_track(self, painter):
        """Draw track centerline."""
        try:
            if not self.track_points or len(self.track_points) < 2:
                return
            
            path = QPainterPath()
            path.moveTo(self.track_points[0].x, self.track_points[0].y)
            
            for i in range(1, len(self.track_points), 3):
                if i + 2 < len(self.track_points):
                    p1 = self.track_points[i]
                    p2 = self.track_points[i + 1]
                    p3 = self.track_points[i + 2]
                    path.cubicTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
            
            path.lineTo(self.track_points[0].x, self.track_points[0].y)
            
            # Track surface
            painter.setPen(QPen(QColor(80, 80, 80), 20))
            painter.drawPath(path)
            
            # Centerline
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.drawPath(path)
            
            # Start/finish line
            if len(self.track_points) > 200:
                pt = self.track_points[200]
                painter.setPen(QPen(Qt.GlobalColor.white, 3))
                normal_x = -math.sin(pt.theta)
                normal_y = math.cos(pt.theta)
                hw = 10
                painter.drawLine(int(pt.x - normal_x * hw), int(pt.y - normal_y * hw),
                                int(pt.x + normal_x * hw), int(pt.y + normal_y * hw))
            
            # 100 CHECKPOINT MARKERS (1% intervals)
            # These help visualize car progression and calculate gaps accurately
            if len(self.track_points) > 100:
                painter.setPen(QPen(QColor(100, 100, 100), 1))  # Gray checkpoints
                checkpoint_interval = len(self.track_points) // 100
                for i in range(0, len(self.track_points), checkpoint_interval):
                    if i < len(self.track_points):
                        pt = self.track_points[i]
                        normal_x = -math.sin(pt.theta)
                        normal_y = math.cos(pt.theta)
                        hw = 5  # Smaller than start/finish
                        painter.drawLine(int(pt.x - normal_x * hw), int(pt.y - normal_y * hw),
                                        int(pt.x + normal_x * hw), int(pt.y + normal_y * hw))
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
            screen = QApplication.primaryScreen().geometry()
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
            
            # Player control
            self.player_driver_id: Optional[int] = None
            self.player_overrides: Dict[str, float] = {'pace': 0.7, 'overtake': 0.5}  # pace: 0.5-1.0, overtake: 0.0-1.0
            # Event emitter
            self.emitter = EventEmitter()
            self.emitter.position_update.connect(self._on_position_update)
            self.emitter.race_finished.connect(self._on_race_finished)
            self.emitter.event.connect(self._on_event)
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
        
        # Left: Track display
        self.track_widget = None  # Will be created after track loads
        left_container = QWidget()
        self.left_layout = QVBoxLayout(left_container)
        self.left_layout.addWidget(QLabel("Loading track..."))
        layout.addWidget(left_container, 3)
        
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
        player_layout = QVBoxLayout(player_controls)
        
        # Pace control
        pace_label_top = QLabel("Race Pace: Balanced")
        self.pace_value_label = pace_label_top
        player_layout.addWidget(pace_label_top)
        
        self.pace_slider = QSlider(Qt.Orientation.Horizontal)
        self.pace_slider.setMinimum(0)
        self.pace_slider.setMaximum(100)
        self.pace_slider.setValue(50)
        self.pace_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pace_slider.setTickInterval(10)
        self.pace_slider.valueChanged.connect(self._on_pace_changed)
        player_layout.addWidget(self.pace_slider)
        
        pace_hint = QLabel("Conservative ← → Aggressive")
        pace_hint.setStyleSheet("font-size: 10px;")
        pace_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_layout.addWidget(pace_hint)
        
        player_layout.addSpacing(10)
        
        # Overtake aggressiveness
        overtake_label_top = QLabel("Overtaking: Moderate")
        self.overtake_value_label = overtake_label_top
        player_layout.addWidget(overtake_label_top)
        
        self.overtake_slider = QSlider(Qt.Orientation.Horizontal)
        self.overtake_slider.setMinimum(0)
        self.overtake_slider.setMaximum(100)
        self.overtake_slider.setValue(50)
        self.overtake_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.overtake_slider.setTickInterval(10)
        self.overtake_slider.valueChanged.connect(self._on_overtake_changed)
        player_layout.addWidget(self.overtake_slider)
        
        overtake_hint = QLabel("Cautious ← → Aggressive")
        overtake_hint.setStyleSheet("font-size: 10px;")
        overtake_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_layout.addWidget(overtake_hint)
        
        right_panel.addWidget(player_controls)
        
        # Standings table (row order = position, no need for Pos column)
        right_panel.addWidget(QLabel("<h3>Live Standings</h3>"))
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(3)
        self.standings_table.setHorizontalHeaderLabels(["Driver", "Lap", "Gap"])
        self.standings_table.setMinimumWidth(400)
        right_panel.addWidget(self.standings_table)
        
        layout.addLayout(right_panel, 1)
        
        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1B1E;
            }
            QWidget {
                background-color: #1A1B1E;
                color: #B9F2FF;
                font-family: 'Inter', sans-serif;
            }
            QPushButton {
                background-color: #B9F2FF;
                color: #1A1B1E;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DD2D4A;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #353839;
                color: #666666;
            }
            QLabel {
                color: #B9F2FF;
            }
            QTableWidget {
                background-color: #252627;
                color: #B9F2FF;
                gridline-color: #353839;
            }
            QHeaderView::section {
                background-color: #353839;
                color: #B9F2FF;
                padding: 5px;
                border: none;
            }
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
                    if item.widget():
                        item.widget().deleteLater()
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
                colors = [
                    QColor(255, 50, 50), QColor(50, 150, 255), QColor(50, 255, 50),
                    QColor(255, 255, 50), QColor(255, 150, 50), QColor(200, 50, 255),
                    QColor(50, 255, 255), QColor(255, 150, 150), QColor(150, 255, 150),
                    QColor(200, 200, 255)
                ]
                
                cars = []
                # Starting grid: Stagger cars along track direction (not side-to-side)
                # Formation: 2 cars per row, 10m spacing between rows
                # Row 1: positions 0, 0 (side by side via lateral offset)
                # Row 2: positions 15, 15
                # Row 3: positions 30, 30, etc.
                for i, driver in enumerate(self.drivers):
                    row = i // 2  # 0,1 -> row 0; 2,3 -> row 1; etc.
                    grid_spacing = 15.0  # meters between rows
                    start_position = row * grid_spacing
                    
                    cars.append(Car(
                        driver_id=driver.id,
                        driver_name=driver.name,
                        s=start_position,  # Staggered start positions
                        color=colors[i % len(colors)],
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
                    self.standings_table.setItem(i, 0, QTableWidgetItem(driver_name))
                    self.standings_table.setItem(i, 1, QTableWidgetItem("0"))
                    self.standings_table.setItem(i, 2, QTableWidgetItem("-"))
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
                                print("[ANIMATION] First position data received - starting animation NOW")
                                if self.track_widget:
                                    try:
                                        self.track_widget.start_animation()
                                        print("[ANIMATION] Animation timer started")
                                    except Exception as e:
                                        print(f"[ERROR] Failed to start animation: {e}")
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
                                try:
                                    driver_id = pos_data.get("driver_id")
                                    if driver_id is None:
                                        continue
                                    
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
                                    if frame % 30 == 0:  # Update table once per second
                                        self.emitter.event.emit(f"standings_update|{driver_id}|{position}|{lap}")
                                        
                                except Exception as e:
                                    print(f"ERROR updating position for driver {driver_id}: {e}")
                        
                        elif event_type == "dnf":
                            driver_id = event.get("driver_id")
                            driver_name = event.get("driver_name", f"Driver {driver_id}")
                            reason = event.get("reason", "unknown")
                            lap = event.get("lap", 0)
                            print(f"[DNF] {driver_name} DNF on lap {lap}: {reason}")
                            
                            if self.track_widget and driver_id is not None:
                                if hasattr(self.track_widget, 'mark_dnf'):
                                    self.track_widget.mark_dnf(driver_id)
                        
                        elif event_type == "race_finished":
                            total_laps = event.get("total_laps", 0)
                            race_time = event.get("race_time", 0.0)
                            print(f"\n🏁 Race finished! {total_laps} laps in {race_time:.1f}s")

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
                        import traceback
                        traceback.print_exc()
                
                print("Starting simulate_race with comprehensive engine...")
                # Get track_points safely
                track_pts = getattr(self, 'track_points', None)
                results = simulate_race(
                    self.drivers,
                    self.track,
                    seed=None,
                    laps=3,  # Testing with 3 laps
                    verbose=True,  # Enable verbose for terminal output
                    event_callback=event_callback,
                    stop_event=self.stop_event,
                    lap_delay=0.5,
                    db=self.db,  # Pass database for team data
                    track_points=track_pts,  # Pass visual track for unified position mapping
                    player_driver_id=self.player_driver_id,  # Player-controlled driver
                    player_overrides=self.player_overrides.copy()  # Player's pace and overtake settings
                )
                
                print(f"Race simulation complete, {len(results) if results else 0} results")
                
                # Don't save from race thread - database is in main thread
                # Results will be saved via race_finished event if needed
            
            except Exception as e:
                error_msg = f"Race error: {e}"
                print(f"ERROR in race_runner: {e}")
                import traceback
                traceback.print_exc()
                self.emitter.event.emit(error_msg)
        
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
            
            # Update standings table
            for row in range(self.standings_table.rowCount()):
                item = self.standings_table.item(row, 1)
                if item:
                    driver_name = item.text()
                    driver = next((d for d in self.drivers if d.name == driver_name), None)
                    if driver and driver.id == data['driver_id']:
                        self.standings_table.setItem(row, 0, QTableWidgetItem(str(data['position'])))
                        self.standings_table.setItem(row, 2, QTableWidgetItem(str(data['lap'])))
                        break
        except Exception as e:
            print(f"ERROR in _on_position_update: {e}")
    
    def _on_race_finished(self, results: list):
        """Handle race finish."""
        try:
            print(f"Race finished event received with {len(results)} results")
            self.info_label.setText("Race finished!")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
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
        - standings_update: Position changes during race
        - General info messages
        
        STANDINGS UPDATE FORMAT:
        "standings_update|driver_id|position|lap|time_seconds|position_m"
        
        Example: "standings_update|5|1|3|185.4|19234.5"
        Means: Driver 5 is in P1, on lap 3, at 185.4 seconds, position 19234.5m
        """
        # Check if this is a standings update
        if message.startswith("standings_update|"):
            try:
                # Parse the message
                parts = message.split("|")
                driver_id = int(parts[1])
                race_position = int(parts[2])
                lap = int(parts[3])
                time_seconds = float(parts[4]) if len(parts) > 4 else 0.0
                position_m = float(parts[5]) if len(parts) > 5 else 0.0
                
                # === STORE RACE STATE FOR EACH DRIVER ===
                # We need to track all drivers to calculate gaps properly
                if not hasattr(self, '_race_state'):
                    self._race_state = {}  # {driver_id: {position, lap, time, distance}}
                
                driver = next((d for d in self.drivers if d.id == driver_id), None)
                if driver:
                    self._race_state[driver_id] = {
                        'name': driver.name,
                        'position': race_position,
                        'lap': lap,
                        'time': time_seconds,
                        'distance': position_m
                    }
                
                # === REBUILD STANDINGS TABLE ===
                # We need to sort by TOTAL PROGRESS (lap * track_length + position_m)
                # This gives us the true racing order
                standings_list = []
                for did, data in self._race_state.items():
                    # Calculate total progress
                    total_progress = data['lap'] * 6350 + (data['distance'] % 6350)
                    standings_list.append({
                        'driver_id': did,
                        'name': data['name'],
                        'position': data['position'],
                        'lap': data['lap'],
                        'time': data['time'],
                        'distance': data['distance'],
                        'total_progress': total_progress
                    })
                
                # === SORT BY TOTAL PROGRESS (DESCENDING) ===
                # Car with most progress is leader
                standings_list.sort(key=lambda x: -x['total_progress'])
                
                # === FIND LEADER FOR GAP CALCULATION ===
                leader_time = standings_list[0]['time'] if standings_list else 0.0
                leader_lap = standings_list[0]['lap'] if standings_list else 0
                
                # === UPDATE TABLE ROWS ===
                for row, entry in enumerate(standings_list):
                    # Column 0: Driver Name
                    self.standings_table.setItem(row, 0, QTableWidgetItem(entry['name']))
                    
                    # Column 1: Current Lap
                    self.standings_table.setItem(row, 1, QTableWidgetItem(str(entry['lap'])))
                    
                    # Column 2: Gap to Leader
                    if row == 0:
                        # Leader shows "-"
                        gap_text = "-"
                    else:
                        # Calculate gap
                        lap_diff = leader_lap - entry['lap']
                        if lap_diff > 0:
                            # Multiple laps behind
                            gap_text = f"+{lap_diff}L"
                        else:
                            # Same lap - show time gap
                            time_gap = entry['time'] - leader_time
                            if time_gap > 0:
                                gap_text = f"+{time_gap:.2f}s"
                            else:
                                gap_text = "-"
                    
                    self.standings_table.setItem(row, 2, QTableWidgetItem(gap_text))
                
                # === DEBUG: Log standings every 3 seconds ===
                if not hasattr(self, '_last_standings_log'):
                    self._last_standings_log = 0
                import time
                if time.time() - self._last_standings_log > 3.0:
                    self._last_standings_log = time.time()
                    print(f"\n  [STANDINGS] Current order:")
                    for i, entry in enumerate(standings_list[:5]):
                        print(f"    P{i+1}: {entry['name']} (L{entry['lap']}, {entry['time']:.1f}s)")
                    
            except Exception as e:
                print(f"  [ERROR] Failed to update standings: {e}")
                import traceback
                traceback.print_exc()
        else:
            self.info_label.setText(message)
    
    def _on_pace_changed(self, value):
        """Handle pace slider change."""
        if value < 33:
            pace_text = "Conservative"
        elif value < 67:
            pace_text = "Balanced"
        else:
            pace_text = "Aggressive"
        
        # Map slider value (0-100) to push_intensity (0.5-1.0)
        self.player_overrides['pace'] = 0.5 + (value / 100.0) * 0.5
        self.pace_value_label.setText(f"Race Pace: {pace_text} ({value}%)")
        print(f"[PLAYER] Pace adjusted to {value}% ({pace_text}) -> push_intensity: {self.player_overrides['pace']:.2f}")
    
    def _on_overtake_changed(self, value):
        """Handle overtake aggressiveness slider change."""
        if value < 33:
            aggr_text = "Cautious"
        elif value < 67:
            aggr_text = "Moderate"
        else:
            aggr_text = "Aggressive"
        
        # Map slider value (0-100) to overtaking multiplier (0.0-1.0)
        self.player_overrides['overtake'] = value / 100.0
        self.overtake_value_label.setText(f"Overtaking: {aggr_text} ({value}%)")
        print(f"[PLAYER] Overtake aggression adjusted to {value}% ({aggr_text}) -> multiplier: {self.player_overrides['overtake']:.2f}")
    
    def set_player_driver(self, driver):
        """Set the player-controlled driver."""
        if driver:
            self.player_driver_id = driver.id
            print(f"[RACE WINDOW] Player driver set: {driver.name} (ID: {driver.id})")
        else:
            self.player_driver_id = None
    
    def set_display_mode(self, mode: str):
        """Set display mode: 'windowed', 'borderless', or 'fullscreen'."""
        self.display_mode = mode
        screen = QApplication.primaryScreen().geometry()
        
        if mode == "windowed":
            self.setWindowFlags(Qt.WindowType.Window)
            self.showNormal()
            self.setGeometry(100, 100, 1600, 900)
            print("[INFO] Race window: windowed mode (1600x900)")
        
        elif mode == "borderless":
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setGeometry(screen)
            self.showMaximized()
            print("[INFO] Race window: borderless windowed fullscreen")
        
        elif mode == "fullscreen":
            self.setWindowFlags(Qt.WindowType.Window)
            self.showFullScreen()
            print("[INFO] Race window: exclusive fullscreen")
        
        self.show()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard events."""
        if event.key() == Qt.Key.Key_Escape:
            # ESC key: Stop race and return to menu
            print("[INFO] ESC pressed - returning to main menu")
            self.stop_race()
            self.return_to_menu.emit()
            self.close()
        else:
            super().keyPressEvent(event)


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
