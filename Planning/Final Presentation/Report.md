
National College of Ireland

Project Submission Sheet 



Student Name:	
Eoin Fitzsimons

Student ID:	
X23151374

Programme:	
Computing	
Year:	
4

Module:	
Final Project

Lecturer:	
Frances Sheridan
Submission Due Date:	13/05/2026


Project Title:	
Momentum
Word Count:	


I hereby certify that the information contained in this (my submission) is information pertaining to research I conducted for this project.  All information other than my own contribution will be fully referenced and listed in the relevant bibliography section at the rear of the project.
ALL internet material must be referenced in the references section.  Students are encouraged to use the Harvard Referencing Standard supplied by the Library.  To use other author's written or electronic work is illegal (plagiarism) and may result in disciplinary action.  Students may be required to undergo a viva (oral examination) if there is suspicion about the validity of their submitted work.



Signature:	
Eoin Fitzsimons

Date:	
12/12/2025


PLEASE READ THE FOLLOWING INSTRUCTIONS:

1.	Please attach a completed copy of this sheet to each project (including multiple copies).
2.	Projects should be submitted to your Programme Coordinator.
3.	You must ensure that you retain a HARD COPY of ALL projects, both for your own reference and in case a project is lost or mislaid.  It is not sufficient to keep a copy on computer.  Please do not bind projects or place in covers unless specifically requested.
4.	You must ensure that all projects are submitted to your Programme Coordinator on or before the required submission date.  Late submissions will incur penalties.
5.	All projects must be submitted and passed in order to successfully complete the year.  Any project/assignment not submitted will be marked as a fail.
6.	Please check that you read AI and Academic Integrity Acknowledgement Supplments in this document




Office Use Only
Signature:	
Date:	
Penalty Applied (if applicable):	

AI Acknowledgement Supplement
Final project
Momentum

Your Name/Student Number 	Course 	Date 
 Eoin Fitzsimons	 Computing	 12/12/2025

This section is a supplement to the main assignment, to be used if AI was used in any capacity in the creation of your assignment; if you have queries about how to do this, please contact your lecturer. For an example of how to fill these sections out, please click here.

AI Acknowledgment 

This section acknowledges the AI tools that were utilized in the process of completing this assignment. 

Tool Name 	Brief Description 	Link to tool 
 GPT-5 mini	 Free version with github vscode	 gpt-5-mini Model | OpenAI API

 Claude Sonnet 4.5	 Premium version with github vscode – free in limited usage	 Introducing Claude Sonnet 4.5 \ Anthropic

 

Description of AI Usage 

This section provides a more detailed description of how the AI tools were used in the assignment. It includes information about the prompts given to the AI tool, the responses received, and how these responses were utilized or modified in the assignment. One table should be used for each tool used. 

GPT 5 mini

To analyse the project and the rubric to see what is missing at the time

I paste full rubric in and ask how what I currently have relates to it.

 

Project Analysis — Rubric Coverage and Evidence

This document summarises how the current repository maps to the assessment rubric you provided. For each rubric area I list the evidence found in the repo, a short assessment of coverage (Covered / Partial / Missing), and recommended next steps that raise the quality of evidence for assessors.

1. Executive summary

- Purpose: give assessors a onepage view of aims, methods, principal results and conclusions.

- Evidence in repo: `Planning/Technical Report/Contents.md`, `Planning/Technical Report/Introduction/introduction.md`, `README.md`.

- Assessment: Partial — the README and Introduction provide context, but there is no single polished onepage Executive Summary file suitable for marking.

- Recommendation: add `Planning/Technical Report/Executive_Summary.md` (one page) summarising aims, approach, key results and main conclusions.

2. Project Proposal (15%)

- Evidence:

  - `Planning/Technical Report/Proposal/Proposal Draft.md`

  - Planning notes in `Planning/*` and `README.md` background sections.

- Assessment: Covered (draft exists). The proposal contains research, motivation and scope; may need refinement for final submission.

- Recommendation: produce a final version (polished language, clear aims/objectives, one-page summary for assessors) and place it as `Planning/Technical Report/Proposal/Proposal_Final.md`.

3. Communication Skills (10%)

- Evidence:

  - `Planning/Midpoint Presentation/presentation_plan.md` (slide plan, demo script)

  - Diagrams in `Planning/Technical Report/diagrams/` and `Planning/Design and Architecture/` (draw.io and exports)

- Assessment: Partial — planning and diagrams are strong, but the final slide deck and a sample demo recording are not present in the repo.

- Recommendation: add `Planning/Midpoint Presentation/Slides.pdf` and a short demo video `Planning/Midpoint Presentation/demo_short.mp4`. Also add speaker notes and a short rehearsal checklist.

4. Project Analysis & Planning (10%)

- Evidence:

  - `Planning/` folder: schedules, `update_dates*.ps1`, milestone notes, design diagrams and use case planning.

  - `Planning/Technical Report/Contents.md` and `introduction.md` show planned structure and mapping.

- Assessment: Covered — conceptual diagrams, scheduling and milestone files exist.

- Recommendation: add a short trace that links specific highrisk tasks to mitigation steps (e.g., "DNF tuning" → diagrams → tuning plan → tests) to make the mapping explicit.

5. Requirements Engineering (40%)

- Evidence:

  - Use cases: `Planning/UseCases/*`, exported diagrams in `Planning/UseCases/exports/`.

  - Data model: `Momentum/Python/database/models.py` (dataclasses and `SCHEMA_SQL`).

  - `Planning/Technical Report/Contents.md` enumerates functional and nonfunctional sections.

- Assessment: Strong coverage — documented use cases, data schema and detailed TOC are present. This area is well supported.

- Recommendation: create a Requirements Traceability Matrix (RTM) file: `Planning/Technical Report/Requirements_Traceability.md` mapping requirement id → implementing module(s) → test(s) → status.

6. Prototype (25%)

- Evidence:

  - GUI and run scripts: `Momentum/Python/GUI/gui_game.py`, `Momentum/Python/GUI/launcher.py`, `Momentum/Python/GUI/gui_race_visual.py`.

  - Simulation engine: `Momentum/Python/RaceLogic/realtime_race_engine.py` and `simulation.py`.

  - DB and seed scripts: `scripts/generate_and_seed_db.py` and related scripts.

  - Tests: `Momentum/Python/tests/*` and `archive/basic-race-legacy/tests/*`.

- Assessment: Covered — runnable prototype exists, but a short reproducible demo asset (screencast, test-run logs, or screenshots) would make it easier for an assessor to verify functionality quickly.

- Recommendation: add `Planning/Midpoint Presentation/demo_evidence.md` with explicit run commands and expected outputs; include a screenshot and short MP4 demo.

7. Testing and Evaluation (supporting material)

- Evidence:

  - Unit and integration tests in `Momentum/Python/tests/` and legacy archive.

  - `Planning/Testing/Plan.md` describes manual/automation testing approaches.

  - Playtesting notes: `Reflections/Reflection December.md`, logs in `logs/`.

- Assessment: Partial — test code exists, and plans are documented. However, concise test result summaries, graphs or metric tables are not yet collated into a results appendix.

- Recommendation: add `Planning/Technical Report/Test_Results.md` summarising key metrics (e.g., DNF counts per lap pre/post tuning, unit test pass rates). Export simple plots or tables (CSV + PNG) into `Planning/Technical Report/assets/`.

8. Reflective journals and supplementary materials

- Evidence: `Reflections/Reflection December.md` and other notes in `Planning/`.

- Assessment: Covered — reflective material exists for appendices.

- Recommendation: ensure each reflection references the date and work performed and add them as appendices in the final report.

9. Diagrams and architecture

- Evidence: draw.io/exports in `Planning/Technical Report/diagrams/` and `Planning/Design and Architecture/`.

- Assessment: Covered — diagrams are present in editable forms and exports.

- Recommendation: embed selected diagrams directly into the final `Technical Report` markdown files to ensure assessors can view them without opening draw.io.

Actionable next steps (priority order)

1. Create a short onepage Executive Summary: `Planning/Technical Report/Executive_Summary.md` (high impact for assessors).

2. Add final slide deck and a 60–90s screencast of the Quick Race demo to `Planning/Midpoint Presentation/` (addresses Communication Skills).

3. Produce Requirements Traceability Matrix: `Planning/Technical Report/Requirements_Traceability.md` (addresses Requirements Engineering).

4. Add Test Results appendix summarising metrics and any outstanding issues: `Planning/Technical Report/Test_Results.md`.

5. Create `Planning/Midpoint Presentation/demo_evidence.md` with explicit run commands, screenshots and expected console/log snippets (helps prototype marking).

Notes on reproducibility

- To reproduce the demo locally: use the commands in `README.md` or `Planning/Testing/Plan.md`. Key entries: `python -m venv .venv` → `pip install -r Momentum/Python/requirements.txt` → `python Momentum/Python/GUI/launcher.py` (or `python Momentum/Python/GUI/gui_game.py`).

- If you want, I can add an automated script that launches a headless short-run harness and collects DNF/telemetry metrics for rapid iteration (useful for test results appendix).

Conclusion

The repository contains substantial evidence across the major rubric categories: proposal material, planning and diagrams, use cases and data models, a working prototype, and tests. The highestvalue additions to maximise marks are a concise Executive Summary, a final slide deck and short demo video, a Requirements Traceability Matrix, and a short test results appendix with clear metrics. I can produce any of those files next — please tell me which to create first.

 

Evidence of AI Usage 

This section includes evidence of significant prompts and responses used or generated through the AI tool. It should provide a clear understanding of the extent to which the AI tool was used in the assignment. Evidence may be attached via screenshots or text. 

Additional Evidence: 

I need a run through of all my files and tell me how they function together, I'm thinking of starting again from proper specifications outline but would like to take what we have done here and learn from it.

This was from before I worked on the use cases and project plan, I was testing out systems for how I would actually achieve my goals, I had different scraps of code all over the place and wanted to know what it thought was usable.

I'll create a short todo plan, mark the first item in-progress, then pull a few representative files (core configs, systems, disciplines, vehicle, simulation) to ground the walkthrough. Expected outcome: I can produce an accurate architecture summary and suggested spec/refactor areas. 

Created 5 todos

Now I'll read a set of representative files to ground the walkthrough: config, simulation, systems (championship_manager, currency_system, staff_management), database_manager, vehicle, and a discipline rulebook. I'll read larger chunks to capture context. 

Read [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/config.py)

