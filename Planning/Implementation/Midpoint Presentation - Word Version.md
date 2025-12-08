### At-a-glance: what the MVP delivers

- Single-discipline quick race: single-seater race simulation with player-selectable driver and tuning preset via the Quick Race UI (`MainMenuWindow` > `QuickRaceSetupWindow`).
- Realtime agent-based simulation: the race engine advances in discrete ticks (~30 ticks/s) and drives AI decision-making, lap progression and incidents.
- Visualiser: `RaceWindow` with `TrackWidget` renders the generated circuit and animates cars using per-tick position events emitted by the engine.
- Player controls: the player can actively manage race pace and overtaking aggressiveness using UI sliders. These controls map to a combined "push intensity" value that affects speed, tyre wear and fatigue.
- Stress / fatigue mechanic: sustained high push increases player fatigue/stress, which degrades performance (reaction time, consistency) and raises incident probability; fatigue recovers over time when pace is reduced or during pit stops. Telemetry exposes `push_intensity`, `push_fatigue`, and `tire_condition` for live HUD display and post-race analysis.
- Telemetry & persistence: driver and race telemetry are saved to allow replay and analysis (batched writes to minimize IO).

#### How to run the demo

**Prerequisites**: Python 3.10+ (tested on 3.11 and 3.13), PyQt6, NumPy, and other dependencies listed in `requirements.txt`.

**Setup and launch**:

```powershell
# Navigate to Python backend directory
cd Momentum/Python

# Create and activate virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Launch the PyQt6 GUI demo (primary method)
python GUI/gui_game.py

# Alternative: run Quick Race visual demo
python GUI/gui_race_visual.py

# Run tests (optional)
python tests/test_playability.py
python tests/test_race_simulation.py
```

**Troubleshooting**: if the database is missing or corrupt, regenerate it with `python scripts/regenerate_database.py`. If circuits are missing, import them with `python scripts/import_circuits.py`.

### Architecture & core files

- Launcher / UI: `Momentum/Python/GUI/launcher.py` starts the application and wires `MainMenuWindow` to `RaceWindow`.
- Main menu & setup: `Momentum/Python/GUI/gui_main_menu.py` - driver selection, tuning presets, and start controls.
- Visualiser & track generator: `Momentum/Python/GUI/gui_race_visual.py` - `CircuitGenerator`, `TrackWidget`, and event handling for real-time updates.
- Simulation adapter: `Momentum/Python/services/race_simulation_api.py` - public function `simulate_race(...)` used by visual/demo code; selects discipline adapter or falls back to `RealtimeRaceEngine`.
- Engines: `Momentum/Python/RaceLogic/realtime_race_engine.py` (real-time loop) and `Momentum/Python/RaceLogic/base_race_engine.py` (abstract discipline API and shared utilities).
- Data layer: `Momentum/Python/database/models.py` (data models: `Driver`, `Team`, `Track`, `RaceResult`) and `Momentum/Python/database/database_manager.py` (DB access).

This dependency chain explains the runtime path: `launcher.py` > `gui_main_menu` > `RaceWindow` → `services.simulate_race(...)` (services) > engine (realtime or discipline adapter) > engine emits events > `gui_race_visual` consumes events and updates the UI.

Note: runtime orchestration is split — the `MomentumLauncher` creates the `RaceWindow`, but `RaceWindow` is responsible for calling `services.simulate_race(...)` and managing the background simulation thread. The launcher does not directly invoke the simulation service; it only instantiates and configures the visual window.

### Detailed runtime flow (MVP race)

1. User selects Quick Race and picks a `Driver` from a list loaded by `DatabaseManager.get_all_drivers()`.
2. Quick race builds a `config` object (player driver, `tuning_preset`, display mode) and the launcher calls `RaceWindow` with that config.
3. `RaceWindow` ensures a visual `TrackWidget` exists and requests a track via `CircuitGenerator.generate(track_length_km=...)`.
4. The visualiser requests `simulate_race(...)` from `services.race_simulation_api` with `drivers`, `track`, `event_callback` and optional `player_driver_id` and `player_overrides`.
5. `simulate_race` attempts to instantiate a discipline adapter via `_load_discipline_engine`; if none is available it falls back to `RealtimeRaceEngine`.
6. The engine runs its per-tick loop and calls the provided `event_callback(position_event)` to report positions, lap completions and incidents.
7. `gui_race_visual.TrackWidget` receives position events (thread-safe via Qt signals) and maps absolute positions to track points, animating cars smoothly using an animation timer.
8. Telemetry and key events (lap times, incidents, DNF) are written out in batches to minimize per-tick IO overhead.

