# Implementation — Chosen Features

This section documents four implemented features with code-grounded traceability, algorithm-level explanation, and explicit responsibility boundaries. The objective is to demonstrate design ownership and implementation reasoning without reducing the chapter to line-by-line code narration.

Chosen features:

1. Reliability modelling (Weibull-based failure process)
2. Track-closure solver for generated circuits (regularised least-squares + derivative-free refinement)
3. Overtaking and wheel-to-wheel battle resolution
4. Driver/team attribute mapping from persistence layer to runtime performance

---

## Feature 1 — Reliability Modelling (Weibull Failure Process)

### Implementation Location and Execution Boundary

- RealtimeRaceEngine._weibull_incremental_failure_prob (realtime_race_engine.py).
- RealtimeRaceEngine._check_solo_incident (realtime_race_engine.py).
- HAZARD_CANDIDATES and calibration scoring pipeline (calibrate_3lap.py).

Responsibility split:

- The engine owns event-time hazard evaluation and DNF state mutation.
- Calibration tooling owns offline parameter selection against target discipline metrics.

### Algorithmic Behaviour

The engine does not sample directly from the full Weibull CDF over race horizon. Instead, it computes an incremental window probability for each simulation step.

With Weibull CDF:

$$
F(t) = 1 - e^{-(t/\eta)^\beta}
$$

the per-step failure probability over $\Delta t$ is evaluated as:

$$
P_{step} = F(t + \Delta t) - F(t)
$$

This is implemented by `_weibull_incremental_failure_prob()` and then applied to separate tyre and mechanical channels in `_check_solo_incident()`.

The incremental formulation is equivalent to a first-order finite difference approximation of the Weibull hazard integral, ensuring compatibility with discrete simulation ticks while preserving monotonic hazard growth under $\beta > 1$.

The channel-specific probabilities are then modulated by race context:

- Tyre failure path: scales hazard by tyre-condition depletion, consistency, setup and tyre-management effects.
- Mechanical path: scales hazard by push intensity/fatigue stress and reliability staff effect, then clips to a bounded maximum probability per tick.

### Design Rationale

Why Weibull (instead of exponential):

- Exponential assumes constant hazard ($\beta = 1$), which under-represents wear-out behaviour.
- Weibull supports increasing hazard for $\beta > 1$, allowing realistic late-race clustering of failures.
- Independent parameter sets (`tyre_eta`, `tyre_beta`, `mech_eta`, `mech_beta`) allow heterogeneous failure physics across subsystem types.

Why incremental evaluation at tick resolution:

- Preserves compatibility with discrete-time race loop execution.
- Enables local context scaling (push/fatigue/tyre state) at the same temporal granularity as state updates.
- Uses bounded per-step probabilities (clipping) to maintain numerical stability in a 30 Hz loop and avoid pathological event bursts from extreme transient states.

Computational complexity:

- Weibull evaluation is O(1) per subsystem per tick.
- Per-driver reliability update remains constant-time per tick, so total cost scales linearly with grid size.

### Validation Path

`calibrate_3lap.py` evaluates candidate hazard parameter sets against discipline targets (DNF rate and overtake signal), making reliability tuning reproducible and traceable rather than ad hoc.

---

## Feature 2 — Track-Creation Closure Solver (Regularised Solver Pipeline)

### Implementation Location and Execution Boundary

- Solver constants and optimisation policy (closure_solver.py).
- Continuous/discrete primitive simulation kernels: _simulate_primitives and _simulate_primitives_continuous (closure_solver.py).
- Main solve pipeline solve_closure (closure_solver.py).
- GUI call site CircuitGenerator._maybe_solve_closure (gui_race_visual.py).

Responsibility split:

- `closure_solver.py` owns numerical closure.
- GUI owns invocation policy and application of returned multipliers.

### Algorithmic Behaviour

The solver uses a two-stage optimisation strategy:

1. Stage 1 (continuous regularised least-squares):
	- `residuals_continuous()` computes closure residuals in $(x, y, \theta)$ space.
	- A regularisation term is appended as $(m_i - 1)\lambda$ for each multiplier $m_i$, controlled by `CLOSURE_REGULARIZATION_WEIGHT`.
	- `scipy.optimize.least_squares` provides a stable initial point under bounded parameters.

2. Stage 2 (discrete refinement):
	- `obj_discrete()` minimises the norm of residuals from full discrete primitive simulation.
	- `_minimize_discrete_with_fallback()` runs Powell first, then Nelder-Mead fallback if needed.

Success is declared only if final positional norm and angular error satisfy explicit tolerances (`CLOSURE_POSITION_TOLERANCE_M`, `CLOSURE_ANGLE_TOLERANCE_RAD`).

The two-stage optimisation decomposes a non-convex constraint surface into a convex relaxation (least squares) followed by a non-smooth refinement stage, reducing sensitivity to discretisation artefacts in primitive-based geometry evaluation.

### Design Rationale

Why regularised least-squares + derivative-free refinement:

- Pure single-pass least-squares is sensitive to local conditioning and may not align with discrete primitive semantics used by the generator.
- Regularisation penalises multiplier drift from nominal values, preventing degenerate geometric scaling modes.
- Derivative-free second stage reduces sensitivity to local minima introduced by discontinuities in discrete primitive evaluation.
- Bounded multiplier intervals and explicit success tolerances provide deterministic acceptance criteria despite local non-convexity.

Computational complexity:

- Optimisation cost is dominated by repeated primitive simulation, yielding O(k*n), where k is optimiser iterations and n is adjustable primitives.

