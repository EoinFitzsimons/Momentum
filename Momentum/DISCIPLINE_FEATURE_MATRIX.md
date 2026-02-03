# Discipline Feature Implementation Matrix

**Date:** February 3, 2026  
**Status:** Critical Feature Gaps Identified

## Overview

The game has **6 racing disciplines** with **comprehensive design specs** (see GAME_DESIGN_DOCUMENT.md), but implementation is **heavily skewed toward Single Seater** with 4 of 6 disciplines using generic engines.

### Design Intent vs Implementation Gap

| What Was Designed | What's Implemented | Gap |
|-------------------|--------------------|-----|
| 6 unique discipline simulators | 2 unique engines (Single Seater, Drag) + 4 generic | **4 disciplines missing** |
| Pit stop strategy (SS, Touring, Endurance) | Passive tire/fuel only | **No pit system** |
| Drift judging system (Urban Street) | Generic lap racing | **Completely different format** |
| Joker lap system (Rallycross) | Database supports it | **No enforcement logic** |
| Driver swaps (Endurance) | Database columns exist | **Not implemented** |
| Damage model | Generic crash probability | **Incomplete - no damage tracking** |

---

## Design Specification (From GAME_DESIGN_DOCUMENT.md)

The design document comprehensively specifies mechanics for each discipline:

### **SINGLE_SEATER (50-70 laps, 1-2 stops)**
- ✅ **Tire compounds:** Soft/Medium/Hard selection
- ✅ **Pit stop windows:** Strategic timing vs track position
- ✅ **Fuel optimization:** Load calculation for stint length
- ✅ **Damage:** Bent panels affect aerodynamics

### **PRODUCTION_TOURING (Circuit racing)**
- ✅ **Tire management:** Surface-dependent grip loss
- ✅ **Pit stops:** Fuel/tire strategy (1-3 stops)
- ✅ **Damage:** Body/suspension damage from contact
- ⚠️ **Fuel:** Optional multi-stint strategy

### **URBAN_STREET / Drift**
- ✅ **Drift Scoring:** Angle, speed, line, proximity (judged format)
- ✅ **Tandem Battles:** Head-to-head lead/chase judging
- ⚠️ **Tire Management:** Drift-specific (overheating, sliding wear)
- ✅ **Setup:** Drift suspension vs grip racing tuning

### **DRAG_ACCELERATION**
- ✅ **Launch Grip:** Tire compound affects 60-foot time
- ✅ **Reaction Time:** Driver skill dominates outcome
- ✅ **60-Foot Times:** Determines race winner
- ✅ **Burnout Damage:** Pre-race tire preparation

### **SPRINT_RALLYCROSS (Mixed surface)**
- ✅ **Mandatory Joker Lap:** Longer alternate route (1-3 sec slower)
- ✅ **Tactical Timing:** When to take joker (strategic decision)
- ✅ **Bracket Format:** Qualifying → Semi-finals → Finals
- ✅ **Tire Selection:** Compound choice for track conditions

### **ENDURANCE (4-24 hour races)**
- ✅ **Driver Rotation:** 2-3 drivers per car, managed fatigue
- ✅ **Fuel Strategy:** Double/triple stinting for overtaking
- ✅ **Pit Stops:** Mandatory driver changes every 2-4 hours
- ✅ **Driver Fatigue:** Performance degrades during stint
- ✅ **Damage Persistence:** Multi-stage carry-through (service park repairs)

### **Generic Damage Model (All Disciplines)**
- ✅ **Component Damage:** Engine, suspension, transmission, bodywork
- ✅ **Damage Assessment Crew:** Staff role affects repair efficiency
- ✅ **Performance Impact:** Damage reduces grip, speed, reliability

---

## Discipline Implementation Status

