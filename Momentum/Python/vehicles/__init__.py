"""
Vehicles Module - Single Seater Focus

Racing vehicle systems including:
- Single seater (Formula) car rendering with realistic detail
- Aerodynamic elements (front wing, DRS flap, rear wing)
- Visible mechanical components (suspension, wheels, cockpit)
- Livery management (team colors, driver numbers)
- Vehicle configuration (fuel, tires, brake balance)
- GUI integration for race visualisation

MVP focuses exclusively on Formula-style open-wheel single seater racing.
"""

from vehicles.vehicle_appearance import (
    VehicleType,
    Livery,
    VehicleRenderer,
    VehicleConfiguration,
    create_team_livery,
)
from vehicles.appearance_integration import (
    VehicleAppearanceManager,
    get_appearance_manager,
    initialize_appearance_manager,
    get_vehicle_type_for_discipline,
)

__all__ = [
    "VehicleType",
    "Livery",
    "VehicleRenderer",
    "VehicleConfiguration",
    "create_team_livery",
    "VehicleAppearanceManager",
    "get_appearance_manager",
    "initialize_appearance_manager",
    "get_vehicle_type_for_discipline",
]
