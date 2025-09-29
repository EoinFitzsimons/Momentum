"""
Momentum Motorsport Simulation - Database Models

This module defines the complete data model for the Momentum multi-discipline
motorsport simulation system. It provides SQLite-based persistent storage
for all simulation entities including drivers, teams, tracks, championships,
and race results.

Data Model Overview:
- Driver: Individual racers with skill attributes and career statistics
- Team: Racing organizations with budgets, tiers, and operational data
- Track: Racing circuits with physical and gameplay characteristics
- Championship: Competition series with rules and point systems
- Race: Individual race events with conditions and metadata
- RaceResult: Race outcomes linking drivers, teams, and performance data

Key Features:
- Normalized relational schema with foreign key constraints
- Data validation through CHECK constraints
- Performance optimization via strategic indexing
- Flexible multi-discipline support (Formula, Rally, Endurance, Street)
- Career progression tracking with historical statistics

Compatibility: SQLite 3.7+, Python 3.8+
Authors: Final Year Project - Computer Science
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class Driver:
    """
    Driver Entity Model
    
    Represents individual racing drivers in the simulation with comprehensive
    attribute modeling for realistic performance simulation. Each driver has
    five core performance attributes that influence race outcomes through the
    Monte Carlo simulation engine.
    
    Performance Attributes (0.0 = Poor, 1.0 = Exceptional):
        - skill: Raw driving talent and speed
        - consistency: Ability to maintain performance lap after lap
        - aggression: Willingness to take risks and make bold moves
        - racecraft: Strategic racing intelligence and situational awareness
        - adaptability: Ability to adjust to changing conditions (weather, track, car)
    
    Career Statistics:
        - career_wins: Total race victories
        - career_podiums: Total podium finishes (1st, 2nd, 3rd places)
        - career_points: Cumulative championship points earned
    
    Usage in Simulation:
        Driver attributes are weighted and combined with team performance,
        track characteristics, and random factors to determine race outcomes
        via Monte Carlo methods.
    """
    # Core identification and personal information
    id: int                                    # Unique driver identifier
    name: str                                  # Full driver name
    nationality: str                           # ISO country code (e.g., "GBR", "USA")
    birth_date: str                           # Birth date in YYYY-MM-DD format
    
    # Performance attributes (normalized 0.0-1.0 scale)
    skill: float                              # Raw driving talent and speed (0.0-1.0)
    consistency: float                        # Performance reliability (0.0-1.0)
    aggression: float                         # Risk-taking tendency (0.0-1.0)
    racecraft: float                          # Strategic intelligence (0.0-1.0)
    adaptability: float                       # Environmental adaptation (0.0-1.0)
    
    # Career statistics and progression
    career_wins: int = 0                      # Total race victories
    career_podiums: int = 0                   # Total podium finishes (top 3)
    career_points: int = 0                    # Cumulative championship points
    
    # Additional metadata and historical depth
    biography: str = ""                       # Driver background and career history
    career_highlights: str = ""               # Major achievements and memorable moments
    personality_traits: str = ""              # Character traits affecting AI decisions
    career_phase: str = "active"              # active, rookie, veteran, retired
    
    # Team and relationship data
    current_team_id: Optional[int] = None     # Current team assignment (FK to teams.id)
    previous_teams: str = ""                  # JSON list of previous team associations
    
    # AI decision-making factors
    risk_tolerance: float = 0.5               # Affects strategic decisions (0.0-1.0)
    team_loyalty: float = 0.5                 # Likelihood to stay with team (0.0-1.0)
    media_savvy: float = 0.5                  # Marketing and sponsorship appeal (0.0-1.0)

@dataclass
class Team:
    """
    Team Entity Model
    
    Represents racing organizations/constructors in the simulation. Teams employ
    drivers and compete in championships across different motorsport disciplines.
    Financial resources (budget) and organizational tier directly impact
    competitive performance through car development and operational excellence.
    
    Discipline Categories:
        - "formula": Open-wheel racing (F1, F2, F3 style)
        - "rally": Off-road stage racing (WRC style)
        - "endurance": Long-distance circuit racing (Le Mans style)
        - "street": Production-based touring car racing
    
    Performance Tiers:
        - "tier1": Elite teams with maximum budgets and resources
        - "tier2": Competitive midfield teams with moderate resources
        - "tier3": Smaller teams with limited budgets and resources
    
    Financial Model:
        Budget directly influences car performance, development rate, and
        strategic options during races. Higher budgets enable better cars
        and more sophisticated race strategies.
    """
    # Core identification and organizational information
    id: int                                   # Unique team identifier
    name: str                                 # Team/constructor name
    nationality: str                          # Team's home country (ISO code)
    founded_year: int                         # Year team was established
    
    # Competitive classification
    discipline: str                           # Racing category (formula/rally/endurance/street)
    tier: str                                 # Performance tier (tier1/tier2/tier3)
    
    # Operational and financial data
    budget: float                             # Annual budget in millions USD
    headquarters: str                         # Team's base location/factory
    team_principal: str                       # Team leader/manager name
    
    # Career achievements and metadata
    biography: str = ""                       # Team history and background
    founding_story: str = ""                  # Team origins and philosophy
    total_wins: int = 0                       # Total race victories
    total_podiums: int = 0                    # Total podium finishes
    championships: int = 0                    # Constructor/team championship titles
    
    # Financial and operational characteristics
    financial_stability: float = 0.7          # Economic health indicator (0.0-1.0)
    management_quality: float = 0.6           # Operational excellence rating (0.0-1.0)
    innovation_focus: float = 0.5             # R&D and technology emphasis (0.0-1.0)
    
    # AI personality and decision-making traits
    risk_appetite: float = 0.5                # Strategic risk tolerance (0.0-1.0)
    driver_development: float = 0.5           # Focus on nurturing talent vs hiring stars (0.0-1.0)
    brand_focus: float = 0.5                  # Marketing vs performance priority (0.0-1.0)

@dataclass
class Track:
    """
    Track/Circuit Entity Model
    
    Represents racing venues with detailed characteristics that influence
    race outcomes and driver performance. Each track has unique properties
    that interact with driver attributes to create realistic performance
    variations across different circuits.
    
    Surface Types:
        - "tarmac": Sealed asphalt surfaces (most formula and street racing)
        - "gravel": Loose gravel surfaces (rally stages)
        - "mixed": Combination of surface types (some rally stages)
    
    Difficulty Factors (0.0-1.0 scale):
        - difficulty: Overall challenge level affecting all drivers
        - weather_impact: How much weather conditions affect lap times
        - overtaking_difficulty: How hard it is to pass other cars
    
    Simulation Impact:
        Track characteristics modify driver performance during races.
        Technical tracks favor skill/racecraft, while power tracks
        may favor different attributes. Weather impact determines how
        much rain affects race outcomes.
    """
    # Core identification and geographical information
    id: int                                   # Unique track identifier
    name: str                                 # Circuit/venue name
    country: str                              # Track location country
    length_km: float                          # Track length in kilometers
    
    # Physical and gameplay characteristics
    surface_type: str                         # Surface material (tarmac/gravel/mixed)
    difficulty: float                         # Overall challenge level (0.0-1.0)
    weather_impact: float                     # Weather sensitivity factor (0.0-1.0)
    overtaking_difficulty: float              # Passing difficulty (0.0-1.0)
    
    # Classification and records
    discipline: str                           # Racing discipline (formula/rally/endurance/street)
    lap_record_time: Optional[str] = None     # Fastest recorded lap time (MM:SS.mmm)
    description: str = ""                     # Track description and notable features

@dataclass
class Championship:
    """
    Championship/Series Entity Model
    
    Represents organized racing competitions with specific rules, point systems,
    and seasonal structures. Championships define the competitive framework
    within which races occur and standings are calculated.
    
    Points System:
        Stored as JSON string defining point awards by finishing position.
        Example: '{"1": 25, "2": 18, "3": 15, "4": 12, "5": 10}'
        Allows flexible point structures for different series.
    
    Season Structure:
        Each championship runs annual seasons with fixed number of races.
        Season length determines championship duration and competitive balance.
    """
    # Core identification and classification
    id: int                                   # Unique championship identifier
    name: str                                 # Championship/series name
    discipline: str                           # Racing discipline (formula/rally/endurance/street)
    tier: str                                 # Competition level (tier1/tier2/tier3)
    
    # Competition structure and rules
    season_length: int                        # Number of races per season
    points_system: str                        # JSON string defining point awards by position
    
    # Temporal information
    current_season: int                       # Active season year
    founded_year: int                         # Championship establishment year
    description: str = ""                     # Championship history and characteristics

@dataclass
class Race:
    """
    Race Event Entity Model
    
    Represents individual race events within championships. Each race links
    a championship, track, and specific conditions to create unique competitive
    scenarios for simulation.
    
    Weather Conditions:
        - "dry": Clear conditions with optimal grip
        - "wet": Rain conditions affecting lap times and strategy
        - "mixed": Changing conditions during race
    
    Race Status:
        - "scheduled": Future race not yet run
        - "completed": Race finished with results recorded
        - "cancelled": Race cancelled due to circumstances
    """
    # Core identification and relationships
    id: int                                   # Unique race identifier
    championship_id: int                      # Parent championship (FK)
    track_id: int                             # Venue for race (FK)
    
    # Scheduling and organization
    season: int                               # Season year
    round_number: int                         # Race number within season
    race_date: str                            # Race date (YYYY-MM-DD format)
    
    # Race conditions and specifications
    weather_conditions: str                   # Weather during race (dry/wet/mixed)
    race_duration_minutes: int                # Planned race duration
    status: str                               # Race status (scheduled/completed/cancelled)

@dataclass
class RaceResult:
    """
    Race Result Entity Model
    
    Records individual driver performance in specific races. Links drivers,
    teams, and races to capture complete competitive outcomes including
    positions, points awarded, and special achievements.
    
    Points Calculation:
        Points are awarded based on finishing position according to the
        championship's point system. Additional points may be awarded for
        achievements like fastest lap.
    
    Grid vs Final Position:
        - grid_position: Starting position after qualifying
        - position: Final race finishing position
        Difference indicates race performance and position changes.
    """
    # Core identification and relationships
    id: int                                   # Unique result identifier
    race_id: int                              # Race event (FK)
    driver_id: int                            # Driver participant (FK)
    team_id: int                              # Team affiliation (FK)
    
    # Performance and outcomes
    position: int                             # Final finishing position (1st, 2nd, etc.)
    points: int                               # Championship points awarded
    
    # Special achievements and additional data
    fastest_lap: bool = False                 # Whether driver achieved fastest lap
    dnf_reason: Optional[str] = None          # Reason for non-finish (if applicable)
    grid_position: int = 1                    # Starting grid position after qualifying

# Database Schema Creation SQL
SCHEMA_SQL = """
-- Drivers table
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nationality TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    skill REAL NOT NULL CHECK(skill >= 0.0 AND skill <= 1.0),
    consistency REAL NOT NULL CHECK(consistency >= 0.0 AND consistency <= 1.0),
    aggression REAL NOT NULL CHECK(aggression >= 0.0 AND aggression <= 1.0),
    racecraft REAL NOT NULL CHECK(racecraft >= 0.0 AND racecraft <= 1.0),
    adaptability REAL NOT NULL CHECK(adaptability >= 0.0 AND adaptability <= 1.0),
    career_wins INTEGER DEFAULT 0,
    career_podiums INTEGER DEFAULT 0,
    career_points INTEGER DEFAULT 0,
    biography TEXT DEFAULT '',
    current_team_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_team_id) REFERENCES teams (id)
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    nationality TEXT NOT NULL,
    founded_year INTEGER NOT NULL,
    discipline TEXT NOT NULL CHECK(discipline IN ('formula', 'rally', 'endurance', 'street')),
    tier TEXT NOT NULL CHECK(tier IN ('tier1', 'tier2', 'tier3')),
    budget REAL NOT NULL,
    headquarters TEXT NOT NULL,
    team_principal TEXT NOT NULL,
    biography TEXT DEFAULT '',
    total_wins INTEGER DEFAULT 0,
    total_podiums INTEGER DEFAULT 0,
    championships INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracks table
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    length_km REAL NOT NULL,
    surface_type TEXT NOT NULL CHECK(surface_type IN ('tarmac', 'gravel', 'mixed')),
    difficulty REAL NOT NULL CHECK(difficulty >= 0.0 AND difficulty <= 1.0),
    weather_impact REAL NOT NULL CHECK(weather_impact >= 0.0 AND weather_impact <= 1.0),
    overtaking_difficulty REAL NOT NULL CHECK(overtaking_difficulty >= 0.0 AND overtaking_difficulty <= 1.0),
    discipline TEXT NOT NULL CHECK(discipline IN ('formula', 'rally', 'endurance', 'street')),
    lap_record_time TEXT,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Championships table
