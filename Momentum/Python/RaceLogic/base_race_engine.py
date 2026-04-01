# -*- coding: utf-8 -*-
"""
Base Race Engine - Extensible architecture for multi-discipline racing simulation

Provides abstract base class and shared functionality for all racing disciplines.
Adapted from archive for MVP midpoint demo with focus on single seaters.

Key Features:
- Abstract base class that disciplines inherit from
- Comprehensive driver attribute utilization (50+ attributes)
- Performance calculation weighting: 50% driver, 30% team, 10% weather, 10% track
- Weather and track condition impact modeling
- Reliability and incident simulation
- Event emission system for GUI integration

MVP Status:
- Base architecture complete and extensible
- Single seater implementation in separate file (single_seater_discipline.py)
- Other disciplines can be added by extending BaseDisciplineEngine

Authors: Eoin Fitzsimons

"""

import random
import numpy as np
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from database.models import Driver, Team, Track
from config import RANDOM_SEED, DRIVER_ATTRIBUTE_DEFAULT


class RacingDiscipline(Enum):
    """Racing discipline categories - MVP focuses on SINGLE_SEATER"""
    SINGLE_SEATER = "SINGLE_SEATER"
    PRODUCTION_TOURING = "PRODUCTION_TOURING"
    URBAN_STREET = "URBAN_STREET"
    DRAG_ACCELERATION = "DRAG_ACCELERATION"
    SPRINT_RALLYCROSS = "SPRINT_RALLYCROSS"
    ENDURANCE = "ENDURANCE"


@dataclass
class RaceContext:
    """
    Complete race context for simulation
    
    Contains all necessary data for simulating races with comprehensive
    driver attributes, team performance, and environmental conditions.
    """
    # Core race data
    discipline: RacingDiscipline
    track: Track
    drivers: List[Driver]
    teams: Dict[int, Team]
    total_laps: int

    # Environmental conditions (default to optimal/dry)
    weather_conditions: Dict[str, float] = field(default_factory=lambda: {
        "temperature": 20.0,      # Celsius
        "humidity": 50.0,         # Percentage
        "wind_speed": 5.0,        # km/h
        "precipitation": 0.0,     # mm/h (0 = dry)
        "visibility": 100.0       # Percentage
    })

    track_conditions: Dict[str, Any] = field(default_factory=lambda: {
        "grip_level": 1.0,        # 1.0 = optimal grip
        "surface_temp": 25.0,     # Celsius
        "rubbering": 0.5,         # Track rubber buildup (0-1)
        "surface_wear": 0.1       # Track degradation (0-1)
    })

    # Optional callback for event emission (for GUI integration)
    event_callback: Optional[Callable[[Dict[str, Any]], None]] = None


