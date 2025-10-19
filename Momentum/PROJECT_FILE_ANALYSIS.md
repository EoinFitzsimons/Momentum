# Momentum — Per-file analysis and how each file maps to the proposal

This document provides a detailed analysis for each file currently in `Momentum` (Python code and key assets). For each file I state:

- Purpose: what the file is for
- Responsibilities: main functions / classes or data contained
- Interactions / dependencies: who calls it and what it calls
- Noted issues or technical debt (observed from codebase)
- Concrete suggestions (refactor, rename, separate concerns)

---

NOTE: many files contain richer implementations; this analysis summarizes responsibilities and sensible actions to prepare a clean rebuild that matches the supplied proposal.

## Files

### Momentum/Python/vehicles/__init__.py

Purpose: Package initializer for the `vehicles` module.
Responsibilities: Exposes package-level imports (if any) and marks the directory as a Python package.
Interactions: Imported by other modules that use vehicle types.
Issues: Often left empty; ensure it exports stable symbols or remains intentionally empty.
Suggestions: If the package is public, explicitly export the primary classes (e.g., `RaceCar`) to simplify imports: `from .vehicle import RaceCar`.

### Momentum/Python/vehicles/vehicle.py

Purpose: Domain dataclass(s) for vehicles and their components (e.g., `RaceCar`).
Responsibilities: Provide composition of components (aerodynamics, chassis, engine, electronics) and performance helpers (e.g., `get_total_power`, `check_discipline_compliance`).
Interactions: Referenced by discipline rulebooks, engines, and vehicle development system. Likely read by simulation orchestrators when evaluating car performance.
Issues: Potential mixing of domain logic and simulation (methods may do heavy calculations). Naming may be generic; ensure methods are small and testable.
Suggestions: Keep `Vehicle` as a pure domain model with small, well-named methods. Move heavy performance calculations into `engines` or domain services and add unit tests for component interactions.

### Momentum/Python/test_gen.py

Purpose: Likely used for ad-hoc generation/testing of names or sample data.
Responsibilities: Quick scripts for generating sample data or testing generation logic.
Interactions: May call the intelligent name generator or DB scripts.
Issues: Utility/test scripts can accumulate non-deterministic outputs and stray development code.
Suggestions: Move stable generators into `systems/intelligent_name_generator.py` and keep `test_gen.py` as a small executable example in `examples/` or `tests/` with deterministic seeds.

### Momentum/Python/requirements.txt

Purpose: Lists Python dependencies required to run the project.
Responsibilities: Pin or list required libraries (e.g., numpy, fastapi, pydantic, Faker).
Interactions: Used by contributors to create virtual environments; used in CI or Docker setup.
Issues: Ensure versions are pinned for reproducibility. Missing dev/test dependencies (pytest, mypy) may reduce developer hygiene.
Suggestions: Split `requirements.txt` into `requirements.txt` (runtime) and `requirements-dev.txt` (test, lint, typecheck) or move to `pyproject.toml`/`poetry` for modern dependency management.

### Momentum/Python/generate_initial_database.py

Purpose: Procedural content pipeline to create the initial SQLite data set (teams, drivers, staff, tracks).
Responsibilities: Uses `intelligent_name_generator` and `database_manager` to populate `momentum.db` with realistic fake data.
Interactions: Calls `systems/intelligent_name_generator.py`, writes to `database/database_manager.py`.
Issues: Scripts like this often contain ad-hoc logic and may duplicate repository code (direct DB writes vs using repository abstraction).
Suggestions: Keep the script but refactor DB operations through a `Repository` interface. Add a CLI flag to seed deterministically using an RNG seed. Add verification output and small unit tests that run in-memory.

### Momentum/Python/test_names.py

Purpose: Testing for name generation logic and uniqueness.
Responsibilities: Verifies `intelligent_name_generator` outputs valid and unique names given constraints.
Interactions: Depends on `systems/intelligent_name_generator.py` and possibly SQLite tracking DB.
Issues: Ensure the tests use an ephemeral DB or mocks to avoid altering the real `used_names.db`.
Suggestions: Convert to proper pytest tests, use fixtures to create temporary DBs, and assert deterministic behavior using a seed.

### Momentum/Python/simulation.py

Purpose: FastAPI server and simulation entrypoints (core API surface for the backend).
Responsibilities: Defines HTTP routes (e.g., `/simulate/race`), request validation, building a `SimulationContext`, calling the `RaceSimulator`, and persisting results.
Interactions: Calls `database/database_manager.py`, `disciplines/race_simulation.py`, `config.py`, and possibly `systems/*` modules.
Issues: Historically mixed presentation and business logic; `simulate_race` contains several responsibilities (fetch/create race, normalize driver attributes, call simulator, persist results). Cognitive complexity and testing difficulties reported earlier.
Suggestions: Keep the file as the thin HTTP surface. Move orchestration logic into `services/simulation_service.py` and use repositories for DB access. Convert request/response models to Pydantic DTOs. Add integration tests using FastAPI TestClient.

### Momentum/Python/database_generation_report.txt

Purpose: Artifact summarizing database generation runs.
Responsibilities: Human-readable report; used for tracking content generation results.
Interactions: Generated by scripts such as `generate_initial_database.py`.
Issues: Can be outdated or ignored; keep in docs only if useful.
Suggestions: Archive old reports in `docs/` or convert to structured logs (JSON) if programmatic checks are required.

### Momentum/Python/README.md

