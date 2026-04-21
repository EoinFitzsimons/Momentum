## Design and Architecture

### Current

Momentum
is built on Python 3.13 and uses PyQt6 for the GUI. The architecture consists
of specialised classes that manage different aspects of the simulation. The
core simulation uses a realtime agent-based approach where drivers are
autonomous AI entities making decisions at 30 FPS based on race conditions and
their attributes.

#### 1.1.1.1

Core Architecture Classes

The
simulation architecture can be broken down into key classes that handle
initialisation, state management, player interaction, and visual
representation.

##### 1.1.1.1.1

MomentumLauncher (Application Controller)

Location:
Momentum/Python/GUI/launcher.py

This
class manages the overall application lifecycle. It initialises the PyQt
application, manages transitions between the main menu and race windows, and
handles player configuration.

When
you start Momentum, the launcher creates a QApplication and shows the
MainMenuWindow. When the player selects a driver and starts a race it creates a
RaceWindow and connects its return signal back to the menu.

##### 1.1.1.1.2

MainMenuWindow (Player Setup)

Location:
Momentum/Python/GUI/gui_main_menu.py

This
is where players configure their race. The class loads the driver database via
DatabaseManager and presents a list of available drivers. Players select a
driver.

When
the player clicks Start Race the window emits a start_race_signal carrying a
config dictionary containing the selected driver and tuning preset.

##### 1.1.1.1.3

RaceWindow (Main Game View)

Location:
Momentum/Python/GUI/gui_race_visual.py

This
is the core gameplay class. It manages the visual track display, live car
rendering, standings table, and timing information. The RaceWindow contains
several key responsibilities:

* Track Generation: Uses
  CircuitGenerator to create a procedural racing circuit based on the track
  length. The circuit is built from straight sections and clothoid corner
  transitions and uses closure logic to complete a loop back to the start
  line.
* Race Execution: When the
  race starts the window spawns a race_runner thread that calls
  simulate_race from the race simulation API. This thread runs the
  RealtimeRaceEngine in the background and emits position updates at 30 FPS.
* Event Handling: The
  RaceWindow subscribes to position updates via EventEmitter signals. Every
  frame (30 times per second) the engine sends car positions, lap counts,
  gaps, and race status. The window updates the visual display and standings
  table based on these events.
* Player Input: The window
  captures input for pace adjustments and overtaking aggression. These
  inputs update player_overrides which the engine reads every tick to
  control the player's car.

##### 1.1.1.1.4

RealtimeRaceEngine (Simulation Core)

Location:
Momentum/Python/RaceLogic/realtime_race_engine.py

The
engine runs at 30 FPS and updates each driver's state every timestep (0.033s).
Each driver is represented by a DriverState object that tracks physical state
(position, velocity, lap), race situation (gaps, nearby cars), strategic state
(racing mode, push intensity), and component degradation (tyres, fuel).

Main
loop steps per frame:

* AI Decision Making:
  update_racing_mode decides to attack, defend, manage pace, or cruise.
  Player-controlled drivers skip AI logic and use player_overrides.
* Performance Calculation:
  Speed based on driver attributes, team capability, push intensity, tyre
  condition, fuel load, and slipstream.
* Position Update: Move
  car forward based on speed and timestep.
* Lap Detection: Detect
  crossing of start/finish, record lap times.
* Incident Checking:
  Detect collisions or incidents and log them.
* Degradation and Fatigue:
  Update tyres, fuel, and push fatigue which affect mistake probability.
* Position Emission: Emit
  position events for the GUI to render.

##### 1.1.1.1.5

DatabaseManager (Persistence Layer)

Location:
Momentum/Python/database/database_manager.py

Handles
database operations for drivers, teams, tracks, championships, races, and race
results. Uses SQLite and initialises schema on first run. The engine queries
this manager to load driver and team data and, on race completion, results can
be persisted back to the database.

##### 1.1.1.1.6

VehicleRenderer (Visual Representation)

Location:
Momentum/Python/vehicles/vehicle_appearance.py

Renders
simplified top-down car sprites using PyQt's QPainter. Livery colors are
generated deterministically by team ID.

#### 1.1.1.2

