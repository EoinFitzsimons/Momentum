# Use Cases

## UC-1: Read Driver Details

### Scope

Retrieve a complete driver profile with attributes across multiple categories (technical, physical, mental, racecraft) to configure drivers for race simulation.

### Description

The system provides driver information to the GUI and simulation engine. A driver profile contains name, nationality, age, skill ratings, and team assignment.

### Actors

- **GUI** - displays driver information for race setup and team management screens.
- **Simulation Engine** - retrieves driver data to initialise AI agents for race simulation.
- **System** - retrieves and returns driver records.

### Flow Description

#### Precondition

The system has a populated driver database; requested driver record exists.

#### Activation

Starts when the GUI loads a race setup screen or the simulation engine initialises a race.

#### Main Flow

- The GUI or simulation engine requests a driver profile.
- The system retrieves the driver record with all attributes.
- The system validates the driver data is complete.
- The GUI displays the driver details, or the simulation engine initialises the driver for race execution.
- **Flow ends** when the driver profile is displayed or race initialisation is complete.

#### Alternate Flow A1

- The requested driver does not exist in the system.
- The system notifies the caller that the driver was not found.
- **Flow returns to** the driver selection screen or the screen that initiated the request.

#### Alternate Flow A2

- The driver database connection fails.
- The system displays an error message and offers to retry or regenerate the database.
- **Flow returns to** the main menu or returns control to the user.

#### Exceptional Flow E1

- The driver record contains incomplete or corrupt data.
- The system logs the error for diagnostic purposes.
- The system uses default attribute values to allow continued operation.
- **Flow continues** with the operation using the default values and the user is notified of degraded data.

#### Termination

The driver profile is displayed or used for simulation initialisation.

---

## UC-2: Read Race Configuration

### Scope

Retrieve track information including layout, surface type, and race parameters to configure the simulation engine.

### Description

The system provides track data to the GUI and simulation engine. Track records include name, location, length, surface characteristics, and corner configuration.

### Actors

- **GUI** - displays track information on race setup screens.
- **Simulation Engine** - loads track configuration for physics calculations.
- **System** - retrieves and provides track records.

### Flow Description

#### Precondition

The system has a populated track database with at least one track record.

#### Activation

Starts when the GUI loads a race setup screen or the simulation engine begins initialisation.

#### Main Flow

- The GUI or simulation engine requests track data.
- The system retrieves the track record with configuration details.
- The system validates the track data is complete and consistent.
- The GUI displays the track information, or the simulation engine loads the track for race execution.
- **Flow ends** when the track is displayed or ready for simulation.

#### Alternate Flow A1

- The requested track does not exist.
- The system notifies the caller that the track was not found.
- **Flow returns to** the track selection screen with guidance to select another track.

#### Alternate Flow A2

- The track database is empty or unpopulated.
- The system notifies the user and displays a message explaining that tracks are not yet available.
- **Flow returns to** the main menu.

#### Exceptional Flow E1

- The track record contains missing or invalid data.
- The system logs the error and uses reasonable defaults for missing attributes.
- The system allows the race to proceed with the available track data.
- **Flow continues** with the operation and the user is notified of the issue.

#### Termination

The track is displayed or loaded for simulation.

---

## UC-3: Create Race Result

### Scope

Capture and persist the outcome of a completed race simulation, including positions, lap times, and DNF information.

### Description

When a race simulation completes, the system records the final classification with finishing positions, times, and any retirements.

### Actors

- **Simulation Engine** - executes the race and generates final results.
- **GUI** - displays the race results to the user.
- **System** - persists race results to storage.

### Flow Description

#### Precondition

A race simulation has been executed and completed or terminated by the user.

#### Activation

Starts when the race simulation finishes or is stopped.

#### Main Flow

- The simulation engine completes the race and generates classification data.
- The system validates that all participants are accounted for and positions are sequential.
- The system stores the race results with the final classification, times, and any DNF statuses.
- The GUI displays the race results to the user.
- **Flow ends** when the results are persisted and displayed.

#### Alternate Flow A1

- The user stops the race before completion.
- The simulation engine returns partial results with the current positions.
- The system stores the partial results and marks the race as incomplete.
- **Flow returns to** the race results screen showing the partial classification.

#### Alternate Flow A2

- All participants fail to finish (all DNF).
- The system creates result records for all drivers marked as DNF.
- The system persists the results with DNF reasons recorded.
- **Flow continues** and the GUI displays the DNF results.

#### Exceptional Flow E1

- The system fails to store race results.
- The system displays an error message and allows the user to retry or proceed.
- The race results remain visible on screen but a warning indicates they were not saved.
- **Flow continues** with manual backup options offered to the user.

#### Exceptional Flow E2

- The race result data is invalid or incomplete.
- The system logs the error and attempts to store what data is available.
- The user is warned that some race data could not be saved.
- **Flow continues** with partial results displayed.

#### Termination

Race results are persisted and displayed to the user.

---

## UC-4: Read Race Results

### Scope

Retrieve and display historical race classification and result data from completed races.

### Description

The system provides access to stored race results including finishing positions, times, and DNF information for analysis and display.

### Actors

- **GUI** - requests and displays race results.
- **User** - navigates to view race history.
- **System** - retrieves and provides stored results.

