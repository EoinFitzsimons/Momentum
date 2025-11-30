# Use Cases

## UC-1: Read Driver Details

### Scope

Provide the simulation service with a complete driver profile and runtime status required to instantiate the driver in a race simulation.

### Description

How the game backend returns a driver's attributes, contract/team association and runtime state (injury/fatigue/availability) so the Simulation Service can include the driver in race initialisation and performance calculations.

### Actors

- `Simulation Service` — requests driver payloads for simulation initialisation.
- `Drivers DB` — stores driver records and runtime state.

### Use Case Diagram

### Flow Description

#### Precondition

The system is in initialisation mode for a race; the driver record exists and the driver is eligible for selection.

#### Activation

This use case starts when the Simulation Service requests a driver's data for race setup.

#### Main flow

The system identifies the requested `driverId` and validates its format.

1. The Simulation Service requests the driver's profile from the backend (see A1).
2. The system retrieves the driver record and runtime state from the database (see E1).
3. The system returns the payload and initialises the driver object for the race.

#### Alternate flow

A1: Requested `driverId` invalid — return `400 Bad Request` with validation errors.
A2: Driver is ineligible (injured/unavailable) — return `409 Conflict` with status and reason.

#### Exceptional flow

E1: Database read failure — return `503 Service Unavailable` and include diagnostic id.
E2: Deserialization or payload assembly failure — return `500` and include error reference.

#### Termination

Caller receives payload; simulation proceeds to instantiate driver.



## UC-2: Read Race Configuration

### Scope

Provide race configuration (track, weather, lap count, ruleset) to the Simulation Service and clients.

### Description

The backend returns the configuration used for a given event so the Simulation Service and UI prepare appropriate settings.

### Actors

- `Simulation Service` - consumes configuration for simulations.
- `Client UI` - displays configuration to users.

### Use Case Diagram

### Flow Description

#### Precondition

Race configuration exists for the requested event.

#### Activation

Starts when a client or the Simulation Service requests event configuration.

#### Main flow

1. The caller requests configuration for an `eventId`.
2. The system validates `eventId`, fetches track, laps, weather and ruleset, and returns the configuration.

#### Alternate flow

A1: Invalid `eventId` - return `400` with validation errors.
A2: Partial configuration - return available fields with `partial: true` and a warning flag.

#### Exceptional flow

E1: Database read error or connection timeout - return `503 Service Unavailable`.
E2: Permission denied - return `403 Forbidden`.

#### Termination

Caller proceeds to initialisation.



## UC-3: Create Race Result

### Scope

Persist race outcomes (positions, times, incidents) and trigger standings updates.

### Description

The Simulation Service posts generated race results; the backend validates and persists results, marks the event complete and enqueues standings recalculation.

### Actors

- `Simulation Service` - submits generated race results.
- `Standings Service` - recalculates standings from persisted results.

### Use Case Diagram

### Flow Description

#### Precondition

Race event exists and is writable.

#### Activation

Starts when the simulation finishes or an operator submits results.

#### Main flow

1. The Simulation Service submits the result payload.
2. The system validates the payload and event state, stores `race_results` in a transaction, and marks the event complete.
3. The system enqueues a standings recalculation job and returns acknowledgement.

#### Alternate flow

A1: Validation failure - return `400` with field-level errors.
A2: Event already finalised - return `409 Conflict` and provide adjustment options.

#### Exceptional flow

E1: Database write failure - rollback and return `500`.
E2: Partial persistence detected - return `500` with reference id and queue reconciliation.

#### Termination

Event status updated; standings update job queued.



## UC-4: Read Race Results

### Scope

Return stored race results for display and historical access.

### Description

Provide classification, lap and penalty data for completed events.

### Actors

- `Client UI` - requests and displays results.
- `Reporting Service` - consumes results for summaries.

### Use Case Diagram

### Flow Description

#### Precondition

Results exist for the requested event.

#### Activation

Starts when client requests results by `eventId`.

#### Main flow

1. Validate `eventId`.
2. Retrieve classification and related data.
3. Return results to caller.

#### Alternate flow

A1: No results found - return `404 Not Found`.
A2: Provisional results - return `provisional: true` with timestamp.

#### Exceptional flow

E1: Database read failure - return `503` and optionally a cached snapshot.
E2: Deserialization error - return `500` with error reference.

#### Termination

Client displays results.



## UC-5: Read Championship Details

### Scope

Return championship metadata, calendar and standings snapshot.

### Description

Aggregate championship name, discipline, calendar and current standings for UIs and services.

### Actors

