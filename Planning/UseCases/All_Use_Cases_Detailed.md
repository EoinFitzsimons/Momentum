# Use Cases

## UC-1: Read Driver Details

### Scope

Retrieve a complete driver profile with 50+ attributes across 7 categories (technical, mental, physical, racecraft, personality, discipline preferences) from the SQLite database for race simulation initialisation.

### Description

The GUI or Simulation Service queries the database manager to retrieve a driver record containing all racing attributes, team assignment, and current status. The system returns the full driver object which is used to initialise the AI agent for real-time race simulation.

### Actors

- `GUI` - requests driver data for race setup screens and displays.
- `Simulation Service` - requests driver profiles for real-time race engine initialisation.
- `Database Manager` - executes SQL queries against the SQLite database and returns driver objects.

### Flow Description

#### Precondition

The system has loaded the database; driver records exist with complete attribute sets.

#### Activation

This use case starts when the GUI loads the race setup screen or when the Simulation Service initialises a race session.

#### Main flow

1. The GUI or Simulation Service calls `DatabaseManager.get_all_drivers()` or `get_driver(driver_id)`.
2. The Database Manager executes a `SELECT` query against the `drivers` table.
3. The system validates that driver records contain all required attributes (0-100 scale for skills).
4. The system returns `Driver` objects with full attribute payloads.
5. For race simulation, each driver is instantiated as an AI agent with decision-making capabilities.

#### Alternate flow

A1: Requested `driverId` does not exist - return `None` and GUI displays error message.
A2: Database file not found - GUI displays connection error and prompts database regeneration.

#### Exceptional flow

E1: Database read failure or corruption - GUI catches exception, logs to `logs/` directory, and displays user-friendly error with regeneration option.
E2: Missing or invalid attributes - Database Manager logs warning and uses default values (50.0) for missing skills.

#### Termination

Client receives driver objects and proceeds with race initialisation or display rendering.

### Use Case Diagram

## UC-2: Read Race Configuration

### Scope

Retrieve track information (175 circuits with IMA grading, surface types, characteristics) and race parameters from the SQLite database to configure the real-time race simulation engine.

### Description

The GUI and Simulation Service query track records containing length, surface type, corners, and IMA characteristics. The system loads this data to initialise the track map with 100 evenly-spaced checkpoints, corner types (slow/medium/fast), and DRS zones for the physics engine.

### Actors

- `GUI` - requests track data for race setup and displays circuit information.
- `Simulation Service` - loads track configuration to initialise the `TrackMap` and physics calculations.
- `Database Manager` - queries the `tracks` table and returns `Track` objects.

### Flow Description

#### Precondition

Database contains 175 circuit definitions imported from `data/circuits_database.json`.

#### Activation

Starts when the GUI loads the race setup screen and requests available tracks, or when the Simulation Service begins a race session.

#### Main flow

1. GUI calls `DatabaseManager.get_all_tracks()` or `get_track(track_id)`.
2. Database Manager executes `SELECT` query against the `tracks` table.
3. System returns `Track` objects containing name, length (km), country, surface type, and IMA grading.
4. For simulation, the engine generates a `TrackMap` with corner sections and racing physics parameters.
5. The circuit is rendered in the GUI with 100 checkpoint markers at 1% intervals.

#### Alternate flow

A1: Invalid `track_id` requested - return `None` and GUI displays error or fallback message.
A2: No tracks available in database - GUI prompts user to run `scripts/import_circuits.py` to populate track data.

#### Exceptional flow

E1: Database read error - GUI logs exception to `logs/database_generation.log` and displays connection error.
E2: Missing track characteristics - System uses default values (medium corners, standard grip) and logs warning.

#### Termination

Caller receives track configuration and proceeds to simulation or display rendering.

### Use Case Diagram

## UC-3: Create Race Result

### Scope

Capture race outcomes from the real-time simulation engine (positions, lap times, DNF reasons, incidents) and persist results to the SQLite database for historical tracking and future standings calculations.

### Description

The real-time race engine runs a physics simulation at 30 FPS where each driver is controlled by an AI decision-making agent. These agents process track conditions, competitor positions, and vehicle state to make strategic decisions (overtaking, defending, pit strategy) every frame. Upon race completion, the engine returns classification data including final positions, lap times, DNF status, and incident details. Results are validated and persisted to the database with atomic transactions.

