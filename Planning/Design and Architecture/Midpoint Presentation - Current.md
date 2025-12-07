# Design and Architecture

## Current

Momentum is built on Python 3.13 and uses PyQt6 for the GUI. The architecture consists of specialized classes that manage different aspects of the simulation. The core simulation uses a realtime agent-based approach where drivers are autonomous AI entities making decisions at 30 FPS based on race conditions and their attributes.

Core Architecture Classes

The simulation architecture can be broken down into key classes that handle initialization, state management, player interaction, and visual representation.

MomentumLauncher (Application Controller)
Location: Momentum/Python/GUI/launcher.py

This class manages the overall application lifecycle. It initializes the PyQt application, manages transitions between the main menu and race windows, and handles player configuration.

When you start Momentum the launcher creates a QApplication and shows the MainMenuWindow. When the player selects a driver and starts a race it creates a RaceWindow and connects its return signal back to the menu.

MainMenuWindow (Player Setup)
Location: Momentum/Python/GUI/gui_main_menu.py

This is where players configure their race. The class loads the driver database via DatabaseManager and presents a list of available drivers. Players select a driver and set their pace and overtaking aggression using sliders. These settings become player overrides that affect how the AI controls the player's car during the race.

When the player clicks Start Race the window emits a start_race_signal carrying a config dictionary containing the selected driver and tuning preset.

RaceWindow (Main Game View)
Location: Momentum/Python/GUI/gui_race_visual.py

This is the core gameplay class. It manages the visual track display, live car rendering, standings table, and timing information. The RaceWindow contains several key responsibilities:

Track Generation: Uses CircuitGenerator to create a procedural racing circuit based on the track length. The circuit is built from straight sections and clothoid corner transitions and uses closure logic to complete a loop back to the start line.

Race Execution: When the race starts the window spawns a race_runner thread that calls simulate_race from the race simulation API. This thread runs the RealtimeRaceEngine in the background and emits position updates at 30 FPS.

Event Handling: The RaceWindow subscribes to position updates via EventEmitter signals. Every frame (30 times per second) the engine sends car positions, lap counts, gaps, and race status. The window updates the visual display and standings table based on these events.

Player Input: The window captures keyboard input for pace adjustments (up/down arrows) and overtaking aggression (left/right arrows). These inputs update player_overrides which the engine reads every tick to control the player's car.

RealtimeRaceEngine (Simulation Core)
Location: Momentum/Python/RaceLogic/realtime_race_engine.py

This is the simulation engine that drives the race. The engine runs at 30 FPS and updates each driver's state every timestep (0.033 seconds). Each driver is represented by a DriverState object that tracks physical state (position, velocity, lap), race situation (gaps, position, nearby cars), strategic state (racing mode, push intensity), and component degradation (tires, fuel).

The engine's main loop performs these steps every frame:

AI Decision Making: For each driver call update_racing_mode which examines gaps to cars ahead and behind and decides whether to attack, defend, manage pace, or cruise. Player-controlled drivers skip AI logic and use player_overrides from the UI sliders instead.

Performance Calculation: Calculate speed based on driver attributes, team capability, push intensity, tire condition, fuel load, and whether the car is in a slipstream.

Position Update: Move the car forward based on calculated speed and timestep. Update velocity and position values.

Lap Detection: Check if the car crossed the start/finish line by comparing previous position to current position. If a lap was completed call complete_lap to record lap time.

Incident Checking: Check for collisions by examining gaps between nearby cars. If a car is too close to another trigger an incident (spin, contact, or mechanical failure).

Degradation and Fatigue: Reduce tire condition and fuel load based on push intensity. Accumulate push fatigue when drivers push hard which increases mistake probability.

Position Emission: Create a position event containing all car states and emit it via the event callback so the GUI can update.

DatabaseManager (Persistence Layer)
Location: Momentum/Python/database/database_manager.py

This class handles all database operations for drivers, teams, tracks, championships, and race results. It uses SQLite as the backend database and provides CRUD operations with transaction management and foreign key constraint enforcement.

The manager initializes the database schema on first run creating tables for drivers (with 50+ attributes), teams, tracks, championships, races, and race_results. During race initialization the engine queries the DatabaseManager to load driver and team data. After the race completes results can be persisted back to the database.

