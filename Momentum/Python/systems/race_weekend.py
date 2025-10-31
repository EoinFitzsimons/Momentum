"""
Race Weekend Management System

Handles complete race weekend flow:
- Practice sessions
- Qualifying
- Race simulation
- Results processing
- Points allocation
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
import random

from database.database_manager import DatabaseManager
from disciplines.race_simulation import RaceSimulator, SimulationContext


@dataclass
class SessionResult:
    """Result from a single session (practice/qualifying/race)"""
    session_type: str  # "practice", "qualifying", "race"
    driver_id: int
    driver_name: str
    team_id: int
    team_name: str
    position: int
    time_or_points: float  # Lap time for practice/quali, points for race
    gap_to_leader: float = 0.0
    fastest_lap: Optional[float] = None
    incidents: List[str] = None
    
    def __post_init__(self):
        if self.incidents is None:
            self.incidents = []


@dataclass
class RaceWeekendResults:
    """Complete results from a race weekend"""
    race_id: int
    circuit_name: str
    discipline: str
    date: str
    
    # Session results
    practice_results: List[SessionResult]
    qualifying_results: List[SessionResult]
    race_results: List[SessionResult]
    
    # Race statistics
    fastest_lap_driver: str = ""
    fastest_lap_time: float = 0.0
    pole_position_driver: str = ""
    race_winner: str = ""
    
    # Incidents and highlights
    dnf_drivers: List[str] = None
    safety_cars: int = 0
    incidents: List[str] = None
    
    def __post_init__(self):
        if self.dnf_drivers is None:
            self.dnf_drivers = []
        if self.incidents is None:
            self.incidents = []


class RaceWeekendManager:
    """
    Manages complete race weekend execution
    
    Coordinates practice, qualifying, and race sessions
    with realistic progression and driver performance.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.simulator = RaceSimulator()
    
    def run_practice_session(
        self,
        race_id: int,
        session_number: int = 1
    ) -> List[SessionResult]:
        """
        Run a practice session
        
        Args:
            race_id: Database race ID
            session_number: Which practice session (1, 2, 3)
        
        Returns:
            Practice session results
        """
        # Get race details
        race = self.db.get_race_by_id(race_id)
        if not race:
            raise ValueError(f"Race {race_id} not found")
        
        # Get participating drivers
        # For now, get all teams in discipline and their drivers
        teams = self.db.get_teams_by_discipline(race.discipline)
        
        results = []
        base_lap_time = self._estimate_lap_time(race.circuit_id, race.discipline)
        
        for team in teams[:20]:  # Limit to 20 teams for now
            drivers = self.db.get_drivers_by_team(team.id)
            
            for driver in drivers[:2]:  # Max 2 drivers per team
                # Simulate lap time with variance
                # Use average of key driving skills as overall rating
                skill_avg = (driver.raw_speed + driver.consistency + driver.cornering_skill) / 3.0
                skill_factor = (100 - skill_avg) / 100.0
                car_factor = random.uniform(0.95, 1.05)
                practice_variance = random.uniform(0.98, 1.03)
                
                lap_time = base_lap_time * (1.0 + skill_factor * 0.05) * car_factor * practice_variance
                
                results.append(SessionResult(
                    session_type=f"practice_{session_number}",
                    driver_id=driver.id,
                    driver_name=driver.name,
                    team_id=team.id,
                    team_name=team.name,
                    position=0,  # Will be sorted
                    time_or_points=lap_time,
                    fastest_lap=lap_time
                ))
        
        # Sort by lap time and assign positions
        results.sort(key=lambda x: x.time_or_points)
        for idx, result in enumerate(results, 1):
            result.position = idx
            result.gap_to_leader = result.time_or_points - results[0].time_or_points
        
        return results
    
    def run_qualifying(
        self,
        race_id: int,
        format: str = "standard"
    ) -> List[SessionResult]:
        """
        Run qualifying session
        
        Args:
            race_id: Database race ID
            format: Qualifying format ("standard", "knockout", "one_shot")
        
        Returns:
            Qualifying results (starting grid)
        """
        race = self.db.get_race_by_id(race_id)
        if not race:
            raise ValueError(f"Race {race_id} not found")
        
        teams = self.db.get_teams_by_discipline(race.discipline)
        
        results = []
        base_lap_time = self._estimate_lap_time(race.circuit_id, race.discipline)
        
        for team in teams[:20]:
            drivers = self.db.get_drivers_by_team(team.id)
            
            for driver in drivers[:2]:
                # Qualifying is tighter than practice
                # Use key qualifying attributes
                skill_avg = (driver.raw_speed + driver.qualifying_pace + driver.cornering_skill) / 3.0
                skill_factor = (100 - skill_avg) / 100.0
                car_factor = random.uniform(0.97, 1.03)
                qualifying_variance = random.uniform(0.995, 1.005)
                
                lap_time = base_lap_time * (1.0 + skill_factor * 0.03) * car_factor * qualifying_variance
                
                results.append(SessionResult(
                    session_type="qualifying",
                    driver_id=driver.id,
                    driver_name=driver.name,
                    team_id=team.id,
                    team_name=team.name,
                    position=0,
                    time_or_points=lap_time,
                    fastest_lap=lap_time
                ))
        
        # Sort and assign grid positions
        results.sort(key=lambda x: x.time_or_points)
        for idx, result in enumerate(results, 1):
            result.position = idx
            result.gap_to_leader = result.time_or_points - results[0].time_or_points
        
        return results
    
    def run_race(
        self,
        race_id: int,
        starting_grid: Optional[List[SessionResult]] = None,
        weather: str = "dry"
    ) -> List[SessionResult]:
        """
        Run the main race using the existing race simulation engine
        
        Args:
            race_id: Database race ID
            starting_grid: Qualifying results (if None, generate random grid)
            weather: Weather conditions
        
        Returns:
            Race results with points
        """
        race = self.db.get_race_by_id(race_id)
        if not race:
            raise ValueError(f"Race {race_id} not found")
        
        # Get circuit - it's already a Track object from the database
        track = self.db.get_circuit_by_id(race.circuit_id)
        if not track:
            raise ValueError(f"Circuit {race.circuit_id} not found")
        
        # Get teams and drivers
        team_list = self.db.get_teams_by_discipline(race.discipline)[:20]
        teams_dict = {}
        driver_list = []
        
        for team in team_list:
            teams_dict[team.id] = team
            drivers = self.db.get_drivers_by_team(team.id)
            driver_list.extend(drivers[:2])  # Add first 2 drivers from each team
        
        # Build simulation context with proper objects
        context = SimulationContext(
            race=race,
            track=track,
            drivers=driver_list,
            teams=teams_dict,
            weather_factor=1.0 if weather == "Clear" else 0.8
        )
        
        # Run simulation - returns List[RaceResult]
        simulation_results = self.simulator.simulate_race(context)
        
        # Convert to SessionResult format with points
        results = []
        points_system = self._get_points_system(race.discipline)
        
        for idx, race_result in enumerate(simulation_results, 1):
            points = points_system.get(idx, 0)
            
            # Check if fastest lap (bonus point)
            if race_result.fastest_lap and idx <= 10:
                points += 1
            
            # Get driver and team names from the objects we passed in
            driver = next((d for d in driver_list if d.id == race_result.driver_id), None)
            team = teams_dict.get(race_result.team_id)
            
            results.append(SessionResult(
                session_type="race",
                driver_id=race_result.driver_id,
                driver_name=driver.name if driver else f"Driver {race_result.driver_id}",
                team_id=race_result.team_id,
                team_name=team.name if team else f"Team {race_result.team_id}",
                position=idx,
                time_or_points=points,
                fastest_lap=race_result.fastest_lap_time if hasattr(race_result, 'fastest_lap_time') else None,
                gap_to_leader=race_result.gap_to_leader if hasattr(race_result, 'gap_to_leader') else 0.0
            ))
        
        return results
    
    def execute_complete_weekend(
        self,
        race_id: int,
        skip_practice: bool = False,
        weather: str = "dry"
    ) -> RaceWeekendResults:
        """
        Execute complete race weekend
        
        Args:
            race_id: Database race ID
            skip_practice: Skip practice sessions
            weather: Weather conditions
        
        Returns:
            Complete weekend results
        """
        race = self.db.get_race_by_id(race_id)
        circuit = self.db.get_circuit_by_id(race.circuit_id)
        
        # Practice sessions
        practice_results = []
        if not skip_practice:
            practice_results = self.run_practice_session(race_id, session_number=1)
        
        # Qualifying
        qualifying_results = self.run_qualifying(race_id)
        
        # Race
        race_results = self.run_race(race_id, starting_grid=qualifying_results, weather=weather)
        
        # Build complete results
        weekend_results = RaceWeekendResults(
            race_id=race_id,
            circuit_name=circuit.name if circuit else "Unknown",
            discipline=race.discipline,
            date=datetime.now().strftime("%Y-%m-%d"),
            practice_results=practice_results,
            qualifying_results=qualifying_results,
            race_results=race_results
        )
        
        # Extract highlights
        if qualifying_results:
            weekend_results.pole_position_driver = qualifying_results[0].driver_name
        
        if race_results:
            weekend_results.race_winner = race_results[0].driver_name
            
            # Find fastest lap
            fastest = min(
                [r for r in race_results if r.fastest_lap],
                key=lambda x: x.fastest_lap or float('inf'),
                default=None
            )
            if fastest and fastest.fastest_lap:
                weekend_results.fastest_lap_driver = fastest.driver_name
                weekend_results.fastest_lap_time = fastest.fastest_lap
        
        return weekend_results
    
    def _estimate_lap_time(self, circuit_id: int, discipline: str) -> float:
        """Estimate base lap time for circuit"""
        circuit = self.db.get_circuit_by_id(circuit_id)
        
        if not circuit:
            return 90.0  # Default 1:30
        
        # Base time on circuit length
        base_time = circuit.length_km * 15  # ~15 seconds per km
        
        # Adjust by discipline
        discipline_factors = {
            "SINGLE_SEATER": 0.85,
            "PRODUCTION_TOURING": 1.1,
            "RALLY_STAGE": 1.3,
            "URBAN_STREET": 1.0,
            "DRAG_ACCELERATION": 0.1,  # Very short
            "SPRINT_RALLYCROSS": 0.9,
            "ENDURANCE": 1.05
        }
        
        factor = discipline_factors.get(discipline, 1.0)
        return base_time * factor
    
    def _get_points_system(self, discipline: str) -> Dict[int, int]:
        """Get points system for discipline"""
        # F1-style points (can customize per discipline later)
        return {
            1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
            6: 8, 7: 6, 8: 4, 9: 2, 10: 1
        }
