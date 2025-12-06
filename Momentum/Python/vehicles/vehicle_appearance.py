"""
Vehicle Appearance System - Single Seater Focus

Defines visual characteristics for open-wheel racing cars including:
- Livery colors and patterns (team colors)
- Open-wheel Formula car rendering
- Aerodynamic elements (front/rear wings, DRS flap)
- Racing number display
- Detailed cockpit and mechanical elements

MVP focuses on Single Seater (Formula-style) racing only.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, QPointF
import math


class VehicleType(Enum):
    """Racing vehicle type (MVP: Single Seater only)"""
    SINGLE_SEATER = "single_seater"  # Open-wheel Formula racing


@dataclass
class Livery:
    """Car paint scheme and design"""
    primary_color: QColor         # Main body color
    secondary_color: QColor       # Stripe/accent color
    trim_color: QColor            # Details color
    team_name: str                # Displayed on side
    driver_number: int            # Racing number


class VehicleRenderer:
    """Renders open-wheel single seater race cars"""

    @staticmethod
    def render_single_seater_car(painter: QPainter, livery: 'Livery',
                                 scale: float = 1.0) -> None:
        """
        Render single-seater race car (Formula style).

        Features:
        - Open cockpit with visible driver
        - Front wing
        - Rear wing
        - Visible suspension elements
        - Slender profile with 2-3 meter width, 5+ meter length
        - Exposed wheels (characteristic of open-wheel racing)
        - Sidepod air intakes
        - Modern styling
        """
        painter.save()

        # Main chassis body (single tube monocoque)
        painter.setBrush(QBrush(livery.primary_color))
        painter.setPen(QPen(livery.trim_color, 1.5))

        # Car body - elongated for open-wheel single seater
        body_length = 9.0 * scale
        body_width = 1.6 * scale
        painter.drawRect(int(-body_length / 2), int(-body_width / 2),
                         int(body_length), int(body_width))

        # === FRONT WING ===
        # Main plane
        wing_y_offset = -body_width / 2 - 2.0 * scale
        front_wing_base = [
            QPointF(-3.5 * scale, wing_y_offset),
            QPointF(3.5 * scale, wing_y_offset),
            QPointF(3.0 * scale, wing_y_offset - 1.0 * scale),
            QPointF(-3.0 * scale, wing_y_offset - 1.0 * scale),
        ]

        painter.setBrush(QBrush(livery.secondary_color))
        painter.drawPolygon([p for p in front_wing_base])

        # Endplates (vertical extensions for downforce)
        painter.setPen(QPen(livery.trim_color, 1))
        painter.drawLine(int(-3.5 * scale), int(wing_y_offset),
                         int(-3.5 * scale), int(wing_y_offset - 1.5 * scale))
        painter.drawLine(int(3.5 * scale), int(wing_y_offset),
                         int(3.5 * scale), int(wing_y_offset - 1.5 * scale))

        # === SIDEPODS & AIR INTAKES ===
        # Left sidepod
        painter.setBrush(QBrush(QColor(livery.primary_color.red() - 30,
                                       livery.primary_color.green() - 30,
                                       livery.primary_color.blue() - 30)))
        painter.drawRect(int(-4.0 * scale), int(-body_width / 2 - 0.5 * scale),
                         int(1.5 * scale), int(1.2 * scale))
        # Right sidepod
        painter.drawRect(int(2.5 * scale), int(-body_width / 2 - 0.5 * scale),
                         int(1.5 * scale), int(1.2 * scale))

        # === COCKPIT & DRIVER ===
        # Halo safety device (modern regulation)
        halo_color = QColor(200, 200, 200)
        painter.setPen(QPen(halo_color, 2))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        # Halo is a loop around cockpit
        painter.drawEllipse(int(-1.2 * scale), int(-body_width / 2 - 1.2 * scale),
                           int(2.4 * scale), int(1.8 * scale))

        # Cockpit opening
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(livery.trim_color, 0.5))
        painter.drawRect(int(-0.8 * scale), int(-body_width / 4),
                         int(1.6 * scale), int(1.0 * scale))

        # Visible driver (small rectangle inside cockpit)
        painter.setBrush(QBrush(QColor(200, 150, 100)))  # Skin tone
        painter.drawRect(int(-0.5 * scale), int(-body_width / 8),
                         int(1.0 * scale), int(0.6 * scale))

        # === REAR WING ===
        # Main plane
        rear_wing_y = body_width / 2 + 1.5 * scale
        rear_wing_base = [
            QPointF(-2.5 * scale, rear_wing_y),
            QPointF(2.5 * scale, rear_wing_y),
            QPointF(2.2 * scale, rear_wing_y + 1.2 * scale),
            QPointF(-2.2 * scale, rear_wing_y + 1.2 * scale),
        ]

        painter.setBrush(QBrush(livery.secondary_color))
        painter.drawPolygon([p for p in rear_wing_base])

        # DRS flap (adjustable rear wing element)
        drs_y = rear_wing_y + 1.4 * scale
        painter.setBrush(QBrush(QColor(livery.secondary_color.red() + 40,
                                       livery.secondary_color.green() + 40,
                                       livery.secondary_color.blue() + 40)))
        painter.drawRect(int(-1.8 * scale), int(drs_y),
                         int(3.6 * scale), int(0.5 * scale))

        # Rear wing endplates
        painter.setPen(QPen(livery.trim_color, 1))
        painter.drawLine(int(-2.5 * scale), int(rear_wing_y),
                         int(-2.5 * scale), int(rear_wing_y + 1.5 * scale))
        painter.drawLine(int(2.5 * scale), int(rear_wing_y),
                         int(2.5 * scale), int(rear_wing_y + 1.5 * scale))

        # === SUSPENSION & WHEELS ===
        # Visible suspension geometry (push-rods, springs)
        # Front left suspension
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawLine(int(-2.5 * scale), int(-body_width / 2),
                         int(-2.8 * scale), int(-body_width / 2 - 1.2 * scale))
        # Front right suspension
        painter.drawLine(int(2.5 * scale), int(-body_width / 2),
                         int(2.8 * scale), int(-body_width / 2 - 1.2 * scale))
        # Rear left suspension
        painter.drawLine(int(-2.5 * scale), int(body_width / 2),
                         int(-2.8 * scale), int(body_width / 2 + 1.0 * scale))
        # Rear right suspension
        painter.drawLine(int(2.5 * scale), int(body_width / 2),
                         int(2.8 * scale), int(body_width / 2 + 1.0 * scale))

        # Visible wheels (large, slick tires)
        # Front wheels (smaller than rear)
        wheel_positions = [
            # Front left
            (int(-2.8 * scale), int(-body_width / 2 - 1.2 * scale), 0.7),
            # Front right
            (int(2.8 * scale), int(-body_width / 2 - 1.2 * scale), 0.7),
            # Rear left
            (int(-2.8 * scale), int(body_width / 2 + 1.0 * scale), 0.95),
            # Rear right
            (int(2.8 * scale), int(body_width / 2 + 1.0 * scale), 0.95),
        ]

        painter.setBrush(QBrush(QColor(20, 20, 20)))  # Black tire
        painter.setPen(QPen(QColor(80, 80, 80), 0.5))
        for wheel_x, wheel_y, tire_size in wheel_positions:
            tire_radius = tire_size * scale
            painter.drawEllipse(int(wheel_x - tire_radius),
                              int(wheel_y - tire_radius),
                              int(2 * tire_radius), int(2 * tire_radius))

            # Wheel rim (inner circle)
            painter.setBrush(QBrush(QColor(120, 120, 120)))
            painter.drawEllipse(int(wheel_x - tire_radius * 0.4),
                              int(wheel_y - tire_radius * 0.4),
                              int(2 * tire_radius * 0.4),
                              int(2 * tire_radius * 0.4))

        painter.restore()

    @staticmethod
    def render_car(painter: QPainter, vehicle_type: VehicleType,
                   livery: 'Livery', scale: float = 1.0) -> None:
        """
        Render car based on vehicle type.

        Args:
            painter: QPainter instance for drawing
            vehicle_type: Type of racing vehicle (currently only SINGLE_SEATER for MVP)
            livery: Paint scheme and design
            scale: Zoom/scale factor for rendering
        """
        if vehicle_type == VehicleType.SINGLE_SEATER:
            VehicleRenderer.render_single_seater_car(painter, livery, scale)
        else:
            # Fallback: simple rectangle for safety
            painter.setBrush(QBrush(livery.primary_color))
            painter.setPen(QPen(livery.trim_color, 1))
            painter.drawRect(-5, -2, 10, 4)

    @staticmethod
    def render_racing_number(painter: QPainter, number: int,
                            number_color: QColor = QColor(255, 255, 255),
                            bg_color: Optional[QColor] = None) -> None:
        """
        Render driver's racing number on car.
        
        Args:
            painter: QPainter instance
            number: Driver number (1-999)
            number_color: Color of number text
            bg_color: Optional background color for number box
        """
        painter.save()
        
        # Draw background if specified
        if bg_color:
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(number_color, 1))
            painter.drawRect(-2, -1.5, 4, 3)
        
        # Draw number text
        painter.setFont(painter.font())
        painter.setPen(QPen(number_color, 1))
        text = str(number).zfill(2)  # Pad with leading zero
        # Note: Simple text rendering; PyQt6 would use drawText with QFont
        
        painter.restore()


@dataclass
class VehicleConfiguration:
    """Complete vehicle setup for a single seater race entry"""
    livery: Livery
    driver_number: int
    team_id: int
    fuel_load_kg: float = 105.0  # Single seater fuel load ~105kg
    tire_compound: str = "medium"  # soft, medium, hard (Pirelli spec)
    aerodynamic_setup: str = "balanced"  # low_downforce, balanced, high_downforce
    brake_balance: float = 0.5  # 0.0-1.0 front/rear balance

    def to_display_string(self) -> str:
        """Format as human-readable car description"""
        return (f"#{self.driver_number} - {self.livery.team_name} "
                f"(Formula Single Seater)")


# Factory function for creating typical liveries
def create_team_livery(team_id: int, team_name: str, 
                       driver_number: int) -> Livery:
    """
    Create livery based on team ID.
    
    Uses a rotation of classic team colors for visual distinction.
    """
    team_colors = [
        (QColor(220, 20, 20), QColor(255, 255, 0), QColor(0, 0, 0)),    # Red/Yellow
        (QColor(0, 80, 180), QColor(255, 255, 255), QColor(255, 165, 0)),  # Blue/White
        (QColor(0, 140, 80), QColor(255, 255, 255), QColor(200, 200, 200)), # Green/White
        (QColor(100, 100, 100), QColor(255, 255, 255), QColor(255, 0, 0)), # Silver/White
        (QColor(200, 0, 120), QColor(255, 215, 0), QColor(255, 255, 255)), # Pink/Gold
    ]
    
    primary, secondary, trim = team_colors[team_id % len(team_colors)]
    return Livery(primary, secondary, trim, team_name, driver_number)
