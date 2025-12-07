## Implementation - Integrated Walkthrough (MVP + Roadmap)

This chapter describes the current playable implementation used for the midpoint demo (MVP single-seater quick race), the runtime architecture and data flows, and the set of unattached/future systems planned for later development. The text is aimed at non-developer readers and product reviewers; file and symbol names are included to help locate code in the repository.

### At-a-glance: what the MVP delivers

- Single-discipline quick race: single-seater race simulation with player-selectable driver and tuning preset via the Quick Race UI (`MainMenuWindow` → `QuickRaceSetupWindow`).
- Realtime agent-based simulation: the race engine advances in discrete ticks (~30 ticks/s) and drives AI decision-making, lap progression and incidents.
- Visualiser: `RaceWindow` with `TrackWidget` renders the generated circuit and animates cars using per-tick position events emitted by the engine.
- Persistence & telemetry: driver data, career statistics and basic persistent state use SQLite via `DatabaseManager`; telemetry traces are stored (batched) for later inspection.

### Architecture & core files

- Launcher / UI: `Momentum/Python/GUI/launcher.py` starts the application and wires `MainMenuWindow` to `RaceWindow`.
- Main menu & setup: `Momentum/Python/GUI/gui_main_menu.py` - driver selection, tuning presets, and start controls.
- Visualiser & track generator: `Momentum/Python/GUI/gui_race_visual.py` - `CircuitGenerator`, `TrackWidget`, and event handling for real-time updates.
- Simulation adapter: `Momentum/Python/services/race_simulation_api.py` - public function `simulate_race(...)` used by visual/demo code; selects discipline adapter or falls back to `RealtimeRaceEngine`.
- Engines: `Momentum/Python/RaceLogic/realtime_race_engine.py` (real-time loop) and `Momentum/Python/RaceLogic/base_race_engine.py` (abstract discipline API and shared utilities).
- Data layer: `Momentum/Python/database/models.py` (data models: `Driver`, `Team`, `Track`, `RaceResult`) and `Momentum/Python/database/database_manager.py` (DB access).

This dependency chain explains the runtime path: `launcher.py` → `gui_main_menu` → `simulate_race` (services) → engine (realtime or discipline adapter) → engine emits events → `gui_race_visual` consumes events and updates the UI.

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
- AI decisions: agents evaluate local context (gap ahead/behind, tyre and fuel conditions, relative performance) and choose modes such as ATTACK/DEFEND/MANAGE.
- Performance model: driver attributes and a team factor combine to produce lap- and tick-level performance; safety systems clamp behaviour when required.
- Incidents and reliability: the engine uses probabilistic checks combining driver/team attributes and environmental stress to determine mechanical DNFs and collisions.

Note: while the model references team properties (tier, budget) for performance and reliability, the MVP UI does not expose team selection. To keep the playable demo simple, `services.race_simulation_api` will create placeholder `Team` objects for drivers if no team data is provided.

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

For the midpoint demo the persistence surface can be the minimal set: driver updates, session metadata and telemetry - sufficient to show progression without a full career UI.

### Teams and current exposure

- Codebase: `Team` exists as a full model in `database/models.py` and is supported in `database_manager.py`.
- UI: the Quick Race UI does not present team selection; drivers are shown independently. The simulation code tolerates this by creating placeholder `Team` instances where necessary.

Recommendation: document this explicitly in the Implementation chapter (done here) and add a future UX task to surface team selection when ready.

### Testing, determinism and reproducibility

- Gameplay is non-deterministic by design: tick timing, thread scheduling and system timing mean exact replays are not guaranteed.
- For development and QA, provide optional deterministic tools:
  - Seeded track generation for repeatable circuit layouts.
  - Deterministic RNG mode (controlled seed) and an execution mode to run the engine in a single-threaded, deterministic manner for automated testing.
  - Telemetry-first reproducibility: store full telemetry traces of positions and events so individual sessions can be inspected or replayed in a deterministic player.

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

Below is a single, integrated section that presents each key runtime function by name, then the code excerpt, and finally a concise explanation of how it works and why it matters. This mirrors the Quick Race runtime path: GUI launcher → Quick Race setup → services adapter → realtime engine → visualiser + persistence.

Note: you mentioned an "attack / maintain / defend" diagram - keep using that diagram as the canonical visual. I have not altered it; please confirm the filename or I can place a copy under `Planning/Implementation/attack-maintain-defend.mmd` if you want.

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
adapter = _load_discipline_engine(context, seed=seed)
if adapter is not None:
  return adapter.simulate_race(context)

# Fallback to realtime engine
engine = RealtimeRaceEngine(seed=seed)

# Fetch team data if available, otherwise create placeholders
teams_dict = {}
if db and drivers is not None:
  # attempt to fetch via db.get_team
  ...
if not teams_dict and drivers is not None:
  for driver in drivers:
    teams_dict[driver.current_team_id] = Team(
      id=driver.current_team_id,
      name=f"Team {driver.current_team_id}",
      discipline="formula",
      tier="tier2",
      budget=100.0,
      headquarters="Unknown",
      team_principal="Unknown"
    )

results = engine.simulate_race(drivers=drivers, teams=teams_dict, track=track, total_laps=laps, event_callback=event_callback, ...)
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
  - `_update_racing_mode`: decides whether the driver is pushing, defending, or conserving (based on tyre/fuel/strategy).
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

---

**Main classes & algorithms (summary)**

- `RealtimeRaceEngine` (core): ticked simulation loop; per-driver state updates; RNG-driven probabilistic events; emits per-frame telemetry via `event_callback`.
- `CircuitGenerator`: procedural track building and rescaling; returns an ordered list of `TrackPoint` for visualisation and physics mapping.
- `DatabaseManager`: thin SQLite wrapper for CRUD on drivers, teams, tracks; used by UI and services to load/save state.
- `Race Simulation API` (services): adapter pattern that loads a discipline-specific engine when available, otherwise falls back to the realtime engine; responsible for context assembly (drivers, teams, track, seed) and converting engine outputs to API-friendly `RaceResult` objects.
- GUI flow: `QuickRaceSetup` → `MomentumLauncher.start_race` → `RaceWindow` initialisation → `services.simulate_race` invocation (via button or event) → engine runs in background thread and emits events → `TrackWidget.update_car_realtime` receives events and updates visuals.

Mapping to your Attack / Maintain / Defend diagram

- The engine's `_update_racing_mode` maps directly to the Attack / Maintain / Defend states in your diagram: code decides mode transitions (attack → defend → conserve) based on tyre/fuel/position inputs. Keep the diagram as the authoritative flow; this document references it. If you confirm the filename, I will link it into this chapter.

Next steps I can take (pick one):

- Expand any of the above excerpts with full verbatim function bodies (I have them available), or
- Move the full function extracts into a separate `appendix/code-excerpts.md` and keep the main chapter concise (recommended), or
- Link the exact diagram file into this document and add a small cross-reference block.