Purpose: Project README with instructions for running the Momentum backend.
Responsibilities: Onboarding developers, describing setup, usage, and high-level architecture.
Interactions: Points users to `requirements.txt`, `simulation.py`, and `generate_initial_database.py`.
Issues: Ensure README is accurate and includes minimal reproducible steps to run the demo.
Suggestions: Add a quick start section with commands to create a venv, install deps, run DB generation, and start the server.

### Momentum/Python/currency_cache.json

Purpose: A cached snapshot of currency or pricing data used by currency/procurement systems.
Responsibilities: Provide fast lookups for currency conversion and caching external API responses.
Interactions: `systems/currency_system.py` will likely read/write to this cache.
Issues: Binary JSON file may drift from source of truth; check if it should be regenerated or kept in `.gitignore`.
Suggestions: Keep cache out of version control unless essential; add regeneration script to `generate_initial_database.py`.

### Momentum/Python/config.py

Purpose: Central configuration constants and domain definitions (attribute lists, DB path, MONTE_CARLO_ITERATIONS, RANDOM_SEED, discipline registry).
Responsibilities: Single source of truth for global flags and attribute names used across engines and DB.
Interactions: Imported by `simulation.py`, `disciplines/*`, `database/*`.
Issues: Large lists of attributes are defined here; coupling may arise if different parts of the code expect different shapes.
Suggestions: Keep config minimal and move sensitive/operational values into environment variables via a config loader. Document default values and permitted ranges.

### Momentum/Python/CLEANUP_SUMMARY.md

Purpose: Documentation describing cleanup tasks previously performed.
Responsibilities: Notes on name generation, API cleanups, or other maintenance.
Interactions: Informational only.
Issues: Keep updated or move to repository issues if the file becomes stale.
Suggestions: Move operational notes into `docs/` or a `CHANGELOG.md`.

### Momentum/Python/API_KEY_SECURITY.md

Purpose: Documentation about API key usage and security guidance.
Responsibilities: Provide instructions for storing keys, restrictions, and recommendations (e.g., environment variables, not in source control).
Interactions: Useful for environment setup and deploying the API.
Issues: Ensure documentation matches current implementation (if API keys are used by external services).
Suggestions: Add sample .env and instructions for local development and CI.

### Momentum/Python/API_DOCUMENTATION.md

Purpose: API docs for the FastAPI endpoints (possibly manual docs complementary to FastAPI auto-docs).
Responsibilities: Explain endpoints, request/response schema, and sample payloads.
Interactions: Used by Unity front-end developers and testers.
Issues: Keep in sync with actual FastAPI schemas; if FastAPI is used, consider redirecting to automatic OpenAPI docs.
Suggestions: Keep short examples and link to `/docs` (Swagger) served by FastAPI for the canonical docs.

### Momentum/Python/test_cultural_names.py

Purpose: Test cases validating culturally accurate name generation.
Responsibilities: Ensure `intelligent_name_generator` creates names with expected scripts (Cyrillic, Kanji, diacritics).
Interactions: Uses `systems/intelligent_name_generator.py` and possibly the `used_names.db`.
Issues: Tests should not write to production `used_names.db` — use temp DBs.
Suggestions: Convert to pytest, use parametrized inputs per locale, and assert deterministic outputs with a seed.

### Momentum/Python/vehicles/components/__init__.py

Purpose: Package initializer to expose vehicle component modules.
Responsibilities: Optionally re-export component classes.
Interactions: Imported by `vehicles.vehicle` or engines.
Issues: Keep exports explicit to avoid circular imports.
Suggestions: Define an `__all__` to control public API.

### Momentum/Python/vehicles/components/enums.py

Purpose: Enumerations for vehicle parts, drivetrain types, fuel types, or component categories.
Responsibilities: Provide typed constants used across vehicle and engine code.
Interactions: Imported by `vehicles/components/*` and `vehicle.py`.
Issues: Keep enum names clear and documented.
Suggestions: Use Python `Enum` with explicit docstrings and consider centralizing shared constants in `config.py` only when appropriate.

### Momentum/Python/vehicles/components/engine.py

Purpose: Implementation of engine component semantics: power, reliability, upgrade paths.
Responsibilities: Calculate engine power contribution, reliability penalties, and compatibility checks.
Interactions: Used by `vehicles/vehicle.py` and discipline engines when evaluating car performance.
Issues: Component code may reproduce similar calculations across components; check for duplication.
Suggestions: Keep components pure and small, provide serialization helpers, and add unit tests for calculation boundaries.

### Momentum/Python/vehicles/components/electronics.py

Purpose: Vehicle electronics system model (e.g., ERS, traction control, ECU effects).
Responsibilities: Provide simulation of electronics influence on lap times or reliability.
Interactions: Engaged by engines for disciplines where electronics matter.
Issues: Discipline-specific behavior can leak into component code; keep components generic.
Suggestions: Provide parameterized behavior via discipline configs (weights) rather than embedding discipline logic here.

### Momentum/Python/vehicles/components/drivetrain.py

Purpose: Drivetrain component (gearbox, differential) modeling.
Responsibilities: Provide speed/acceleration penalties and failure modes.
Interactions: Combined into `RaceCar` total performance.
Issues: As above, avoid discipline-specific branching.
Suggestions: Create test fixtures for common drivetrain configs.

### Momentum/Python/vehicles/components/chassis.py

Purpose: Chassis properties – weight, stiffness, aero mounting points.
Responsibilities: Influence vehicle handling and tire wear calculations.
Interactions: Used in vehicle handling models inside discipline engines.
Issues: Physical constants may be hard-coded; prefer configurable parameters.
Suggestions: Provide crisp normalization and unit documentation.

