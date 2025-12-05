
National College of Ireland

Project Proposal

Momentum: Multi-Discipline Motorsport Management Simulator

2nd December 2025

Computing - Software Development

2025/2026

Eoin Andrew Fitzsimons

X23151374

X23151374@student.ncirl.ie

Objectives

Momentum will create a multi-discipline motorsport management simulator addressing the current market gap between Football Manager's depth and existing motorsport titles' limited scope. From building open wheelers that stick at full speed around circuit turns driven by aerodynamic downforce, to rally racing through blizzards whilst managing snow tyre condition and co-driver pace notes, the system encompasses the breadth of competitive motorsport within a unified framework. A persistent world enables emergent narratives as all championships progress simultaneously regardless of player focus.

Core Technical Goals:

Real-time agent-based race simulation at 30 FPS with AI decision-making and spatial awareness

Procedural championship generation with automated balance validation

Multi-discipline architecture using abstract base classes for code reuse

Desktop GUI enabling race-by-race player interaction with live car movement visualization

Novel Contributions:

Extensible discipline engine architecture enabling new racing categories without core simulation rewrites

Automated procedural validation ensuring competitive balance through statistical testing

Python-based implementation demonstrating complex multi-league simulation without enterprise engines

Background

Having invested 6,890 hours in Football Manager since 2015, I recognise its appeal stems from emergent simulation depth rather than football itself. Existing motorsport managers fail to replicate this despite motorsport's global following (F1: 445M viewers, WRC: 800M cumulative audience). F1 Manager 2024 achieves only 14.7 hours median playtime versus Football Manager's 89.3 hours, whilst Motorsport Manager (446K sales, abandoned 2017) proved multi-discipline appetite but failed on execution.

Meeting Objectives:

**Real-Time Race Simulation:** Will implement continuous 30 FPS agent-based simulation where AI drivers make frame-by-frame decisions based on race situation (gaps, position, tire condition, fuel load). Driver attributes (50+ per individual) will influence physics calculations, AI behavior, and spatial awareness. Drivers will actively choose racing modes (ATTACK/DEFEND/MANAGE/CRUISE) based on gaps to nearby cars and their own skills (overtaking, defensive_driving, tire_management). On-track view will display live car movement with position tracking updated every frame. Validation tests will verify AI decision-making responds correctly to race situations and position updates maintain 30 FPS performance.

**Competitive Balance:** Will implement automated validation through simulated seasons, flagging extreme imbalances (single team >40% wins, failed normality tests). Developer tuning will establish competitive orders that evolve through comprehensive development systems and regulation changes, mirroring real motorsport dynamics.

**Extensible Architecture:** Will define abstract base class simulation interface (simulate_race(), calculate_performance_weights()). New disciplines will inherit this foundation without modifying core engine, demonstrating software engineering principles for complex domain modelling.

**Persistent World:** Will use SQLite database to track all entities (drivers, teams, tracks, championships) with career progression driven by performance vs expectations, contract cycles, and hidden potential curves. All leagues will advance concurrently regardless of player focus.

State of the Art

| Title                                     | Strengths                                                                                     | Critical Gaps                                                                                                 |
| ----------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Football Manager 2024(Sports Interactive) | 143 leagues, persistent world, emergent narratives, 1,000+ hour engagement, extensive modding | Team sport structure incompatible with motorsport, licensing model unsuitable                                 |
| F1 Manager 2024(Frontier)                 | Authentic presentation, detailed development mechanics, real-time decisions                   | Predictable AI, linear progression, single discipline (F1/F2), static driver potential, 14.7h median playtime |
| Motorsport Manager(Playsport, 2016)       | Multi-discipline framework, accessible pricing, fictional universe                            | Static world (no procedural generation), small scale (200 drivers), abandoned 2017                            |

How Momentum Differentiates:

Procedural Generation vs Static Content: Existing titles use handcrafted rosters with limited scale (F1 Manager: 44 drivers, Motorsport Manager: 200). Momentum generates drivers/teams/championships algorithmically with hidden potential enabling larger roster depth (1,000+ drivers) and emergent narratives.

Extensible Architecture vs Monolithic Design: Adding new racing categories to F1 Manager or Motorsport Manager requires fundamental rewrites. Momentum's abstract base class architecture enables new disciplines through inheritance without touching core simulation logic.

Extensible Architecture vs Monolithic Design: Adding new racing categories to F1 Manager or Motorsport Manager requires fundamental rewrites. Momentum's abstract base class architecture enables new disciplines through inheritance without touching core simulation logic.

Open Architecture: Python/SQLite stack with GPL licensing enables academic transparency and potential community extensions, contrasting with proprietary closed engines.

Technical Approach

Architecture:

Backend: Python + FastAPI REST API, SQLite database, async request handling

Frontend: PyQt6 desktop GUI with direct Python integration and native UI components

Rationale: Prioritises simulation depth over visual spectacle, enables rapid prototyping, eliminates licensing costs

Multi-Discipline Engine (Target Implementation):

