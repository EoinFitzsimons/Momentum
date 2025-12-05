# Data, User, Environmental & Usability Requirements - DRAFT

## Data Requirements

### Overview
Momentum maintains a comprehensive motorsport simulation database supporting 7 racing disciplines, 1,781 drivers, 1,095 teams, 175 circuits, and 57,936 staff members. Data architecture uses SQLite with entity-relationship normalization to support both transactional operations (contracts, race results) and reporting queries (standings, statistics).

### Data Entities & Attributes

#### Driver Entity
- **Core Attributes**: driver_id, name, nationality, age, experience_level
- **Discipline Preferences** (0-100 scale): 
  - single_seater_affinity, rally_affinity, endurance_affinity, drag_affinity, street_affinity, rallycross_affinity, touring_affinity
- **Technical Skills** (0-100 scale): raw_speed, cornering_skill, qualifying_pace, racecraft, consistency, car_setup_understanding, aerodynamics_understanding, surface_adaptation
- **Physical Attributes** (0-100 scale): racecraft, concentration, stress_resistance, reaction_time, fitness_level
- **Mental Attributes** (0-100 scale): determination, aggression, risk_tolerance, learning_curve
- **Personality Traits** (0-100 scale): team_player_score, media_handling, mentality
- **Employment**: contract_team_id, contract_start_date, contract_end_date, salary_currency, salary_amount
- **Race History**: races_competed, wins, podiums, pole_positions, fastest_laps, points_total

#### Team Entity
- **Identity**: team_id, name, headquarters_location, founding_year, budget_currency, budget_amount
- **Discipline Focus**: primary_discipline, secondary_disciplines, specialization_level (0-100)
- **Hierarchy**: tier (1-5, where 1 = top-tier), market_segment (luxury/premium/mid-market/budget)
- **Relationships**: owner_id, manager_id, primary_sponsor_ids, secondary_sponsor_ids
- **Infrastructure**: factory_quality (0-100), wind_tunnel_capability (0-100), simulation_center_capability (0-100)
- **Performance**: recent_race_average_position, championship_standing_position, reliability_index (0-100)

#### Track/Circuit Entity
- **Identity**: circuit_id, name, country, city, established_year
- **Physical Characteristics**:
  - layout_type (street/permanent/temporary)
  - total_length_km, number_of_corners, overtaking_opportunities (0-10)
  - elevation_change_m, average_lap_time_reference_s
  - surface_type (asphalt/gravel/mixed)
  - weather_susceptibility (0-100, higher = more weather-dependent)
- **IMA Grading**: safety_rating (0-100), security_rating (0-100), medical_facility_rating (0-100)
- **Racing Characteristics**:
  - high_speed_sections, technical_sections, corner_types (hairpin_count, chicane_count, etc.)
  - driver_preference_data (which driver attributes matter most here)
- **Capacity**: spectator_capacity, pit_lane_length_m, garage_spaces

#### Staff Entity
- **Identity**: staff_id, name, nationality, age, experience_years
- **Role Classification**:
  - role_type (engineer, mechanic, strategist, physiotherapist, aerodynamicist, etc. - 25+ roles)
  - specialization_discipline (which discipline they specialize in)
  - experience_level (junior/senior/expert)
- **Competence**: skill_rating (0-100), reliability_score (0-100), innovation_score (0-100)
- **Employment**: employed_team_id, contract_start_date, contract_end_date, salary_currency, salary_amount
- **Performance Multipliers**: 
  - driver_development_bonus (0-1.0)
  - race_performance_bonus (0-1.0)
  - reliability_improvement_bonus (0-1.0)

#### Race Result Entity
- **Race Identity**: result_id, race_id, circuit_id, race_date, discipline_type
- **Driver/Team Info**: driver_id, team_id, car_number, grid_position, final_position
- **Performance Data**:
  - laps_completed, completed_percentage (0-100)
  - fastest_lap_time_s, slowest_lap_time_s, average_lap_time_s
  - pit_stop_count, pit_stop_time_total_s
  - tyre_degradation_observed (0-100)
  - fuel_consumption_observed (liters)
  - reliability_issues (boolean flags for each component)
