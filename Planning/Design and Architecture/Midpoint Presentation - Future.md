
Planned Architecture - Career Mode Aligned to Use Cases

Purpose

This document describes the planned architecture for Momentum with Career Mode as the primary gameplay flow. It is rewritten to explicitly support the 29 use cases defined in Planning/UseCases/All_Use_Cases_Detailed.md. Each component below maps to the use-cases it implements or supports.

Design goals (aligned to use cases)

- Support full career lifecycle (UC-1, UC-3, UC-5, UC-10, UC-19): load drivers, run races, persist results, and progress seasons.
- Provide reliable management APIs for teams, drivers, staff, tracks, and championships (UC-1..UC-15, UC-21..UC-26, UC-28..UC-29).
- Keep interactive realtime simulation responsive while enabling headless batch jobs (UC-3, UC-6, UC-9, UC-16, UC-18).
- Provide durable persistence and audit trails for saves, contracts, and career events (UC-2, UC-4, UC-11, UC-12).

Core components and responsibility mapping

- Database Manager (existing)
	- Role: single canonical data access layer (reads/writes drivers, teams, tracks, races, race_results, championships, staff_members).
	- Use cases: UC-1, UC-2, UC-4, UC-5, UC-11, UC-15, UC-21, UC-24.

- Career Manager (new service/library)
	- Role: manage player profiles, calendar progression, contracts lifecycle, career events, and save/load operations.
	- Use cases: UC-3 (applies results to career), UC-5 (season/standings integration), UC-10 (create championship on rollover), UC-12 (create team via career flows), UC-16, UC-18.

- Race Simulation Service (existing engine, formalised interface)
	- Role: host realtime ticked simulations (30 FPS) for interactive races and expose a headless quick-sim API for batch runs.
	- Use cases: UC-3 (create results), UC-8 (race scheduling -> simulation), UC-9 (status transitions during simulation), UC-27 (staff modifiers applied during sim).

- Job Queue & Worker (new)
	- Role: durable job table and worker process to run long tasks: quick-sim batches, season ticks, standings recalculation, driver/staff generation.
	- Use cases: UC-6 (update standings), UC-10 (season rollover jobs), UC-19 (batch driver progression), UC-21/UC-22 (generation jobs), UC-2/UC-24 import jobs.

- Standings Service (new or library function)
	- Role: compute and persist championship standings based on race_results and championships.points_system.
	- Use cases: UC-5, UC-6.

- API Layer (FastAPI existing)
	- Role: expose endpoints for GUI and admin tools (career endpoints, job control, quick-sim trigger, read/write operations).
	- Use cases: UC-1..UC-29 (serves the full API surface).

- Storage Service (existing or simple file storage)
	- Role: store non-relational assets: liveries, branding, and custom tracks (UC-24, UC-28, UC-29).

Schema alignment and minimal additions

The repository schema already implements key domain tables (drivers, teams, tracks, races, race_results, championships, staff_members). To fully support the use cases, add the following minimal tables and map them to use cases:

- career_profiles (UC-5, UC-10, UC-12)
	- Purpose: store player profile state (profile_id, player_name, primary_driver_id, balance, settings, last_saved_at).

- career_events (UC-3, UC-16, UC-18)
	- Purpose: immutable audit trail of career-significant actions (profile_id, event_type, payload_json, created_at).

- contracts (UC-16, UC-18)
	- Purpose: record driver/staff contracts historically (driver_id/staff_id, team_id, start_date, end_date, salary, clauses, status).

- jobs (UC-6, UC-10, UC-19, UC-21)
	- Purpose: durable queue for background tasks - fields: id, type, payload_json, status, created_at, started_at, finished_at, result_ref, error_message.

- standings (UC-5, UC-6)
	- Purpose: precomputed standings per championship/season for fast reads and historical snapshots.

Why these additions matter (use-case mapping)