### Engine internals (summary, non-developer language)

- Tick loop: each tick updates driver states, computes speed/position, checks for collisions and mechanical failures, and emits compact updates consumed by the GUI.
- AI decisions: agents evaluate local context (gap ahead/behind, tyre and fuel conditions, relative performance) and choose modes: **Attack** (overtaking), **Defend** (protecting position), or **Manage** (conserving resources).
- Performance model: driver attributes and a team factor combine to produce lap- and tick-level performance; safety systems clamp behaviour when required.
- Incidents and reliability: the engine uses probabilistic checks combining driver/team attributes and environmental stress to determine mechanical DNFs and collisions.

The model references team properties (tier, budget) for performance and reliability, but the MVP UI does not expose team selection. To keep the playable demo simple, `services.race_simulation_api` creates placeholder `Team` objects for drivers when no team data is provided.

### Track generation (parameterisation and reuse)

The `CircuitGenerator` is designed to produce closed circuits from a composable instruction set; the generator is already used to create the single track in the MVP. To produce multiple distinct circuits, the generator accepts and should expose the following parameters:

- `track_length_km` (float) - the target circuit length; the generator rescales the point list to match exactly.
- `complexity_level` (int or enum) - controls how many corners and clothoid transitions are included.
- `straight_variation` (float) - influences straight segment lengths and variety.
- `corner_sharpness_profile` (distribution) - configures corner radii and clothoid curvature.
- `seed` (optional) - only for development testing to reproduce a generated layout; gameplay remains non-deterministic.

Design guidance:

- Add an API `generate(track_length_km, complexity_level, ...)` that returns the point list and sector metadata. Store generator parameters alongside any exported circuit file (JSON) so layouts can be reproduced for QA.
- Use sector metadata to influence overtaking logic, pit strategy and visual indicators in the UI.

### Persistence, telemetry and career progress

- Storage: `DatabaseManager` and the SQLite DB are the canonical store for driver profiles, career stats and track metadata.
- Autosave/checkpoints: implement checkpoints at key game milestones (session exit, championship round end). A checkpoint includes DB changes and a small session metadata file.
- Telemetry: write race traces in batched CSV/JSON files (or separate telemetry DB table) to allow replay, debugging and performance analysis.
- Migration: each save/checkpoint includes a format version to enable safe migrations as features evolve.

#### Telemetry batching policy

**Batch size and flush conditions**:

- Batch size: 100 position events per driver (configurable via `TELEMETRY_BATCH_SIZE` in `config.py`).
- Flush triggers: (1) batch full, (2) lap completion, (3) race end, (4) 5-second idle timeout.
- Format: JSON Lines (`.jsonl`) for per-event storage; one event per line for streaming replay.
- File path: `logs/telemetry/race_{timestamp}_{track_id}.jsonl`.

**Failure handling**: if a batch write fails (disk full, permission error), the engine logs the error and continues. Partial batches are written to a `.partial` suffix file and can be recovered manually. Telemetry failures do not abort the race.

For the midpoint demo the persistence surface can be the minimal set: driver updates, session metadata and telemetry - sufficient to show progression without a full career UI.

Implementation notes: telemetry batching and event emission are implemented in the realtime engine (`Momentum/Python/RaceLogic/realtime_race_engine.py`). The engine performs batched telemetry writes and exposes telemetry and position events to the services layer. The GUI (`Momentum/Python/GUI/gui_race_visual.py`) receives telemetry updates via Qt signals for HUD display, while `Momentum/Python/services/race_simulation_api.py` acts as the adaptor connecting higher-level callers to the engine.

### Teams and current exposure

- Codebase: `Team` exists as a full model in `database/models.py` and is supported in `database_manager.py`.
- UI: the Quick Race UI does not present team selection; drivers are shown independently. The simulation code tolerates this by creating placeholder `Team` instances where necessary.

Implementation notes: placeholder `Team` objects are created in `Momentum/Python/services/race_simulation_api.py` when drivers lack team records in the database. This allows the engine to receive a complete `teams` context while keeping the Quick Race UI minimal.

