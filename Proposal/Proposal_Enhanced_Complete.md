National College of Ireland

Project Proposal

**Momentum: Multi-Discipline Motorsport Management Simulator**

2nd December 2025

Computing – Software Development

2025/2026

Eoin Andrew Fitzsimons

X23151374

X23151374@student.ncirl.ie

# 1 Objectives

Momentum addresses the market gap between Football Manager's simulation depth and existing motorsport titles' limited scope. From building open-wheelers that stick at full speed around circuit turns driven by aerodynamic downforce, to rally racing through blizzards whilst managing snow tyre condition and co-driver pace notes, the system encompasses the breadth of competitive motorsport within a unified framework. This aligns with established frameworks on simulation engagement and procedural generation (Sweetser and Wyeth, 2005; Shaker, Togelius and Nelson, 2016).

**Core Technical Goals:**

* Event-driven race simulation generating lap-by-lap outcomes with real-time position tracking
* Procedural championship generation with automated balance validation
* Multi-discipline architecture using abstract base classes for code reuse
* Desktop GUI enabling race-by-race player interaction and career management

**Novel Contributions:**

* Extensible discipline engine architecture enabling new racing categories without core simulation rewrites
* Automated statistical validation ensuring competitive balance through correlation testing and distribution analysis (Silver, 2012)
* Python-based implementation demonstrating complex multi-league simulation without enterprise engines

# 2 Background

Long-term engagement in simulation games connects strongly to emergent narrative behaviour and complex state spaces (Sweetser and Wyeth, 2005). Football Manager demonstrates this with median engagement exceeding 1,000 hours for substantial portions of its player base (Sports Interactive, 2019). Having invested 6,890 hours since 2015, I recognise its appeal stems from systemic depth rather than sport preference.

Motorsport management games have not replicated this engagement. F1 Manager 2024 achieves median playtime of 14.7 hours (SteamDB, 2024) despite motorsport's global following (F1: 445M viewers, WRC: 800M cumulative audience). Motorsport Manager (446K sales, abandoned 2017) demonstrated multi-discipline viability but had limited scale (200 drivers) and discontinued development (SteamSpy, 2023).

**Meeting Objectives:**

**Real-Time Race Simulation:** Event-driven race simulation generates lap-by-lap outcomes with trackable incidents (overtakes, tyre wear, damage, fuel management, pit strategy). Driver attributes (50+ per individual) feed weighted performance calculations (40% skill, 30% vehicle, 20% environment, 10% randomness). On-track view displays race progression with visual position tracking. Statistical validation tests verify correlation (r > 0.7) between attributes and results.

**Competitive Balance:** Automated validation provides baseline testing through simulated seasons, flagging extreme imbalances (single team >40% wins, failed normality tests). Developer tuning establishes competitive orders that evolve through comprehensive development systems and regulation changes, mirroring real motorsport dynamics.

**Extensible Architecture:** Abstract base class defines simulation interface (`simulate_race()`, `calculate_performance_weights()`). New disciplines inherit this foundation without modifying core engine. Demonstrates software engineering principles for complex domain modelling.

**Persistent World:** SQLite database tracks all entities (drivers, teams, tracks, championships) with career progression driven by performance vs expectations, contract cycles, and hidden potential curves. All leagues advance concurrently regardless of player focus.

# 3 State of the Art

| Title                                                | Strengths                                                                                     | Critical Gaps                                                                                                 |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Football Manager 2024** (Sports Interactive) | 143 leagues, persistent world, emergent narratives, 1,000+ hour engagement, extensive modding | Team sport structure incompatible with motorsport, licensing model unsuitable                                 |
| **F1 Manager 2024** (Frontier)                 | Authentic presentation, detailed development mechanics, real-time decisions                   | Predictable AI, linear progression, single discipline (F1/F2), static driver potential, 14.7h median playtime |
| **Motorsport Manager** (Playsport, 2016)       | Multi-discipline framework, accessible pricing, fictional universe                            | Static world (no procedural generation), small scale (200 drivers), abandoned 2017                            |

**How Momentum Differentiates:**

**Procedural Generation vs Static Content:** Existing titles use handcrafted rosters with limited scale (F1 Manager: 44 drivers, Motorsport Manager: 200). Momentum generates drivers/teams/championships algorithmically with hidden potential enabling larger roster depth (1,000+ drivers) and emergent narratives.

**Extensible Architecture vs Monolithic Design:** Adding new racing categories to F1 Manager or Motorsport Manager requires fundamental rewrites. Momentum's abstract base class architecture enables new disciplines through inheritance without touching core simulation logic.

**Extensible Architecture vs Monolithic Design:** Adding new racing categories to F1 Manager or Motorsport Manager requires fundamental rewrites. Momentum's abstract base class architecture enables new disciplines through inheritance without touching core simulation logic.

