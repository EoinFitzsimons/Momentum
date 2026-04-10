# Momentum Backend Tests

This folder contains the maintained automated tests for the Python backend.

## How the test setup works

- `conftest.py`
  - Creates a fresh temporary SQLite database for each test.
  - Seeds known teams, tracks, and drivers so tests are repeatable.
  - Patches the FastAPI app to use the temporary test database.

## What each test file checks

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

## Commands

- Run everything:

  - `pytest Momentum/Python/tests -q`
- Run only unit tests:

  - `pytest Momentum/Python/tests -m unit -q`
- Run only integration tests:

  - `pytest Momentum/Python/tests -m integration -q`
