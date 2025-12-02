# 4.0 Technical Approach

## 4.1 Architecture Overview

**Backend: Python + FastAPI**
- REST API providing race simulation and game logic
- SQLite database (single-file deployment advantage)
- Async request handling for concurrent season processing
- Lightweight deployment (no enterprise framework dependencies)

**Frontend: PyQt6 GUI**
- Native desktop application with Python integration
- Direct access to backend simulation without API layer
- Qt framework provides professional UI components
- Cross-platform support (Windows, Mac, Linux)

**Why PyQt6?**
PyQt6 delivers professional desktop application quality whilst maintaining development velocity. Benefits include:
- Seamless Python integration (no separate language for frontend)
- Mature UI framework with extensive widget library
- Native performance without browser overhead
- Direct database access without REST API complexity
- Qt Designer for rapid UI prototyping

This architecture prioritises functionality over visual spectacle, allowing focus on simulation depth rather than 3D graphics engine complexity.

## 4.2 Multi-Discipline Engine Design

**Abstract Base Class Pattern**

All seven disciplines inherit from `BaseDisciplineEngine`:

```python
class BaseDisciplineEngine(ABC):
    @abstractmethod
    def simulate_race(self, context: DisciplineContext) -> RaceResult:
        pass
    
    @abstractmethod
    def calculate_performance_weights(self) -> PerformanceWeights:
        pass
```

**Discipline-Specific Implementations**

*Single-Seater Engine*
- Attributes emphasised: qualifying_pace (25% weight), aerodynamics_understanding (20%), cornering_skill (20%)
- Events: Grid penalties, DRS availability, tyre strategy, safety cars
- Qualifying: Separate simulation determining grid order

*Rally Engine*
- Attributes emphasised: surface_adaptation (30%), co_driver_communication (25%), car_control (20%)
- Co-driver system: Separate entity with pace note accuracy attribute affecting time loss
- Surface variation: Gravel/tarmac/snow modifiers (±15% performance swing)
- Stage-based: No direct competition, individual time trial format

*Endurance Engine*
- Attributes emphasised: consistency (30%), mechanical_sympathy (25%), tire_management (20%)
- Multi-driver: 2-3 drivers per car with fatigue system
- Time-based: 6/12/24 hour durations with reliability degradation curves
- Pit stop orchestration: Crew efficiency attributes, fuel calculation, tyre allocation

*Drag Engine*
- Attributes emphasised: reaction_time (40%), acceleration_control (30%), starting_skill (20%)
- Bracket system: Single-elimination tournament
- Run duration: 4-10 seconds per race
- Mechanical focus: Engine tuning, gear ratios, launch control parameters

*Street/Urban Engine*
- Attributes emphasised: traffic_navigation (25%), consistency (25%), energy_management (20%)
- Limited overtaking: Narrow circuits favour qualifying position
- Attack Mode: Energy boost system requiring strategic timing
- Environmental: Track evolution (rubber buildup) affecting grip levels

*Rallycross Engine*
- Attributes emphasised: starting_skill (30%), joker_lap_timing (25%), mixed_surface_adaptation (20%)
- Format: Short 5-6 lap races, knockout qualifying
- Joker lap: Compulsory alternate route (usually slower), strategic timing crucial
- Contact: Aggressive racing permitted, damage system affects performance

*Touring Car Engine*
- Attributes emphasised: racecraft (30%), consistency (25%), overtaking_skill (20%)
- Success ballast: Weight added to winners (+25kg per win, max 75kg)
- Multiple races: Weekend format with reverse grid race
- Close competition: Performance convergence rules limit development gap

**Performance Weighting Formula**

Base calculation across all disciplines:
```
Final Performance = (Driver Skill × 40%) + (Vehicle Performance × 30%) + 
                   (Environmental Factors × 20%) + (Random Variance × 10%)
```

Discipline-specific attribute sets modify which driver skills contribute to "Driver Skill" component.

## 4.3 Monte Carlo Race Simulation

**Why Monte Carlo?**

