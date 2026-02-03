# Discipline Feature Scope Clarification

**Author's Intent (from brainstorming):**

## Where Features Apply

### Tire & Fuel Management
- ✅ **Single Seater** - Full pit stop strategy (tire compounds, fuel loads)
- ✅ **Endurance** - Fuel management for multi-stint races
- ⚠️ **Production/Touring** - Optional multi-stop strategy
- ❌ **Rallycross** - NOT NEEDED (short sprint races)
- ❌ **Drag** - NOT NEEDED (one-off 1000m runs)
- 🔄 **Drift** - CUSTOM TIRE MANAGEMENT (heat/grip model, not lap wear)

### Joker Lap System
- ✅ **Rallycross ONLY** - Mandatory alternate route strategy

### Drift Scoring System  
- ✅ **Urban Street ONLY** - Judged competition (tandem battles, style points)

### Damage Model
- ✅ **Generic for all disciplines** - Single impact/damage system
  - Component tracking (engine, suspension, transmission, bodywork)
  - Performance impact (speed, grip, reliability loss)
  - Repair mechanics (crew skill affects fix time)

### Driver Swaps
- ✅ **Endurance ONLY** - Multi-driver management

---

## Implementation Priority

### HIGH (Core Mechanics - Blocks Playability)
1. **Pit Stop System** - Required for Single Seater and Endurance viability
2. **Penalty System** - Consequences for reckless driving (all disciplines)
3. **Drift Scoring** - Urban Street unplayable without judging

### MEDIUM (Discipline Definition)
4. **Joker Lap Logic** - Rallycross unplayable without mandatory joker
5. **Endurance Driver Swaps** - 4+ hour races need multi-driver stints
6. **Damage Model Enhancement** - Beyond binary crash→DNF

### LOW (Discipline Specialization)
7. **Tire/Fuel Strategy** - Only applies to SS, Touring, Endurance
8. **Discipline-Specific Engines** - 4 of 6 still missing

### NOT NEEDED
- Tire/fuel for Rallycross (handled by weather/surface instead)
- Tire/fuel for Drag (one-off races)
- Pit stops for Rallycross/Drag/Drift
- Joker laps for 5 other disciplines

---

## Design Philosophy

Each discipline should feel **fundamentally different** at a mechanical level:

| Discipline | Core Mechanic | Strategy Layer | Key Skill |
|------------|---------------|-----------------|-----------|
| Single Seater | Lap racing | Pit strategy (tires/fuel) | Consistency + planning |
| Touring | Lap racing | Multi-stop + traffic | Traffic management |
| Drift | Judged tandem | Style optimization | Angle/proximity control |
| Drag | One-off runs | Launch grip selection | Reaction time |
| Rallycross | Mixed surface | Joker timing | Adaptability |
| Endurance | Long-distance | Driver/fuel stints | Fatigue management |

The goal isn't "6 versions of the same game" - it's "6 completely different management games that happen to involve racing."

---

## Design vs Implementation Gap

**What Was Designed:** Complete, bespoke systems for each discipline  
**What's Implemented:** Single Seater + generic engine reused 4 times  
**Gap Size:** ~60% of design work remains

The GAME_DESIGN_DOCUMENT is comprehensive. The implementation tried to use 1 engine for everything.
