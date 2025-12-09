Project Analysis — Rubric Coverage and Evidence

This document summarises how the current repository maps to the assessment rubric you provided. For each rubric area I list the evidence found in the repo, a short assessment of coverage (Covered / Partial / Missing), and recommended next steps that raise the quality of evidence for assessors.

1. Executive summary

- Purpose: give assessors a one‑page view of aims, methods, principal results and conclusions.
- Evidence in repo: `Planning/Technical Report/Contents.md`, `Planning/Technical Report/Introduction/introduction.md`, `README.md`.
- Assessment: Partial — the README and Introduction provide context, but there is no single polished one‑page Executive Summary file suitable for marking.
- Recommendation: add `Planning/Technical Report/Executive_Summary.md` (one page) summarising aims, approach, key results and main conclusions.

2. Project Proposal (15%)

- Evidence:
  - `Planning/Technical Report/Proposal/Proposal Draft.md`
  - Planning notes in `Planning/*` and `README.md` background sections.
- Assessment: Covered (draft exists). The proposal contains research, motivation and scope; may need refinement for final submission.
- Recommendation: produce a final version (polished language, clear aims/objectives, one-page summary for assessors) and place it as `Planning/Technical Report/Proposal/Proposal_Final.md`.

3. Communication Skills (10%)

- Evidence:
  - `Planning/Midpoint Presentation/presentation_plan.md` (slide plan, demo script)
  - Diagrams in `Planning/Technical Report/diagrams/` and `Planning/Design and Architecture/` (draw.io and exports)
- Assessment: Partial — planning and diagrams are strong, but the final slide deck and a sample demo recording are not present in the repo.
- Recommendation: add `Planning/Midpoint Presentation/Slides.pdf` and a short demo video `Planning/Midpoint Presentation/demo_short.mp4`. Also add speaker notes and a short rehearsal checklist.

4. Project Analysis & Planning (10%)

- Evidence:
  - `Planning/` folder: schedules, `update_dates*.ps1`, milestone notes, design diagrams and use case planning.
  - `Planning/Technical Report/Contents.md` and `introduction.md` show planned structure and mapping.
- Assessment: Covered — conceptual diagrams, scheduling and milestone files exist.
- Recommendation: add a short trace that links specific high‑risk tasks to mitigation steps (e.g., "DNF tuning" → diagrams → tuning plan → tests) to make the mapping explicit.

5. Requirements Engineering (40%)

- Evidence:
  - Use cases: `Planning/UseCases/*`, exported diagrams in `Planning/UseCases/exports/`.
  - Data model: `Momentum/Python/database/models.py` (dataclasses and `SCHEMA_SQL`).
  - `Planning/Technical Report/Contents.md` enumerates functional and non‑functional sections.
- Assessment: Strong coverage — documented use cases, data schema and detailed TOC are present. This area is well supported.
- Recommendation: create a Requirements Traceability Matrix (RTM) file: `Planning/Technical Report/Requirements_Traceability.md` mapping requirement id → implementing module(s) → test(s) → status.

6. Prototype (25%)

- Evidence:
  - GUI and run scripts: `Momentum/Python/GUI/gui_game.py`, `Momentum/Python/GUI/launcher.py`, `Momentum/Python/GUI/gui_race_visual.py`.
  - Simulation engine: `Momentum/Python/RaceLogic/realtime_race_engine.py` and `simulation.py`.
  - DB and seed scripts: `scripts/generate_and_seed_db.py` and related scripts.
  - Tests: `Momentum/Python/tests/*` and `archive/basic-race-legacy/tests/*`.
- Assessment: Covered — runnable prototype exists, but a short reproducible demo asset (screencast, test-run logs, or screenshots) would make it easier for an assessor to verify functionality quickly.
- Recommendation: add `Planning/Midpoint Presentation/demo_evidence.md` with explicit run commands and expected outputs; include a screenshot and short MP4 demo.

7. Testing and Evaluation (supporting material)

- Evidence:
  - Unit and integration tests in `Momentum/Python/tests/` and legacy archive.
  - `Planning/Testing/Plan.md` describes manual/automation testing approaches.
  - Playtesting notes: `Reflections/Reflection December.md`, logs in `logs/`.
- Assessment: Partial — test code exists, and plans are documented. However, concise test result summaries, graphs or metric tables are not yet collated into a results appendix.
- Recommendation: add `Planning/Technical Report/Test_Results.md` summarising key metrics (e.g., DNF counts per lap pre/post tuning, unit test pass rates). Export simple plots or tables (CSV + PNG) into `Planning/Technical Report/assets/`.

8. Reflective journals and supplementary materials

- Evidence: `Reflections/Reflection December.md` and other notes in `Planning/`.
- Assessment: Covered — reflective material exists for appendices.
- Recommendation: ensure each reflection references the date and work performed and add them as appendices in the final report.

9. Diagrams and architecture

- Evidence: draw.io/exports in `Planning/Technical Report/diagrams/` and `Planning/Design and Architecture/`.
- Assessment: Covered — diagrams are present in editable forms and exports.
- Recommendation: embed selected diagrams directly into the final `Technical Report` markdown files to ensure assessors can view them without opening draw.io.

Actionable next steps (priority order)

1. Create a short one‑page Executive Summary: `Planning/Technical Report/Executive_Summary.md` (high impact for assessors).  
2. Add final slide deck and a 60–90s screencast of the Quick Race demo to `Planning/Midpoint Presentation/` (addresses Communication Skills).  
3. Produce Requirements Traceability Matrix: `Planning/Technical Report/Requirements_Traceability.md` (addresses Requirements Engineering).  
4. Add Test Results appendix summarising metrics and any outstanding issues: `Planning/Technical Report/Test_Results.md`.  
5. Create `Planning/Midpoint Presentation/demo_evidence.md` with explicit run commands, screenshots and expected console/log snippets (helps prototype marking).  

Notes on reproducibility

- To reproduce the demo locally: use the commands in `README.md` or `Planning/Testing/Plan.md`. Key entries: `python -m venv .venv` → `pip install -r Momentum/Python/requirements.txt` → `python Momentum/Python/GUI/launcher.py` (or `python Momentum/Python/GUI/gui_game.py`).  
- If you want, I can add an automated script that launches a headless short-run harness and collects DNF/telemetry metrics for rapid iteration (useful for test results appendix).

Conclusion

The repository contains substantial evidence across the major rubric categories: proposal material, planning and diagrams, use cases and data models, a working prototype, and tests. The highest‑value additions to maximise marks are a concise Executive Summary, a final slide deck and short demo video, a Requirements Traceability Matrix, and a short test results appendix with clear metrics. I can produce any of those files next — please tell me which to create first.
