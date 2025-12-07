# Design and Architecture

## Current

Momentum is built on Python 3.13 and uses PyQt6 for the GUI. The architecture consists of specialized classes that manage different aspects of the simulation. The core simulation uses a realtime agent-based approach where drivers are autonomous AI entities making decisions at 30 FPS based on race conditions and their attributes.

### Core Architecture Classes

The simulation architecture can be broken down into key classes that handle initialization, state management, player interaction, and visual representation.

#### MomentumLauncher (Application Controller)

Location: `Momentum/Python/GUI/launcher.py`

This class manages the overall application lifecycle. It initializes the PyQt application, manages transitions between the main menu and race windows, and handles player configuration.

When you start Momentum the launcher creates a QApplication and shows the MainMenuWindow. When the player selects a driver and starts a race it creates a RaceWindow and connects its return signal back to the menu.

#### MainMenuWindow (Player Setup)

Location: `Momentum/Python/GUI/gui_main_menu.py`

This is where players configure their race. The class loads the driver database via `DatabaseManager` and presents a list of available drivers. Players select a driver and set their pace and overtaking aggression using sliders. These settings become player overrides that affect how the AI controls the player's car during the race.

When the player clicks Start Race the window emits a `start_race_signal` carrying a config dictionary containing the selected driver and tuning preset.

#### RaceWindow (Main Game View)

Location: `Momentum/Python/GUI/gui_race_visual.py`

This is the core gameplay class. It manages the visual track display, live car rendering, standings table, and timing information. The RaceWindow contains several key responsibilities:

- Track Generation: Uses `CircuitGenerator` to create a procedural racing circuit based on the track length. The circuit is built from straight sections and clothoid corner transitions and uses closure logic to complete a loop back to the start line.
- Race Execution: When the race starts the window spawns a `race_runner` thread that calls `simulate_race` from the race simulation API. This thread runs the `RealtimeRaceEngine` in the background and emits position updates at 30 FPS.
- Event Handling: The RaceWindow subscribes to position updates via `EventEmitter` signals. Every frame (30 times per second) the engine sends car positions, lap counts, gaps, and race status. The window updates the visual display and standings table based on these events.
- Player Input: The window captures keyboard input for pace adjustments and overtaking aggression. These inputs update `player_overrides` which the engine reads every tick to control the player's car.

#### RealtimeRaceEngine (Simulation Core)

Location: `Momentum/Python/RaceLogic/realtime_race_engine.py`

The engine runs at 30 FPS and updates each driver's state every timestep (0.033s). Each driver is represented by a `DriverState` object that tracks physical state (position, velocity, lap), race situation (gaps, nearby cars), strategic state (racing mode, push intensity), and component degradation (tires, fuel).

Main loop steps per frame:

- AI Decision Making: `update_racing_mode` decides to attack, defend, manage pace, or cruise. Player-controlled drivers skip AI logic and use `player_overrides`.
- Performance Calculation: Speed based on driver attributes, team capability, push intensity, tire condition, fuel load, and slipstream.
- Position Update: Move car forward based on speed and timestep.
- Lap Detection: Detect crossing of start/finish; record lap times.
- Incident Checking: Detect collisions or incidents and log them.
- Degradation and Fatigue: Update tires, fuel, and push fatigue which affect mistake probability.
- Position Emission: Emit position events for the GUI to render.

#### DatabaseManager (Persistence Layer)

Location: `Momentum/Python/database/database_manager.py`

Handles database operations for drivers, teams, tracks, championships, races, and race results. Uses SQLite and initializes schema on first run. The engine queries this manager to load driver and team data and, on race completion, results can be persisted back to the database.

#### VehicleRenderer (Visual Representation)

Location: `Momentum/Python/vehicles/vehicle_appearance.py`

Renders simplified top-down car sprites using PyQt's `QPainter`. Livery colors are generated deterministically by team ID.

### Folder Structure (current)

- `Momentum/Python/GUI`: UI code (launcher, main menu, race window, component health displays).
- `Momentum/Python/RaceLogic`: Core simulation engine and discipline modules.
- `Momentum/Python/database`: Models and manager (`models.py`, `database_manager.py`).
- `Momentum/Python/services`: Service layer including `race_simulation_api`.
- `Momentum/Python/vehicles`: Appearance, rendering utilities.
- `Momentum/Python/api`: FastAPI routes for headless mode.
- `Momentum/Python/systems`: Game systems (currency, staff, world state).
- `Momentum/Python/scripts`: Utilities (db generation, import, build helpers).
- `Momentum/Python/tests`: Test files.

