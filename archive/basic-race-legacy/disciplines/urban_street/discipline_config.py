"""Urban Street, Drag Acceleration, Sprint Rallycross, and Endurance Discipline Configs"""

# URBAN STREET
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class UrbanStreetConfig:
    name: str = "Urban Street Racing"
    short_code: str = "US"
    description: str = "Street circuit racing in city environments"
    
    typical_race_distance_km: float = 250.0
    typical_race_duration_minutes: float = 90.0
    typical_grid_size: int = 22
    requires_pit_stops: bool = True
    
    qualifying_format: str = "single_lap"
    standing_start: bool = True
    weather_dependent: bool = True
    
    points_system: Optional[Dict[int, int]] = None
    
    def __post_init__(self):
        if self.points_system is None:
            self.points_system = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    
    def calculate_points(self, position: int, fastest_lap: bool = False) -> int:
        return self.points_system.get(position, 0)
    
    def get_typical_circuits(self) -> List[str]:
        return ["Monaco", "Singapore", "Baku", "Miami", "Las Vegas"]


@dataclass
class DragAccelerationConfig:
    name: str = "Drag Acceleration Racing"
    short_code: str = "DA"
    description: str = "Quarter-mile straight-line acceleration racing"
    
    typical_race_distance_km: float = 0.402  # 1/4 mile
    typical_race_duration_minutes: float = 0.25  # ~15 seconds
    typical_grid_size: int = 2  # Head-to-head
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


@dataclass
class EnduranceConfig:
    name: str = "Endurance Racing"
    short_code: str = "EN"
    description: str = "Long-distance multi-driver racing"
    
    typical_race_distance_km: float = 1000.0
    typical_race_duration_minutes: float = 360.0  # 6 hours
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


# Singletons
URBAN_STREET_CONFIG = UrbanStreetConfig()
DRAG_ACCELERATION_CONFIG = DragAccelerationConfig()
SPRINT_RALLYCROSS_CONFIG = SprintRallycrossConfig()
ENDURANCE_CONFIG = EnduranceConfig()