| Discipline | Engine | Tire Strategy | Fuel Mgmt | Joker Laps | Drift Scoring | Pit Stops | Car Sprites | Status |
|------------|--------|---------------|-----------|------------|---------------|-----------|-------------|--------|
| **Single Seater** | ✅ Full | ✅ **DESIGNED** | ✅ **DESIGNED** | N/A | N/A | ✅ **DESIGNED** | ❌ No | 70% |
| **Production/Touring** | ❌ Generic | ✅ **DESIGNED** | ⚠️ Optional | N/A | N/A | ✅ **DESIGNED** | ❌ No | 15% |
| **Urban Street (Drift)** | ❌ Generic | ⚠️ Drift-specific | N/A | N/A | ❌ **MISSING** | N/A | ❌ No | 10% |
| **Drag/Acceleration** | ✅ Custom | ⚠️ Launch grip | N/A | N/A | N/A | N/A | ❌ No | 60% |
| **Sprint/Rallycross** | ❌ Generic | ⚠️ Optional | ⚠️ Optional | ❌ **MISSING** | N/A | N/A | ❌ No | 10% |
| **Endurance** | ❌ Generic | ✅ **DESIGNED** | ✅ **DESIGNED** | N/A | N/A | ✅ **DESIGNED** | ❌ No | 15% |

**Legend:**
- ✅ **Fully Implemented** - Feature working and tested
- ⚠️ **Passive Only** - Exists but not interactive/strategic
- ❌ **Missing** - Not implemented
- N/A - Not applicable to this discipline

---

## Critical Missing Features

### 1. **Tire & Fuel Management** ⚠️ PASSIVE ONLY

**What EXISTS:**
```python
# In realtime_race_engine.py:
tire_condition: float = 1.0     # Degrades over time
fuel_load: float = 1.0          # Burns during race
TIRE_DEGRADATION_RATE = 0.00001
FUEL_BURN_RATE = 0.00002

# Effects on performance:
tire_penalty = 1.0 - (1.0 - state.tire_condition) * 0.25  # Up to 25% slower
fuel_bonus = 1.0 + (1.0 - state.fuel_load) * 0.03  # 3% faster when empty
```

**Design Says (GAME_DESIGN_DOCUMENT.md):**
- **Single Seater:** Tire compound selection (Soft/Medium/Hard), fuel load optimization, pit stop timing
- **Endurance:** Fuel strategy (multi-stinting), driver changes, fuel efficiency for longer stints
- **Production/Touring:** Tire management per surface, multi-stop strategy
- **Drag:** Launch grip tier selection
- **Rallycross:** Optional tire adaptation (no pit stops)

**What's MISSING:**
- ❌ **No pit stop system** - drivers can't change tires or refuel anywhere
- ❌ **No compound selection** - can't choose Soft/Medium/Hard
- ❌ **No undercut/overcut strategy** - pit timing has zero gameplay
- ❌ **No tire temperature/warm-up** - fresh tires instantly usable
- ❌ **No fuel saving mode** - can't trade speed for economy
- ❌ **Database columns exist** (`pitstops`, `tyre_strategy`) but **unused**

**Applies To:** Single Seater (HIGH priority), Endurance (HIGH priority), Production/Touring (MEDIUM)  
**Does NOT Apply To:** Rallycross (short sprints), Drag (one-off runs)  
**Drift-Specific:** Would need "tire heat" system instead of lap wear

---

### 2. **Joker Laps (Rallycross)** ❌ NOT IMPLEMENTED

**Design Says (GAME_DESIGN_DOCUMENT.md):**
- Mandatory "Joker Lap" (longer alternate route, 1-3 seconds slower)
- Tactical timing: when to take joker creates strategy depth
- Must take it once per race
- Race Strategist staff role affects joker timing

**What EXISTS:**
```python
# Database has joker_enabled column
# Track generation script creates joker lap geometry in database
# GUI can parse and render joker lap routes
```

**What's MISSING:**
- ❌ **No enforcement** - drivers don't take mandatory joker lap
- ❌ **No strategy** - can't choose when to take joker (early/late/tactical)
- ❌ **No penalty** for missing or not taking joker
- ❌ **No visualization** of who has/hasn't taken joker
- ❌ **No overtaking mechanics** using joker timing

**FIA Rallycross Rules:** 1-3 laps on main circuit → mandatory joker once → back to main circuit. Strategic timing creates overtaking/defensive opportunities.

