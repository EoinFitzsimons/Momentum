Implementation

This section explains how challenging systems in Momentum were implemented with specific code examples showing the technical solutions.

AI Decision Making and Player Overrides

Location: Momentum/Python/RaceLogic/realtime_race_engine.py, update_racing_mode function

The simulation uses an AI decision-making system where each driver is an autonomous agent that evaluates race conditions every frame (30 times per second) and adjusts their behavior. Player-controlled drivers can override the AI using real-time UI slider inputs.

The function first checks if the current driver is player-controlled. If yes it applies the player overrides from the UI sliders and skips all AI logic:

Check if player-controlled: if the driver ID matches player_driver_id
Apply player push intensity: read push value from player_overrides dictionary and assign to state.push_intensity
Apply overtake aggression: read overtake multiplier and adjust racing mode based on gaps. Higher multiplier triggers ATTACK mode more easily
Log player control: every 5 seconds print debug info showing push, mode, and gap ahead
Return early: skip all AI logic below

For AI-controlled drivers the system uses driver attributes to create personality-based behavior:

Extract driver attributes: get raw_speed, aggression, consistency, and risk_tolerance from the driver object (all normalized to 0.0 to 1.0)
Calculate base push: combine raw_speed, aggression, and risk_tolerance with weights to produce a base push intensity between 0.4 and 1.0
Add variability: less consistent drivers get more random variation in their push intensity
Evaluate track position: check gap ahead using track-aware overtaking evaluation system

The track-aware overtaking system examines the current track section (straight, slow corner, medium corner, fast corner, braking zone) and evaluates if an overtaking opportunity exists:

Find car ahead: locate the DriverState object for the car in front
Get track section: query the track map to determine section type and corner data at current position
Calculate gap in meters: convert time gap to distance gap using current velocity
Call evaluate_overtaking_opportunity: passes attacker driver, defender driver, speeds, gap, section type, and corner data. Returns should_attempt flag, success probability, and attempt type
If overtaking opportunity exists: set racing mode to ATTACK and increase push intensity by 35 percent (from base push up to maximum 1.0). Log the overtake attempt showing driver names, gap, and success chance
If no opportunity: set racing mode to MANAGE and keep base push intensity

Similarly for defensive driving when a car is close behind:

Find car behind: locate DriverState object for following car
Get track section: query track map at current position
Calculate defensive action: calls calculate_defensive_action which returns defensive strategy and racing line recommendation
Set mode to DEFEND: increase push by 10 percent and assign recommended racing line

For drivers with comfortable gaps (more than 3 seconds ahead and behind):

Set mode to MANAGE: conserve equipment
Apply conservation factor: consistent drivers reduce push more than inconsistent drivers
Use ideal racing line: no defensive positioning needed

Performance Calculation and Speed Modeling

Location: Momentum/Python/RaceLogic/realtime_race_engine.py, calculate_speed function

The speed calculation combines driver skill, team capability, push intensity, tire condition, fuel load, push fatigue, and environmental factors like slipstream.

Start with reference speed: base speed is 80 meters per second
Apply push multiplier: push intensity of 0.5 gives 85 percent speed, push of 1.0 gives 115 percent speed. This creates a nonlinear relationship where pushing harder has diminishing returns
Extract driver attributes: get raw_speed, cornering_skill, consistency from driver object (normalized to 0.0 to 1.0)
Calculate driver modifier: combine attributes with weights to produce a multiplier between 0.90 and 1.10
Apply team performance: team capability adds 0 to 5 percent bonus
Check track position: determine if car is in corner or on straight using sine wave approximation (8 corners per lap)
Apply corner modifier: if in corner multiply by 0.85 to 1.0 based on cornering skill. If on straight use full speed
Calculate final base speed: multiply reference speed by all modifiers

Then apply degradation and situational factors:

