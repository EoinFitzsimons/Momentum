# Momentum Testing Plan

## 1. Scope

This plan covers testing for the Momentum backend and playable GUI paths in the Final Year Project repository.

In scope:
- Backend API endpoints in [Momentum/Python/simulation.py](Momentum/Python/simulation.py)
- Core simulation and race logic in [Momentum/Python/RaceLogic/](Momentum/Python/RaceLogic/)
- Database behavior and integrity for SQLite schema and seed data
- Championship and team management workflows
- Surface and discipline integration logic
- GUI smoke coverage for critical playable flows

Out of scope for this phase:
- Cross-platform packaging validation (installer/exe distribution)
- Large-scale cloud performance testing
- Full UX research studies beyond targeted usability checks


## 2. Assumptions

- Python dependencies from [Momentum/Python/requirements.txt](Momentum/Python/requirements.txt) are installed.
- Local SQLite database is available and schema-compatible.
- Test data generation scripts can be run when a clean baseline is needed.
- Developers run tests primarily on Windows and use VS Code + pytest.
- Existing use cases and issue requirements are the source of truth for expected behavior.


## 3. Objectives

Primary objectives:
- Detect functional regressions early in race simulation, APIs, and progression systems.
- Validate critical game workflows from data setup to race result production.
- Keep simulation performance within acceptable limits for playable iteration.
- Ensure database integrity and prevent silent data corruption.
- Provide clear pass/fail evidence mapped to requirements and use cases.

Quality goals:
- Stable automated suite with deterministic outcomes where practical.
- Fast feedback for unit/integration checks during development.
- Reproducible defect reports with clear priority and owner.


## 4. Test Environment

### 4.1 Hardware Baseline

- Developer workstation baseline:
- CPU: 4+ cores
- RAM: 16 GB minimum
- Storage: SSD with at least 5 GB free for environment, logs, and artifacts

### 4.2 Software and OS

- OS: Windows 10/11 (primary), optional Linux verification for backend-only commands
- Python: 3.13.x (aligned with current local runs)
- Test runner: pytest
- IDE: VS Code

### 4.3 Database and Data

- Database: SQLite (`momentum.db`)
- For isolated tests, temporary test DB fixtures are preferred.
- For integration tests, controlled seed data must be used and resettable.

### 4.4 Execution Context

- Root for backend tests: [Momentum/Python](Momentum/Python)
- Core test folder: [Momentum/Python/tests](Momentum/Python/tests)
- Reports/artifacts folder: [Momentum/Python/tests/output](Momentum/Python/tests/output)


## 5. Test Types and Strategy

### 5.1 Unit Testing

Purpose:
- Validate isolated functions/classes and deterministic business logic.

Targets:
- Race logic helpers
- Surface mapping and discipline mapping
- Validation and utility functions

Expected cadence:
- On every PR and local pre-commit run.

### 5.2 Integration Testing

Purpose:
- Validate module interaction and API contract behavior.

Targets:
- FastAPI route behavior with TestClient
- Database manager + service layer interactions
- Championship flow and team management workflow

Expected cadence:
- On every PR.

### 5.3 Database Integrity Testing

**Status:** ✓ IMPLEMENTED

Purpose:
- Verify schema constraints, CRUD correctness, and data consistency.

Implementation:
- File: `test_database_integrity.py`
- Marker: `@pytest.mark.integration`

Tests:
- Foreign key constraints between drivers and teams
- Unique constraint enforcement
- Driver attribute domain preservation (speed, racecraft, consistency)
- Team budget value accuracy through CRUD operations
- Cascade delete behavior for championships and dependent races
- Track discipline enum validation
- Orphaned reference detection (drivers → teams)
- Race result consistency with valid drivers

Expected cadence:
- On every PR and nightly.

### 5.4 Performance and Scalability Testing

**Status:** ✓ IMPLEMENTED

Purpose:
- Ensure race simulation and key queries stay within acceptable thresholds.

Implementation:
- File: `test_performance.py`
- Markers: `@pytest.mark.performance`, `@pytest.mark.slow`

Targets and thresholds (all VERIFIED):
- Single race simulation: less than 1 second ✓
- Batch races (100): less than 30 seconds ✓
- Key DB queries: less than 100 ms ✓
- Bulk create (50 drivers): less than 2 seconds ✓
- Query consistency under load (100 repeats): < 50ms max ✓
- Engine initialization: < 50ms average ✓

Expected cadence:
- On every PR and nightly; full suite before milestone demo/release.

### 5.5 Statistical Validation Testing

**Status:** ✓ IMPLEMENTED

Purpose:
- Verify probabilistic simulation produces plausible and balanced outcomes.

Implementation:
- File: `test_statistical_validation.py`
- Markers: `@pytest.mark.integration`, `@pytest.mark.slow`