### Actors

- `Real-time Race Engine` - executes race simulation and generates position updates every frame (30 FPS).
- `GUI` - receives race results and displays final classification to the user.
- `Database Manager` - persists race results to the `race_results` table (planned feature).

### Flow Description

#### Precondition

Race simulation has been initialised with drivers, teams, and track configuration; simulation is running or has completed.

#### Activation

Starts when the race simulation completes all laps or is terminated early via the stop button.

#### Main flow

1. The Real-time Race Engine completes the simulation loop and generates final classification.
2. Engine returns a list of `RaceResult` objects containing driver ID, position, laps completed, best lap time, total time, and DNF reason if applicable.
3. GUI receives the `race_finished` event with results payload.
4. System validates that all drivers are accounted for and positions are sequential.
5. (Planned) Database Manager persists results using `INSERT INTO race_results` within a transaction.
6. GUI displays final standings table with positions, times, and gaps.

#### Alternate flow

A1: Race stopped early by user - engine returns partial results with current positions and marks race as incomplete.
A2: All drivers DNF - return valid results with DNF status for all participants and log reason distribution.

#### Exceptional flow

E1: Database write failure during persistence - log error to `logs/` directory, display results in GUI but warn that they were not saved.
E2: Results validation failure (missing drivers, duplicate positions) - log detailed diagnostic and display what data is available.

#### Termination

Race results displayed in GUI standings table; system ready for next race or user action.

### Use Case Diagram

## UC-4: Read Race Results

### Scope

Retrieve historical race results from the database for display in the GUI, including final classification, lap times, and DNF information.

### Description

The system queries completed race records to display historical results. Results include finishing positions, lap times, DNF reasons, and incident details for analysis and comparison.

### Actors

- `GUI` - requests and displays historical race results.
- `Database Manager` - queries the `race_results` table and joins with driver/team data.

### Flow Description

#### Precondition

Race results have been persisted to the database from previous simulations.

#### Activation

Starts when user navigates to race history screen or requests results for a specific event.

#### Main flow

1. GUI calls `DatabaseManager.get_race_results(race_id)` or `get_championship_results(championship_id)`.
2. Database Manager executes `SELECT` query joining `race_results`, `drivers`, and `teams` tables.
3. System returns ordered list of results with driver names, positions, times, and DNF reasons.
4. GUI displays results in standings table format.

#### Alternate flow

A1: No results found for requested race - GUI displays "No results available" message.
A2: Partial results due to incomplete race - GUI displays available data and marks as "Race Incomplete".

#### Exceptional flow

E1: Database read failure - GUI logs error and displays cached results if available from previous session.
E2: Corrupt result data - System logs validation errors and displays partial data with warning.

#### Termination

GUI displays historical results and awaits user navigation.

### Use Case Diagram

## UC-5: Read Championship Details

### Scope

Retrieve championship information including season parameters, calendar of events, current standings, and points allocations across 7 racing disciplines.

### Description

The system maintains championship records tracking season-long competitions. Each championship contains a calendar of races, points standings, and discipline-specific rules for the simulation.

### Actors

- `GUI` - displays championship standings, calendar, and season progress.
- `Game Loop` - manages season progression and championship state (planned feature).
- `Database Manager` - queries championship, standings, and calendar data.

### Flow Description

#### Precondition

Championship has been created with discipline, season year, and initial calendar.

#### Activation

Starts when user navigates to championship screen or game loop initialises a season.

#### Main flow

1. GUI or Game Loop requests championship data via `DatabaseManager.get_championship(championship_id)`.
2. System retrieves championship metadata (discipline, year, points system).
3. System queries calendar entries and aggregates standings from race results.
4. GUI displays championship overview with standings table and upcoming races.

#### Alternate flow

A1: Championship has no races yet - display empty calendar with option to schedule events.
A2: Standings unavailable - calculate standings from existing race results or display zero points.

#### Exceptional flow

E1: Database query failure - GUI displays error and offers retry or cached data.
E2: Invalid championship structure - System logs diagnostic and prompts database verification.

#### Termination

GUI displays championship view with standings and calendar; system awaits user interaction.

### Use Case Diagram

## UC-6: Update Championship Standings

### Scope

Recalculate and persist championship standings after results are recorded.