### Flow Description

#### Precondition

At least one race has been completed and results have been stored.

#### Activation

Starts when the user navigates to view race results or race history.

#### Main Flow

- The user requests race results for a specific race or championship.
- The system retrieves the stored race results.
- The system assembles the complete classification with driver names, teams, positions, and times.
- The GUI displays the results in a standings table format.
- **Flow ends** when the race results are displayed.

#### Alternate Flow A1

- No results are found for the requested race.
- The system notifies the user that no results are available.
- **Flow returns to** the race history screen or menu.

#### Alternate Flow A2

- The race was incomplete or partial.
- The system displays the available results and marks them as incomplete.
- **Flow returns to** the race history view with the incomplete flag visible.

#### Exceptional Flow E1

- The system fails to retrieve stored results.
- The system displays an error message.
- If cached results are available from memory, the system displays them marked as possibly stale.
- **Flow continues** with the best available data shown.

#### Exceptional Flow E2

- Stored result data is corrupted or inconsistent.
- The system logs the error and displays the data that could be recovered.
- The user is warned that some result data may be missing or incorrect.
- **Flow continues** with partial or degraded results displayed.

#### Termination

Race results are displayed to the user, who can then navigate to other screens or compare results.

---

## UC-5: Read Championship Details

### Scope

Retrieve championship metadata including season information, standings, and calendar of scheduled races.

### Description

The system provides comprehensive championship information to the GUI for display during season progression.

### Actors

- **GUI** - displays championship information and standings.
- **User** - navigates to view championship details.
- **System** - retrieves and aggregates championship data.

### Flow Description

#### Precondition

At least one championship exists and is active.

#### Activation

Starts when the user navigates to the championship overview screen.

#### Main Flow

- The user requests championship details for a specific championship.
- The system retrieves the championship metadata including year, discipline, and rules.
- The system retrieves the current standings by aggregating race results.
- The system retrieves the schedule of races planned for the season.
- The GUI displays the championship overview with standings table and upcoming events.
- **Flow ends** when the championship information is displayed.

#### Alternate Flow A1

- The championship has no races scheduled yet.
- The system displays the championship information with an empty calendar.
- The GUI shows an option to add races to the schedule.
- **Flow continues** with the option for the user to create race events.

#### Alternate Flow A2

- The championship has no race results yet (standings are empty).
- The system displays the championship information and shows zero points for all entries.
- **Flow continues** with the empty standings displayed.

#### Exceptional Flow E1

- The system fails to retrieve championship data.
- The system displays an error message and offers retry options.
- If cached championship data is available, it is displayed marked as possibly stale.
- **Flow continues** with available data or returns to the main menu.

#### Exceptional Flow E2

- The championship structure is invalid or corrupted in storage.
- The system logs a diagnostic error.
- The system displays what data could be recovered.
- The user is notified of the issue and offered recovery options.
- **Flow returns to** the main menu or menu with recovery options.

#### Termination

Championship overview is displayed with standings and calendar information.

---

## UC-6: Update Championship Standings

### Scope

Recalculate and persist updated championship standings after a race completes.

### Description

The system recalculates the championship points and standings following each completed race using discipline-specific point systems.

### Actors

- **System** - triggers recalculation when results are recorded.
- **User/Admin** - may manually request recalculation.

### Flow Description

#### Precondition

A championship exists with completed races and stored results.

#### Activation

Starts when a race is completed and results are persisted, or when explicitly requested.

#### Main Flow

- The system gathers all completed race results for the championship.
- The system applies the championship's points system to calculate points for each race.
- The system aggregates the points for each driver across all races.
- The system computes the final standings with drivers sorted by total points.
- The system applies tie-breaking rules if needed.
- The standings are persisted in storage.
- Subscribers to standings updates are notified of the change.
- **Flow ends** when standings are persisted and notifications sent.

#### Alternate Flow A1

- A partial or incremental update is requested instead of full recalculation.
- The system recalculates only the affected portion of standings.
- The system persists the updated standings.
- **Flow continues** with partial standings propagated.

#### Alternate Flow A2

- Multiple standings recalculations are requested concurrently.
- The system queues subsequent requests and processes them after the first completes.
- **Flow returns to** the caller with status indicating queueing.

#### Exceptional Flow E1

- The points system rules are missing or invalid.
- The system logs the error and uses default point values.
- Standings are calculated and marked as using default rules.
- An alert is raised for administrative review.
- **Flow continues** with degraded standings.

#### Exceptional Flow E2

- The system fails to persist updated standings.
- The system logs the error and queues the standings update for retry.
- The user is notified of the persistence issue.
- **Flow continues** and retry is scheduled automatically.

#### Termination

Updated standings are computed and persisted; downstream systems are notified.

---

## UC-7: Create Race Event

### Scope

Add a new race event to a championship calendar with date, track, and configuration.

### Description

The system creates a new race event entry in the championship schedule with validation for date and track conflicts.

### Actors

- **User/Admin** - creates a new race event.
- **System** - validates and records the event.

### Flow Description

#### Precondition

A championship exists and is open for event creation; tracks are available.

#### Activation

Starts when the user submits a new race event creation.

#### Main Flow