### Momentum/Python/vehicles/components/aerodynamics.py

Purpose: Aerodynamic modeling (downforce vs drag tradeoffs).
Responsibilities: Functions to compute aerodynamic balance and track-specific setups.
Interactions: Used primarily by single-seater and touring engines.
Issues: Complex aero models can be expensive; keep simplified formulas for management simulation.
Suggestions: Allow multiple fidelity levels (simple scalar vs lookup table) controlled by config.

### Momentum/Python/database/models.py

Purpose: Dataclasses for domain models and the `SCHEMA_SQL` for DB creation.
Responsibilities: Define `Driver`, `Team`, `Track`, `Race`, and `RaceResult` dataclasses plus the SQL statements required to create schema.
Interactions: Used by `database_manager` for mapping rows to dataclasses.
Issues: Having `SCHEMA_SQL` embedded can be fine for small projects but becomes hard to maintain; mixing dataclass definitions and raw SQL is a smell.
Suggestions: Split dataclasses into `domain/` package and move schema SQL into `database/migrations/` or separate files. Consider using a lightweight ORM or minimal repository layer.

### Momentum/Python/systems/intelligent_name_generator.py

Purpose: Procedural name generator using Faker with locale mapping and uniqueness tracking.
Responsibilities: Provide names for drivers, staff, and teams and persist used names to `data/used_names.db`.
Interactions: Called by `generate_initial_database.py` and possibly by UI or generation endpoints.
Issues: The generator is described as robust; ensure it has an injectable RNG and can run deterministically for tests.
Suggestions: Add tests for locale fallbacks, and expose a `seed` parameter to make runs deterministic.

### Momentum/Python/database/momentum.db

Purpose: The SQLite database file for runtime persistence.
Responsibilities: Stores all persistent tables (drivers, races, results).
Interactions: Read/written by `database_manager.py` and generation scripts.
Issues: Including a binary DB in version control is generally discouraged unless it's a seed DB; ensure it's intentional.
Suggestions: If this is a seed DB used for demos, keep it but document how to regenerate. Otherwise add to `.gitignore` and keep schema/sql seed scripts instead.

### Momentum/Python/disciplines/race_simulation.py

Purpose: Monte Carlo orchestration and `RaceSimulator` implementation.
Responsibilities: Run many iterations of race state, aggregate positional probabilities, and output `RaceResult` objects.
Interactions: Calls discipline engines (or implements per-discipline logic), uses RNG, and returns results to `simulation.py`.
Issues: Historically used legacy RNG; refactor to use a `Generator` instance passed in. Cognitive complexity per function noted earlier.
Suggestions: Keep `RaceSimulator` pure and accept injected dependencies: engine factory, RNG, iteration count. Add unit tests with small iterations.

### Momentum/Python/disciplines/__init__.py

Purpose: Package initializer for discipline modules.
Responsibilities: May expose registry of available disciplines or default engine factory.
Interactions: `simulation.py` may import discipline registry from here.
Issues: Ensure it doesn't import heavy modules to avoid side-effects at import time.
Suggestions: Expose simple factory function or mapping of discipline name → engine class.

### Momentum/Python/systems/vehicle_development.py

Purpose: Simulate vehicle upgrades, development points, and resource allocation.
Responsibilities: Apply development decisions to vehicle components and budgets.
Interactions: Called by team management systems and possibly by `vehicle` tests.
Issues: Might directly manipulate DB or global state – prefer to return deterministic patch objects which services can apply within transactions.
Suggestions: Keep domain-only behavior here and rely on services to persist changes.

### Momentum/Python/disciplines/multi_discipline_simulator.py

Purpose: Higher-level coordinator for running different discipline simulations and selecting engines.
Responsibilities: Provide an orchestration layer that chooses the correct discipline engine and runs the simulation.
Interactions: Called by `simulation.py`; uses `disciplines/*_engine.py` modules.
Issues: Potential duplication with `race_simulation.py` (validate single responsibility: one orchestration layer).
Suggestions: Consolidate orchestration into a single `simulator` module with a pluggable engine registry.

### Momentum/Python/systems/supplier_management.py

Purpose: Manage suppliers and component procurement dynamics.
Responsibilities: Provide supplier catalogs, prices, and procurement effects on performance.
Interactions: Interacts with `currency_system.py` and `vehicle_development.py` for spending and supply effects.
Issues: Supplier and procurement modeling may be simplistic; consider modeling lead times and reliability.
Suggestions: Keep supplier data separate (e.g., `data/suppliers.json`) and implement procurement flows in services with transaction boundaries.

### Momentum/Python/docs/NAME_GENERATION_SOLUTION.md

Purpose: Documentation describing the intelligent name generation solution and design choices.
Responsibilities: Explain locales, uniqueness strategy, and performance.
Interactions: Used for project documentation and evidence of design decisions.
Issues: Markdown lint issues were flagged earlier; ensure headings spacing and fenced code blocks are properly formatted.
Suggestions: Keep docs concise and link to `systems/intelligent_name_generator.py` for implementation details.

### Momentum/Python/data/used_names.db

Purpose: SQLite DB tracking used names to avoid duplicates.
Responsibilities: Ensure name uniqueness across generated personnel.
Interactions: Written by `intelligent_name_generator.py`.
Issues: Binary DB in repository; consider moving to generated artifact or documenting its role.
Suggestions: Use in-memory DB for tests and provide a seed/restore script to recreate production DB for demos.