### Description

### Actors

- `Standings Service` - triggers recalculation and consumes updated standings.
- `Admin` - may invoke recalculation manually.

### Flow Description

#### Precondition

Championship and results exist.

#### Activation

Starts when results are created or adjusted.

#### Main flow

1. Gather results for the championship.
2. Apply points system and compute standings.
3. Persist updated standings and notify consumers.

#### Alternate flow

A1: Partial update requested - return `202 Accepted` with job id for async completion.
A2: Concurrent updates - return `409 Conflict` with current version.

#### Exceptional flow

E1: Points rules missing - return `500` and log for admin attention.
E2: Persistence error - roll back and queue retry.

#### Termination

Standings persisted.

### Use Case Diagram

## UC-7: Create Race Event

### Scope

Add a race event to a championship calendar (track, date, configuration).

### Description

An admin or scheduler submits an event; the backend validates and persists the event record.

### Actors

- `Admin` - creates and manages race events.
- `Scheduler` - schedules events programmatically.

### Flow Description

#### Precondition

Championship exists and is editable.

#### Activation

Starts when an admin posts new event details.

#### Main flow

1. Validate dates and track availability.
2. Insert event record into `races`.
3. Return created resource.

#### Alternate flow

A1: Date/track conflict - return `409 Conflict` with conflicts and alternatives.
A2: Validation warning - return `200` with `warnings` and allow override.

#### Exceptional flow

E1: Database write failure - return `500` and persist request to retry queue.
E2: External sync failure - create event in draft and return `202 Accepted` with sync pending.

#### Termination

Calendar updated; notifications may be sent.

### Use Case Diagram

## UC-8: Read Race Schedule

### Scope

Retrieve championship calendar/schedule for UI display.

### Description

Return ordered list of events with dates, tracks and statuses.

### Actors

- `User / UI` - requests the schedule for display.
- `Calendar Service` - synchronises events externally when configured.

### Flow Description

#### Precondition

Championship or season exists.

#### Activation

Starts when client opens the calendar screen.

#### Main flow

1. Validate championship/season.
2. Retrieve ordered events and metadata.
3. Return schedule to caller.

#### Alternate flow

A1: Championship not found - return `404 Not Found` with guidance to create a championship first.
A2: Championship exists but has no events - return empty schedule with a message suggesting adding events.

#### Exceptional flow

E1: Database read error - return `503 Service Unavailable` with diagnostic id; offer cached schedule if available.
E2: Permission or tenancy error - return `403`.

#### Termination

Client displays schedule.

#### Post condition

System awaits next request.

### Use Case Diagram

## UC-9: Update Race Status

### Scope

Change a race event status (scheduled → in-progress → completed → cancelled).

### Description

Update event lifecycle state and notify dependent systems.

### Actors

- `Simulation/Service` - updates status during simulation.
- `Admin` - may manually change status.
- `Notification Service` - receives lifecycle events.

### Flow Description

#### Precondition

Event exists and caller has permission.

#### Activation

Starts when a service or admin posts a status update.

#### Main flow

1. Validate transition is allowed.
2. Update `races.status` accordingly.
3. Emit notifications/events.

#### Alternate flow

A1: Invalid lifecycle transition (e.g., completed → scheduled) - return `400 Bad Request` with allowed transitions and current state.
A2: Caller requests cancellation during in-progress - return `202 Accepted` and initiate graceful abort procedures (safety checks, rollback attempts).

#### Exceptional flow

E1: Database write error or optimistic lock fail - return `500` and include current event state; schedule a background reconciliation job.
E2: Notification subsystem failure - update status but record notification failure for later retry; return `200` with `notificationsPending: true`.

#### Termination

Event status updated and notifications sent.

#### Post condition

System awaits next lifecycle event.

### Use Case Diagram

## UC-10: Create Championship

### Scope

Create a new championship/season automatically on season rollover, with base rules and an empty calendar.

### Description

On season rollover the Game Loop computes the next season parameters, instantiates a championship record with a ruleset and calendar placeholder, persists it, and notifies downstream systems (scheduling, AI, UI) that a new season is available.

### Actors

- `Game Loop / Scheduler` - triggers automatic season rollover and championship creation.
- `Policy Service` - validates or supplies rulesets.
- `Event Scheduler` - consumes the new championship to populate events.

