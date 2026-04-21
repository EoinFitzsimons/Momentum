# Momentum - Multi-discipline Motorsport Management Simulator

## Project Overview

Momentum is a **final year Computer Science project**: comprehensive motorsport management simulation spanning **6 racing disciplines** (Single Seater, Production/Touring, Urban/Street (Drifting), Drag/Acceleration, Sprint/Rallycross, Endurance). Architecture: **Python FastAPI backend** providing race simulation and game logic via REST API, with **PyQt6 desktop GUI** for interactive gameplay. **Current Status**: Backend ~70% playable (core simulation + 13 pytest tests), GUI 60% complete (5 functional screens + 3 in development).

## Project Structure

Momentum/Python/
├── simulation.py                     # Main FastAPI entry point
├── config.py                         # Centralized configuration (env vars)
├── init_db.py                        # Database initialization
├── logging_system.py                 # Logging and error reporting
├── requirements.txt                  # Python dependencies
├── pytest.ini                        # Pytest configuration
│
├── RaceLogic/                        # ⭐ Core simulation engines
│   ├── base_race_engine.py           # Abstract base class for all disciplines
│   ├── realtime_race_engine.py       # Main race simulation engine (Monte Carlo)
│   ├── track_physics.py              # Track dynamics, grip, elevation
│   ├── overtaking_system.py          # AI overtaking logic
│   ├── closure_solver.py             # Traffic & gap calculations
│   └── disciplines/                  # 6 Discipline-specific implementations
│       ├── single_seater/
│       │   └── single_seater_discipline.py
│       ├── production_touring/
│       │   └── production_touring_discipline.py
│       ├── urban_street/
│       │   └── urban_street_discipline.py
│       ├── drag_acceleration/
│       │   └── drag_acceleration_discipline.py
│       ├── sprint_rallycross/
│       │   └── sprint_rallycross_discipline.py
│       └── endurance/
│           └── endurance_discipline.py
│
├── GUI/                              # ⭐ PyQt6 GUI (capitalised)
│   ├── launcher.py                   # Entry point - main menu
│   ├── gui_main_menu.py              # Main menu screen
│   ├── gui_race_visual.py            # Real-time 30 FPS race visualization (PLAYABLE)
│   ├── gui_championship.py           # Championship management screen
│   ├── gui_career.py                 # Career mode/season progression
│   ├── gui_navbar.py                 # Navigation bar component
│   ├── responsive_utils.py           # Responsive layout utilities
│   ├── infield_presets.py            # Track decal/prop presets
│   ├── props_placer.py               # Prop/decal placement tools
│   ├── assets/                       # Images, sprites, textures
│   └── tools/                        # GUI development tools
│
├── database/                         # ⭐ SQLite persistence layer
│   ├── models.py                     # Data models & schema definition
│   ├── models/
│   │   └── multi_discipline_models.py
│   ├── database_manager.py           # CRUD operations, transactions
│   ├── database_factory.py           # Database initialization patterns
│   ├── database_extensions.py        # Extended queries
│   ├── migration_scaffold.py         # Schema migration tools
│   └── momentum.db                   # Main SQLite database
│
├── services/                         # ⭐ Business logic layer (NOT systems/)
│   ├── race_simulation_api.py        # Dynamic discipline loading, race orchestration
│   ├── championship_service.py       # Championship/season/standings management
│   ├── progression_service.py        # Season progression, race advancement
│   ├── team_service.py               # Team CRUD, attributes, budget
│   ├── driver_attributes.py          # Driver skill calculation & aging
│   ├── hiring_service.py             # Staff hiring/contract management
│   ├── persistence_sqlite.py         # Data persistence wrapper
│   └── track_surface_service.py      # Track condition simulation
│
│
├── tests/                            # ⭐ Comprehensive pytest suite (13 files)
│   ├── conftest.py                   # Pytest fixtures & configuration
│   ├── README.md                     # Test documentation & run instructions
│   ├── test_integration_api_contracts.py        # API contract tests
│   ├── test_integration_championship_flow.py    # Championship flow tests
│   ├── test_integration_database_layer.py       # Database layer tests
│   ├── test_integration_full_career_season.py   # Full season simulation
│   ├── test_unit_championship_rules.py          # Championship rules
│   ├── test_unit_gui_launcher_smoke.py          # GUI smoke tests
│   ├── test_unit_racelogic_discipline_loader.py # Discipline loading
│   ├── test_unit_racelogic_single_seater.py     # Single Seater discipline
│   ├── test_unit_racelogic_production_touring.py
│   ├── test_unit_racelogic_urban_street.py
│   ├── test_unit_racelogic_sprint_rallycross.py
│   ├── test_unit_racelogic_endurance.py
│   ├── test_unit_racelogic_drag_acceleration.py
│   ├── test_unit_track_surface_service.py
│   └── output/                       # Test reports & coverage data
│
├── mvp_tests/                        # Quick-check test scripts (3 files)
│
├── scripts/                          # Utility & admin scripts
│   ├── import_circuits.py            # Import 175 circuits from JSON
│   ├── tools/
│   │   ├── import_circuits_idempotent.py
│   │   └── [other utilities]
│
├── data/                             # Static data files
│   ├── circuits_database.json        # 175 circuit definitions (NOT YET IMPORTED)
│   └── currency_cache.json           # Exchange rate cache
│
├── api/                              # API schemas & request/response models
│   ├── schemas.py                    # Pydantic models
│   └── __init__.py
│
├── docs/                             # Documentation
│   ├── CHAMPIONSHIP_MANAGEMENT.md
│   ├── MATHEMATICS_AND_FUNCTION_SOURCES.md
│   └── [other docs]
│
├── vehicles/                         # Vehicle systems (minimal)
├── tools/                            # Development tools
└── logs/                             # Auto-generated log files

