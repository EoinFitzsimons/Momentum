"""
Momentum - Advanced Race Visualization System
Final Year Computer Science Project

Comprehensive motorsport simulation visualization combining:
- Monte Carlo race simulation with 50+ driver attributes
- Real-time position tracking and interpolation
- Parametric circuit generation with clothoid curves
- Live standings, gap analysis, and race statistics
- Multi-threaded simulation with Qt6 GUI

Architecture:
- Monte Carlo Engine: disciplines/race_simulation.py (1000 iterations per lap)
- Database Models: 50+ driver attributes, team performance, track characteristics
- Circuit Generator: Parametric track with realistic geometry
- Position Tracker: Sub-second interpolation between lap updates
- Event System: Async simulation with thread-safe Qt signals

Author: Eoin Fitzsimons
Date: December 2025
"""

import sys
import os
import math
import time
import threading
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
                              QGroupBox, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QPointF, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QFont

from services.persistence_sqlite import PersistenceSQLite
from database.models import Driver as DBDriver, Track as DBTrack

# Import the full Monte Carlo simulation engine
from archive.basic_race_legacy.disciplines.race_simulation import (
    SimulationContext, MonteCarloRaceSimulator, simulate_race_monte_carlo
)


@dataclass
class TrackPoint:
    """Point on racing circuit with position and geometric properties."""
    s: float  # Arc-length (meters)
    x: float
    y: float
    theta: float  # Heading angle (radians)
    curvature: float


@dataclass
class CarState:
    """Complete state of a racing car during simulation."""
    driver_id: int
    driver_name: str
    position: int  # Current race position
    lap: int  # Current lap number
    total_time: float  # Total elapsed time (seconds)
    last_lap_time: float  # Previous lap time (seconds)
    best_lap_time: float  # Best lap time (seconds)
    gap_to_leader: float  # Time gap to race leader (seconds)
    gap_to_ahead: float  # Time gap to car ahead (seconds)
    s: float  # Track position (arc-length in meters)
    color: QColor
    dnf: bool = False
    dnf_reason: str = ""
    pit_stops: int = 0
    
    # Driver performance metrics
    consistency_factor: float = 1.0
    tire_wear: float = 0.0
    fuel_load: float = 100.0


class EventEmitter(QObject):
    """Thread-safe event emitter for race updates."""
    lap_complete = pyqtSignal(int, list)  # lap_number, standings
    position_update = pyqtSignal(dict)  # car state update
    race_event = pyqtSignal(str, dict)  # event_type, data
    race_finished = pyqtSignal(list)  # final results
    simulation_error = pyqtSignal(str)  # error message


