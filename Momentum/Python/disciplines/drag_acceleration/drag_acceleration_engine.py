"""
Drag/Acceleration Racing Engine - Pure straight-line acceleration simulation

Implements drag racing with:
- Reaction time importance at start
- Launch technique and traction management
- Power-to-weight ratio optimization
- Bracket racing and elimination formats
- Tree timing and staging procedures
- Burnout box and tire warming

Features:
- Reaction time simulation with perfect tree timing
- Launch control and traction management
- Straight-line acceleration physics
- Bracket racing with dial-in times
- Elimination tournament formats
- Pro vs sportsman class distinctions

Authors: Final Year Project - Computer Science
"""

import random
from typing import List, Dict, Optional, Tuple
from enum import Enum

from database.models import Driver, Team, RaceResult
from ..base_engine import BaseDisciplineEngine, DisciplineContext, RacingDiscipline, RaceEventType


class DragRaceFormat(Enum):
    """Drag racing formats"""
    HEADS_UP = "heads_up"      # Fastest time wins
    BRACKET = "bracket"        # Consistency racing with dial-ins
    INDEX = "index"           # Handicap based on class


class DragClass(Enum):
    """Drag racing classes"""
    TOP_FUEL = "top_fuel"
    FUNNY_CAR = "funny_car"
    PRO_STOCK = "pro_stock"
    SPORTSMAN = "sportsman"
    STREET = "street"