## Core Simulation Architecture

### Discipline-Specific Engines (RaceLogic/)

Each of 6 disciplines inherits from `BaseDisciplineEngine` in `RaceLogic/base_race_engine.py`:

**Inherited Methods (All Disciplines):**

- `calculate_performance()` - 40% driver, 30% team, 20% env, 10% random
- `simulate_race_result()` - Monte Carlo race simulation
- `calculate_driver_performance()` - Skill-based performance weighting

**Discipline-Specific Overrides:**

| Discipline                     | Key File                             | Performance Factors                                 |
| ------------------------------ | ------------------------------------ | --------------------------------------------------- |
| **Single Seater**        | `single_seater_discipline.py`      | Qualifying pace, raw speed, aerodynamics, racecraft |
| **Production/Touring**   | `production_touring_discipline.py` | Consistency, reliability, tire management, setup    |
| **Urban/Street (Drift)** | `urban_street_discipline.py`       | Drift control, car control, reactions, precision    |
| **Drag/Acceleration**    | `drag_acceleration_discipline.py`  | Reaction time, acceleration control, starting       |
| **Sprint/Rallycross**    | `sprint_rallycross_discipline.py`  | Handling, short-burst performance, car control      |
| **Endurance**            | `endurance_discipline.py`          | Tire mgmt, fuel mgmt, consistency, reliability      |

**Dynamic Loading** ([services/race_simulation_api.py](services/race_simulation_api.py)):

```python
# Disciplines loaded at runtime from: RaceLogic.disciplines.{discipline_name}.{discipline_name}_discipline
engine = _load_discipline_engine(context)  # Selects correct discipline dynamically
```

### Race Simulation Flow

1. **Setup** ([realtime_race_engine.py](RaceLogic/realtime_race_engine.py)): Track physics, weather, conditions
2. **Qualify** ([single_seater_discipline.py](RaceLogic/disciplines/single_seater/single_seater_discipline.py)): Grid determination
3. **Race Loop** (30 FPS game loop): Driver updates, overtaking, collisions, safety cars
4. **Pit Strategy** ([endurance_discipline.py](RaceLogic/disciplines/endurance/endurance_discipline.py)): Tire/fuel stops
5. **Results** ([realtime_race_engine.py](RaceLogic/realtime_race_engine.py)): Points, penalties, championship update

