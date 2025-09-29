"""
Urban/Street Racing Engine - Street racing and drift competition simulation

Implements urban racing with:
- Drift scoring and style points system
- Street racing on public roads simulation
- Police chase risk and illegal racing elements
- Crowd reaction and atmosphere impact
- Modified cars and tuning culture
- Underground racing scene mechanics

Features:
- Drift competitions with angle, speed, and line scoring
- Illegal street racing with risk vs reward
- Car modification and tuning impact
- Crowd and atmosphere influence on performance
- Police interference simulation
- Underground ranking and reputation system

Authors: Final Year Project - Computer Science
"""

import random
from typing import List, Dict, Optional, Tuple
from enum import Enum

from database.models import Driver, Team, RaceResult
from .base_engine import BaseDisciplineEngine, DisciplineContext, RacingDiscipline, RaceEventType


class UrbanEventType(Enum):
    """Urban racing event types"""
    DRIFT_COMPETITION = "drift"
    STREET_RACE = "street_race"
    TOUGE_BATTLE = "touge"
    DRAG_RACE = "drag"


class DriftJudgingCriteria(Enum):
    """Drift competition judging criteria"""
    ANGLE = "angle"
    SPEED = "speed"
    LINE = "line"
    STYLE = "style"


class UrbanStreetEngine(BaseDisciplineEngine):
    """
    Urban/Street Racing Engine
    
    Simulates underground racing culture including drift competitions,
    illegal street racing, and modified car culture. Emphasizes style,
    risk-taking, and crowd atmosphere over pure racing performance.
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        self.discipline = RacingDiscipline.URBAN_STREET
    
    def get_attribute_weights(self) -> Dict[str, float]:
        """Driver attribute weights for urban racing"""
        return {
            "skill": 0.25,        # Important but not everything
            "consistency": 0.15,   # Less important in street culture
            "racecraft": 0.20,     # Important for street racing
            "adaptability": 0.25,  # Crucial for varied conditions
            "aggression": 0.35     # Highest importance for risk-taking
        }
    
    def get_supported_event_types(self) -> List[RaceEventType]:
        """Urban racing supports practice and main events"""
        return [RaceEventType.QUALIFYING, RaceEventType.MAIN_RACE]
    
    def get_strategic_elements(self) -> List[str]:
        """Key strategic elements in urban racing"""
        return [
            "drift_technique", "car_tuning", "street_knowledge", "risk_assessment",
            "crowd_appeal", "style_points", "police_avoidance", "reputation_management"
        ]
    
    def get_scoring_system(self) -> Dict[str, str]:
        """Urban racing scoring system"""
        return {
            "type": "urban_points",
            "drift_scoring": True,
            "style_bonus": True,
            "crowd_favorite": True,
            "reputation_points": True
        }
    
    def simulate_event(self, context: DisciplineContext) -> List[RaceResult]:
        """Route to appropriate simulation based on event configuration"""
        # Determine urban event type from context
        urban_event_type = self._determine_urban_event_type(context)
        
        if context.event_type == RaceEventType.QUALIFYING:
            return self._simulate_practice_session(context, urban_event_type)
        elif context.event_type == RaceEventType.MAIN_RACE:
            if urban_event_type == UrbanEventType.DRIFT_COMPETITION:
                return self._simulate_drift_competition(context)
            elif urban_event_type == UrbanEventType.STREET_RACE:
                return self._simulate_street_race(context)
            else:
                return self._simulate_street_race(context)  # Default to street race
        else:
            raise ValueError(f"Unsupported event type for Urban Racing: {context.event_type}")
    
    def _determine_urban_event_type(self, context: DisciplineContext) -> UrbanEventType:
        """Determine what type of urban event this is"""
        discipline_config = getattr(context, 'discipline_config', {})
        event_type = discipline_config.get('urban_type', 'street_race')
        
        urban_type_map = {
            'drift': UrbanEventType.DRIFT_COMPETITION,
            'street': UrbanEventType.STREET_RACE,
            'touge': UrbanEventType.TOUGE_BATTLE,
            'drag': UrbanEventType.DRAG_RACE
        }
        
        return urban_type_map.get(event_type, UrbanEventType.STREET_RACE)
    
    def _simulate_practice_session(self, context: DisciplineContext, 
                                 urban_type: UrbanEventType) -> List[RaceResult]:
        """
        Simulate practice session for urban events
        
        Practice allows drivers to learn the course and test setups
        without police interference or crowd pressure.
        """
        practice_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base performance
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Practice-specific factors
            course_learning = driver.adaptability * 0.02
            setup_optimization = self._calculate_tuning_ability(driver, team) * 0.15
            
            # Less pressure in practice
            pressure_factor = 1.0  # No crowd pressure
            
            total_performance = base_performance + course_learning + setup_optimization
            practice_performance[driver.id] = total_performance * pressure_factor
        
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
    
    def _simulate_drift_competition(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate drift competition with style scoring
        
        Features:
        - Multiple judging criteria (angle, speed, line, style)
        - Crowd reaction influence
        - Style points and showmanship
        - Judge scoring system
        """
        drift_scores = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Calculate drift performance across multiple criteria
            total_score = 0.0
            
            # Angle scoring (0-100)
            angle_score = self._calculate_drift_angle_score(driver, team, context)
            
            # Speed scoring (0-100)  
            speed_score = self._calculate_drift_speed_score(driver, team, context)
            
            # Line scoring (0-100)
            line_score = self._calculate_drift_line_score(driver, team, context)
            
            # Style scoring (0-100)
            style_score = self._calculate_drift_style_score(driver, team, context)
            
            # Crowd favorite bonus
            crowd_bonus = self._calculate_crowd_appeal(driver, context)
            
            # Judge bias (simulates human judging inconsistency)
            judge_variance = self.rng.normal(0, 3.0)
            
            total_score = (angle_score + speed_score + line_score + style_score) / 4.0
            total_score += crowd_bonus + judge_variance
            
            # Ensure score stays within bounds
            total_score = max(0.0, min(100.0, total_score))
            
            drift_scores[driver.id] = total_score
        
        # Sort by drift score (highest first)
        sorted_scores = sorted(drift_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        
        for position, (driver_id, score) in enumerate(sorted_scores, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            points = self.calculate_points(position, RaceEventType.MAIN_RACE)
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=points,
                fastest_lap=False,  # Not applicable for drift
                dnf_reason=None,
                grid_position=position
            )
            results.append(result)
        
        return results
    
    def _simulate_street_race(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate illegal street race with risk factors
        
        Features:
        - Police chase risk
        - Traffic interference
        - High stakes atmosphere
        - Reputation and respect
        """
        street_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base racing performance
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Street racing factors
            street_knowledge = self._calculate_street_knowledge(driver, context)
            risk_taking = driver.aggression * 0.2
            car_tuning = self._calculate_tuning_ability(driver, team) * 0.15
            
            # Crowd and atmosphere pressure
            pressure_handling = self._calculate_pressure_handling(driver, context)
            
            # Traffic navigation ability
            traffic_skill = (driver.racecraft + driver.adaptability) / 2.0 * 0.1
            
            total_performance = (
                base_performance * 0.4 +
                street_knowledge * 0.2 +
                risk_taking * 0.15 +
                car_tuning * 0.15 +
                pressure_handling * 0.05 +
                traffic_skill * 0.05
            )
            
            # Apply street racing incidents
            final_performance, dnf_reason = self._apply_street_racing_incidents(
                total_performance, driver, context
            )
            
            street_performance[driver.id] = (final_performance, dnf_reason)
        
        # Sort by performance
        sorted_performance = sorted(street_performance.items(), key=lambda x: x[1][0], reverse=True)
        results = []
        
        for position, (driver_id, (performance, dnf_reason)) in enumerate(sorted_performance, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            points = self.calculate_points(position, RaceEventType.MAIN_RACE)
            
            # Reputation bonus for top finishers
            if position <= 3:
                reputation_bonus = [5, 3, 1][position - 1]
                points += reputation_bonus
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=points if dnf_reason is None else 0,
                fastest_lap=False,
                dnf_reason=dnf_reason,
                grid_position=position
            )
            results.append(result)
        
        return results
    
    def _calculate_tuning_ability(self, driver: Driver, team: Team) -> float:
        """Calculate car tuning and modification effectiveness"""
        # Driver skill in car setup
        tuning_skill = (driver.skill + driver.adaptability) / 2.0
        
        # Team's tuning capability (underground teams vary widely)
        team_tuning = 0.7 if team.tier == "tier1" else 0.5 if team.tier == "tier2" else 0.3
        
        return tuning_skill * team_tuning * 0.01
    
    def _calculate_drift_angle_score(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate drift angle scoring (0-100)"""
        # Base on aggression and skill
        angle_ability = (driver.aggression * 0.7 + driver.skill * 0.3)
        
        # Car setup for angle
        car_setup = self._calculate_tuning_ability(driver, team) * 50
        
        # Add variance for execution
        execution_variance = self.rng.normal(0, 5.0)
        
        base_score = (angle_ability / 100.0) * 70 + car_setup + execution_variance
        return max(0.0, min(100.0, base_score))
    
    def _calculate_drift_speed_score(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate drift speed scoring (0-100)"""
        # Base on skill and aggression
        speed_ability = (driver.skill * 0.6 + driver.aggression * 0.4)
        
        # Car power and setup
        car_power = self._calculate_tuning_ability(driver, team) * 60
        
        execution_variance = self.rng.normal(0, 4.0)
        
        base_score = (speed_ability / 100.0) * 65 + car_power + execution_variance
        return max(0.0, min(100.0, base_score))
    
    def _calculate_drift_line_score(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate drift line scoring (0-100)"""
        # Base on consistency and skill
        line_ability = (driver.consistency * 0.6 + driver.skill * 0.4)
        
        # Adaptability for course knowledge
        course_adaptation = driver.adaptability * 0.2
        
        execution_variance = self.rng.normal(0, 3.0)
        
        base_score = (line_ability / 100.0) * 75 + course_adaptation + execution_variance
        return max(0.0, min(100.0, base_score))
    
    def _calculate_drift_style_score(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate drift style scoring (0-100)"""
        # Style is subjective - based on aggression and uniqueness
        style_factor = (driver.aggression * 0.8 + driver.racecraft * 0.2)
        
        # Car visual modifications (simplified)
        visual_appeal = self.rng.uniform(0.8, 1.2)
        
        # Creativity and flair
        creativity_bonus = self.rng.uniform(-5.0, 10.0)
        
        base_score = (style_factor / 100.0) * 60 + visual_appeal * 20 + creativity_bonus
        return max(0.0, min(100.0, base_score))
    
    def _calculate_crowd_appeal(self, driver: Driver, context: DisciplineContext) -> float:
        """Calculate crowd favorite bonus"""
        # Aggressive drivers tend to be crowd favorites
        crowd_appeal = driver.aggression * 0.05
        
        # Random crowd reaction
        crowd_reaction = self.rng.uniform(-2.0, 5.0)
        
        return crowd_appeal + crowd_reaction
    
    def _calculate_street_knowledge(self, driver: Driver, context: DisciplineContext) -> float:
        """Calculate local street knowledge"""
        # Combination of adaptability and experience
        local_knowledge = driver.adaptability * 0.015
        
        # Simulate home advantage
        home_advantage = self.rng.choice([0.0, 0.01, 0.02])  # Some drivers know the area
        
        return local_knowledge + home_advantage
    
    def _calculate_pressure_handling(self, driver: Driver, context: DisciplineContext) -> float:
        """Calculate ability to handle crowd pressure and high stakes"""
        # Consistency helps with pressure
        pressure_resistance = driver.consistency * 0.008
        
        # Crowd pressure factor
        crowd_pressure = self.rng.uniform(-0.01, 0.005)
        
        return pressure_resistance + crowd_pressure
    
    def _apply_street_racing_incidents(self, performance: float, driver: Driver, 
                                     context: DisciplineContext) -> Tuple[float, Optional[str]]:
        """Apply street racing specific incidents"""
        incident_roll = self.rng.random()
        
        # Street racing has unique risks
        police_chase_chance = 0.05  # 5% chance of police interference
        traffic_incident_chance = 0.03  # 3% chance of traffic collision
        mechanical_failure_chance = 0.02  # Modified cars less reliable
        
        # Aggressive drivers have higher incident risk
        aggression_risk = driver.aggression * 0.01
        
        total_risk = police_chase_chance + traffic_incident_chance + mechanical_failure_chance + aggression_risk
        
        if incident_roll < police_chase_chance:
            # Police chase - race called off
            return 0.0, "police_chase"
        elif incident_roll < police_chase_chance + traffic_incident_chance:
            # Traffic incident
            if self.rng.random() < 0.6:  # 60% chance it's not race ending
                return performance * self.rng.uniform(0.6, 0.9), None
            else:
                return 0.0, "accident"
        elif incident_roll < total_risk:
            # Mechanical failure (modified cars break more)
            return 0.0, "mechanical"
        else:
            # Clean race with potential aggression bonus
            aggression_bonus = driver.aggression * 0.005
            return performance + aggression_bonus, None
    
    def calculate_points(self, position: int, event_type: RaceEventType) -> int:
        """Calculate points using urban racing system"""
        if event_type != RaceEventType.MAIN_RACE:
            return 0
        
        # Urban racing points (more top-heavy, winner takes most)
        points_table = [25, 15, 10, 8, 6, 5, 4, 3, 2, 1]
        
        if position <= len(points_table):
            return points_table[position - 1]
        else:
            return 0


# Export the engine
__all__ = ['UrbanStreetEngine', 'UrbanEventType', 'DriftJudgingCriteria']