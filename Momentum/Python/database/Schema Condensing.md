Schema Condensing

This document lists driver attributes and provides a structured culling/condensing decision table to help you choose which fields to keep, compute, merge or move to JSON/history tables.

## Attributes (excerpt)

- `racecraft`, `overtaking`, `defensive_driving`, `cornering_skill`, `braking_technique`, `acceleration_control`, `spatial_awareness`, `vehicle_control`
- Physical & mental: `physical_fitness`, `reaction_time`, `concentration`, `pressure_handling`, `pain_tolerance`, `g_force_tolerance`, `coordination`, `multitasking`, `mental_resilience`, `adrenaline_management`
- Technical: `setup_knowledge`, `mechanical_sympathy`, `tire_management`, `fuel_management`, `aerodynamics_understanding`, `suspension_feel`, `engine_management`, `data_analysis`
- Discipline aptitudes: `single_seater_aptitude`, `touring_car_aptitude`, `rally_aptitude`, `street_racing_aptitude`, `drag_racing_aptitude`, `rallycross_aptitude`, `endurance_aptitude`
- Racecraft & strategy: `race_strategy`, `pit_entry_exit`, `traffic_management`, `qualifying_pace`, `race_pace`, `starting_skill`, `tyre_warming`, `energy_management`
- Environment: `wet_weather_skill`, `night_driving`, `heat_tolerance`, `cold_tolerance`, `altitude_adaptation`, `visibility_adaptation`, `surface_adaptation`
- Personal/social: `media_handling`, `sponsorship_appeal`, `fan_engagement`, `team_player`, `leadership`, `professionalism`
- Career stats & metadata: `career_wins`, `career_podiums`, `career_points`, `career_starts`, `career_dnf`, `seasons_active`, `single_seater_wins`, `touring_wins`, `rally_wins`, `street_wins`, `drag_wins`, `rallycross_wins`, `endurance_wins`, `biography`, `career_highlights`, `preferred_discipline`, `career_phase`, `current_team_id`, `previous_teams`, `contract_length`, `salary`, `form_trend`, `peak_performance_age`, `retirement_age`, `learning_rate`, `championship_titles`, `rookie_of_year_awards`, `fastest_laps`, `pole_positions`

---

## Culling Decision Table — usage, recommendation, effort, risk

This table summarises how attributes are actually used in the codebase (engine, overtaking, track physics, services, DB), and gives a clear recommended action to help you decide what to cull, merge, compute or keep.

- Attribute / Group: `raw_speed`

  - Usage: Core input to lap-time/push calculations across `realtime_race_engine.py`, `services/driver_attributes.py`, discipline weightings and ordering in DB queries.
  - Primary call sites: `realtime_race_engine.py`, `services/driver_attributes.py`, `database_manager.py` (ordering/filtering).
  - Recommendation: KEEP (persisted).
  - Rationale: High read frequency and used in sorting and many algorithms; cheap to persist and required for reporting.
  - Effort: Low. Risk: Low.

- Attribute / Group: `racecraft`

  - Usage: Used directly and inside overtaking formulas; influences attack/defend decisions and incident probability.
  - Primary call sites: `overtaking_system.py`, `realtime_race_engine.py`, discipline weightings.
  - Recommendation: KEEP (persisted) but introduce a computed `racecraft_rating` for UIs/aggregates.
  - Rationale: Semantically distinct from overtaking; widely referenced in core logic.
  - Effort: Low. Risk: Low.

- Attribute / Group: `overtaking`
  - User suggestion: "go into racecraft" (noted)
  - Usage: Primary contributor in overtaking probability and attacker logic in `overtaking_system.py` and `realtime_race_engine.py`.
  - Primary call sites: `overtaking_system.py`, `realtime_race_engine.py`, `services/driver_attributes.py`.
  - Recommendation: KEEP as separate persisted field (do NOT collapse into racecraft immediately). Consider later MERGE into a single `wheel_to_wheel` metric if you consolidate many small racecraft sub-attributes—this needs retuning/testing.
  - Rationale: Explicit weight coefficients rely on it; merging would require thorough retuning/testing of coefficients.
  - Effort: Medium if merging. Risk: Medium.