- Career profiles and career events provide the data shape needed for UC-5 (career view), UC-3 (apply results to career), UC-16/UC-18 (contract lifecycle), and UC-19 (seasonal progression and driver ageing).
- Contracts as a first-class table satisfy UC-16/UC-18 (sign/renew/terminate) with historical records for auditing and conflict detection.
- Jobs and a worker process let background work implement UC-6 (async standings), UC-10 (auto championship creation), UC-21/22 (generator jobs), and UC-19 (batch updates) safely without blocking GUI threads.

Detailed use-case mapping (high level)

- UC-1 (Read Driver Details): Database Manager exposes get_driver(id) - driver attributes read directly from drivers table and passed to Race Simulation Service for agent initialization.
- UC-2 (Read Race Configuration): tracks table used by Database Manager to build TrackMap and simulation parameters.
- UC-3/UC-4 (Create/Read Race Results): Race Simulation Service produces results which are validated and inserted into race_results. GUI and Database Manager read historical results via get_race_results.
- UC-5/UC-6 (Championship & Standings): Standings Service reads race_results and championships.points_system to compute standings; results persisted to standings table or computed on demand.
- UC-7..UC-9, UC-10 (Event lifecycle & scheduling): Career Manager and Job Worker coordinate calendar creation, event insertion (races), and status transitions. Admin and automated systems use API endpoints for these actions.
- UC-11..UC-16 (Teams, Contracts, Transfers): Team management uses teams, contracts, drivers and jobs to validate budgets, persist contract records, and apply roster changes.
- UC-17..UC-18 (Staff pool and contracts): staff_members table plus contracts record staff assignment and salary impacts on team budgets.
- UC-19..UC-23 (generation, progression, deletion): Jobs trigger generator or batch processes to update drivers/staff, create new entities, or archive/delete championships and tracks.
- UC-24..UC-26 (Track CRUD): API endpoints for creating, updating and deleting tracks that validate geometry and enforce schedule constraints.
- UC-27 (Staff modifiers): Simulation Service queries aggregated staff modifiers via Database Manager and applies modifiers during simulation ticks.
- UC-28..UC-29 (Appearance & Branding): Storage Service plus metadata fields in drivers/teams support cosmetic updates; Database Manager returns asset references to GUI.

Concurrency and reliability notes (practical constraints)

- Keep GUI responsive: run all heavy tasks (quick-sim, season tick, standings recalculation, generator) in Job Worker processes. Use jobs table for durable handoff.
- SQLite caveat: keep transactions short; for heavy concurrent workers consider an eventual migration to Postgres for multi-worker scaling.
- Auditability: write career_events for any operation that updates player profile state to enable save/restore and debugging.

Migration and phased implementation mapped to use cases

Phase 1 - API + persistence alignment (low friction, immediate impact)
	- Add career_profiles and career_events. Implement API endpoints for UC-1..UC-5 and UC-7..UC-9 so GUI can display career and event data.

Phase 2 - Jobs and background processing (medium effort)
	- Add jobs table and single-worker implementation. Implement quick-sim and standings recalculation jobs to satisfy UC-6, UC-10, UC-19.

Phase 3 - Contracts, staff flows and UI (feature-complete)
	- Add contracts table and staff/finance UI flows. Implement UC-11..UC-18 features including contract conflict checks and budget validation.

Phase 4 - Polishing & scaling
	- Add standings snapshots, optional simulation_runs aggregation, tests, logging, and admin tooling for UC-21..UC-29. Evaluate DB scaling if multi-worker performance requires it.

Acceptance criteria (mapped)

- UC-1..UC-5: GUI can load driver/track/championship data and display a career dashboard.
- UC-3/UC-4/UC-6: Race results are produced, persisted to race_results, and standings recalc jobs produce consistent standings.
- UC-10/UC-19/UC-21: Season rollover and batch progression operations complete via jobs and update profiles and drivers as expected.

Next steps I can perform now

