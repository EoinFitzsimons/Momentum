"""
Game Loop and Championship System

Manages season progression, race scheduling, championship standings, and game state.
Provides a simplified, functional game loop for the backend simulation.

Features:
- Season initialization and progression
- Race calendar generation
- Championship standings calculation
- Points system management
- Season completion and winners
- Save/load game state

Authors: Final Year Project - Computer Science
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

from database.database_manager import DatabaseManager
from database.models import Championship, Race, RaceResult, Driver, Team, Track
from disciplines.race_simulation import RaceSimulator, SimulationContext


# Standard F1-style points system (top 10 positions)
DEFAULT_POINTS_SYSTEM = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
    6: 8, 7: 6, 8: 4, 9: 2, 10: 1
}


@dataclass
class ChampionshipStanding:
    """Individual driver/team standing in championship"""
    driver_id: int
    driver_name: str
    team_id: int
    team_name: str
    points: int
    wins: int
    podiums: int
    races_completed: int
    best_finish: int


@dataclass
class SeasonState:
    """Current state of a racing season"""
    season_year: int
    championship_id: int
    championship_name: str
    discipline: str
    
    current_round: int
    total_rounds: int
    
    races_completed: List[int]  # Race IDs
    races_remaining: List[int]  # Race IDs
    
    driver_standings: List[ChampionshipStanding]
    team_standings: List[Tuple[int, str, int]]  # (team_id, team_name, points)
    
    is_season_complete: bool = False
    champion_driver_id: Optional[int] = None
    champion_team_id: Optional[int] = None


class GameLoop:
    """
    Main game loop manager for championship progression
    
    Handles season flow, race execution, standings updates, and game state persistence.
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize game loop with database connection"""
        self.db = db_manager or DatabaseManager()
        self.simulator = RaceSimulator()
        self.current_season: Optional[SeasonState] = None
    
    def create_season(self, discipline: str, num_races: int = 10, season_year: int = 2025) -> SeasonState:
        """
        Create a new championship season
        
        Args:
            discipline: Racing discipline (SINGLE_SEATER, etc.)
            num_races: Number of races in season
            season_year: Year for the season
            
        Returns:
            SeasonState object representing the new season
        """
        # Get or create championship for this discipline
        championship = self._get_or_create_championship(discipline, season_year)
        
        # Get tracks for this discipline
        all_tracks = self.db.get_tracks_by_discipline(discipline)
        if len(all_tracks) < num_races:
            num_races = len(all_tracks)
        
        # Select tracks for the season (first N tracks)
        selected_tracks = all_tracks[:num_races]
        
        # Create race calendar
        race_ids = []
        start_date = datetime(season_year, 3, 1)  # Start in March
        
        for round_num, track in enumerate(selected_tracks, 1):
            race_date = start_date + timedelta(weeks=2 * (round_num - 1))
            
            race = Race(
                id=0,  # Will be assigned by database
                championship_id=championship.id,
                track_id=track.id,
                season=season_year,
                round_number=round_num,
                race_date=race_date.strftime("%Y-%m-%d"),
                weather_conditions="dry",
                race_duration_minutes=90,
                status="scheduled"
            )
            
            race_id = self.db.create_race(race)
            race_ids.append(race_id)
        
        # Initialize season state
        season = SeasonState(
            season_year=season_year,
            championship_id=championship.id,
            championship_name=championship.name,
            discipline=discipline,
            current_round=1,
            total_rounds=num_races,
            races_completed=[],
            races_remaining=race_ids,
            driver_standings=[],
            team_standings=[]
        )
        
        self.current_season = season
        return season
    
    def simulate_next_race(self, weather: str = "dry", num_laps: int = 50) -> Dict:
        """
        Simulate the next scheduled race in the season
        
        Args:
            weather: Weather conditions (dry/wet/mixed)
            num_laps: Number of laps to race
            
        Returns:
            Dictionary with race results and updated standings
        """
        if not self.current_season:
            raise ValueError("No active season. Call create_season() first.")
        
        if not self.current_season.races_remaining:
            raise ValueError("No races remaining in season. Season is complete.")
        
        # Get next race
        next_race_id = self.current_season.races_remaining[0]
        race = self.db.get_race(next_race_id)
        
        if not race:
            raise ValueError(f"Race {next_race_id} not found in database")
        
        # Get track
        track = self.db.get_track_by_id(race.track_id)
        
        # Get participating teams and drivers
        teams_list = self.db.get_teams_by_discipline(self.current_season.discipline)
        selected_teams = teams_list[:20]  # Max 20 teams
        
        all_drivers = []
        teams_dict = {}
        
        for team in selected_teams:
            teams_dict[team.id] = team
            drivers = self.db.get_drivers_by_team(team.id)
            if drivers:
                all_drivers.extend(drivers[:2])  # Max 2 drivers per team
        
        # Map weather to factor
        weather_map = {"dry": 1.0, "wet": 0.7, "mixed": 0.85}
        weather_factor = weather_map.get(weather.lower(), 1.0)
        
        # Update race object with details
        race.weather_conditions = weather
        race.status = "completed"
        
        # Create simulation context
        context = SimulationContext(
            race=race,
            track=track,
            drivers=all_drivers,
            teams=teams_dict,
            weather_factor=weather_factor
        )
        
        # Run simulation
        race_results = self.simulator.simulate_race(context)
        
        # Store results in database
        for result in race_results:
            self.db.create_race_result(result)
        
        # Update race status in database
        self.db.update_race_status(race.id, "completed")
        
        # Update driver statistics
        for result in race_results:
            if result.position == 1:
                self.db.update_driver_stats(result.driver_id, wins=1, podiums=1, points=result.points)
            elif result.position <= 3:
                self.db.update_driver_stats(result.driver_id, podiums=1, points=result.points)
            else:
                self.db.update_driver_stats(result.driver_id, points=result.points)
        
        # Update season state
        self.current_season.races_completed.append(next_race_id)
        self.current_season.races_remaining.pop(0)
        self.current_season.current_round += 1
        
        # Recalculate standings
        self._update_standings()
        
        # Check if season is complete
        if not self.current_season.races_remaining:
            self._complete_season()
        
        # Format results for return
        formatted_results = []
        for result in race_results:
            driver = next((d for d in all_drivers if d.id == result.driver_id), None)
            team = teams_dict.get(result.team_id)
            
            formatted_results.append({
                "position": result.position,
                "driver": f"{driver.first_name} {driver.last_name}" if driver else "Unknown",
                "team": team.name if team else "Unknown",
                "driver_id": result.driver_id,
                "team_id": result.team_id,
                "points": result.points,
                "fastest_lap": result.fastest_lap,
                "status": result.status
            })
        
        return {
            "race_id": race.id,
            "round": race.round_number,
            "track": track.name,
            "weather": weather,
            "num_laps": num_laps,
            "results": formatted_results,
            "season_status": {
                "current_round": self.current_season.current_round,
                "total_rounds": self.current_season.total_rounds,
                "races_remaining": len(self.current_season.races_remaining),
                "is_complete": self.current_season.is_season_complete
            },
            "championship_leader": self._get_championship_leader()
        }
    
    def get_season_state(self) -> Optional[Dict]:
        """Get current season state as dictionary"""
        if not self.current_season:
            return None
        
        return {
            "season_year": self.current_season.season_year,
            "championship": self.current_season.championship_name,
            "discipline": self.current_season.discipline,
            "current_round": self.current_season.current_round,
            "total_rounds": self.current_season.total_rounds,
            "races_completed": len(self.current_season.races_completed),
            "races_remaining": len(self.current_season.races_remaining),
            "is_complete": self.current_season.is_season_complete,
            "driver_standings": [
                {
                    "position": idx + 1,
                    "driver": standing.driver_name,
                    "team": standing.team_name,
                    "points": standing.points,
                    "wins": standing.wins,
                    "podiums": standing.podiums
                }
                for idx, standing in enumerate(self.current_season.driver_standings[:10])
            ],
            "champion": self._get_champion_info() if self.current_season.is_season_complete else None
        }
    
    def _get_or_create_championship(self, discipline: str, season_year: int) -> Championship:
        """Get existing championship or create new one"""
        # Try to get existing championship for this discipline
        championships = self.db.get_all_championships()
        
        for champ in championships:
            if champ.discipline == discipline:
                return champ
        
        # Create new championship
        championship = Championship(
            id=0,
            name=f"{discipline.replace('_', ' ').title()} Championship",
            discipline=discipline,
            tier="tier1",
            season_length=10,
            points_system=json.dumps(DEFAULT_POINTS_SYSTEM),
            current_season=season_year,
            founded_year=season_year,
            description=f"Premier {discipline.replace('_', ' ')} racing series"
        )
        
        champ_id = self.db.create_championship(championship)
        championship.id = champ_id
        return championship
    
    def _update_standings(self):
        """Recalculate championship standings based on all completed races"""
        if not self.current_season:
            return
        
        # Get all results for completed races
        driver_points = {}  # driver_id -> {points, wins, podiums, races, best_finish}
        team_points = {}    # team_id -> points
        
        for race_id in self.current_season.races_completed:
            results = self.db.get_race_results(race_id)
            
            for result in results:
                # Update driver stats
                if result.driver_id not in driver_points:
                    driver_points[result.driver_id] = {
                        'points': 0,
                        'wins': 0,
                        'podiums': 0,
                        'races': 0,
                        'best_finish': 99
                    }
                
                driver_points[result.driver_id]['points'] += result.points
                driver_points[result.driver_id]['races'] += 1
                
                if result.position == 1:
                    driver_points[result.driver_id]['wins'] += 1
                    driver_points[result.driver_id]['podiums'] += 1
                elif result.position <= 3:
                    driver_points[result.driver_id]['podiums'] += 1
                
                if result.position < driver_points[result.driver_id]['best_finish']:
                    driver_points[result.driver_id]['best_finish'] = result.position
                
                # Update team points
                if result.team_id not in team_points:
                    team_points[result.team_id] = 0
                team_points[result.team_id] += result.points
        
        # Create driver standings list
        driver_standings = []
        for driver_id, stats in driver_points.items():
            driver = self.db.get_driver(driver_id)
            team = self.db.get_team(driver.current_team_id) if driver else None
            
            if driver and team:
                standing = ChampionshipStanding(
                    driver_id=driver_id,
                    driver_name=f"{driver.first_name} {driver.last_name}",
                    team_id=team.id,
                    team_name=team.name,
                    points=stats['points'],
                    wins=stats['wins'],
                    podiums=stats['podiums'],
                    races_completed=stats['races'],
                    best_finish=stats['best_finish']
                )
                driver_standings.append(standing)
        
        # Sort by points (descending), then by wins, then by best finish
        driver_standings.sort(key=lambda x: (-x.points, -x.wins, x.best_finish))
        
        # Create team standings list
        team_standings = []
        for team_id, points in team_points.items():
            team = self.db.get_team(team_id)
            if team:
                team_standings.append((team_id, team.name, points))
        
        team_standings.sort(key=lambda x: -x[2])  # Sort by points descending
        
        # Update season state
        self.current_season.driver_standings = driver_standings
        self.current_season.team_standings = team_standings
    
    def _complete_season(self):
        """Mark season as complete and determine champions"""
        if not self.current_season or not self.current_season.driver_standings:
            return
        
        self.current_season.is_season_complete = True
        
        # Set champions
        if self.current_season.driver_standings:
            self.current_season.champion_driver_id = self.current_season.driver_standings[0].driver_id
        
        if self.current_season.team_standings:
            self.current_season.champion_team_id = self.current_season.team_standings[0][0]
    
    def _get_championship_leader(self) -> Optional[Dict]:
        """Get current championship leader"""
        if not self.current_season or not self.current_season.driver_standings:
            return None
        
        leader = self.current_season.driver_standings[0]
        return {
            "driver": leader.driver_name,
            "team": leader.team_name,
            "points": leader.points,
            "wins": leader.wins
        }
    
    def _get_champion_info(self) -> Optional[Dict]:
        """Get season champion information"""
        if not self.current_season.is_season_complete:
            return None
        
        driver_champ = None
        team_champ = None
        
        if self.current_season.champion_driver_id:
            champ_standing = next(
                (s for s in self.current_season.driver_standings 
                 if s.driver_id == self.current_season.champion_driver_id),
                None
            )
            if champ_standing:
                driver_champ = {
                    "driver": champ_standing.driver_name,
                    "team": champ_standing.team_name,
                    "points": champ_standing.points,
                    "wins": champ_standing.wins,
                    "podiums": champ_standing.podiums
                }
        
        if self.current_season.champion_team_id:
            team_info = next(
                (t for t in self.current_season.team_standings 
                 if t[0] == self.current_season.champion_team_id),
                None
            )
            if team_info:
                team_champ = {
                    "team": team_info[1],
                    "points": team_info[2]
                }
        
        return {
            "driver_champion": driver_champ,
            "team_champion": team_champ
        }
