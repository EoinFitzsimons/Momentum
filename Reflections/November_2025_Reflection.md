# November 2025 Reflection

| Student Name    | Eoin Andrew Fitzsimons |
| -------------- | - |
| Student Number | X23151374 |
| Course         | BSc (Honours) in Computing - Software Development |
| Supervisor     | [Supervisor Name] |

**Month:** November 2025

## What? Reflect on what has happened in your project this month?

In November, I made a **critical architectural pivot** that fundamentally changed the project's simulation approach:

**Initial Implementation (Early November):**
- Started with Monte Carlo statistical simulation as proposed
- Implemented `base_engine.py` with probability-based lap time calculations
- Created `single_seater_discipline.py` using statistical aggregation
- Built basic GUI that showed only lap completion events

**The Pivot (Mid-November):**
- Realized Monte Carlo approach produced "lap time calculator" rather than live racing
- User testing revealed: "I want aware AI that makes decisions based on information available to them"
- Requirement emerged: 30 FPS continuous simulation with cars moving on track
- Complete architecture rebuild required

**New Implementation (Late November → Early December):**
- Built `realtime_race_engine.py` (493 lines) - agent-based simulation at 30 FPS
- Implemented AI decision-making system with racing modes (ATTACK/DEFEND/MANAGE/CRUISE)
- Added spatial awareness: gap calculations, slipstream detection, nearby car tracking
- Created continuous physics: speed = f(skills, team, tires, fuel, slipstream, corners)
- Integrated with GUI: cars now move smoothly on track with live position updates
- Fixed Driver attribute mapping errors (aggression/risk_appetite → actual DB attributes)
- Adjusted simulation speed from 100x → 5x real-time for watchable racing

**Testing & Validation:**
- Created `test_full_race_no_gui.py`: 47-lap race, 10 drivers, 123,697 position updates ✅
- Created `test_realtime_quick.py`: Quick 3-lap validation ✅
- Created `test_speed_check.py`: Speed verification (33s for 2 laps at 5x) ✅
- GUI integration successful: lap counting, standings updates, smooth car movement ✅

## So What? Consider what that meant for your project progress. What were your successes? What challenges still remain?

### Successes:

1. **Architecture Proved Correct:** Agent-based approach delivers the "aware AI" requirement
   - Drivers actively respond to race situations (gaps, positions, tire condition)
   - AI decision-making visible: drivers switch between racing modes based on context
   - Spatial awareness working: slipstream, gap management, nearby car detection

2. **Performance Achieved:** 30 FPS sustained over full 47-lap race
   - 2.7M+ position updates per race without performance degradation
   - Real-time calculation of physics, AI decisions, and spatial awareness
   - Smooth GUI integration with thread-safe Qt signals

3. **Technical Debt Eliminated:** Fixed critical issues
   - Driver attribute mapping now uses actual database schema
   - Simulation speed now watchable (5x real-time vs 100x)
   - Lap counting properly updates in GUI standings table

4. **Deliverable Status:** Core engine **complete and functional**
   - Single Seater discipline fully working
   - GUI shows live racing with moving cars
   - Database integration solid (1,781 drivers, 175 tracks)

### Challenges Remaining:

1. **High DNF Rate (90%)**: Incident probability needs tuning
   - Current: 9/10 drivers retire in 47-lap race
   - Target: <30% DNF rate for realistic racing
   - Fix: Reduce base incident probability from 0.00001 → 0.000002

2. **Documentation Outdated**: All planning docs reference Monte Carlo
   - Proposal mentions "Monte Carlo simulation" 8+ times
   - Technical Report Section 5.2.1 describes statistical algorithm
   - GitHub Issue #5 titled "Monte Carlo Race Simulation Engine"
   - `simulation_attribute_mapping.md` uses lap-by-lap formulas

3. **Incomplete Disciplines**: Only Single Seater tested
   - Rally, Endurance, Drag, Touring, Street, Rallycross need implementation
   - Core engine extensible but discipline-specific logic required

4. **Missing Features**:
   - Qualifying simulation (currently database order for grid)
   - Championship points calculation (no F1-style 25-18-15 system)
   - Pit stops (fuel/tire strategy not implemented)
   - Safety cars/incidents beyond DNF

## Now What? What can you do to address outstanding challenges?

### Immediate Actions (December 1-9 - Midpoint Submission):

1. **Update Documentation (Priority: CRITICAL)**
   - Rewrite Technical Report Section 5.2.1: "Monte Carlo" → "Agent-Based Architecture"
   - Update Proposal: Remove Monte Carlo references, describe 30 FPS approach
   - Update GitHub Issue #5: Retitle and rewrite for agent-based engine
   - Update `simulation_attribute_mapping.md` for continuous physics formulas

2. **Lower DNF Rate (Priority: HIGH)**
   - Adjust `_check_incident()` in `realtime_race_engine.py`
   - Test with 47-lap race until <30% DNF rate achieved
   - Document tuning parameters in STATUS_REALTIME_ENGINE.md

3. **Validate GUI Demo (Priority: HIGH)**
   - Full end-to-end test: launch GUI → select race → watch completion
   - Verify lap counting, standings updates, car movement
   - Prepare for live midpoint demonstration

4. **Update Testing Documentation (Priority: MEDIUM)**
   - Section 6.1.2: Rewrite "Monte Carlo Statistical Validation"
   - Add frame-rate consistency tests
   - Document AI behavior validation tests

### Post-Midpoint (December 10-20):

5. **Implement Additional Disciplines**
   - Rally: Add co-driver, surface_adaptation, pace notes
   - Endurance: Pit stops, driver swaps, reliability focus
   - Target: 3-4 disciplines working by Christmas

6. **Add Championship Points**
   - F1-style points system (25-18-15-12-10-8-6-4-2-1)
   - Fastest lap bonus
   - Season standings calculation

7. **Qualifying Simulation**
   - Use `qualifying_pace` and `qualifying_optimization` attributes
   - Generate realistic grid positions
   - Single flying lap format

### Risk Mitigation:

- **If DNF tuning takes >2 days**: Submit with known issue, document as "balance tuning required"
- **If documentation updates take >3 days**: Focus on Technical Report only, defer other docs
- **If additional disciplines block**: Submit with Single Seater only, others as "future work"

### Key Lesson Learned:

**Fail fast on architecture decisions.** The Monte Carlo approach took 2 weeks to realize it was wrong for the requirements. Earlier user testing (even informal) would have caught this. Going forward: validate core assumptions with quick prototypes before deep implementation.

---

**Student Signature:** Eoin Fitzsimons  
**Date:** December 3, 2025