Recommendation: document this explicitly in the Implementation chapter (done here) and add a future UX task to surface team selection when ready.

### Testing, determinism and reproducibility

- Gameplay is non-deterministic by design: tick timing, thread scheduling and system timing mean exact replays are not guaranteed.
- For development and QA, provide optional deterministic tools:
  - Seeded track generation for repeatable circuit layouts.
  - Deterministic RNG mode (controlled seed) and an execution mode to run the engine in a single-threaded, deterministic manner for automated testing.
  - Telemetry-first reproducibility: store full telemetry traces of positions and events so individual sessions can be inspected or replayed in a deterministic player.

#### Seed/Determinism Scope

| Subsystem              | Accepts `seed`? | Purpose                         | Default Behaviour                 |
| ---------------------- | ----------------- | ------------------------------- | --------------------------------- |
| `CircuitGenerator`   | Yes (future)      | Repeatable track layouts for QA | Random layout                     |
| `RealtimeRaceEngine` | Yes               | Deterministic RNG for tests     | Non-deterministic (`seed=None`) |
| `Name generators`    | No (not exposed)  | Driver/team name generation     | Random                            |
| `Telemetry replay`   | N/A               | Replay recorded session         | Uses stored events                |

To enable deterministic mode: pass `seed=42` (or any integer) to the services entrypoint (see `Momentum/Python/services/race_simulation_api.py`) — the services layer forwards the seed to the engine. The realtime engine (`Momentum/Python/RaceLogic/realtime_race_engine.py`) constructs a NumPy RNG (`np.random.default_rng(seed)`) to control probabilistic events (mistakes, incidents, performance variance). Track generation currently does not consistently expose a seed parameter; exposing a seed in `CircuitGenerator.generate(...)` is a recommended QA improvement to achieve fully repeatable sessions.

### Threading and concurrency

The race simulation uses a multi-threaded architecture to avoid blocking the GUI:

- **Main thread (Qt)**: runs the GUI event loop, handles user input, and renders the visualiser.
- **Background thread (`T_engine`)**: runs `engine.simulate_race(...)` and emits position events at ~30 FPS.

Event flow:

1. GUI calls `simulate_race(...)` in a background thread (via `threading.Thread`).
2. Engine executes the tick loop and calls `event_callback(position_event)` from `T_engine`.
3. Callback posts events to the Qt main thread using `EventEmitter.position_update.emit(...)` (a Qt signal).
4. Qt main thread receives the signal and calls `TrackWidget.update_car_realtime(...)` to update visuals.

Shutdown:

- The GUI sets a `stop_event` (threading.Event) when the user closes the race window.
- The engine checks `stop_event.is_set()` each tick and exits the loop if set.
- The background thread is joined with a 2-second timeout to ensure clean shutdown.

### Unattached systems - concise roadmap

- Teams UX & Contracts - add team selection, contracts and budget effects.
- Championship/Season system - calendar creation, standings and season progression.
- Save manager & cloud sync - robust save/export/import flows and optional cloud sync.
- Staff & vehicle upgrades - hire staff and apply upgrades to vehicles over seasons.
- Additional disciplines - implement discipline adapters in `RaceLogic/disciplines/` and tune attribute weightings.
- Track library - import/export circuits and provide curated track selection UI.

### Appendix: where to look for the code referenced above

- `Momentum/Python/GUI/launcher.py` - application entry and window orchestration
- `Momentum/Python/GUI/gui_main_menu.py` - main menu and quick race setup
- `Momentum/Python/GUI/gui_race_visual.py` - visualiser and `CircuitGenerator`
- `Momentum/Python/services/race_simulation_api.py` - public simulation API (adapter selection)
- `Momentum/Python/RaceLogic/realtime_race_engine.py` - realtime engine implementation
- `Momentum/Python/RaceLogic/base_race_engine.py` - discipline API and shared utilities
- `Momentum/Python/database/models.py` and `.../database_manager.py` - data model and persistence

## Functions, Code & Explanations (integrated)

Below is a single, integrated section that presents each key runtime function by name, then the code excerpt, and finally a concise explanation of how it works and why it matters. This mirrors the Quick Race runtime path: GUI launcher > Quick Race setup > services adapter > realtime engine > visualiser + persistence.