### Momentum/Python/systems/staff_management.py

Purpose: Manage staff assignments, hiring/firing, and staff attributes.
Responsibilities: Provides functions to assign personnel roles and calculate effects on team performance.
Interactions: Uses `intelligent_name_generator` for staff creation and interacts with `database_manager`.
Issues: Ensure separation between domain logic and DB writes; currently could be mixed.
Suggestions: Provide clear domain functions and let services persist within transactions.

### Momentum/Python/examples/staff_examples.py

Purpose: Example usage script demonstrating staff creation or management features.
Responsibilities: Showcase typical flows (create staff, assign team) for developers.
Interactions: Calls `systems/staff_management.py` and DB helpers.
Issues: These examples can rot if not updated; ensure examples are lightweight and deterministic.
Suggestions: Move to `examples/` (already present) but keep them minimal and add `--seed` option.

### Momentum/Python/docs/driver_system_summary.md

Purpose: Design document summarizing the driver attribute system and validations.
Responsibilities: Explain attribute categories, weighting, and validation approaches.
Interactions: Helpful for reviewers and as a design source for engines.
Issues: Multiple Markdown lint issues were flagged earlier; also ensure the document matches code (attribute names and counts).
Suggestions: Keep documentation in sync with `config.py` attribute lists. Consider adding an attribute glossary linking to code.

### Momentum/Python/systems/currency_system.py

Purpose: Financial operations and currency conversions for teams and suppliers.
Responsibilities: Handle budgets, apply expenditures, and possibly currency conversions (cache used in `currency_cache.json`).
Interactions: Used by `systems/*` and `championship_manager` for fine-grained updates.
Issues: Must ensure atomicity when applying budget changes; avoid race conditions in concurrent simulation runs.
Suggestions: Use repository transaction boundaries (SQLite supports transactions) and add tests to validate budget constraints.

### Momentum/Python/tests/test_staff_system.py

Purpose: Unit tests for staff management logic.
Responsibilities: Validate staff creation, assignment, and effects on teams.
Interactions: Should use temporary DB or mocks.
Issues: Ensure tests don't modify the real DB in repo.
Suggestions: Convert to pytest fixtures and assert idempotent behavior; run tests in CI.

### Momentum/Python/disciplines/base_engine.py

Purpose: Base class and helper functions used by discipline engines (performance calculations, RNG helper, reliability checks).
Responsibilities: Provide shared logic and default implementations used by discipline-specific engines.
Interactions: Imported by `*_engine.py` modules, referenced by `race_simulation.py`.
Issues: Contains some historically problematic code (legacy RNG usage, nested ternaries) — already modernised in earlier edits.
Suggestions: Define a clear interface here (e.g., `calculate_base_performance(driver, vehicle, track, rng)`) and keep RNG injection consistent.

### Momentum/Python/docs/CLEANUP_NAMEAPI_PARANAMES.md

Purpose: Design notes or cleanup guidance related to name APIs and ParaNames dataset.
Responsibilities: Explain decision to use Faker over ParaNames and cleanup steps.
Interactions: Informational.
Issues: Keep as historical documentation; tidy up formatting.
Suggestions: Archive or consolidate with `docs/NAME_GENERATION_SOLUTION.md` if overlap exists.

### Momentum/Python/data/placeholder_names.py

Purpose: Small helper/wrapper file likely containing fallback name lists used in generation.
Responsibilities: Provide a minimal fallback dataset for name generation.
Interactions: `intelligent_name_generator.py` may fallback to this list if Faker locales lack coverage.
Issues: Ensure content is licensed or generated.
Suggestions: Keep compact; document the fallback policy.

### Momentum/Python/database/database_manager.py

Purpose: Primary SQLite access layer; CRUD for drivers, teams, tracks, races, and race results.
Responsibilities: Open DB connections, run queries, map rows to dataclasses, and serialize dataclasses to DB.
Interactions: Called by `simulation.py`, `generate_initial_database.py`, and systems modules.
Issues: Currently acts as a monolithic manager performing many responsibilities — consider splitting into multiple `Repository` classes (DriverRepository, RaceRepository). Some helper functions may be missing (e.g., `get_track` added earlier).
Suggestions: Introduce repository pattern, keep low-level SQL here, and provide typed method signatures with docstrings. Add error handling and transaction support.

### Momentum/Python/tests/test_driver_system.py

Purpose: Unit tests for driver attribute and progression logic.
Responsibilities: Validate rating calculations, attribute normalization, and progression rules.
Interactions: Use `database/models.py` dataclasses and possibly small in-memory DB fixtures.
Issues: Ensure deterministic outcomes by controlling RNG seeds in tests.
Suggestions: Use pytest parametrized tests to cover edge cases and ensure isolation from persistent DB.

### Momentum/Python/systems/championship_manager.py

Purpose: Apply championship rules: points distribution, standings updates, promotion/relegation logic.
Responsibilities: Given `RaceResult` objects, update championship standings and award points.
Interactions: Takes results from `simulation.py` and writes standings via `database_manager`.
Issues: Possibly mixes IO and business logic in a single module; testability may suffer.
Suggestions: Split into pure functions for points calculation and a service to persist updates. Add unit tests that run with in-memory DB.

### Momentum/Python/database/database_factory.py

