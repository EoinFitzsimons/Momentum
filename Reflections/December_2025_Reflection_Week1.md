# December 2025 Reflection — Week 1

| Student Name | Eoin Andrew Fitzsimons |
|---|---|
| Student Number | X23151374 |
| Course | BSc (Hons) Computing - Software Development |

Month: December 2025 (Week 1)

## Summary (Dec 1–7)

- This week we moved from a Monte Carlo idea to a real-time agent engine.
- The engine runs at 30 FPS and agents make decisions each frame.
- The GUI shows cars moving, laps count, and standings update live.

## What we did today (Dec 5)

- Cleaned warnings in `realtime_race_engine.py`:
  - Made the `seed` parameter optional to fix a Pylance type warning.
  - Removed unused variables like `target_lap_time`, `overtaking_tendency`, `is_overtaking_zone`, and `CAR_WIDTH`.
  - Replaced unused return values with `_` to silence Sonar warnings.
  - Simplified some function signatures and updated call sites to remove unused parameters.

## Main successes

- Engine runs stable: long race tests completed without crashes.
- GUI integration works: cars move and the UI updates correctly.
- Tests exist for quick checks and full race runs.

## Problems left

- Documentation is out of date and needs rewriting before the midpoint.
- Race balance: too many DNFs — we must tune incident and degradation rates.
- Missing features: qualifying, pit stops, and championship points.

## Plan (this week)

- Finish documentation updates (technical report and proposal).
- Tune balance parameters and run test races.
- Import tracks if time allows and run GUI tests.

---

Student: Eoin Fitzsimons
Date: December 5, 2025

Next update: December 10, 2025