- The user provides race event details including date, track, and configuration.
- The system validates that the track exists and is available.
- The system checks for date conflicts with other scheduled races in the championship.
- The system assigns a round number based on the current calendar size.
- The system stores the new race event.
- The GUI displays confirmation of the new race added to the calendar.
- **Flow ends** when the race event is created and visible in the calendar.

#### Alternate Flow A1

- The selected date conflicts with another scheduled race.
- The system notifies the user of the conflict and displays other available dates.
- The user can select an alternative date and resubmit.
- **Flow returns to** event creation with the conflict resolved or cancelled.

#### Alternate Flow A2

- The selected track is unavailable or invalid.
- The system notifies the user and displays available tracks.
- The user selects another track and resubmits.
- **Flow returns to** event creation with a valid track selected.

#### Exceptional Flow E1

- The system fails to store the new race event.
- The system logs the error and displays a message to the user.
- The system offers to retry the creation.
- **Flow returns to** the event creation form to retry or cancel.

#### Exceptional Flow E2

- Mandatory event fields are missing or invalid.
- The system displays validation errors for each invalid field.
- The user corrects the fields and resubmits.
- **Flow returns to** event creation with validation feedback.

#### Termination

Race event is created and added to the championship calendar.

---

## UC-8: Read Race Schedule

### Scope

Retrieve and display the ordered calendar of races scheduled for a championship season.

### Description

The system provides the season schedule showing all planned races with dates, tracks, and status information.

### Actors

- **GUI** - requests and displays the race schedule.
- **User** - navigates to view the schedule.
- **System** - retrieves and provides schedule data.

### Flow Description

#### Precondition

A championship exists; may or may not have races scheduled.

#### Activation

Starts when the user navigates to view the championship calendar.

#### Main Flow

- The user requests the race schedule for a championship.
- The system retrieves all races for the championship, ordered by round number.
- The system assembles the schedule with date, track, round number, and current status for each race.
- The GUI displays the calendar in chronological order.
- **Flow ends** when the schedule is displayed.

#### Alternate Flow A1

- The championship does not exist.
- The system notifies the user and displays a message.
- The GUI provides guidance on creating a championship.
- **Flow returns to** the main championship screen or menu.

#### Alternate Flow A2

- The championship exists but no races are scheduled.
- The system returns an empty schedule.
- The GUI displays an empty calendar and offers an option to add races.
- **Flow continues** with guidance to schedule events.

#### Exceptional Flow E1

- The system fails to retrieve schedule data.
- The system displays an error message and attempts to show cached schedule data if available.
- **Flow returns to** the menu or retries the request.

#### Exceptional Flow E2

- The schedule data is incomplete or corrupt.
- The system retrieves and displays the available schedule data.
- The user is warned that some data may be missing.
- **Flow continues** with partial schedule displayed.

#### Termination

Race schedule is displayed to the user for the selected championship.

---

## UC-9: Update Race Status

### Scope

Change a race event's lifecycle status through stages: scheduled → in-progress → completed (or cancelled).

### Description

The system manages race state transitions with validation of allowed transitions and updates to related data.

### Actors

- **Simulation Engine** - updates status during and after race execution.
- **User/Admin** - may manually change status for management purposes.
- **System** - validates and processes status changes.

### Flow Description

#### Precondition

A race event exists; the user has permission to change its status.

#### Activation

Starts when a status change is requested (e.g., starting a race, completing it, or cancelling).

#### Main Flow

- The user or system requests a race status change with the new target status.
- The system validates that the transition is allowed (e.g., scheduled → in-progress is allowed; completed → scheduled is not).
- The system updates the race event status.
- Dependent systems are notified of the status change.
- **Flow ends** when status is updated and notifications sent.

#### Alternate Flow A1

- An invalid status transition is attempted (e.g., trying to transition from completed back to in-progress).
- The system rejects the transition and displays the allowed transitions for the current state.
- The user can select a valid transition or cancel.
- **Flow returns to** the race management screen.

#### Alternate Flow A2

- The user requests race cancellation while the race is in-progress.
- The system initiates graceful abort procedures and transitions the race to cancelled.
- Related data is updated to reflect the cancellation.
- **Flow returns to** the race management screen with cancellation confirmed.

#### Exceptional Flow E1

- The system fails to update the race status in storage.
- The system logs the error and displays a message.
- The system queues the status change for retry.
- The user is informed of the issue and given retry options.
- **Flow continues** with automatic retry scheduled.

#### Exceptional Flow E2

- Notification of dependent systems fails during status change.
- The system completes the status update but records the notification failure.
- The user is notified that the status was changed but some notifications may be pending.
- **Flow continues** with notifications retried automatically.

#### Termination

Race status is updated and stored; dependent systems are notified of the change.

---

## UC-10: Create Championship

### Scope

Create a new championship record for a season with initial configuration and empty calendar.

### Description

The system creates a new championship season with discipline, rules, and placeholder for events to be scheduled.

### Actors

- **User/Admin** - initiates championship creation.
- **System** - validates and creates the championship record.

### Flow Description

#### Precondition

The user has permission to create championships; season configuration is available.

#### Activation

Starts when the user submits a championship creation request.

#### Main Flow

