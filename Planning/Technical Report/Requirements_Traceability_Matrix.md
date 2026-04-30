# Requirements Traceability Matrix

## Status Key
- Verified Implemented: Requirement behaviour is present, evidenced in code, and supported by tests/demo.
- Deferred: Requirement intentionally moved out of current submission scope.

## Scope Note
This matrix maps UC-1 to UC-29. Core gameplay use cases are marked from code and tests; administrative, generation, and cosmetic flows are marked where the current repository supports them or deferred where the user-facing workflow is not yet part of the delivered scope.

## Priority Key
- High: Core gameplay and core platform behaviour.
- Medium: Career depth, management systems, progression quality.
- Low: Polish, extended customization, advanced tools.

## Matrix
| Req ID | Requirement Summary | Priority | Status | Code Evidence | Test Evidence | Demo Evidence | Notes and Next Action |
|---|---|---|---|---|---|---|---|
| UC-1 | Read driver details | High | Verified Implemented | Momentum/Python/database/database_manager.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | GUI driver selection flow in launcher | Keep response schema stable for final demo |
| UC-2 | Read race configuration | High | Verified Implemented | Momentum/Python/GUI/gui_main_menu.py, Momentum/Python/GUI/launcher.py, Momentum/Python/GUI/gui_championship.py | Momentum/Python/tests/test_unit_gui_launcher_smoke.py | Quick Race setup screen and launcher flow | Keep config schema stable for final demo |
| UC-3 | Create race result | High | Verified Implemented | Momentum/Python/database/database_manager.py, Momentum/Python/RaceLogic/realtime_race_engine.py | Momentum/Python/tests/test_integration_full_career_season.py | Race completion in GUI | Keep persistence alias for compatibility |
| UC-4 | Read race results | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship and race result views | Add response snapshot to report appendix |
| UC-5 | Read championship details | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship overview screen | Confirm no duplicate route declarations remain |
| UC-6 | Update championship standings | Medium | Verified Implemented | Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_unit_championship_rules.py, Momentum/Python/tests/test_integration_championship_flow.py | Standings refresh during season flow | Add tie-breaker example in report |
| UC-7 | Create race event | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship schedule management | Add negative test case evidence to appendix |
| UC-8 | Read race schedule | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship schedule view | Add season filter evidence |
| UC-9 | Update race status | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | Race lifecycle transitions | Document valid transition rules in report |
| UC-10 | Create championship | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/championship_service.py | Momentum/Python/tests/test_integration_championship_flow.py | New championship flow | Add output example to technical report |
| UC-11 | Read team details | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Team profile screen | Add role-based access note |
| UC-12 | Create team | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_use_case_coverage.py | Team creation flow | Confirm the returned team schema stays stable |
| UC-13 | Read player team details | Medium | Verified Implemented | Momentum/Python/simulation.py, Momentum/Python/services/team_service.py | Momentum/Python/tests/test_integration_api_contracts.py | Player team endpoint call | Verify header behaviour in demo script |
| UC-14 | Update team attributes | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Team edit interaction | Add optimistic locking explanation if used |
| UC-15 | Read available drivers | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Hiring browse flow | Add filtering demonstration |
| UC-16 | Update driver contract | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Contract update operation | Add salary cap example in appendix |
| UC-17 | Read available staff | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_api_contracts.py | Staff listing flow | Add sort/filter evidence |
| UC-18 | Update staff contract | Medium | Verified Implemented | Momentum/Python/services/hiring_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Staff contract update | Add conflict handling evidence |
| UC-19 | Update driver skills and age | Medium | Verified Implemented | Momentum/Python/services/progression_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_full_career_season.py | End-of-season progression run | Add before/after attribute sample |
| UC-20 | Update team budget | Medium | Verified Implemented | Momentum/Python/services/team_service.py, Momentum/Python/simulation.py | Momentum/Python/tests/test_integration_database_layer.py | Budget allocate endpoint | Add budget transaction example |
| UC-21 | Create new driver | Low | Deferred | Momentum/Python/scripts/seed_career_mode.py, Momentum/Python/scripts/generate_discipline_tracks.py | Momentum/Python/tests/test_simulation_reproducibility.py, Momentum/Python/tests/test_use_case_coverage.py | Driver pool generation scripts | Current build reuses the seeded driver pool instead of exposing a delivered create-driver workflow |
| UC-22 | Create new staff member | Low | Deferred | Momentum/Python/scripts/seed_career_mode.py | Momentum/Python/tests/test_simulation_reproducibility.py, Momentum/Python/tests/test_use_case_coverage.py | Staff pool generation scripts | Current build reuses the seeded staff pool instead of exposing a delivered create-staff workflow |
| UC-23 | Delete championship | Low | Verified Implemented | Momentum/Python/database/database_manager.py, Momentum/Python/GUI/gui_championship.py, Momentum/Python/GUI/gui_career.py | Momentum/Python/tests/test_integration_championship_flow.py | Championship management delete action | Database manager and GUI both expose championship deletion |
| UC-24 | Create custom track | Low | Deferred | Momentum/Python/database/database_manager.py, Momentum/Python/scripts/generate_discipline_tracks.py, Momentum/Python/services/track_surface_service.py | Momentum/Python/tests/test_unit_track_surface_service.py, Momentum/Python/tests/test_use_case_coverage.py | Track generation tools and exports | The repository supports track generation tooling, but not a finished end-user custom-track creation flow |
| UC-25 | Update track characteristics | Low | Deferred | Momentum/Python/database/database_manager.py, Momentum/Python/services/track_surface_service.py | Momentum/Python/tests/test_unit_track_surface_service.py, Momentum/Python/tests/test_use_case_coverage.py | Track surface and generation tooling | Track surface updates exist at the data/service level; the editable management flow is not delivered as a user feature |
| UC-26 | Delete track | Low | Deferred | Momentum/Python/database/database_manager.py, Momentum/Python/scripts/generate_discipline_tracks.py | Momentum/Python/tests/test_unit_track_surface_service.py, Momentum/Python/tests/test_use_case_coverage.py | Track generation and maintenance tooling | Track removal/archival is not exposed as a finished end-user workflow |
| UC-27 | Read staff performance modifiers | Medium | Verified Implemented | Momentum/Python/RaceLogic/realtime_race_engine.py, Momentum/Python/RaceLogic/track_physics.py, Momentum/Python/services/driver_attributes.py | Momentum/Python/tests/test_discipline_edge_cases.py, Momentum/Python/tests/test_integration_srs.py, Momentum/Python/tests/test_use_case_coverage.py | Staff modifiers are consumed by simulation | Simulation reads staff-driven modifiers through the engine and helper layer |
| UC-28 | Update driver appearance | Low | Verified Implemented | Momentum/Python/vehicles/appearance_integration.py, Momentum/Python/vehicles/vehicle_appearance.py, Momentum/Python/GUI/gui_race_visual.py | Momentum/Python/tests/test_vehicle_rendering.py, Momentum/Python/tests/test_vehicle_appearance_render.py, Momentum/Python/tests/test_use_case_coverage.py | Livery and vehicle appearance rendering | Cosmetic driver appearance is implemented through the vehicle appearance system |
| UC-29 | Update team branding | Low | Verified Implemented | Momentum/Python/vehicles/appearance_integration.py, Momentum/Python/vehicles/vehicle_appearance.py, Momentum/Python/GUI/gui_race_visual.py | Momentum/Python/tests/test_vehicle_rendering.py, Momentum/Python/tests/test_vehicle_appearance_render.py, Momentum/Python/tests/test_use_case_coverage.py | Team livery and branding rendering | Team branding is implemented through livery/appearance generation and rendering |

## Coverage Summary
- Verified Implemented: 23
- Deferred: 6

## Gap-Closure Checklist
1. Keep the scope note aligned with the report body and presentation.
2. Align report language with this matrix status table before final submission.
3. Re-run the full test suite after any status changes.
4. Treat Momentum/Python/tests/test_use_case_coverage.py as the canonical UC mapping test file for the late-stage coverage gaps.
