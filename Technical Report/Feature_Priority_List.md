# Feature Priority List - Momentum
## Ranked by Importance to Core Gameplay

**Principle:** What is the MINIMUM needed for a playable motorsport management game?

---

## 🔴 HIGH PRIORITY - Must Have for Basic Playability

### P1: Single Race Execution
**Why it's high priority:** This is the absolute core - if you can't run a single race, nothing else matters.

**Required CRUD Operations:**
1. **READ Drivers** - Load driver attributes (skill, consistency, speed)
2. **READ Teams** - Load team capabilities (budget, performance level)
3. **READ Races** - Load race details (circuit, distance, conditions)
4. **CREATE Race_Results** - Save race outcomes (positions, points, times)

**Use Cases Needed:**
- UC-1: Read Driver Details
- UC-2: Read Team Details  
- UC-3: Read Race Configuration
- UC-4: Create Race Result

**Database Tables:** Drivers (read), Teams (read), Races (read), Race_Results (create)

---

### P2: View Race Results
**Why it's high priority:** Players need to see what happened in the race they just ran.

**Required CRUD Operations:**
1. **READ Race_Results** - Display finishing positions, points, lap times

**Use Cases Needed:**
- UC-5: Read Race Results

**Database Tables:** Race_Results (read)

---

### P3: Championship Standings
**Why it's high priority:** Racing means nothing without tracking who's winning the championship.

**Required CRUD Operations:**
1. **READ Championships** - Load championship configuration (name, discipline, points system)
2. **READ Race_Results** - Aggregate points across multiple races
3. **UPDATE Championships** - Update standings after each race

**Use Cases Needed:**
- UC-6: Read Championship Details
- UC-7: Update Championship Standings

**Database Tables:** Championships (read, update), Race_Results (read)

---

### P4: Multi-Race Season
**Why it's high priority:** A championship needs multiple races to be meaningful.

**Required CRUD Operations:**
1. **CREATE Races** - Add races to championship calendar
2. **READ Races** - Display calendar/schedule
3. **UPDATE Races** - Mark races as completed
4. **CREATE Race_Results** - Save results for each race in season

**Use Cases Needed:**
- UC-8: Create Race Event
- UC-9: Read Race Schedule
- UC-10: Update Race Status (scheduled → completed)

**Database Tables:** Races (create, read, update), Race_Results (create), Championships (read)

---

### P5: Championship Creation
**Why it's high priority:** Need to start new seasons/championships.

**Required CRUD Operations:**
1. **CREATE Championships** - Start new championship/season

**Use Cases Needed:**
- UC-11: Create Championship (start new season)

**Database Tables:** Championships (create)

---

## 🟡 MEDIUM PRIORITY - Essential for Career Mode

### P6: Team Management (Basic)
**Why it's medium priority:** Player needs to control a team to make meaningful decisions.

**Required CRUD Operations:**
1. **CREATE Teams** - Initialize player's team at career start
2. **READ Teams** - View team stats, budget, performance
3. **UPDATE Teams** - Modify budget, development level, reputation

**Use Cases Needed:**
- UC-12: Create New Team (career start)
- UC-13: Read Team Details (team screen)
- UC-14: Update Team Attributes (budget changes, development)

**Database Tables:** Teams (create, read, update)

---

### P7: Driver Hiring/Management
**Why it's medium priority:** Team needs drivers to compete.

**Required CRUD Operations:**
1. **READ Drivers** - Browse available drivers
2. **UPDATE Drivers** - Assign driver to team (change team_id)

**Use Cases Needed:**
- UC-15: Read Available Drivers (driver market)
- UC-16: Update Driver Contract (hire/sign)

**Database Tables:** Drivers (read, update)
**Note:** No CREATE needed - 1,781 drivers already in database can be recycled

---

### P8: Basic Staff Management
**Why it's medium priority:** Staff affect team performance (engineers, mechanics).

**Required CRUD Operations:**
1. **READ Staff_Members** - View available staff
2. **UPDATE Staff_Members** - Assign staff to team (change team_id)

**Use Cases Needed:**
- UC-17: Read Available Staff
- UC-18: Update Staff Contract (hire)

**Database Tables:** Staff_Members (read, update)
**Note:** No CREATE needed - 57,936 staff already in database can be recycled

---

### P9: Driver Progression/Aging
**Why it's medium priority:** Drivers should improve/decline over time for long-term play. Can also "recycle" retired drivers by updating ages and attributes instead of deleting.

