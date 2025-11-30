"""
Drag Acceleration Discipline Configuration
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class DragAccelerationConfig:
    name: str = "Drag Acceleration Racing"
    short_code: str = "DA"
    description: str = "Quarter-mile straight-line acceleration racing"
    
    typical_race_distance_km: float = 0.402
    typical_race_duration_minutes: float = 0.25
    typical_grid_size: int = 2
    requires_pit_stops: bool = False
    
    qualifying_format: str = "elimination"
    standing_start: bool = True
    weather_dependent: bool = True
    
    points_system: Optional[Dict[int, int]] = None
    
    def __post_init__(self):
        if self.points_system is None:
            self.points_system = {1: 10, 2: 5, 3: 3, 4: 1}
    
    def calculate_points(self, position: int, fastest_lap: bool = False) -> int:
        return self.points_system.get(position, 0)
    
    def get_typical_circuits(self) -> List[str]:
        return ["Santa Pod", "NHRA Indianapolis", "Sydney Dragway"]


DRAG_ACCELERATION_CONFIG = DragAccelerationConfig()

__all__ = ['DragAccelerationConfig', 'DRAG_ACCELERATION_CONFIG']
