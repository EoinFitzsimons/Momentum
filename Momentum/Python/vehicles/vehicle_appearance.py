"""
Vehicle Appearance System - Single Seater (cleaned)

Polygonal, top-down renderer for single-seater cars used by the GUI
and headless PNG preview tests. This implementation is concise and
avoids stray top-level statements so it imports cleanly for pytest.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QPointF


class VehicleType(Enum):
    SINGLE_SEATER = "single_seater"


@dataclass
class Livery:
    primary_color: QColor
    secondary_color: QColor
    trim_color: QColor
    team_name: str
    driver_number: int


class VehicleRenderer:
    """Renders a simplified polygonal top-down single-seater."""

    @staticmethod
    def render_single_seater_car(painter: QPainter, livery: Livery, scale: float = 1.0, steering_angle: float = 0.0) -> None:
        """
        Render single-seater car with optional steering angle for front wheels.
        
        Args:
            painter: QPainter instance
            livery: Car livery/colors
            scale: Rendering scale
            steering_angle: Front wheel steering angle in degrees (typically -15 to +15)
        """
        painter.save()

        # Dimensions (local coordinates: X across track, Y along car length)
        body_length = 9.4 * scale
        body_width = 1.85 * scale  # wider for better proportions
        half_l = body_length / 2.0
        half_w = body_width / 2.0

        # Body polygon (tapered nose and rear) - centred at (0,0), Y along length
        # Ensure perfect symmetry by mirroring X coordinates
        # Points ordered counter-clockwise from nose tip
        nose_taper_fraction = 0.48  # controls nose taper width
        nose_taper_length = 0.09    # controls nose taper depth
        mid_start = -0.04           # where max width begins
        mid_end = 0.38              # where rear taper begins
        
        body_poly = [
            QPointF(0.0, -half_l),                                        # nose tip (top centre)
            QPointF(-nose_taper_fraction * half_w, -half_l + nose_taper_length * body_length),  # left nose taper
            QPointF(-half_w, mid_start * body_length),                   # left mid-front
            QPointF(-half_w, half_l),                                    # left rear (flat edge)
            QPointF(half_w, half_l),                                     # right rear (flat edge)
            QPointF(half_w, mid_start * body_length),                    # right mid-front (mirror)
            QPointF(nose_taper_fraction * half_w, -half_l + nose_taper_length * body_length),  # right nose taper (mirror)
        ]

        # Body base
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(livery.trim_color, 1.0))
        painter.drawPolygon(QPolygonF(body_poly))

        # Central narrow stripe (primary colour) - perfectly centred
        stripe_w = max(1.0, 0.24 * scale)
        stripe_poly = [
            QPointF(-stripe_w / 2, -half_l + 0.08 * body_length),
            QPointF(-stripe_w / 2, half_l - 0.08 * body_length),
            QPointF(stripe_w / 2, half_l - 0.08 * body_length),
            QPointF(stripe_w / 2, -half_l + 0.08 * body_length),
        ]
        painter.setBrush(QBrush(livery.primary_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF(stripe_poly))

        # Compact front wing (trapezoid wider at front, narrower at back toward body)
        fw_span = body_width * 2.6
        fw_depth = max(0.42 * scale, 0.32 * scale)
        fw_y = -half_l - fw_depth * 0.45
        front_wing = [
            QPointF(-fw_span * 0.86 / 2, fw_y),
            QPointF(fw_span * 0.86 / 2, fw_y),
            QPointF(fw_span / 2, fw_y + fw_depth),
            QPointF(-fw_span / 2, fw_y + fw_depth),
        ]
        painter.setBrush(QBrush(livery.secondary_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF(front_wing))

        # Compact rear wing (trapezoid wider at back, narrower toward body)
        rw_span = body_width * 2.6
        rw_depth = fw_depth
        rw_y = half_l
        rear_wing = [
            QPointF(-rw_span / 2, rw_y),
            QPointF(rw_span / 2, rw_y),
            QPointF(rw_span * 0.86 / 2, rw_y + rw_depth),
            QPointF(-rw_span * 0.86 / 2, rw_y + rw_depth),
        ]
        painter.drawPolygon(QPolygonF(rear_wing))

        # Halo (simplified rectangular frame) - thin, non-filled, centred
        halo_w = 2.4 * scale
        halo_h = 1.6 * scale
        painter.setPen(QPen(QColor(200, 200, 200), max(1.0, 1.0 * scale)))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(int(-halo_w / 2), int(-0.5 * scale - halo_h / 2), int(halo_w), int(halo_h))

        # Cockpit + driver (simple rectangles, centred)
        cockpit_w = 1.7 * scale
        cockpit_h = 1.0 * scale
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.setPen(QPen(livery.trim_color, 0.6))
        painter.drawRect(int(-cockpit_w / 2), int(-0.3 * scale), int(cockpit_w), int(cockpit_h))

        driver_w = 1.0 * scale
        driver_h = 0.58 * scale
        painter.setBrush(QBrush(QColor(200, 150, 100)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(int(-driver_w / 2), int(-0.12 * scale), int(driver_w), int(driver_h))

        # Suspension hints (thin lines) - symmetrical
        susp_color = QColor(100, 100, 100)
        susp_x_inner = 2.0 * scale
        susp_x_outer = 2.5 * scale
        painter.setPen(QPen(susp_color, 1))
        # Front suspension (symmetrical)
        painter.drawLine(int(-susp_x_inner), int(-0.5 * scale), int(-susp_x_outer), int(-2.2 * scale))
        painter.drawLine(int(susp_x_inner), int(-0.5 * scale), int(susp_x_outer), int(-2.2 * scale))
        # Rear suspension (symmetrical)
        painter.drawLine(int(-susp_x_inner), int(0.5 * scale), int(-susp_x_outer), int(2.0 * scale))
        painter.drawLine(int(susp_x_inner), int(0.5 * scale), int(susp_x_outer), int(2.0 * scale))

        # Wheels - front wheels can rotate with steering_angle
        wheel_x_offset = 2.0 * scale  # track width
        front_wheel_y = -2.3 * scale  # moved further forward (halfway to front wing)
        rear_wheel_y = 2.1 * scale    # moved further back (halfway to rear wing)
        
        tire_color = QColor(20, 20, 20)
        tire_outline = QColor(80, 80, 80)
        
        # All wheels same size
        tire_radius = 0.64 * scale
        wheel_w = int(max(1, 2 * tire_radius * 0.62))  # short dimension across track
        wheel_h = int(max(1, 2 * tire_radius * 1.12))  # long dimension along car length
        
        painter.setBrush(QBrush(tire_color))
        painter.setPen(QPen(tire_outline, 1))
        
        # Front wheels with steering rotation
        if abs(steering_angle) > 0.1:
            # Draw rotated front wheels
            for side_multiplier, wheel_x in [(-1, -wheel_x_offset), (1, wheel_x_offset)]:
                painter.save()
                painter.translate(wheel_x, front_wheel_y)
                painter.rotate(steering_angle)
                painter.drawRect(int(-wheel_w / 2), int(-wheel_h / 2), wheel_w, wheel_h)
                painter.restore()
        else:
            # Straight wheels
            painter.drawRect(int(-wheel_x_offset - wheel_w / 2), int(front_wheel_y - wheel_h / 2), wheel_w, wheel_h)
            painter.drawRect(int(wheel_x_offset - wheel_w / 2), int(front_wheel_y - wheel_h / 2), wheel_w, wheel_h)
        
        # Rear wheels (always straight)
        painter.drawRect(int(-wheel_x_offset - wheel_w / 2), int(rear_wheel_y - wheel_h / 2), wheel_w, wheel_h)
        painter.drawRect(int(wheel_x_offset - wheel_w / 2), int(rear_wheel_y - wheel_h / 2), wheel_w, wheel_h)

        painter.restore()

    @staticmethod
    def render_car(painter: QPainter, vehicle_type: VehicleType, livery: Livery, scale: float = 1.0) -> None:
        if vehicle_type == VehicleType.SINGLE_SEATER:
            VehicleRenderer.render_single_seater_car(painter, livery, scale)
        else:
            painter.setBrush(QBrush(livery.primary_color))
            painter.setPen(QPen(livery.trim_color, 1))
            painter.drawRect(-5, -2, 10, 4)

    @staticmethod
    def render_racing_number(painter: QPainter, number: int, number_color: QColor = QColor(255, 255, 255), bg_color: Optional[QColor] = None) -> None:
        painter.save()
        if bg_color:
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(number_color, 1))
            painter.drawRect(int(-2), int(-1.5), int(4), int(3))
        painter.setFont(painter.font())
        painter.setPen(QPen(number_color, 1))
        painter.restore()


@dataclass
class VehicleConfiguration:
    livery: Livery
    driver_number: int
    team_id: int
    fuel_load_kg: float = 105.0
    tire_compound: str = "medium"
    aerodynamic_setup: str = "balanced"
    brake_balance: float = 0.5

    def to_display_string(self) -> str:
        return f"#{self.driver_number} - {self.livery.team_name} (Formula Single Seater)"


def create_team_livery(team_id: int, team_name: str, driver_number: int) -> Livery:
    team_colors = [
        (QColor(220, 20, 20), QColor(255, 255, 0), QColor(0, 0, 0)),
        (QColor(0, 80, 180), QColor(255, 255, 255), QColor(255, 165, 0)),
        (QColor(0, 140, 80), QColor(255, 255, 255), QColor(200, 200, 200)),
        (QColor(100, 100, 100), QColor(255, 255, 255), QColor(255, 0, 0)),
        (QColor(200, 0, 120), QColor(255, 215, 0), QColor(255, 255, 255)),
    ]
    primary, secondary, trim = team_colors[team_id % len(team_colors)]
    return Livery(primary, secondary, trim, team_name, driver_number)