**Current State:** Sprint/Rallycross uses generic race engine - joker lap logic completely absent.

**Design Intent:** Joker lap is **the defining mechanic** of the discipline (like pit stops for Single Seater, drift scoring for Urban Street)

---

### 3. **Drift Scoring System** ❌ NOT IMPLEMENTED

**Design Says (GAME_DESIGN_DOCUMENT.md):**
```
Drift Scoring: Angle, speed, line, smoke, proximity to walls
Tandem Battles: Lead/chase runs with judges deciding winner
Bracket Tournament: Top qualifiers advance (32→16→8→4→2→1)
Style Points: Transitions, smoke, proximity scoring
```

**What EXISTS:**
```python
# Urban Street discipline exists
# Driver has drift_control attribute
# Team names mention "drift"
# Staff role: DRIFT_COACH
```

**What's MISSING:**
- ❌ **No drift scoring system** - angle/speed/line/proximity scoring
- ❌ **No tandem battles** - judged head-to-head runs (lead/chase format)
- ❌ **No qualifying format** - top drivers advance to bracket
- ❌ **No bracket tournament** - single elimination rounds
- ❌ **No style points** - smoke, angle transitions not scored
- ❌ **Uses generic race engine** - just standard lap times with "drift" branding

**Design Intent:** Drift is **judged competition**, not lap time racing. Completely different mechanic from Circuit/Drag disciplines.

**Real Drift Competition Format:**
1. Solo qualifying runs (scored on angle/speed/line)
2. Top 32/16 advance to bracket
3. Tandem battles (lead/chase, judges score both)
4. Single elimination bracket to final

**Current State:** Urban Street is literally identical to Single Seater racing, just with "drift" in the name.

**Tire Management (Drift-Specific):** Would need custom model tracking tire heat/grip rather than lap wear.

---

### 4. **Pit Stop System** ❌ NOT IMPLEMENTED

**Design Says (GAME_DESIGN_DOCUMENT.md):**
- **Single Seater:** 1-2 strategic pit stops (50-70 laps)
- **Endurance:** Mandatory driver changes + refueling every 2-4 hours
- **Production/Touring:** 1-3 pit stops depending on fuel/tire strategy
- **Staff Impact:** MECHANIC role affects pit stop speed

**What EXISTS:**
```python
# Database columns: pitstops INTEGER, tyre_strategy TEXT
# Staff roles: MECHANIC affects pitstop base_effects
# OvertakeAttemptType.UNDERCUT exists (pit strategy concept)
```

**What's MISSING:**
- ❌ **No pit stop logic** - drivers never enter pits
- ❌ **No tire compound choices** - soft/medium/hard strategies not selectable
- ❌ **No pit stop time calculation** - crew skill has no effect
- ❌ **No fuel-only stops** (endurance racing)
- ❌ **No driver changes** - endurance needs multi-driver stints
- ❌ **No pit lane entry/exit** - where are pits?

**Critical For (Priority):**
- **Single Seater** (HIGH): Tire strategy is 50% of race strategy
- **Endurance** (HIGH): 4-6 hour races **REQUIRE** refueling and driver changes
- **Production/Touring** (MEDIUM): Multi-stint races with optional stops

**Does NOT Apply To:**
- **Drag** - one-off 1000m runs, no pit stops
- **Rallycross** - short sprint races, no pit stops
- **Drift** - judged format, no pit stops

---

### 5. **Discipline-Specific Engines** ❌ 4 of 6 MISSING

**Implemented:**
- ✅ `single_seater_discipline.py` - Full custom engine
- ✅ `drag_acceleration_discipline.py` - Reaction time, staging, burnout

**Missing:**
- ❌ `production_touring_discipline.py` - Falls back to generic engine
- ❌ `urban_street_discipline.py` - **No drift scoring system**
- ❌ `sprint_rallycross_discipline.py` - **No joker lap logic**
- ❌ `endurance_discipline.py` - **No driver swaps, no refueling**

**Consequence:** 4 of 6 disciplines use the same generic single-seater-style racing.

---