- Attribute / Group: `vehicle_control`, `cornering_skill`, `braking_technique`, `acceleration_control`, `suspension_feel`
  - User suggestion: "Could go into racecraft and pace" (noted)
  - Usage: Frequently combined in engine code and overtaking logic to compute handling/exit speeds and corner performance.
  - Primary call sites: `track_physics.py`, `overtaking_system.py`, `realtime_race_engine.py`.
  - Recommendation: PERSIST fine-grained attributes for now, but add a computed `vehicle_handling` aggregate that other modules can consume; later merge less-used fields into `attributes_extra` if you need to reduce column count.
  - Rationale: Many formulas weight these differently; keeping them avoids risking regressions. Computed aggregate reduces code duplication and centralises tuning.
  - Effort: Low to add computed helper; High to remove columns. Risk: Low for compute, High for destructive schema changes.

- Attribute / Group: `tyre_warming`, `tire_management`
  - User suggestion: "fo into tyres" (noted — meaning move under tyre management)
  - Usage: Used in tyre / warmup logic and racing mode transitions; also referenced in GUI/strategy descriptions.
  - Primary call sites: `realtime_race_engine.py`, discipline docs.
  - Recommendation: MERGE conceptually into `tire_management` (persist one canonical field) or keep both but prefer `tire_management` as canonical and deprecate `tyre_warming` with a computed shim during transition.
  - Rationale: Overlap is semantic; consolidation is straightforward but requires search-and-replace/backfill.
  - Effort: Medium. Risk: Low.

- Attribute / Group: `engine_management`, `mechanical_sympathy`, `setup_knowledge`, `suspension_feel`, `aerodynamics_understanding`
  - User suggestion: "car development" (noted)
  - Usage: Technical knowledge / engine control used for long-term performance and pit/strategy choices; some used in pace calculations.
  - Primary call sites: `services/driver_attributes.py`, discipline weightings, `database_manager.py`.
  - Recommendation: KEEP but consider MERGE of conceptually overlapping attributes into two persisted fields: `technical_knowledge` (setup + aero + mech sympathy) and `engine_management` (driving-specific power modes). Or keep as-is and mark as lower-priority for culling.
  - Rationale: These are lower-frequency relative to raw_speed/overtaking, but useful for season progression and driver development.
  - Effort: Medium. Risk: Medium.

- Attribute / Group: `age`, `birth_date`

  - Usage: `birth_date` is persisted; `age` is persisted but can get out of sync. `age` appears in DB schema and manager inserts/loads.
  - Primary call sites: `database/models.py`, `database_manager.py`.
  - Recommendation: MOVE to computed property: persist `birth_date` only, compute `age` at runtime (avoid persisting `age`). Mark `age` for removal from schema on an eventual migration.
  - Rationale: Deterministic value; removing `age` saves redundancy and avoids stale data.
  - Effort: Low to implement compute shim; Medium to drop column. Risk: Low.

- Attribute / Group: `defensive_driving`, `spatial_awareness`, `pressure_handling`, `concentration`
  - User suggestion: "racecraft" (noted)
  - Usage: Inputs to defensive logic, collision avoidance, and stamina/consistency calculations.
  - Primary call sites: `overtaking_system.py`, `realtime_race_engine.py`.
  - Recommendation: KEEP persisted; add computed `defensive_rating` if you want a single UI field. Do not cull unless you consolidate multiple mental attributes into `mental_resilience` first.
  - Effort: Low. Risk: Low.

- Attribute / Group: `learning_rate`, `peak_performance_age`, `retirement_age`, `career_phase`
  - User suggestion: "yeah these are ok" (noted)
  - Usage: Used for progression modelling and career simulation, not per-frame engine code.
  - Primary call sites: planning/progression systems, docs, scripts.
  - Recommendation: KEEP (persisted) but move static metadata that is rarely updated into `attributes_extra` JSON if you need to reduce column count; these are safe to store elsewhere.
  - Effort: Low. Risk: Low.