- **Race Events**:
  - collisions_count, penalties_count, off_track_incidents_count
  - overtakes_completed, overtakes_attempted, overtakes_successful_percentage
  - yellow_flags_triggered, safety_car_involvement (boolean)
- **Points Awarded**: championship_points, bonus_points, driver_rating

#### Championship/Season Entity
- **Identity**: championship_id, season_year, discipline_type
- **Structure**:
  - race_count, total_rounds, points_system (current points formula)
  - start_date, end_date, status (planning/ongoing/completed)
- **Standings**: 
  - driver_standings (dynamic, updated per race)
  - team_standings (dynamic, updated per race)
  - current_leader_driver_id, current_leader_team_id

### Data Structures & Relationships

**UML Entity-Relationship Diagram Summary:**
```
Driver (1) ---> (N) RaceResult
Driver (1) ---> (1) Team
Driver (1) ---> (N) ContractHistory
Team (1) ---> (N) Staff
Team (1) ---> (N) RaceResult
Team (1) ---> (N) ChampionshipEntry
Circuit (1) ---> (N) RaceResult
RaceResult (N) ---> (1) Championship
Race (1) ---> (N) RaceResult
Championship (1) ---> (N) Race
```

### Data Formats & Validation Rules

#### Numeric Attributes
- **0-100 Scale Attributes**: All skill, preference, and quality ratings must be floats in range [0.0, 100.0]
- **Percentages**: Completed_percentage, overtakes_successful_percentage must be in [0, 100]
- **Time Values**: All lap times in seconds (float), pit stop times > 0
- **Currency**: Budget amounts in specified currency (EUR default), salary amounts > 0

#### Text/String Attributes
- **Names**: Max 100 characters, alphanumeric + spaces, no special characters except hyphens
- **Nationality**: 2-letter ISO country code (e.g., "IE", "GB", "DE")
- **Enums**: 
  - layout_type ∈ {street, permanent, temporary}
  - role_type ∈ {engineer, mechanic, strategist, physiotherapist, aerodynamicist, ...25+ roles}
  - tier ∈ {1, 2, 3, 4, 5}
  - status ∈ {planning, ongoing, completed}

#### Constraints & Business Rules
1. **Driver Contract Uniqueness**: No driver can have overlapping active contracts
2. **Staff Capacity**: Each team has max staff count based on tier (Tier 1 = 50+ staff, Tier 5 = 5-10 staff)
3. **Race Date Ordering**: Races in championship must have monotonically increasing dates
4. **Budget Validity**: Team budget must be non-negative; salary_amount ≤ team_budget_remaining
5. **Experience Validity**: driver_age ≥ 16; experience_years ≤ driver_age - 16
6. **Championship Uniqueness**: Only one active championship per discipline per season
7. **Result Completion**: final_position must be filled when race_status = "completed"
8. **Overtaking Logic**: overtakes_completed ≤ overtakes_attempted

#### Data Persistence Rules
- **Transactional**: All race results, contracts, and race events use ACID transactions (SQLite with PRAGMA journal_mode=WAL)
- **Archival**: Completed championships older than 5 seasons can be archived to backup database
- **Audit Trail**: Driver attribute changes, contract modifications logged with timestamp and user_id
- **Referential Integrity**: Foreign key constraints enforced; orphaned records prevented

### Data Output Formats
- **API Responses**: JSON with ISO 8601 timestamps, decimal precision 2 for currency
- **CSV Export**: Championship standings, race results (UTF-8 encoding, comma-separated)
- **Telemetry**: Binary format (saved to `saves/telemetry_*.csv` for post-race analysis)
- **Reports**: Markdown summary tables for standings, statistics

---

## User Requirements

