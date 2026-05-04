Test Cases (extracted from implemented test suite)
=================================================

This file maps the implemented pytest functions to concise names, their purpose (taken from test docstrings), and pytest markers used in the suite. Use these as the authoritative list for recording results.

1) Database integrity (file: test_database_integrity.py) — marker: integration
   - test_foreign_key_constraint_driver_team_relationship: Verify driver foreign key to team is enforced.
   - test_unique_constraint_prevents_duplicate_track_names: Verify track name retrieval and distinction.
   - test_domain_range_driver_attributes_within_bounds: Verify driver attribute domains preserved through CRUD.
   - test_team_budget_domain_preserved_through_crud: Verify team budget updates persist correctly.
   - test_cascade_delete_championship_removes_dependent_races: Verify cascade delete removes dependent races.
   - test_track_discipline_consistency: Verify track discipline enum validity.
   - test_no_orphaned_driver_references_to_teams: Ensure no orphaned driver->team references.
   - test_race_result_consistency_with_drivers: Verify race results reference valid drivers.

2) Performance (file: test_performance.py) — marker: performance (+ slow on some tests)
   - test_single_race_simulation_under_threshold: Single race < 1s.
   - test_batch_race_simulation_performance: 100 races < 30s and avg < 0.3s.
   - test_database_query_performance_driver_retrieval: Driver retrieval timing targets.
   - test_database_query_performance_team_lookup: Team lookup timing targets.
   - test_database_bulk_create_performance: Bulk driver creation performance.
   - test_database_query_consistency_under_load (slow): Query timing consistency under repeated access.
   - test_race_engine_initialization_performance (slow): Engine init timing target.

3) Statistical validation (file: test_statistical_validation.py) — marker: integration (+ slow for long races)
   - test_skill_attribute_affects_finishing_position: Skill correlates with finishing position.
   - test_upset_frequency_is_bounded: Upset frequency within expected bounds.
   - test_distribution_of_lap_times_is_plausible: Lap time distribution plausibility and variance.
   - test_randomness_seed_produces_consistent_results: Determinism for same seed.
   - test_different_seeds_produce_different_outcomes: Different seeds produce variation.
   - test_track_surface_affects_driver_performance: Surface affects performance.
   - test_long_race_distance_produces_consistent_winner (slow): Long races favor skilled drivers.

4) Integration flows and API contracts (various files) — marker: integration
   - test_integration_api_contracts.py: API contract and payload validations.
   - test_integration_championship_flow.py: Championship flow end-to-end.
   - test_integration_database_layer.py: Database access layer integration tests.
   - test_integration_full_career_season.py: Full career/season simulation flows.

5) GUI and accessibility checks
   - test_unit_gui_launcher_smoke.py — marker: unit: launcher starts and basic UI smoke checks.
   - test_accessibility_ui_checks.py — marker: unit: automated accessibility lint checks and manual checklist points.

6) Property-based and randomness checks
   - test_property_based_randomness.py — marker: unit: randomness and property-based characteristics.

7) Use-case coverage
   - test_use_case_coverage.py — marker: integration: maps implemented tests to documented use cases.

Notes and next steps
--------------------
- These test names and docstrings are the authoritative source; I will update `Test_Results.md` with per-test evidence (command snippets and short log excerpts) next.
- I will also reconcile and merge the existing `Plan.md` content with the plain-English Test Summary and remove the placeholder docs I added earlier unless you prefer to keep them.