### Championship Management ([services/championship_service.py](services/championship_service.py))

- **Create**: `create_championship(name, discipline, teams, calendar)` → returns Championship ID
- **Progress**: `progress_to_next_race()` → auto-schedules next race
- **Standings**: `get_championship_standings(championship_id)` → current points table
- **Track Data**: Uses `data/circuits_database.json` (175 circuits, but **not yet imported to DB**)

## Database Layer (SQLite)

**Models** ([database/models.py](database/models.py)):

```python
@dataclass class Driver:              # 60+ attributes (skill, age, contract, nationality, etc.)
@dataclass class Team:                # Budget, discipline, tier, HQ location
@dataclass class Championship:        # Season/standings management
@dataclass class Race:                # Scheduled race metadata
@dataclass class RaceResult:          # Race outcome, points, fastest lap
@dataclass class StaffMember:         # Staff role, rating, contract
@dataclass class Track:               # 175 circuit definitions (schema ready, data not imported)
```

**Current Data State:**

- ✅ 1,781 drivers in database
- ✅ 1,095 teams in database
- ✅ 57,936 staff members in database
- ❌ **0 tracks** - schema exists but circuits_database.json not imported
- ❌ Must run `scripts/import_circuits.py` to populate tracks

**Access Pattern** (consistent across codebase):

```python
from database.database_manager import DatabaseManager
from config import DATABASE_PATH

db = DatabaseManager()
teams = db.get_teams_by_discipline("SINGLE_SEATER")
```

## API Endpoints (simulation.py)

**20+ FastAPI endpoints** with error handling:

| Endpoint                             | Method | Purpose                      |
| ------------------------------------ | ------ | ---------------------------- |
| `/`                                | GET    | Root endpoint info           |
| `/health`                          | GET    | API availability check       |
| `/drivers`                         | GET    | All drivers (with filtering) |
| `/teams`                           | GET    | All teams (with filtering)   |
| `/teams/{team_id}`                 | GET    | Specific team details        |
| `/teams`                           | POST   | Create new team              |
| `/teams/{team_id}/budget`          | GET    | Team budget details          |
| `/teams/{team_id}/budget/allocate` | POST   | Allocate budget              |
| `/championships`                   | POST   | Create championship          |
| `/championships/{id}`              | GET    | Championship details         |
| `/championships/{id}/standings`    | GET    | Points standings             |
| `/championships/{id}/schedule`     | GET    | Race calendar                |
| `/simulate/race`                   | POST   | Run single race              |
| `/races/{race_id}/results`         | GET    | Race results                 |
| `/races/{race_id}/complete`        | POST   | Mark race complete           |
| [+ 5 more endpoints]                 | -      | Staff, driver updates, etc.  |

**CORS**: Configured for `*` (development only - restrict in production)

## GUI Implementation (PyQt6)

**Entry Point**: `GUI/launcher.py` (run this to start the game)

**Implemented Screens** (✅ Functional):

1. **Main Menu** ([gui_main_menu.py](GUI/gui_main_menu.py)): Driver selection, quick race setup
2. **Race Visualization** ([gui_race_visual.py](GUI/gui_race_visual.py)): Real-time 30 FPS race playable (PRIMARY TEST METHOD)
3. **Championship Manager** ([gui_championship.py](GUI/gui_championship.py)): Create/view championships
4. **Career Mode** ([gui_career.py](GUI/gui_career.py)): Season progression, standings
5. **Navigation Bar** ([gui_navbar.py](GUI/gui_navbar.py)): Menu navigation component

**In Development** (⚠️ Not fully complete):

6. **Garage/Workshop** - Team attribute management (not implemented)
7. **Component Health** - Vehicle condition tracking (not implemented)
8. **Log Viewer** - Diagnostics tool (not implemented)

**Utilities:**

- `responsive_utils.py` - Dynamic resizing, responsive layouts
- `infield_presets.py` - Track decal/prop presets
- `props_placer.py` - Prop placement tools
- `assets/` - Images, sprites, textures

## Testing

**Pytest Suite** (13 comprehensive tests):

