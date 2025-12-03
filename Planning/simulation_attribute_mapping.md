# Real-Time Agent-Based Simulation Attribute Mapping

**Purpose:** Map driver and track attributes (from `database/models.py`) to real-time physics calculations in the 30 FPS agent-based simulation engine (`realtime_race_engine.py`). This replaces the previous lap-by-lap statistical approach.

**Architecture:** Each driver is an autonomous agent with continuous position updates at 30 FPS. Physics calculations occur every frame (0.033 seconds) based on driver skills, team capability, environmental conditions, and AI decision-making.

## Conventions
- All driver attributes use 0–100 scale. Normalize to 0.0–1.0: `norm(x) = x/100`
- Physics operates at **30 FPS** (timestep = 1/30 = 0.033 seconds)
- Position integration: `position_m += velocity_mps * timestep`
- Higher attribute values → better performance (except wear/fuel consumption)
- Racing modes affect speed multipliers and resource consumption

## 1) Core Speed Calculation (Per-Frame Physics)

**Implemented in:** `RealtimeRaceEngine._calculate_speed()`

```python
base_speed_mps = (
    0.40 * weighted_driver_skills +
    0.30 * team_capability_normalized +
    0.20 * tire_condition +
    0.10 * (1.0 - fuel_load * 0.02)
)

# Weighted driver skills (example for Single Seater)
weighted_skills = (
    0.25 * norm(raw_speed) +
    0.20 * norm(cornering_skill) +
    0.15 * norm(racecraft) +
    0.12 * norm(consistency) +
    0.10 * norm(physical_fitness) +
    0.08 * norm(setup_knowledge) +
    0.10 * norm(tire_management)
)

# Slipstream bonus (within 50m)
if gap_ahead < 50.0:
    base_speed_mps *= 1.05  # +5% in slipstream

# Racing mode multipliers
mode_multipliers = {
    RacingMode.ATTACK: 1.03,   # +3% speed, high tire wear
    RacingMode.DEFEND: 0.98,   # -2% speed, blocking
    RacingMode.MANAGE: 1.00,   # Optimal balance
    RacingMode.CRUISE: 0.97    # -3% speed, conserving
}

final_speed_mps = base_speed_mps * mode_multipliers[racing_mode]
final_speed_mps *= track_speed_scale  # Track-specific (e.g., 50 m/s average)
```

**Key Changes from Lap-by-Lap:**
- ❌ **Removed:** `BaseLapTime`, lap-based formulas
- ✅ **Added:** Continuous velocity in meters/second
- ✅ **Added:** Real-time position integration
- ✅ **Added:** Racing mode multipliers

## 2) Tire Degradation (Per-Frame)

**Implemented in:** `RealtimeRaceEngine._update_driver_state()`

**Inputs:**
- `tire_management` (driver): Higher reduces wear rate
- `racing_mode`: ATTACK increases wear significantly
- Track surface abrasiveness

**Per-Frame Wear Calculation:**
```python
base_wear_per_second = 0.0001  # 0.01% per second baseline

# Racing mode wear multipliers
mode_wear = {
    RacingMode.ATTACK: 2.0,   # Double wear rate
    RacingMode.DEFEND: 1.3,   # Elevated wear
    RacingMode.MANAGE: 1.0,   # Normal wear
    RacingMode.CRUISE: 0.7    # Reduced wear
}

# Driver skill mitigation
management_factor = 1.0 - (norm(tire_management) * 0.4)

# Calculate wear for this frame
wear_this_frame = (
    base_wear_per_second * 
    timestep * 
    mode_wear[racing_mode] * 
    management_factor *
    track_abrasion_factor
)

tire_condition -= wear_this_frame  # 1.0 = new, 0.0 = destroyed
tire_condition = max(0.0, tire_condition)
```

**Speed Impact:**
- Tire condition directly affects speed calculation (20% weight in speed formula)
- `speed_mps *= (0.2 * tire_condition)` component

**AI Response:**
- When `tire_condition < 0.6`, AI switches to MANAGE mode
- Reduces wear rate and preserves remaining tire life

## 3) Incidents & DNF (Per-Frame Probability)

**Implemented in:** `RealtimeRaceEngine._check_incident()`

**Inputs:**
- `mechanical_sympathy`, `professionalism`, `adrenaline_management`
- Racing mode (ATTACK/DEFEND increases risk)