RealtimeRaceEngine class will provide continuous 30 FPS simulation with physics-based speed calculations and AI decision-making. Each discipline will extend this base with discipline-specific logic.

Physics formula per frame (to be implemented): speed_mps = base_speed × (driver_skill × team_performance × push_intensity × tire_penalty × fuel_bonus × slipstream × corner_factor)

AI Decision-Making: Drivers will analyze race situation every frame and select racing mode based on gaps (ATTACK if gap_ahead < 1.0s, DEFEND if gap_behind < 0.5s, MANAGE for tire conservation, CRUISE when comfortable)

Planned discipline differentiation:

- **Single-Seater:** Aerodynamics, slipstream effects, cornering_skill emphasis
- **Rally:** Surface adaptation, co-driver communication, pace notes  
- **Endurance:** Tire/fuel management, consistency over speed, mechanical_sympathy
- **Drag:** Reaction time, acceleration_control, launch technique
- **Street Racing:** Urban circuits, damage risks, spectator interaction
- **Rallycross:** Mixed surface transitions, controlled chaos, adaptability
- **Production/Touring:** Balance of performance, reliability emphasis, accessibility

Real-Time Continuous Simulation (Target Implementation):

Physics-based simulation will run at 30 FPS (0.033s timestep) with continuous position updates, speed calculations, and AI decision-making. Driver attributes will directly influence speed (raw_speed, cornering_skill, consistency), AI behavior (overtaking, defensive_driving, racecraft), and degradation (tire_management, mechanical_sympathy). Spatial awareness system will track gaps to nearby cars (<100m), detect slipstream opportunities (<50m), and enable AI to respond to race situations. On-track view will visualize live car movement with position updated every frame. 2D track visualization will show cars moving around circuit in real-time, enabling player observation of strategy and AI decision-making.

Procedural Generation (Planned for Final Implementation):

Championships will be generated with three-tier budget distribution (Tier 1: 90-100% cap, Tier 2: 60-80%, Tier 3: 40-60%). Drivers will be generated with base attributes 40-60, specialisation boosts, and hidden potential curves. Teams will be procedurally created with realistic capability profiles.

Validation: Automated testing will run 1,000 simulated seasons verifying competitive balance (no team >40% wins, normal distribution of outcomes, realistic performance spread).

Cultural authenticity will be ensured via Faker library (24 locales) to provide regional naming patterns per discipline, creating authentic-feeling fictional universes.

Technical Details

Implementation Language and Libraries:

Backend: Python 3.11, FastAPI (async REST API), SQLite (embedded database), NumPy/SciPy (statistical calculations), Faker (multi-locale name generation), Pydantic (data validation)

Frontend: PyQt6 (desktop GUI), Matplotlib (data visualisation), Qt Designer (UI prototyping)

Development: Git/GitHub (version control), Black (code formatting), mypy (type checking), pytest (testing)

Database Design:

Normalised schema (3NF) with seven core entities:

Driver: 50+ attributes across technical, mental, physical, racecraft, and discipline-specific categories (0-100 scale)

Team: Budget, discipline, vehicle performance, facility ratings

Track: Dimensions, surface, IMA grading, compatible disciplines

Championship: Calendar, points system, budget cap, technical regulations

Race, RaceResult, Staff: Supporting entities for event management

Foreign key constraints enforce referential integrity. Indexes on frequently queried columns (discipline, rating, team_id).

API Structure:

REST endpoints for race simulation (POST /simulate/race), championship management (POST /season/create, GET /season/standings), and entity queries (GET /drivers, /teams, /tracks). OpenAPI documentation auto-generated.

Testing Approach (Target for Final Submission):

Unit Tests: Attribute calculations, physics formula verification, database operations (80% coverage target)

Integration Tests: Full race workflows, championship progression, multi-discipline consistency, player control responsiveness

Performance Tests: Concurrent race handling, memory profiling, query optimisation, frame-rate consistency (30 FPS sustained)

Statistical Validation: Normal distribution verification (Shapiro-Wilk test), correlation analysis (r > 0.7), competitive balance metrics

User Acceptance: 5-10 testers evaluating realism, engagement, balance, longevity

Special Resources Required

Hardware: Development machine (i5-9400F, 16GB RAM) suitable for target workload. No specialised GPU required (CPU-bound simulation).

Software: Entirely open-source stack (Python, FastAPI, SQLite, PyQt6, NumPy, Git). PyQt6 GPL license suitable for academic use. VS Code for development environment.

Data Sources: Circuit database (tracks designed for race table integration, no licensing required). Faker library for procedural name generation (24 locales).

Cost: €0 total development cost. All software open-source, existing hardware sufficient.

Supervision Requirements: Fortnightly meetings for architecture review, statistical validation guidance, and testing strategy feedback.

Project Plan

Semester 1 (September-December 2025):

Months 1-2 (Sep-Oct): Requirements engineering (use cases, functional/non-functional requirements, acceptance criteria). Architecture design (ERD, API structure, discipline engine hierarchy). Monte Carlo engine implementation with statistical validation.