Traditional race simulators calculate outcomes deterministically (Codemasters F1 games) or use simplified probability (Football Manager's match engine approximates). Monte Carlo enables:
- Statistical accuracy with acceptable performance
- Natural variation preventing identical results
- Attribute-driven outcomes without hard-coded scenarios
- Scalability to multiple concurrent races

**Simulation Process**

1. **Pre-race Setup**
   - Load driver attributes (50+ per driver)
   - Calculate vehicle performance scores
   - Apply weather/track condition modifiers
   - Generate starting grid (qualifying simulation or predetermined)

2. **Lap-by-Lap Iteration**
   - Run 1,000 iterations per lap (configurable)
   - Each iteration calculates lap time from attribute combination
   - Random events probability checked (mechanical failure, crashes, overtakes)
   - Aggregate results determine most probable outcome

3. **Performance Calculation**
   ```python
   lap_time = base_lap_time + driver_modifier + vehicle_modifier + 
              weather_modifier + random_variance
   ```

4. **Event Probability**
   - Mechanical failure: Base 2% per lap × (100 - mechanical_sympathy) / 100
   - Crash: Base 1% per lap × (100 - consistency) / 100
   - Overtake success: Attacking overtaking_skill vs defending racecraft

5. **Result Aggregation**
   - Position changes tracked across iterations
   - Most common outcome selected (median lap time)
   - Championship points awarded per discipline rules

**Performance Optimisation**

Target: Complete 50-lap race simulation in under 100ms

Techniques applied:
- NumPy vectorisation (process all drivers simultaneously)
- Attribute pre-calculation (cache expensive operations)
- Probability tables (pre-computed distributions)
- Adaptive iteration count (reduce iterations if outcome convergence detected)

Current performance: 87ms average for 20-driver field, 50-lap race (tested on i5-9400F, 16GB RAM).

## 4.4 Procedural Championship Generation

**Generation Goals**

1. Balanced competition (no team dominates predictably)
2. Realistic feeder series (lower formulas feed higher categories)
3. Cultural authenticity (discipline-appropriate team names)
4. Budget realism (operating costs match real-world equivalents)

**Team Generation Algorithm**

```
For each discipline:
  Generate 10-12 teams with budget distribution:
    - Tier 1 (Top): 2 teams at 90-100% budget cap
    - Tier 2 (Midfield): 4-5 teams at 60-80% budget cap
    - Tier 3 (Backmarker): 4-5 teams at 40-60% budget cap
  
  Assign headquarters locations (affects staff hiring costs)
  Generate team names using cultural patterns
  Allocate manufacturer partnerships (where applicable)
```

**Driver Generation Algorithm**

```
For each championship:
  Generate 20-24 drivers per category
  
  Attribute generation:
    Base attributes: Random 40-60 (prevents immediate superstars)
    Specialisation: Boost 2-3 attributes by +10-15 (creates archetypes)
    Age: 18-35 for lower categories, 22-40 for premier classes
    Potential: Hidden attribute determining peak rating and age
  
  Progression curves:
    Young drivers (18-25): +2-5 rating per season
    Prime drivers (26-32): ±1 rating variance
    Declining drivers (33+): -1-3 rating per season
```

**Validation System**

Generated championships must pass quality checks:

1. **Competitive Balance Test**
   - Run 1,000 simulated seasons
   - Verify no single team wins >40% of championships
   - Ensure all teams win at least once across 1,000 seasons

2. **Performance Distribution Test**
   - Driver ratings must form bell curve (normal distribution)
   - Vehicle performance must span 5-10 second lap time range
   - Midfield teams cluster within 1% performance gap

3. **Authenticity Test**
   - Budget allocations match real-world team spending
   - Driver salaries correlate with performance ratings
   - Team facility costs reflect headquarters location (Monaco expensive, Eastern Europe cheaper)

4. **Progression Path Test**
   - Successful drivers in feeder series receive promotion offers
   - Underperforming premier class drivers demoted to lower categories
   - Retirement ages cluster around real-world patterns (35-40)

**Cultural Authenticity Layer**

Faker library (24 locales) generates names matching discipline culture:

- Rally: Scandinavian/Finnish bias (WRC historical dominance)
- Single-Seater: International mix weighted toward European/Brazilian names (F1 patterns)
- NASCAR/Drag: North American naming patterns
- Touring Cars: Regional variation per championship (BTCC British-focused, V8 Supercars Australian)

Team names follow six authentic patterns:
1. Manufacturer teams (e.g., "Apex Motorsport")
2. Personal names (e.g., "Fitzsimons Racing")
3. Geographic references (e.g., "Silverstone Performance")
4. Sponsor names (e.g., "Velocity Energy Racing")
5. Heritage names (e.g., "Classic Automotive")
6. Technical terms (e.g., "Traction Engineering")

No real-world trademarks used (avoids licensing issues whilst maintaining authenticity).

## 4.5 Persistent World Simulation

**Simultaneous League Processing**

All championships progress concurrently:

```python
def advance_season(world_state: WorldState) -> WorldState:
    # Process all leagues in parallel
    for discipline in RacingDiscipline:
        championships = world_state.get_championships(discipline)
        for championship in championships:
            race_result = simulate_next_race(championship)
            update_standings(championship, race_result)
            process_transfers(championship)
            update_driver_ratings(championship)
    
    return world_state
```

**Transfer Market System**

Driver movements driven by:
- Performance vs expectations (underperforming champions sought by better teams)
- Contract expiry (AI negotiates deals based on budget/driver demands)
- Promotion opportunities (feeder series winners move to premier classes)
- Retirement (age-based probability, injury-triggered forced retirement)

Budget constraints enforce realism:
```
Team total spend = Driver salaries + Staff salaries + Facilities + Development + Operations
```

Top-tier single-seater team: £130M budget cap
- Driver salaries: £40-60M (2 drivers)
- Staff salaries: £25-35M (200+ personnel)
- Facilities: £10-15M annual operating costs
- Development: £20-30M (within technical regulations)
- Operations: £5-10M (transport, logistics, hospitality)

**Driver Progression Simulation**

Attributes evolve based on:
- Results (podiums boost confidence, retirements decrease it)
- Age (peak years 26-32, decline post-33)
- Experience (first 3 seasons show rapid improvement)
- Training (team investment affects development rate)

Hidden potential attribute determines peak rating:
- Low potential: Peak 70-75 rating
- Average potential: Peak 75-85 rating
- High potential: Peak 85-95 rating
- Generational talent: Peak 95+ rating (rare, 1-2 per generation)

**World State Persistence**

Save file structure (JSON format):
```json
{
  "season": 2025,
  "day": 145,
  "championships": [...],
  "drivers": [...],
  "teams": [...],
  "historical_results": [...],
  "player_progress": {...}
}
```

Estimated file size: 5-10MB for full season with all disciplines active.

## 4.6 Technology Stack

**Backend Technologies**

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| API Framework | FastAPI | 0.104.1 | Async support, automatic OpenAPI docs, Python type hints |
| Database | SQLite | 3.43 | Single-file deployment, zero configuration, adequate for 800K+ records |
| Simulation | NumPy + SciPy | 1.26 + 1.11 | Vectorised operations, statistical distributions |
| Name Generation | Faker | 20.1.0 | Multi-locale support, realistic name patterns |
| Currency | python-dotenv + requests | 1.0 + 2.31 | Real-time exchange rates, environment configuration |
| Validation | Pydantic | 2.5 | Runtime type checking, data validation |
| Testing | pytest | 7.4 | Comprehensive test framework, fixtures support |

**Frontend Technologies**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| GUI Framework | PyQt6 | 6.6 | Native desktop UI, cross-platform |
| Visualisation | Matplotlib | 3.8 | Race position charts, telemetry graphs |
| Data Tables | QTableWidget | PyQt6 | Driver/team listings, standings |
| Styling | Qt Style Sheets | - | Custom theming matching motorsport aesthetics |
| UI Design | Qt Designer | 6.6 | Rapid UI mockup and prototyping |

**Development Tools**

| Tool | Purpose |
|------|---------|
| Visual Studio Code | Primary IDE with Python extensions |
| Git + GitHub | Version control, issue tracking |
| Black | Python code formatting (PEP 8 compliance) |
| mypy | Static type checking |
| Postman | API endpoint testing |

---

# 5.0 Technical Details

## 5.1 Database Schema

**Driver Table** (50+ attributes)

```sql
CREATE TABLE drivers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    nationality TEXT,
    age INTEGER,
    
    -- Technical Skills (0-100 scale)
    raw_speed REAL,
    cornering_skill REAL,
    braking_skill REAL,
    acceleration_control REAL,
    qualifying_pace REAL,
    
    -- Mental Attributes
    consistency REAL,
    decision_making REAL,
    pressure_handling REAL,
    concentration REAL,
    
    -- Physical Attributes
    fitness REAL,
    reaction_time REAL,
    stamina REAL,
    
    -- Racecraft
    overtaking_skill REAL,
    defending_skill REAL,
    spatial_awareness REAL,
    race_starts REAL,
    
    -- Discipline-Specific
    surface_adaptation REAL,         -- Rally
    co_driver_communication REAL,    -- Rally
    mechanical_sympathy REAL,        -- Endurance
    tire_management REAL,            -- Endurance
    energy_management REAL,          -- Formula E/Street
    
    -- Career Data
    current_team_id INTEGER,
    contract_end_year INTEGER,
    salary INTEGER,
    championship_wins INTEGER,
    race_wins INTEGER,
    podiums INTEGER,
    
    -- Hidden Attributes
    potential INTEGER,               -- Peak rating achievable
    personality_type TEXT,           -- Affects AI decisions
    preferred_disciplines TEXT,      -- JSON array
    
    FOREIGN KEY (current_team_id) REFERENCES teams(id)
);
```

**Team Table**

```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    discipline TEXT NOT NULL,
    headquarters TEXT,
    
    -- Financial
    budget INTEGER,
    budget_tier INTEGER,            -- 1 (top) to 3 (backmarker)
    
    -- Performance
    vehicle_performance REAL,       -- 0-100 aggregate
    technical_staff_quality REAL,   -- Affects development rate
    pit_crew_efficiency REAL,       -- Pit stop time modifier
    
    -- Facilities
    factory_level INTEGER,          -- 1-5, affects development
    wind_tunnel_level INTEGER,
    simulator_level INTEGER,
    
    FOREIGN KEY discipline REFERENCES championships(discipline)
);
```

**Track Table**

```sql
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT,
    
    -- Layout Characteristics
    length_km REAL,
    corners INTEGER,
    surface_type TEXT,              -- Tarmac, gravel, snow, mixed
    
    -- IMA Grading System
    ima_grade TEXT,                 -- Grade 1-6 (safety rating)
    
    -- Performance Factors
    high_speed_ratio REAL,          -- Percentage of lap at high speed
    technical_sections INTEGER,     -- Number of complex corner sequences
    elevation_change REAL,          -- Metres vertical variation
    
    -- Environmental
    typical_weather TEXT,
    temperature_range TEXT,
    
    -- Discipline Compatibility
    compatible_disciplines TEXT     -- JSON array
);
```

**Championship Table**

```sql
CREATE TABLE championships (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    discipline TEXT NOT NULL,
    tier INTEGER,                   -- 1 (premier) to 5 (grassroots)
    season INTEGER,
    
    -- Structure
    num_rounds INTEGER,
    calendar TEXT,                  -- JSON array of track IDs with dates
    points_system TEXT,             -- JSON array [25,18,15,12,10,8,6,4,2,1]
    
    -- Rules
    budget_cap INTEGER,
    technical_regulations TEXT,     -- JSON describing allowed modifications
    
    -- Status
    current_round INTEGER,
    standings TEXT                  -- JSON array of {driver_id, points, wins}
);
```

**Current Database Contents**

- 1,781 drivers across all disciplines
- 1,095 teams (varies per discipline: 10-24 teams each)
- 175 tracks (circuits_database.json awaiting import)
- 57,936 staff (engineers, mechanics, strategists)

## 5.2 API Endpoint Design

**Core Simulation Endpoints**

```
POST /simulate/race
Request: {
  "championship_id": int,
  "race_number": int,
  "weather": "dry|wet|mixed",
  "track_condition": "green|optimal|rubbered"
}
Response: {
  "results": [
    {"position": 1, "driver_id": 123, "time": "1:32:45.123", "points": 25},
    ...
  ],
  "events": [
    {"lap": 12, "driver_id": 45, "event": "mechanical_failure"},
    ...
  ],
  "fastest_lap": {"driver_id": 78, "time": "1:23.456"},
  "simulation_time_ms": 87
}
```

```
POST /season/create
Request: {
  "discipline": "SINGLE_SEATER",
  "tier": 1,
  "num_teams": 10,
  "num_races": 20
}
Response: {
  "championship_id": 15,
  "calendar": [...],
  "teams": [...],
  "drivers": [...]
}
```

```
GET /season/standings
Parameters: championship_id
Response: {
  "driver_standings": [
    {"position": 1, "driver_id": 123, "points": 225, "wins": 8},
    ...
  ],
  "constructor_standings": [
    {"position": 1, "team_id": 5, "points": 412},
    ...
  ]
}
```

**Database Query Endpoints**

```
GET /drivers?discipline=SINGLE_SEATER&min_rating=80
Response: [
  {
    "id": 123,
    "name": "Liam Murphy",
    "age": 24,
    "overall_rating": 87,
    "current_team": "Apex Motorsport",
    "key_attributes": {
      "raw_speed": 91,
      "qualifying_pace": 89,
      "consistency": 82
    }
  },
  ...
]
```

```
GET /teams?discipline=RALLY_STAGE&budget_tier=1
Response: [...]
```

```
GET /tracks?discipline=ENDURANCE&country=France
Response: [...]
```

**Game Loop Endpoints (In Development)**

```
POST /game/advance-day
Request: {"save_id": "player_save_001"}
Response: {
  "new_date": "2025-06-15",
  "events": [
    {"type": "race_completed", "championship": "Formula 1", "winner": "Driver X"},
    {"type": "contract_offer", "driver": "Driver Y", "team": "Team Z"},
    ...
  ]
}
```

## 5.3 Testing Strategy

**Unit Testing**

Target: 80% code coverage for core simulation

Test categories:
- Attribute calculations (verify weighting formulas)
- Monte Carlo convergence (ensure statistical validity)
- Database operations (CRUD integrity)
- API request/response validation (Pydantic schemas)

Example test:
```python
def test_single_seater_performance_calculation():
    driver = create_test_driver(raw_speed=90, cornering=85, qualifying=88)
    vehicle = create_test_vehicle(performance=87)
    context = create_test_context(weather="dry", track="high_speed")
    
    result = SingleSeaterEngine().calculate_performance(driver, vehicle, context)
    
    assert 85 <= result <= 95  # Expected range
    assert result > calculate_performance(worse_driver, vehicle, context)
```

**Integration Testing**

Full race simulations with known inputs:
- Verify race completion without errors
- Check championship points allocation
- Validate driver rating updates post-race
- Ensure database consistency after transactions

**Playability Testing**

Key metrics:
- Time to complete single race (target: <100ms)
- Time to complete full season (target: <30s)
- Memory usage (target: <2GB)
- UI responsiveness (target: <16ms frame time)

User experience testing:
- Can player understand simulation outcomes?
- Do results feel fair/realistic?
- Is progression satisfying?
- Are AI decisions believable?

**Statistical Validation**

Monte Carlo accuracy tests:
- Run 10,000 identical races
- Verify normal distribution of results
- Ensure no single driver wins >25% (proves variance)
- Check for systematic biases (e.g., pole position advantage should be ~15-20% win rate)

Performance validation:
- Compare simulated lap times to real-world equivalents (Formula 1: 1:30-1:40 for typical circuit)
- Verify championship points distributions match real seasons (dominant team ~50-60% of points, not 80-90%)

## 5.4 Known Limitations & Risks

**Current Implementation Status**

| Component | Completion | Status |
|-----------|-----------|---------|
| Simulation Engine | 85% | Core logic working, needs event variety |
| Database Models | 95% | All tables defined, track import pending |
| API Endpoints | 70% | Simulation working, game loop incomplete |
| PyQt6 GUI | 60% | Core screens functional, needs polish |
| Save/Load System | 0% | Not yet implemented |
| AI Decision Engine | 30% | Basic logic, needs personality-driven behaviour |

**Technical Risks**

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Monte Carlo performance degradation with 100+ concurrent races | Medium | High | Implement adaptive iteration counts, parallel processing |
| Database size exceeding SQLite practical limits | Low | Medium | Current projections show 50MB max per season, SQLite handles GB files |
| Procedural generation creating unbalanced championships | Medium | High | Validation suite rejects unbalanced outputs, manual oversight |
| AI making obviously illogical decisions | High | Medium | Personality system constrains decisions, playtesting exposes issues |

**Scope Management**

Minimum viable product for midpoint (December 2025):
- ✅ Single-seater discipline fully functional
- ✅ Working race simulation with statistical accuracy
- ✅ Database with 1,000+ drivers and teams
- ✅ API endpoints for race simulation
- ⚠️ PyQt6 GUI demonstrating playability (partial)
- ❌ Game loop/season progression (incomplete)
- ❌ Save/load system (not started)

Final deliverable (May 2026):
- All seven disciplines playable
- Complete game loop with season progression
- Save/load system
- Polished PyQt6 interface with data visualisation
- AI decision-making with personality system
- Comprehensive testing across all disciplines

Features deferred to post-graduation:
- Multiplayer career mode
- Steam Workshop integration
- Custom championship editor
- Historical season mode (recreate famous championships)

---

# 6.0 Resources Required

## 6.1 Development Environment

**Hardware**
- Development machine: i5-9400F, 16GB RAM, GTX 1660 (existing)
- Target performance: Runs adequately on i5 4th gen, 8GB RAM minimum
- No GPU requirements for simulation (CPU-bound)

**Software** (All Free/Open Source)
- Python 3.11 (free)
- Visual Studio Code (free)
- Git + GitHub (free for students)
- Unity Personal Edition (free up to $100K revenue)
- SQLite (public domain)
- PyQt6 (GPL license, suitable for academic use)

**Cloud Services** (Optional)
- GitHub repository hosting (free)
- Documentation hosting (GitHub Pages, free)

## 6.2 Data Sources

**Circuit Data**
- 175 circuits designed in `circuits_database.json`
- Real-world track lengths, corner counts from publicly available sources
- IMA grade information from FIA public documents
- No licensed content (all tracks renamed, characteristics generic)

**Name Generation**
- Faker library (open source, 24 locales)
- NameAPI and ParaNames as fallback (API key required, free tier sufficient)

**Currency Exchange Rates**
- ExchangeRate-API (free tier: 1,500 requests/month)
- Cache system reduces API calls to 1-2 per day

## 6.3 Budget Analysis

| Item | Cost | Justification |
|------|------|---------------|
| Development Hardware | £0 | Using existing PC |
| Software Licenses | £0 | Open source stack (PyQt6 GPL, Python, SQLite) |
| API Services | £0 | Free tiers sufficient for development |
| Cloud Hosting (Optional) | £0 | GitHub provides adequate infrastructure |
| **Total Development Cost** | **£0** | No expenditure required |

**Post-Graduation Commercial Considerations**

If pursuing commercial release:
- PyQt6 Commercial License: £450/year (if GPL incompatible with commercial model)
- Steam Direct fee: £80 (one-time per game)
- Marketing budget: £5,000-10,000 (estimated for indie launch)
- Legal costs (trademark filing, EULA): £1,000-2,000

**Revenue Projections (Speculative)**

Conservative estimate based on Motorsport Manager as benchmark:
- Price point: £15.99 (below F1 Manager, above mobile games)
- Steam revenue split: 70% to developer
- Sales target: 10,000 copies in first year (2.2% of Motorsport Manager's lifetime sales)
- Gross revenue: £159,900
- Net revenue after Steam cut: £111,930
- Break-even after commercial costs: ~£100,000 profit

Optimistic estimate:
- Price point: £24.99 (matching football management tier)
- Sales target: 50,000 copies (matching successful indie management sims)
- Net revenue after costs: £800,000+

YouTube content creator effect: Football Manager attributes 15-20% of sales to YouTube discovery (Sports Interactive GDC 2019). If 20 creators with 50K average subscribers produce content, potential reach: 1M viewers. Conservative 2% conversion: 20,000 sales.

## 6.4 Time Allocation

**Semester 1 (September - December 2025)**
- Weeks 1-4: Requirements engineering, proposal refinement
- Weeks 5-8: Core simulation engine development
- Weeks 9-12: Database implementation, API development
- Week 13: Midpoint submission preparation

**Semester 2 (January - May 2026)**
- Weeks 1-4: Complete game loop system
- Weeks 5-8: PyQt6 GUI completion and polish
- Weeks 9-12: Testing, bug fixing, refinement
- Weeks 13-14: Final report writing
- Week 15: Presentation preparation

**Weekly Time Commitment**
- Development: 15-20 hours
- Research/reading: 3-5 hours
- Documentation: 2-3 hours
- Testing/debugging: 5-7 hours
- **Total: 25-35 hours per week**

## 6.5 Supervisor Expectations

Seeking supervisor expertise in:
- Software architecture review (ensuring scalable design patterns)
- Statistical validation (Monte Carlo methodology verification)
- Testing strategy guidance (appropriate coverage metrics)
- Academic writing support (technical report structure)

Meeting frequency: Fortnightly (30-45 minutes)

Progress reporting: Functional demonstrations preferred over slide presentations

---