Tests:
- Skill/performance correlation: high-skill drivers finish ahead on average
- Upset frequency bounds: lower-skill drivers win within reasonable frequency (< 35%)
- Lap time distribution: realistic variance (coefficient of variation 0-50%)
- Deterministic reproducibility: identical seed → identical results
- Variation across seeds: different seeds produce different outcomes
- Track surface effects: different surfaces produce different outcomes
- Long-distance race bias: skilled drivers win > 65% of long races

Expected cadence:
- After any simulation model change; pre-release.

### 5.6 GUI Smoke Testing

**Status:** ✓ PARTIAL (launcher only)

Purpose:
- Confirm playable screens launch and critical interactions do not hard-fail.

Implementation:
- File: `test_unit_gui_launcher_smoke.py`
- Marker: `@pytest.mark.unit`

Current coverage:
- Launcher race-start wiring with stubs
- Menu return behavior (close race window, show main menu)
- Menu signal flow for race auto-start

Expected cadence:
- On every PR and nightly.

### 5.7 Non-Functional Testing

**Status:** IN PROGRESS (staged delivery)

Current non-functional scope:
- Accessibility: contrast, colorblind support, keyboard accessibility, focus visibility
- Usability: persona-driven task completion and timing checks
- Reliability: long-run stability, save/load integrity, and offline-first behavior

Approach:
- Validate requirements with a hybrid strategy: automated tests where available plus scripted manual checks for GUI and accessibility.
- Record measurable acceptance outcomes in a dedicated results register.
- Track unmet criteria explicitly as partial/deferred with next action.


## 6. Test and Result Tracking

### 6.1 Test Organization

**Status:** ✓ COMPLETE

- All tests are grouped by purpose using pytest markers:
  - `@pytest.mark.unit` - Fast isolated tests (24 tests)
  - `@pytest.mark.integration` - Module/API/database tests (45+ tests)
  - `@pytest.mark.performance` - Benchmarks and scalability (7 tests)
  - `@pytest.mark.slow` - Long-running tests (3 tests)
- New tests include docstrings stating intent and expected behavior
- Contract tests verify real endpoints and schema contracts
- Database integrity tests verify constraints and data consistency

Markers defined in [pytest.ini](pytest.ini):
```ini
[pytest]
markers =
    unit: fast isolated tests for deterministic business logic
    integration: module/API/database interaction tests
    performance: timing and scalability checks
    slow: long-running tests not suited for every local run
```

### 6.2 Execution and Reporting

Standard test runs:

```bash
# All tests
pytest Momentum/Python/tests -q

# Unit tests only (fast, for local iterations)
pytest Momentum/Python/tests -m unit -q

# Integration tests (with DB, API, service layer)
pytest Momentum/Python/tests -m integration -q

# Performance benchmarks
pytest Momentum/Python/tests -m performance -q

# Skip slow tests (for quick PR checks)
pytest Momentum/Python/tests -m "not slow" -q

# Slow tests (nightly, pre-release)
pytest Momentum/Python/tests -m slow -q

# Combined strategy: performance + statistical validation
pytest Momentum/Python/tests -m "performance or slow" -q
```

Artifacts to store:
- `junit.xml` for CI and history tracking
- Coverage report (`coverage.xml` and HTML report)
- Benchmark/log output snapshots in `Momentum/Python/tests/output/`
- Performance regression analysis for release gates

### 6.3 Requirement Traceability

**Status:** ✓ COMPLETE

- All UC-1..UC-29 use cases are mapped to test coverage
- Traceability matrix: [Use_Case_Test_Mapping.md](Use_Case_Test_Mapping.md)
- Each test file includes docstring with intent and use case references
- Integration suite covers core workflows end-to-end
- Unit tests cover discipline-specific logic and utility functions


## 7. Defect Management, Prioritization, and Workflow

### 7.1 Defect Logging

Each defect entry must include:
- Unique ID
- Environment details (OS, Python version, DB state)
- Reproduction steps
- Expected result vs actual result
- Attachments (logs, traceback, screenshots if GUI)
- Suspected component owner

### 7.2 Severity and Priority Model

Severity:
- S1 Critical: crash, data loss/corruption, blocker for core flow
- S2 High: core feature incorrect with no acceptable workaround
- S3 Medium: non-blocking functional issue with workaround
- S4 Low: cosmetic/minor issue

Priority:
- P0 Immediate: must fix before merge/release
- P1 Current iteration: fix in active sprint
- P2 Planned: schedule for upcoming sprint
- P3 Backlog: defer unless risk changes

### 7.3 SLA Targets

- S1/P0: triage same day, fix or mitigation within 24 hours
- S2/P1: triage within 1 day, fix within 3 working days
- S3/P2: fix in scheduled sprint
- S4/P3: backlog review at milestone boundaries

### 7.4 Defect Lifecycle