```bash
# Run all tests
cd Momentum/Python
pytest tests -q

# Run unit tests only
pytest tests -m unit -q

# Run integration tests only
pytest tests -m integration -q

# Run specific test file
pytest tests/test_integration_championship_flow.py -v
```

**Test Coverage:**

- ✅ API contract validation (6 tests)
- ✅ Championship/season flow (4 tests)
- ✅ Database layer operations (5 tests)
- ✅ Full season simulation (1 test)
- ✅ Championship rules (4 tests)
- ✅ GUI smoke tests (launcher)
- ✅ All 6 discipline engines
- ✅ Track surface service

**See** [tests/README.md](Momentum/Python/tests/README.md) for detailed test documentation

**MVP Tests** ([mvp_tests/](Momentum/Python/mvp_tests/)): Quick-check scripts for rapid validation

## Configuration

**Environment Variables** ([config.py](config.py)):

```python
# Always import from config, never hardcode
from config import DATABASE_PATH, DEFAULT_CURRENCY, MONTE_CARLO_ITERATIONS

# Key settings:
DATABASE_PATH          # SQLite database location
DEFAULT_CURRENCY       # EUR (default)
MONTE_CARLO_ITERATIONS # Simulation runs per race
STAFF_ROLES_CONFIG     # Staff role impact multipliers
```

Load from `.env` file (not in git):

```
DATABASE_PATH=/path/to/momentum.db
DEFAULT_CURRENCY=EUR
MONTE_CARLO_ITERATIONS=1000
```

## Developer Workflows

### Start Backend API

```powershell
cd Momentum/Python
python -m uvicorn simulation:app --reload --host 127.0.0.1 --port 8000
# API available at http://localhost:8000
```

### Run GUI Game (Primary Testing Method)

```powershell
cd Momentum/Python
python GUI/launcher.py
# Opens PyQt6 main menu, playable race visualization
```

### Import Track Data

```powershell
cd Momentum/Python
python scripts/import_circuits.py
# Loads 175 circuits from data/circuits_database.json into momentum.db
```

### Run Tests

```powershell
cd Momentum/Python
pytest tests -q                    # All tests
pytest tests -m unit -q            # Unit tests only
pytest tests/test_*.py -v          # Specific test with verbose output
```

## Known Issues & Limitations

### ⚠️ Track Data Not Imported

- `data/circuits_database.json` exists with 175 circuit definitions
- **NOT YET LOADED** into SQLite database (0 tracks in DB)
- Schema ready but data missing
- **Action**: Run `scripts/import_circuits.py` to fix
- **Impact**: Race simulation endpoint can fail with missing track data

### ⚠️ Empty systems/ Directory

- `systems/` folder exists but is empty (legacy location)
- Game logic moved to `services/` directory
- No `game_loop.py`, `currency.py`, `staff.py`, `world_state.py` files
- **Note**: Core systems in `services/championship_service.py`, `progression_service.py`, etc.

### ⚠️ GUI Screens Not Implemented

- Garage/workshop management (not built)
- Component/vehicle health tracking (not built)
- Log viewer diagnostics tool (not built)
- **Note**: Core playable race visualization works in `gui_race_visual.py`

### ⚠️ Track Data Integration Status

- ✅ Schema designed in `database/models.py`
- ✅ 175 circuits defined in `data/circuits_database.json`
- ❌ Import tool exists but not executed
- ⚠️ **Required for full gameplay**

## Critical Code Patterns

### Discipline Implementation

**Always inherit from** `BaseDisciplineEngine`:

```python
from RaceLogic.base_race_engine import BaseDisciplineEngine

class SingleSeaterEngine(BaseDisciplineEngine):
    def calculate_performance(self, context) -> float:
        # 40% driver, 30% team, 20% env, 10% random
        ...
  
    def simulate_race_result(self, context) -> RaceResult:
        # Monte Carlo simulation
        ...
```

**Module Path Pattern**: `RaceLogic.disciplines.{discipline_name}.{discipline_name}_discipline`

### Accessing Database