### Flow Description

#### Precondition

End-of-season tick reached; ruleset templates and calendar seeding configuration are available.

#### Activation

Triggered automatically by the `Game Loop` on season rollover (no manual admin intervention required).

#### Main flow

1. Game Loop determines season rollover has occurred and computes seed parameters (year, discipline, ruleset template).
2. System requests/validates the ruleset from `Policy Service`.
3. System creates the championship record with initial metadata and an empty calendar.
4. System persists the championship atomically and emits events to `Event Scheduler`, `AI` and `UI`.

#### Alternate flow

A1: Ruleset validation fails - select fallback template and continue, or mark championship as `requiresReview` and emit admin notification.

#### Exceptional flow

E1: Database write failure - rollback and schedule a retry; emit diagnostic id to monitoring and place a recovery job in the maintenance queue.

#### Termination

Championship record created and downstream systems notified.

#### Post condition

Event Scheduler and AI begin populating events and participants for the new season.

### Use Case Diagram

## UC-11: Read Team Details

### Scope

Retrieve complete team profile including budget (€130M cap for top-tier Single Seater), tier classification, headquarters, discipline specialisation, and assigned drivers.

### Description

The system maintains 1,095 team records across 7 racing disciplines. Each team has budget constraints, tier classification (tier1/tier2/tier3), and performance multipliers that affect simulation outcomes.

### Actors

- `GUI` - displays team information on management screens.
- `Simulation Service` - requests team data to calculate performance multipliers for race simulation.
- `Database Manager` - queries the `teams` table and joins with driver assignments.

### Flow Description

#### Precondition

Team records exist in database with complete attribute sets.

#### Activation

Starts when GUI loads team management screen or simulation engine initialises a race.

#### Main flow

1. GUI or Simulation Service calls `DatabaseManager.get_team(team_id)` or `get_teams_by_discipline(discipline)`.
2. Database Manager executes `SELECT` query against `teams` table.
3. System retrieves team metadata including budget, tier, headquarters, and discipline.
4. For simulation, engine calculates team performance multiplier (0.55 to 0.95) based on tier and budget.
5. GUI displays team profile or simulation applies multipliers to driver performance.

#### Alternate flow

A1: Invalid `team_id` - return `None` and GUI displays "Team not found" error.
A2: Team has no assigned drivers - display team info with empty roster.

#### Exceptional flow

E1: Database read failure - GUI logs error to `logs/` and displays connection error with retry option.
E2: Missing team attributes - System uses default values (tier2, €100M budget) and logs warning.

#### Termination

GUI displays team screen or simulation proceeds with team performance calculations.

#### Post condition

System awaits next team query or user action.

### Use Case Diagram

## UC-12: Create New Team

### Scope

Create a new team record (initial roster, budget, HQ).

### Description

Player or admin creates a team; the system allocates starting assets or placeholders.

### Actors

- `Player/Admin` - initiates team creation.
- `Provisioning Service` - reserves starting resources.

### Flow Description

#### Precondition

Requester authorised; required seed data available.

#### Activation

Starts when player/admin submits team creation.

#### Main flow

1. Validate request and reserve resources.
2. Insert team record and assign initial roster/placeholders.
3. Return created team.

#### Alternate flow

A1: Resource conflict (e.g., team name or HQ occupied) - return `409 Conflict` with suggested alternatives and actions to resolve.
A2: Missing seed data - return `422 Unprocessable Entity` with details on required fields.

#### Exceptional flow

E1: Database transaction failure - return `500` and log the full request for replay.
E2: External provisioning failure (e.g., storage) - create the team in `pending` state and notify admin.

#### Termination

Team visible in lists.

#### Post condition

System awaits next management action.

### Use Case Diagram

## UC-13: Read Team Details (player team)

### Scope

Return player's own team with editable flags and affordances.

### Description

Provide editable team data for the player's management screen.

### Actors

- `Player` - owner of the team and primary editor.
- `Auth Service` - validates ownership and permissions.

### Flow Description

#### Precondition

Player has a team.

#### Activation

Starts when player opens their team management screen.

#### Main flow

1. Validate player's identity and team ownership.
2. Return team data with editable flags.

#### Alternate flow

A1: Player has no team - return `404 Not Found` with guidance to create or join a team and links to relevant endpoints.

