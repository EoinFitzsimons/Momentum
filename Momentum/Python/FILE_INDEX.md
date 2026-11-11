# Momentum/Python — Per-file Index

This file is an automated, hand-curated per-file index with a concise one-line summary for every file under `Momentum/Python`.

## Top-level

- [Momentum/Python/__init__.py](__init__.py): Package initializer for the Python package (ensures imports work during tests and simple runners).
- [Momentum/Python/config.py](config.py): Environment-driven configuration and constants for simulation, DB paths, API and simulation parameters.
- [Momentum/Python/logging_system.py](logging_system.py): Centralized singleton logging system and crash-report utilities.
- [Momentum/Python/init_db.py](init_db.py): Script to initialise and validate the SQLite database schema for development/testing.
- [Momentum/Python/quick_check.py](quick_check.py): Lightweight DB schema quick-check utility used in CI/dev.
- [Momentum/Python/simulation.py](simulation.py): FastAPI application entrypoint exposing the public REST API for championships, races, teams, hiring and progression.
- [Momentum/Python/Momentum.spec](Momentum.spec): PyInstaller spec used to build the packaged Momentum executable.
- [Momentum/Python/requirements.txt](requirements.txt): Runtime Python dependencies list.
- [Momentum/Python/requirements-dev.txt](requirements-dev.txt): Development and test dependencies.
- [Momentum/Python/pytest.ini](pytest.ini): Pytest configuration for running the test suite.
- [Momentum/Python/mypy.ini](mypy.ini): MyPy static type-checker configuration.
- [Momentum/Python/.flake8](.flake8): Flake8 linting configuration.

## API

- [Momentum/Python/api/__init__.py](api/__init__.py): API package marker.
- [Momentum/Python/api/schemas.py](api/schemas.py): Pydantic request/response models and schema definitions for the FastAPI endpoints.

## Database

- [Momentum/Python/database/database_manager.py](database/database_manager.py): Core SQLite database manager with schema init, migrations, and CRUD operations.
- [Momentum/Python/database/database_factory.py](database/database_factory.py): Helper to create or configure database instances (factory pattern).
- [Momentum/Python/database/database_extensions.py](database/database_extensions.py): Utility DB extensions (row factory, helpers) to augment sqlite connections.
- [Momentum/Python/database/migration_scaffold.py](database/migration_scaffold.py): Migration scaffolding and helper functions to apply DB updates safely.
- [Momentum/Python/database/race_result_persistence.py](database/race_result_persistence.py): Abstraction for persisting and querying race results.
- [Momentum/Python/database/momentum.db.mig](database/momentum.db.mig): Bundled migrated DB fixture (binary DB backup used for packaging/seeding).
- [Momentum/Python/database/momentum.db.mig.backup](database/momentum.db.mig.backup): Backup of the bundled DB.
- [Momentum/Python/database/models.py](database/models.py): Legacy re-export shim pointing to `database/models/__init__.py` for backward compatibility.
- [Momentum/Python/database/models/__init__.py](database/models/__init__.py): Data models (Driver, Team, Track, Championship, Race, RaceResult) and `SCHEMA_SQL` definition.
- [Momentum/Python/database/models/multi_discipline_models.py](database/models/multi_discipline_models.py): Discipline-aware data structures and model specialisations.

## Services

