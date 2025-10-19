# Momentum — Project file map and relationship to proposal

This document explains how the current repository files combine and function, and how they relate to the project proposal sections (Simulation Engine, Procedural Content Generation, AI Decision-Making, Unity front-end). It is a focused analysis (read-only) that maps existing code to the planned features and highlights where functionality is present, partial, or missing. Use this as a reference for planning a rebuild or producing a specification.

---

## Top-level layout (relevant folders and important files)

- `Momentum/`
  - `Python/` — main implementation: simulation, database, disciplines, systems, AI, docs, and tests.
    - `config.py` — global constants and configuration (DB path, attribute lists, simulation params).
    - `simulation.py` — FastAPI-based API entrypoint and the surface used to run simulations (exposes `/simulate/race` and related endpoints).
    - `generate_initial_database.py` — content generation script used to populate the SQLite DB with procedurally created drivers, teams and other entities.
    - `requirements.txt` — dependency list for Python environment.
    - `database/` — persistence layer and models.
      - `models.py` — dataclass definitions for domain objects (Driver, Team, Track, Race, RaceResult) and the SQL `SCHEMA_SQL` used to create the DB.
      - `database_manager.py` — SQLite-based CRUD layer and convenience functions used across the project.
      - `database_factory.py` — (if present) DB creation helpers.
      - `models/` — supplemental domain models (multi_discipline, staff, supplier models).
    - `disciplines/` — discipline-specific engines and rulebooks, plus a shared `base_engine.py` and `race_simulation.py`.
      - `base_engine.py` — common helpers used by discipline engines (performance calculation, RNG helper, reliability simulation).
      - `race_simulation.py` / `multi_discipline_simulator.py` — Monte Carlo orchestration and the `RaceSimulator` that runs iterations and aggregates results.
      - Subfolders for each discipline (e.g., `single_seater/`, `endurance/`, `rally_stage/`, `urban_street/`, `production_touring/`, `sprint_rallycross/`, `drag_acceleration/`) each containing a `*_engine.py` and `rulebook.py`.
    - `systems/` — higher-level systems that operate on domain data
      - `championship_manager.py` — championship orchestration logic (standings, points application) (partial/experimental).
      - `currency_system.py` — currency and budget handling.
      - `intelligent_name_generator.py` — procedural name generator (Faker-based) used to populate initial database.
      - `staff_management.py`, `supplier_management.py`, `vehicle_development.py` — additional domain systems.
    - `ai/` — AI decision modules
      - `decision_engine.py` — higher-level AI decision logic used by teams (rule-based heuristics; RL experiments may be absent or minimal).
    - `vehicles/` — vehicle dataclasses and component code used by discipline engines and rulebooks.
    - `docs/` — markdown documentation (design notes, driver_system_summary.md, NAME_GENERATION_SOLUTION.md, etc.).
    - `tests/` — unit/integration tests and example scripts.
  - `Unity/` — presumably the front-end project (not deeply integrated in this repo; likely separate Unity project files).
  - `Technical Report/` — final report drafts and sections.

---

## How the files combine at runtime (high-level flow)

1. The API / CLI surface: `Momentum/Python/simulation.py` provides the HTTP endpoints (FastAPI). It validates input and triggers simulation flows.
2. Data access layer: `database/database_manager.py` reads/writes domain objects to the SQLite database defined by `models.py` `SCHEMA_SQL`.
3. Orchestration: the API or scripts call the simulation orchestration functions (either `multi_discipline_simulator.RaceSimulator` or discipline-specific engines directly) to compute race outcomes.
4. Engines & Rulebooks: Per-discipline engine modules (e.g., `single_seater/single_seater_engine.py`) implement the logic for computing performance in a session. They use helpers from `base_engine.py` (performance scoring, reliability checks, RNG usage) and consult rulebooks for technical-eligibility checks.
5. AI & Systems: After outcomes are computed, higher-level systems (championship manager, currency system) consume results to update standings, budgets, and driver progression. The `ai/decision_engine.py` may be used to simulate team choices (pit calls, setups) where implemented.
6. Persistence: Results (`RaceResult`, `Race`) are persisted back to the SQLite DB using `database_manager.save_race_result` and related functions.
7. Procedural generation: `generate_initial_database.py` and `systems/intelligent_name_generator.py` create the initial teams, drivers and other entities used by simulations.
8. Front-end: Unity (separate folder) is intended to communicate with the Python back-end over JSON/HTTP; the current repo contains the back-end API but likely not a fully wired Unity integration.

---

## Mapping code to the proposal sections

