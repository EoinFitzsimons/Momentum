"""
Championship Standings Management

Tracks driver and constructor championship points,
calculates standings, and manages season progression.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict

from database.database_manager import DatabaseManager
from systems.race_weekend import SessionResult


@dataclass
class DriverStanding:
    """Driver championship standing"""
    position: int
    driver_id: int
    driver_name: str
    team_id: int
    team_name: str
    points: float
    wins: int = 0
    podiums: int = 0
    poles: int = 0
    fastest_laps: int = 0
    races_entered: int = 0
    dnf_count: int = 0
    position_change: int = 0  # +/- from last race


@dataclass
class ConstructorStanding:
    """Constructor/Team championship standing"""
    position: int
    team_id: int
    team_name: str
    points: float
    wins: int = 0
    podiums: int = 0
    poles: int = 0
    one_two_finishes: int = 0
    races_entered: int = 0
    position_change: int = 0


@dataclass
class ChampionshipStandings:
    """Complete championship standings"""
    championship_id: int
    discipline: str
    season: int
    races_completed: int
    total_races: int
    
    driver_standings: List[DriverStanding] = field(default_factory=list)
    constructor_standings: List[ConstructorStanding] = field(default_factory=list)
    
    # Recent race winner
    last_race_winner: str = ""
    last_race_circuit: str = ""


class StandingsManager:
    """
    Manages championship standings calculations and updates
    
    Tracks points, wins, and statistics across a season.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # In-memory standings cache (championship_id -> standings)
        self.standings_cache: Dict[int, ChampionshipStandings] = {}
    
    def initialize_championship(
        self,
        championship_id: int,
        discipline: str,
        season: int,
        total_races: int
    ) -> ChampionshipStandings:
        """
        Initialize new championship standings
        
        Args:
            championship_id: Database championship ID
            discipline: Racing discipline
            season: Season year
            total_races: Total races in season
        
        Returns:
            Empty standings structure
        """
        standings = ChampionshipStandings(
            championship_id=championship_id,
            discipline=discipline,
            season=season,
            races_completed=0,
            total_races=total_races
        )
        
        # Initialize driver standings for all drivers in discipline
        teams = self.db.get_teams_by_discipline(discipline)[:20]
        
        for team in teams:
            drivers = self.db.get_drivers_by_team(team.id)
            
            for driver in drivers[:2]:
                standings.driver_standings.append(DriverStanding(
                    position=0,
                    driver_id=driver.id,
                    driver_name=f"{driver.first_name} {driver.last_name}",
                    team_id=team.id,
                    team_name=team.name,
                    points=0.0
                ))
        
        # Initialize constructor standings
        for team in teams:
            standings.constructor_standings.append(ConstructorStanding(
                position=0,
                team_id=team.id,
                team_name=team.name,
                points=0.0
            ))
        
        # Sort and assign initial positions
        self._update_positions(standings)
        
        # Cache and return
        self.standings_cache[championship_id] = standings
        return standings
    
    def update_with_race_results(
        self,
        championship_id: int,
        race_results: List[SessionResult],
        circuit_name: str
    ) -> ChampionshipStandings:
        """
        Update standings with race results
        
        Args:
            championship_id: Championship to update
            race_results: Race results with points
            circuit_name: Name of circuit
        
        Returns:
            Updated standings
        """
        standings = self.standings_cache.get(championship_id)
        if not standings:
            raise ValueError(f"Championship {championship_id} not initialized")
        
        # Store previous positions for change calculation
        previous_driver_positions = {
            ds.driver_id: ds.position 
            for ds in standings.driver_standings
        }
        previous_constructor_positions = {
            cs.team_id: cs.position 
            for cs in standings.constructor_standings
        }
        
        # Update driver standings
        driver_dict = {ds.driver_id: ds for ds in standings.driver_standings}
        constructor_dict = {cs.team_id: cs for cs in standings.constructor_standings}
        
        # Track team finishes for 1-2 detection
        team_finishes: Dict[int, List[int]] = defaultdict(list)
        
        for result in race_results:
            # Update driver
            if result.driver_id in driver_dict:
                driver = driver_dict[result.driver_id]
                driver.points += result.time_or_points
                driver.races_entered += 1
                
                if result.position == 1:
                    driver.wins += 1
                if result.position <= 3:
                    driver.podiums += 1
                if result.fastest_lap:
                    driver.fastest_laps += 1
                
                # Track team finish positions
                team_finishes[result.team_id].append(result.position)
            
            # Update constructor
            if result.team_id in constructor_dict:
                constructor = constructor_dict[result.team_id]
                constructor.points += result.time_or_points
                constructor.races_entered += 1
                
                if result.position == 1:
                    constructor.wins += 1
                if result.position <= 3:
                    constructor.podiums += 1
        
        # Check for 1-2 finishes
        for team_id, positions in team_finishes.items():
            if len(positions) >= 2 and 1 in positions and 2 in positions:
                constructor_dict[team_id].one_two_finishes += 1
        
        # Update positions
        self._update_positions(standings)
        
        # Calculate position changes
        for driver in standings.driver_standings:
            old_pos = previous_driver_positions.get(driver.driver_id, driver.position)
            driver.position_change = old_pos - driver.position  # Positive = moved up
        
        for constructor in standings.constructor_standings:
            old_pos = previous_constructor_positions.get(constructor.team_id, constructor.position)
            constructor.position_change = old_pos - constructor.position
        
        # Update metadata
        standings.races_completed += 1
        if race_results:
            standings.last_race_winner = race_results[0].driver_name
            standings.last_race_circuit = circuit_name
        
        return standings
    
    def add_qualifying_results(
        self,
        championship_id: int,
        qualifying_results: List[SessionResult]
    ):
        """Update pole position count from qualifying"""
        standings = self.standings_cache.get(championship_id)
        if not standings:
            return
        
        driver_dict = {ds.driver_id: ds for ds in standings.driver_standings}
        constructor_dict = {cs.team_id: cs for cs in standings.constructor_standings}
        
        # Award pole position to P1
        if qualifying_results:
            pole_sitter = qualifying_results[0]
            if pole_sitter.driver_id in driver_dict:
                driver_dict[pole_sitter.driver_id].poles += 1
            if pole_sitter.team_id in constructor_dict:
                constructor_dict[pole_sitter.team_id].poles += 1
    
    def get_standings(self, championship_id: int) -> Optional[ChampionshipStandings]:
        """Get current standings for championship"""
        return self.standings_cache.get(championship_id)
    
    def get_driver_position(self, championship_id: int, driver_id: int) -> int:
        """Get driver's current championship position"""
        standings = self.standings_cache.get(championship_id)
        if not standings:
            return 0
        
        for driver in standings.driver_standings:
            if driver.driver_id == driver_id:
                return driver.position
        
        return 0
    
    def get_top_drivers(self, championship_id: int, count: int = 10) -> List[DriverStanding]:
        """Get top N drivers"""
        standings = self.standings_cache.get(championship_id)
        if not standings:
            return []
        
        return standings.driver_standings[:count]
    
    def get_top_constructors(self, championship_id: int, count: int = 10) -> List[ConstructorStanding]:
        """Get top N constructors"""
        standings = self.standings_cache.get(championship_id)
        if not standings:
            return []
        
        return standings.constructor_standings[:count]
    
    def _update_positions(self, standings: ChampionshipStandings):
        """Recalculate positions based on points"""
        # Sort drivers by points (desc), then wins, then podiums
        standings.driver_standings.sort(
            key=lambda x: (-x.points, -x.wins, -x.podiums)
        )
        
        for idx, driver in enumerate(standings.driver_standings, 1):
            driver.position = idx
        
        # Sort constructors
        standings.constructor_standings.sort(
            key=lambda x: (-x.points, -x.wins, -x.podiums)
        )
        
        for idx, constructor in enumerate(standings.constructor_standings, 1):
            constructor.position = idx
    
    def is_championship_decided(self, championship_id: int) -> bool:
        """Check if championship is mathematically decided"""
        standings = self.standings_cache.get(championship_id)
        if not standings:
            return False
        
        if len(standings.driver_standings) < 2:
            return False
        
        # Calculate max possible points remaining
        races_remaining = standings.total_races - standings.races_completed
        max_points_per_race = 26  # 25 + 1 fastest lap
        max_possible = races_remaining * max_points_per_race
        
        leader = standings.driver_standings[0]
        second = standings.driver_standings[1]
        
        # Leader has mathematically won
        return leader.points - second.points > max_possible
    
    def get_championship_battle_info(self, championship_id: int) -> Dict:
        """Get info about close championship battles"""
        standings = self.standings_cache.get(championship_id)
        if not standings or len(standings.driver_standings) < 2:
            return {}
        
        leader = standings.driver_standings[0]
        second = standings.driver_standings[1]
        
        gap = leader.points - second.points
        races_remaining = standings.total_races - standings.races_completed
        
        return {
            'leader': leader.driver_name,
            'leader_team': leader.team_name,
            'second': second.driver_name,
            'second_team': second.team_name,
            'points_gap': gap,
            'races_remaining': races_remaining,
            'is_close': gap < 25,  # Within one race win
            'is_decided': self.is_championship_decided(championship_id)
        }
