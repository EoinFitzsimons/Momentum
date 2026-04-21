# H1 Plan and Traceability Pack

## Section A: H1 Finish Plan (Rubric-Aligned)

### Purpose
This plan converts the current repository state into examiner-ready evidence for the Final Examination Rubric.

### Rubric Weighting and Strategy
- Requirements Engineering (40%): Highest priority. Convert broad artifacts into traceable, verifiable evidence.
- Technology and Implementation (30%): Preserve current strength and remove final technical risks.
- Prototype (25%): Ensure reliable and repeatable live demonstration.
- Communication, Documentation, Showcase, Supervisor Interaction (remaining): Package work professionally and consistently.

### Workstream 1: Requirements Engineering (40%)
#### Objective
Produce a complete and auditable trace from requirement to implementation, test, and demo evidence.

#### Tasks
1. Complete and maintain the traceability matrix in this file.
2. For each requirement, assign one status only: Verified Implemented or Deferred.
3. Ensure each Verified Implemented row has:
- Code evidence
- Test evidence
- Demo evidence
4. For Deferred rows, add a reason and next action.

#### Deliverables
- Completed matrix with no empty status cells.
- Requirement coverage summary (counts by status).

### Workstream 2: Technology and Implementation (30%)
#### Objective
Eliminate known correctness risks and provide strong implementation proof.

#### Tasks
1. Resolve duplicate route declaration risk in simulation API.
2. Run full backend test suite and store result output.
3. Prepare one implementation evidence page listing core modules and responsibilities.
4. Validate no IDE problems in critical files.

#### Deliverables
- Clean API route map with no duplicate decorators.
- Passing test report snapshot.
- Implementation evidence section in report.

### Workstream 3: Prototype and Showcase (25% + 5%)
#### Objective
Guarantee a smooth, reproducible demo under time pressure.

#### Tasks
1. Create a deterministic demo runbook (launch command, steps, expected results).
2. Create backup demo video (60-120 seconds).
3. Capture screenshot evidence for setup, race, and result stages.
4. Prepare fallback plan for runtime issues.

#### Deliverables
- Demo runbook markdown.
- Backup video file.
- Screenshot evidence page.

### Workstream 4: Documentation (10%)
#### Objective
Raise report quality to thesis-like consistency and referencing standard.

#### Tasks
1. Remove draft/export artifacts and stale sections.
2. Ensure consistent Harvard-style referencing throughout final report files.
3. Add concise test results appendix with key metrics.
4. Add explicit limitations and future work section linked to matrix deferred items.

#### Deliverables
- Clean final report files.
- Bibliography and in-text reference consistency pass.
- Testing appendix with pass/fail summary and interpretation.

### Workstream 5: Communication and Viva Preparation (5% + 5%)
#### Objective
Deliver a clear argument and answer questions with confidence.

#### Tasks
1. Finalize presentation deck aligned with rubric language.
2. Rehearse 5-minute script with timing checkpoints.
3. Prepare concise answers for likely technical and design questions.
4. Keep supervisor interaction log updated with date, decision, and action.

#### Deliverables
- Final slides.
- Q and A one-pager.
- Supervisor log.

### 7-Day Execution Sequence
1. Day 1: Complete matrix statuses and evidence links for all requirements.
2. Day 2: Fill evidence gaps for high-priority requirements.
3. Day 3: Implementation cleanup and full test verification.
4. Day 4: Demo runbook, screenshots, and backup recording.
5. Day 5: Documentation polish and reference consistency pass.
6. Day 6: Slide finalization and timed rehearsal.
7. Day 7: Full dry run under exam conditions.

### Definition of Done
1. Every requirement has one status and linked evidence.
2. All critical demo flows run without manual patching.
3. Full backend tests pass.
4. Report sections are coherent, referenced, and aligned with implementation truth.
5. Presentation and backup assets are ready and tested.

### Risk Register (Final Week)
| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Demo runtime issue | High | Medium | Backup video and fallback script |
| Requirement-evidence mismatch | High | Medium | Matrix validation pass before submission |
| Last-minute regression | Medium | Medium | Freeze window plus full regression test run |
| Documentation inconsistency | Medium | Medium | Single final editorial pass |

### Ownership and Cadence
- Daily 20-minute evidence review against matrix.
- Daily checkpoint: completed rows, open gaps, blockers.
- Freeze new feature development 48 hours before final demo unless critical bug fix.

---

## Section B: Requirements Traceability Matrix

### Status Key
- Verified Implemented: Requirement behaviour is present, evidenced in code, and supported by tests/demo.
- Deferred: Requirement intentionally moved out of current submission scope.

### Priority Key
- High: Core gameplay and core platform behaviour.
- Medium: Career depth, management systems, progression quality.
- Low: Polish, extended customization, advanced tools.

### Matrix
This matrix is limited to gameplay-facing use cases. Administrative, seed, and database-maintenance flows are excluded from the gameplay evidence set.

