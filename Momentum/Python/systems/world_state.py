"""
Game World State Management

Manages the persistent state of the game world including current date,
active championships, player team, and overall game progression.

This is the CORE of the game - everything flows through here.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from database.database_manager import DatabaseManager
from database.models import Team, Driver, Championship, Race


@dataclass
class PlayerProfile:
    """Player's profile and career information"""
    player_name: str
    team_id: int
    career_start_date: str
    current_season: int = 1
    total_races: int = 0
    total_wins: int = 0
    total_podiums: int = 0
    podium_finishes: int = 0  # Alias for compatibility
    career_earnings: float = 0.0
    championships_won: int = 0


@dataclass
class GameWorldState:
    """Complete state of the game world at any point in time"""
    # Time and progression
    current_date: str  # ISO format: "2025-03-15"
    calendar_year: int
    season_number: int  # Career season counter (1, 2, 3...)
    
    # Player state
    player_profile: Optional[PlayerProfile]
    
    # Active championship
    active_championship_id: Optional[int]
    current_race_index: int  # Which race in the season (0-based)
    
    # Game metadata
    save_name: str = "default_save"
    last_saved: str = ""
    game_version: str = "0.1.0"


class GameWorld:
    """
    Main game world manager - handles all game state and progression
    
    This is the heart of the game. Everything else plugs into this.
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize game world"""
        self.db = db_manager or DatabaseManager()
        self.state: Optional[GameWorldState] = None
        self.current_season_races: List[Race] = []
        
    def new_game(self, player_name: str, starting_discipline: str = "SINGLE_SEATER") -> GameWorldState:
        """
        Start a new game
        
        Args:
            player_name: Player's name
            starting_discipline: Which racing discipline to start in
            
        Returns:
            Initial game world state
        """
        # Create player profile
        player = PlayerProfile(
            player_name=player_name,
            team_id=0,  # Will be selected in team selection phase
            career_start_date="2025-03-01",
            current_season=1
        )
        
        # Create initial world state
        self.state = GameWorldState(
            current_date="2025-03-01",
            calendar_year=2025,
            season_number=1,
            player_profile=player,
            active_championship_id=None,
            current_race_index=0,
            save_name=f"{player_name.lower().replace(' ', '_')}_career"
        )
        
        return self.state
    
    def select_team(self, team_id: int) -> bool:
        """
        Select player's starting team
        
        Args:
            team_id: ID of team to join
            
        Returns:
            True if successful
        """
        if not self.state or not self.state.player_profile:
            return False
        
        # Verify team exists
        team = self.db.get_team(team_id)
        if not team:
            return False
        
        # Assign team to player
        self.state.player_profile.team_id = team_id
        return True
    
    def create_championship_season(
        self, 
        discipline: str, 
        num_races: int = 10,
        championship_name: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new championship season
        
        Args:
            discipline: Racing discipline
            num_races: Number of races in season
            championship_name: Optional custom name
            
        Returns:
            Championship ID (generated internally for now)
        """
        if not self.state:
            return None
        
        # Generate a temporary championship ID
        # In a real implementation, this would be saved to database
        champ_id = hash(f"{discipline}_{self.state.calendar_year}") % 1000000
        
        # Generate race calendar
        self.current_season_races = self._generate_race_calendar(
            championship_id=champ_id,
            discipline=discipline,
            num_races=num_races
        )
        
        self.state.active_championship_id = champ_id
        self.state.current_race_index = 0
        
        # Initialize standings in the parent game
        # This will be called from the GUI which has the standings_manager
        
        return champ_id
    
    def _generate_race_calendar(
        self,
        championship_id: int,
        discipline: str,
        num_races: int
    ) -> List[Any]:  # Returns list of race-like objects
        """
        Generate race calendar for the season
        
        Args:
            championship_id: Championship ID
            discipline: Racing discipline
            num_races: Number of races to generate
            
        Returns:
            List of race-like objects with necessary attributes
        """
        # Get available circuits for this discipline
        circuits = self.db.get_circuits_by_discipline(discipline)
        
        if not circuits:
            raise ValueError(f"No circuits found for discipline: {discipline}")
        
        # Select random circuits (no repeats)
        import random
        selected_circuits = random.sample(circuits, min(num_races, len(circuits)))
        
        # Generate races at 2-week intervals starting from current date
        races = []
        race_date = datetime.fromisoformat(self.state.current_date)
        
        # Simple race object class
        class SimpleRace:
            def __init__(self, race_id, circuit_id, circuit, round_num, date, discipline):
                self.id = race_id
                self.circuit_id = circuit_id
                self.circuit = circuit  # Store full circuit object
                self.discipline = discipline
                self.round_number = round_num
                self.race_date = date
                self.status = "scheduled"
                self.total_laps = 50
        
        for i, circuit in enumerate(selected_circuits):
            race_id = championship_id * 1000 + i + 1  # Generate unique ID
            race = SimpleRace(
                race_id=race_id,
                circuit_id=circuit.id,
                circuit=circuit,
                round_num=i + 1,
                date=race_date.strftime("%Y-%m-%d"),
                discipline=discipline
            )
            races.append(race)
            
            # Next race in 2 weeks
            race_date += timedelta(weeks=2)
        
        return races
    
    def get_next_race(self) -> Optional[Race]:
        """
        Get the next scheduled race
        
        Returns:
            Next race or None if season complete
        """
        if not self.state or not self.current_season_races:
            return None
        
        if self.state.current_race_index >= len(self.current_season_races):
            return None  # Season complete
        
        return self.current_season_races[self.state.current_race_index]
    
    def advance_to_next_race(self) -> Optional[Race]:
        """
        Advance time to the next race
        
        Returns:
            Next race or None if season complete
        """
        next_race = self.get_next_race()
        if not next_race:
            return None
        
        # Update current date to race date
        self.state.current_date = next_race.race_date
        
        return next_race
    
    def complete_race(self, race_id: int) -> bool:
        """
        Mark a race as completed and advance to next
        
        Args:
            race_id: ID of completed race
            
        Returns:
            True if successful
        """
        if not self.state:
            return False
        
        # Increment race index
        self.state.current_race_index += 1
        
        # Update player stats
        if self.state.player_profile:
            self.state.player_profile.total_races += 1
        
        return True
    
    def is_season_complete(self) -> bool:
        """Check if current season is complete"""
        if not self.state or not self.current_season_races:
            return False
        
        return self.state.current_race_index >= len(self.current_season_races)
    
    def advance_season(self) -> bool:
        """
        Complete current season and advance to next
        
        Returns:
            True if successful
        """
        if not self.state:
            return False
        
        # Increment season counters
        self.state.season_number += 1
        self.state.calendar_year += 1
        self.state.current_race_index = 0
        
        if self.state.player_profile:
            self.state.player_profile.current_season += 1
        
        # Clear current season data
        self.current_season_races = []
        self.state.active_championship_id = None
        
        # Set date to start of new season
        self.state.current_date = f"{self.state.calendar_year}-03-01"
        
        return True
    
    def save_game(self, save_name: Optional[str] = None) -> bool:
        """
        Save current game state to disk
        
        Args:
            save_name: Optional save file name
            
        Returns:
            True if successful
        """
        if not self.state:
            return False
        
        if save_name:
            self.state.save_name = save_name
        
        # Update last saved timestamp
        self.state.last_saved = datetime.now().isoformat()
        
        # Create saves directory if it doesn't exist
        saves_dir = Path("saves")
        saves_dir.mkdir(exist_ok=True)
        
        # Save to JSON file
        save_path = saves_dir / f"{self.state.save_name}.json"
        
        save_data = {
            "state": asdict(self.state),
            "current_season_races": [asdict(race) for race in self.current_season_races]
        }
        
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        return True
    
    def load_game(self, save_name: str) -> bool:
        """
        Load game state from disk
        
        Args:
            save_name: Name of save file (without .json)
            
        Returns:
            True if successful
        """
        save_path = Path("saves") / f"{save_name}.json"
        
        if not save_path.exists():
            return False
        
        with open(save_path, 'r') as f:
            save_data = json.load(f)
        
        # Reconstruct state
        state_dict = save_data["state"]
        
        # Reconstruct player profile if exists
        player_profile = None
        if state_dict.get("player_profile"):
            player_profile = PlayerProfile(**state_dict["player_profile"])
        
        self.state = GameWorldState(
            current_date=state_dict["current_date"],
            calendar_year=state_dict["calendar_year"],
            season_number=state_dict["season_number"],
            player_profile=player_profile,
            active_championship_id=state_dict.get("active_championship_id"),
            current_race_index=state_dict["current_race_index"],
            save_name=state_dict.get("save_name", "default_save"),
            last_saved=state_dict.get("last_saved", ""),
            game_version=state_dict.get("game_version", "0.1.0")
        )
        
        # Reconstruct races
        # Note: This is simplified - in real implementation would need proper Race reconstruction
        self.current_season_races = []
        # TODO: Implement proper race reconstruction from saved data
        
        return True
    
    def list_saves(self) -> List[str]:
        """
        List all available save files
        
        Returns:
            List of save file names (without .json extension)
        """
        saves_dir = Path("saves")
        if not saves_dir.exists():
            return []
        
        return [f.stem for f in saves_dir.glob("*.json")]
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current game state for display
        
        Returns:
            Dictionary with state information
        """
        if not self.state:
            return {"status": "no_game_loaded"}
        
        summary = {
            "status": "active",
            "current_date": self.state.current_date,
            "calendar_year": self.state.calendar_year,
            "season": self.state.season_number,
            "player_name": self.state.player_profile.player_name if self.state.player_profile else None,
            "current_race": f"{self.state.current_race_index + 1}/{len(self.current_season_races)}" if self.current_season_races else "No active season",
            "season_complete": self.is_season_complete()
        }
        
        return summary
