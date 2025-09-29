"""
Sprint/Rallycross Racing Engine - Short mixed-surface racing simulation

Implements rallycross/sprint racing with:
- Heat race qualification system
- Mixed surface racing (tarmac + gravel sections)
- Joker lap mandatory alternate route
- Semi-final and final progression system
- Aggressive wheel-to-wheel contact racing
- Quick format with multiple short races

Features:
- Heat race seeding for semi-finals and final
- Mandatory joker lap strategic timing
- Mixed surface grip transitions
- High contact racing with incident simulation
- Quick-fire elimination format
- Multi-class field management

Authors: Final Year Project - Computer Science
"""

import random
from typing import List, Dict, Optional, Tuple
from enum import Enum

from database.models import Driver, Team, RaceResult
from .base_engine import BaseDisciplineEngine, DisciplineContext, RacingDiscipline, RaceEventType


class RallycrossEventStage(Enum):
    """Rallycross event progression stages"""
    QUALIFYING_HEATS = "heats"
    SEMI_FINALS = "semi_finals"  
    FINAL = "final"


class JokerLapStatus(Enum):
    """Joker lap completion status"""
    NOT_TAKEN = "not_taken"
    TAKEN = "taken"
    PENALTY = "penalty"


class SprintRallycrossEngine(BaseDisciplineEngine):
    """
    Sprint/Rallycross Racing Engine
    
    Simulates short-format mixed-surface racing with heat races,
    joker laps, and aggressive wheel-to-wheel competition on
    circuits combining tarmac and gravel sections.
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        self.discipline = RacingDiscipline.SPRINT_RALLYCROSS
        self.joker_lap_status = {}  # Track joker lap completion per driver
    
    def get_attribute_weights(self) -> Dict[str, float]:
        """Driver attribute weights for rallycross"""
        return {
            "skill": 0.25,        # Mixed surface driving skill
            "consistency": 0.20,   # Important for heat system
            "racecraft": 0.25,     # Crucial for close racing
            "adaptability": 0.30,  # Most important for surface changes
            "aggression": 0.25     # Contact racing and overtaking
        }
    
    def get_supported_event_types(self) -> List[RaceEventType]:
        """Rallycross supports practice and race events"""
        return [RaceEventType.QUALIFYING, RaceEventType.MAIN_RACE]
    
    def get_strategic_elements(self) -> List[str]:
        """Key strategic elements in rallycross"""
        return [
            "joker_lap_timing", "surface_transition", "contact_racing", "heat_strategy",
            "launch_technique", "traffic_management", "mixed_surface_skill", "incident_avoidance"
        ]
    
    def get_scoring_system(self) -> Dict[str, str]:
        """Rallycross scoring system"""
        return {
            "type": "rallycross_championship",
            "heat_points": True,
            "semi_final_bonus": True,
            "final_multiplier": True,
            "joker_lap_penalty": True
        }
    
    def simulate_event(self, context: DisciplineContext) -> List[RaceResult]:
        """Route to appropriate simulation based on event configuration"""
        rallycross_stage = self._determine_rallycross_stage(context)
        
        if context.event_type == RaceEventType.QUALIFYING:
            return self._simulate_practice_session(context)
        elif context.event_type == RaceEventType.MAIN_RACE:
            if rallycross_stage == RallycrossEventStage.QUALIFYING_HEATS:
                return self._simulate_qualifying_heats(context)
            elif rallycross_stage == RallycrossEventStage.SEMI_FINALS:
                return self._simulate_semi_finals(context)
            else:  # FINAL
                return self._simulate_final(context)
        else:
            raise ValueError(f"Unsupported event type for Rallycross: {context.event_type}")
    
    def _determine_rallycross_stage(self, context: DisciplineContext) -> RallycrossEventStage:
        """Determine which stage of rallycross event this is"""
        discipline_config = getattr(context, 'discipline_config', {})
        stage = discipline_config.get('rallycross_stage', 'heats')
        
        stage_map = {
            'heats': RallycrossEventStage.QUALIFYING_HEATS,
            'semi_finals': RallycrossEventStage.SEMI_FINALS,
            'final': RallycrossEventStage.FINAL
        }
        
        return stage_map.get(stage, RallycrossEventStage.QUALIFYING_HEATS)
    
    def _simulate_practice_session(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate rallycross practice session
        
        Practice allows drivers to learn the mixed surface layout
        and test joker lap timing without competition pressure.
        """
        practice_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base performance
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Practice-specific factors
            surface_learning = driver.adaptability * 0.02
            joker_lap_practice = driver.skill * 0.015
            setup_optimization = 0.01  # Car setup for mixed surfaces
            
            total_performance = base_performance + surface_learning + joker_lap_practice + setup_optimization
            practice_performance[driver.id] = total_performance
        
        # Sort by performance
        sorted_performance = sorted(practice_performance.items(), key=lambda x: x[1], reverse=True)
        results = []
        
        for position, (driver_id, performance) in enumerate(sorted_performance, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=0,  # No practice points
                fastest_lap=False,
                dnf_reason=None,
                grid_position=position
            )
            results.append(result)
        
        return results
    
    def _simulate_qualifying_heats(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate rallycross qualifying heats
        
        Multiple heat races determine starting positions for semi-finals.
        All drivers compete in heats with points awarded based on finishing position.
        """
        # Divide drivers into heats (typically 6 drivers per heat)
        heat_groups = self._create_heat_groups(context.drivers)
        all_heat_results = []
        
        for heat_number, heat_drivers in enumerate(heat_groups, 1):
            heat_context = self._create_heat_context(context, heat_drivers)
            heat_results = self._simulate_single_heat(heat_context, heat_number)
            all_heat_results.extend(heat_results)
        
        # Sort by heat points to determine overall qualifying order
        all_heat_results.sort(key=lambda x: (-x.points, x.position))
        
        # Update positions for overall classification
        for overall_position, result in enumerate(all_heat_results, 1):
            result.grid_position = overall_position
        
        return all_heat_results
    
    def _simulate_single_heat(self, context: DisciplineContext, heat_number: int) -> List[RaceResult]:
        """
        Simulate a single qualifying heat race
        
        Features short 4-6 lap race with mandatory joker lap
        and high contact racing probability
        """
        # Initialize joker lap tracking for this heat
        for driver in context.drivers:
            self.joker_lap_status[driver.id] = JokerLapStatus.NOT_TAKEN
        
        race_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base racing performance
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Rallycross specific factors
            mixed_surface_skill = self._calculate_mixed_surface_ability(driver, team)
            launch_performance = self._calculate_rallycross_launch(driver, team, context)
            contact_racing_skill = (driver.racecraft + driver.aggression) / 2.0 * 0.12
            
            # Joker lap strategy and execution
            joker_lap_impact = self._simulate_joker_lap_strategy(driver, context)
            
            # Traffic and incident management
            traffic_management = driver.racecraft * 0.08
            
            total_performance = (
                base_performance * 0.35 +
                mixed_surface_skill * 0.25 +
                launch_performance * 0.15 +
                contact_racing_skill * 0.15 +
                traffic_management * 0.10
            ) + joker_lap_impact
            
            # Apply rallycross incidents (high contact rate)
            final_performance, dnf_reason = self._apply_rallycross_incidents(total_performance, driver, context)
            
            race_performance[driver.id] = (final_performance, dnf_reason)
        
        # Apply joker lap penalties
        self._apply_joker_lap_penalties(race_performance)
        
        # Sort by performance
        sorted_performance = sorted(race_performance.items(), key=lambda x: x[1][0], reverse=True)
        results = []
        
        for position, (driver_id, (performance, dnf_reason)) in enumerate(sorted_performance, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            heat_points = self._calculate_heat_points(position, len(context.drivers))
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=heat_points if dnf_reason is None else 0,
                fastest_lap=False,
                dnf_reason=dnf_reason,
                grid_position=0  # Will be set later
            )
            results.append(result)
        
        return results
    
    def _simulate_semi_finals(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate rallycross semi-finals
        
        Top qualifiers advance to semi-finals with higher stakes
        and more aggressive racing for final positions.
        """
        return self._simulate_elimination_race(context, is_final=False)
    
    def _simulate_final(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate rallycross final
        
        Championship points multiplied for final with
        maximum pressure and aggressive racing.
        """
        return self._simulate_elimination_race(context, is_final=True)
    
    def _simulate_elimination_race(self, context: DisciplineContext, is_final: bool = False) -> List[RaceResult]:
        """
        Simulate semi-final or final race with higher stakes
        """
        # Reset joker lap tracking
        for driver in context.drivers:
            self.joker_lap_status[driver.id] = JokerLapStatus.NOT_TAKEN
        
        race_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Enhanced performance calculation for elimination races
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Higher pressure and stakes
            pressure_factor = 1.1 if is_final else 1.05
            pressure_handling = self._calculate_pressure_performance(driver, is_final)
            
            # Rallycross factors with higher intensity
            mixed_surface_skill = self._calculate_mixed_surface_ability(driver, team) * 1.2
            contact_racing = self._calculate_elimination_contact_skill(driver, is_final)
            
            # Strategic joker lap in elimination race
            joker_strategy = self._simulate_elimination_joker_strategy(driver, context, is_final)
            
            total_performance = (
                base_performance * pressure_factor +
                pressure_handling +
                mixed_surface_skill +
                contact_racing +
                joker_strategy
            )
            
            # Higher incident rates in elimination races
            final_performance, dnf_reason = self._apply_elimination_incidents(
                total_performance, driver, context, is_final
            )
            
            race_performance[driver.id] = (final_performance, dnf_reason)
        
        # Apply joker lap penalties
        self._apply_joker_lap_penalties(race_performance)
        
        # Sort results
        sorted_performance = sorted(race_performance.items(), key=lambda x: x[1][0], reverse=True)
        results = []
        
        point_multiplier = 2.0 if is_final else 1.5  # Final worth more points
        
        for position, (driver_id, (performance, dnf_reason)) in enumerate(sorted_performance, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            base_points = self.calculate_points(position, RaceEventType.MAIN_RACE)
            final_points = int(base_points * point_multiplier) if dnf_reason is None else 0
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=final_points,
                fastest_lap=False,
                dnf_reason=dnf_reason,
                grid_position=position
            )
            results.append(result)
        
        return results
    
    def _calculate_mixed_surface_ability(self, driver: Driver, team: Team) -> float:
        """Calculate ability to handle mixed tarmac/gravel surfaces"""
        # Adaptability is key for surface transitions
        surface_adaptability = driver.adaptability * 0.008
        
        # Car setup for mixed surfaces
        setup_versatility = (0.8 if team.tier == "tier1" else 
                           0.6 if team.tier == "tier2" else 0.4) * 0.02
        
        # Skill in managing grip transitions
        transition_skill = driver.skill * 0.005
        
        return surface_adaptability + setup_versatility + transition_skill
    
    def _calculate_rallycross_launch(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate rallycross start performance (often from gravel)"""
        # Launch technique on loose surface
        launch_skill = (driver.skill + driver.aggression) / 2.0 * 0.01
        
        # Car's ability to hook up on gravel
        traction_system = (0.9 if team.tier == "tier1" else 
                          0.7 if team.tier == "tier2" else 0.5) * 0.015
        
        return launch_skill + traction_system
    
    def _simulate_joker_lap_strategy(self, driver: Driver, context: DisciplineContext) -> float:
        """
        Simulate joker lap timing strategy
        
        Drivers must take joker lap once per race - timing is strategic
        """
        # Strategic thinking affects joker lap timing
        strategy_skill = (driver.racecraft + driver.consistency) / 2.0
        
        # Determine when to take joker lap (early, mid, or late race)
        joker_timing_preference = self.rng.choice(['early', 'mid', 'late'])
        
        # Calculate optimal timing bonus/penalty
        if joker_timing_preference == 'early':
            # Early joker - avoids traffic but may lose track position
            timing_impact = 0.005 if strategy_skill > 70 else -0.01
        elif joker_timing_preference == 'mid':
            # Mid-race joker - balanced approach
            timing_impact = 0.002
        else:  # late
            # Late joker - risky but can gain positions if timed well
            timing_impact = 0.01 if strategy_skill > 80 else -0.015
        
        self.joker_lap_status[driver.id] = JokerLapStatus.TAKEN
        return timing_impact
    
    def _simulate_elimination_joker_strategy(self, driver: Driver, context: DisciplineContext, 
                                           is_final: bool) -> float:
        """Enhanced joker lap strategy for elimination races"""
        base_strategy = self._simulate_joker_lap_strategy(driver, context)
        
        # Higher stakes mean more careful timing
        if is_final:
            strategic_bonus = driver.racecraft * 0.001
            return base_strategy + strategic_bonus
        
        return base_strategy
    
    def _apply_joker_lap_penalties(self, race_performance: Dict) -> None:
        """Apply penalties for drivers who didn't take mandatory joker lap"""
        for driver_id, (performance, dnf_reason) in race_performance.items():
            if self.joker_lap_status.get(driver_id) == JokerLapStatus.NOT_TAKEN:
                # Heavy penalty for not taking joker lap
                race_performance[driver_id] = (performance * 0.5, dnf_reason)
                self.joker_lap_status[driver_id] = JokerLapStatus.PENALTY
    
    def _apply_rallycross_incidents(self, performance: float, driver: Driver, 
                                  context: DisciplineContext) -> Tuple[float, Optional[str]]:
        """Apply rallycross specific incidents (very high contact rates)"""
        incident_roll = self.rng.random()
        
        # Very high incident rates due to close racing and mixed surfaces
        contact_incident_chance = 0.12  # 12% chance of contact
        surface_incident_chance = 0.05  # 5% chance of surface-related issue
        mechanical_chance = 0.02       # 2% chance of mechanical failure
        
        # Aggressive drivers have higher risk but also more overtaking success
        aggression_factor = driver.aggression * 0.015
        
        total_incident_chance = contact_incident_chance + surface_incident_chance + mechanical_chance
        
        if incident_roll < mechanical_chance:
            return 0.0, "mechanical"
        elif incident_roll < contact_incident_chance:
            # Contact incident - often not race ending in rallycross
            if self.rng.random() < 0.8:  # 80% continue with damage
                damage_impact = self.rng.uniform(0.1, 0.4)
                return performance * (1.0 - damage_impact), None
            else:
                return 0.0, random.choice(["contact", "accident", "puncture"])
        elif incident_roll < surface_incident_chance:
            # Surface-related incident (off-track, spin, etc.)
            return performance * self.rng.uniform(0.7, 0.9), None
        else:
            # Clean race with potential aggression bonus
            return performance + aggression_factor * 0.5, None
    
    def _apply_elimination_incidents(self, performance: float, driver: Driver, 
                                   context: DisciplineContext, is_final: bool) -> Tuple[float, Optional[str]]:
        """Higher incident rates in elimination races due to desperation"""
        base_performance, dnf_reason = self._apply_rallycross_incidents(performance, driver, context)
        
        if is_final and dnf_reason is None:
            # Extra pressure in final can cause mistakes
            pressure_incident = self.rng.random() < 0.03  # 3% additional risk
            if pressure_incident:
                if self.rng.random() < 0.5:
                    return base_performance * 0.8, None  # Mistake but continue
                else:
                    return 0.0, "pressure_mistake"
        
        return base_performance, dnf_reason
    
    def _calculate_pressure_performance(self, driver: Driver, is_final: bool) -> float:
        """Calculate performance under elimination pressure"""
        base_pressure_handling = driver.consistency * 0.005
        
        if is_final:
            # Final has maximum pressure
            final_pressure_bonus = driver.racecraft * 0.003
            return base_pressure_handling + final_pressure_bonus
        
        return base_pressure_handling
    
    def _calculate_elimination_contact_skill(self, driver: Driver, is_final: bool) -> float:
        """Enhanced contact racing skill for elimination races"""
        base_contact_skill = (driver.racecraft + driver.aggression) / 2.0 * 0.01
        
        if is_final:
            # Final requires maximum racecraft
            return base_contact_skill * 1.3
        
        return base_contact_skill * 1.1
    
    def _create_heat_groups(self, drivers: List) -> List[List]:
        """Divide drivers into heat groups (typically 6 drivers per heat)"""
        drivers_per_heat = 6
        heat_groups = []
        
        for i in range(0, len(drivers), drivers_per_heat):
            heat_group = drivers[i:i + drivers_per_heat]
            heat_groups.append(heat_group)
        
        return heat_groups
    
    def _create_heat_context(self, context: DisciplineContext, heat_drivers: List) -> DisciplineContext:
        """Create context for individual heat race"""
        # Create new context with only heat drivers (simplified)
        return context  # In real implementation, would filter drivers
    
    def _calculate_heat_points(self, position: int, field_size: int) -> int:
        """Calculate points for heat race finishing position"""
        # Heat points based on position (higher for better positions)
        heat_points_table = [6, 5, 4, 3, 2, 1]  # Top 6 get points
        
        if position <= len(heat_points_table):
            return heat_points_table[position - 1]
        else:
            return 0
    
    def calculate_points(self, position: int, event_type: RaceEventType) -> int:
        """Calculate points using rallycross championship system"""
        if event_type != RaceEventType.MAIN_RACE:
            return 0
        
        # Rallycross main race points
        points_table = [25, 20, 16, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        
        if position <= len(points_table):
            return points_table[position - 1]
        else:
            return 0


# Export the engine
__all__ = ['SprintRallycrossEngine', 'RallycrossEventStage', 'JokerLapStatus']