**Required CRUD Operations:**
1. **UPDATE Drivers** - Modify skill attributes based on performance/age (or reset for retired drivers)
2. **READ Race_Results** - Analyze performance to determine progression

**Use Cases Needed:**
- UC-19: Update Driver Skills/Age (end of season, or recycle retired drivers)

**Database Tables:** Drivers (update), Race_Results (read)

---

### P10: Financial Management
**Why it's medium priority:** Adds strategic depth - can you afford good drivers/staff?

**Required CRUD Operations:**
1. **UPDATE Teams** - Modify budget (income from sponsors, costs from salaries)
2. **READ Teams** - Display financial status

**Use Cases Needed:**
- UC-20: Update Team Budget (end of race/season)

**Database Tables:** Teams (read, update)

---

## 🟢 LOW PRIORITY - Nice to Have / Polish

### P11: Create New Drivers/Staff
**Why it's low priority:** Database has 1,781 drivers and 57,936 staff already. Can recycle existing entities by updating ages/attributes instead of creating new ones when people retire.

**Required CRUD Operations:**
1. **CREATE Drivers** - Generate new rookie drivers (optional enhancement)
2. **CREATE Staff_Members** - Generate new staff entering job market (optional enhancement)

**Use Cases Needed:**
- UC-21: Create New Driver (rookie generation)
- UC-22: Create New Staff Member (staff generation)

**Database Tables:** Drivers (create), Staff_Members (create)
**Note:** Not needed for basic gameplay - existing entities can be recycled

---

### P12: Championship Cleanup
**Why it's low priority:** Deleting old championships is cleanup, not core gameplay.

**Required CRUD Operations:**
1. **DELETE Championships** - Remove old/completed championships

**Use Cases Needed:**
- UC-23: Delete Championship (cleanup old saves)

**Database Tables:** Championships (delete)

---

### P13: Track Management
**Why it's low priority:** 175 tracks already in circuits_database.json can be pre-populated. Creating/editing tracks is not core gameplay.

**Required CRUD Operations:**
1. **CREATE Tracks** - Add custom tracks (nice to have, not essential)
2. **UPDATE Tracks** - Modify track characteristics (not essential)
3. **DELETE Tracks** - Remove unused tracks (not essential)

**Use Cases Needed:**
- UC-24: Create Custom Track (advanced feature)
- UC-25: Update Track Characteristics (advanced feature)
- UC-26: Delete Track (cleanup)

**Database Tables:** Tracks (create, update, delete)
**Note:** READ Tracks is already covered in P1 (high priority)

---

### P14: Staff Performance Impact
**Why it's low priority:** Makes staff hiring more meaningful, but not essential for basic gameplay.

**Required CRUD Operations:**
1. **READ Staff_Members** - Get staff attributes (engineer skill, mechanic skill)
2. **READ Teams** - Apply staff bonuses to team performance in races

**Use Cases Needed:**
- UC-27: Read Staff Performance Modifiers (during race simulation)

**Database Tables:** Staff_Members (read), Teams (read)

---

### P15: Advanced Customization
**Why it's low priority:** Game should work with procedurally generated content; custom names/logos are polish.

**Required CRUD Operations:**
1. **UPDATE Drivers** - Change driver name/appearance (cosmetic)
2. **UPDATE Teams** - Change team name/colors (cosmetic)

**Use Cases Needed:**
- UC-28: Update Driver Appearance (cosmetic)
- UC-29: Update Team Branding (cosmetic)

**Database Tables:** Drivers (update), Teams (update)
**Note:** Already covered by existing UPDATE operations - just different use cases

---

## Summary: Minimum Viable Use Cases (MVP)

To have a **basic playable motorsport management game**, you need these use cases:

### 🔴 HIGH Priority (Must Have - Core Gameplay):
1. ✅ UC-1: Read Driver Details
2. ✅ UC-2: Read Team Details
3. ✅ UC-3: Read Race Configuration
4. ✅ UC-4: Create Race Result
5. ✅ UC-5: Read Race Results
6. ✅ UC-6: Read Championship Details
7. ✅ UC-7: Update Championship Standings
8. ✅ UC-8: Create Race Event
9. ✅ UC-9: Read Race Schedule
10. ✅ UC-10: Update Race Status
11. ✅ UC-11: Create Championship

**Total: 11 use cases for basic playability**