### Overview
Momentum is designed for motorsport enthusiasts who want to manage and simulate racing championships across 7 disciplines. Users span from casual players (single-race players) to competitive players (full career modes). The system must support the following user personas and their scenarios.

### User Personas

#### Persona 1: Casual Racer (Gary)
- **Background**: Plays racing games 5-10 hours/week, enjoys quick races without deep management
- **Goals**: Run quick race simulations, see exciting AI overtakes, experience different racing types
- **Typical Tasks**:
  - Select pre-built championship (Single-Seater, Rally, Drag)
  - Pick a track from 175 available circuits
  - Run a 10-20 minute race simulation
  - View race highlights and final results
- **Preferences**: Minimal setup, instant gratification, visual feedback during race
- **Success Metric**: Can complete a full race within 3 clicks from main menu

#### Persona 2: Team Manager (Priya)
- **Background**: Enjoys complex strategy games, likes managing resources and talent
- **Goals**: Build a competitive team, manage staff and driver contracts, compete in season championship
- **Typical Tasks**:
  - Create custom team with budget allocation
  - Hire drivers and staff (engineers, mechanics, strategists)
  - Negotiate contracts and manage payroll
  - Analyze driver performance across multiple races
  - Adjust team strategy (pit stop timing, tire compounds, car setup)
  - Track championship standings over full season (12-20 races)
- **Preferences**: Deep menus, data-driven decision making, save/load game state
- **Success Metric**: Manage team through full season; see measurable improvement from race 1 to race 20

#### Persona 3: Competition Enthusiast (Marcus)
- **Background**: Watches real motorsport, wants to replicate real championship drama
- **Goals**: Create realistic championship simulations, test "what-if" scenarios, share results
- **Typical Tasks**:
  - Import real-world driver/team/track data (or use 175 pre-built circuits)
  - Create 20-race championship calendar
  - Simulate full season multiple times with different setups
  - Compare results across runs
  - Export standings/results for comparison with real data
- **Preferences**: Automation, batch operations, data export, realistic simulation
- **Success Metric**: Can create and simulate realistic 20-race championship in < 30 minutes

#### Persona 4: System Admin/Content Creator
- **Background**: Wants to extend Momentum with new content (tracks, drivers, championships)
- **Goals**: Create custom racing disciplines, import new circuits, generate synthetic driver data
- **Typical Tasks**:
  - Add 10 new circuits to the database
  - Create custom championship format
  - Generate 500 new drivers with realistic attributes
  - Configure difficulty levels (AI aggression, performance scaling)
- **Preferences**: CLI tools, bulk operations, scripting support
- **Success Metric**: Can import 175 circuits and generate 1,800 drivers without manual editing

### Functional Goals from User Perspective

#### Goal 1: Create & Configure a Championship
**User Story**: "As a team manager, I want to create a custom single-seater championship with 16 races, custom points system, and specific driver roster so I can run my own competitive simulation."

**Acceptance Criteria**:
- [ ] User can select or create new championship in < 2 clicks
- [ ] Championship configuration page allows:
  - [ ] Discipline selection (7 types)
  - [ ] Number of rounds (1-30)
  - [ ] Points system (dropdown: F1 2024, F2, F3, Custom)
  - [ ] Driver roster selection (predefined pools or custom)
  - [ ] Track calendar (pick from 175 circuits, or upload custom)
- [ ] Estimated race time per round displayed
- [ ] User can preview calendar before confirming
- [ ] Championship saved and can be resumed later

#### Goal 2: Simulate a Single Race
**User Story**: "As a casual racer, I want to run a single race simulation and watch real-time overtakes and drama so I can enjoy the racing experience without complex management."

**Acceptance Criteria**:
- [ ] User can initiate race in < 3 clicks from main menu
- [ ] Real-time visualization shows:
  - [ ] Driver positions (top 10 minimum)
  - [ ] Gap to leader and next car
  - [ ] Current lap/total laps
  - [ ] Pit stop activity
  - [ ] Overtake events (highlighted in UI)
