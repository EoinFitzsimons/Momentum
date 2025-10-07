"""
Base Discipline Engine - Common functionality for all racing disciplines

Provides abstract base class and shared utilities that all discipline-specific
simulation engines inherit from. Contains common performance calculations,
weather impact, and base simulation framework.

Authors: Final Year Project - Computer Science
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from database.models import Driver, Team, Track, Race, RaceResult
from config import RANDOM_SEED


class RacingDiscipline(Enum):
    """Racing discipline categories"""
    SINGLE_SEATER = "SINGLE_SEATER"
    PRODUCTION_TOURING = "PRODUCTION_TOURING"
    RALLY_STAGE = "RALLY_STAGE"
    URBAN_STREET = "URBAN_STREET"
    DRAG_ACCELERATION = "DRAG_ACCELERATION"
    SPRINT_RALLYCROSS = "SPRINT_RALLYCROSS"
    ENDURANCE = "ENDURANCE"


class RaceEventType(Enum):
    """Types of race events within a discipline"""
    QUALIFYING = "qualifying"
    PRACTICE = "practice"
    HEAT = "heat"
    STAGE = "stage"
    MAIN_RACE = "main_race"
    ELIMINATION = "elimination"
    FINAL = "final"


@dataclass
class DisciplineContext:
    """
    Enhanced race context for discipline-specific simulation
    
    Contains all necessary data for simulating races across different
    racing disciplines, with support for discipline-specific parameters.
    """
    # Core race data
    discipline: RacingDiscipline
    event_type: RaceEventType
    race: Race
    track: Track
    drivers: List[Driver]
    teams: Dict[int, Team]
    
    # Environmental conditions
    weather_conditions: Optional[Dict[str, float]] = None
    track_conditions: Optional[Dict[str, float]] = None
    
    # Discipline-specific parameters
    discipline_config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.weather_conditions is None:
            self.weather_conditions = {
                "temperature": 20.0,    # Celsius
                "humidity": 50.0,       # Percentage
                "wind_speed": 5.0,      # km/h
                "precipitation": 0.0,   # mm/h (0 = dry)
                "visibility": 100.0     # Percentage
            }
        
        if self.track_conditions is None:
            self.track_conditions = {
                "grip_level": 1.0,      # 1.0 = optimal grip
                "surface_temp": 25.0,   # Celsius
                "rubbering": 0.5,       # Track rubber buildup (0-1)
                "surface_wear": 0.1     # Track degradation (0-1)
            }
        
        if self.discipline_config is None:
            self.discipline_config = {}


class BaseDisciplineEngine(ABC):
    """
    Abstract base class for discipline-specific simulation engines
    
    Provides common functionality and interface that all racing disciplines
    must implement. Each discipline inherits from this class and implements
    its own unique simulation logic, scoring systems, and race formats.
    
    Common Features:
    - Driver performance calculation with discipline-specific weighting
    - Weather and track impact assessment
    - Team performance evaluation
    - Base statistical methods for race simulation
    
    Abstract Methods (must be implemented by subclasses):
    - simulate_event(): Main simulation logic
    - calculate_points(): Scoring system
    - get_attribute_weights(): Driver attribute importance
    """
    
    def __init__(self, seed: int = RANDOM_SEED):
        """Initialize engine with random seed for reproducible results"""
        self.rng = np.random.RandomState(seed)
        random.seed(seed)
        self.discipline = None  # Set in subclasses
    
    @abstractmethod
    def simulate_event(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate a racing event and return results
        
        Args:
            context: Complete race context with participants and conditions
            
        Returns:
            List of race results with positions, points, and race data
        """
        pass
    
    @abstractmethod
    def calculate_points(self, position: int, event_type: RaceEventType) -> int:
        """
        Calculate championship points for a finishing position
        
        Args:
            position: Finishing position (1-based)
            event_type: Type of event (race, qualifying, etc.)
            
        Returns:
            Points awarded for the position
        """
        pass
    
    @abstractmethod
    def get_attribute_weights(self) -> Dict[str, float]:
        """
        Get driver attribute importance weights for this discipline
        
        Each discipline defines which of the 50+ driver attributes are most
        important and how they should be weighted in performance calculations.
        
        Returns:
            Dictionary mapping attribute names to weight values (0-1)
            Can include any combination of driver attributes like:
            - Core: raw_speed, consistency, racecraft, overtaking, etc.
            - Physical: physical_fitness, reaction_time, concentration, etc.
            - Technical: setup_knowledge, tire_management, fuel_management, etc.
            - Discipline-specific aptitudes: single_seater_aptitude, rally_aptitude, etc.
            - Environmental: wet_weather_skill, night_racing_skill, etc.
        """
        pass
    
    # Common methods available to all disciplines
    
    def get_supported_event_types(self) -> List[RaceEventType]:
        """Get event types supported by this discipline"""
        return [RaceEventType.QUALIFYING, RaceEventType.MAIN_RACE]
    
    def get_scoring_system(self) -> Dict[str, Any]:
        """Get scoring system information for this discipline"""
        return {
            "type": "position_based",
            "points": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        }
    
    def get_strategic_elements(self) -> List[str]:
        """Get list of strategic elements important for this discipline"""
        return ["driver_skill", "team_performance", "weather_adaptation"]
    
    def calculate_base_performance(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """
        Calculate base driver+team performance score using comprehensive attribute system
        
        Uses the full 50+ attribute driver model with discipline-specific weighting
        applied through get_attribute_weights().
        
        Args:
            driver: Driver with comprehensive attributes (50+ attributes)
            team: Team with budget and tier
            context: Race context with conditions
            
        Returns:
            Base performance score (0.0 - 100.0 scale, normalized to 0-1)
        """
        # Get discipline-specific attribute weights
        weights = self.get_attribute_weights()
        
        # Calculate weighted driver performance using new attribute system
        driver_score = 0.0
        total_weight = 0.0
        
        # Core driving skills
        for attr_name, weight in weights.items():
            if hasattr(driver, attr_name):
                attr_value = getattr(driver, attr_name)
                driver_score += (attr_value / 100.0) * weight  # Normalize to 0-1 scale
                total_weight += weight
        
        # Normalize driver score
        if total_weight > 0:
            driver_score /= total_weight
        
        # Team performance based on budget and tier
        team_performance = self.calculate_team_performance(team)
        
        # Environmental factors
        weather_impact = self.calculate_weather_impact(driver, context)
        track_impact = self.calculate_track_impact(driver, context.track)
        
        return (driver_score * 0.5 + team_performance * 0.3 + 
                weather_impact * 0.1 + track_impact * 0.1)
    
    def calculate_team_performance(self, team: Team) -> float:
        """Calculate team performance factor based on tier and budget"""
        tier_multipliers = {"tier1": 0.9, "tier2": 0.7, "tier3": 0.5}
        base = tier_multipliers.get(team.tier, 0.5)
        budget_factor = min(team.budget / 200.0, 1.0) * 0.3  # Max 30% from budget
        return min(base + budget_factor, 1.0)
    
    def calculate_weather_impact(self, driver: Driver, context: DisciplineContext) -> float:
        """
        Calculate weather impact on performance
        
        Weather affects different disciplines differently. This base implementation
        can be overridden by disciplines that need specialized weather handling.
        """
        conditions = context.weather_conditions
        
        # Rain impact varies by discipline
        rain_factor = 1.0 - (conditions["precipitation"] / 20.0)  # Heavy rain = 20mm/h
        rain_adaptation = driver.adaptability * (1.0 - rain_factor) + rain_factor
        
        # Wind impact (varies by discipline)
        wind_impact = 1.0 - (conditions["wind_speed"] / 100.0 * 0.1)  # Max 10% impact
        
        # Temperature impact on performance
        temp_impact = self.calculate_temperature_impact(conditions["temperature"])
        
        return (rain_adaptation * 0.5 + wind_impact * 0.25 + temp_impact * 0.25)
    
    def calculate_temperature_impact(self, temperature: float) -> float:
        """Calculate temperature impact on performance (can be overridden)"""
        # Optimal range is typically 15-25°C
        optimal_temp = 20.0
        temp_deviation = abs(temperature - optimal_temp)
        return max(0.7, 1.0 - (temp_deviation / 30.0))  # Max 30% penalty for extreme temps
    
    def calculate_track_impact(self, driver: Driver, track: Track) -> float:
        """Calculate track suitability impact on performance"""
        # Track difficulty affects adaptability requirement
        difficulty_impact = 1.0 - (track.difficulty * (1.0 - driver.adaptability) * 0.3)
        
        # Surface type preferences (can be overridden by disciplines)
        surface_impact = 1.0  # Default neutral
        
        return difficulty_impact * surface_impact
    
    def simulate_reliability(self, team: Team, context: DisciplineContext) -> float:
        """
        Simulate mechanical reliability for the race
        
        Returns:
            Reliability factor (1.0 = no issues, 0.0 = DNF)
        """
        base_reliability = 0.95 - (0.15 if team.tier == "tier3" else 
                                  0.08 if team.tier == "tier2" else 0.03)
        
        # Weather can affect reliability
        weather_stress = context.weather_conditions["precipitation"] * 0.02
        
        final_reliability = base_reliability - weather_stress
        
        # Random mechanical failure check
        if self.rng.random() > final_reliability:
            return 0.0  # DNF
        
        return 1.0
    
    def apply_race_incidents(self, performance: float, context: DisciplineContext) -> Tuple[float, Optional[str]]:
        """
        Apply random race incidents that can affect performance
        
        Args:
            performance: Current performance score
            context: Race context
            
        Returns:
            Tuple of (modified_performance, dnf_reason)
        """
        incident_roll = self.rng.random()
        
        # Base incident chances
        minor_incident_chance = 0.05  # 5% chance of small issue
        major_incident_chance = 0.02  # 2% chance of major issue
        
        if incident_roll < major_incident_chance:
            # Major incident (DNF)
            return 0.0, random.choice(["mechanical", "accident", "disqualification"])
        elif incident_roll < minor_incident_chance:
            # Minor incident (performance hit)
            return performance * self.rng.uniform(0.7, 0.9), None
        else:
            # No incident
            return performance, None


# Export the base classes
__all__ = [
    'BaseDisciplineEngine', 'DisciplineContext', 'RacingDiscipline', 'RaceEventType'
]