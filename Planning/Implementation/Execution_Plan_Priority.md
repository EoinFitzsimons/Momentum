# Momentum Execution Plan (Priority Order)

Date: 1 April 2026

## Goal

Complete the highest-impact remaining work in a practical order, with each stage producing visible progress in gameplay quality and report evidence.

## Priority 1 - User-facing gameplay completion

### 1.1 Main menu and race mode flow

File:
- Momentum/Python/GUI/gui_main_menu.py

Actions:
- Remove any remaining placeholder messaging in race mode selection text.
- Verify Championship and Career mode buttons always route to implemented handlers.
- Confirm no dead-end GUI paths (no action buttons without working destination).

Effort:
- Small (0.5 to 1 day)

Impact:
- High (first impression, demo stability, GUI section screenshots)

Acceptance checks:
- Every main menu action opens a functional screen.
- No placeholder text is visible during normal user flow.

### 1.2 Drag bracket and race visual polish

Files:
- Momentum/Python/GUI/gui_race_visual.py
- Momentum/Python/RaceLogic/disciplines/drag_acceleration/drag_acceleration_discipline.py

Actions:
- Remove placeholder labels in drag heat emissions where realistic values exist.
- Ensure bracket progression updates are deterministic and readable.
- Validate winner propagation and round transitions in GUI tree.

Effort:
- Medium (1 to 2 days)

Impact:
- High (discipline completeness, implementation evidence)

Acceptance checks:
- Drag heats show real lane names/times in normal races.
- Bracket state updates correctly from first heat to final.

## Priority 2 - Data integrity and simulation service reliability

### 2.1 Race simulation API fallback hardening

File:
- Momentum/Python/services/race_simulation_api.py

Actions:
- Reduce silent fallback behaviour that can hide data issues.
- Improve warnings when adapter loading fails.
- Ensure team resolution prioritises database data before synthetic defaults.

Effort:
- Medium (1 day)

Impact:
- High (core reliability and debugging clarity)

Acceptance checks:
- Missing adapter/team data is logged clearly.
- Successful runs use real team data when available.

### 2.2 Temporary race object cleanup

File:
- Momentum/Python/database/database_manager.py

Actions:
- Replace temporary race placeholders (for example fixed circuit id) with safer lookup behaviour.
- Add explicit validation message when race records are absent.

Effort:
- Medium (1 day)

Impact:
- Medium to high (data correctness for championship/report claims)

Acceptance checks:
- No hard-coded race placeholders in production path.
- Race retrieval path fails explicitly when source data is missing.

## Priority 3 - Test evidence package (for report sections 2.5 and 2.6)

### 3.1 Targeted test additions

Folder:
- Momentum/Python/tests/

Actions:
- Add integration tests covering:
  - drag bracket progression
  - discipline adapter resolution
  - race result persistence from simulation output
- Add one regression test for each fixed placeholder path.

Effort:
- Medium (1 to 2 days)

Impact:
- Very high (grading evidence)

Acceptance checks:
- New tests run green locally.
- Fail-first behaviour demonstrated for at least one historical bug.

### 3.2 Test results appendix content

Suggested file to create:
- Planning/Technical Report/Test_Results.md

Actions:
- Record unit/integration/end-user test evidence in table format.
- Include pass/fail counts, notable defects fixed, and key runtime metrics.

Effort:
- Small to medium (0.5 to 1 day)

Impact:
- Very high (report quality and traceability)

Acceptance checks:
- Every test category has concrete evidence and outcomes.
- Metrics in evaluation section can be traced back to this appendix.

## Priority 4 - Report synchronisation with live implementation

### 4.1 Design versus implementation separation

Files to review:
- Planning/Design and Architecture/Help.md
- Planning/UseCases/All_Use_Cases.md
- Planning/UseCases/All_Use_Cases_Detailed.md

Actions:
- Keep use cases behaviour-focused (no method names or class names).
- Keep design section component/flow-focused.
- Keep code-level details and snippets in implementation section only.

Effort:
- Small (0.5 day)

Impact:
- High (supervisor feedback alignment)

Acceptance checks:
- Use case text reads as actor/system behaviour only.
- Implementation section contains the code references.

## Priority 5 - Optional quality hardening (if time remains)

### 5.1 Reduce silent exception swallowing in critical paths

Files:
- Momentum/Python/GUI/gui_race_visual.py
- Momentum/Python/RaceLogic/realtime_race_engine.py
- Momentum/Python/services/persistence_sqlite.py

Actions:
- Replace silent pass statements in critical runtime paths with structured warning logs.
- Keep non-fatal behaviour where needed, but preserve observability.

Effort:
- Medium (1 to 2 days)

Impact:
- Medium (maintainability and debugging speed)

Acceptance checks:
- Critical exceptions produce actionable log output.
- No user-facing crashes introduced.

## Suggested execution sequence (one-week view)

1. Main menu and drag bracket completion.
2. Simulation API and database race retrieval hardening.
3. Add targeted tests and run full suite.
4. Produce test evidence appendix and evaluation tables.
5. Final report synchronisation pass.

## Definition of done

- Core race flow and drag flow demonstrate without placeholders.
- Adapter-based discipline loading is stable and observable.
- Test evidence exists for unit, integration, and end-user testing.
- Report sections 2.2 to 2.6 are consistent with actual implementation.
- Conclusions and further development are evidence-based, not speculative.
