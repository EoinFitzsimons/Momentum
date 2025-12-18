Slide 1: Hello, I’m Eoin Fitzsimons. (0:00–0:30)

This is Momentum - a multi‑discipline motorsport management simulator. The project goal is simple: build a credible, extensible simulation that produces believable, emergent stories while remaining runnable on a standard desktop for an examiner demo.

Aim: create a compact, reproducible simulator that produces emergent race narratives across multiple disciplines and is verifiable for examiner evidence.

Measurable objectives:

- Playable Quick Race visualiser demonstrating realtime agent interactions.
- Optional post‑run export of results for offline analysis
- Canonical attribute services computing derived signals used by engine and UI.

What I’ll show today: a brief description of the problem and design, the runnable Quick Race GUI demo, and the roadmap for turning this prototype into a persistent world.

Slide 2: THE PAST (0:30–1:20)

Problem: existing motorsport management titles are often single‑discipline or shallow in simulation. They prioritise presentation or linear progression over long‑term emergent systems.

Design response: a canonical attribute schema and modular systems. Instead of dozens of overlapping attributes, the project stores a compact canonical set and computes derived signals at runtime. This keeps the DB clean and the behaviour rich.

Approach: procedural generation to create teams, drivers and tracks when needed; agentic simulation for live interactions; and a small set of automated tests to validate edge cases and preserve reproducibility.

Who it’s for: players, academics and designers who need deep, consistent multi‑discipline simulation and reproducible scenarios for balancing and analysis.

What sets it apart: Momentum persists a small canonical attribute set and computes nuanced derived signals (aggression, bravery, vehicle control) at runtime - enabling rich emergent behaviour without a large, redundant dataset. Runs are intentionally unseeded to promote variability and emergent stories; optional export enables post‑run verification if required.

Slide 3: THE PRESENT (1:20–2:40 including demo narration setup)

What’s implemented and demo‑ready: the desktop GUI launcher, a Quick Race flow with driver selection and radar visualisations, a race visualiser that receives real‑time position updates, an agent‑based 30‑FPS race engine, and a lightweight SQLite persistence module used for seeded demos and tests.

Key technical notes

- The GUI is PyQt6 and drives the demo flow (launcher -> MainMenu -> RaceWindow).
- The simulation API chooses a discipline adapter when available or falls back to RealtimeRaceEngine which simulates agents making attack/defend/manage decisions each tick.
- Driver attributes are canonical and hydrated from the DB; derived signals (aggression, bravery, vehicle control) are computed in services/driver_attributes.py.
 Python 3.13 - stable, typed, easy to work with.
 FastAPI - simple HTTP endpoints for running simulations and tests.
 SQLite - single-file database for saving runs and evidence.
 NumPy - small numeric helpers and RNG used in the race code (no pandas or SciPy).
 PyQt6 - desktop GUI toolkit used for the Quick Race visualiser.

Slide 4: THE FUTURE

Planned priorities to complete before final submission:

- Persistent world & season progression so leagues evolve whether the player is active or not.
- Robust save/load and deterministic seeding for reproducible testing and examiner evidence.
- UI polish and a small suite of reproducible scenario tests (playtest harnesses) to demonstrate stability across seasons.

Concrete near‑term milestones and priorities:

- Milestone 1 - Demonstrate emergent runs: verify Quick Race produces varied, watchable emergent behaviour across runs and representative tracks.
- Milestone 2 - Export & verify: add optional post‑run export of results/logs for offline analysis and examiner verification (does not seed gameplay).
- Milestone 3 - Track import: import the full track DB into SQLite and validate metadata for use in all disciplines.

Prioritisation: Milestone 1 and 2 are highest priority to demonstrate emergent behaviour while providing optional evidence; Milestone 3 then enables fuller discipline coverage.

Risks & mitigations: performance at scale (mitigate with vectorised compute and optional worker processes), dataset quality (mitigate with procedural rules and automatic balancing), and demo fragility (mitigate with automated checks and a short recorded backup).

Slide 5: QUESTIONS (4:40–5:00)

Thank you - that’s the demo and the plan. Any questions?
