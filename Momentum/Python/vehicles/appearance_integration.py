"""
Vehicle Appearance Integration for GUI.

Provides utilities to bridge vehicle appearance system with race visualisation,
including discipline-specific vehicle model selection.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, TYPE_CHECKING
from database.models import Driver, Team
from vehicles.vehicle_appearance import (
    QColor,
    VehicleRenderer,
    VehicleType,
    Livery,
    VehicleConfiguration,
    create_team_livery,
)

if TYPE_CHECKING:
    from PyQt6.QtGui import QPainter


class VehicleAppearanceManager:
    """Manages vehicle appearance for all race participants"""

    def __init__(self):
        """Initialise appearance cache for drivers"""
        self.vehicle_configs: Dict[int, VehicleConfiguration] = {}
        self.driver_liveries: Dict[int, Livery] = {}
        self.driver_vehicle_types: Dict[int, VehicleType] = {}

    def create_vehicle_for_driver(
        self, driver: Driver, team: Team
    ) -> VehicleConfiguration:
        """
        Create vehicle configuration for a driver.

        Args:
            driver: Driver database model
            team: Team database model

        Returns:
            VehicleConfiguration with livery and specifications
        """
        # Use driver.id as the racing number (unique identifier)
        livery = create_team_livery(driver.id, f"Driver {driver.id}", driver.id)
        self.driver_liveries[driver.id] = livery
        team_discipline = (
            getattr(team, "discipline", None) if team is not None else None
        )
        vehicle_type = get_vehicle_type_for_discipline(
            str(team_discipline or "SINGLE_SEATER")
        )
        self.driver_vehicle_types[driver.id] = vehicle_type

        config = VehicleConfiguration(
            livery=livery,
            driver_number=driver.id,
            team_id=team.id if team is not None else 0,
            fuel_load_kg=105.0,  # Single seater spec fuel
            tyre_compound="medium",
            aerodynamic_setup="balanced",
        )

        self.vehicle_configs[driver.id] = config
        return config

    def get_vehicle_config(self, driver_id: int) -> Optional[VehicleConfiguration]:
        """Retrieve vehicle configuration for a driver"""
        return self.vehicle_configs.get(driver_id)

    def get_livery(self, driver_id: int) -> Optional[Livery]:
        """Retrieve livery for a driver"""
        return self.driver_liveries.get(driver_id)

    def render_car_on_track(
        self,
        painter: QPainter,
        driver_id: int,
        x: float,
        y: float,
        rotation: float = 0.0,
        scale: float = 1.0,
    ) -> bool:
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
            painter, self.get_vehicle_type(driver_id), config.livery, scale
        )

        painter.restore()
        return True

    def get_car_color_for_driver(self, driver_id: int) -> Optional[QColor]:
        """Get primary car colour for a driver (for UI elements)"""
        livery = self.driver_liveries.get(driver_id)
        if livery:
            return livery.primary_color
        return None

    def set_vehicle_type(self, driver_id: int, discipline: str) -> None:
        """Persist resolved vehicle type for a driver."""
        self.driver_vehicle_types[driver_id] = get_vehicle_type_for_discipline(
            discipline
        )

    def get_vehicle_type(
        self, driver_id: int, default_discipline: str = "SINGLE_SEATER"
    ) -> VehicleType:
        """Return cached driver vehicle type, falling back to discipline mapping."""
        return self.driver_vehicle_types.get(
            driver_id, get_vehicle_type_for_discipline(default_discipline)
        )

    def set_vehicle_setup(
        self,
        driver_id: int,
        fuel_load: Optional[float] = None,
        tyre_compound: Optional[str] = None,
        aero_setup: Optional[str] = None,
    ) -> bool:
        """
        Update vehicle setup parameters during race weekend.

        Args:
            driver_id: Driver ID
            fuel_load: New fuel load in kg
            tyre_compound: soft, medium, hard
            aero_setup: low_downforce, balanced, high_downforce

        Returns:
            True if update successful
        """
        config = self.vehicle_configs.get(driver_id)
        if not config:
            return False

        if fuel_load is not None:
            config.fuel_load_kg = fuel_load
        # Use canonical parameter `tyre_compound`
        if tyre_compound is not None:
            config.tyre_compound = tyre_compound
        if aero_setup is not None:
            config.aerodynamic_setup = aero_setup

        return True


def get_vehicle_type_for_discipline(discipline: str) -> VehicleType:
    """
    Map racing discipline to vehicle type.

    Args:
        discipline: Discipline name (e.g., SINGLE_SEATER)

    Returns:
        VehicleType matching the discipline
    """
    normalized = re.sub(
        r"[^a-z0-9]+", "_", str(discipline or "").strip().lower()
    ).strip("_")
    mapping = {
        "single_seater": VehicleType.SINGLE_SEATER,
        "production_touring": VehicleType.PRODUCTION_TOURING,
        "production_touring_gt": VehicleType.PRODUCTION_TOURING,
        "urban_street": VehicleType.URBAN_STREET,
        "drag_acceleration": VehicleType.DRAG_ACCELERATION,
        "sprint_rallycross": VehicleType.SPRINT_RALLYCROSS,
        "endurance": VehicleType.ENDURANCE,
    }
    return mapping.get(normalized, VehicleType.SINGLE_SEATER)


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