Tire degradation: worn tires lose grip. Tire condition of 0.5 applies 12.5 percent penalty
Fuel weight: lighter car is faster. Empty fuel tank (fuel load 0.0) gives 3 percent bonus
Push fatigue: accumulated stress from pushing hard. Fatigue above 0.3 reduces speed by up to 25 percent when exhausted (fatigue 1.0)
Slipstream boost: if in_slipstream flag is true multiply speed by 1.0 plus slipstream bonus (typically 5 to 10 percent)
Dirty air penalty: if following closely in a corner (within dirty air distance) reduce speed by dirty air penalty (typically 5 to 10 percent). Only applies in corners not on straights

Collision avoidance logic prevents rear-end collisions:

Check gap ahead: if less than 0.8 seconds
Calculate distance gap: convert time gap to meters using current velocity
Compare to minimum gap: need at least 1.2 car lengths (6 meters)
Apply safety factor: if too close reduce speed proportionally. Minimum 65 percent speed
Heavy braking: if dangerously close (less than 0.7 car lengths) multiply speed by 0.75 for emergency braking

Finally add consistency variance:

Calculate variance: inconsistent drivers have more lap-to-lap variation (up to plus or minus 5 percent)
Apply random factor: use RNG to add small speed variation each frame

Event Emission and GUI Updates

Location: Momentum/Python/RaceLogic/realtime_race_engine.py main loop and Momentum/Python/GUI/gui_race_visual.py event handling

The simulation runs in a background thread and communicates with the GUI through event callbacks. Every frame (30 times per second) the engine creates a position event and emits it to the GUI.

In the engine main loop:

Update all driver states: call update_racing_mode, calculate_speed, update position for each driver
Sort drivers by position: order by lap number then position on track
Build position event: create dictionary containing current time, active drivers list with id, name, position, lap, gap ahead, gap behind, best lap time for each driver
Call event callback: invoke the callback function with position event data

In the RaceWindow GUI class:

Subscribe to events: connect EventEmitter position_update signal to update_standings slot
Receive position event: update_standings function receives event dictionary on main GUI thread (Qt signal ensures thread safety)
Update visual display: redraw track with car positions from event data
Update standings table: populate table rows with position, driver name, lap, gap
Update timing display: show current race time and best lap times

The event system is thread-safe because it uses Qt signals which automatically marshal data from the race_runner thread to the main GUI thread.

Lap Detection and Completion

Location: Momentum/Python/RaceLogic/realtime_race_engine.py, complete_lap function

Lap detection works by tracking each driver's position along the track and detecting when they cross the start/finish line.

Each frame check if position crossed track length:

Previous position: stored from last frame
Current position: updated after speed calculation
If current position modulo track length is less than previous position modulo track length: lap was completed

When lap is detected call complete_lap:

Increment lap counter: state.lap plus equals 1
Calculate lap time: distance traveled divided by average velocity
Store lap time: append to lap times list for this driver
Update best lap: if lap time is faster than previous best update best lap time
Record lap start position: save current position for next lap timing

The UI displays lap as lap counter plus 1 because the engine counts completed laps starting from 0 but players expect to see lap 1 for the first lap.

Collision Detection and Incident System

Location: Momentum/Python/RaceLogic/realtime_race_engine.py, check_incident function

The collision detection system checks for incidents between cars and solo incidents like mechanical failures.

For each driver iterate through all other drivers:

Skip if not running: ignore DNF cars
Check lap equality: only check cars on same lap
Calculate longitudinal gap: distance along track between cars using modulo arithmetic to handle track wrapping
If gap is less than safe following distance (10 meters): potential incident

Determine if cars are racing wheel-to-wheel:

Check racing modes: if either car is in ATTACK or DEFEND mode they are overtaking (side-by-side)
If overtaking and gap is less than 1.5 car lengths: contact risk exists
Calculate combined skill: average vehicle control, spatial awareness, and racecraft attributes of both drivers (normalized to 0.0 to 1.0)
Check tire condition: worn tires reduce car control
Calculate contact probability: very small base probability (0.000002) multiplied by skill and tire factors
Roll random check: if contact occurs both cars DNF with contact_during_overtake reason
Log collision: append entry to collision_log with lap, time, position, type, both driver IDs and names, description

If not overtaking but cars are very close (less than 1 car length):

Calculate relative velocity: difference in speeds between cars
Determine who is behind: compare positions to find rear car
If rear car closing at more than 15 meters per second: rear-end collision risk
Rear car DNFs with rear_end_collision reason
Log collision: record incident details