### Function: `MomentumLauncher.start_race`

```python
def start_race(self, config: dict):
  print(f"[LAUNCHER] Starting race with config: {config}")
  self.race_config = config

  if self.race_window:
    self.race_window.close()
    self.race_window = None

  self.race_window = RaceWindow()

  player_driver = config.get('driver')
  if player_driver:
    self.race_window.set_player_driver(player_driver)

  tuning_preset = config.get('tuning_preset', 'balanced')
  self.race_window.set_tuning_preset(tuning_preset)

  display_mode = config.get("display_mode", "borderless")
  self.race_window.set_display_mode(display_mode)

  self.race_window.return_to_menu.connect(self.return_to_menu)
  self.race_window.show()

  driver_name = getattr(config['driver'], 'name', 'Unknown Driver')
  print(f"[LAUNCHER] Race started with player: {driver_name}")
```

Explanation:

- Purpose: create and show the `RaceWindow`, configure the player driver and visual/tuning options, and wire the UI signals back to the main menu.
- Inputs: `config` dictionary (contains `driver`, `tuning_preset`, `display_mode`, etc.).
- Behaviour: safe-closes any existing race window, instantiates a new visual window, passes selected driver and presets, connects `return_to_menu` signal, and displays it. This is purely UI orchestration: no simulation logic runs here.

### Function: `QuickRaceSetup._start_race` (from `gui_main_menu.py`)

```python
def _start_race(self):
  current_item = self.driver_list.currentItem()
  if not current_item:
    QMessageBox.warning(self, "No Driver", "Please select a driver.")
    return

  self.selected_driver = current_item.data(Qt.ItemDataRole.UserRole)
  selected_preset = self.preset_combo.currentData()

  config = {
    "driver": self.selected_driver,
    "display_mode": self.display_mode,
    "tuning_preset": selected_preset
  }

  self.race_start.emit(config)
  self.accept()
```

Explanation:

- Purpose: collect user choices from the Quick Race UI and emit a `race_start` event carrying the configuration.
- Inputs: UI controls (`driver_list`, `preset_combo`, display toggles).
- Behaviour: validates selection, packages `driver` and other settings into a `config` dict, emits `race_start` (handled by the launcher), and closes the dialog.

Why it matters: this function is the bridge between player selection and the runtime path - it constructs the `config` that `start_race` and later the services layer consume.

### Function: `services.race_simulation_api.simulate_race` (adapter selection + placeholders)

```python
def simulate_race(
    drivers: Optional[List[Driver]] = None,
    track: Optional[Track] = None,
    seed: Optional[int] = None,
    laps: Optional[int] = None,
    verbose: bool = False,
    event_callback: Optional[Callable[[dict], None]] = None,
    stop_event=None,
    db: Optional[Any] = None,
    track_points: Optional[List] = None,
    player_driver_id: Optional[int] = None,
    player_overrides: Optional[Dict[str, float]] = None,
    context: Optional[RaceContext] = None,
) -> List[RaceResult]:
    """Run real-time agent-based race simulation at 30 FPS"""
  
    # Try to load discipline-specific adapter
    if context is not None:
        adapter = _load_discipline_engine(context, seed=seed)
        if adapter is not None:
            return adapter.simulate_race(context)
        engine = RealtimeRaceEngine(seed=seed)
        drivers = context.drivers
        track = context.track
        laps = context.total_laps
    else:
        engine = RealtimeRaceEngine(seed=seed)
  
    # Fetch team data from DB or create placeholders
    teams_dict = {}
    if db and drivers is not None:
        try:
            team_ids = {d.current_team_id for d in drivers if d.current_team_id}
            get_team_fn = getattr(db, "get_team", None)
            for team_id in team_ids:
                if callable(get_team_fn):
                    team = get_team_fn(team_id)
                    if team:
                        teams_dict[team_id] = team
        except Exception as e:
            if verbose:
                print(f"Warning: Could not fetch team data: {e}")
  
    # Create placeholder teams for any missing
    if not teams_dict and drivers is not None:
        for driver in drivers:
            if driver.current_team_id not in teams_dict:
                teams_dict[driver.current_team_id] = Team(
                    id=driver.current_team_id,
                    name=f"Team {driver.current_team_id}",
                    nationality="USA",
                    founded_year=2020,
                    discipline="formula",
                    tier="tier2",
                    budget=100.0,
                    headquarters="Unknown",
                    team_principal="Unknown"
                )
  
    return engine.simulate_race(
        drivers=drivers,
        teams=teams_dict,
        track=track,
        total_laps=laps,
        event_callback=event_callback,
        stop_event=stop_event
    )
```