This gives a practical balance between numerical stability and geometric fidelity.

---

## Feature 3 — Overtaking and Battling Logic

### Implementation Location and Execution Boundary

- Overtake decision model evaluate_overtaking_opportunity (overtaking_system.py).
- Logistic mapping utility _logistic_probability (overtaking_system.py).
- Runtime orchestration functions _evaluate_overtake_opportunities, _resolve_active_overtakes, and _resolve_single_overtake_attempt (realtime_race_engine.py).
- Contact-risk and battle state fields active_overtakes, _overtake_pair_cooldown, and OVERTAKE_INCIDENT_MULTIPLIER (realtime_race_engine.py).
- Geometry context TrackSection and TrackCorner (track_physics.py).

Responsibility split:

- `overtaking_system.py` computes attempt decision and baseline success probability from latent signals.
- `realtime_race_engine.py` manages attempt lifecycle, cooldown, resolution timing, and incident side-effects.
- `track_physics.py` provides section/corner semantics used by the decision model.

### Algorithmic Behaviour

Decisioning is latent-score based.

For each candidate pair, the model computes a weighted attacker-defender signal incorporating racecraft/aggression/bravery, defender response attributes, speed delta and track context. The latent value is transformed to probability by logistic mapping:

$$
P(success) = \frac{1}{1 + e^{-kz}}
$$

where $z$ is the latent advantage and $k$ is slope control (discipline tuning handle).

The latent score $z$ is constructed as a weighted affine combination of driver skill differentials and track-dependent modifiers, ensuring invariance under scale shifts in raw attribute distributions.

Runtime orchestration:

- Candidate generation and attempt logging occur before activation.
- active_overtakes stores in-progress interactions as bounded-duration battle objects.
- _resolve_single_overtake_attempt applies completion/abort criteria and commits deterministic state transitions.
- Pair cooldown via _overtake_pair_cooldown suppresses immediate re-entry into the same attacker-defender interaction.
- _maybe_trigger_overtake_contact applies conditional incident amplification during high-overlap phases.

### Design Rationale

Why logistic overtake model:

- Produces bounded probabilities with smooth sensitivity to multivariate latent signals.
- Supports interpretable tuning through slopes and feature weights.
- Avoids brittle threshold-only behaviour that can produce unrealistic binary outcomes.

Why separate decision and orchestration layers:

- Keeps tactical model independent from race-state mutation and event emission.
- Enables isolated calibration of latent-score weights without reparameterising event-lifecycle logic.

Computational complexity:

- Candidate evaluation is restricted to local competitors, giving neighbourhood-linear behaviour rather than full pairwise combinatorics.

---

## Feature 4 — Driver/Team Attributes to On-Track Performance

### Implementation Location and Execution Boundary

- Canonical-safe attribute access and derived-signal functions get_safe_attribute, get_driver_aggression, get_driver_wheel_to_wheel_ability, get_driver_confidence, and get_attribute_value (driver_attributes.py).
- Base performance composition calculate_base_performance and _calculate_team_performance (base_race_engine.py).
- Persistence/hydration boundary _hydrate_driver, get_all_drivers, and get_all_teams (database_manager.py).

Responsibility split:

- Database layer hydrates canonical `Driver` and `Team` records.
- Attribute service normalises/clamps values and computes derived behavioural signals.
- Race engines consume these values to compute discipline-specific performance and tactical behaviour.

### Algorithmic Behaviour

This feature is not a single formula; it is a staged transformation pipeline:

1. Persistence stage:
	- SQL rows are hydrated into typed driver/team objects by `DatabaseManager`.

2. Canonical mapping stage:
	- `get_safe_attribute()` enforces bounded, null-safe reads.
	- Derived metrics (aggression, confidence, wheel-to-wheel ability) are weighted combinations of canonical fields.

3. Engine aggregation stage:
	- `calculate_base_performance()` computes weighted composition of driver, team and environmental terms.
	- Team contribution is separately calculated in `_calculate_team_performance()` from tier and budget factors.

The separation between canonical attributes and derived behavioural metrics enforces schema stability while allowing non-linear transformations at the simulation layer without requiring persistence schema modification.

Computationally, bounded clamping at attribute-ingress and normalized weighted aggregation keep output scales stable under missing/noisy fields and prevent unbounded propagation into race-time probability models.

The aggregation stage is a weighted affine transform over normalized inputs, while derived behavioural metrics apply bounded non-linear composites; this decomposition preserves interpretability at the persistence boundary and expressiveness at the simulation boundary.

Computational complexity:

- Attribute transformation can be precomputed per race session.
- Runtime lookups are O(1) per driver per tick after precomputation.

### Design Rationale

Why this layered mapping (instead of direct raw attribute use everywhere):

- Prevents duplication of clamping/default logic across simulation modules.
- Maintains a stable canonical schema while allowing derived tactical signals for specific subsystems.
- Supports discipline extensibility by separating generic attribute access from discipline-specific weighting logic.

---

## Cross-Feature Traceability Summary

- Reliability dynamics are integrated at runtime in `RealtimeRaceEngine` and tuned offline in `calibrate_3lap`.
- Geometry closure is solved numerically in `closure_solver` and invoked by GUI circuit generation.
- Overtake probability generation is separated from battle lifecycle orchestration and incident handling.
- Driver/team data flows from DB hydration to canonical attribute mapping to performance computation.

The implementation therefore satisfies the intended architecture: each feature has a clear ownership boundary, explicit algorithmic mechanism, and traceable code-level grounding.