1. Add SQL snippets to Momentum/Python/database/models.py SCHEMA_SQL for career_profiles, career_events, contracts, and jobs, following the project's schema style.
2. Scaffold a minimal Momentum/Python/tools/worker.py that reads the jobs table, runs a trivial job (standings recalculation or quick-sim placeholder), and updates job status.
3. Create a Mermaid target_architecture.md diagram that visualises the Career Manager, Job Worker, Race Simulation Service, Database, and GUI interactions mapped to the UC groups.

Tell me which of the three tasks above you want me to do first and I'll implement it and run a quick verification where possible.


Planned Architecture

Overview

This document describes the planned (target) architecture for the final Momentum project. It focuses on structural changes and new services required to support the full set of use cases, reliable persistence of results, batch simulations for championships, and a clear separation between interactive UI and headless processing.

Design goals

- Full coverage of core use cases: driver and track management, event creation, race execution, results persistence, and standings calculation.
- Support both interactive realtime races and headless batch/quick simulations with repeatable outcomes.
- Minimise coupling between GUI and simulation so backend services can run independently for automation and analysis.
- Keep deployment and tooling simple: prefer small additions to the existing SQLite-based system, but design migration paths to a server database if needed.

High-level components (target)

- Frontend (PyQt6 GUI): unchanged in purpose; becomes a consumer of backend services and job status rather than the only runtime for the simulation.

- Race Simulation Service: a headless service that can run either the realtime engine or a lower-fidelity quick-sim evaluator. This service exposes a clean API and can be executed by the GUI or by background workers.

- Job Queue and Worker(s): a simple job table and worker that executes long-running or batched tasks (quick-sim batches, standings recalculation, import tasks). Jobs are tracked and can be retried.

- Standings Service: a dedicated component to compute championship standings from stored race results. Runs as a callable library and as a background job.

- Persistence Layer: existing DatabaseManager remains the canonical data access layer. New tables are added for jobs, race_results, standings, and optional aggregated simulation_runs.

- Admin / API Layer: FastAPI endpoints for administrative tasks and batch triggers. Examples: POST /simulate/quick, POST /jobs, GET /jobs/{id}, POST /standings/recalculate, GET /race_results/{id}.

Data model (additions)

- race_results: stores final classification per race (race_id, driver_id, position, total_time, best_lap, dnf_reason, incident_log). Used for UC-3 and UC-4.
- standings: stores computed championship standings (championship_id, driver_id/team_id, points, version, computed_at).
- jobs: stores queued tasks (id, type, payload JSON, status, created_at, started_at, finished_at, result_location, error_message).
- simulation_runs: optional summary table for batched quick-sim iterations (seed, winner_id, stats) to reduce storage needs for full telemetry.

APIs and interactions

- Interactive flow: GUI requests driver and track data from DatabaseManager, spawns a realtime run via Race Simulation Service (local call or API), subscribes to position updates for live rendering. At race finish the engine triggers persistence of a race_results row.

- Headless batch flow: Admin or GUI calls POST /simulate/quick with parameters (iterations, mode, seed range). The API enqueues a quick_sim job. Worker consumes the job, runs iterations, writes simulation_runs summaries and optional telemetry, and marks the job complete.

- Standings flow: After results persist, a recalculate_standings job can be enqueued automatically or invoked manually. Worker runs Standings Service and updates the standings table.

Migration plan (phased)

Phase 1 - Results persistence and simple APIs (priority)

- Implement race_results schema and add engine code to persist final results atomically at race end.
- Add GET endpoints to read results and championships for the GUI.

Phase 2 - Jobs and Standings Service

- Implement jobs table and a single-worker process. Create the Standings Service and a recalculate_standings job type.

Phase 3 - Quick-sim evaluator

- Implement quick-sim mode: a lower-fidelity evaluator that can run many iterations fast and produce aggregated summaries. Expose POST /simulate/quick API and worker handling.