### 🟡 MEDIUM Priority (Career Mode Depth):
12. ✅ UC-12: Create New Team
13. ✅ UC-13: Read Team Details (team screen)
14. ✅ UC-14: Update Team Attributes
15. ✅ UC-15: Read Available Drivers
16. ✅ UC-16: Update Driver Contract
17. ✅ UC-17: Read Available Staff
18. ✅ UC-18: Update Staff Contract
19. ✅ UC-19: Update Driver Skills/Age (includes recycling retired drivers)
20. ✅ UC-20: Update Team Budget

**Total: 9 additional use cases for full career mode (20 total)**

### 🟢 LOW Priority (Polish & Advanced Features):
21. ✅ UC-21: Create New Driver (not needed - recycle existing 1,781 drivers)
22. ✅ UC-22: Create New Staff Member (not needed - recycle existing 57,936 staff)
23. ✅ UC-23: Delete Championship
24. ✅ UC-24: Create Custom Track
25. ✅ UC-25: Update Track Characteristics
26. ✅ UC-26: Delete Track
27. ✅ UC-27: Read Staff Performance Modifiers
28. ✅ UC-28: Update Driver Appearance
29. ✅ UC-29: Update Team Branding

**Total: 9 additional use cases for polish (29 total)**

---

## Recommended Use Case Writing Order

### Phase 1: HIGH Priority (Core Gameplay - Write These First!)
**Start with READ operations** (easiest, no database changes):
1. UC-1: Read Driver Details
2. UC-2: Read Team Details
3. UC-3: Read Race Configuration
4. UC-5: Read Race Results
5. UC-6: Read Championship Details
6. UC-9: Read Race Schedule

**Then CREATE operations** (simple inserts):
7. UC-4: Create Race Result
8. UC-8: Create Race Event
9. UC-11: Create Championship

**Finally UPDATE operations** (more complex):
10. UC-7: Update Championship Standings
11. UC-10: Update Race Status

**Total: 11 use cases = Minimum viable game**

---

### Phase 2: MEDIUM Priority (Career Mode - Write These Second)
**Team management**:
12. UC-12: Create New Team
13. UC-13: Read Team Details (team screen)
14. UC-14: Update Team Attributes

**Driver management**:
15. UC-15: Read Available Drivers
16. UC-16: Update Driver Contract

**Staff management**:
17. UC-17: Read Available Staff
18. UC-18: Update Staff Contract

**Progression systems**:
19. UC-19: Update Driver Skills/Age (includes recycling retired drivers)
20. UC-20: Update Team Budget

**Total: 9 additional use cases = Full career mode**

---

### Phase 3: LOW Priority (Polish - Write These Last, If Time Permits)
21. UC-21: Create New Driver (not essential - 1,781 existing drivers can be recycled)
22. UC-22: Create New Staff Member (not essential - 57,936 existing staff can be recycled)
23. UC-23: Delete Championship
24. UC-24: Create Custom Track
25. UC-25: Update Track Characteristics
26. UC-26: Delete Track
27. UC-27: Read Staff Performance Modifiers
28. UC-28: Update Driver Appearance (cosmetic)
29. UC-29: Update Team Branding (cosmetic)

**Total: 9 additional use cases = Polish and advanced features**

---

## CRUD Operation Matrix

| Table | Create | Read | Update | Delete | Priority Summary |
|-------|--------|------|--------|--------|------------------|
| **Races** | UC-8 (P4) 🔴 | UC-3, UC-9 (P1, P4) 🔴 | UC-10 (P4) 🔴 | Not needed | 🔴 HIGH: All CRUD except Delete |
| **Race_Results** | UC-4 (P1) 🔴 | UC-5 (P2) 🔴 | Not needed | Not needed | 🔴 HIGH: Create & Read only |
| **Championships** | UC-11 (P5) 🔴 | UC-6 (P3) 🔴 | UC-7 (P3) 🔴 | UC-23 (P11) 🟢 | 🔴 HIGH: Create/Read/Update<br>� LOW: Delete |
| **Drivers** | UC-21 (P11) � | UC-1 (P1) 🔴<br>UC-15 (P7) 🟡 | UC-16 (P7) 🟡<br>UC-19 (P9) 🟡 | Not needed | 🔴 HIGH: Read only<br>🟡 MEDIUM: Update only<br>🟢 LOW: Create (recycle instead) |
| **Teams** | UC-12 (P6) 🟡 | UC-2 (P1) 🔴<br>UC-13 (P6) 🟡 | UC-14 (P6) 🟡<br>UC-20 (P10) 🟡 | Not needed | 🔴 HIGH: Read only<br>🟡 MEDIUM: Create/Update |
| **Staff_Members** | UC-22 (P11) � | UC-17 (P8) 🟡<br>UC-27 (P14) 🟢 | UC-18 (P8) 🟡 | Not needed | 🟡 MEDIUM: Read/Update<br>🟢 LOW: Create (recycle instead) |
| **Tracks** | UC-24 (P12) 🟢 | UC-3 (P1) 🔴 | UC-25 (P12) 🟢 | UC-26 (P12) 🟢 | 🔴 HIGH: Read only<br>🟢 LOW: Create/Update/Delete |

