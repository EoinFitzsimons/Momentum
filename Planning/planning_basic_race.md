**Planning: Basic Race (Branch: basic-race)**

Scope: implement the minimal vertical slice required to run "drivers on a track" → one deterministic race and persist results.
This maps to three use cases (HIGH priority):
- UC-1: Read Driver Details
- UC-2: Read Race Configuration
- UC-3: Create Race Result

Goals
- Produce a working demo script that seeds a tiny DB, runs a single seeded race, and writes results.
- Keep design intentionally small but with clear adapter boundaries (persistence, simulator, orchestration).

Planned files / modules (suggested minimal layout)
- `Momentum/Python/persistence_iface.py` — small interface describing persistence methods (read/write). Example methods:
  - `get_driver(driver_id) -> Driver` 
  - `list_drivers() -> List[Driver]`
  - `get_track(track_id) -> Track`
  - `create_race(race: Race) -> int` (returns race_id)
  - `save_race_results(race_id: int, results: List[RaceResult]) -> None`

- `Momentum/Python/persistence_sqlite.py` — concrete sqlite3 implementation (in-memory for tests; file for demo).

- `Momentum/Python/sim_simple.py` — simple simulator implementing:
  - `simulate_race(drivers: List[Driver], track: Track, seed: Optional[int]) -> List[RaceResult]`
  - deterministic behaviour via RNG seed parameter

- `Momentum/Python/run_basic_race.py` — orchestration/demo script:
  - seeds DB (small set), loads drivers & track, calls `simulate_race`, saves results and prints summary

- `Technical Report/planning_basic_race.md` (this file) — design notes and acceptance criteria

Minimal data members required (domain models, reduced)
- Driver: `id`, `name`, `raw_speed` (float), `consistency` (float)
- Track: `id`, `name`, `length_km` (float), optional `weather`/`difficulty`
- Race: `id`, `track_id`, `race_date`, `race_duration_minutes`
- RaceResult: `race_id`, `driver_id`, `position`, `time_seconds`, `fastest_lap` (bool)

Key methods & responsibilities
- Persistence interface (`persistence_iface.py`)
  - Keep only high-value methods used by MVP, return simple dataclasses or dicts.

- Simulator (`sim_simple.py`)
  - Generate per-driver raw lap time using formula: base_time = f(track.length_km, driver.raw_speed)
  - Apply random variation scaled by `(1 - driver.consistency/100)` using seeded RNG
  - Compute total race time (e.g., sum of N laps or scaled single-lap proxy)
  - Return ordered `RaceResult` list with positions and times

- Orchestration (`run_basic_race.py`)
  - Use the `persistence` implementation to load drivers and track
  - Call `simulate_race` with a fixed `seed` (documented) for reproducibility
  - Persist results via `save_race_results`
  - Print a short summary table to stdout

Acceptance tests (pytest skeleton names)
- `tests/test_uc01_read_driver.py` — verify `get_driver` returns expected fields for seeded DB
- `tests/test_uc02_read_race_config.py` — verify track and race config load correctly
- `tests/test_uc03_create_race_result.py` — run simulation with seed and assert `save_race_results` creates rows; assert ordering and unique positions

Design constraints & rationale
- Keep interfaces tiny: callers (simulator, orchestration) depend only on the minimal persistence interface.
- Use dataclasses (or existing `database/models.py` dataclasses) for the domain objects to avoid duplicating schemas.
- Keep simulation pure: `simulate_race` should not perform IO; it should accept domain objects and return results.
- Start with sqlite3 in-memory for tests, file-backed DB for demo script. Keep `SCHEMA_SQL` as reference/data source; initial small seed script can create reduced tables or reuse canonical tables but only populate a small set.

Iteration plan (micro milestones)
- Step 0 (planning): this doc reviewed and branch created.
- Step 1 (skeleton): add `persistence_iface.py` and `sim_simple.py` with stubs and unit tests that import but not run heavy logic.
- Step 2 (persistence): implement `persistence_sqlite.py` using in-memory sqlite and small helper to create seed data. Add `test_uc01` and `test_uc02` that use the in-memory DB.
- Step 3 (simulator): implement `simulate_race` with seeded RNG and unit tests verifying deterministic ordering.
- Step 4 (orchestration): implement `run_basic_race.py`, wire persistence + simulator, run and inspect results; add `test_uc03`.

Notes about future extensions
- When ready to expand (teams, standings, multiple races), keep `persistence_iface` stable; add new methods rather than changing signatures. This avoids breaking callers.
- If a refactor is needed later (e.g., migrate to ORM), ensure tests cover behaviour so changes are safe.

Estimated effort (rough)
- Step 1: 1–2 hours
- Step 2: 2–4 hours
- Step 3: 2–4 hours (includes deterministic test tuning)
- Step 4: 1–2 hours

Next steps I can take (on `basic-race` branch, only if you ask):
- Create the initial stub files and tests (I will not commit them until you confirm).
- Or, leave the plan for you to review and implement.

End of planning note.
