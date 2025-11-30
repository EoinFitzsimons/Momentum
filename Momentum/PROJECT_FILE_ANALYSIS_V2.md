# Momentum — Comprehensive File Analysis (Organized by Architecture)

> **Last Updated:** October 23, 2025  
> **Purpose:** Complete per-file analysis organised by architectural layer to understand the codebase structure and identify next steps.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Summary](#architecture-summary)
3. [File Analysis by Layer](#file-analysis-by-layer)
   - [Layer 1: Configuration & Constants](#layer-1-configuration--constants)
   - [Layer 2: Domain Models](#layer-2-domain-models)
   - [Layer 3: Data Access Layer](#layer-3-data-access-layer)
   - [Layer 4: Core Systems](#layer-4-core-systems)
   - [Layer 5: Simulation Engines](#layer-5-simulation-engines)
   - [Layer 6: API Layer](#layer-6-api-layer)
   - [Layer 7: Utilities & Scripts](#layer-7-utilities--scripts)
   - [Layer 8: Tests](#layer-8-tests)
   - [Layer 9: Documentation](#layer-9-documentation)
4. [Cross-Cutting Concerns](#cross-cutting-concerns)
5. [Technical Debt Summary](#technical-debt-summary)
6. [Next Steps Recommendations](#next-steps-recommendations)

---

## Project Overview

**Momentum** is a multi-discipline motorsport management simulation system featuring:
- Monte Carlo race simulation across 7+ racing disciplines
- SQLite persistence with comprehensive domain models
- FastAPI REST API for simulation execution
- Intelligent procedural content generation (drivers, teams, staff)
- Unity front-end integration (in progress)

**Key Technologies:** Python 3.x, FastAPI, SQLite, NumPy, Faker, Unity (C#)

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│                       simulation.py                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Core Systems Layer                        │
│  championship_manager, currency_system, staff_management,   │
│  vehicle_development, supplier_management, name_generator   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Simulation Engines Layer                    │
│  race_simulation.py, base_engine.py, multi_discipline_sim   │
│  + 7 discipline-specific engines (single_seater, rally...)   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Domain Models Layer                       │
│  Driver, Team, Track, Race, RaceResult, Vehicle, Staff...   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Data Access Layer (DAL)                     │
│           database_manager.py, database_factory.py           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     SQLite Database                          │
│                      momentum.db                             │
└─────────────────────────────────────────────────────────────┘
```

---

## File Analysis by Layer

### Layer 1: Configuration & Constants

#### `config.py`

**Purpose:** Central configuration hub containing all constants, attribute definitions, and domain enumerations.

**Responsibilities:**
- Database path configuration (`MOMENTUM_DB_PATH`)
- Monte Carlo simulation parameters (`MONTE_CARLO_ITERATIONS`, `RANDOM_SEED`)
- Driver attribute lists (50+ attributes across physical, mental, technical categories)
- Discipline registry and mappings
- Currency configurations
- Global feature flags

**Interactions:**
- Imported by: ALL modules (simulation.py, engines, database_manager, systems)
- Dependencies: None (pure configuration)

**Issues:**
- Large monolithic config file (~500+ lines)
- Mixing of different concern types (DB paths, simulation params, domain data)
- Hard-coded attribute lists may become stale

**Suggestions:**
- ✅ Split into separate configs: `database_config.py`, `simulation_config.py`, `domain_config.py`
- ✅ Move environment-specific values to `.env` file
- ✅ Add validation for attribute name consistency
- ✅ Document attribute ranges and units

**Priority:** HIGH (foundational to entire system)

---

### Layer 2: Domain Models

#### `database/models.py`

**Purpose:** Core domain model dataclasses and database schema definitions.

**Responsibilities:**
- Defines dataclasses: `Driver`, `Team`, `Track`, `Championship`, `Race`, `RaceResult`
- Contains `SCHEMA_SQL` for SQLite table creation
- Provides data validation and default values
- Maps database rows to Python objects

**Key Classes:**
```python
- Driver: 50+ attributes (ratings, specializations, nationality)
- Team: budget, discipline, staff, performance metrics
- Track: layout, surface, characteristics, discipline suitability
- Race: event definition linking track, discipline, participants
- RaceResult: finishing positions, times, points, incidents
- Championship: season structure, points system, standings
```

**Interactions:**
- Used by: database_manager (CRUD operations), engines (simulation input)
- Imports: None (pure domain)

**Issues:**
- ⚠️ Mixing dataclasses with SQL schema definitions (separation of concerns)
- ⚠️ Schema is embedded as string literals (hard to maintain)
- ⚠️ No migration strategy for schema changes
- ⚠️ Some validation logic missing (e.g., rating bounds)

**Suggestions:**
- 🔧 Extract `SCHEMA_SQL` to separate `schema.sql` file or use Alembic migrations
- 🔧 Add `@dataclass` validation using `__post_init__` for rating bounds
- 🔧 Consider splitting into smaller model files (driver_models.py, race_models.py)
- 🔧 Add JSON serialization helpers for API responses

**Priority:** HIGH (core domain)

---

#### `database/models/multi_discipline_models.py`

**Purpose:** Extended domain models for multi-discipline functionality.

**Responsibilities:**
- `MultiDisciplineDriver`: cross-discipline skill tracking
- `MultiDisciplineTeam`: multi-category team operations
- `Vehicle`: generic vehicle model with discipline-specific configs
- Extended `Track` and `Championship` models

**Interactions:**
- Used by: multi_discipline_simulator.py, championship_manager.py
- Imports: base models.py

**Issues:**
- Some duplication with base models.py
- Unclear boundary between base and multi-discipline models

**Suggestions:**
- 🔧 Clarify inheritance/composition strategy
- 🔧 Document when to use base vs multi-discipline models

**Priority:** MEDIUM

---

#### `database/models/staff_models.py`

**Purpose:** Staff and personnel domain models.

**Responsibilities:**
- `StaffMember`: roles, skills, salaries, attributes
- `TeamStaffing`: staff composition and budget allocation
- Enums: `StaffRole`, `StaffTier`, `BudgetCategory`
- Helper functions: `generate_staff_requirements()`, `calculate_role_importance()`

**Key Entities:**
- Staff roles: Technical Director, Chief Engineer, Data Analyst, Strategist, Pit Crew
- Tier system: Budget, Midfield, Top Team, Elite
- Skill categories: Technical, Leadership, Experience

**Interactions:**
- Used by: staff_management.py, championship_manager.py
- Imports: base models

**Issues:**
- Helper functions mixed with models (should be in systems layer)
- Staff progression system not fully implemented

**Suggestions:**
- 🔧 Move helper functions to `systems/staff_management.py`
- 🔧 Add staff development/training mechanics
- 🔧 Implement staff morale and performance tracking

**Priority:** MEDIUM

---

#### `database/models/supplier_models.py`

**Purpose:** Supplier and procurement domain models.

**Responsibilities:**
- `Supplier`: name, category, tier, pricing, quality ratings
- `ComponentContract`: pricing, delivery terms, performance bonuses
- Enums: `SupplierCategory` (Engine, Chassis, Electronics, Tire)
- Tier system and quality impact calculations

**Interactions:**
- Used by: supplier_management.py, vehicle_development.py
- Imports: base models

**Issues:**
- Supplier catalog not fully populated
- Contract negotiation mechanics incomplete

**Suggestions:**
- 🔧 Add supplier reputation and relationship tracking
- 🔧 Implement dynamic pricing based on performance
- 🔧 Add exclusive supplier deals and partnerships

**Priority:** LOW (feature expansion)

---

#### `vehicles/vehicle.py`

**Purpose:** Vehicle domain model with component composition.

**Responsibilities:**
- `RaceCar` class: composite vehicle with components
- Component integration: aerodynamics, chassis, engine, electronics, drivetrain
- Performance calculations: power-to-weight, overall condition, compliance
- Damage simulation and maintenance tracking

**Key Methods:**
```python
- get_total_power() -> float
- get_power_to_weight_ratio() -> float
- get_overall_condition() -> float
- simulate_session(duration, intensity)
- apply_crash_damage(severity)
- check_discipline_compliance() -> bool
```

**Interactions:**
- Used by: engines (performance evaluation), vehicle_development.py
- Imports: component classes from vehicles/components/

**Issues:**
- ⚠️ Performance calculations may be better in engine layer
- ⚠️ Damage model is simplified (no component-specific damage)
- ⚠️ Setup/tuning system not implemented

**Suggestions:**
- 🔧 Extract performance calculations to discipline engines
- 🔧 Add vehicle setup system (aero balance, suspension, gearing)
- 🔧 Implement component-specific wear and failure modes
- ✅ Add unit tests for component interactions

**Priority:** MEDIUM

---

#### `vehicles/components/` (6 files)

**Component Files:**
1. `enums.py`: All component-related enumerations
2. `engine.py`: Engine and hybrid power unit models
3. `aerodynamics.py`: Aero packages, wings, tires
4. `chassis.py`: Chassis, suspension, brakes
5. `drivetrain.py`: Gearbox, differential, drivetrain
6. `electronics.py`: ECU, steering, safety systems

**Common Pattern for All Components:**
```python
- Component class with attributes (performance, reliability, cost)
- Performance contribution methods
- Wear/degradation tracking
- Discipline-specific validation
- Upgrade path definitions
```

**Issues:**
- ⚠️ Component interactions not fully modeled
- ⚠️ Upgrade costs and development time not integrated
- ⚠️ Some discipline-specific logic leaking into components

**Suggestions:**
- 🔧 Keep components generic, discipline logic in engines
- 🔧 Add component compatibility matrix
- 🔧 Implement component synergy bonuses
- ✅ Add component test fixtures

**Priority:** MEDIUM (per-component analysis available if needed)

---

### Layer 3: Data Access Layer

#### `database/database_manager.py`

**Purpose:** Centralized database access layer providing CRUD operations for all entities.

**Responsibilities:**
- SQLite connection management
- CRUD operations for: drivers, teams, tracks, races, results, championships
- Row-to-dataclass mapping
- Query execution and error handling
- Transaction management (partial)

**Key Methods:**
```python
# Drivers
- get_driver(driver_id) -> Driver
- get_all_drivers() -> List[Driver]
- add_driver(driver) -> int
- update_driver(driver)

# Teams
- get_team(team_id) -> Team
- get_teams_by_discipline(discipline) -> List[Team]
- add_team(team) -> int

# Races
- get_race(race_id) -> Race
- create_race(race) -> int
- save_race_result(result)
- get_results_for_race(race_id) -> List[RaceResult]

# Tracks
- get_track(track_id) -> Track
- get_all_tracks() -> List[Track]
```

**Interactions:**
- Used by: simulation.py, generate_initial_database.py, ALL systems
- Imports: models.py, config.py

**Issues:**
- ⚠️ **Monolithic class with 40+ methods** (violates Single Responsibility)
- ⚠️ **Direct SQL string concatenation** (SQL injection risk in some methods)
- ⚠️ **No connection pooling** (creates new connection per operation)
- ⚠️ **Inconsistent error handling** (some methods fail silently)
- ⚠️ **No transaction support** across operations
- ⚠️ **Missing methods** (e.g., get_track was added later)

**Suggestions:**
- 🔥 **CRITICAL:** Split into repository pattern (DriverRepository, TeamRepository, etc.)
- 🔥 **CRITICAL:** Add proper parameterized queries everywhere
- 🔧 Implement connection pooling or context managers
- 🔧 Add transaction decorators for atomic operations
- 🔧 Add comprehensive error handling and logging
- ✅ Add integration tests for all CRUD operations

**Priority:** CRITICAL (foundational infrastructure)

---

#### `database/database_factory.py`

**Purpose:** Database initialization and schema creation utility.

**Responsibilities:**
- Create SQLite database file
- Execute schema SQL from models.py
- Initialize empty database structure
- Provide factory methods for test databases

**Key Methods:**
```python
- create_database(db_path) -> None
- initialize_schema(connection) -> None
- create_in_memory_db() -> Connection (for tests)
```

**Interactions:**
- Used by: generate_initial_database.py, test setup
- Imports: models.py (for SCHEMA_SQL)

**Issues:**
- Simple but functional
- No migration support
- No version tracking

**Suggestions:**
- 🔧 Add database version table
- 🔧 Implement basic migration system or integrate Alembic
- ✅ Add schema validation on startup

**Priority:** LOW (works but could be enhanced)

---

### Layer 4: Core Systems

#### `systems/intelligent_name_generator.py`

**Purpose:** Procedural name generation with cultural accuracy and uniqueness tracking.

**Responsibilities:**
- Generate culturally accurate driver/staff names using Faker
- Locale mapping (40+ countries/nationalities)
- Uniqueness tracking via SQLite (`used_names.db`)
- Gender-aware name generation
- Team name generation

**Key Features:**
- Locale fallback chain (specific → region → generic)
- Script support: Latin, Cyrillic, Kanji, Arabic, etc.
- Deterministic mode with seed support
- Collision detection and retry logic

**Key Methods:**
```python
- generate_driver_name(nationality, gender) -> dict
- generate_team_name(category, tier) -> str
- is_name_used(name) -> bool
- mark_name_used(name)
```

**Interactions:**
- Used by: generate_initial_database.py, staff_management.py
- Imports: Faker, SQLite

**Issues:**
- ✅ Well-implemented and robust
- Minor: used_names.db in repo (should be generated artifact)

**Suggestions:**
- ✅ Already excellent, minimal changes needed
- 🔧 Add batch generation mode for performance
- 🔧 Move used_names.db to .gitignore

**Priority:** LOW (already high quality)

---

#### `systems/staff_management.py`

**Purpose:** Staff hiring, assignment, and performance management system.

**Responsibilities:**
- Staff market simulation
- Hiring and firing mechanics
- Salary calculation and negotiation
- Staff assignment to roles
- Performance impact calculations
- Staff development and training

**Key Classes:**
```python
- StaffMarket: available staff pool, market dynamics
- StaffManagementSystem: team staffing operations
```

**Key Methods:**
```python
- generate_available_staff(count, tiers)
- hire_staff(team_id, staff_member)
- fire_staff(team_id, staff_id)
- calculate_staff_impact(staffing) -> performance_modifier
- assign_staff_to_role(staff_id, role)
```

**Interactions:**
- Uses: intelligent_name_generator, staff_models, database_manager
- Used by: championship_manager, simulation.py

**Issues:**
- Staff market not fully dynamic
- Training/development incomplete
- Morale system missing

**Suggestions:**
- 🔧 Add staff contract system (length, buyout clauses)
- 🔧 Implement staff poaching mechanics
- 🔧 Add staff specialization trees
- ✅ Add tests for salary calculations

**Priority:** MEDIUM

---

#### `systems/supplier_management.py`

**Purpose:** Supplier catalog, procurement, and contract management.

**Responsibilities:**
- Supplier database and catalog
- Component procurement
- Contract negotiation
- Pricing and quality tier system
- Supplier relationship tracking

**Key Class:**
```python
- SupplierManager: procurement operations
```

**Key Methods:**
```python
- get_available_suppliers(category) -> List[Supplier]
- negotiate_contract(supplier_id, terms)
- purchase_component(supplier_id, component_type)
- calculate_delivery_time(supplier_tier)
```

**Interactions:**
- Uses: supplier_models, currency_system, database_manager
- Used by: vehicle_development.py

**Issues:**
- Supplier catalog sparsely populated
- Contract mechanics simplified
- No exclusivity or partnership deals

**Suggestions:**
- 🔧 Expand supplier catalog with real-world inspired suppliers
- 🔧 Add supplier reputation system
- 🔧 Implement multi-year exclusive deals
- 🔧 Add component delivery delays and quality variance

**Priority:** LOW (feature expansion)

---

#### `systems/vehicle_development.py`

**Purpose:** Vehicle upgrade and development point allocation system.

**Responsibilities:**
- Development point (DP) system
- Component upgrade paths
- Resource allocation (budget + DP)
- Development project tracking
- Performance gain calculations

**Key Classes:**
```python
- DevelopmentProject: upgrade in progress
- VehicleDevelopmentEngine: development orchestrator
```

**Key Methods:**
```python
- start_development_project(component, target_level)
- allocate_resources(project_id, dp_amount, budget)
- complete_project() -> upgraded_component
- calculate_development_time(complexity, resources)
```

**Interactions:**
- Uses: vehicle models, supplier_management, currency_system
- Used by: championship_manager (season progression)

**Issues:**
- Development time simulation not integrated with calendar
- No risk of development failures
- Component synergies not modeled

**Suggestions:**
- 🔧 Add development risk/reliability trade-offs
- 🔧 Implement diminishing returns on upgrades
- 🔧 Add component testing phase before race deployment
- 🔧 Link to calendar system for time-based development

**Priority:** MEDIUM

---

#### `systems/currency_system.py`

**Purpose:** Multi-currency financial system with conversion and budget management.

**Responsibilities:**
- Currency conversion (EUR, USD, GBP, JPY, etc.)
- Exchange rate caching (`currency_cache.json`)
- Budget calculations and tracking
- Financial transactions
- Budget cap enforcement (e.g., F1-style caps)

**Key Classes:**
```python
- Currency(Enum): supported currencies
- CurrencyConfig: conversion rates, cache settings
- CurrencySystem: financial operations
```

**Key Methods:**
```python
- convert(amount, from_currency, to_currency) -> float
- format_currency(amount, currency) -> str
- check_budget_cap_compliance(team_budget, discipline)
- apply_expenditure(team_id, amount, category)
```

**Interactions:**
- Uses: currency_cache.json (external API or static rates)
- Used by: supplier_management, vehicle_development, staff_management

**Issues:**
- Exchange rates may be outdated (cache strategy unclear)
- Budget tracking not integrated with calendar
- No inflation or market fluctuations

**Suggestions:**
- 🔧 Document cache refresh strategy
- 🔧 Add budget history tracking
- 🔧 Implement sponsor income system
- ✅ Add currency conversion tests

**Priority:** LOW

---

#### `systems/championship_manager.py`

**Purpose:** Championship orchestration, season calendar, standings, and driver contracts.

**Responsibilities:**
- Championship points calculation
- Standings updates
- Driver contracts and transfer system
- Season calendar management
- Promotion/relegation logic
- Transfer windows

**Key Classes:**
```python
- ChampionshipManager: season orchestration
- TransferMarket: driver trading system
- SeasonCalendar: event scheduling
- DriverContract: contract terms and status
```

**Key Methods:**
```python
- calculate_points(position, points_system) -> int
- update_standings(race_results)
- process_driver_transfer(driver_id, from_team, to_team)
- open_transfer_window(window_type)
- check_contract_expiry(season_end_date)
```

**Interactions:**
- Uses: ALL systems (orchestrator role)
- Used by: simulation.py, season progression scripts

**Issues:**
- ⚠️ Season progression not fully automated
- ⚠️ Contract negotiation simplified
- ⚠️ Multi-season persistence unclear

**Suggestions:**
- 🔧 Add full season simulation mode
- 🔧 Implement contract negotiation AI
- 🔧 Add driver retirement and rookie promotion
- 🔧 Link to calendar system for race scheduling

**Priority:** HIGH (key gameplay system)

---

### Layer 5: Simulation Engines

#### `disciplines/base_engine.py`

**Purpose:** Base class and shared utilities for all discipline-specific engines.

**Responsibilities:**
- Abstract base class defining engine interface
- Shared performance calculation helpers
- RNG utilities (now modernized with numpy.random.Generator)
- Reliability and incident calculations
- Common race state management

**Key Classes/Functions:**
```python
- RacingDiscipline(Enum): discipline types
- RaceEventType(Enum): practice, qualifying, race
- DisciplineContext: simulation parameters
- BaseDisciplineEngine(ABC): base engine class
```

**Abstract Methods:**
```python
- calculate_base_performance(driver, vehicle, track, rng)
- simulate_session(context, drivers, vehicles, track)
- apply_discipline_modifiers(base_performance, context)
```

**Shared Utilities:**
```python
- generate_incident(probability, rng) -> bool
- calculate_reliability_failure(component_condition, rng)
- normalize_attributes(driver, scale)
```

**Interactions:**
- Extended by: All 7 discipline engines
- Used by: race_simulation.py

**Issues:**
- ✅ Recently modernized (RNG, type hints)
- Some complexity in shared calculations

**Suggestions:**
- ✅ Keep as stable base
- 🔧 Add more shared utilities to reduce engine duplication
- ✅ Add unit tests for helper functions

**Priority:** LOW (already well-structured)

---

#### `disciplines/race_simulation.py`

**Purpose:** Monte Carlo race simulator orchestrating multiple simulation iterations.

**Responsibilities:**
- Run N iterations of race simulation (default: 1000)
- Aggregate positional probability distributions
- Calculate expected finishing positions
- Incident and DNF probability tracking
- Performance variance modeling

**Key Classes:**
```python
- SimulationContext: parameters for simulation run
- RaceSimulator: Monte Carlo orchestrator
```

**Key Methods:**
```python
- simulate_race(context, drivers, teams, track) -> RaceResult
- run_single_iteration(context, rng) -> finishing_order
- aggregate_results(iterations) -> probability_distribution
- calculate_expected_positions(distribution) -> List[position]
```

**Workflow:**
```
1. Build simulation context
2. For i in range(MONTE_CARLO_ITERATIONS):
   a. Get discipline engine
   b. Run single race iteration
   c. Record finishing order
3. Aggregate probability distribution
4. Calculate expected positions
5. Return RaceResult with probabilities
```

**Interactions:**
- Uses: discipline engines, base_engine
- Used by: simulation.py (API), multi_discipline_simulator

**Issues:**
- ⚠️ Some coupling with specific discipline logic
- ⚠️ Performance with high iteration counts
- RNG modernization needed (now uses legacy random)

**Suggestions:**
- 🔥 **Inject numpy.random.Generator instance** (like base_engine)
- 🔧 Add iteration count as parameter (not hard-coded)
- 🔧 Add progress reporting for long simulations
- ✅ Add deterministic tests with known seed

**Priority:** HIGH (core simulation)

---

#### `disciplines/multi_discipline_simulator.py`

**Purpose:** High-level coordinator for multi-discipline races and engine selection.

**Responsibilities:**
- Select appropriate engine based on discipline
- Route simulation requests to correct engine
- Handle multi-discipline events (if supported)
- Aggregate cross-discipline results

**Key Class:**
```python
- MultiDisciplineSimulator: engine router
```

**Key Methods:**
```python
- simulate_race(race, drivers, teams, track) -> RaceResult
- get_engine_for_discipline(discipline) -> BaseDisciplineEngine
- validate_discipline_compatibility(race, track)
```

**Interactions:**
- Uses: all discipline engines, race_simulation.py
- Used by: simulation.py

**Issues:**
- Potential duplication with race_simulation.py
- Unclear if this is needed (single orchestrator?)

**Suggestions:**
- 🔧 Clarify role vs race_simulation.py
- 🔧 Consider merging into single orchestrator
- 🔧 Or make this the primary orchestrator with race_simulation as helper

**Priority:** MEDIUM (architectural clarity)

---

#### Discipline-Specific Engines (7 engines)

Each discipline has 3 files: `engine.py`, `rulebook.py`, `discipline_config.py`

**Disciplines:**
1. **Single Seater** (`single_seater/`)
2. **Rally Stage** (`rally_stage/`)
3. **Endurance** (`endurance/`)
4. **Production Touring** (`production_touring/`)
5. **Drag/Acceleration** (`drag_acceleration/`)
6. **Sprint Rallycross** (`sprint_rallycross/`)
7. **Urban Street** (`urban_street/`)

**Common Pattern:**

**`*_engine.py`:** 
- Extends `BaseDisciplineEngine`
- Implements `calculate_base_performance()`
- Implements `simulate_session()` for practice/quali/race
- Applies discipline-specific modifiers (tire wear, fuel, etc.)

**`rulebook.py`:**
- Vehicle compliance validation
- Technical regulations
- Disqualification rules
- Class restrictions

**`discipline_config.py`:**
- Attribute weight configurations
- Session parameters (length, tire sets)
- Incident probabilities
- Performance modifiers

**Priority:** MEDIUM (individual engine review available on request)

**Common Issues Across All Engines:**
- Some code duplication in performance calculations
- Attribute normalization inconsistencies
- Direct database access in some engines (should use repositories)
- Testing coverage varies

**Common Suggestions:**
- 🔧 Extract common patterns to base_engine
- 🔧 Standardize attribute weighting format
- 🔧 Remove DB dependencies from engines (pure functions)
- ✅ Add per-engine unit tests with fixtures

---

### Layer 6: API Layer

#### `simulation.py`

**Purpose:** FastAPI application serving as the HTTP interface for the simulation backend.

**Responsibilities:**
- Define REST API endpoints
- Request/response validation
- Build simulation contexts from HTTP requests
- Orchestrate simulation calls
- Persist results to database
- Error handling and logging

**Endpoints:**
```python
GET  /              # Root info
GET  /health        # Health check
GET  /stats         # Database statistics
GET  /drivers       # List all drivers
GET  /teams         # List teams (optional discipline filter)
POST /simulate/race # Run race simulation
GET  /test          # Test endpoint
```

**Key POST `/simulate/race` Flow:**
```
1. Validate request JSON (discipline, race_id, drivers)
2. Fetch/create race from database
3. Fetch drivers, teams, track from database
4. Build SimulationContext
5. Call RaceSimulator.simulate_race()
6. Persist RaceResult to database
7. Return result JSON
```

**Interactions:**
- Uses: database_manager, race_simulation, championship_manager, config
- Used by: Unity front-end, API clients

**Issues:**
- ⚠️ **CRITICAL: Mixed concerns** (presentation + orchestration + data access)
- ⚠️ **High cognitive complexity** in simulate_race endpoint
- ⚠️ Attribute normalization done in API layer (should be in engine)
- ⚠️ Direct database calls (no repository abstraction)
- ⚠️ Limited error handling
- ⚠️ No request validation schemas (Pydantic models)

**Suggestions:**
- 🔥 **CRITICAL:** Extract orchestration to `services/simulation_service.py`
- 🔥 **CRITICAL:** Create Pydantic request/response models
- 🔧 Use repository pattern for data access
- 🔧 Add comprehensive error handling middleware
- 🔧 Add request logging and metrics
- 🔧 Add API versioning (/v1/simulate/race)
- ✅ Add integration tests with FastAPI TestClient

**Priority:** CRITICAL (main API interface)

---

### Layer 7: Utilities & Scripts

#### `generate_initial_database.py`

**Purpose:** Procedural content generation script to populate initial database with realistic data.

**Responsibilities:**
- Generate drivers (500+) across all disciplines and nationalities
- Generate teams (100+) with budgets and characteristics
- Generate tracks (50+) with varied layouts and surfaces
- Generate staff members
- Populate initial database schema

**Key Class:**
```python
- DatabaseGenerator: content generation orchestrator
```

**Generation Process:**
```
1. Initialize database schema
2. Generate drivers by nationality and discipline
3. Generate teams by tier and discipline
4. Generate tracks by discipline and region
5. Generate staff pool
6. Assign initial team compositions
7. Generate database_generation_report.txt
```

**Interactions:**
- Uses: intelligent_name_generator, database_manager, database_factory
- Writes to: momentum.db

**Issues:**
- Ad-hoc generation logic (could be more configurable)
- No deterministic seed option exposed
- Direct database writes (bypasses repository)
- Generation report as text file (not structured)

**Suggestions:**
- 🔧 Add CLI arguments for seed, counts, disciplines
- 🔧 Make generation deterministic with --seed flag
- 🔧 Output JSON report for programmatic validation
- 🔧 Add verification tests (count checks, constraint validation)
- ✅ Add to README quickstart

**Priority:** MEDIUM

**CLI Suggestion:**
```bash
python generate_initial_database.py --seed 42 --drivers 500 --teams 100 --output report.json
```

---

#### `test_gen.py`

**Purpose:** Ad-hoc testing script for name generation.

**Status:** Utility script, likely outdated

**Suggestions:**
- 🔧 Move stable examples to `examples/`
- 🔧 Convert to proper pytest tests
- ⚠️ Consider removing if obsolete

**Priority:** LOW

---

#### `test_names.py`

**Purpose:** Name generation testing.

**Suggestions:**
- 🔧 Convert to pytest in `tests/`
- ✅ Use ephemeral database for tests

**Priority:** LOW

---

#### `test_cultural_names.py`

**Purpose:** Test culturally accurate name generation (Cyrillic, Kanji, diacritics).

**Suggestions:**
- 🔧 Convert to pytest
- ✅ Add parametrized tests per locale

**Priority:** LOW

---

### Layer 8: Tests

#### `tests/test_driver_system.py`

**Purpose:** Unit tests for driver attribute and progression logic.

**Status:** Class-based test runner (not pytest)

**Suggestions:**
- 🔧 Convert to pytest with fixtures
- ✅ Add parametrized tests for edge cases
- ✅ Use in-memory DB

**Priority:** MEDIUM

---

#### `tests/test_staff_system.py`

**Purpose:** Staff management tests.

**Status:** Class-based test runner

**Suggestions:**
- 🔧 Convert to pytest
- ✅ Add salary calculation tests

**Priority:** MEDIUM

---

#### `tests/simple_driver_test.py`

**Purpose:** Basic driver smoke tests.

**Suggestions:**
- 🔧 Merge into test_driver_system.py
- 🔧 Convert to pytest

**Priority:** LOW

---

#### `tests/examples/driver_examples.py`

**Purpose:** Example driver creation scripts.

**Status:** Good examples but not tests

**Suggestions:**
- ✅ Keep as examples
- 🔧 Add deterministic seed
- 🔧 Move to top-level `examples/`

**Priority:** LOW

---

### Layer 9: Documentation

#### `README.md`

**Purpose:** Project onboarding and setup instructions.

**Current State:** Basic instructions

**Suggestions:**
- 🔥 **Add Quickstart section** (task #4 in todo)
- ✅ Add prerequisites
- ✅ Add one-command demo
- ✅ Link to API docs (/docs)

**Priority:** HIGH (task #4)

---

#### `API_DOCUMENTATION.md`

**Purpose:** Manual API documentation.

**Suggestions:**
- 🔧 Link to FastAPI auto-generated docs
- 🔧 Add example requests/responses
- ✅ Keep sample payloads

**Priority:** MEDIUM

---

#### `API_KEY_SECURITY.md`

**Purpose:** API key usage and security guidance.

**Status:** Good practice doc

**Priority:** LOW

---

#### `CLEANUP_SUMMARY.md`

**Purpose:** Historical cleanup notes.

**Suggestions:**
- 🔧 Move to docs/ or archive

**Priority:** LOW

---

#### `docs/` folder files:

- `NAME_GENERATION_SOLUTION.md`: ✅ Good design doc
- `driver_system_summary.md`: ✅ Good design doc (needs MD lint fixes)
- `CLEANUP_NAMEAPI_PARANAMES.md`: Archive candidate

---

#### `database_generation_report.txt`

**Purpose:** Generation run artifact.

**Suggestions:**
- 🔧 Move to .gitignore
- 🔧 Generate as JSON

**Priority:** LOW

---

## Cross-Cutting Concerns

### 1. Testing Strategy

**Current State:**
- ⚠️ Class-based test runners (not pytest)
- ⚠️ Tests may modify production DB
- ⚠️ Limited coverage
- ⚠️ Non-deterministic tests (no seed control)

**Recommendations:**
- 🔥 Convert all tests to pytest
- 🔥 Use fixtures for database and RNG
- 🔥 Add in-memory SQLite for tests
- ✅ Add CI/CD pipeline (GitHub Actions)
- ✅ Target 70%+ coverage on core systems

**Priority:** CRITICAL (task #3)

---

### 2. Database Architecture

**Current Issues:**
- ⚠️ Monolithic database_manager
- ⚠️ No connection pooling
- ⚠️ No transaction management
- ⚠️ SQL injection risk in some queries
- ⚠️ No migration system

**Recommendations:**
- 🔥 Implement Repository pattern
- 🔥 Add parameterized queries everywhere
- 🔧 Add transaction context managers
- 🔧 Integrate Alembic for migrations
- ✅ Add database connection pool

**Priority:** CRITICAL

---

### 3. Configuration Management

**Current Issues:**
- ⚠️ Monolithic config.py
- ⚠️ No environment variable support
- ⚠️ Hard-coded paths

**Recommendations:**
- 🔧 Split config into domain-specific files
- 🔧 Add .env support (python-dotenv)
- 🔧 Add config validation
- ✅ Document all config options

**Priority:** MEDIUM

---

### 4. Error Handling

**Current State:**
- ⚠️ Inconsistent error handling
- ⚠️ Silent failures in some modules
- ⚠️ No logging framework

**Recommendations:**
- 🔧 Add Python logging throughout
- 🔧 Define custom exception hierarchy
- 🔧 Add error handling middleware in FastAPI
- ✅ Log all database operations

**Priority:** HIGH

---

### 5. Code Quality

**Issues:**
- ⚠️ No type hints in older code
- ⚠️ Inconsistent formatting
- ⚠️ Magic numbers and hard-coded values
- ⚠️ Long functions (cognitive complexity)

**Recommendations:**
- ✅ Add mypy for type checking
- ✅ Add black for formatting
- ✅ Add pylint/flake8 for linting
- 🔧 Refactor long functions
- 🔧 Extract magic numbers to constants

**Priority:** MEDIUM

---

## Technical Debt Summary

### Critical Issues (Fix Before Demo)
1. ⚠️ **simulation.py complexity** - refactor into service layer
2. ⚠️ **database_manager monolith** - split into repositories
3. ⚠️ **No test suite** - convert to pytest, add fixtures
4. ⚠️ **SQL injection risks** - parameterize all queries
5. ⚠️ **No error handling** - add logging and exception handling

### High Priority (Fix Soon)
6. ⚠️ **RNG modernization** in race_simulation.py
7. ⚠️ **No transaction management** - add DB transactions
8. ⚠️ **Configuration mess** - split config.py
9. ⚠️ **Championship manager incomplete** - season progression
10. ⚠️ **No API validation** - add Pydantic models

### Medium Priority (Post-Demo)
11. Vehicle setup/tuning system missing
12. Staff development incomplete
13. Supplier catalog sparse
14. Vehicle development not time-integrated
15. Multi-discipline simulator clarification

### Low Priority (Future)
16. Component synergies
17. Dynamic pricing
18. Staff morale tracking
19. Migration system
20. Performance optimization

---

## Next Steps Recommendations

Based on your todo list and codebase analysis, here's the recommended priority order:

### Phase 1: Critical Stabilization (Complete Tasks #2, #3)
**Goal:** Get a working, testable demo

1. **Fix simulation.py** (2-3 hours)
   - Extract service layer
   - Add Pydantic models
   - Clean up error handling

2. **Create minimal test suite** (2-3 hours)
   - Convert 1-2 key tests to pytest
   - Add database fixtures
   - Get one green test run

3. **Fix database_manager** (2-3 hours)
   - Parameterize queries
   - Add error handling
   - Add transaction support for race simulation

### Phase 2: Demo Preparation (Complete Task #4)
**Goal:** Make it easy to run

4. **Create quickstart README** (1 hour)
   - Add installation steps
   - Add one-command demo
   - Add troubleshooting

5. **Test end-to-end flow** (1 hour)
   - Fresh install test
   - Database generation
   - API call test
   - Document any failures

### Phase 3: Documentation (Complete Tasks #5, #6)
**Goal:** Prepare deliverables

6. **Technical report outline** (2-3 hours)
   - Map sections to code files
   - Extract key diagrams
   - Document design decisions

7. **Presentation prep** (2-3 hours)
   - Create slide outline
   - Prepare demo script
   - Take screenshots

### Phase 4: Unity Integration (Complete Task #9)
**Goal:** Show full stack

8. **Finalize Unity README** (mark task #9 complete)
9. **Optional: Create Unity scene** (2-3 hours if time)

### Phase 5: Polish (Optional Task #7)
10. **Record demo video** (1-2 hours)

---

## Estimated Time Breakdown

| Phase | Tasks | Time | Priority |
|-------|-------|------|----------|
| Phase 1: Stabilization | #2, #3 | 6-9 hours | CRITICAL |
| Phase 2: Demo | #4 | 2 hours | CRITICAL |
| Phase 3: Docs | #5, #6 | 4-6 hours | HIGH |
| Phase 4: Unity | #9 | 1-3 hours | MEDIUM |
| Phase 5: Video | #7 | 1-2 hours | OPTIONAL |
| **TOTAL** | | **14-22 hours** | |

---

## Questions for You

Before I proceed with detailed fixes, please answer:

1. **How much time do you have before submission?** (days/weeks)
2. **Is the Unity front-end required or nice-to-have?**
3. **Do you have any existing working demo?** (can you run the API now?)
4. **Which tasks are MUST-HAVE vs optional?**
5. **Do you want me to start with Phase 1 (stabilization)?**

Let me know and I'll create detailed fix plans for each priority area! 🚀