- [ ] Race completes in < 5 minutes for 30-lap race (real-time playback optional, fast-forward available)
- [ ] Results show podium, fastest lap, best overtaker of the race
- [ ] User can share/export results

#### Goal 3: Manage Team Finances & Staff
**User Story**: "As a team manager, I want to hire drivers and staff, negotiate contracts, and manage a salary budget so my team's performance improves and I stay within budget constraints."

**Acceptance Criteria**:
- [ ] User can view available drivers with:
  - [ ] Name, age, experience, skill ratings (0-100 scale)
  - [ ] Estimated salary (automatically calculated)
  - [ ] Discipline affinity scores
- [ ] Hire driver UI shows:
  - [ ] Salary impact on team budget
  - [ ] Estimated driver performance in team setup
  - [ ] Contract duration options (1-5 years)
- [ ] User can see current team roster with:
  - [ ] Driver/staff names, salaries, contract expiry dates
  - [ ] Performance in current season
  - [ ] Optional actions: extend contract, release, promote/demote role
- [ ] Budget tracking shows:
  - [ ] Current budget remaining
  - [ ] Payroll total
  - [ ] Spending by category (driver salaries, staff, R&D investment)
- [ ] User receives warning when approaching budget limit (90%, 100%)

#### Goal 4: View Championship Standings & Statistics
**User Story**: "As a competition enthusiast, I want to see up-to-date championship standings, driver/team statistics, and historical comparisons so I can track my simulation's realism and progress."

**Acceptance Criteria**:
- [ ] Standings screen shows:
  - [ ] Driver championship table (ranked by points, diff to leader, races completed)
  - [ ] Team championship table (same metrics)
  - [ ] Detailed stats per driver (races, wins, podiums, DNFs, avg finishing position)
  - [ ] Discipline-specific stats (e.g., fastest lap count, overtakes in rally)
- [ ] Statistics dashboard includes:
  - [ ] Lap time distributions (histogram)
  - [ ] Performance trends (driver skill correlation to results)
  - [ ] Race-by-race breakdown
  - [ ] Head-to-head driver comparisons
- [ ] User can export standings as CSV or JSON
- [ ] Historical standings (previous seasons) accessible

#### Goal 5: Adjust Race Difficulty & AI Behavior
**User Story**: "As a casual racer, I want to adjust difficulty settings so the AI is challenging but fair, and I can select which racing discipline feels best to me."

**Acceptance Criteria**:
- [ ] Settings menu allows:
  - [ ] Difficulty slider: Easy / Normal / Hard / Expert
  - [ ] AI aggression: Defensive / Balanced / Aggressive
  - [ ] Realism mode: Arcade (forgiving) / Sim (punishing)
  - [ ] Damage model: Off / Reduced / Full
  - [ ] Weather impact: Off / Reduced / Full
- [ ] User can preview difficulty impact (estimated win probability displayed)
- [ ] Settings persist across sessions

### UML Use Case Diagram Overview
(Summary - full UML diagram to be provided in Implementation section)

```
Actor: Player
├─ UC-1: Read Driver Details
├─ UC-2: Read Race Configuration
├─ UC-3: Create Race Result (Simulate Race)
├─ UC-4 to UC-10: Championship Management (7 use cases)
├─ UC-11 to UC-14: Team Management (4 use cases)
├─ UC-15 to UC-19: Personnel Management (5 use cases)
└─ UC-20: Multi-Currency Financial System

Actor: System Administrator
├─ Import Circuits
├─ Generate Synthetic Drivers
├─ Configure AI Difficulty
└─ Batch Data Operations
```

---

## Environmental Requirements

### Overview
Momentum is a desktop application designed for single-user or LAN environments. It requires Python 3.11+, SQLite, and modest hardware. The architecture separates frontend (PyQt6 GUI) from backend (FastAPI), enabling optional web deployment.

### Hardware Requirements

