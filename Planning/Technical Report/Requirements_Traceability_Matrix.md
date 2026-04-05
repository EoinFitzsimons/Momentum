# Requirements Traceability Matrix

## Status Key
- Verified Implemented: Requirement behavior is present, evidenced in code, and supported by tests/demo.
- Partially Implemented: Core behavior exists but has missing integration, incomplete validation, or missing test/demo proof.
- Deferred: Requirement intentionally moved out of current submission scope.

## Priority Key
- High: Core gameplay and core platform behavior.
- Medium: Career depth, management systems, progression quality.
- Low: Polish, extended customization, advanced tools.

## Matrix
| Req ID | Requirement Summary | Priority | Status | Code Evidence | Test Evidence | Demo Evidence | Notes and Next Action |
|---|---|---|---|---|---|---|---|
| UC-1 | Read driver details | High | Verified Implemented | Momentum/Python/database/database_manager.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | GUI driver selection flow in launcher | Keep response schema stable for final demo |
| UC-2 | Read race configuration | High | Partially Implemented | Momentum/Python/GUI/gui_main_menu.py, Momentum/Python/services/race_simulation_api.py | Momentum/Python/mvp_tests/test_uc02_race_config.py | Quick Race setup screen | Add explicit API contract test for configuration payload |
| UC-3 | Create race result | High | Partially Implemented | Momentum/Python/services/persistence_sqlite.py, Momentum/Python/RaceLogic/realtime_race_engine.py | Momentum/Python/mvp_tests/test_uc03_create_race_result.py | Race completion in GUI | Add unified persistence call in default GUI flow |
| UC-4 | Read race results | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship and race result views | Add response snapshot to report appendix |
| UC-5 | Read championship details | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship overview screen | Confirm no duplicate route declarations remain |
| UC-6 | Update championship standings | Medium | Verified Implemented | Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_unit_championship_rules.py, Momentum/Python/tests/test_integration_championship_flow.py | Standings refresh during season flow | Add tie-breaker example in report |
| UC-7 | Create race event | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship schedule management | Add negative test case evidence to appendix |
| UC-8 | Read race schedule | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship schedule view | Add season filter evidence |
| UC-9 | Update race status | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Race lifecycle transitions | Document valid transition rules in report |
| UC-10 | Create championship | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | New championship flow | Add output example to technical report |
| UC-11 | Read team details | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Team profile screen | Add role-based access note |
| UC-12 | Create new team | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Team creation path | Add validation matrix for team fields |
| UC-13 | Read player team details | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/team_service.py | Momentum/Python/tests/test_integration_api_contracts.py | Player team endpoint call | Verify header behavior in demo script |
| UC-14 | Update team attributes | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Team edit interaction | Add optimistic locking explanation if used |
| UC-15 | Read available drivers | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Hiring browse flow | Add filtering demonstration |
| UC-16 | Update driver contract | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Contract update operation | Add salary cap example in appendix |
| UC-17 | Read available staff | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Staff listing flow | Add sort/filter evidence |
| UC-18 | Update staff contract | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Staff contract update | Add conflict handling evidence |
| UC-19 | Update driver skills and age | Medium | Verified Implemented | Momentum/Python/services/progression_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_full_career_season.py | End-of-season progression run | Add before/after attribute sample |
| UC-20 | Update team budget | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Budget allocate endpoint | Add budget transaction example |
| UC-21 | Create new driver | Low | Partially Implemented | Momentum/Python/database/database_manager.py, seed scripts | Momentum/Python/tests/test_integration_database_layer.py | Admin or script flow | Add dedicated API endpoint and contract test |
| UC-22 | Create new staff member | Low | Partially Implemented | Momentum/Python/database/database_manager.py, seed scripts | Momentum/Python/tests/test_integration_database_layer.py | Staff seed flow | Add dedicated API endpoint and validation tests |
| UC-23 | Delete championship | Low | Partially Implemented | Momentum/Python/database/database_manager.py | No dedicated automated test yet | Maintenance path only | Add endpoint, guardrails, and integration tests |
| UC-24 | Create custom track | Low | Partially Implemented | Momentum/Python/scripts/import_circuits.py, database layer | No dedicated automated test yet | Script-based setup | Add API and form-based creation flow |
| UC-25 | Update track characteristics | Low | Partially Implemented | Momentum/Python/services/track_surface_service.py, database layer | Momentum/Python/tests/test_unit_track_surface_service.py | Track data pipeline evidence | Add endpoint-level update test |
| UC-26 | Delete track | Low | Deferred | Database-level operations only | No dedicated automated test yet | Not in live demo scope | Keep deferred and explain rationale in report |
| UC-27 | Read staff performance modifiers | Low | Partially Implemented | Momentum/Python/config.py, Momentum/Python/services/hiring_service.py | No dedicated automated test yet | Hiring and staffing narrative | Add explicit endpoint and contract test |
| UC-28 | Update driver appearance | Low | Partially Implemented | Momentum/Python/vehicles/vehicle_appearance.py, GUI integration | No dedicated automated test yet | Visual customization demo path | Add persistence and regression tests |
| UC-29 | Update team branding | Low | Partially Implemented | GUI and vehicle appearance modules | No dedicated automated test yet | Visual identity workflow | Add API or persistence proof |

## Coverage Summary (Initial Baseline)
- Verified Implemented: 18
- Partially Implemented: 10
- Deferred: 1

## Gap-Closure Checklist
1. Add missing automated tests for low-priority but claimed features.
2. Add explicit endpoint evidence where behavior currently exists only in scripts.
3. Align report language with this matrix status table before final submission.
4. Re-run full test suite after any status changes.

## Evidence Rules for Final Submission
1. Do not mark a requirement Verified Implemented unless there is both code and test evidence.
2. If demo-only evidence exists but no test evidence, use Partially Implemented.
3. Keep Notes and Next Action concrete and time-bounded.
4. Freeze matrix 24 hours before submission and include a final timestamped update.