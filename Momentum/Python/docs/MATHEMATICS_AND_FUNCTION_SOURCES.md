# Mathematics and Function Sources

This document summarises the mathematics used by the game and points to the exact function sources.

## 0) Notation and External Maths Definitions

Use this section as a global reference for symbols/constants reused later.

### Core notation

- `exp(z)`: natural exponential function (`e^z`).
- `pi`: circle constant, approximately `3.14159`.
- `||v||_2`: Euclidean norm (L2 magnitude) of vector `v`.
- `clamp(x, lo, hi)`: clip `x` into interval `[lo, hi]`.

### Logistic function

`logistic(z) = 1 / (1 + exp(-z))`

- Output is in `(0, 1)`.
- Steepness constants such as `k` and `k_risk` scale `z` before logistic evaluation.
- Larger steepness causes faster transition between low and high probability regions.

### Weibull reliability model

`F(t) = 1 - exp(-(t/eta)^beta)`

- `eta` (scale): characteristic life/horizon; larger `eta` delays failures.
- `beta` (shape): hazard shape; `beta > 1` gives wear-out behaviour with rising hazard.

### Derivative-free optimisation methods

- `Powell`: directional derivative-free local optimisation.
- `Nelder-Mead`: simplex-based derivative-free local optimisation.
- In this project, Powell is primary and Nelder-Mead is fallback for robustness.

### Frequent model coefficients

- `a1, a2, a3`: linear feature weights in latent overtake-score models.
- `b`: bias/intercept term in latent overtake-score models.
- `k_driver`: steepness in normalised exponential driver-attribute mapping.
- `lambda`: regularisation weight in least-squares closure objective.

### Threshold and piecewise rules

- Extra tyre wear penalties apply in piecewise bands after 70% and 90% wear.
- Pit-stop decisions are boolean threshold rules combining tyre/fuel/lap constraints and projected loss.

## 1) Base Performance Model

Source file:
- `Momentum/Python/RaceLogic/base_race_engine.py`

Source functions:
- `BaseDisciplineEngine.calculate_base_performance`
- `BaseDisciplineEngine._calculate_team_performance`
- `BaseDisciplineEngine._calculate_weather_impact`
- `BaseDisciplineEngine._calculate_temperature_impact`
- `BaseDisciplineEngine._calculate_track_impact`

### Equations

Driver weighted score:

`driver_score = sum(weight_i * (attribute_i / 100)) / sum(weight_i)`

Composite performance:

`performance = 0.5 * driver_score + 0.3 * team_performance + 0.1 * weather_impact + 0.1 * track_impact`

Team performance:

`tier_base in {tier1:0.9, tier2:0.7, tier3:0.5}`

`budget_factor = min(team_budget / 200.0, 1.0) * 0.3`

`team_performance = min(tier_base + budget_factor, 1.0)`

Weather impact blend:

`weather_impact = 0.5 * rain_adaptation + 0.25 * wind_impact + 0.25 * temp_impact`

Temperature impact:

`temp_impact = max(0.7, 1.0 - abs(temp_c - 20.0)/30.0)`

Track impact:

`difficulty_impact = 1.0 - (difficulty * (1.0 - adaptability) * 0.3)`

`learning_impact = 0.9 + 0.1 * track_learning`

`track_impact = difficulty_impact * learning_impact`

## 2) Reliability and Incident Probability

Source file:
- `Momentum/Python/RaceLogic/base_race_engine.py`

Source functions:
- `BaseDisciplineEngine.check_mechanical_failure`
- `BaseDisciplineEngine.check_race_incident`

### Equations

Mechanical failure probability per lap:

`total_failure_rate = base_failure_rate + weather_stress + temp_stress`

Where:
- `base_failure_rate` depends on team tier
- `weather_stress = precipitation * 0.0002`
- `temp_stress = 0.0003` for extreme temperatures, else `0.0`

Incident probability per lap:

`total_incident_rate = base_incident_rate * consistency_factor * aggression_factor * weather_factor * traffic_factor`

With:
- `consistency_factor = 1.0 - (consistency / 200.0)`
- `aggression_factor = 1.0 + (aggression / 500.0)`

## 3) Real-Time Speed, Degradation, and Gaps

Source file:
- `Momentum/Python/RaceLogic/realtime_race_engine.py`

