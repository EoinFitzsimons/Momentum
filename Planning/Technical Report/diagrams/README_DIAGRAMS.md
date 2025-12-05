# UML Diagrams for Momentum Technical Report

## Diagrams Created

All diagrams are created in draw.io format (.drawio files) and are ready for export to PNG.

| Diagram | File | Purpose | Size |
|---------|------|---------|------|
| 1. System Architecture | ARCHITECTURE_DIAGRAM.drawio | Complete system components (PyQt6, FastAPI, SQLite, RaceLogic) | 10.3 KB |
| 2. Database ER Diagram | DATABASE_ER_DIAGRAM.drawio | Entity relationships (Driver, Team, Circuit, Staff, Race, Championship) | 11.9 KB |
| 3. 30 FPS Event Loop | EVENT_LOOP_30FPS.drawio | Real-time race engine timing breakdown (33ms per frame) | 12.2 KB |
| 4. Agent Decision State Machine | AGENT_STATE_MACHINE.drawio | Driver AI decision flow (pit stops, overtaking, speed control) | 14.2 KB |
| 5. Deployment Architecture | DEPLOYMENT_ARCHITECTURE.drawio | Windows/macOS/Linux deployment targets and database locations | 9.5 KB |
| 6. System Use Cases | SYSTEM_USE_CASES.drawio | All 29 use cases (UC-1 to UC-29) with relationships | 15.3 KB |

**Total: 73.4 KB of comprehensive UML diagrams**

## How to Export to PNG

### Option 1: Manual Export in draw.io (Recommended)