| Req ID | Requirement Summary | Priority | Status | Code Evidence | Test Evidence | Demo Evidence | Notes and Next Action |
|---|---|---|---|---|---|---|---|
| UC-1 | Read driver details | High | Verified Implemented | Momentum/Python/database/database_manager.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | GUI driver selection flow in launcher | Keep response schema stable for final demo |
| UC-2 | Read race configuration | High | Verified Implemented | Momentum/Python/GUI/gui_main_menu.py, Momentum/Python/GUI/launcher.py, Momentum/Python/GUI/gui_championship.py | Momentum/Python/tests/test_unit_gui_launcher_smoke.py | Quick Race setup screen and launcher flow | Keep config schema stable for final demo |
| UC-3 | Create race result | High | Verified Implemented | Momentum/Python/database/database_manager.py, Momentum/Python/RaceLogic/realtime_race_engine.py | Momentum/Python/mvp_tests/test_uc03_create_race_result.py | Race completion in GUI | Keep persistence alias for compatibility |
| UC-4 | Read race results | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship and race result views | Add response snapshot to report appendix |
| UC-5 | Read championship details | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship overview screen | Confirm no duplicate route declarations remain |
| UC-6 | Update championship standings | Medium | Verified Implemented | Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_unit_championship_rules.py, Momentum/Python/tests/test_integration_championship_flow.py | Standings refresh during season flow | Add tie-breaker example in report |
| UC-7 | Create race event | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship schedule management | Add negative test case evidence to appendix |
| UC-8 | Read race schedule | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship schedule view | Add season filter evidence |
| UC-9 | Update race status | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Race lifecycle transitions | Document valid transition rules in report |
| UC-10 | Create championship | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | New championship flow | Add output example to technical report |
| UC-11 | Read team details | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Team profile screen | Add role-based access note |
| UC-13 | Read player team details | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/team_service.py | Momentum/Python/tests/test_integration_api_contracts.py | Player team endpoint call | Verify header behaviour in demo script |
| UC-14 | Update team attributes | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Team edit interaction | Add optimistic locking explanation if used |
| UC-15 | Read available drivers | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Hiring browse flow | Add filtering demonstration |
| UC-16 | Update driver contract | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Contract update operation | Add salary cap example in appendix |
| UC-17 | Read available staff | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Staff listing flow | Add sort/filter evidence |
| UC-18 | Update staff contract | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Staff contract update | Add conflict handling evidence |
| UC-19 | Update driver skills and age | Medium | Verified Implemented | Momentum/Python/services/progression_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_full_career_season.py | End-of-season progression run | Add before/after attribute sample |
| UC-20 | Update team budget | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Budget allocate endpoint | Add budget transaction example |

### Coverage Summary (Revised)
- Verified Implemented: 19
- Deferred: 0

### Gap-Closure Checklist
1. Keep the gameplay-only scope statement aligned with the report body and presentation.
2. Align report language with this matrix status table before final submission.
3. Re-run full test suite after any status changes.

### Evidence Rules for Final Submission
1. Do not mark a requirement Verified Implemented unless there is both code and test evidence.
2. If evidence is incomplete or non-auditable, use Deferred and explain why.
3. Keep Notes and Next Action concrete and time-bounded.
4. Freeze matrix 24 hours before submission and include a final timestamped update.

---

## Section C: Evidence Integration Section (For Final Report)

### Purpose
This section standardizes how implementation evidence is presented so rubric claims are auditable and consistent.

### How to Use This Section
1. Reference the traceability matrix as the single source of truth for requirement status.
2. For each major rubric heading, include direct evidence links to code, tests, and demo artifacts.
3. Keep claims specific and measurable.

### Suggested Placement in Technical Report
- Insert after Implementation and before Testing and Evaluation.
- Cross-reference this section from Conclusions and Further Development.

### Section Template
#### 1. Requirements Coverage Evidence
- Provide totals from the matrix:
- Verified Implemented count
- Deferred count
- Explain why deferred items were excluded from current submission scope.

#### 2. Implementation Quality Evidence
- Summarize architecture by layer:
- API Layer: endpoints and validation
- Service Layer: business logic and rules
- Data Layer: persistence and schema integrity
- Simulation Layer: race engine and decision model
- Provide one concrete example per layer.

#### 3. Testing Evidence
- Include latest test run output summary.
- Split by test type:
- Unit tests
- Integration tests
- End-to-end or scenario tests
- Include key regression tests and why they matter.

#### 4. Prototype and Demo Evidence
- Provide a short demo pathway with expected outputs.
- Include fallback evidence:
- Backup recording
- Screenshots at critical checkpoints
- Link each checkpoint to requirement IDs.

#### 5. Limitations and Future Work Evidence
- List non-implemented requirements from the matrix.
- For each, include:
- Technical reason
- Risk impact
- Planned remedy

### Evidence Table Template
| Claim | Requirement IDs | Code Evidence | Test Evidence | Demo Evidence | Result |
|---|---|---|---|---|---|
| Championship lifecycle is implemented | UC-5, UC-6, UC-7, UC-8, UC-9, UC-10 | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship creation and schedule demo | Pass |
| Driver progression is season-aware | UC-19 | Momentum/Python/services/progression_service.py | Momentum/Python/tests/test_integration_full_career_season.py | Season completion demo | Pass |
| Hiring and contracts are operational | UC-15, UC-16, UC-17, UC-18 | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Hiring workflow demo | Pass |

### Writing Rules
1. Avoid generic statements such as fully implemented unless linked to direct evidence.
2. Use identical requirement IDs across matrix, report chapters, and slides.
3. Keep all evidence paths consistent with repository structure.
4. Prefer short factual statements over descriptive marketing language.

### Final Submission Checklist
1. Matrix status totals match statements in this section.
2. All Pass claims have at least one test reference.
3. Demo claims have screenshot or video evidence.
4. Deferred items are acknowledged in limitations and future work.