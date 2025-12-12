# Midpoint Presentation Plan

Project: Momentum - Multi-Discipline Motorsport Management Simulator
Presenter: Eoin Fitzsimons
Date: 12 December 2025
Duration: 3 minutes + Q&A

---

## Five-Slide Deck (Speaker Notes & Rubric Mapping)

Slide 1 - Title

- Title: Momentum - Multi-Discipline Motorsport Management Simulator
- One line: Presenter: Eoin Fitzsimons - passionate about motorsport and sports simulation games
- Presenter to say: concise elevator pitch and a brief factual note: "Prototype developed via iterative tests and targeted refactors (see repo commits)."
- Rubric: Communication, Proposal

Slide 2 - The Past - What Compares?

- What: historical context and comparable titles (Motorsport Manager, F1 Manager) and lessons from legacy scripts and playtests.
- Presenter to state: how historical analysis and legacy code audits shaped priorities (see `logs/commits_november_2025.md`).
- Rubric: High Level Analysis, Proposal

Slide 3 - The Present - The MVP

- What: current MVP - playable quick-race, core engine, MVP tests, archived legacy code and data artifacts.
- Audience: early testers and demonstrators; intended user feedback loop.
- Current scope: quick race, telemetry, import scripts; limitations: incomplete season flow and save/load.
- Rubric: Proposal, Project Analysis & Planning

Slide 4 - The Future - What Will Come?

- Roadmap: CI with seeded tests, packaging via `scripts/build_exe.py`, performance improvements (vectorize, multiprocessing), and full season/game loop completion.
- Dev actions: complete `systems/game_loop.py`, extend `tests/test_playability.py` for CI, validate full DB import.
- Rubric: Technology & Tools, Preliminary Data Analysis

Slide 5 - Demo + Next Steps

- Demo: Quick Race (RaceWindow HUD and telemetry). Fallback: pre-generated telemetry JSON and screenshots.
- Next milestones (2-4 weeks): finish `systems/game_loop.py`, add CI seeded tests, run `scripts/build_exe.py`.
- Ask: time for CI runs and a short packaging sprint.
- Rubric: Prototype, Supporting Technology, Project Analysis