- The user provides championship details including name, discipline, season year, and points system.
- The system validates the provided information.
- The system creates the championship record with initial status (empty calendar, no standings).
- The system stores the championship in persistent storage.
- The system notifies dependent systems that a new championship is available.
- The GUI displays confirmation and displays the new championship.
- **Flow ends** when the championship is created and stored.

#### Alternate Flow A1

- The selected ruleset or points system is invalid or missing.
- The system uses a default ruleset and continues with championship creation.
- The championship is marked for review to confirm the default ruleset is acceptable.
- **Flow continues** with championship created using defaults.

#### Exceptional Flow E1

- The system fails to store the championship.
- The system logs the error and displays a message to the user.
- The system queues the championship creation for automatic retry.
- **Flow returns to** the championship creation screen with retry option.

#### Exceptional Flow E2

- Required fields are missing or invalid.
- The system displays validation errors.
- The user corrects the fields and resubmits.
- **Flow returns to** championship creation with feedback.

#### Termination

Championship is created and stored; downstream systems are notified.

---

## UC-11: Read Team Details

### Scope

Retrieve comprehensive team profile including budget, tier classification, roster, and performance information.

### Description

The system provides complete team information to the GUI for display on team management and information screens.

### Actors

- **GUI** - requests and displays team information.
- **User** - navigates to view team details.
- **System** - retrieves and provides team records.

### Flow Description

#### Precondition

At least one team exists in the system.

#### Activation

Starts when the user navigates to view team details.

#### Main Flow

- The user requests details for a specific team.
- The system retrieves the team record including name, discipline, tier, budget, and headquarters.
- The system retrieves the current roster (assigned drivers and staff).
- The system retrieves financial information including budget status and expenditures.
- The GUI displays the complete team profile.
- **Flow ends** when team details are displayed.

#### Alternate Flow A1

- The requested team does not exist.
- The system notifies the user that the team was not found.
- **Flow returns to** the team selection or team list screen.

#### Alternate Flow A2

- The team has no assigned drivers or staff.
- The system displays the team information with an empty roster.
- The GUI shows the roster as empty and may offer hiring options.
- **Flow continues** with empty roster displayed.

#### Exceptional Flow E1

- The system fails to retrieve team data.
- The system displays an error message.
- If available, cached team data is shown marked as possibly stale.
- **Flow continues** with available data or returns to team list.

#### Exceptional Flow E2

- Team data is incomplete or corrupt.
- The system retrieves and displays available data.
- The user is warned that some team information may be missing.
- **Flow continues** with partial team profile displayed.

#### Termination

Team profile is displayed with complete or partial information.

---

## UC-12: Create Team

### Scope

Create a new team record with initial configuration, budget allocation, and optional roster.

### Description

The system creates a new team entry for a player or as an NPC team with starting resources and configuration.

### Actors

- **User/Admin** - creates a new team.
- **System** - validates and provisions the team.

### Flow Description

#### Precondition

The user has permission to create teams; resources are available for allocation.

#### Activation

Starts when the user submits a team creation request.

#### Main Flow

- The user provides team details including name, discipline, headquarters location, and starting tier.
- The system validates the team information (unique name, valid discipline, etc.).
- The system allocates starting resources and budget based on team tier.
- The system creates the team record.
- The system stores the team in persistent storage.
- The GUI displays confirmation and the new team.
- **Flow ends** when the team is created and stored.

#### Alternate Flow A1

- The team name already exists.
- The system notifies the user and suggests alternative names.
- The user provides a new name and resubmits.
- **Flow returns to** team creation with conflict resolved.

#### Alternate Flow A2

- The selected discipline is not available or invalid.
- The system notifies the user and displays available disciplines.
- The user selects a valid discipline and resubmits.
- **Flow returns to** team creation with valid discipline selected.

#### Exceptional Flow E1

- The system fails to create or store the team.
- The system logs the error and displays a message.
- The system queues the team creation for automatic retry.
- **Flow returns to** the team creation screen with retry option.

#### Exceptional Flow E2

- Resource allocation fails (insufficient budget available).
- The system notifies the user and adjusts the team tier or starting resources.
- The user is prompted to confirm the adjusted allocation.
- **Flow returns to** team creation with adjusted parameters.

#### Termination

Team is created with initial budget and configuration; ready for roster management.

---

## UC-13: Read Player Team

### Scope

Retrieve the player's own team information with editable fields and management options.

### Description

The system provides the player's team data for management purposes, including roster and budget that can be modified.

### Actors

- **GUI** - requests and displays the player's team.
- **Player** - views and manages their team.
- **System** - retrieves the player's team record.

### Flow Description

#### Precondition

The player has an assigned team; authorization is valid.

#### Activation

Starts when the player navigates to their team management screen.

#### Main Flow

- The system identifies the player's team assignment.
- The system retrieves the team record with all details including roster and budget.
- The system marks fields that are editable for the player.
- The GUI displays the player's team profile with editable controls.
- **Flow ends** when the team is displayed with edit options available.

#### Alternate Flow A1

- The player does not have an assigned team.
- The system notifies the player and displays guidance on creating or joining a team.
- The GUI provides options to create a new team or join an existing one.
- **Flow returns to** the main menu or team creation flow.

#### Exceptional Flow E1

- The system fails to retrieve the player's team.
- The system displays an error message.
- If cached team data is available, it is shown marked as possibly stale.
- **Flow returns to** the main menu with error handling.

