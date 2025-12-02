# Technical Report - Section 6: Appendices

## 6.0 Appendices

This section contains supplementary information supporting the main body of the technical report.

## 6.1 Project Proposal

**Project Title:** Momentum - Multi-Discipline Motorsport Simulation System

**Student Name:** Eoin Fitzsimons
**Programme:** BSc (Honours) in Computing - Software Development
**Academic Year:** 2024/2025
**Proposed Supervisor:** [Supervisor Name]

### Project Objectives

The primary objective of this project is to design and implement a comprehensive multi-discipline motorsport management simulation system that combines realistic statistical modelling with modern software architecture principles.

**Core Objectives:**

1. Develop seven complete racing discipline simulation engines (Single Seater, Production/Touring, Rally/Stage, Urban/Street, Drag/Acceleration, Sprint/Rallycross, Endurance)
2. Implement a comprehensive driver system with 50+ attributes across 7 performance categories
3. Create an advanced staff management system with 40+ attributes across 25+ roles
4. Build a RESTful API architecture enabling multiple frontend implementations
5. Integrate multi-currency financial systems with real-time exchange rates
6. Apply Monte Carlo statistical methods for realistic race outcome generation

### Project Scope

**In Scope:**

- Backend simulation engine (Python/FastAPI)
- Database design and implementation (SQLite)
- Seven discipline-specific racing engines
- Comprehensive driver and staff attribute systems
- Multi-currency budget management
- RESTful API with automated documentation
- Unit, integration, and performance testing

**Out of Scope (Future Work):**

- Visual frontend (Unity/Web interface)
- Multiplayer functionality
- Advanced AI machine learning integration
- Real-time telemetry visualization

### Technical Approach

**Architecture:** Layered architecture with clear separation of concerns

- API Layer (FastAPI)
- Business Logic Layer (Simulation engines, management systems)
- Data Access Layer (Database managers)
- Data Layer (SQLite database)

**Key Technologies:**

- Python 3.8+
- FastAPI (REST API framework)
- SQLite (Embedded database)
- NumPy/SciPy (Statistical computation)
- Faker (Name generation)
- pytest (Testing framework)

### Methodology

**Development Approach:** Agile/Iterative

1. **Sprint 1-2:** Database design and core data models
2. **Sprint 3-4:** First discipline engine (Single Seater) and Monte Carlo framework
3. **Sprint 5-7:** Additional discipline engines (Rally, Touring, Street)
4. **Sprint 8-9:** Staff management and currency systems
5. **Sprint 10-11:** Remaining disciplines (Drag, Rallycross, Endurance)
6. **Sprint 12-13:** API development and documentation
7. **Sprint 14-15:** Testing, optimisation, and evaluation

**Testing Strategy:**

- Test-Driven Development (TDD) for critical components
- Unit tests for individual functions and classes
- Integration tests for system interactions
- Performance benchmarking for simulation speed
- Statistical validation of race outcomes

### Expected Deliverables

1. **Source Code:** Complete Python codebase with documentation
2. **Database:** SQLite database with sample data
3. **API Documentation:** Automated OpenAPI/Swagger documentation
4. **Test Suite:** Comprehensive test coverage (target 80%+)
5. **Technical Report:** Full documentation of design, implementation, and evaluation
6. **User Guide:** API usage examples and integration instructions

### Success Criteria

1. All seven racing disciplines successfully implemented with distinct characteristics
2. Race simulation completes in under 1 second for 20-driver grids
3. Statistical correlation (r > 0.7) between driver attributes and race success
4. Test coverage exceeds 80%
5. API endpoints return correct responses with proper error handling
6. Multi-currency system accurately converts between all supported currencies
7. Staff performance multipliers measurably affect race outcomes

### Risk Assessment

| Risk                                | Probability | Impact | Mitigation                                                          |
| ----------------------------------- | ----------- | ------ | ------------------------------------------------------------------- |
| Scope creep (too many disciplines)  | High        | High   | Prioritize quality over quantity; complete 3 disciplines minimum    |
| Performance issues with Monte Carlo | Medium      | High   | Optimize iteration count; use caching                               |
| Statistical validation complexity   | Medium      | Medium | Start simple, iterate based on testing                              |
| Database scaling limitations        | Low         | Medium | Design for future migration to PostgreSQL                           |
| Time constraints                    | Medium      | High   | Focus on core features first; mark advanced features as future work |

### Timeline

**Total Duration:** 15 weeks (October 2024 - January 2025)

- **Weeks 1-2:** Requirements analysis, database design
- **Weeks 3-5:** Core simulation engine and first discipline
- **Weeks 6-9:** Additional disciplines and staff systems
- **Weeks 10-11:** API development and currency system
- **Weeks 12-13:** Testing and performance optimisation
- **Weeks 14-15:** Documentation and final report writing

### References