#### Minimum (Playable)
- **CPU**: Dual-core processor @ 2.0 GHz (Intel i5-7th gen or equivalent)
- **RAM**: 4 GB
- **Storage**: 2 GB SSD (for application, database, save files)
- **GPU**: Integrated graphics (no NVIDIA/AMD required; rendering via PyQt6 CPU)
- **Network**: None required (offline operation supported)

#### Recommended (Smooth Experience)
- **CPU**: Quad-core processor @ 2.5 GHz (Intel i7-8th gen or AMD Ryzen 5)
- **RAM**: 8 GB (allows multiple races in background)
- **Storage**: 4 GB SSD (faster database queries)
- **GPU**: Discrete GPU (optional, improves real-time telemetry visualization)
- **Network**: 10 Mbps (only needed for multiplayer or cloud features; not in MVP)

#### Performance Targets
- **30 FPS real-time race simulation**: 20-driver race on recommended hardware
- **Race initialization time**: < 2 seconds
- **Database query time**: < 500 ms for standings retrieval
- **Application startup time**: < 3 seconds

### Operating Systems

#### Supported
- **Windows**: 10 (Build 1909+), 11 (all versions)
- **macOS**: 11 Big Sur+, 12 Monterey+, 13 Ventura+ (Intel & Apple Silicon)
- **Linux**: Ubuntu 20.04 LTS, 22.04 LTS, Fedora 36+

#### Not Supported
- **Windows**: 7, 8, 8.1 (EOL; Python 3.11 incompatible)
- **macOS**: < 11 (legacy OpenGL issues)
- **Linux**: Older distributions without Python 3.11 prebuilt packages

### Software Stack & Dependencies

#### Core Dependencies (must be installed)
| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.104+ | REST API backend |
| uvicorn | 0.24+ | ASGI application server |
| PyQt6 | 6.4+ | Desktop GUI framework |
| SQLite | 3.35+ | Database (bundled with Python) |
| NumPy | 1.24+ | Numerical calculations (simulation) |
| Pandas | 2.0+ | Data analysis (standings) |
| Pydantic | 2.0+ | Data validation |
| Faker | 20.0+ | Synthetic data generation |

#### Optional Dependencies
| Component | Purpose | Platform |
|-----------|---------|----------|
| PyInstaller | Executable build (Windows .exe) | Windows |
| Pytest | Unit testing | Development |
| Black | Code formatting | Development |
| mypy | Static type checking | Development |

#### External Integrations (Optional)
- **Real-time currency exchange rates**: requests library + OpenExchangeRates API (fallback: cached rates)
- **Weather data**: (future) OpenWeatherMap API for realistic weather conditions

### Network & Deployment

#### Single-Player (Offline)
- **Network Required**: No
- **Setup**: Standalone desktop application
- **Database**: Local SQLite file
- **Deployment**: PyInstaller executable bundle

#### LAN Multiplayer (Future)
- **Network Required**: Yes (TCP/IP on local network)
- **Setup**: FastAPI backend on server, multiple PyQt6 clients
- **Database**: Shared SQLite on server (or PostgreSQL for multi-user locks)
- **Deployment**: Backend on NAS/server; clients via network share or REST API

#### Cloud Deployment (Future)
- **Network Required**: Yes (HTTPS required)
- **Setup**: FastAPI backend on cloud VM, web frontend (React/Vue)
- **Database**: PostgreSQL/MySQL on cloud
- **Deployment**: Docker containers on AWS/Azure/GCP

### Data Storage & Persistence

#### Database Location
- **Windows**: `C:\Users\<username>\Documents\FinalProject\Momentum\Python\momentum.db`
- **macOS**: `~/Documents/FinalProject/Momentum/Python/momentum.db`
- **Linux**: `~/Documents/FinalProject/Momentum/Python/momentum.db`

#### Save Game Files
- **Location**: `saves/` directory in application root
- **Format**: CSV telemetry, JSON game state
- **Backup**: Manual user backup recommended; no automatic cloud sync