Source functions:
- `RealtimeRaceEngine._calculate_speed`
- `RealtimeRaceEngine._driver_attr_factor`
- `RealtimeRaceEngine._apply_driver_degradation`
- `RealtimeRaceEngine._apply_dirty_air_penalty`
- `RealtimeRaceEngine._apply_collision_avoidance`
- `RealtimeRaceEngine._update_gap_ahead_and_slipstream`
- `RealtimeRaceEngine._update_gap_behind`
- `RealtimeRaceEngine._advance_driver_position`

### Equations

Position update per frame (`dt = 1/30`):

`position_next = position_now + speed_mps * dt`

Driver attribute nonlinear mapping (used for speed, cornering, and consistency):

`x = clamp(attribute / 100.0, 0.0, 1.0)`

`driver_factor = (1 - exp(-k_driver * x)) / (1 - exp(-k_driver))`

With `k_driver = 2.6`.

Interpretation:
- This is a normalised exponential saturation curve.
- `k_driver` controls curvature/steepness: larger `k_driver` gives faster early gains and stronger diminishing returns near 1.0.

Speed construction (conceptual):

`speed = reference_speed * push_multiplier * driver_modifier * team_modifier * corner_modifier`

Then multiplied by:
- tyre penalty
- fuel bonus
- fatigue penalty
- slipstream bonus (if active)
- dirty-air penalty (if in corner and close)
- collision-avoidance slowdown (if unsafe gap)
- consistency noise

Then clamped to `[MIN_SPEED_MPS, MAX_SPEED_MPS]`.

Collision-avoidance speed shaping now uses a smooth desired-gap ratio instead of hard threshold braking:

`desired_gap = standstill_gap + headway_time * speed`

`speed_next = speed * clip((actual_gap / desired_gap)^1.35, 0.40, 1.0)`

Tyre and fuel update per frame:

`degradation = TYRE_DEGRADATION_RATE * push_intensity * surface_multiplier * compound_multiplier`

`tyre_condition = max(0.0, tyre_condition - degradation)`

`fuel_load = fuel_load - FUEL_BURN_RATE`

Current realtime tyre wear uses compound profiles rather than one flat multiplier:

`degradation = TYRE_BASE_WEAR_RATE * wear_multiplier * surface_multiplier * driver_wear_factor * push_multiplier * fatigue_multiplier`

Where compound profile values are:

`soft -> wear_multiplier=1.55, pace_base=1.02, pace_falloff_max=0.24`

`medium -> wear_multiplier=1.00, pace_base=1.00, pace_falloff_max=0.18`

`hard -> wear_multiplier=0.72, pace_base=0.985, pace_falloff_max=0.13`

`wet/rain -> wear_multiplier=1.18, pace_base=0.95, pace_falloff_max=0.16`

Progressive pace falloff from wear:

`wear = 1.0 - clamp(tyre_condition, 0.0, 1.0)`

`pace_multiplier = clamp(pace_base - pace_falloff_max * wear ^ pace_falloff_curve - extra_wear_penalty, 0.72, 1.03)`

where `extra_wear_penalty` adds additional loss once wear exceeds 70% and 90%.

Explicit threshold form used by the current model:

`extra_wear_penalty = 0`

`extra_wear_penalty += 0.20 * (wear - 0.70)` for `wear > 0.70`

`extra_wear_penalty += 0.35 * (wear - 0.90)` for `wear > 0.90`

AI pit-stop trigger uses projected tyre loss over a short stint horizon:

`projected_wear = wear_rate_per_step * steps_per_lap * laps_ahead`

`projected_condition = max(0.0, current_condition - projected_wear)`

`projected_loss_seconds = baseline_lap_seconds * (current_pace_multiplier - future_pace_multiplier) * laps_ahead`

AI pits when `current_condition <= 0.58` or `projected_loss_seconds >= 1.45` and enough laps remain.

Decision rule notation:

`pit_now = (laps_remaining > PIT_MIN_LAPS_REMAINING) and ((current_condition <= 0.58) or (projected_loss_seconds >= 1.45))`

## 4) Driver Mistake Risk (Realtime)

Source file:
- `Momentum/Python/RaceLogic/realtime_race_engine.py`

Source function:
- `RealtimeRaceEngine._check_driver_mistake`

### Equation

