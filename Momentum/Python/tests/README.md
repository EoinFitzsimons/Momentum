# Momentum Backend Test Suite

This test suite is designed to be explainable in the technical report and traceable to project quality goals.

## Structure

- `conftest.py`
  - Deterministic fixtures
  - Isolated temp SQLite DB per test
  - Seeded reference data
  - FastAPI `TestClient` patched to test DB

- `test_unit_track_surface_service.py`
  - Unit tests for discipline-to-surface and grip mapping rules

- `test_unit_championship_rules.py`
  - Unit tests for points system logic

- `test_integration_database_layer.py`
  - CRUD and persistence integration tests for database manager

- `test_integration_api_contracts.py`
  - Endpoint contract tests for `/health`, `/drivers`, `/teams`, `/teams/me`

- `test_integration_championship_flow.py`
  - Championship calendar creation, race lifecycle, standings recalculation

## Why this suite is report-friendly

- Every test has a clear single purpose and deterministic expected outcome.
- Integration tests validate real interfaces, not synthetic mock dictionaries.
- Temporary databases avoid cross-test contamination and make runs reproducible.
- Test categories (`unit`, `integration`) map to the testing plan sections.

## Suggested Runs

- Full suite:
  - `pytest Momentum/Python/tests -q`

- Unit only:
  - `pytest Momentum/Python/tests -m unit -q`

- Integration only:
  - `pytest Momentum/Python/tests -m integration -q`
