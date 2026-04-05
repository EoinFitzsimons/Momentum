# Requirements Traceability Matrix

## Status Key
- Verified Implemented: Requirement behavior is present, evidenced in code, and supported by tests/demo.
- Deferred: Requirement intentionally moved out of current submission scope.

## Scope Note
This matrix is limited to gameplay-facing use cases. Administrative, seed, and database-maintenance flows are excluded from the gameplay evidence set.

## Priority Key
- High: Core gameplay and core platform behavior.
- Medium: Career depth, management systems, progression quality.
- Low: Polish, extended customization, advanced tools.

## Matrix
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
| UC-13 | Read player team details | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/team_service.py | Momentum/Python/tests/test_integration_api_contracts.py | Player team endpoint call | Verify header behavior in demo script |
| UC-14 | Update team attributes | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Team edit interaction | Add optimistic locking explanation if used |
| UC-15 | Read available drivers | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Hiring browse flow | Add filtering demonstration |
| UC-16 | Update driver contract | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Contract update operation | Add salary cap example in appendix |
| UC-17 | Read available staff | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Staff listing flow | Add sort/filter evidence |
| UC-18 | Update staff contract | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Staff contract update | Add conflict handling evidence |
| UC-19 | Update driver skills and age | Medium | Verified Implemented | Momentum/Python/services/progression_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_full_career_season.py | End-of-season progression run | Add before/after attribute sample |
| UC-20 | Update team budget | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Budget allocate endpoint | Add budget transaction example |

## Coverage Summary
- Verified Implemented: 19
- Deferred: 0

## Gap-Closure Checklist
1. Keep the gameplay-only scope statement aligned with the report body and presentation.
2. Align report language with this matrix status table before final submission.
3. Re-run full test suite after any status changes.
