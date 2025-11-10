# Momentum - Multi-discipline Motorsport Management Simulator

## Project Overview

Momentum is a comprehensive motorsport management simulation spanning **7 racing disciplines** (Single Seater, Production/Touring, Rally/Stage, Urban/Street, Drag/Acceleration, Sprint/Rallycross, Endurance). The architecture consists of a **Python FastAPI backend** providing race simulation and game logic, with planned Unity frontend integration. The backend is ~60-70% playable with core simulation working but game loop/progression incomplete.

## Architecture

### Core Structure

Momentum/Python/           # Primary Python backend codebase
├── simulation.py          # Main FastAPI entry point (uvicorn simulation:app)
├── config.py              # Centralized configuration (env vars via dotenv)
├── logging_system.py      # Logging and crash reporting system
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
│
├── gui/                   # PyQt6 GUI components
│   ├── gui_game.py        # Main game interface (primary testing method)
│   ├── gui_garage.py      # Garage/workshop screen
│   ├── gui_component_health.py # Component health widgets
│   └── log_viewer.py      # Log viewing tool
│
├── scripts/               # Utility and admin scripts
│   ├── generate_initial_database.py # Database generation
│   ├── regenerate_database.py       # Database regeneration
│   ├── import_circuits.py           # Circuit data import
│   ├── verify_database.py           # Database verification
│   ├── check_db_state.py            # Database state checker
│   └── build_exe.py                 # PyInstaller build script
│
├── data/                  # Data files
│   ├── circuits_database.json # 175 circuit definitions
│   └── currency_cache.json    # Exchange rate cache
│
├── logs/                  # Log files (auto-generated)
│   ├── database_generation.log
│   └── database_generation_report.txt
│
├── docs/                  # Documentation
│   ├── API_KEY_SECURITY.md
│   └── CLEANUP_SUMMARY.md
│
├── database/              # SQLite database
│   ├── models.py          # Data models (Driver: 50+ attrs, Team, Track, etc.)
│   ├── database_manager.py # CRUD operations, transaction management
│   ├── database_factory.py # Database initialization patterns
│   └── momentum.db        # Main database file
│
├── disciplines/           # 7 racing discipline simulators
│   ├── base_engine.py     # Abstract base class for all disciplines
│   ├── multi_discipline_simulator.py # Orchestration layer
│   ├── race_simulation.py # Core Monte Carlo simulation
│   └── [discipline]/      # single_seater, rally_stage, endurance, etc.
│
├── systems/               # Game systems (currency, staff, world_state, game_loop)
├── api/                   # API schemas and request/response models
├── ai/                    # AI decision engine
├── services/              # Service layer components
├── vehicles/              # Vehicle systems
├── tests/                 # Test files
├── tools/                 # Development tools
└── saves/                 # Save game filesDatabase Layer (SQLite)

- **Driver Model**: 50+ attributes across 7 categories (technical, mental, physical, racecraft, personality, discipline preferences). All attributes use 0-100 scale.
- **Team Model**: Budget, tier, headquarters, discipline specialization
- **Track Model**: 175 circuits with IMA grading, surface types, characteristics
- **Current Data**: 1,781 drivers, 1,095 teams, 175 tracks, 57,936 staff
- **Path Resolution**: `config.DATABASE_PATH` anchored to package directory (absolute path conversion prevents CWD issues)

### Simulation Engine (Monte Carlo)

Each discipline inherits from `BaseDisciplineEngine` in `disciplines/base_engine.py`:

- **Performance Weighting**: 40% driver skill, 30% team capability, 20% environmental, 10% randomness
- **Discipline-Specific Logic**: Each racing type has unique simulation characteristics (e.g., rally uses co-driver attributes, drag uses reaction time, endurance emphasizes reliability)
- **Context Pattern**: `DisciplineContext` dataclass bundles race, track, drivers, teams, weather, track conditions

### Multi-Currency System

Real-time exchange rate support (EUR default) configured in `config.py`:

- Budget caps: €130M EUR for top-tier Single Seater (2025 values)
- Staff salaries and team budgets scale by discipline (€800K to €12M+)
- Cache file: `data/currency_cache.json` (update interval: 3600s)

### Name Generation

Intelligent multi-locale system using **Faker library** (24 locales):

- Team names: 6 authentic patterns (no real-world conflicts)
- Driver names: Latin-script compatible, culturally appropriate
- Circuit names: 175 unique with realistic branding
- Configuration in `config.py` with NameAPI and ParaNames fallback support

## Developer Workflows

### Running the Backend

```powershell
# From Momentum/Python directory:
cd Momentum\Python
python -m uvicorn simulation:app --reload --host 127.0.0.1 --port 8000
# Alternative: python simulation.py (uvicorn called at __main__)
```

### Testing Approaches

```powershell
# Playability assessment (comprehensive backend check)
python tests/test_playability.py

# Individual test scripts (no pytest required, in tests/ folder):
python tests/test_race_simulation.py      # Single race simulation
python tests/test_game_loop_api.py        # Season/championship API
python tests/test_2025_season.py          # Full season simulation
python tests/test_cultural_names.py       # Name generation validation

# GUI playable game (PyQt6 interface - PRIMARY testing method):
python gui/gui_game.py

# Alternative CLI game (terminal interface):
python cli_game.py

# Database utilities (in scripts/ folder):
python scripts/verify_database.py        # Check database contents
python scripts/check_db_state.py         # Verify championships/races
python scripts/import_circuits.py        # Import 175 circuits from JSON
```