#### Exceptional Flow E2

- Authorization check determines the player does not own the displayed team.
- The system revokes edit permissions and displays the team in read-only mode.
- The user is notified of the permission issue.
- **Flow continues** with read-only team view.

#### Termination

Player's team is displayed with appropriate edit permissions and management options available.

---

## UC-14: Update Team Attributes

### Scope

Modify team settings including budget allocation, facility upgrades, and strategic configuration.

### Description

The system allows players and admins to update team properties with validation of budget and resource constraints.

### Actors

- **Player** - updates their team attributes.
- **Admin** - may update any team attributes.
- **System** - validates and persists changes.

### Flow Description

#### Precondition

The user has edit permissions for the team; the team exists in storage.

#### Activation

Starts when the user submits team attribute updates.

#### Main Flow

- The user edits team attributes such as name, headquarters, or budget allocation.
- The system validates the changes against available budget and constraints.
- The system checks that new attribute values are acceptable (e.g., name is unique, values are in valid ranges).
- The system persists the updated team record.
- The system notifies subscribers of the team update.
- The GUI displays the updated team information.
- **Flow ends** when changes are persisted and displayed.

#### Alternate Flow A1

- The proposed budget allocation exceeds available funds.
- The system notifies the user of the shortfall and suggests alternatives.
- The user can adjust the allocation or request additional funding.
- **Flow returns to** team update with revised budget or cancellation.

#### Alternate Flow A2

- A facility upgrade is requested.
- The system validates the upgrade is available and cost is covered by budget.
- The system deducts the upgrade cost and applies the upgrade.
- **Flow continues** with upgrade applied and budget deducted.

#### Exceptional Flow E1

- The system fails to persist team updates.
- The system logs the error and displays a message.
- The system queues the update for automatic retry.
- **Flow continues** with retry scheduled.

#### Exceptional Flow E2

- Concurrent updates to team data are detected.
- The system displays the current team state and informs the user of the conflict.
- The user can retry or merge their changes with current state.
- **Flow returns to** team update screen with current data displayed.

#### Termination

Team attributes are updated and persisted; subscribers are notified of changes.

---

## UC-15: Read Available Drivers

### Scope

Retrieve a list of drivers available for hiring/contract with filtering and pagination.

### Description

The system provides a browsable pool of uncontracted drivers for team recruitment, with support for filtering by discipline, rating, and other criteria.

### Actors

- **GUI** - requests and displays available drivers.
- **Player** - browses drivers for hiring.
- **System** - retrieves and filters driver records.

### Flow Description

#### Precondition

At least one uncontracted driver exists in the system.

#### Activation

Starts when the user opens the driver hiring/recruitment screen.

#### Main Flow

- The user optionally applies filters (discipline, rating range, etc.).
- The user optionally selects pagination parameters (page number, results per page).
- The system retrieves uncontracted drivers matching the filters.
- The system sorts drivers by requested criteria (rating, age, etc.).
- The system returns the paginated results with availability status and estimated cost.
- The GUI displays the available driver list.
- **Flow ends** when driver candidates are displayed.

#### Alternate Flow A1

- No drivers match the applied filters.
- The system returns an empty result set.
- The GUI displays a message indicating no matches and suggests relaxing filters.
- **Flow returns to** the driver search with filter options visible.

#### Alternate Flow A2

- The results exceed a single page.
- The system provides pagination information including total count and navigation.
- The user can browse to other pages of results.
- **Flow continues** with paginated results displayed.

#### Exceptional Flow E1

- The system fails to retrieve driver data.
- The system displays an error message.
- If available, cached driver list is shown marked as possibly stale.
- **Flow returns to** the main screen or offers retry.

#### Exceptional Flow E2

- Search or filter logic fails.
- The system falls back to a basic driver list without filtering.
- The user is notified of reduced search capabilities.
- **Flow continues** with unfiltered driver list displayed.

#### Termination

List of available drivers is displayed for recruitment.

---

## UC-16: Update Driver Contract

### Scope

Sign, renew, modify, or terminate a driver contract and update team roster and budget accordingly.

### Description

The system manages driver employment, updating roster assignments, contract terms, and team finances.

### Actors

- **Player** - initiates driver contract actions.
- **System** - validates and processes contracts.

### Flow Description

#### Precondition

A driver and team exist; negotiation terms are determined.

#### Activation

Starts when the player submits a driver contract action (signing, renewal, termination).

#### Main Flow

- The player selects a driver and confirms contract terms (length, salary, etc.).
- The system validates that the team has sufficient budget for the contract.
- The system validates contract constraints (duration limits, salary cap rules, etc.).
- The system creates or updates the contract record.
- The system updates the driver's team assignment.
- The system deducts salary from the team budget.
- The system persists the contract changes.
- The GUI displays confirmation of the contract action.
- **Flow ends** when contract is persisted and roster is updated.

#### Alternate Flow A1

- The team has insufficient budget for the proposed contract.
- The system notifies the player of the budget shortfall.
- The player can reduce the contract value, seek sponsorship, or cancel.
- **Flow returns to** contract negotiation with budget options.

#### Alternate Flow A2

