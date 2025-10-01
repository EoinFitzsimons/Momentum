"""
Rally/Stage Racing Engine - Time-based stage racing simulation

Implements rally-style competition with:
- Time-based stage racing (no direct competition)
- Weather and surface condition impact
- Pace notes and road book navigation
- Service parks and mechanical management
- Co-driver impact on performance
- Route finding and risk management

Features:
- Individual time trial format per stage
- Multiple surface types (tarmac, gravel, snow, ice)
- Dynamic weather conditions affecting grip
- Mechanical reliability over long events
- Strategic risk vs reward decisions
- Service park limitations between stages

Authors: Final Year Project - Computer Science
"""

import random
from typing import List, Dict, Optional, Tuple
from enum import Enum

from database.models import Driver, Team, RaceResult
from ..base_engine import BaseDisciplineEngine, DisciplineContext, RacingDiscipline, RaceEventType


class SurfaceType(Enum):
    """Rally stage surface types"""
    TARMAC = "tarmac"
    GRAVEL = "gravel" 
    SNOW = "snow"
    ICE = "ice"
    MIXED = "mixed"


class RallyStageEngine(BaseDisciplineEngine):
    """
    Rally/Stage Racing Engine
    
    Simulates time-based rally competition where drivers compete
    against the clock on closed public roads with varying surfaces
    and weather conditions. Focus on navigation, risk management,
    and mechanical preservation over multi-day events.
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        self.discipline = RacingDiscipline.RALLY_STAGE
    
    def get_attribute_weights(self) -> Dict[str, float]:
        """Driver attribute weights for rally racing"""
        return {
            "skill": 0.35,        # Highest importance - precision driving
            "consistency": 0.25,   # Critical for multi-stage events
            "racecraft": 0.10,     # Less important (no direct competition)
            "adaptability": 0.35,  # Crucial for changing conditions
            "aggression": 0.20     # Risk vs reward balance
        }
    
    def get_supported_event_types(self) -> List[RaceEventType]:
        """Rally supports shakedown and stage racing"""
        return [RaceEventType.QUALIFYING, RaceEventType.MAIN_RACE]  # Qualifying = Shakedown
    
    def get_strategic_elements(self) -> List[str]:
        """Key strategic elements in rally racing"""
        return [
            "pace_notes", "surface_adaptation", "weather_reading", "risk_management",
            "mechanical_preservation", "navigation", "co_driver_communication", "tire_choice"
        ]
    
    def get_scoring_system(self) -> Dict[str, str]:
        """Rally scoring system based on stage times"""
        return {
            "type": "rally_time",
            "time_based": True,
            "power_stage_bonus": True,  # Bonus points for final stage
            "stage_wins": True,         # Points for individual stage wins
            "overall_points": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        }
    
    def simulate_event(self, context: DisciplineContext) -> List[RaceResult]:
        """Route to appropriate simulation based on event type"""
        if context.event_type == RaceEventType.QUALIFYING:
            return self._simulate_shakedown(context)
        elif context.event_type == RaceEventType.MAIN_RACE:
            return self._simulate_rally_stages(context)
        else:
            raise ValueError(f"Unsupported event type for Rally: {context.event_type}")
    
    def _simulate_shakedown(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate rally shakedown stage
        
        Shakedown is a practice stage where crews can test their cars
        and pace notes before the rally begins. Sets running order.
        """
        shakedown_times = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base performance calculation
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Shakedown specific factors (less aggressive approach)
            setup_testing = driver.adaptability * 0.02
            pace_note_verification = driver.skill * 0.015
            conservative_approach = 0.95  # Most crews drive conservatively in shakedown
            
            # Add some variance for testing different approaches
            testing_variance = self.rng.normal(0, 0.02)
            
            # Convert performance to time (inverse relationship)
            base_time = 100.0  # Baseline stage time in seconds
            performance_factor = base_performance + setup_testing + pace_note_verification + testing_variance
            stage_time = base_time / (performance_factor * conservative_approach)
            
            shakedown_times[driver.id] = stage_time
        
        # Sort by time (fastest first)
        sorted_times = sorted(shakedown_times.items(), key=lambda x: x[1])
        results = []
        
        for position, (driver_id, stage_time) in enumerate(sorted_times, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=0,  # No points for shakedown
                fastest_lap=False,
                dnf_reason=None,
                grid_position=position  # Running order for rally stages
            )
            results.append(result)
        
        return results
    
    def _simulate_rally_stages(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate multi-stage rally event
        
        Features:
        - Multiple stages with different surfaces and conditions
        - Cumulative time-based competition
        - Mechanical reliability over distance
        - Strategic risk management
        - Service park limitations
        """
        # Generate rally stages for this event
        stages = self._generate_rally_stages(context)
        
        # Initialize driver cumulative times and status
        cumulative_times = {}
        driver_status = {}  # Track mechanical issues, penalties, etc.
        
        for driver in context.drivers:
            cumulative_times[driver.id] = 0.0
            driver_status[driver.id] = {
                'active': True,
                'mechanical_health': 1.0,
                'penalty_time': 0.0,
                'stage_wins': 0
            }
        
        # Simulate each stage
        for stage_num, stage_info in enumerate(stages, 1):
            stage_results = self._simulate_single_stage(
                context, stage_info, stage_num, driver_status
            )
            
            # Update cumulative times and status
            for driver_id, stage_result in stage_results.items():
                if driver_status[driver_id]['active']:
                    cumulative_times[driver_id] += stage_result['time']
                    cumulative_times[driver_id] += stage_result.get('penalty_time', 0.0)
                    driver_status[driver_id]['mechanical_health'] *= stage_result.get('mechanical_factor', 1.0)
                    
                    # Check for stage win
                    if stage_result.get('stage_win', False):
                        driver_status[driver_id]['stage_wins'] += 1
                    
                    # Check for retirement
                    if stage_result.get('dnf_reason'):
                        driver_status[driver_id]['active'] = False
                        driver_status[driver_id]['dnf_reason'] = stage_result['dnf_reason']
            
            # Service park between stages (simplified)
            if stage_num % 3 == 0:  # Service every 3 stages
                self._apply_service_park_effects(driver_status, context)
        
        # Calculate final results
        results = self._calculate_rally_results(cumulative_times, driver_status, context)
        
        return results
    
    def _generate_rally_stages(self, context: DisciplineContext) -> List[Dict]:
        """Generate stages for the rally with varying characteristics"""
        # Rally typically has 15-25 stages, we'll simulate 8-12 for performance
        num_stages = self.rng.randint(8, 12)
        stages = []
        
        for stage_num in range(1, num_stages + 1):
            # Vary surface types throughout the rally
            if stage_num <= 3:
                surface = SurfaceType.TARMAC  # Start on tarmac
            elif stage_num <= 6:
                surface = SurfaceType.GRAVEL  # Move to gravel
            else:
                surface = self.rng.choice([SurfaceType.GRAVEL, SurfaceType.SNOW])
            
            # Stage characteristics
            stage_info = {
                'number': stage_num,
                'surface': surface,
                'length': self.rng.uniform(8.0, 25.0),  # km
                'difficulty': self.rng.uniform(0.7, 1.3),
                'weather_factor': context.weather_conditions.get("precipitation", 0.0),
                'is_power_stage': stage_num == num_stages,  # Last stage is power stage
                'spectator_stage': stage_num in [1, num_stages // 2, num_stages]
            }
            
            stages.append(stage_info)
        
        return stages
    
    def _simulate_single_stage(self, context: DisciplineContext, stage_info: Dict, 
                             stage_num: int, driver_status: Dict) -> Dict:
        """Simulate a single rally stage for all active drivers"""
        stage_results = {}
        stage_times = []
        
        for driver in context.drivers:
            if not driver_status[driver.id]['active']:
                continue
                
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Calculate stage time
            stage_time, stage_result_data = self._calculate_stage_time(
                driver, team, stage_info, driver_status[driver.id], context
            )
            
            stage_results[driver.id] = stage_result_data
            if stage_result_data.get('dnf_reason') is None:
                stage_times.append((driver.id, stage_time))
        
        # Determine stage winner
        if stage_times:
            stage_times.sort(key=lambda x: x[1])
            winner_id = stage_times[0][0]
            stage_results[winner_id]['stage_win'] = True
            
            # Power stage bonus points
            if stage_info['is_power_stage']:
                # Award bonus points for top 5 on power stage
                for i, (driver_id, _) in enumerate(stage_times[:5]):
                    bonus_points = [5, 4, 3, 2, 1][i]
                    stage_results[driver_id]['power_stage_points'] = bonus_points
        
        return stage_results
    
    def _calculate_stage_time(self, driver: Driver, team: Team, stage_info: Dict,
                            driver_status: Dict, context: DisciplineContext) -> Tuple[float, Dict]:
        """Calculate individual driver's time for a stage"""
        # Base performance
        base_performance = self.calculate_base_performance(driver, team, context)
        
        # Surface adaptation
        surface_skill = self._calculate_surface_adaptation(driver, stage_info['surface'])
        
        # Weather impact
        weather_skill = self._calculate_weather_adaptation(driver, stage_info, context)
        
        # Navigation and pace notes
        navigation_skill = (driver.skill + driver.adaptability) / 2.0 * 0.15
        
        # Risk vs reward (aggression vs consistency)
        risk_factor = self._calculate_risk_factor(driver, stage_info)
        
        # Mechanical health impact
        mechanical_factor = driver_status['mechanical_health']
        
        # Stage difficulty impact
        difficulty_impact = stage_info['difficulty'] * 0.1
        
        # Calculate total performance
        total_performance = (
            base_performance * 0.4 +
            surface_skill * 0.2 +
            weather_skill * 0.15 +
            navigation_skill * 0.15 +
            risk_factor * 0.1
        ) * mechanical_factor
        
        # Convert to time (base time adjusted by performance)
        base_stage_time = stage_info['length'] * 3.0  # ~3 minutes per km baseline
        stage_time = base_stage_time / total_performance + difficulty_impact
        
        # Apply incidents and mechanical issues
        final_time, result_data = self._apply_rally_incidents(
            stage_time, driver, stage_info, driver_status
        )
        
        return final_time, result_data
    
    def _calculate_surface_adaptation(self, driver: Driver, surface: SurfaceType) -> float:
        """Calculate driver's adaptation to surface type"""
        adaptability = driver.adaptability * 0.01
        skill_factor = driver.skill * 0.008
        
        # Surface-specific modifiers
        surface_modifiers = {
            SurfaceType.TARMAC: 0.0,      # Baseline
            SurfaceType.GRAVEL: -0.02,    # More challenging
            SurfaceType.SNOW: -0.04,      # Requires skill
            SurfaceType.ICE: -0.06,       # Most challenging
            SurfaceType.MIXED: -0.03      # Requires adaptability
        }
        
        base_adaptation = adaptability + skill_factor
        surface_penalty = surface_modifiers.get(surface, 0.0)
        
        return base_adaptation + surface_penalty
    
    def _calculate_weather_adaptation(self, driver: Driver, stage_info: Dict, 
                                    context: DisciplineContext) -> float:
        """Calculate weather adaptation ability"""
        weather_conditions = context.weather_conditions
        precipitation = weather_conditions.get("precipitation", 0.0)
        
        # Weather skill based on adaptability and consistency
        weather_skill = (driver.adaptability * 0.6 + driver.consistency * 0.4) * 0.01
        
        # Weather penalty
        weather_penalty = precipitation * 0.03
        
        # Spectator stages are often more pressured
        pressure_factor = 0.02 if stage_info.get('spectator_stage', False) else 0.0
        
        return weather_skill - weather_penalty - pressure_factor
    
    def _calculate_risk_factor(self, driver: Driver, stage_info: Dict) -> float:
        """Calculate risk vs reward factor"""
        # Aggressive drivers push harder but risk more
        aggression_bonus = driver.aggression * 0.008
        consistency_safety = driver.consistency * 0.005
        
        # Risk increases with stage difficulty
        risk_multiplier = 1.0 + (stage_info['difficulty'] - 1.0) * 0.5
        
        net_risk_reward = (aggression_bonus - consistency_safety) * risk_multiplier
        
        return net_risk_reward
    
    def _apply_rally_incidents(self, stage_time: float, driver: Driver, 
                             stage_info: Dict, driver_status: Dict) -> Tuple[float, Dict]:
        """Apply rally-specific incidents and mechanical issues"""
        result_data = {
            'time': stage_time,
            'penalty_time': 0.0,
            'mechanical_factor': 1.0,
            'dnf_reason': None
        }
        
        incident_roll = self.rng.random()
        
        # Rally incident rates (higher than circuit racing)
        mechanical_failure_chance = 0.02 * stage_info['difficulty']
        navigation_error_chance = 0.01
        off_road_chance = driver.aggression * 0.015
        
        if incident_roll < mechanical_failure_chance:
            # Mechanical issue
            if self.rng.random() < 0.3:  # 30% chance of retirement
                result_data['dnf_reason'] = random.choice([
                    "mechanical", "engine", "transmission", "suspension"
                ])
                result_data['time'] = float('inf')
            else:  # Time penalty for repairs
                result_data['penalty_time'] = self.rng.uniform(30.0, 180.0)
                result_data['mechanical_factor'] = 0.95
        
        elif incident_roll < navigation_error_chance:
            # Navigation error (wrong turn, missed junction)
            result_data['penalty_time'] = self.rng.uniform(10.0, 60.0)
        
        elif incident_roll < off_road_chance:
            # Off-road excursion
            if self.rng.random() < 0.1:  # 10% chance of retirement
                result_data['dnf_reason'] = "accident"
                result_data['time'] = float('inf')
            else:
                # Time loss recovering
                result_data['time'] += self.rng.uniform(5.0, 30.0)
        
        return result_data['time'], result_data
    
    def _apply_service_park_effects(self, driver_status: Dict, context: DisciplineContext) -> None:
        """Apply service park effects between stage groups"""
        for driver_id, status in driver_status.items():
            if status['active'] and status['mechanical_health'] < 1.0:
                # Service can restore some mechanical health
                service_quality = self.rng.uniform(0.1, 0.3)
                status['mechanical_health'] = min(1.0, 
                    status['mechanical_health'] + service_quality
                )
    
    def _calculate_rally_results(self, cumulative_times: Dict, driver_status: Dict, 
                               context: DisciplineContext) -> List[RaceResult]:
        """Calculate final rally results from cumulative times"""
        # Sort active drivers by cumulative time
        active_drivers = [
            (driver_id, time) for driver_id, time in cumulative_times.items()
            if driver_status[driver_id]['active']
        ]
        active_drivers.sort(key=lambda x: x[1])
        
        # Add retired drivers at the end
        retired_drivers = [
            (driver_id, cumulative_times[driver_id]) 
            for driver_id in driver_status.keys()
            if not driver_status[driver_id]['active']
        ]
        
        results = []
        position = 1
        
        # Process finishing drivers
        for driver_id, final_time in active_drivers:
            driver = next(d for d in context.drivers if d.id == driver_id)
            points = self.calculate_points(position, RaceEventType.MAIN_RACE)
            
            # Add power stage bonus points
            power_stage_points = 0
            # This would be calculated from stage results in real implementation
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=points + power_stage_points,
                fastest_lap=False,  # Rally uses stage wins instead
                dnf_reason=None,
                grid_position=position  # Not applicable for rally
            )
            results.append(result)
            position += 1
        
        # Process retired drivers
        for driver_id, _ in retired_drivers:
            driver = next(d for d in context.drivers if d.id == driver_id)
            dnf_reason = driver_status[driver_id].get('dnf_reason', 'retired')
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=0,
                fastest_lap=False,
                dnf_reason=dnf_reason,
                grid_position=position
            )
            results.append(result)
            position += 1
        
        return results
    
    def calculate_points(self, position: int, event_type: RaceEventType) -> int:
        """Calculate points using rally system"""
        if event_type != RaceEventType.MAIN_RACE:
            return 0
        
        # Rally points system
        points_table = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        
        if position <= len(points_table):
            return points_table[position - 1]
        else:
            return 0


# Export the engine
__all__ = ['RallyStageEngine', 'SurfaceType']