#### Exceptional flow

E1: Database read error - return `503 Service Unavailable` and include a diagnostic id.
E2: Authorization check failure - return `403`.

#### Termination

Player views editable team screen.

#### Post condition

System awaits further edits.

### Use Case Diagram

## UC-14: Update Team Attributes

### Scope

Modify team attributes (budget allocation, HQ upgrades, staff assignments).

### Description

Player or admin updates team settings which are validated and persisted.

### Actors

- `Player/Admin` - submits updates.
- `Finance Service` - validates budget changes.

### Flow Description

#### Precondition

Requester authorised and has sufficient resources.

#### Activation

Starts when client submits team updates.

#### Main flow

1. Validate changes and budget.
2. Persist updates.
3. Return updated resource.

#### Alternate flow

A1: Insufficient funds detected - return `422 Unprocessable Entity` with required amount and suggestions (sponsor, loan, reduce spend).
A2: Concurrent update to budget - return `409 Conflict` with current balance and retry instructions.

#### Exceptional flow

E1: Database write/commit failure - return `500` and enqueue the update for manual reconciliation.
E2: Audit/logging service failure - persist the change but flag audit missing; return `200` with `auditPending: true`.

#### Termination

Changes reflected on subsequent reads.

#### Post condition

System awaits next request.

### Use Case Diagram

## UC-15: Read Available Drivers

### Scope

Return list of uncontracted or transfer-available drivers for recruitment.

### Description

Provide filtered and paginated driver pool for the market UI.

### Actors

- `Player` - browses and filters available drivers.
- `Team AI` - automated consumer of driver listings.

### Flow Description

#### Precondition

Driver pool exists.

#### Activation

Starts when user opens driver market.

#### Main flow

1. Apply filters/pagination.
2. Return driver list with availability flags.

#### Alternate flow

A1: Filter parameters return no matches - return `200 OK` with empty list and suggestions to relax filters.
A2: Partial data due to pagination limits - include `hasMore: true` and next-page token.

#### Exceptional flow

E1: Database query failure - return `503 Service Unavailable` with diagnostic id; if cached pool exists return cached results marked `stale: true`.
E2: Indexing/search service failure - fall back to simple DB query and note reduced fidelity.

#### Termination

Client displays candidate drivers.

#### Post condition

System awaits next query.

### Use Case Diagram

## UC-16: Update Driver Contract

### Scope

Sign, renew or terminate driver contracts and update team roster and budget.

### Description

Persist contract terms and adjust availability and team budgets.

### Actors

- `Team Manager` - negotiates and confirms driver contracts.
- `Admin` - enforces or modifies contract rules when required.

### Flow Description

#### Precondition

Driver and team exist; negotiation outcome determined.

#### Activation

Starts when contract terms are finalised and submitted.

#### Main flow

1. Validate budget and contract rules.
2. Persist contract and update roster/budget.
3. Return confirmation.

#### Alternate flow

A1: Budget shortfall during contract update - return `422` with required funding and options (defer, partial contract, renegotiate).
A2: Contract already signed by another party - return `409 Conflict` with current contract details.

#### Exceptional flow

E1: Database write error - rollback, return `500` and include reference id for support.
E2: Payment gateway or external finance service failure - abort contract update, return `502 Bad Gateway` and queue retry.

#### Termination

Driver assigned and availability updated.

#### Post condition

System awaits next contract action.

### Use Case Diagram

## UC-17: Read Available Staff

### Scope

Return list of available staff for hiring with roles and modifiers.

### Description

Provide paginated staff pool for recruitment screens.

### Actors

- `Player` - requests staff listings.
- `HR Service` - provides staff filters and pools.

### Flow Description

#### Precondition

Staff pool exists.

#### Activation

Starts when player opens staff hiring screen.

#### Main flow

1. Apply filters and paginate.
2. Return staff list with core stats and cost.

#### Alternate flow

A1: No staff matching filters - return `200 OK` with empty list and filter suggestions.
A2: Partial availability (some staff on contract) - return available subset with `availability: limited` flag.

#### Exceptional flow

E1: Database or search index failure - return `503 Service Unavailable` and provide cached results if available.
E2: Data corruption in staff records detected - return `500` and set a maintenance flag.

#### Termination

Client displays staff candidates.