Month 3 (November): Database schema implementation with procedural generation system. Multiple discipline engines (single-seater, rally, endurance, drag). Initial GUI prototyping.

Month 4 (December): API endpoint implementation and integration. Comprehensive testing suite (unit, integration, performance). Midpoint documentation and presentation preparation.

Midpoint Deliverable (December 12, 2025):

GitHub tracking: 16 issues across 2 milestones (Midpoint Submission, Final Submission).

HIGH Priority (Midpoint):

Issue #2-4: Core API endpoints (UC-1: Read Driver Details, UC-2: Read Race Configuration, UC-3: Create Race Result)

Issue #5: Monte Carlo simulation engine (<1s race completion, r > 0.7 correlation)

Issue #6: Database schema with procedural generation (drivers, teams, tracks, staff)

Issue #11: Technical documentation (requirements engineering, diagrams, use cases)

Issue #12: Presentation slides with live demo preparation

Issue #13: Working PyQt6 GUI demonstrating race workflow

Issue #14: Testing suite (unit, integration, performance, statistical validation)

Semester 2 (January-May 2026):

Months 5-6 (Jan-Feb): Career mode foundation (save/load, calendar system, event management). AI decision engine for contract negotiations and team strategy. GUI enhancement with data visualisation.

Month 7 (March): Complete remaining disciplines. Advanced visualisation (race charts, telemetry, championship graphs). Integration of all seven discipline engines.

Months 8-9 (Apr-May): Comprehensive testing to 80% coverage. Statistical validation and balance verification. Technical report completion. Final presentation preparation. Submission May 13, 2026.

Risk Management:

| Risk                    | Probability | Mitigation                                                                      | Contingency                                               |
| ----------------------- | ----------- | ------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Monte Carlo performance | Medium      | Early benchmarking, NumPy vectorisation, adaptive iteration counts              | Reduce iterations (sacrifice 2-3% accuracy for 50% speed) |
| Procedural balance      | Medium      | Automated validation suite (1,000+ test seasons), manual oversight              | Pre-generate 50 canonical championships                   |
| GUI complexity          | Medium      | Qt Designer rapid prototyping, usability testing, follow FM patterns            | Focus on core screens only (race, standings, garage)      |
| Scope creep             | High        | Strict MVP definition, feature freeze April 1, prioritisation matrix            | Defer lower-priority disciplines post-submission          |
| Time management         | Medium      | 25-35 hours weekly, weekly supervision (student-led agendas), daily Git commits | Submit functional subset (3-4 disciplines minimum)        |

Quality Assurance: PEP 8 compliance, type hints, comprehensive docstrings, daily Git commits, feature branch workflow, tagged releases (v0.1 midpoint, v1.0 final).

Gantt Chart:

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/efd4b708-2f31-4a57-aa03-54ddf96b6d83)

Testing

Unit Testing:pytest framework targeting 80% coverage for core simulation. Test categories include physics calculations (speed formula verification), AI decision-making (racing mode selection logic), frame-rate consistency (30 FPS sustained performance), database operations (CRUD integrity), API validation (Pydantic schema enforcement).

Integration Testing: Full race simulation workflows with known inputs. Verify race completion, championship points allocation, driver state updates, database transaction consistency. Multi-discipline independence testing ensures concurrent races don't interfere.

Performance Testing: Race event generation accuracy, concurrent race handling, database query optimisation, memory profiling across extended gameplay sessions. Load testing for scalability validation.

Performance Validation: Frame-rate consistency testing (30 FPS sustained over 47-lap races), AI behavior verification (racing mode switches based on gaps), spatial awareness accuracy (gap calculations, slipstream detection), competitive balance metrics (varied finishing orders across races), position update integrity (no teleporting or negative positions).

User Acceptance Testing: Developer self-testing with potential informal feedback from interested parties (not committed). Evaluation criteria:

Realism (subjective assessment of race events and career progression)

Engagement (continued playability across multiple sessions)

UI Clarity (intuitive navigation and information presentation)

Competitive Balance (varied race outcomes, no systematic dominance)

Career Longevity (sustained interest across multiple seasons)

Comparative Success Metrics:

| Feature            | Momentum Target | F1 Manager 2024 | Motorsport Manager |
| ------------------ | --------------- | --------------- | ------------------ |
| Disciplines        | 7               | 1 (F1/F2)       | 3                  |
| Procedural Content | Yes             | No              | No                 |
| Driver Pool        | 1,000+          | 44              | 200                |
| Career Depth       | Unlimited       | Unlimited       | Unlimited          |

Bug Tracking: GitHub Issues with priority labels (critical, high, medium, low) and category tags (simulation, database, api, ui). Response time: Critical (same day), High (3 days), Medium (1 week), Low (backlog).

Profiling:cProfile (performance), memory_profiler (RAM usage), Qt Performance Analyser (GUI responsiveness).

* 
* [•••]()
* 
* Go to[ ] Page
