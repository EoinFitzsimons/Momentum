Q: Why Python and PyQt6 for the demo?

A: Python lets me prototype quickly and reuse scientific libraries (NumPy/pandas). PyQt6 gives a straightforward, offline desktop UI that is stable for a timed, local demo.

Q: How do you ensure results are reproducible?
A: Demo runs can be seeded; RNG seeds and any demo parameters are preserved with results. The seeded persistence helper inserts a minimal track and drivers to ensure a consistent starting state.

Q: Why an agent-based realtime engine instead of only Monte Carlo?
A: Monte Carlo was useful early for exploring balance and failure modes. The agent-based engine produces emergent, watchable behaviour that’s better for an interactive demo and for modelling driver interactions like overtakes.

Q: What data do you use for drivers and tracks?
A: All data is synthetic or project-generated. Driver attributes are stored in the canonical schema; the GUI loads hydrated `Driver` objects via the `DatabaseManager`. The current demo uses a single seeded track; a larger track DB is present for future work.

Q: How are driver attributes modelled to avoid redundancy?
A: The code uses a canonical persisted attribute set and computes derived signals (bravery, aggression, vehicle control) in `services/driver_attributes.py`. This keeps stored data compact while allowing nuanced behaviour.

Q: Does the GUI persist results automatically?
A: Persistence is available via `PersistenceSQLite.save_race_results`. Scripts and service code call this when configured; the GUI flow can be wired to persistence but demo mode focuses on live visual output and returning to menu.

Q: How did you validate the simulation?
A: Small unit/validation tests live under `Momentum/Python/mvp_tests/` and targeted playtests capture DNFs, lap-time variance and incidents. Early Monte Carlo runs also helped stress-test edge cases.

Q: What are the main limitations today?
A: The prototype is single-process and optimised for demo scale. Season progression, persistent world state, and full UI polish remain future work.

Q: How would you scale performance for larger simulations?
A: Options: vectorise more logic with NumPy, move tight loops to Cython/compiled extensions, or run Monte Carlo/batch simulations across multiple worker processes or a cluster for offline analysis.

Q: Why SQLite for persistence?
A: Lightweight, zero-config, portable for examiner demos. It supports the project’s reproducible, file-backed workflows without requiring a DB server.

Q: Data ethics and privacy?
A: All driver data is synthetic (Faker/seeding). No personal data is used in the demo, and seeds or sample generation logs can be provided if required.
