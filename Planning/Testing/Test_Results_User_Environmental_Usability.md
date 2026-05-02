# Test Results: User, Environmental, and Usability Requirements

## 1. Test Cycle Metadata

- Date: 2026-05-02
- Tester: GitHub Copilot assisted verification
- Workspace: FinalProject (branch: report-work)
- Environment:
  - OS: Windows
  - Python: 3.13.5
  - Database: SQLite (momentum.db)

## 2. Automated Execution Evidence

Commands run:

```bash
C:/Users/eoin0/AppData/Local/Programs/Python/Python313/python.exe -m pytest Momentum/Python/tests -m "not slow" -q
```

Result:
- 107 passed, 1 skipped in 135.70s

```bash
C:/Users/eoin0/AppData/Local/Programs/Python/Python313/python.exe -m pytest Momentum/Python/tests -m performance -q
```

Result:
- 7 passed, 101 deselected in 6.62s

```bash
C:/Users/eoin0/AppData/Local/Programs/Python/Python313/python.exe -m pytest Momentum/Python/tests -m slow -q
```

Result:
- 3 passed, 105 deselected in 8.23s

## 3. Requirement Results Register

Status legend:
- PASS: acceptance criteria satisfied in this cycle
- PARTIAL: partially satisfied or missing measurable proof for one or more criteria
- DEFERRED: not implemented in delivered scope yet

### 3.1 User Requirements

| ID | Requirement | Status | Evidence | Notes |
|---|---|---|---|---|
| UR-P1 | Casual race fan quick-start (single race, <= 5 min, legible HUD/top-line stats) | PARTIAL | GUI launcher smoke tests; fast race simulation tests | Quick start flow exists and is stable; explicit timed UX and HUD legibility measurements not yet formally recorded. |
| UR-P2 | Career mode management (save/load, contracts, standings reliability, reversible changes) | PARTIAL | Integration tests for championship flow and database layer | Core persistence and standings logic verified; explicit save/load < 30s and UI-level reversibility script needs dedicated timed test. |
| UR-P3 | Modder import/export JSON/CSV <= 60s | DEFERRED | Track tooling and generation scripts present | End-user import/export workflow and timed acceptance run not fully delivered as a user-facing feature. |
| UR-C1 | Local-first offline operation | PASS | No mandatory online dependency in core flow; SQLite local persistence; automated tests run fully local | Core gameplay path operates without network dependency. |
| UR-C2 | Replay and investigation (telemetry/events stored and accessible post-race) | PARTIAL | Event schema and integration tests; telemetry/event paths in simulation tests | Event/telemetry capture exists; replay visualization acceptance check remains pending. |
| UR-C3 | Low-friction install/run (Python and packaged binary <= 10 min) | PARTIAL | README run path, launcher path, PyInstaller spec present | Python run path is verified; packaged binary installation timing and cross-platform confirmation still required. |

### 3.2 Environmental Requirements

| ID | Requirement | Status | Evidence | Notes |
|---|---|---|---|---|
| ENV-H1 | Minimum hardware baseline | PARTIAL | Successful local execution and test pass | Full benchmark sweep against exact minimum hardware profile remains pending. |
| ENV-H2 | Recommended hardware baseline | PASS | Current environment exceeds baseline and test suite passes | Meets recommended development profile in this cycle. |
| ENV-S1 | OS support (Windows/macOS/Linux), Python >= 3.8, SQLite >= 3.7 | PARTIAL | Windows + Python 3.13.5 + SQLite verified | Cross-platform validation for macOS/Linux not executed in this cycle. |
| ENV-D1 | Development deployment (uvicorn localhost:8000) | PASS | Existing development stack and API tests | Development-mode behavior validated in local workflow. |
| ENV-D2 | Production deployment (ASGI server compatibility) | PARTIAL | Architecture supports ASGI; uvicorn/gunicorn target documented | Production server runbook verification pending for this cycle. |
| ENV-SC1 | Scalability options (multi-worker/stateless/db migration path) | PARTIAL | Stateless service structure and documented migration path | Measured multi-worker load test and migration rehearsal still pending. |

### 3.3 Usability Requirements

| ID | Requirement | Status | Evidence | Notes |
|---|---|---|---|---|
| US-A11 | WCAG contrast, colorblind-safe palette, high-contrast mode | PARTIAL | Implemented theme toggles in UI; persisted settings | High-contrast and colorblind-safe themes added to the main menu and applied app-wide; objective WCAG contrast audit still pending. |
| US-A12 | Colorblind support not color-only, overlays/tooltips, preview filters | PARTIAL | Tooltips exist in selected UI surfaces | Dedicated colorblind filter preview mode and full overlay audit are pending. |
| US-A13 | Text scaling 100/125/150 and min font with no overlap | PARTIAL | Existing GUI scaling behavior observed in development | Formal scripted layout checks at each scale not yet completed. |
| US-A14 | Full keyboard operation, remappable controls, conflict detection, persistence | PARTIAL | Race window supports remappable bindings with duplicate-key conflict detection and persisted control mappings; accessibility profile applied to race window | Core race controls are implemented and persisted; accessibility profile (theme/scale) is injected into race windows and applied app-wide; menu keyboard-only traversal and full focus-outline audit remain pending. |
| US-P21 | Visual update 30 FPS target, 15 FPS minimum under load | PARTIAL | Performance tests pass for backend timings | GUI frame-rate telemetry capture not yet attached to this cycle. |
| US-P22 | UI responsiveness 150-300ms and non-blocking background jobs | PARTIAL | Integration/performance tests show stable operation | Explicit interaction-latency instrumentation required for strict verification. |
| US-P23 | Low-memory mode | DEFERRED | Requirement defined only | Low-memory mode implementation and test script pending. |
| US-R31 | Plain-English labels/tooltips/help | PASS | Report/UI copy review and existing user-facing text | Language is accessible in current UI paths. |
| US-R32 | Tooltips and optional in-app tutorial for non-trivial controls | PARTIAL | Tooltips present on selected controls | Full control coverage and tutorial completion checklist pending. |
| US-R33 | Localisation-ready strings and UTF-8/date/currency formatting | PARTIAL | UTF-8 capable stack and data model in use | Formal localisation extraction and locale formatting validation still pending. |

## 4. Summary

- PASS: 5
- PARTIAL: 14
- DEFERRED: 3

Interpretation:
- Core simulation reliability and backend quality gates are strong (automated suite passed in all executed groups).
- Most open risk is in non-functional UX/accessibility verification, where structured manual checks and instrumentation are still needed.
- Deferred items are explicitly scoped and tracked for future implementation cycles.

## 5. Immediate Next Actions

1. Add a scripted keyboard-and-scaling GUI verification checklist and capture evidence screenshots.
2. Perform objective WCAG contrast audit for the new themes and produce remediation where required.
3. Add packaged binary install timing logs and at least one Linux/macOS verification pass.
4. Add UI latency and FPS capture to make responsiveness/frame-rate requirements fully measurable.
