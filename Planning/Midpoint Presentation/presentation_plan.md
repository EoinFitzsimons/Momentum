# Midpoint Presentation Plan

**Project:** Momentum - Multi-Discipline Motorsport Management Simulator  
**Presenter:** Eoin Fitzsimons  
**Date:** 12 December 2025  
**Duration:** 3 minutes + Q&A  

---

## Presentation Structure

### 1. Opening (20 seconds)
- **Project title and elevator pitch**
  - "Momentum: A comprehensive motorsport management simulator spanning 7 racing disciplines"
  - Problem: Existing games focus on single disciplines (F1 Manager, WRC) — no unified multi-discipline experience
  - Solution: Event-driven race simulation with extensible architecture for diverse motorsport categories

### 2. Technical Architecture (40 seconds)
- **Core components overview**
  - Python FastAPI backend (REST API)
  - SQLite persistent world (1,781 drivers, 1,095 teams, 175 circuits)
  - PyQt6 desktop GUI (midpoint demo)
  - Event-driven race simulation engine

- **Key architectural decision: Abstract Base Discipline Engine**
  - Inheritance pattern allows adding new disciplines without modifying core logic
  - Each discipline (Single Seater, Rally, Endurance, etc.) implements `simulate_race()` with discipline-specific rules
  - Shared performance calculation, weather, and track condition systems

### 3. Procedural Content Generation (40 seconds)
**Critical clarification on terminology:**

- **Not runtime generation** — pre-generation at database initialization
- **Not random** — controlled, rule-based generation with validation

**How it works:**
- **Define design rules:** Attribute distributions, correlations, constraints (e.g., `raw_speed` correlates with `qualifying_pace`, r > 0.7)
- **Algorithm executes rules:** Generates entities (drivers, teams, circuits) within your design space
- **Validation gates:** Statistical tests (Shapiro–Wilk normality, correlation checks) reject invalid entities
- **Iterative tuning:** Adjust rules → regenerate → validate → repeat until output matches design vision

**Developer control:**
- Distributions (mean, standard deviation)
- Correlations between attributes
- Cultural authenticity rules (Faker locales for realistic names)
- Budget tiers, salary scales, discipline specializations
- Acceptance thresholds for validation

**Why this approach:**
- **Scale:** 1,781 drivers vs. manually typing 50
- **Consistency:** Rules applied uniformly across thousands of entities
- **Realistic distributions:** Not uniform noise — real-world talent curves
- **Flexibility:** Regenerate entire database with adjusted rules in minutes

**Academic framing:** "Authoring through algorithm" — parameterized deterministic generation where designer defines creative rules, system executes at scale (Shaker et al., 2016)

### 4. Live Demo (60 seconds)
**Working prototype walkthrough:**

- **Driver Browser**
  - Search/filter 1,781 drivers by name, discipline, attributes
  - Show attribute detail panel (50+ attributes across 7 categories)
  - Demonstrate cultural name diversity (24 Faker locales)

- **Race Configuration**
  - Select discipline (Single Seater demo)
  - Choose circuit from 175 available
  - Pick drivers/teams for grid
  - Set weather and track conditions

- **Simulation Execution**
  - Start race simulation
  - Show progress indicator (event-driven lap-by-lap processing)
  - Display real-time on-track visualisation (2D dots around track)
  - Demonstrate dynamic events (overtakes, tyre wear, pit stops)

- **Results Display**
  - Final classification with lap times
  - Performance breakdown by driver/team
  - Championship points allocation

### 5. Project Status & Next Steps (20 seconds)
**Completed (Midpoint):**
- Core simulation engine (Monte Carlo, event-driven)
- Database schema and initial data generation (validated)
- Working PyQt6 prototype demo
- Abstract discipline architecture (7 disciplines designed, 3 implemented)

**Remaining for Final Submission (May 2026):**
- Complete all 7 discipline simulators
- Championship/season progression system
- Staff management and contracts
- Enhanced 3D visualisation (post-graduation stretch goal)
- Performance optimisation and testing

---

## Key Talking Points

### Differentiation from Existing Games
- **F1 Manager 2024:** Single discipline only
- **Motorsport Manager:** Limited to 3 categories, discontinued
- **Momentum:** 7 disciplines with unified persistent world and cross-discipline career progression

### Technical Challenges Addressed
1. **Extensibility:** How to add new disciplines without breaking existing code?
   - Solution: Abstract base class inheritance pattern
2. **Realism vs. Performance:** How to simulate detailed physics without sacrificing speed?
   - Solution: Monte Carlo statistical simulation with event-driven incidents
