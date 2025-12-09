Introduction

Background

Why undertake this project?

This project was chosen because existing motorsport management titles typically restrict players to a single discipline (commonly Formula 1) or fall short of the systems depth needed for authentic team-and-driver simulation.

Aims

- Realtime agent-based racing engine that provides per-frame position updates and discrete events (DNF, lap complete) via a callback interface.
- Discipline modules allowing per-discipline configuration (rules, scoring, vehicle characteristics).
- Compact driver/team data model supporting core attributes, career metadata and contract information.
- REST API endpoints for simulation orchestration and data access, plus a minimal PyQt6 GUI for visualization and manual playtesting.
- Team/staff systems (budget, operations rating, strategy profiles) that influence race performance and long-term progression.
- Playtesting and tuning tools: scripts to run short scenarios, collect logs and compare metrics (DNFs, position volatility, lap times).
What does the project aim to achieve?

High-level aims:
- Broader coverage: build a single platform that supports multiple disciplines so gameplay and balance can be compared across formats instead of being limited to one archetype.
- Depth over novelty: focus on delivering detailed management systems (contracting, staff impact, budget scaling and vehicle setup) and credible on-track behaviour rather than pursuing research-oriented exploration.
- Practical deliverability: use a Python-based, single-repository approach (SQLite persistence, FastAPI, PyQt6) so the project can be developed, tested and demonstrated on a standard development machine without heavy infrastructure.

Planned features (concise):
- Realtime agent-based racing engine that provides per-frame position updates and discrete events (DNF, lap complete) via a callback interface.
- Discipline modules allowing per-discipline configuration (rules, scoring, vehicle characteristics).
- Compact driver/team data model supporting core attributes, career metadata and contract information.
- REST API endpoints for simulation orchestration and data access, plus a minimal PyQt6 GUI for visualization and manual playtesting.
- Team/staff systems (budget, operations rating, strategy profiles) that influence race performance and long-term progression.
- Playtesting and tuning tools: scripts to run short scenarios, collect logs and compare metrics (DNFs, position volatility, lap times).
- Realtime agent-based racing engine that provides per-frame position updates and discrete events (DNF, lap complete) via a callback interface.
- Discipline modules allowing per-discipline configuration (rules, scoring, vehicle characteristics).
- Compact driver/team data model supporting core attributes, career metadata and contract information.
- REST API endpoints for simulation orchestration and data access, plus a minimal PyQt6 GUI for visualization and manual playtesting.
- Team/staff systems (budget, operations rating, strategy profiles) that influence race performance and long-term progression.
- Playtesting and tuning tools: scripts to run short scenarios, collect logs and compare metrics (DNFs, position volatility, lap times).

Technology

What technology will be used and how (based on the repository and requirements)?

Core stack (from `Momentum/Python/requirements.txt` and codebase):
- Python 3.13 — runtime and development.
- FastAPI + Uvicorn — API server and orchestration (`simulation.py`).
- SQLite — lightweight persistence (schema & dataclasses live in `database/models.py`).
- NumPy, pandas, SciPy — numeric libraries used for physics-like calculations and analysis.
- PyTorch (`torch`) — available for experimental AI models (strategy/decision networks) if needed.
- PyQt6 — GUI toolkit used for the launcher and race visualiser.
- Pydantic — data validation for API schemas.
- Faker, python-dotenv, requests — utilities for data generation and environment/config handling.
- Shapely, bezier — geometry libraries used for track/visual geometry utilities.

How these technologies map to planned features:
- The realtime engine is a Python module that will be invoked by either the API or GUI; it emits structured events consumed by the GUI and by test harnesses.
- FastAPI provides a small orchestration layer for starting/stopping simulations and returning persistent race results.
- SQLite keeps the project portable and easy to distribute; its SQL schema is maintained as `SCHEMA_SQL` in `database/models.py`.

Structure

Document layout and purpose of each section (headings):
- Section 1 — Introduction: motivations, planned aims, and technology choices (this section).
- Section 2 — System Design: detailed architecture, module descriptions (`RaceLogic/`, `disciplines/`, `database/`, `GUI/`), interfaces and configuration points.
- Section 3 — Implementation Notes: file-by-file notes, configuration variables (in `config.py`), and developer instructions to run the GUI and API locally.
- Section 4 — Roadmap & Milestones: prioritised list of tasks, acceptance criteria and time estimates for milestones (game loop, save/load, track import, staff systems).
- Section 5 — Risks & Mitigations: technical and project risks (e.g., first-lap incident rates, test coverage) and concrete mitigation steps.
- Section 6 — Evaluation Plan: playtesting methodology, metrics to gather, and sample tuning experiments.
- Appendices — Code snippets, sample run logs, and developer setup notes.

This introduction is intentionally concise: later sections will expand on the module-level design, show example configuration, and record tuning experiments and their results.


