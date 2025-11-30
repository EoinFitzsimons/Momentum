# Component Integration - Manual Test Plan

## ✅ Fixed Issues

### Issue #1: Team Attribute Errors
**Problem**: Code was using `team.total_annual_budget` and `team.primary_discipline` which don't exist on the Team model.

**Root Cause**: Mismatch between expected and actual Team model attributes.

**Solution**: Updated to use correct attributes:
- `team.total_annual_budget` → `team.budget`
- `team.primary_discipline` → `team.discipline`

**Files Modified**:
- `systems/vehicle_creation_helper.py` (line 86-87)
- `systems/component_integration.py` (line 58)

**Result**: ✅ Career now starts successfully with component initialization

---

## Manual Testing Checklist

### 1. Career Start ✅
**Status**: PASSED
- [x] Start new career
- [x] Select team
- [x] Components initialized for player vehicle
- [x] Performance multiplier calculated (75.0% shown in log)

**Evidence**:
```
✓ Initialized components for Bonnet Racing's SINGLE_SEATER car
  - Car ID: 102025
  - Performance: 75.0%
```

---

### 2. Component Wear During Race Weekend
**Status**: TO TEST

**Test Steps**:
1. Start career and select team
2. Navigate to race weekend
3. Complete practice sessions (should apply 60min @ 70% wear)
4. Complete qualifying (should apply 30min @ 95% wear)
5. Open garage screen
6. Verify component health has decreased

**Expected Results**:
- Engine: ~97-98% health (lost 0.08% per practice + qualifying)
- Tires: ~90-92% health (lost ~2.35% per practice session + 3.5% qualifying)
- Other components: slight wear (<1%)

**Pass Criteria**:
- Health bars show wear (not all at 100%)
- Performance multiplier < 1.0 if significant wear
- Garage displays accurate component status

---

### 3. Component Health Visualization
**Status**: TO TEST

**Test Steps**:
1. After race weekend, click "🔧 GARAGE & WORKSHOP" from Career Hub
2. Verify left panel shows all 11 components with health bars
3. Check color coding matches health levels:
   - Green (≥80%): Excellent
   - Cyan (60-80%): Good
   - Yellow (40-60%): Worn
   - Orange (20-40%): Damaged
   - Red (<20%): Critical

**Expected Results**:
- All components visible with percentage and status
- Overall health percentage calculated
- Performance multiplier displayed
- Components needing replacement listed (if any <50%)

**Pass Criteria**:
- Health bars render correctly
- Colors match health thresholds
- Data matches actual component state

---

### 4. Component Repair System
**Status**: TO TEST

**Test Steps**:
1. In garage screen, adjust repair extent slider to 100%
2. Click "Repair All Components"
3. Confirm repair dialog
4. Verify:
   - Component health restored to 100%
   - Team budget decreased by repair cost
   - Repair appears in history table

**Alternative Test - Individual Repair**:
1. Select single component from dropdown (e.g., "Tires")
2. Set repair extent (e.g., 50%)
3. Click "Repair Selected Component"
4. Verify only that component repaired to selected extent

**Expected Results**:
- Health bars update immediately
- Budget decreases correctly
- Repair history table shows new entry with:
  - Components repaired
  - Cost (in millions)
  - Time (in hours)
  - Success status

**Pass Criteria**:
- Repair restores health accurately
- Cost calculation correct
- History persists after screen refresh

---

### 5. Database Persistence
**Status**: TO TEST

**Test Steps**:
1. Complete race weekend (components worn)
2. Perform some repairs
3. Note current component states and repair history
4. **Close the game completely**
5. Reopen game and load career
6. Open garage screen
7. Verify component states match pre-close state

**Expected Results**:
- Component health percentages identical
- Repair history table shows all previous repairs
- Damage events preserved (if any crashes occurred)
- Overall health and performance multiplier same

**Database Tables to Verify**:
- `component_states`: RaceCar pickled data saved
- `component_health_history`: Health snapshots recorded
- `damage_events`: Crashes/damage logged
- `repair_history`: Repair operations stored

