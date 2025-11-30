"""
Production Touring Discipline Configuration

Metadata and competition parameters for production-based touring car racing.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ProductionTouringConfig:
    """Configuration and metadata for Production Touring racing"""
    
    name: str = "Production Touring Car Racing"
    short_code: str = "PT"
    description: str = "Production-based sedan and coupe racing with close competition"
    
    # Competition format
    typical_race_distance_km: float = 100.0
    typical_race_duration_minutes: float = 45.0
    typical_grid_size: int = 26
    requires_pit_stops: bool = False
    driver_changes_allowed: bool = False
    
    qualifying_format: str = "single_lap"
    standing_start: bool = True
    
    weather_dependent: bool = True
    wet_tires_available: bool = True
    safety_car_enabled: bool = True
    
    # Pit stop rules
    refueling_allowed: bool = False
    tire_changes_required: bool = False
    minimum_pit_stop_duration_seconds: float = 0.0
    
    # Points system
    points_system: Optional[Dict[int, int]] = None
    fastest_lap_bonus: bool = False
    
    def __post_init__(self):
        if self.points_system is None:
            self.points_system = {
                1: 25, 2: 20, 3: 16, 4: 13, 5: 11,
                6: 10, 7: 9, 8: 8, 9: 7, 10: 6,
                11: 5, 12: 4, 13: 3, 14: 2, 15: 1
            }
    
    def calculate_points(self, position: int, fastest_lap: bool = False) -> int:
        return self.points_system.get(position, 0)
    
    def get_typical_circuits(self) -> List[str]:
        return [
            "Brands Hatch",
            "Oulton Park",
            "Donington Park",
            "Thruxton Circuit",
            "Snetterton Circuit"
        ]


PRODUCTION_TOURING_CONFIG = ProductionTouringConfig()

__all__ = ['ProductionTouringConfig', 'PRODUCTION_TOURING_CONFIG']