- [Momentum/Python/services/championship_service.py](services/championship_service.py): Championship lifecycle logic: points systems, standings calculation, calendar and tie-break rules.
- [Momentum/Python/services/team_service.py](services/team_service.py): Team management business logic (create/update teams, budgets, allocations).
- [Momentum/Python/services/hiring_service.py](services/hiring_service.py): Hiring, contract and staff/driver availability logic.
- [Momentum/Python/services/progression_service.py](services/progression_service.py): Season progression and promotion/relegation rules.
- [Momentum/Python/services/race_simulation_api.py](services/race_simulation_api.py): Helpers to run and persist race simulations, context population and fallback behaviour.
- [Momentum/Python/services/race_engine_factory.py](services/race_engine_factory.py): Factory functions to create discipline-specific race engines and realtime engines.
- [Momentum/Python/services/progression_service.py](services/progression_service.py): (duplicate listing) season progression helpers.
- [Momentum/Python/services/career_season_service.py](services/career_season_service.py): Career mode season orchestration and results handling.
- [Momentum/Python/services/career_result_service.py](services/career_result_service.py): Persisting career-mode race results and mapping to career progression.
- [Momentum/Python/services/persistence_sqlite.py](services/persistence_sqlite.py): SQLite-backed persistence adapter used by higher-level services.
- [Momentum/Python/services/track_surface_service.py](services/track_surface_service.py): Surface and grip profile helper calculations used by racing logic.
- [Momentum/Python/services/driver_attributes.py](services/driver_attributes.py): Driver attribute normalisers and useful derived getters for UI/logic.

## RaceLogic

- [Momentum/Python/RaceLogic/base_race_engine.py](RaceLogic/base_race_engine.py): Base discipline engine with performance models, reliability, incident checks, and points mapping.
- [Momentum/Python/RaceLogic/realtime_race_engine.py](RaceLogic/realtime_race_engine.py): 30 FPS agent-based realtime race engine (AI drivers, overtaking, tyre/fuel models).
- [Momentum/Python/RaceLogic/track_physics.py](RaceLogic/track_physics.py): Track maps, sections and racing line structures used by realtime engine.
- [Momentum/Python/RaceLogic/overtaking_system.py](RaceLogic/overtaking_system.py): Overtake opportunity evaluation and outcome resolution utilities.
- [Momentum/Python/RaceLogic/closure_solver.py](RaceLogic/closure_solver.py): Circuit closure solver using SciPy to ensure generated track instructions form closed loops.
- [Momentum/Python/RaceLogic/disciplines/single_seater/single_seater_discipline.py](RaceLogic/disciplines/single_seater/single_seater_discipline.py): Discipline adapter: single-seater rules and calibrations.
- [Momentum/Python/RaceLogic/disciplines/endurance/endurance_discipline.py](RaceLogic/disciplines/endurance/endurance_discipline.py): Endurance discipline adapter and race rules.
- [Momentum/Python/RaceLogic/disciplines/production_touring/production_touring_discipline.py](RaceLogic/disciplines/production_touring/production_touring_discipline.py): Production/Touring discipline adapter.
- [Momentum/Python/RaceLogic/disciplines/urban_street/urban_street_discipline.py](RaceLogic/disciplines/urban_street/urban_street_discipline.py): Urban/Street (drifting) discipline adapter.
- [Momentum/Python/RaceLogic/disciplines/drag_acceleration/drag_acceleration_discipline.py](RaceLogic/disciplines/drag_acceleration/drag_acceleration_discipline.py): Drag/Acceleration discipline adapter.
- [Momentum/Python/RaceLogic/disciplines/sprint_rallycross/sprint_rallycross_discipline.py](RaceLogic/disciplines/sprint_rallycross/sprint_rallycross_discipline.py): Sprint/Rallycross discipline adapter.

## GUI