#### Database Size Estimates
- **Initial Load**: ~15 MB (1,781 drivers, 1,095 teams, 175 tracks, 57,936 staff)
- **Per Season**: +2-5 MB (race results, championship data)
- **Growth Cap**: ~200 MB for 10 years of game data

### External Interfaces & API Contracts

#### FastAPI Backend Endpoints
- **Base URL**: `http://127.0.0.1:8000` (localhost, single-player)
- **Health Check**: `GET /health` → `{"status": "ok"}`
- **Drivers**: `GET /drivers?discipline=SINGLE_SEATER&limit=100`
- **Race Simulation**: `POST /simulate/race` with payload
- **Championship Standings**: `GET /season/{season_id}/standings`

#### PyQt6 Frontend Integration
- **Threading**: All API calls via QThread to prevent UI blocking
- **Signal/Slot**: Qt signals for inter-component communication
- **Telemetry**: Real-time race data fed to visualization via QTimer (30 Hz polling)

#### File I/O
- **Database**: SQLite PRAGMA synchronous=NORMAL; journal_mode=WAL for concurrent reads
- **Configuration**: `.env` file (not in git) for API keys, paths, settings
- **Log Files**: `logs/` directory with crash reports and activity logs

### Development & Build Environment

#### Build Pipeline
1. **Code Quality**: pytest (unit tests), black (formatting), mypy (type checking)
2. **Packaging**: PyInstaller for Windows .exe, dmg for macOS, AppImage for Linux
3. **CI/CD**: GitHub Actions (optional) for automated builds
4. **Version Control**: Git; releases tagged as `v1.0.0`, `v1.1.0`, etc.

#### Target Platforms for Release
- **Windows**: .exe installer (tested on Windows 10/11)
- **macOS**: .dmg bundle (universal binary for Intel & Apple Silicon)
- **Linux**: AppImage (portable) or snap (Ubuntu)

---

## Usability Requirements

### Overview
Momentum prioritizes **accessibility and learnability** for a diverse audience (casual gamers to simulation enthusiasts). Interaction design targets 2-hour onboarding for complex features and < 30 seconds for simple tasks (e.g., starting a race).

### Learnability Metrics

#### Requirement 1: Novice Onboarding
**Metric**: New users (zero prior Momentum experience) must complete a tutorial championship and understand core mechanics within 2 hours.

**Acceptance Criteria**:
- [ ] Tutorial mode covers:
  - [ ] Main menu navigation (< 5 min)
  - [ ] Creating a championship (< 10 min)
  - [ ] Simulating a single race, understanding UI (< 15 min)
  - [ ] Reading standings and basic statistics (< 10 min)
  - [ ] Hiring a driver and managing budget (< 15 min)
  - [ ] Free-form play with guided hints (remaining time)
- [ ] Guided highlights (UI tooltips, video snippets) appear automatically on first visit to each screen
- [ ] Tutorial can be skipped, but **strongly recommended** for first run
- [ ] Progress saved after each major step

#### Requirement 2: Expert Efficiency
**Metric**: Experienced users (> 10 hours playtime) must perform common tasks quickly without tutorial support.

**Acceptance Criteria**:
- [ ] Keyboard shortcuts available for frequent actions:
  - [ ] Ctrl+N: New Championship
  - [ ] Ctrl+S: Save Game
  - [ ] Ctrl+R: Run Race
  - [ ] Ctrl+H: View History
- [ ] Quick-start buttons available on each main screen (bypass deep menus)
- [ ] Customizable UI (adjustable font size, dark mode toggle, layout presets)
- [ ] Expert mode disables hints and confirmation dialogs (opt-in via settings)

#### Requirement 3: Documentation & Help
**Metric**: Users must find answers to "How do I...?" questions within 2 minutes via in-game help system.

**Acceptance Criteria**:
- [ ] In-game help menu with:
  - [ ] FAQ (30+ questions covering common tasks)
  - [ ] Glossary of terms (driver attributes, track characteristics, race formats)
  - [ ] Video tutorials (linked; optional external YouTube channel)
  - [ ] Contact support email