- The driver is already contracted to another team.
- The system notifies the player that the driver is unavailable.
- The system provides alternatives or guidance for transfer procedures.
- **Flow returns to** driver selection with conflict noted.

#### Exceptional Flow E1

- The system fails to persist the contract.
- The system logs the error and displays a message.
- The system queues the contract for automatic retry.
- **Flow continues** with retry scheduled.

#### Exceptional Flow E2

- Contract validation fails due to rule violations.
- The system displays the validation errors.
- The player adjusts contract terms and resubmits.
- **Flow returns to** contract negotiation with feedback.

#### Termination

Driver contract is created or updated; roster and budget are adjusted.

---

## UC-17: Read Available Staff

### Scope

Retrieve a list of available staff for hiring with roles, ratings, and estimated costs.

### Description

The system provides a browsable pool of uncontracted staff members for team recruitment, supporting role-based filtering.

### Actors

- **GUI** - requests and displays available staff.
- **Player** - browses staff for hiring.
- **System** - retrieves and filters staff records.

### Flow Description

#### Precondition

At least one uncontracted staff member exists in the system.

#### Activation

Starts when the player opens the staff hiring screen.

#### Main Flow

- The player optionally applies filters (role, rating range, etc.).
- The system retrieves uncontracted staff members matching the filters.
- The system sorts staff by requested criteria (rating, role, etc.).
- The system returns the results with availability status and salary information.
- The GUI displays the available staff list.
- **Flow ends** when staff candidates are displayed.

#### Alternate Flow A1

- No staff match the applied filters.
- The system returns an empty result set.
- The GUI displays a message suggesting different filter criteria.
- **Flow returns to** the staff search with filter options visible.

#### Alternate Flow A2

- Some staff are partially available (e.g., contracted part-time).
- The system returns the staff with availability flags and constraints.
- The GUI displays the availability status for each candidate.
- **Flow continues** with full staff list and constraints displayed.

#### Exceptional Flow E1

- The system fails to retrieve staff data.
- The system displays an error message.
- If available, cached staff list is shown marked as possibly stale.
- **Flow returns to** the main screen or offers retry.

#### Exceptional Flow E2

- Staff data is corrupt or incomplete.
- The system retrieves and displays available staff data.
- The user is notified that some staff information may be missing.
- **Flow continues** with partial staff list displayed.

#### Termination

List of available staff is displayed for recruitment.

---

## UC-18: Update Staff Contract

### Scope

Hire, release, or modify staff contracts and update team roster and budget accordingly.

### Description

The system manages staff employment, updating team assignments, contract terms, and finances.

### Actors

- **Player** - initiates staff contract actions.
- **System** - validates and processes contracts.

### Flow Description

#### Precondition

A staff member and team exist; contract terms are determined.

#### Activation

Starts when the player submits a staff contract action.

#### Main Flow

- The player selects staff and confirms contract terms (role, length, salary).
- The system validates the team has sufficient budget for the salary.
- The system validates contract constraints (duration, salary cap, staff limits per role).
- The system creates or updates the contract record.
- The system updates the staff member's team assignment.
- The system adjusts the team budget for salary costs.
- The system persists the contract changes.
- The GUI displays confirmation of the contract action.
- **Flow ends** when contract is persisted and roster is updated.

#### Alternate Flow A1

- The team has insufficient budget for the staff salary.
- The system notifies the player of the budget shortfall.
- The player can reduce the offer, defer hiring, or cancel.
- **Flow returns to** contract negotiation with budget guidance.

#### Alternate Flow A2

- The staff member is no longer available at contract confirmation.
- The system notifies the player that the staff member was hired elsewhere.
- The system suggests alternative staff members.
- **Flow returns to** staff selection.

#### Exceptional Flow E1

- The system fails to persist the contract.
- The system logs the error and displays a message.
- The system queues the contract for automatic retry.
- **Flow continues** with retry scheduled.

#### Exceptional Flow E2

- Contract validation fails due to rule violations (e.g., too many staff of same role).
- The system displays the validation errors and constraints.
- The player adjusts contract terms and resubmits.
- **Flow returns to** contract negotiation with feedback.

#### Termination

Staff contract is created or updated; roster and budget are adjusted.

---

## UC-19: Update Driver Skills and Age

### Scope

Apply periodic end-of-season updates to driver attributes including aging, skill progression, retirement, and recycling.

### Description

The system manages driver lifecycle including skill development over time, retirement when age thresholds are reached, and generation of new rookie drivers from retired drivers.

### Actors

- **System** - executes periodic progression updates.
- **Admin** - may trigger manual progression.

### Flow Description

#### Precondition

At least one driver exists; season end has been reached or progression is manually triggered.

#### Activation

Starts at the end of each season automatically or when manually requested by admin.

#### Main Flow

- The system iterates through all active drivers.
- The system applies age increments based on time elapsed.
- The system applies skill progression formulas based on age, experience, and performance.
- The system checks retirement eligibility based on age and performance thresholds.
- Eligible drivers are marked as retired.
- Retired drivers are recycled: new rookie drivers are generated to replace them.
- All changes are persisted.
- Subscribers are notified of progression updates.
- **Flow ends** when all drivers are processed and changes are stored.

#### Alternate Flow A1

