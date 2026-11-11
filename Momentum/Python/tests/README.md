# Momentum Backend Tests

This folder contains the maintained automated tests for the Python backend.

## How the test setup works

- `conftest.py`
  - Creates a fresh temporary SQLite database for each test.
  - Seeds known teams, tracks, and drivers so tests are repeatable.
  - Patches the FastAPI app to use the temporary test database.

## Test Categories and Markers

Tests are organized by category using pytest markers:
- `@pytest.mark.unit` - Fast, isolated tests for deterministic business logic
- `@pytest.mark.integration` - Module/API/database interaction tests  
- `@pytest.mark.performance` - Timing and scalability benchmarks
- `@pytest.mark.slow` - Long-running tests not suited for every local run

## What each test file checks

### Unit Tests

- `test_unit_track_surface_service.py`
  - Checks that each discipline maps to the expected default surface.
  - Checks grip values for known and unknown surfaces.
  - Checks that track surfaces are only overwritten when appropriate.

- `test_unit_racelogic_discipline_loader.py`
  - Checks that dynamic discipline loading resolves the correct engine class for every discipline.
  - Checks that `simulate_race(context=...)` uses the discipline adapter path when available.

- `test_unit_racelogic_single_seater.py`
  - Checks single-seater attribute weights include core fields.
  - Checks the adapter forwards context values to the realtime engine.
  - Checks aggressive preset tuning is applied (for example, slipstream bonus).

- `test_unit_racelogic_production_touring.py`
  - Checks production touring adapter tuning and argument forwarding to realtime simulation.
  - Includes a placeholder test for deeper touring-specific behaviour as implementation grows.

- `test_unit_racelogic_urban_street.py`
  - Checks urban street adapter tuning and argument forwarding to realtime simulation.
  - Includes a placeholder test for future drift-specific scoring/judging behaviour.

- `test_unit_racelogic_sprint_rallycross.py`
  - Checks sprint rallycross adapter tuning and argument forwarding to realtime simulation.

- `test_unit_racelogic_endurance.py`
  - Checks endurance adapter tuning and argument forwarding to realtime simulation.
  - Includes a placeholder test for future stint/reliability-specific behaviour.

- `test_unit_racelogic_drag_acceleration.py`
  - Checks drag representative selection (one per team, including player override rules).
  - Checks head-to-head winner logic, including DNF/red-light handling.
  - Checks player pace/overtake overrides affect elapsed run time correctly.

- `test_unit_championship_rules.py`
  - Checks points allocation rules by discipline.
  - Checks fastest-lap bonus behaviour.
  - Checks out-of-range finishing positions return zero points.

- `test_unit_gui_launcher_smoke.py`
  - Checks launcher race-start wiring with stubs.
  - Checks returning to menu closes race window and shows main menu.
  - Checks menu signal flow can automatically start a race.

- `test_unit_career_season_service.py`
  - Checks season rollover and tier movement logic.
  - Checks promotion/relegation calculations for teams.

- `test_property_based_randomness.py`
  - Uses Hypothesis for property-based testing of performance calculations.
  - Verifies performance functions handle extreme attribute values without NaN/Inf.
  - Tests numeric stability with random input combinations.

- `test_discipline_edge_cases.py`
  - Tests numeric stability (no NaN/inf) under extreme attributes and weather conditions.
  - Verifies lap times remain non-negative across all disciplines.
  - Checks reasonable bounds under extreme inputs.

### Integration Tests

- `test_integration_database_layer.py`
  - Checks real create/read/update flows through the database manager.
  - Checks track updates persist.
  - Checks normalized discipline filtering and database stats responses.

- `test_integration_api_contracts.py`
  - Checks real FastAPI endpoint contracts for:
    - `/health`
    - `/drivers`
    - `/teams`
    - `/teams/me`
  - Checks expected status codes and response envelope shape.