#### Post condition

System awaits next request.

### Use Case Diagram

## UC-18: Update Staff Contract

### Scope

Hire, fire or renegotiate staff contracts and persist changes to team resources.

### Description

Assign staff to teams, record salary and update budgets.

### Actors

- `Player` - initiates hiring/renegotiation.
- `Team Manager` - manages staff assignments.

### Flow Description

#### Precondition

Staff profile exists and is available.

#### Activation

Starts when hiring/renegotiation action is confirmed.

#### Main flow

1. Validate terms and budget.
2. Persist contract and update team state.
3. Return confirmation.

#### Alternate flow

A1: Insufficient funds - return `422 Unprocessable Entity` with required funding detail and rollback any provisional assignments.
A2: Candidate no longer available at confirmation - return `409 Conflict` and provide alternatives.

#### Exceptional flow

E1: Database write failure - rollback and return `500` with support reference.
E2: Concurrent contract update detected - return `409` with current contract state and instructions to retry.

#### Termination

Staff assigned and salary deducted from budget.

#### Post condition

System awaits further HR actions.

### Use Case Diagram

## UC-19: Update Driver Skills/Age

### Scope

Periodic update of driver attributes (ageing, progression/regression) and handle retirements/recycling.

### Description

Perform end-of-season or scheduled updates to driver skills and ages; mark retirees and optionally regenerate/recycle entities.

### Actors

- `Scheduler` (Game Loop) - triggers seasonal maintenance jobs.
- `Admin` - may invoke manual progression runs.

### Flow Description

#### Precondition

Driver population present.

#### Activation

Starts at season end or scheduled tick.

#### Main flow

1. System iterates drivers and adjusts skills and ages.
2. Flag retired drivers and recycle or replace per policy.
3. Persist updates.

#### Alternate flow

A1: Emergency update due to injury or incident - apply immediate decrement to affected driver(s), mark as `underReview`, and notify teams.
A2: Player-triggered training boost - apply progression rules and mark a cooldown period.

#### Exceptional flow

E1: Batch update failure during season tick - return `500`, log affected driver ids and schedule a retry job.
E2: Constraint violation (e.g., negative attribute) - abort update for affected records and flag for manual review.

#### Termination

Driver records updated for next season.

#### Post condition

System awaits next scheduled update.

### Use Case Diagram

## UC-20: Update Team Budget

### Scope

Adjust team budget for income/expenses, sponsor payouts and race fees.

### Description

Apply transactions affecting a team's budget and persist them.

### Actors

- `Finance System` - posts transactions affecting team budgets.
- `Game Loop` - triggers periodic income/expense events.

### Flow Description

#### Precondition

Team exists.

#### Activation

Starts when a transaction affecting budget occurs.

#### Main flow

1. Validate transaction and atomicity.
2. Update team budget.
3. Return updated balance.

#### Alternate flow

A1: Insufficient funds for debit - reject the transaction with `402 Payment Required` (or `422`) and suggest corrective actions (sponsor, loan, adjust expenses).
A2: Pending transactions that affect available balance - return `409 Conflict` with pending transaction list.

#### Exceptional flow

E1: Database write failure - return `500` and enqueue transaction for replay.

#### Termination

Team budget updated and awaiting next transaction.

### Use Case Diagram

## UC-21: Create New Driver

### Scope

Add a driver to the hireable pool by recycling an existing placeholder or generating a new driver profile when pool thresholds require expansion.

### Description

Maintain and expand the hireable driver pool to support roster growth, replacement of retired drivers, and content variety. The system prefers recycling deactivated driver records when suitable; otherwise the Generator Service creates a new driver profile validated against uniqueness and configured policy constraints.

### Actors

- `Admin` - requests manual creation.
- `System` - scheduled or policy-driven generator.
- `Generator Service` - produces seeded attribute payloads for new drivers.

### Flow Description

#### Precondition

Driver pool is below configured threshold or an explicit admin request to create a driver is received; seeding and generation configuration are available.

#### Activation

Triggered by `POST /api/drivers/generate` from an admin or by an automated roster expansion job.

#### Main flow

1. Validate request and policy constraints (pool thresholds, allowed classes).
2. Attempt to select a recycle candidate from the deactivated pool; if none available, call `Generator Service` to create attributes.
3. Validate generated attributes (unique name, valid age, discipline suitability).
4. Persist the driver record inside a transaction and mark availability.
5. Return `201 Created` with the driver resource.