For solo incidents check tire condition and mechanical reliability:

If tire condition below 0.1: chance of tire failure
If random check triggers: DNF with tire_failure reason
Mechanical failures: very rare random chance based on team reliability attribute

Starting Grid Initialization

Location: Momentum/Python/RaceLogic/realtime_race_engine.py, initialize_race function

The race initialization creates the starting grid with spacing between cars to reduce first-lap collisions.

For each driver in grid order:

Calculate starting position: position equals index times starting spacing (20 meters per car)
Create DriverState object: initialize with driver data, team data, starting position, initial push intensity based on driver attributes
Store in race state: add to driver_states dictionary
Initialize lap times: create empty list for lap time recording

The 20 meter spacing was increased from 10 meters after testing showed too many first-lap incidents. The larger spacing gives drivers more reaction time at race start.

Player Override System

Location: Momentum/Python/GUI/gui_race_visual.py keyboard handling and Momentum/Python/RaceLogic/realtime_race_engine.py override application

The player can adjust their car's behavior in real-time using keyboard inputs which modify the player_overrides dictionary that the engine reads every frame.

In RaceWindow class:

Override keyPressEvent: intercept keyboard input
Check key code: up/down arrows adjust pace slider, left/right arrows adjust overtaking slider
Update slider values: increment or decrement slider position
Read slider values: get current pace and overtaking values (0.0 to 1.0)
Calculate combined push: average of pace and overtaking sliders
Update player_overrides dictionary: set push and overtake keys
Dictionary is shared with engine: race_runner thread reads it every frame

In RealtimeRaceEngine update_racing_mode:

Check if player-controlled: compare driver ID to player_driver_id
Read player_overrides dictionary: get push and overtake values
Apply directly to DriverState: skip all AI logic and use player values
Player has full control: can push as hard or soft as they want, can adjust overtaking aggression independently

This creates an interactive experience where the player can respond to race situations (push harder to catch up, back off to save tires, be more or less aggressive with overtaking) while AI drivers follow their personality-based strategies.

Track Generation System

Location: Momentum/Python/GUI/gui_race_visual.py, CircuitGenerator class

The track generator creates procedural racing circuits using straight sections and clothoid corner transitions with closure logic to complete the loop.

Start with empty track points list
Add initial straight: first section along X axis
Generate corners and straights: alternate between straight sections and corner sections using random lengths and angles
Use clothoid transitions: corners are generated with smooth entry and exit curves
Check closure: after adding several sections check distance from current point to start point
If close enough trigger closure mode: adjust final sections to complete the loop back to start line
If not close add more sections and check again

The circuit generator ensures the track forms a closed loop that cars can lap repeatedly. The start/finish line is always at position 0 meters and the track length determines when a lap is complete.

Future Work: Quick Simulation Options

Purpose: provide a fast non-interactive option to advance championships or run statistics without watching full races.

Approaches under consideration:

Repeated headless runs: run the simulation many times with different RNG seeds and collect wins, podiums, and lap time statistics. Aggregate results to estimate championship outcomes
Lower-fidelity per-lap mode: evaluate races per lap or per sector using simpler math (attribute comparisons instead of frame-by-frame physics) to cut runtime by 10x or more
Analytic estimator: use a statistical model to predict finish probabilities from driver and team performance scores without running the simulation
Parallel execution: run iterations in parallel using multiple processes or background worker queues to speed up batch experiments

Tests and Validation

Headless renderer test: saves PNG images of rendered cars to verify vehicle appearance without opening GUI
GUI integration test: injects mock standings updates to verify UI updates correctly without running full engine
Playability test: comprehensive backend check that validates database, simulation, and API functionality

Extension Points

Add new racing disciplines: inherit from BaseDisciplineEngine and implement discipline-specific rules
Record RNG seeds: for repeatable experiments save the seed value used to initialize the random number generator
Batch telemetry writes: accumulate position data and write to database in batches instead of every frame to improve performance
Throttle UI updates: reduce event emission frequency (e.g. 10 FPS instead of 30 FPS) if performance issues occur