CREATE TABLE IF NOT EXISTS championships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    discipline TEXT NOT NULL CHECK(discipline IN ('formula', 'rally', 'endurance', 'street')),
    tier TEXT NOT NULL CHECK(tier IN ('tier1', 'tier2', 'tier3')),
    season_length INTEGER NOT NULL,
    points_system TEXT NOT NULL, -- JSON string
    current_season INTEGER NOT NULL,
    founded_year INTEGER NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Races table
CREATE TABLE IF NOT EXISTS races (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    championship_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    race_date TEXT NOT NULL,
    weather_conditions TEXT DEFAULT 'dry',
    race_duration_minutes INTEGER NOT NULL,
    status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (championship_id) REFERENCES championships (id),
    FOREIGN KEY (track_id) REFERENCES tracks (id),
    UNIQUE(championship_id, season, round_number)
);

-- Race results table
CREATE TABLE IF NOT EXISTS race_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    race_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    points INTEGER DEFAULT 0,
    fastest_lap BOOLEAN DEFAULT FALSE,
    dnf_reason TEXT,
    grid_position INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (race_id) REFERENCES races (id),
    FOREIGN KEY (driver_id) REFERENCES drivers (id),
    FOREIGN KEY (team_id) REFERENCES teams (id),
    UNIQUE(race_id, driver_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_drivers_team ON drivers(current_team_id);
CREATE INDEX IF NOT EXISTS idx_teams_discipline ON teams(discipline);
CREATE INDEX IF NOT EXISTS idx_tracks_discipline ON tracks(discipline);
CREATE INDEX IF NOT EXISTS idx_races_championship_season ON races(championship_id, season);
CREATE INDEX IF NOT EXISTS idx_race_results_race ON race_results(race_id);
CREATE INDEX IF NOT EXISTS idx_race_results_driver ON race_results(driver_id);
"""