### Simulation Engine (proposal) — where it exists in code
- `disciplines/race_simulation.py` and `disciplines/multi_discipline_simulator.py` implement Monte Carlo style orchestration; these are the core of the proposal's Simulation Engine.
- `disciplines/base_engine.py` contains shared performance calculations and reliability simulation. Discipline-specific engines implement domain weighting and event logic.
- `simulation.py` exposes endpoints to trigger race simulation and returns results; this corresponds to the "API & integration" portion of the proposal.

Status: Present and functional in prototype form. The Monte Carlo engine exists and is used; however iteration counts, determinism (seed passing), and separation between orchestration and persistence need review (some mixing currently exists).

### Procedural Content Generation (proposal) — where it exists
- `generate_initial_database.py` and `systems/intelligent_name_generator.py` handle content generation: drivers, teams, and names. The `database/models.py` holds schema used to store generated entities.

Status: Implemented for initial population. The generator uses Faker and caching; it produces many realistic names and entities. Track generation appears to be simpler (attributes stored in `Track` model) and may be less feature-rich than the proposal description.

### AI Decision-Making (proposal) — where it exists
- `ai/decision_engine.py` contains heuristics for team/driver decisions. It appears to be rule-based; there are references to higher-level decision flows in systems modules (championship manager, staff management).

Status: Basic rule-based AI exists. Full reinforcement learning (PyTorch pipelines) described in the proposal is not present in the repository as of the current snapshot — RL was proposed but not implemented here.

### Unity Front-End (proposal) — where it exists
- `Unity/` folder is present, indicating a front-end project exists, but within the repository there is little evidence of an automated integration between Unity and the Python back-end beyond JSON-based API endpoints in `simulation.py`.

Status: A Unity front-end may be present, but integration points are primarily via the FastAPI JSON endpoints. The repo shows no CI or automation to build Unity; Unity work is likely separate and manual.

---

## File-by-file (concise) — what each important file does

- `config.py` — central constants (attribute lists, default seeds, MonteCarlo iterations); used widely across engines and API.
- `simulation.py` — FastAPI server and handlers; builds SimulationContext objects and calls simulator functions. Contains helper logic and persistence calls.
- `generate_initial_database.py` — script to generate initial DB content using the intelligent name generator and other procedural rules.
- `database/models.py` — dataclasses and `SCHEMA_SQL`. Source of truth for DB tables and object shapes.
- `database/database_manager.py` — direct SQLite access, query helpers and CRUD methods used by API and generation scripts.
- `disciplines/base_engine.py` — utilities: RNG factory, base performance calculations, reliability functions.
- `disciplines/race_simulation.py` — Monte Carlo orchestration for a full race; aggregates iteration results into race probabilities.
- `disciplines/<discipline>/*_engine.py` & `rulebook.py` — discipline-specific rules, attribute weightings, and event resolution code.
- `systems/championship_manager.py` — applies points, updates standings (needs review for correctness and separation from simulation code).
- `systems/intelligent_name_generator.py` — Faker-based name generation; used by database population.
- `ai/decision_engine.py` — rule-based decision-making helpers for team behavior.
- `vehicles/vehicle.py` — `RaceCar` dataclass and component interactions referenced by rulebooks.
- `tests/` — unit tests and example scripts for validation of some components.

---

## Observations: how the code implements the proposal goals (quick)

- Multi-discipline simulation: code structure supports multiple discipline modules; engines are implemented per-discipline.
- Monte Carlo race outcomes: implemented in `race_simulation.py` and used by `simulation.py`.
- Procedural generation: present via `generate_initial_database.py` + name generator.
- Persistent multi-season storage: SQLite schema exists; code persists races and results.
- AI: basic rule-based AI present; advanced RL experiments mentioned in proposal are not implemented in repo.
- Front-end: Unity folder exists; back-end API is present to support JSON exchange but the integration is not fully automated here.

---

## Gaps vs. proposal (analysis-only)

- Reinforcement learning (PyTorch) for AI decision-making: not implemented (proposal-level claim). The repo contains rule-based AI only.
- Unity↔Python pipeline: API exists, but a documented/automated integration or example Unity client using endpoints is not present.
- Robust separation of layers: some modules mix DB access, orchestration and API concerns (e.g., `simulation.py` contains both API and DB normalization code).
- Test coverage: there are tests, but complete unit/integration coverage for engines, services, and deterministic Monte Carlo is limited.
- Performance & background job handling: Monte Carlo can be computationally expensive; a background worker model is not present.

---

## How to use this document

- Reference it when you write a formal specification or decide which modules to preserve/refactor.
- Use the file mappings to assign ownership during refactor sprints (e.g., `repositories`, `services`, `engines`).
- Keep the `generate_initial_database.py` and `intelligent_name_generator.py` as the canonical procedural generation baseline.

---

If you want, I can convert this into a more formal `SPEC.md` that lists public interfaces and required behavior for each module (still in analysis mode). Tell me what level of detail you want next.