- An emergency update is required for a single driver due to injury.
- The system allows targeted updates to individual drivers outside the normal schedule.
- The affected driver's attributes are modified and persisted.
- **Flow returns to** normal operation.

#### Alternate Flow A2

- A player-triggered training session is performed during the season.
- The system applies a limited skill boost to the selected driver.
- A cooldown timer is set to prevent abuse.
- **Flow continues** with training boost applied.

#### Exceptional Flow E1

- The batch progression fails for some drivers.
- The system logs the error with affected driver IDs.
- Failed drivers are skipped in this update cycle and retry is scheduled.
- The system completes with partial updates and notifies admin.
- **Flow continues** with partial updates persisted and retry queued.

#### Exceptional Flow E2

- Skill values become invalid (e.g., negative or exceeding limits).
- The system clamps values to valid ranges.
- The affected records are logged for review.
- Skill progression completes with clamped values.
- **Flow continues** with values corrected.

#### Termination

Driver attributes are updated for next season; retiring drivers are recycled with new rookies.

---

## UC-20: Update Team Budget

### Scope

Adjust team budget based on income from race results, expenses, and financial transactions.

### Description

The system manages team finances including salary payments, race fees, income, and sponsor funds.

### Actors

- **System** - applies periodic budget adjustments (income, expenses).
- **Admin/Player** - may request manual budget adjustments for special circumstances.

### Flow Description

#### Precondition

A team exists with a current budget.

#### Activation

Starts when a financial transaction occurs (race completed, season tick, sponsor payout) or is manually requested.

#### Main Flow

- A financial event triggers a budget transaction (income, expense, or transfer).
- The system validates the transaction is legitimate and the team can afford it.
- The system calculates the amount to be added or deducted.
- The system updates the team's budget balance.
- The system persists the transaction and new balance.
- Subscribers are notified of the budget change.
- **Flow ends** when budget is updated and transaction is logged.

#### Alternate Flow A1

- A debit transaction would result in insufficient funds.
- The system rejects the transaction and displays the shortfall.
- The player is offered options (defer expense, seek sponsor, reduce spending).
- **Flow returns to** main team management with options for fund raising.

#### Alternate Flow A2

- Multiple concurrent transactions are requested for the same team.
- The system queues subsequent transactions to process sequentially.
- Each transaction is processed in order with updated budget state.
- **Flow returns to** with transaction queue status.

#### Exceptional Flow E1

- The system fails to persist a budget transaction.
- The system logs the error and queues the transaction for retry.
- The user is notified of the issue and retry is scheduled.
- **Flow continues** with transaction persisted on retry.

#### Exceptional Flow E2

- A financial calculation produces invalid results (overflow, precision error).
- The system logs the error and uses fallback calculation.
- The transaction completes with logged error for review.
- **Flow continues** with fallback calculation used.

#### Termination

Team budget is updated and financial transaction is logged.

---

## UC-21: Create New Driver (Deferred - Future)

### Scope

Generate or recycle driver profiles to expand the hireable pool.

### Description

The system maintains an adequate pool of available drivers through generation and recycling of retired drivers.

### Actors

- **System** - executes driver pool maintenance.
- **Admin** - may trigger manual generation.

### Flow Description

#### Precondition

Pool size is below threshold or manual request received.

#### Activation

Starts when pool maintenance is triggered or manually requested.

#### Main Flow

- The system checks if recycling retired drivers is viable.
- If recycled drivers are insufficient, new drivers are generated with random attributes.
- Generated drivers are validated for uniqueness and data consistency.
- New drivers are marked as available in the hireable pool.
- **Flow ends** when drivers are added to the available pool.

#### Exceptional Flow E1

- Driver generation fails.
- System logs error and retries or uses cached pool.
- **Flow continues** with fallback.

#### Termination

Driver pool is expanded; generation completes.

---

## UC-22: Create New Staff Member (Deferred - Future)

### Scope

Generate or recycle staff to expand the hireable pool.

### Description

The system maintains an adequate pool of available staff through generation and recycling.

### Actors

- **System** - executes staff pool maintenance.

### Flow Description

#### Precondition

Pool size is below threshold.

#### Activation

Starts when pool maintenance is triggered.

#### Main Flow

- New staff members are generated with assigned roles and attributes.
- Staff are validated for data consistency.
- Staff are marked as available for hiring.
- **Flow ends** when staff are added to available pool.

#### Termination

Staff pool is expanded.

---

## UC-23: Delete Championship

### Scope

Remove or archive a championship record and related race data (admin only, deferred scope).

### Description

The system allows deletion or archival of championships with referential integrity checks.

### Actors

- **Admin** - authorized to delete or archive championships.
- **System** - validates and performs deletion.

### Flow Description

#### Precondition

Admin has appropriate authorization; championship exists.

#### Activation

Starts when admin requests championship deletion or archival.

#### Main Flow

- The system checks for dependent records (races, results, standings).
- If no dependencies or admin confirms cascade delete, the championship is removed.
- Related records are deleted or archived per retention policy.
- The operation is persisted.
- **Flow ends** when championship is removed or archived.

#### Alternate Flow A1

- Dependent records prevent deletion.
- System displays the dependencies.
- Admin can choose to archive instead of delete, or proceed with cascade.
- **Flow returns to** deletion with new option selected.