### Data Flow and Event System

- Player starts race from MainMenuWindow which emits `start_race_signal`.
- Launcher creates RaceWindow and sets player driver and tuning preset.
- RaceWindow spawns `race_runner` thread that calls `simulate_race`.
- `simulate_race` creates `RealtimeRaceEngine` and runs the simulation loop.
- Engine emits position events at 30 FPS; RaceWindow updates visuals and standings.
- On race finish the engine emits `race_finished` with results and incident log.

### Concurrency Model

- Desktop: single process, main GUI thread + `race_runner` thread. Communication via Qt signals.
- API/headless: FastAPI under uvicorn; simulations run as background tasks.

### Design Rationale and Limitations

- SQLite for portability and bundling.
- PyQt6 for low-level rendering control and headless rendering for tests.
- Realtime agent-based approach for interactive races and visible AI decisions.
- Season progression and some save/load flows are incomplete.

---

## Future

### Purpose

This document describes the planned architecture for Momentum with Career Mode as the primary gameplay flow. It is rewritten to explicitly support the 29 use cases defined in `Planning/UseCases/All_Use_Cases_Detailed.md`.

### Design goals (aligned to use cases)

- Support full career lifecycle (UC-1, UC-3, UC-5, UC-10, UC-19): load drivers, run races, persist results, and progress seasons.
- Provide reliable management APIs for teams, drivers, staff, tracks, and championships (UC-1..UC-15, UC-21..UC-26, UC-28..UC-29).
- Keep interactive realtime simulation responsive while enabling headless batch jobs (UC-3, UC-6, UC-9, UC-16, UC-18).
- Provide durable persistence and audit trails for saves, contracts, and career events (UC-2, UC-4, UC-11, UC-12).

### Core components and responsibility mapping

- Database Manager (existing)

  - Role: canonical data access layer for domain tables.
  - Use cases: UC-1, UC-2, UC-4, UC-5, UC-11, UC-15, UC-21, UC-24.
- Career Manager (new)

  - Role: manage player profiles, calendar progression, contracts lifecycle, career events, and save/load operations.
  - Use cases: UC-3, UC-5, UC-10, UC-12, UC-16, UC-18.
- Race Simulation Service (existing engine)

  - Role: host realtime ticked simulations and provide headless quick-sim.
  - Use cases: UC-3, UC-8, UC-9, UC-27.
- Job Queue & Worker (new)

  - Role: durable job table and worker process for background tasks.
  - Use cases: UC-6, UC-10, UC-19, UC-21/UC-22, UC-2/UC-24.
- Standings Service (new or library)

  - Role: compute and persist championship standings.
  - Use cases: UC-5, UC-6.
- API Layer (FastAPI existing)

  - Role: expose endpoints for GUI and admin tools.
  - Use cases: UC-1..UC-29.
- Storage Service (existing or simple file storage)

  - Role: store non-relational assets: liveries, branding, and custom tracks (UC-24, UC-28, UC-29).

### Schema alignment and minimal additions

- `career_profiles` (UC-5, UC-10, UC-12): profile state store.
- `career_events` (UC-3, UC-16, UC-18): immutable audit trail.
- `contracts` (UC-16, UC-18): contract history.
- `jobs` (UC-6, UC-10, UC-19, UC-21): durable background queue.
- `standings` (UC-5, UC-6): precomputed standings snapshots.

### Migration and phases

- Phase 1: `career_profiles` and `career_events` + basic API.
- Phase 2: `jobs` and single-worker quick-sim/standings.
- Phase 3: `contracts`, staff and finance flows.
- Phase 4: `standings` snapshots, simulation_runs, tests, and DB scale evaluation.

### Next steps

1. Add `SCHEMA_SQL` snippets for the recommended tables.
2. Scaffold a `Momentum/Python/tools/worker.py` to consume `jobs` and run a placeholder job.
3. Create a Mermaid `target_architecture.md` diagram mapping components to use-case groups.
