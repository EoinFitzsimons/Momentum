# December 2025 Reflection

| Student Name    | Eoin Andrew Fitzsimons |
| -------------- | - |
| Student Number | X23151374 |
| Course         | BSc (Honours) in Computing - Software Development |
| Supervisor     | [Supervisor Name] |

**Month:** December 2025 (Week 1)

## What? Reflect on what has happened in your project this month?

**Week 1 (December 1-7):**

**Monday-Tuesday (Dec 2-3): Documentation Crisis Discovery**
- Realized ALL planning documents reference Monte Carlo architecture
- Discovered GitHub Issue #5 titled "Monte Carlo Race Simulation Engine" - completely outdated
- Technical Report Section 5.2.1 describes statistical algorithm that no longer exists
- Proposal mentions "Monte Carlo simulation" 8+ times throughout
- `simulation_attribute_mapping.md` uses lap-by-lap formulas incompatible with current 30 FPS approach

**Tuesday-Wednesday (Dec 3-4): Engine Refinement**
- Fixed Driver attribute errors (`aggression`/`risk_appetite` didn't exist in database)
- Mapped to actual attributes: `overtaking`, `adrenaline_management`, `professionalism`
- Adjusted simulation speed: 100x → 5x real-time (watchable racing)
- Fixed GUI lap counting with thread-safe Qt signals
- Created comprehensive test suite: `test_full_race_no_gui.py`, `test_realtime_quick.py`, `test_speed_check.py`

**Current Status (as of Dec 3):**
- Real-time engine **fully functional** - 123,697 position updates in 47-lap test ✅
- GUI integration **working** - cars move on track, laps count, standings update ✅
- Testing **comprehensive** - quick tests, full race tests, speed verification ✅
- Documentation **critically outdated** - major rewrite needed before midpoint ⚠️

## So What? Consider what that meant for your project progress. What were your successes? What challenges still remain?

### Successes:

1. **Engine Robustness Proven:**
   - Full 47-lap race with 10 drivers: 4,123 seconds simulation time (68.7 minutes racing)
   - 123,697 position updates without crashes or memory leaks
   - AI decision-making observable: drivers switching ATTACK/DEFEND/MANAGE modes
   - Spatial awareness working: gap calculations, slipstream detection functional

2. **Test Infrastructure Established:**
   - Three levels of testing: quick (3 laps), medium (speed check), comprehensive (47 laps)
   - All tests runnable without GUI for CI/CD potential
   - Performance metrics documented: 5x real-time speed, 30 FPS sustained

3. **GUI Integration Stable:**
   - Thread-safe event handling via Qt signals
   - Smooth car movement on track visualization
   - Live standings table updates
   - No crashes during normal operation

4. **Problem Identification:**
   - High DNF rate (90%) identified and root cause known (incident probability too high)
   - Documentation debt quantified: 5 major documents need rewrites
   - GitHub issues out of sync with actual implementation

### Challenges Remaining:

1. **Documentation Debt (CRITICAL for Midpoint - Dec 12):**
   - Technical Report Section 5.2.1 needs complete rewrite (~2 hours)
   - Proposal needs Monte Carlo references removed/updated (~1 hour)
   - `simulation_attribute_mapping.md` needs continuous formulas (~1.5 hours)
   - GitHub Issue #5 needs retitle and description rewrite (~30 mins)
   - Testing section needs agent-based test cases (~1 hour)
   - **Total estimate: 6 hours documentation work**

2. **Balance Tuning (HIGH Priority):**
   - DNF rate 90% → target <30%
   - Base incident probability: 0.00001 → 0.000002 (needs testing)
   - Tire degradation rate may be too aggressive
   - Fuel consumption rate needs validation

3. **Missing Core Features (MEDIUM Priority):**
   - Qualifying simulation (currently database order start grid)
   - Championship points calculation (no 25-18-15 system)
   - Pit stops not implemented
   - Only Single Seater discipline tested (6 others untouched)

4. **Performance Optimization (LOW Priority):**
   - Currently running 3x real-time vs target 5x
   - Frame processing overhead from event callbacks
   - Could optimize with numpy vectorization of gap calculations

### Risks to Midpoint Submission (Dec 12 - 9 days):

**HIGH RISK:**
- Documentation rewrite taking longer than estimated (lose demo prep time)
- DNF tuning requiring multiple test iterations (each 47-lap test = 13-15 mins)

**MEDIUM RISK:**
- GUI threading edge case causing crash during live demo
- Track data missing (0 tracks currently imported vs 175 designed)

**LOW RISK:**
- Performance degradation during longer races (already tested 47 laps ✅)

## Now What? What can you do to address outstanding challenges?

### This Week (Dec 4-7): Documentation Sprint

**Wednesday (Dec 4):**
- [ ] Rewrite Technical Report Section 5.2.1 (2 hours)
  - Remove Monte Carlo algorithm description (lines 102-200)
  - Add "Real-Time Agent-Based Architecture" section
  - Document DriverState, RacingMode, AI decision-making
  - Include 30 FPS physics calculation

**Thursday (Dec 5):**
- [ ] Update Proposal document (1 hour)
  - Line 23: Monte Carlo → Real-time agent-based
  - Line 51: Event-driven lap-by-lap → Continuous 30 FPS
  - Technical Approach section rewrite
- [ ] Update `simulation_attribute_mapping.md` (1.5 hours)
  - Replace lap-by-lap formulas with continuous physics
  - Document frame-by-frame calculations
  - Add AI decision-making attribute usage

**Friday (Dec 6):**
- [ ] Update GitHub Issue #5 via API (30 mins)
  - Retitle: "Real-Time Agent-Based Race Simulation Engine"
  - Rewrite description and acceptance criteria
  - Check off completed tasks
- [ ] Update Technical Report Testing section (1 hour)
  - Section 6.1.2: Frame-rate testing instead of Monte Carlo validation
  - Add AI behavior test cases
  - Document spatial awareness tests

**Saturday-Sunday (Dec 7-8): Balance Tuning**
- [ ] Lower DNF rate (4 hours)
  - Test incident probability: 0.00001 → 0.000002
  - Run 10x 47-lap tests to verify <30% DNF rate
  - Adjust tire degradation if needed
  - Document final parameters

### Next Week (Dec 9-12): Midpoint Prep

**Monday (Dec 9):**
- [ ] Import 175 tracks from circuits_database.json (1 hour)
  - Run `scripts/import_circuits.py`
  - Verify database has 175 tracks
  - Test race with multiple tracks

**Tuesday (Dec 10):**
- [ ] Full GUI end-to-end testing (2 hours)
  - Launch → Select drivers → Configure race → Watch complete race
  - Test with 5 lap, 10 lap, 20 lap races
  - Verify no threading errors
  - Document any edge cases

**Wednesday (Dec 11):**
- [ ] Prepare midpoint presentation (4 hours)
  - Update slides to reflect agent-based approach
  - Prepare live demo script
  - Practice demo twice (dry runs)
  - Backup video recording of working demo

**Thursday (Dec 12):**
- [ ] **Midpoint Submission & Presentation**

### Contingency Plans:

**If documentation takes >6 hours:**
- Focus ONLY on Technical Report Section 5.2.1 and Proposal
- Defer `simulation_attribute_mapping.md` update (internal doc)
- GitHub issues can be updated post-presentation

**If DNF tuning doesn't converge:**
- Submit with known issue documented
- Include in "Limitations" section
- Explain as balance parameter requiring more testing

**If track import fails:**
- Create 10 test tracks manually
- Sufficient for demo purposes
- Full import post-midpoint

### Key Priorities (Dec 4-12):

1. **Documentation rewrite (40% of effort)** - MUST be done for written submission
2. **Balance tuning (30% of effort)** - Important for realistic demo
3. **Demo preparation (20% of effort)** - Practice makes perfect
4. **Track import (10% of effort)** - Nice to have, not critical

### Lessons Applied:

- **Time-box documentation work**: Set 6-hour limit, deliver what's possible
- **Test-driven balancing**: Each parameter change gets 47-lap validation
- **Demo-first mentality**: Prioritize features visible in 10-minute presentation

---

**Student Signature:** Eoin Fitzsimons  
**Date:** December 3, 2025  
**Next Update:** December 10, 2025 (Pre-Midpoint Check-in)