- [ ] Context-sensitive help (? icon on each screen; clicking shows relevant FAQ)
- [ ] Searchable help (user can search "overtaking" and find relevant FAQs)

### Accessibility Constraints

#### Requirement 4: Visual Accessibility
**Standard**: WCAG 2.1 Level AA compliance where applicable to desktop GUI.

**Acceptance Criteria**:
- [ ] Color contrast ratio ≥ 4.5:1 for all text (verified via WebAIM Contrast Checker)
- [ ] Text scaling: UI remains functional at 125% and 200% magnification
- [ ] Font selection: Sans-serif primary font (readability); min size 12pt default
- [ ] Color blindness support: Don't rely solely on color to convey information
  - [ ] Graphs use pattern fills in addition to color
  - [ ] Driver/team identification uses both color AND icons/labels
- [ ] Dark mode available (UI elements readable on dark background)

#### Requirement 5: Input Accessibility
**Standard**: Keyboard-only navigation; mouse-free operation possible for all core tasks.

**Acceptance Criteria**:
- [ ] Tab order logical and predictable throughout UI
- [ ] Tab+Shift cycles backward through UI elements
- [ ] Enter key activates buttons; Space toggles checkboxes
- [ ] Escape key closes dialogs and returns to previous menu
- [ ] All dropdown menus keyboard-navigable (Arrow keys)
- [ ] Mouse hover tooltips duplicated as keyboard-accessible help text

#### Requirement 6: Audio/Alerts Accessibility
**Standard**: Information conveyed visually; audio cues supplementary only.

**Acceptance Criteria**:
- [ ] No critical information conveyed via sound alone
- [ ] Optional sound effects (pit stop alarm, collision sound) have visual equivalents (on-screen alert)
- [ ] Sound volume user-adjustable or mutable

### Response Time Expectations

#### Requirement 7: Interaction Latency
**Target**: All user-initiated actions receive visible feedback within **500 ms** maximum.

**Acceptance Criteria**:
- [ ] **Button click** → visible state change (highlight, text change): < 100 ms
- [ ] **Menu open/close** animation: < 300 ms
- [ ] **Database query** (e.g., load standings): < 500 ms
- [ ] **Save game**: < 1 second (user sees spinner/progress bar)
- [ ] **Race initialization**: < 2 seconds (loading screen with progress)
- [ ] **Standings table render** (20 rows): < 200 ms

#### Requirement 8: Real-Time Simulation Responsiveness
**Target**: 30 FPS race simulation (frame displayed every ~33 ms).

**Acceptance Criteria**:
- [ ] Race visualization updates at minimum 30 FPS on recommended hardware
- [ ] No UI blocking during race (race runs in background thread; UI remains responsive to user clicks)
- [ ] Fast-forward race (2x, 5x, 10x speed) available without dropping below 30 FPS
- [ ] Pause race functionality: pause-to-resume transition < 50 ms

### Error Rate Thresholds & Recovery

#### Requirement 9: Data Integrity & Error Handling
**Target**: Critical errors (e.g., database corruption, invalid race data) prevent game crash; user offered recovery option.

**Acceptance Criteria**:
- [ ] Unhandled exceptions caught and logged (never a raw traceback shown to user)
- [ ] User sees friendly error dialog: "Sorry, something went wrong. [Report / Continue]"
- [ ] Auto-save before race simulation; if race crashes, user can resume from save point
- [ ] Validation errors caught before database write (e.g., "Budget exceeded; reduce salary")
- [ ] Deprecation warnings: Old save files (v1.0) still load in v1.1 (backward compatibility)

#### Requirement 10: Input Validation & User Correction
**Target**: User input errors caught immediately; clear guidance on correction offered.

**Acceptance Criteria**:
- [ ] Numeric fields reject non-numeric input (or auto-correct)
- [ ] Date fields show calendar picker; invalid dates rejected
- [ ] Dropdown fields only allow predefined options
- [ ] Required fields marked with asterisk (*); submission blocked if empty
- [ ] Error messages specific: "Driver name too long (max 100 chars)" not "Invalid input"
- [ ] Suggestion auto-complete: typing driver name triggers auto-complete dropdown