---

## Mapping to Technical Report Structure

Based on NCI technical report template:

### Section 2.1.1.4: Use Cases
- Include **ALL use cases** (UC-1 through UC-31 if you write them all)
- **Group by priority** (Critical, High, Medium, Low)
- Use the Championship examples as template for CRUD format
- Mark which use cases are **currently implemented** vs planned

### Section 2.1.2: Functional Requirements
- Map priorities to functional requirements:
  - FR-1: System shall simulate single race (P1)
  - FR-2: System shall display race results (P2)
  - FR-3: System shall track championship standings (P3)
  - FR-4: System shall support multi-race seasons (P4)
  - FR-5: System shall allow team management (P5)
  - etc.

### Section 2.1.3: Non-Functional Requirements
- Performance: Race simulation must complete within 5 seconds
- Scalability: Support 20+ drivers per race
- Reliability: Database persistence with ACID compliance
- Usability: PyQt6 GUI with intuitive navigation

### Section 3: Implementation
- Show how each priority was implemented:
  - P1-P4: disciplines/race_simulation.py, database/database_manager.py
  - P5-P7: systems/staff_management.py, gui/gui_game.py
  - P8-P11: systems/game_loop.py (partially complete)

### Section 5: Testing
- Map test files to priorities:
  - test_race_simulation.py validates P1
  - test_2025_season.py validates P3-P4
  - test_driver_system.py validates P6, P9
  - test_staff_system.py validates P7, P11

---

## Key Insights for Your Supervisor

### Priority Structure (3 Levels):
1. **🔴 HIGH Priority = 11 use cases** (P1-P5: race execution, results, standings, multi-race seasons, championship creation)
   - These are ESSENTIAL for basic playability
   - Without these, you have no game

2. **🟡 MEDIUM Priority = 9 use cases** (P6-P10: teams, drivers, staff, progression, finances)
   - These make it a proper career management game
   - Add depth and strategic decision-making
   - **Excludes CREATE for drivers/staff** - can recycle existing database entities

3. **🟢 LOW Priority = 9 use cases** (P11-P15: new entity creation, cleanup, customization, advanced features)
   - Nice-to-have polish and advanced features
   - Can be documented as "future enhancements"
   - Includes CREATE drivers/staff (not needed - recycle existing entities instead)

### Current Implementation Status:
- **HIGH (P1-P5):** ✅ 70% implemented (race simulation works, standings tracked, but game loop incomplete)
- **MEDIUM (P6-P10):** ⚠️ 40% implemented (models exist, hiring/firing endpoints missing)
- **LOW (P11-P14):** ❌ 10% implemented (mostly unimplemented nice-to-have features)

### For Minimum Viable Submission:
- **Write at least 11 use cases** (HIGH priority) = Basic playable game
- **Aim for 20 use cases** (HIGH + MEDIUM) = Full career mode
- **Low priority use cases** can be documented as "future work" if time is limited

### Smart Design Decision:
- **No need to CREATE/DELETE drivers or staff** - database has 1,781 drivers and 57,936 staff
- When drivers retire, simply UPDATE their age/attributes to "recycle" them as rookies
- This simplifies implementation and reduces CRUD operations from 29 to 20 for MVP

### DELETE Operations:
- Only 2 DELETE operations needed (Championships, Tracks)
- Both are LOW priority cleanup operations
- Not essential for core gameplay
- Focus on CREATE, READ, UPDATE for MVP

### Academic Justification:
This priority structure demonstrates proper software engineering methodology:
- ✅ Requirements prioritized by user value (MoSCoW method)
- ✅ Incremental development (HIGH → MEDIUM → LOW)
- ✅ Honest documentation of implementation status
- ✅ Clear distinction between MVP and enhancements