- Career stats (`career_wins`, `podiums`, `starts`, `dnf`, discipline-specific wins)

  - Usage: Aggregated results; should be derived from `race_results` and `driver_career_stats` aggregate table.
  - Primary call sites: reporting, UI, save/load.
  - Recommendation: MOVE out of core `drivers` table into a `driver_career_stats` aggregate table or compute on demand. Keep caching columns only if performance requires (but mark as derived and rebuildable).
  - Rationale: Normalisation reduces update contention and size of driver row writes.
  - Effort: Medium. Risk: Medium (requires migration/backfill).

- Less-used / optional attributes (`media_handling`, `sponsorship_appeal`, `fan_engagement`, `biography`, `career_highlights`, `previous_teams`)
  - User suggestion: "All these can go" (noted)
  - Usage: UI, docs, external presentation. `previous_teams` stored as JSON text.
  - Recommendation: MOVE into `attributes_extra` JSON column or a `profile` table. Keep `biography`/`career_highlights` small text fields if they are used in the UI; move `previous_teams` to a history table if you need structured queries.
  - Effort: Low. Risk: Low.

Quick decision matrix (one-line actions)

- KEEP persisted: `raw_speed`, `racecraft`, `overtaking`, `defensive_driving`, `spatial_awareness`, `consistency`.
- COMPUTE (non-destructive helper): `age` (from `birth_date`), `racecraft_rating`, `vehicle_handling`, `defensive_rating`.
- MERGE (medium effort, needs retuning): `tyre_warming` -> `tire_management`; consider merging technical knowledge fields into `technical_knowledge` if column count is a priority.
- MOVE (to JSON or history tables): `previous_teams`, optional metadata (`media_handling`, `fan_engagement`), seldom-updated career metadata.
- RELOCATE (normalize): career stats -> `driver_career_stats` or derived from `race_results`.

Recommended immediate steps (low-risk, high-value)

1. Add computed properties and helper functions in `Momentum/Python/database/models.py` and `Momentum/Python/services/driver_attributes.py`:
   - `Driver.age` -> compute from `birth_date`.
   - `Driver.racecraft_rating` -> weighted aggregate of `racecraft`, `overtaking`, `defensive_driving`, `spatial_awareness`.
   - `Driver.vehicle_handling` -> aggregate of `vehicle_control`, `cornering_skill`, `braking_technique`, `suspension_feel`.
2. Update `services/driver_attributes.py` to use these helpers (centralise weighting there).
3. Run the DB init and test race engine to ensure no behaviour changes. Fix the `db.init_database()` error before attempting any schema migration.

If you want persisted consolidation (next-phase)

- Create `driver_career_stats` table (aggregates) and move career counters there.
- Add optional `attributes_extra` JSON column to `drivers` to store low-priority / bulky fields.
- Backfill: populate aggregates from `race_results` and copy optional fields into `attributes_extra` month-by-month.
- Finally, rebuild `drivers` table if you need to drop columns (SQLite requires CREATE TABLE AS SELECT / rename/drop sequence).

Next step: I can implement the non-destructive computed helpers in `database/models.py` and update `services/driver_attributes.py` now. Should I proceed?
# Schema Condensing

This document lists driver attributes and provides a structured culling/condensing decision table to help you choose which fields to keep, compute, merge or move to JSON/history tables.

## Attributes (excerpt)