VehicleRenderer (Visual Representation)
Location: Momentum/Python/vehicles/vehicle_appearance.py

This class renders simplified top-down car sprites using PyQt's QPainter. Each car is drawn as a polygon body with wings, cockpit, suspension hints, and rectangular tires. The renderer supports a steering_angle parameter that rotates the front tires to show steering input. Livery colors are generated deterministically based on team ID so the same team always gets the same colors.

Folder Structure Breakdown

Momentum/Python/GUI: All user interface code including launcher, main menu, race window, and component health displays.

Momentum/Python/RaceLogic: Core simulation engine and discipline-specific modules. The realtime_race_engine contains the 30 FPS tick loop. base_race_engine defines the abstract BaseDisciplineEngine class. disciplines folder contains concrete implementations for single seater, rally, endurance, etc.

Momentum/Python/database: Database models and manager. models.py defines Driver, Team, Track, Race, RaceResult classes and the SQL schema. database_manager.py provides all CRUD operations.

Momentum/Python/services: Service layer including race_simulation_api which is the public interface for running simulations. This module loads discipline adapters and orchestrates race execution.

Momentum/Python/vehicles: Vehicle appearance and rendering. vehicle_appearance.py contains VehicleRenderer and livery generation. appearance_integration.py provides VehicleAppearanceManager for managing multiple cars.

Momentum/Python/api: FastAPI routes for headless API mode. simulation.py defines REST endpoints for querying drivers, teams, and running simulations without the GUI.

Momentum/Python/systems: Game systems including currency conversion, staff management, and world state tracking.

Momentum/Python/scripts: Utility scripts for database generation, circuit import, and build helpers.

Momentum/Python/tests: Test files including headless render tests and GUI integration tests.

Data Flow and Event System

Player starts race from MainMenuWindow which emits start_race_signal with driver config.

Launcher creates RaceWindow and calls set_player_driver and set_tuning_preset.

RaceWindow spawns race_runner thread which calls simulate_race from the race simulation API.

simulate_race creates RealtimeRaceEngine and starts the main simulation loop.

Engine updates all driver states at 30 FPS and emits position events via event_callback.

RaceWindow receives position events through EventEmitter signals and updates the visual display and standings table.

Player keyboard input modifies player_overrides which the engine reads every tick to control the player's car.

When the race finishes the engine emits a race_finished event with results and collision log.

RaceWindow displays final results and allows the player to return to the menu.

Concurrency Model

Desktop mode uses a single process with two threads. The main thread runs the PyQt event loop and handles all GUI rendering and input. The race_runner thread executes the simulation engine and emits position events. Communication between threads uses Qt signals which are thread-safe.

API mode runs the FastAPI server under uvicorn. Simulation requests are handled as background tasks that can run concurrently with other API operations.

Design Rationale

SQLite provides portability and simplifies distribution. The entire database can be bundled with the executable.

PyQt6 gives low-level rendering control via QPainter and supports headless rendering for tests.

The realtime agent-based approach provides live interactive races with visible AI decision making which is more engaging than instant batch results.

Separation between the core engine and discipline-specific modules allows adding new racing types without modifying the main simulation loop.

30 FPS update rate balances realism (enough granularity for overtaking and incidents) with performance (can simulate 20+ cars smoothly).

Limitations and Future Work

Season progression and some save/load flows are still in progress.

Start-line collisions were reduced by increasing starting spacing in the realtime engine.

The system supports seeded randomness for repeatability. Monte Carlo batch experiments are documented for reference, but the main simulation path uses the realtime AI agent. Record RNG seeds for repeatability.

Future: quick or batched simulations

Purpose: provide a fast option to advance championships or run statistics without watching full races.

Approaches:

Repeated headless runs: run the simulation many times with different seeds and collect results.

Lower-fidelity mode: evaluate per-lap or per-sector using simpler math to speed runs.

Analytic estimator: estimate finish probabilities from performance scores.

Parallel execution: run iterations in parallel or use background workers.

Where diagrams are located

Editable draw.io files and exported PNG images are in Planning/Design and Implementation/Diagrams. Use these for slides and walkthroughs.

## Future