- `Client UI` - displays championship metadata and standings.
- `Analytics` - consumes standings for reports.

### Use Case Diagram

### Flow Description

#### Precondition

Championship exists.

#### Activation

Starts when client requests championship details.

#### Main flow

1. Validate `championshipId`.
2. Aggregate metadata, calendar and standings.
3. Return combined payload.

#### Alternate flow

A1: Championship archived - return `readOnly: true` and archive date.
A2: Partial standings - return `partial: true` and link to computation job.

#### Exceptional flow

E1: DB query timeout - return `503` with diagnostic id.
E2: Permission denied - return `403`.

#### Termination

Client displays championship view.



## UC-6: Update Championship Standings

### Scope

Recalculate and persist championship standings after results are recorded.

### Description

Gather results and apply the championship points rules to compute and persist standings.

### Actors

- `Standings Service` - triggers recalculation and consumes updated standings.
- `Admin` - may invoke recalculation manually.

### Use Case Diagram

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



## UC-7: Create Race Event

### Scope

Add a race event to a championship calendar (track, date, configuration).

### Description

An admin or scheduler submits an event; the backend validates and persists the event record.

### Actors

- `Admin` - creates and manages race events.
- `Scheduler` - schedules events programmatically.

### Use Case Diagram

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



### UC-8: Read Race Schedule

### Scope

Retrieve championship calendar/schedule for UI display.

### Description

Return ordered list of events with dates, tracks and statuses.

### Actors

- `User / UI` - requests the schedule for display.
- `Calendar Service` - synchronises events externally when configured.

### Use Case Diagram

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



### UC-9: Update Race Status

### Scope

Change a race event status (scheduled → in-progress → completed → cancelled).

### Description

Update event lifecycle state and notify dependent systems.

### Actors

- `Simulation/Service` - updates status during simulation.
- `Admin` - may manually change status.
- `Notification Service` - receives lifecycle events.

### Use Case Diagram

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



### UC-10: Create Championship

### Scope

Create a new championship/season with base rules and empty calendar.

### Description

Admin creates a championship record which can then accept events and teams.

### Actors

- `Admin` - creates and configures championships.
- `Policy Service` - validates rulesets.

### Use Case Diagram

### Flow Description

#### Precondition

Requester has permission to create championships.

#### Activation

Starts when admin submits championship definition.

#### Main flow

1. Validate rules and uniqueness of name.
2. Insert championship record.
3. Return created resource.

#### Alternate flow

A1: Rules validation failure - return `400 Bad Request` with rule-level errors; admin corrects and resubmits.
A2: Name conflict - return `409 Conflict` with existing championship id; provide option to rename.

#### Exceptional flow

E1: Database persistence failure - return `500` and write the request to an audit log for manual replay.
E2: Background task creation failure (e.g., scheduling post-creation jobs) - return `201 Created` but include `jobsPending: true`.

#### Termination

Championship available for events.

#### Post condition

System awaits further management operations.



### UC-11: Read Team Details

### Scope

Return full team profile for team screen (budget, staff, vehicles, drivers).

### Description

Provide aggregated team information for display or simulation.

### Actors

- `Player / UI` - views team details.
- `Simulation Service` - requests team data for simulation.

### Use Case Diagram

### Flow Description

#### Precondition

Team exists.

#### Activation

Starts when client requests team by id.

#### Main flow

1. Validate `teamId`.
2. Retrieve roster, staff and financials.
3. Return payload.

#### Alternate flow

A1: Team is private or restricted - return `403 Forbidden` with guidance on access requirements.
A2: Partial data due to missing financials - return available roster and staff but mark `financials: unavailable`.

#### Exceptional flow

E1: Database read timeout - return `503 Service Unavailable` and a diagnostic id; offer cached response if available.
E2: Denormalised join failure (aggregations) - return `500` and suggest requesting individual endpoints as workaround.

#### Termination

Client displays team screen.

#### Post condition

System awaits next request.



### UC-12: Create New Team

### Scope

Create a new team record (initial roster, budget, HQ).

### Description

Player or admin creates a team; the system allocates starting assets or placeholders.

### Actors

- `Player/Admin` - initiates team creation.
- `Provisioning Service` - reserves starting resources.

### Use Case Diagram

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



### UC-13: Read Team Details (player team)

### Scope

Return player's own team with editable flags and affordances.

### Description

Provide editable team data for the player's management screen.

### Actors

- `Player` - owner of the team and primary editor.
- `Auth Service` - validates ownership and permissions.

### Use Case Diagram

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



### UC-14: Update Team Attributes

