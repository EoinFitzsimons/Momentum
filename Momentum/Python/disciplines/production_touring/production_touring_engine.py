"""
Production/Touring Car Racing Engine - Door-to-door racing simulation

Implements close-quarters racing with:
- Success ballast system for championship balance
- Reverse grid races for excitement
- Multi-class racing support
- Contact racing and incident simulation
- Weight penalties and performance balancing

Features:
- Aggressive wheel-to-wheel racing dynamics
- Success ballast affecting car performance
- Reverse grid race formats
- Higher incident rates than open-wheel racing
- Multi-class field management
- Modified points systems for entertainment

Authors: Final Year Project - Computer Science
"""

import random
from typing import List, Dict, Optional, Tuple

from database.models import Driver, Team, RaceResult
from ..base_engine import BaseDisciplineEngine, DisciplineContext, RacingDiscipline, RaceEventType


class ProductionTouringEngine(BaseDisciplineEngine):
    """
    Production and Touring Car Racing Engine
    
    Simulates close-contact racing with emphasis on racecraft, 
    door-to-door battles, and entertainment-focused race formats
    like reverse grids and success ballast systems.
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        self.discipline = RacingDiscipline.PRODUCTION_TOURING
    
    def get_attribute_weights(self) -> Dict[str, float]:
        """Driver attribute weights for production/touring car racing"""
        return {
            # Core driving skills emphasizing contact racing
            "racecraft": 0.18,              # Most important for door-to-door racing
            "overtaking": 0.15,             # Critical for passing in traffic
            "defensive_driving": 0.12,      # Protecting position in close racing
            "raw_speed": 0.10,              # Less important than racecraft
            "consistency": 0.10,            # Some importance for championships
            
            # Physical traits for aggressive racing
            "concentration": 0.08,          # Focus during close battles
            "reaction_time": 0.08,          # Quick responses in traffic
            "multitasking": 0.06,           # Managing multiple battles
            "pressure_handling": 0.06,      # High-pressure racing
            
            # Technical knowledge for setup
            "setup_knowledge": 0.08,        # Car balance for close racing
            "tire_management": 0.06,        # Tire preservation in contact
            "mechanical_sympathy": 0.08,    # Preserving car in contact racing
            
            # Discipline preference
            "touring_car_aptitude": 0.15,   # Natural preference for touring cars
            
            # Race craft specific to touring cars
            "traffic_management": 0.12,     # Navigation through fields
            "pit_stop_coordination": 0.06,  # Working with crew efficiently
            "safety_car_awareness": 0.08,   # Maximizing opportunities
            
            # Environmental adaptation
            "car_adaptation": 0.08,         # Different car balance each race
            "surface_adaptation": 0.06,     # Various track surfaces
            
            # Personal traits emphasizing aggression
            "risk_appetite": 0.10,          # Willingness to make bold moves
            "team_cooperation": 0.06,       # Working within team strategy
            "ego_management": 0.04          # Handling contact and criticism
        }
    
    def get_supported_event_types(self) -> List[RaceEventType]:
        """Touring cars support qualifying and main races"""
        return [RaceEventType.QUALIFYING, RaceEventType.MAIN_RACE]
    
    def get_strategic_elements(self) -> List[str]:
        """Key strategic elements in touring car racing"""
        return [
            "racecraft", "contact_racing", "success_ballast", "reverse_grid",
            "traffic_management", "overtaking_skill", "defensive_driving"
        ]
    
    def get_scoring_system(self) -> Dict[str, str]:
        """Touring car scoring system (often more spread out)"""
        return {
            "type": "touring_car",
            "main_points": [20, 17, 15, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            "fastest_lap_bonus": 0,  # Often no fastest lap bonus
            "reverse_grid_bonus": True
        }
    
    def simulate_event(self, context: DisciplineContext) -> List[RaceResult]:
        """Route to appropriate simulation based on event type"""
        if context.event_type == RaceEventType.QUALIFYING:
            return self._simulate_qualifying(context)
        elif context.event_type == RaceEventType.MAIN_RACE:
            return self._simulate_race(context)
        else:
            raise ValueError(f"Unsupported event type for Touring Cars: {context.event_type}")
    
    def _simulate_qualifying(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate touring car qualifying
        
        Features:
        - Less aerodynamic dependency than single seaters
        - Focus on mechanical grip and driver skill
        - Success ballast affecting performance
        - Setup window importance
        """
        qualifying_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base performance calculation
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Touring car specific factors
            setup_versatility = driver.adaptability * 0.025  # Setup flexibility important
            mechanical_grip = (driver.skill + driver.consistency) / 2.0 * 0.02
            
            # Success ballast impact (simulated based on championship position)
            ballast_penalty = self._calculate_ballast_penalty(driver, context)
            
            # Less luck factor than single seaters (more mechanical series)
            qualifying_variance = self.rng.normal(0, 0.01)
            
            total_performance = (
                base_performance + setup_versatility + mechanical_grip + 
                qualifying_variance - ballast_penalty
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
                points=0,  # No qualifying points in most touring car series
                fastest_lap=False,
                dnf_reason=None,
                grid_position=position
            )
            results.append(result)
        
        return results
    
    def _simulate_race(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate touring car main race
        
        Features:
        - High contact racing probability
        - Reverse grid option
        - Success ballast effects
        - Multi-class racing support
        - Enhanced incident simulation
        """
        race_performance = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Base race performance
            base_performance = self.calculate_base_performance(driver, team, context)
            
            # Touring car race factors
            close_racing_ability = self._calculate_close_racing_skill(driver)
            contact_racing_skill = self._calculate_contact_racing_ability(driver)
            traffic_management = driver.racecraft * 0.15
            
            # Success ballast penalty
            ballast_penalty = self._calculate_ballast_penalty(driver, context)
            
            # Multi-class factors (if enabled)
            class_performance_factor = self._calculate_class_factor(driver, team, context)
            
            # Defensive driving ability
            defensive_skill = (driver.racecraft + driver.aggression) / 2.0 * 0.1
            
            # Reliability (slightly lower than single seaters due to contact)
            reliability_factor = self._calculate_touring_reliability(team, context)
            
            total_performance = (
                base_performance * 0.4 + 
                close_racing_ability * 0.25 +
                contact_racing_skill * 0.15 +
                traffic_management * 0.10 +
                defensive_skill * 0.05 +
                class_performance_factor * 0.05
            ) * reliability_factor - ballast_penalty
            
            # Enhanced incident simulation for contact racing
            final_performance, dnf_reason = self._apply_touring_incidents(total_performance, driver, context)
            
            race_performance[driver.id] = (final_performance, dnf_reason)
        
        # Handle reverse grid if configured
        if self._is_reverse_grid_race(context):
            final_order = self._apply_reverse_grid(race_performance)
        else:
            final_order = sorted(race_performance.items(), key=lambda x: x[1][0], reverse=True)
        
        # Create results
        results = []
        for position, (driver_id, (performance, dnf_reason)) in enumerate(final_order, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            points = self.calculate_points(position, RaceEventType.MAIN_RACE)
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=points if dnf_reason is None else 0,
                fastest_lap=False,  # Will be assigned if applicable
                dnf_reason=dnf_reason,
                grid_position=position  # Simplified
            )
            results.append(result)
        
        # Assign fastest lap (if series awards it)
        self._assign_fastest_lap(results, context)
        
        return results
    
    def _calculate_ballast_penalty(self, driver: Driver, context: DisciplineContext) -> float:
        """
        Calculate success ballast penalty based on championship position
        
        Success ballast systems add weight to championship leaders to level competition.
        """
        # Simulate championship position effect (would normally come from database)
        # For now, use a simplified random assignment
        championship_position = self.rng.randint(1, len(context.drivers))
        
        # Ballast penalties typically affect top 3-8 drivers
        if championship_position == 1:
            return 0.08  # 8% performance penalty for leader
        elif championship_position == 2:
            return 0.06  # 6% penalty for second
        elif championship_position == 3:
            return 0.04  # 4% penalty for third
        elif championship_position <= 8:
            return 0.02  # 2% penalty for top 8
        else:
            return 0.0   # No penalty for others
    
    def _calculate_close_racing_skill(self, driver: Driver) -> float:
        """Calculate ability to race wheel-to-wheel"""
        # Combination of racecraft and aggression for close racing
        close_racing = (driver.racecraft * 0.7 + driver.aggression * 0.3)
        
        # Add some variance for racing instinct
        racing_instinct = self.rng.normal(0, 0.02)
        
        return close_racing * 0.2 + racing_instinct
    
    def _calculate_contact_racing_ability(self, driver: Driver) -> float:
        """Calculate ability to handle contact and physical racing"""
        # Aggression and consistency for handling contact
        contact_ability = (driver.aggression * 0.6 + driver.consistency * 0.4)
        
        return contact_ability * 0.15
    
    def _calculate_class_factor(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate multi-class performance factor"""
        # Check if multi-class racing is enabled
        discipline_config = getattr(context, 'discipline_config', {})
        if not discipline_config.get('multi_class', False):
            return 0.0
        
        # Simulate different class performance (would be based on actual car classes)
        class_multiplier = self.rng.choice([0.95, 1.0, 1.05])  # Different class speeds
        return (class_multiplier - 1.0) * 0.5  # Convert to performance modifier
    
    def _calculate_touring_reliability(self, team: Team, context: DisciplineContext) -> float:
        """Calculate reliability with higher incident rates than single seaters"""
        base_reliability = 0.92 - (0.15 if team.tier == "tier3" else 
                                  0.08 if team.tier == "tier2" else 0.03)
        
        # Contact racing increases mechanical stress
        contact_stress = 0.03
        
        # Weather impact
        weather_stress = context.weather_conditions["precipitation"] * 0.02
        
        final_reliability = base_reliability - contact_stress - weather_stress
        
        # Check for mechanical failure
        if self.rng.random() > final_reliability:
            return 0.0  # DNF
        
        return 1.0
    
    def _apply_touring_incidents(self, performance: float, driver: Driver, context: DisciplineContext) -> Tuple[float, Optional[str]]:
        """Apply touring car specific incidents (higher contact rates)"""
        incident_roll = self.rng.random()
        
        # Higher incident rates than single seaters due to contact racing
        contact_incident_chance = 0.08  # 8% chance of contact incident
        mechanical_incident_chance = 0.03  # 3% chance of mechanical issue
        
        # Aggressive drivers have higher incident risk but also more overtaking success
        aggression_risk = driver.aggression * 0.02
        aggression_reward = driver.aggression * 0.01
        
        total_incident_chance = contact_incident_chance + mechanical_incident_chance + aggression_risk
        
        if incident_roll < mechanical_incident_chance:
            # Mechanical DNF
            return 0.0, "mechanical"
        elif incident_roll < contact_incident_chance:
            # Contact incident
            if self.rng.random() < 0.7:  # 70% chance it's not a DNF
                performance_hit = self.rng.uniform(0.1, 0.3)
                return performance * (1.0 - performance_hit), None
            else:  # 30% chance it's a DNF
                return 0.0, random.choice(["contact", "accident", "spin"])
        elif incident_roll < total_incident_chance:
            # Minor racing incident
            return performance * self.rng.uniform(0.85, 0.95), None
        else:
            # Clean race with potential aggression bonus
            return performance + aggression_reward, None
    
    def _is_reverse_grid_race(self, context: DisciplineContext) -> bool:
        """Check if this is a reverse grid race"""
        discipline_config = getattr(context, 'discipline_config', {})
        return discipline_config.get('reverse_grid', False)
    
    def _apply_reverse_grid(self, race_performance: Dict) -> List[Tuple]:
        """Apply reverse grid to top performers"""
        # Sort by performance first
        sorted_performance = sorted(race_performance.items(), key=lambda x: x[1][0], reverse=True)
        
        # Reverse top 8 positions (common in touring cars)
        top_8 = sorted_performance[:8]
        remaining = sorted_performance[8:]
        
        # Reverse the top 8
        reversed_top_8 = list(reversed(top_8))
        
        # Combine reversed top 8 with remaining in original order
        return reversed_top_8 + remaining
    
    def _assign_fastest_lap(self, results: List[RaceResult], context: DisciplineContext) -> None:
        """Assign fastest lap if the series awards it"""
        discipline_config = getattr(context, 'discipline_config', {})
        if not discipline_config.get('fastest_lap_bonus', False):
            return
        
        # Only finishers are eligible
        finishers = [r for r in results if r.dnf_reason is None]
        
        if not finishers:
            return
        
        # Fastest lap often goes to someone with good pace (weighted by position)
        weights = [1.0 / (r.position * 0.5 + 0.5) for r in finishers]  # Top positions more likely
        fastest_lap_driver = self.rng.choice(finishers, p=[w/sum(weights) for w in weights])
        
        fastest_lap_driver.fastest_lap = True
        # Note: Touring cars often don't award bonus points for fastest lap
    
    def calculate_points(self, position: int, event_type: RaceEventType) -> int:
        """Calculate points using touring car system"""
        if event_type != RaceEventType.MAIN_RACE:
            return 0
        
        # Touring car points system (more spread out for closer championship)
        points_table = [20, 17, 15, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        
        if position <= len(points_table):
            return points_table[position - 1]
        else:
            return 0


# Export the engine
__all__ = ['ProductionTouringEngine']