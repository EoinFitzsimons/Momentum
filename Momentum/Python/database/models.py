""" models used for lightweight database views and minimal persistence.

This module contains the small 7-table dataclasses (Driver, Team, Track, Championship,
Race, RaceResult, StaffMember) and a  `SCHEMA_SQL` string used for
lightweight schema initialization where desired.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone


@dataclass
class Driver:
    id: int
    name: str
    nationality: str
    birth_date: str

    # Core performance attributes (0-100 scale)
    speed: float = 50.0
    racecraft: float = 50.0
    consistency: float = 50.0
    fitness: float = 50.0
    reactions: float = 50.0
    pressure: float = 50.0
    setup_knowledge: float = 50.0
    fuel_management: float = 50.0
    tyre_management: float = 50.0

    # Feedback & adaptability
    feedback: float = 50.0
    adaptability: float = 50.0

    # Career core stats
    career_points: int = 0
    career_podiums: int = 0
    career_starts: int = 0
    career_dnf: int = 0
    seasons_active: int = 0

    # Discipline-specific wins
    single_seater_wins: int = 0
    touring_wins: int = 0
    rally_wins: int = 0
    street_wins: int = 0
    drag_wins: int = 0
    rallycross_wins: int = 0
    endurance_wins: int = 0

    # Career progression
    peak_performance_age: Optional[int] = None
    retirement_age: Optional[int] = None
    learning_rate: float = 1.0
    form_trend: float = 0.0

    # Metadata
    biography: str = ""
    career_highlights: str = ""
    preferred_discipline: str = "SINGLE_SEATER"
    career_phase: str = "active"

    # Team & contract data
    current_team_id: Optional[int] = None
    previous_teams: str = "[]"  # JSON list stored as text
    contract_length: Optional[int] = None
    salary: Optional[float] = None
    name_locale: Optional[str] = None
    
    # Legacy/extra data
    # legacy attributes_extra removed

    @property
    def computed_age(self) -> int:
        if not self.birth_date:
            return 0
        try:
            bd = datetime.strptime(self.birth_date, "%Y-%m-%d").date()
            today = datetime.now(timezone.utc).date()
            years = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            return int(years)
        except Exception:
            return 0


@dataclass
class Team:
    id: int
    name: str
    nationality: str
    discipline: str
    tier: str
    budget: float
    founded_year: int = 1950
    team_principal: str = ""
    history: str = ""
    total_wins: int = 0
    total_podiums: int = 0
    championships: int = 0
    operations_rating: float = 50.0
    strategy_profile: str = "standard"


@dataclass
class Track:
    id: int
    name: str
    country: str
    primary_discipline: str

    # Special segments & behaviors
    is_point_to_point: bool = False
    joker_enabled: bool = False
    instructions_json: Optional[str] = None
    geometry_json: Optional[str] = None
    pit_entry_index: Optional[int] = None
    pit_exit_index: Optional[int] = None


@dataclass
class Championship:
    id: int
    name: str
    discipline: str
    season_length: int
    points_system: str
    current_season: int


@dataclass
class Race:
    id: int
    championship_id: int
    track_id: int
    season: int
    round_number: int
    race_date: str
    weather_conditions: str
    laps: int
    status: str = "scheduled"
    



@dataclass
class RaceResult:
    id: int
    race_id: int
    driver_id: int
    team_id: int
    position: int
    fastest_lap: bool = False
    points: int = 0
    dnf_reason: Optional[str] = None


@dataclass
class StaffMember:
    id: int
    name: str
    role: str
    rating: float
    current_team_id: Optional[int] = None


#  SCHEMA_SQL kept for tooling that needs the minimal 7-table schema
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nationality TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    speed REAL NOT NULL DEFAULT 50.0 CHECK(speed BETWEEN 0.0 AND 100.0),
    racecraft REAL NOT NULL DEFAULT 50.0 CHECK(racecraft BETWEEN 0.0 AND 100.0),
    consistency REAL NOT NULL DEFAULT 50.0 CHECK(consistency BETWEEN 0.0 AND 100.0),
    fitness REAL NOT NULL DEFAULT 50.0 CHECK(fitness BETWEEN 0.0 AND 100.0),
    reactions REAL NOT NULL DEFAULT 50.0 CHECK(reactions BETWEEN 0.0 AND 100.0),
    pressure REAL NOT NULL DEFAULT 50.0 CHECK(pressure BETWEEN 0.0 AND 100.0),
    setup_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(setup_knowledge BETWEEN 0.0 AND 100.0),
    fuel_management REAL NOT NULL DEFAULT 50.0 CHECK(fuel_management BETWEEN 0.0 AND 100.0),
    tyre_management REAL NOT NULL DEFAULT 50.0 CHECK(tyre_management BETWEEN 0.0 AND 100.0),

    feedback REAL NOT NULL DEFAULT 50.0 CHECK(feedback BETWEEN 0.0 AND 100.0),
    adaptability REAL NOT NULL DEFAULT 50.0 CHECK(adaptability BETWEEN 0.0 AND 100.0),

    career_points INTEGER DEFAULT 0,
    career_podiums INTEGER DEFAULT 0,
    career_starts INTEGER DEFAULT 0,
    career_dnf INTEGER DEFAULT 0,
    seasons_active INTEGER DEFAULT 0,

    single_seater_wins INTEGER DEFAULT 0,
    touring_wins INTEGER DEFAULT 0,
    rally_wins INTEGER DEFAULT 0,
    street_wins INTEGER DEFAULT 0,
    drag_wins INTEGER DEFAULT 0,
    rallycross_wins INTEGER DEFAULT 0,
    endurance_wins INTEGER DEFAULT 0,

    peak_performance_age INTEGER DEFAULT NULL,
    retirement_age INTEGER DEFAULT NULL,
    learning_rate REAL DEFAULT 1.0,
    form_trend REAL DEFAULT 0.0,

    biography TEXT DEFAULT '',
    career_highlights TEXT DEFAULT '',
    preferred_discipline TEXT DEFAULT 'SINGLE_SEATER',
    career_phase TEXT DEFAULT 'active',

    current_team_id INTEGER,
    previous_teams TEXT DEFAULT '[]',
    contract_length INTEGER DEFAULT NULL,
    salary REAL DEFAULT NULL,
    name_locale TEXT DEFAULT NULL,
    FOREIGN KEY (current_team_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    nationality TEXT NOT NULL,
    discipline TEXT NOT NULL,
    tier TEXT NOT NULL,
    budget REAL NOT NULL,
    founded_year INTEGER DEFAULT NULL,
    team_principal TEXT DEFAULT '',
    history TEXT DEFAULT '',
    total_wins INTEGER DEFAULT 0,
    total_podiums INTEGER DEFAULT 0,
    championships INTEGER DEFAULT 0,
    operations_rating REAL NOT NULL DEFAULT 50.0 CHECK(operations_rating BETWEEN 0.0 AND 100.0),
    strategy_profile TEXT DEFAULT 'standard'
);

CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    primary_discipline TEXT NOT NULL,
    -- Special segments & behavior flags
    is_point_to_point INTEGER NOT NULL DEFAULT 0,
    joker_enabled INTEGER NOT NULL DEFAULT 0,
    instructions_json TEXT DEFAULT NULL,
    geometry_json TEXT DEFAULT NULL,
    pit_entry_index INTEGER DEFAULT NULL,
    pit_exit_index INTEGER DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS championships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    discipline TEXT NOT NULL,
    season_length INTEGER NOT NULL,
    points_system TEXT NOT NULL,
    current_season INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS races (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    championship_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    race_date TEXT NOT NULL,
    status TEXT DEFAULT 'scheduled',
    FOREIGN KEY (championship_id) REFERENCES championships(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);

CREATE TABLE IF NOT EXISTS race_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    race_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    points INTEGER DEFAULT 0,
    FOREIGN KEY (race_id) REFERENCES races(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS staff_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    current_team_id INTEGER,
    FOREIGN KEY (current_team_id) REFERENCES teams(id)
);

CREATE INDEX IF NOT EXISTS idx_drivers_team ON drivers(current_team_id);
CREATE INDEX IF NOT EXISTS idx_teams_discipline ON teams(discipline);
CREATE INDEX IF NOT EXISTS idx_race_results_driver ON race_results(driver_id);
"""
