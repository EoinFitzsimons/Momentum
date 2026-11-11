# Configuration settings for Momentum simulation
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# NAME GENERATION CONFIGURATION
# ============================================================================

# NameAPI Service Configuration
NAMEAPI_KEY = os.getenv("NAMEAPI_KEY")
NAMEAPI_RATE_LIMIT = float(os.getenv("NAMEAPI_RATE_LIMIT", "1.0"))
NAMEAPI_MAX_RETRIES = int(os.getenv("NAMEAPI_MAX_RETRIES", "3"))
USE_NAMEAPI_PRIMARY = os.getenv("USE_NAMEAPI_PRIMARY", "true").lower() == "true"
ENABLE_FALLBACK = os.getenv("ENABLE_FALLBACK", "true").lower() == "true"
NAMEAPI_CACHE_SIZE = int(os.getenv("NAMEAPI_CACHE_SIZE", "1000"))

# ParaNames Configuration
PARANAMES_TSV_PATH = os.getenv("PARANAMES_TSV_PATH", "data/paranames.tsv")
PARANAMES_DB_PATH = os.getenv("PARANAMES_DB_PATH", "data/paranames.db")

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_FILENAME = "momentum.db"

# Database Configuration
if getattr(sys, "frozen", False):
    _bundled_database_path = (
        Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        / "database"
        / DATABASE_FILENAME
    )
else:
    _bundled_database_path = Path(__file__).resolve().parent / "database" / DATABASE_FILENAME

if getattr(sys, "frozen", False):
    _default_database_path = (
        Path(
            os.getenv(
                "MOMENTUM_DATA_DIR",
                os.path.join(
                    os.getenv("LOCALAPPDATA", os.path.expanduser("~")),
                    "Momentum",
                ),
            )
        )
        / DATABASE_FILENAME
    )
else:
    _default_database_path = (
        Path(__file__).resolve().parent / "database" / DATABASE_FILENAME
    )

DATABASE_PATH = os.getenv("DATABASE_PATH", str(_default_database_path))
BUNDLED_DATABASE_PATH = _bundled_database_path

# Ensure DATABASE_PATH is absolute and anchored to this package directory.
# This prevents a relative path from .env (e.g. "database/momentum.db") resolving
# relative to the current working directory when the app is launched from
# elsewhere.
if not os.path.isabs(DATABASE_PATH):
    DATABASE_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), DATABASE_PATH)
    )

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