### Scope

Modify team attributes (budget allocation, HQ upgrades, staff assignments).

### Description

Player or admin updates team settings which are validated and persisted.

### Actors

- `Player/Admin` - submits updates.
- `Finance Service` - validates budget changes.

### Use Case Diagram

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



### UC-15: Read Available Drivers

### Scope

Return list of uncontracted or transfer-available drivers for recruitment.

### Description

Provide filtered and paginated driver pool for the market UI.

### Actors

- `Player` - browses and filters available drivers.
- `Team AI` - automated consumer of driver listings.

### Use Case Diagram

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



### UC-16: Update Driver Contract

### Scope

Sign, renew or terminate driver contracts and update team roster and budget.

### Description

Persist contract terms and adjust availability and team budgets.

### Actors

- `Team Manager` - negotiates and confirms driver contracts.
- `Admin` - enforces or modifies contract rules when required.

### Use Case Diagram

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



### UC-17: Read Available Staff

### Scope

Return list of available staff for hiring with roles and modifiers.

### Description

Provide paginated staff pool for recruitment screens.

### Actors

- `Player` - requests staff listings.
- `HR Service` - provides staff filters and pools.

### Use Case Diagram

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



### UC-18: Update Staff Contract

### Scope

Hire, fire or renegotiate staff contracts and persist changes to team resources.

### Description

Assign staff to teams, record salary and update budgets.

### Actors

- `Player` - initiates hiring/renegotiation.
- `Team Manager` - manages staff assignments.

### Use Case Diagram

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



### UC-19: Update Driver Skills/Age

### Scope

Periodic update of driver attributes (ageing, progression/regression) and handle retirements/recycling.

### Description

Perform end-of-season or scheduled updates to driver skills and ages; mark retirees and optionally regenerate/recycle entities.

### Actors

- `Scheduler` (Game Loop) - triggers seasonal maintenance jobs.
- `Admin` - may invoke manual progression runs.

### Use Case Diagram

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



### UC-20: Update Team Budget

### Scope

Adjust team budget for income/expenses, sponsor payouts and race fees.

### Description

Apply transactions affecting a team's budget and persist them.

### Actors

- `Finance System` - posts transactions affecting team budgets.
- `Game Loop` - triggers periodic income/expense events.

### Use Case Diagram

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



### UC-22: Create New Staff Member (staff generation)

### Scope

Generate new staff when required (optional).

### Description

Create or recycle staff records for hireable pool expansion.

### Actors

- `Admin/System` - triggers staff generation or pool maintenance.

### Use Case Diagram

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



### UC-23: Delete Championship

### Scope

Remove or archive a championship (admin only).

### Description

Delete or archive championship and related resources according to retention policy.

### Actors

- `Admin` - authorised to delete or archive championships.

### Use Case Diagram

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



### UC-24: Create Custom Track

### Scope

Add a custom track with characteristics for use in events.

### Description

Designer or admin submits track metadata and layout which becomes available for events.

### Actors

- `Designer/Admin` - submits track definitions and layout files.

### Use Case Diagram

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



### UC-25: Update Track Characteristics

### Scope

Modify track parameters (surface, length, grip) for balancing.

### Description

Admin updates track metadata and future events use revised parameters.

### Actors

- `Admin` - submits track updates.

### Use Case Diagram

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



### UC-26: Delete Track

### Scope

Remove custom or unused tracks with checks for scheduled use.

### Description

Admin removes track or archives it if scheduled in future.

### Actors

- `Admin` - initiates deletion or archiving of tracks.

### Use Case Diagram

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



### UC-27: Read Staff Performance Modifiers

### Scope

Return computed staff modifiers used by the simulation for team performance.

### Description

Provide staff-based modifiers (mechanic efficiency, strategist value) to the Simulation Service.

### Actors

- `Simulation Service` - requests computed modifiers for a team.

### Use Case Diagram

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



### UC-28: Update Driver Appearance

### Scope

Change cosmetic appearance for a driver (helmet, livery) - non-gameplay affecting.

### Description

Player edits and saves driver appearance assets which are stored and served to UI.

### Actors

- `Player` - creates or edits appearance assets.
- `Storage Service` - stores and serves asset files.

### Use Case Diagram

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



### UC-29: Update Team Branding

### Scope

Update team visual branding assets and metadata (logos, colours).

### Description

Player or admin uploads branding assets and updates team metadata for display in UI.

### Actors

- `Player/Admin` - uploads branding assets.
- `Storage/DB` - stores branding files and metadata.

### Use Case Diagram

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
