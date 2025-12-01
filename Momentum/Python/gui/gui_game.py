"""Minimal PyQt6 GUI for the basic-race MVP.

Features:
- Start / Stop controls
- Strategy selector (placeholder)
- Live event feed (pit, incident)
- Standings table updated at the end
- Uses `simulate_race` directly and subscribes to `event_callback`

The module handles missing PyQt6 by printing an explanatory message so it
can be imported in CI or headless environments.
"""
from __future__ import annotations

import os
import threading
import time
import math
from datetime import datetime
from typing import Optional, TYPE_CHECKING

try:
    from PyQt6 import QtWidgets, QtCore
    from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PyQt6.QtCore import pyqtSignal, QObject
    HAS_QT = True
except Exception:  # pragma: no cover - optional dependency
    HAS_QT = False

if TYPE_CHECKING:
    # Help static type checkers (Pylance) resolve Qt symbols when available
    from PyQt6 import QtWidgets as _QtWidgets  # noqa: F401
    from PyQt6.QtWidgets import QApplication as _QApplication, QMainWindow as _QMainWindow, QMessageBox as _QMessageBox  # noqa: F401
    from PyQt6.QtCore import QObject as _QObject, pyqtSignal as _pyqtSignal  # noqa: F401

# If PyQt6 isn't present at analysis/runtime define lightweight Any fallbacks
from typing import Any
if not HAS_QT:
    QtWidgets: Any = None
    QtCore: Any = None
    QApplication: Any = None
    QMainWindow: Any = None
    QMessageBox: Any = None
    pyqtSignal: Any = None
    QObject: Any = None

# Define an EventEmitter that uses Qt signals when available, otherwise a stub.
# We avoid redeclaring the same symbol twice (Pylance warns) by creating a
# small adapter: when Qt is available we create a thin subclass, otherwise a
# plain Python stub is used and assigned to the name `EventEmitter` once.
if TYPE_CHECKING:
    # Provide a typing-time-only EventEmitter shape so static analysis is happy.
    class EventEmitter:  # pragma: no cover - typing-only stub
        event: Any

        def __init__(self):
            ...

        def connect(self, *_args, **_kwargs):
            ...

        def emit(self, *_args, **_kwargs):
            ...
else:
    if HAS_QT:
        class _QtEventEmitter(QObject):
            event = pyqtSignal(object)

        EventEmitter = _QtEventEmitter
    else:
        class EventEmitter:
            def __init__(self):
                self.event = self

            def connect(self, *_args, **_kwargs):
                return None

            def emit(self, *_args, **_kwargs):
                return None

from persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race

# Global settings
class AppSettings:
    display_mode = "borderless"  # windowed, borderless, fullscreen


class TelemetryLogger:
    def __init__(self, out_dir: str = "saves"):
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(out_dir, f"telemetry_{ts}.csv")
        # write header
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("type,subtype,lap,driver_id,extra\n")

    def handle(self, event: dict) -> None:
        etype = event.get("type")
        subtype = event.get("subtype")
        lap = event.get("lap")
        driver = event.get("driver_id")
        extra = {}
        if "delay" in event:
            extra["delay"] = event["delay"]
        if "pit_time" in event:
            extra["pit_time"] = event["pit_time"]
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"{etype},{subtype},{lap},{driver},{extra}\n")


class PositionTracker:
    """Track driver positions lap-by-lap for visualization."""
    def __init__(self):
        self.laps = []  # List of dicts: {lap_num: int, positions: {driver_id: pos}}
        self.driver_names = {}  # {driver_id: name}
    
    def add_lap(self, lap_num: int, standings: list):
        """Record positions for a lap."""
        positions = {}
        for s in standings:
            driver_id = s.get("driver_id")
            position = s.get("position")
            name = s.get("name", f"Driver {driver_id}")
            if driver_id:
                positions[driver_id] = position
                self.driver_names[driver_id] = name
        self.laps.append({"lap_num": lap_num, "positions": positions})
    
    def get_position_history(self, driver_id):
        """Get list of positions for a driver across all laps."""
        return [lap["positions"].get(driver_id) for lap in self.laps]
    
    def get_all_drivers(self):
        """Get list of all driver IDs that participated."""
        return list(self.driver_names.keys())


if not HAS_QT:
    def main():
        print("PyQt6 is not installed. Install it (`pip install PyQt6`) to run the GUI.")

    if __name__ == "__main__":
        main()

