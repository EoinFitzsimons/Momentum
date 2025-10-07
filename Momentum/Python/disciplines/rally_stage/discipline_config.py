"""
Rally Stage Discipline Configuration
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class RallyStageConfig:
    """Configuration for Rally Stage racing"""
    
    name: str = "Rally Stage Racing"
    short_code: str = "RS"
    description: str = "Point-to-point time attack on gravel, tarmac, and mixed surfaces"
    
    typical_race_distance_km: float = 25.0
    typical_race_duration_minutes: float = 15.0
    typical_grid_size: int = 1  # Time attack, one at a time
    requires_pit_stops: bool = False
    driver_changes_allowed: bool = False
    
    qualifying_format: str = "time_attack"
    standing_start: bool = True
    
    weather_dependent: bool = True
    wet_tires_available: bool = False  # Uses gravel/snow tires
    safety_car_enabled: bool = False
    
    refueling_allowed: bool = True
    tire_changes_required: bool = False
    
    points_system: Optional[Dict[int, int]] = None
    fastest_lap_bonus: bool = False
    
    def __post_init__(self):
        if self.points_system is None:
            self.points_system = {
                1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
                6: 8, 7: 6, 8: 4, 9: 2, 10: 1
            }
    
    def calculate_points(self, position: int, fastest_lap: bool = False) -> int:
        return self.points_system.get(position, 0)
    
    def get_typical_circuits(self) -> List[str]:
        return [
            "Monte Carlo Rally",
            "Rally Finland",
            "Rally Sweden",
            "Wales Rally GB",
            "Rally Mexico"
        ]


RALLY_STAGE_CONFIG = RallyStageConfig()

__all__ = ['RallyStageConfig', 'RALLY_STAGE_CONFIG']
