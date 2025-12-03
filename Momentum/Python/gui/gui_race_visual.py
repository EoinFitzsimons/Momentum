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
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath

from services.persistence_sqlite import PersistenceSQLite
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
            'total_angle': 0
        }
        
        # Scale circuit instructions based on track length
        scale = track_length_km / 6.0  # Base is ~6km
        
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
        ]
        
        CircuitGenerator._process_instructions(circuit_instructions, state)
        CircuitGenerator._add_closure(state)
        CircuitGenerator._finalize_circuit(segments)
        
        return segments
    
    @staticmethod
    def _process_instructions(instructions, state):
        for instruction in instructions:
            if instruction[0] == 'S':
                CircuitGenerator._add_straight(instruction[1], state)
            elif instruction[0] == 'C':
                angle_deg, radius, clothoid_len, k = instruction[1:5]
                CircuitGenerator._add_corner(angle_deg * math.pi / 180, radius, clothoid_len, k, state)
    
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
    def _add_closure(state):
        """
        Add proper closure to create a complete closed loop.
        
        CRITICAL FUNCTION: This creates the connection back to the start of the track.
        Without this, the track would be an open path, not a loop.
        
        Strategy:
        1. Calculate angle deficit (how much rotation needed to point back to start)
        2. Add corners to turn the track back toward start point
        3. Add straight section to close the physical gap
        4. DO NOT force exact closure - let modulo wrapping handle the loop
        
        WHY: Forcing exact closure causes teleportation. Instead, we let the
        rendering code wrap positions using modulo arithmetic (position % track_length).
        """
        segments = state['segments']
        start_x, start_y = segments[0].x, segments[0].y
        
        # Calculate gap to start point
        dx = start_x - state['current_x']
        dy = start_y - state['current_y']
        dist = math.hypot(dx, dy)
        
        # Calculate angle deficit (need to turn 360° total for closed loop)
        angle_deficit = 2 * math.pi - state['total_angle']
        
        print(f"  [CLOSURE] Gap to start: {dist:.1f}m, Angle deficit: {math.degrees(angle_deficit):.1f}°")
        
        # Step 1: Add corners to close angle deficit
        if abs(angle_deficit) > math.radians(5):
            turn_dir = 1 if angle_deficit > 0 else -1
            remaining = abs(angle_deficit)
            
            if remaining > math.radians(60):
                # Large deficit: split into two corners
                angles = [remaining * 0.55 * turn_dir, remaining * 0.45 * turn_dir]
                for angle in angles:
                    CircuitGenerator._add_straight(180, state)
                    CircuitGenerator._add_corner(angle, 100, 50, 0.0001, state)
            else:
                # Small deficit: single corner
                CircuitGenerator._add_straight(180, state)
                CircuitGenerator._add_corner(angle_deficit, 120, 52, 0.00009, state)
        
        # Step 2: Add straight to close physical gap
        dx = start_x - state['current_x']
        dy = start_y - state['current_y']
        dist = math.hypot(dx, dy)
        
        if dist > 5:
            # Add final straight section pointing toward start
            num_points = int(dist)
            for i in range(num_points):
                state['current_x'] += math.cos(state['current_theta'])
                state['current_y'] += math.sin(state['current_theta'])
                segments.append(TrackPoint(
                    state['current_s'] + i,
                    state['current_x'],
                    state['current_y'],
                    state['current_theta'],
                    0
                ))
            state['current_s'] += num_points
        
        # Step 3: Store track length for modulo wrapping
        # The track is now a closed loop, but NOT perfectly closed
        # The rendering code will use modulo to wrap positions
        print(f"  [CLOSURE] Track loop complete, total length: {state['current_s']}m")
    
    @staticmethod
    def _finalize_circuit(segments):
        """Add wraparound points and scale/center circuit."""
        if not segments:
            return
        
        # CRITICAL FIX FOR TELEPORTATION:
        # Duplicate the first 150 points at the end of the array
        # This creates a seamless visual loop when cars wrap from end to start
        # Without this, cars jump visually when position wraps via modulo
        original_length = len(segments)
        wraparound_count = min(150, original_length)
        print(f"  [FINALIZE] Adding {wraparound_count} wraparound points to prevent teleportation")
        
        for i in range(wraparound_count):
            original_pt = segments[i]
            wrap_pt = TrackPoint(
                original_length + i,  # Extended arc-length
                original_pt.x,
                original_pt.y,
                original_pt.theta,
                original_pt.curvature
            )
            segments.append(wrap_pt)
        
        print(f"  [FINALIZE] Track now has {len(segments)} points (original: {original_length})")
        
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
                
                # === POSITION MAPPING: Engine → Visual Track ===
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
                        
                        # === STEP 2: MAP TO TRACK POINT INDEX ===
                        # Convert position (0 to track_length) into array index
                        # The track_points array has wraparound points at the end for seamless looping
                        # So we can directly use normalized_s as the index (with safety clamp)
                        idx = int(normalized_s)
                        # Safety clamp - allow using wraparound points at end of array
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
                        # To move sideways, we rotate 90° (pi/2 radians)
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
    
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Momentum - Race Visualization")
            self.setGeometry(100, 100, 1600, 900)
            # Race state
            self.db: Optional[PersistenceSQLite] = None
            self.drivers = []
            self.track = None
            self.race_thread: Optional[threading.Thread] = None
            self.stop_event: Optional[threading.Event] = None
            self.driver_lap_times: Dict[int, float] = {}  # Track last lap time per driver
            self.race_start_time: float = 0.0
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
                self.db = PersistenceSQLite()
            except Exception as e:
                self.info_label.setText(f"Database connection failed: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Database initialization failed: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Load drivers
            try:
                all_drivers = self.db.list_drivers()
                if not all_drivers:
                    self.info_label.setText("Error: No drivers in database")
                    self.start_btn.setEnabled(False)
                    print("ERROR: No drivers found in database")
                    return
                
                self.drivers = all_drivers[:10] if len(all_drivers) >= 10 else all_drivers
                print(f"Loaded {len(self.drivers)} drivers")
            except Exception as e:
                self.info_label.setText(f"Failed to load drivers: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Failed to load drivers: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Load track
            try:
                # Get first track (track_id = 1)
                self.track = self.db.get_track(1)
                if not self.track:
                    self.info_label.setText("Error: No tracks in database")
                    self.start_btn.setEnabled(False)
                    print("ERROR: No track with id=1 found in database")
                    return
                
                print(f"Loaded track: {self.track.name} ({self.track.length_km:.2f}km)")
            except Exception as e:
                self.info_label.setText(f"Failed to load track: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Failed to load track: {e}")
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
                
                track_length = track_points[-1].s if track_points else 5000
                print(f"Generated circuit with {len(track_points)} points, length: {track_length:.0f}m")
                
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
                    self.standings_table.setItem(i, 0, QTableWidgetItem(driver.name))
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
                            print(f"❌ {driver_name} DNF on lap {lap}: {reason}")
                            
                            if self.track_widget and driver_id is not None:
                                if hasattr(self.track_widget, 'mark_dnf'):
                                    self.track_widget.mark_dnf(driver_id)
                        
                        elif event_type == "race_finished":
                            total_laps = event.get("total_laps", 0)
                            race_time = event.get("race_time", 0.0)
                            print(f"\n🏁 Race finished! {total_laps} laps in {race_time:.1f}s")
                            
                            if hasattr(self.emitter, 'race_finished'):
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
                    verbose=True,  # Enable verbose for terminal output
                    event_callback=event_callback,
                    stop_event=self.stop_event,
                    lap_delay=0.5,
                    db=self.db,  # Pass database for team data
                    track_points=track_pts  # Pass visual track for unified position mapping
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


def main():
    import traceback
    from PyQt6.QtWidgets import QMessageBox
    app = QApplication(sys.argv)
    try:
        window = RaceWindow()
        window.show()
        print("[DEBUG] RaceWindow created and shown.")
        # Show a message box to confirm GUI launch
        msg = QMessageBox()
        msg.setWindowTitle("Momentum GUI Test")
        msg.setText("Momentum GUI window launched successfully. If you see this, the window is visible.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    except Exception as e:
        print("[ERROR] Exception during GUI launch:", e)
        traceback.print_exc()
        raise
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
