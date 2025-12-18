Slide 1: Hello, I’m Eoin Fitzsimons. (0:00–0:30)

This is Momentum - a multi‑discipline motorsport management simulator. The project goal is simple: build a credible, extensible simulation that produces believable, emergent stories while remaining runnable on a standard desktop for an examiner demo.

What I’ll show today: a brief description of the problem and design, the runnable demo (Quick Race GUI), and the roadmap for turning this prototype into a persistent world. I’ll only present evidence you can verify in the demo and in the supporting files.

Slide 2: THE PAST (0:30–1:20)

Problem: existing motorsport management titles are either single‑discipline or shallow in simulation. They sacrifice long‑term, emergent systems for presentation or fixed, linear progression.

Design response: a canonical attribute schema and modular systems. Instead of dozens of overlapping attributes, the project stores a compact canonical set and computes derived signals at runtime. This keeps the DB clean and the behaviour rich.

Approach: procedural generation to create teams, drivers and tracks when needed; agentic simulation for live interactions; and a small set of automated tests to validate edge cases and preserve reproducibility.

Slide 3: THE PRESENT (1:20–2:40 including demo narration setup)

What’s implemented and demo‑ready: the desktop GUI launcher, a Quick Race flow with driver selection and radar visualisations, a race visualiser that receives real‑time position updates, an agent‑based 30‑FPS race engine, and a lightweight SQLite persistence module used for seeded demos and tests.

Key technical notes (one sentence each):

- The GUI is PyQt6 and drives the demo flow (launcher -> MainMenu -> RaceWindow).
- The simulation API chooses a discipline adapter when available or falls back to RealtimeRaceEngine which simulates agents making attack/defend/manage decisions each tick.
- Driver traits are canonical and hydrated from the DB; derived signals (aggression, bravery, vehicle control) are computed in services/driver_attributes.py.

Demo plan (I will run this now - aim: ~2 minutes):

1) Open the app and click Quick Race. (Say: “I’ll select a driver and start a short, watchable race.”) - 10s
2) Point out the driver radar and the tuning preset. (Say: “Radar shows key skills; presets adjust race behaviour.”) - 15s
3) Start the race; narrate one or two emergent events: an overtake or tyre degradation, and show pace/overtake controls. (Narration: “You can see how driver attributes and slipstream influence overtakes.”) - 80–90s
4) Return to menu and note where results would be persisted or inspected in the DB. (Say: “Results can be saved via the persistence layer for analysis.”) - 10s

I will now run the Quick Race demo and narrate the key behaviours.

Slide 4: THE FUTURE (4:00–4:40)

Planned priorities to complete before final submission:

- Persistent world & season progression so leagues evolve whether the player is active or not.
- Robust save/load and deterministic seeding for reproducible testing and examiner evidence.
- UI polish and a small suite of reproducible scenario tests (playtest harnesses) to demonstrate stability across seasons.

Risks & mitigations: performance at scale (mitigate with vectorised compute and optional worker processes), dataset quality (mitigate with procedural rules and automatic balancing), and demo fragility (mitigate with seeded demo scripts and automated checks).

Slide 5: QUESTIONS (4:40–5:00)

Thank you - that’s the demo and the plan. Any questions?
