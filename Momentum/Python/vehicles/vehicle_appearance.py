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
    ENDURANCE = "endurance"  # WEC Hypercars/LMDh
    DRAG_ACCELERATION = "drag_acceleration"  # Top Fuel Dragsters
    SPRINT_RALLYCROSS = "sprint_rallycross"  # Rallycross Hatchbacks
    PRODUCTION_TOURING = "production_touring"  # GT Cars
    URBAN_STREET = "urban_street"  # Drift Coupes


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
    def render_endurance_hypercar(painter: QPainter, livery: Livery, scale: float = 1.0, steering_angle: float = 0.0) -> None:
        """
        Render WEC LMH/LMDh hypercar - FULLY ENCLOSED body with integrated wheel arches.
        """
        painter.save()

        body_length = 10.0 * scale
        body_width = 3.6 * scale
        half_l = body_length / 2.0
        half_w = body_width / 2.0

        # Wheel positions (need to define early for body cutouts)
        front_wheel_y = -2.8 * scale
        rear_wheel_y = 2.5 * scale
        wheel_arch_width = 1.8 * scale

        # MAIN BODY - smooth endurance car outline with integrated wheel bulges
        body_poly = [
            QPointF(0.0, -half_l),  # nose tip
            QPointF(-0.35 * half_w, -half_l + 0.1 * body_length),  # nose sides
            # Front wheel arch bulge (left)
            QPointF(-half_w * 0.95, front_wheel_y - 0.9 * scale),
            QPointF(-half_w, front_wheel_y),  # peak of front arch
            QPointF(-half_w * 0.95, front_wheel_y + 0.9 * scale),
            # Side body (left)
            QPointF(-half_w * 0.88, 0.0),  # mid-body indent
            # Rear wheel arch bulge (left)
            QPointF(-half_w * 0.95, rear_wheel_y - 1.0 * scale),
            QPointF(-half_w, rear_wheel_y),  # peak of rear arch
            QPointF(-half_w * 0.95, rear_wheel_y + 1.0 * scale),
            # Rear taper
            QPointF(-0.65 * half_w, half_l - 0.15 * body_length),
            QPointF(-0.4 * half_w, half_l),
            QPointF(0.4 * half_w, half_l),
            QPointF(0.65 * half_w, half_l - 0.15 * body_length),
            # Rear wheel arch bulge (right)
            QPointF(half_w * 0.95, rear_wheel_y + 1.0 * scale),
            QPointF(half_w, rear_wheel_y),
            QPointF(half_w * 0.95, rear_wheel_y - 1.0 * scale),
            # Side body (right)
            QPointF(half_w * 0.88, 0.0),
            # Front wheel arch bulge (right)
            QPointF(half_w * 0.95, front_wheel_y + 0.9 * scale),
            QPointF(half_w, front_wheel_y),
            QPointF(half_w * 0.95, front_wheel_y - 0.9 * scale),
            QPointF(0.35 * half_w, -half_l + 0.1 * body_length),
        ]

        painter.setBrush(QBrush(livery.primary_color))
        painter.setPen(QPen(QColor(0, 0, 0), 1.8))
        painter.drawPolygon(QPolygonF(body_poly))

        # Windscreen (small, raked)
        windscreen_poly = [
            QPointF(-1.0 * scale, -2.0 * scale),
            QPointF(1.0 * scale, -2.0 * scale),
            QPointF(0.85 * scale, -0.5 * scale),
            QPointF(-0.85 * scale, -0.5 * scale),
        ]
        painter.setBrush(QBrush(QColor(30, 60, 90, 200)))
        painter.setPen(QPen(QColor(20, 20, 20), 1.0))
        painter.drawPolygon(QPolygonF(windscreen_poly))

        # Side racing stripe
        painter.setBrush(QBrush(livery.secondary_color))
        painter.setPen(Qt.PenStyle.NoPen)
        for x_side in [-1, 1]:
            stripe_poly = [
                QPointF(x_side * 0.9 * scale, -3.0 * scale),
                QPointF(x_side * 1.2 * scale, -3.0 * scale),
                QPointF(x_side * 1.3 * scale, 2.8 * scale),
                QPointF(x_side * 1.0 * scale, 2.8 * scale),
            ]
            painter.drawPolygon(QPolygonF(stripe_poly))

        # Front splitter (extends beyond body)
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.setPen(QPen(livery.trim_color, 1.0))
        splitter_poly = [
            QPointF(-1.6 * scale, -half_l - 0.3 * scale),
            QPointF(1.6 * scale, -half_l - 0.3 * scale),
            QPointF(1.3 * scale, -half_l + 0.1 * scale),
            QPointF(-1.3 * scale, -half_l + 0.1 * scale),
        ]
        painter.drawPolygon(QPolygonF(splitter_poly))

        # Rear wing (high-mounted)
        painter.setBrush(QBrush(livery.secondary_color))
        rw_poly = [
            QPointF(-1.8 * scale, half_l + 0.4 * scale),
            QPointF(1.8 * scale, half_l + 0.4 * scale),
            QPointF(1.5 * scale, half_l + 1.0 * scale),
            QPointF(-1.5 * scale, half_l + 1.0 * scale),
        ]
        painter.drawPolygon(QPolygonF(rw_poly))

        # Wheels inside arches (small circles, mostly hidden)
        painter.setBrush(QBrush(QColor(25, 25, 25)))
        painter.setPen(QPen(QColor(60, 60, 60), 1.0))
        tire_r = 0.5 * scale
        for wheel_y in [front_wheel_y, rear_wheel_y]:
            for wheel_x in [-half_w * 0.75, half_w * 0.75]:
                painter.drawEllipse(int(wheel_x - tire_r), int(wheel_y - tire_r), 
                                   int(2 * tire_r), int(2 * tire_r))

        painter.restore()

    @staticmethod
    def render_top_fuel_dragster(painter: QPainter, livery: Livery, scale: float = 1.0) -> None:
        """
        Render Top Fuel dragster - COMPLETELY different: thin exposed chassis, massive wheel contrast.
        """
        painter.save()

        body_length = 16.0 * scale  # Extremely long
        half_l = body_length / 2.0

        # Thin central chassis spine
        chassis_w = 0.5 * scale
        painter.setBrush(QBrush(QColor(90, 90, 90)))
        painter.setPen(QPen(QColor(40, 40, 40), 1.5))
        painter.drawRect(int(-chassis_w / 2), int(-half_l + 1.0 * scale), 
                        int(chassis_w), int(body_length - 4.0 * scale))

        # Tiny front cockpit (far forward)
        cockpit_y = -half_l + 2.0 * scale
        painter.setBrush(QBrush(livery.primary_color))
        painter.setPen(QPen(QColor(0, 0, 0), 1.5))
        cockpit_poly = [
            QPointF(-0.7 * scale, cockpit_y),
            QPointF(0.7 * scale, cockpit_y),
            QPointF(0.6 * scale, cockpit_y + 1.5 * scale),
            QPointF(-0.6 * scale, cockpit_y + 1.5 * scale),
        ]
        painter.drawPolygon(QPolygonF(cockpit_poly))

        # Driver helmet
        painter.setBrush(QBrush(livery.secondary_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(-0.3 * scale), int(cockpit_y + 0.4 * scale), 
                          int(0.6 * scale), int(0.6 * scale))

        # MASSIVE rear engine block
        engine_y = half_l - 3.0 * scale
        painter.setBrush(QBrush(livery.primary_color))
        painter.setPen(QPen(QColor(0, 0, 0), 2.0))
        painter.drawRect(int(-1.4 * scale), int(engine_y), int(2.8 * scale), int(2.6 * scale))

        # Supercharger intake (iconic)
        painter.setBrush(QBrush(QColor(220, 220, 220)))
        painter.setPen(QPen(QColor(60, 60, 60), 1.2))
        painter.drawRect(int(-0.8 * scale), int(engine_y - 0.7 * scale), 
                        int(1.6 * scale), int(0.9 * scale))

        # Exhaust pipes (both sides)
        painter.setBrush(QBrush(QColor(140, 140, 140)))
        for x_side in [-1, 1]:
            painter.drawRect(int(x_side * 1.5 * scale - 0.15 * scale), int(engine_y + 0.5 * scale),
                           int(0.3 * scale), int(1.8 * scale))

        # Front wing (thin, wide)
        painter.setBrush(QBrush(livery.secondary_color))
        painter.setPen(QPen(livery.trim_color, 1.0))
        fw_poly = [
            QPointF(-2.2 * scale, -half_l - 0.3 * scale),
            QPointF(2.2 * scale, -half_l - 0.3 * scale),
            QPointF(1.8 * scale, -half_l + 0.1 * scale),
            QPointF(-1.8 * scale, -half_l + 0.1 * scale),
        ]
        painter.drawPolygon(QPolygonF(fw_poly))

        # HUGE rear wing
        painter.setBrush(QBrush(livery.primary_color))
        rw_poly = [
            QPointF(-2.8 * scale, half_l + 0.5 * scale),
            QPointF(2.8 * scale, half_l + 0.5 * scale),
            QPointF(2.4 * scale, half_l + 1.5 * scale),
            QPointF(-2.4 * scale, half_l + 1.5 * scale),
        ]
        painter.drawPolygon(QPolygonF(rw_poly))

        # WHEELS - dramatic size contrast
        tire_color = QColor(20, 20, 20)
        painter.setBrush(QBrush(tire_color))
        painter.setPen(QPen(QColor(70, 70, 70), 1.5))

        # Tiny skinny front wheels
        front_y = -half_l + 1.2 * scale
        front_x = 1.0 * scale
        front_r = 0.35 * scale
        painter.drawEllipse(int(-front_x - front_r * 0.3), int(front_y - front_r), 
                          int(front_r * 0.6), int(2 * front_r))
        painter.drawEllipse(int(front_x - front_r * 0.3), int(front_y - front_r), 
                          int(front_r * 0.6), int(2 * front_r))

        # ENORMOUS rear slicks
        rear_y = half_l - 1.5 * scale
        rear_x = 2.0 * scale
        rear_r = 1.6 * scale
        painter.drawEllipse(int(-rear_x - rear_r * 0.9), int(rear_y - rear_r * 0.65), 
                          int(rear_r * 1.8), int(rear_r * 1.3))
        painter.drawEllipse(int(rear_x - rear_r * 0.9), int(rear_y - rear_r * 0.65), 
                          int(rear_r * 1.8), int(rear_r * 1.3))

        painter.restore()

    @staticmethod
    def render_rallycross_hatchback(painter: QPainter, livery: Livery, scale: float = 1.0, steering_angle: float = 0.0) -> None:
        """
        Render rallycross hatchback - BOXY compact body with prominent wheel arches.
        """
        painter.save()

        body_length = 7.2 * scale
        body_width = 3.2 * scale
        half_l = body_length / 2.0
        half_w = body_width / 2.0

        front_wheel_y = -1.9 * scale
        rear_wheel_y = 1.8 * scale

        # BOXY HATCHBACK BODY with flared arches
        body_poly = [
            QPointF(0.0, -half_l),  # nose
            QPointF(-0.55 * half_w, -half_l + 0.15 * body_length),  # hood corner
            # Front wheel arch bulge
            QPointF(-half_w * 0.92, front_wheel_y - 0.75 * scale),
            QPointF(-half_w, front_wheel_y),  # arch peak
            QPointF(-half_w * 0.92, front_wheel_y + 0.75 * scale),
            QPointF(-half_w * 0.85, 0.0),  # door area
            # Rear wheel arch bulge
            QPointF(-half_w * 0.92, rear_wheel_y - 0.8 * scale),
            QPointF(-half_w, rear_wheel_y),  # arch peak
            QPointF(-half_w * 0.92, rear_wheel_y + 0.8 * scale),
            # Rear hatch (flat)
            QPointF(-0.5 * half_w, half_l),
            QPointF(0.5 * half_w, half_l),
            # Right side mirror
            QPointF(half_w * 0.92, rear_wheel_y + 0.8 * scale),
            QPointF(half_w, rear_wheel_y),
            QPointF(half_w * 0.92, rear_wheel_y - 0.8 * scale),
            QPointF(half_w * 0.85, 0.0),
            QPointF(half_w * 0.92, front_wheel_y + 0.75 * scale),
            QPointF(half_w, front_wheel_y),
            QPointF(half_w * 0.92, front_wheel_y - 0.75 * scale),
            QPointF(0.55 * half_w, -half_l + 0.15 * body_length),
        ]

        painter.setBrush(QBrush(livery.primary_color))
        painter.setPen(QPen(QColor(0, 0, 0), 2.0))
        painter.drawPolygon(QPolygonF(body_poly))

        # Hood and roof stripe
        painter.setBrush(QBrush(livery.secondary_color))
        painter.setPen(Qt.PenStyle.NoPen)
        stripe_poly = [
            QPointF(-0.5 * scale, -2.8 * scale),
            QPointF(0.5 * scale, -2.8 * scale),
            QPointF(0.5 * scale, 1.0 * scale),
            QPointF(-0.5 * scale, 1.0 * scale),
        ]
        painter.drawPolygon(QPolygonF(stripe_poly))

        # Windows (hatchback style)
        painter.setBrush(QBrush(QColor(25, 45, 65, 220)))
        painter.setPen(QPen(QColor(15, 15, 15), 1.0))
        # Windscreen
        windscreen_poly = [
            QPointF(-0.8 * scale, -1.5 * scale),
            QPointF(0.8 * scale, -1.5 * scale),
            QPointF(0.75 * scale, -0.3 * scale),
            QPointF(-0.75 * scale, -0.3 * scale),
        ]
        painter.drawPolygon(QPolygonF(windscreen_poly))
        # Side/rear glass
        painter.drawRect(int(-0.9 * scale), int(-0.2 * scale), int(1.8 * scale), int(1.4 * scale))

        # Roll cage bars
        painter.setPen(QPen(QColor(190, 190, 190), 1.5))
        for x in [-0.5 * scale, 0.5 * scale]:
            painter.drawLine(int(x), int(-1.0 * scale), int(x), int(0.8 * scale))

        # Hood scoop (rally essential)
        painter.setBrush(QBrush(QColor(25, 25, 25)))
        painter.setPen(QPen(livery.trim_color, 1.0))
        painter.drawRect(int(-0.45 * scale), int(-2.2 * scale), int(0.9 * scale), int(0.6 * scale))

        # Rear roof wing
        painter.setBrush(QBrush(livery.secondary_color))
        wing_poly = [
            QPointF(-1.4 * scale, half_l + 0.2 * scale),
            QPointF(1.4 * scale, half_l + 0.2 * scale),
            QPointF(1.2 * scale, half_l + 0.7 * scale),
            QPointF(-1.2 * scale, half_l + 0.7 * scale),
        ]
        painter.drawPolygon(QPolygonF(wing_poly))

        # Wheels partially visible in arches
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(QColor(80, 80, 80), 1.5))
        tire_r = 0.55 * scale
        for wheel_y in [front_wheel_y, rear_wheel_y]:
            for wheel_x in [-half_w * 0.7, half_w * 0.7]:
                painter.drawEllipse(int(wheel_x - tire_r), int(wheel_y - tire_r),
                                   int(2 * tire_r), int(2 * tire_r))

        painter.restore()

    @staticmethod
    def render_gt_car(painter: QPainter, livery: Livery, scale: float = 1.0, steering_angle: float = 0.0) -> None:
        """
        Render GT3/GT4 car - SLEEK enclosed sports car with smooth curves.
        """
        painter.save()

        body_length = 8.6 * scale
        body_width = 3.4 * scale
        half_l = body_length / 2.0
        half_w = body_width / 2.0

        front_wheel_y = -2.4 * scale
        rear_wheel_y = 2.2 * scale

        # SLEEK GT SPORTS CAR BODY with integrated arches
        body_poly = [
            QPointF(0.0, -half_l),  # nose point
            QPointF(-0.45 * half_w, -half_l + 0.18 * body_length),  # hood
            # Front fender curve
            QPointF(-half_w * 0.9, front_wheel_y - 0.85 * scale),
            QPointF(-half_w * 0.95, front_wheel_y),
            QPointF(-half_w * 0.9, front_wheel_y + 0.85 * scale),
            QPointF(-half_w * 0.82, 0.1 * body_length),  # door
            # Rear fender curve (wider)
            QPointF(-half_w * 0.92, rear_wheel_y - 0.95 * scale),
            QPointF(-half_w * 0.98, rear_wheel_y),
            QPointF(-half_w * 0.92, rear_wheel_y + 0.95 * scale),
            # Rear taper
            QPointF(-0.6 * half_w, half_l - 0.12 * body_length),
            QPointF(-0.38 * half_w, half_l),
            QPointF(0.38 * half_w, half_l),
            QPointF(0.6 * half_w, half_l - 0.12 * body_length),
            # Right rear fender
            QPointF(half_w * 0.92, rear_wheel_y + 0.95 * scale),
            QPointF(half_w * 0.98, rear_wheel_y),
            QPointF(half_w * 0.92, rear_wheel_y - 0.95 * scale),
            QPointF(half_w * 0.82, 0.1 * body_length),
            # Right front fender
            QPointF(half_w * 0.9, front_wheel_y + 0.85 * scale),
            QPointF(half_w * 0.95, front_wheel_y),
            QPointF(half_w * 0.9, front_wheel_y - 0.85 * scale),
            QPointF(0.45 * half_w, -half_l + 0.18 * body_length),
        ]

        painter.setBrush(QBrush(livery.primary_color))
        painter.setPen(QPen(QColor(0, 0, 0), 1.6))
        painter.drawPolygon(QPolygonF(body_poly))

        # Side racing stripes (GT3 style)
        painter.setBrush(QBrush(livery.secondary_color))
        painter.setPen(Qt.PenStyle.NoPen)
        for x_side in [-1, 1]:
            stripe_poly = [
                QPointF(x_side * 1.05 * scale, -2.8 * scale),
                QPointF(x_side * 1.35 * scale, -2.8 * scale),
                QPointF(x_side * 1.45 * scale, 2.6 * scale),
                QPointF(x_side * 1.15 * scale, 2.6 * scale),
            ]
            painter.drawPolygon(QPolygonF(stripe_poly))

        # Windscreen (low, raked)
        painter.setBrush(QBrush(QColor(20, 45, 70, 210)))
        painter.setPen(QPen(QColor(10, 10, 10), 1.0))
        windscreen_poly = [
            QPointF(-1.05 * scale, -1.8 * scale),
            QPointF(1.05 * scale, -1.8 * scale),
            QPointF(0.95 * scale, -0.2 * scale),
            QPointF(-0.95 * scale, -0.2 * scale),
        ]
        painter.drawPolygon(QPolygonF(windscreen_poly))
        # Side windows
        painter.drawRect(int(-1.1 * scale), int(-0.1 * scale), int(2.2 * scale), int(1.6 * scale))

        # Front splitter (GT3 aggressive)
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.setPen(QPen(livery.trim_color, 1.1))
        splitter_poly = [
            QPointF(-1.7 * scale, -half_l - 0.35 * scale),
            QPointF(1.7 * scale, -half_l - 0.35 * scale),
            QPointF(1.4 * scale, -half_l + 0.05 * scale),
            QPointF(-1.4 * scale, -half_l + 0.05 * scale),
        ]
        painter.drawPolygon(QPolygonF(splitter_poly))

        # Rear wing (high GT3 wing)
        painter.setBrush(QBrush(livery.secondary_color))
        wing_poly = [
            QPointF(-1.9 * scale, half_l + 0.35 * scale),
            QPointF(1.9 * scale, half_l + 0.35 * scale),
            QPointF(1.6 * scale, half_l + 0.95 * scale),
            QPointF(-1.6 * scale, half_l + 0.95 * scale),
        ]
        painter.drawPolygon(QPolygonF(wing_poly))

        # Wheels mostly hidden in arches
        painter.setBrush(QBrush(QColor(25, 25, 25)))
        painter.setPen(QPen(QColor(70, 70, 70), 1.3))
        tire_r = 0.6 * scale
        for wheel_y in [front_wheel_y, rear_wheel_y]:
            for wheel_x in [-half_w * 0.7, half_w * 0.7]:
                painter.drawEllipse(int(wheel_x - tire_r), int(wheel_y - tire_r),
                                   int(2 * tire_r), int(2 * tire_r))

        painter.restore()

    @staticmethod
    def render_drift_coupe(painter: QPainter, livery: Livery, scale: float = 1.0, steering_angle: float = 0.0) -> None:
        """
        Render drift coupe - Clean JDM sports coupe with wide stance and drift aesthetics.
        """
        painter.save()

        body_length = 7.6 * scale
        body_width = 2.8 * scale
        half_l = body_length / 2.0
        half_w = body_width / 2.0

        front_wheel_y = -2.0 * scale
        rear_wheel_y = 1.85 * scale

        # CLEAN COUPE BODY with subtle flares
        body_poly = [
            QPointF(0.0, -half_l),  # nose
            QPointF(-0.5 * half_w, -half_l + 0.22 * body_length),  # hood corner
            # Front fender with subtle flare
            QPointF(-half_w * 0.88, front_wheel_y - 0.7 * scale),
            QPointF(-half_w * 0.98, front_wheel_y),
            QPointF(-half_w * 0.88, front_wheel_y + 0.7 * scale),
            QPointF(-half_w * 0.78, 0.25 * body_length),  # door
            # Rear fender with wider flare
            QPointF(-half_w * 0.85, rear_wheel_y - 0.75 * scale),
            QPointF(-half_w * 1.0, rear_wheel_y),
            QPointF(-half_w * 0.85, rear_wheel_y + 0.75 * scale),
            # Flat hatchback rear (like Focus)
            QPointF(-half_w * 0.85, half_l - 0.08 * body_length),
            QPointF(-half_w * 0.85, half_l),
            QPointF(half_w * 0.85, half_l),
            QPointF(half_w * 0.85, half_l - 0.08 * body_length),
            # Right rear fender
            QPointF(half_w * 0.85, rear_wheel_y + 0.75 * scale),
            QPointF(half_w * 1.0, rear_wheel_y),
            QPointF(half_w * 0.85, rear_wheel_y - 0.75 * scale),
            QPointF(half_w * 0.78, 0.25 * body_length),
            # Right front fender
            QPointF(half_w * 0.88, front_wheel_y + 0.7 * scale),
            QPointF(half_w * 0.98, front_wheel_y),
            QPointF(half_w * 0.88, front_wheel_y - 0.7 * scale),
            QPointF(0.5 * half_w, -half_l + 0.22 * body_length),
        ]

        painter.setBrush(QBrush(livery.primary_color))
        painter.setPen(QPen(QColor(0, 0, 0), 1.6))
        painter.drawPolygon(QPolygonF(body_poly))

        # Clean hood stripe
        painter.setBrush(QBrush(livery.secondary_color))
        painter.setPen(Qt.PenStyle.NoPen)
        stripe_poly = [
            QPointF(-0.4 * scale, -3.2 * scale),
            QPointF(0.4 * scale, -3.2 * scale),
            QPointF(0.4 * scale, -0.8 * scale),
            QPointF(-0.4 * scale, -0.8 * scale),
        ]
        painter.drawPolygon(QPolygonF(stripe_poly))

        # Side graphics (symmetric, cleaner)
        for x_side in [-1, 1]:
            side_poly = [
                QPointF(x_side * 1.0 * scale, -1.5 * scale),
                QPointF(x_side * 1.3 * scale, -1.5 * scale),
                QPointF(x_side * 1.4 * scale, 2.2 * scale),
                QPointF(x_side * 1.1 * scale, 2.2 * scale),
            ]
            painter.drawPolygon(QPolygonF(side_poly))

        # Low coupe windows
        painter.setBrush(QBrush(QColor(20, 30, 45, 230)))
        painter.setPen(QPen(QColor(10, 10, 10), 0.8))
        # Windscreen
        windscreen_poly = [
            QPointF(-0.9 * scale, -1.7 * scale),
            QPointF(0.9 * scale, -1.7 * scale),
            QPointF(0.8 * scale, -0.3 * scale),
            QPointF(-0.8 * scale, -0.3 * scale),
        ]
        painter.drawPolygon(QPolygonF(windscreen_poly))
        # Side/rear glass
        painter.drawRect(int(-0.85 * scale), int(-0.2 * scale), int(1.7 * scale), int(1.3 * scale))

        # Twin exhaust tips
        painter.setBrush(QBrush(QColor(140, 140, 140)))
        painter.setPen(QPen(QColor(60, 60, 60), 0.9))
        exhaust_r = 0.2 * scale
        for x_pos in [-0.65 * scale, 0.65 * scale]:
            painter.drawEllipse(int(x_pos - exhaust_r), int(half_l - 0.12 * scale),
                              int(2 * exhaust_r), int(2 * exhaust_r))

        # Wheels in arches
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(QColor(90, 90, 90), 1.4))
        tire_r = 0.56 * scale
        for wheel_y in [front_wheel_y, rear_wheel_y]:
            for wheel_x in [-half_w * 0.68, half_w * 0.68]:
                painter.drawEllipse(int(wheel_x - tire_r), int(wheel_y - tire_r),
                                   int(2 * tire_r), int(2 * tire_r))

        painter.restore()

    @staticmethod
    def render_car(painter: QPainter, vehicle_type: VehicleType, livery: Livery, scale: float = 1.0, steering_angle: float = 0.0) -> None:
        """
        Main entry point for rendering any vehicle type.
        
        Args:
            painter: QPainter instance
            vehicle_type: Type of vehicle to render
            livery: Car livery/colors
            scale: Rendering scale
            steering_angle: Steering angle for front wheels (default 0.0)
        """
        if vehicle_type == VehicleType.SINGLE_SEATER:
            VehicleRenderer.render_single_seater_car(painter, livery, scale, steering_angle)
        elif vehicle_type == VehicleType.ENDURANCE:
            VehicleRenderer.render_endurance_hypercar(painter, livery, scale, steering_angle)
        elif vehicle_type == VehicleType.DRAG_ACCELERATION:
            VehicleRenderer.render_top_fuel_dragster(painter, livery, scale)
        elif vehicle_type == VehicleType.SPRINT_RALLYCROSS:
            VehicleRenderer.render_rallycross_hatchback(painter, livery, scale, steering_angle)
        elif vehicle_type == VehicleType.PRODUCTION_TOURING:
            VehicleRenderer.render_gt_car(painter, livery, scale, steering_angle)
        elif vehicle_type == VehicleType.URBAN_STREET:
            VehicleRenderer.render_drift_coupe(painter, livery, scale, steering_angle)
        else:
            # Fallback simple rectangle
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