**Per-Frame Incident Probability:**
```python
base_incident_per_second = 0.00001  # 0.001% per second

# Racing mode risk multipliers
mode_risk = {
    RacingMode.ATTACK: 2.5,   # High risk
    RacingMode.DEFEND: 1.8,   # Elevated risk
    RacingMode.MANAGE: 1.0,   # Normal
    RacingMode.CRUISE: 0.5    # Low risk
}

# Driver skill mitigation
skill_factor = (
    norm(mechanical_sympathy) * 0.4 +
    norm(professionalism) * 0.3 +
    norm(adrenaline_management) * 0.3
)

incident_probability = (
    base_incident_per_second * 
    timestep * 
    mode_risk[racing_mode] *
    (1.5 - skill_factor)  # Lower skill = higher risk
)

if random() < incident_probability:
    driver.dnf = True
    EMIT event: driver_retired
```

**Key Changes:**
- ❌ **Removed:** Lap-based incident checks
- ✅ **Added:** Continuous per-frame probability
- ✅ **Added:** Racing mode affects risk (ATTACK mode = 2.5x base risk)

## 4) AI Decision-Making & Racing Modes

**Implemented in:** `RealtimeRaceEngine._update_racing_mode()`

**Inputs:**
- `gap_ahead`, `gap_behind` (spatial awareness)
- `tire_condition`, `fuel_load`
- `overtaking`, `defensive_driving`, `racecraft`

**Mode Selection Algorithm:**
```python
def determine_racing_mode(driver_state):
    # Overtaking opportunity
    if gap_ahead < 20.0 and tire_condition > 0.6:
        return RacingMode.ATTACK
    
    # Defending position
    if gap_behind < 15.0:
        return RacingMode.DEFEND
    
    # Tire preservation
    if tire_condition < 0.6:
        return RacingMode.MANAGE
    
    # Comfortable lead/out of contention
    if gap_ahead > 100.0 and gap_behind > 100.0:
        return RacingMode.CRUISE
    
    # Default competitive pace
    return RacingMode.MANAGE
```

**Spatial Awareness System:**
```python
# Calculate gaps to nearby cars
gap_ahead = next_car.position_m - current_car.position_m
gap_behind = current_car.position_m - previous_car.position_m

# Detect slipstream (within 50m)
if gap_ahead < 50.0:
    slipstream_active = True
    speed_bonus = 1.05  # +5% speed

# Find nearby cars for AI context
nearby_cars = [
    car for car in all_cars 
    if abs(car.position_m - current_car.position_m) < 100.0
]
```

**Key Changes:**
- ❌ **Removed:** Lap-based overtake probability calculations
- ✅ **Added:** Continuous AI decision-making every frame
- ✅ **Added:** Four racing modes with distinct behaviors
- ✅ **Added:** Spatial awareness (gaps, slipstream, nearby cars)

5) Strategy & pit behaviour

Inputs:
- `race_strategy`, `pit_preference` (if present), `team_budget` (optional), `driver.tire_management`, `track.length_km`

Default behaviour: prefer pitting when tyre_wear > 0.6. Strategy modifiers:
- Aggressive: pit later (threshold=0.7), push harder (increase aggression multiplier)
- Conservative: pit earlier (threshold=0.5), lower aggression, reduce incident chance

6) Qualifying / start performance

Inputs:
- `reaction_time`, `starting_skill`, `concentration`

Start advantage: compute `start_bonus` = small time reduction (0..1s) influenced by norm(starting_skill) and reaction_time.

7) Driver energy/consistency across race

Use `consistency` to scale per-lap noise: LapNoiseScale = base_noise * (1 - norm(consistency)). Also apply minor fatigue scaling over many laps (for detailed mode) using `physical_fitness` and `g_force_tolerance`.

8) Track characteristics

- `length_km` → BaseLapTime
- `surface_type` / `grip_modifier` → affects tyre_wear and base lap (lower grip increases lap times and wear)
- `corneriness` / `number_of_corners` (if modelled) → weight of `cornering_skill` component
- `altitude` / `temperature` / `weather` flags → modifiers for engine/fuel performance and incident rate (detailed mode)

9) Fast-lane implementation notes

- Normalize attributes to 0..1 once on load to avoid repeated division.
- Keep a small, tunable set of constants in `sim_simple.py` or a config module for weights and thresholds.
- Make simulation deterministic by using a single RNG with seed passed into `run_mvp`; avoid separate global RNGs.
- Expose a callback to stream lap events (pit, incident, overtake) so the GUI and telemetry writer can record them in real time.

10) Quick calibration and tests

- Create unit tests that check monotonic relationships: increasing `raw_speed` should (all else equal) reduce lap time. Increasing `tyre_management` should reduce wear.
- Provide a small calibration script that runs repeated seeded simulations and prints sensitivity (delta in finishing time) per attribute to help tune weights.

11) Next steps

1. Review this mapping and approve or adjust weights/choice of attributes.
2. I'll update `PersistenceSQLite` to load full driver/track rows and provide normalized fields to the simulator.
3. Refactor `sim_simple.py` to implement these mappings and add event callbacks for GUI/telemetry.

Document author: assistant (planning artifact for `basic-race`)
