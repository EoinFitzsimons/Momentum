# Testing Plan

## Overview

- Purpose: validate correctness, stability and usability of the MVP (Quick Race + visualiser + engine). Cover Unit, Integration, System and End‑User testing.
- Scope: `Momentum/Python` backend and `Momentum/Python/GUI` visual layers, plus integration between them (services → engine → GUI). Excludes unrelated archive or legacy folders.

## Testing Tools

- Python 3.10+ and project `requirements.txt` (virtualenv recommended).
- PyTest (optional) — run `pytest` to execute test suites.
- Manual testing using the PyQt6 GUI (`GUI/gui_game.py`, `GUI/gui_race_visual.py`).
- Logging and telemetry: engine writes telemetry `.jsonl` files in `logs/telemetry/` for evidence and replay.
- Artifacts: screenshots (`.png`), telemetry `.jsonl`, test output logs (stdout/stderr), and generated images in `Momentum/Python/tests/output/`.

## Quick commands (PowerShell)

```powershell
cd Momentum/Python
# Run single test script
python tests/test_vehicle_rendering.py

# Run all tests with pytest
pip install -r requirements.txt
pytest -q

# Run GUI demo (end-user testing)
python GUI/gui_game.py
python GUI/gui_race_visual.py
```

## Test levels & responsibilities

- Unit tests: small focused tests for pure functions, rendering helpers, model conversions. (Authors: module owners).
- Integration tests: services → engine → GUI event flow; database read/write coverage via `DatabaseManager` methods.
- System / End‑User tests: manual scenarios using the GUI (Quick Race flow), verify HUD, pace control, telemetry, and graceful shutdown.
- Regression tests: replay telemetry traces with deterministic seed mode where available.

## Use Case → Test Mapping (examples)

- UC1_ReadDriverDetails: Unit/Integration test `DatabaseManager.get_all_drivers()` returns non-empty list; End‑User: open Quick Race UI, select driver, verify details panel shows stats.
- UC2_ReadRaceConfiguration: Integration test Quick Race setup builds `config` dict correctly and launcher receives it; End‑User: set display/tuning options, start race and confirm `RaceWindow` reflects choices.
- UC3_CreateRaceResult / UC4_ReadRaceResults: Integration test after a completed race a `race_results` entry is written in DB (or saved artifact); Evidence: DB row or exported results JSON.
- RACE-LIVE: System test engine emits `position_update` events and `TrackWidget` animates cars with standings updates; Evidence: HUD screenshots and telemetry `.jsonl`.

## Functional Test Specifications (template + examples)

### Test Spec Template

- Test ID: `FT-<Area>-<NN>`  
- Title: short description  
- Precondition: environment/setup (DB present, virtualenv active)  
- Steps: numbered actions  
- Expected result: pass criteria  
- Evidence: log files, screenshots, DB query, test output

### Examples

- FT-DB-01: Load drivers from DB
	- Precondition: `momentum.db` exists with drivers table populated
	- Steps: `python -c "from database.database_manager import DatabaseManager; print(len(DatabaseManager().get_all_drivers()))"`
	- Expected: prints integer >= 1
	- Evidence: stdout captured as `Planning/Testing/evidence/FT-DB-01_output.txt`

- IT-RACE-01: Start Quick Race and confirm engine thread runs
	- Precondition: GUI will be used; DB has drivers
	- Steps: Launch `python GUI/gui_game.py`, select driver, start race, watch console for "Race thread started"
	- Expected: background thread started and HUD updates within a few seconds
	- Evidence: console log, HUD screenshot, telemetry file in `logs/telemetry/`

## Non‑Functional Tests

- Performance / Throughput: measure engine tick rate under nominal load (10–30 drivers). Metric: sustained 25–35 ticks/s; record CPU and memory.
- Responsiveness (GUI): UI remains responsive during race. Metric: no UI freeze >250 ms; frame drops <10% (manual observation).
- Determinism / Reproducibility: run `simulate_race` with the same `seed` twice and compare telemetry outputs byte-for-byte.
- Reliability / Fault‑handling: simulate telemetry write failure (mock or read-only dir) and confirm engine logs error and continues; check for `.partial` files.
- Usability / Accessibility: new user can start Quick Race within 2 minutes; sliders labelled and keyboard accessible.

## End‑User / Acceptance Testing

- Happy-path: Start app → select driver → set tuning preset → start Quick Race → watch to completion → verify standings and saved telemetry.
- Edge / failure scenarios: Force a DNF and confirm UI marks RETIRED and disables controls; stop & restart race to ensure stop_event handling.
- Acceptance criteria: Core Quick Race flow completes end‑to‑end with no unhandled exceptions; telemetry files created; player controls affect HUD and telemetry.

## Evidence & Results (collection guidance)

- Unit tests: save test runner output `pytest -q > Planning/Testing/evidence/unit_test_results.txt`.
- Integration tests: collect console logs, telemetry `.jsonl`, and HUD screenshots named by test ID.
- End‑User tests: record screen capture or screenshots per step; include short test report with pass/fail and notes.
- Existing repo artifacts: `Momentum/Python/tests/output/vehicle_topdown.png` can be used as rendering evidence.

## Test reporting and storage

- Files & locations:
	- `Planning/Testing/Plan.md` (this document)
	- `Planning/Testing/test_specs/` (individual test spec files)
	- `Planning/Testing/evidence/` (all captured logs, screenshots, telemetry)

- Continuous evidence: consider adding a CI job to run unit tests and publish `test_results_unit.xml` for inclusion in reports.

## Sample test spec (markdown)

Filename: `Planning/Testing/test_specs/FT-DB-01.md`

```
# FT-DB-01 — Load drivers from DB
## Precondition:
- `Momentum/Python/momentum.db` exists and is accessible.
## Steps:
1. Open PowerShell.
2. Activate venv and run `python -c "from database.database_manager import DatabaseManager; print(len(DatabaseManager().get_all_drivers()))"`.
## Expected:
- Terminal prints an integer >= 1.
## Evidence:
- Save terminal output as `Planning/Testing/evidence/FT-DB-01_output.txt`.
## Pass/Fail:
- Pass if integer >= 1 and no exceptions; otherwise fail.
```

## Metrics & Acceptance

- Unit tests: target 100% for small modules; Integration: document known issues.  
- Coverage: optional target >70% for core modules (database, engine, services). Use `coverage.py`.

## Next steps

- Generate `Planning/Testing/test_specs/` files for prioritized use-cases; I can scaffold 6–10 specs if you want.
- Run unit tests now and collect outputs (I can run them and return logs/evidence).

---

End of testing plan.