1. Open [draw.io](https://app.diagrams.net)
2. Click **File → Open → Upload From**
3. Select each `.drawio` file from this directory
4. Once opened, click **File → Export As → PNG**
5. Set quality to **High (300 DPI)** for technical report
6. Save as PNG with same name in this directory

### Option 2: Batch Export via Command Line (if `drawio-cli` installed)

```bash
drawio-cli -p ARCHITECTURE_DIAGRAM.png ARCHITECTURE_DIAGRAM.drawio
drawio-cli -p DATABASE_ER_DIAGRAM.png DATABASE_ER_DIAGRAM.drawio
drawio-cli -p EVENT_LOOP_30FPS.png EVENT_LOOP_30FPS.drawio
drawio-cli -p AGENT_STATE_MACHINE.png AGENT_STATE_MACHINE.drawio
drawio-cli -p DEPLOYMENT_ARCHITECTURE.png DEPLOYMENT_ARCHITECTURE.drawio
drawio-cli -p SYSTEM_USE_CASES.png SYSTEM_USE_CASES.drawio
```

### Option 3: Desktop Application

1. Download [draw.io Desktop](https://github.com/jgraph/drawio-desktop/releases)
2. Open each `.drawio` file
3. **File → Export As → PNG**

## Diagram Content Summary

### ARCHITECTURE_DIAGRAM.drawio
**Components:**
- Client Layer: PyQt6 GUI (launcher, race visualization, standings, team management)
- API Layer: FastAPI on port 8000 with 6 key endpoints
- Backend Services: RaceLogic (real-time engine), Overtaking System, Track Physics, Weather System
- 7 Discipline Engines (Single Seater, Rally, Endurance, Drag, Street, Rallycross, Touring)
- Data Access Layer: Database Manager, API Schemas (Pydantic)
- Database Layer: SQLite (1,781 drivers, 1,095 teams, 175 circuits, 57,936 staff)
- Data Files: circuits_database.json, currency_cache.json, saves, logs
- Configuration: config.py + .env

**Color Coding:**
- Blue: API/Communication
- Green: Backend Services
- Yellow: Discipline Engines
- Orange: Data Access
- Pink: Database
- Teal: Data Files

---

### DATABASE_ER_DIAGRAM.drawio
**Entities (7 main + 1 history table):**
1. **DRIVER**: 50+ attributes (skills, disciplines, employment, statistics)
2. **TEAM**: Budget, specialization, infrastructure ratings, performance metrics
3. **CIRCUIT**: 175 unique circuits with physical characteristics, IMA grading, racing features
4. **STAFF**: 25+ role types, competence ratings, performance bonuses
5. **RACE**: Championship reference, circuit, date, configuration, conditions
6. **RACE_RESULT**: 20+ attributes (position, times, degradation, events, points)
7. **CHAMPIONSHIP**: Season structure, status, points system, leader tracking
8. **CONTRACT_HISTORY**: Audit trail for driver/staff contracts

**Relationships:**
- Driver (1) → Team (N) [employed by]
- Team (1) → Staff (N) [employs]
- Team (1) → Race Result (N) [scored for]
- Circuit (1) → Race (N) [held at]
- Championship (1) → Race (N) [part of]
- Race (1) → Race Result (N) [produced by]
- Driver (1) → Race Result (N) [earned by]
- Contract (N) → Driver/Team (1) [history of]

**Scale:** 1,781 drivers × 1,095 teams × 175 circuits × 57,936 staff × ~500 race results per season

---

### EVENT_LOOP_30FPS.drawio
**Timing Budget: 33.3ms per frame (30 FPS)**

**11-Step Pipeline:**
1. Frame Start
2. Get Frame Time (Δt)
3. Input Handling (~1ms)
4. Driver Decisions (~5ms) - agent evaluation
5. Physics Calculations (~8ms) - CRITICAL PATH
6. Collision Detection (~3ms)
7. Overtaking System (~5ms)
8. Lap Completion (~3ms)
9. Environment Updates (~2ms)
10. Race State Aggregation (~2ms)
11. Telemetry Export (~2ms)
12. Render UI (~3ms)
13. Frame Complete / Sleep to 33.3ms

**Bottleneck Analysis:**
- Physics (8ms) + Decisions (5ms) = 13ms = 39% of budget
- Most critical for maintaining 30 FPS on 20+ driver races
- Real-time visualization doesn't block simulation (async)

---

### AGENT_STATE_MACHINE.drawio
**Per-Lap Decision Cycle:**

**States:**
1. **Read Environment** - Gather 8 data inputs
2. **Evaluate Position** - Determine current race context
3. **Risk Assessment** - Calculate overtaking viability
4. **Pit Stop Decision** (Diamond) - YES → Pit Stop, NO → Overtake Check
5. **Execute Pit Stop** - Service and resume
6. **Overtake Decision** (Diamond) - YES → Attempt, NO → Defensive Driving
7. **Execute Overtake** - Gap closing and maneuver
8. **Overtake Success** (Diamond) - Evaluate result
9. **Defensive Driving** - Hold/Block position
10. **Speed Decision** (3 options) - Aggressive (100%), Balanced (85%), Conservative (60%)
11. **Update Racing Line** - Dynamic line calculation
12. **Mistake Check** - Random driver error
13. **Output Speed Control** - Acceleration/Maintain/Brake
14. **Lap Complete?** (Diamond) - YES → Next Lap, NO → Continue cycle

**Decision Priority (in order):**
1. Safety > Survive race
2. Fuel/Tires > Any position gain
3. Strategy > Pit execution
4. Overtaking > When opportunity exists
5. Speed > Maximize legally

**Personality Modifiers:**
- Aggressive: Higher overtake rate, higher speed
- Defensive: Lower overtake, prefer established positions
- Calculating: Better pit timing, fuel management

---

### DEPLOYMENT_ARCHITECTURE.drawio
**4 Deployment Scenarios:**

#### Windows 10/11
- Python 3.11+ MSI installer
- PyInstaller .exe bundle
- Database: `C:\Users\<user>\Documents\FinalProject\...momentum.db`
- Port: 8000 (localhost)

#### macOS 11+
- Python 3.11+ via Homebrew/PyEnv
- PyInstaller .app bundle (universal: Intel + Apple Silicon)
- Database: `~/Documents/FinalProject/.../momentum.db`
- Port: 8000 (localhost)

#### Linux (Ubuntu 20.04 LTS+)
- Python 3.11+ via apt
- AppImage or Snap package
- Database: `~/Documents/FinalProject/.../momentum.db`
- Port: 8000 (localhost)

#### Future: LAN Multiplayer (v2.0)
- Server architecture with shared PostgreSQL
- Multi-client REST API calls
- Network-based synchronization

**Dependency Matrix:**
- All platforms: Python 3.11+, PyQt6 6.4+, FastAPI 0.104+, SQLite 3.35+

**Performance:**
- Windows: Excellent
- macOS: Very Good (Metal rendering)
- Linux: Good (GPU-dependent)
- Minimum: 4 GB RAM
- Recommended: 8 GB RAM

---

### SYSTEM_USE_CASES.drawio
**29 Total Use Cases organized by category:**

**MVP (v1.0) - Solid Ellipses:**
- **UC-1 to UC-3 (Core):** Read Driver Details, Read Race Config, Create Race Result
- **UC-4 to UC-10 (Championship):** Create/Read/Update/Delete Championship, Add Race, View Standings, Save
- **UC-11 to UC-14 (Team Management):** Create Team, Read Details, Update Team, Delete Team
- **UC-15 to UC-19 (Personnel):** Read Drivers, Update Driver Contract, Read Staff, Update Staff Contract, Manage Budget
- **UC-20 (Finance):** Multi-Currency Financial System

**Future (v2.0+) - Dashed Ellipses:**
- **UC-21 to UC-29:** Difficulty Settings, AI Behavior Config, Replay System, Stats Export, Mod Support, Achievements, Tutorial, Multiplayer, Mobile Port

**Relationships:**
- UC-3 includes UC-1, UC-2 (<<includes>>)
- UC-4 includes UC-5 (read required for create)
- UC-9 includes UC-5 (standings read from championship)

**Color Coding:**
- Blue: Read-only operations
- Green: Championship management
- Orange: Team management
- Yellow: Personnel management
- Purple: Financial system
- Red: Advanced/future features

---

## Integration with Technical Report

Each diagram should be embedded in the relevant section of the technical report:

1. **Design & Architecture section** → ARCHITECTURE_DIAGRAM.png
2. **Design & Architecture section** → DATABASE_ER_DIAGRAM.png
3. **Implementation section** → EVENT_LOOP_30FPS.png
4. **Implementation section** → AGENT_STATE_MACHINE.png
5. **Environmental Requirements section** → DEPLOYMENT_ARCHITECTURE.png
6. **Requirements (Functional) section** → SYSTEM_USE_CASES.png

**Markdown Syntax for Embedding:**
```markdown
![Architecture Diagram](diagrams/ARCHITECTURE_DIAGRAM.png)
```

---

## Export Quality Settings

**Recommended PNG Export Settings (in draw.io):**
- Scale: 2x (for high DPI)
- Width: 2400px
- Height: 1600px
- Quality: High (300 DPI for print)
- Background: White

This ensures diagrams are crisp and readable in both digital and printed formats.
