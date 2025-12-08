# Midpoint Presentation Plan

**Project:** Momentum — Multi-Discipline Motorsport Management Simulator
**Presenter:** Eoin Fitzsimons
**Date:** 12 December 2025
**Duration:** 3 minutes + Q&A

---

## Overview

Concise, practiceable presentation plan for the 3-minute midpoint demo. Includes a short 4-slide demo outline, demo script timings, technical setup checklist and backup options.

---

## 4-Slide Presentation (3 minutes total)

- **Slide 1 — Title:** Project name, author, date. Speaker note: one-line intro and elevator pitch.
- **Slide 2 — Problem & Motivation:** Market gap and why Momentum matters. Speaker note: 1–2 concise bullets.
- **Slide 3 — MVP Highlights:** What works now (engine, data scale, prototype capabilities). Speaker note: bullet the key deliverables — no live demo actions on this slide.
- **Slide 4 — Future & Ask:** Immediate next milestone and resources requested.

Keep slides tightly focused — slides are the 3-minute presentation. Do not perform any live application actions during the slide deck.

---

## Post-slides Live Demo (separate, NOT part of the 3-minute slot) — Script (60 seconds)

- [0:00–0:10] Quick Race setup (post-slides): select discipline and driver — Speaker prompt: "Now I'll run a short Quick Race to demonstrate the prototype." 
- [0:10–0:35] Run the Quick Race: show `RaceWindow` HUD, push/pacing controls and one incident/overtake — Speaker prompt: "Observe push intensity, tyre wear and on-track events." 
- [0:35–0:50] Summary & telemetry: open persisted trace / results summary — Speaker prompt: "Telemetry is saved for replay and analysis." 
- [0:50–1:00] Short technical callout and wrap: threading, reproducibility options — Speaker prompt: "Engine emits events (~30Hz); seedable for deterministic QA runs."

Note: this live demo is additional to the 3-minute slide time. Practice the slide→demo transition to keep the presentation itself within the allotted slot.

---

## Key Slides (visual aids)

- Slide 1: Title + one-line elevator pitch, project logo (if available).
- Slide 2: One compact architecture diagram (backend, engine, GUI) and one bullet on extensibility (Abstract Discipline Engine).
- Slide 3: Single screenshot of `RaceWindow` with HUD callouts and two inline notes: push controls + telemetry filename.
- Slide 4: Roadmap bullets (team UX, championship system, save manager) and the single next milestone.

Recommended images: `Planning/Technical Report/Proposal/Wireframes/fig_03_ui_main.png` and `fig_04_ui_home.png` (use fig_03 on Slide 3).

---

## Technical Setup Checklist (important to run before demo)

Run these steps ~10–30 minutes before presenting:

```powershell
# From project root
cd c:\Users\eoin0\Documents\Code\FinalProject\FinalProject\Momentum\Python

# Start backend (if needed by GUI)
python -m uvicorn simulation:app --reload

# Launch the application launcher (recommended). Note: `launcher.py` activates the virtualenv internally.
python GUI/launcher.py
```

Quick verifications:
- Verify `logs/telemetry` contains a recent trace (or pre-create one to show if needed).
- Preconfigure Quick Race to avoid spending time in menus.

Backup materials:
- Screenshots of the demo flow (driver browser, race window, results).
- Pre-generated CSV/JSON of a race result to show if live demo fails.

Notes for switching to the live demo after slides:
- Option A (recommended): Pre-launch the `launcher.py` and have the Quick Race pre-configured and paused on the race setup screen. After finishing Slide 4, switch to the GUI and start the demo immediately.
- Option B: If you prefer not to pre-launch, keep the backend running and launch `python GUI/launcher.py` during the brief slide transition; this risks a small delay — practice the sequence once.
- Ensure projector input switching is tested so you can smoothly move from slides to the running application.

---

## Talking Points & Anticipated Questions (short)

- Differentiator: multi-discipline persistent world vs single-discipline competitors.
- Architecture: Abstract discipline engine enables adding new racing types without core changes.
- Procedural generation: deterministic, rule-based pipeline for scale and realism.

Anticipated Q&A: balance of generated drivers, deterministic testing (seed), UI choice (PyQt6 vs web). Keep answers short and reference the repo/docs for detail.

---

## Post-Presentation Actions

- Capture feedback and update `Technical Report/Technical_Report.md` and slide notes.
- Add any demo failures and fixes to the repo's `logs/commits_november_2025.md` or a new `presentation_postmortem.md`.

---

## Contacts & Links

- Repo: https://github.com/EoinFitzsimons/FinalProject
- Main demo entry: `Momentum/Python/GUI/gui_game.py`
- Simulation API: `Momentum/Python/services/race_simulation_api.py`
- Technical report: `Technical Report/Technical_Report.md`

---

*Prepared for a 3-minute midpoint demo. Practice at least twice with the exact machine and projector setup.*