# Simulation Parameters
MONTE_CARLO_ITERATIONS = int(os.getenv("MONTE_CARLO_ITERATIONS", "1000"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# AI Configuration
AI_DECISION_FREQUENCY = int(os.getenv("AI_DECISION_FREQUENCY", "5"))  # seconds
STRATEGY_COMPLEXITY = os.getenv("STRATEGY_COMPLEXITY", "medium")  # low, medium, high

# ============================================================================
# CURRENCY CONFIGURATION
# ============================================================================

# Currency System Settings
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "EUR")  # EUR, USD, GBP, JPY, CHF
CURRENCY_UPDATE_INTERVAL = int(
    os.getenv("CURRENCY_UPDATE_INTERVAL", "3600")
)  # seconds (1 hour)
USE_LIVE_EXCHANGE_RATES = os.getenv("USE_LIVE_EXCHANGE_RATES", "true").lower() == "true"
CURRENCY_CACHE_FILE = os.getenv(
    "CURRENCY_CACHE_FILE",
    os.path.join(os.path.dirname(__file__), "data", "currency_cache.json"),
)

# Motorsport Budget Configuration (2025 values)
SINGLE_SEATER_BUDGET_CAP_EUR = float(
    os.getenv("SINGLE_SEATER_BUDGET_CAP_EUR", "130000000")
)  # €130M EUR
ENABLE_BUDGET_ENFORCEMENT = (
    os.getenv("ENABLE_BUDGET_ENFORCEMENT", "true").lower() == "true"
)
BUDGET_VIOLATION_PENALTY = float(
    os.getenv("BUDGET_VIOLATION_PENALTY", "0.1")
)  # 10% performance penalty

# ============================================================================
# API CONFIGURATION
# ============================================================================

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"

# CORS Configuration
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv(
    "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOG_FILE = os.getenv("LOG_FILE", "logs/momentum.log")

# ============================================================================
# DEVELOPMENT SETTINGS
# ============================================================================

DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
ENABLE_DEBUG_ENDPOINTS = os.getenv("ENABLE_DEBUG_ENDPOINTS", "true").lower() == "true"
MOCK_EXTERNAL_APIS = os.getenv("MOCK_EXTERNAL_APIS", "false").lower() == "true"

DISCIPLINES = {
    "SINGLE_SEATER": {
        "name": "Single Seater Racing",
        "description": "Formula-style open-wheel racing",
    },
    "PRODUCTION_TOURING": {
        "name": "Production/Touring Car Racing",
        "description": "GT and touring car racing",
    },
    "URBAN_STREET": {
        "name": "Urban/Street Racing",
        "description": "Drifting-focused urban street racing",
    },
    "DRAG_ACCELERATION": {
        "name": "Drag/Acceleration Racing",
        "description": "Straight-line acceleration racing",
    },
    "SPRINT_RALLYCROSS": {
        "name": "Sprint/Rallycross Racing",
        "description": "Mixed-surface short-circuit racing",
    },
    "ENDURANCE": {
        "name": "Endurance Racing",
        "description": "Long-distance prototype and GT racing",
    },
}

# ============================================================================
# STAFF ROLES & DISCIPLINE IMPACTS
# ============================================================================

# Configuration used by staffing systems, salary estimation, and future
# performance multipliers. Impacts are expressed as fractional modifiers
# (e.g., 0.06 = +6% to a category when fully utilized).
STAFF_ROLES_CONFIG = {
    "TEAM_PRINCIPAL": {
        "weight": 1,
        "rating_range": (65.0, 95.0),
        "base_effects": {"operations": 0.08, "morale": 0.05, "budget_efficiency": 0.04},
        "discipline_modifiers": {"ENDURANCE": 1.1, "DRAG_ACCELERATION": 0.9},
    },
    "TECHNICAL_DIRECTOR": {
        "weight": 1,
        "rating_range": (65.0, 95.0),
        "base_effects": {"car_performance": 0.07, "reliability": 0.04},
        "discipline_modifiers": {"ENDURANCE": 1.1},
    },
    "RACE_ENGINEER": {
        "weight": 6,
        "rating_range": (55.0, 90.0),
        "base_effects": {"setup": 0.06, "consistency": 0.03},
        "discipline_modifiers": {},
    },
    "STRATEGIST": {
        "weight": 4,
        "rating_range": (55.0, 90.0),
        "base_effects": {"strategy": 0.07},
        "discipline_modifiers": {"ENDURANCE": 1.2},
    },
    "DATA_ANALYST": {
        "weight": 4,
        "rating_range": (50.0, 85.0),
        "base_effects": {"strategy": 0.03, "racecraft": 0.02},
        "discipline_modifiers": {},
    },
    "MECHANIC": {
        "weight": 12,
        "rating_range": (45.0, 85.0),
        "base_effects": {"reliability": 0.05, "pitstop": 0.03},
        "discipline_modifiers": {"DRAG_ACCELERATION": 0.9},
    },
    "AERODYNAMICIST": {
        "weight": 3,
        "rating_range": (50.0, 90.0),
        "base_effects": {"aero": 0.06},
        "discipline_modifiers": {"DRAG_ACCELERATION": 0.7, "URBAN_STREET": 0.8},
    },
    "POWERTRAIN_ENGINEER": {
        "weight": 3,
        "rating_range": (50.0, 90.0),
        "base_effects": {"power": 0.06, "reliability": 0.03},
        "discipline_modifiers": {"DRAG_ACCELERATION": 1.2},
    },
    "SUSPENSION_ENGINEER": {
        "weight": 3,
        "rating_range": (50.0, 88.0),
        "base_effects": {"handling": 0.05, "drift_control": 0.04},
        "discipline_modifiers": {"URBAN_STREET": 1.2, "SPRINT_RALLYCROSS": 1.1},
    },
    "TYRE_SPECIALIST": {
        "weight": 2,
        "rating_range": (50.0, 85.0),
        "base_effects": {"tyre_management": 0.06},
        "discipline_modifiers": {"ENDURANCE": 1.2},
    },
    "CREW_CHIEF": {
        "weight": 3,
        "rating_range": (55.0, 90.0),
        "base_effects": {"pitstop": 0.05, "operations": 0.03},
        "discipline_modifiers": {},
    },
    "DRIFT_COACH": {
        "weight": 2,
        "rating_range": (55.0, 90.0),
        "base_effects": {"drift_control": 0.08, "style": 0.04},
        "discipline_modifiers": {"URBAN_STREET": 1.4},
    },
    "SIMULATOR_DRIVER": {
        "weight": 2,
        "rating_range": (45.0, 75.0),
        "base_effects": {"setup": 0.03, "consistency": 0.02},
        "discipline_modifiers": {},
    },
    "SPORTS_PSYCHOLOGIST": {
        "weight": 2,
        "rating_range": (45.0, 80.0),
        "base_effects": {"pressure": 0.05, "focus": 0.03},
        "discipline_modifiers": {},
    },
    "LOGISTICS_MANAGER": {
        "weight": 2,
        "rating_range": (45.0, 80.0),
        "base_effects": {"operations": 0.04, "reliability": 0.02},
        "discipline_modifiers": {},
    },
    "MARKETING_DIRECTOR": {
        "weight": 2,
        "rating_range": (40.0, 75.0),
        "base_effects": {"sponsorship": 0.06},
        "discipline_modifiers": {},
    },
}

# ============================================================================
# DRIVER ATTRIBUTES (50+ Comprehensive Attributes)
# ============================================================================

# Core Driving Skills (10 attributes)
DRIVER_CORE_SKILLS = [
    "raw_speed",
    "consistency",
    "racecraft",
    "overtaking",
    "defensive_driving",
    "cornering_skill",
    "braking_technique",
    "acceleration_control",
    "spatial_awareness",
    "vehicle_control",
]

# Physical & Mental Traits (10 attributes)
DRIVER_PHYSICAL_MENTAL = [
    "physical_fitness",
    "reaction_time",
    "concentration",
    "pressure_handling",
    "pain_tolerance",
    "g_force_tolerance",
    "coordination",
    "multitasking",
    "mental_resilience",
    "adrenaline_management",
]

# Technical Knowledge (8 attributes)
DRIVER_TECHNICAL = [
    "setup_knowledge",
    "mechanical_sympathy",
    "tyre_management",
    "fuel_management",
    "aerodynamics_understanding",
    "suspension_feel",
    "engine_management",
    "data_analysis",
]

# Discipline Specializations (6 attributes)
DRIVER_DISCIPLINE_APTITUDES = [
    "single_seater_aptitude",
    "production_touring_aptitude",
    "urban_street_aptitude",
    "drag_acceleration_aptitude",
    "sprint_rallycross_aptitude",
    "endurance_aptitude",
]

# Race Craft & Strategy (8 attributes)
DRIVER_STRATEGY = [
    "race_strategy",
    "pit_stop_coordination",
    "traffic_management",
    "tyre_strategy",
    "fuel_strategy",
    "safety_car_awareness",
    "qualifying_optimization",
    "championship_thinking",
]

# Environmental Adaptation (7 attributes)
DRIVER_ADAPTATION = [
    "wet_weather_skill",
    "night_racing_skill",
    "temperature_adaptation",
    "altitude_adaptation",
    "surface_adaptation",
    "car_adaptation",
    "track_learning",
]

# Personal & Social Traits (6 attributes)
DRIVER_PERSONAL = [
    "media_presence",
    "team_cooperation",
    "leadership_ability",
    "risk_appetite",
    "ego_management",
    "commercial_appeal",
]

# Specialized Skills (2 attributes)
DRIVER_SPECIALIZED = ["energy_management", "stint_management"]

# Development & Career Traits (4 attributes)
DRIVER_DEVELOPMENT = [
    "learning_rate",
    "team_loyalty",
    "ambition_level",
    "discipline_switching_tendency",
]

# All Driver Attributes Combined (56 total)
ALL_DRIVER_ATTRIBUTES = (
    DRIVER_CORE_SKILLS
    + DRIVER_PHYSICAL_MENTAL
    + DRIVER_TECHNICAL
    + DRIVER_DISCIPLINE_APTITUDES
    + DRIVER_STRATEGY
    + DRIVER_ADAPTATION
    + DRIVER_PERSONAL
    + DRIVER_SPECIALIZED
    + DRIVER_DEVELOPMENT
)

# Attribute value range (0.0 to 100.0 scale used in models)
DRIVER_ATTRIBUTE_MIN = 0.0
DRIVER_ATTRIBUTE_MAX = 100.0
DRIVER_ATTRIBUTE_DEFAULT = 50.0

# UI / Race configuration
# Number of drivers on the grid by default (used by race visualiser and quick race)
# Grid sizes come from each discipline's RaceFormat; RACE_GRID_SIZE in the
# environment forces a fixed cap for testing.
_grid_override = os.getenv("RACE_GRID_SIZE")
RACE_GRID_SIZE_OVERRIDE = int(_grid_override) if _grid_override else None
RACE_GRID_SIZE = RACE_GRID_SIZE_OVERRIDE or 20
# Number of drivers to show in the quick-race selection list
QUICK_RACE_LIST_SIZE = int(os.getenv("QUICK_RACE_LIST_SIZE", "20"))
# Rendering configuration: target frames per second for GUI animation
RENDER_FPS = int(
    os.getenv("RENDER_FPS", "200")
)  # 200 FPS = ultra-smooth (high CPU usage)
