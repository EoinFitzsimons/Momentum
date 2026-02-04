Implementation status — demo inventory
=======================================

Purpose
-------

This document records the current, accurate implementation status for the demo and the codebase pieces you should rely on for the 5‑minute presentation. It separates "Implemented / Demo‑ready" items from "Prototype / Legacy / Not for demo" items so examiners see only the runnable parts.

Implemented / Demo-ready (GUI demo - use these)
-----------------------------------------------

- `Momentum/Python/GUI/launcher.py` — GUI entry; runnable desktop launcher for the demo (this is the demo you will present).
- `Momentum/Python/GUI/gui_main_menu.py` — main menu UI: Quick Race flow, driver selection, display modes, tuning presets, and race start signal.
- `Momentum/Python/GUI/gui_race_visual.py` — race visualisation and integration layer: renders cars, receives simulation events, and exposes in-race controls (pace, overtakes) and return-to-menu behaviour.
- `Momentum/Python/RaceLogic/realtime_race_engine.py` — real‑time agent-driven race engine used by the GUI.
- `Momentum/Python/services/driver_attributes.py` — canonical driver attributes and derived signals used by the GUI and engine.
- `Momentum/Python/services/persistence_sqlite.py` — persistence layer used by the application to save results when invoked by the GUI.
 - `Momentum/Python/data/circuits_database.json` — track asset file with many definitions; not used by the current GUI demo. The live demo uses a single active track (seeded in the DB or provided by `PersistenceSQLite.seed_sample_data()`).
- `Momentum/Python/mvp_tests/` — small validation/unit tests useful for validating demo behaviour (example files: `test_uc01_driver.py`, `test_uc02_race_config.py`).

How to run the GUI demo (recommended)
-------------------------------------

- Launch the GUI application (recommended for your live demo):

```powershell
python Momentum/Python/GUI/launcher.py
```

Demo steps to perform on stage (follow this order, aim for ~2 minutes demo):

1. Main Menu: click "Quick Race".
2. Quick Race Setup: select the first driver card (default), optionally change the tuning preset to show behaviour differences, and pick a track from the dropdown (default is fine).
3. Click "Start Race" to begin the visualised simulation.
4. During the race: demonstrate the pace and overtaking controls (these are active in the race window) and point out how driver attributes affect behaviour.
5. Finish: use "Return to Menu" to show the main menu re-appearing and where results are persisted.

Notes: the GUI flow emits a race configuration dict (driver, display_mode, tuning_preset, track_id) to the launcher which instantiates `RaceWindow` and runs the simulation. Use the GUI for live demos rather than the scripted runners if you want interactive control.

<!-- Prototype/legacy runner scripts and archive references removed from this document as requested. -->

Verified precise behaviours (read from code)
--------------------------------------------

- The `MainMenuWindow` (`Momentum/Python/GUI/gui_main_menu.py`) loads drivers with `DatabaseManager().get_all_drivers()` and displays the first `QUICK_RACE_LIST_SIZE` drivers in the quick-race dialog.
- Driver cards use `services.driver_attributes.get_display_name`, `get_display_nationality`, and `get_driver_skill_int` for UI text, and the radar visual is populated from `get_driver_radar_values(driver)`.
- Track selection in the quick-race dialog attempts to call `db.get_all_tracks()`; if no tracks are present the UI shows a placeholder entry "Test Circuit (Default)".
- Starting a race emits a config dict containing `driver`, `display_mode`, `tuning_preset`, and `track_id` which `launcher.py` passes to `RaceWindow`.
- `RaceWindow.set_player_driver(driver)` ensures the player driver is present in the internal `drivers` list and will rebuild the on-track `cars` and standings table if needed.
- `RaceWindow.set_tuning_preset(preset)` stores the preset (e.g. `balanced`, `aggressive`, `tyre_sensitive`) and prints a debug line; the preset value is passed to the simulation via the race configuration.
- `RaceWindow.set_display_mode(mode)` switches window flags and geometry between `windowed`, `borderless`, and `fullscreen` as implemented in the race window.
- The simulation engine integration uses `services.race_simulation_api.simulate_race(...)`. That API will either load a discipline adapter or fall back to `RealtimeRaceEngine`.
- `RealtimeRaceEngine.simulate_race(...)` (in `Momentum/Python/RaceLogic/realtime_race_engine.py`) is a 30 FPS agent-based engine: it builds a `TrackMap`, steps drivers each timestep, emits position update events via the provided `event_callback`, and returns a list of result dicts. The API calls the engine with `realtime_speed=5.0` by default for watchable output.
- Persistence: `services/persistence_sqlite.py` implements `PersistenceSQLite` with `save_race_results(race_id, results)`. Scripts (`tools/*`, `scripts/*`) call this for batch/demo persistence. The GUI windows do not automatically call `save_race_results` unless explicitly wired to a persistence layer.
- Database initialisation and hydration are handled by `database/database_manager.py`: it ensures `SCHEMA_SQL` exists, creates the DB path if needed, and `_hydrate_driver` converts DB rows into the compact `Driver` dataclass used throughout the UI and services.
- The demo-seeding helper in `PersistenceSQLite.seed_sample_data()` inserts a minimal single track record (`id=1, 'Short Circuit'`) when seeding; scripted runners may rely on this seeded track, whereas the GUI will show a placeholder if the DB is empty.