`mistake_prob = base_probability * push_risk * skill_factor * fatigue_multiplier * tyre_multiplier`

Where factors are built from consistency, vehicle control, fatigue, tyres, and push level.

Consistency and vehicle control are now passed through the same nonlinear driver mapping before contributing to `skill_factor`.

## 5) Overtaking Success and Incident Risk

Source file:
- `Momentum/Python/RaceLogic/overtaking_system.py`

Source functions:
- `evaluate_overtaking_opportunity`
- `calculate_defensive_action`
- `calculate_incident_risk`
- `resolve_overtake_outcome`

### Key formulas

Straight/braking/corner success probabilities are now logistic in latent competition score:

`P(success) = 1 / (1 + exp(-k * latent_signal))`

with section-specific `latent_signal` built from attacker score, defender score, speed/track context and maneuver type.

Representative straight latent structure:

`latent = a1*attacker_score - a2*defender_score + a3*speed_factor - b`

then `P = logistic(k * latent)` and clipped to guardrails.

Symbol meaning:
- `k`: logistic steepness (how quickly probability transitions from unlikely to likely).
- `a1, a2, a3`: feature weights for attacker quality, defender resistance, and speed context.
- `b`: bias/intercept term that sets baseline difficulty for that overtake type.

Previous linear form (retained here for historical reference):

`success_prob = 0.25 + 0.45*attacker_score - 0.25*defender_score + 0.35*speed_factor`

was replaced by bounded logistic forms for improved realism and diminishing returns.

Incident risk during overtake:

`incident_prob = base_risk * risk_multiplier * overlap_risk`

`risk_multiplier = 0.45 + 1.8 * logistic(k_risk * risk_pressure)`

`risk_pressure` combines aggression, bravery, overlap and inverse control skill.

Then clipped.

`k_risk` is the logistic steepness for incident escalation: larger values make risk rise more sharply once pressure crosses the midpoint.

Outcome resolution:
- sample incident first
- if no incident, sample success using `success_probability`

## 6) Pit and Joker Strategy Math

Source file:
- `Momentum/Python/RaceLogic/realtime_race_engine.py`

Source functions:
- `RealtimeRaceEngine._should_start_pit_stop`
- `RealtimeRaceEngine._emit_pit_window_open_if_needed`
- `RealtimeRaceEngine._enter_pit_lane`
- `RealtimeRaceEngine._maybe_apply_rallycross_joker`
- `RealtimeRaceEngine._joker_penalty_seconds`

### Logic math

Pit decisions combine thresholds on:
- laps remaining
- tyre condition
- fuel load
- mandatory-stop window
- player `come_in` override

Boolean form (player override + threshold logic):

`pit_now = player_come_in or hard_tyre_trigger or fuel_trigger or mandatory_window_trigger or ai_projected_loss_trigger`

AI tyre compound choice is also selected here using stint length and wear state:
```
`soft` for short stints or late-race fuel-offensive runs

`medium` for balanced stints

`hard` for longer stints when wear is already low and the remaining race distance is high
```
Joker penalty:

`penalty = RALLYCROSS_JOKER_BASE_PENALTY_S * skill_adjust + jitter`

`skill_adjust` is derived from consistency; final penalty is lower-bounded.

Lower bound in implementation:

`penalty = max(1.8, RALLYCROSS_JOKER_BASE_PENALTY_S * skill_adjust + jitter)`

Consistency in this context is also nonlinear-mapped via `RealtimeRaceEngine._driver_attr_factor`.

## 6b) Solo Failure Hazard (Realtime)

Source file:
- `Momentum/Python/RaceLogic/realtime_race_engine.py`

Source functions:
- `RealtimeRaceEngine._weibull_incremental_failure_prob`
- `RealtimeRaceEngine._check_solo_incident`

Weibull cumulative form:

`F(t) = 1 - exp(-(t/eta)^beta)`

Frame-step incremental hazard used in simulation:

`P_fail_step = F(t + dt) - F(t)`

Parameter meaning (standard Weibull):
- `eta` (scale): characteristic life/horizon; larger `eta` delays failures.
- `beta` (shape): hazard shape; `beta > 1` gives wear-out behaviour with rising hazard over time.

Mechanical and tyre-related solo failures now derive from this incremental Weibull hazard, then are modulated by push stress, tyre condition, reliability, setup, and tyre-management effects.

