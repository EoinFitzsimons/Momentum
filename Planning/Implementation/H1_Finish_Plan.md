# H1 Finish Plan (Rubric-Aligned)

## Purpose
This plan converts the current repository state into examiner-ready evidence for the Final Examination Rubric.

## Rubric Weighting and Strategy
- Requirements Engineering (40%): Highest priority. Convert broad artifacts into traceable, verifiable evidence.
- Technology and Implementation (30%): Preserve current strength and remove final technical risks.
- Prototype (25%): Ensure reliable and repeatable live demonstration.
- Communication, Documentation, Showcase, Supervisor Interaction (remaining): Package work professionally and consistently.

## Workstream 1: Requirements Engineering (40%)
### Objective
Produce a complete and auditable trace from requirement to implementation, test, and demo evidence.

### Tasks
1. Complete and maintain the traceability matrix in Planning/Technical Report/Requirements_Traceability_Matrix.md.
2. For each requirement, assign one status only: Verified Implemented, Partially Implemented, Deferred.
3. Ensure each Verified Implemented row has:
- Code evidence
- Test evidence
- Demo evidence
4. For Partially Implemented and Deferred rows, add a reason and next action.

### Deliverables
- Completed matrix with no empty status cells.
- Requirement coverage summary (counts by status).

## Workstream 2: Technology and Implementation (30%)
### Objective
Eliminate known correctness risks and provide strong implementation proof.

### Tasks
1. Resolve duplicate route declaration risk in simulation API.
2. Run full backend test suite and store result output.
3. Prepare one implementation evidence page listing core modules and responsibilities.
4. Validate no IDE problems in critical files.

### Deliverables
- Clean API route map with no duplicate decorators.
- Passing test report snapshot.
- Implementation evidence section in report.

## Workstream 3: Prototype and Showcase (25% + 5%)
### Objective
Guarantee a smooth, reproducible demo under time pressure.

### Tasks
1. Create a deterministic demo runbook (launch command, steps, expected results).
2. Create backup demo video (60-120 seconds).
3. Capture screenshot evidence for setup, race, and result stages.
4. Prepare fallback plan for runtime issues.

### Deliverables
- Demo runbook markdown.
- Backup video file.
- Screenshot evidence page.

## Workstream 4: Documentation (10%)
### Objective
Raise report quality to thesis-like consistency and referencing standard.

### Tasks
1. Remove draft/export artifacts and stale sections.
2. Ensure consistent Harvard-style referencing throughout final report files.
3. Add concise test results appendix with key metrics.
4. Add explicit limitations and future work section linked to matrix deferred items.

### Deliverables
- Clean final report files.
- Bibliography and in-text reference consistency pass.
- Testing appendix with pass/fail summary and interpretation.

## Workstream 5: Communication and Viva Preparation (5% + 5%)
### Objective
Deliver a clear argument and answer questions with confidence.

### Tasks
1. Finalize presentation deck aligned with rubric language.
2. Rehearse 5-minute script with timing checkpoints.
3. Prepare concise answers for likely technical and design questions.
4. Keep supervisor interaction log updated with date, decision, and action.

### Deliverables
- Final slides.
- Q and A one-pager.
- Supervisor log.

## 7-Day Execution Sequence
1. Day 1: Complete matrix statuses and evidence links for all requirements.
2. Day 2: Fill evidence gaps for high-priority requirements.
3. Day 3: Implementation cleanup and full test verification.
4. Day 4: Demo runbook, screenshots, and backup recording.
5. Day 5: Documentation polish and reference consistency pass.
6. Day 6: Slide finalization and timed rehearsal.
7. Day 7: Full dry run under exam conditions.

## Definition of Done
1. Every requirement has one status and linked evidence.
2. All critical demo flows run without manual patching.
3. Full backend tests pass.
4. Report sections are coherent, referenced, and aligned with implementation truth.
5. Presentation and backup assets are ready and tested.

## Risk Register (Final Week)
| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Demo runtime issue | High | Medium | Backup video and fallback script |
| Requirement-evidence mismatch | High | Medium | Matrix validation pass before submission |
| Last-minute regression | Medium | Medium | Freeze window plus full regression test run |
| Documentation inconsistency | Medium | Medium | Single final editorial pass |

## Ownership and Cadence
- Daily 20-minute evidence review against matrix.
- Daily checkpoint: completed rows, open gaps, blockers.
- Freeze new feature development 48 hours before final demo unless critical bug fix.