### Workload & Input Limits

#### Requirement 11: Data Entry Efficiency
**Target**: Complex operations (e.g., importing 500 drivers) completable without excessive manual input.

**Acceptance Criteria**:
- [ ] Bulk import via CSV/JSON supported (drag-drop file into UI)
- [ ] Copy-paste data into tables supported (paste multiple rows)
- [ ] Template creation (create "Tier 1 Single-Seater Team" template; auto-fill staff roles)
- [ ] Pre-built championship templates (F1-style, Indy-style, rallying, etc.)
- [ ] Undo/Redo for all data modifications (max depth: 20 actions)

#### Requirement 12: Task Complexity Cap
**Target**: No single task requires > 10 UI clicks; most common tasks < 5 clicks.

**Acceptance Criteria**:
- [ ] **Quickest path to race**: Main Menu → Select Championship → Run Race (3 clicks)
- [ ] **Hire driver**: Team Menu → Staff → Drivers → Select Driver → Confirm (5 clicks)
- [ ] **View standings**: Main Menu → Championship → Standings (3 clicks)
- [ ] Advanced operations (multi-round scheduling, AI parameter tuning) may require more clicks but offer one-click shortcuts for power users

### Interface Consistency & Standards

#### Requirement 13: Design Consistency
**Target**: UI follows consistent layout, color scheme, and interaction patterns across all screens.

**Acceptance Criteria**:
- [ ] All screens share:
  - [ ] Top navigation bar (Back, Home, Settings, Help)
  - [ ] Consistent button style (Primary/Secondary/Danger colors)
  - [ ] Consistent typography (Title, Body, Caption text sizes)
  - [ ] Consistent spacing (margins, padding, gutters)
- [ ] Color scheme adheres to brand guidelines (Branding/style_guide.md)
- [ ] Icons reused consistently (same icon for same action across UI)
- [ ] Terminology consistent: "driver salary" not "driver pay" or "driver compensation" across screens

#### Requirement 14: Platform Conventions
**Target**: UI respects native platform conventions (Windows/macOS/Linux) for familiarity.

**Acceptance Criteria**:
- [ ] **Windows**: Menu bar follows Windows conventions; Ctrl+X/C/V for cut/copy/paste
- [ ] **macOS**: Menu bar in top system menu; Cmd+X/C/V shortcuts; Cmd+Q closes app
- [ ] **Linux**: GNOME or KDE conventions (whichever PyQt6 targets)
- [ ] File dialogs use native file browser (Qt native) not custom implementation
- [ ] Right-click context menus available where expected

#### Requirement 15: Mobile/Touch Responsiveness (Future Consideration)
**Target** (if web version deployed): Touch targets minimum 48x48 pixels; swipe gestures work naturally.

**Acceptance Criteria** (deferred for MVP):
- [ ] Buttons and clickable areas ≥ 48x48 px (accommodates touch without precision)
- [ ] Swipe-left/right for navigation between screens (optional)
- [ ] Touch keyboard doesn't obscure critical UI elements
- [ ] Long-press alternatives to right-click context menus

---

## Summary

This document specifies 15 concrete, measurable usability requirements across learnability, accessibility, performance, error handling, input efficiency, and interface consistency. Each requirement includes acceptance criteria that can be tested and verified during development and QA.

**Key Principles**:
1. **Accessibility First**: WCAG 2.1 AA, keyboard navigation, color blind safe, dark mode
2. **Fast & Responsive**: 30 FPS racing, < 500 ms interaction latency, < 2 hour onboarding
3. **Clear & Helpful**: In-game help, error messages, tooltips, tutorial mode
4. **Consistent & Familiar**: Design adheres to brand guidelines and platform conventions
5. **Forgiving**: Undo/Redo, auto-save, error recovery, input validation