## 7) Discipline Adapter Tuning

Source files:
- `Momentum/Python/RaceLogic/disciplines/single_seater/single_seater_discipline.py`
- `Momentum/Python/RaceLogic/disciplines/drag_acceleration/drag_acceleration_discipline.py`
- `Momentum/Python/RaceLogic/disciplines/endurance/endurance_discipline.py`
- `Momentum/Python/RaceLogic/disciplines/sprint_rallycross/sprint_rallycross_discipline.py`
- `Momentum/Python/RaceLogic/disciplines/urban_street/urban_street_discipline.py`
- `Momentum/Python/RaceLogic/disciplines/production_touring/production_touring_discipline.py`

Source functions:
- per-file `get_attribute_weights`
- per-file `calculate_lap_time`
- per-file tuning helpers (for example `_apply_base_tuning`, `_apply_tuning`)

These adapters define discipline-specific coefficients while delegating race execution to `RealtimeRaceEngine`.

## 8) Championship Points Mathematics

Source file:
- `Momentum/Python/services/championship_service.py`

Source functions:
- `ChampionshipService.calculate_points`
- `ChampionshipService.recalculate_standings`

### Equations

Points are table-driven by discipline:

`base_points = points_table[position - 1]` if in range, else `0`

Fastest-lap bonus:

`total_points = base_points + fastest_lap_bonus`

Standings are aggregated and ranked by tie-break logic after total accumulation.

## 9) Hiring and Budget Mathematics

Source file:
- `Momentum/Python/services/hiring_service.py`

Source functions:
- `HiringService.estimate_driver_salary`
- `HiringService.estimate_staff_salary`
- `HiringService.calculate_team_salary_commitment`
- `HiringService.check_salary_cap_compliance`
- `HiringService.validate_contract_budget`

### Equations

Driver salary estimate:

`base_salary = (cap * 0.05) * skill_factor`

`final_salary = base_salary * achievement_bonus * experience_factor * age_factor`

Then clamped to min and max bounds.

Staff salary estimate (linear interpolation):

`estimated = min_salary + (max_salary - min_salary) * (rating / 100.0)`

Cap compliance:

`projected_commitment = current_commitment + additional_salary`

`is_compliant = projected_commitment <= cap`

Budget checks include signing bonus and reserve buffer thresholds.

## 10) Season Progression and Ageing Curves

Source file:
- `Momentum/Python/services/progression_service.py`

Source functions:
- `ProgressionService.calculate_age_factor`
- `ProgressionService.calculate_skill_progression`
- `ProgressionService.check_retirement_eligibility`

### Core math

Age factor is a piecewise function by age band (rookie growth, peak, decline).

Season progression applies random multipliers to skill groups using:
- age
- learning rate
- races completed
- diminishing returns at high skill

Retirement chance is age-band and performance dependent.

## 11) Track Closure Solver Mathematics

Source file:
- `Momentum/Python/RaceLogic/closure_solver.py`

Source functions:
- `_integrate_clothoid_discrete`
- `_integrate_clothoid_continuous`
- `_simulate_primitives`
- `_simulate_primitives_continuous`
- `_build_param_list`
- `_minimize_discrete_with_fallback`
- `solve_closure`
- `apply_multipliers_to_instructions`

Source constants:
- `CLOSURE_PRIMARY_MINIMIZE_METHOD`
- `CLOSURE_FALLBACK_MINIMIZE_METHOD`
- `CLOSURE_PRIMARY_MINIMIZE_OPTIONS`
- `CLOSURE_FALLBACK_MINIMIZE_OPTIONS`
- `CLOSURE_PARAM_MIN`
- `CLOSURE_PARAM_MAX`
- `CLOSURE_REGULARIZATION_WEIGHT`
- `CLOSURE_POSITION_TOLERANCE_M`
- `CLOSURE_ANGLE_TOLERANCE_RAD`

### Problem definition

Find multiplier vector `p` (one scale per straight/corner primitive) such that:
- final `x` is near 0
- final `y` is near 0
- final heading `theta` is near `2*pi`

Residual vector:

`r(p) = [x(p), y(p), wrap(theta(p) - 2*pi)]`

### Optimisation stages

Stage 1 (continuous least squares):
- Solve on continuous clothoid integration with bounds
- Includes regularisation terms towards 1.0 multipliers

