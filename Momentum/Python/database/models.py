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
    Driver Entity Model - Comprehensive Multi-Discipline Driver System
    
    Represents individual racing drivers with 50+ attributes covering all aspects
    of motorsport performance. Drivers can compete across all disciplines with
    varying levels of aptitude and preference, just like real-world drivers
    who may excel in one area but can compete in multiple categories.
    
    Attribute Categories:
    1. Core Driving Skills (10 attributes) - fundamental driving abilities
    2. Physical & Mental Traits (10 attributes) - fitness, focus, pressure handling
    3. Technical Knowledge (8 attributes) - car setup, mechanical understanding
    4. Discipline Specializations (7 attributes) - aptitude for different racing types
    5. Race Craft & Strategy (8 attributes) - tactical racing intelligence
    6. Environmental Adaptation (7 attributes) - handling different conditions
    7. Personal & Social Traits (6 attributes) - personality and media presence
    
    All attributes use 0.0-100.0 scale (0=Poor, 50=Average, 100=Exceptional)
    Drivers have preferences and aptitudes but aren't locked to single disciplines.
    """
    # ===== CORE IDENTIFICATION =====
    id: int                                    # Unique driver identifier
    name: str                                  # Full driver name
    nationality: str                           # ISO country code (e.g., "GBR", "USA")
    birth_date: str                           # Birth date in YYYY-MM-DD format
    age: int = 25                             # Current age (affects performance curves)
    
    # ===== CORE DRIVING SKILLS (10 attributes) =====
    # Fundamental driving abilities that apply to all disciplines
    raw_speed: float = 50.0                   # Pure pace and fast lap ability
    consistency: float = 50.0                 # Maintaining performance over stints
    racecraft: float = 50.0                   # Strategic racing intelligence
    overtaking: float = 50.0                  # Ability to pass other drivers
    defensive_driving: float = 50.0           # Protecting position and blocking
    cornering_skill: float = 50.0             # Apex speed and racing line optimization
    braking_technique: float = 50.0           # Late braking and brake management
    acceleration_control: float = 50.0        # Launch technique and traction management
    spatial_awareness: float = 50.0           # Track positioning and gap judgment
    vehicle_control: float = 50.0             # Car handling at the limit
    
    # ===== PHYSICAL & MENTAL TRAITS (10 attributes) =====
    # Physical fitness and mental strength affecting performance
    physical_fitness: float = 50.0            # Endurance and physical conditioning
    reaction_time: float = 50.0               # Quick reflexes and response speed
    concentration: float = 50.0               # Mental focus over long periods
    pressure_handling: float = 50.0           # Performance under stress/pressure
    pain_tolerance: float = 50.0              # Handling discomfort and fatigue
    g_force_tolerance: float = 50.0           # Physical tolerance for high G forces
    coordination: float = 50.0                # Hand-eye coordination and smoothness
    multitasking: float = 50.0                # Managing multiple tasks simultaneously
    mental_resilience: float = 50.0           # Recovery from mistakes and setbacks
    adrenaline_management: float = 50.0       # Controlling excitement and nerves
    
    # ===== TECHNICAL KNOWLEDGE (8 attributes) =====
    # Understanding of car mechanics and setup
    setup_knowledge: float = 50.0             # Car setup and tuning understanding
    mechanical_sympathy: float = 50.0         # Preserving car components and reliability
    tire_management: float = 50.0             # Managing tire wear and grip
    fuel_management: float = 50.0             # Fuel saving and consumption optimization
    aerodynamics_understanding: float = 50.0  # Knowledge of aero effects and setup
    suspension_feel: float = 50.0             # Sensing car balance and handling
    engine_management: float = 50.0           # Power delivery and engine modes
    data_analysis: float = 50.0               # Interpreting telemetry and feedback
    
    # ===== DISCIPLINE SPECIALIZATIONS (7 attributes) =====
    # Natural aptitude for different racing categories
    single_seater_aptitude: float = 50.0      # Formula/open-wheel racing preference
    touring_car_aptitude: float = 50.0        # Close-contact production car racing
    rally_aptitude: float = 50.0              # Stage rally and off-road racing
    street_racing_aptitude: float = 50.0      # Urban/street racing and drifting
    drag_racing_aptitude: float = 50.0        # Straight-line acceleration racing
    rallycross_aptitude: float = 50.0         # Mixed-surface sprint racing
    endurance_aptitude: float = 50.0          # Long-distance racing specialization
    
    # ===== RACE CRAFT & STRATEGY (8 attributes) =====
    # Tactical and strategic racing abilities
    race_strategy: float = 50.0               # Understanding race strategy and timing
    pit_entry_exit: float = 50.0              # Pit lane entry/exit skill and timing
    traffic_management: float = 50.0          # Navigating through slower cars
    qualifying_pace: float = 50.0             # Extracting maximum single-lap pace
    race_pace: float = 50.0                   # Sustained race pace over full distance
    starting_skill: float = 50.0              # Launch technique and first lap performance
    tyre_warming: float = 50.0                # Bringing tires to optimal temperature
    energy_management: float = 50.0           # Managing power/fuel/battery strategically
    
    # ===== ENVIRONMENTAL ADAPTATION (7 attributes) =====
    # Adapting to different conditions and circumstances
    wet_weather_skill: float = 50.0           # Performance in rain and wet conditions
    night_driving: float = 50.0               # Racing in low visibility/darkness
    heat_tolerance: float = 50.0              # Handling hot temperature extremes
    cold_tolerance: float = 50.0              # Handling cold temperature extremes
    altitude_adaptation: float = 50.0          # Performance at high altitude tracks
    visibility_adaptation: float = 50.0       # Adjusting to fog/dust/low visibility
    surface_adaptation: float = 50.0          # Adjusting to different track surfaces
    
    # ===== PERSONAL & SOCIAL TRAITS (6 attributes) =====
    # Personality and interpersonal characteristics
    media_handling: float = 50.0              # Working with media and public relations
    sponsorship_appeal: float = 50.0          # Attractiveness to sponsors and brands
    fan_engagement: float = 50.0              # Fan interaction and popularity
    team_player: float = 50.0                 # Working effectively within team
    leadership: float = 50.0                  # Natural leadership and influence
    professionalism: float = 50.0             # Professional conduct and attitude
    
    # ===== CAREER STATISTICS & PROGRESSION =====
    career_wins: int = 0                      # Total race victories across all disciplines
    career_podiums: int = 0                   # Total podium finishes (top 3)
    career_points: int = 0                    # Cumulative championship points
    career_starts: int = 0                    # Total race entries
    career_dnf: int = 0                       # Did not finish count
    seasons_active: int = 0                   # Number of seasons competed
    
    # Discipline-specific career stats
    single_seater_wins: int = 0               # Wins in formula/single seater categories
    touring_wins: int = 0                     # Wins in touring/production car racing
    rally_wins: int = 0                       # Wins in rally/stage racing
    street_wins: int = 0                      # Wins in street/urban racing
    drag_wins: int = 0                        # Wins in drag/acceleration racing
    rallycross_wins: int = 0                  # Wins in rallycross/sprint racing
    endurance_wins: int = 0                   # Wins in endurance racing
    
    # ===== ADDITIONAL METADATA =====
    biography: str = ""                       # Driver background and career history
    career_highlights: str = ""               # Major achievements and memorable moments
    preferred_discipline: str = "single_seater" # Primary discipline preference
    career_phase: str = "active"              # rookie, rising, peak, veteran, declining, retired
    
    # Team and relationship data
    current_team_id: Optional[int] = None     # Current team assignment (FK to teams.id)
    previous_teams: str = ""                  # JSON list of previous team associations
    contract_length: int = 1                  # Remaining contract years
    salary: float = 1.0                       # Annual salary in millions USD
    
    # Performance trends and development
    form_trend: str = "stable"                # improving, stable, declining
    peak_performance_age: int = 28            # Age at which driver peaks
    retirement_age: int = 40                  # Expected retirement age
    learning_rate: float = 50.0               # Speed of attribute improvement
    
    # Special traits and achievements
    championship_titles: int = 0              # Total championship victories
    rookie_of_year_awards: int = 0            # Rookie season recognition
    fastest_laps: int = 0                     # Career fastest lap awards
    pole_positions: int = 0                   # Career pole position count
    
    def get_discipline_rating(self, discipline: str) -> float:
        """
        Calculate overall performance rating for a specific discipline
        
        This method provides a comprehensive evaluation of how well this driver
        would perform in the given discipline, considering their aptitude for
        that discipline as well as their overall driving abilities.
        
        Args:
            discipline: The racing discipline to evaluate
                      ("single_seater", "touring_car", "rally", "street_racing",
                       "drag_racing", "rallycross", "endurance")
        
        Returns:
            Overall performance rating (0-100 scale)
        """
        # Get discipline-specific aptitude
        aptitude_map = {
            "single_seater": self.single_seater_aptitude,
            "touring_car": self.touring_car_aptitude,
            "rally": self.rally_aptitude,
            "street_racing": self.street_racing_aptitude,
            "drag_racing": self.drag_racing_aptitude,
            "rallycross": self.rallycross_aptitude,
            "endurance": self.endurance_aptitude
        }
        
        discipline_aptitude = aptitude_map.get(discipline, 50.0)
        
        # Calculate average of key driving attributes
        core_skills = (
            self.raw_speed + self.consistency + self.racecraft + 
            self.vehicle_control + self.spatial_awareness
        ) / 5.0
        
        # Weight combination: 60% discipline aptitude, 40% core skills
        overall_rating = (discipline_aptitude * 0.6) + (core_skills * 0.4)
        
        return round(min(100.0, max(0.0, overall_rating)), 1)
    
    def get_overall_rating(self) -> float:
        """
        Calculate overall driver rating across all attributes
        
        Returns:
            Overall rating (0-100) representing driver's general ability
        """
        # Average of all core driving skills and key attributes
        core_skills = [
            self.raw_speed, self.consistency, self.racecraft, self.overtaking,
            self.vehicle_control, self.concentration, self.pressure_handling,
            self.setup_knowledge, self.tire_management, self.race_strategy
        ]
        
        return sum(core_skills) / len(core_skills)

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
-- Drivers table with comprehensive 50+ attributes
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nationality TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    age INTEGER NOT NULL DEFAULT 25,
    
    -- Core Driving Skills (10 attributes)
    raw_speed REAL NOT NULL DEFAULT 50.0 CHECK(raw_speed >= 0.0 AND raw_speed <= 100.0),
    consistency REAL NOT NULL DEFAULT 50.0 CHECK(consistency >= 0.0 AND consistency <= 100.0),
    racecraft REAL NOT NULL DEFAULT 50.0 CHECK(racecraft >= 0.0 AND racecraft <= 100.0),
    overtaking REAL NOT NULL DEFAULT 50.0 CHECK(overtaking >= 0.0 AND overtaking <= 100.0),
    defensive_driving REAL NOT NULL DEFAULT 50.0 CHECK(defensive_driving >= 0.0 AND defensive_driving <= 100.0),
    cornering_skill REAL NOT NULL DEFAULT 50.0 CHECK(cornering_skill >= 0.0 AND cornering_skill <= 100.0),
    braking_technique REAL NOT NULL DEFAULT 50.0 CHECK(braking_technique >= 0.0 AND braking_technique <= 100.0),
    acceleration_control REAL NOT NULL DEFAULT 50.0 CHECK(acceleration_control >= 0.0 AND acceleration_control <= 100.0),
    spatial_awareness REAL NOT NULL DEFAULT 50.0 CHECK(spatial_awareness >= 0.0 AND spatial_awareness <= 100.0),
    vehicle_control REAL NOT NULL DEFAULT 50.0 CHECK(vehicle_control >= 0.0 AND vehicle_control <= 100.0),
    
    -- Physical & Mental Traits (10 attributes)
    physical_fitness REAL NOT NULL DEFAULT 50.0 CHECK(physical_fitness >= 0.0 AND physical_fitness <= 100.0),
    reaction_time REAL NOT NULL DEFAULT 50.0 CHECK(reaction_time >= 0.0 AND reaction_time <= 100.0),
    concentration REAL NOT NULL DEFAULT 50.0 CHECK(concentration >= 0.0 AND concentration <= 100.0),
    pressure_handling REAL NOT NULL DEFAULT 50.0 CHECK(pressure_handling >= 0.0 AND pressure_handling <= 100.0),
    pain_tolerance REAL NOT NULL DEFAULT 50.0 CHECK(pain_tolerance >= 0.0 AND pain_tolerance <= 100.0),
    g_force_tolerance REAL NOT NULL DEFAULT 50.0 CHECK(g_force_tolerance >= 0.0 AND g_force_tolerance <= 100.0),
    coordination REAL NOT NULL DEFAULT 50.0 CHECK(coordination >= 0.0 AND coordination <= 100.0),
    multitasking REAL NOT NULL DEFAULT 50.0 CHECK(multitasking >= 0.0 AND multitasking <= 100.0),
    mental_resilience REAL NOT NULL DEFAULT 50.0 CHECK(mental_resilience >= 0.0 AND mental_resilience <= 100.0),
    adrenaline_management REAL NOT NULL DEFAULT 50.0 CHECK(adrenaline_management >= 0.0 AND adrenaline_management <= 100.0),
    
    -- Technical Knowledge (8 attributes)
    setup_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(setup_knowledge >= 0.0 AND setup_knowledge <= 100.0),
    mechanical_sympathy REAL NOT NULL DEFAULT 50.0 CHECK(mechanical_sympathy >= 0.0 AND mechanical_sympathy <= 100.0),
    tire_management REAL NOT NULL DEFAULT 50.0 CHECK(tire_management >= 0.0 AND tire_management <= 100.0),
    fuel_management REAL NOT NULL DEFAULT 50.0 CHECK(fuel_management >= 0.0 AND fuel_management <= 100.0),
    aerodynamics_understanding REAL NOT NULL DEFAULT 50.0 CHECK(aerodynamics_understanding >= 0.0 AND aerodynamics_understanding <= 100.0),
    suspension_feel REAL NOT NULL DEFAULT 50.0 CHECK(suspension_feel >= 0.0 AND suspension_feel <= 100.0),
    engine_management REAL NOT NULL DEFAULT 50.0 CHECK(engine_management >= 0.0 AND engine_management <= 100.0),
    data_analysis REAL NOT NULL DEFAULT 50.0 CHECK(data_analysis >= 0.0 AND data_analysis <= 100.0),
    
    -- Discipline Specializations (7 attributes)
    single_seater_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(single_seater_aptitude >= 0.0 AND single_seater_aptitude <= 100.0),
    touring_car_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(touring_car_aptitude >= 0.0 AND touring_car_aptitude <= 100.0),
    rally_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(rally_aptitude >= 0.0 AND rally_aptitude <= 100.0),
    street_racing_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(street_racing_aptitude >= 0.0 AND street_racing_aptitude <= 100.0),
    drag_racing_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(drag_racing_aptitude >= 0.0 AND drag_racing_aptitude <= 100.0),
    rallycross_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(rallycross_aptitude >= 0.0 AND rallycross_aptitude <= 100.0),
    endurance_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(endurance_aptitude >= 0.0 AND endurance_aptitude <= 100.0),
    
    -- Race Craft & Strategy (8 attributes)
    race_strategy REAL NOT NULL DEFAULT 50.0 CHECK(race_strategy >= 0.0 AND race_strategy <= 100.0),
    pit_entry_exit REAL NOT NULL DEFAULT 50.0 CHECK(pit_entry_exit >= 0.0 AND pit_entry_exit <= 100.0),
    traffic_management REAL NOT NULL DEFAULT 50.0 CHECK(traffic_management >= 0.0 AND traffic_management <= 100.0),
    qualifying_pace REAL NOT NULL DEFAULT 50.0 CHECK(qualifying_pace >= 0.0 AND qualifying_pace <= 100.0),
    race_pace REAL NOT NULL DEFAULT 50.0 CHECK(race_pace >= 0.0 AND race_pace <= 100.0),
    starting_skill REAL NOT NULL DEFAULT 50.0 CHECK(starting_skill >= 0.0 AND starting_skill <= 100.0),
    tyre_warming REAL NOT NULL DEFAULT 50.0 CHECK(tyre_warming >= 0.0 AND tyre_warming <= 100.0),
    energy_management REAL NOT NULL DEFAULT 50.0 CHECK(energy_management >= 0.0 AND energy_management <= 100.0),
    
    -- Environmental Adaptation (7 attributes)
    wet_weather_skill REAL NOT NULL DEFAULT 50.0 CHECK(wet_weather_skill >= 0.0 AND wet_weather_skill <= 100.0),
    night_driving REAL NOT NULL DEFAULT 50.0 CHECK(night_driving >= 0.0 AND night_driving <= 100.0),
    heat_tolerance REAL NOT NULL DEFAULT 50.0 CHECK(heat_tolerance >= 0.0 AND heat_tolerance <= 100.0),
    cold_tolerance REAL NOT NULL DEFAULT 50.0 CHECK(cold_tolerance >= 0.0 AND cold_tolerance <= 100.0),
    altitude_adaptation REAL NOT NULL DEFAULT 50.0 CHECK(altitude_adaptation >= 0.0 AND altitude_adaptation <= 100.0),
    visibility_adaptation REAL NOT NULL DEFAULT 50.0 CHECK(visibility_adaptation >= 0.0 AND visibility_adaptation <= 100.0),
    surface_adaptation REAL NOT NULL DEFAULT 50.0 CHECK(surface_adaptation >= 0.0 AND surface_adaptation <= 100.0),
    
    -- Personal & Social Traits (6 attributes)
    media_handling REAL NOT NULL DEFAULT 50.0 CHECK(media_handling >= 0.0 AND media_handling <= 100.0),
    sponsorship_appeal REAL NOT NULL DEFAULT 50.0 CHECK(sponsorship_appeal >= 0.0 AND sponsorship_appeal <= 100.0),
    fan_engagement REAL NOT NULL DEFAULT 50.0 CHECK(fan_engagement >= 0.0 AND fan_engagement <= 100.0),
    team_player REAL NOT NULL DEFAULT 50.0 CHECK(team_player >= 0.0 AND team_player <= 100.0),
    leadership REAL NOT NULL DEFAULT 50.0 CHECK(leadership >= 0.0 AND leadership <= 100.0),
    professionalism REAL NOT NULL DEFAULT 50.0 CHECK(professionalism >= 0.0 AND professionalism <= 100.0),
    
    -- Career Stats
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
    discipline TEXT NOT NULL CHECK(discipline IN ('SINGLE_SEATER', 'PRODUCTION_TOURING', 'RALLY_STAGE', 'URBAN_STREET', 'DRAG_ACCELERATION', 'SPRINT_RALLYCROSS', 'ENDURANCE')),
    tier TEXT NOT NULL CHECK(tier IN ('tier1', 'tier2', 'tier3', 'tier4', 'tier5')),
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
    discipline TEXT NOT NULL CHECK(discipline IN ('SINGLE_SEATER', 'PRODUCTION_TOURING', 'RALLY_STAGE', 'URBAN_STREET', 'DRAG_ACCELERATION', 'SPRINT_RALLYCROSS', 'ENDURANCE')),
    lap_record_time TEXT,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Championships table
CREATE TABLE IF NOT EXISTS championships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    discipline TEXT NOT NULL CHECK(discipline IN ('SINGLE_SEATER', 'PRODUCTION_TOURING', 'RALLY_STAGE', 'URBAN_STREET', 'DRAG_ACCELERATION', 'SPRINT_RALLYCROSS', 'ENDURANCE')),
    tier TEXT NOT NULL CHECK(tier IN ('tier1', 'tier2', 'tier3', 'tier4', 'tier5')),
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

-- Staff Members table with comprehensive 40+ attributes
CREATE TABLE IF NOT EXISTS staff_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nationality TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    age INTEGER NOT NULL DEFAULT 30,
    current_team_id INTEGER,
    role TEXT NOT NULL CHECK(role IN ('aerodynamics_engineer', 'cad_designer', 'chief_engineer', 'co-driver', 
                                      'commercial_manager', 'communications_manager', 'data_analyst', 'data_engineer',
                                      'design_engineer', 'development_driver', 'driver_coach', 'driving_consultant',
                                      'electronics_engineer', 'electronics_technician', 'engine_engineer', 'equipment_manager',
                                      'finance_manager', 'fitness_trainer', 'fuel_systems_technician', 'general_manager',
                                      'hr_manager', 'instructor', 'lead_driver', 'logistics_coordinator', 'marketing_manager',
                                      'materials_engineer', 'mechanic', 'media_relations', 'medical_officer', 'nutritionist',
                                      'operations_manager', 'performance_analyst', 'performance_engineer', 'photographer',
                                      'physiotherapist', 'pit_crew_chief', 'press_officer', 'race_engineer', 'race_strategist',
                                      'reserve_driver', 'safety_officer', 'setup_engineer', 'simulator_driver', 'sports_psychologist',
                                      'strategy_engineer', 'systems_engineer', 'team_principal', 'technical_director',
                                      'telemetry_engineer', 'test_driver', 'tire_technician', 'transport_manager',
                                      'vehicle_dynamics_engineer', 'videographer')),
    tier TEXT NOT NULL CHECK(tier IN ('tier1', 'tier2', 'tier3', 'tier4', 'tier5', 'tier6')),
    
    -- Core Competencies (10 attributes)
    technical_expertise REAL NOT NULL DEFAULT 50.0 CHECK(technical_expertise >= 0.0 AND technical_expertise <= 100.0),
    experience_years INTEGER NOT NULL DEFAULT 5,
    management_skill REAL NOT NULL DEFAULT 50.0 CHECK(management_skill >= 0.0 AND management_skill <= 100.0),
    innovation_ability REAL NOT NULL DEFAULT 50.0 CHECK(innovation_ability >= 0.0 AND innovation_ability <= 100.0),
    problem_solving REAL NOT NULL DEFAULT 50.0 CHECK(problem_solving >= 0.0 AND problem_solving <= 100.0),
    attention_to_detail REAL NOT NULL DEFAULT 50.0 CHECK(attention_to_detail >= 0.0 AND attention_to_detail <= 100.0),
    work_under_pressure REAL NOT NULL DEFAULT 50.0 CHECK(work_under_pressure >= 0.0 AND work_under_pressure <= 100.0),
    adaptability REAL NOT NULL DEFAULT 50.0 CHECK(adaptability >= 0.0 AND adaptability <= 100.0),
    learning_speed REAL NOT NULL DEFAULT 50.0 CHECK(learning_speed >= 0.0 AND learning_speed <= 100.0),
    decision_making REAL NOT NULL DEFAULT 50.0 CHECK(decision_making >= 0.0 AND decision_making <= 100.0),
    
    -- Technical Specializations (8 attributes)
    aerodynamics_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(aerodynamics_knowledge >= 0.0 AND aerodynamics_knowledge <= 100.0),
    engine_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(engine_knowledge >= 0.0 AND engine_knowledge <= 100.0),
    suspension_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(suspension_knowledge >= 0.0 AND suspension_knowledge <= 100.0),
    tire_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(tire_knowledge >= 0.0 AND tire_knowledge <= 100.0),
    electronics_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(electronics_knowledge >= 0.0 AND electronics_knowledge <= 100.0),
    data_analysis_skill REAL NOT NULL DEFAULT 50.0 CHECK(data_analysis_skill >= 0.0 AND data_analysis_skill <= 100.0),
    cfd_expertise REAL NOT NULL DEFAULT 50.0 CHECK(cfd_expertise >= 0.0 AND cfd_expertise <= 100.0),
    simulation_expertise REAL NOT NULL DEFAULT 50.0 CHECK(simulation_expertise >= 0.0 AND simulation_expertise <= 100.0),
    
    -- Strategic & Leadership (7 attributes)
    race_strategy_skill REAL NOT NULL DEFAULT 50.0 CHECK(race_strategy_skill >= 0.0 AND race_strategy_skill <= 100.0),
    team_leadership REAL NOT NULL DEFAULT 50.0 CHECK(team_leadership >= 0.0 AND team_leadership <= 100.0),
    negotiation_skill REAL NOT NULL DEFAULT 50.0 CHECK(negotiation_skill >= 0.0 AND negotiation_skill <= 100.0),
    budget_management REAL NOT NULL DEFAULT 50.0 CHECK(budget_management >= 0.0 AND budget_management <= 100.0),
    resource_allocation REAL NOT NULL DEFAULT 50.0 CHECK(resource_allocation >= 0.0 AND resource_allocation <= 100.0),
    long_term_planning REAL NOT NULL DEFAULT 50.0 CHECK(long_term_planning >= 0.0 AND long_term_planning <= 100.0),
    risk_assessment REAL NOT NULL DEFAULT 50.0 CHECK(risk_assessment >= 0.0 AND risk_assessment <= 100.0),
    
    -- Communication & People Skills (6 attributes)
    communication REAL NOT NULL DEFAULT 50.0 CHECK(communication >= 0.0 AND communication <= 100.0),
    driver_relationship REAL NOT NULL DEFAULT 50.0 CHECK(driver_relationship >= 0.0 AND driver_relationship <= 100.0),
    team_motivation REAL NOT NULL DEFAULT 50.0 CHECK(team_motivation >= 0.0 AND team_motivation <= 100.0),
    conflict_resolution REAL NOT NULL DEFAULT 50.0 CHECK(conflict_resolution >= 0.0 AND conflict_resolution <= 100.0),
    media_handling REAL NOT NULL DEFAULT 50.0 CHECK(media_handling >= 0.0 AND media_handling <= 100.0),
    stakeholder_management REAL NOT NULL DEFAULT 50.0 CHECK(stakeholder_management >= 0.0 AND stakeholder_management <= 100.0),
    
    -- Discipline Specializations (7 attributes)
    single_seater_expertise REAL NOT NULL DEFAULT 50.0 CHECK(single_seater_expertise >= 0.0 AND single_seater_expertise <= 100.0),
    touring_car_expertise REAL NOT NULL DEFAULT 50.0 CHECK(touring_car_expertise >= 0.0 AND touring_car_expertise <= 100.0),
    rally_expertise REAL NOT NULL DEFAULT 50.0 CHECK(rally_expertise >= 0.0 AND rally_expertise <= 100.0),
    street_racing_expertise REAL NOT NULL DEFAULT 50.0 CHECK(street_racing_expertise >= 0.0 AND street_racing_expertise <= 100.0),
    drag_racing_expertise REAL NOT NULL DEFAULT 50.0 CHECK(drag_racing_expertise >= 0.0 AND drag_racing_expertise <= 100.0),
    rallycross_expertise REAL NOT NULL DEFAULT 50.0 CHECK(rallycross_expertise >= 0.0 AND rallycross_expertise <= 100.0),
    endurance_expertise REAL NOT NULL DEFAULT 50.0 CHECK(endurance_expertise >= 0.0 AND endurance_expertise <= 100.0),
    
    -- Personal Traits (5 attributes)
    reliability REAL NOT NULL DEFAULT 50.0 CHECK(reliability >= 0.0 AND reliability <= 100.0),
    loyalty REAL NOT NULL DEFAULT 50.0 CHECK(loyalty >= 0.0 AND loyalty <= 100.0),
    ambition REAL NOT NULL DEFAULT 50.0 CHECK(ambition >= 0.0 AND ambition <= 100.0),
    professionalism REAL NOT NULL DEFAULT 50.0 CHECK(professionalism >= 0.0 AND professionalism <= 100.0),
    work_ethic REAL NOT NULL DEFAULT 50.0 CHECK(work_ethic >= 0.0 AND work_ethic <= 100.0),
    
    -- Additional Technical Skills (4 attributes)
    materials_science REAL NOT NULL DEFAULT 50.0 CHECK(materials_science >= 0.0 AND materials_science <= 100.0),
    cad_design REAL NOT NULL DEFAULT 50.0 CHECK(cad_design >= 0.0 AND cad_design <= 100.0),
    manufacturing_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(manufacturing_knowledge >= 0.0 AND manufacturing_knowledge <= 100.0),
    quality_control REAL NOT NULL DEFAULT 50.0 CHECK(quality_control >= 0.0 AND quality_control <= 100.0),
    
    -- Advanced Analytical Skills (7 attributes)
    telemetry_analysis REAL NOT NULL DEFAULT 50.0 CHECK(telemetry_analysis >= 0.0 AND telemetry_analysis <= 100.0),
    performance_modeling REAL NOT NULL DEFAULT 50.0 CHECK(performance_modeling >= 0.0 AND performance_modeling <= 100.0),
    statistical_methods REAL NOT NULL DEFAULT 50.0 CHECK(statistical_methods >= 0.0 AND statistical_methods <= 100.0),
    pattern_recognition REAL NOT NULL DEFAULT 50.0 CHECK(pattern_recognition >= 0.0 AND pattern_recognition <= 100.0),
    predictive_analytics REAL NOT NULL DEFAULT 50.0 CHECK(predictive_analytics >= 0.0 AND predictive_analytics <= 100.0),
    software_proficiency REAL NOT NULL DEFAULT 50.0 CHECK(software_proficiency >= 0.0 AND software_proficiency <= 100.0),
    database_management REAL NOT NULL DEFAULT 50.0 CHECK(database_management >= 0.0 AND database_management <= 100.0),
    
    -- Operational Skills (5 attributes)
    pit_stop_efficiency REAL NOT NULL DEFAULT 50.0 CHECK(pit_stop_efficiency >= 0.0 AND pit_stop_efficiency <= 100.0),
    crisis_management REAL NOT NULL DEFAULT 50.0 CHECK(crisis_management >= 0.0 AND crisis_management <= 100.0),
    equipment_maintenance REAL NOT NULL DEFAULT 50.0 CHECK(equipment_maintenance >= 0.0 AND equipment_maintenance <= 100.0),
    logistics_coordination REAL NOT NULL DEFAULT 50.0 CHECK(logistics_coordination >= 0.0 AND logistics_coordination <= 100.0),
    safety_protocols REAL NOT NULL DEFAULT 50.0 CHECK(safety_protocols >= 0.0 AND safety_protocols <= 100.0),
    
    -- Financial & Commercial Skills (3 attributes)
    commercial_acumen REAL NOT NULL DEFAULT 50.0 CHECK(commercial_acumen >= 0.0 AND commercial_acumen <= 100.0),
    sponsorship_development REAL NOT NULL DEFAULT 50.0 CHECK(sponsorship_development >= 0.0 AND sponsorship_development <= 100.0),
    cost_optimisation REAL NOT NULL DEFAULT 50.0 CHECK(cost_optimisation >= 0.0 AND cost_optimisation <= 100.0),
    
    -- Career & Development (4 attributes)
    previous_teams TEXT DEFAULT '',
    education_level TEXT DEFAULT 'bachelor',
    certifications TEXT DEFAULT '',
    languages_spoken INTEGER DEFAULT 1,
    contract_type TEXT DEFAULT 'full_time',
    
    -- Performance & Satisfaction (4 attributes)
    job_satisfaction REAL NOT NULL DEFAULT 75.0 CHECK(job_satisfaction >= 0.0 AND job_satisfaction <= 100.0),
    workload_capacity REAL NOT NULL DEFAULT 100.0 CHECK(workload_capacity >= 0.0 AND workload_capacity <= 200.0),
    current_workload REAL NOT NULL DEFAULT 50.0 CHECK(current_workload >= 0.0 AND current_workload <= 200.0),
    performance_rating REAL NOT NULL DEFAULT 75.0 CHECK(performance_rating >= 0.0 AND performance_rating <= 100.0),
    
    -- Career & Contract
    salary_demand REAL NOT NULL DEFAULT 50000.0,
    contract_years_remaining INTEGER DEFAULT 1,
    biography TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_team_id) REFERENCES teams (id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_drivers_team ON drivers(current_team_id);
CREATE INDEX IF NOT EXISTS idx_teams_discipline ON teams(discipline);
CREATE INDEX IF NOT EXISTS idx_tracks_discipline ON tracks(discipline);
CREATE INDEX IF NOT EXISTS idx_races_championship_season ON races(championship_id, season);
CREATE INDEX IF NOT EXISTS idx_race_results_race ON race_results(race_id);
CREATE INDEX IF NOT EXISTS idx_race_results_driver ON race_results(driver_id);
CREATE INDEX IF NOT EXISTS idx_staff_team ON staff_members(current_team_id);
CREATE INDEX IF NOT EXISTS idx_staff_role ON staff_members(role);
"""