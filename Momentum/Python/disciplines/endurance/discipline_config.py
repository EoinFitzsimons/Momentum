"""
Endurance Racing Discipline Configuration
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class EnduranceConfig:
    name: str = "Endurance Racing"
    short_code: str = "EN"
    description: str = "Long-distance multi-driver racing"
    
    typical_race_distance_km: float = 1000.0
    typical_race_duration_minutes: float = 360.0
    typical_grid_size: int = 60
    requires_pit_stops: bool = True
    driver_changes_allowed: bool = True
    
    qualifying_format: str = "average_of_drivers"
    standing_start: bool = True
    weather_dependent: bool = True
    
    refueling_allowed: bool = True
    tire_changes_required: bool = True
    
    points_system: Optional[Dict[int, int]] = None
    
    def __post_init__(self):
        if self.points_system is None:
            self.points_system = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    
    def calculate_points(self, position: int, fastest_lap: bool = False) -> int:
        return self.points_system.get(position, 0)
    
    def get_typical_circuits(self) -> List[str]:
        return ["Le Mans", "Spa 24h", "Nurburgring 24h", "Daytona", "Sebring"]


ENDURANCE_CONFIG = EnduranceConfig()

__all__ = ['EnduranceConfig', 'ENDURANCE_CONFIG']