Least-squares objective form:

`min_p || [x(p), y(p), wrap(theta(p)-2*pi), lambda*(p_1-1), ..., lambda*(p_n-1)] ||_2^2`

with `lambda = CLOSURE_REGULARIZATION_WEIGHT`.

Stage 2 (discrete refinement):
- Minimise `||r(p)||_2` on discrete simulation
- Uses `CLOSURE_PRIMARY_MINIMIZE_METHOD` (Powell), then
	`CLOSURE_FALLBACK_MINIMIZE_METHOD` (Nelder-Mead) fallback

Method note:
- Powell and Nelder-Mead are derivative-free optimisers from numerical optimisation literature.
- Powell is used first for robust line-search style progress; Nelder-Mead is a simplex fallback when Powell fails to converge satisfactorily.

Success criteria:
- `pos_norm = ||[x, y]|| < CLOSURE_POSITION_TOLERANCE_M`
- `ang_err = abs(wrap(theta - 2*pi)) < CLOSURE_ANGLE_TOLERANCE_RAD`

### Angle wrapping

`wrap(a)` normalises heading to `[-pi, pi]` for stable residual behaviour.

## 12) Staff Runtime Impact and Diminishing Returns

Source file:
- `Momentum/Python/RaceLogic/realtime_race_engine.py`

Source functions:
- `RealtimeRaceEngine._hydrate_staff_effects_for_teams`
- `RealtimeRaceEngine._rating_impact_factor`
- `RealtimeRaceEngine._saturate_staff_effect`
- `RealtimeRaceEngine._get_team_multiplier`
- `RealtimeRaceEngine._enter_pit_lane`
- `RealtimeRaceEngine._maybe_trigger_overtake_contact`
- `RealtimeRaceEngine._maybe_trigger_rear_end_incident`
- `RealtimeRaceEngine._check_solo_incident`

### Equations

Per-staff rating nonlinear contribution:

`r = clamp(rating / 100.0, 0.0, 1.0)`

`rating_factor = (1 - exp(-k_staff_rating * r)) / (1 - exp(-k_staff_rating))`

With `k_staff_rating = 3.0`.

Raw role effect accumulation (per team, per effect key):

`raw_effect_j = sum_over_staff(base_effect_j * rating_factor * discipline_modifier)`

Saturating diminishing returns for aggregate staff effects:

`staff_effect_j = C * (1 - exp(-k_staff_sat * (raw_effect_j / C)))`

With:
- `C = STAFF_EFFECT_CAP = 0.35`
- `k_staff_sat = STAFF_EFFECT_SATURATION_STRENGTH = 1.35`

This creates strong early gains and progressively smaller gains near cap.

### Where these effects are applied

- Team pace multiplier via operations, car_performance, power, handling, aero, strategy
- Pit service time reduction via pitstop, operations, strategy
- Overtake/contact and rear-end DNF risk reduction via reliability, consistency, racecraft
- Solo tyre-spin and mechanical risk reduction via tyre_management, setup, reliability

## 13) Curve Calibration Reference

This section provides concrete example points for the active nonlinear curves in the race engine.

### Driver attribute mapping reference (`k_driver = 2.6`)

| Raw Attribute | Nonlinear Factor |
|---|---|
| 40 | 0.6984 |
| 60 | 0.8532 |
| 80 | 0.9453 |
| 95 | 0.9889 |

Interpretation:
- The jump from 40 to 60 is large.
- The jump from 80 to 95 is much smaller (tail-off near elite).

### Staff rating mapping reference (`k_staff_rating = 3.0`)

| Raw Rating | Rating Factor |
|---|---|
| 40 | 0.7354 |
| 60 | 0.8784 |
| 80 | 0.9569 |
| 95 | 0.9915 |

### Staff aggregate saturation reference (`C = 0.35`, `k_staff_sat = 1.35`)

| Raw Aggregate Effect | Saturated Effect |
|---|---|
| 0.03 | 0.0382 |
| 0.06 | 0.0723 |
| 0.12 | 0.1297 |
| 0.18 | 0.1752 |
| 0.24 | 0.2113 |
| 0.30 | 0.2400 |
| 0.36 | 0.2627 |

Interpretation:
- Early accumulation improves quickly.
- High accumulation keeps improving, but at progressively lower marginal gain.