#### Alternate flow

A1: Recycle candidate unavailable - generate new attributes and continue.
A2: Minor validation warnings - persist with a `warnings` field and return `201 Created`.
A3: Name or identity conflict - mutate the attribute (rename) and retry up to configured attempts; on exhaustion return `409 Conflict` with guidance.

#### Exceptional flow

E1: Database write failure - rollback and return `500` with diagnostic id for support.
E2: Generator Service unavailable - return `503 Service Unavailable` and schedule a retry job.
E3: Policy or configuration violation - return `422 Unprocessable Entity` with policy details.

#### Termination

Driver record created and visible in the hireable pool.

#### Post condition

Driver returned in subsequent listing endpoints and system awaits next generation task.

### Use Case Diagram

## UC-22: Create New Staff Member (staff generation)

### Scope

Generate new staff when required (optional).

### Description

Create or recycle staff records for hireable pool expansion.

### Actors

- `Admin/System` - triggers staff generation or pool maintenance.

### Flow Description

#### Precondition

Staff pool needs expansion.

#### Activation

Triggered by admin or scheduled regeneration.

#### Main flow

1. Generate staff attributes and persist.
2. Return created staff record.

#### Alternate flow

A1: Attribute conflict or duplicate identity - alter generated attributes (name, hometown) and retry generation automatically.
A2: Pool constraints prevent generation - return `422` with explanation (e.g., max drivers reached).

#### Exceptional flow

E1: Database write failure - return `500` and record the attempted generation for retry.
E2: Resource exhaustion (temp files, quota) - return `503` and back off generation.

#### Termination

Staff visible in hiring pool.

#### Post condition

System awaits next generation.

### Use Case Diagram

## UC-23: Delete Championship

### Scope

Remove or archive a championship (admin only).

### Description

Delete or archive championship and related resources according to retention policy.

### Actors

- `Admin` - authorised to delete or archive championships.

### Flow Description

#### Precondition

Admin authorised and backup policy confirmed.

#### Activation

Starts when admin confirms deletion.

#### Main flow

1. Perform integrity checks.
2. Delete or archive resources.
3. Return confirmation.

#### Alternate flow

A1: Referential integrity prevents deletion - return `409 Conflict` with list of dependent resources and suggested cleanup steps.
A2: Admin chooses archive instead of delete - archive resources and return `200 OK` with `archived: true` flag.

#### Exceptional flow

E1: Database cascade failure - return `500` and halt operation; create a rollback plan and notify admin.
E2: Backup/restore service failure during deletion - abort and recommend manual intervention.

#### Termination

Championship removed or archived.

#### Post condition

System awaits next admin action.

### Use Case Diagram

## UC-24: Create Custom Track

### Scope

Add a custom track with characteristics for use in events.

### Description

Designer or admin submits track metadata and layout which becomes available for events.

### Actors

- `Designer/Admin` - submits track definitions and layout files.

### Flow Description

#### Precondition

Creator authorised.

#### Activation

Starts when track creation form is submitted.

#### Main flow

1. Validate track data.
2. Insert track record.
3. Return created track resource.

#### Alternate flow

A1: Invalid or incomplete track layout submitted - return `400 Bad Request` with field-level errors and validation hints.
A2: Duplicate track name or coordinates - return `409 Conflict` with resolution options.

#### Exceptional flow

E1: Database write failure - return `500` and log the payload for manual replay.
E2: Geometry parsing failure - return `422 Unprocessable Entity` with parsing error details.

#### Termination

Track available for event creation.

#### Post condition

System awaits next track management action.

### Use Case Diagram

## UC-25: Update Track Characteristics

### Scope

Modify track parameters (surface, length, grip) for balancing.

### Description

Admin updates track metadata and future events use revised parameters.

### Actors

- `Admin` - submits track updates.

### Flow Description

#### Precondition

Track exists and is editable.

#### Activation

Starts when admin submits updates.

#### Main flow

1. Validate and persist updates.
2. Return updated resource.

#### Alternate flow

A1: Track is scheduled in upcoming events - return `409 Conflict` and offer `archive` or `force` options with explicit confirmation.
A2: Minor characteristic change allowed - apply change with `warnings` indicating affected events.