**Pass Criteria**:
- No data loss after game close/reopen
- All component states accurately restored
- Historical data (repairs, damage) preserved

---

### 6. Component Damage from Crashes
**Status**: TO TEST (requires crash simulation)

**Test Steps**:
1. Simulate race with crash (if crash system implemented)
2. Check garage after race
3. Verify damaged components show reduced health
4. Check damage events in database

**Expected Results**:
- Crash reduces health of multiple components
- Damage severity varies by component type
- `damage_events` table records:
  - Component name
  - Severity (0.0 to 1.0)
  - Cause ("crash")
  - Session type and lap number

**Pass Criteria**:
- Crash damage applied realistically
- Database logs event correctly
- Garage UI shows damage

---

### 7. Performance Impact of Component Health
**Status**: TO TEST

**Test Steps**:
1. Note baseline race performance with 100% health
2. Run multiple race weekends without repairs
3. Components degrade to 70-80% health
4. Compare race results/lap times
5. Verify performance multiplier reflects degradation

**Expected Results**:
- Performance multiplier decreases as components wear
- Lap times slower with worn components
- Race results worse with degraded car

**Calculation**:
```python
performance_multiplier = average(all_component_health_percentages) / 100
# Example: (80 + 85 + 90 + ... ) / 11 / 100 = 0.85
```

**Pass Criteria**:
- Performance impact visible in results
- Multiplier calculation accurate
- Player incentivized to maintain components

---

### 8. Repair Cost vs Budget Management
**Status**: TO TEST

**Test Steps**:
1. Note team budget (e.g., $120M)
2. Wear components to 50% health
3. Check repair cost estimate in garage
4. Perform repair
5. Verify budget decreased correctly
6. Attempt repair with insufficient budget

**Expected Results**:
- Repair cost scales with:
  - Number of components
  - Repair extent percentage
  - Component technology level
- Budget prevents repairs if insufficient
- Cost estimate matches actual cost charged

**Pass Criteria**:
- Cost calculation realistic
- Budget constraint enforced
- Clear feedback when insufficient funds

---

### 9. Edge Cases
**Status**: TO TEST

**Test Cases**:

#### 9.1 Component at 0% Health
- Run component to 0% health (extreme wear/damage)
- Verify doesn't crash game
- Check performance impact (should be severe)
- Verify repair still possible

#### 9.2 Multiple Repairs Same Component
- Repair engine to 70%
- Later repair same engine to 90%
- Verify health updates correctly
- Check history shows both repairs

#### 9.3 Season Transition
- Complete season with worn components
- Start new season
- Verify components carry over (or reset if intended)

#### 9.4 Vehicle Switch
- If multiple vehicles supported
- Switch between vehicles
- Verify correct component states for each

---

## Automated Test Coverage

### Existing Tests (tests/test_component_integration.py)
✅ Component creation
✅ Development level extraction
✅ Component manager creation
✅ RaceCar instance storage

### Tests to Add
- [ ] Practice session wear simulation
- [ ] Qualifying session wear simulation  
- [ ] Repair cost calculation
- [ ] Database save/load cycle
- [ ] Health history tracking
- [ ] Damage event logging
- [ ] Performance multiplier calculation

---

## Known Limitations

1. **Race damage not yet implemented**: No crashes during races apply component damage yet
2. **Track characteristics not factored**: All tracks wear components equally
3. **Weather effects missing**: Rain/heat don't affect wear rates
4. **Component replacement**: Only repairs, not full replacement with new parts
5. **AI team components**: AI teams don't have component systems yet (only player)

---

## Success Criteria Summary

The component integration is considered **fully functional** when:

- ✅ Career starts without errors
- ⏳ Components wear during practice/qualifying/race
- ⏳ Garage UI displays accurate health data
- ⏳ Repairs restore health and cost money
- ⏳ Database persistence works across sessions
- ⏳ Performance impact visible in race results
- ⏳ All edge cases handled gracefully

**Current Status**: 1/7 criteria verified ✅

**Next Step**: Run through test checklist items 2-9 to verify full integration.
