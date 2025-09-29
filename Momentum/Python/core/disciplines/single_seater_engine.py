"""
Single Seater Racing Engine - Formula-style racing simulation

Implements F1, F2, F3 style racing with:
- Qualifying + Main Race format
- Tire strategy and pit stops
- DRS zones and overtaking aids
- Grid penalties and starting procedures
- Points system with fastest lap bonus

Features:
- Multi-session weekend format (Practice, Qualifying, Race)
- Complex tire compound strategy
- Fuel load optimization
- Weather adaptation for different compounds
- DRS effectiveness simulation
- Pit stop execution quality
- Reliability simulation with weather impact

Authors: Final Year Project - Computer Science
"""

import random
from typing import List, Dict, Optional

from database.models import Driver, Team, RaceResult
from .base_engine import BaseDisciplineEngine, DisciplineContext, RacingDiscipline, RaceEventType


class SingleSeaterEngine(BaseDisciplineEngine):
    """
    Single Seater Racing Engine (F1, F2, F3 style)
    
    Simulates Formula-style racing with sophisticated tire strategy,
    pit stops, DRS systems, and weather adaptation. Features both
    qualifying and race simulation with realistic performance factors.
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        self.discipline = RacingDiscipline.SINGLE_SEATER
    
    def get_attribute_weights(self) -> Dict[str, float]:
        """Driver attribute weights for single seater racing (F1/Formula style)"""
        return {
            # Core driving skills (high importance)
            "raw_speed": 0.20,              # Critical for qualifying and race pace
            "consistency": 0.15,            # Essential for championship success
            "racecraft": 0.12,              # Important for wheel-to-wheel racing
            "cornering_skill": 0.15,        # Crucial for single seater performance
            "braking_technique": 0.10,      # Late braking into corners
            
            # Physical and mental traits
            "concentration": 0.08,          # Long race focus
            "reaction_time": 0.06,          # Quick reflexes for starts/overtakes
            "g_force_tolerance": 0.08,      # High G forces in single seaters
            "pressure_handling": 0.06,      # Championship pressure
            
            # Technical knowledge
            "setup_knowledge": 0.10,        # Car setup crucial in F1
            "tire_management": 0.08,        # Strategic tire use
            "fuel_management": 0.06,        # Fuel strategy importance
            "aerodynamics_understanding": 0.08,  # Aero critical in single seaters
            
            # Single seater specific
            "single_seater_aptitude": 0.12, # Natural preference for formula racing
            
            # Race craft and strategy
            "qualifying_optimization": 0.10, # Grid position critical
            "race_strategy": 0.08,          # Strategic thinking
            "overtaking": 0.08,             # Passing ability
            "defensive_driving": 0.06,      # Position defense
            
            # Environmental adaptation
            "wet_weather_skill": 0.08,      # Wet conditions common
            "car_adaptation": 0.06,         # Adapting to car changes
            "track_learning": 0.05,         # Learning new circuits
            
            # Personal traits
            "risk_appetite": 0.04,          # Calculated risk-taking
            "championship_thinking": 0.06   # Long-term strategic view
        }
    
    def get_supported_event_types(self) -> List[RaceEventType]:
        """Single seater supports practice, qualifying, and main race"""
        return [RaceEventType.PRACTICE, RaceEventType.QUALIFYING, RaceEventType.MAIN_RACE]
    
    def get_strategic_elements(self) -> List[str]:
        """Key strategic elements in single-seater racing"""
        return [
            "tire_strategy", "fuel_load", "drs_usage", "pit_timing", 
            "grid_position", "weather_adaptation", "setup_optimization"
        ]
    
    def get_scoring_system(self) -> Dict[str, str]:
        """F1-style scoring system information"""
        return {
            "type": "f1_style",
            "main_points": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],
            "fastest_lap_bonus": 1,
            "fastest_lap_requirement": "top_10_finish"
        }
    
    def simulate_event(self, context: DisciplineContext) -> List[RaceResult]:
        """Route to appropriate simulation based on event type"""
        if context.event_type == RaceEventType.QUALIFYING:
            return self._simulate_qualifying(context)
        elif context.event_type == RaceEventType.MAIN_RACE:
            return self._simulate_race(context)
        elif context.event_type == RaceEventType.PRACTICE:
            return self._simulate_practice(context)
        else:
            raise ValueError(f"Unsupported event type for Single Seater: {context.event_type}")
    
    def _simulate_qualifying(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate F1-style qualifying session
        
        Features:
        - Low fuel qualifying advantage
        - Tire compound strategy
        - Setup optimization impact
        - Track knowledge from practice
        - Weather adaptation
        """
        qualifying_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base performance calculation
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Single seater qualifying factors
            fuel_load_advantage = 0.025  # Qualifying with minimal fuel
            tire_advantage = self._calculate_tire_advantage(team, context)
            setup_optimization = driver.racecraft * 0.02  # Setup knowledge
            track_knowledge = self._calculate_track_knowledge(driver, context)
            weather_adaptation = self._calculate_qualifying_weather_impact(driver, context)
            
            # Random qualifying variance (purple sectors, mistakes)
            qualifying_variance = self.rng.normal(0, 0.015)
            
            total_performance = (
                base_performance + fuel_load_advantage + tire_advantage + 
                setup_optimization + track_knowledge + weather_adaptation + 
                qualifying_variance
            )
            
            qualifying_performance[driver.id] = total_performance
        
        # Sort by performance (higher is better)
        sorted_performance = sorted(qualifying_performance.items(), key=lambda x: x[1], reverse=True)
        results = []
        
        for position, (driver_id, performance) in enumerate(sorted_performance, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=0,  # No points for qualifying in F1 style
                fastest_lap=False,
                dnf_reason=None,
                grid_position=position
            )
            results.append(result)
        
        return results
    
    def _simulate_race(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate F1-style main race
        
        Features:
        - Tire strategy simulation
        - Pit stop execution
        - Fuel strategy optimization
        - DRS effectiveness
        - Weather impact on strategy
        - Mechanical reliability
        """
        race_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base race performance
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Race-specific strategy factors
            tire_strategy_impact = self._simulate_tire_strategy(driver, team, context)
            pit_stop_quality = self._simulate_pit_stops(driver, team, context)
            fuel_strategy = self._simulate_fuel_strategy(driver, team, context)
            race_management = driver.racecraft * 0.03
            
            # DRS and overtaking effectiveness
            drs_effectiveness = self._calculate_drs_effectiveness(driver, context)
            
            # Reliability check
            reliability_factor = self.simulate_reliability(team, context)
            
            # Combine all factors
            total_performance = (
                base_performance * 0.55 + 
                tire_strategy_impact * 0.20 +
                pit_stop_quality * 0.12 +
                fuel_strategy * 0.05 +
                race_management * 0.05 +
                drs_effectiveness * 0.03
            ) * reliability_factor
            
            # Apply race incidents
            final_performance, dnf_reason = self.apply_race_incidents(total_performance, context)
            
            race_performance[driver.id] = (final_performance, dnf_reason)
        
        # Sort by performance
        sorted_performance = sorted(race_performance.items(), key=lambda x: x[1][0], reverse=True)
        results = []
        
        for position, (driver_id, (performance, dnf_reason)) in enumerate(sorted_performance, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            points = self.calculate_points(position, RaceEventType.MAIN_RACE)
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=points if dnf_reason is None else 0,
                fastest_lap=False,  # Will be assigned below
                dnf_reason=dnf_reason,
                grid_position=position  # Would normally come from qualifying
            )
            results.append(result)
        
        # Assign fastest lap bonus (top 10 finishers only)
        self._assign_fastest_lap_bonus(results)
        
        return results
    
    def _simulate_practice(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate practice session (simplified)
        
        Practice sessions are mainly for setup work and don't award points,
        but they contribute to track knowledge for qualifying.
        """
        # Practice results aren't typically stored as race results
        # This is a placeholder for future practice session features
        return []
    
    def _calculate_tire_advantage(self, team: Team, context: DisciplineContext) -> float:
        """Calculate tire compound advantage in qualifying"""
        # Top teams get better tire allocation and strategy
        if team.tier == "tier1":
            return 0.03
        elif team.tier == "tier2":
            return 0.02
        else:
            return 0.01
    
    def _calculate_track_knowledge(self, driver: Driver, context: DisciplineContext) -> float:
        """Calculate track knowledge benefit from practice sessions"""
        # Combines adaptability and consistency for learning track
        track_learning = (driver.adaptability + driver.consistency) / 2.0
        return track_learning * 0.015
    
    def _calculate_qualifying_weather_impact(self, driver: Driver, context: DisciplineContext) -> float:
        """Calculate weather impact specific to qualifying"""
        conditions = context.weather_conditions
        precipitation = conditions["precipitation"]
        
        if precipitation > 1.0:  # Wet conditions
            # Wet weather qualifying is highly skill dependent
            wet_skill = (driver.adaptability * 0.6 + driver.skill * 0.4)
            return (wet_skill - 0.5) * 0.1  # Can be positive or negative
        else:
            # Dry conditions - minimal impact
            return 0.005
    
    def _simulate_tire_strategy(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Simulate tire strategy effectiveness"""
        # Base strategy quality depends on team performance
        team_strategy = self.calculate_team_performance(team) * 0.8
        
        # Driver tire management skills
        tire_management = driver.consistency * 0.4
        
        # Weather adaptation affects tire choice
        weather_conditions = context.weather_conditions
        if weather_conditions["precipitation"] > 0:
            weather_strategy = driver.adaptability * 0.3
        else:
            weather_strategy = 0.1
        
        # Random strategy execution variance
        strategy_execution = self.rng.normal(0, 0.02)
        
        return team_strategy + tire_management + weather_strategy + strategy_execution
    
    def _simulate_pit_stops(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Simulate pit stop execution quality"""
        # Team tier heavily influences pit stop performance
        base_pit_performance = self.calculate_team_performance(team)
        
        # Driver input during pit stops (radio communication, positioning)
        driver_input = driver.racecraft * 0.1
        
        # Random pit stop execution variance
        pit_variance = self.rng.normal(0, 0.08)
        
        pit_performance = base_pit_performance + driver_input + pit_variance
        
        # Clamp between reasonable bounds
        return max(0.1, min(1.0, pit_performance))
    
    def _simulate_fuel_strategy(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Simulate fuel strategy optimization"""
        # Fuel strategy is primarily team-dependent
        team_fuel_strategy = self.calculate_team_performance(team) * 0.6
        
        # Driver fuel management (smooth driving, energy recovery)
        driver_fuel_mgmt = (driver.consistency + driver.racecraft) / 2.0 * 0.2
        
        return team_fuel_strategy + driver_fuel_mgmt
    
    def _calculate_drs_effectiveness(self, driver: Driver, context: DisciplineContext) -> float:
        """Calculate DRS (Drag Reduction System) effectiveness"""
        # Aggressive drivers use DRS more effectively for overtaking
        drs_usage = driver.aggression * 0.025
        
        # Racecraft helps with DRS timing and positioning
        drs_timing = driver.racecraft * 0.015
        
        return drs_usage + drs_timing
    
    def _assign_fastest_lap_bonus(self, results: List[RaceResult]) -> None:
        """Assign fastest lap bonus point to eligible driver"""
        # Only drivers finishing in top 10 are eligible for fastest lap bonus
        top_10_finishers = [r for r in results if r.position <= 10 and r.dnf_reason is None]
        
        if not top_10_finishers:
            return
        
        # Simulate fastest lap probability (weighted toward top performers)
        weights = [1.0 / r.position for r in top_10_finishers]  # Higher positions more likely
        fastest_lap_driver = self.rng.choice(top_10_finishers, p=[w/sum(weights) for w in weights])
        
        fastest_lap_driver.fastest_lap = True
        fastest_lap_driver.points += 1
    
    def calculate_points(self, position: int, event_type: RaceEventType) -> int:
        """Calculate championship points using F1 system"""
        if event_type != RaceEventType.MAIN_RACE:
            return 0  # No points for qualifying or practice
        
        # F1 points system
        points_table = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        
        if position <= len(points_table):
            return points_table[position - 1]
        else:
            return 0


# Export the engine
__all__ = ['SingleSeaterEngine']