- [Momentum/Python/GUI/launcher.py](GUI/launcher.py): Application launcher that boots QApplication, main menu, and race visual windows; handles race flow routing.
- [Momentum/Python/GUI/gui_main_menu.py](GUI/gui_main_menu.py): Main menu UI with race selection, quick-race lists and driver cards.
- [Momentum/Python/GUI/gui_race_visual.py](GUI/gui_race_visual.py): Race visualiser window integrating simulation engine, rendering, and controls.
- [Momentum/Python/GUI/gui_championship.py](GUI/gui_championship.py): Championship management UI and pre-race setup dialogs.
- [Momentum/Python/GUI/gui_career.py](GUI/gui_career.py): Career mode HQ window and progression controls.
- [Momentum/Python/GUI/window_utils.py](GUI/window_utils.py): Window sizing and helper utilities for PyQt windows.
- [Momentum/Python/GUI/infield_presets.py](GUI/infield_presets.py): Presets for infield prop placement and decoration.
- [Momentum/Python/GUI/props_placer.py](GUI/props_placer.py): Utilities to position scenery props on generated track images.
- [Momentum/Python/GUI/themed_messagebox.py](GUI/themed_messagebox.py): Themed messagebox wrappers (info/warning dialogs).
- [Momentum/Python/GUI/accessibility_settings.py](GUI/accessibility_settings.py): Accessibility profile storage and application helpers.
- [Momentum/Python/GUI/responsive_utils.py](GUI/responsive_utils.py): Responsive layout helpers to support multiple window sizes.
- [Momentum/Python/GUI/props_placer.py](GUI/props_placer.py): (duplicate listing) prop placement utilities.
- [Momentum/Python/GUI/GUI assets (images & props)](GUI/assets/): Image assets (grass tiles, prop PNGs) used by the GUI.
- [Momentum/Python/GUI/tools/generate_placeholder_sprites.py](GUI/tools/generate_placeholder_sprites.py): Helper to generate placeholder sprites for packaging/testing.
- [Momentum/Python/GUI/tools/generate_grass_tile.py](GUI/tools/generate_grass_tile.py): Utility to procedural generate grass tile textures.

## Vehicles