- `racecraft`, `overtaking`, `defensive_driving`, `cornering_skill`, `braking_technique`, `acceleration_control`, `spatial_awareness`, `vehicle_control`
- Physical & mental: `physical_fitness`, `reaction_time`, `concentration`, `pressure_handling`, `pain_tolerance`, `g_force_tolerance`, `coordination`, `multitasking`, `mental_resilience`, `adrenaline_management`
- Technical: `setup_knowledge`, `mechanical_sympathy`, `tire_management`, `fuel_management`, `aerodynamics_understanding`, `suspension_feel`, `engine_management`, `data_analysis`
- Discipline aptitudes: `single_seater_aptitude`, `touring_car_aptitude`, `rally_aptitude`, `street_racing_aptitude`, `drag_racing_aptitude`, `rallycross_aptitude`, `endurance_aptitude`
- Racecraft & strategy: `race_strategy`, `pit_entry_exit`, `traffic_management`, `qualifying_pace`, `race_pace`, `starting_skill`, `tyre_warming`, `energy_management`
- Environment: `wet_weather_skill`, `night_driving`, `heat_tolerance`, `cold_tolerance`, `altitude_adaptation`, `visibility_adaptation`, `surface_adaptation`
- Personal/social: `media_handling`, `sponsorship_appeal`, `fan_engagement`, `team_player`, `leadership`, `professionalism`
- Career stats & metadata: `career_wins`, `career_podiums`, `career_points`, `career_starts`, `career_dnf`, `seasons_active`, `single_seater_wins`, `touring_wins`, `rally_wins`, `street_wins`, `drag_wins`, `rallycross_wins`, `endurance_wins`, `biography`, `career_highlights`, `preferred_discipline`, `career_phase`, `current_team_id`, `previous_teams`, `contract_length`, `salary`, `form_trend`, `peak_performance_age`, `retirement_age`, `learning_rate`, `championship_titles`, `rookie_of_year_awards`, `fastest_laps`, `pole_positions`

---

## Culling Decision Table — usage, recommendation, effort, risk

This table summarises how attributes are actually used in the codebase (engine, overtaking, track physics, services, DB), and gives a clear recommended action to help you decide what to cull, merge, compute or keep.

- Attribute / Group: `raw_speed`

  - Usage: Core input to lap-time/push calculations across `realtime_race_engine.py`, `services/driver_attributes.py`, discipline weightings and ordering in DB queries.
  - Primary call sites: `realtime_race_engine.py`, `services/driver_attributes.py`, `database_manager.py` (ordering/filtering).
  - Recommendation: KEEP (persisted).
  - Rationale: High read frequency and used in sorting and many algorithms; cheap to persist and required for reporting.
  - Effort: Low. Risk: Low.
- Attribute / Group: `racecraft`

  - Usage: Used directly and inside overtaking formulas; influences attack/defend decisions and incident probability.
  - Primary call sites: `overtaking_system.py`, `realtime_race_engine.py`, discipline weightings.
  - Recommendation: KEEP (persisted) but introduce a computed `racecraft_rating` for UIs/aggregates.
  - Rationale: Semantically distinct from overtaking; widely referenced in core logic.
  - Effort: Low. Risk: Low.
- Attribute / Group: `overtaking`` go into racecraft

  - Usage: Primary contributor in overtaking probability and attacker logic in `overtaking_system.py` and `realtime_race_engine.py`.
  - Primary call sites: `overtaking_system.py`, `realtime_race_engine.py`, `services/driver_attributes.py`.
  - Recommendation: KEEP as separate persisted field (do NOT collapse into racecraft immediately). Consider later MERGE into a single `wheel_to_wheel` metric if you consolidate many small racecraft sub-attributes.
  - Rationale: Explicit weight coefficients rely on it; merging would require thorough retuning/testing of coefficients.
  - Effort: Medium if merging. Risk: Medium.
- Attribute / Group: `vehicle_control`, `cornering_skill`, `braking_technique`, `acceleration_control`, `suspension_feel `` Could go into racecraft and pace

  - Usage: Frequently combined in engine code and overtaking logic to compute handling/exit speeds and corner performance.
  - Primary call sites: `track_physics.py`, `overtaking_system.py`, `realtime_race_engine.py`.
  - Recommendation: PERSIST core fine-grained attributes for now, but add a computed `vehicle_handling` aggregate that other modules can consume; later merge less-used fields into `attributes_extra` if you need to reduce column count.
  - Rationale: Many formulas weight these differently; keeping them avoids risking regressions. Computed aggregate reduces code duplication and centralises tuning.
  - Effort: Low to add computed helper; High to remove columns. Risk: Low for compute, High for destructive schema changes.