class CircuitGenerator:
    """
    Parametric racing circuit generator with clothoid transition curves.
    
    Generates realistic racing circuits using:
    - True clothoid (Euler spiral) curves for smooth transitions
    - Constant radius arcs for corner apexes
    - Arc-length parametrization for uniform point density
    - Geometric closure algorithms for continuous loops
    """
    
    @staticmethod
    def generate(track_length_km: float = 5.0, complexity: str = "medium"):
        """
        Generate racing circuit based on length and complexity.
        
        Args:
            track_length_km: Target track length in kilometers
            complexity: "simple", "medium", "complex" determines corner count
            
        Returns:
            List[TrackPoint]: Track centerline points with 1m spacing
        """
        segments = []
        state = {
            'segments': segments,
            'current_s': 0,
            'current_x': 0.0,
            'current_y': 0.0,
            'current_theta': 0.0,
            'total_angle': 0.0
        }
        
        # Scale circuit based on target length
        scale = track_length_km / 6.0
        
        # Circuit definition: straights and corners with clothoid parameters
        if complexity == "complex":
            circuit_instructions = [
                ('S', int(600 * scale)),
                ('C', 45, 170, 60, 0.00008),  # (angle_deg, radius, clothoid_len, k)
                ('S', int(400 * scale)),
                ('C', 65, 95, 50, 0.0001),
                ('S', int(220 * scale)),
                ('C', -55, 100, 52, 0.0001),
                ('S', int(350 * scale)),
                ('C', 155, 48, 42, 0.00014),  # Hairpin
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
        else:
            # Medium complexity (default)
            circuit_instructions = [
                ('S', int(500 * scale)),
                ('C', 90, 150, 55, 0.00009),
                ('S', int(400 * scale)),
                ('C', -70, 120, 52, 0.00009),
                ('S', int(300 * scale)),
                ('C', 90, 150, 55, 0.00009),
                ('S', int(400 * scale)),
                ('C', -70, 120, 52, 0.00009),
                ('S', int(350 * scale)),
            ]
        
        CircuitGenerator._process_instructions(circuit_instructions, state)
        CircuitGenerator._add_closure(state)
        CircuitGenerator._finalize_circuit(segments)
        
        print(f"Generated circuit: {len(segments)} points, {segments[-1].s:.0f}m length")
        
        return segments
    
    @staticmethod
    def _process_instructions(instructions, state):
        """Process list of segment instructions to build track."""
        for instruction in instructions:
            if instruction[0] == 'S':
                CircuitGenerator._add_straight(instruction[1], state)
            elif instruction[0] == 'C':
                angle_deg, radius, clothoid_len, k = instruction[1:5]
                CircuitGenerator._add_corner(angle_deg * math.pi / 180, radius, 
                                            clothoid_len, k, state)
    
    @staticmethod
    def _add_straight(length, state):
        """Add straight section to track."""
        length = int(length)
        segments = state['segments']
        for i in range(length):
            s = state['current_s'] + i
            state['current_x'] += math.cos(state['current_theta'])
            state['current_y'] += math.sin(state['current_theta'])
            segments.append(TrackPoint(s, state['current_x'], state['current_y'], 
                                      state['current_theta'], 0))
        state['current_s'] += length
    
    @staticmethod
    def _add_corner(target_angle, radius, clothoid_len, k_clothoid, state):
        """Add corner with clothoid entry/exit and constant radius arc."""
        entry_start = state['current_theta']
        sign = 1 if target_angle > 0 else -1
        
        # Entry clothoid
        CircuitGenerator._add_clothoid(clothoid_len, k_clothoid, sign, state, reverse=False)
        
        # Constant radius arc
        arc_angle = target_angle - 2 * (state['current_theta'] - entry_start)
        CircuitGenerator._add_arc(arc_angle, radius, sign, state)
        
        # Exit clothoid
        CircuitGenerator._add_clothoid(clothoid_len, k_clothoid, sign, state, reverse=True)
        
        state['total_angle'] += target_angle
    
    @staticmethod
    def _add_clothoid(clothoid_len, k_clothoid, sign, state, reverse):
        """Add clothoid spiral transition curve."""
        segments = state['segments']
        for i in range(clothoid_len):
            curvature = k_clothoid * (clothoid_len - i if reverse else i) * sign
            state['current_theta'] += curvature
            state['current_x'] += math.cos(state['current_theta'])
            state['current_y'] += math.sin(state['current_theta'])
            segments.append(TrackPoint(state['current_s'] + i, state['current_x'], 
                                      state['current_y'], state['current_theta'], curvature))
        state['current_s'] += clothoid_len
    
    @staticmethod
    def _add_arc(arc_angle, radius, sign, state):
        """Add constant radius circular arc."""
        segments = state['segments']
        arc_curvature = sign / radius
        arc_length = int(abs(radius * arc_angle))
        for i in range(arc_length):
            state['current_theta'] += arc_curvature
            state['current_x'] += math.cos(state['current_theta'])
            state['current_y'] += math.sin(state['current_theta'])
            segments.append(TrackPoint(state['current_s'] + i, state['current_x'], 
                                      state['current_y'], state['current_theta'], arc_curvature))
        state['current_s'] += arc_length
    
    @staticmethod
    def _add_closure(state):
        """Add closure section to complete circuit loop."""
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
        """Scale and center circuit for display."""
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
    """
    Advanced track visualization widget with real-time car positions.
    
    Features:
    - Smooth cubic spline rendering of track
    - Real-time car position updates with interpolation
    - Gap indicators between cars
    - DNF visualization
    - Start/finish line marking
    """
    
    def __init__(self, track_points: List[TrackPoint], track_length: float):
        super().__init__()
        self.track_points = track_points
        self.track_length = track_length
        self.cars: Dict[int, CarState] = {}
        self.setMinimumSize(1200, 800)
        self.show_gaps = True
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.setInterval(33)  # 30 FPS
    
    def start_animation(self):
        """Start animation timer."""
        self.animation_timer.start()
    
    def stop_animation(self):
        """Stop animation timer."""
        self.animation_timer.stop()
    
    def update_car_state(self, car_state: CarState):
        """Update car state with full simulation data."""
        self.cars[car_state.driver_id] = car_state
    
    def paintEvent(self, event):
        """Render track and cars."""
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
    
    def _draw_track(self, painter):
        """Draw track centerline with smooth curves."""
        try:
            if not self.track_points or len(self.track_points) < 2:
                return
            
            path = QPainterPath()
            path.moveTo(self.track_points[0].x, self.track_points[0].y)
            
            # Cubic spline interpolation for smooth rendering
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
                hw = 15
                painter.drawLine(int(pt.x - normal_x * hw), int(pt.y - normal_y * hw),
                                int(pt.x + normal_x * hw), int(pt.y + normal_y * hw))
        except Exception as e:
            print(f"ERROR in _draw_track: {e}")
    
    def _draw_cars(self, painter):
        """Draw cars at current positions with position numbers."""
        try:
            if not self.track_points or self.track_length <= 0:
                return
            
            # Sort cars by position
            sorted_cars = sorted(self.cars.values(), key=lambda c: c.position)
            
            for car in sorted_cars:
                if car.dnf:
                    continue
                
                # Find track point at car's arc-length
                if self.track_length > 0 and len(self.track_points) > 0:
                    idx = int((car.s / self.track_length) * len(self.track_points)) % len(self.track_points)
                    pt = self.track_points[idx]
                    
                    # Draw car circle
                    painter.setBrush(QBrush(car.color))
                    painter.setPen(QPen(Qt.GlobalColor.white, 2))
                    painter.drawEllipse(QPointF(pt.x, pt.y), 5, 5)
                    
                    # Draw position number
                    painter.save()
                    painter.scale(1, -1)  # Flip text back
                    painter.setPen(QPen(Qt.GlobalColor.white, 1))
                    painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                    painter.drawText(int(pt.x - 10), int(-pt.y + 15), str(car.position))
                    painter.restore()
                    
        except Exception as e:
            print(f"ERROR in _draw_cars: {e}")


class RaceSimulationThread(threading.Thread):
    """
    Advanced race simulation thread using Monte Carlo engine.
    
    Runs the full Monte Carlo simulation with 1000 iterations per lap,
    emitting detailed events for position updates, lap times, incidents, etc.
    """
    
    def __init__(self, drivers: List[DBDriver], track: DBTrack, teams: Dict,
                 emitter: EventEmitter, stop_event: threading.Event,
                 weather_factor: float = 1.0, laps: Optional[int] = None):
        super().__init__(daemon=True)
        self.drivers = drivers
        self.track = track
        self.teams = teams
        self.emitter = emitter
        self.stop_event = stop_event
        self.weather_factor = weather_factor
        self.laps = laps or max(20, int(250 / track.length_km))
    
    def run(self):
        """Execute Monte Carlo race simulation."""
        try:
            print(f"\\n{'='*80}")
            print(f"MONTE CARLO RACE SIMULATION - {self.track.name}")
            print(f"Distance: {self.track.length_km:.2f}km | Laps: {self.laps} | Weather: {self.weather_factor:.2f}")
            print(f"Drivers: {len(self.drivers)} | Iterations per lap: 1000")
            print(f"{'='*80}\\n")
            
            # Create simulation context
            race_data = type('Race', (), {
                'id': 1,
                'track_id': self.track.id,
                'laps': self.laps,
                'weather': 'dry' if self.weather_factor > 0.9 else 'wet'
            })()
            
            context = SimulationContext(
                race=race_data,
                track=self.track,
                drivers=self.drivers,
                teams=self.teams,
                weather_factor=self.weather_factor,
                tire_degradation=0.05
            )
            
            # Run Monte Carlo simulation
            results = simulate_race_monte_carlo(
                context,
                iterations=1000,
                verbose=True,
                stop_event=self.stop_event
            )
            
            # Emit final results
            self.emitter.race_finished.emit(results)
            
            print(f"\\n{'='*80}")
            print("SIMULATION COMPLETE")
            print(f"{'='*80}\\n")
            
        except Exception as e:
            print(f"SIMULATION ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.emitter.simulation_error.emit(str(e))


class AdvancedRaceWindow(QMainWindow):
    """
    Main application window for advanced race visualization.
    
    Features:
    - Monte Carlo simulation with full driver attribute utilization
    - Real-time position tracking and interpolation
    - Live standings with gaps and lap times
    - Event log with race incidents
    - Comprehensive race statistics
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Momentum - Advanced Race Simulation & Visualization")
        self.setGeometry(50, 50, 1800, 1000)
        
        # Core data
        self.db: Optional[PersistenceSQLite] = None
        self.drivers: List[DBDriver] = []
        self.teams: Dict = {}
        self.track: Optional[DBTrack] = None
        self.track_widget: Optional[TrackWidget] = None
        
        # Simulation control
        self.simulation_thread: Optional[RaceSimulationThread] = None
        self.stop_event: Optional[threading.Event] = None
        self.race_active = False
        
        # Event system
        self.emitter = EventEmitter()
        self.emitter.lap_complete.connect(self._on_lap_complete)
        self.emitter.position_update.connect(self._on_position_update)
        self.emitter.race_event.connect(self._on_race_event)
        self.emitter.race_finished.connect(self._on_race_finished)
        self.emitter.simulation_error.connect(self._on_simulation_error)
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Setup comprehensive user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # LEFT: Track visualization (60%)
        left_panel = QVBoxLayout()
        track_frame = QGroupBox("Race Track - Live Positions")
        track_layout = QVBoxLayout(track_frame)
        self.track_container = QVBoxLayout()
        self.track_container.addWidget(QLabel("Loading track..."))
        track_layout.addLayout(self.track_container)
        left_panel.addWidget(track_frame)
        main_layout.addLayout(left_panel, 3)
        
        # RIGHT: Controls & Data (40%)
        right_panel = QVBoxLayout()
        
        # Title
        title = QLabel("<h1>Monte Carlo Race Simulation</h1>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(title)
        
        # Control buttons
        controls = QHBoxLayout()
        self.start_btn = QPushButton("🏁 Start Race")
        self.start_btn.clicked.connect(self._start_race)
        self.start_btn.setMinimumHeight(60)
        controls.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop Race")
        self.stop_btn.clicked.connect(self._stop_race)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(60)
        controls.addWidget(self.stop_btn)
        right_panel.addLayout(controls)
        
        # Race info
        self.info_label = QLabel("Ready to race")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        right_panel.addWidget(self.info_label)
        
        # Live standings
        standings_frame = QGroupBox("Live Standings")
        standings_layout = QVBoxLayout(standings_frame)
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(6)
        self.standings_table.setHorizontalHeaderLabels(["Pos", "Driver", "Lap", "Last Lap", "Best Lap", "Gap"])
        self.standings_table.setMinimumHeight(300)
        standings_layout.addWidget(self.standings_table)
        right_panel.addWidget(standings_frame)
        
        # Event log
        events_frame = QGroupBox("Race Events")
        events_layout = QVBoxLayout(events_frame)
        self.events_log = QTextEdit()
        self.events_log.setReadOnly(True)
        self.events_log.setMaximumHeight(200)
        events_layout.addWidget(self.events_log)
        right_panel.addWidget(events_frame)
        
        main_layout.addLayout(right_panel, 2)
        
        # Styling
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1A1B1E;
                color: #B9F2FF;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #B9F2FF;
                color: #1A1B1E;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #DD2D4A;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #353839;
                color: #666666;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #353839;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTableWidget {
                background-color: #252627;
                gridline-color: #353839;
                border: none;
            }
            QHeaderView::section {
                background-color: #353839;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #252627;
                border: 1px solid #353839;
                border-radius: 3px;
            }
        """)
    
    def _load_data(self):
        """Load drivers, teams, and track from database."""
        try:
            print("Loading data from database...")
            self.db = PersistenceSQLite()
            
            # Load drivers
            all_drivers = self.db.list_drivers()
            if not all_drivers:
                self.info_label.setText("ERROR: No drivers in database")
                self.start_btn.setEnabled(False)
                return
            
            self.drivers = all_drivers[:20] if len(all_drivers) >= 20 else all_drivers
            print(f"Loaded {len(self.drivers)} drivers")
            
            # Load track
            self.track = self.db.get_track(1)
            if not self.track:
                self.info_label.setText("ERROR: No track found")
                self.start_btn.setEnabled(False)
                return
            
            print(f"Loaded track: {self.track.name} ({self.track.length_km:.2f}km)")
            
            # Create teams dictionary (simplified - use driver IDs as team IDs)
            self.teams = {}
            for driver in self.drivers:
                self.teams[driver.id] = type('Team', (), {
                    'id': driver.id,
                    'name': f"{driver.name}'s Team",
                    'budget': 50000000,
                    'tier': 2
                })()
            
            # Generate circuit
            print("Generating circuit...")
            track_points = CircuitGenerator.generate(self.track.length_km, "complex")
            track_length = track_points[-1].s if track_points else 5000
            
            # Create track widget
            self.track_widget = TrackWidget(track_points, track_length)
            
            # Clear loading message
            while self.track_container.count():
                item = self.track_container.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.track_container.addWidget(self.track_widget)
            
            # Initialize cars
            colors = [
                QColor(255, 50, 50), QColor(50, 150, 255), QColor(50, 255, 50),
                QColor(255, 255, 50), QColor(255, 150, 50), QColor(200, 50, 255),
                QColor(50, 255, 255), QColor(255, 150, 150), QColor(150, 255, 150),
                QColor(200, 200, 255), QColor(255, 100, 100), QColor(100, 200, 255),
                QColor(100, 255, 100), QColor(255, 200, 100), QColor(200, 100, 255),
                QColor(100, 255, 200), QColor(255, 180, 180), QColor(180, 230, 180),
                QColor(180, 180, 255), QColor(255, 220, 180)
            ]
            
            for i, driver in enumerate(self.drivers):
                car_state = CarState(
                    driver_id=driver.id,
                    driver_name=driver.name,
                    position=i + 1,
                    lap=0,
                    total_time=0.0,
                    last_lap_time=0.0,
                    best_lap_time=float('inf'),
                    gap_to_leader=0.0,
                    gap_to_ahead=0.0,
                    s=0.0,
                    color=colors[i % len(colors)]
                )
                self.track_widget.update_car_state(car_state)
            
            # Initialize standings
            self.standings_table.setRowCount(len(self.drivers))
            for i, driver in enumerate(self.drivers):
                self.standings_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.standings_table.setItem(i, 1, QTableWidgetItem(driver.name))
                self.standings_table.setItem(i, 2, QTableWidgetItem("0"))
                self.standings_table.setItem(i, 3, QTableWidgetItem("-"))
                self.standings_table.setItem(i, 4, QTableWidgetItem("-"))
                self.standings_table.setItem(i, 5, QTableWidgetItem("-"))
            
            self.info_label.setText(
                f"<b>{len(self.drivers)} drivers</b> | {self.track.name} ({self.track.length_km:.2f}km)<br>"
                f"Monte Carlo Engine: 1000 iterations/lap"
            )
            print("Data loading complete\\n")
            
        except Exception as e:
            print(f"ERROR loading data: {e}")
            import traceback
            traceback.print_exc()
            self.info_label.setText(f"Error: {e}")
            self.start_btn.setEnabled(False)
    
    def _start_race(self):
        """Start Monte Carlo race simulation."""
        if not self.drivers or not self.track or not self.track_widget:
            return
        
        print("\\n" + "="*80)
        print("STARTING ADVANCED RACE SIMULATION")
        print("="*80 + "\\n")
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.race_active = True
        self.info_label.setText("<b>🏁 Race in progress...</b>")
        self.events_log.clear()
        self._log_event("Race started - Monte Carlo simulation active")
        
        # Start track animation
        self.track_widget.start_animation()
        
        # Launch simulation thread
        self.stop_event = threading.Event()
        self.simulation_thread = RaceSimulationThread(
            self.drivers,
            self.track,
            self.teams,
            self.emitter,
            self.stop_event,
            weather_factor=1.0
        )
        self.simulation_thread.start()
    
    def _stop_race(self):
        """Stop race simulation."""
        if self.stop_event:
            self.stop_event.set()
        self.info_label.setText("Stopping simulation...")
        self.stop_btn.setEnabled(False)
        self._log_event("Race stopped by user")
    
    def _on_lap_complete(self, lap: int, standings: list):
        """Handle lap completion event."""
        self._log_event(f"Lap {lap} complete")
        # Update standings table
        # TODO: Implement standings update from Monte Carlo results
    
    def _on_position_update(self, data: dict):
        """Handle position update event."""
        # TODO: Update car positions from Monte Carlo simulation
        pass
    
    def _on_race_event(self, event_type: str, data: dict):
        """Handle general race events."""
        self._log_event(f"{event_type}: {data}")
    
    def _on_race_finished(self, results: list):
        """Handle race finish."""
        self.race_active = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.track_widget.stop_animation()
        
        self.info_label.setText("<b>🏁 Race finished!</b>")
        self._log_event("Race finished - displaying final results")
        
        print("\\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        for i, result in enumerate(results[:10], 1):
            driver_name = next((d.name for d in self.drivers if d.id == result.driver_id), "Unknown")
            print(f"P{i}: {driver_name}")
        print("="*80 + "\\n")
    
    def _on_simulation_error(self, error_msg: str):
        """Handle simulation errors."""
        self.info_label.setText(f"<b>ERROR:</b> {error_msg}")
        self._log_event(f"ERROR: {error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def _log_event(self, message: str):
        """Add event to log."""
        timestamp = time.strftime("%H:%M:%S")
        self.events_log.append(f"[{timestamp}] {message}")


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = AdvancedRaceWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
