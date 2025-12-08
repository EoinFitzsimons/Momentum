"""
Momentum Motorsport Simulation - Database Models (archived copy)

This file is an archived snapshot of the original `Momentum/Python/database/models.py`.
It has been moved to `archive/models.py` to make way for a simplified, improved
schema in `Momentum/Python/database/` as requested. Keep this file read-only
as the canonical historical record of the previous schema and model definitions.
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
    """
    # ===== CORE IDENTIFICATION =====
    id: int                                    # Unique driver identifier
    name: str                                  # Full driver name
    nationality: str
    birth_date: str                           # Birth date in YYYY-MM-DD format
    age: int = 25

    # ===== CORE DRIVING SKILLS (10 attributes) =====
    raw_speed: float = 50.0
    consistency: float = 50.0
    racecraft: float = 50.0
    overtaking: float = 50.0
    defensive_driving: float = 50.0
    cornering_skill: float = 50.0
    braking_technique: float = 50.0
    acceleration_control: float = 50.0
    spatial_awareness: float = 50.0
    vehicle_control: float = 50.0

    # ===== PHYSICAL & MENTAL TRAITS (10 attributes) =====
    physical_fitness: float = 50.0
    reaction_time: float = 50.0
    concentration: float = 50.0
    pressure_handling: float = 50.0
    pain_tolerance: float = 50.0
    g_force_tolerance: float = 50.0
    coordination: float = 50.0
    multitasking: float = 50.0
    mental_resilience: float = 50.0
    adrenaline_management: float = 50.0

    # ===== TECHNICAL KNOWLEDGE (8 attributes) =====
    setup_knowledge: float = 50.0
    mechanical_sympathy: float = 50.0
    tire_management: float = 50.0
    fuel_management: float = 50.0
    aerodynamics_understanding: float = 50.0
    suspension_feel: float = 50.0
    engine_management: float = 50.0
    data_analysis: float = 50.0

    # ===== DISCIPLINE SPECIALIZATIONS (7 attributes) =====
    single_seater_aptitude: float = 50.0
    touring_car_aptitude: float = 50.0
    rally_aptitude: float = 50.0
    street_racing_aptitude: float = 50.0
    drag_racing_aptitude: float = 50.0
    rallycross_aptitude: float = 50.0
    endurance_aptitude: float = 50.0

    # ===== RACE CRAFT & STRATEGY (8 attributes) =====
    race_strategy: float = 50.0
    pit_entry_exit: float = 50.0
    traffic_management: float = 50.0
    qualifying_pace: float = 50.0
    race_pace: float = 50.0
    starting_skill: float = 50.0
    tyre_warming: float = 50.0
    energy_management: float = 50.0

    # ===== ENVIRONMENTAL ADAPTATION (7 attributes) =====
    wet_weather_skill: float = 50.0
    night_driving: float = 50.0
    heat_tolerance: float = 50.0
    cold_tolerance: float = 50.0
    altitude_adaptation: float = 50.0
    visibility_adaptation: float = 50.0
    surface_adaptation: float = 50.0

    # ===== PERSONAL & SOCIAL TRAITS (6 attributes) =====
    media_handling: float = 50.0
    sponsorship_appeal: float = 50.0
    fan_engagement: float = 50.0
    team_player: float = 50.0
    leadership: float = 50.0
    professionalism: float = 50.0

    # ===== CAREER STATISTICS & PROGRESSION =====
    career_wins: int = 0
    career_podiums: int = 0
    career_points: int = 0
    career_starts: int = 0
    career_dnf: int = 0
    seasons_active: int = 0

    single_seater_wins: int = 0
    touring_wins: int = 0
    rally_wins: int = 0
    street_wins: int = 0
    drag_wins: int = 0
    rallycross_wins: int = 0
    endurance_wins: int = 0

    biography: str = ""
    career_highlights: str = ""
    preferred_discipline: str = "single_seater"
    career_phase: str = "active"

    current_team_id: Optional[int] = None
    previous_teams: str = ""
    contract_length: int = 1
    salary: float = 1.0

    form_trend: str = "stable"
    peak_performance_age: int = 28
    retirement_age: int = 40
    learning_rate: float = 50.0

    championship_titles: int = 0
    rookie_of_year_awards: int = 0
    fastest_laps: int = 0
    pole_positions: int = 0

    def get_discipline_rating(self, discipline: str) -> float:
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
        core_skills = (
            self.raw_speed + self.consistency + self.racecraft +
            self.vehicle_control + self.spatial_awareness
        ) / 5.0
        overall_rating = (discipline_aptitude * 0.6) + (core_skills * 0.4)
        return round(min(100.0, max(0.0, overall_rating)), 1)

    def get_overall_rating(self) -> float:
        core_skills = [
            self.raw_speed, self.consistency, self.racecraft, self.overtaking,
            self.vehicle_control, self.concentration, self.pressure_handling,
            self.setup_knowledge, self.tire_management, self.race_strategy
        ]
        return sum(core_skills) / len(core_skills)

    @property
    def skill(self) -> float:
        return self.raw_speed

    @property
    def adaptability(self) -> float:
        return (self.wet_weather_skill + self.surface_adaptation +
                self.visibility_adaptation) / 3.0

    @property
    def aggression(self) -> float:
        return (self.overtaking + self.defensive_driving) / 2.0

    @property
    def first_name(self) -> str:
        return self.name.split()[0] if self.name else ""

    @property
    def last_name(self) -> str:
        parts = self.name.split()
        return parts[-1] if len(parts) > 1 else ""


