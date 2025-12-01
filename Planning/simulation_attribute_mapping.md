# Simulation Attribute Mapping

Purpose: map existing driver and track attributes (from `database/models.py`) to simulation factors used by the lap-by-lap engine. This document should be used as the canonical reference when refactoring `sim_simple.py` to use the full schema.

Conventions
- All driver attributes are in the 0–100 scale. Normalize to 0.0–1.0 for formulas: norm(x) = x/100.
- Positive effects: higher value improves performance (may reduce lap time). Negative effects: higher value increases cost (e.g., tyre wear). Document sign clearly.
- Use weighted linear combinations for initial implementation. Replace by calibrated non-linear functions if needed later.

1) Core lap-time formula (high-level)

BaseLapTime (s) = track.length_km * 60.0

DriverPerformanceFactor = w_speed * (1 - norm(raw_speed))
                       + w_corner * (1 - norm(cornering_skill)) * track.corner_factor
                       + w_brake * (1 - norm(braking_technique)) * track.braking_factor
                       + w_accel * (1 - norm(acceleration_control)) * track.accel_factor

LapTime = BaseLapTime * (1 + DriverPerformanceFactor) * TyrePenalty * FuelPenalty + RandomNoise

Where:
- TyrePenalty = 1 + tyre_wear * tyre_penalty_scale (see tyre wear mapping)
- FuelPenalty = 1 + fuel_load_factor * fuel_penalty_scale
- RandomNoise is scaled by (1 - norm(consistency)) to reflect lap-to-lap variance

Recommended initial weights (tuneable):
- w_speed = 0.45
- w_corner = 0.20
- w_brake = 0.10
- w_accel = 0.10
- remaining 0.05 reserved for strategy/other

2) Tyre management & wear

Inputs:
- `tyre_management` (driver): higher reduces wear rate
- `aggression` inferred from (raw_speed vs consistency): aggression = clamp((raw_speed - consistency) / 50, 0, 1)
- track.surface_grip (if present) or `track.grip_modifier`

WearRatePerLap = base_wear + aggression * aggression_wear + (1 - norm(tyre_management)) * management_factor + track_abrasion

Where base_wear = 0.01..0.03, aggression_wear ~= 0.01..0.03, management_factor ~= 0.02

TyrePenalty = 1.0 + (accumulated_wear * tyre_penalty_scale)  # tyre_penalty_scale ~= 0.35

Pit decision: pit when accumulated_wear > threshold OR when expected remaining laps * predicted_wear would exceed safe limit.

3) Reliability / incidents / DNF

Inputs:
- `mechanical_sympathy`, `reliability` (if present), `concentration`, `fatigue` (derived from laps)

BaseIncidentRate = baseline (e.g., 0.002 per lap)
ReliabilityModifier = (1 - norm(mechanical_sympathy)) * reliability_weight
ConcentrationModifier = (1 - norm(concentration)) * concentration_weight

IncidentChance = BaseIncidentRate + ReliabilityModifier + ConcentrationModifier + track_hazard

If Incident occurs: 25% chance of DNF (retirement), otherwise time loss random(5..35s)

4) Overtaking & racecraft

Inputs:
- `racecraft`, `overtaking`, `defensive_driving`, `spatial_awareness`, `raw_speed`

RelativePerformance = small delta in lap_time between two drivers
OvertakeProbability ~ sigmoid( alpha*(attacker_advantage) + beta*racecraft + gamma*overtaking - delta*defensive )

Initial simple model: per-lap, if attacker cumulative time < defender cumulative time - gap_threshold, then attempt overtake with probability P where
P = clamp(0.05 + 0.4*(norm(overtaking)) + 0.3*(norm(racecraft)) - 0.2*(norm(defensive_driving)) + 0.2*(speed_diff_norm), 0.01, 0.9)

Successful overtake reduces attacker total_time by small amount (1-3s) and increases defender time by similar amount to simulate position change.

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