class BaseDisciplineEngine(ABC):
    """
    Abstract base class for discipline-specific simulation engines

    All racing disciplines (single seater, rally, endurance, etc.) inherit
    from this class and implement discipline-specific logic while sharing
    common performance calculation infrastructure.

    Key Responsibilities:
    - Calculate driver+team performance using comprehensive attribute weighting
    - Model weather and track condition impacts
    - Simulate mechanical reliability and race incidents
    - Provide lap-by-lap race progression
    - Emit events for GUI integration (lap start, standings, DNF, race finish)

    Abstract Methods (must be implemented by subclasses):
    - simulate_race(): Main simulation logic for lap-by-lap racing
    - get_attribute_weights(): Discipline-specific driver attribute importance
    - calculate_lap_time(): Calculate lap time for a driver

    Performance Weighting (default):
    - 50% driver attributes (weighted by get_attribute_weights())
    - 30% team performance (budget, tier, capabilities)
    - 10% weather conditions (rain, wind, temperature)
    - 10% track characteristics (difficulty, surface, layout)
    """

    def __init__(self, seed: int = RANDOM_SEED):
        """
        Initialise engine with random seed for reproducible results

        Args:
            seed: Random seed for numpy and python random generators
        """
        # Initialise numpy random generator (modern API)
        self.rng = np.random.default_rng(seed)
        random.seed(seed)
        self.discipline: Optional[RacingDiscipline] = None

    @abstractmethod
    def simulate_race(self, context: RaceContext) -> List[Dict[str, Any]]:
        """
        Simulate a complete race and return final results

        Must be implemented by each discipline to handle lap-by-lap simulation,
        event emission, and result compilation.

        Args:
            context: Complete race context with drivers, track, conditions

        Returns:
            List of result dictionaries with driver_id, position, time, etc.
        """
        pass

    @abstractmethod
    def get_attribute_weights(self) -> Dict[str, float]:
        """
        Get driver attribute importance weights for this discipline

        Each discipline defines which of the 50+ driver attributes are most
        important and how they should be weighted in performance calculations.

        Returns:
            Dictionary mapping attribute names to weight values (0-1 scale).
            Example for single seaters:
            {
                "raw_speed": 0.20,              # Critical for lap time
                "consistency": 0.15,            # Essential for race performance
                "cornering_skill": 0.15,        # Crucial in formula racing
                "single_seater_aptitude": 0.12, # Discipline preference
                "tire_management": 0.08,        # Strategic importance
                "concentration": 0.08,          # Mental endurance
                # ... more attributes
            }

        Available Attribute Categories:
        - Core skills: raw_speed, consistency, racecraft, overtaking,
          defending, etc.
        - Physical: fitness, reaction_time, concentration,
          g_force_tolerance, etc.
        - Environmental: wet_weather_skill, night_racing_skill, etc.
        """
        pass

    @abstractmethod
    def calculate_lap_time(self, driver: Driver, team: Team,
                          context: RaceContext,
                          lap_number: int, current_position: int) -> float:
        """
        Calculate lap time for a driver considering all factors

        Must be implemented by each discipline to apply discipline-specific
        lap time calculations (tire wear, fuel load, traffic, etc.).

        Args:
            driver: Driver with comprehensive attributes
            team: Team with budget and tier
            context: Race context with track and conditions
            lap_number: Current lap number (for tire/fuel degradation)
            current_position: Driver's current race position (for traffic)

        Returns:
            Lap time in seconds
        """
        pass

    # ====================================================================
    # Common Methods - Available to all disciplines
    # ====================================================================

    def calculate_base_performance(self, driver: Driver, team: Team,
                                  context: RaceContext) -> float:
        """Calculate base driver and team performance score.
        
        Uses the full 50+ attribute driver model with discipline-specific
        weighting applied through get_attribute_weights(). This is the
        foundation of all performance calculations.
        
        Performance Weighting:
        - 50% driver skill (weighted by discipline-specific attributes)
        - 30% team performance (budget, tier, capabilities)
        - 10% weather impact (rain, wind, temperature)
        - 10% track impact (difficulty, surface, layout)

        Args:
            driver: Driver with 50+ attributes (0-100 scale)
            team: Team with budget and tier
            context: Race context with conditions

        Returns:
            Base performance score (0.0 to 1.0 scale, normalized)
        """
        # Get discipline-specific attribute weights
        weights = self.get_attribute_weights()

        # Calculate weighted driver performance using comprehensive attributes
        driver_score = 0.0
        total_weight = 0.0

        # Use canonical-aware attribute lookup so discipline weightings that
        # reference legacy names still compute values derived from the
        # canonical schema. This avoids creating synthesized legacy fields.
        from services.driver_attributes import get_attribute_value

        for attr_name, weight in weights.items():
            try:
                attr_value = get_attribute_value(driver, attr_name)
            except Exception:
                attr_value = DRIVER_ATTRIBUTE_DEFAULT if 'DRIVER_ATTRIBUTE_DEFAULT' in globals() else 50.0

            if attr_value is not None:
                # Normalize attribute (0-100 scale) to 0-1 scale
                normalized_value = float(attr_value) / 100.0
                driver_score += normalized_value * weight
                total_weight += weight

        # Normalize driver score to 0-1 scale
        if total_weight > 0:
            driver_score /= total_weight
        else:
            driver_score = 0.5  # Default if no attributes found

        # Team performance based on budget and tier
        team_performance = self._calculate_team_performance(team)

        # Environmental factors
        weather_impact = self._calculate_weather_impact(driver, context)
        track_impact = self._calculate_track_impact(driver, context.track)

        # Combine with default weighting:
        # 50% driver, 30% team, 10% weather, 10% track
        return (driver_score * 0.5 +
                team_performance * 0.3 +
                weather_impact * 0.1 +
                track_impact * 0.1)
    
    def _calculate_team_performance(self, team: Team) -> float:
        """
        Calculate team performance factor based on tier and budget

        Args:
            team: Team with tier and budget attributes

        Returns:
            Team performance factor (0.0 to 1.0)
        """
        # Base performance by tier
        tier_multipliers = {
            "tier1": 0.9,  # Top tier teams
            "tier2": 0.7,  # Mid tier teams
            "tier3": 0.5   # Lower tier teams
        }
        base_performance = tier_multipliers.get(team.tier.lower(), 0.5)

        # Budget factor (up to 30% bonus, capped at 1.0)
        # Assuming €200M is maximum budget
        budget_factor = min(team.budget / 200.0, 1.0) * 0.3

        return min(base_performance + budget_factor, 1.0)
    
    def _calculate_weather_impact(self, driver: Driver,
                                  context: RaceContext) -> float:
        """
        Calculate weather impact on performance

        Weather affects different disciplines differently. Subclasses can
        override for specialized weather handling.

        Args:
            driver: Driver with weather-related attributes
            context: Race context with weather conditions

        Returns:
            Weather impact factor (0.0 to 1.0)
        """
        conditions = context.weather_conditions

        # Rain impact - heavy rain reduces performance unless skilled
        precipitation = conditions["precipitation"]
        if precipitation > 0.5:  # Wet conditions (>0.5mm/h)
            # Use wet_weather_skill if available, otherwise adaptability
            wet_skill = getattr(driver, 'wet_weather_skill',
                              driver.adaptability)
            rain_factor = 1.0 - (precipitation / 20.0)
            rain_adaptation = ((wet_skill / 100.0) *
                             (1.0 - rain_factor) + rain_factor)
        else:
            rain_adaptation = 1.0

        # Wind impact (up to 10% reduction)
        wind_speed = conditions["wind_speed"]
        wind_impact = max(0.9, 1.0 - (wind_speed / 100.0))

        # Temperature impact on performance
        temperature = conditions["temperature"]
        temp_impact = self._calculate_temperature_impact(temperature)

        # Combine factors (weights: 50% rain, 25% wind, 25% temperature)
        return (rain_adaptation * 0.5 + wind_impact * 0.25 +
                temp_impact * 0.25)
    
    def _calculate_temperature_impact(self,
                                     temperature: float) -> float:
        """Calculate temperature impact on performance.
        
        Optimal temperature range is typically 15 to 25 degrees Celsius.
        Extreme temperatures reduce performance unless driver has heat
        or cold tolerance.
        
        Args:
            temperature: Temperature in Celsius
        
        Returns:
            Temperature impact factor (0.7 to 1.0)
        """
        optimal_temp = 20.0
        temp_deviation = abs(temperature - optimal_temp)
        # Max 30% penalty for extreme temperatures (+40C or -10C)
        return max(0.7, 1.0 - (temp_deviation / 30.0))
    
    def _calculate_track_impact(self, driver: Driver,
                               track: Track) -> float:
        """
        Calculate track suitability impact on performance

        Track difficulty, surface type, and layout characteristics affect
        driver performance based on adaptability and track learning
        ability.

        Args:
            driver: Driver with track-related attributes
            track: Track with difficulty and characteristics

        Returns:
            Track impact factor (0.0 to 1.0)
        """
        # Track difficulty affects adaptability requirement
        difficulty = getattr(track, 'difficulty', 5) / 10.0
        adaptability = driver.adaptability / 100.0
        difficulty_impact = 1.0 - (difficulty *
                                  (1.0 - adaptability) * 0.3)

        # Track learning ability
        track_learning = getattr(driver, 'track_learning',
                                driver.adaptability) / 100.0
        learning_impact = 0.9 + (track_learning * 0.1)

        return difficulty_impact * learning_impact
    
    def check_mechanical_failure(self, team: Team,
                                context: RaceContext,
                                lap_number: int) -> Optional[str]:
        """
        Check if mechanical failure occurs on this lap

        Reliability simulation based on team tier, weather stress, and
        random chance. Lower tier teams and harsh conditions increase
        failure probability.

        Args:
            team: Team with tier attribute
            context: Race context with weather conditions
            lap_number: Current lap number

        Returns:
            DNF reason string if failure occurs, None otherwise
        """
        # Base reliability by tier (% chance of failure per lap)
        tier_failure_rates = {
            "tier1": 0.0003,  # 0.03% per lap (~2% over 60 laps)
            "tier2": 0.0008,  # 0.08% per lap (~5% over 60 laps)
            "tier3": 0.0015   # 0.15% per lap (~9% over 60 laps)
        }
        base_failure_rate = tier_failure_rates.get(team.tier.lower(),
                                                   0.001)

        # Weather increases failure rate
        precipitation = context.weather_conditions["precipitation"]
        weather_stress = precipitation * 0.0002

        # Temperature extremes increase failure rate
        temperature = context.weather_conditions["temperature"]
        if temperature > 35 or temperature < 5:
            temp_stress = 0.0003
        else:
            temp_stress = 0.0

        total_failure_rate = (base_failure_rate + weather_stress +
                             temp_stress)

        # Random failure check
        if self.rng.random() < total_failure_rate:
            # Determine failure type
            failure_types = ["mechanical", "engine", "gearbox",
                           "suspension", "electrical"]
            return random.choice(failure_types)

        return None
    
    def check_race_incident(self, driver: Driver,
                          context: RaceContext,
                          lap_number: int,
                          current_position: int) -> Optional[str]:
        """Check if driver is involved in race incident.
        
        Incidents (crashes, spins, contact) are more likely for aggressive
        drivers, in poor conditions, and early in the race when traffic is
        dense.
        
        Args:
            driver: Driver with consistency and aggression attributes
            context: Race context with conditions
            lap_number: Current lap number
            current_position: Driver current position
        
        Returns:
            DNF reason string if incident occurs, None otherwise
        """
        # Base incident rate (low probability)
        base_incident_rate = 0.0002  # 0.02% per lap

        # Consistency reduces incident risk
        consistency_factor = 1.0 - (driver.consistency / 200.0)

        # Aggression increases incident risk slightly
        aggression_factor = 1.0 + (driver.aggression / 500.0)

        # Weather increases incident risk
        precipitation = context.weather_conditions["precipitation"]
        if precipitation > 1.0:
            weather_factor = 1.0 + (precipitation / 10.0)
        else:
            weather_factor = 1.0

        # Traffic increases incident risk (first lap most dangerous)
        if lap_number == 1:
            traffic_factor = 3.0
        elif lap_number <= 5:
            traffic_factor = 2.0
        else:
            traffic_factor = 1.0

        total_incident_rate = (base_incident_rate * consistency_factor *
                              aggression_factor * weather_factor *
                              traffic_factor)

        # Random incident check
        if self.rng.random() < total_incident_rate:
            # Determine incident type
            incident_types = ["accident", "collision", "spin",
                            "off_track"]
            return random.choice(incident_types)

        return None
    
    def emit_event(self, event_type: str, data: Dict[str, Any],
                  context: RaceContext):
        """
        Emit race event to callback (for GUI integration)

        Args:
            event_type: Type of event (lap_start, standings, dnf,
                       race_finished)
            data: Event data dictionary
            context: Race context with event callback
        """
        if context.event_callback:
            event = {"type": event_type, **data}
            try:
                context.event_callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")


# Export the base classes and enums
__all__ = [
    'BaseDisciplineEngine',
    'RaceContext',
    'RacingDiscipline'
]
