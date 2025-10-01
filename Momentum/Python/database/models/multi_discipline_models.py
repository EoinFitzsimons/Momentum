"""
Momentum Motorsport Simulation - Multi-Discipline Models

This module extends the base data models to support all 7 racing disciplines:
- Single Seater: Open-wheel formula racing with aerodynamic focus
- Production/Touring: Production-based touring car racing
- Rally/Stage: Point-to-point rally racing on varied surfaces
- Urban/Street: Street circuits and urban racing environments
- Drag/Acceleration: Straight-line acceleration racing
- Sprint/Rallycross: Mixed-surface sprint racing
- Endurance: Long-distance multi-class racing

Each discipline has unique characteristics, vehicle development paths,
and specific driver skill requirements.

Authors: Final Year Project - Computer Science
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class RacingDiscipline(Enum):
    """Supported racing disciplines matching the actual implementation"""
    SINGLE_SEATER = "SINGLE_SEATER"
    PRODUCTION_TOURING = "PRODUCTION_TOURING"
    RALLY_STAGE = "RALLY_STAGE"
    URBAN_STREET = "URBAN_STREET"
    DRAG_ACCELERATION = "DRAG_ACCELERATION"
    SPRINT_RALLYCROSS = "SPRINT_RALLYCROSS"
    ENDURANCE = "ENDURANCE"


@dataclass
class Vehicle:
    """
    Vehicle Development Model - Multi-Discipline Car System
    
    Represents the technical package for each of the 7 racing disciplines with
    component-based development system. Teams invest budget into different areas 
    to improve competitive performance across:
    - Single Seater, Production/Touring, Rally/Stage, Urban/Street,
    - Drag/Acceleration, Sprint/Rallycross, Endurance
    
    All vehicles are cars (no motorcycles) with discipline-specific characteristics.
    """
    # ===== CORE IDENTIFICATION =====
    id: int                                   # Unique vehicle identifier
    team_id: int                             # Owner team (FK to teams.id)
    discipline: str                          # RacingDiscipline enum value
    season_year: int                         # Season this car competes in
    
    # ===== OVERALL PERFORMANCE RATING =====
    overall_performance: float = 0.5         # Combined performance rating (0.0-1.0)
    
    # ===== UNIVERSAL COMPONENTS (all disciplines) =====
    # Core systems that every racing car needs
    aerodynamics: float = 0.5                # Downforce, drag, and airflow management
    chassis: float = 0.5                     # Structural integrity, weight, and rigidity
    electronics: float = 0.5                 # Control systems, telemetry, and data logging
    reliability: float = 0.5                 # Component durability and failure resistance
    safety_systems: float = 0.5              # Roll cages, impact protection, fire suppression
    
    # ===== POWERTRAIN SYSTEMS =====
    # Engine/motor configurations vary by discipline
    engine_power: Optional[float] = None     # ICE power (Single Seater, Production, Rally, Drag, Rallycross, Endurance)
    electric_powertrain: Optional[float] = None  # Electric motor systems (Urban/Street, hybrid systems)
    hybrid_systems: Optional[float] = None   # Combined ICE+electric (Endurance, some Single Seater)
    
    # ===== MECHANICAL SYSTEMS =====
    # Physical components that affect handling and performance
    suspension: float = 0.5                  # Suspension setup and tuning (critical for Rally/Rallycross)
    brakes: float = 0.5                      # Braking performance and cooling (especially Endurance)
    transmission: float = 0.5                # Gearbox and drivetrain efficiency
    tires_compound: float = 0.5              # Tire selection and performance optimization
    
    # ===== DISCIPLINE-SPECIFIC SPECIALIZATIONS =====
    # Components that are particularly important for certain disciplines
    
    # Single Seater specific
    single_seater_aero_package: Optional[float] = None    # Advanced wings, floors, diffusers
    
    # Production/Touring specific  
    touring_car_setup: Optional[float] = None             # Close-racing optimization
    
    # Rally/Stage specific
    rally_durability: Optional[float] = None              # Off-road protection and robustness
    all_terrain_capability: Optional[float] = None        # Multi-surface performance
    
    # Urban/Street specific
    energy_management: Optional[float] = None             # Electric efficiency and regeneration
    street_adaptability: Optional[float] = None           # City circuit optimization
    
    # Drag/Acceleration specific
    launch_systems: Optional[float] = None                # Launch control and traction management
    straight_line_optimization: Optional[float] = None    # Maximum acceleration focus
    
    # Sprint/Rallycross specific
    mixed_surface_setup: Optional[float] = None           # Tarmac/gravel versatility
    quick_adaptation: Optional[float] = None              # Rapid setup changes
    
    # Endurance specific
    long_distance_reliability: Optional[float] = None     # Extended operation capability
    pit_stop_efficiency: Optional[float] = None           # Quick service optimization
    driver_comfort: Optional[float] = None                # Ergonomics for long stints
    
    # ===== SUPPLIER RELATIONSHIPS =====
    # Track which components are in-house vs supplier-provided
    engine_supplier_id: Optional[int] = None             # Engine supplier (None = in-house)
    tire_supplier_id: Optional[int] = None               # Tire supplier (None = in-house)
    brake_supplier_id: Optional[int] = None              # Brake supplier (None = in-house)
    transmission_supplier_id: Optional[int] = None       # Transmission supplier (None = in-house)
    suspension_supplier_id: Optional[int] = None         # Suspension supplier (None = in-house)
    electronics_supplier_id: Optional[int] = None        # Electronics supplier (None = in-house)
    aerodynamics_supplier_id: Optional[int] = None       # Aero supplier (None = in-house)
    fuel_supplier_id: Optional[int] = None               # Fuel supplier (None = in-house)
    specialty_supplier_id: Optional[int] = None          # Specialty components (nitrous, etc.)
    
    # ===== DEVELOPMENT STRATEGY =====
    development_philosophy: str = "balanced"             # "make", "buy", "balanced"
    in_house_components: Optional[List[str]] = None      # Components developed internally
    outsourced_components: Optional[List[str]] = None    # Components from suppliers
    
    # ===== DEVELOPMENT AND BUDGET =====
    development_budget_spent: float = 0.0                 # Budget invested this season
    supplier_budget_spent: float = 0.0                    # Budget spent on supplier contracts
    development_focus: Optional[Dict[str, float]] = None  # Component -> investment percentage
    upgrade_potential: float = 0.5                        # Remaining development capacity
    
    # ===== PERFORMANCE TRACKING =====
    performance_history: Optional[List[Dict]] = None      # Race-by-race performance data
    competitive_ranking: int = 1                          # Position in field (1=best, higher=worse)
    development_rate: float = 0.1                         # Speed of improvement per season
    supplier_performance_bonus: float = 0.0               # Performance boost from suppliers
    
    def get_total_annual_cost(self) -> float:
        """Calculate total annual cost including development and suppliers"""
        return self.development_budget_spent + self.supplier_budget_spent
    
    def is_component_in_house(self, component_type: str) -> bool:
        """Check if a component is developed in-house"""
        supplier_map = {
            "engine": self.engine_supplier_id,
            "tires": self.tire_supplier_id,
            "brakes": self.brake_supplier_id,
            "transmission": self.transmission_supplier_id,
            "suspension": self.suspension_supplier_id,
            "electronics": self.electronics_supplier_id,
            "aerodynamics": self.aerodynamics_supplier_id,
            "fuel": self.fuel_supplier_id,
            "specialty": self.specialty_supplier_id
        }
        
        return supplier_map.get(component_type) is None
    
    def get_supplier_dependencies(self) -> List[int]:
        """Get list of all supplier IDs this vehicle depends on"""
        supplier_ids = [
            self.engine_supplier_id, self.tire_supplier_id, self.brake_supplier_id,
            self.transmission_supplier_id, self.suspension_supplier_id, 
            self.electronics_supplier_id, self.aerodynamics_supplier_id,
            self.fuel_supplier_id, self.specialty_supplier_id
        ]
        
        return [sid for sid in supplier_ids if sid is not None]


@dataclass
class MultiDisciplineDriver:
    """
    Extended Driver Entity Model - Comprehensive Multi-Discipline Driver System
    
    Represents individual racing drivers with 50+ attributes covering all aspects
    of motorsport performance. This class extends the base Driver model to support
    multi-discipline competition across all 7 racing categories. Drivers can compete 
    across disciplines with varying levels of aptitude and preference, just like 
    real-world drivers who may excel in one area but can compete in multiple categories.
    
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
    
    # ===== MULTI-DISCIPLINE PARTICIPATION (required fields) =====
    active_disciplines: List[str]             # Currently competing disciplines
    primary_discipline: str                   # Main focus/strongest discipline
    
    # ===== CORE IDENTIFICATION (with defaults) =====
    age: int = 25                             # Current age (affects performance curves)
    biography: str = ""                       # Driver background and career history
    career_phase: str = "active"              # rookie, rising, peak, veteran, declining, retired
    preferred_discipline: str = "SINGLE_SEATER" # Primary discipline preference
    
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
    # Natural aptitude for different racing categories - matching our 7 disciplines
    single_seater_aptitude: float = 50.0      # Single Seater (Formula) racing preference
    production_touring_aptitude: float = 50.0 # Production/Touring car racing
    rally_stage_aptitude: float = 50.0        # Rally/Stage racing and off-road
    urban_street_aptitude: float = 50.0       # Urban/Street racing and city circuits
    drag_acceleration_aptitude: float = 50.0  # Drag/Acceleration racing specialization
    sprint_rallycross_aptitude: float = 50.0  # Sprint/Rallycross mixed-surface racing
    endurance_aptitude: float = 50.0          # Endurance racing specialization
    
    # ===== RACE CRAFT & STRATEGY (8 attributes) =====
    # Tactical and strategic racing abilities
    race_strategy: float = 50.0               # Understanding race strategy and timing
    pit_stop_coordination: float = 50.0       # Working with pit crew effectively
    traffic_management: float = 50.0          # Navigating through slower cars
    tire_strategy: float = 50.0               # Strategic tire choice and timing
    fuel_strategy: float = 50.0               # Strategic fuel management decisions
    safety_car_awareness: float = 50.0        # Maximizing safety car opportunities
    qualifying_optimization: float = 50.0     # Extracting maximum single-lap pace
    championship_thinking: float = 50.0       # Long-term championship management
    
    # ===== ENVIRONMENTAL ADAPTATION (7 attributes) =====
    # Adapting to different conditions and circumstances
    wet_weather_skill: float = 50.0           # Performance in rain and wet conditions
    night_racing_skill: float = 50.0          # Racing in low visibility conditions
    temperature_adaptation: float = 50.0      # Handling hot/cold temperature extremes
    altitude_adaptation: float = 50.0          # Performance at high altitude tracks
    surface_adaptation: float = 50.0          # Adjusting to different track surfaces
    car_adaptation: float = 50.0              # Quickly adapting to new/different cars
    track_learning: float = 50.0              # Speed of learning new circuits
    
    # ===== PERSONAL & SOCIAL TRAITS (6 attributes) =====
    # Personality and interpersonal characteristics
    media_presence: float = 50.0              # Charisma and marketing appeal
    team_cooperation: float = 50.0            # Working effectively within team
    leadership_ability: float = 50.0          # Natural leadership and influence
    risk_appetite: float = 50.0               # Willingness to take calculated risks
    ego_management: float = 50.0              # Handling success and criticism
    commercial_appeal: float = 50.0           # Sponsor and fan attraction
    
    # ===== DISCIPLINE-SPECIFIC SPECIALIZED SKILLS =====
    # Additional skills that only apply to certain disciplines
    energy_management: float = 50.0           # Electric powertrain optimization (Urban/Street)
    stint_management: float = 50.0            # Long-stint performance management (Endurance)
    
    # ===== CAREER STATISTICS & PROGRESSION =====
    career_wins: int = 0                      # Total race victories across all disciplines
    career_podiums: int = 0                   # Total podium finishes (top 3)
    career_points: int = 0                    # Cumulative championship points
    career_starts: int = 0                    # Total race entries
    career_dnf: int = 0                       # Did not finish count
    seasons_active: int = 0                   # Number of seasons competed
    
    # Discipline-specific career stats
    single_seater_wins: int = 0               # Wins in Single Seater categories
    production_touring_wins: int = 0          # Wins in Production/Touring car racing
    rally_stage_wins: int = 0                 # Wins in Rally/Stage racing
    urban_street_wins: int = 0                # Wins in Urban/Street racing
    drag_acceleration_wins: int = 0           # Wins in Drag/Acceleration racing
    sprint_rallycross_wins: int = 0           # Wins in Sprint/Rallycross racing
    endurance_wins: int = 0                   # Wins in Endurance racing
    
    # ===== MULTI-DISCIPLINE CONTRACT & TEAM INFORMATION =====
    current_contracts: Optional[Dict[str, int]] = None    # discipline -> team_id
    contract_values: Optional[Dict[str, float]] = None    # discipline -> annual_salary
    contract_lengths: Optional[Dict[str, int]] = None     # discipline -> remaining_years
    
    # ===== PERFORMANCE TRENDS AND DEVELOPMENT =====
    form_trend: str = "stable"                # improving, stable, declining
    peak_performance_age: int = 28            # Age at which driver peaks
    retirement_age: int = 40                  # Expected retirement age
    learning_rate: float = 50.0               # Speed of attribute improvement
    
    # ===== SPECIAL ACHIEVEMENTS =====
    championship_titles: int = 0              # Total championship victories across disciplines
    championship_titles_by_discipline: Optional[Dict[str, int]] = None
    rookie_of_year_awards: int = 0            # Rookie season recognition
    fastest_laps: int = 0                     # Career fastest lap awards
    pole_positions: int = 0                   # Career pole position count
    
    # ===== AI PERSONALITY AND DECISION-MAKING =====
    team_loyalty: float = 50.0                # Tendency to stay with teams
    ambition_level: float = 50.0              # Drive to move up disciplines/tiers
    discipline_switching_tendency: float = 50.0 # Willingness to try new disciplines
    
    def get_discipline_rating(self, discipline: str) -> float:
        """
        Calculate overall performance rating for a specific discipline
        
        This method provides a comprehensive evaluation of how well this driver
        would perform in the given discipline, considering their aptitude for
        that discipline as well as their overall driving abilities.
        
        Args:
            discipline: The racing discipline to evaluate
                      ("SINGLE_SEATER", "PRODUCTION_TOURING", "RALLY_STAGE", 
                       "URBAN_STREET", "DRAG_ACCELERATION", "SPRINT_RALLYCROSS", "ENDURANCE")
        
        Returns:
            Overall performance rating (0-100 scale)
        """
        # Get discipline-specific aptitude
        aptitude_map = {
            "SINGLE_SEATER": self.single_seater_aptitude,
            "PRODUCTION_TOURING": self.production_touring_aptitude,
            "RALLY_STAGE": self.rally_stage_aptitude,
            "URBAN_STREET": self.urban_street_aptitude,
            "DRAG_ACCELERATION": self.drag_acceleration_aptitude,
            "SPRINT_RALLYCROSS": self.sprint_rallycross_aptitude,
            "ENDURANCE": self.endurance_aptitude
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
    
    def get_discipline_career_stats(self, discipline: str) -> Dict[str, int]:
        """
        Get career statistics for a specific discipline
        
        Args:
            discipline: The racing discipline to get stats for
        
        Returns:
            Dictionary containing wins, podiums, points, and starts for the discipline
        """
        wins_map = {
            "SINGLE_SEATER": self.single_seater_wins,
            "PRODUCTION_TOURING": self.production_touring_wins,
            "RALLY_STAGE": self.rally_stage_wins,
            "URBAN_STREET": self.urban_street_wins,
            "DRAG_ACCELERATION": self.drag_acceleration_wins,
            "SPRINT_RALLYCROSS": self.sprint_rallycross_wins,
            "ENDURANCE": self.endurance_wins
        }
        
        wins = wins_map.get(discipline, 0)
        
        # Calculate approximate podiums and starts based on wins
        # These would normally be tracked separately in a full implementation
        estimated_podiums = int(wins * 2.5)  # Assume 2.5x podiums to wins ratio
        estimated_starts = int(wins * 15)    # Assume 15x starts to wins ratio
        estimated_points = int(wins * 25)    # Rough points estimate
        
        return {
            "wins": wins,
            "podiums": estimated_podiums,
            "points": estimated_points,
            "starts": estimated_starts
        }


@dataclass  
class MultiDisciplineTeam:
    """
    Extended Team model supporting multiple racing disciplines
    
    Teams can participate in multiple championships simultaneously,
    with budget allocation and technical expertise varying by discipline.
    """
    # Base team information (required fields first)
    id: int
    name: str
    nationality: str
    founded_year: int
    headquarters: str
    team_principal: str
    biography: str
    founding_story: str
    
    # Multi-discipline participation (required fields)
    active_disciplines: List[str]   # Currently competing disciplines
    primary_discipline: str         # Main focus/investment
    total_annual_budget: float      # Total across all disciplines
    
    # Optional multi-discipline fields
    discipline_history: Optional[Dict[str, int]] = None  # discipline -> years_participating
    budget_allocation: Optional[Dict[str, float]] = None  # discipline -> budget_percentage
    
    # Organizational capabilities
    management_quality: float = 0.6
    financial_stability: float = 0.7
    
    # Technical expertise per discipline (affects development efficiency)
    technical_expertise: Optional[Dict[str, float]] = None  # discipline -> expertise_level
    
    # Facilities and infrastructure
    wind_tunnel_quality: float = 0.5        # Aerodynamic development
    simulator_quality: float = 0.5          # Driver training and setup
    manufacturing_capability: float = 0.5    # In-house vs outsourced parts
    data_analysis_capability: float = 0.5    # Telemetry and performance analysis
    
    # Discipline-specific facilities
    rally_test_stages: Optional[float] = None     # Rally development capability
    endurance_pit_crew_quality: Optional[float] = None  # Endurance pit stop performance
    electric_powertrain_expertise: Optional[float] = None # Electric vehicle specialisation
    
    # AI personality and strategic approach
    risk_appetite: float = 0.5
    innovation_focus: float = 0.5
    driver_development_focus: float = 0.5
    brand_marketing_focus: float = 0.5
    
    # Performance tracking
    total_wins_all_disciplines: int = 0
    total_podiums_all_disciplines: int = 0  
    championships_by_discipline: Optional[Dict[str, int]] = None
    
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
    
    # Circuit-specific
    corner_count: Optional[int] = None
    straight_length_km: Optional[float] = None
    elevation_change_m: Optional[float] = None
    
    # Rally-specific
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
    # Single Seater: Sprint races, qualifying formats
    has_sprint_races: bool = False
    qualifying_format: str = "standard"  # "standard", "knockout", "superpole"
    
    # Endurance: Multi-class racing
    racing_classes: Optional[List[str]] = None  
    
    # Rally: Stage-based scoring
    stage_points_system: bool = False
    power_stage_bonus: bool = False
    
    # Practice/qualifying structure
    practice_sessions: int = 3
    
    # Point systems (position -> points)
    points_system: Optional[Dict[int, int]] = None
    
    # Additional point scoring opportunities
    fastest_lap_points: int = 0
    pole_position_points: int = 0
    
    # Championship regulations
    minimum_races_for_points: int = 1
    dropped_rounds: int = 0  # Number of worst results dropped
    
    # Participating teams and drivers
    registered_teams: Optional[List[int]] = None  # team_ids
    registered_drivers: Optional[List[int]] = None  # driver_ids
    
    # Current standings
    team_standings: Optional[Dict[int, int]] = None  # team_id -> points
    driver_standings: Optional[Dict[int, int]] = None  # driver_id -> points


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
    # Endurance: Multi-class racing with different winners
    race_classes: Optional[List[str]] = None
    
    # Rally: Multiple stages with stage winners
    stage_results: Optional[Dict[int, Dict[int, float]]] = None  # stage_num -> {driver_id: time}
    
    # Safety and incidents
    safety_car_periods: int = 0
    red_flag_periods: int = 0
    total_incidents: int = 0


# Development progression trees for each discipline
DISCIPLINE_DEVELOPMENT_TREES = {
    "SINGLE_SEATER": {
        "aerodynamics": ["front_wing", "rear_wing", "floor", "diffuser"],
        "engine": ["power_unit", "fuel_efficiency", "reliability"],
        "chassis": ["monocoque", "weight_distribution", "suspension"],
        "electronics": ["ecu", "telemetry", "driver_aids"],
        "reliability": ["component_durability", "preventive_maintenance"]
    },
    "PRODUCTION_TOURING": {
        "aerodynamics": ["body_kit", "splitter", "rear_wing"],
        "engine": ["turbo_mapping", "exhaust_system", "cooling"],
        "chassis": ["roll_cage", "suspension_geometry", "weight_reduction"],
        "electronics": ["traction_control", "abs_tuning", "data_logging"],
        "safety": ["impact_protection", "fire_suppression"]
    },
    "RALLY_STAGE": {
        "chassis": ["suspension_travel", "underbody_protection", "roll_cage"],
        "engine": ["turbo_anti_lag", "power_delivery", "durability"],
        "transmission": ["differential_tuning", "gear_ratios"],
        "safety": ["impact_structures", "navigation_systems"],
        "durability": ["component_protection", "maintenance_intervals"]
    },
    "URBAN_STREET": {
        "electric_powertrain": ["battery_efficiency", "regen_systems", "motor_mapping"],
        "aerodynamics": ["efficiency_focus", "cooling_optimization"],
        "chassis": ["weight_optimization", "handling_balance"],
        "electronics": ["energy_management", "software_systems"],
        "safety": ["impact_protection", "visibility_systems"]
    },
    "DRAG_ACCELERATION": {
        "engine": ["nitrous_systems", "supercharging", "power_optimization"],
        "transmission": ["launch_control", "gear_ratios", "torque_converter"],
        "chassis": ["weight_transfer", "aerodynamic_drag", "safety_systems"],
        "tires": ["compound_selection", "pressure_optimization"],
        "safety": ["roll_cage", "fire_suppression", "parachute_systems"]
    },
    "SPRINT_RALLYCROSS": {
        "chassis": ["all_terrain_suspension", "ground_clearance", "durability"],
        "engine": ["power_delivery", "turbo_response", "cooling"],
        "transmission": ["all_wheel_drive", "torque_distribution"],
        "aerodynamics": ["mixed_surface_optimization", "cooling_ducts"],
        "safety": ["impact_protection", "visibility_systems"]
    },
    "ENDURANCE": {
        "aerodynamics": ["efficiency_focus", "cooling_systems", "stability"],
        "engine": ["fuel_efficiency", "durability", "hybrid_systems"],
        "chassis": ["driver_comfort", "pit_accessibility", "weight_distribution"],
        "reliability": ["component_lifecycle", "preventive_systems"],
        "strategy": ["fuel_management", "tire_strategy", "driver_rotation"]
    }
}

# Comprehensive skill requirements per discipline using the 50+ attribute system
# Each discipline has different weightings for the various driver attributes
DISCIPLINE_SKILL_WEIGHTS = {
    "SINGLE_SEATER": {
        # Core driving skills (heavily weighted)
        "raw_speed": 0.12, "consistency": 0.10, "racecraft": 0.08, "qualifying_optimization": 0.08,
        "cornering_skill": 0.07, "overtaking": 0.06, "spatial_awareness": 0.06,
        
        # Technical knowledge (important for setup)
        "setup_knowledge": 0.06, "tire_management": 0.05, "aerodynamics_understanding": 0.04,
        "data_analysis": 0.04, "fuel_management": 0.03,
        
        # Physical & mental (moderate importance)
        "concentration": 0.05, "pressure_handling": 0.05, "reaction_time": 0.04,
        "g_force_tolerance": 0.03, "multitasking": 0.03,
        
        # Strategy and environmental
        "race_strategy": 0.04, "safety_car_awareness": 0.03, "wet_weather_skill": 0.02
    },
    
    "PRODUCTION_TOURING": {
        # Racecraft and physical contact skills prioritized
        "racecraft": 0.12, "overtaking": 0.10, "defensive_driving": 0.09, "spatial_awareness": 0.08,
        "raw_speed": 0.08, "consistency": 0.07, "vehicle_control": 0.07,
        
        # Physical traits (wheel-to-wheel racing demands)
        "pressure_handling": 0.06, "reaction_time": 0.05, "concentration": 0.05,
        "adrenaline_management": 0.04, "mental_resilience": 0.04,
        
        # Technical and strategy
        "setup_knowledge": 0.05, "tire_management": 0.04, "race_strategy": 0.04,
        "traffic_management": 0.03, "mechanical_sympathy": 0.03
    },
    
    "RALLY_STAGE": {
        # Adaptability and surface skills critical
        "surface_adaptation": 0.15, "car_adaptation": 0.10, "track_learning": 0.09,
        "raw_speed": 0.08, "vehicle_control": 0.08, "spatial_awareness": 0.07,
        
        # Environmental conditions (rally-specific)
        "wet_weather_skill": 0.06, "temperature_adaptation": 0.05, "concentration": 0.05,
        
        # Technical knowledge
        "suspension_feel": 0.06, "setup_knowledge": 0.05, "mechanical_sympathy": 0.05,
        
        # Mental strength for risk management
        "mental_resilience": 0.04, "risk_appetite": 0.03, "pressure_handling": 0.04
    },
    
    "URBAN_STREET": {
        # Adaptation and energy management for electric/street racing
        "car_adaptation": 0.10, "track_learning": 0.09, "energy_management": 0.08,
        "raw_speed": 0.08, "consistency": 0.08, "racecraft": 0.07,
        
        # Technical knowledge for electric systems
        "engine_management": 0.07, "data_analysis": 0.06, "setup_knowledge": 0.06,
        "fuel_management": 0.05, # (Energy management in electric)
        
        # Environmental and strategic
        "traffic_management": 0.06, "qualifying_optimization": 0.05, "race_strategy": 0.05,
        "spatial_awareness": 0.05, "pressure_handling": 0.04, "concentration": 0.04
    },
    
    "DRAG_ACCELERATION": {
        # Launch and acceleration technique paramount
        "acceleration_control": 0.20, "reaction_time": 0.15, "raw_speed": 0.12,
        "consistency": 0.10, "qualifying_optimization": 0.08,
        
        # Technical precision
        "engine_management": 0.08, "data_analysis": 0.06, "setup_knowledge": 0.05,
        
        # Mental focus (short, intense races)
        "concentration": 0.06, "pressure_handling": 0.05, "adrenaline_management": 0.05
    },
    
    "SPRINT_RALLYCROSS": {
        # Mixed surface and adaptability
        "surface_adaptation": 0.12, "car_adaptation": 0.10, "racecraft": 0.09,
        "raw_speed": 0.08, "vehicle_control": 0.08, "overtaking": 0.07,
        
        # Physical demands of mixed racing
        "reaction_time": 0.06, "spatial_awareness": 0.06, "concentration": 0.05,
        "g_force_tolerance": 0.04, "coordination": 0.04,
        
        # Technical and environmental
        "setup_knowledge": 0.05, "track_learning": 0.05, "wet_weather_skill": 0.04,
        "tire_management": 0.04, "suspension_feel": 0.03
    },
    
    "ENDURANCE": {
        # Consistency and stamina prioritized
        "consistency": 0.15, "physical_fitness": 0.12, "concentration": 0.10,
        "mental_resilience": 0.08, "stint_management": 0.08, # Custom endurance skill
        
        # Technical management over long distances
        "tire_management": 0.08, "fuel_management": 0.07, "mechanical_sympathy": 0.06,
        "setup_knowledge": 0.05, "engine_management": 0.05,
        
        # Strategic thinking
        "race_strategy": 0.06, "championship_thinking": 0.05, "pit_stop_coordination": 0.05
    }
}

__all__ = [
    'RacingDiscipline', 'Vehicle', 'MultiDisciplineDriver', 'MultiDisciplineTeam', 
    'Track', 'Championship', 'Race', 'DISCIPLINE_DEVELOPMENT_TREES', 
    'DISCIPLINE_SKILL_WEIGHTS'
]