Folder Structure (current)

* Momentum/Python/GUI: UI
  code (launcher, main menu, race window, component health displays).
* Momentum/Python/RaceLogic:
  Core simulation engine and discipline modules.
* Momentum/Python/database:
  Models and manager (models.py, database_manager.py).
* Momentum/Python/services:
  Service layer including race_simulation_api.
* Momentum/Python/vehicles:
  Appearance, rendering utilities.
* Momentum/Python/api:
  FastAPI routes for headless mode.
* Momentum/Python/systems:
  Game systems (currency, staff, world state).
* Momentum/Python/scripts:
  Utilities (db generation, import, build helpers).
* Momentum/Python/tests:
  Test files.

##### 1.1.1.2.1

Data Flow and Event System

* Player starts race from
  MainMenuWindow which emits start_race_signal.
* Launcher creates
  RaceWindow and sets player driver and tuning preset.
* RaceWindow spawns
  race_runner thread that calls simulate_race.
* simulate_race creates
  RealtimeRaceEngine and runs the simulation loop.
* Engine emits position
  events at 30 FPS: RaceWindow updates visuals and standings.
* On race finish the
  engine emits race_finished with results and incident log.

##### 1.1.1.2.2

Concurrency Model

* Desktop: single process,
  main GUI thread + race_runner thread. Communication via Qt signals.
* API/headless: FastAPI
  under uvicorn, simulations run as background tasks.

#### 1.1.1.3

Design Rationale and Limitations

* SQLite for portability
  and bundling.
* PyQt6 for low-level
  rendering control and headless rendering for tests.
* Realtime agent-based
  approach for interactive races and visible AI decisions.
* Season progression and
  some save/load flows are incomplete.

### [1.1.2

Future]()

#### 1.1.2.1

Design goals

The future architecture should improve clarity and reliability without changing
the core identity of the project (desktop-first, realtime simulation, SQLite).

The goals are:

* Complete the full player
  loop: choose a driver, run a season, save progress, and continue later.
* Keep race simulation
  responsive in the GUI while allowing optional background simulation for
  non-interactive tasks.
* Make data updates safer
  and easier to trace (results, contracts, budgets, progression).
* Introduce new systems in
  small steps so the project remains testable throughout development.

#### 1.1.2.2

Planned components and responsibilities

The target architecture is based on a small number of clear services rather
than many abstract layers.

* DatabaseManager (existing):
  remains the single access point for database reads/writes.
* Race Simulation Service
  (existing): runs realtime races for GUI mode and quick simulations for
  non-visual mode.
* Career Manager (new):
  manages player profile state, season calendar progression, save/load, and
  long-term career events.
* Standings/Results Service
  (new): centralises points calculation, standings generation, and season
  summaries.
* Background Worker
  (new, lightweight): handles longer jobs (batch simulation, annual
  progression) so the UI stays responsive.

This keeps the architecture understandable: GUI calls service layer, service
layer updates data through DatabaseManager, and the worker is used only when a
task is too expensive for immediate execution.

#### 1.1.2.3

Data model additions

Only a few tables are needed to support the missing gameplay loop:

* career_profiles: stores
  current player career state (season, team, finances, settings).
* career_events: append-only
  log for major actions (signings, retirements, season transitions).
* contracts: contract
  lifecycle history for drivers and staff.
* jobs: queued background
  operations with status/result metadata.
* standings_snapshots:
  optional cached standings to speed up UI loading.

These additions are intentionally minimal and align with existing entities
(drivers, teams, championships, races, results).

#### 1.1.2.4

Migration and phases

Implementation is split into practical phases with a usable outcome at each
step:

* Phase 1: Career state
  foundation. Add career_profiles and career_events, with save/load endpoints
  and GUI integration.
* Phase 2: Season automation.
  Add standings service and basic season progression (advance round, complete
  season, create next season).
* Phase 3: Contracts and
  finance hardening. Add contract history and validation rules for budget and
  salary constraints.
* Phase 4: Background
  processing and optimisation. Add lightweight job worker for longer tasks,
  then profile performance and stabilise tests.

Risk is reduced by keeping each phase independently testable and backwards
compatible with the current race flow.
