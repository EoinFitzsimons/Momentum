"""
Sprint Rallycross Discipline Configuration
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class SprintRallycrossConfig:
    name: str = "Sprint Rallycross"
    short_code: str = "SR"
    description: str = "Mixed-surface circuit racing with jumps"
    
    typical_race_distance_km: float = 8.0
    typical_race_duration_minutes: float = 6.0
    typical_grid_size: int = 6
    requires_pit_stops: bool = False
    
    qualifying_format: str = "heat_races"
    standing_start: bool = True
    weather_dependent: bool = True
    
    points_system: Optional[Dict[int, int]] = None
    
    def __post_init__(self):
        if self.points_system is None:
            self.points_system = {1: 25, 2: 20, 3: 16, 4: 13, 5: 11, 6: 10}
    
    def calculate_points(self, position: int, fastest_lap: bool = False) -> int:
        return self.points_system.get(position, 0)
    
    def get_typical_circuits(self) -> List[str]:
        return ["Holjes", "Lydden Hill", "Loheac", "Mettet"]


SPRINT_RALLYCROSS_CONFIG = SprintRallycrossConfig()

__all__ = ['SprintRallycrossConfig', 'SPRINT_RALLYCROSS_CONFIG']