Purpose: Helper to create or initialize the SQLite DB (runs `SCHEMA_SQL`), possibly for testing.
Responsibilities: Create the database schema and seed initial data if required.
Interactions: Used by `generate_initial_database.py` and in test setup.
Issues: Ensure idempotent behavior and clear migration/version handling.
Suggestions: Add a minimal migration version table or switch to using Alembic for complex schemas.

### Momentum/Python/tests/simple_driver_test.py

Purpose: Tiny unit tests or smoke tests for driver-related functions.
Responsibilities: Quick guards against breaking changes.
Interactions: Use `database.models` and domain helper functions.
Issues: Convert to canonical pytest style and organize under `tests/` with fixtures.
Suggestions: Merge with `test_driver_system.py` where appropriate to avoid fragmentation.

### Momentum/Python/ai/decision_engine.py

Purpose: AI decision-making for teams and drivers — likely rule-based heuristics.
Responsibilities: Provide functions to simulate pit decisions, strategy selection, and team-level choices.
Interactions: Called by systems or simulation orchestrator to produce deterministic actions.
Issues: RL components described in proposal are not present here; the module likely contains simple heuristics and thresholds.
Suggestions: Document decision inputs/outputs and add a small functional test harness to exercise common scenarios.

### Momentum/Python/disciplines/single_seater/rulebook.py

Purpose: Rulebook for single-seater discipline: technical limits, weight and power constraints.
Responsibilities: Validate vehicle compliance and specify discipline constraints.
Interactions: Used by `single_seater_engine.py` to validate cars and possibly disqualify entries.
Issues: Earlier static analysis flagged typing issues and unused local variables in validation functions.
Suggestions: Clean up type annotations (Optional[List[str]]), ensure validation returns stable, documented error lists, and add unit tests covering edge cases.

### Momentum/Python/disciplines/production_touring/rulebook.py

Purpose: Rulebook for production/touring discipline, similar to single-seater rulebook but with different checks.
Responsibilities: Validate vehicle modifications, safety, and allowed components.
Interactions: Called by `production_touring_engine.py`.
Issues: Rule differences should be documented in `docs/`.
Suggestions: Add examples of allowed/disallowed setups and unit tests.

### Momentum/Python/disciplines/endurance/__init__.py

Purpose: Mark the endurance discipline package.
Responsibilities: Possibly expose package-level constants or engine factory.
Interactions: Imported by orchestrator to register the engine.
Issues: Keep import light to avoid heavy imports at module load.
Suggestions: Expose a factory function rather than importing engine at package import time.

### Momentum/Python/disciplines/production_touring/production_touring_engine.py

Purpose: Engine implementation for production/touring car races.
Responsibilities: Translate driver and vehicle attributes to performance modifiers, simulate race sessions, and return `RaceResult` objects.
Interactions: Uses `base_engine` helpers, rulebook validations, vehicle components, and RNG. Called by `multi_discipline_simulator`.
Issues: Ensure deterministic behavior with seeded RNG and unit-testable components.
Suggestions: Decouple database access and persistent writes; accept a `Generator` instance for RNG.

### Momentum/Python/disciplines/single_seater/discipline_config.py

Purpose: Discipline-specific configuration for single-seater racing (attribute weights, tire behavior, session lengths).
Responsibilities: Provide constants used by `single_seater_engine.py`.
Interactions: Imported by the engine.
Issues: Keep config small and documented (units, expected range).
Suggestions: Consider representing weights as JSON or dataclass to support validation.

### Momentum/Python/disciplines/endurance/rulebook.py

Purpose: Rule enforcement for endurance races; may include driver stint limits and minimum rest.
Responsibilities: Validate team-driver combinations and car compliance for endurance events.
Interactions: Called by `endurance_engine.py` and by simulation orchestrator.
Issues: Add unit tests for rule boundaries (e.g., maximum stint length).
Suggestions: Keep rulebook pure; return structured error objects rather than booleans.

### Momentum/Python/disciplines/urban_street/discipline_config.py

Purpose: Configuration constants for urban/street racing (surface, risk factors, crowd influence).
Responsibilities: Provide modifiers used by `urban_street_engine.py`.
Interactions: Engine imports and uses.
Issues: Document assumptions (e.g., higher incident rate in urban events).
Suggestions: Keep realistic defaults and expose ability to tune via environment variables.

### Momentum/Python/disciplines/production_touring/discipline_config.py

Purpose: Config for production/touring discipline (see production touring engine).
Responsibilities & Interactions: Similar to other discipline configs; used by `production_touring_engine.py`.
Issues: Consistency — use same config format across disciplines.
Suggestions: Use a common `DisciplineConfig` dataclass in `disciplines/` to standardize fields.

### Momentum/Python/disciplines/endurance/endurance_engine.py

Purpose: Endurance racing engine: simulating long races, fatigue, driver swaps, reliability.
Responsibilities: Model driver fatigue, pit stops strategies, mechanical wear, and aggregate finishing probabilities.
Interactions: Uses `base_engine` helpers and `endurance.rulebook`.
Issues: High complexity by nature — split into smaller helper functions for stamina, reliability, and pit strategy.
Suggestions: Add unit tests for driver fatigue model and a small integration test with controlled RNG.

### Momentum/Python/disciplines/endurance/discipline_config.py

Purpose & Responsibilities: Config constants for endurance racing (race duration, tyre degradation rates).
Suggestions: Same as other discipline configs; make config validation explicit.

### Momentum/Python/disciplines/rally_stage/__init__.py

Purpose: Package marker for rally stage discipline.
Responsibilities: Module exports or factory methods.
Suggestions: Keep import lightweight; provide registration function for engine.