### 6. **Car Sprites/Visual Assets** ❌ ONLY SINGLE SEATER

**What EXISTS:**
```
GUI/assets/
  grass_tile.png
  props/
    tree_pine.png
    tree_oak.png
    tree_birch.png
    rock_1.png
    bush_1.png
```

**What's MISSING:**
- ❌ **No car sprites at all** - not even for single seater
- ❌ **No discipline-specific visuals:**
  - Single Seater: Open-wheel F1-style cars
  - Production/Touring: Sedans/GT cars with closed cockpits
  - Urban Street: Modified street cars (body kits, wide tires)
  - Drag: Dragsters (long wheelbase, parachutes, slicks)
  - Rallycross: Rally cars (roof scoops, mud flaps, knobby tires)
  - Endurance: Prototype LMP/GT cars (closed cockpit, aerodynamic)

**Current Visualization:** Just track geometry with trees/rocks - no cars rendered.

---

## Feature Completion by System

### Race Engine Core
- ✅ 30 FPS real-time simulation
- ✅ Driver AI decision-making (attack/defend/manage)
- ✅ Overtaking system with skill checks
- ✅ Tire degradation (passive)
- ✅ Fuel consumption (passive)
- ❌ **Pit stop system** (0%)
- ❌ **Penalties** (0%)
- ❌ **Safety car/yellows** (0%)

### Discipline Features
- ✅ Single Seater engine (70%)
- ✅ Drag racing engine (60%)
- ❌ **Drift scoring** (0%)
- ❌ **Joker lap system** (0%)
- ❌ **Endurance driver swaps** (0%)
- ❌ **Touring car qualifying** (0%)

### Strategic Depth
- ⚠️ Tire wear exists but **no pit stops to manage it**
- ⚠️ Fuel burn exists but **no saving mode or refueling**
- ❌ **No compound choices** (soft/medium/hard)
- ❌ **No setup adjustments** (wings, gearing)
- ❌ **No weather strategy** (wet vs dry tires)

### Visual Presentation
- ✅ Track geometry rendering
- ✅ Track props (trees, rocks)
- ❌ **No car sprites** (0%)
- ❌ **No pit lane graphics** (0%)
- ❌ **No tire smoke/effects** (0%)
- ❌ **No damage visualization** (0%)

---

## Recommendations (Priority Order)

### CRITICAL (Blocks Playability)
1. **Implement Pit Stop System** - Without this, tire/fuel systems are pointless
2. **Add Penalty System** - Currently no consequences for reckless driving
3. **Create Drift Scoring** - Urban Street is unplayable without judging

### HIGH (Core Discipline Features)
4. **Joker Lap Logic** - Sprint/Rallycross unplayable without mandatory alternate route
5. **Endurance Driver Swaps** - 4-6 hour races need multi-driver stints
6. **Production/Touring Engine** - Needs qualifying format, race format differences

### MEDIUM (Strategic Depth)
7. **Tire Compound Choices** - Soft/medium/hard strategies
8. **Fuel Saving Mode** - Trade speed for economy
9. **Setup Adjustments** - Wings, gearing, suspension

### LOW (Polish)
10. **Car Sprites** - Visual differentiation between disciplines
11. **Pit Lane Graphics** - Show pit activity
12. **Tire Smoke Effects** - Drift/lockup visuals

---

## Honest Assessment

**The Problem:** You have a sophisticated **Single Seater** racing engine that's being used for all 6 disciplines with minimal adaptation.

**Reality Check:**
- Drift competitions aren't lap time races
- Rallycross requires joker lap strategy
- Endurance needs multiple drivers per car
- No discipline can function without pit stops (except drag racing)

**What Works:** Single seater racing with passive tire/fuel degradation.

**What Doesn't:** Everything else is just single seater racing with different names.

---

**Status:** The game is essentially a **Single Seater simulator** pretending to support 6 disciplines. Either:
1. Focus exclusively on Single Seater and polish it
2. Implement discipline-specific systems properly (250+ hours work)
3. Remove unsupported disciplines from the game

Current approach of "6 disciplines" without implementing their defining features is misleading.