else:


    if TYPE_CHECKING:
        _BaseWindow = _QMainWindow
        _BaseDialog = _QtWidgets.QDialog
    elif HAS_QT:
        _BaseWindow = QMainWindow
        _BaseDialog = QtWidgets.QDialog
    else:
        _BaseWindow = object
        _BaseDialog = object


    class DriverSelectionDialog(_BaseDialog):
        """Driver selection screen with attribute visualization and biography."""
        
        def __init__(self, drivers: list, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Select Your Driver")
            self.drivers = drivers
            self.selected_driver = None
            self.setFixedSize(1920, 1080)
            
            # Apply Momentum color scheme
            self.setStyleSheet("""
                QDialog {
                    background-color: #353839;
                    color: #B9F2FF;
                }
                QLabel {
                    color: #B9F2FF;
                }
                QGroupBox {
                    color: #B9F2FF;
                    border: 1px solid #B9F2FF;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
                QListWidget {
                    background-color: #FFFFFF;
                    color: #353839;
                    border: 1px solid #B9F2FF;
                }
                QPushButton {
                    background-color: #B9F2FF;
                    color: #353839;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DD2D4A;
                    color: #FFFFFF;
                }
                QTabWidget::pane {
                    border: 1px solid #B9F2FF;
                    background-color: #353839;
                }
                QTabBar::tab {
                    background-color: #252627;
                    color: #B9F2FF;
                    padding: 8px 16px;
                    border: 1px solid #B9F2FF;
                }
                QTabBar::tab:selected {
                    background-color: #B9F2FF;
                    color: #353839;
                }
            """)
            
            layout = QtWidgets.QHBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            
            # Left panel: driver list
            left_panel = QtWidgets.QVBoxLayout()
            
            title_label = QtWidgets.QLabel("<h1>Available Drivers</h1>")
            try:
                from PyQt6.QtCore import Qt
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            except (ImportError, AttributeError):
                pass
            left_panel.addWidget(title_label)
            
            self.driver_list = QtWidgets.QListWidget()
            self.driver_list.setMinimumWidth(300)
            try:
                from PyQt6.QtGui import QFont
                font = QFont("Inter", 12)
                self.driver_list.setFont(font)
            except (ImportError, AttributeError):
                pass
            for driver in drivers:
                self.driver_list.addItem(f"{driver.name} ({driver.nationality})")
            getattr(self.driver_list.currentRowChanged, "connect")(self.on_driver_selected)
            left_panel.addWidget(self.driver_list)
            
            confirm_btn = QtWidgets.QPushButton("Select Driver")
            confirm_btn.setMinimumHeight(60)
            getattr(confirm_btn.clicked, "connect")(self.accept)
            left_panel.addWidget(confirm_btn)
            
            layout.addLayout(left_panel, 1)
            
            # Right panel: driver details
            right_panel = QtWidgets.QVBoxLayout()
            right_panel.setSpacing(15)
            
            # Biography section
            bio_group = QtWidgets.QGroupBox("Driver Biography")
            bio_group.setFixedHeight(250)
            bio_layout = QtWidgets.QVBoxLayout(bio_group)
            self.bio_label = QtWidgets.QLabel("Select a driver to view details")
            self.bio_label.setWordWrap(True)
            try:
                from PyQt6.QtGui import QFont
                bio_font = QFont("Inter", 11)
                self.bio_label.setFont(bio_font)
            except (ImportError, AttributeError):
                pass
            bio_layout.addWidget(self.bio_label)
            right_panel.addWidget(bio_group)
            
            # Attributes section with tabs for different categories
            attr_tabs = QtWidgets.QTabWidget()
            
            # Core Skills tab
            self.core_canvas = QtWidgets.QLabel()
            self.core_canvas.setFixedSize(1200, 700)
            attr_tabs.addTab(self.core_canvas, "Core Skills")
            
            # Physical & Mental tab
            self.physical_canvas = QtWidgets.QLabel()
            self.physical_canvas.setFixedSize(1200, 700)
            attr_tabs.addTab(self.physical_canvas, "Physical & Mental")
            
            # Technical tab
            self.technical_canvas = QtWidgets.QLabel()
            self.technical_canvas.setFixedSize(1200, 700)
            attr_tabs.addTab(self.technical_canvas, "Technical")
            
            # Discipline Aptitudes tab
            self.discipline_canvas = QtWidgets.QLabel()
            self.discipline_canvas.setFixedSize(1200, 700)
            attr_tabs.addTab(self.discipline_canvas, "Disciplines")
            
            right_panel.addWidget(attr_tabs)
            
            layout.addLayout(right_panel, 3)
            
            # Select first driver by default
            if drivers:
                self.driver_list.setCurrentRow(0)
        
        def on_driver_selected(self, index: int):
            if index < 0 or index >= len(self.drivers):
                return
            
            driver = self.drivers[index]
            self.selected_driver = driver
            
            # Update biography
            age = driver.age
            nationality = driver.nationality
            wins = driver.career_wins
            podiums = driver.career_podiums
            starts = driver.career_starts
            
            bio_html = f"""
            <h3>{driver.name}</h3>
            <p><b>Age:</b> {age} years old</p>
            <p><b>Nationality:</b> {nationality}</p>
            <p><b>Birth Date:</b> {driver.birth_date}</p>
            <hr>
            <h4>Career Statistics</h4>
            <p><b>Race Starts:</b> {starts}</p>
            <p><b>Wins:</b> {wins}</p>
            <p><b>Podiums:</b> {podiums}</p>
            <p><b>Points:</b> {driver.career_points}</p>
            <p><b>Seasons Active:</b> {driver.seasons_active}</p>
            """
            self.bio_label.setText(bio_html)
            
            # Draw attribute charts
            self.draw_radar_chart(self.core_canvas, [
                ("Raw Speed", driver.raw_speed),
                ("Consistency", driver.consistency),
                ("Racecraft", driver.racecraft),
                ("Overtaking", driver.overtaking),
                ("Cornering", driver.cornering_skill),
                ("Braking", driver.braking_technique),
                ("Acceleration", driver.acceleration_control),
                ("Awareness", driver.spatial_awareness),
            ])
            
            self.draw_radar_chart(self.physical_canvas, [
                ("Fitness", driver.physical_fitness),
                ("Reaction", driver.reaction_time),
                ("Focus", driver.concentration),
                ("Pressure", driver.pressure_handling),
                ("G-Force", driver.g_force_tolerance),
                ("Coordination", driver.coordination),
                ("Resilience", driver.mental_resilience),
            ])
            
            self.draw_radar_chart(self.technical_canvas, [
                ("Setup", driver.setup_knowledge),
                ("Mech. Sympathy", driver.mechanical_sympathy),
                ("Tire Mgmt", driver.tire_management),
                ("Fuel Mgmt", driver.fuel_management),
                ("Aero", driver.aerodynamics_understanding),
                ("Data Analysis", driver.data_analysis),
            ])
            
            self.draw_radar_chart(self.discipline_canvas, [
                ("Single Seater", driver.single_seater_aptitude),
                ("Touring Car", driver.touring_car_aptitude),
                ("Rally", driver.rally_aptitude),
                ("Street", driver.street_racing_aptitude),
                ("Drag", driver.drag_racing_aptitude),
                ("Rallycross", driver.rallycross_aptitude),
                ("Endurance", driver.endurance_aptitude),
            ])
        
        def draw_radar_chart(self, canvas: Any, attributes: list):
            """Draw a radar/spider chart for driver attributes."""
            try:
                from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap
                from PyQt6.QtCore import Qt, QPointF
            except ImportError:
                canvas.setText("Chart unavailable")
                return
            
            width = canvas.width()
            height = canvas.height()
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(0x35, 0x38, 0x39))  # Charcoal Grey background
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            center_x = width // 2
            center_y = height // 2
            radius = min(width, height) // 2 - 60
            
            num_attrs = len(attributes)
            if num_attrs == 0:
                painter.end()
                canvas.setPixmap(pixmap)
                return
            
            # Draw concentric circles for scale (0, 25, 50, 75, 100)
            painter.setPen(QPen(QColor(0x60, 0x60, 0x60), 1))  # Subtle grid lines
            for scale in [0.25, 0.5, 0.75, 1.0]:
                r = int(radius * scale)
                painter.drawEllipse(center_x - r, center_y - r, r * 2, r * 2)
            
            # Draw axes and labels
            painter.setPen(QPen(QColor(0xB9, 0xF2, 0xFF), 1))  # Cyan Blue axes
            painter.setFont(QFont("Inter", 9))
            
            points = []
            for i, (label, value) in enumerate(attributes):
                angle = 2 * math.pi * i / num_attrs - math.pi / 2
                
                # Draw axis line
                end_x = center_x + radius * math.cos(angle)
                end_y = center_y + radius * math.sin(angle)
                painter.drawLine(center_x, center_y, int(end_x), int(end_y))
                
                # Draw label
                label_dist = radius + 20
                label_x = center_x + label_dist * math.cos(angle)
                label_y = center_y + label_dist * math.sin(angle)
                painter.drawText(int(label_x - 40), int(label_y - 10), 80, 20,
                               Qt.AlignmentFlag.AlignCenter, label)
                
                # Calculate point for value
                value_normalized = min(max(value, 0), 100) / 100.0
                point_x = center_x + radius * value_normalized * math.cos(angle)
                point_y = center_y + radius * value_normalized * math.sin(angle)
                points.append(QPointF(point_x, point_y))
            
            # Draw filled polygon for attributes
            if points:
                painter.setBrush(QBrush(QColor(0xB9, 0xF2, 0xFF, 100)))  # Cyan Blue with transparency
                painter.setPen(QPen(QColor(0xB9, 0xF2, 0xFF), 2))  # Cyan Blue outline
                from PyQt6.QtGui import QPolygonF as _QPolygonF
                polygon = _QPolygonF(points)
                painter.drawPolygon(polygon)
                
                # Draw points
                painter.setBrush(QBrush(QColor(0xDD, 0x2D, 0x4A)))  # Racing Red points for contrast
                for point in points:
                    painter.drawEllipse(point, 4, 4)
            
            painter.end()
            canvas.setPixmap(pixmap)
        
        def get_selected_driver(self):
            return self.selected_driver


    class RaceResultsGraph(QtWidgets.QWidget):
        """Widget to display race position changes over laps as a line graph."""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.position_tracker = None
        
        def set_data(self, position_tracker: PositionTracker):
            """Load position tracking data and trigger repaint."""
            self.position_tracker = position_tracker
            self.update()
        
        def paintEvent(self, event):
            """Draw the position graph."""
            if not self.position_tracker or not self.position_tracker.laps:
                return
            
            try:
                from PyQt6.QtGui import QPainter, QPen, QColor, QFont
                from PyQt6.QtCore import Qt
            except ImportError:
                return
            
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Set background
            painter.fillRect(self.rect(), QColor(0x35, 0x38, 0x39))  # Charcoal Grey
            
            # Chart dimensions with proper margins to prevent overflow
            margin_left = 50
            margin_right = 150  # Extra space for driver names
            margin_top = 50
            margin_bottom = 50
            width = self.width() - margin_left - margin_right
            height = self.height() - margin_top - margin_bottom
            
            num_laps = len(self.position_tracker.laps)
            drivers = self.position_tracker.get_all_drivers()
            max_position = len(drivers)
            
            if num_laps < 2 or max_position < 1:
                return
            
            # Draw title
            painter.setPen(QPen(QColor(0xB9, 0xF2, 0xFF)))  # Cyan Blue
            painter.setFont(QFont("Inter", 14, 600))
            painter.drawText(margin_left, 30, "Race Position Changes")
            
            # Draw grid lines and labels
            painter.setPen(QPen(QColor(0x60, 0x60, 0x60), 1))  # Subtle grid
            painter.setFont(QFont("Inter", 9))
            
            # Vertical grid (positions)
            for pos in range(1, max_position + 1):
                y = margin_top + (pos - 1) * (height / max(max_position - 1, 1))
                painter.drawLine(margin_left, int(y), margin_left + width, int(y))
                painter.setPen(QPen(QColor(0xB9, 0xF2, 0xFF)))  # Cyan labels
                painter.drawText(10, int(y) + 5, f"P{pos}")
                painter.setPen(QPen(QColor(0x60, 0x60, 0x60), 1))
            
            # Horizontal grid (laps)
            for lap_idx in range(0, num_laps, max(1, num_laps // 10)):
                x = margin_left + lap_idx * (width / max(num_laps - 1, 1))
                painter.drawLine(int(x), margin_top, int(x), margin_top + height)
                painter.setPen(QPen(QColor(0xB9, 0xF2, 0xFF)))  # Cyan labels
                painter.drawText(int(x) - 10, margin_top + height + 20, f"L{lap_idx}")
                painter.setPen(QPen(QColor(0x60, 0x60, 0x60), 1))
            
            # Draw position lines for each driver
            colors = [
                QColor(0xB9, 0xF2, 0xFF),  # Cyan Blue (brand)
                QColor(0xDD, 0x2D, 0x4A),  # Racing Red (brand)
                QColor(0xF5, 0xF5, 0xF5),  # Snow White (brand)
                QColor(0xFF, 0xA5, 0x00),  # Orange
                QColor(0x00, 0xFF, 0x7F),  # Spring Green
                QColor(0xFF, 0xFF, 0x00),  # Yellow
                QColor(0xFF, 0x00, 0xFF),  # Magenta
                QColor(0x00, 0xBF, 0xFF),  # Deep Sky Blue
                QColor(0xFF, 0x69, 0xB4),  # Hot Pink
                QColor(0x7F, 0xFF, 0x00),  # Chartreuse
            ]
            
            for idx, driver_id in enumerate(drivers[:10]):  # Show top 10
                color = colors[idx % len(colors)]
                painter.setPen(QPen(color, 2))
                
                positions = self.position_tracker.get_position_history(driver_id)
                points = []
                
                for lap_idx, pos in enumerate(positions):
                    if pos is None:
                        continue
                    x = margin_left + lap_idx * (width / max(num_laps - 1, 1))
                    y = margin_top + (pos - 1) * (height / max(max_position - 1, 1))
                    points.append((int(x), int(y)))
                
                # Draw line segments
                for i in range(len(points) - 1):
                    painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
                
                # Draw driver name at final position
                if points:
                    final_x, final_y = points[-1]
                    driver_name = self.position_tracker.driver_names.get(driver_id, f"D{driver_id}")
                    painter.drawText(final_x + 5, final_y + 5, driver_name[:15])
            
            painter.end()


    class MainWindow(_BaseWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Momentum - Motorsport Management")
            self.apply_display_mode()
            
            # Apply Momentum color scheme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #353839;
                    color: #B9F2FF;
                }
                QWidget {
                    background-color: #353839;
                    color: #B9F2FF;
                }
                QLabel {
                    color: #B9F2FF;
                }
                QPushButton {
                    background-color: #B9F2FF;
                    color: #353839;
                    border: none;
                    padding: 10px 20px;
                    font-size: 16px;
                    font-weight: bold;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #DD2D4A;
                    color: #FFFFFF;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
                QListWidget {
                    background-color: #252627;
                    color: #B9F2FF;
                    border: 1px solid #B9F2FF;
                }
                QTableWidget {
                    background-color: #FFFFFF;
                    color: #353839;
                    border: 1px solid #B9F2FF;
                    gridline-color: #B9F2FF;
                    alternate-background-color: #F5F5F5;
                }
                QTableWidget::item {
                    padding: 8px;
                }
                QHeaderView::section {
                    background-color: #B9F2FF;
                    color: #353839;
                    padding: 10px;
                    border: 1px solid #353839;
                    font-weight: bold;
                    font-size: 14px;
                }
                QProgressBar {
                    border: 1px solid #B9F2FF;
                    background-color: #252627;
                    text-align: center;
                    color: #B9F2FF;
                }
                QProgressBar::chunk {
                    background-color: #B9F2FF;
                }
            """)

            # Central widget with stacked layout for menu/race views
            self.central = QtWidgets.QWidget()
            self.setCentralWidget(self.central)
            self.main_layout = QtWidgets.QStackedLayout(self.central)
            
            # Create main menu screen
            self.menu_screen = self._create_menu_screen()
            self.main_layout.addWidget(self.menu_screen)
            
            # Create race screen
            self.race_screen = self._create_race_screen()
            self.main_layout.addWidget(self.race_screen)
            
            # Start on menu screen
            self.main_layout.setCurrentIndex(0)

            self.emitter = EventEmitter()
            try:
                getattr(self.emitter.event, "connect")(self.on_event)
            except Exception:
                # Signal stubs may not support connect; ignore in that case
                pass

            self._thread: Optional[threading.Thread] = None
            self._stop_flag = threading.Event()
            self._stop_event: Optional[threading.Event] = None
            self.telemetry = TelemetryLogger()
            self.selected_driver = None
            self.position_tracker = PositionTracker()
        
        def apply_display_mode(self):
            """Apply the current display mode setting."""
            try:
                from PyQt6.QtCore import Qt
            except ImportError:
                return
            
            if AppSettings.display_mode == "fullscreen":
                self.showFullScreen()
            elif AppSettings.display_mode == "borderless":
                self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
                self.setGeometry(0, 0, 1920, 1080)
                self.show()
            else:  # windowed
                self.setWindowFlags(Qt.WindowType.Window)
                self.resize(1920, 1080)
                self.show()

        def _create_menu_screen(self):
            """Create the main menu screen with Choose Driver and Exit buttons."""
            menu_widget = QtWidgets.QWidget()
            menu_layout = QtWidgets.QVBoxLayout(menu_widget)
            
            # Add spacing at top
            menu_layout.addStretch(1)
            
            # Title
            title = QtWidgets.QLabel("<h1>Momentum</h1><h3>Motorsport Management Simulator</h3>")
            try:
                from PyQt6.QtCore import Qt as _Qt
                title.setAlignment(_Qt.AlignmentFlag.AlignCenter)
            except (ImportError, AttributeError):
                pass
            menu_layout.addWidget(title)
            
            menu_layout.addStretch(1)
            
            # Buttons container
            button_container = QtWidgets.QWidget()
            button_layout = QtWidgets.QVBoxLayout(button_container)
            button_layout.setSpacing(20)
            
            # Choose Driver button
            choose_driver_btn = QtWidgets.QPushButton("Choose Driver")
            choose_driver_btn.setMinimumHeight(50)
            choose_driver_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
            getattr(choose_driver_btn.clicked, "connect")(self.on_choose_driver)
            button_layout.addWidget(choose_driver_btn)
            
            # Options button
            options_btn = QtWidgets.QPushButton("Options")
            options_btn.setMinimumHeight(50)
            options_btn.setStyleSheet("font-size: 16px;")
            getattr(options_btn.clicked, "connect")(self.show_options)
            button_layout.addWidget(options_btn)
            
            # Exit button
            exit_btn = QtWidgets.QPushButton("Exit")
            exit_btn.setMinimumHeight(50)
            exit_btn.setStyleSheet("font-size: 16px;")
            getattr(exit_btn.clicked, "connect")(self.close)
            button_layout.addWidget(exit_btn)
            
            # Center the buttons
            try:
                from PyQt6.QtCore import Qt as _Qt
                button_layout.setAlignment(_Qt.AlignmentFlag.AlignCenter)
            except (ImportError, AttributeError):
                pass
            menu_layout.addWidget(button_container)
            
            menu_layout.addStretch(2)
            
            return menu_widget
        
        def _create_race_screen(self):
            """Create the race screen with controls and standings."""
            race_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(race_widget)
            
            # Top bar with controls
            controls = QtWidgets.QHBoxLayout()
            
            # Start/Stop buttons
            self.start_btn = QtWidgets.QPushButton("Start Race")
            self.stop_btn = QtWidgets.QPushButton("Stop Race")
            self.stop_btn.setEnabled(False)
            controls.addWidget(self.start_btn)
            controls.addWidget(self.stop_btn)
            
            controls.addStretch()
            
            # View Results Graph button
            self.view_graph_btn = QtWidgets.QPushButton("View Position Graph")
            self.view_graph_btn.setEnabled(False)
            getattr(self.view_graph_btn.clicked, "connect")(self.show_results_graph)
            controls.addWidget(self.view_graph_btn)
            
            # Back to menu button
            back_btn = QtWidgets.QPushButton("Back to Menu")
            getattr(back_btn.clicked, "connect")(self.back_to_menu)
            controls.addWidget(back_btn)
            
            layout.addLayout(controls)
            
            # Progress bar
            self.progress = QtWidgets.QProgressBar()
            layout.addWidget(self.progress)
            
            # Tabs for different views
            self.race_tabs = QtWidgets.QTabWidget()
            
            # Live view tab (splitter with event feed and standings)
            live_widget = QtWidgets.QWidget()
            live_layout = QtWidgets.QVBoxLayout(live_widget)
            
            splitter = QtWidgets.QSplitter()
            
            # Event feed
            self.event_list = QtWidgets.QListWidget()
            splitter.addWidget(self.event_list)
            
            # Standings table
            self.table = QtWidgets.QTableWidget(0, 4)
            self.table.setHorizontalHeaderLabels(["Pos", "#", "Driver", "Time"])
            self.table.setAlternatingRowColors(True)
            try:
                from PyQt6.QtWidgets import QHeaderView
                header = self.table.horizontalHeader()
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
                header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            except (ImportError, AttributeError):
                pass
            splitter.addWidget(self.table)
            
            live_layout.addWidget(splitter)
            self.race_tabs.addTab(live_widget, "Live Race")
            
            # Results graph tab
            self.results_graph = RaceResultsGraph()
            self.race_tabs.addTab(self.results_graph, "Position Graph")
            
            layout.addWidget(self.race_tabs)
            
            # Wire up start/stop buttons
            getattr(self.start_btn.clicked, "connect")(self.start_race)
            getattr(self.stop_btn.clicked, "connect")(self.stop_race)
            
            # Initialize emitter
            self.emitter = EventEmitter()
            try:
                getattr(self.emitter.event, "connect")(self.on_event)
            except Exception:
                pass
            
            return race_widget

        def show_options(self):
            """Show options dialog for display settings."""
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Options")
            dialog.setFixedSize(500, 300)
            dialog.setStyleSheet(self.styleSheet())
            
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setSpacing(20)
            
            # Title
            title = QtWidgets.QLabel("<h2>Display Settings</h2>")
            try:
                from PyQt6.QtCore import Qt
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            except (ImportError, AttributeError):
                pass
            layout.addWidget(title)
            
            # Display mode group
            mode_group = QtWidgets.QGroupBox("Display Mode")
            mode_layout = QtWidgets.QVBoxLayout(mode_group)
            
            self.windowed_radio = QtWidgets.QRadioButton("Windowed (1920x1080)")
            self.borderless_radio = QtWidgets.QRadioButton("Borderless Windowed (1920x1080)")
            self.fullscreen_radio = QtWidgets.QRadioButton("Fullscreen")
            
            # Set current mode
            if AppSettings.display_mode == "windowed":
                self.windowed_radio.setChecked(True)
            elif AppSettings.display_mode == "borderless":
                self.borderless_radio.setChecked(True)
            else:
                self.fullscreen_radio.setChecked(True)
            
            mode_layout.addWidget(self.windowed_radio)
            mode_layout.addWidget(self.borderless_radio)
            mode_layout.addWidget(self.fullscreen_radio)
            layout.addWidget(mode_group)
            
            layout.addStretch()
            
            # Buttons
            button_layout = QtWidgets.QHBoxLayout()
            apply_btn = QtWidgets.QPushButton("Apply")
            cancel_btn = QtWidgets.QPushButton("Cancel")
            
            def apply_settings():
                if self.windowed_radio.isChecked():
                    AppSettings.display_mode = "windowed"
                elif self.borderless_radio.isChecked():
                    AppSettings.display_mode = "borderless"
                else:
                    AppSettings.display_mode = "fullscreen"
                self.apply_display_mode()
                dialog.accept()
            
            getattr(apply_btn.clicked, "connect")(apply_settings)
            getattr(cancel_btn.clicked, "connect")(dialog.reject)
            
            button_layout.addWidget(apply_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec()
        
        def on_choose_driver(self):
            """Handle Choose Driver button - show driver selection then switch to race screen."""
            db = PersistenceSQLite()
            db.ensure_schema()
            drivers = []
            for did in range(1, 21):
                d = db.get_driver(did)
                if d is not None:
                    drivers.append(d)
            
            if len(drivers) == 0:
                db.seed_sample_data(count=20)
                drivers = db.list_drivers()
            
            if not drivers:
                QMessageBox.warning(self, "No Drivers", "No drivers available for selection.")
                return
            
            dialog = DriverSelectionDialog(drivers, self)
            if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                return
            
            self.selected_driver = dialog.get_selected_driver()
            if not self.selected_driver:
                return
            
            # Switch to race screen
            self.main_layout.setCurrentIndex(1)
            self.append_event(f"Selected driver: {self.selected_driver.name}")
            self.setWindowTitle(f"Momentum - {self.selected_driver.name}")
        
        def show_results_graph(self):
            """Switch to the position graph tab."""
            self.race_tabs.setCurrentIndex(1)
        
        def back_to_menu(self):
            """Return to main menu screen."""
            # Stop any running race
            if self._stop_event is not None:
                self._stop_event.set()
            
            # Clear race screen
            self.event_list.clear()
            self.table.setRowCount(0)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.view_graph_btn.setEnabled(False)
            self.position_tracker = PositionTracker()  # Reset tracker
            self.race_tabs.setCurrentIndex(0)  # Back to live view
            
            # Switch to menu
            self.main_layout.setCurrentIndex(0)
            self.setWindowTitle("Momentum - Motorsport Management")

        def _format_time(self, seconds: float) -> str:
            """Format time in seconds as HH:MM:SS.mmm"""
            if seconds is None or seconds >= 1000000000:
                return "DNF"
            
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

        def append_event(self, text: str) -> None:
            self.event_list.addItem(text)
            self.event_list.scrollToBottom()

        def on_event(self, ev: dict) -> None:
            # Called in the Qt main thread via signal
            # Debug: always print incoming events to console for diagnosis
            try:
                print("GUI event:", ev)
            except Exception:
                pass

            et = ev.get("type")
            if et == "lap_start":
                lap = ev.get("lap")
                self.append_event(f"Lap {lap} start")
                # progress estimate (approx)
                # if laps not known, keep indeterminate
            elif et == "pit":
                self.append_event(f"PIT: driver {ev.get('driver_id')} lap {ev.get('lap')}")
            elif et == "incident":
                st = ev.get("subtype")
                self.append_event(f"INCIDENT({st}): driver {ev.get('driver_id')} lap {ev.get('lap')}")
            elif et == "race_finished":
                self.append_event("Race finished")
                results = ev.get("results", [])
                # At race finish show final table (results are minimal dicts)
                self.update_table(results)
                # Enable results graph viewing
                self.view_graph_btn.setEnabled(True)
                self.results_graph.set_data(self.position_tracker)
            elif et == "standings":
                # Live per-lap standings: update table with names and times
                standings = ev.get("standings", [])
                lap = ev.get("lap")
                
                # Track positions for graph
                if lap is not None:
                    self.position_tracker.add_lap(lap, standings)
                
                # Convert standings to table rows with Pos/#/Driver/Time
                self.table.setRowCount(len(standings))
                for i, r in enumerate(standings):
                    pos = r.get("position", i + 1)
                    driver_id = r.get("driver_id", "")
                    name = r.get("name", f"Driver {driver_id}")
                    t = r.get("time_seconds")
                    self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(pos)))
                    self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(driver_id)))
                    self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(name))
                    self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(self._format_time(t)))
            elif et == "error":
                # show errors in the GUI as well as telemetry
                msg = ev.get("message", "Unknown error")
                self.append_event(f"ERROR: {msg}")
                print("GUI error:", msg)
            # write to telemetry
            try:
                self.telemetry.handle(ev)
            except Exception:
                pass

        def update_table(self, results: list):
            """Update table with final race results including driver names."""
            # Need to get driver names from database
            db = PersistenceSQLite()
            driver_names = {}
            for r in results:
                driver_id = r.get("driver_id")
                if driver_id and driver_id not in driver_names:
                    driver = db.get_driver(driver_id)
                    driver_names[driver_id] = driver.name if driver else f"Driver {driver_id}"
            
            self.table.setRowCount(len(results))
            for i, r in enumerate(results):
                pos = r.get("position", i + 1)
                driver_id = r.get("driver_id")
                name = driver_names.get(driver_id, f"Driver {driver_id}")
                t = r.get("time_seconds")
                
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(pos)))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(driver_id)))
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(name))
                self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(self._format_time(t)))

        def _prepare_db_and_drivers(self):
            """Open persistence, ensure schema, and return (db, drivers, track).

            Loads the first 20 drivers by id from the persistent DB if present,
            otherwise falls back to non-destructive demo seeding.
            """
            db = PersistenceSQLite()
            db.ensure_schema()

            drivers = []
            for did in range(1, 21):
                d = db.get_driver(did)
                if d is not None:
                    drivers.append(d)

            if len(drivers) == 0:
                db.seed_sample_data(count=20)
                drivers = db.list_drivers()

            track = db.get_track(1)
            return db, drivers, track

        def _make_event_callback(self):
            """Return an event callback function that forwards events into Qt."""
            def evcb(e: dict):
                try:
                    print("evcb called:", e)
                except Exception:
                    pass
                try:
                    getattr(self.emitter.event, "emit")(e)
                except Exception:
                    pass

            return evcb

        def _emit_safe(self, event: dict):
            try:
                getattr(self.emitter.event, "emit")(event)
            except Exception:
                pass

        def start_race(self):
            """Start the race on a background thread (cooperative cancellation).

            This method orchestrates DB preparation, event callback creation,
            simulator execution and saving results. Most logic is delegated to
            helper methods to keep cognitive complexity low.
            """
            if not self.selected_driver:
                QMessageBox.warning(self, "No Driver", "Please select a driver first.")
                return
            
            self.append_event(f"Starting race with {self.selected_driver.name}...")
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.view_graph_btn.setEnabled(False)
            self._stop_flag.clear()
            self.event_list.clear()
            self.table.setRowCount(0)
            self.position_tracker = PositionTracker()  # Reset tracker for new race
            self.race_tabs.setCurrentIndex(0)  # Switch to live view

            # run simulation in background thread
            def runner():
                results = []
                try:
                    db, drivers, track = self._prepare_db_and_drivers()
                    evcb = self._make_event_callback()

                    # prepare stop event with default lap delay for pacing
                    self._stop_event = threading.Event()
                    lap_delay = 0.5

                    # Run simulator with cooperative stop and per-lap delay
                    results = simulate_race(
                        drivers,
                        track,
                        seed=None,
                        verbose=False,
                        event_callback=evcb,
                        stop_event=self._stop_event,
                        lap_delay=lap_delay,
                    )

                    # save results
                    db.save_race_results(race_id=1, results=results)
                except Exception as exc:
                    self._emit_safe({"type": "error", "message": str(exc)})
                finally:
                    # ensure results exists and emit final event
                    try:
                        _results = results
                    except NameError:
                        _results = []
                    self._emit_safe({"type": "race_finished", "results": [{"driver_id": r.driver_id, "time_seconds": getattr(r, 'time_seconds', None), "position": r.position} for r in _results]})

            self._thread = threading.Thread(target=runner, daemon=True)
            self._thread.start()

        def stop_race(self):
            # cooperative stop: set the stop event so simulate_race can exit early
            if self._stop_event is not None:
                self._stop_event.set()
                self.append_event("Stop requested — attempting to cancel race")
            else:
                # fallback: set legacy flag
                self._stop_flag.set()
                self.append_event("Stop requested (legacy fallback)")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)


    def main():
        app = QApplication([])
        w = MainWindow()
        w.show()
        # No automatic start by default — user initiates runs via the Start button.

        app.exec()


    if __name__ == "__main__":
        main()
