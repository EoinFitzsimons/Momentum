"""
Endurance Racing Engine - Long-distance multi-driver racing simulation

Implements endurance racing with:
- Multi-driver stints and driver changes
- Fuel strategy and pit stop management
- Reliability and mechanical preservation
- Day/night racing transitions
- Weather evolution over long races
- Strategic tire and fuel management

Features:
- Driver rotation and stint management
- Long-term fuel and tire strategy
- Mechanical reliability over distance
- Day/night cycle performance changes
- Weather evolution simulation
- Safety car and caution periods
- Multi-class racing with different regulations

Authors: Final Year Project - Computer Science
"""

import random
from typing import List, Dict, Optional, Tuple
from enum import Enum

from database.models import Driver, Team, RaceResult
from .base_engine import BaseDisciplineEngine, DisciplineContext, RacingDiscipline, RaceEventType


class EnduranceRaceLength(Enum):
    """Endurance race duration categories"""
    SPRINT_ENDURANCE = "sprint"      # 2-4 hours
    CLASSIC_ENDURANCE = "classic"    # 6-12 hours  
    LEGENDARY_ENDURANCE = "legendary" # 24+ hours


class RacePhase(Enum):
    """Different phases of endurance races"""
    DAY_START = "day_start"
    DAY_MIDDLE = "day_middle"
    SUNSET = "sunset"
    NIGHT = "night"
    SUNRISE = "sunrise"
    DAY_FINISH = "day_finish"


