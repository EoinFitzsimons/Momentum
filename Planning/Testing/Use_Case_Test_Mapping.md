# Use-Case Test Mapping

## Use Case Coverage

| Use Case | Test Files                                                                                                                                           | Evidence                                                  |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| UC-1     | test_integration_api_contracts.py                                                                                                                    | Driver details API contract validation                    |
| UC-2     | test_integration_api_contracts.py                                                                                                                    | Team details API contract validation                      |
| UC-3     | test_integration_championship_flow.py                                                                                                                | Race configuration retrieval and validation               |
| UC-4     | test_integration_championship_flow.py                                                                                                                | Championship creation flow                                |
| UC-5     | test_integration_championship_flow.py                                                                                                                | Race scheduling within championship                       |
| UC-6     | test_integration_championship_flow.py                                                                                                                | Race execution                                            |
| UC-7     | test_integration_championship_flow.py                                                                                                                | Race result recording                                     |
| UC-8     | test_integration_championship_flow.py                                                                                                                | Championship progression calculation                      |
| UC-9     | test_integration_championship_flow.py                                                                                                                | Driver standings update                                   |
| UC-10    | test_integration_championship_flow.py                                                                                                                | Team standings update                                     |
| UC-11    | test_integration_api_contracts.py                                                                                                                    | Team details API contract validation                      |
| UC-12    | test_use_case_coverage.py (`test_uc12_create_team_and_uc13_read_team_details`)                                                                     | Team creation via `TeamService` and `DatabaseManager` |
| UC-13    | test_integration_api_contracts.py, test_use_case_coverage.py (`test_uc12_create_team_and_uc13_read_team_details`)                                  | Team profile retrieval via API and direct service         |
| UC-14    | test_integration_database_layer.py                                                                                                                   | Team attribute updates                                    |
| UC-15    | test_integration_api_contracts.py                                                                                                                    | Staff listing API contract validation                     |
| UC-16    | test_integration_database_layer.py                                                                                                                   | Staff contract signature recording                        |
| UC-17    | test_integration_api_contracts.py, test_use_case_coverage.py (`test_uc17_uc18_staff_hiring_flow`)                                                  | Staff listing via API and `HiringService`               |
| UC-18    | test_integration_database_layer.py, test_use_case_coverage.py (`test_uc17_uc18_staff_hiring_flow`)                                                 | Staff contract signing via database and service           |
| UC-19    | test_integration_full_career_season.py                                                                                                               | Full career season progression                            |
| UC-20    | test_integration_database_layer.py                                                                                                                   | Staff performance record updates                          |
| UC-21    | test_simulation_reproducibility.py, test_use_case_coverage.py (`test_uc21_uc22_generation_helpers_produce_valid_entities`)                         | Driver generation helpers produce usable payloads         |
| UC-22    | test_simulation_reproducibility.py, test_use_case_coverage.py (`test_uc21_uc22_generation_helpers_produce_valid_entities`)                         | Staff generation helpers produce usable payloads          |
| UC-23    | test_integration_championship_flow.py, test_use_case_coverage.py (`test_uc23_delete_championship_cascades_races_and_results`)                      | Championship deletion with cascade to races and results   |
| UC-24    | test_unit_track_surface_service.py, test_use_case_coverage.py (`test_uc24_uc25_create_and_update_track`)                                           | Custom track creation                                     |
| UC-25    | test_unit_track_surface_service.py, test_use_case_coverage.py (`test_uc24_uc25_create_and_update_track`)                                           | Track attribute updates                                   |
| UC-26    | test_unit_track_surface_service.py, test_use_case_coverage.py (`test_uc26_delete_track_removes_dependent_races_and_results`)                       | Track deletion with cascade to races and results          |
| UC-27    | test_discipline_edge_cases.py, test_integration_srs.py, test_use_case_coverage.py (`test_uc27_staff_performance_effects_feed_realtime_engine`)     | Staff roster effects feed the realtime race engine        |
| UC-28    | test_vehicle_rendering.py, test_vehicle_appearance_render.py, test_use_case_coverage.py (`test_uc28_uc29_vehicle_appearance_and_branding_helpers`) | Driver appearance helpers and rendering                   |
| UC-29    | test_vehicle_rendering.py, test_vehicle_appearance_render.py, test_use_case_coverage.py (`test_uc28_uc29_vehicle_appearance_and_branding_helpers`) | Team branding helpers and rendering                       |