### Database Operations

```python
# Standard pattern across codebase:
from database.database_manager import DatabaseManager
from config import DATABASE_PATH  # Always use this, not hardcoded paths

db = DatabaseManager()
drivers = db.get_all_drivers()
teams = db.get_teams_by_discipline("SINGLE_SEATER")
```

### API Endpoint Patterns

Key endpoints in `simulation.py`:

- `GET /health` - Health check (use for Unity connectivity tests)
- `GET /drivers` - Returns all 1,781 drivers with attributes
- `GET /teams?discipline=SINGLE_SEATER` - Filtered team queries
- `POST /simulate/race` - Core race simulation endpoint
- `POST /season/create` - Initialize championship season
- `GET /season/standings` - Championship standings

CORS configured for `*` (development only) - restrict in production.

## Critical Patterns

### Discipline Enum

```python
from disciplines.base_engine import RacingDiscipline
# Always use: SINGLE_SEATER, PRODUCTION_TOURING, RALLY_STAGE, 
# URBAN_STREET, DRAG_ACCELERATION, SPRINT_RALLYCROSS, ENDURANCE
```

### Configuration Access

**Always** import from `config.py`, never hardcode values:

```python
from config import DATABASE_PATH, DEFAULT_CURRENCY, MONTE_CARLO_ITERATIONS
# Environment variables loaded via python-dotenv (.env file)
```

### Driver Attributes

Driver skills are 0-100 floats. Key attributes by discipline:

- **Single Seater**: raw_speed, cornering_skill, qualifying_pace, aerodynamics_understanding
- **Rally**: surface_adaptation, co_driver_communication (note: co-driver is separate entity)
- **Endurance**: tire_management, fuel_management, consistency, mechanical_sympathy
- **Drag**: acceleration_control, reaction_time, starting_skill

## Known Issues & Incomplete Systems

### ⚠️ Missing Game Loop (Status: 10% complete)

- `systems/game_loop.py` exists but **untested/unvalidated**
- Season progression, championship standings, calendar management not fully functional
- Save/load game state not implemented
- See `HONEST_STATUS.md` and `PLAYABILITY_STATUS.md` for details

### ⚠️ Track Data Integration (Status: 20% complete)

- 175 circuits designed in `data/circuits_database.json`
- **Not yet imported into SQLite database** (0 tracks currently)
- Race simulation endpoint errors due to missing track data
- Fix: `scripts/import_circuits.py` exists but needs validation

### ⚠️ Staff Management (Status: 40% complete)

- Staff models fully defined (40+ attributes, 25+ roles)
- Hiring/firing/contract endpoints not implemented
- Performance multiplier system designed but not integrated into simulation

### ⚠️ Unity Frontend (Status: 5% complete)

- `UnityApiClient.cs` provides basic HTTP client
- See `Momentum/Unity/README.md` for CORS setup
- No UI scenes, just API connectivity example

## Dependencies & Build

```
# Core dependencies (requirements.txt):
fastapi, uvicorn       # Web API
numpy, pandas, scipy   # Simulation math
pydantic              # Data validation
Faker, requests       # Name generation, HTTP
python-dotenv         # Environment config
PyQt6                 # GUI (gui/gui_game.py, gui/gui_garage.py)
pytest, black, mypy   # Dev tools

# Build executable (experimental):
python scripts/build_exe.py   # PyInstaller-based, includes momentum.db
```

## Technical Report Context

This is a **final year Computer Science project**. Technical report sections exist in `Technical Report/` covering:

- Design & Implementation
- Requirements analysis
- Testing & Evaluation
- Use cases and system architecture

## Quick Start for New Contributors

1. Read `README.md` (root and `Momentum/Python/README.md`)
2. Check `PLAYABILITY_STATUS.md` for current feature status
3. Review `GAME_DESIGN_DOCUMENT.md` for gameplay mechanics
4. Run `python tests/test_playability.py` to validate backend setup
5. Start API: `uvicorn simulation:app --reload`
6. Test playability: `python gui/gui_game.py` for PyQt6 GUI game interface (primary testing method)

## File Naming Conventions

- Test files: `tests/test_*.py` (runnable directly, no pytest framework required)
- GUI components: `gui/*.py` (PyQt6 GUI screens and widgets)
- Scripts: `scripts/*.py` (database generation, import tools, build scripts)
- Core engines: `disciplines/[discipline_name]/` directories
- Status docs: `*.md` in `Momentum/` (STATUS_REPORT, HONEST_STATUS, PLAYABILITY_STATUS)
- API schemas: `api/schemas.py` (Pydantic models for request/response)

## When Editing Code

- **Configuration**: Add new settings to `config.py` with env var support
- **Database Models**: Extend in `database/models.py`, update `SCHEMA_SQL` string
- **New Discipline**: Inherit from `BaseDisciplineEngine`, implement abstract methods
- **API Endpoints**: Add to `simulation.py`, follow existing pattern with try/except HTTPException
- **Testing**: Create standalone `test_*.py` files that can run without pytest