class DragAccelerationEngine(BaseDisciplineEngine):
    """
    Drag/Acceleration Racing Engine
    
    Simulates pure straight-line acceleration racing where reaction time,
    launch technique, and power delivery are critical. Features both
    professional heads-up racing and sportsman bracket racing formats.
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        self.discipline = RacingDiscipline.DRAG_ACCELERATION
    
    def get_attribute_weights(self) -> Dict[str, float]:
        """Driver attribute weights for drag racing"""
        return {
            "skill": 0.30,        # Launch technique and gear changes
            "consistency": 0.35,   # Most important for bracket racing
            "racecraft": 0.05,     # Minimal importance in straight line
            "adaptability": 0.15,  # Track conditions adaptation
            "aggression": 0.25     # Reaction time and risk tolerance
        }
    
    def get_supported_event_types(self) -> List[RaceEventType]:
        """Drag racing supports qualifying and elimination rounds"""
        return [RaceEventType.QUALIFYING, RaceEventType.MAIN_RACE]
    
    def get_strategic_elements(self) -> List[str]:
        """Key strategic elements in drag racing"""
        return [
            "reaction_time", "launch_technique", "traction_management", "power_delivery",
            "gear_change_timing", "consistency", "dial_in_strategy", "tree_timing"
        ]
    
    def get_scoring_system(self) -> Dict[str, str]:
        """Drag racing scoring system"""
        return {
            "type": "elimination",
            "format": "tournament",
            "reaction_time_bonus": True,
            "et_record_bonus": True,
            "speed_record_bonus": True
        }
    
    def simulate_event(self, context: DisciplineContext) -> List[RaceResult]:
        """Route to appropriate simulation based on event type"""
        if context.event_type == RaceEventType.QUALIFYING:
            return self._simulate_qualifying_runs(context)
        elif context.event_type == RaceEventType.MAIN_RACE:
            return self._simulate_elimination_rounds(context)
        else:
            raise ValueError(f"Unsupported event type for Drag Racing: {context.event_type}")
    
    def _simulate_qualifying_runs(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate drag racing qualifying runs
        
        Drivers get multiple attempts to set their best time
        for elimination seeding or dial-in establishment
        """
        best_times = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Each driver gets 2-3 qualifying runs
            num_runs = 2 + (1 if self.rng.random() < 0.3 else 0)  # 70% get 2 runs, 30% get 3
            best_et = float('inf')
            
            for run in range(num_runs):
                # Simulate each qualifying run
                et_time, reaction_time, top_speed = self._simulate_drag_run(driver, team, context, is_qualifying=True)
                
                if et_time < best_et:
                    best_et = et_time
            
            best_times[driver.id] = best_et
        
        # Sort by best ET (fastest first)
        sorted_times = sorted(best_times.items(), key=lambda x: x[1])
        results = []
        
        for position, (driver_id, et_time) in enumerate(sorted_times, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=0,  # No qualifying points in drag racing
                fastest_lap=False,
                dnf_reason=None,
                grid_position=position  # Seeding for eliminations
            )
            results.append(result)
        
        return results
    
    def _simulate_elimination_rounds(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate drag racing elimination tournament
        
        Head-to-head elimination rounds until final winner
        """
        # Determine race format
        drag_format = self._determine_drag_format(context)
        
        if drag_format == DragRaceFormat.BRACKET:
            return self._simulate_bracket_racing(context)
        else:
            return self._simulate_heads_up_eliminations(context)
    
    def _simulate_heads_up_eliminations(self, context: DisciplineContext) -> List[RaceResult]:
        """Simulate heads-up elimination format (fastest wins)"""
        active_drivers = list(context.drivers)
        elimination_results = []
        current_round = 1
        
        while len(active_drivers) > 1:
            round_winners = []
            round_losers = []
            
            # Pair up drivers for head-to-head races
            pairs = self._create_elimination_pairs(active_drivers)
            
            for driver1, driver2 in pairs:
                winner, loser = self._simulate_heads_up_race(driver1, driver2, context)
                round_winners.append(winner)
                round_losers.append(loser)
            
            # Record eliminated drivers
            for loser in round_losers:
                position = len(elimination_results) + len(round_losers)
                points = self._calculate_elimination_points(position, len(context.drivers))
                
                result = RaceResult(
                    id=0,
                    race_id=context.race.id,
                    driver_id=loser.id,
                    team_id=loser.current_team_id,
                    position=position,
                    points=points,
                    fastest_lap=False,
                    dnf_reason=None,
                    grid_position=0
                )
                elimination_results.append(result)
            
            active_drivers = round_winners
            current_round += 1
        
        # Winner gets first place
        if active_drivers:
            winner = active_drivers[0]
            winner_result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=winner.id,
                team_id=winner.current_team_id,
                position=1,
                points=self._calculate_elimination_points(1, len(context.drivers)),
                fastest_lap=False,
                dnf_reason=None,
                grid_position=0
            )
            elimination_results.insert(0, winner_result)
        
        return elimination_results
    
    def _simulate_bracket_racing(self, context: DisciplineContext) -> List[RaceResult]:
        """
        Simulate bracket racing (consistency format)
        
        Drivers set dial-in times and try to run as close as possible
        without going faster (breaking out)
        """
        bracket_results = {}
        
        for driver in context.drivers:
            team = context.teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Establish dial-in time (predicted ET)
            dial_in_time = self._calculate_dial_in_time(driver, team, context)
            
            # Simulate actual run
            actual_et, reaction_time, top_speed = self._simulate_drag_run(driver, team, context, is_qualifying=False)
            
            # Calculate bracket result
            bracket_score = self._calculate_bracket_score(dial_in_time, actual_et, reaction_time)
            
            bracket_results[driver.id] = {
                'score': bracket_score,
                'dial_in': dial_in_time,
                'actual_et': actual_et,
                'reaction_time': reaction_time,
                'breakout': actual_et < dial_in_time  # Faster than dial-in = disqualification
            }
        
        # Sort by bracket score (lower is better)
        sorted_results = sorted(bracket_results.items(), 
                              key=lambda x: (x[1]['breakout'], x[1]['score']))
        
        results = []
        for position, (driver_id, result_data) in enumerate(sorted_results, 1):
            driver = next(d for d in context.drivers if d.id == driver_id)
            points = self.calculate_points(position, RaceEventType.MAIN_RACE)
            
            # Breakout = disqualification
            if result_data['breakout']:
                points = 0
                dnf_reason = "breakout"
            else:
                dnf_reason = None
            
            result = RaceResult(
                id=0,
                race_id=context.race.id,
                driver_id=driver_id,
                team_id=driver.current_team_id,
                position=position,
                points=points,
                fastest_lap=False,
                dnf_reason=dnf_reason,
                grid_position=position
            )
            results.append(result)
        
        return results
    
    def _simulate_drag_run(self, driver: Driver, team: Team, context: DisciplineContext, 
                          is_qualifying: bool = False) -> Tuple[float, float, float]:
        """
        Simulate a single drag racing run
        
        Returns: (ET time, reaction time, top speed)
        """
        # Reaction time (0.000-1.000 seconds, perfect is around 0.020)
        reaction_time = self._calculate_reaction_time(driver, context)
        
        # Launch performance
        launch_effectiveness = self._calculate_launch_performance(driver, team, context)
        
        # Straight-line acceleration
        acceleration_performance = self._calculate_acceleration(driver, team, context)
        
        # Calculate elapsed time (ET)
        base_et = 10.0  # Base ET for class (would vary by car class)
        et_modifier = 1.0 - (launch_effectiveness + acceleration_performance)
        elapsed_time = base_et * et_modifier
        
        # Add some variance
        if is_qualifying:
            variance = self.rng.normal(0, 0.02)  # Less variance in qualifying
        else:
            variance = self.rng.normal(0, 0.05)  # More variance under pressure
        
        elapsed_time += variance
        
        # Calculate top speed (simplified)
        top_speed = 120.0 + acceleration_performance * 50.0 + self.rng.normal(0, 3.0)
        
        return elapsed_time, reaction_time, top_speed
    
    def _calculate_reaction_time(self, driver: Driver, context: DisciplineContext) -> float:
        """Calculate driver reaction time to starting tree"""
        # Base reaction time influenced by aggression and consistency
        base_reaction = 0.100  # 100ms base
        
        # Aggression helps with quick reactions
        aggression_bonus = (driver.aggression - 50.0) / 100.0 * 0.050
        
        # Consistency helps with timing
        consistency_factor = (driver.consistency - 50.0) / 100.0 * 0.020
        
        # Add some random variance
        reaction_variance = self.rng.normal(0, 0.020)
        
        reaction_time = base_reaction - aggression_bonus - consistency_factor + reaction_variance
        
        # Clamp to realistic range (0.000 to 0.500)
        return max(0.000, min(0.500, reaction_time))
    
    def _calculate_launch_performance(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate launch effectiveness (traction and technique)"""
        # Driver skill affects launch technique
        launch_skill = driver.skill * 0.001
        
        # Team setup affects traction
        traction_setup = (0.8 if team.tier == "tier1" else 
                         0.6 if team.tier == "tier2" else 0.4) * 0.05
        
        # Track conditions affect grip
        track_prep = context.weather_conditions.get("temperature", 25) / 1000.0  # Hotter = less grip
        
        return launch_skill + traction_setup - track_prep
    
    def _calculate_acceleration(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate straight-line acceleration performance"""
        # Power-to-weight ratio (team dependent)
        power_factor = (0.9 if team.tier == "tier1" else 
                       0.7 if team.tier == "tier2" else 0.5) * 0.08
        
        # Driver's ability to manage power
        power_management = (driver.skill + driver.consistency) / 2.0 * 0.0005
        
        # Adaptability for changing conditions
        condition_adaptation = driver.adaptability * 0.0003
        
        return power_factor + power_management + condition_adaptation
    
    def _determine_drag_format(self, context: DisciplineContext) -> DragRaceFormat:
        """Determine drag racing format"""
        discipline_config = getattr(context, 'discipline_config', {})
        format_type = discipline_config.get('drag_format', 'heads_up')
        
        format_map = {
            'heads_up': DragRaceFormat.HEADS_UP,
            'bracket': DragRaceFormat.BRACKET,
            'index': DragRaceFormat.INDEX
        }
        
        return format_map.get(format_type, DragRaceFormat.HEADS_UP)
    
    def _create_elimination_pairs(self, drivers: List) -> List[Tuple]:
        """Create head-to-head pairs for elimination round"""
        pairs = []
        for i in range(0, len(drivers) - 1, 2):
            pairs.append((drivers[i], drivers[i + 1]))
        
        return pairs
    
    def _simulate_heads_up_race(self, driver1: Driver, driver2: Driver, 
                              context: DisciplineContext) -> Tuple[Driver, Driver]:
        """Simulate head-to-head drag race"""
        team1 = context.teams.get(driver1.current_team_id)
        team2 = context.teams.get(driver2.current_team_id)
        
        # Simulate runs for both drivers
        et1, rt1, speed1 = self._simulate_drag_run(driver1, team1, context)
        et2, rt2, speed2 = self._simulate_drag_run(driver2, team2, context)
        
        # Winner is fastest overall time (reaction + ET)
        total_time1 = rt1 + et1
        total_time2 = rt2 + et2
        
        if total_time1 < total_time2:
            return driver1, driver2
        else:
            return driver2, driver1
    
    def _calculate_dial_in_time(self, driver: Driver, team: Team, context: DisciplineContext) -> float:
        """Calculate driver's dial-in time prediction"""
        # Predict what time they think they can run
        expected_et, _, _ = self._simulate_drag_run(driver, team, context, is_qualifying=True)
        
        # Add strategic padding (consistency affects strategy)
        padding = (100.0 - driver.consistency) / 100.0 * 0.1
        
        return expected_et + padding
    
    def _calculate_bracket_score(self, dial_in: float, actual_et: float, reaction_time: float) -> float:
        """Calculate bracket racing score"""
        # Score is based on how close actual ET is to dial-in plus reaction time
        et_difference = abs(actual_et - dial_in)
        total_score = reaction_time + et_difference
        
        return total_score
    
    def _calculate_elimination_points(self, position: int, total_drivers: int) -> int:
        """Calculate points based on elimination position"""
        # Points based on how far you advance
        if position == 1:
            return 100  # Winner
        elif position <= 2:
            return 75   # Runner-up
        elif position <= 4:
            return 50   # Semi-final
        elif position <= 8:
            return 25   # Quarter-final
        else:
            return 10   # Early rounds
    
    def calculate_points(self, position: int, event_type: RaceEventType) -> int:
        """Calculate points using drag racing system"""
        if event_type != RaceEventType.MAIN_RACE:
            return 0
        
        # Drag racing points (tournament style)
        points_table = [100, 75, 50, 40, 32, 25, 20, 15, 12, 10, 8, 6, 4, 2, 1]
        
        if position <= len(points_table):
            return points_table[position - 1]
        else:
            return 1


# Export the engine
__all__ = ['DragAccelerationEngine', 'DragRaceFormat', 'DragClass']