```python
from database.database_manager import DatabaseManager
from config import DATABASE_PATH

db = DatabaseManager()
drivers = db.get_all_drivers()
team = db.get_team_by_id(team_id)
```

### Loading Discipline Dynamically

```python
from services.race_simulation_api import _load_discipline_engine

discipline = "SINGLE_SEATER"
engine = _load_discipline_engine(context)  # Auto-selects correct discipline
```

### Driver Attributes (0-100 scale)

Each discipline uses different key attributes:

**Single Seater**: `qualifying_pace`, `raw_speed`, `aerodynamics_understanding`, `racecraft`

**Urban/Street (Drift)**: `drift_control`, `car_control`, `consistency`, `reactions`

**Endurance**: `tire_management`, `fuel_management`, `consistency`, `mechanical_sympathy`

**Drag**: `reaction_time`, `acceleration_control`, `starting_skill`

### Configuration Access

```python
from config import DATABASE_PATH, DEFAULT_CURRENCY, MONTE_CARLO_ITERATIONS

# Always use config imports, never hardcode paths
if not os.path.exists(DATABASE_PATH):
    raise FileNotFoundError(f"Database not found at {DATABASE_PATH}")
```

## File Organization

- **Race Simulation**: `RaceLogic/` + `services/race_simulation_api.py`
- **Game Management**: `services/championship_service.py`, `progression_service.py`
- **Database**: `database/` (models, manager, factory)
- **API Server**: `simulation.py` (FastAPI app)
- **GUI**: `GUI/launcher.py` (entry point), `GUI/gui_*.py` (screens)
- **Tests**: `tests/test_*.py` (pytest format)
- **Configuration**: `config.py` (env vars)

## When Adding/Modifying Code

### Adding a New Discipline

1. Create file in `RaceLogic/disciplines/{name}/{name}_discipline.py`
2. Inherit from `BaseDisciplineEngine`
3. Implement `calculate_performance()` and `simulate_race_result()`
4. Update enum if needed (currently 6 disciplines hardcoded)

### Adding a Database Model

1. Define dataclass in `database/models.py`
2. Add schema to `models.py` SQL definition
3. Implement in `database_manager.py` CRUD methods
4. Test with `tests/test_integration_database_layer.py`

### Adding API Endpoint

1. Add method to `simulation.py`
2. Use `@app.get()` or `@app.post()` decorator
3. Include try/except with `HTTPException` for errors
4. Document in this file

### Adding GUI Screen

1. Create `GUI/gui_screen_name.py`
2. Inherit from PyQt6 QMainWindow or QWidget
3. Call from `GUI/launcher.py` or navigation
4. Test with `pytest tests/test_unit_gui_launcher_smoke.py`

### Running/Debugging

```powershell
# Backend
python -m uvicorn simulation:app --reload

# GUI
python GUI/launcher.py

# Tests
pytest tests -v

# Quick diagnostics
python mvp_tests/quick_check.py
```

## Project Documentation

- **Technical Design**: `Planning/Design and Architecture/`
- **Game Design**: `Planning/GAME_DESIGN_DOCUMENT.md`
- **Requirements**: `Planning/Requirements/`
- **Use Cases**: `Planning/UseCases/`
- **Testing Plan**: `Planning/Testing/Plan.md`
- **Technical Report**: `Planning/Technical Report/`
- **API Math**: `Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md`
- **Championship Rules**: `Momentum/Python/docs/CHAMPIONSHIP_MANAGEMENT.md`

## Discipline Enum Reference

```python
# Use these strings for discipline identification
SINGLE_SEATER = "SINGLE_SEATER"
PRODUCTION_TOURING = "PRODUCTION_TOURING"
URBAN_STREET = "URBAN_STREET"  # Drifting
DRAG_ACCELERATION = "DRAG_ACCELERATION"
SPRINT_RALLYCROSS = "SPRINT_RALLYCROSS"
ENDURANCE = "ENDURANCE"

# NOT USED: RALLY_STAGE (removed due to complexity)
```

---

**Last Updated**: April 2026 | **Project Status**: 70% Backend Playable, 60% GUI Complete | **Disciplines**: 6/6 Implemented
