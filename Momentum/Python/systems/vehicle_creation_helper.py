"""
Vehicle Creation Helper

Creates vehicles with integrated component systems when teams are formed.
Bridges between abstract database Vehicle models and concrete RaceCar instances.

Authors: Final Year Project - Computer Science
"""

from typing import Optional
from database.models.multi_discipline_models import Vehicle, MultiDisciplineTeam
from systems.component_integration import ComponentIntegration
from vehicles.vehicle import RaceCar


class VehicleCreationHelper:
    """
    Helper class for creating vehicles with component integration
    
    This is called when:
    - New teams join a championship (create initial car)
    - Teams develop new cars for new seasons
    - Player selects a team (initialize player team's car components)
    """
    
    def __init__(self, component_integration: ComponentIntegration):
        self.component_integration = component_integration
    
    def create_team_vehicle(
        self, 
        team: MultiDisciplineTeam, 
        season_year: int,
        discipline: str,
        starting_budget_tier: str = "midfield"
    ) -> tuple[Vehicle, RaceCar]:
        """
        Create a vehicle for a team with component integration
        
        Args:
            team: The team creating the vehicle
            season_year: Which season year this car is for
            discipline: Racing discipline (should match team's active disciplines)
            starting_budget_tier: "frontrunner", "midfield", "backmarker"
            
        Returns:
            Tuple of (abstract Vehicle, concrete RaceCar)
        """
        # Determine starting development levels based on budget tier
        dev_levels = self._get_starting_dev_levels(starting_budget_tier, discipline)
        
        # Create abstract Vehicle model
        vehicle = Vehicle(
            id=self._generate_vehicle_id(team.id, season_year),
            team_id=team.id,
            discipline=discipline,
            season_year=season_year,
            overall_performance=dev_levels.get("overall", 0.5),
            aerodynamics=dev_levels.get("aerodynamics", 0.5),
            chassis=dev_levels.get("chassis", 0.5),
            electronics=dev_levels.get("electronics", 0.5),
            reliability=dev_levels.get("reliability", 0.5),
            safety_systems=dev_levels.get("safety_systems", 0.5),
            engine_power=dev_levels.get("engine_power"),
            suspension=dev_levels.get("suspension", 0.5),
            brakes=dev_levels.get("brakes", 0.5),
            transmission=dev_levels.get("transmission", 0.5),
            tires_compound=dev_levels.get("tires_compound", 0.5)
        )
        
        # Create concrete RaceCar with components
        race_car = self.component_integration.create_race_car_from_vehicle(vehicle, team)
        
        return vehicle, race_car
    
    def initialize_player_team_vehicles(self, team: MultiDisciplineTeam) -> None:
        """
        Initialize component systems for player's selected team
        
        This is called when player selects a team at career start.
        Assumes the team already has a Vehicle in the database.
        
        Args:
            team: Player's selected team
        """
        # Use team's discipline
        discipline = team.discipline
        budget = team.budget
        
        # Create a default vehicle if needed
        vehicle, race_car = self.create_team_vehicle(
            team=team,
            season_year=2025,
            discipline=discipline,
            starting_budget_tier=self._determine_budget_tier(budget)
        )
        
        print(f"✓ Initialized components for {team.name}'s {vehicle.discipline} car")
        print(f"  - Car ID: {race_car.car_id}")
        print(f"  - Performance: {vehicle.overall_performance:.1%}")
    
    def _get_starting_dev_levels(self, tier: str, discipline: str) -> dict:
        """
        Get starting development levels based on budget tier
        
        Args:
            tier: "frontrunner", "midfield", "backmarker"
            discipline: Racing discipline
            
        Returns:
            Dict of component -> development level
        """
        # Base levels by tier
        tier_levels = {
            "frontrunner": 0.75,
            "midfield": 0.50,
            "backmarker": 0.35
        }
        
        base_level = tier_levels.get(tier, 0.50)
        
        # Discipline-specific adjustments
        discipline_focus = {
            "SINGLE_SEATER": ["aerodynamics", "chassis", "electronics"],
            "PRODUCTION_TOURING": ["chassis", "suspension", "brakes"],
            "RALLY_STAGE": ["suspension", "transmission", "reliability"],
            "URBAN_STREET": ["electronics", "brakes", "aerodynamics"],
            "DRAG_ACCELERATION": ["engine_power", "transmission", "electronics"],
            "SPRINT_RALLYCROSS": ["suspension", "transmission", "aerodynamics"],
            "ENDURANCE": ["reliability", "brakes", "aerodynamics"]
        }
        
        focus_areas = discipline_focus.get(discipline, [])
        
        # Build development levels
        dev_levels = {
            "overall": base_level,
            "aerodynamics": base_level + (0.1 if "aerodynamics" in focus_areas else 0),
            "chassis": base_level + (0.1 if "chassis" in focus_areas else 0),
            "electronics": base_level + (0.1 if "electronics" in focus_areas else 0),
            "reliability": base_level + (0.1 if "reliability" in focus_areas else 0),
            "safety_systems": base_level,
            "engine_power": base_level + (0.1 if "engine_power" in focus_areas else 0),
            "suspension": base_level + (0.1 if "suspension" in focus_areas else 0),
            "brakes": base_level + (0.1 if "brakes" in focus_areas else 0),
            "transmission": base_level + (0.1 if "transmission" in focus_areas else 0),
            "tires_compound": base_level
        }
        
        # Clamp all values to 0.0-1.0
        return {k: max(0.0, min(1.0, v)) for k, v in dev_levels.items()}
    
    def _determine_budget_tier(self, budget: float) -> str:
        """
        Determine budget tier from team budget
        
        Args:
            budget: Team budget in millions
            
        Returns:
            "frontrunner", "midfield", or "backmarker"
        """
        if budget >= 150.0:
            return "frontrunner"
        elif budget >= 80.0:
            return "midfield"
        else:
            return "backmarker"
    
    def _generate_vehicle_id(self, team_id: int, season_year: int) -> int:
        """
        Generate unique vehicle ID
        
        Args:
            team_id: Team ID
            season_year: Season year
            
        Returns:
            Unique vehicle ID
        """
        # Simple ID generation: team_id * 10000 + season_year
        return team_id * 10000 + season_year


__all__ = ['VehicleCreationHelper']