**Open Architecture:** Python/SQLite stack with GPL licensing enables academic transparency and potential community extensions, contrasting with proprietary closed engines.

# 4 Technical Approach

**Architecture:**

* Backend: Python + FastAPI REST API, SQLite database, async request handling
* Frontend: PyQt6 desktop GUI with direct Python integration and native UI components
* Rationale: Prioritises simulation depth over visual spectacle, enables rapid prototyping, eliminates licensing costs

**Multi-Discipline Engine:**

Abstract `BaseDisciplineEngine` class defines interface for all seven disciplines. Each implements `simulate_race(context)` with discipline-specific logic and `calculate_performance_weights()` defining attribute importance.

Performance formula: Driver Skill (40%) + Vehicle (30%) + Environment (20%) + Randomness (10%)

Discipline differentiation examples:

* Single-Seater: Qualifying pace, aerodynamics, DRS strategy
* Rally: Surface adaptation, co-driver communication, pace notes
* Endurance: Consistency, mechanical sympathy, multi-driver fatigue
* Drag: Reaction time, launch control, bracket elimination

**Event-Driven Race Simulation:**

Lap-by-lap race progression with real-time incident generation (overtakes, slipstream, dirty air effects, tyre degradation, damage, refuelling where applicable). Driver attributes influence event probabilities and outcomes. On-track view visualises race progression with position tracking. Future scope includes 3D rendering post-graduation; current implementation uses 2D position indicators around track layouts.

**Procedural Generation:**

Championships generated with three-tier budget distribution (Tier 1: 90-100% cap, Tier 2: 60-80%, Tier 3: 40-60%). Drivers generated with base attributes 40-60, specialisation boosts, and hidden potential curves.

Validation: Automated testing runs 1,000 simulated seasons verifying competitive balance (no team >40% wins, normal distribution of outcomes, realistic performance spread).

Cultural authenticity via Faker library (24 locales) ensures regional naming patterns per discipline.

# 5 Technical Details

**Implementation Language and Libraries:**

* **Backend:** Python 3.11, FastAPI (async REST API), SQLite (embedded database), NumPy/SciPy (statistical calculations), Faker (multi-locale name generation), Pydantic (data validation)
* **Frontend:** PyQt6 (desktop GUI), Matplotlib (data visualisation), Qt Designer (UI prototyping)
* **Development:** Git/GitHub (version control), Black (code formatting), mypy (type checking), pytest (testing)

**Database Design:**

Normalised schema (3NF) with seven core entities:

* **Driver:** 50+ attributes across technical, mental, physical, racecraft, and discipline-specific categories (0-100 scale)
* **Team:** Budget, discipline, vehicle performance, facility ratings
* **Track:** Dimensions, surface, IMA grading, compatible disciplines
* **Championship:** Calendar, points system, budget cap, technical regulations
* **Race, RaceResult, Staff:** Supporting entities for event management

Foreign key constraints enforce referential integrity. Indexes on frequently queried columns (discipline, rating, team_id).

**API Structure:**

REST endpoints for race simulation (`POST /simulate/race`), championship management (`POST /season/create`, `GET /season/standings`), and entity queries (`GET /drivers`, `/teams`, `/tracks`). OpenAPI documentation auto-generated.

**Testing Approach:**

* **Unit Tests:** Attribute calculations, simulation convergence, database operations (80% coverage target)
* **Integration Tests:** Full race workflows, championship progression, multi-discipline consistency
* **Performance Tests:** Concurrent race handling, memory profiling, query optimisation
* **Statistical Validation:** Normal distribution verification (Shapiro-Wilk test), correlation analysis (r > 0.7), competitive balance metrics
* **User Acceptance:** Developer self-testing with potential informal feedback (not committed)

# 6 Special Resources Required

**Hardware:** Development machine (i5-9400F, 16GB RAM) suitable for target workload. No specialised GPU required (CPU-bound simulation).

**Software:** Entirely open-source stack (Python, FastAPI, SQLite, PyQt6, NumPy, Git). PyQt6 GPL license suitable for academic use. VS Code for development environment.

**Data Sources:** Circuit database (tracks designed for race table integration, no licensing required). Faker library for procedural name generation (24 locales).

**Cost:** €0 total development cost. All software open-source, existing hardware sufficient.

**Supervision Requirements:** Weekly meetings (student-led agendas) for architecture review, statistical validation guidance, and testing strategy feedback.

# 7 Project Plan

**Semester 1 (September-December 2025):**

**Months 1-2 (Sep-Oct):** Requirements engineering (use cases, functional/non-functional requirements, acceptance criteria). Architecture design (ERD, API structure, discipline engine hierarchy). Monte Carlo engine implementation with statistical validation.

**Month 3 (November):** Database schema implementation with procedural generation system. Multiple discipline engines (single-seater, rally, endurance, drag). Initial GUI prototyping.

