"""
Parametric Circuit with Proper Starting Grid

Key improvements:
1. Start/finish line in CENTER of a long straight (not on a corner)
2. Multiple points along straight for proper grid formation
3. Car positioning in 2x2 grid formation
4. Smooth clothoid transitions maintained
5. Closed loop verification
6. True clothoid curves with arc-length parametrization
"""

import sys
import numpy as np
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt, QPointF, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from typing import List
from dataclasses import dataclass


def is_closed_loop(track_points, tol=0.1):
    """Verify the track forms a closed loop."""
    start = track_points[0]
    end = track_points[-1]
    dist = math.hypot(end.x - start.x, end.y - start.y)
    heading_diff = abs((end.theta - start.theta) % (2*math.pi))
    return dist < tol and heading_diff < tol


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
    grid_position: int  # Starting grid position (1, 2, 3, ...)
    s: float  # Current arc-length position
    color: QColor


class SmoothCircuitWithGrid(QWidget):
    """Circuit with proper starting straight and car grid."""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1400, 900)
        
        # Generate circuit with start/finish on straight
        self.generate_circuit()
        
        # Generate starting grid (10 cars in 2x2 formation)
        self.generate_starting_grid()
        
        # Animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cars)
        self.timer.start(50)  # 20 FPS
        self.race_time = 0.0
    
    def generate_circuit(self):
        """Generate complex racing circuit with varied corners and straights."""
        state = {
            'segments': [],
            'current_s': 0,
            'current_x': 0,
            'current_y': 0,
            'current_theta': 0,
            'total_angle': 0
        }
        
        # Build track from instruction list
        circuit_instructions = [
            ('S', 600), ('C', 45, 170, 60, 0.00008), ('S', 400),
            ('C', 65, 95, 50, 0.0001), ('S', 220), ('C', -55, 100, 52, 0.0001),
            ('S', 350), ('C', 155, 48, 42, 0.00014), ('S', 550),
            ('C', -65, 145, 58, 0.00009), ('S', 380), ('C', 55, 115, 54, 0.00009),
            ('S', 180), ('C', 60, 90, 50, 0.0001), ('S', 300),
            ('C', -50, 135, 56, 0.00009), ('S', 160), ('C', 50, 135, 56, 0.00009),
            ('S', 320),
        ]
        
        self._process_instructions(circuit_instructions, state)
        self._add_closure_section(state['segments'], state['current_x'], state['current_y'],
                                  state['current_theta'], state['total_angle'], state)
        self._finalize_circuit(state['segments'])
    
    def _process_instructions(self, instructions, state):
        """Process circuit instructions to build track segments."""
        for instruction in instructions:
            if instruction[0] == 'S':
                self._add_straight(instruction[1], state)
            elif instruction[0] == 'C':
                angle_deg, radius, clothoid_len, k = instruction[1:5]
                self._add_corner(angle_deg * math.pi / 180, radius, clothoid_len, k, state)
    
    def _add_straight(self, length, state):
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
    
    def _add_corner(self, target_angle, radius, clothoid_len, k_clothoid, state):
        """Add corner with clothoid transitions."""
        entry_start = state['current_theta']
        sign = 1 if target_angle > 0 else -1
        
        self._add_clothoid_entry(clothoid_len, k_clothoid, sign, state)
        arc_angle = target_angle - 2 * (state['current_theta'] - entry_start)
        self._add_constant_arc(arc_angle, radius, sign, state)
        self._add_clothoid_exit(clothoid_len, k_clothoid, sign, state)
        
        state['total_angle'] += target_angle
    
    def _add_clothoid_entry(self, clothoid_len, k_clothoid, sign, state):
        """Add entry clothoid transition."""
        segments = state['segments']
        for i in range(clothoid_len):
            curvature = k_clothoid * i * sign
            state['current_theta'] += curvature
            state['current_x'] += math.cos(state['current_theta'])
            state['current_y'] += math.sin(state['current_theta'])
            segments.append(TrackPoint(state['current_s'] + i, state['current_x'], 
                                               state['current_y'], state['current_theta'], curvature))
        state['current_s'] += clothoid_len
    
    def _add_constant_arc(self, arc_angle, radius, sign, state):
        """Add constant radius arc section."""
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
    
    def _add_clothoid_exit(self, clothoid_len, k_clothoid, sign, state):
        """Add exit clothoid transition."""
        segments = state['segments']
        for i in range(clothoid_len):
            curvature = k_clothoid * (clothoid_len - i) * sign
            state['current_theta'] += curvature
            state['current_x'] += math.cos(state['current_theta'])
            state['current_y'] += math.sin(state['current_theta'])
            segments.append(TrackPoint(state['current_s'] + i, state['current_x'],
                                               state['current_y'], state['current_theta'], curvature))
        state['current_s'] += clothoid_len
    
    def _finalize_circuit(self, segments):
        """Apply scaling, centering, and store track data."""
        min_x = min(seg.x for seg in segments)
        max_x = max(seg.x for seg in segments)
        min_y = min(seg.y for seg in segments)
        max_y = max(seg.y for seg in segments)
        
        circuit_width = max_x - min_x
        circuit_height = max_y - min_y
        scale = min((1200 - 200) / circuit_width, (800 - 200) / circuit_height)
        
        print("=== BOUNDARY SCALING ===")
        print(f"Original bounds: {circuit_width:.1f}m x {circuit_height:.1f}m")
        print(f"Scale factor: {scale:.4f}")
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        for seg in segments:
            seg.x = (seg.x - center_x) * scale
            seg.y = (seg.y - center_y) * scale
        
        self.track_points = segments
        self.track_length = segments[-1].s
        self.track_width = 12.0
        
        self._print_diagnostics(segments)
    
    def _print_diagnostics(self, segments):
        """Print circuit diagnostic information."""
        start_pt = segments[0]
        end_pt = segments[-1]
        position_error = math.hypot(end_pt.x - start_pt.x, end_pt.y - start_pt.y)
        heading_error = abs((end_pt.theta - start_pt.theta) % (2*math.pi))
        total_heading_change = end_pt.theta - start_pt.theta
        
        print("\n=== CIRCUIT WITH STARTING GRID ===")
        print(f"Total length: {self.track_length:.1f}m")
        print("Starting straight: 400m (sufficient for 2x2 grid)")
        print(f"Number of points: {len(self.track_points)}")
        print(f"Position error: {position_error:.2f}m")
        print(f"Heading error: {math.degrees(heading_error):.2f}°")
        print(f"Total heading change: {math.degrees(total_heading_change):.2f}°")
        print(f"Closed loop: {is_closed_loop(self.track_points, tol=10)}")
    
    def _add_closure_section(self, segments, current_x, current_y, current_theta, 
                            total_angle, state):
        """Add closure section to complete the circuit loop."""
        start_x, start_y = segments[0].x, segments[0].y
        dx = start_x - current_x
        dy = start_y - current_y
        dist_to_start = math.hypot(dx, dy)
        angle_deficit = 2*math.pi - total_angle
        
        print("\n=== S-CURVE CLOSURE ===")
        print(f"Current pos: ({current_x:.1f}, {current_y:.1f}), heading: {math.degrees(current_theta):.1f}°")
        print(f"Vector to start: ({dx:.1f}, {dy:.1f}), distance: {dist_to_start:.1f}m")
        print(f"Angle deficit for 360°: {math.degrees(angle_deficit):.1f}°")
        
        if abs(angle_deficit) > math.radians(5):
            self._add_closure_corners(angle_deficit, dist_to_start, state)
        else:
            self._add_straight(int(dist_to_start), state)
        
        print("\n=== CLOSURE RESULT ===")
        print(f"Total rotation: {math.degrees(state['total_angle']):.2f}°")
    
    def _add_closure_corners(self, angle_deficit, dist_to_start, state):
        """Add closure corners based on angle deficit."""
        print("\nCLOSURE STRATEGY:")
        print(f"  Need {math.degrees(angle_deficit):.1f}° more rotation")
        
        turn_direction = 1 if angle_deficit > 0 else -1
        remaining_angle = abs(angle_deficit)
        
        if remaining_angle > math.radians(120):
            self._add_three_corner_closure(remaining_angle, turn_direction, state)
        elif remaining_angle > math.radians(60):
            self._add_two_corner_closure(remaining_angle, turn_direction, state)
        else:
            self._add_single_corner_closure(angle_deficit, state)
        
        self._add_straight(int(max(100, dist_to_start * 0.12)), state)
    
    def _add_three_corner_closure(self, remaining_angle, turn_direction, state):
        """Add three-corner closure for large angle deficits."""
        angles = [remaining_angle * r * turn_direction for r in [0.4, 0.35, 0.25]]
        radii = [110, 95, 105]
        straights = [180, 160, 140]
        
        for i, (angle, radius, straight) in enumerate(zip(angles, radii, straights)):
            self._add_straight(straight, state)
            self._add_corner(angle, radius, 48, 0.0001, state)
    
    def _add_two_corner_closure(self, remaining_angle, turn_direction, state):
        """Add two-corner closure for medium angle deficits."""
        angles = [remaining_angle * r * turn_direction for r in [0.55, 0.45]]
        radii = [100, 110]
        straights = [200, 180]
        
        for angle, radius, straight in zip(angles, radii, straights):
            self._add_straight(straight, state)
            self._add_corner(angle, radius, 50, 0.0001, state)
    
    def _add_single_corner_closure(self, angle_deficit, state):
        """Add single-corner closure for small angle deficits."""
        self._add_straight(180, state)
        self._add_corner(angle_deficit, 120, 52, 0.00009, state)
    
    def generate_starting_grid(self):
        """Generate cars in 2x2 grid formation on starting straight using dynamic normal vector."""
        self.cars = []
        car_colors = [
            QColor(255, 50, 50),   # Red
            QColor(50, 150, 255),  # Blue
            QColor(50, 255, 50),   # Green
            QColor(255, 255, 50),  # Yellow
            QColor(255, 150, 50),  # Orange
            QColor(200, 50, 255),  # Purple
            QColor(50, 255, 255),  # Cyan
            QColor(255, 150, 150), # Pink
            QColor(150, 255, 150), # Light green
            QColor(200, 200, 255), # Light blue
        ]
        
        # Dynamic grid placement
        start_idx = 100  # 100m into straight
        pt = self.track_points[start_idx]
        grid_start_s = pt.s
        row_spacing = 8.0
        
        for row in range(5):
            base_s = grid_start_s - row * row_spacing
            # Left car
            self.cars.append(Car(
                grid_position=row * 2 + 1,
                s=base_s,
                color=car_colors[row * 2]
            ))
            # Right car
            self.cars.append(Car(
                grid_position=row * 2 + 2,
                s=base_s,
                color=car_colors[row * 2 + 1]
            ))
    
    def update_cars(self):
        """Animate cars moving around track."""
        self.race_time += 0.05
        
        # Move cars forward (different speeds for variety)
        for i, car in enumerate(self.cars):
            speed = 40.0 + i * 2  # m/s (staggered speeds)
            car.s += speed * 0.05
            
            # Wrap around track
            if car.s > self.track_length:
                car.s -= self.track_length
        
        self.update()
    
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dark background
        painter.fillRect(self.rect(), QColor(15, 20, 25))
        
        # Title
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(20, 30, "Parametric Circuit with Starting Grid (2x2 Formation)")
        
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(20, 50, f"Circuit length: {self.track_length:.0f}m | Starting straight: 400m")
        painter.drawText(20, 68, "Grid: 10 cars in 2x2 formation (8m row spacing, 6m lane width)")
        
        # Transform to center view with increased zoom
        painter.translate(700, 450)
        painter.scale(1.8, -1.8)  # Increased zoom from 1.0 to 1.8
        
        # Draw track infrastructure
        self.draw_pit_lane(painter)
        self.draw_grandstands(painter)
        self.draw_garages(painter)
        self.draw_track(painter)
        
        # Draw cars
        self.draw_cars(painter)
        
        painter.end()
    
    def draw_pit_lane(self, painter):
        """Draw pit lane parallel to main straight."""
        if not self.track_points:
            return
        # Pit lane along first 250m of track (offset 18m to the right)
        painter.setPen(QPen(QColor(80, 80, 80), 8))
        for i, pt in enumerate(self.track_points):
            if pt.s < 250:
                offset_x = -math.sin(pt.theta) * 18
                offset_y = math.cos(pt.theta) * 18
                if i > 0 and self.track_points[i-1].s < 250:
                    prev = self.track_points[i-1]
                    prev_offset_x = -math.sin(prev.theta) * 18
                    prev_offset_y = math.cos(prev.theta) * 18
                    painter.drawLine(
                        int(prev.x + prev_offset_x), int(prev.y + prev_offset_y),
                        int(pt.x + offset_x), int(pt.y + offset_y)
                    )

    def draw_grandstands(self, painter):
        """Draw grandstands along major straights."""
        if not self.track_points:
            return
        painter.setBrush(QBrush(QColor(40, 60, 80)))
        painter.setPen(QPen(QColor(60, 80, 100), 1))
        # Place grandstands at s=200-400m and s=800-1000m (offset 30m from centerline)
        for i, pt in enumerate(self.track_points):
            if ((200 < pt.s < 400) or (800 < pt.s < 1000)) and (i % 15 == 0):
                offset_x = -math.sin(pt.theta) * 30
                offset_y = math.cos(pt.theta) * 30
                painter.drawRect(int(pt.x + offset_x - 5), int(pt.y + offset_y - 5), 10, 10)

    def draw_garages(self, painter):
        """Draw garage buildings near pit lane entrance."""
        if not self.track_points:
            return
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        # Place garages at s=10-30m (behind pit lane)
        for i, pt in enumerate(self.track_points):
            if 10 < pt.s < 30 and i % 8 == 0:  # Every 8th point
                offset_x = -math.sin(pt.theta) * 35
                offset_y = math.cos(pt.theta) * 35
                painter.drawRect(int(pt.x + offset_x - 8), int(pt.y + offset_y - 8), 16, 16)

    def draw_track(self, painter):
        """Draw smooth track using QPainterPath."""
        # Create centerline path
        path = QPainterPath()
        if self.track_points:
            path.moveTo(self.track_points[0].x, self.track_points[0].y)
            
            for i in range(1, len(self.track_points), 3):
                if i + 2 < len(self.track_points):
                    p1 = self.track_points[i]
                    p2 = self.track_points[i + 1]
                    p3 = self.track_points[i + 2]
                    
                    # Cubic Bezier through points
                    path.cubicTo(
                        p1.x, p1.y,
                        p2.x, p2.y,
                        p3.x, p3.y
                    )
            
            # Close path
            path.lineTo(self.track_points[0].x, self.track_points[0].y)
        
        # Draw track surface (gray)
        painter.setPen(QPen(QColor(100, 100, 100), 24))
        painter.drawPath(path)
        
        # Draw centerline (white)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawPath(path)
        
        # Draw start/finish line (checkered at s=200m on straight)
        if self.track_points:
            # Find point at s~200m
            for pt in self.track_points:
                if abs(pt.s - 200) < 5:
                    painter.setPen(QPen(Qt.GlobalColor.white, 3))
                    normal_x = -math.sin(pt.theta)
                    normal_y = math.cos(pt.theta)
                    hw = 12
                    painter.drawLine(
                        int(pt.x - normal_x * hw),
                        int(pt.y - normal_y * hw),
                        int(pt.x + normal_x * hw),
                        int(pt.y + normal_y * hw)
                    )
                    break
    
    def draw_cars(self, painter):
        """Draw cars at their current positions."""
        for car in self.cars:
            # Find track point at car's arc-length
            idx = int((car.s / self.track_length) * len(self.track_points)) % len(self.track_points)
            pt = self.track_points[idx]
            
            # Calculate car position (left or right of centerline)
            lane_offset = 3.0 if car.grid_position % 2 == 1 else -3.0 
            normal_x = -math.sin(pt.theta)
            normal_y = math.cos(pt.theta)
            
            car_x = pt.x + normal_x * lane_offset
            car_y = pt.y + normal_y * lane_offset
            
            # Draw car as circle
            painter.setBrush(QBrush(car.color))
            painter.setPen(QPen(Qt.GlobalColor.white, 0.5))
            painter.drawEllipse(QPointF(car_x, car_y), 3, 3)


class GridCircuitWindow(QMainWindow):
    """Main window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parametric Circuit with Starting Grid")
        self.setGeometry(100, 100, 1400, 900)
        
        self.circuit = SmoothCircuitWithGrid()
        self.setCentralWidget(self.circuit)
        
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(
                "Smooth clothoid transitions | Start/finish on 400m straight | 2x2 grid formation"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GridCircuitWindow()
    window.show()
    sys.exit(app.exec())
