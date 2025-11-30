"""
Single Seater Discipline Configuration

Metadata and competition parameters for single-seater formula racing.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class SingleSeaterConfig:
    """Configuration and metadata for Single Seater racing"""
    
    # Discipline identity
    name: str = "Single Seater Formula Racing"
    short_code: str = "SS"
    description: str = "Open-wheel formula racing with hybrid power units and advanced aerodynamics"
    
    # Competition format
    typical_race_distance_km: float = 305.0
    typical_race_duration_minutes: float = 90.0
    typical_grid_size: int = 20
    requires_pit_stops: bool = True
    driver_changes_allowed: bool = False
    
    # Starting format
    qualifying_format: str = "elimination"  # Q1, Q2, Q3
    standing_start: bool = True
    formation_lap: bool = True
    
    # Race conditions
    weather_dependent: bool = True
    wet_tires_available: bool = True
    safety_car_enabled: bool = True
    
    # Pit stop rules
    refueling_allowed: bool = False
    tire_changes_required: bool = True
    minimum_pit_stop_duration_seconds: float = 2.0
    minimum_tire_compounds_required: int = 2
    
    # Points system (FIA Formula 1 style)
    points_system: Dict[int, int] = None
    fastest_lap_bonus: bool = True
    fastest_lap_points: int = 1
    
    def __post_init__(self):
        if self.points_system is None:
            self.points_system = {
                1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
                6: 8, 7: 6, 8: 4, 9: 2, 10: 1
            }
    
    def calculate_points(self, position: int, fastest_lap: bool = False, 
                        finished_in_top_10: bool = True) -> int:
        """
        Calculate championship points
        
        Args:
            position: Finishing position (1-indexed)
            fastest_lap: Whether driver achieved fastest lap
            finished_in_top_10: Fastest lap bonus only if finished in top 10
            
        Returns:
            Championship points earned
        """
        points = self.points_system.get(position, 0)
        
        if fastest_lap and self.fastest_lap_bonus and finished_in_top_10:
            points += self.fastest_lap_points
        
        return points
    
    def get_typical_circuits(self) -> List[str]:
        """Get list of typical single-seater circuits"""
        return [
            "Monaco Street Circuit",
            "Silverstone Circuit",
            "Monza Circuit",
            "Spa-Francorchamps",
            "Suzuka Circuit",
            "Circuit of the Americas",
            "Red Bull Ring",
            "Circuit de Barcelona-Catalunya"
        ]


# Singleton instance
SINGLE_SEATER_CONFIG = SingleSeaterConfig()


__all__ = ['SingleSeaterConfig', 'SINGLE_SEATER_CONFIG']