#### Exceptional Flow E1

- Deletion fails due to database error.
- System logs error and rolls back any partial deletes.
- Admin is notified and offered manual intervention options.
- **Flow returns to** with error handling.

#### Termination

Championship is deleted or archived.

---

## UC-24: Create Custom Track (Deferred - Out of Scope)

### Scope

Create custom track records for use in championship events (player track configuration deferred).

### Description

Add track entries to the system via admin tools or track database import.

### Actors

- **Admin** - creates track records.

### Flow Description

#### Precondition

Track data or configuration is available.

#### Activation

Starts when track creation is submitted.

#### Main Flow

- Track details are validated.
- Track record is created and stored.
- **Flow ends** when track is available for use.

#### Termination

Track record is created.

**Note:** Player-facing track customization is deferred to future design. Current delivery uses pre-seeded tracks.

---

## UC-25: Update Track Characteristics (Deferred - Out of Scope)

### Scope

Modify track parameters for balancing (admin/future feature).

### Description

Update track configuration attributes via admin tools.

### Actors

- **Admin** - updates track records.

### Flow Description

#### Precondition

Track exists and is editable.

#### Activation

Starts when updates are submitted.

#### Main Flow

- Track changes are validated.
- Track record is updated.
- **Flow ends** when changes are persisted.

#### Termination

Track record is updated.

**Note:** Player-facing track modification is deferred to future design.

---

## UC-26: Delete Track (Deferred - Out of Scope)

### Scope

Remove track records (admin/future feature, not player-editable).

### Description

Delete or archive track records from the system.

### Actors

- **Admin** - deletes or archives tracks.

### Flow Description

#### Precondition

Admin authorized; track eligible for deletion.

#### Activation

Starts when deletion is requested.

#### Main Flow

- System checks for scheduled races using the track.
- If none or admin confirms, track is deleted or archived.
- **Flow ends** when track is removed.

#### Termination

Track is deleted or archived.

**Note:** Track deletion is internal/admin-only (renamed to `_delete_track()` in code). Player track configuration is out of scope.

---

## UC-27: Read Staff Performance Modifiers

### Scope

Retrieve computed staff impact modifiers for use during race simulation.

### Description

The system provides staff-based performance modifiers to the simulation engine based on assigned team staff and their ratings.

### Actors

- **Simulation Engine** - requests staff performance factors.
- **System** - computes and provides modifiers.

### Flow Description

#### Precondition

At least one staff member is assigned to the team, or team exists without staff.

#### Activation

Starts when the simulation engine requests performance modifiers for a team.

#### Main Flow

- The system retrieves all staff assigned to the team.
- The system aggregates staff attributes (role, rating, specialisation).
- The system computes performance modifier values based on staff composition.
- The modifier set is returned to the simulation engine.
- The simulation engine applies the modifiers to team performance calculations during the race.
- **Flow ends** when modifiers are applied during race execution.

#### Alternate Flow A1

- The team has no assigned staff.
- The system returns default modifier values (neutral factors).
- The simulation engine uses the defaults for race calculations.
- **Flow continues** with default modifiers.

#### Alternate Flow A2

- Staff data is incomplete or missing.
- The system computes modifiers using available data.
- A flag indicates the modifiers may not reflect full staff impact.
- **Flow continues** with partial modifiers returned and flagged as incomplete.

#### Exceptional Flow E1

- The system fails to retrieve staff data.
- The system returns default modifiers and logs an error.
- The simulation engine continues with defaults and degraded accuracy.
- **Flow continues** with fallback defaults.

#### Exceptional Flow E2

- Modifier calculation fails due to invalid data.
- The system logs the error and provides fallback default values.
- The user/admin is notified of the calculation issue.
- **Flow continues** with fallback modifiers.

#### Termination

Staff performance modifiers are provided to and applied by the simulation engine during race execution.

---

## UC-28: Update Driver Appearance (Deferred - Out of Scope)

### Scope

Modify driver cosmetic appearance (helmets, suits, faces) - deferred to future design.

### Description

Player uploads appearance assets and customizations for cosmetic display.

### Actors

- **Player** - uploads appearance assets.

### Flow Description

#### Precondition

Player owns driver; appearance system available.

#### Activation

Starts when appearance upload is submitted.

#### Main Flow

- Assets are validated for format and size.
- Appearance record is updated or created.
- **Flow ends** when appearance is persisted.

#### Termination

Appearance updated for display.

**Note:** Player-facing driver appearance customization (faces, helmets, suits) is deferred to future design. Current delivery focuses on core gameplay mechanics.

---

## UC-29: Update Team Branding (Deferred - Out of Scope)

### Scope

Modify team visual branding assets (logos, colours) - deferred to future design.

### Description

Player uploads team branding assets for display in menus and during races.

### Actors

- **Player** - uploads branding assets.

### Flow Description

#### Precondition

Player owns team; asset storage available.

#### Activation

Starts when branding upload is submitted.

#### Main Flow

- Assets are validated.
- Branding record is updated.
- **Flow ends** when branding is persisted.

#### Termination

Team branding updated for display.

**Note:** Player-facing team branding customization (logos, menu colours) is deferred to future design. Current delivery uses system-generated team livery in race visualization only.

---
