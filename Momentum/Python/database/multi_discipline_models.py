"""
Momentum Motorsport Simulation - Multi-Discipline Models

This module extends the base data models to support all 7 racing disciplines:
- Formula 1: Premier open-wheel racing
- Formula 2: Development series for F1
- Formula 3: Entry-level formula racing  
- WEC (World Endurance Championship): Multi-class endurance racing
- WRC (World Rally Championship): Stage-based rally racing
- MotoGP: Premier motorcycle racing
- Formula E: Electric open-wheel racing

Each discipline has unique characteristics, vehicle development trees,
and specific driver skill requirements.

Authors: Final Year Project - Computer Science
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class RacingDiscipline(Enum):
    """Supported racing disciplines in the simulation"""
    FORMULA_1 = "F1"
    FORMULA_2 = "F2" 
    FORMULA_3 = "F3"
    WEC = "WEC"
    WRC = "WRC"
    MOTOGP = "MotoGP"
    FORMULA_E = "FormulaE"


@dataclass
class Vehicle:
    """
    Vehicle/Motorcycle Development Model
    
    Represents the technical package for each discipline with component-based
    development system. Teams invest budget into different areas to improve
    competitive performance.
    """
    id: int
    team_id: int
    discipline: str  # RacingDiscipline value
    season_year: int
    
    # Core vehicle performance (0.0-1.0 normalized)
    overall_performance: float = 0.5
    
    # Universal components (all disciplines)
    aerodynamics: float = 0.5      # Downforce and drag efficiency
    chassis: float = 0.5           # Structural integrity and weight
    electronics: float = 0.5       # Control systems and telemetry
    reliability: float = 0.5       # Component durability
    
    # Discipline-specific components
    engine_power: Optional[float] = None      # ICE disciplines (F1, F2, F3, WEC, WRC)
    electric_powertrain: Optional[float] = None  # Formula E, hybrid systems
    suspension: Optional[float] = None        # Critical for WRC, important for circuits
    brakes: Optional[float] = None           # Especially important for WEC
    transmission: Optional[float] = None      # Manual for WRC, advanced for F1
    
    # MotoGP specific
    bike_balance: Optional[float] = None      # Weight distribution and handling
    engine_braking: Optional[float] = None    # Engine characteristics
    tire_management: Optional[float] = None   # Tire wear optimization
    
    # Development budget allocation this season
    development_budget_spent: float = 0.0
    development_focus: Dict[str, float] = None  # Component -> investment percentage
    
    # Performance history tracking
    performance_history: List[Dict] = None  # Race-by-race performance data


@dataclass
class MultiDisciplineDriver:
    """
    Extended Driver model supporting all 7 racing disciplines
    
    Drivers can compete across multiple disciplines with varying skill levels.
    Some drivers excel in specific areas (e.g., rally vs circuit racing).
    """
    # Base driver information (inherited from original Driver model)
    id: int
    name: str
    nationality: str
    birth_date: str
    biography: str
    career_phase: str  # rookie, active, veteran, retired
    
    # Multi-discipline participation
    active_disciplines: List[str]  # Currently competing disciplines
    primary_discipline: str        # Main focus/strongest discipline
    
    # Base attributes (apply to all disciplines)
    base_skill: float = 0.5
    base_consistency: float = 0.5
    base_racecraft: float = 0.5
    base_adaptability: float = 0.5
    
    # Physical attributes (more important for certain disciplines)
    fitness_level: float = 0.5     # Endurance for WEC, physicality for WRC
    reaction_time: float = 0.5     # Critical for MotoGP and F1
    mental_strength: float = 0.5   # Pressure handling
    technical_feedback: float = 0.5 # Vehicle development input
    
    # Discipline-specific skill modifiers (multiplier on base skills)
    f1_skill_modifier: float = 1.0
    f2_skill_modifier: float = 1.0
    f3_skill_modifier: float = 1.0
    wec_skill_modifier: float = 1.0     # Endurance racing specialization
    wrc_skill_modifier: float = 1.0     # Rally/off-road specialization  
    motogp_skill_modifier: float = 1.0  # Motorcycle specialization
    formulae_skill_modifier: float = 1.0 # Electric racing adaptation
    
    # Specialized skills for specific disciplines
    # Rally-specific
    pace_note_reading: Optional[float] = None    # WRC co-driver communication
    surface_adaptation: Optional[float] = None   # Gravel/snow/tarmac adaptation
    
    # Endurance-specific  
    stint_management: Optional[float] = None     # WEC long-stint performance
    night_racing: Optional[float] = None         # Low visibility performance
    
    # MotoGP-specific
    bike_feel: Optional[float] = None           # Motorcycle handling intuition
    lean_angle_confidence: Optional[float] = None # Cornering aggression
    
    # Career statistics per discipline
    discipline_stats: Dict[str, Dict[str, int]] = None  # discipline -> {wins, podiums, points, starts}
    
    # Contract and team information
    current_contracts: Dict[str, int] = None    # discipline -> team_id
    contract_values: Dict[str, float] = None    # discipline -> annual_salary
    
    # AI personality factors
    risk_tolerance: float = 0.5
    team_loyalty: float = 0.5
    media_savvy: float = 0.5
    ambition_level: float = 0.5  # Drive to move up disciplines (F3->F2->F1)


@dataclass  
class MultiDisciplineTeam:
    """
    Extended Team model supporting multiple racing disciplines
    
    Teams can participate in multiple championships simultaneously,
    with budget allocation and technical expertise varying by discipline.
    """
    # Base team information
    id: int
    name: str
    nationality: str
    founded_year: int
    headquarters: str
    team_principal: str
    biography: str
    founding_story: str
    
    # Multi-discipline participation
    active_disciplines: List[str]   # Currently competing disciplines
    primary_discipline: str         # Main focus/investment
    discipline_history: Dict[str, int] = None  # discipline -> years_participating
    
    # Financial structure
    total_annual_budget: float      # Total across all disciplines
    budget_allocation: Dict[str, float] = None  # discipline -> budget_percentage
    
    # Organizational capabilities
    management_quality: float = 0.6
    financial_stability: float = 0.7
    
    # Technical expertise per discipline (affects development efficiency)
    technical_expertise: Dict[str, float] = None  # discipline -> expertise_level
    
    # Facilities and infrastructure
    wind_tunnel_quality: float = 0.5        # Aerodynamic development
    simulator_quality: float = 0.5          # Driver training and setup
    manufacturing_capability: float = 0.5    # In-house vs outsourced parts
    data_analysis_capability: float = 0.5    # Telemetry and performance analysis
    
    # Discipline-specific facilities
    rally_test_stages: Optional[float] = None     # WRC development capability
    endurance_pit_crew_quality: Optional[float] = None  # WEC pit stop performance
    motogp_chassis_expertise: Optional[float] = None     # MotoGP bike development
    electric_powertrain_expertise: Optional[float] = None # Formula E specialization
    
    # AI personality and strategic approach
    risk_appetite: float = 0.5
    innovation_focus: float = 0.5
    driver_development_focus: float = 0.5
    brand_marketing_focus: float = 0.5
    
    # Performance tracking
    total_wins_all_disciplines: int = 0
    total_podiums_all_disciplines: int = 0  
    championships_by_discipline: Dict[str, int] = None
    
    # Strategic preferences
    preferred_driver_age_range: tuple = (20, 35)  # (min_age, max_age)
    cross_discipline_strategy: str = "focused"     # "focused", "diversified", "developmental"


@dataclass
class Track:
    """
    Enhanced Track model supporting all racing disciplines
    
    Different disciplines use different track types with unique characteristics
    that affect vehicle setup and driver skill requirements.
    """
    id: int
    name: str
    location: str
    country: str
    discipline: str  # Which racing discipline uses this track
    
    # Physical characteristics
    length_km: float
    
    # Discipline-specific track types
    track_type: str  # "circuit", "street", "rally_stage", "oval"
    surface_type: str = "tarmac"  # "tarmac", "gravel", "snow", "mixed"
    
    # Circuit-specific (F1, F2, F3, WEC, Formula E)
    corner_count: Optional[int] = None
    straight_length_km: Optional[float] = None
    elevation_change_m: Optional[float] = None
    
    # Rally-specific (WRC)
    stage_type: Optional[str] = None  # "forest", "mountain", "coastal"
    average_width_m: Optional[float] = None
    weather_variability: Optional[float] = None  # How much weather affects this stage
    
    # Track characteristics affecting strategy (0.0-1.0)
    overtaking_difficulty: float = 0.5
    tire_wear_factor: float = 0.5
    fuel_consumption_factor: float = 0.5
    crash_risk: float = 0.3
    
    # Weather impact factors
    rain_likelihood: float = 0.2
    temperature_variance: float = 0.3
    wind_factor: float = 0.1


@dataclass
class Championship:
    """
    Enhanced Championship model for multi-discipline series management
    
    Each discipline has its own championship structure with unique rules,
    point systems, and seasonal formats.
    """
    id: int
    name: str
    discipline: str
    season_year: int
    
    # Championship structure
    total_rounds: int
    current_round: int = 0
    
    # Discipline-specific formats
    # F1/F2/F3: Sprint races, qualifying formats
    has_sprint_races: bool = False
    qualifying_format: str = "standard"  # "standard", "knockout", "superpole"
    
    # WEC: Multi-class racing
    racing_classes: List[str] = None  # ["LMP1", "LMP2", "GTE-Pro", "GTE-Am"]
    
    # WRC: Stage-based scoring
    stage_points_system: bool = False
    power_stage_bonus: bool = False
    
    # MotoGP: Practice/qualifying structure
    practice_sessions: int = 3
    
    # Point systems (position -> points)
    points_system: Dict[int, int] = None
    
    # Additional point scoring opportunities
    fastest_lap_points: int = 0
    pole_position_points: int = 0
    
    # Championship regulations
    minimum_races_for_points: int = 1
    dropped_rounds: int = 0  # Number of worst results dropped
    
    # Participating teams and drivers
    registered_teams: List[int] = None  # team_ids
    registered_drivers: List[int] = None  # driver_ids
    
    # Current standings
    team_standings: Dict[int, int] = None  # team_id -> points
    driver_standings: Dict[int, int] = None  # driver_id -> points


@dataclass
class Race:
    """
    Enhanced Race model supporting all discipline formats
    
    Different disciplines have vastly different race formats, from single
    races (F1) to multi-day events (WRC) to endurance races (WEC).
    """
    id: int
    championship_id: int
    track_id: int
    race_name: str
    race_date: str
    
    # Race format (discipline-dependent)
    race_format: str  # "grand_prix", "sprint", "endurance", "rally", "time_trial"
    
    # Duration/distance
    scheduled_distance_km: Optional[float] = None  # Circuit races
    scheduled_duration_hours: Optional[float] = None  # Endurance races
    total_stages: Optional[int] = None  # Rally events
    
    # Weather and conditions
    weather_conditions: str = "dry"  # "dry", "wet", "mixed"
    temperature_celsius: float = 20.0
    wind_speed_kph: float = 5.0
    
    # Track conditions (especially important for WRC)
    track_condition: str = "optimal"  # "optimal", "slippery", "rough", "muddy"
    grip_level: float = 1.0  # 0.0-1.0 multiplier on normal grip
    
    # Race status
    status: str = "scheduled"  # "scheduled", "practice", "qualifying", "racing", "finished"
    
    # Session types for the weekend
    has_practice: bool = True
    has_qualifying: bool = True
    has_warmup: bool = False
    
    # Discipline-specific features
    # WEC: Multi-class racing with different winners
    race_classes: List[str] = None
    
    # WRC: Multiple stages with stage winners
    stage_results: Dict[int, Dict[int, float]] = None  # stage_num -> {driver_id: time}
    
    # Safety and incidents
    safety_car_periods: int = 0
    red_flag_periods: int = 0
    total_incidents: int = 0


# Development progression trees for each discipline
DISCIPLINE_DEVELOPMENT_TREES = {
    "F1": {
        "aerodynamics": ["front_wing", "rear_wing", "floor", "sidepods"],
        "engine": ["power_unit", "ers_system", "fuel_efficiency"],
        "chassis": ["monocoque", "weight_distribution", "stiffness"],
        "electronics": ["ecu", "sensors", "data_logging"],
        "reliability": ["component_durability", "preventive_maintenance"]
    },
    "F2": {
        "aerodynamics": ["wing_optimization", "drag_reduction"],
        "engine": ["power_mapping", "reliability_tuning"],
        "chassis": ["setup_optimization", "weight_reduction"],
        "electronics": ["basic_telemetry", "driver_aids"]
    },
    "F3": {
        "aerodynamics": ["basic_wing_tuning"],
        "chassis": ["setup_basics", "handling_balance"],
        "electronics": ["standard_systems"]
    },
    "WEC": {
        "aerodynamics": ["endurance_efficiency", "cooling_ducts"],
        "engine": ["fuel_efficiency", "hybrid_systems", "durability"],
        "chassis": ["driver_comfort", "pit_stop_optimization"],
        "reliability": ["24h_endurance", "component_lifecycle"]
    },
    "WRC": {
        "chassis": ["suspension_travel", "underbody_protection", "weight_distribution"],
        "engine": ["turbo_mapping", "anti_lag_system"],
        "transmission": ["differential_tuning", "gear_ratios"],
        "safety": ["roll_cage", "fire_suppression"]
    },
    "MotoGP": {
        "engine": ["power_delivery", "engine_braking"],
        "chassis": ["frame_geometry", "swingarm_design"],
        "electronics": ["traction_control", "wheelie_control", "engine_mapping"],
        "aerodynamics": ["winglets", "fairing_design"]
    },
    "FormulaE": {
        "electric_powertrain": ["battery_efficiency", "motor_power", "regen_systems"],
        "aerodynamics": ["efficiency_focus", "cooling_optimization"],
        "chassis": ["weight_optimization", "driver_ergonomics"],
        "electronics": ["energy_management", "software_optimization"]
    }
}

# Skill requirements per discipline (which driver attributes are most important)
DISCIPLINE_SKILL_WEIGHTS = {
    "F1": {"skill": 0.35, "consistency": 0.25, "racecraft": 0.25, "adaptability": 0.15},
    "F2": {"skill": 0.30, "consistency": 0.30, "racecraft": 0.25, "adaptability": 0.15},
    "F3": {"skill": 0.25, "consistency": 0.35, "racecraft": 0.20, "adaptability": 0.20},
    "WEC": {"consistency": 0.40, "skill": 0.25, "adaptability": 0.20, "racecraft": 0.15},
    "WRC": {"adaptability": 0.35, "skill": 0.30, "racecraft": 0.20, "consistency": 0.15},
    "MotoGP": {"skill": 0.40, "racecraft": 0.25, "consistency": 0.20, "adaptability": 0.15},
    "FormulaE": {"adaptability": 0.30, "skill": 0.25, "consistency": 0.25, "racecraft": 0.20}
}

__all__ = [
    'RacingDiscipline', 'Vehicle', 'MultiDisciplineDriver', 'MultiDisciplineTeam', 
    'Track', 'Championship', 'Race', 'DISCIPLINE_DEVELOPMENT_TREES', 
    'DISCIPLINE_SKILL_WEIGHTS'
]