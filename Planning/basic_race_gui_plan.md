# Basic-Race GUI MVP Plan

Status: Draft
Owner: EoinFitzsimons
Branch: basic-race

## 1. Purpose

This document defines a clear, actionable plan for the Basic-Race MVP with a small PyQt6 GUI. The goal is to deliver a playable vertical slice that demonstrates the core management loop: make at least one decision, run a race, observe per-lap events and final standings, and persist the result.

The emphasis is on visible cause→effect, deterministic reproducibility, and a presentable GUI for demos and evaluation.

## 2. Goals & Acceptance Criteria

- Goal 1: Provide a minimal PyQt6 GUI which lets the user set a seed, choose fidelity (quick/standard/detailed), and a single strategy toggle (e.g., pit-aggressive vs pit-conservative), then start a race.
- Goal 2: The simulator must emit per-lap telemetry (events) and final standings; telemetry must be saved to `logs/race_<timestamp>.csv`.
- Goal 3: Results must be reproducible for a given seed and fidelity.

Acceptance criteria (all must pass):
- `run_mvp(seed=42, fidelity='standard')` completes and returns results (smoke test).
- GUI displays live standings and an event feed during the race (no blocking UI thread).
- Telemetry file written and includes per-lap rows for each driver.
- Changing the strategy option leads to at least one observable change in result for some seed (documented sample seed in report).

## 3. Scope

In-scope (MVP):
- PyQt6 GUI with Start/Stop, Seed, Fidelity, Strategy selector, live standings panel, event feed, and progress bar.
- Background simulator runner (thread) that streams per-lap events to the GUI and writes telemetry.
- Run modes: `quick` (fast, for CI), `standard` (demo), `detailed` (heavier, optional). Default: `standard` for demos; `quick` used in CI.
- Persistence: use existing `PersistenceSQLite` (file `database/momentum.db`) and `logs/` for telemetry.

Out-of-scope (for now):
- Full race UI visualisation (3D/track map) or complex animations.
- Multiplayer/networked features, championships, or long-term progression systems.

## 4. User Stories (mapped to UC)

- As a player (UC-1), I can view driver details and choose a strategy before a race.
- As a player (UC-2), I can view and edit basic race configuration (seed, fidelity).
- As a player (UC-3), I can run a race, see per-lap events, and save results for later analysis.

## 5. Wireframe & Components

Main window layout (left-to-right):
- Controls strip (top): `Seed` input, `Fidelity` dropdown, `Strategy` dropdown, `Start` button, `Stop` button, `Save Telemetry`.
- Left pane: Live standings table (position, driver, laps, total time, pitstops).
- Right pane: Event feed (scrolling list of per-lap messages: "Lap 4 — Driver X pitted (+22s)").
- Bottom: Progress bar with current lap / total laps and a small status label.

Implementation notes:
- Run simulator in a worker thread (QThread or Python Thread + Qt signal bridge). Do not block main thread.
- Simulator will call a callback or emit signals on: lap_start(lap), lap_event(driver_id, message, lap, lap_time), lap_update(driver_state), race_finished(results, telemetry_path).

## 6. Architecture & Data Flow

1. GUI triggers Run command → construct `run_mvp` parameters (seed, fidelity, strategy profile).
2. Background runner calls simulator with a callback object that forwards events to GUI signals and writes telemetry incremental to CSV.
3. On finish, runner calls `PersistenceSQLite.save_race_results(...)` and emits `race_finished` with the results path.

Files to add/update:
- `Momentum/Python/gui/gui_game.py` — main GUI app (PyQt6).
- `Momentum/Python/gui/__init__.py` — package initializer.
- `Momentum/Python/run_basic_race.py` — expose headless `run_mvp(...)` (already present) and a `run_mvp_stream(...)` for GUI callbacks.
- `Momentum/Python/sim_simple.py` — add lightweight event-callback support (already accepts `verbose` — add callback param).

## 7. Milestones & Estimated Effort

Estimated total time: 2–3 days of focused work.

- Day 0.5 — Design & wireframe, finalize acceptance tests (this doc).
- Day 1.0 — Implement GUI skeleton and background runner; wire Start/Stop and seed/fidelity controls.
- Day 0.5 — Integrate simulator callback streaming and write telemetry to CSV; live standings + event feed.
- Day 0.5 — Add headless GUI test mode, smoke tests and documentation; polish and demo scripting.

Deliverables by milestone:
- End of Day 1: Running PyQt6 app that can start a stubbed background runner.
- End of Day 2: Full streaming simulator integration, telemetry files, and acceptance test passing locally.

## 8. Testing & CI

- Local unit tests: `tests/test_run_mvp_smoke.py` — ensure `run_mvp(seed=42, fidelity='quick')` returns deterministic output.
- GUI test mode: headless run that exercises the same code path (no window) for CI.
- Telemetry validation test: runs a demo and asserts that `logs/race_<ts>.csv` exists and has expected columns.

CI notes:
- Use `quick` fidelity for CI smoke tests to keep run-time fast.
- Add GitHub Action job that runs `pytest -k run_mvp` and the headless GUI smoke.

## 9. Risks & Mitigations

- Risk: GUI thread blocking if simulator is not offloaded. Mitigation: use QThread or Python Thread + Qt signals; write integration tests.
- Risk: Detailed mode runs too slow. Mitigation: default to `quick` for CI and provide `detailed` behind an explicit flag; add caching for repeated seeds.
- Risk: Name collision or DB path issues on different dev machines. Mitigation: write telemetry to repo-relative `logs/` and ensure `PersistenceSQLite` creates `database/` if missing.

## 10. Success Metrics

- Can demo a seeded race with visible lap events and final podium in front of assessors.
- Smoke test runs in CI without timing out (target < 2 minutes for full job; `quick` tests < 10s).
- Player-visible decision affects the outcome for documented seeds.

## 11. Next steps (immediate)

1. Confirm scope and acceptance criteria in this document.
2. I'll implement the GUI skeleton `Momentum/Python/gui/gui_game.py` and the simulator callback bridge.
3. Run local demo, produce telemetry, and push branch updates for review.

---
Generated planning artifact for `basic-race` GUI MVP.