### Momentum/Python/disciplines/drag_acceleration/__init__.py

Purpose: Package marker for drag/acceleration discipline.
Suggestions: Same as other discipline packages.

### Momentum/Python/disciplines/rally_stage/rulebook.py

Purpose: Rally-specific rules (safety, car classes, co-driver, stage legality).
Responsibilities: Validate entries and check stage eligibility.
Suggestions: Add tests for stage-eligibility rules and document constraints.

### Momentum/Python/disciplines/drag_acceleration/rulebook.py

Purpose: Rulebook for drag racing (classes, reaction time importance).
Responsibilities: Provide validations for straight-line setups.
Suggestions: Keep rules small and deterministic; provide sample test cases.

### Momentum/Python/disciplines/single_seater/single_seater_engine.py

Purpose: Simulate single-seater sessions (practice, qualifying, race) using attribute weightings.
Responsibilities: Convert driver and vehicle attributes to lap-time modifiers, manage session logic and incident probabilities.
Interactions: Uses `discipline_config`, `rulebook`, `base_engine`, and vehicle components.
Issues: Ensure attribute normalization (db scale vs engine scale) is consistent.
Suggestions: Centralize normalization in an adapter and unit test the engine with mocked drivers.

### Momentum/Python/disciplines/rally_stage/rally_stage_engine.py

Purpose: Rally stage simulation: per-stage time calculation, surface adaptation, and weather effects.
Responsibilities: Aggregate stage times per driver and introduce stage-specific incidents.
Interactions: Uses terrain and track attributes from `Track` models.
Suggestions: Provide deterministic seed and small unit tests for stage time computations.

### Momentum/Python/disciplines/drag_acceleration/drag_acceleration_engine.py

Purpose: Drag race simulation (reaction times, terminal speed).
Responsibilities: Compute short-run times and small variance distributions.
Suggestions: Keep engine small and fast; ensure RNG seed usage is consistent.

### Momentum/Python/disciplines/rally_stage/discipline_config.py

Purpose: Rally-specific constants (surface multipliers, weather probabilities).
Suggestions: Document units and ranges.

### Momentum/Python/disciplines/drag_acceleration/discipline_config.py

Purpose: Drag-specific config (distance, reaction time distribution).
Suggestions: As above.

### Momentum/Python/disciplines/sprint_rallycross/discipline_config.py

Purpose: Sprint/rallycross config constants.
Suggestions: Standardize config representation across disciplines.

### Momentum/Python/disciplines/single_seater/__init__.py

Purpose: Package initializer for single-seater discipline.
Suggestions: Provide a registration function for the engine and clear exported API.

### Momentum/Python/disciplines/sprint_rallycross/rulebook.py

Purpose: Rulebook for sprint rallycross events (mixed surfaces, joker lap rules).
Suggestions: Explicit unit tests for joker lap interactions and class validations.

### Momentum/Python/tests/examples/driver_examples.py

Purpose: Example script demonstrating driver creation and simple simulations.
Responsibilities: Provide sample usage code for developers.
Suggestions: Keep deterministic and move heavy examples to docs.

### Momentum/Python/disciplines/production_touring/__init__.py

Purpose: Package initializer for production touring discipline.
Suggestions: Provide engine factory exports.

### Momentum/Python/disciplines/urban_street/rulebook.py

Purpose: Rulebook for urban/street racing (customisation impact, legality on city circuits).
Suggestions: Validate vehicle modifications and driver personality effects.

### Momentum/Python/disciplines/urban_street/__init__.py

Purpose: Package initializer for urban street discipline.
Suggestions: Keep light and document exports.

### Momentum/Python/disciplines/sprint_rallycross/sprint_rallycross_engine.py

Purpose: Engine for sprint rallycross events.
Responsibilities: Simulate quick, high-variance races with mix-surface handling.
Suggestions: Small but well-tested engine to ensure reproducible distributions.

### Momentum/Python/disciplines/sprint_rallycross/__init__.py

Purpose: Package initializer for sprint rallycross discipline.

### Momentum/Python/disciplines/urban_street/urban_street_engine.py

Purpose: Urban/street race simulation engine focusing on customization and incident risk.
Suggestions: Provide tests for customization effects and incidents.

### Momentum/Python/database/models/__init__.py

Purpose: Package marker for database model module and possibly exports.

### Momentum/Python/database/models/supplier_models.py

Purpose: Supplier model dataclasses — defines suppliers and their attributes.
Suggestions: Keep data small, add docstrings for fields.

### Momentum/Python/database/models/staff_models.py

Purpose: Dataclasses for staff members (roles, skills).
Suggestions: Group staff skills and provide validation helpers.

### Momentum/Python/database/models/multi_discipline_models.py

Purpose: Support additional domain models that span multiple disciplines (composite types).
Suggestions: Keep cross-discipline shared structures here; document shared attributes.

### Momentum/Python/docs/PROJECT_FILE_MAP.md

Purpose: File map created earlier describing high-level file relationships (this is the summary you asked for earlier).
Notes: Keep updated as the repo evolves.

### Momentum/Python/docs/PROJECT_FILE_LIST.md

Purpose: File manifest listing all files under Momentum (created earlier).
Notes: Useful audit artifact.

### Momentum/Unity/

Purpose: Unity front-end project directory (not expanded in this analysis).
Notes: Unity projects are large; if you want a breakdown I can expand it, but it may contain many binary and meta files.

### Momentum/Technical Report/