Explanation:

- Purpose: central entrypoint for simulating a race. It tries to load a discipline-specific engine (adapter). If an adapter is available (e.g., tailored simulators), it delegates to it. Otherwise it instantiates the `RealtimeRaceEngine` fallback.
- Team handling: if the database lacks team entries for drivers (common in quick, throwaway races), the service creates placeholder `Team` objects so the engine receives a complete context. This is why docs should state that the UI might not expose teams even though the engine expects them.
- Seed handling: `seed` is passed through to allow deterministic runs for QA; gameplay uses non-deterministic RNG by default.

### Class / Function: `RealtimeRaceEngine` - `simulate_race` (core loop)

```python
def simulate_race(...):
  # initialize race_state and track map
  while not self._race_finished(race_state):
    for driver_id, state in race_state.driver_states.items():
      if not state.running:
        continue
      self._update_racing_mode(state, race_state)
      speed_mps = self._calculate_speed(state, track_length_m)
      # apply mistakes, update position
      state.position_m += speed_mps * timestep
      # handle lap completion, degradation, incidents
    self._update_race_situation(race_state)
    if event_callback:
      event_callback(self._create_position_event(race_state, frame))
```

Explanation (algorithms & structure):

- Core idea: this is a real-time, tick-based loop (target ~30Hz). At each tick the engine updates every driver's state (mode, speed), applies randomised events (mistakes, incidents), advances positions, and emits position/telemetry events to listeners (the GUI visualiser, telemetry persister or tests).
- RNG: the engine constructs a NumPy Generator (`np.random.default_rng(seed)`) in its constructor. Passing a `seed` gives repeatable runs (useful for tests); gameplay should not rely on fixed seeds.
- Subsystems:
  - `_update_racing_mode`: decides the driver's mode (**Attack**, **Defend**, or **Manage**) based on tyre/fuel state, gaps to rivals, and overtaking opportunities. Code enum: `RacingMode.ATTACK`, `RacingMode.DEFEND`, `RacingMode.MANAGE`.
  - `_calculate_speed`: computes a target speed from driver skill, car performance, track segment, and weather. The returned speed is modified by stochastic noise for realism.
  - Incident handling: probabilistic checks for spins/collisions/mechanical failures; when triggered they change `state.running` and produce event records.
- Output: generates `RaceResult` records and emits per-frame `position` events for the GUI.

Interesting snippet (pseudo-detail):

```python
# deciding a mistake
mistake_chance = base_mistake_rate * (1.0 - state.driver.error_resilience)
if self.rng.random() < mistake_chance:
  self._apply_mistake(state)
```

#### PositionEvent Schema

The engine emits position events at ~30 Hz via `event_callback`. Each event is a Python `dict` with the following structure:

```python
{
  "type": "position_update",
  "frame": int,              # Frame number (0, 1, 2, ...)
  "time": float,             # Race elapsed time (seconds)
  "positions": [             # List of driver states
    {
      "driver_id": int,
      "driver_name": str,
      "position": int,       # Race position (1st, 2nd, ...)
      "lap": int,            # Current lap number
      "position_m": float,   # Absolute position (metres from start)
      "velocity_mps": float, # Current velocity (m/s)
      "racing_mode": str,    # "attack", "defend", or "manage"
      "push_intensity": float,  # 0.0-1.0
      "push_fatigue": float,    # 0.0-1.0
      "tire_condition": float,  # 1.0=new, 0.0=worn
      "fuel_load": float,       # 1.0=full, 0.0=empty
      "gap_ahead": float,       # Seconds to car ahead
      "gap_behind": float,      # Seconds to car behind
      "running": bool           # False if DNF
    },
    ...
  ]
}
```

**Threading & consumption**: the engine runs on a background thread (`T_engine`) and calls `event_callback(position_event)` directly from that thread. The GUI must marshal the event to the Qt main thread using `QMetaObject.invokeMethod` or a Qt signal (`EventEmitter.position_update.emit(position_event)`). See `gui_race_visual.py` for the `EventEmitter` pattern.