- Attribute / Group: `tyre_warming`, `tire_management`` fo into tyres

  - Usage: Used in tyre / warmup logic and racing mode transitions; also referenced in GUI/strategy descriptions.
  - Primary call sites: `realtime_race_engine.py`, discipline docs.
  - Recommendation: MERGE conceptually into `tire_management` (persist one canonical field) or keep both but prefer `tire_management` as canonical and deprecate `tyre_warming` with a computed shim during transition.
  - Rationale: Overlap is semantic; consolidation is straightforward but requires search-and-replace/backfill.
  - Effort: Medium. Risk: Low.
- Attribute / Group: `engine_management`, `mechanical_sympathy`, `setup_knowledge`, `suspension_feel`, `aerodynamics_understanding`` car development

  - Usage: Technical knowledge / engine control used for long-term performance and pit/strategy choices; some used in pace calculations.
  - Primary call sites: `services/driver_attributes.py`, discipline weightings, `database_manager.py`.
  - Recommendation: KEEP but consider MERGE of conceptually overlapping attributes into two persisted fields: `technical_knowledge` (setup + aero + mech sympathy) and `engine_management` (driving-specific power modes). Or keep as-is and mark as lower-priority for culling.
  - Rationale: These are lower-frequency relative to raw_speed/overtaking, but useful for season progression and driver development.
  - Effort: Medium. Risk: Medium.
- Attribute / Group: `age`, `birth_date`

  - Usage: `birth_date` is persisted; `age` is persisted but can get out of sync. `age` appears in DB schema and manager inserts/loads.
  - Primary call sites: `database/models.py`, `database_manager.py`.
  - Recommendation: MOVE to computed property: persist `birth_date` only, compute `age` at runtime (avoid persisting `age`). Mark `age` for removal from schema on an eventual migration.
  - Rationale: Deterministic value; removing `age` saves redundancy and avoids stale data.
  - Effort: Low to implement compute shim; Medium to drop column. Risk: Low.
- Attribute / Group: `defensive_driving`, `spatial_awareness`, `pressure_handling`, `concentration`` racecraft

  - Usage: Inputs to defensive logic, collision avoidance, and stamina/consistency calculations.
  - Primary call sites: `overtaking_system.py`, `realtime_race_engine.py`.
  - Recommendation: KEEP persisted; add computed `defensive_rating` if you want a single UI field. Do not cull unless you consolidate multiple mental attributes into `mental_resilience` first.
  - Effort: Low. Risk: Low.
- Attribute / Group: `learning_rate`, `peak_performance_age`, `retirement_age`, `career_phase`` yeah these are ok

  - Usage: Used for progression modelling and career simulation, not per-frame engine code.
  - Primary call sites: planning/progression systems, docs, scripts.
  - Recommendation: KEEP (persisted) but move static metadata that is rarely updated into `attributes_extra` JSON if you need to reduce column count; these are safe to store elsewhere.
  - Effort: Low. Risk: Low.
- Career stats (career_wins, podiums, starts, dnf, discipline-specific wins)

+ - Usage: Aggregated results; should be derived from `race_results` and `driver_career_stats` aggregate table.
+ - Primary call sites: reporting, UI, save/load.
+ - Recommendation: MOVE out of core `drivers` table into a `driver_career_stats` aggregate table or compute on demand. Keep caching columns only if performance requires (but mark as derived and rebuildable).
+ - Rationale: Normalisation reduces update contention and size of driver row writes.
+ - Effort: Medium. Risk: Medium (requires migration/backfill).
+ 

+- Less-used / optional attributes (media_handling, sponsorship_appeal, fan_engagement, biography, career_highlights, previous_teams) - All these can go

+ - Usage: UI, docs, external presentation. `previous_teams` stored as JSON text.
+ - Recommendation: MOVE into `attributes_extra` JSON column or a `profile` table. Keep `biography`/`career_highlights` small text fields if they are used in the UI; move `previous_teams` to a history table if you need structured queries.
+ - Effort: Low. Risk: Low.