Purpose: The technical report drafts and final submission artifacts.
Notes: Important for evaluation but not part of code execution.

---

## Cross-file concerns and global issues (summary)

- Layering and separation: Several modules mix concerns (API, orchestration, DB I/O). For a clean rebuild, separate into `api/`, `services/`, `domain/`, `repositories/`, `engines/`.
- Determinism: Ensure all stochastic behavior receives an injected RNG/seed to make tests deterministic.
- Repositories: Consolidate DB code into repository classes; avoid direct SQL across application code.
- Tests: Convert all ad-hoc scripts and test files into pytest tests with fixtures and avoid touching the real DB files in repo.
- Documentation hygiene: Fix markdown linting issues and keep docs close to code with links.
- Binary artifacts in repo: Consider removing `momentum.db` and `used_names.db` and replacing with seed scripts.

---

## Next steps (analysis only — you control next actions)

- If you want, I can produce an expanded per-file analysis that includes:
  - Function/class lists and likely method signatures by parsing each file (more work, useful for spec-writing).
  - A formal `SPEC.md` that lists public interfaces, DTOs (Pydantic models), and repository signatures to guide a rebuild.
- Alternatively, I can produce a CSV/JSON manifest from the file list enabling programmatic consumption.

Tell me which direction you want next (detailed parsing of file contents, SPEC.md, or machine-readable manifest). I will not make any code changes unless you ask.

---

### Extracted function & class signatures (auto-generated)

The following section lists class and function signatures parsed from the Python files under `Momentum/Python`. This is an automated extraction of top-level class and def lines (useful as an index of public interfaces). It's intended to be a quick reference — if you want full method parameter lists or docstrings added, tell me and I will expand entries per file.

Note: signatures were collected via a repository grep for lines starting with `class ` or `def `.

#### Momentum/Python/vehicles/vehicle.py

- class RaceCar:
- def get_total_power(self) -> float:
- def get_power_to_weight_ratio(self) -> float:
- def get_overall_condition(self) -> float:
- def simulate_session(self, duration_minutes: float, intensity: float):
- def apply_crash_damage(self, severity: float):
- def requires_service(self) -> Dict[str, bool]:
- def perform_full_service(self):
- def check_discipline_compliance(self) -> bool:
- def get_performance_summary(self) -> Dict[str, any]:

#### Momentum/Python/vehicles/components/enums.py

- class RacingDiscipline(Enum):
- class AspirationType(Enum):
- class FuelSystem(Enum):
- class FuelType(Enum):
- class EngineConfiguration(Enum):
- class HybridSystemType(Enum):
- class EnergyStorageType(Enum):
- class ERSMode(Enum):
- class GearboxType(Enum):
- class DifferentialType(Enum):
- class DrivetrainLayout(Enum):
- class SuspensionType(Enum):
- class ChassisMaterial(Enum):
- class DamperType(Enum):
- class BrakeMaterial(Enum):
- class BrakeConfiguration(Enum):
- class AeroConfiguration(Enum):
- class WingType(Enum):
- class TireType(Enum):
- class TireCompound(Enum):
- class ControlUnitType(Enum):
- class SteeringType(Enum):
- class SafetyRating(Enum):

#### Momentum/Python/vehicles/components/engine.py

- class EngineComponent:
- class HybridPowerUnit:

#### Momentum/Python/vehicles/components/electronics.py

- class ElectronicControlUnit:
- class SteeringSystem:
- class SafetySystem:

#### Momentum/Python/vehicles/components/drivetrain.py

- class Gearbox:
- class Differential:
- class Drivetrain:

#### Momentum/Python/vehicles/components/chassis.py

- class Suspension:
- class BrakeSystem:
- class Chassis:

#### Momentum/Python/vehicles/components/aerodynamics.py

- class AerodynamicsPackage:
- class Tire:
- class TireSet:

#### Momentum/Python/tests/test_staff_system.py

- class StaffSystemTester:
- def main():

#### Momentum/Python/tests/test_driver_system.py

- class DriverSystemTester:
- def main():

#### Momentum/Python/tests/simple_driver_test.py

- def test_basic_driver_functionality():
- def test_driver_specializations():
- def main():

#### Momentum/Python/tests/examples/driver_examples.py

- def create_formula_specialist() -> Driver:
- def create_touring_car_battler() -> Driver:
- def create_rally_legend() -> Driver:
- def create_versatile_all_rounder() -> Driver:
- def get_performance_level(rating: float) -> str:
- def print_driver_profile(driver, disciplines):
- def demonstrate_driver_versatility():

#### Momentum/Python/systems/vehicle_development.py

- class ComponentType(Enum):
- class DevelopmentProject:
- class VehicleDevelopmentEngine:

#### Momentum/Python/systems/supplier_management.py

- class SupplierManager:

#### Momentum/Python/systems/staff_management.py

- class StaffMarket:
- class StaffManagementSystem:

#### Momentum/Python/systems/intelligent_name_generator.py

- class IntelligentNameGenerator:
- def generate_driver_name(nationality: str = 'USA', gender: Optional[str] = None) -> dict:

#### Momentum/Python/systems/currency_system.py