@dataclass
class Team:
    id: int
    name: str
    nationality: str
    founded_year: int
    discipline: str
    tier: str
    budget: float
    headquarters: str
    team_principal: str
    biography: str = ""
    founding_story: str = ""
    total_wins: int = 0
    total_podiums: int = 0
    championships: int = 0
    financial_stability: float = 0.7
    management_quality: float = 0.6
    innovation_focus: float = 0.5
    risk_appetite: float = 0.5
    driver_development: float = 0.5
    brand_focus: float = 0.5


@dataclass
class Track:
    id: int
    name: str
    country: str
    region: str
    circuit_type: str
    ima_grade: str
    primary_discipline: str
    length_km: float
    turns: int
    left_turns: int
    right_turns: int
    elevation_change_m: float
    max_gradient_percent: float
    min_gradient_percent: float
    surface: str
    track_width_avg_m: float
    track_width_min_m: float
    track_width_max_m: float
    avg_speed_kmh: float
    top_speed_kmh: float
    longest_straight_m: int
    shortest_straight_m: int
    tightest_corner_radius_m: float
    climate: str
    avg_temp_summer_c: float
    avg_temp_winter_c: float
    rainfall_mm_annual: int
    altitude_m: int
    pit_boxes: int
    pit_lane_length_m: float
    pit_speed_limit_kmh: int
    paddock_capacity_teams: int
    grandstand_capacity: int
    drs_zones: int
    safety_car_probability: float
    night_racing_capable: bool
    wet_weather_racing: bool
    is_active: bool
    debut_year: int
    last_used_year: Optional[int] = None
    created_at: Optional[str] = None
    surface_type: str = "tarmac"
    difficulty: float = 0.5
    weather_impact: float = 0.5
    overtaking_difficulty: float = 0.5
    discipline: str = ""
    lap_record_time: Optional[str] = None
    description: str = ""


@dataclass
class Championship:
    id: int
    name: str
    discipline: str
    tier: str
    season_length: int
    points_system: str
    current_season: int
    founded_year: int
    description: str = ""


@dataclass
class Race:
    id: int
    championship_id: int
    track_id: int
    season: int
    round_number: int
    race_date: str
    weather_conditions: str
    race_duration_minutes: int
    status: str

    @property
    def circuit_id(self) -> int:
        return self.track_id

    @property
    def discipline(self) -> str:
        return getattr(self, '_discipline', 'SINGLE_SEATER')


@dataclass
class RaceResult:
    id: int
    race_id: int
    driver_id: int
    team_id: int
    position: int
    points: int
    fastest_lap: bool = False
    dnf_reason: Optional[str] = None
    grid_position: int = 1