**Month 4 (December):** API endpoint implementation and integration. Comprehensive testing suite (unit, integration, performance). Midpoint documentation and presentation preparation.

**Midpoint Deliverable (December 12, 2025):**

GitHub tracking: 16 issues across 2 milestones (Midpoint Submission, Final Submission).

*HIGH Priority (Midpoint):*

* Issue #2-4: Core API endpoints (UC-1: Read Driver Details, UC-2: Read Race Configuration, UC-3: Create Race Result)
* Issue #5: Monte Carlo simulation engine (<1s race completion, r > 0.7 correlation)
* Issue #6: Database schema with procedural generation (drivers, teams, tracks, staff)
* Issue #11: Technical documentation (requirements engineering, diagrams, use cases)
* Issue #12: Presentation slides with live demo preparation
* Issue #13: Working PyQt6 GUI demonstrating race workflow
* Issue #14: Testing suite (unit, integration, performance, statistical validation)

**Semester 2 (January-May 2026):**

**Months 5-6 (Jan-Feb):** Career mode foundation (save/load, calendar system, event management). AI decision engine for contract negotiations and team strategy. GUI enhancement with data visualisation.

**Month 7 (March):** Complete remaining disciplines. Advanced visualisation (race charts, telemetry, championship graphs). Integration of all seven discipline engines.

**Months 8-9 (Apr-May):** Comprehensive testing to 80% coverage. Statistical validation and balance verification. Technical report completion. Final presentation preparation. **Submission May 13, 2026.**

**Risk Management:**

| Risk                    | Probability | Mitigation                                                                      | Contingency                                               |
| ----------------------- | ----------- | ------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Monte Carlo performance | Medium      | Early benchmarking, NumPy vectorisation, adaptive iteration counts              | Reduce iterations (sacrifice 2-3% accuracy for 50% speed) |
| Procedural balance      | Medium      | Automated validation suite (1,000+ test seasons), manual oversight              | Pre-generate 50 canonical championships                   |
| GUI complexity          | Medium      | Qt Designer rapid prototyping, usability testing, follow FM patterns            | Focus on core screens only (race, standings, garage)      |
| Scope creep             | High        | Strict MVP definition, feature freeze April 1, prioritisation matrix            | Defer lower-priority disciplines post-submission          |
| Time management         | Medium      | 25-35 hours weekly, weekly supervision (student-led agendas), daily Git commits | Submit functional subset (3-4 disciplines minimum)        |

**Quality Assurance:** PEP 8 compliance, type hints, comprehensive docstrings, daily Git commits, feature branch workflow, tagged releases (v0.1 midpoint, v1.0 final).

**Gantt Chart:** See appendix for visual timeline (September 2025 - May 2026).

# 8 Testing

**Unit Testing:** pytest framework targeting 80% coverage for core simulation. Test categories include attribute calculations (weighting formula verification), Monte Carlo convergence (statistical validity), database operations (CRUD integrity), API validation (Pydantic schema enforcement).

**Integration Testing:** Full race simulation workflows with known inputs. Verify race completion, championship points allocation, driver state updates, database transaction consistency. Multi-discipline independence testing ensures concurrent races don't interfere.

**Performance Testing:** Race event generation accuracy, concurrent race handling, database query optimisation, memory profiling across extended gameplay sessions. Load testing for scalability validation.

**Statistical Validation:** Normal distribution verification (Shapiro-Wilk test), correlation analysis between driver attributes and results (r > 0.7 target), competitive balance metrics (no single driver/team dominance), systematic bias detection (pole position advantage, weather impacts).

**User Acceptance Testing:** Developer self-testing with potential informal feedback from interested parties (not committed). Evaluation criteria:

1. Realism (subjective assessment of race events and career progression)
2. Engagement (continued playability across multiple sessions)
3. UI Clarity (intuitive navigation and information presentation)
4. Competitive Balance (varied race outcomes, no systematic dominance)
5. Career Longevity (sustained interest across multiple seasons)

**Comparative Success Metrics:**

| Feature            | Momentum Target | F1 Manager 2024 | Motorsport Manager |
| ------------------ | --------------- | --------------- | ------------------ |
| Disciplines        | 7               | 1 (F1/F2)       | 3                  |
| Procedural Content | Yes             | No              | No                 |
| Driver Pool        | 1,000+          | 44              | 200                |
| Career Depth       | Unlimited       | Unlimited       | Unlimited          |

**Bug Tracking:** GitHub Issues with priority labels (critical, high, medium, low) and category tags (simulation, database, api, ui). Response time: Critical (same day), High (3 days), Medium (1 week), Low (backlog).

**Profiling:** cProfile (performance), memory_profiler (RAM usage), Qt Performance Analyser (GUI responsiveness).

# 9 References
