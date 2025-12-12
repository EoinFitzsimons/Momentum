Presentation Script - 3-minute slides

Total time: 3:00 (180 seconds)
Keep pacing steady: 140-160 words per minute.

Slide 1 - Title (20s)

- Line: "Hello, I am Eoin Fitzsimons. I am a passionate fan of motorsport and sports simulation games."
- Line: "Project: Momentum - a multi-discipline motorsport management simulator modeling seven racing disciplines and a persistent career system."
- Note: include one factual reference: "Prototype developed via iterative tests and targeted refactors."

Transition (5s)

- Line: "First, a brief comparison with existing titles."

Slide 2 - The Past - What Compares? (40s)

- Point: Existing games provide polished presentation but often use linear progression and limited emergent systems.
- Point: Research question - add systemic depth and scale while preserving performance and reproducibility.
- Evidence: Legacy playability scripts and audits exposed inconsistent data imports and brittle demo flows; this informed priorities: automated import/verification and a minimal testable quick-race path.

Transition (5s)

- Line: "Current state - the MVP."

Slide 3 - The Present - The MVP (50s)

- Point: MVP capabilities - playable Quick Race, Monte Carlo engine, telemetry capture, initial PyQt6 GUI.
- Point: Actions taken - archived legacy code, added MVP playability tests, implemented import and verify scripts for circuit data.
- Point: Working items - quick-race demo, deterministic name generation, telemetry saved to logs/telemetry.
- Point: Limitations - season flow, save/load, and high-fidelity Monte Carlo remain for later work.

Transition (5s)

- Line: "Planned work and toolchain improvements."

Slide 4 - The Future - What Will Come? (30s)

- Point: Roadmap - complete deterministic game loop, extend seeded tests to CI, apply performance improvements (vectorize hotspots, optional multiprocessing), finalise packaging via scripts/build_exe.py.
- Point: Immediate dev actions - complete systems/game_loop.py and validate full DB import.
- Request: time for CI runs and a short packaging sprint.

Transition (5s)

- Line: "Demo and next steps."

Slide 5 - Demo + Next Steps (25s)

- Demo plan: run a Quick Race showing RaceWindow HUD and telemetry summary; fallback - open pre-generated telemetry JSON and screenshots.
- Next milestones: complete systems/game_loop.py, add CI seeded tests, validate full DB import, package executable.
- Closing line: "Thank you. I am ready for questions."

Fallback lines (brief)

- Use pre-generated telemetry JSON and screenshots if live demo is not possible.
- Option to run a headless quick-race via API to avoid GUI startup time.

Anticipated questions (short answers)

- How reproducible are runs? - Monte Carlo is seedable; seeds are available in tests/test_playability.py.
- Why PyQt6 and not web? - Desktop provides low-latency telemetry access and a compact development cycle; web is planned for distribution.
- How will scaling be handled? - Data pipelines and deterministic generation scale; heavy simulations run offline with higher iterations and multiprocessing.