Read [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/simulation.py#1-1), lines 1 to 400

Read [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/database/database_manager.py#1-1), lines 1 to 400

Read [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/database/models.py#1-1), lines 1 to 400

Read [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/disciplines/single_seater/rulebook.py)

I'll mark the first todo completed and start the second (analyzing core interactions), then run a workspace-wide error check to report any syntax/type errors. Expected outcome: updated todo state and a short errors summary. 

Starting (2/5) *Analyze core interactions*

Now I'll run a project-wide error check to surface syntax or lint-like errors so I can mention build status. I'll call the get_errors tool. 

Checked workspace, 14 problems found in [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/simulation.py), [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/disciplines/single_seater/rulebook.py), [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/disciplines/urban_street/urban_street_engine.py)

Starting (3/5) *Identify improvements & spec outline*

I'll give a focused, actionable walkthrough of the codebase you attached, explain how the pieces interact at runtime, list the highest-priority gaps, and propose a clear spec outline and small refactors/tests you can make next. Short progress update: I read representative files (config.py, simulation.py, models.py, database_manager.py, rulebook.py) and ran a workspace error check to surface syntax/typing issues. What's next: you can pick one of the prioritized improvements below and I can implement it (tests + verify) in this workspace.

## Quick project map (top-level pieces)

- config.py

  - Central config constants (DB path, discipline list, driver attributes, simulation params, currency settings, API host/port).

- simulation.py

  - FastAPI server entrypoint. Exposes endpoints: `/`, `/health`, `/stats`, drivers, `/teams`, `/simulate/race`.

  - Creates `DatabaseManager()` and `RaceSimulator()` global instances and currently returns mock results from `/simulate/race`.

- database

  - models.py — dataclasses representing Driver, Team, Track, Championship, Race, etc. Also includes SCHEMA_SQL (used by DB manager).

  - database_manager.py — Database access layer using SQLite. Initializes schema and provides CRUD operations (drivers, staff, teams, tracks, etc.). Many full-featured methods.

  - `database_factory.py` — likely utilities to seed/prepare DB (not inspected in detail here).

- disciplines

  - Discipline modules (single_seater, endurance, rally_stage, etc.). Each discipline contains `discipline_config.py`, `*_engine.py` (simulation logic), and rulebook.py (technical regulations / validation).

  - Example: rulebook.py contains `SingleSeaterRulebook` with many `validate_*` methods and a singleton `SINGLE_SEATER_RULEBOOK`.

- systems

  - Simulation systems: `championship_manager.py`, `currency_system.py`, `intelligent_name_generator.py`, `staff_management.py`, `supplier_management.py`, `vehicle_development.py`. These coordinate higher-level processes (championship scoring, currency updates, name generation, staff hiring, supplier/vehicle dev).

- vehicles

  - `vehicle.py` and `components/` — vehicle models and subcomponents (aerodynamics, chassis, engine, etc.). Discipline rulebooks validate these objects.

- ai

  - e.g., `decision_engine.py` — AI decision logic for teams/drivers.

- tests and other tests

  - Unit/test files exist (`test_driver_system.py`, `test_staff_system.py`, etc.) and examples. Useful starting points for test coverage and behavior descriptions.

- Docs and supporting files

  - `API_DOCUMENTATION.md`, README.md, `docs/` with design notes and name-generation docs.

## How things function together (runtime flow)

1. API request arrives at simulation.py (FastAPI).

2. Endpoints call into core services:

   - `db_manager` (`DatabaseManager`) for persistence (drivers, teams, tracks, championships).

   - `race_simulator` (`RaceSimulator`) — the Monte Carlo engine that should coordinate discipline-specific engines.

3. `RaceSimulator` (in `disciplines/race_simulation.py`) is expected to:

   - Build a `SimulationContext` (drivers, teams, track, weather, rules).

   - Dispatch to a discipline engine (e.g., `single_seater/single_seater_engine.py`) which implements the discipline's logic: lap times, reliability, pit strategy, weather effects.

   - Use discipline `rulebook` (e.g., `SingleSeaterRulebook`) to validate vehicles before sim.

   - Return ordered `RaceResult` objects; results are optionally stored via `DatabaseManager`.

4. `DatabaseManager`:

   - Initializes schema (using `SCHEMA_SQL` in models.py), provides CRUD and query methods (drivers, teams, staff, tracks, championships, race_results).

5. `systems/*` provide cross-cutting responsibilities:

   - `championship_manager` applies points systems and carries championship standing updates.

   - `currency_system` fetches/exposes exchange rates (caching, using currency_cache.json).

   - `intelligent_name_generator` creates driver names (uses NameAPI or local fallback).

6. `vehicles` components are composed to represent a `RaceCar` object and validated via rulebooks per discipline.

This is a classic layered design:

- API layer (simulation.py) -> orchestration layer (`RaceSimulator`, `systems/*`) -> discipline engines & rulebooks -> domain models & persistence (`database/*`) -> assets and components (`vehicles/*`, `ai/*`, `data/*`).

## Key files I read and what they do (concise)

- config.py — global feature flags, constants, attribute lists. Good single source of truth.

- simulation.py — API + mock simulate endpoint. Intended to hook into `RaceSimulator` but currently returns simplified mock results.

- models.py — rich dataclasses with methods like `get_discipline_rating()`. Also includes SCHEMA_SQL (DB creation).

- database_manager.py — schema init, get_connection, and many CRUD methods. Seems intended to be the canonical DB API.

- rulebook.py — discipline-specific validations (engine/hybrid/weight/aero/electronics/safety). Singleton `SINGLE_SEATER_RULEBOOK`.

- `vehicles/*` (not fully opened) — likely defines components referenced by rulebooks.

## Small "contract" for the core simulate flow

- Inputs:

  - race_id (int, optional), track_id, championship_id, weather_conditions (dry/wet/mixed), participants: List[{driver_id, team_id, vehicle_id?}]

- Outputs:

  - race_id, weather, results: List[{driver_id, team_id, position, points, fastest_lap, lap_times..., status}], simulation_status

- Error modes:

  - DB connectivity error, invalid participants, non-compliant vehicle (rulebook violations), engine exception in discipline engine

- Success criteria:

  - Returns deterministic-ish results under the same seed/config, updates DB (race results + championship), and respects per-discipline rules/penalties

## Edge cases to cover

- Missing driver or team IDs in participants

- Vehicle not compliant with discipline rulebook -> should be disqualified or penalized

- Database schema mismatch or locked DB file (concurrency)

- Large participant lists (> grid size)

- Mixed disciplines or invalid discipline filter when requesting teams

- Currency system failing when `USE_LIVE_EXCHANGE_RATES` enabled

## Issues found (from automated checks)

I scanned and ran an error check; notable findings to address (high to low priority):

1. simulation.py

   - TODO: `/simulate/race` currently uses mock results and contains a `# TODO: Integrate with full Monte Carlo simulation engine`. The endpoint does not call `race_simulator.simulate_race()` yet.

2. rulebook.py

   - Type hints: fields annotated as `list` or `Dict[...]` are set to `None` defaults. Pylance / type check suggests using `Optional[list]` or set defaults to actual lists/dicts.

   - Unused local variables in `validate_vehicle` flow: `engine_ok`, `hybrid_ok`, etc., are assigned but not used. Simple fix: replace with `_` or use the boolean.

3. urban_street_engine.py (error outputs show)

   - Unused parameters and nested conditional expression warnings: remove or use parameters, extract conditional into clearer statements.

4. Potential missing methods: simulation.py refers to `db_manager.get_all_teams()` in a comment but uses `get_teams_by_discipline`. Confirm whether a `get_all_teams` exists.

Overall the "get_errors" check returned a number of lint/typing items that should be quick to fix.

Quality gates (quick triage)

- Build: NOT RUN — I didn't run a full build. (PASS/FAIL: unknown)

- Lint / Typecheck: FAIL — the automated check found typing/unused-variable issues in discipline rulebook.py, `urban_street_engine.py`, and a TODO in simulation.py.

- Tests: NOT RUN — there are tests present, but I didn't run pytest here.

If you want, I can run the test suite and report failing tests next.

## Suggested specification outline (to re-start from a proper spec)

Below is a concise, prioritized spec outline you can expand into a formal document. It maps directly to the existing code.

1. Overview and Goals

   - Purpose: multi-discipline motorsport management simulation (teaching/analysis/game)

   - Non-goals: (e.g., not a real-time racing physics engine)

2. Actors

   - API consumer (Unity/frontend), simulation operator, data admin (seed DB), team AI

3. Domains & Data Model

   - Driver, Team, Vehicle, Track, Championship, Race, RaceResult, StaffMember

   - Define mandatory/optional fields and invariants (e.g., driver attributes range 0–100)

4. Disciplines & Rules

   - For each discipline: race format, grid size, tyre rules, pitstop logic, penalty rules

   - Link rulebooks to vehicle validation & in-race penalties

5. Simulation lifecycle / API contract

   - Endpoints with request/response payloads (`simulate/race`, drivers, `/teams`)

   - Race simulation flow: validate inputs -> check compliance -> create SimulationContext -> run Monte Carlo -> persist results -> return results

6. Engines & Extensibility

   - Core `RaceSimulator` responsibilities (seed control, iterations, parallelism)

   - Discipline engine interface (simulate_race(context) -> results)

   - Rulebook interface (validate_vehicle(vehicle) -> compliant bool + violations)

7. Persistence & DB Schema

   - Schema versioning, migration policy, backup frequency

8. External integrations

   - NameAPI (rate limit, caching), currency API (caching & offline mode)

9. Testing & CI

   - Unit tests for rulebooks, DB API (use in-memory SQLite), discipline engines (deterministic seeds), integration tests for API

10. Non-functional: performance targets, determinism, concurrency, logging & observability

I can write this into a `SPEC.md` and map each spec section to exact files/functions.

## Priority improvements (recommended next actions)

High priority (small, high-value):

1. Wire the `simulate/race` endpoint to the real `RaceSimulator.simulate_race()` (implement or stub `RaceSimulator` if missing).

2. Fix rulebook type hints and minor lint issues (replace `list = None` with `Optional[list]` or default `[]`; change unused locals to `_`).

3. Add a small unit test for `SingleSeaterRulebook.validate_vehicle()` covering:

   - compliant vehicle

   - vehicle missing hybrid when hybrid_required is True

   - engine exceeding displacement

4. Add a lightweight integration test for `/simulate/race` using `TestClient` (FastAPI) that asserts the endpoint calls the simulator and returns the expected shape.

Medium priority:

5. Implement DB manager `get_all_teams` (if used) or update code to use existing `get_teams_by_discipline`.

6. Add seed handling to `RaceSimulator` to allow deterministic tests (use `config.RANDOM_SEED`).

7. Add SCHEMA versioning and a small DB-seed script (`generate_initial_database.py` exists — review and wire to CI).

Lower priority:

8. Linting, mypy typing across the package.

9. Add CI pipeline configuration (GitHub Actions) to run tests, mypy, flake8 on PRs.

## Concrete small refactors & tests I recommend (low-risk)

- In rulebook.py:

  - Change annotations:

    - `aspiration_allowed: Optional[list[str]] = None`

    - `hybrid_systems_allowed: Optional[list[str]] = None`

    - `minimum_cockpit_opening_dimensions_mm: Optional[Dict[str, float]] = None`

  - Replace unused local variables in `validate_vehicle` with underscore `_` or use them (e.g., collect pass/fail).

- In simulation.py:

  - Replace mock results with a call to `race_simulator.simulate_race()` and add a fallback if the engine raises an exception.

- Add tests:

  - `tests/test_rulebooks.py` with a dataclass or simple dummy `vehicle` object that has the expected attributes (engine, hybrid_unit, total_mass, aerodynamics, ecu, safety).

  - Use `sqlite3` in-memory DB for `DatabaseManager` unit tests.

If you'd like, I can implement the rulebook typing fixes and a unit test for `SingleSeaterRulebook` now. Those are small, quick, and will make the codebase pass the automated type checks I ran.

## How to run / verify locally

(Assumes you're in Python)

Install environment and run tests:

```powershell

# Create virtualenv and activate (PowerShell)

python -m venv .venv

.\.venv\Scripts\Activate.ps1

# Install dependencies

pip install -r requirements.txt

# Run tests

pytest -q

```

Run API (development):

```powershell

# From Momentum/Python

uvicorn simulation:app --host 127.0.0.1 --port 8000 --reload

```

Quick lint/type checks (optional):

```powershell

pip install mypy flake8

mypy .

flake8 .

```

## Next steps I can take for you (pick one)

- Option A — Implement the safe, small refactors (fix rulebook.py typing, clean unused locals), add unit test for `SingleSeaterRulebook`, run tests and report results.

- Option B — Wire `/simulate/race` to call the `RaceSimulator` (implement `RaceSimulator.simulate_race` minimal API) and add an integration test for the endpoint.

- Option C — Draft the `SPEC.md` spec outline fully (expand each section with fields, contracts, and acceptance criteria).

- Option D — Run the full test suite and create a short GitHub Actions workflow to run tests/mypy on PRs.

Tell me which option you want next (or pick multiple), and I will start immediately. If you choose a code change I will:

- Update the todo list state and mark the work in-progress,

- Make the edits,

- Run tests and mypy/linters,

- Report results and propose next steps.

Additional Evidence: 

Read recursively from launcher.py and see the actial implementation as quite a lot of features are not included here, and some non existant features are included

As much as AI is helpful for planning, when I keep iterating and going in different paths, it can hallucinate and say things are there when they are not actually there. It is still much faster to use it to trawl through what is written though than manually, I try to make my own decisions from the data, not just have it decide.

I'll scan `launcher.py` to confirm implemented features, note missing/extra items, and summarize differences with the document. I'll start by reading the file.

Starting: *Read `launcher.py`* (1/3)

Read [](file:///c%3A/Users/eoin0/Documents/Code/FinalProject/FinalProject/Momentum/Python/GUI/launcher.py)

Completed: *Read `launcher.py`* (1/3)

Quick summary of what I checked and next steps: I read launcher.py and compared the actual implementation with what's claimed in your Midpoint document.

What launcher.py actually implements

- Starts a Qt `QApplication` and sets style.

- Shows `MainMenuWindow` and connects `start_race_signal` to `start_race`.

- `start_race(config)`:

  - Closes an existing `race_window` (if any).

  - Instantiates `RaceWindow`.

  - Calls `set_player_driver()`, `set_tuning_preset()`, and `set_display_mode()` on the `RaceWindow` using values from `config`.

  - Connects `race_window.return_to_menu` to `return_to_menu`.

  - Shows the `race_window`.

  - Prints log lines (including a message that pace/overtake controls are available in the race window).

- `return_to_menu()` closes the race window and shows the main menu again.

Claims in the Midpoint doc that are NOT implemented in launcher.py

- There is no call to `simulate_race(...)` or any services layer in launcher.py — it only opens the visualiser window. (Doc text implies the launcher wires into the simulation pipeline.)

- launcher.py does not build a `RaceContext`, populate teams, or pass a seed / telemetry config.

- It does not initialize or validate the database, nor call `DatabaseManager`.

- It does not manage telemetry batching, logging, or save checkpoints.

- It does not handle deterministic mode flags or expose RNG seeding.

- It does not create placeholder `Team` objects or perform any adapter selection — that logic belongs in `services.race_simulation_api` / engine code.

- There are no feature flags, CLI options, or additional UI wiring beyond what’s required to show/close windows.

Documented features that appear to be overstated (or located elsewhere)

- The doc lists orchestration steps (launcher → simulate_race → engine) as if launcher.py performs them; in the code the launcher hands control to `RaceWindow`, which contains the code to start the race thread and call `simulate_race`. So the orchestration is split (doc implies a single place).

- The doc’s “At-a-glance” suggests telemetry, team placeholder creation and deterministic seeding are part of the launcher flow — in reality these are handled deeper in `services` or `RaceWindow`/engine.

Actionable recommendations

- Update the Midpoint document to reflect the actual runtime flow:

  - Replace any phrasing that says the launcher calls `simulate_race(...)` with: “Launcher creates `RaceWindow`. `RaceWindow` is responsible for calling `services.simulate_race(...)` and managing the background simulation thread.”

  - Move implementation notes about telemetry batching, team placeholders and seeding into the `services`/engine sections or explicitly state which file handles each responsibility (`services/race_simulation_api.py`, `RaceLogic/realtime_race_engine.py`, `GUI/gui_race_visual.py`).

- If you prefer the launcher to perform higher-level orchestration, we can:

  - Patch launcher.py to construct a `RaceContext` and call `simulate_race(...)` itself (but that duplicates responsibilities currently in `RaceWindow`), or

  - Leave launcher.py minimal and update docs for clarity (recommended).

- I can prepare a small patch to the Midpoint doc with the corrected wording and explicit file->responsibility mappings (I can do that now if you want).

Which do you want next?

- Update the Midpoint doc wording (I can patch it).

- Or change code so launcher.py performs the orchestration (I can implement that, but we should discuss design first).


National College of Ireland

BSc (Honours) in Computing Software Development

 Academic Year 2025/2026

Student Name: Eoin Fitzsimons

Student Number: X23151374

Student Email: x23151374@student.ncirl.ie

Project Title: Momentum - Multi-Discipline Motorsport Simulation System

Technical Report


Contents

Contents 22

Executive Summary 29

1 Introduction 30

1.1 Background 30

1.2 Aims 30

1.3 Technology 31

1.4 Structure 32

2 System 34

2.1 Functional Requirements 34

2.1.1 HIGH Priority (Must Have - Core Gameplay): 34

2.1.2 MEDIUM Priority (Career Mode Depth): 34

2.1.3 LOW Priority (Polish & Advanced Features): 34

2.2 UC-1: Read Driver Details 35

2.2.1 Scope 35

2.2.2 Description 35

2.2.3 Actors 35

2.2.4 Flow Description 36

2.3 UC-2: Read Race Configuration 37

2.3.1 Scope 37

2.3.2 Description 37

2.3.3 Actors 37

2.3.4 Flow Description 37

2.4 UC-3: Create Race Result 39

2.4.1 Scope 39

2.4.2 Description 39

2.4.3 Actors 39

2.4.4 Flow Description 39

2.5 UC-4: Read Race Results 40

2.5.1 Scope 40

2.5.2 Description 40

2.5.3 Actors 40

2.5.4 Flow Description 41

2.6 UC-5: Read Championship Details 42

2.6.1 Scope 42

2.6.2 Description 42

2.6.3 Actors 42

2.6.4 Flow Description 42

2.7 UC-6: Update Championship Standings 43

2.7.1 Scope 43

2.7.2 Description 44

2.7.3 Actors 44

2.7.4 Flow Description 44

2.8 UC-7: Create Race Event 45

2.8.1 Scope 45

2.8.2 Description 45

2.8.3 Actors 45

2.8.4 Flow Description 45

2.9 UC-8: Read Race Schedule 46

2.9.1 Scope 46

2.9.2 Description 46

2.9.3 Actors 46

2.9.4 Flow Description 46

2.10 UC-9: Update Race Status 47

2.10.1 Scope 47

2.10.2 Description 48

2.10.3 Actors 48

2.10.4 Flow Description 48

2.11 UC-10: Create Championship 48

2.11.1 Scope 49

2.11.2 Description 49

2.11.3 Actors 49

2.11.4 Flow Description 49

2.12 UC-11: Read Team Details 50

2.12.1 Scope 51

2.12.2 Description 51

2.12.3 Actors 51

2.12.4 Flow Description 51

2.13 UC-12: Create New Team 52

2.13.1 Scope 52

2.13.2 Description 52

2.13.3 Actors 52

2.13.4 Flow Description 52

2.14 UC-13: Read Team Details (player team) 54

2.14.1 Scope 54

2.14.2 Description 54

2.14.3 Actors 54

2.14.4 Flow Description 54

2.15 UC-14: Update Team Attributes 55

2.15.1 Scope 55

2.15.2 Description 55

2.15.3 Actors 56

2.15.4 Flow Description 56

2.16 UC-15: Read Available Drivers 56

2.16.1 Scope 57

2.16.2 Description 57

2.16.3 Actors 57

2.16.4 Flow Description 57

2.17 UC-16: Update Driver Contract 58

2.17.1 Scope 59

2.17.2 Description 59

2.17.3 Actors 59

2.17.4 Flow Description 59

2.18 UC-17: Read Available Staff 59

2.18.1 Scope 60

2.18.2 Description 60

2.18.3 Actors 60

2.18.4 Flow Description 60

2.19 UC-18: Update Staff Contract 61

2.19.1 Scope 61

2.19.2 Description 62

2.19.3 Actors 62

2.19.4 Flow Description 62

2.20 UC-19: Update Driver Skills/Age 63

2.20.1 Scope 63

2.20.2 Description 63

2.20.3 Actors 63

2.20.4 Flow Description 63

2.21 UC-20: Update Team Budget 65

2.21.1 Scope 65

2.21.2 Description 65

2.21.3 Actors 65

2.21.4 Flow Description 65

2.22 UC-21: Create New Driver 66

2.22.1 Scope 66

2.22.2 Description 66

2.22.3 Actors 67

2.22.4 Flow Description 67

2.23 UC-22: Create New Staff Member (staff generation) 68

2.23.1 Scope 68

2.23.2 Description 68

2.23.3 Actors 68

2.23.4 Flow Description 68

2.24 UC-23: Delete Championship 69

2.24.1 Scope 69

2.24.2 Description 69

2.24.3 Actors 69

2.24.4 Flow Description 69

2.25 UC-24: Create Custom Track 70

2.25.1 Scope 70

2.25.2 Description 71

2.25.3 Actors 71

2.25.4 Flow Description 71

2.26 UC-25: Update Track Characteristics 72

2.26.1 Scope 72

2.26.2 Description 72

2.26.3 Actors 72

2.26.4 Flow Description 72

2.27 UC-26: Delete Track 73

2.27.1 Scope 73

2.27.2 Description 73

2.27.3 Actors 73

2.27.4 Flow Description 73

2.28 UC-27: Read Staff Performance Modifiers 74

2.28.1 Scope 74

2.28.2 Description 74

2.28.3 Actors 75

2.28.4 Flow Description 75

2.29 UC-28: Update Driver Appearance 76

2.29.1 Scope 76

2.29.2 Description 76

2.29.3 Actors 76

2.29.4 Flow Description 76

2.30 UC-29: Update Team Branding 77

2.30.1 Scope 77

2.30.2 Description 77

2.30.3 Actors 77

2.30.4 Flow Description 77

2.31 Data Requirements 79

2.31.1 Database Schema 79

2.31.2 Data Integrity 80

2.31.3 Performance Optimisations 80

2.31.4 Diagram 81

2.32 User Requirements 82

2.32.1 Primary user personas: 82

2.32.2 Cross-cutting user requirements: 83

2.33 Environmental Requirements 84

2.33.1 Hardware Requirements: 84

2.33.2 Software Requirements: 84

2.33.3 Deployment Requirements: 84

2.33.4 Scalability Considerations: 84

2.34 Usability Requirements 85

2.34.1 Accessibility 85

2.34.2 Performance 86

2.34.3 Readability 86

2.35 Design & Architecture 88

2.36 Implementation 89

2.37 Graphical User Interface (GUI) 91

2.37.1 Main Menu 91

2.37.2 Race Screen 92

2.38 Testing 93

2.39 Evaluation 94

3 Conclusions 95

4 Further Development or Research 96

5 Bibliography 97

6 Appendices 99

6.1 Project Proposal 99

6.1.1 Objectives 99

6.1.2 Background 101

6.1.3 State of the Art 102

6.1.4 Technical Approach 103

6.1.5 Technical Details 104

6.1.6 Special Resources Required 105

6.1.7 Project Plan 107

6.1.8 Testing 109

6.2 Reflective Journals 110

6.3 Other materials used 115


Executive Summary

The project delivers a multi-discipline motorsport management simulator designed to provide statistically rich, credible racing behaviour and deep team-management systems within a lightweight, locally runnable environment. The report documents the motivation, aims, architecture, implementation and requirements of the system, establishing a formal basis for the completed work and future development.

The simulator addresses the limited scope of existing titles by integrating multiple racing disciplines, detailed management mechanics and a realtime event-driven race engine. Background influences include modding work on car-centric games and exposure to simple retro racers, guiding the emphasis on expressive vehicle systems and low-fi visual presentation.

Core aims include broad discipline coverage, depth of management features (contracts, staff, budgets, setup), and practical deployability. Planned features comprise per-frame racing telemetry, discipline modules, a compact driver/team model, a PyQt6 interface, staff and budget systems, and playtesting tools for collecting quantitative metrics such as DNFs, lap-time distributions and volatility.

The technology stack is based on Python 3.13, FastAPI, Uvicorn, Pydantic, SQLite, NumPy/pandas/SciPy, PyTorch, PyQt6, and geometry libraries (Shapely, Bezier). This combination supports rapid iteration, scientific analysis, portable distribution and performant desktop visualisation.

Functional requirements are prioritised into core gameplay tasks (reading driver data, reading race configuration, generating race results), extended career-mode functionality (championship logic, team management, driver/staff contracts, budgets, ageing and skill updates), and optional enhancement features (custom tracks, branding, appearance updates, and creation of new driver/staff pools). The report also outlines the system structure: requirements and use cases, architecture, and GUI design.


Introduction

Background

Motorsport management simulation games have been a niche but dedicated gaming genre since the 1990s. However, most existing games focus on a single discipline (usually Formula 1) or lack the depth required for authentic simulation. Games like Football Manager have shown that deep statistical simulation can create compelling gameplay, but motorsport has remained underserved. The motivation stemmed from both personal interest in motorsport and the technical challenge of building a complex simulation system that balances realism with performance.

Over the summer I spent time modding and studying car-centric games being Juiced and Need for Madness. That work reinforced my interest in vehicle dynamics and UI for car-focused tools, and it influenced the direction of this project: continue with car-centric coding, reuse practical techniques from the modding workflows and prioritise features that make vehicle and team systems expressive for players.

During an internship at HSE, my manager would bring out a Raspberry Pi and we would play simple racing games from his childhood like Micro Machines during lunch, those sessions inspired parts of the game's low‑fi graphics and vehicle‑focused presentation.

Aims

High level aims

Broader coverage: provide a single platform that supports multiple racing disciplines so gameplay and balance can be compared across formats.

Depth over novelty: prioritise detailed management systems (contracts, staff effects, budget scaling, vehicle setup) and credible on-track behaviour.

Practical deliverability: keep the project runnable on a standard computer using a single repository and lightweight dependencies.

Planned features

Realtime decision-driven racing engine that emits per-frame position updates and discrete events (DNF, lap complete).

Discipline modules enabling per-discipline configuration for rules, scoring and vehicle characteristics.

Compact driver/team data model with core attributes and career metadata.

PyQt6 GUI for visualisation.

Team and staff systems (budgets, operations rating, strategy profiles) that influence performance over a season and beyond.

Playtesting and tuning tools: scripts that run short scenarios and collect metrics (DNFs, position volatility, lap times). For assistance of tuning data for the final product.

Technology

Core Language

Python 3.13:

Reason: Modern, productive language with strong scientific and tooling ecosystems, good for rapid iteration and student projects.

Advantage over alternatives: Easier to prototype than Java/C# and has far richer data-science libraries than many web-focused languages, less ops overhead than compiled languages.

(Python Software Foundation, 2026)

Backend and API

FastAPI + Uvicorn + Pydantic:

Reason: Fast, async-first web framework with automatic validation and OpenAPI generation, Uvicorn is a lightweight ASGI server. Pydantic gives robust model validation for API schemas.

Advantage over alternatives: Faster development and clearer request/response models vs. Flask, simpler async support than Django, better runtime performance and type-safety compared with many microframeworks.

(FastAPI, 2026) (Pydantic, 2026) (Uvicorn, 2026)

Data Storage

SQLite:

Reason: Single-file, zero-admin persistent storage that’s simple to bundle with the project and ideal for a desktop game/simulator.

Advantage over alternatives: Far easier to set up than PostgreSQL or MySQL for local dev and distribution, good performance for moderate-sized datasets used by the game.

(SQLite Consortium, 2026)

Computation and Analysis

NumPy, SciPy, Matplotlib:

Reason: Battle-tested numerical and data-manipulation libraries for vectorised computations, statistics, and analysis/export tasks.

Advantage over alternatives: Mature ecosystem, high performance for numerical workloads, and strong interoperability across scientific libraries.

(NumPy Developers, 2026) (SciPy Community, 2026)

Desktop User Interface

PyQt6:

Reason: Stable, native-feeling desktop GUI toolkit with good performance for interactive visualisers and complex widgets.

Advantage over alternatives: Better native widget fidelity and performance than Tkinter, simpler native look and more features than Kivy for desktop apps, lighter and more responsive than Electron-based stacks.

(Riverbank Computing Limited, 2026)

Supporting Libraries

Faker, python-dotenv, Unidecode, Pillow:

Reason: 

Faker: realistic seeded name generation for drivers/teams.

python-dotenv: simple environment config loading for dev/prod differences.

Unidecode: Normalises Unicode text into ASCII-compatible formats for consistent processing.

Pillow: Provides image processing capabilities for asset handling.

Advantage over alternatives: Each is lightweight, well-documented and widely used in, making onboarding easier.

(Faker Contributors, 2026) (Kumar, 2026) (Gross, 2026) (Python Pillow Team, 2026)

Why this stack overall:

Focused on rapid development, reproducible local execution, and a strong scientific toolchain for simulation and analysis. The stack maintains a simple runtime model suitable for desktop distribution (SQLite, PyQt6) while supporting structured backend services and data processing (FastAPI, NumPy). The selected technologies prioritise developer productivity, portability, and the ability to extend or replace individual components with minimal architectural impact.

Structure

Executive Summary: a concise synopsis of the project aims, methods, principal results and conclusions intended for quick inspection by assessors.

1 Introduction: background motivation, high-level aims, a formal description of the chosen technology stack, and this structural overview.

2 System: comprehensive requirements and use cases. Presents prioritised functional requirements (HIGH/MEDIUM/LOW), detailed use case specifications (UC-1 ... UC-29), data requirements and constraints, user and environmental requirements, and usability targets.

Design and Architecture: high-level architecture diagrams, module decomposition, interfaces and data models. Covers both the current implementation and planned future extensions.

Implementation: concrete implementation notes, file and package layout, configuration and instructions to run the system locally (including scripts used for data generation and testing).

Graphical User Interface (GUI): descriptions of the launcher, main menu and race visualiser screens, plus any custom widgets and interaction patterns used for playtesting.

Testing: test strategy and harnesses, unit and integration tests, playtesting procedures and metric collection (for example DNF counts, lap-time distributions and volatility measures).

Evaluation: presentation of experimental results gathered from playtests and simulation runs, analysis of outcomes against acceptance criteria, and limitations of the current work.

Conclusions: summary of project outcomes, lessons learned and the extent to which aims were met.

Further Development or Research: recommended next steps, planned features and possible research directions arising from the project.

Bibliography and Appendices: references, project proposal, reflective journals and additional materials used to support the report.

System

Functional Requirements

The following functional requirements are listed in priority order:

HIGH Priority (Must Have - Core Gameplay):

UC-1: Read Driver Details

UC-2: Read Race Configuration

UC-3: Create Race Result

MEDIUM Priority (Career Mode Depth):

UC-4: Read Race Results

UC-5: Read Championship Details

UC-6: Update Championship Standings

UC-7: Create Race Event

UC-8: Read Race Schedule

UC-9: Update Race Status

UC-12: Create Championship

UC-11: Read Team Details

UC-12: Create New Team

UC-13: Read Team Details (team screen)

UC-14: Update Team Attributes

UC-15: Read Available Drivers

UC-16: Update Driver Contract

UC-17: Read Available Staff

UC-18: Update Staff Contract

UC-19: Update Driver Skills/Age (includes recycling retired drivers)

UC-20: Update Team Budget

LOW Priority (Polish & Advanced Features):

UC-21: Create New Driver (not needed - recycle existing 1,781 drivers)

UC-22: Create New Staff Member (not needed - recycle existing 57,936 staff)

UC-23: Delete Championship

UC-24: Create Custom Track

UC-25: Update Track Characteristics

UC-26: Delete Track

UC-27: Read Staff Performance Modifiers

UC-28: Update Driver Appearance

UC-29: Update Team Branding

UC-1: Read Driver Details



Scope

Retrieve a complete driver profile with attributes across multiple categories (technical, physical, mental, racecraft) to configure drivers for race simulation.

Description

The system provides driver information to the GUI and simulation engine. A driver profile contains name, nationality, age, skill ratings, and team assignment.

Actors

GUI - displays driver information for race setup and team management screens.

Simulation Engine - retrieves driver data to initialise AI agents for race simulation.

System - retrieves and returns driver records.

Flow Description

Precondition

The system has a populated driver database; requested driver record exists.

Activation

Starts when the GUI loads a race setup screen or the simulation engine initialises a race.

Main Flow

The GUI or simulation engine requests a driver profile.

The system retrieves the driver record with all attributes.

The system validates the driver data is complete.

The GUI displays the driver details, or the simulation engine initialises the driver for race execution.

Flow ends when the driver profile is displayed or race initialisation is complete.

Alternate Flow A1

The requested driver does not exist in the system.

The system notifies the caller that the driver was not found.

Flow returns to the driver selection screen or the screen that initiated the request.

Alternate Flow A2

The driver database connection fails.

The system displays an error message and offers to retry or regenerate the database.

Flow returns to the main menu or returns control to the user.

Exceptional Flow E1

The driver record contains incomplete or corrupt data.

The system logs the error for diagnostic purposes.

The system uses default attribute values to allow continued operation.

Flow continues with the operation using the default values and the user is notified of degraded data.

Termination

The driver profile is displayed or used for simulation initialisation.

UC-2: Read Race Configuration



Scope

Retrieve track information including layout, surface type, and race parameters to configure the simulation engine.

Description

The system provides track data to the GUI and simulation engine. Track records include name, location, length, surface characteristics, and corner configuration.

Actors

GUI - displays track information on race setup screens.

Simulation Engine - loads track configuration for physics calculations.

System - retrieves and provides track records.

Flow Description

Precondition

The system has a populated track database with at least one track record.

Activation

Starts when the GUI loads a race setup screen or the simulation engine begins initialisation.

Main Flow

The GUI or simulation engine requests track data.

The system retrieves the track record with configuration details.

The system validates the track data is complete and consistent.

The GUI displays the track information, or the simulation engine loads the track for race execution.

Flow ends when the track is displayed or ready for simulation.

Alternate Flow A1

The requested track does not exist.

The system notifies the caller that the track was not found.

Flow returns to the track selection screen with guidance to select another track.

Alternate Flow A2

The track database is empty or unpopulated.

The system notifies the user and displays a message explaining that tracks are not yet available.

Flow returns to the main menu.

Exceptional Flow E1

The track record contains missing or invalid data.

The system logs the error and uses reasonable defaults for missing attributes.

The system allows the race to proceed with the available track data.

Flow continues with the operation, and the user is notified of the issue.

Termination

The track is displayed or loaded for simulation.

UC-3: Create Race Result



Scope

Capture and persist the outcome of a completed race simulation, including positions, lap times, and DNF information.

Description

When a race simulation completes, the system records the final classification with finishing positions, times, and any retirements.

Actors

Simulation Engine - executes the race and generates final results.

GUI - displays the race results to the user.

System - persists race results to storage.

Flow Description

Precondition

A race simulation has been executed and completed or terminated by the user.

Activation

Starts when the race simulation finishes or is stopped.

Main Flow

The simulation engine completes the race and generates classification data.

The system validates that all participants are accounted for and positions are sequential.

The system stores the race results with the final classification, times, and any DNF statuses.

The GUI displays the race results to the user.

Flow ends when the results are persisted and displayed.

Alternate Flow A1

The user stops the race before completion.

The simulation engine returns partial results with the current positions.

The system stores the partial results and marks the race as incomplete.

Flow returns to the race results screen showing the partial classification.

Alternate Flow A2

All participants fail to finish (all DNF).

The system creates result records for all drivers marked as DNF.

The system persists the results with DNF reasons recorded.

Flow continues and the GUI displays the DNF results.

Exceptional Flow E1

The system fails to store race results.

The system displays an error message and allows the user to retry or proceed.

The race results remain visible on screen but a warning indicates they were not saved.

Flow continues with manual backup options offered to the user.

Exceptional Flow E2

The race result data is invalid or incomplete.

The system logs the error and attempts to store what data is available.

The user is warned that some race data could not be saved.

Flow continues with partial results displayed.

Termination

Race results are persisted and displayed to the user.

UC-4: Read Race Results



Scope

Retrieve and display historical race classification and result data from completed races.

Description

The system provides access to stored race results including finishing positions, times, and DNF information for analysis and display.

Actors

GUI - requests and displays race results.

User - navigates to view race history.

System - retrieves and provides stored results.

Flow Description

Precondition

At least one race has been completed and results have been stored.

Activation

Starts when the user navigates to view race results or race history.

Main Flow

The user requests race results for a specific race or championship.

The system retrieves the stored race results.

The system assembles the complete classification with driver names, teams, positions, and times.

The GUI displays the results in a standings table format.

Flow ends when the race results are displayed.

Alternate Flow A1

No results are found for the requested race.

The system notifies the user that no results are available.

Flow returns to the race history screen or menu.

Alternate Flow A2

The race was incomplete or partial.

The system displays the available results and marks them as incomplete.

Flow returns to the race history view with the incomplete flag visible.

Exceptional Flow E1

The system fails to retrieve stored results.

The system displays an error message.

If cached results are available from memory, the system displays them marked as possibly stale.

Flow continues with the best available data shown.

Exceptional Flow E2

Stored result data is corrupted or inconsistent.

The system logs the error and displays the data that could be recovered.

The user is warned that some result data may be missing or incorrect.

Flow continues with partial or degraded results displayed.

Termination

Race results are displayed to the user, who can then navigate to other screens or compare results.

UC-5: Read Championship Details



Scope

Retrieve championship metadata including season information, standings, and calendar of scheduled races.

Description

The system provides comprehensive championship information to the GUI for display during season progression.

Actors

GUI - displays championship information and standings.

User - navigates to view championship details.

System - retrieves and aggregates championship data.

Flow Description

Precondition

At least one championship exists and is active.

Activation

Starts when the user navigates to the championship overview screen.

Main Flow

The user requests championship details for a specific championship.

The system retrieves the championship metadata including year, discipline, and rules.

The system retrieves the current standings by aggregating race results.

The system retrieves the schedule of races planned for the season.

The GUI displays the championship overview with standings table and upcoming events.

Flow ends when the championship information is displayed.

Alternate Flow A1

The championship has no races scheduled yet.

The system displays the championship information with an empty calendar.

The GUI shows an option to add races to the schedule.

Flow continues with the option for the user to create race events.

Alternate Flow A2

The championship has no race results yet (standings are empty).

The system displays the championship information and shows zero points for all entries.

Flow continues with the empty standings displayed.

Exceptional Flow E1

The system fails to retrieve championship data.

The system displays an error message and offers retry options.

If cached championship data is available, it is displayed marked as possibly stale.

Flow continues with available data or returns to the main menu.

Exceptional Flow E2

The championship structure is invalid or corrupted in storage.

The system logs a diagnostic error.

The system displays what data could be recovered.

The user is notified of the issue and offered recovery options.

Flow returns to the main menu or menu with recovery options.

Termination

Championship overview is displayed with standings and calendar information.

UC-6: Update Championship Standings



Scope

Recalculate and persist updated championship standings after a race completes.

Description

The system recalculates the championship points and standings following each completed race using discipline-specific point systems.

Actors

System - triggers recalculation when results are recorded.

User/Admin - may manually request recalculation.

Flow Description

Precondition

A championship exists with completed races and stored results.

Activation

Starts when a race is completed and results are persisted, or when explicitly requested.

Main Flow

The system gathers all completed race results for the championship.

The system applies the championship's points system to calculate points for each race.

The system aggregates the points for each driver across all races.

The system computes the final standings with drivers sorted by total points.

The system applies tie-breaking rules if needed.

The standings are persisted in storage.

Subscribers to standings updates are notified of the change.

Flow ends when standings are persisted and notifications sent.

Alternate Flow A1

A partial or incremental update is requested instead of full recalculation.

The system recalculates only the affected portion of standings.

The system persists the updated standings.

Flow continues with partial standings propagated.

Alternate Flow A2

Multiple standings recalculations are requested concurrently.

The system queues subsequent requests and processes them after the first completes.

Flow returns to the caller with status indicating queueing.

Exceptional Flow E1

The points system rules are missing or invalid.

The system logs the error and uses default point values.

Standings are calculated and marked as using default rules.

An alert is raised for administrative review.

Flow continues with degraded standings.

Exceptional Flow E2

The system fails to persist updated standings.

The system logs the error and queues the standings update for retry.

The user is notified of the persistence issue.

Flow continues and retry is scheduled automatically.

Termination

Updated standings are computed and persisted; downstream systems are notified.

UC-7: Create Race Event 



Scope

Add a new race event to a championship calendar with date, track, and configuration.

Description

The system creates a new race event entry in the championship schedule with validation for date and track conflicts.

Actors

User/Admin - creates a new race event.

System - validates and records the event.

Flow Description

Precondition

A championship exists and is open for event creation; tracks are available.

Activation

Starts when the user submits a new race event creation.

Main Flow

The user provides race event details including date, track, and configuration.

The system validates that the track exists and is available.

The system checks for date conflicts with other scheduled races in the championship.

The system assigns a round number based on the current calendar size.

The system stores the new race event.

The GUI displays confirmation of the new race added to the calendar.

Flow ends when the race event is created and visible in the calendar.

Alternate Flow A1

The selected date conflicts with another scheduled race.

The system notifies the user of the conflict and displays other available dates.

The user can select an alternative date and resubmit.

Flow returns to event creation with the conflict resolved or cancelled.

Alternate Flow A2

The selected track is unavailable or invalid.

The system notifies the user and displays available tracks.

The user selects another track and resubmits.

Flow returns to event creation with a valid track selected.

Exceptional Flow E1

The system fails to store the new race event.

The system logs the error and displays a message to the user.

The system offers to retry the creation.

Flow returns to the event creation form to retry or cancel.

Exceptional Flow E2

Mandatory event fields are missing or invalid.

The system displays validation errors for each invalid field.

The user corrects the fields and resubmits.

Flow returns to event creation with validation feedback.

Termination

Race event is created and added to the championship calendar.


UC-8: Read Race Schedule



Scope

Retrieve and display the ordered calendar of races scheduled for a championship season.

Description

The system provides the season schedule showing all planned races with dates, tracks, and status information.

Actors

GUI - requests and displays the race schedule.

User - navigates to view the schedule.

System - retrieves and provides schedule data.

Flow Description

Precondition

A championship exists; may or may not have races scheduled.

Activation

Starts when the user navigates to view the championship calendar.

Main Flow

The user requests the race schedule for a championship.

The system retrieves all races for the championship, ordered by round number.

The system assembles the schedule with date, track, round number, and current status for each race.

The GUI displays the calendar in chronological order.

Flow ends when the schedule is displayed.

Alternate Flow A1

The championship does not exist.

The system notifies the user and displays a message.

The GUI provides guidance on creating a championship.

Flow returns to the main championship screen or menu.

Alternate Flow A2

The championship exists but no races are scheduled.

The system returns an empty schedule.

The GUI displays an empty calendar and offers an option to add races.

Flow continues with guidance to schedule events.

Exceptional Flow E1

The system fails to retrieve schedule data.

The system displays an error message and attempts to show cached schedule data if available.

Flow returns to the menu or retries the request.

Exceptional Flow E2

The schedule data is incomplete or corrupt.

The system retrieves and displays the available schedule data.

The user is warned that some data may be missing.

Flow continues with partial schedule displayed.

Termination

Race schedule is displayed to the user for the selected championship.

UC-9: Update Race Status



Scope

Change a race event's lifecycle status through stages: scheduled → in-progress → completed (or cancelled).

Description

The system manages race state transitions with validation of allowed transitions and updates to related data.

Actors

Simulation Engine - updates status during and after race execution.

User/Admin - may manually change status for management purposes.

System - validates and processes status changes.

Flow Description

Precondition

A race event exists; the user has permission to change its status.

Activation

Starts when a status change is requested (e.g., starting a race, completing it, or cancelling).

Main Flow

The user or system requests a race status change with the new target status.

The system validates that the transition is allowed (e.g., scheduled → in-progress is allowed; completed → scheduled is not).

The system updates the race event status.

Dependent systems are notified of the status change.

Flow ends when status is updated and notifications sent.

Alternate Flow A1

An invalid status transition is attempted (e.g., trying to transition from completed back to in-progress).

The system rejects the transition and displays the allowed transitions for the current state.

The user can select a valid transition or cancel.

Flow returns to the race management screen.

Alternate Flow A2

The user requests race cancellation while the race is in-progress.

The system initiates graceful abort procedures and transitions the race to cancelled.

Related data is updated to reflect the cancellation.

Flow returns to the race management screen with cancellation confirmed.

Exceptional Flow E1

The system fails to update the race status in storage.

The system logs the error and displays a message.

The system queues the status change for retry.

The user is informed of the issue and given retry options.

Flow continues with automatic retry scheduled.

Exceptional Flow E2

Notification of dependent systems fails during status change.

The system completes the status update but records the notification failure.

The user is notified that the status was changed but some notifications may be pending.

Flow continues with notifications retried automatically.

Termination

Race status is updated and stored; dependent systems are notified of the change.

UC-10: Create Championship



Scope

Create a new championship record for a season with initial configuration and empty calendar.

Description

The system creates a new championship season with discipline, rules, and placeholder for events to be scheduled.

Actors

User/Admin - initiates championship creation.

System - validates and creates the championship record.

Flow Description

Precondition

The user has permission to create championships; season configuration is available.

Activation

Starts when the user submits a championship creation request.

Main Flow

The user provides championship details including name, discipline, season year, and points system.

The system validates the provided information.

The system creates the championship record with initial status (empty calendar, no standings).

The system stores the championship in persistent storage.

The system notifies dependent systems that a new championship is available.

The GUI displays confirmation and displays the new championship.

Flow ends when the championship is created and stored.

Alternate Flow A1

The selected ruleset or points system is invalid or missing.

The system uses a default ruleset and continues with championship creation.

The championship is marked for review to confirm the default ruleset is acceptable.

Flow continues with championship created using defaults.

Exceptional Flow E1

The system fails to store the championship.

The system logs the error and displays a message to the user.

The system queues the championship creation for automatic retry.

Flow returns to the championship creation screen with retry option.

Exceptional Flow E2

Required fields are missing or invalid.

The system displays validation errors.

The user corrects the fields and resubmits.

Flow returns to championship creation with feedback.

Termination

Championship is created and stored; downstream systems are notified.

UC-11: Read Team Details



Scope

Retrieve comprehensive team profile including budget, tier classification, roster, and performance information.

Description

The system provides complete team information to the GUI for display on team management and information screens.

Actors

GUI - requests and displays team information.

User - navigates to view team details.

System - retrieves and provides team records.

Flow Description

Precondition

At least one team exists in the system.

Activation

Starts when the user navigates to view team details.

Main Flow

The user requests details for a specific team.

The system retrieves the team record including name, discipline, tier, budget, and headquarters.

The system retrieves the current roster (assigned drivers and staff).

The system retrieves financial information including budget status and expenditures.

The GUI displays the complete team profile.

Flow ends when team details are displayed.

Alternate Flow A1

The requested team does not exist.

The system notifies the user that the team was not found.

Flow returns to the team selection or team list screen.

Alternate Flow A2

The team has no assigned drivers or staff.

The system displays the team information with an empty roster.

The GUI shows the roster as empty and may offer hiring options.

Flow continues with empty roster displayed.

Exceptional Flow E1

The system fails to retrieve team data.

The system displays an error message.

If available, cached team data is shown marked as possibly stale.

Flow continues with available data or returns to team list.

Exceptional Flow E2

Team data is incomplete or corrupt.

The system retrieves and displays available data.

The user is warned that some team information may be missing.

Flow continues with partial team profile displayed.

Termination

Team profile is displayed with complete or partial information.

UC-12: Create New Team



Scope

Create a new team record with initial configuration, budget allocation, and optional roster.

Description

The system creates a new team entry for a player or as an NPC team with starting resources and configuration.

Actors

User/Admin - creates a new team.

System - validates and provisions the team.

Flow Description

Precondition

The user has permission to create teams; resources are available for allocation.

Activation

Starts when the user submits a team creation request.

Main Flow

The user provides team details including name, discipline, headquarters location, and starting tier.

The system validates the team information (unique name, valid discipline, etc.).

The system allocates starting resources and budget based on team tier.

The system creates the team record.

The system stores the team in persistent storage.

The GUI displays confirmation and the new team.

Flow ends when the team is created and stored.

Alternate Flow A1

The team name already exists.

The system notifies the user and suggests alternative names.

The user provides a new name and resubmits.

Flow returns to team creation with conflict resolved.

Alternate Flow A2

The selected discipline is not available or invalid.

The system notifies the user and displays available disciplines.

The user selects a valid discipline and resubmits.

Flow returns to team creation with valid discipline selected.

Exceptional Flow E1

The system fails to create or store the team.

The system logs the error and displays a message.

The system queues the team creation for automatic retry.

Flow returns to the team creation screen with retry option.

Exceptional Flow E2

Resource allocation fails (insufficient budget available).

The system notifies the user and adjusts the team tier or starting resources.

The user is prompted to confirm the adjusted allocation.

Flow returns to team creation with adjusted parameters.

Termination

Team is created with initial budget and configuration; ready for roster management.

UC-13: Read Team Details (player team)



Scope

Retrieve the player's own team information with editable fields and management options.

Description

The system provides the player's team data for management purposes, including roster and budget that can be modified.

Actors

GUI - requests and displays the player's team.

Player - views and manages their team.

System - retrieves the player's team record.

Flow Description

Precondition

The player has an assigned team; authorization is valid.

Activation

Starts when the player navigates to their team management screen.

Main Flow

The system identifies the player's team assignment.

The system retrieves the team record with all details including roster and budget.

The system marks fields that are editable for the player.

The GUI displays the player's team profile with editable controls.

Flow ends when the team is displayed with edit options available.

Alternate Flow A1

The player does not have an assigned team.

The system notifies the player and displays guidance on creating or joining a team.

The GUI provides options to create a new team or join an existing one.

Flow returns to the main menu or team creation flow.

Exceptional Flow E1

The system fails to retrieve the player's team.

The system displays an error message.

If cached team data is available, it is shown marked as possibly stale.

Flow returns to the main menu with error handling.

Exceptional Flow E2

Authorization check determines the player does not own the displayed team.

The system revokes edit permissions and displays the team in read-only mode.

The user is notified of the permission issue.

Flow continues with read-only team view.

Termination

Player's team is displayed with appropriate edit permissions and management options available.

UC-14: Update Team Attributes



Modify team settings including budget allocation, facility upgrades, and strategic configuration.

Description

The system allows players and admins to update team properties with validation of budget and resource constraints.

Actors

Player - updates their team attributes.

Admin - may update any team attributes.

System - validates and persists changes.

Flow Description

Precondition

The user has edit permissions for the team; the team exists in storage.

Activation

Starts when the user submits team attribute updates.

Main Flow

The user edits team attributes such as name, headquarters, or budget allocation.

The system validates the changes against available budget and constraints.

The system checks that new attribute values are acceptable (e.g., name is unique, values are in valid ranges).

The system persists the updated team record.

The system notifies subscribers of the team update.

The GUI displays the updated team information.

Flow ends when changes are persisted and displayed.

Alternate Flow A1

The proposed budget allocation exceeds available funds.

The system notifies the user of the shortfall and suggests alternatives.

The user can adjust the allocation or request additional funding.

Flow returns to team update with revised budget or cancellation.

Alternate Flow A2

A facility upgrade is requested.

The system validates the upgrade is available and cost is covered by budget.

The system deducts the upgrade cost and applies the upgrade.

Flow continues with upgrade applied and budget deducted.

Exceptional Flow E1

The system fails to persist team updates.

The system logs the error and displays a message.

The system queues the update for automatic retry.

Flow continues with retry scheduled.

Exceptional Flow E2

Concurrent updates to team data are detected.

The system displays the current team state and informs the user of the conflict.

The user can retry or merge their changes with current state.

Flow returns to team update screen with current data displayed.

Termination

Team attributes are updated and persisted; subscribers are notified of changes.


UC-15: Read Available Drivers



Scope

Retrieve a list of drivers available for hiring/contract with filtering and pagination.

Description

The system provides a browsable pool of uncontracted drivers for team recruitment, with support for filtering by discipline, rating, and other criteria.

Actors

GUI - requests and displays available drivers.

Player - browses drivers for hiring.

System - retrieves and filters driver records.

Flow Description

Precondition

At least one uncontracted driver exists in the system.

Activation

Starts when the user opens the driver hiring/recruitment screen.

Main Flow

The user optionally applies filters (discipline, rating range, etc.).

The user optionally selects pagination parameters (page number, results per page).

The system retrieves uncontracted drivers matching the filters.

The system sorts drivers by requested criteria (rating, age, etc.).

The system returns the paginated results with availability status and estimated cost.

The GUI displays the available driver list.

Flow ends when driver candidates are displayed.

Alternate Flow A1

No drivers match the applied filters.

The system returns an empty result set.

The GUI displays a message indicating no matches and suggests relaxing filters.

Flow returns to the driver search with filter options visible.

Alternate Flow A2

The results exceed a single page.

The system provides pagination information including total count and navigation.

The user can browse to other pages of results.

Flow continues with paginated results displayed.

Exceptional Flow E1

The system fails to retrieve driver data.

The system displays an error message.

If available, cached driver list is shown marked as possibly stale.

Flow returns to the main screen or offers retry.

Exceptional Flow E2

Search or filter logic fails.

The system falls back to a basic driver list without filtering.

The user is notified of reduced search capabilities.

Flow continues with unfiltered driver list displayed.

Termination

List of available drivers is displayed for recruitment.

UC-16: Update Driver Contract 



Scope

Sign, renew, modify, or terminate a driver contract and update team roster and budget accordingly.

Description

The system manages driver employment, updating roster assignments, contract terms, and team finances.

Actors

Player - initiates driver contract actions.

System - validates and processes contracts.

Flow Description

Precondition

A driver and team exist; negotiation terms are determined.

Activation

Starts when the player submits a driver contract action (signing, renewal, termination).

Main Flow

The player selects a driver and confirms contract terms (length, salary, etc.).

The system validates that the team has sufficient budget for the contract.

The system validates contract constraints (duration limits, salary cap rules, etc.).

The system creates or updates the contract record.

The system updates the driver's team assignment.

The system deducts salary from the team budget.

The system persists the contract changes.

The GUI displays confirmation of the contract action.

Flow ends when contract is persisted and roster is updated.

Alternate Flow A1

The team has insufficient budget for the proposed contract.

The system notifies the player of the budget shortfall.

The player can reduce the contract value, seek sponsorship, or cancel.

Flow returns to contract negotiation with budget options.

Alternate Flow A2

The driver is already contracted to another team.

The system notifies the player that the driver is unavailable.

The system provides alternatives or guidance for transfer procedures.

Flow returns to driver selection with conflict noted.

Exceptional Flow E1

The system fails to persist the contract.

The system logs the error and displays a message.

The system queues the contract for automatic retry.

Flow continues with retry scheduled.

Exceptional Flow E2

Contract validation fails due to rule violations.

The system displays the validation errors.

The player adjusts contract terms and resubmits.

Flow returns to contract negotiation with feedback.

Termination

Driver contract is created or updated; roster and budget are adjusted.

UC-17: Read Available Staff



Scope

Retrieve a list of available staff for hiring with roles, ratings, and estimated costs.

Description

The system provides a browsable pool of uncontracted staff members for team recruitment, supporting role-based filtering.

Actors

GUI - requests and displays available staff.

Player - browses staff for hiring.

System - retrieves and filters staff records.

Flow Description

Precondition

At least one uncontracted staff member exists in the system.

Activation

Starts when the player opens the staff hiring screen.

Main Flow

The player optionally applies filters (role, rating range, etc.).

The system retrieves uncontracted staff members matching the filters.

The system sorts staff by requested criteria (rating, role, etc.).

The system returns the results with availability status and salary information.

The GUI displays the available staff list.

Flow ends when staff candidates are displayed.

Alternate Flow A1

No staff match the applied filters.

The system returns an empty result set.

The GUI displays a message suggesting different filter criteria.

Flow returns to the staff search with filter options visible.

Alternate Flow A2

Some staff are partially available (e.g., contracted part-time).

The system returns the staff with availability flags and constraints.

The GUI displays the availability status for each candidate.

Flow continues with full staff list and constraints displayed.

Exceptional Flow E1

The system fails to retrieve staff data.

The system displays an error message.

If available, cached staff list is shown marked as possibly stale.

Flow returns to the main screen or offers retry.

Exceptional Flow E2

Staff data is corrupt or incomplete.

The system retrieves and displays available staff data.

The user is notified that some staff information may be missing.

Flow continues with partial staff list displayed.

Termination

List of available staff is displayed for recruitment.

UC-18: Update Staff Contract



Scope

Hire, release, or modify staff contracts and update team roster and budget accordingly.

Description

The system manages staff employment, updating team assignments, contract terms, and finances.

Actors

Player - initiates staff contract actions.

System - validates and processes contracts.

Flow Description

Precondition

A staff member and team exist; contract terms are determined.

Activation

Starts when the player submits a staff contract action.

Main Flow

The player selects staff and confirms contract terms (role, length, salary).

The system validates the team has sufficient budget for the salary.

The system validates contract constraints (duration, salary cap, staff limits per role).

The system creates or updates the contract record.

The system updates the staff member's team assignment.

The system adjusts the team budget for salary costs.

The system persists the contract changes.

The GUI displays confirmation of the contract action.

Flow ends when contract is persisted and roster is updated.

Alternate Flow A1

The team has insufficient budget for the staff salary.

The system notifies the player of the budget shortfall.

The player can reduce the offer, defer hiring, or cancel.

Flow returns to contract negotiation with budget guidance.

Alternate Flow A2

The staff member is no longer available at contract confirmation.

The system notifies the player that the staff member was hired elsewhere.

The system suggests alternative staff members.

Flow returns to staff selection.

Exceptional Flow E1

The system fails to persist the contract.

The system logs the error and displays a message.

The system queues the contract for automatic retry.

Flow continues with retry scheduled.

Exceptional Flow E2

Contract validation fails due to rule violations (e.g., too many staff of same role).

The system displays the validation errors and constraints.

The player adjusts contract terms and resubmits.

Flow returns to contract negotiation with feedback.

Termination

Staff contract is created or updated; roster and budget are adjusted.

UC-19: Update Driver Skills/Age



Scope

Apply periodic end-of-season updates to driver attributes including aging, skill progression, retirement, and recycling.

Description

The system manages driver lifecycle including skill development over time, retirement when age thresholds are reached, and generation of new rookie drivers from retired drivers.

Actors

System - executes periodic progression updates.

Admin - may trigger manual progression.

Flow Description

Precondition

At least one driver exists; season end has been reached or progression is manually triggered.

Activation

Starts at the end of each season automatically or when manually requested by admin.

Main Flow

The system iterates through all active drivers.

The system applies age increments based on time elapsed.

The system applies skill progression formulas based on age, experience, and performance.

The system checks retirement eligibility based on age and performance thresholds.

Eligible drivers are marked as retired.

Retired drivers are recycled: new rookie drivers are generated to replace them.

All changes are persisted.

Subscribers are notified of progression updates.

Flow ends when all drivers are processed and changes are stored.

Alternate Flow A1

An emergency update is required for a single driver due to injury.

The system allows targeted updates to individual drivers outside the normal schedule.

The affected driver's attributes are modified and persisted.

Flow returns to normal operation.

Alternate Flow A2

A player-triggered training session is performed during the season.

The system applies a limited skill boost to the selected driver.

A cooldown timer is set to prevent abuse.

Flow continues with training boost applied.

Exceptional Flow E1

The batch progression fails for some drivers.

The system logs the error with affected driver IDs.

Failed drivers are skipped in this update cycle and retry is scheduled.

The system completes with partial updates and notifies admin.

Flow continues with partial updates persisted and retry queued.

Exceptional Flow E2

Skill values become invalid (e.g., negative or exceeding limits).

The system clamps values to valid ranges.

The affected records are logged for review.

Skill progression completes with clamped values.

Flow continues with values corrected.

Termination

Driver attributes are updated for next season; retiring drivers are recycled with new rookies.

UC-20: Update Team Budget 



Scope

Adjust team budget based on income from race results, expenses, and financial transactions.

Description

The system manages team finances including salary payments, race fees, income, and sponsor funds.

Actors

System - applies periodic budget adjustments (income, expenses).

Admin/Player - may request manual budget adjustments for special circumstances.

Flow Description

Precondition

A team exists with a current budget.

Activation

Starts when a financial transaction occurs (race completed, season tick, sponsor payout) or is manually requested.

Main Flow

A financial event triggers a budget transaction (income, expense, or transfer).

The system validates the transaction is legitimate and the team can afford it.

The system calculates the amount to be added or deducted.

The system updates the team's budget balance.

The system persists the transaction and new balance.

Subscribers are notified of the budget change.

Flow ends when budget is updated and transaction is logged.

Alternate Flow A1

A debit transaction would result in insufficient funds.

The system rejects the transaction and displays the shortfall.

The player is offered options (defer expense, seek sponsor, reduce spending).

Flow returns to main team management with options for fund raising.

Alternate Flow A2

Multiple concurrent transactions are requested for the same team.

The system queues subsequent transactions to process sequentially.

Each transaction is processed in order with updated budget state.

Flow returns to with transaction queue status.

Exceptional Flow E1

The system fails to persist a budget transaction.

The system logs the error and queues the transaction for retry.

The user is notified of the issue and retry is scheduled.

Flow continues with transaction persisted on retry.

Exceptional Flow E2

A financial calculation produces invalid results (overflow, precision error).

The system logs the error and uses fallback calculation.

The transaction completes with logged error for review.

Flow continues with fallback calculation used.

Termination

Team budget is updated and financial transaction is logged.

UC-23: Delete Championship 



Scope

Remove or archive a championship record and related race data

Description

The system allows deletion or archival of championships with referential integrity checks.

Actors

Admin - authorized to delete or archive championships.

System - validates and performs deletion.

Flow Description

Precondition

Admin has appropriate authorization; championship exists.

Activation

Starts when admin requests championship deletion or archival.

Main Flow

The system checks for dependent records (races, results, standings).

If no dependencies or admin confirms cascade delete, the championship is removed.

Related records are deleted or archived per retention policy.

The operation is persisted.

Flow ends when championship is removed or archived.

Alternate Flow A1

Dependent records prevent deletion.

System displays the dependencies.

Admin can choose to archive instead of delete, or proceed with cascade.

Flow returns to deletion with new option selected.

Exceptional Flow E1

Deletion fails due to database error.

System logs error and rolls back any partial deletes.

Admin is notified and offered manual intervention options.

Flow returns to with error handling.

Termination

Championship is deleted or archived.

UC-24: Create Custom Track



Scope

Create custom track records for use in championship events

Description

Add track entries to the system via admin tools or track database import.

Actors

Admin - creates track records.

Flow Description

Precondition

Track data or configuration is available.

Activation

Starts when track creation is submitted.

Main Flow

Track details are validated.

Track record is created and stored.

Flow ends when track is available for use.

Termination

Track record is created.

Note: Player-facing track customization is deferred to future design. Current delivery uses pre-seeded tracks.

UC-27: Read Staff Performance Modifiers 



Scope

Retrieve computed staff impact modifiers for use during race simulation.

Description

The system provides staff-based performance modifiers to the simulation engine based on assigned team staff and their ratings.

Actors

Simulation Engine - requests staff performance factors.

System - computes and provides modifiers.

Flow Description

Precondition

At least one staff member is assigned to the team, or team exists without staff.

Activation

Starts when the simulation engine requests performance modifiers for a team.

Main Flow

The system retrieves all staff assigned to the team.

The system aggregates staff attributes (role, rating, specialisation).

The system computes performance modifier values based on staff composition.

The modifier set is returned to the simulation engine.

The simulation engine applies the modifiers to team performance calculations during the race.

Flow ends when modifiers are applied during race execution.

Alternate Flow A1

The team has no assigned staff.

The system returns default modifier values (neutral factors).

The simulation engine uses the defaults for race calculations.

Flow continues with default modifiers.

Alternate Flow A2

Staff data is incomplete or missing.

The system computes modifiers using available data.

A flag indicates the modifiers may not reflect full staff impact.

Flow continues with partial modifiers returned and flagged as incomplete.

Exceptional Flow E1

The system fails to retrieve staff data.

The system returns default modifiers and logs an error.

The simulation engine continues with defaults and degraded accuracy.

Flow continues with fallback defaults.

Exceptional Flow E2

Modifier calculation fails due to invalid data.

The system logs the error and provides fallback default values.

The user/admin is notified of the calculation issue.

Flow continues with fallback modifiers.

Termination

Staff performance modifiers are provided to and applied by the simulation engine during race execution.


Data Requirements

This section documents the project's persistent database schema and related data requirements. The database uses a lightweight SQLite schema (SCHEMA_SQL) with seven primary tables and a small set of indexes.

Database Schema

The database contains the following tables (principal columns shown):

Drivers

Primary Key: id (INTEGER PRIMARY KEY AUTOINCREMENT)

Biographical: name (TEXT NOT NULL), nationality (TEXT NOT NULL), birth_date (TEXT NOT NULL)

Performance attributes (REAL, 0.0–100.0 with CHECK where applicable): speed, racecraft, consistency, fitness, reactions, pressure, setup_knowledge, fuel_management, tyre_management, feedback, adaptability

Career statistics: career_points (INTEGER), career_podiums (INTEGER), career_starts (INTEGER), career_dnf (INTEGER), seasons_active (INTEGER)

Discipline wins: single_seater_wins, touring_wins, rally_wins, street_wins, drag_wins, rallycross_wins, endurance_wins (INTEGER)

Career progression & metadata: peak_performance_age (INTEGER), retirement_age (INTEGER), learning_rate (REAL), form_trend (REAL), biography (TEXT), career_highlights (TEXT), preferred_discipline (TEXT), career_phase (TEXT)

Team/contract: current_team_id (INTEGER), previous_teams (TEXT JSON-string), contract_length (INTEGER), salary (REAL), name_locale (TEXT)

Foreign key: current_team_id references teams(id)

Teams

Primary Key: id (INTEGER PRIMARY KEY AUTOINCREMENT)

Fields: name (TEXT NOT NULL UNIQUE), nationality (TEXT NOT NULL), discipline (TEXT NOT NULL), tier (TEXT NOT NULL), budget (REAL NOT NULL)

Optional: founded_year, team_principal, history (TEXT), total_wins, total_podiums, championships (INTEGER)

Performance attributes: operations_rating (REAL DEFAULT 50.0, CHECK 0.0–100.0), strategy_profile (TEXT)

Tracks

Primary Key: id (INTEGER PRIMARY KEY AUTOINCREMENT)

Fields: name (TEXT NOT NULL), country (TEXT NOT NULL), primary_discipline (TEXT NOT NULL)

Physical/auxiliary: is_point_to_point (INTEGER 0/1), joker_enabled (INTEGER 0/1), instructions_json (TEXT), geometry_json (TEXT), pit_entry_index, pit_exit_index

Note: additional track geometry and physical attributes are modelled in the Track dataclass and can be persisted in JSON fields when required.

Championships

Primary Key: id (INTEGER PRIMARY KEY AUTOINCREMENT)

Fields: name (TEXT NOT NULL UNIQUE), discipline (TEXT NOT NULL), season_length (INTEGER NOT NULL), points_system (TEXT NOT NULL), current_season (INTEGER NOT NULL)

Races

Primary Key: id (INTEGER PRIMARY KEY AUTOINCREMENT)

Foreign Keys: championship_id (REFERENCES championships(id)), track_id (REFERENCES tracks(id))

Fields: season (INTEGER), round_number (INTEGER), race_date (TEXT NOT NULL), weather_conditions (TEXT), laps (INTEGER), status (TEXT DEFAULT 'scheduled')

RaceResults

Primary Key: id (INTEGER PRIMARY KEY AUTOINCREMENT)

Foreign Keys: race_id (REFERENCES races(id)), driver_id (REFERENCES drivers(id)), team_id (REFERENCES teams(id))

Fields: position (INTEGER NOT NULL), fastest_lap (INTEGER 0/1 DEFAULT 0), points (INTEGER DEFAULT 0), dnf_reason (TEXT)

Expanded persisted fields: time_seconds, grid_position, laps_completed, best_lap_time, average_lap_time, pitstops, tyre_strategy, penalties_seconds, penalty_reason, gap_to_winner_seconds, status (TEXT DEFAULT 'FINISHED'), recorded_at

StaffMembers

Primary Key: id (INTEGER PRIMARY KEY AUTOINCREMENT)

Fields: name (TEXT NOT NULL), role (TEXT NOT NULL), rating (REAL DEFAULT 50.0), current_team_id (INTEGER REFERENCES teams(id))

Data Integrity

Foreign key constraints: Implemented for drivers.current_team_id -> teams(id), races.championship_id -> championships(id), races.track_id -> tracks(id), race_results.(race_id,driver_id,team_id) -> races/drivers/teams, and staff_members.current_team_id -> teams(id).

CHECK constraints: Core driver and team numeric attributes (e.g., speed, operations_rating) include CHECK(range) clauses in SCHEMA_SQL to enforce 0.0–100.0 where appropriate.

UNIQUE constraints: teams.name and championships.name are declared UNIQUE to prevent duplicates.

NOT NULL: Critical fields use NOT NULL (e.g., driver name, nationality, birth_date; team name, discipline, budget; race race_date).

Performance Optimisations

Indexes: The schema creates the following indexes: idx_drivers_team on drivers(current_team_id), idx_teams_discipline on teams(discipline), and idx_race_results_driver on race_results(driver_id).

Query patterns: Query patterns favour small, targeted queries and joins; larger or optional payloads are stored as JSON/text to avoid wide tables.

Composite lookups are supported to efficiently query races by championship, season and round, and to fetch results by race.

Diagram


User Requirements

Primary user personas:

Personal

Specific

Measurable

Achievable

Relevant

Time-bound

Casual Race Fans

Start a single race using default driver and configuration

Complete a race within 5 minutes, HUD text legible, top-line stats visible without extra menus

Default presets and simplified HUD provided

Fast, entertaining access for casual players

Within 5 minutes of app launch

Management / Career Mode Players

Save/load careers, manage teams and drivers, adjust contracts

Save/load completes without data loss, standings recalculation finishes reliably, contract/transfer changes reversible via UI

Backed by SQLite persistence, background job queue, and UI validation

Supports deep career management and championship progression

Operations completed within session, save/load <30 seconds

Modders / Content Creators

Import/export tracks, drivers, or balance changes using JSON/CSV

Custom track import succeeds and visible, names can be added/modified

Tools provided with documented asset pipeline, RNG seeds hidden

Enables content creation and community engagement

Import/export completes within 60 seconds for standard files

Cross-cutting user requirements:

Requirement

Specific

Measurable

Achievable

Relevant

Time-bound

Local-first

Game runs fully offline

All core features accessible offline

SQLite included, no mandatory online services

Ensures usability in offline environments

Instant availability on app launch

Replay and Investigation

Races record telemetry and events

Telemetry stored, replay visualisation accessible

Batched IO writes minimise overhead, simulation non-deterministic

Allows analysis of AI and player performance

Telemetry available immediately after race completion

Low Friction Installer/Run

Install and run via Python or packaged binary

Instructions execute successfully, binary launches app without additional setup

PyInstaller binary provided, minimal Python dependencies documented

Reduces barriers for non-technical users

Installation and launch completed within 10 minutes


Environmental Requirements

Hardware Requirements:

Minimum: 2GB RAM, 500MB disk space, 1GHz dual-core CPU

Recommended: 4GB RAM, 1GB disk space, 2GHz quad-core CPU

Software Requirements:

Operating System: Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)

Python: Version 3.8 or higher

Database: SQLite 3.7+

Deployment Requirements:

Development: Local uvicorn server on localhost:8000

Production: ASGI-compatible server (uvicorn, gunicorn)

Database: File-based SQLite (momentum.db)

Scalability Considerations:

API can run multiple worker processes

Database can migrate to PostgreSQL/MySQL for multi-user scenarios

Stateless design enables horizontal scaling


Usability Requirements

Accessibility

Colour and contrast

Specifics

All informational colour pairs must meet WCAG 2.1 contrast ratios: at least 4.5:1 for normal text and 3:1 for large text/icons. (World Wide Web Consortium, 2025) Provide a colourblind-safe palette option (deuteranopia/protanopia/tritanopia safe) and ensure graphs can be read without colour alone (use patterns, shapes, or icons). Implement a high-contrast mode. (World Wide Web Consortium, 2025)

Acceptance Criteria

All text and icons meet the required contrast ratios. Colourblind-safe palette is available and testable. High-contrast mode can be toggled and preserves readability.

Colourblind support

Specifics

Avoid using red/green as the sole differentiator. Provide shape/icon overlays and tooltips. Provide a toggle to preview UI using common colour-blind filters for validation.

Acceptance Criteria

Colourblind filters correctly display all UI elements without reliance on colour alone. Tooltips and overlays convey the same information as colour cues.

Text & scaling

Specifics

Support UI scaling (100% / 125% / 150%) and a minimum font size option. Ensure dynamic resizing of panels preserves usability.

Acceptance Criteria

UI remains fully usable at all supported scaling levels. No content overlaps or truncation occurs.

Keyboard and input

Specifics

Arrow keys move focus. Enter activates the focused item. Escape returns to the previous screen. Tab and Shift Tab cycle focus. All focusable elements display an outline. Spacebar toggles pause or resume. A increases push intensity. Z decreases push intensity. X toggles overtaking aggression mode. R restarts the race when paused and after a confirmation dialogue. All race controls must be remappable. Conflict detection must prevent duplicate bindings. Remapped bindings must persist across sessions.

Acceptance Criteria

The full interface must be operable using keyboard only. Spacebar toggles pause unless remapped. Remapped bindings take effect immediately. All focusable elements show a visible outline during keyboard navigation.

Performance

Frame rate targets

Specifics

Target GUI/simulation visual update rate: 30 FPS. Minimum acceptable visual responsiveness: 15 FPS during heavy load. Simulation logic can run decoupled from rendering, logic ticks target 30 ticks/sec.

Acceptance Criteria

GUI maintains target frame rate under normal load. Low-fidelity mode maintains minimum responsiveness under heavy load.

Responsiveness

Specifics

UI actions (menu navigation, opening panels) respond within 150–300 ms. Long-running tasks run as background jobs with progress indicators.

Acceptance Criteria

All UI interactions respond within specified limits. Background tasks do not block the UI.

Resource usage

Specifics

Provide a low-memory mode that reduces telemetry retention and drops non-essential animations.

Acceptance Criteria

Low-memory mode is functional and maintains core usability.

Readability

Clear language

Specifics

Use plain English for labels, tooltips, and help text.

Acceptance Criteria

All UI text is understandable by users without technical background.

Tooltips and help

Specifics

All non-trivial controls must have explanatory tooltips and an optional in-app short tutorial.

Acceptance Criteria

Tooltips provide sufficient context. Tutorial covers all non-obvious controls.

Localisation

Specifics

Design UI strings for easy translation. Support UTF-8 locales and date/currency formatting.

Acceptance Criteria

All UI text can be translated without breaking layouts. Locale-specific formatting displays correctly.


Design & Architecture

Current

Future

UC-21: Create New Driver



Scope

Generate or recycle driver profiles to expand the hireable pool.

Description

The system maintains an adequate pool of available drivers through generation and recycling of retired drivers.

Actors

System - executes driver pool maintenance.

Admin - may trigger manual generation.

Flow Description

Precondition

Pool size is below threshold or manual request received.

Activation

Starts when pool maintenance is triggered or manually requested.

Main Flow

The system checks if recycling retired drivers is viable.

If recycled drivers are insufficient, new drivers are generated with random attributes.

Generated drivers are validated for uniqueness and data consistency.

New drivers are marked as available in the hireable pool.

Flow ends when drivers are added to the available pool.

Exceptional Flow E1

Driver generation fails.

System logs error and retries or uses cached pool.

Flow continues with fallback.

Termination

Driver pool is expanded; generation completes.

UC-22: Create New Staff Member

Scope

Generate or recycle staff to expand the hireable pool.

Description

The system maintains an adequate pool of available staff through generation and recycling.

Actors

System - executes staff pool maintenance.

Flow Description

Precondition

Pool size is below threshold.

Activation

Starts when pool maintenance is triggered.

Main Flow

New staff members are generated with assigned roles and attributes.

Staff are validated for data consistency.

Staff are marked as available for hiring.

Flow ends when staff are added to available pool.

Termination

Staff pool is expanded.

UC-25: Update Track Characteristics 



Scope

Modify track parameters for balancing (admin/future feature).

Description

Update track configuration attributes via admin tools.

Actors

Admin - updates track records.

Flow Description

Precondition

Track exists and is editable.

Activation

Starts when updates are submitted.

Main Flow

Track changes are validated.

Track record is updated.

Flow ends when changes are persisted.

Termination

Track record is updated.

Note: Player-facing track modification is deferred to future design.

UC-26: Delete Track 



Scope

Remove track records 

Description

Delete or archive track records from the system.

Actors

Admin - deletes or archives tracks.

Flow Description

Precondition

Admin authorized; track eligible for deletion.

Activation

Starts when deletion is requested.

Main Flow

System checks for scheduled races using the track.

If none or admin confirms, track is deleted or archived.

Flow ends when track is removed.

Termination

Track is deleted or archived.

UC-28: Update Driver Appearance 



Scope

Modify driver cosmetic appearance (helmets, suits, faces) - deferred to future design.

Description

Player uploads appearance assets and customizations for cosmetic display.

Actors

Player - uploads appearance assets.

Flow Description

Precondition

Player owns driver; appearance system available.

Activation

Starts when appearance upload is submitted.

Main Flow

Assets are validated for format and size.

Appearance record is updated or created.

Flow ends when appearance is persisted.

Termination

Appearance updated for display.

Note: Player-facing driver appearance customization (faces, helmets, suits) is deferred to future design. Current delivery focuses on core gameplay mechanics.

UC-29: Update Team Branding 



Scope

Modify team visual branding assets (logos, colours)

Description

Player uploads team branding assets for display in menus and during races.

Actors

Player - uploads branding assets.

Flow Description

Precondition

Player owns team; asset storage available.

Activation

Starts when branding upload is submitted.

Main Flow

Assets are validated.

Branding record is updated.

Flow ends when branding is persisted.

Termination

Team branding updated for display.

Note: Player-facing team branding customization (logos, menu colours) is deferred to future design. Current delivery uses system-generated team livery in race visualization only.


Implementation

Reliability, Weibull distribution

The Concise Guide to Weibull Distribution



Track closure, Tikhonov regularisation and total least squares.

P:TEXSIMAX -1 43 43

Issues


Graphical User Interface (GUI)

Main Menu

Starting Page



Setup Screen



Race Screen

Pre-Race – Full Track Camera



Mid Race – Follow Car Camera




Testing

Test Plan

The testing work for Momentum was organised at management level around the 29119 structure. The scope covered the core simulation, database integrity, API and workflow integration, accessibility checks, performance checks, and the use-case coverage needed to support release decisions. The main objective was to confirm that the system behaves correctly, remains stable under repeat use, and produces evidence that can be traced back to the implemented tests. The strategy combined unit, integration, performance, accessibility, and end-to-end checks using pytest, SQLite test fixtures, simulation harnesses, and GUI smoke checks. The environment for the latest run was Windows with Python 3.13, pytest, and the project’s SQLite-backed test fixtures. The latest execution was run on 2026-05-04 as part of the final validation cycle. The main risks tracked in this phase were unregistered custom pytest markers, isolated skipped tests, and the usual possibility of state-related regressions in a simulation project where persistence and workflow logic are tightly connected.

Test Case Specification

The test case specification was built from the implemented pytest suite and mapped to the behaviours that matter most in the system. Representative cases included database integrity checks for driver-team links, unique track handling, driver attribute persistence, championship cascade behaviour, and race-result consistency. Performance cases covered single-race simulation timing, batch simulation throughput, query timing, bulk create speed, and engine initialisation. Statistical validation cases checked whether skill, seed, track surface, and race length produce plausible outcomes. Additional coverage included API contracts, championship flow, database round-trips, GUI smoke checks, accessibility checks, schema validation, and use-case coverage. Each case was written to state what it checks, the method used, and the expected result, so the test design remains traceable and easy to audit.

Test Execution Log

The latest execution log is the command `python -m pytest -q`, run on 2026-05-04. The suite collected 112 tests and completed with 111 passed, 1 skipped, and 0 failed in 86.41 seconds. The skipped test was isolated to an event-schema emission case, while the rest of the suite completed successfully across accessibility, database integrity, discipline edge cases, API contracts, championship flow, database integration, performance, statistical validation, GUI smoke, and use-case coverage. The only warnings reported were related to unregistered custom pytest markers, which did not affect the pass/fail outcome.

Test Completion Report

The final summary from the latest cycle is positive: the implemented test suite passed with no failures and only one skipped test. The defect overview for this cycle is therefore limited; no active test-breaking defects were exposed by the run, although the custom marker warnings should be cleaned up to keep the test configuration tidy. From a release-readiness perspective, the core system is in a strong state for presentation because the major functional, integration, performance, and validation checks all passed. The remaining risk is mainly procedural rather than functional, which means the current build is suitable for release presentation with the skipped case and marker warnings recorded as minor follow-up items rather than blockers.


Evaluation

Evaluation was carried out iteratively throughout development. The core simulation and progression behaviours are stable, while user-facing quality checks still require deeper formal measurement.

Conclusions

Momentum meets its core objective as a stable multi-discipline simulation system with reliable progression and persistence. It should be presented as a strong implemented core with clearly defined improvement areas.

Further Development or Research

Future work should deepen measurable user-experience validation, extend analytical race features, and improve deployment consistency. Research can focus on how simulation balance and event dynamics shape long-term realism and engagement.


Bibliography

Faker Contributors, 2026. Faker Documentation. [Online] 
Available at: https://faker.readthedocs.io/
[Accessed 26 4 2026].

FastAPI, 2026. FastAPI Documentation. [Online] 
Available at: https://fastapi.tiangolo.com/
[Accessed 26 4 2026].

Gross, A., 2026. Unidecode (PyPI project). [Online] 
Available at: https://pypi.org/project/Unidecode/
[Accessed 26 4 2026].

Kumar, S., 2026. python-dotenv Documentation. [Online] 
Available at: https://saurabh-kumar.com/python-dotenv/
[Accessed 26 4 2026].

NumPy Developers, 2026. NumPy Documentation. [Online] 
Available at: https://numpy.org/doc/
[Accessed 26 4 2026].

Pydantic, 2026. Pydantic Documentation. [Online] 
Available at: https://docs.pydantic.dev/
[Accessed 26 4 2026].

Python Pillow Team, 2026. Pillow Documentation. [Online] 
Available at: https://pillow.readthedocs.io/
[Accessed 26 4 2026].

Python Software Foundation, 2026. Black Documentation. [Online] 
Available at: https://black.readthedocs.io/
[Accessed 26 4 2026].

PyTorch Contributors, 2026. PyTorch Documentation. [Online] 
Available at: https://pytorch.org/docs/stable/
[Accessed 26 4 2026].

Riverbank Computing Limited, 2026. PyQt6 Documentation. [Online] 
Available at: https://www.riverbankcomputing.com/software/pyqt/
[Accessed 26 4 2026].

SciPy Community, 2026. SciPy Documentation. [Online] 
Available at: https://docs.scipy.org/doc/scipy/
[Accessed 26 4 2026].

SQLite Consortium, 2026. SQLite Documentation. [Online] 
Available at: https://www.sqlite.org/docs.html
[Accessed 26 4 2026].

Uvicorn, 2026. Uvicorn Documentation. [Online] 
Available at: https://www.uvicorn.org/
[Accessed 26 4 2026].

World Wide Web Consortium, 2025. WCAG 2.1 Understanding Docs. [Online] 
Available at: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
[Accessed 8 December 2025].


Appendices

Project Proposal



National College of Ireland

Project Proposal

Momentum

11/12/25

Computing

Software Development

2025/2026

Eoin Andrew Fitzsimons

X23151374

X23151374@student.ncirl.ie

Objectives

Momentum aims to design and implement a prototype motorsport management simulator that captures the scale, depth, and unpredictability of real-world racing ecosystems. Unlike existing titles, which currently focus on a limited range of disciplines (e.g., Formula 1 and limited feeder systems), it will model a wide variety of racing disciplines, each with its own unique challenges and culture. For example, rally racing will feature dynamic terrain and weather, requiring teams to adapt strategies for gravel, tarmac, or snow. Endurance racing will simulate human factors such as driver fatigue, teamwork, and mechanical reliability over long events. Street racing will emphasise customisation, driver personality, and the underground culture that shapes rivalries and alliances. By capturing these distinctions, the simulator will aim to represent a more varied and context-sensitive motorsport environment, where each series presents different management challenges.

The objective is to simulate a persistent game world where events unfold across all leagues, regardless of whether the player is directly involved. By doing so, the system mirrors the emergent qualities of Football Manager, supporting diverse career trajectories that may differ across playthroughs.

A further objective is to offer a high degree of customisation. Players will be able to modify or generate new teams, drivers, and competitions. Procedural generation will be a cornerstone, enabling large-scale fictional ecosystems that feel authentic while avoiding licensing restrictions.

The project will demonstrate implementation across key areas including simulation design and AI-driven decision-making. The intended prototype will model core systems such as driver progression, economic management, league standings, and race outcomes, with a focus on achieving computational efficiency.

The project’s objective is to produce a management simulator that can serve as a foundation for future extension. It seeks to address an identified gap in current games by emphasising simulation depth and customisation, rather than prioritising graphical fidelity.


Background

My passion for motorsport spans a wide range of disciplines, from open-wheel racing to rally, endurance, and street racing. While some recent games, such as The Crew Motorfest, successfully capture the unique feel and culture of different racing series, they focus on driving experiences rather than management. Existing management games, on the other hand, tend to concentrate on a single discipline or lack the depth and variety needed to authentically represent the full spectrum of motorsport. No current title combines the breadth of racing types, the distinctiveness of each discipline, and the emergent, persistent world of a management simulation. This project seeks to address that gap by integrating the unique characteristics of multiple racing series into a single, dynamic management experience.

Having spent extensive hours in Football Manager, I have experienced the appeal of large, complex simulations that generate emergent stories. Despite having a stronger interest in Formula 1 and motorsport generally than in football, I find myself drawn more to Football Manager than to existing motorsport management titles. This reveals an important insight: the attraction lies not in the sport itself, but in the richness of the simulated world.

By comparison, current motorsport titles such as F1 Manager and Motorsport Manager are limited. Their focus is on presentation and visuals rather than world depth. The lack of customisation and the narrow scope of simulated leagues lead to repetitive experiences over time.

This project seeks to address this gap by exploring how the thematic appeal of motorsport can be combined with the systemic depth characteristic of Football Manager. The objectives outlined in Section 1.0 will be met by designing algorithms that support persistent multi-league simulation, driver development models, and financial/strategic systems. Procedural content generation will be used to overcome licensing limitations and create a fictional but believable motorsport ecosystem.


State of the Art

Current motorsport management titles include Motorsport Manager (2016) and F1 Manager (2022–2024). These games present detailed races and authentic visuals, but their simulation depth is fundamentally limited. Driver development is linear and predetermined, making long-term play predictable. Once a player has learned the optimal strategies, the outcomes become repetitive. In contrast, Football Manager maintains replayability by simulating an immense global ecosystem of leagues, players, and staff, where no two careers are the same. This difference highlights the gap between motorsport management games and the broader standard of emergent sports simulations.

Another limitation of existing motorsport titles is their lack of customisation. Players cannot easily expand leagues, create fictional scenarios, or reshape the competitive environment. The games are tightly constrained by licensing agreements and static structures, which prevents the freedom that makes Football Manager engaging. Furthermore, the game worlds are small in scale, restricted to a handful of categories such as Formula 1 or Formula 2, with little simulation occurring outside the top tiers. By comparison, Football Manager tracks hundreds of leagues and thousands of clubs across multiple nations, with events unfolding regardless of direct player involvement.

This project aims to distinguish itself by adopting that philosophy. The simulation will extend beyond open-wheel racing, with multiple tiers within each discipline. Every league will progress whether the player manages there or not, creating a sense of a living world. Because official licensing is not available, all teams, drivers, and championships will be procedurally created, which also allows experimentation with unique structures, rivalries, and narratives. By prioritising breadth, depth, customisation, and emergent systems, this project will investigate how principles seen in Football Manager’s large-scale simulation might be adapted to a motorsport context.

It is worth noting that some recent non-management racing games, such as The Crew Motorfest, have made significant strides in capturing the unique feel, culture, and challenges of different racing disciplines. These titles demonstrate that it is possible to authentically represent the diversity of motorsport, from rally to endurance to street racing. However, they focus on the driving experience and do not offer the persistent, emergent management simulation that is central to this project. No current management title integrates the breadth of racing types, the distinctiveness of each discipline, and a persistent simulation world. This project aims to explore how these elements can be combined within a prototype, developing a management simulator that reflects both the variety and complexity of motorsport ecosystems.


Technical Approach

Momentum is being built using agile software principles. The system is organised into three main parts: the Simulation Engine, Database Management, and the Front-End Interface. Each part works together to create a realistic and engaging motorsport management experience.

Simulation Engine

The simulation engine is the heart of the system. Its design is inspired by popular motorsport management games and research into multi-agent systems. The engine handles things like how drivers improve over time, how teams manage their finances, how races are decided, and how multiple leagues can run at once. Race results are calculated using Monte Carlo simulations, which take into account driver skills, car performance, track details, weather, and random events. The financial side uses probability-based models to reflect real-world unpredictability, such as changes in sponsorship or unexpected costs. This means, for example, that a team with less money might have to take more risks with their strategy, which can change how the whole league plays out.

Database Management

The database management system is responsible for creating and storing all the teams, drivers, tracks, and championships. It uses algorithms to generate these elements based on certain rules and probabilities, ensuring that each league is balanced and diverse. Driver traits like skill, temperament, and fatigue are set according to the needs of the league. Tracks are created with different weather, locations, and surfaces, which all affect how races play out. Team budgets and resources are also assigned by the database, helping to create a dynamic and evolving competition. The system keeps an eye on things like driver diversity and league balance, making automatic adjustments to keep the game fair and interesting. All aspects of content creation and generation are managed here, so references to procedural generation are now part of database management.

Front-End Interface

The front-end interface, built in Python, displays race data, standings, driver stats, and financial dashboards. It shows the results of simulations and AI decisions, and updates in real time as the game progresses. When users make decisions or change strategies, these are sent to the back end, which updates the league data. The interface provides instant feedback on how the league is evolving and how the AI and database management systems are affecting the game.

Iteration, Feedback, and Scalability

The development plan is broken into clear phases, with regular feedback and review. Progress is measured by tracking things like driver development, AI improvements, financial stability, and the diversity of the database-generated content. The system is designed to be modular, so new features or motorsport types can be added without having to rebuild everything. Data is stored efficiently to allow for long-term, multi-league play, making Momentum a robust and replayable motorsport management simulator.


Technical Details

Momentum uses Python for both the front-end dashboards and the back-end simulation logic and database management. The system relies on NumPy for fast calculations, Pandas for handling data, and SciPy for advanced statistics. The database uses SQLite to store all the information about drivers, teams, tracks, and championships, making it easy to save and load multi-season histories. All content creation and generation are handled by the database management system.

Race Outcome Simulation

Race results are produced by a real-time, agent-based engine. Each driver is modelled as an autonomous AI agent that makes decisions on every simulation tick, targeting a frame rate of about 30 ticks per second. Agents consider their attributes, car condition, tyre state, fuel, nearby rivals, team orders and track conditions when choosing actions such as attack, defend, overtake or conserve. Discipline specific rules are applied by the engine to reflect differences between single seater, rally, endurance and other formats. Randomness is retained for low probability events such as mechanical failures or incidents, so outcomes remain unpredictable, but most race behaviour emerges from agent interactions rather than repeated sampling. Performance sensitive results are cached where appropriate to keep leaderboards and UI queries responsive.

Driver Progression

Driver attributes like speed, consistency, aggression, adaptability, and fatigue are tracked as numbers that can change over time. How a driver develops depends on their past results, which are stored in the database. Growth and decline are modelled using probability-based functions, so each driver's career is unique. Fatigue and injuries are also tracked, with recovery periods built in, making each season different and challenging.

Data Management

All teams, drivers, tracks, and championships are created and managed by the database management system. It uses algorithms to ensure that everything is balanced and diverse, with different locations and themes for tracks and championships. Before anything is saved, the system checks that the league will be fair and interesting. This approach makes every playthrough unique and replayable, and all content generation is now part of database management.

Performance Optimisation & Integration

The Python backend uses fast, vectorised calculations and keeps frequently used data in memory for speed. League states are saved at the end of each season, so progress is never lost. The system uses JSON to keep everything in sync between the front end and database management. The design makes it easy to add new features or motorsport types in the future, without having to change the core of the game.


Special Resources Required

Hardware Requirements

Momentum's Python GUI and simulation backend have modest hardware requirements. For typical development and use:

Minimum Requirements:

CPU: Dual-core processor (e.g., Intel i3 or AMD equivalent)

RAM: 4 GB

Storage: 500 MB free disk space

GPU: Integrated graphics (no dedicated GPU required)

Display: 1366x768 resolution

Recommended Requirements:

CPU: Quad-core processor (e.g., Intel i5 or AMD Rysen 3)

RAM: 8 GB

Storage: 1 GB free disk space

GPU: Integrated or basic dedicated GPU (optional)

Display: 1920x1080 resolution

These specifications are sufficient for running and developing the Python GUI, simulation, and database management systems. Higher-end hardware is only needed if running very large-scale simulations.

Software and Libraries

The front end is built in Python, which handles all the graphics, user interface, and telemetry displays. The back end also runs on Python 3.11, using NumPy, Pandas, and SciPy for calculations and data handling. All persistent data is stored in SQLite, which is lightweight and works across platforms. This setup is enough for multi-season and multi-league play and can be upgraded to a bigger database if needed for very large simulations. SQLite also allows safe rollbacks during testing.

Optional Resources

Cloud-based virtual machines (like AWS, Azure, or GCP) can be used for large-scale testing of multi-league simulations, helping to optimise performance. Git version control is used for safe, collaborative development. Automated testing is handled by tools like GitHub Actions or GitLab CI. Since all content is generated by the database management system, there is no need for licensed assets. Optional plugins can improve telemetry displays for advanced analysis.

Summary

Together, these resources provide all the computing power, software, and support needed to run a persistent, scalable motorsport management simulator, without needing expensive enterprise solutions.


Project Plan

Project Overview

Momentum will be developed in clear, manageable phases, using agile methods. Each phase builds on the last, with milestones to track progress. The plan ensures that the core systems are working before expanding the database management system. Regular feedback and testing help refine the algorithms and keep the simulation balanced and realistic.

Requirements and Design

The first phase is about defining what the project will do, how it will be structured, and how the database management system will work. The main goals are to have realistic driver progression, dynamic race results, and persistent multi-league play, with all teams, drivers, tracks, and championships created and managed by the database system. The database will be created before the game and packaged with it, so that every player has the same starting point. Non-functional goals include making sure the system is efficient, scalable, and easy to maintain. Design documents, diagrams, and flowcharts will be created to clarify and organise the project plan. This phase also sets performance targets and database designs and defines how the Python components will communicate.

Core Simulation Engine Development

The next phase is building the simulation engine, which is the core of the project. This includes setting up league structures, how drivers improve, how finances work, and how races are decided. Driver skills, fatigue, and personality are modelled using probability-based systems. Team finances, including budgets and sponsorships, are also handled with realistic randomness. Race results are calculated using Monte Carlo simulations, considering all the important factors. Data is managed efficiently to keep the game running smoothly, even with many leagues and seasons.

Database Management

Once the simulation engine is working, the focus shifts to the database management system. This part is responsible for creating and storing all teams, drivers, tracks, and championship schedules. It uses algorithms to make sure everything is diverse and balanced, with different locations and themes. Before anything is saved, the system checks that the league will be fair and interesting. This phase also adds tools for batch creation and automatic checking of content, making sure every playthrough is unique and replayable.

Front-End Integration

The Python front end is connected to the backend to show race data, leaderboards, team dashboards, and driver stats. Updates are sent smoothly to keep the interface responsive. The user interface is tested for clarity and ease of use. Integration ensures that all changes from the simulation and database management systems are shown accurately in the game.

Iterative Testing and Refinement

Testing happens in cycles, with milestones for things like driver development, financial stability, AI variety, realistic race results, and multi-league play. Feedback from each cycle is used to improve the algorithms and keep the simulation balanced. The system is monitored to make sure rivalries, race outcomes, and league progression all feel realistic. Performance is checked and improved as needed to keep everything running smoothly.

Final Evaluation and Documentation

The final phase reviews how the system behaves, the user experience, stability, and overall performance. All code is documented, and detailed reports are created on simulation accuracy and database management. This phase makes sure that Momentum works as a complete, persistent, and scalable motorsport management simulator, meeting all the goals set out at the start.

The project plan is designed to move smoothly from design to deployment, with clear milestones and dependencies. Regular feedback and testing ensure that Momentum delivers a realistic and engaging experience, while staying easy to maintain and expand in the future.

Gantt Chart




Testing

Testing Strategy

Testing follows a layered and iterative approach: isolated logic is checked first, integrated workflows are validated next, and full-system behaviour is then reviewed under realistic conditions.

Reflective Journals

Supervision & Reflection Template 

Student Name

Eoin Fitzsimons

Student Number

X23151374

Course

Computing

Supervisor

Month: September

What? 

Came up with idea, a motorsport management simulator game, I found that all others in the sector are too shallow.

I have installed unity and activated the student plan.

I have downloaded notion to keep track of structure of the project.

I have decided to use a python backend with SQLite data storage and Unity front end

I use GitHub for version control

So What? 

That alleviated the pressure of coming up and sifting through ideas, so that was a great success, but I am still at stage one essentially as I have nothing beyond an idea currently.

It’s a direction to go in, but a large hill to tackle.

It gave me a structure to write my notes into

I have a structure in mind

I have backups if I don’t like a change I made

Now What? 

I need to come up with a proper name, a plan of attack, (which actually works as a name), and some basic branding that will improve the initial start in my opinion.

Need to figure out how to learn unity

Need to plan out my notes on the project structure.

Need to learn the languages

Plan branch paths and naming schemes

Student Signature


Supervision & Reflection Template 

Student Name

Eoin Fitzsimons

Student Number

X23151374

Course

Computing

Supervisor

Emer Thornbury

Month: October

What? 

I started building a Python prototype for my game. I began work on the team management, car development, financial management, and the race weekend structure and connected them through a basic Python GUI. The current version is only a prototype. None of the systems are fully finished, and the race simulation is not yet implemented. The main goal was to test ideas and system integration before moving to a more advanced platform.

So What? 

The prototype allowed me to experiment with the game’s logic and data flow, and to identify key challenges early. While the Python GUI is functional enough for testing, it is not intended for the final product. My main success was establishing a working foundation for the game’s systems. The biggest challenge is that the project is still at an early stage, with many features incomplete or missing.

Now What? 

Continue developing and refining the core systems in Python until the logic is solid.

Use the Python prototype as a reference and testing ground for gameplay mechanics.

Focus on implementing a real race simulation and improving system completeness before porting to Unity.

Student Signature

Eoin Fitzsimons

Supervision & Reflection Template 

Student Name

Eoin

Student Number

X23151374

Course

Computing

Supervisor

Month: November

What? 

Reflect on what has happened in your project this month?

took a break to work on other assignments

proposal, CRUD use cases, and feature priority 

mostly planning stuff

So What? 

Consider what that meant for your project progress.  What were your successes? What challenges still remain? 

Certainly helped give a direction with use cases and priorities, realised initial proposal was just plain stupid, overly ambitious, and unrealistic for a college project.

Now What? 

What can you do to address outstanding challenges? 

Get started on coding around use cases

Student Signature


Supervision & Reflection Template 

Student Name

Eoin

Student Number

X23151374

Course

Computing

Supervisor

Month: December

What? 

Reflect on what has happened in your project this month?

Built the real-time agent engine and connected it to the GUI.

Fixed a set of code warnings and cleaned up some function signatures.

Ran tests (quick checks and longer validation).

So What? 

Consider what that meant for your project progress.  What were your successes? What challenges still remain? 

The project now simulates live racing cars move continuously, and agents make per-frame decisions attack/defend/manage

This change gives visible, behaviour for demos, but some docs still describe the old Monte Carlo approach.

also found balance issues too many DNFs in long races that need tuning.

Now What? 

What can you do to address outstanding challenges? 

Rewrite the technical report and proposal to describe the agent-based approach.

Tune incident parameters to reduce DNFs 

Run GUI tests and import track data for the midpoint demo.

Student Signature



Other materials used

Any other reference material used in the project for example evaluation surveys etc.