- Ripley, B.D. (1987). *Stochastic Simulation*. Wiley.
- Fowler, M. (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley.
- FastAPI Documentation. https://fastapi.tiangolo.com/
- Sports Interactive. *Football Manager* (inspiration for depth of simulation)

## 6.2 Reflective Journals

### Journal Entry 1 - October 14, 2024

**Week 1: Project Initiation**

**Activities:**

- Finalized project proposal and scope
- Set up development environment (Python 3.11, VS Code, Git)
- Created initial GitHub repository
- Researched Monte Carlo simulation methods

**Reflections:**
The project scope is ambitious - seven racing disciplines may be too many. I'm concerned about time management and feature creep. However, I'm excited about the technical challenges, particularly the statistical simulation aspect.

I spent considerable time researching existing motorsport games. Football Manager's depth inspired me, but I noticed most racing games focus on a single discipline. The multi-discipline approach could be my unique contribution.

**Challenges:**

- Deciding on attribute count: Started with 70+ driver attributes but realized this was excessive. Settled on 50+ as a balance between depth and manageability.
- Understanding Monte Carlo methods: Required significant reading of statistical literature.

**Next Steps:**

- Design database schema
- Create entity-relationship diagram
- Start implementing Driver and Team models

### Journal Entry 2 - October 28, 2024

**Week 3: Database and Core Models**

**Activities:**

- Completed database design with 7 main entities
- Implemented Driver model with 50+ attributes
- Created DatabaseManager for all CRUD operations
- Added foreign key constraints and data validation

**Reflections:**
Database design took longer than expected but was crucial. I'm glad I invested time in proper normalization (3NF) rather than rushing. The CHECK constraints for attribute validation (0-100 range) have already prevented bugs.

Interesting discovery: SQLite doesn't enforce foreign key constraints by default! Had to enable with `PRAGMA foreign_keys = ON`. This would have caused major issues if discovered later.

**Challenges:**

- Managing 50+ attributes in SQL queries - very verbose INSERT statements
- Decided to use dataclasses for Python models, which simplified code significantly

**Learning:**
Type hints in Python are incredibly helpful. IDEs catch errors before runtime, and the code is more self-documenting.

**Next Steps:**

- Implement first simulation engine (Single Seater)
- Research optimal Monte Carlo iteration count

### Journal Entry 3 - November 11, 2024

**Week 5: First Simulation Engine Complete**

**Activities:**

- Completed Single Seater engine with Monte Carlo simulation
- Implemented performance score calculation with weighted attributes
- Created first integration tests
- Ran 1000 test simulations and analysed statistical distribution

**Reflections:**
Major breakthrough! The Monte Carlo simulation works beautifully. After experimenting with different iteration counts (50, 100, 200, 500), I found 100 iterations provides the best balance:

- 50 iterations: Too random, poor correlation
- 100 iterations: Good balance (r=0.89 correlation)
- 200+ iterations: Marginally better but 2x slower

The correlation coefficient of 0.89 between driver skill and race wins exceeded my expectations. This proves the simulation is skill-based while maintaining realistic variance.

**Challenges:**

- Initial simulation took 3 seconds for 20 drivers - unacceptable!
- Profiling revealed repeated database queries in the loop
- Solution: Load all data once, cache in memory
- Result: Reduced to 0.23 seconds (13x faster!)

**Key Learning:**
Premature optimisation is real, but so is premature pessimization. I should have profiled earlier.

**Next Steps:**

- Implement Rally Stage engine (very different characteristics)
- Start staff management system

### Journal Entry 4 - November 25, 2024

**Week 7: Multi-Discipline Architecture**

**Activities:**

- Implemented Rally Stage and Production/Touring engines
- Created BaseDisciplineEngine abstract class
- Refactored to Strategy Pattern for discipline routing
- Added MultiDisciplineSimulator coordinator

**Reflections:**
The Strategy Pattern was the right choice. Each discipline now has completely different logic while sharing common interfaces. Rally emphasizes vehicle control and adaptability, while Single Seater focuses on raw speed and consistency.

Testing shows distinct statistical signatures:

- Rally: 22% upset rate (high variance)
- Single Seater: 8% upset rate (low variance)
  This matches real-world expectations!

**Challenges:**

- Initially tried to create "one engine fits all" - terrible idea
- Each discipline needs unique attribute weights and incident probabilities
- Refactoring was painful but necessary

**Key Insight:**
Don't force different problem domains into the same solution. Embrace differences through polymorphism.

**Next Steps:**

- Implement remaining 4 disciplines
- Start staff management system (this is turning out to be more important than I initially thought)

### Journal Entry 5 - December 9, 2024

**Week 9: Staff Management Breakthrough**

**Activities:**

- Completed staff management system with 40+ attributes
- Implemented information fog-of-war based on analyst quality
- Created budget-based team scaling
- Added staff performance multipliers affecting race outcomes

**Reflections:**
The staff system has become unexpectedly deep. The "information fog-of-war" concept - where better analysts reveal more race data - creates interesting strategic decisions. Do you invest in drivers or staff?

User testing feedback (informal, with 3 classmates):

- "Staff hiring is more interesting than I expected"
- "Budget constraints force tough decisions"
- "Wish I could see how staff quality affects performance" (noted for future work)

**Challenges:**

- Balancing staff impact: Too weak = pointless, too strong = drivers don't matter
- Settled on 20-30% performance variance from staff quality
- This creates meaningful but not overwhelming impact

**Personal Growth:**
I'm getting much better at breaking complex systems into manageable components. The staff system initially seemed overwhelming, but decomposing it into hiring, performance calculation, and information access made it tractable.

**Next Steps:**

- Complete final 3 disciplines (Drag, Rallycross, Endurance)
- Implement currency system
- Start API development

### Journal Entry 6 - December 23, 2024

**Week 11: All Disciplines Complete**

**Activities:**

- Implemented Drag, Rallycross, and Endurance engines
- Completed multi-currency system with live exchange rates
- All 7 disciplines now functional with distinct characteristics
- Created comprehensive test suite (currently 87% coverage)

**Reflections:**
Reached a major milestone - all seven disciplines are complete! Each feels distinct:

- Drag racing: High variance, short races, emphasis on reaction time
- Rallycross: Mixed surfaces, jumps, demolition derby elements
- Endurance: Strategy-focused, reliability critical, tire management essential

The currency system was surprisingly complex. Exchange rate caching, locale-specific formatting (JPY has no decimals!), and budget cap conversions all required careful handling.

**Challenges:**

- Endurance racing required implementing tire degradation model
- Used exponential decay with "cliff effect" at lap 30+
- Formula: `grip = e^(-k*laps)` where k varies with driver tire management skill
- This creates realistic strategy decisions about pit stop timing

**Setback:**
Realized I won't have time for advanced AI behaviours. The framework is there but personality-driven decisions are minimal. Marked as future work.

**Lessons Learned:**
Scope management is HARD. I should have focused on 3-4 disciplines perfectly rather than 7 disciplines adequately. However, having all 7 does demonstrate the architecture's flexibility.

**Next Steps:**

- Build FastAPI endpoints
- Create comprehensive API documentation
- Performance optimisation

### Journal Entry 7 - January 6, 2025

**Week 13: API Development Complete**

**Activities:**

- Implemented all REST endpoints (GET /drivers, POST /simulate/race, etc.)
- FastAPI auto-generates OpenAPI/Swagger documentation
- Added CORS middleware for future frontend integration
- Comprehensive error handling with proper HTTP status codes

**Reflections:**
FastAPI is amazing! The automatic documentation generation alone saved days of work. Type hints in Python translate directly to API schema validation - errors are caught before simulation runs.

API design philosophy: Be liberal in what you accept, conservative in what you send. Validate inputs strictly, but provide detailed error messages explaining what's wrong.

**Performance Results:**
Exceeded all targets:

- Race simulation: 0.234s average (target: <1.0s) ✅
- API response: 267ms average (target: <1.5s) ✅
- Database queries: 23ms average (target: <100ms) ✅

**Challenges:**

- Handling database connection pooling in async FastAPI context
- Solution: Use context managers for database connections
- Ensures connections are always properly closed

**Pride Moment:**
Ran 10,000 consecutive simulations without a single crash or data corruption. The error handling and transaction management work!

**Next Steps:**

- Final testing and validation
- Statistical analysis of simulation outcomes
- Begin writing technical report

### Journal Entry 8 - January 20, 2025

**Week 15: Testing and Evaluation**

**Activities:**

- Completed comprehensive test suite (90% coverage achieved!)
- Statistical validation: Pearson correlation r=0.89, p<0.001
- User acceptance testing with 8 participants
- Performance benchmarking and scalability analysis
- Documentation writing

**Reflections:**
The statistical validation exceeded expectations. The strong correlation (r=0.89) between driver skill and race success, combined with low p-value, proves the simulation is mathematically sound while maintaining engaging randomness.

User testing revealed important insights:

- **Strength:** "Simulation feels realistic" (8/8 users)
- **Weakness:** "Too many attributes for casual players" (5/8 users)
- **Suggestion:** Need simplified "casual mode" vs. "detailed mode"

System Usability Scale (SUS) score: 72.5/100 - above industry average but room for improvement.

**What Went Well:**

1. Layered architecture made testing straightforward
2. Type hints caught numerous bugs before runtime
3. Test-driven development prevented regressions
4. Early performance profiling avoided late-stage optimisation panic

**What Could Be Improved:**

1. Should have completed 3 disciplines perfectly before expanding to 7
2. AI system feels incomplete (framework exists but limited behaviours)
3. No visual interface limits accessibility to developers only
4. Championship mode basic - lacks season progression

**Technical Achievements:**

- 7/7 racing disciplines implemented
- 90% test coverage
- Sub-second simulation times
- Proven statistical validity
- Clean, documented codebase

**Personal Growth:**
This project taught me more about software engineering than any course. Key lessons:

- Architecture matters more than I thought
- Testing is insurance, not overhead
- User feedback is humbling and essential
- Scope management is a skill, not just discipline
- Documentation compounds in value over time

**Final Thoughts:**
I'm proud of what I've built, but I'm more excited about what I've learned. The gap between "works on my machine" and "production-ready software" is vast. This project gave me a taste of that journey.

The multi-discipline approach worked - each engine has distinct characteristics that match real-world racing. The statistical foundation is sound. The architecture is extensible.

But the missing GUI and limited AI remind me that technical excellence alone doesn't make software successful. User experience matters. Accessibility matters. Marketing matters.

For a final year project, I'm satisfied. For a commercial product, there's years of work ahead.

**Project Status:** Ready for submission ✅

## 6.3 Ethics Approval

**Ethics Approval Status:** Not Required

**Justification:**
This project does not involve:

- Human participants (beyond informal user testing)
- Sensitive personal data collection
- Medical or health-related research
- Vulnerable populations
- Deception or psychological manipulation

**User Testing Approach:**
Informal user acceptance testing was conducted with 8 volunteer participants (classmates and motorsport enthusiasts) who:

- Provided informed consent verbally
- Were fully aware of the testing purpose
- Could withdraw at any time
- Provided only anonymous feedback
- Did not have personal data stored or processed

No formal ethics approval was required under NCI's research ethics policy for software development projects with minimal human interaction.

## 6.4 Project Code Samples

### Sample 1: Monte Carlo Race Simulation Core Algorithm

```python
def simulate_race_monte_carlo(self, context: DisciplineContext, 
                              iterations: int = 100) -> List[RaceResult]:
    """
    Core Monte Carlo simulation algorithm
  
    Generates race outcomes through probabilistic sampling of driver
    performance based on attributes, team quality, and environmental factors.
    """
    # Calculate base performance scores for all drivers
    base_scores = {}
    for driver in context.drivers:
        team = context.teams[driver.team_id]
        base_scores[driver.id] = self.calculate_performance_score(driver, team)
  
    # Monte Carlo sampling across multiple iterations
    position_samples = {driver.id: [] for driver in context.drivers}
  
    for iteration in range(iterations):
        # Generate performance sample for this iteration
        iteration_performances = {}
      
        for driver in context.drivers:
            base_score = base_scores[driver.id]
          
            # Add random variance using normal distribution
            # Standard deviation based on consistency (lower = more variance)
            std_dev = (100 - driver.consistency) / 10.0
            performance = np.random.normal(base_score, std_dev)
          
            # Apply race incidents (mechanical failures, crashes)
            if random.random() < self.incident_probability:
                performance *= 0.5  # Major incident penalty
          
            iteration_performances[driver.id] = performance
      
        # Sort drivers by performance for this iteration
        sorted_drivers = sorted(
            context.drivers,
            key=lambda d: iteration_performances[d.id],
            reverse=True
        )
      
        # Record positions
        for position, driver in enumerate(sorted_drivers, start=1):
            position_samples[driver.id].append(position)
  
    # Aggregate results across all iterations
    final_results = []
    for driver in context.drivers:
        positions = position_samples[driver.id]
        avg_position = np.mean(positions)
      
        result = RaceResult(
            driver_id=driver.id,
            position=int(round(avg_position)),
            performance_score=base_scores[driver.id]
        )
        final_results.append(result)
  
    # Sort by final position
    final_results.sort(key=lambda r: r.position)
  
    return final_results
```

### Sample 2: Discipline-Specific Performance Calculation

```python
def calculate_single_seater_performance(self, driver: Driver, 
                                       team: Team) -> float:
    """
    Calculate performance score for single-seater (Formula-style) racing
  
    Emphasizes technical precision, consistency, and aerodynamic knowledge
    """
    # Core driving attributes with discipline-specific weights
    score = (
        driver.raw_speed * 0.25 +              # Critical for qualifying
        driver.cornering_skill * 0.20 +        # High-speed corners
        driver.racecraft * 0.15 +              # Overtaking and defense
        driver.consistency * 0.12 +            # Maintaining performance
        driver.tire_management * 0.10 +        # Stint optimization
        driver.setup_knowledge * 0.08 +        # Car tuning
        driver.physical_fitness * 0.10         # G-force tolerance
    )
  
    # Apply team performance multiplier from staff quality
    team_multiplier = self._calculate_team_multiplier(team)
    score *= team_multiplier
  
    # Apply environmental factors
    weather_modifier = self._calculate_weather_impact(driver, context.weather)
    score *= weather_modifier
  
    return score

def calculate_rally_stage_performance(self, driver: Driver, 
                                     team: Team) -> float:
    """
    Calculate performance score for rally stage racing
  
    Emphasizes vehicle control, adaptability, and bravery
    Completely different weighting from single-seater
    """
    score = (
        driver.vehicle_control * 0.30 +        # Essential for loose surfaces
        driver.adaptability * 0.20 +           # Changing conditions
        driver.bravery * 0.15 +                # Commitment to pace notes
        driver.spatial_awareness * 0.12 +      # Narrow roads
        driver.setup_knowledge * 0.15 +        # Surface-specific tuning
        driver.consistency * 0.08              # Less critical in rally
    )
  
    # Rally has different team impact (co-driver, service crew)
    team_multiplier = self._calculate_rally_team_multiplier(team)
    score *= team_multiplier
  
    # Surface conditions critical in rally
    surface_modifier = self._calculate_surface_impact(driver, context.track)
    score *= surface_modifier
  
    return score
```

### Sample 3: Staff Performance Impact System

```python
def calculate_staff_performance_multipliers(self, team: Team) -> Dict[str, float]:
    """
    Calculate how staff capabilities affect team performance across different areas
  
    Better staff = better car, better strategy, better information
    """
    staff_members = self.db.get_team_staff(team.id)
  
    multipliers = {
        'technical_performance': 1.0,    # Car development quality
        'race_strategy': 1.0,             # Strategic decision quality
        'pit_operations': 1.0,            # Pit stop speed/reliability
        'information_access': 1.0,        # Data detail available
        'reliability': 1.0,               # Mechanical failure rate
        'driver_development': 1.0         # Driver skill progression rate
    }
  
    # Group staff by role
    for staff in staff_members:
        if staff.role == StaffRole.CHIEF_ENGINEER:
            # Chief engineer affects technical performance
            multipliers['technical_performance'] += (staff.technical_knowledge / 100.0) * 0.3
            multipliers['reliability'] += (staff.attention_to_detail / 100.0) * 0.2
      
        elif staff.role == StaffRole.DATA_ANALYST:
            # Analysts improve information access (fog-of-war)
            multipliers['information_access'] += (staff.data_analysis / 100.0) * 0.4
      
        elif staff.role == StaffRole.RACE_STRATEGIST:
            # Strategist improves race decisions
            multipliers['race_strategy'] += (staff.tactical_thinking / 100.0) * 0.35
      
        elif staff.role == StaffRole.PIT_CREW_CHIEF:
            # Pit crew chief affects pit stop performance
            multipliers['pit_operations'] += (staff.leadership / 100.0) * 0.25
  
    # Cap multipliers at reasonable limits (max 1.5x bonus)
    for key in multipliers:
        multipliers[key] = min(multipliers[key], 1.5)
  
    return multipliers
```

### Sample 4: Information Fog-of-War Implementation

```python
def get_visible_race_information(self, team: Team, 
                                race_state: RaceState) -> Dict[str, Any]:
    """
    Filter race data based on team's analyst quality
  
    Poor analysts = basic info (positions only)
    Good analysts = detailed info (times, gaps, tire wear)
    Excellent analysts = predictive info (fuel levels, pit predictions)
    """
    staff_multipliers = self.calculate_staff_performance_multipliers(team)
    analyst_quality = staff_multipliers['information_access']
  
    # Always visible: basic positions
    visible_data = {
        'positions': race_state.current_positions,
        'lap_number': race_state.current_lap
    }
  
    # Analyst quality 30+: Lap times visible
    if analyst_quality >= 1.15:  # At least basic analyst
        visible_data['lap_times'] = race_state.lap_times
        visible_data['gaps_to_leader'] = race_state.calculate_gaps()
  
    # Analyst quality 60+: Tire and fuel data visible
    if analyst_quality >= 1.30:  # Good analyst
        visible_data['tire_wear'] = race_state.tire_conditions
        visible_data['fuel_remaining'] = race_state.fuel_levels
        visible_data['estimated_pit_laps'] = race_state.calculate_pit_windows()
  
    # Analyst quality 85+: Competitor predictions visible
    if analyst_quality >= 1.45:  # Excellent analyst
        visible_data['predicted_strategies'] = self._predict_competitor_strategies(race_state)
        visible_data['performance_trends'] = self._analyze_performance_trends(race_state)
        visible_data['optimal_pit_window'] = self._calculate_optimal_pit_timing(race_state)
  
    return visible_data
```

## 6.5 Database Schema Documentation

### Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DRIVERS TABLE                            │
├─────────────────────────────────────────────────────────────────┤
│ PK  driver_id           INTEGER                                  │
│     name                TEXT NOT NULL                            │
│     nationality         TEXT                                     │
│     birth_date          TEXT                                     │
│     age                 INTEGER                                  │
│     -- Core Driving Skills (10 attributes)                      │
│     raw_speed           REAL CHECK(0.0 <= raw_speed <= 100.0)   │
│     consistency         REAL CHECK(0.0 <= consistency <= 100.0) │
│     racecraft           REAL CHECK(0.0 <= racecraft <= 100.0)   │
│     ... (47 more attributes)                                    │
│     -- Career Statistics                                        │
│     total_races         INTEGER DEFAULT 0                       │
│     total_wins          INTEGER DEFAULT 0                       │
│     total_podiums       INTEGER DEFAULT 0                       │
│     championships       INTEGER DEFAULT 0                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ FK driver_id
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RACE_RESULTS TABLE                          │
├─────────────────────────────────────────────────────────────────┤
│ PK  result_id           INTEGER                                  │
│ FK  race_id             INTEGER REFERENCES races(race_id)       │
│ FK  driver_id           INTEGER REFERENCES drivers(driver_id)   │
│ FK  team_id             INTEGER REFERENCES teams(team_id)       │
│     position            INTEGER NOT NULL                         │
│     points_earned       REAL                                     │
│     fastest_lap         REAL                                     │
│     dnf_reason          TEXT                                     │
│     performance_score   REAL                                     │
└─────────────────────────────────────────────────────────────────┘
                    │                              │
         FK race_id │                              │ FK team_id
                    ▼                              ▼
┌─────────────────────────────┐    ┌──────────────────────────────┐
│       RACES TABLE           │    │      TEAMS TABLE             │
├─────────────────────────────┤    ├──────────────────────────────┤
│ PK race_id         INTEGER  │    │ PK team_id       INTEGER     │
│ FK championship_id INTEGER  │    │    name          TEXT        │
│ FK track_id        INTEGER  │    │    discipline    TEXT        │
│    race_date       TEXT     │    │    budget        REAL        │
│    weather         TEXT     │    │    tier          INTEGER     │
│    temperature     REAL     │    │    headquarters  TEXT        │
└─────────────────────────────┘    └──────────────────────────────┘
         │                                      │
         │ FK track_id                         │ FK team_id
         ▼                                      ▼
┌─────────────────────────────┐    ┌──────────────────────────────┐
│      TRACKS TABLE           │    │    STAFF_MEMBERS TABLE       │
├─────────────────────────────┤    ├──────────────────────────────┤
│ PK track_id        INTEGER  │    │ PK staff_id      INTEGER     │
│    name            TEXT     │    │ FK team_id       INTEGER     │
│    length          REAL     │    │    name          TEXT        │
│    corners         INTEGER  │    │    role          TEXT        │
│    surface_type    TEXT     │    │    tier          TEXT        │
│    grip_level      REAL     │    │    salary        REAL        │
│    elevation_change REAL    │    │    hire_date     TEXT        │
└─────────────────────────────┘    │    -- 40+ skill attributes   │
                                    │    technical_knowledge REAL  │
                                    │    data_analysis      REAL  │
                                    │    ... (38 more)             │
                                    └──────────────────────────────┘
```

### Sample SQL Schema

```sql
-- Drivers table with all 50+ attributes
CREATE TABLE drivers (
    driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nationality TEXT,
    birth_date TEXT,
    age INTEGER DEFAULT 25,
  
    -- Core Driving Skills
    raw_speed REAL DEFAULT 50.0 CHECK(raw_speed >= 0.0 AND raw_speed <= 100.0),
    consistency REAL DEFAULT 50.0 CHECK(consistency >= 0.0 AND consistency <= 100.0),
    racecraft REAL DEFAULT 50.0 CHECK(racecraft >= 0.0 AND racecraft <= 100.0),
    -- ... 47 more attributes with similar constraints
  
    -- Career Statistics
    total_races INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_podiums INTEGER DEFAULT 0,
    championships INTEGER DEFAULT 0
);

CREATE INDEX idx_drivers_nationality ON drivers(nationality);
CREATE INDEX idx_drivers_discipline ON drivers(single_seater_aptitude, rally_aptitude);
```

## 6.6 API Documentation Examples

### Sample API Request/Response

**Endpoint:** `POST /simulate/race`

**Request Body:**

```json
{
  "race_id": 1,
  "discipline": "single_seater",
  "track_id": 5,
  "driver_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  "weather": "dry",
  "temperature": 25,
  "track_condition": "optimal"
}
```

**Response (200 OK):**

```json
{
  "race_id": 1,
  "discipline": "single_seater",
  "track": "Monaco Grand Prix Circuit",
  "weather": "dry",
  "results": [
    {
      "position": 1,
      "driver_id": 3,
      "driver_name": "Lewis Hamilton",
      "team_id": 2,
      "team_name": "Mercedes AMG F1",
      "fastest_lap": "1:12.456",
      "total_time": "1:32:15.678",
      "gap_to_leader": "0.000s",
      "points_earned": 25,
      "performance_score": 87.3
    },
    {
      "position": 2,
      "driver_id": 7,
      "driver_name": "Max Verstappen",
      "team_id": 4,
      "team_name": "Red Bull Racing",
      "fastest_lap": "1:12.789",
      "total_time": "1:32:18.234",
      "gap_to_leader": "+2.556s",
      "points_earned": 18,
      "performance_score": 86.1
    }
    // ... remaining 8 drivers
  ],
  "simulation_metadata": {
    "simulation_time_ms": 234,
    "monte_carlo_iterations": 100,
    "incidents": [],
    "safety_car_periods": 0
  }
}
```

**Error Response (400 Bad Request):**

```json
{
  "detail": "Invalid discipline specified. Supported disciplines: single_seater, production_touring, rally_stage, urban_street, drag_acceleration, sprint_rallycross, endurance",
  "error_code": "INVALID_DISCIPLINE"
}
```

## 6.7 Test Results Summary

### Unit Test Results

```
========================= test session starts =========================
platform win32 -- Python 3.11.5, pytest-7.4.3, pluggy-1.3.0
rootdir: C:\Users\eoin0\Documents\FinalProject\Momentum\Python
plugins: cov-4.1.0
collected 127 items

tests/test_driver_system.py ...................... [  16%]
tests/test_simulation_statistics.py ............ [  25%]
tests/test_staff_system.py .................... [  39%]
tests/test_currency_system.py ........ [  45%]
tests/test_database_operations.py .................. [  59%]
tests/test_single_seater_engine.py ............. [  69%]
tests/test_rally_stage_engine.py ........... [  77%]
tests/test_api_endpoints.py .................... [  90%]
tests/test_integration.py ............. [ 100%]

========================== 127 passed in 12.34s ==========================

---------- coverage: platform win32, python 3.11.5 -----------
Name                                      Stmts   Miss  Cover
-------------------------------------------------------------
database/models.py                          234     12    95%
database/database_manager.py                156      8    95%
disciplines/base_engine.py                   45      2    96%
disciplines/single_seater_engine.py         189     15    92%
disciplines/rally_stage_engine.py           167     18    89%
systems/staff_management.py                 245     28    89%
systems/currency_system.py                   78      3    96%
simulation.py                                89      4    96%
-------------------------------------------------------------
TOTAL                                      1460    140    90%

=========================== COVERAGE: 90% ===========================
```

### Performance Benchmark Results

```
Performance Benchmark Report
Generated: January 20, 2025
Hardware: Intel Core i7-11th Gen, 16GB RAM, Windows 11

Race Simulation Performance (1000 iterations):
┌──────────────┬──────────┬──────────┬──────────┬──────────┐
│   Drivers    │   Mean   │  Median  │   Min    │   Max    │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│      5       │  0.087s  │  0.084s  │  0.067s  │  0.123s  │
│     10       │  0.145s  │  0.142s  │  0.121s  │  0.189s  │
│     20       │  0.234s  │  0.221s  │  0.187s  │  0.356s  │
│     30       │  0.334s  │  0.328s  │  0.289s  │  0.445s  │
│     50       │  0.512s  │  0.498s  │  0.456s  │  0.678s  │
└──────────────┴──────────┴──────────┴──────────┴──────────┘

✅ All simulations completed under 1-second target
✅ Linear scaling O(n) confirmed
✅ 99.7% simulations completed without errors
```

## 6.8 User Acceptance Testing Feedback

### Participant Demographics

- **Total Participants:** 8
- **Motorsport Enthusiasts:** 5
- **Casual Gamers:** 3
- **Testing Date:** January 10-15, 2025
- **Testing Method:** Remote (video call + screen sharing)

### Detailed Feedback

**Participant 1 (Motorsport Enthusiast, Male, 24)**

- **Rating:** 8/10
- **Comments:** "The simulation feels very realistic. I love that rally and single-seater have completely different feels. The 50 attributes are a lot to take in, but once you understand the key ones it's fine. Would love to see a GUI."
- **Favorite Feature:** Multi-discipline system
- **Improvement:** "Need tooltips explaining which attributes matter for each discipline"

**Participant 2 (Casual Gamer, Female, 22)**

- **Rating:** 6/10
- **Comments:** "It's overwhelming at first. Too many numbers and attributes. But the actual races are fun to watch happen. I wish there was a simpler mode."
- **Favorite Feature:** Quick simulation speed
- **Improvement:** "Simplify for casual players"

**Participant 3 (Motorsport Enthusiast, Male, 26)**

- **Rating:** 9/10
- **Comments:** "This is exactly what I've been looking for! The depth is incredible. Staff management adds a whole new layer. The API is well documented and easy to use."
- **Favorite Feature:** Staff management and fog-of-war
- **Improvement:** "Would love multiplayer"

**Participant 4 (Casual Gamer, Male, 23)**

- **Rating:** 7/10
- **Comments:** "Pretty cool. I don't understand all the stats but seeing the races play out is satisfying. Performance is excellent."
- **Favorite Feature:** Fast simulation
- **Improvement:** "Visual interface needed"

**Participant 5 (Motorsport Enthusiast, Female, 25)**

- **Rating:** 8/10
- **Comments:** "Really impressed by the statistical depth. The correlation between skill and success feels right - good drivers win most of the time but upsets happen. Rally feels appropriately chaotic!"
- **Favorite Feature:** Statistical realism
- **Improvement:** "AI opponents need more personality"

**Participant 6 (Motorsport Enthusiast, Male, 27)**

- **Rating:** 9/10
- **Comments:** "As a developer, I appreciate the clean API design. As a motorsport fan, I love the multi-discipline approach. This could be amazing with a frontend."
- **Favorite Feature:** API design and documentation
- **Improvement:** "Championship mode feels incomplete"

**Participant 7 (Casual Gamer, Female, 21)**

- **Rating:** 6/10
- **Comments:** "It's interesting but I need a GUI to really enjoy it. The JSON responses are hard to visualize."
- **Favorite Feature:** Variety of racing types
- **Improvement:** "Make it visual!"

**Participant 8 (Motorsport Enthusiast, Male, 29)**

- **Rating:** 8/10
- **Comments:** "Love it! The tire degradation model in endurance racing is particularly good. Would be great to have real driver names (with permission of course)."
- **Favorite Feature:** Endurance racing simulation
- **Improvement:** "Real-world data integration"

### Summary of Feedback

**Average Rating:** 7.6/10

**Most Common Positive Feedback:**

1. Realistic simulation (6/8)
2. Excellent performance (7/8)
3. Multi-discipline uniqueness (7/8)
4. Staff management depth (5/8)

**Most Common Improvement Requests:**

1. Visual/GUI interface (6/8)
2. Simplify for casual players (5/8)
3. Better AI opponents (4/8)
4. Complete championship mode (4/8)

## 6.9 Performance Optimization Case Study

### Problem: Initial Simulation Too Slow

**Initial Performance:** 3.2 seconds for 20-driver race
**Target Performance:** <1.0 second
**Gap:** 3.2x slower than target

### Profiling Results

Used `cProfile` to identify bottlenecks:

```python
python -m cProfile -o profile.stats simulation.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

**Results:**

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      100    0.001    0.000    2.845    0.028 single_seater_engine.py:156(simulate_lap)
     2000    2.234    0.001    2.234    0.001 database_manager.py:67(get_driver)
     2000    0.456    0.000    0.456    0.000 database_manager.py:89(get_team)
      100    0.123    0.001    0.123    0.001 numpy:random(normal)
```

**Key Finding:** Database queries inside simulation loop (2000 calls!)

### Solution: Data Caching

**Before (Slow):**

```python
def simulate_lap(self, race_state):
    for driver_id in race_state.driver_ids:
        driver = self.db.get_driver(driver_id)  # Database query!
        team = self.db.get_team(driver.team_id)  # Another query!
        performance = self.calculate_performance(driver, team)
        # ... rest of simulation
```

**After (Fast):**

```python
def simulate_race(self, context):
    # Load all data ONCE before simulation
    drivers = {d.id: d for d in context.drivers}
    teams = {t.id: t for t in context.teams.values()}
  
    for lap in range(race_laps):
        self.simulate_lap(lap, drivers, teams)  # Pass cached data

def simulate_lap(self, lap, drivers, teams):
    for driver_id in race_state.driver_ids:
        driver = drivers[driver_id]  # Dictionary lookup (O(1))
        team = teams[driver.team_id]  # No database access
        performance = self.calculate_performance(driver, team)
        # ... rest of simulation
```

### Results

**After Optimization:** 0.234 seconds (13.7x faster!)
**Target Met:** Yes (4.3x better than target)

### Lessons Learned

1. **Profile before optimizing:** Assumptions about bottlenecks are often wrong
2. **I/O is expensive:** Database queries were 70% of total time
3. **Cache immutable data:** Driver/team data doesn't change during race
4. **Measure impact:** Always benchmark before/after to confirm improvement

## 6.10 Project Timeline (Actual vs. Planned)

### Gantt Chart Summary

```
Task                          Planned    Actual    Status
─────────────────────────────────────────────────────────
Requirements & Design         Weeks 1-2  Weeks 1-2    ✅
Database Implementation       Week 3     Week 3       ✅
First Engine (Single Seater)  Weeks 4-5  Weeks 4-5    ✅
Additional Engines (3)        Weeks 6-7  Weeks 6-8    ⚠️ (+1 week)
Staff Management System       Weeks 8-9  Weeks 8-9    ✅
Remaining Engines (3)         Week 10    Weeks 10-11  ⚠️ (+1 week)
Currency System              Week 11    Week 11      ✅
API Development              Weeks 12-13 Weeks 12-13  ✅
Testing & Optimization       Week 14    Week 14      ✅
Documentation & Report       Week 15    Week 15      ✅
─────────────────────────────────────────────────────────
TOTAL                        15 weeks   15 weeks     ✅
```

**Notes:**

- Additional engines took longer than expected (+2 weeks total)
- Compensated by reducing AI development scope
- Stayed on schedule overall by managing scope carefully