SCHEMA_SQL = """
-- Drivers table (archived schema snapshot)
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nationality TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    age INTEGER NOT NULL DEFAULT 25,
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
    setup_knowledge REAL NOT NULL DEFAULT 50.0 CHECK(setup_knowledge >= 0.0 AND setup_knowledge <= 100.0),
    mechanical_sympathy REAL NOT NULL DEFAULT 50.0 CHECK(mechanical_sympathy >= 0.0 AND mechanical_sympathy <= 100.0),
    tire_management REAL NOT NULL DEFAULT 50.0 CHECK(tire_management >= 0.0 AND tire_management <= 100.0),
    fuel_management REAL NOT NULL DEFAULT 50.0 CHECK(fuel_management >= 0.0 AND fuel_management <= 100.0),
    aerodynamics_understanding REAL NOT NULL DEFAULT 50.0 CHECK(aerodynamics_understanding >= 0.0 AND aerodynamics_understanding <= 100.0),
    suspension_feel REAL NOT NULL DEFAULT 50.0 CHECK(suspension_feel >= 0.0 AND suspension_feel <= 100.0),
    engine_management REAL NOT NULL DEFAULT 50.0 CHECK(engine_management >= 0.0 AND engine_management <= 100.0),
    data_analysis REAL NOT NULL DEFAULT 50.0 CHECK(data_analysis >= 0.0 AND data_analysis <= 100.0),
    single_seater_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(single_seater_aptitude >= 0.0 AND single_seater_aptitude <= 100.0),
    touring_car_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(touring_car_aptitude >= 0.0 AND touring_car_aptitude <= 100.0),
    rally_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(rally_aptitude >= 0.0 AND rally_aptitude <= 100.0),
    street_racing_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(street_racing_aptitude >= 0.0 AND street_racing_aptitude <= 100.0),
    drag_racing_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(drag_racing_aptitude >= 0.0 AND drag_racing_aptitude <= 100.0),
    rallycross_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(rallycross_aptitude >= 0.0 AND rallycross_aptitude <= 100.0),
    endurance_aptitude REAL NOT NULL DEFAULT 50.0 CHECK(endurance_aptitude >= 0.0 AND endurance_aptitude <= 100.0),
    race_strategy REAL NOT NULL DEFAULT 50.0 CHECK(race_strategy >= 0.0 AND race_strategy <= 100.0),
    pit_entry_exit REAL NOT NULL DEFAULT 50.0 CHECK(pit_entry_exit >= 0.0 AND pit_entry_exit <= 100.0),
    traffic_management REAL NOT NULL DEFAULT 50.0 CHECK(traffic_management >= 0.0 AND traffic_management <= 100.0),
    qualifying_pace REAL NOT NULL DEFAULT 50.0 CHECK(qualifying_pace >= 0.0 AND qualifying_pace <= 100.0),
    race_pace REAL NOT NULL DEFAULT 50.0 CHECK(race_pace >= 0.0 AND race_pace <= 100.0),
    starting_skill REAL NOT NULL DEFAULT 50.0 CHECK(starting_skill >= 0.0 AND starting_skill <= 100.0),
    tyre_warming REAL NOT NULL DEFAULT 50.0 CHECK(tyre_warming >= 0.0 AND tyre_warming <= 100.0),
    energy_management REAL NOT NULL DEFAULT 50.0 CHECK(energy_management >= 0.0 AND energy_management <= 100.0),
    wet_weather_skill REAL NOT NULL DEFAULT 50.0 CHECK(wet_weather_skill >= 0.0 AND wet_weather_skill <= 100.0),
    night_driving REAL NOT NULL DEFAULT 50.0 CHECK(night_driving >= 0.0 AND night_driving <= 100.0),
    heat_tolerance REAL NOT NULL DEFAULT 50.0 CHECK(heat_tolerance >= 0.0 AND heat_tolerance <= 100.0),
    cold_tolerance REAL NOT NULL DEFAULT 50.0 CHECK(cold_tolerance >= 0.0 AND cold_tolerance <= 100.0),
    altitude_adaptation REAL NOT NULL DEFAULT 50.0 CHECK(altitude_adaptation >= 0.0 AND altitude_adaptation <= 100.0),
    visibility_adaptation REAL NOT NULL DEFAULT 50.0 CHECK(visibility_adaptation >= 0.0 AND visibility_adaptation <= 100.0),
    surface_adaptation REAL NOT NULL DEFAULT 50.0 CHECK(surface_adaptation >= 0.0 AND surface_adaptation <= 100.0),
    media_handling REAL NOT NULL DEFAULT 50.0 CHECK(media_handling >= 0.0 AND media_handling <= 100.0),
    sponsorship_appeal REAL NOT NULL DEFAULT 50.0 CHECK(sponsorship_appeal >= 0.0 AND sponsorship_appeal <= 100.0),
    fan_engagement REAL NOT NULL DEFAULT 50.0 CHECK(fan_engagement >= 0.0 AND fan_engagement <= 100.0),
    team_player REAL NOT NULL DEFAULT 50.0 CHECK(team_player >= 0.0 AND team_player <= 100.0),
    leadership REAL NOT NULL DEFAULT 50.0 CHECK(leadership >= 0.0 AND leadership <= 100.0),
    professionalism REAL NOT NULL DEFAULT 50.0 CHECK(professionalism >= 0.0 AND professionalism <= 100.0),
    career_wins INTEGER DEFAULT 0,
    career_podiums INTEGER DEFAULT 0,
    career_points INTEGER DEFAULT 0,
    biography TEXT DEFAULT '',
    current_team_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_team_id) REFERENCES teams (id)
);
"""
