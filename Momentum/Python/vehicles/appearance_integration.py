"""
Vehicle Appearance Integration for GUI

Provides utilities to bridge vehicle appearance system with race visualisation.
Handles livery creation, single seater car rendering during races, and telemetry display.

MVP Focus: Single Seater Formula Racing Only
"""

from typing import Dict, Optional
from PyQt6.QtGui import QColor, QPainter
from database.models import Driver, Team
from vehicles.vehicle_appearance import (
    VehicleRenderer, VehicleType, Livery, VehicleConfiguration,
    create_team_livery
)


class VehicleAppearanceManager:
    """Manages vehicle appearance for all race participants"""

    def __init__(self):
        """Initialise appearance cache for drivers"""
        self.vehicle_configs: Dict[int, VehicleConfiguration] = {}
        self.driver_liveries: Dict[int, Livery] = {}

    def create_vehicle_for_driver(self, driver: Driver, team: Team) -> VehicleConfiguration:
        """
        Create vehicle configuration for a driver.

        Args:
            driver: Driver database model
            team: Team database model

        Returns:
            VehicleConfiguration with livery and specifications
        """
        # Use driver.id as the racing number (unique identifier)
        # Phase 1: simple driver-based liveries (teams not yet used)
        livery = create_team_livery(driver.id, f"Driver {driver.id}", driver.id)
        self.driver_liveries[driver.id] = livery

        config = VehicleConfiguration(
            livery=livery,
            driver_number=driver.id,
            team_id=team.id if team is not None else 0,
            fuel_load_kg=105.0,  # Single seater spec fuel
            tire_compound="medium",
            aerodynamic_setup="balanced"
        )

        self.vehicle_configs[driver.id] = config
        return config

    def get_vehicle_config(self, driver_id: int) -> Optional[VehicleConfiguration]:
        """Retrieve vehicle configuration for a driver"""
        return self.vehicle_configs.get(driver_id)

    def get_livery(self, driver_id: int) -> Optional[Livery]:
        """Retrieve livery for a driver"""
        return self.driver_liveries.get(driver_id)

    def render_car_on_track(self, painter: QPainter, driver_id: int,
                           x: float, y: float, rotation: float = 0.0,
                           scale: float = 1.0) -> bool:
        """
        Render a car at track position.

        Args:
            painter: QPainter for drawing
            driver_id: Driver ID
            x: X coordinate on track canvas
            y: Y coordinate on track canvas
            rotation: Rotation angle in degrees
            scale: Scale factor for rendering

        Returns:
            True if rendered successfully, False if driver not found
        """
        config = self.vehicle_configs.get(driver_id)
        if not config:
            return False

        painter.save()
        painter.translate(x, y)
        painter.rotate(rotation)

        VehicleRenderer.render_car(
            painter, VehicleType.SINGLE_SEATER, config.livery, scale
        )

        painter.restore()
        return True

    def get_car_color_for_driver(self, driver_id: int) -> Optional[QColor]:
        """Get primary car colour for a driver (for UI elements)"""
        livery = self.driver_liveries.get(driver_id)
        if livery:
            return livery.primary_color
        return None

    def set_vehicle_setup(self, driver_id: int, fuel_load: Optional[float] = None,
                         tire_compound: Optional[str] = None,
                         aero_setup: Optional[str] = None) -> bool:
        """
        Update vehicle setup parameters during race weekend.

        Args:
            driver_id: Driver ID
            fuel_load: New fuel load in kg
            tire_compound: soft, medium, hard
            aero_setup: low_downforce, balanced, high_downforce

        Returns:
            True if update successful
        """
        config = self.vehicle_configs.get(driver_id)
        if not config:
            return False

        if fuel_load is not None:
            config.fuel_load_kg = fuel_load
        if tire_compound is not None:
            config.tire_compound = tire_compound
        if aero_setup is not None:
            config.aerodynamic_setup = aero_setup

        return True


def get_vehicle_type_for_discipline(discipline: str) -> VehicleType:
    """
    Map racing discipline to vehicle type.

    Args:
        discipline: Discipline name (e.g., SINGLE_SEATER)

    Returns:
        VehicleType - for MVP, always SINGLE_SEATER
    """
    # MVP only supports SINGLE_SEATER
    return VehicleType.SINGLE_SEATER


# Global appearance manager instance
_appearance_manager: Optional[VehicleAppearanceManager] = None


def get_appearance_manager() -> VehicleAppearanceManager:
    """Get or create global appearance manager"""
    global _appearance_manager
    if _appearance_manager is None:
        _appearance_manager = VehicleAppearanceManager()
    return _appearance_manager


def initialize_appearance_manager() -> VehicleAppearanceManager:
    """Initialise appearance manager (called at application startup)"""
    global _appearance_manager
    _appearance_manager = VehicleAppearanceManager()
    return _appearance_manager