- `test_integration_championship_flow.py`
  - Checks championship season creation and discipline surface assignment.
  - Checks race lifecycle transitions.
  - Checks standings recalculation and tie-break ordering.
  - Checks date-conflict validation for race events.

- `test_integration_full_career_season.py`
  - Runs a small full-season pipeline using seeded data.
  - Checks races are scheduled and completed.
  - Checks standings are produced and ranked.

- `test_use_case_coverage.py`
  - Maps tests to UC-1..UC-29 use case requirements.
  - Covers team creation/management workflows.
  - Covers staff hiring and contract flows.
  - Covers track creation and deletion with cascade behavior.
  - Covers vehicle appearance and team branding helpers.
  - Covers driver/staff generation and progression logic.

- `test_integration_srs.py`
  - Tests SRS requirements (R-SIM-002, R-DISC-001, R-EVT-001, R-FAIL-001).
  - Validates discipline adapter contracts.
  - Checks adapter instantiation and attribute weight retrieval.
  - Verifies event callback invocation.

- `test_simulation_reproducibility.py`
  - Tests R-SIM-001: Deterministic simulation reproducibility.
  - Verifies identical RaceContext + seed produce identical results.
  - Validates serialized events and standings consistency.

- `test_event_schema_emission.py`
  - Validates events emitted during realtime run against JSON schemas.
  - Verifies event envelope structure and required fields.
  - Checks event type validation against schema definitions.

### Database Integrity Tests

- `test_database_integrity.py`
  - Verifies foreign key constraints between drivers and teams.
  - Checks unique constraints are enforced where required.
  - Validates driver attributes remain within expected domains.
  - Verifies team budget values persist accurately.
  - Tests cascade delete behavior for championships and races.
  - Checks track discipline values are valid enum members.
  - Verifies no orphaned driver references to teams.
  - Validates race results reference valid drivers.

### Performance & Scalability Tests

- `test_performance.py`
  - Single race simulation: verifies completion within 1 second target.
  - Batch races (100): checks 30 second target for 100 race simulations.
  - Database query performance: verifies driver/team lookups under 100ms.
  - Bulk create performance: checks 50 driver insertions within 2 seconds.
  - Query consistency under load: verifies performance remains stable.
  - Race engine initialization: checks engine creation performance.
  - Tests marked with `@pytest.mark.performance` and `@pytest.mark.slow`.

### Statistical Validation Tests

- `test_statistical_validation.py`
  - Verifies skill attributes correlate with race finishing positions.
  - Validates upset race frequency is bounded within reasonable limits.
  - Checks lap time distributions are plausible.
  - Verifies determinism: same seed produces identical outcomes.
  - Validates different seeds produce varied race outcomes.
  - Tests track surface effects on driver performance.
  - Verifies long-distance races favor skilled drivers consistently.
  - Tests marked with `@pytest.mark.integration` and `@pytest.mark.slow`.

### Migration and Schema Tests

- `test_migration_tire_to_tyre.py`
  - Tests database migration script for tire→tyre column rename.
  - Verifies data preservation during schema changes.

## Running Tests

### Run everything:

```bash
pytest Momentum/Python/tests -q
```

### Run only unit tests:

```bash
pytest Momentum/Python/tests -m unit -q
```

### Run only integration tests:

```bash
pytest Momentum/Python/tests -m integration -q
```

### Run only performance tests:

```bash
pytest Momentum/Python/tests -m performance -q
```

### Run slow tests (long-running, for nightly/pre-release):

```bash
pytest Momentum/Python/tests -m slow -q
```

### Exclude slow tests (for quick local iterations):

```bash
pytest Momentum/Python/tests -m "not slow" -q
```

### Run with coverage:

```bash
pytest Momentum/Python/tests --cov=Momentum/Python --cov-report=html
```

## Test Output

- Reports and artifacts are stored in `Momentum/Python/tests/output/`
- Coverage reports are generated as HTML for detailed inspection
- Test logs are captured for debugging failed runs