- class Currency(Enum):
- class CurrencyConfig:
- class CurrencySystem:
- def format_currency(amount: float, currency: Currency = Currency.EUR,
- def get_single_seater_budget_cap(currency: Currency = Currency.EUR) -> str:

#### Momentum/Python/systems/championship_manager.py

- class ContractStatus(Enum):
- class TransferWindow(Enum):
- class DriverContract:
- class SeasonCalendar:
- class ChampionshipManager:
- class TransferMarket:

#### Momentum/Python/simulation.py

- def root():
- def health_check():
- def get_database_stats():
- def get_all_drivers():
- def get_teams(discipline: Optional[str] = None):
- def simulate_race(request: Dict[str, Any]):
- def test_endpoint():

#### Momentum/Python/generate_initial_database.py

- class DatabaseGenerator:
- def main():

#### Momentum/Python/examples/staff_examples.py

- def create_technical_director_legend() -> StaffMember:
- def create_data_analytics_specialist() -> StaffMember:
- def create_veteran_strategist() -> StaffMember:
- def create_pit_crew_chief() -> StaffMember:
- def create_budget_team_configuration(team_id: int) -> TeamStaffing:
- def create_premium_team_configuration(team_id: int) -> TeamStaffing:
- def demonstrate_staff_system_capabilities():

#### Momentum/Python/disciplines/single_seater/single_seater_engine.py

- class SingleSeaterEngine(BaseDisciplineEngine):

#### Momentum/Python/disciplines/single_seater/rulebook.py

- class SingleSeaterRulebook:

#### Momentum/Python/disciplines/single_seater/discipline_config.py

- class SingleSeaterConfig:

#### Momentum/Python/disciplines/race_simulation.py

- class SimulationContext:
- class RaceSimulator:

#### Momentum/Python/database/models.py

- class Driver:
- class Team:
- class Track:
- class Championship:
- class Race:
- class RaceResult:

#### Momentum/Python/disciplines/rally_stage/rally_stage_engine.py

- class SurfaceType(Enum):
- class RallyStageEngine(BaseDisciplineEngine):

#### Momentum/Python/disciplines/rally_stage/rulebook.py

- class RallyStageRulebook:

#### Momentum/Python/disciplines/rally_stage/discipline_config.py

- class RallyStageConfig:

#### Momentum/Python/disciplines/production_touring/production_touring_engine.py

- class ProductionTouringEngine(BaseDisciplineEngine):

#### Momentum/Python/disciplines/production_touring/discipline_config.py

- class ProductionTouringConfig:

#### Momentum/Python/database/models/supplier_models.py

- class SupplierCategory(Enum):
- class SupplierTier(Enum):
- class Supplier:
- class ComponentContract:

#### Momentum/Python/database/models/staff_models.py

- class StaffRole(Enum):
- class StaffTier(Enum):
- class BudgetCategory(Enum):
- class StaffMember:
- class TeamStaffing:
- def generate_staff_requirements(budget: float, discipline: str) -> Dict[StaffRole, Tuple[int, int]]:
- def calculate_role_importance(role: StaffRole, discipline: str) -> float:

#### Momentum/Python/database/models/multi_discipline_models.py

- class RacingDiscipline(Enum):
- class Vehicle:
- class MultiDisciplineDriver:
- class MultiDisciplineTeam:
- class Track:
- class Championship:
- class Race:

#### Momentum/Python/disciplines/multi_discipline_simulator.py

- class MultiDisciplineSimulator:
- def simulate_race(race: Race, drivers: List[Driver], teams: Dict[int, Team],

#### Momentum/Python/database/database_manager.py

- class DatabaseManager:

#### Momentum/Python/disciplines/endurance/endurance_engine.py

- class EnduranceRaceLength(Enum):
- class RacePhase(Enum):
- class EnduranceEngine(BaseDisciplineEngine):

#### Momentum/Python/disciplines/endurance/rulebook.py

- class EnduranceRulebook:

#### Momentum/Python/disciplines/endurance/discipline_config.py

- class EnduranceConfig:

#### Momentum/Python/database/database_factory.py

- class DatabaseFactory:

#### Momentum/Python/disciplines/drag_acceleration/drag_acceleration_engine.py

- class DragRaceFormat(Enum):
- class DragClass(Enum):
- class DragAccelerationEngine(BaseDisciplineEngine):

#### Momentum/Python/disciplines/drag_acceleration/discipline_config.py

- class DragAccelerationConfig:

#### Momentum/Python/disciplines/drag_acceleration/rulebook.py

- class DragAccelerationRulebook:

#### Momentum/Python/disciplines/base_engine.py

- class RacingDiscipline(Enum):
- class RaceEventType(Enum):
- class DisciplineContext:
- class BaseDisciplineEngine(ABC):

#### Momentum/Python/data/placeholder_names.py

- class RaceFormat(Enum):
- class LeagueInfo(NamedTuple):
- class DriverProfile:
- def generate_team_name(category: str = None, tier: int = None) -> str:
- def generate_driver_name(nationality: str = None, gender: str = "ANY") -> Dict[str, str]:
- def calculate_total_entities():
- def generate_league_structure(league_code: str) -> dict:
- def get_random_driver_name(discipline: str = None) -> DriverProfile:
- def get_random_team_name(category: str = None) -> str:
- def get_random_track(discipline: str) -> Dict:
- def get_country_name(country_code: str) -> str:
- def get_all_league_codes() -> List[str]:
- def get_leagues_by_category(category: str) -> Dict:
- def generate_bulk_drivers(count: int, country_distribution: Dict[str, float] = None) -> List[Dict[str, str]]:
- def get_name_generation_stats() -> Dict:

#### Momentum/Python/ai/decision_engine.py

- class DecisionType(Enum):
- class AIDecision:
- class TeamPersonality:
- class TeamAI:
- class DriverAI:
