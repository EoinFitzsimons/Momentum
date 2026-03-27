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

Purpose:
- Verify schema constraints, CRUD correctness, and data consistency.

Targets:
- Foreign keys and relationship integrity
- No duplicate IDs where uniqueness is required
- Domain ranges (driver attributes, budgets, track properties)

Expected cadence:
- Nightly and pre-release.

### 5.4 Performance and Scalability Testing

Purpose:
- Ensure race simulation and key queries stay within acceptable thresholds.

Targets and thresholds:
- Single race simulation: less than 1 second (target)
- Batch races (100): less than 30 seconds (target)
- Key DB queries: less than 100 ms (target)

Expected cadence:
- Nightly and before milestone demo/release.

### 5.5 Statistical Validation Testing

Purpose:
- Verify probabilistic simulation produces plausible and balanced outcomes.

Targets:
- Skill/performance correlation
- Upset frequency bounds
- Distribution sanity checks

Expected cadence:
- Pre-release and after simulation model changes.

### 5.6 GUI Smoke Testing

Purpose:
- Confirm playable screens launch and critical interactions do not hard-fail.

Targets:
- Launcher and main gameplay entry points
- Basic race setup and render handoff

Expected cadence:
- Nightly and before demos.

### 5.7 Non-Functional Testing

Accessibility:
- Contrast checks
- Keyboard navigation for primary flows
- Basic screen-reader compatibility where applicable

Usability:
- Targeted task completion tests for representative user personas

Reliability:
- Long-run stability checks (memory and repeated simulation runs)


## 6. Test and Result Tracking

### 6.1 Test Organization

- Tests must be grouped by purpose (`unit`, `integration`, `performance`, `slow` markers).
- New tests must include a docstring that states intent and expected behavior.
- Contract tests should verify real endpoints or schema contracts, not synthetic dictionaries.

### 6.2 Execution and Reporting

- Standard local run: `pytest Momentum/Python/tests -q`
- Marker-specific runs:
- `pytest -m unit`
- `pytest -m integration`
- `pytest -m "performance or slow"`

Artifacts to store:
- `junit.xml` for CI and history
- Coverage report (`coverage.xml` and HTML)
- Benchmark/log output snapshots in [Momentum/Python/tests/output](Momentum/Python/tests/output)

### 6.3 Requirement Traceability

- Each major requirement/use-case must map to at least one test module.
- Maintain a lightweight matrix in the testing report linking:
- Requirement/UC -> Test file -> Last run status


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

- Requirements for the target scope are baselined.
- Test environment is available and reproducible.
- Seed data and fixtures are ready.
- Test cases for changed modules are written or updated.

### 8.2 Exit Criteria

Testing for a release/milestone is complete when all are true:
- 100% of planned unit and integration suites executed.
- 100% of P0/P1 defects resolved or formally waived with sign-off.
- No open S1 defects.
- Performance benchmarks meet agreed thresholds or have approved exceptions.
- Critical user journeys pass end-to-end smoke checks.
- Test report updated with run evidence and traceability.


## 9. Governance and Review Cadence

- Test plan reviewed at start of each milestone.
- Test report updated after major test cycles.
- Defect review and reprioritization at least once per sprint.
- Any change to core simulation behavior requires re-running integration, performance, and statistical suites.