- [Momentum/Python/vehicles/__init__.py](vehicles/__init__.py): Vehicles package initializer.
- [Momentum/Python/vehicles/vehicle_appearance.py](vehicles/vehicle_appearance.py): Vehicle livery and render helpers used by the GUI.
- [Momentum/Python/vehicles/appearance_integration.py](vehicles/appearance_integration.py): Integration glue for vehicle appearance and discipline mapping.
- [Momentum/Python/vehicles/generate_vehicle_previews.py](vehicles/generate_vehicle_previews.py): Script to generate preview images for vehicle types.
- [Momentum/Python/vehicles/previews/*](vehicles/previews/): A set of preview PNGs used in the GUI to show vehicle thumbnails.

## Data & scripts

- [Momentum/Python/data/circuits_database.json](data/circuits_database.json): Seed circuit definitions used to populate the DB and GUI.
- [Momentum/Python/data/countries.py](data/countries.py): Country list and utility used for nationality UI elements.
- [Momentum/Python/scripts/import_circuits.py](scripts/import_circuits.py): Script to import circuits into the database from JSON sources.
- [Momentum/Python/scripts/import_circuits_idempotent.py](scripts/import_circuits_idempotent.py): Idempotent variant of circuits import.
- [Momentum/Python/scripts/generate_discipline_tracks.py](scripts/generate_discipline_tracks.py): Generate track lists per discipline from base circuits.
- [Momentum/Python/scripts/run_sim_and_persist.py](scripts/run_sim_and_persist.py): Headless simulation runner that persists results to DB.
- [Momentum/Python/scripts/seed_career_mode.py](scripts/seed_career_mode.py): Seed career tables for local testing.
- [Momentum/Python/scripts/run_full_career_season.py](scripts/run_full_career_season.py): Script to run a full career season in batch mode.
- [Momentum/Python/scripts/build_exe.ps1](scripts/build_exe.ps1): PowerShell helper to run PyInstaller and create `dist/` package.
- [Momentum/Python/scripts/install_requirements.ps1](scripts/install_requirements.ps1): Windows helper to install requirements via pip.
- [Momentum/Python/scripts/inspect_db_schema.py](scripts/inspect_db_schema.py): Utility to introspect DB schema and print table info.
- [Momentum/Python/scripts/migrate_tire_to_tyre.py](scripts/migrate_tire_to_tyre.py): One-off migration script renaming tyre/tire columns.

## Tools

- [Momentum/Python/tools/*](tools/): Misc developer utilities (track validators, debug renderers, capture screenshot helpers, etc.) used for testing and asset generation.
- Notable: `tools/track_smoke_test.py`, `tools/inspect_render.py`, `tools/capture_accessibility_screenshots.py`, `tools/validate_track_routes.py`.

## Tests

- [Momentum/Python/tests/conftest.py](tests/conftest.py): Pytest fixtures creating deterministic test DBs and test clients.
- [Momentum/Python/tests/test_integration_api_contracts.py](tests/test_integration_api_contracts.py): Integration tests validating the public API contracts.
- [Momentum/Python/tests/test_simulation_reproducibility.py](tests/test_simulation_reproducibility.py): Tests ensuring deterministic simulation when seeded.
- Additional unit/integration tests covering RaceLogic disciplines, DB migrations, GUI smoke tests, and performance checks.

## Docs

- [Momentum/Python/docs/CHAMPIONSHIP_MANAGEMENT.md](docs/CHAMPIONSHIP_MANAGEMENT.md): Design doc for championship lifecycle and rules.
- [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](docs/MATHEMATICS_AND_FUNCTION_SOURCES.md): Math and formulas used across race engines.
- [Momentum/Python/docs/data_model.drawio](docs/data_model.drawio): Diagram source for the DB/data model.

## Packaging & distribution

- [Momentum/Python/dist/Momentum/Momentum.exe](dist/Momentum/Momentum.exe): Packaged Windows executable (PyInstaller output) — binary distribution.

---

## Full per-file listing (every file path)

Below are every file under `Momentum/Python` listed individually with a concise one-line summary.

<!-- AUTO-GENERATED LIST START -->

mypy.ini — MyPy configuration for static type checking.
momentum.spec — PyInstaller spec to build the packaged executable.
logging_system.py — Centralized singleton logging system and crash-report utilities.
init_db.py — Script to initialise and validate the SQLite database schema for development/testing.
__init__.py — Package initializer for the Python package (ensures imports work during tests and simple runners).
vehicles/__init__.py — Vehicles package initializer.
vehicles/vehicle_appearance.py — Vehicle livery and render helpers used by the GUI.
GUI/gui_career.py — Career mode HQ window and progression controls.
vehicles/previews/urban_street_steering.png — Binary preview asset (image).
vehicles/previews/urban_street_preview.png — Binary preview asset (image).
vehicles/previews/sprint_rallycross_steering.png — Binary preview asset (image).
vehicles/previews/sprint_rallycross_preview.png — Binary preview asset (image).
vehicles/previews/single_seater_steering.png — Binary preview asset (image).
vehicles/previews/single_seater_preview.png — Binary preview asset (image).
vehicles/previews/production_touring_steering.png — Binary preview asset (image).
vehicles/previews/production_touring_preview.png — Binary preview asset (image).
vehicles/previews/endurance_steering.png — Binary preview asset (image).
vehicles/previews/endurance_preview.png — Binary preview asset (image).
vehicles/previews/drag_acceleration_preview.png — Binary preview asset (image).
vehicles/generate_vehicle_previews.py — Script to generate preview images for vehicle types.
vehicles/appearance_integration.py — Integration glue for vehicle appearance and discipline mapping.
GUI/window_utils.py — Window sizing and helper utilities for PyQt windows.
data/circuits_database.json — Seed circuit definitions used to populate the DB and GUI.
config.py — Environment-driven configuration and constants for simulation, DB paths, API and simulation parameters.
data/countries.py — Country list and utility used for nationality UI elements.
GUI/tools/generate_placeholder_sprites.py — Helper to generate placeholder sprites for packaging/testing.
GUI/tools/generate_grass_tile.py — Utility to procedural generate grass tile textures.
GUI/themed_messagebox.py — Themed messagebox wrappers (info/warning dialogs).
GUI/responsive_utils.py — Responsive layout helpers to support multiple window sizes.
GUI/props_placer.py — Utilities to position scenery props on generated track images.
GUI/launcher.py — Application launcher that boots QApplication, main menu, and race visual windows; handles race flow routing.
GUI/infield_presets.py — Presets for infield prop placement and decoration.
GUI/gui_race_visual.py — Race visualiser window integrating simulation engine, rendering, and controls.
GUI/gui_navbar.py — GUI navigation bar component.
GUI/gui_main_menu.py — Main menu UI with race selection, quick-race lists and driver cards.
GUI/gui_championship.py — Championship management UI and pre-race setup dialogs.
tools/capture_accessibility_screenshots.py — Tool to capture accessibility variants of GUI screens.
tools/calibrate_3lap.py — Tool to calibrate lap timing parameters.
tools/accessibility_check.py — Accessibility check utilities for UI.
.flake8 — Flake8 linting configuration.
docs/MATHEMATICS_AND_FUNCTION_SOURCES.md — Math and formulas used across race engines.
docs/MATHEMATICS_AND_FUNCTION_SOURCES.docx — Binary docx of the mathematics doc.
docs/data_model.drawio — Diagram source for the DB/data model.
docs/CHAMPIONSHIP_MANAGEMENT.md — Design doc for championship lifecycle and rules.
GUI/accessibility_settings.py — Accessibility profile storage and application helpers.
FILE_INDEX.md — This per-file index (auto-generated and editable).
GUI/assets/grass_tile.png — Binary GUI asset (grass tile image).
requirements.txt — Runtime Python dependencies list.
requirements-dev.txt — Development and test dependencies.
database/migration_scaffold.py — Migration scaffolding and helper functions to apply DB updates safely.
database/database_manager.py — Core SQLite database manager with schema init, migrations, and CRUD operations.
database/database_factory.py — Helper to create or configure database instances (factory pattern).
database/database_extensions.py — Utility DB extensions (row factory, helpers) to augment sqlite connections.
database/models.py — Legacy re-export shim pointing to `database/models/__init__.py` for backward compatibility.
database/race_result_persistence.py — Abstraction for persisting and querying race results.
database/momentum.db.mig.backup — Bundled DB backup (binary).
database/momentum.db.mig — Bundled migrated DB fixture (binary).
pytest.ini — Pytest configuration for running the test suite.
quick_check.py — Lightweight DB schema quick-check utility used in CI/dev.
simulation.py — FastAPI application entrypoint exposing the public REST API for championships, races, teams, hiring and progression.
task_script.py — Misc task runner script used by developers.
tools/gui_tracks_to_png.py — Tool to render track images to PNG for GUI previews.
tools/find_nonascii.py — Utility to find non-ASCII characters in sources.
tools/ENDURANCE_Momentum_Endurance_Circuit.png — Binary asset (track preview image).
tools/DRAG_ACCELERATION_Momentum_Drag_Strip.png — Binary asset (track preview image).
tools/debug_validate_row.py — Debug utility for validating DB rows.
tools/debug_validate_choice.py — Debug utility for validating choice tables.
tools/debug_tune_track_loops.py — Debug tool for track loop tuning.
tools/debug_infield_props.png — Binary debug image.
tools/debug_infield_pixmap.png — Binary debug image.
tools/debug_infield_assets.py — Debug helper for infield assets.
tools/count_pngs.py — Utility to count PNG assets in folders.
tools/count_circuits.py — Utility to count circuits in JSON.
tools/capture_all_screens.py — Tool to capture all GUI screens for review.
tools/capture_accessibility_variants.py — Tool to capture accessibility variants.
tools/print_drivers.py — Quick utility to print sample drivers from DB.
tools/preview_solved_track.png — Binary preview image.
tools/locale_mapping.py — Locale mapping helper.
tools/list_tracks.py — List available tracks from DB.
tools/inspect_tracks.py — Inspect track definitions and validate.
tools/inspect_render.py — Inspect rendering output for track previews.
tools/import_circuits_idempotent.py — Idempotent circuits importer script.
tools/render_preview_track.py — Render preview images for tracks.
tools/render_infield_test.py — Render infield test images.
tools/PRODUCTION_TOURING_Momentum_Touring_Circuit.png — Binary asset (track image).
tools/schema_validator.py — Schema validation helper for input payloads.
tools/run_debug_with_app.py — Run debug harness with application context.
tools/SINGLE_SEATER_Momentum_Grand_Prix_Circuit.png — Binary asset (track image).
database/models/__init__.py — Data models (Driver, Team, Track, Championship, Race, RaceResult) and `SCHEMA_SQL` definition.
database/models/multi_discipline_models.py — Discipline-aware data structures and model specialisations.
RaceLogic/track_physics.py — Track maps, sections and racing line structures used by realtime engine.
dist/Momentum/Momentum.exe — Packaged Windows executable (binary).
services/career_season_service.py — Career mode season orchestration and results handling.
RaceLogic/realtime_race_engine.py — 30 FPS agent-based realtime race engine (AI drivers, overtaking, tyre/fuel models).
RaceLogic/overtaking_system.py — Overtake opportunity evaluation and outcome resolution utilities.
scripts/install_requirements_force_bezier.ps1 — Windows helper to install requirements with force-bezier option.
scripts/install_requirements.ps1 — Windows helper to install requirements via pip.
scripts/inspect_db_schema.py — Utility to introspect DB schema and print table info.
scripts/import_circuits.py — Script to import circuits into the database from JSON sources.
scripts/generate_discipline_tracks.py — Generate track lists per discipline from base circuits.
scripts/build_exe.ps1 — PowerShell helper to run PyInstaller and create `dist/` package.
scripts/run_full_career_season.py — Script to run a full career season in batch mode.
scripts/print_sample_drivers.py — Script to print sample drivers for debugging.
scripts/migrate_tire_to_tyre.py — One-off migration script renaming tyre/tire columns.
scripts/seed_career_mode.py — Seed career tables for local testing.
scripts/run_sim_and_persist.py — Headless simulation runner that persists results to DB.
scripts/test_point_to_point.py — Script/test harness for point-to-point track types.
RaceLogic/closure_solver.py — Circuit closure solver using SciPy to ensure generated track instructions form closed loops.
services/career_result_service.py — Persisting career-mode race results and mapping to career progression.
services/persistence_sqlite.py — SQLite-backed persistence adapter used by higher-level services.
services/hiring_service.py — Hiring, contract and staff/driver availability logic.
services/driver_attributes.py — Driver attribute normalisers and useful derived getters for UI/logic.
services/championship_service.py — Championship lifecycle logic: points systems, standings calculation, calendar and tie-break rules.
services/race_engine_factory.py — Factory functions to create discipline-specific race engines and realtime engines.
RaceLogic/base_race_engine.py — Base discipline engine with performance models, reliability, incident checks, and points mapping.
services/progression_service.py — Season progression and promotion/relegation rules.
services/race_simulation_api.py — Helpers to run and persist race simulations, context population and fallback behaviour.
scripts/_check_race_results.py — Utility to check race results format/consistency.
scripts/_show_race_results_columns.py — Helper to display race results columns for inspection.
services/track_surface_service.py — Surface and grip profile helper calculations used by racing logic.
services/team_service.py — Team management business logic (create/update teams, budgets, allocations).
scripts/__init__.py — Scripts package initializer.
GUI/assets/props/bush_1.png — Binary GUI prop asset (image).
GUI/assets/props/rock_1.png — Binary GUI prop asset (image).
GUI/assets/props/tree_oak.png — Binary GUI prop asset (image).
GUI/assets/props/tree_birch.png — Binary GUI prop asset (image).
GUI/assets/props/tree_pine.png — Binary GUI prop asset (image).
RaceLogic/disciplines/urban_street/urban_street_discipline.py — Urban/Street (drifting) discipline adapter.
api/schemas.py — Pydantic request/response models and schema definitions for the FastAPI endpoints.
api/__init__.py — API package marker.
RaceLogic/disciplines/drag_acceleration/drag_acceleration_discipline.py — Drag/Acceleration discipline adapter.
RaceLogic/disciplines/sprint_rallycross/sprint_rallycross_discipline.py — Sprint/Rallycross discipline adapter.
RaceLogic/disciplines/single_seater/single_seater_discipline.py — Discipline adapter: single-seater rules and calibrations.
RaceLogic/disciplines/production_touring/production_touring_discipline.py — Production/Touring discipline adapter.
RaceLogic/disciplines/endurance/endurance_discipline.py — Endurance discipline adapter and race rules.
tools/_syntax_check.py — Syntax checking helper for the codebase.
tools/validate_track_routes.py — Validate track route geometry.
tools/URBAN_STREET_Momentum_Street_Circuit.png — Binary asset (track image).
tools/track_smoke_test.py — Quick smoke test for track processing.
tools/test_closure_solver.py — Test harness for closure solver.
tools/team_name_generator.py — Team name generation utility.
tools/SPRINT_RALLYCROSS_Momentum_Rallycross_Circuit.png — Binary asset (track image).
tests/test_integration_srs.py — Integration test for sprint rallycross scenarios.
tests/test_integration_full_career_season.py — Integration test running full career season.
tests/test_integration_database_layer.py — Integration test for DB layer operations.
tests/test_integration_championship_flow.py — Integration test for championship lifecycle.
tests/test_integration_api_contracts.py — Integration tests validating the public API contracts.
tests/test_event_schema_emission.py — Tests for event schema emissions.
tests/test_discipline_edge_cases.py — Tests for discipline-specific edge cases.
tests/test_database_integrity.py — Tests to validate DB integrity and constraints.
tests/test_accessibility_ui_checks.py — GUI accessibility checks (headless where necessary).
tests/README.md — Tests documentation and running guidance.
tests/test_use_case_coverage.py — Test ensuring use-case coverage across flows.
tests/test_unit_track_surface_service.py — Unit test for track surface calculations.
tests/test_unit_racelogic_urban_street.py — Unit tests for urban street race logic.
tests/test_unit_racelogic_sprint_rallycross.py — Unit tests for sprint rallycross logic.
tests/test_unit_racelogic_single_seater.py — Unit tests for single seater logic.
tests/test_unit_racelogic_production_touring.py — Unit tests for production touring logic.
tests/test_unit_racelogic_endurance.py — Unit tests for endurance logic.
tests/test_unit_racelogic_drag_acceleration.py — Unit tests for drag/acceleration logic.
tests/test_unit_racelogic_discipline_loader.py — Unit tests for discipline loader behaviour.
tests/test_unit_gui_launcher_smoke.py — GUI launcher smoke test (offscreen Qt).
tests/test_unit_championship_rules.py — Unit tests for championship points and tie-breaks.
tests/test_unit_career_season_service.py — Unit tests for career season orchestration.
tests/test_statistical_validation.py — Statistical tests validating RNG/distribution behaviour.
tests/test_simulation_reproducibility.py — Tests ensuring deterministic simulation when seeded.
tests/test_property_based_randomness.py — Property-based tests exploring randomness properties.
tests/test_performance.py — Performance-focused tests and benchmarks.
tests/test_migration_tire_to_tyre.py — Migration test for tyre/tire column rename.
tests/conftest.py — Pytest fixtures creating deterministic test DBs and test clients.
tests/output/vehicle_topdown_rotated.png — Binary test output image.
tests/output/vehicle_topdown.png — Binary test output image.
