# Configuration settings for Momentum simulation
import os
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

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "database", "momentum.db"))

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
CURRENCY_UPDATE_INTERVAL = int(os.getenv("CURRENCY_UPDATE_INTERVAL", "3600"))  # seconds (1 hour)
USE_LIVE_EXCHANGE_RATES = os.getenv("USE_LIVE_EXCHANGE_RATES", "true").lower() == "true"
CURRENCY_CACHE_FILE = os.getenv("CURRENCY_CACHE_FILE", "currency_cache.json")

# Motorsport Budget Configuration (2025 values)
SINGLE_SEATER_BUDGET_CAP_EUR = float(os.getenv("SINGLE_SEATER_BUDGET_CAP_EUR", "130000000"))  # €130M EUR
ENABLE_BUDGET_ENFORCEMENT = os.getenv("ENABLE_BUDGET_ENFORCEMENT", "true").lower() == "true"
BUDGET_VIOLATION_PENALTY = float(os.getenv("BUDGET_VIOLATION_PENALTY", "0.1"))  # 10% performance penalty

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
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = os.getenv("LOG_FILE", "logs/momentum.log")

# ============================================================================
# DEVELOPMENT SETTINGS
# ============================================================================

DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
ENABLE_DEBUG_ENDPOINTS = os.getenv("ENABLE_DEBUG_ENDPOINTS", "true").lower() == "true"
MOCK_EXTERNAL_APIS = os.getenv("MOCK_EXTERNAL_APIS", "false").lower() == "true"

# Racing Disciplines
DISCIPLINES = {
    "single_seater": {
        "name": "Single Seater Racing",
        "categories": ["Premier", "Second", "Third"],
        "race_duration_minutes": 90
    },
    "rally_stage": {
        "name": "Rally Stage Racing", 
        "categories": ["World", "Regional", "National"],
        "race_duration_minutes": 180
    },
    "endurance": {
        "name": "Endurance Racing",
        "categories": ["Prototype_A", "Prototype_B", "Grand_Touring"],
        "race_duration_minutes": 360
    },
    "urban_street": {
        "name": "Urban Street Racing",
        "categories": ["Sports_GT_A", "Sports_GT_B", "Touring_Car"],
        "race_duration_minutes": 60
    }
}

# Driver Attributes Range (0.0 to 1.0)
DRIVER_ATTRIBUTES = {
    "skill": {"min": 0.1, "max": 1.0},
    "consistency": {"min": 0.1, "max": 1.0},
    "aggression": {"min": 0.0, "max": 1.0},
    "racecraft": {"min": 0.1, "max": 1.0},
    "adaptability": {"min": 0.1, "max": 1.0}
}

# Team Financial Ranges (in millions)
TEAM_BUDGETS = {
    "tier1": {"min": 100, "max": 400},  # Top teams
    "tier2": {"min": 50, "max": 150},   # Mid-field
    "tier3": {"min": 20, "max": 80}     # Lower teams
}