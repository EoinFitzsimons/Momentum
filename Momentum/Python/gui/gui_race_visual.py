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

from persistence_sqlite import PersistenceSQLite
from race_simulation_api import simulate_race


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
        """Add simple closure section."""
        segments = state['segments']
        start_x, start_y = segments[0].x, segments[0].y
        dx = start_x - state['current_x']
        dy = start_y - state['current_y']
        dist = math.hypot(dx, dy)
        angle_deficit = 2 * math.pi - state['total_angle']
        
        if abs(angle_deficit) > math.radians(5):
            turn_dir = 1 if angle_deficit > 0 else -1
            remaining = abs(angle_deficit)
            
            if remaining > math.radians(60):
                angles = [remaining * 0.55 * turn_dir, remaining * 0.45 * turn_dir]
                for angle in angles:
                    CircuitGenerator._add_straight(180, state)
                    CircuitGenerator._add_corner(angle, 100, 50, 0.0001, state)
            else:
                CircuitGenerator._add_straight(180, state)
                CircuitGenerator._add_corner(angle_deficit, 120, 52, 0.00009, state)
        
        CircuitGenerator._add_straight(int(max(100, dist * 0.12)), state)
    
    @staticmethod
    def _finalize_circuit(segments):
        """Scale and center circuit."""
        if not segments:
            return
        
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
        Update car position from real-time simulation (30 FPS updates)
        
        Args:
            driver_id: Driver identifier
            position_m: Absolute position in meters from lap start
            lap: Current lap number
            velocity_mps: Current velocity in meters per second
        """
        for car in self.cars:
            if car.driver_id == driver_id:
                # Update position directly from simulation
                car.s = position_m  # Position in meters along track
                car.lap = lap
                car.velocity_mps = velocity_mps
                break
        
        # Trigger repaint
        self.update()
    
    def _animate_cars(self):
        """Smoothly update car positions based on simulation time - just trigger repaint."""
        if not self.race_active:
            return
        
        self.update()
    
    def mark_dnf(self, driver_id: int):
        """Mark car as DNF."""
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
        except Exception as e:
            print(f"ERROR in _draw_track: {e}")
    
    def _draw_cars(self, painter):
        """Draw cars at current positions."""
        try:
            if not self.track_points or self.track_length <= 0:
                return
            
            for car in self.cars:
                try:
                    if car.dnf:
                        continue
                    
                    # Find track point at car's arc-length
                    if self.track_length > 0 and len(self.track_points) > 0:
                        idx = int((car.s / self.track_length) * len(self.track_points)) % len(self.track_points)
                        pt = self.track_points[idx]
                        
                        # Draw car
                        painter.setBrush(QBrush(car.color))
                        painter.setPen(QPen(Qt.GlobalColor.white, 1))
                        painter.drawEllipse(QPointF(pt.x, pt.y), 4, 4)
                except Exception as e:
                    print(f"ERROR drawing car {car.driver_id}: {e}")
        except Exception as e:
            print(f"ERROR in _draw_cars: {e}")


class RaceWindow(QMainWindow):
    """Main race window with track display and controls."""
    
    def __init__(self):
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
        
        # Standings table
        right_panel.addWidget(QLabel("<h3>Live Standings</h3>"))
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(4)
        self.standings_table.setHorizontalHeaderLabels(["Pos", "Driver", "Lap", "Gap"])
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
            
            # Create cars
            try:
                colors = [
                    QColor(255, 50, 50), QColor(50, 150, 255), QColor(50, 255, 50),
                    QColor(255, 255, 50), QColor(255, 150, 50), QColor(200, 50, 255),
                    QColor(50, 255, 255), QColor(255, 150, 150), QColor(150, 255, 150),
                    QColor(200, 200, 255)
                ]
                
                cars = []
                for i, driver in enumerate(self.drivers):
                    cars.append(Car(
                        driver_id=driver.id,
                        driver_name=driver.name,
                        s=0.0,
                        color=colors[i % len(colors)],
                        total_time=0.0,
                        avg_lap_time=60.0,
                        last_lap=0
                    ))
                
                self.track_widget.set_cars(cars)
                print(f"Created {len(cars)} cars")
            except Exception as e:
                self.info_label.setText(f"Failed to create cars: {e}")
                self.start_btn.setEnabled(False)
                print(f"ERROR: Car creation failed: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Initialize standings table
            try:
                self.standings_table.setRowCount(len(self.drivers))
                for i, driver in enumerate(self.drivers):
                    self.standings_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    self.standings_table.setItem(i, 1, QTableWidgetItem(driver.name))
                    self.standings_table.setItem(i, 2, QTableWidgetItem("0"))
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
        self.info_label.setText("Race in progress...")
        
        # Start smooth animation
        try:
            self.track_widget.start_animation()
            print("Animation started")
        except Exception as e:
            print(f"WARNING: Failed to start animation: {e}")
        
        def race_runner():
            try:
                self.stop_event = threading.Event()
                print("Race thread started")
                
                def event_callback(event: dict):
                    try:
                        event_type = event.get("type")
                        
                        if event_type == "position_update":
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
                                    
                                    # Update track widget with absolute position
                                    if self.track_widget and pos_data.get("running", True):
                                        # Convert absolute position to track position (0-1 scale)
                                        position_m = pos_data.get("position_m", 0.0)
                                        track_length_m = self.track.length_km * 1000.0
                                        
                                        # Normalize to 0-track_length for current lap
                                        lap = pos_data.get("lap", 0)
                                        lap_position = position_m - (lap * track_length_m)
                                        
                                        # Update car position
                                        if hasattr(self.track_widget, 'update_car_realtime'):
                                            self.track_widget.update_car_realtime(
                                                driver_id=driver_id,
                                                position_m=lap_position,
                                                lap=lap,
                                                velocity_mps=pos_data.get("velocity_mps", 0.0)
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
                results = simulate_race(
                    self.drivers,
                    self.track,
                    seed=None,
                    verbose=True,  # Enable verbose for terminal output
                    event_callback=event_callback,
                    stop_event=self.stop_event,
                    lap_delay=0.5,
                    db=self.db  # Pass database for team data
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
        if self.stop_event:
            self.stop_event.set()
        self.info_label.setText("Stopping race...")
        self.stop_btn.setEnabled(False)
        
        # Stop animation
        if self.track_widget:
            self.track_widget.stop_animation()
    
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
        """Handle general events."""
        # Check if this is a standings update
        if message.startswith("standings_update|"):
            try:
                _, driver_id_str, position_str, lap_str = message.split("|")
                driver_id = int(driver_id_str)
                position = int(position_str)
                lap = int(lap_str)
                
                # Update standings table
                for row in range(self.standings_table.rowCount()):
                    item = self.standings_table.item(row, 1)  # Driver name column
                    if item:
                        driver = next((d for d in self.drivers if d.name == item.text()), None)
                        if driver and driver.id == driver_id:
                            self.standings_table.setItem(row, 0, QTableWidgetItem(str(position)))
                            self.standings_table.setItem(row, 2, QTableWidgetItem(str(lap)))
                            break
            except Exception as e:
                print(f"ERROR updating standings: {e}")
        else:
            self.info_label.setText(message)


def main():
    app = QApplication(sys.argv)
    window = RaceWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