Phase 4 - UI and polish

- Add a simple Jobs view in the GUI to monitor background work. Harden logging, retries, and tests.

Acceptance criteria

- The engine persists race_results reliably on race completion. A local test should run a short race and show the race_results row.
- Standings recalculation job produces a standings row matching a manual example computation.
- Quick-sim job can run 100 iterations on a developer machine within the target timeframe (adjustable). Summary statistics are available through the API.

Risks and mitigations

- SQLite concurrency limits: use short transactions and consider moving to Postgres if write contention grows. Keep job worker single-threaded or queue writes.
- Fidelity trade-offs: document differences between quick-sim and realtime; provide both modes.

Next steps (immediate)

1. Replace the race_results table in schema and add an integration test that runs a short race to assert persistence.
2. Implement a minimal jobs table and a trivial worker that can consume and log jobs.
3. Implement the Standings Service and expose POST /standings/recalculate to enqueue work.

Diagrams and artifacts

Add a target architecture diagram to Planning/Design and Architecture/Diagrams named target_architecture.md and a draw.io source target_architecture.drawio. Keep diagrams simple: show GUI, Race Simulation Service, Job Worker, Standings Service, and SQLite.

If you want, I will now replace this file with a mermaid target architecture diagram, or add example SQL for race_results and jobs plus a small worker skeleton in Momentum/Python/tools/ for a smoke test.

Schema alignment and glaring omissions

Repository alignment summary

- What already exists: the codebase already includes full definitions for drivers, teams, tracks, championships, races, race_results, and staff_members in Momentum/Python/database/models.py and the SCHEMA_SQL. These tables cover the majority of data the Career Manager will need.
- Existing career-relevant fields: drivers already includes current_team_id, previous_teams (JSON/text), contract_length, and salary fields. race_results is implemented and will be the canonical persisted race outcome. The championships table includes points_system suitable for standings.

Glaring omissions (minimal, high-impact additions)

- career_profiles (recommended): not present. Needed to model player save state independent of driver rows - stores profile metadata, active driver reference, balance and high-level progression state.
- career_events (recommended): not present. An audit trail for career actions (contract signed, race applied, staff hire/fire) - important for save/restore, debugging, and analytics.
- contracts (recommended): while drivers have contract fields, a dedicated contracts table is required to represent contract history, clauses, and team-driver timelines.
- jobs (recommended): absent. Add a durable jobs table to queue background work (quick-sim, standings recalculation, season advancement). This keeps the GUI responsive and makes batch work retryable.
- standings (optional but useful): pre-computed standings per championship/season improve read performance for the GUI and support historical queries.
- simulation_runs (optional): summary table for aggregated quick-sim outputs if you prefer storing summaries instead of full telemetry.

How the plan will change to match the schema

- Reuse existing tables where sensible: use drivers.current_team_id and drivers.previous_teams for current assignment/history rather than inventing a separate unlocking mechanism.
- Persist race outcomes to the existing race_results table and use championships.points_system to compute points; add standings only if query performance or historical snapshots are required.
- Add minimal new tables (career_profiles, career_events, jobs, contracts) to support Career Mode lifecycle, while keeping the rest of the schema unchanged.

Recommended next tasks (low friction)

1. Add career_profiles and career_events SQL to SCHEMA_SQL so profiles and audit events are available for the Career Manager.
2. Add a small jobs table and scaffold a single-worker Momentum/Python/tools/worker.py that consumes jobs to demonstrate season advancement and quick-sim handling.
3. Keep contracts lightweight initially (driver_id, team_id, start_date, end_date, salary, status) and backfill from existing drivers.contract_length and drivers.salary where appropriate.

Status

- I updated the plan to explicitly align with existing schema and listed the minimal, glaring omissions above.
- Next, if you confirm, I'll either add the SQL snippets to Momentum/Python/database/models.py or scaffold the worker. Tell me which you prefer next and I'll proceed.