### Function: `CircuitGenerator.generate` (signature + behaviour)

```python
@staticmethod
def generate(track_length_km: float = 5.0):
  """Generate circuit based on track length and return list of TrackPoint"""
  # builds segments list, rescales to target length and finalizes circuit
  return segments
```

Explanation:

- Purpose: procedural generation of a closed circuit with sectors and metadata. The generator builds a series of segment instructions (straights, bends), then rescales and smooths the polyline to achieve the requested total length.
- Why it matters: allows quick race creation without importing pre-made circuits and supports visualisation and lap-timing.

### Function: `TrackWidget.update_car_realtime` (visualiser mapping)

```python
def update_car_realtime(self, driver_id: int, position_m: float, lap: int, velocity_mps: float):
  # Called from race simulation thread (~30 FPS)
  if self.track_length > 0 and len(self.track_points) > 0:
    normalized_pos = position_m % self.track_length
    idx = int(normalized_pos)
    # update car.s, prev_s and movement_direction
```

Explanation:

- Purpose: turn absolute metre-based race positions into a visual index and update the on-screen car. Implemented to be callable from a background thread: it posts signals to the Qt main thread rather than directly mutating UI objects.
- Behaviour: normalises the position to the track length, finds the nearest track point, updates the car's position and heading, and adjusts animation smoothing based on `velocity_mps`.

### Function: `DatabaseManager.get_all_drivers`

```python
def get_all_drivers(self) -> List[Driver]:
  with self.get_connection() as conn:
    rows = conn.execute("SELECT * FROM drivers ORDER BY name").fetchall()
    drivers = []
    for row in rows:
      row_dict = dict(row)
      row_dict.pop('created_at', None)
      try:
        drivers.append(Driver(**row_dict))
      except TypeError:
        continue
    return drivers
```

Explanation:

- Purpose: return a list of `Driver` dataclass instances for UI population and simulation input.
- Behaviour: reads the `drivers` table, converts rows to dicts, strips unneeded fields and constructs `Driver` objects. Robust to schema mismatches by catching `TypeError` and skipping malformed rows.

#### Database schema and error handling

**Expected schema version**: the database schema is defined in `database/models.py` and initialized by `DatabaseManager.__init__()`. Current schema includes `drivers`, `teams`, `tracks`, and `race_results` tables. No formal migration system exists yet; schema changes require manual DB regeneration or ALTER TABLE commands.

**Malformed row handling**: `get_all_drivers()` silently skips rows that fail to construct a `Driver` object (caught `TypeError`). This is intentional to allow the UI to load even if the DB contains legacy or corrupt rows. For stricter validation, add a `--strict` mode that logs the row ID and re-raises the exception.

**Migration/validation step**: before loading drivers, call `DatabaseManager.verify_schema()` (future) to check table structure and warn if columns are missing or types mismatch. For midpoint demo, manual verification via `scripts/verify_database.py` is sufficient.

---

**Main classes & algorithms (summary)**

- `RealtimeRaceEngine` (core): ticked simulation loop; per-driver state updates; RNG-driven probabilistic events; emits per-frame telemetry via `event_callback`.
- `CircuitGenerator`: procedural track building and rescaling; returns an ordered list of `TrackPoint` for visualisation and physics mapping.
- `DatabaseManager`: thin SQLite wrapper for CRUD on drivers, teams, tracks; used by UI and services to load/save state.
- `Race Simulation API` (services): adapter pattern that loads a discipline-specific engine when available, otherwise falls back to the realtime engine; responsible for context assembly (drivers, teams, track, seed) and converting engine outputs to API-friendly `RaceResult` objects.
- GUI flow: `QuickRaceSetup` > `MomentumLauncher.start_race` > `RaceWindow` initialisation > `services.simulate_race` invocation (via button or event) > engine runs in background thread and emits events > `TrackWidget.update_car_realtime` receives events and updates visuals.

Mapping to the state diagram

- The engine's `_update_racing_mode` implements the **Attack / Maintain / Defend** transitions shown in the state diagram (see `Planning/Implementation/stateDiagram-v2.mmd` for the canonical visual): decisions are based on tyre and fuel state, relative gaps to rivals, and overtaking opportunities. These mode decisions feed into `_calculate_speed` and incident probability calculations.