3. **Content Scale:** How to populate a world with thousands of entities?
   - Solution: Controlled procedural generation with validation

### Academic Contributions
- Application of procedural content generation to sports simulation
- Multi-agent systems (drivers, teams, staff as autonomous entities)
- Statistical validation of generated content (Shapiro–Wilk, correlation analysis)

---

## Visual Aids

### Slide 1: Title & Problem Statement
- Project logo/title
- Market gap: No unified multi-discipline motorsport manager

### Slide 2: Architecture Diagram
- Component overview (Backend, Database, GUI, Simulation Engine)
- Abstract Base Discipline Engine pattern (UML inheritance diagram)

### Slide 3: Procedural Generation Pipeline
- Flowchart: Define Rules → Generate → Validate → Tune → Accept
- Example: Driver generation with attribute correlations

### Slide 4: Database Scale
- Numbers: 1,781 drivers, 1,095 teams, 175 circuits, 57,936 staff
- Discipline distribution chart

### Slide 5: Live Demo Screenshot
- PyQt6 prototype interface (driver browser, race config, results)

### Slide 6: Timeline & Milestones
- Completed: Core engine, database, prototype
- Remaining: Full discipline suite, season progression, optimisation

---

## Anticipated Questions & Answers

**Q: Why 7 disciplines? Isn't that scope creep?**
A: The abstract base class architecture makes adding disciplines low-cost once the pattern is established. Each discipline is ~300 lines of discipline-specific logic inheriting from the shared base. The engineering challenge was designing the extensible architecture, not implementing each discipline.

**Q: How do you ensure generated drivers are balanced?**
A: Three-stage validation: (1) Statistical tests on distributions (Shapiro–Wilk for normality), (2) Correlation checks between related attributes, (3) Gameplay testing with performance metrics. Reject and regenerate entities that fail thresholds.

**Q: Why PyQt6 instead of web-based UI?**
A: Desktop-first for midpoint to demonstrate full simulation without network latency concerns. FastAPI backend allows future web/mobile clients without changing core logic. PyQt6 provides mature widget library for complex data visualisation.

**Q: What's the performance bottleneck?**
A: Monte Carlo iterations (currently 10,000 per race). Optimisation strategies for final submission: (1) Cython compilation of hot loops, (2) Caching common calculations, (3) Parallel race simulation for championships.

**Q: How do you avoid copyright issues with real circuits/teams?**
A: All content procedurally generated with collision detection against real-world trademarks. Circuit characteristics inspired by real-world patterns but names/branding are synthetic. No licensed content used.

---

## Demo Script (60 seconds timing)

**[0:00–0:15] Driver Browser**
"The database contains 1,781 procedurally generated drivers with culturally authentic names from 24 locales. Each driver has 50+ attributes across technical, mental, physical, and racecraft categories. Let me search for a high-performing Single Seater specialist..." [Filter by discipline, sort by raw_speed]

**[0:15–0:30] Race Configuration**
"I'll configure a Single Seater race at [select iconic circuit from 175 available]. The race setup allows weather conditions, track temperature, and grip level adjustments. I've selected 20 drivers from top-tier teams for the grid..." [Show grid lineup]

**[0:30–0:50] Simulation Execution**
"Starting the race simulation — this is event-driven, processing lap-by-lap with dynamic incidents. You can see the 2D visualisation tracking positions around the circuit. Watch for overtakes, tyre degradation, and pit stop strategy playing out in real time..." [Progress indicator, on-track dots moving]

**[0:50–1:00] Results**
"Race complete. Final classification shows realistic spread based on driver/team performance. Championship points allocated, and all data persists to the database for ongoing career progression." [Results table]

---

## Presentation Delivery Notes

### Tone & Style
- Professional but accessible (final year student presenting to academics and peers)
- Emphasise engineering decisions and trade-offs
- Avoid jargon without explanation (define "Monte Carlo", "event-driven" briefly)

### Pacing
- Speak clearly at moderate pace (~140 words/minute for 3-minute slot)
- Practice demo to ensure 60-second timing (set up race config beforehand to save time)
- Have backup slides ready if demo fails (screenshots of working prototype)

### Engagement
- Make eye contact, not reading slides
- Use pointer/mouse to highlight key UI elements during demo
- Pause for brief questions during demo if time allows

---

## Technical Setup Checklist

### Pre-Presentation (1 hour before)
- [ ] Start FastAPI backend (`uvicorn simulation:app --reload`)
- [ ] Verify database connectivity (run `scripts/verify_database.py`)
- [ ] Launch PyQt6 GUI (`python gui/gui_game.py`)
- [ ] Pre-configure race setup (select circuit, drivers, weather) to save demo time
- [ ] Test race simulation end-to-end (ensure <30 second completion)
- [ ] Close unnecessary applications (free RAM, reduce distraction)