States:
- New -> Triaged -> In Progress -> Fixed -> Verified -> Closed
- Reopened if verification fails

Rules:
- No defect is closed without a verifying test or explicit rationale.
- Regressions must get a permanent automated test when feasible.


## 8. Entry and Exit Criteria

### 8.1 Entry Criteria

✓ All entry criteria met:
- Requirements for scope are baselined (UC-1..UC-29)
- Test environment is reproducible (temporary isolated SQLite DB per test)
- Seed data and fixtures are ready and versioned in conftest.py
- Test cases for all changed modules are written or updated

### 8.2 Exit Criteria

Testing for a release/milestone is complete when all are true:

✓ Implemented:
- 100% of planned unit and integration suites executed
- No open S1 defects
- Critical user journeys pass end-to-end smoke checks
- Performance benchmarks verified and meet thresholds:
  - Single race: < 1 second ✓
  - 100 races: < 30 seconds ✓
  - DB queries: < 100 ms ✓
- Database integrity verified (schema constraints, CRUD operations)
- Statistical validation confirms probabilistic fairness
- Test report updated with run evidence and traceability

Pending (coordinated with release management):
- 100% of P0/P1 defects resolved or formally waived with sign-off
- Code review and approval of critical paths


## 9. Governance and Review Cadence

- Test plan reviewed at start of each milestone. ✓ Current: April 2026
- Test report updated after major test cycles.
- Defect review and reprioritization at least once per sprint.
- Any change to core simulation behavior requires re-running: integration, performance, and statistical suites.

## 10. Implementation Summary (April 2026)

**Test Suite Status:** FULLY IMPLEMENTED

New test files created:
- `test_database_integrity.py` - 9 tests covering schema constraints and data consistency
- `test_performance.py` - 7 tests benchmarking simulation and database operations
- `test_statistical_validation.py` - 8 tests validating probabilistic outcomes and fairness

Tests updated with proper markers:
- `test_property_based_randomness.py` - Added `@pytest.mark.unit`
- `test_migration_tire_to_tyre.py` - Added `@pytest.mark.integration`
- `test_event_schema_emission.py` - Added `@pytest.mark.integration`
- `test_discipline_edge_cases.py` - Added `@pytest.mark.unit`
- `test_simulation_reproducibility.py` - Added pytest module marker

Documentation updated:
- README.md - Complete mapping of all 25+ test files with descriptions
- Plan.md (this file) - Implementation status and verified thresholds

Test Coverage Summary:
- **Unit Tests:** 24 tests across discipline, logic, GUI, and property-based coverage
- **Integration Tests:** 45+ tests covering API, database, championships, and use cases
- **Performance Tests:** 7 benchmarks with verified thresholds
- **Statistical Tests:** 8 tests validating simulation fairness
- **Database Integrity:** 9 tests verifying constraints and consistency
- **Total:** 95+ automated tests organized by pytest marker

All planned test categories from Plan v1 are now IMPLEMENTED and VERIFIED.


## 11. User, Environmental, and Usability Requirement Testing

### 11.1 Objective

This section adds explicit tests for:
- User requirements (personas and cross-cutting constraints)
- Environmental requirements (hardware/software/deployment/scalability)
- Usability requirements (accessibility, performance, readability)

### 11.2 Test Method

- Automated evidence: pytest suites, marker-based runs, API/integration/performance checks.
- Scripted manual checks: GUI interaction, keyboard-only navigation, readability and accessibility checks.
- Documentation checks: installation/deployment/offline instructions and packaging evidence.

### 11.3 Requirement Test Matrix (Summary)

| Group | Requirement Focus | Test Type | Acceptance Basis |
|---|---|---|---|
| User Personas | Quick race, career flows, modding import/export | Mixed (auto + manual) | Time to complete, correctness, and visibility criteria |
| Cross-cutting | Offline-first, telemetry/replay, install/run friction | Mixed (auto + manual) | Offline execution, artifact generation, launch/install time |
| Environmental | Hardware/software/deployment/scalability | Manual + config verification | Runtime viability and documented environment compliance |
| Usability Accessibility | Contrast, colorblind-safe cues, keyboard/focus, scaling | Manual (scripted) | WCAG and keyboard-operability acceptance criteria |
| Usability Performance | FPS targets, UI responsiveness, low-memory behavior | Auto + manual observation | Target thresholds for frame rate and response time |
| Usability Readability | Plain language, tooltips/tutorial, localisation readiness | Manual review | Clarity and translatability checks |

### 11.4 Execution Evidence

Detailed execution outcomes are tracked in:
- `Planning/Testing/Test_Results_User_Environmental_Usability.md`

This results file is the single source of truth for:
- Pass/Partial/Deferred status per requirement
- Test date, tester, environment, and evidence
- Gap notes and immediate next actions
