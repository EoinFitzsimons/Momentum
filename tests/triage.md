# Tests Triage

Purpose
- This file categorises the test files in `Momentum/Python/tests/` to guide a safe refactor. The goal is to keep the behavioural tests, convert demo scripts into pytest fixtures, and remove truly obsolete files.

How to use this file
- `Keep` = tests that should remain and be converted to automated pytest format if not already.
- `Convert` = useful scripts or examples that should be migrated to pytest functions or fixtures.
- `Remove` = obsolete or duplicated files safe to delete after verification.

Summary classification

- Keep
  - `test_game_loop_api.py` — API contract and health checks (convert to pytest + use test client)
  - `test_race_simulation.py` — essential simulation behaviour tests
  - `test_component_integration.py` — component integration tests (convert to parametrised pytest)
  - `test_playability.py` — high-level playability checks (keep)
  - `test_staff_system.py`, `test_driver_system.py` — core systems tests
  - `tests/examples/driver_examples.py` — keep as fixtures or move into `tests/fixtures/driver_fixtures.py`

- Convert
  - `quick_test.py`, `quick_test_race.py` — demo scripts; convert into pytest examples or move to `examples/`.
  - `simple_driver_test.py` — convert to pytest functions and break into focused unit tests.
  - `test_updated_endpoint.py` — convert to contract test and include in CI.
  - `test_gen.py`, `test_names.py`, `test_cultural_names.py` — convert/merge into focused unit tests for name generation.

- Remove (only after verification)
  - Any generated or temporary test artifacts that are duplicates of converted tests. Before deleting, ensure converted equivalents exist.

Next steps recommended
1. Create `tests/fixtures/` and move `examples/driver_examples.py` into fixture form.
2. Convert `quick_test*` scripts into pytest tests under `tests/` or move into `examples/` if they are manual demos.
3. Add a `tests/triage_done.md` after conversion listing files removed and rationale.
4. Add a CI job to run `pytest -q` to guard further refactors.