### Backup Plan
- [ ] Prepare screenshots of working demo in case of live failure
- [ ] Have codebase open in VS Code to show architecture if needed
- [ ] Save pre-run race results as CSV for display if simulation fails

### Equipment
- [ ] Laptop fully charged + power adapter
- [ ] HDMI/DisplayPort adapter for projector
- [ ] Mouse (easier to navigate GUI than trackpad)
- [ ] Water bottle (stay hydrated during Q&A)

---

## Post-Presentation Actions

### Feedback Collection
- Note all questions asked (especially repeated themes)
- Record suggestions for final submission improvements
- Identify unclear explanations that need better articulation

### Documentation Updates
- Update technical report Section 2.2 (Design & Implementation) based on feedback
- Refine procedural generation explanation if terminology confusion observed
- Add clarifications to project README

### Next Development Priorities (based on presentation)
1. Complete remaining 4 discipline simulators (Rally, Endurance, Urban, Drag)
2. Implement championship progression system
3. Add staff management UI screens
4. Performance profiling and optimisation
5. Expand test coverage (target 80% code coverage)

---

## References for Presentation

### Citations to Include
- **Shaker et al. (2016)** - Procedural Content Generation taxonomy
- **Sports Interactive (2019)** - Football Manager simulation architecture (GDC talk)
- **Silver (2012)** - Statistical prediction and Monte Carlo methods
- **Wooldridge (2009)** - Multi-agent systems design patterns

### Technical Documentation Links
- FastAPI: https://fastapi.tiangolo.com/
- PyQt6: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- SQLite: https://www.sqlite.org/docs.html
- NumPy: https://numpy.org/doc/ (statistical distributions)

---

## Accessibility Considerations

### Slide Design
- High contrast text (dark background, white/yellow text)
- Large font sizes (minimum 24pt for body text)
- Avoid red/green color combinations (colorblind-friendly palette)
- Include alt text for all diagrams in slide notes

### Demo Accessibility
- Verbally describe UI actions while performing them
- Use screen reader–compatible widget labels in PyQt6
- Provide text-based result summaries alongside visualisations

---

## Timeline

**Week of 9 Dec:**
- Finalize prototype features (driver browser, race config, simulation, results)
- Create presentation slides (6 slides, ~30 minutes to produce)
- Practice full presentation 3x (refine timing and transitions)

**11 Dec:**
- Final dress rehearsal with timer
- Prepare backup materials (screenshots, code examples)
- Test equipment setup (projector connection, audio if needed)

**12 Dec (Presentation Day):**
- Arrive early for technical setup
- Run through demo sequence once before presenting
- **Deliver presentation**
- Collect feedback and questions

---

## Success Criteria

### Minimum Viable Presentation
- [ ] Clear problem statement and solution overview
- [ ] Demonstrate working prototype (driver browser + race simulation)
- [ ] Explain one key technical decision (Abstract Base Discipline Engine)
- [ ] Stay within 3-minute time limit
- [ ] Answer at least 2 questions competently

### Stretch Goals
- [ ] Articulate procedural generation approach clearly (avoid "random" misconception)
- [ ] Show compelling on-track visualisation during race
- [ ] Demonstrate cultural name diversity and data scale
- [ ] Receive positive feedback on architecture extensibility
- [ ] Generate interest in final submission features

---

## Notes & Observations

*(Add notes during practice runs and after presentation delivery)*

### Practice Run 1 (Date: _______)
- Timing: _____
- Issues identified:
- Improvements needed:

### Practice Run 2 (Date: _______)
- Timing: _____
- Issues identified:
- Improvements needed:

### Practice Run 3 (Date: _______)
- Timing: _____
- Issues identified:
- Improvements needed:

### Actual Presentation (12 Dec 2025)
- Audience size: _____
- Questions asked:
- Feedback received:
- Technical issues (if any):
- Self-assessment:

---

## Contact & Resources

**Project Repository:** https://github.com/EoinFitzsimons/FinalProject  
**Supervisor:** [Name]  
**Email:** [Your NCI email]  

**Additional Materials:**
- Technical Report (in progress): `Technical Report/Technical_Report.md`
- Game Design Document: `Momentum/GAME_DESIGN_DOCUMENT.md`
- Playability Status: `Momentum/PLAYABILITY_STATUS.md`
- Use Cases: `UseCases/All_Use_Cases_Detailed.md`
