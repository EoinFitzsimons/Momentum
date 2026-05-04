# Testing Section Draft Based on Requirements and Use Cases

This is a standalone draft for critique. It is separate from `Report.md` and is written to follow the structure of ISO/IEC/IEEE 29119 while staying grounded in the report’s functional and non-functional requirements and the UC-1 to UC-29 use cases.

## 1. Test Plan

### Scope
The top-level scope is the set of functional requirements and non-functional requirements defined earlier in the report. The functional scope is organised by the priority groups already established in the requirements section: high-priority core gameplay use cases, medium-priority career-mode and workflow use cases, and low-priority polish or advanced-feature use cases. The non-functional scope covers usability, accessibility, performance, responsiveness, environment, and reliability targets.

Within that scope, the use cases act as the traceability layer. The test evidence is not just “what was run”; it is also “which requirement or use case the test supports.” The release-critical focus is on the high-priority functional use cases and the non-functional targets that affect playability and usability. Lower-priority use cases are treated as deferred or optional features unless they are already implemented and traceable in the suite.

### Objectives
The objectives are to confirm that the priority functional requirements behave correctly, to show that the main workflows remain consistent across database, simulation, and interface layers, and to demonstrate that the system meets the practical non-functional targets needed for a final deliverable. A further objective is to show where coverage is complete, where it is partial, and where lower-priority use cases were intentionally left outside the release-critical test set.

### Strategy
The strategy is requirement-led rather than implementation-led. Each major requirement group is mapped to one or more test files, and each test file is mapped to one or more use cases. The execution strategy is layered:

- Unit tests verify isolated logic such as rule calculations, surface mappings, and helper behaviour.
- Integration tests verify end-to-end workflows such as API contracts, race scheduling, championship flow, database round-trips, and use-case coverage.
- Performance and statistical checks verify speed, repeatability, and simulation plausibility.
- Accessibility and GUI smoke checks verify that the interface remains usable and readable.

This means the plan is driven by the requirements, while the test cases and execution log show how those requirements were actually exercised.

### Environment
The latest validation run was executed on Windows with Python 3.13, pytest, and the project’s SQLite-backed fixtures. GUI and accessibility checks used the same local development environment. The run was intentionally representative of normal development conditions so the results could be used as practical release evidence rather than as a one-off lab exercise.

### Schedule
Testing was carried out continuously during development, with the most recent full validation run completed on 2026-05-04. Fast checks were used during active development, while full-suite execution was used for the final evidence pass. Lower-priority requirements were not treated as release blockers and were only included where the implemented suite already provided coverage.

### Risks
The main risks are the same ones that matter in the requirements: broken use-case flows, incorrect data relationships, unreliable simulation behaviour, and interface accessibility problems. A smaller procedural risk is the presence of custom pytest markers that are not registered in the configuration, which creates warnings but does not affect test success. Another risk is that some low-priority use cases remain outside the release-critical scope and should be explicitly noted as deferred or optional.

## 2. Test Case Specification

### Test Cases
The test cases are organised by requirement group and use-case coverage, not by file name alone.

| Requirement group | Representative use cases | Test evidence type | Expected result |
|---|---|---|---|
| Core gameplay | UC-1 Read Driver Details, UC-2 Read Race Configuration, UC-3 Create Race Result | API and simulation integration tests | Driver data, race configuration, and race results are returned correctly and consistently |
| Career mode and workflow | UC-4 to UC-20 | Championship flow, database layer, season progression, and contract-flow tests | Standings, schedules, contracts, budgets, and progression updates behave as specified |
| Lower-priority or optional features | UC-21 to UC-29 | Targeted integration, unit, and rendering-related checks where implemented | Optional features either pass or are clearly marked as deferred / not release-critical |
| Non-functional usability | accessibility, keyboard input, scaling, visibility | GUI smoke and accessibility tests | The interface remains readable, operable, and accessible at the agreed baseline |
| Non-functional performance | simulation speed, query timing, repeated-run behaviour | Performance and statistical validation tests | Timing and repeatability remain within acceptable bounds |

### Expected Results
Expected results are defined from the requirement class rather than from the code path. A passing core gameplay test should show that the requested data or result is produced correctly. A passing career-mode test should show that the workflow can move from setup to progression without breaking persistence or state transitions. A passing non-functional test should show that the system remains usable, responsive, and stable under the stated conditions.

### Coverage Mapping
The current suite traces the main requirement groups as follows:

- UC-1 to UC-3 are covered by API contract tests, championship flow tests, and simulation-related checks.
- UC-4 to UC-20 are covered by championship flow, database layer, full season, and use-case coverage tests.
- UC-21 to UC-29 are covered where implemented by the unit, integration, rendering, or appearance-related tests, but these are lower-priority and should be reported as optional or deferred where appropriate.
- Non-functional accessibility requirements are covered by the accessibility UI checks.
- Non-functional performance requirements are covered by the performance and statistical validation suites.

## 3. Test Execution Log

### What ran
The latest run executed the full pytest suite, including accessibility checks, database integrity tests, discipline edge cases, event schema validation, API contracts, championship flow, database integration, full career season flow, migration checks, performance checks, property-based checks, simulation reproducibility checks, statistical validation, unit-level service and rules tests, GUI smoke checks, track surface service checks, and use-case coverage tests.

### When
The most recent full execution was run on 2026-05-04.

### Pass / Fail outcome
The command `python -m pytest -q` completed with 111 passed, 1 skipped, and 0 failed in 86.41 seconds. The skip was isolated and did not prevent the suite from completing successfully. The only warnings were marker-registration warnings, which should be noted but do not count as test failures.

## 4. Test Completion Report

### Results summary
The final outcome for the implemented suite is positive. The main functional requirements and the important non-functional checks passed, which gives strong evidence that the system is stable enough for final presentation and review.

### Defect overview
No test-breaking defects were exposed by the latest run. The most visible issue is procedural rather than functional: a number of custom pytest markers are not registered, so the test runner reports warnings. In addition, some lower-priority use cases are better treated as deferred or optional rather than release-critical, which should be made explicit in the final report so the scope is honest.

### Release readiness
The build is ready to be presented as a strong implemented core because the core gameplay, workflow, persistence, performance, and usability evidence all points in the right direction. The release-ready claim should be framed carefully: the core requirement groups are validated, while lower-priority use cases and non-critical polish items can be recorded as deferred or future work. That gives a clear and defensible final position.