class EnduranceEngine(BaseDisciplineEngine):
    """
    Endurance Racing Engine
    
    Simulates long-distance racing emphasizing reliability, strategy,
    driver management, and mechanical preservation over extended
    periods with multiple drivers per car.
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        self.discipline = RacingDiscipline.ENDURANCE
        self.driver_stints = {}  # Track driver stint performance
        self.mechanical_health = {}  # Track car reliability
    
    def get_attribute_weights(self) -> Dict[str, float]:
        """Driver attribute weights for endurance racing"""
        return {
            "skill": 0.25,        # Important for stint performance
            "consistency": 0.40,   # Most critical for long races
            "racecraft": 0.15,     # Some wheel-to-wheel racing
            "adaptability": 0.25,  # Changing conditions over time
            "aggression": 0.10     # Least important - preservation focus
        }
    
    def get_supported_event_types(self) -> List[RaceEventType]:
        """Endurance supports practice, qualifying, and race"""
        return [RaceEventType.QUALIFYING, RaceEventType.MAIN_RACE]
    
    def get_strategic_elements(self) -> List[str]:
        """Key strategic elements in endurance racing"""
        return [
            "fuel_strategy", "tire_management", "driver_rotation", "reliability_management",
            "stint_planning", "safety_car_strategy", "day_night_adaptation", "mechanical_preservation"
        ]
    
    def get_scoring_system(self) -> Dict[str, str]:
        """Endurance racing scoring system"""
        return {
            "type": "endurance_championship",
            "distance_bonus": True,
            "reliability_bonus": True,
            "class_positions": True,
            "manufacturers_points": True
        }
    
    def simulate_event(self, context: DisciplineContext) -> List[RaceResult]:
        """Route to appropriate simulation based on event type"""
        if context.event_type == RaceEventType.QUALIFYING:
            return self._simulate_endurance_qualifying(context)
        elif context.event_type == RaceEventType.MAIN_RACE:
            return self._simulate_endurance_race(context)
        else:
            raise ValueError(f"Unsupported event type for Endurance Racing: {context.event_type}")
    
    def _simulate_endurance_qualifying(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate endurance qualifying session
        
        Focus on consistent lap times rather than single fast laps.
        Often uses average of multiple laps or longest stint pace.
        """
        qualifying_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base performance with endurance focus
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Endurance qualifying factors
            consistency_factor = driver.consistency * 0.025  # High importance
            stint_simulation = self._simulate_qualifying_stint(driver, team, context)
            fuel_load_impact = -0.01  # Qualifying with race fuel load
            
            # Less emphasis on single-lap pace
            peak_performance_factor = 0.8  # Not about one fast lap
            
            total_performance = (
                base_performance * peak_performance_factor +
                consistency_factor +
                stint_simulation +
                fuel_load_impact
            )
            
            qualifying_performance[driver.id] = total_performance
        
        # Sort by performance
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
                points=0,  # No qualifying points in endurance
                fastest_lap=False,
                dnf_reason=None,
                grid_position=position
            )
            results.append(result)
        
        return results
    
    def _simulate_endurance_race(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate full endurance race with multiple stints and drivers
        
        Features:
        - Multiple driver stints per car
        - Long-term strategy decisions
        - Mechanical reliability simulation
        - Day/night racing conditions
        - Safety car periods
        """
        # Determine race length and characteristics
        race_length = self._determine_race_length(context)
        race_phases = self._generate_race_phases(race_length)
        
        # Initialize race tracking
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            self.mechanical_health[driver.id] = 1.0
            self.driver_stints[driver.id] = []
        
        # Simulate race in phases
        cumulative_performance = {}
        total_incidents = {}
        
        for driver in context.drivers:
            cumulative_performance[driver.id] = 0.0
            total_incidents[driver.id] = None
        
        for phase_num, race_phase in enumerate(race_phases):
            phase_results = self._simulate_race_phase(context, race_phase, phase_num)
            
            # Accumulate performance
            for driver_id, phase_performance in phase_results.items():
                if total_incidents[driver_id] is None:  # Still running
                    cumulative_performance[driver_id] += phase_performance['performance']
                    
                    # Check for incidents
                    if phase_performance.get('dnf_reason'):
                        total_incidents[driver_id] = phase_performance['dnf_reason']
                    
                    # Update mechanical health
                    self.mechanical_health[driver_id] *= phase_performance.get('reliability_factor', 1.0)
        
        # Calculate final results
        final_results = []
        
        # Sort by cumulative performance (active drivers first)
        active_drivers = [(driver_id, perf) for driver_id, perf in cumulative_performance.items() 
                         if total_incidents[driver_id] is None]
        retired_drivers = [(driver_id, perf) for driver_id, perf in cumulative_performance.items() 
                          if total_incidents[driver_id] is not None]
        
        active_drivers.sort(key=lambda x: x[1], reverse=True)
        retired_drivers.sort(key=lambda x: x[1], reverse=True)
        
        all_drivers = active_drivers + retired_drivers
        
        for position, (driver_id, final_performance) in enumerate(all_drivers, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            points = self.calculate_points(position, RaceEventType.MAIN_RACE)
            
            # Reliability bonus for finishers
            if total_incidents[driver_id] is None:
                reliability_bonus = self._calculate_reliability_bonus(self.mechanical_health[driver_id])
                points += reliability_bonus
            else:
                points = 0
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=points,
                fastest_lap=False,  # Will be assigned separately
                dnf_reason=total_incidents[driver_id],
                grid_position=position
            )
            final_results.append(result)
        
        # Assign fastest lap to a finisher with good pace
        self._assign_endurance_fastest_lap(final_results)
        
        return final_results
    
    def _determine_race_length(self, context: DisciplineContext) -> EnduranceRaceLength:
        """Determine the type of endurance race"""
        discipline_config = getattr(context, 'discipline_config', {})
        length_type = discipline_config.get('endurance_length', 'classic')
        
        length_map = {
            'sprint': EnduranceRaceLength.SPRINT_ENDURANCE,
            'classic': EnduranceRaceLength.CLASSIC_ENDURANCE,
            'legendary': EnduranceRaceLength.LEGENDARY_ENDURANCE
        }
        
        return length_map.get(length_type, EnduranceRaceLength.CLASSIC_ENDURANCE)
    
    def _generate_race_phases(self, race_length: EnduranceRaceLength) -> List[RacePhase]:
        """Generate race phases based on race length"""
        if race_length == EnduranceRaceLength.SPRINT_ENDURANCE:
            # 2-4 hour race - mostly day racing
            return [RacePhase.DAY_START, RacePhase.DAY_MIDDLE, RacePhase.DAY_FINISH]
        
        elif race_length == EnduranceRaceLength.CLASSIC_ENDURANCE:
            # 6-12 hour race - day to night
            return [
                RacePhase.DAY_START, RacePhase.DAY_MIDDLE, RacePhase.SUNSET,
                RacePhase.NIGHT, RacePhase.DAY_FINISH
            ]
        
        else:  # LEGENDARY_ENDURANCE (24+ hours)
            # Full day/night cycle
            return [
                RacePhase.DAY_START, RacePhase.DAY_MIDDLE, RacePhase.SUNSET,
                RacePhase.NIGHT, RacePhase.SUNRISE, RacePhase.DAY_MIDDLE, RacePhase.DAY_FINISH
            ]
    
    def _simulate_race_phase(self, context: DisciplineContext, race_phase: RacePhase, 
                           phase_num: int) -> Dict:
        """Simulate a single phase of the endurance race"""
        phase_results = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Skip if already retired
            if self.mechanical_health[driver.id] <= 0:
                phase_results[driver.id] = {
                    'performance': 0.0,
                    'reliability_factor': 0.0,
                    'dnf_reason': 'mechanical'
                }
                continue
            
            # Calculate phase performance
            phase_performance = self._calculate_phase_performance(driver, team, context, race_phase)
            
            # Driver stint management
            stint_performance = self._simulate_driver_stint(driver, team, context, phase_num)
            
            # Reliability degradation
            reliability_factor = self._calculate_reliability_degradation(driver, team, context, race_phase)
            
            # Strategic elements
            strategy_impact = self._calculate_strategy_impact(driver, team, context, race_phase)
            
            total_performance = phase_performance + stint_performance + strategy_impact
            
            # Apply endurance incidents
            final_performance, dnf_reason = self._apply_endurance_incidents(
                total_performance, driver, team, context, race_phase
            )
            
            phase_results[driver.id] = {
                'performance': final_performance,
                'reliability_factor': reliability_factor,
                'dnf_reason': dnf_reason
            }
        
        return phase_results
    
    def _calculate_phase_performance(self, driver: Driver, team: Team, context: DisciplineContext, 
                                   race_phase: RacePhase) -> float:
        """Calculate performance for specific race phase"""
        base_performance = self.calculate_base_performance(driver, team, context)
        
        # Phase-specific modifiers
        phase_modifiers = {
            RacePhase.DAY_START: 0.02,    # Fresh start bonus
            RacePhase.DAY_MIDDLE: 0.0,    # Baseline
            RacePhase.SUNSET: -0.01,      # Visibility transition
            RacePhase.NIGHT: -0.03,       # Reduced visibility
            RacePhase.SUNRISE: -0.02,     # Fatigue + visibility change
            RacePhase.DAY_FINISH: -0.04   # Maximum fatigue
        }
        
        phase_modifier = phase_modifiers.get(race_phase, 0.0)
        
        # Adaptability helps with changing conditions
        adaptation_bonus = driver.adaptability * 0.0002
        
        return base_performance * 0.3 + phase_modifier + adaptation_bonus
    
    def _simulate_driver_stint(self, driver: Driver, team: Team, context: DisciplineContext, 
                             phase_num: int) -> float:
        """Simulate individual driver stint performance"""
        # Consistency is key for stint performance
        stint_consistency = driver.consistency * 0.001
        
        # Fatigue accumulation over phases
        fatigue_factor = phase_num * 0.005
        
        # Driver's endurance ability (based on consistency and adaptability)
        endurance_ability = (driver.consistency + driver.adaptability) / 2.0 * 0.0008
        
        stint_performance = stint_consistency + endurance_ability - fatigue_factor
        
        # Track this stint
        self.driver_stints[driver.id].append({
            'phase': phase_num,
            'performance': stint_performance,
            'fatigue': fatigue_factor
        })
        
        return stint_performance
    
    def _calculate_reliability_degradation(self, driver: Driver, team: Team, 
                                         context: DisciplineContext, race_phase: RacePhase) -> float:
        """Calculate mechanical reliability degradation per phase"""
        # Base reliability by team tier
        base_reliability = 0.98 if team.tier == "tier1" else 0.95 if team.tier == "tier2" else 0.92
        
        # Driver's mechanical sympathy affects reliability
        mechanical_sympathy = (100.0 - driver.aggression) / 100.0 * 0.02
        
        # Night racing is harder on equipment
        night_stress = 0.01 if race_phase == RacePhase.NIGHT else 0.0
        
        # Weather stress
        weather_stress = context.weather_conditions.get("precipitation", 0.0) * 0.005
        
        phase_reliability = base_reliability + mechanical_sympathy - night_stress - weather_stress
        
        return max(0.85, phase_reliability)  # Minimum 85% reliability per phase
    
    def _calculate_strategy_impact(self, driver: Driver, team: Team, context: DisciplineContext, 
                                 race_phase: RacePhase) -> float:
        """Calculate impact of strategic decisions"""
        # Fuel strategy effectiveness
        fuel_strategy = (driver.racecraft + driver.consistency) / 2.0 * 0.0005
        
        # Tire management
        tire_management = driver.consistency * 0.0003
        
        # Pit stop timing
        pit_strategy = team.tier == "tier1" and 0.001 or 0.0  # Top teams better strategy
        
        return fuel_strategy + tire_management + pit_strategy
    
    def _apply_endurance_incidents(self, performance: float, driver: Driver, team: Team, 
                                 context: DisciplineContext, race_phase: RacePhase) -> Tuple[float, Optional[str]]:
        """Apply endurance racing specific incidents"""
        incident_roll = self.rng.random()
        
        # Endurance incident rates (lower than sprint racing)
        mechanical_failure_chance = 0.015  # Higher over long distance
        driver_error_chance = 0.008        # Fatigue-induced mistakes
        weather_incident_chance = 0.005    # Weather-related issues
        
        # Night racing increases incident risk
        if race_phase == RacePhase.NIGHT:
            driver_error_chance *= 1.5
            
        # Aggressive driving increases mechanical stress
        aggression_risk = driver.aggression * 0.0001
        
        total_risk = mechanical_failure_chance + driver_error_chance + weather_incident_chance + aggression_risk
        
        if incident_roll < mechanical_failure_chance:
            # Mechanical failure
            failure_types = ["engine", "transmission", "suspension", "electrical", "fuel_system"]
            return 0.0, random.choice(failure_types)
        
        elif incident_roll < mechanical_failure_chance + driver_error_chance:
            # Driver error - usually not race ending in endurance
            if self.rng.random() < 0.2:  # 20% chance of retirement
                return 0.0, "accident"
            else:  # Time loss but continue
                time_loss = self.rng.uniform(0.02, 0.08)
                return performance * (1.0 - time_loss), None
        
        elif incident_roll < total_risk:
            # Minor issue - continue with reduced performance
            performance_hit = self.rng.uniform(0.01, 0.05)
            return performance * (1.0 - performance_hit), None
        
        else:
            # Clean phase
            return performance, None
    
    def _simulate_qualifying_stint(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Simulate qualifying stint performance (multiple laps)"""
        # Consistency over multiple laps
        stint_consistency = driver.consistency * 0.015
        
        # Fuel load simulation
        fuel_adjustment = -0.005  # Heavier car for race simulation
        
        return stint_consistency + fuel_adjustment
    
    def _calculate_reliability_bonus(self, mechanical_health: float) -> int:
        """Calculate bonus points for finishing with good reliability"""
        if mechanical_health > 0.95:
            return 3  # Excellent reliability
        elif mechanical_health > 0.90:
            return 2  # Good reliability
        elif mechanical_health > 0.85:
            return 1  # Adequate reliability
        else:
            return 0  # Poor reliability
    
    def _assign_endurance_fastest_lap(self, results: List[RaceResult]) -> None:
        """Assign fastest lap in endurance race"""
        # Only finishers are eligible
        finishers = [r for r in results if r.dnf_reason is None]
        
        if not finishers:
            return
        
        # In endurance racing, fastest lap often goes to lighter cars late in race
        # Weight by position (better positions more likely) but add some randomness
        weights = []
        for result in finishers:
            # Top positions more likely, but not guaranteed
            weight = 1.0 / (result.position * 0.3 + 0.7)
            weights.append(weight)
        
        if weights:
            fastest_lap_driver = self.rng.choice(finishers, p=[w/sum(weights) for w in weights])
            fastest_lap_driver.fastest_lap = True
    
    def calculate_points(self, position: int, event_type: RaceEventType) -> int:
        """Calculate points using endurance championship system"""
        if event_type != RaceEventType.MAIN_RACE:
            return 0
        
        # Endurance racing points (high value for finishing)
        points_table = [50, 36, 30, 26, 22, 19, 16, 14, 12, 10, 8, 6, 4, 3, 2, 1]
        
        if position <= len(points_table):
            return points_table[position - 1]
        else:
            return 1  # Participation point for finishing


# Export the engine
__all__ = ['EnduranceEngine', 'EnduranceRaceLength', 'RacePhase']