#### Exceptional flow

E1: Database write failure - return `500` and queue the request for admin review.
E2: Constraint violation due to dependent events - return `409` and detail the blocking events.

#### Termination

Track updated for future events.

#### Post condition

System awaits next management action.

### Use Case Diagram

## UC-26: Delete Track

### Scope

Remove custom or unused tracks with checks for scheduled use.

### Description

Admin removes track or archives it if scheduled in future.

### Actors

- `Admin` - initiates deletion or archiving of tracks.

### Flow Description

#### Precondition

Admin confirmed deletion policy.

#### Activation

Starts when deletion requested.

#### Main flow

1. Check for scheduled events.
2. If none, delete; else archive or return `409`.

#### Alternate flow

A1: Track has scheduled events - automatically archive and return `200 OK` with `archived: true` when admin confirms, or return `409` if admin cancels.

#### Exceptional flow

E1: DB transaction failure during delete/archive - return `500` and log for manual reconciliation.
E2: File storage deletion error (assets) - mark record archived and flag cleanup pending.

#### Termination

Track removed or archived.

#### Post condition

System awaits further track management.

### Use Case Diagram

## UC-27: Read Staff Performance Modifiers

### Scope

Return computed staff modifiers used by the simulation for team performance.

### Description

Provide staff-based modifiers (mechanic efficiency, strategist value) to the Simulation Service.

### Actors

- `Simulation Service` - requests computed modifiers for a team.

### Flow Description

#### Precondition

Staff members assigned or available.

#### Activation

Starts when simulation requests modifiers for a team.

#### Main flow

1. Aggregate staff attributes for team.
2. Return modifier set to simulator.

#### Alternate flow

A1: Missing or partial staff assignments - return default modifiers and mark `incomplete: true` in response.
A2: Requested team has no staff assigned - return `200 OK` with defaults and a recommendation to hire staff for full modifiers.

#### Exceptional flow

E1: Database read failure - return `503 Service Unavailable` and include diagnostic id.
E2: Aggregation error while computing modifiers - return `500` and provide fallback default values.

#### Termination

Simulation applies modifiers.

#### Post condition

System awaits next modifier request.

### Use Case Diagram

## UC-28: Update Driver Appearance

### Scope

Change cosmetic appearance for a driver (helmet, livery) - non-gameplay affecting.

### Description

Player edits and saves driver appearance assets which are stored and served to UI.

### Actors

- `Player` - creates or edits appearance assets.
- `Storage Service` - stores and serves asset files.

### Flow Description

#### Precondition

Player owns or is authorised to edit driver appearance.

#### Activation

Starts when player submits appearance changes.

#### Main flow

1. Validate assets.
2. Persist appearance metadata and files.
3. Return confirmation.

#### Alternate flow

A1: Invalid asset format or too large - return `400 Bad Request` with accepted formats and size limits.
A2: Asset conflicts (same filename) - return `409 Conflict` and provide renaming options.

#### Exceptional flow

E1: File storage error (S3/local) - return `500` and queue asset upload for retry; return a reference id to the client.
E2: Virus/validation rejection - return `422 Unprocessable Entity` with reason.

#### Termination

Appearance updated for reads.

#### Post condition

System awaits further edits.

### Use Case Diagram

## UC-29: Update Team Branding

### Scope

Update team visual branding assets and metadata (logos, colours).

### Description

Player or admin uploads branding assets and updates team metadata for display in UI.

### Actors

- `Player/Admin` - uploads branding assets.
- `Storage/DB` - stores branding files and metadata.

### Flow Description

#### Precondition

Requester authorised; assets valid.

#### Activation

Starts when branding upload is submitted.

#### Main flow

1. Validate assets and metadata.
2. Persist files and update team record.
3. Return confirmation.

#### Alternate flow

A1: Invalid branding assets - return `400 Bad Request` with clear validation errors and accepted file types.
A2: Asset name conflicts - return `409 Conflict` with suggested renames.

#### Exceptional flow

E1: File store or DB failure - return `500` and persist metadata change to a pending queue.
E2: Permission or quota error - return `403` or `429` as appropriate with remediation steps.

#### Termination

Branding served to UI.

#### Post condition

System awaits next update.

### Use Case Diagram
