"""
Real-Time Agent-Based Racing Simulation Engine

True live racing simulation where drivers are AI agents making decisions
at 30 FPS (0.033s timesteps). Drivers are aware of their surroundings and
actively make racing decisions based on position, gaps, and their attributes.

Key Features:
- 30 FPS simulation (2,700 updates per 90s lap)
- Spatial awareness: drivers know positions of cars around them
- Active AI decision-making: push/conserve, attack/defend
- Real-time overtaking with skill-based outcomes
- Tire degradation and fuel effects over time
- Slipstream/drafting physics
- Live position updates for GUI visualisation

Architecture:
- Each driver is an autonomous agent with state and decision logic
- Physics-based position updates using forces and acceleration
- Vectorized numpy calculations for performance
- Event emission for GUI integration at 30 FPS

Authors: Final Year Project - Computer Science
Date: December 2025
"""

import numpy as np
import time
from typing import List, Dict, Callable, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from database.models import Driver, Team, Track
from RaceLogic.track_physics import TrackMap, TrackSection, RacingLine
from RaceLogic.overtaking_system import (
    OvertakeAttempt, OvertakeAttemptType, DefensiveAction,
    evaluate_overtaking_opportunity, calculate_defensive_action,
    resolve_overtake_outcome
)
from services.driver_attributes import (
    get_safe_attribute,
    get_driver_aggression,
    get_driver_professionalism,
    get_vehicle_control,
    get_cornering_skill,
)


class RacingMode(Enum):
    """Driver's current racing mode"""
    ATTACK = "attack"          # Pushing hard to overtake
    DEFEND = "defend"          # Protecting position
    MANAGE = "manage"          # Conserving tires/fuel, managing gap
    CRUISE = "cruise"          # No immediate pressure


@dataclass
class DriverState:
    """
    Real-time state of a driver during race

    Tracks everything needed for AI decision-making and physics simulation.
    """
    # Identity
    driver_id: int
    driver_name: str
    driver: Driver
    team: Team

    # Physical state (updated every timestep)
    # Absolute position from start line (meters)
    position_m: float = 0.0
    prev_position_m: float = 0.0    # Previous position (for lap detection)
    velocity_mps: float = 0.0       # Current velocity (meters per second)
    lap: int = 0                    # Current lap number

    # Race situation awareness
    gap_ahead: float = 999.0        # Gap to car ahead (seconds)
    gap_behind: float = 999.0       # Gap to car behind (seconds)
    position: int = 1               # Current race position
    cars_nearby: List[int] = field(
        default_factory=list)  # Driver IDs of nearby cars

    # Strategic state
    racing_mode: RacingMode = RacingMode.MANAGE
    push_intensity: float = 0.5     # MUST be set by _update_racing_mode()
    racing_line: RacingLine = RacingLine.IDEAL  # Current racing line choice

    # Component degradation
    tire_condition: float = 1.0     # 1.0=new tires, 0.0=completely worn
    fuel_load: float = 1.0          # 1.0=full tank, 0.0=empty
    tire_compound: str = "medium"  # soft, medium, hard, rain

    # Performance modifiers
    in_slipstream: bool = False     # Currently benefiting from draft
    making_overtake: bool = False   # Currently attempting overtake

    # Incident tracking
    running: bool = True
    dnf_reason: Optional[str] = None
    # Has a DNF event already been emitted for this driver (prevents dupes)
    dnf_event_emitted: bool = False

    # Timing
    total_time: float = 0.0         # Total race time elapsed
    last_lap_time: float = 0.0      # Previous lap time
    best_lap_time: float = 999.0    # Personal best lap

    # Push fatigue and mistakes
    # Accumulated fatigue from pushing hard (0.0-1.0)
    push_fatigue: float = 0.0
    frames_since_mistake: int = 999  # Frames since last mistake (cooldown)
    # Stall detection: consecutive frames with no position change
    stall_frames: int = 0


@dataclass
class RaceState:
    """Overall race state tracking"""
    current_time: float = 0.0       # Race elapsed time (seconds)
    timestep: float = 1.0 / 30.0      # Simulation timestep (0.033s for 30 FPS)

    driver_states: Dict[int, DriverState] = field(default_factory=dict)
    lap_start_positions: Dict[int, float] = field(default_factory=dict)

    total_laps: int = 50
    track_length_m: float = 6000.0

    # For lap detection
    lap_times: Dict[int, List[float]] = field(default_factory=dict)

    # Collision tracking
    collision_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Checkered flag logic: when leader finishes, allow other drivers to finish at line
    checkered_flag_deployed: bool = False  # Set when leader completes all laps
    leader_lap_count: int = 0  # Highest lap count when checkered flag deployed


class RealtimeRaceEngine:
    """
    Real-time agent-based racing simulation engine

    Simulates racing at 30 FPS with drivers making active decisions based on
    their surroundings, attributes, and race situation.
    """

    def __init__(self, seed: Optional[int] = None, db: Optional[Any] = None):
        """Initialise engine with random generator"""
        self.rng = np.random.default_rng(seed)
        # Kept for backward compatibility with older tests that pass `db=`.
        self.db = db

        # Track-aware racing physics
        self.track_map: Optional[TrackMap] = None
        # (attacker_id, defender_id) -> attempt
        self.active_overtakes: Dict[Tuple[int, int], OvertakeAttempt] = {}
        # Recent overtake print timestamps to avoid duplicate console lines
        # key -> last printed race_state.current_time
        self._recent_overtakes: Dict[Tuple[int, int], float] = {}
        # Cooldown for overtakes between the same pair (unordered pair -> expiry time)
        self._overtake_pair_cooldown: Dict[frozenset, float] = {}

        # Physics constants
        self.BASE_SPEED_MPS = 70.0  # ~250 km/h base racing speed
        self.MAX_SPEED_MPS = 90.0   # ~324 km/h maximum speed
        self.MIN_SPEED_MPS = 30.0   # ~108 km/h minimum speed in corners

        # Performance factors
        # === SLIPSTREAM/DRAFTING EFFECT ===
        # When car is within 2 car lengths (50m) behind another, gets speed boost
        # from reduced air resistance. Real F1 data shows 5-10% boost.
        self.SLIPSTREAM_BONUS = 0.07     # 7% speed boost when drafting
        self.SLIPSTREAM_DISTANCE = 50.0  # Meters - effective draft range

        # === DIRTY AIR EFFECT - MUCH STRONGER ===
        # When following closely in corners, turbulent air reduces downforce
        # Real F1: 10-30% downforce loss, translates to ~5% speed loss in
        # corners
        # 15% speed loss in corners when following (was 5%)
        self.DIRTY_AIR_PENALTY = 0.15
        # Meters - dirty air affects up to this distance (was 100m)
        self.DIRTY_AIR_DISTANCE = 150.0
        self.TIRE_DEGRADATION_RATE = 0.00001  # Per timestep degradation
        self.FUEL_BURN_RATE = 0.00002    # Per timestep fuel consumption

        # AI decision parameters - MUCH MORE AGGRESSIVE
        self.ATTACK_THRESHOLD_GAP = 3.0  # Attack if within 3 seconds (was 1.0)
        # Defend if car within 2s behind (was 0.5s)
        self.DEFEND_THRESHOLD_GAP = 2.0
        # Consider cars within 150m as "nearby" (was 100m)
        self.NEARBY_DISTANCE_M = 150.0

        # Incident probabilities (per timestep) - Now track-aware
        self.BASE_INCIDENT_RATE = 0.0000002  # Base rate for normal driving
        self.OVERTAKE_INCIDENT_MULTIPLIER = 3.0  # Multiplier during overtakes

    def simulate_race(
        self,
        drivers: List[Driver],
        teams: Dict[int, Team],
        track: Track,
        total_laps: int = 50,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        stop_event=None,  # Threading event to signal early termination
        realtime_speed: float = 1.0,  # 1.0=real-time, 2.0=2x speed, 0.5=half speed
        # Visual track points for unified position mapping
        track_points: Optional[List[Any]] = None,
        player_driver_id: Optional[int] = None,  # Player-controlled driver ID
        player_team_driver_ids: Optional[List[int]] = None,  # Player-controlled team car IDs
        # Player's pace and overtake settings
        player_overrides: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Simulate complete race with real-time updates

        Args:
            drivers: List of participating drivers
            teams: Dictionary of teams by ID
            track: Track information
            total_laps: Number of laps to race
            event_callback: Callback for position updates and events
            realtime_speed: Simulation speed multiplier

        Returns:
            Final race results
        """
        # Initialise track map for racing physics
        print(f"-> Generating track map for {track.name}...")
        self.track_map = TrackMap(track=track)
        # Keep a reference to the external event callback so internal
        # helpers (overtake resolution / collision detection) can emit
        # DNF events for both parties when necessary.
        self._event_callback = event_callback
        print(f"  OK Track map ready: {len(self.track_map.corners)} corners, {len(self.track_map.drs_zones)} DRS zones")

        # Store visual track points for unified position mapping
        self.track_points = track_points
        if track_points:
            print(f"  OK Using visual track with {len(track_points)} points for position mapping")

        # Store player controls
        self.player_driver_id = player_driver_id
        self.player_team_driver_ids = {int(x) for x in (player_team_driver_ids or []) if x is not None}
        self.player_overrides = player_overrides or {}
        if player_driver_id:
            print(f"  OK Player driver ID {player_driver_id} with overrides: {self.player_overrides}")
        if self.player_team_driver_ids:
            print(f"  OK Player team-controlled drivers: {sorted(self.player_team_driver_ids)}")

        # Initialise race state
        track_length_m = track.length_km * 1000.0
        race_state = self._initialize_race(
            drivers, teams, track_length_m, total_laps)

        # Simulation loop at 30 FPS
        timestep = 1.0 / 30.0
        frame = 0

        # Emit initial positions
        if event_callback:
            event_callback(self._create_position_event(race_state, frame))

        while not self._race_finished(race_state):
            # Check if user requested stop
            if stop_event and stop_event.is_set():
                print("\n[RACE ENGINE] Stop requested - terminating simulation")
                break

            frame_start = time.time()

            # Update each driver
            for driver_id, state in race_state.driver_states.items():
                if not state.running:
                    continue

                # AI Decision Making: determine racing mode and push intensity
                self._update_racing_mode(state, race_state)

                # Calculate performance for this timestep
                speed_mps = self._calculate_speed(state, track_length_m)

                # Guard against non-finite speed values (NaN/inf) which can
                # corrupt positions and stall the race loop. Replace with a
                # conservative minimum speed and log once.
                if not np.isfinite(speed_mps):
                    print(f"  [WARN] Non-finite speed for {state.driver_name} -> replacing with MIN_SPEED_MPS")
                    speed_mps = float(self.MIN_SPEED_MPS)

                # Check for driver mistakes (overdriving)
                mistake_occurred = self._check_driver_mistake(state)
                if mistake_occurred:
                    speed_mps *= 0.3  # Massive speed loss when mistake happens

                # Update position
                distance_this_step = speed_mps * timestep
                state.prev_position_m = state.position_m
                state.position_m += distance_this_step
                state.velocity_mps = speed_mps
                # Lap completion: detect crossing start/finish line
                prev_lap = int(state.prev_position_m // track_length_m)
                curr_lap = int(state.position_m // track_length_m)
                if curr_lap > prev_lap:
                    self._complete_lap(state, race_state)

                # Accumulate total race time for this driver
                state.total_time += timestep

                # Update degradation and fatigue
                # Apply surface x compound wear multipliers
                base_deg = self.TIRE_DEGRADATION_RATE
                # Determine surface from track map (fallbacks supported)
                surf = None
                try:
                    surf = getattr(self.track_map.track, 'surface', None) or getattr(self.track_map.track, 'surface_type', None)
                except Exception:
                    surf = None

                surface_multipliers = {
                    'asphalt': 1.0,
                    'tarmac': 1.0,
                    'concrete': 1.05,
                    'gravel': 1.6,
                    'mixed': 1.3,
                    'dirt': 1.8
                }
                surf_key = (surf or '').lower()
                surface_mul = surface_multipliers.get(surf_key, 1.0)

                compound_multipliers = {
                    'soft': 1.3,
                    'medium': 1.0,
                    'hard': 0.8,
                    'rain': 1.2
                }
                comp_key = (getattr(state, 'tire_compound', 'medium') or 'medium').lower()
                comp_mul = compound_multipliers.get(comp_key, 1.0)

                degradation = base_deg * state.push_intensity * surface_mul * comp_mul
                state.tire_condition = max(0.0, state.tire_condition - degradation)
                state.fuel_load -= self.FUEL_BURN_RATE

                # --- Stall detection: if a car's position does not change for
                # a long period, mark it as stalled to avoid infinite races.
                try:
                    moved = abs(state.position_m - state.prev_position_m) > 0.01
                except Exception:
                    moved = True

                if not moved:
                    state.stall_frames += 1
                else:
                    state.stall_frames = 0

                # If stalled for > 900 frames (~30s at 30 FPS) consider it a
                # retirement to allow the race to conclude.
                if state.stall_frames > 900:
                    state.running = False
                    state.dnf_reason = 'stalled'
                    print(f"  [STALL] {state.driver_name} marked DNF (stalled) after {state.stall_frames} frames")
                    if event_callback:
                        event_callback({
                            "type": "dnf",
                            "driver_id": state.driver_id,
                            "driver_name": state.driver_name,
                            "lap": state.lap,
                            "reason": state.dnf_reason
                        })

                # Accumulate push fatigue (higher when pushing hard)
                if state.push_intensity > 0.8:
                    # Builds up faster when overdriving
                    state.push_fatigue += 0.00035 * \
                        (state.push_intensity - 0.8)
                else:
                    # Slower recovery when backing off
                    state.push_fatigue = max(0.0, state.push_fatigue - 0.00008)

                state.push_fatigue = min(1.0, state.push_fatigue)  # Cap at 1.0
                state.frames_since_mistake += 1

                # Check for incidents
                if self._check_incident(state, race_state):
                    state.running = False
                    # Emit DNF event for this driver if not already emitted
                    if hasattr(self, '_event_callback') and callable(self._event_callback) and not getattr(state, 'dnf_event_emitted', False):
                        try:
                            self._event_callback({
                                "type": "dnf",
                                "driver_id": driver_id,
                                "driver_name": state.driver_name,
                                "lap": state.lap,
                                "reason": state.dnf_reason
                            })
                            state.dnf_event_emitted = True
                        except Exception:
                            pass

            # Update race situation (gaps, positions, nearby cars)
            self._update_race_situation(race_state)

            # === COMPREHENSIVE LOGGING: Track every car every second ===
            if frame % 30 == 0:  # Every 1 second at 30 FPS
                print(f"\n[FRAME {frame}] Race time: {race_state.current_time:.1f}s")
                active_count = sum(
                    1 for s in race_state.driver_states.values() if s.running)
                print(
                    f"  Active cars: {active_count}/{len(race_state.driver_states)}")

                # Log each car's state
                for driver_id, state in sorted(
                        race_state.driver_states.items()):
                    status = "RUNNING" if state.running else f"DNF({
                        state.dnf_reason})"
                    print(f"  Car {driver_id} ({state.driver_name}): "
                          f"P{state.position} | L{state.lap} | "
                          f"pos={state.position_m:.1f}m | v={state.velocity_mps:.1f}m/s | {status}")

            # Emit position update every frame (30 FPS)
            frame += 1
            race_state.current_time += timestep

            if event_callback:
                position_event = self._create_position_event(race_state, frame)
                # Log how many positions we're sending
                if frame % 90 == 0:  # Every 3 seconds
                    print(f"  -> Emitting {len(position_event['positions'])} car positions to GUI")
                event_callback(position_event)

            # Throttle to realtime_speed if needed
            if realtime_speed < 100:  # Don't throttle if running very fast
                frame_duration = time.time() - frame_start
                target_duration = timestep / realtime_speed
                sleep_time = target_duration - frame_duration
                if sleep_time > 0:
                    time.sleep(sleep_time)

        # Compile results FIRST
        results = self._compile_results(race_state)

        # Emit race finished with results and collision log
        if event_callback:
            event_callback({
                "type": "race_finished",
                "total_laps": total_laps,
                "race_time": race_state.current_time,
                "results": results,
                "collision_log": race_state.collision_log
            })

        return results

    def simulate_single_race(
        self,
        drivers: List[Driver],
        teams: Dict[int, Team],
        track: Track,
        discipline: Optional[str] = None,
        total_laps: int = 50,
        seed: Optional[int] = None,
        verbose: bool = False,
        iterations: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Backward-compatible wrapper for older tests and API adapters."""
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        # Kept for signature compatibility.
        _ = discipline
        _ = verbose
        _ = iterations
        _ = kwargs

        # Older tests may pass teams as a list/tuple; normalize to {team_id: team}.
        if not hasattr(teams, 'get'):
            teams = {
                int(getattr(team, 'id', idx + 1)): team
                for idx, team in enumerate(list(teams))
            }

        # Ensure each driver is assigned to a valid team for race init.
        team_ids = list(teams.keys())
        if team_ids:
            for idx, driver in enumerate(drivers):
                if getattr(driver, 'current_team_id', None) not in teams:
                    setattr(driver, 'current_team_id', team_ids[idx % len(team_ids)])

        return self.simulate_race(
            drivers=drivers,
            teams=teams,
            track=track,
            total_laps=total_laps,
        )

    def _initialize_race(
        self,
        drivers: List[Driver],
        teams: Dict[int, Team],
        track_length_m: float,
        total_laps: int
    ) -> RaceState:
        """Initialise race with starting grid"""
        race_state = RaceState(
            total_laps=total_laps,
            track_length_m=track_length_m
        )

        # Create driver states in grid order
        for i, driver in enumerate(drivers):
            team = teams.get(driver.current_team_id)
            if not team:
                continue

            # Stagger starting positions: each car gets a unique longitudinal
            # position on the circuit. The previous spacing (10.0m) was below
            # the engine's safe following distance and caused many collisions
            # on the opening laps. Increase spacing to reduce first-lap contacts.
            # NOTE: SAFE_FOLLOWING_DISTANCE used in collision detection is
            # approximately 15.0m, so pick a spacing comfortably above that.
            starting_position = i * 20.0  # 20m spacing between all cars

            # Calculate initial push intensity based on driver personality
            raw_speed = get_safe_attribute(driver, 'speed') / 100.0
            aggression = get_driver_aggression(driver) / 100.0
            # Risk is derived from professionalism: less professional -> more risk
            professionalism = get_driver_professionalism(driver)
            risk = (100.0 - professionalism) / 100.0
            # Range: 0.3 to 1.0
            initial_push = 0.3 + (raw_speed * 0.2) + \
                (aggression * 0.3) + (risk * 0.2)

            state = DriverState(
                driver_id=driver.id,
                driver_name=driver.name,
                driver=driver,
                team=team,
                position_m=starting_position,
                position=i + 1,
                lap=0,
                push_fatigue=0.0,
                frames_since_mistake=999,
                push_intensity=initial_push
            )

            print(f"  [INIT] {driver.name}: speed={get_safe_attribute(driver,'speed'):.1f} -> initial_push={initial_push:.2f}")

            race_state.driver_states[driver.id] = state
            race_state.lap_times[driver.id] = []

        return race_state

    def _update_racing_mode(self, state: DriverState, race_state: RaceState):
        """
        AI Decision Making: Update driver's racing mode and push intensity

        Uses advanced track-aware overtaking evaluation.
        For player-controlled drivers, overrides are applied from live UI controls.
        """
        driver = state.driver

        # Check if this is a player-controlled car (selected driver or teammate)
        controlled_driver = (
            (hasattr(self, 'player_driver_id') and self.player_driver_id == state.driver_id)
            or (hasattr(self, 'player_team_driver_ids') and state.driver_id in getattr(self, 'player_team_driver_ids', set()))
        )

        if controlled_driver:
            # Apply player overrides from UI sliders
            if hasattr(self, 'player_overrides') and self.player_overrides:
                # Use combined push intensity (average of pace and overtake
                # sliders)
                if 'push' in self.player_overrides:
                    old_push = state.push_intensity
                    state.push_intensity = self.player_overrides['push']

                    # Debug first application
                    if not hasattr(self, '_player_push_logged'):
                        self._player_push_logged = True
                        print(f"[PLAYER PUSH APPLIED] {driver.name}: {old_push:.2f} -> {state.push_intensity:.2f} (from sliders)")

                # Overtake slider affects racing mode only
                if 'overtake' in self.player_overrides:
                    overtake_multiplier = self.player_overrides['overtake']

                    # More aggressive overtaking with higher slider value
                    if state.gap_ahead < (
                            self.ATTACK_THRESHOLD_GAP * (1.5 - overtake_multiplier * 0.5)) and overtake_multiplier > 0.3:
                        state.racing_mode = RacingMode.ATTACK
                    elif state.gap_behind < self.DEFEND_THRESHOLD_GAP:
                        state.racing_mode = RacingMode.DEFEND
                    else:
                        state.racing_mode = RacingMode.MANAGE

                # Debug: Log player control every 5 seconds (150 frames at 30
                # FPS)
                if not hasattr(self, '_player_log_counter'):
                    self._player_log_counter = 0
                self._player_log_counter += 1
                if self._player_log_counter % 150 == 0:
                    print(
                        f"[PLAYER CONTROL] {
                            driver.name}: push={
                            state.push_intensity:.2f}, mode={
                            state.racing_mode.value}, gap_ahead={
                            state.gap_ahead:.1f}s")

                # Player control complete - skip AI logic
                return

        # *** AI DRIVERS: USE ATTRIBUTES TO CREATE DRAMATIC VARIATION ***
        # Use driver's actual canonical attributes to determine natural pace
        raw_speed = get_safe_attribute(driver, 'speed') / 100.0  # 0.0 to 1.0
        aggression = get_driver_aggression(driver) / 100.0
        consistency = get_safe_attribute(driver, 'consistency') / 100.0
        # Risk tolerance derived from professionalism
        professionalism = get_driver_professionalism(driver)
        risk_tolerance = (100.0 - professionalism) / 100.0

        # Base push intensity from driver personality (0.4 to 1.0)
        # Aggressive, high-risk drivers naturally push harder
        base_push = 0.4 + (raw_speed * 0.2) + \
            (aggression * 0.2) + (risk_tolerance * 0.2)
        # Add small per-driver variability (less for consistent drivers)
        variability = (1.0 - consistency) * self.rng.uniform(-0.05, 0.05)
        base_push = max(0.35, min(1.0, base_push + variability))
        state.push_intensity = base_push

        # Track-aware overtaking evaluation
        if state.gap_ahead < self.ATTACK_THRESHOLD_GAP and state.position > 1:
            # Find car ahead
            car_ahead = self._get_car_ahead(state, race_state)
            if car_ahead and self.track_map:
                # Get track section and corner data
                section_type, corner = self.track_map.get_section_at_position(
                    state.position_m % race_state.track_length_m
                )

                # Evaluate overtaking opportunity
                gap_m = state.gap_ahead * state.velocity_mps

                should_attempt, success_prob, attempt_type = evaluate_overtaking_opportunity(
                    attacker=driver,
                    defender=car_ahead.driver,
                    attacker_speed_kmh=state.velocity_mps * 3.6,
                    defender_speed_kmh=car_ahead.velocity_mps * 3.6,
                    gap_m=gap_m,
                    section=section_type,
                    corner=corner
                )

                if should_attempt:
                    # Start overtaking attempt - PUSH MUCH HARDER FOR
                    # AGGRESSIVE OVERTAKING
                    state.racing_mode = RacingMode.ATTACK
                    state.push_intensity = min(
                        # +35% when attacking (was +15%)
                        1.0, base_push + 0.35)

                    # Log overtake attempts for visibility
                    if not hasattr(self, '_overtake_log_counter'):
                        self._overtake_log_counter = 0
                    self._overtake_log_counter += 1
                    if self._overtake_log_counter % 30 == 1:  # Log once per second
                        print(f"  OVERTAKING: {driver.name} attempting to overtake {car_ahead.driver.name}! Gap: {gap_m:.1f}m, Success chance: {success_prob * 100:.0f}%")

                    # Create or update active overtake (respect pair cooldown)
                    key = (state.driver_id, car_ahead.driver_id)
                    pair_key = frozenset((state.driver_id, car_ahead.driver_id))
                    cooldown_expiry = self._overtake_pair_cooldown.get(pair_key, 0.0)
                    if race_state.current_time < cooldown_expiry:
                        # Skip creating a new attempt during cooldown window
                        pass
                    else:
                        if key not in self.active_overtakes:
                            self.active_overtakes[key] = OvertakeAttempt(
                            attacker_id=state.driver_id,
                            defender_id=car_ahead.driver_id,
                            attempt_type=attempt_type,
                                position_m=state.position_m,
                                gap_m=gap_m,
                                speed_advantage_kmh=(
                                    state.velocity_mps - car_ahead.velocity_mps) * 3.6,
                                corner=corner
                        )
                else:
                    state.racing_mode = RacingMode.MANAGE
                    # Stay at base push when managing
            else:
                # Fallback to simple logic
                state.racing_mode = RacingMode.ATTACK
                state.push_intensity = min(1.0, base_push + 0.15)

        elif state.gap_behind < self.DEFEND_THRESHOLD_GAP and state.position < len(race_state.driver_states):
            # Defensive driving with track awareness
            car_behind = self._get_car_behind(state, race_state)
            if car_behind and self.track_map:
                section_type, corner = self.track_map.get_section_at_position(
                    state.position_m % race_state.track_length_m
                )

                # Convert gap from seconds to meters
                gap_m = state.gap_behind * state.velocity_mps

                # Calculate defensive action
                _, racing_line = calculate_defensive_action(
                    defender=driver,
                    attacker=car_behind.driver,
                    gap_m=gap_m,
                    section=section_type,
                    corner=corner
                )

                state.racing_mode = RacingMode.DEFEND
                # Push slightly harder when defending
                state.push_intensity = min(1.0, base_push + 0.10)
                state.racing_line = racing_line
            else:
                state.racing_mode = RacingMode.DEFEND
                state.push_intensity = min(1.0, base_push + 0.10)

        elif state.gap_ahead > 3.0 and state.gap_behind > 3.0:
            # Comfortable gap - conservative drivers back off more
            state.racing_mode = RacingMode.MANAGE
            # Consistent drivers conserve more
            conservation_factor = 1.0 - (consistency * 0.3)
            state.push_intensity = base_push * conservation_factor
            state.racing_line = RacingLine.IDEAL

        else:
            # Cruising - use base pace
            state.racing_mode = RacingMode.CRUISE
            state.push_intensity = base_push
            state.racing_line = RacingLine.IDEAL

        # Tire condition affects push - SIGNIFICANT IMPACT
        if state.tire_condition < 0.7:
            # Can drop to 50% when tires dead
            tire_factor = 0.5 + (state.tire_condition * 0.5)
            state.push_intensity *= tire_factor

        # Add some lap-to-lap variation for excitement
        variance = (1.0 - consistency) * 0.15  # Inconsistent drivers vary more
        state.push_intensity += self.rng.normal(0, variance)
        state.push_intensity = np.clip(
            state.push_intensity, 0.3, 1.0)  # Wider range

    def _calculate_speed(
        self,
        state: DriverState,
        track_length_m: float
    ) -> float:
        """
        Calculate current speed with DRAMATIC variation based on push_intensity

        Returns speed in meters per second.
        """
        driver = state.driver
        team = state.team

        # Base speed from driver canonical skill and team capability
        raw_speed = get_safe_attribute(driver, 'speed') / 100.0
        cornering_skill = get_cornering_skill(driver) / 100.0
        team_performance = self._get_team_multiplier(team)

        # *** PUSH INTENSITY IS THE DOMINANT FACTOR ***
        # Base speed: 80 m/s (288 km/h) - this is just the reference point
        reference_speed = 80.0

        # Push multiplier creates MASSIVE speed differences
        # Conservative (0.5): 0.60x = 48 m/s (173 km/h) - VERY SLOW
        # Balanced (0.7): 0.92x = 74 m/s (266 km/h) - Normal racing
        # Aggressive (1.0): 1.30x = 104 m/s (374 km/h) - FLYING
        push_multiplier = 0.20 + (state.push_intensity * 1.10)

        # Driver skill modifies slightly (5-10% variation)
        driver_modifier = 0.95 + (raw_speed * 0.10)

        # Team performance adds small bonus (0-5%)
        team_modifier = 0.975 + (team_performance * 0.05)

        # Cornering skill affects corners only
        in_corner = self._is_in_corner_proxy(state, track_length_m)

        if in_corner:
            # 85-100% speed in corners
            corner_modifier = 0.85 + (cornering_skill * 0.15)
        else:
            corner_modifier = 1.0  # Full speed on straights

        # Calculate final speed
        speed = reference_speed * push_multiplier * \
            driver_modifier * team_modifier * corner_modifier

        self._log_speed_debug(state, push_multiplier, speed)

        # Tire degradation - worn tires lose grip
        tire_penalty = 1.0 - (1.0 - state.tire_condition) * 0.25
        speed *= tire_penalty

        # Fuel weight - lighter car is faster
        fuel_bonus = 1.0 + (1.0 - state.fuel_load) * 0.03
        speed *= fuel_bonus

        # Push fatigue - accumulated stress from pushing hard
        # Increases mistake probability and slightly reduces performance
        if state.push_fatigue > 0.3:
            # Up to 25% slower when exhausted
            fatigue_penalty = 1.0 - (state.push_fatigue * 0.25)
            speed *= fatigue_penalty

        # === SLIPSTREAM BOOST (straights) ===
        if state.in_slipstream:
            speed *= (1.0 + self.SLIPSTREAM_BONUS)

        speed = self._apply_dirty_air_penalty(speed, state, track_length_m)

        speed = self._apply_collision_avoidance(speed, state)

        # Consistency variance
        consistency = get_safe_attribute(driver, 'consistency') / 100.0
        speed_variance = (1.0 - consistency) * 0.05
        speed *= (1.0 + self.rng.normal(0, speed_variance))

        # Clamp to realistic bounds
        return np.clip(speed, self.MIN_SPEED_MPS, self.MAX_SPEED_MPS)

    def _is_in_corner_proxy(self, state: DriverState, track_length_m: float) -> bool:
        """Approximate corner occupancy using lap-phase sine proxy."""
        position_in_lap = (state.position_m % track_length_m) / track_length_m
        return abs(np.sin(position_in_lap * 2 * np.pi * 8)) > 0.5

    def _log_speed_debug(self, state: DriverState, push_multiplier: float, speed: float) -> None:
        """Emit throttled speed diagnostics for early frames and periodic checkpoints."""
        if not hasattr(self, '_speed_debug_counter'):
            self._speed_debug_counter = 0
        self._speed_debug_counter += 1
        if self._speed_debug_counter < 50 or self._speed_debug_counter % 300 == 0:
            print(
                f"  [SPEED] {state.driver_name}: push={state.push_intensity:.2f} -> mult={push_multiplier:.2f} -> speed={speed:.1f}m/s")

    def _apply_dirty_air_penalty(self, speed: float, state: DriverState, track_length_m: float) -> float:
        """Apply corner dirty-air speed penalty when following too closely."""
        if not (hasattr(self, 'track_map') and self.track_map):
            return speed

        position_on_track = state.position_m % track_length_m
        section_type, _ = self.track_map.get_section_at_position(position_on_track)
        is_corner = section_type in [
            TrackSection.SLOW_CORNER,
            TrackSection.MEDIUM_CORNER,
            TrackSection.FAST_CORNER,
            TrackSection.BRAKING_ZONE,
        ]

        if is_corner and state.velocity_mps > 1.0 and state.gap_ahead < self.DIRTY_AIR_DISTANCE / state.velocity_mps:
            return speed * (1.0 - self.DIRTY_AIR_PENALTY)
        return speed

    def _apply_collision_avoidance(self, speed: float, state: DriverState) -> float:
        """Reduce speed when gap to car ahead is physically unsafe."""
        if state.gap_ahead >= 0.8 or state.velocity_mps <= 0.1:
            return speed

        car_length = 4.0
        minimum_gap = car_length * 1.2
        distance_gap = state.gap_ahead * state.velocity_mps
        if distance_gap >= minimum_gap:
            return speed

        safety_factor = max(0.65, distance_gap / minimum_gap)
        speed *= safety_factor
        if distance_gap < car_length * 0.7:
            speed *= 0.75
        return speed

    def _get_team_multiplier(self, team: Team) -> float:
        """Get team performance multiplier"""
        tier_values = {"tier1": 0.95, "tier2": 0.75, "tier3": 0.55}
        base = tier_values.get(team.tier.lower(), 0.75)

        # Budget factor
        budget_factor = min(team.budget / 200.0, 1.0) * 0.2

        return min(base + budget_factor, 1.0)

    def _update_race_situation(self, race_state: RaceState):
        """Update gaps, positions, nearby cars, slipstream status"""
        # Sort drivers by position
        active_drivers = [
            (did,
             state) for did,
            state in race_state.driver_states.items() if state.running]
        active_drivers.sort(key=lambda x: (-x[1].lap, -x[1].position_m))

        # Update positions and gaps
        for i, (driver_id, state) in enumerate(active_drivers):
            state.position = i + 1

            # Gap ahead (in SECONDS, not laps)
            if i > 0:
                ahead_state = active_drivers[i - 1][1]

                # Calculate PHYSICAL distance gap first (for slipstream check)
                if ahead_state.lap == state.lap:
                    # Same lap - simple distance
                    distance_gap = ahead_state.position_m - state.position_m
                elif ahead_state.lap > state.lap:
                    # Car ahead is on later lap - calculate wrap-around
                    # distance
                    distance_gap = (
                        race_state.track_length_m - state.position_m) + ahead_state.position_m
                else:
                    # We're ahead in lap count (shouldn't happen with proper
                    # sorting)
                    distance_gap = race_state.track_length_m

                # Convert distance to TIME GAP for display
                if ahead_state.lap == state.lap:
                    # Same lap - normal time gap
                    if state.velocity_mps > 0.1:
                        state.gap_ahead = distance_gap / state.velocity_mps
                    else:
                        # Car is stationary/very slow - use base speed for gap
                        # estimate
                        state.gap_ahead = distance_gap / self.BASE_SPEED_MPS if distance_gap > 0 else 0.0
                elif ahead_state.lap > state.lap:
                    # Different lap - encode as 999+N for GUI display
                    lap_diff = ahead_state.lap - state.lap
                    state.gap_ahead = 999.0 + lap_diff  # e.g., 1000.0 means +1 lap
                else:
                    state.gap_ahead = 999.0

                # Check slipstream (within effective draft range, same lap
                # only)
                if distance_gap < self.SLIPSTREAM_DISTANCE and ahead_state.lap == state.lap:
                    state.in_slipstream = True
                else:
                    state.in_slipstream = False
            else:
                state.gap_ahead = 999.0
                state.in_slipstream = False

            # Gap behind
            if i < len(active_drivers) - 1:
                behind_state = active_drivers[i + 1][1]
                if behind_state.lap == state.lap:
                    distance_gap = state.position_m - behind_state.position_m
                    state.gap_behind = distance_gap / self.BASE_SPEED_MPS
                elif state.lap > behind_state.lap:
                    # Car behind is on earlier lap - show as +N laps
                    lap_diff = state.lap - behind_state.lap
                    state.gap_behind = 999.0 + lap_diff  # e.g., 1000.0 means +1 lap
                else:
                    state.gap_behind = 999.0
            else:
                state.gap_behind = 999.0

            # Nearby cars (within 100m on same lap)
            state.cars_nearby = []
            for other_id, other_state in race_state.driver_states.items():
                if other_id != driver_id and other_state.running and other_state.lap == state.lap:
                    distance = abs(other_state.position_m - state.position_m)
                    if distance < self.NEARBY_DISTANCE_M:
                        state.cars_nearby.append(other_id)

    def _complete_lap(self, state: DriverState, race_state: RaceState):
        """Handle lap completion"""
        state.lap += 1

        # Calculate lap time
        if state.lap > 0:
            lap_start_pos = race_state.lap_start_positions.get(
                state.driver_id, 0.0)
            lap_distance = state.position_m - lap_start_pos
            lap_time = lap_distance / state.velocity_mps if state.velocity_mps > 0 else 90.0

            state.last_lap_time = lap_time
            if lap_time < state.best_lap_time:
                state.best_lap_time = lap_time

            race_state.lap_times[state.driver_id].append(lap_time)

        race_state.lap_start_positions[state.driver_id] = state.position_m
        
        # Check if this driver completed all required laps
        if state.lap >= race_state.total_laps:
            state.running = False
            # If this is the first driver to finish, deploy checkered flag
            if not race_state.checkered_flag_deployed:
                race_state.checkered_flag_deployed = True
                race_state.leader_lap_count = state.lap
        # If checkered flag is deployed, finish any driver crossing the line
        elif race_state.checkered_flag_deployed:
            state.running = False

    def _check_driver_mistake(self, state: DriverState) -> bool:
        """
        Check if driver makes a mistake (runs wide, locks up, etc.)

        Probability increases with:
        - High push_intensity (overdriving)
        - Low consistency skill
        - Accumulated fatigue
        - Worn tires

        Returns True if mistake occurs (causing time loss)
        """
        # Don't check too frequently - cooldown period
        if state.frames_since_mistake < 150:  # 5 seconds cooldown
            return False

        # Base mistake probability per frame - INCREASED 10x for visibility
        base_probability = 0.0002

        # *** PUSH INTENSITY MULTIPLIER ***
        # Conservative (0.5): 0.5x mistakes
        # Balanced (0.7): 1.0x mistakes
        # Aggressive (1.0): 5.0x mistakes (MUCH higher risk)
        if state.push_intensity > 0.8:
            push_risk = 1.0 + ((state.push_intensity - 0.8)
                               * 20.0)  # Exponential increase
        else:
            push_risk = state.push_intensity / 0.7  # Linear below aggressive threshold

        # Driver skill reduces mistakes
        consistency = get_safe_attribute(state.driver, 'consistency') / 100.0
        vehicle_control = get_vehicle_control(state.driver) / 100.0
        # Range: 0.0 to 2.0
        skill_factor = 2.0 - (consistency + vehicle_control)

        # Fatigue increases mistakes
        # Up to 4x when exhausted
        fatigue_multiplier = 1.0 + (state.push_fatigue * 3.0)

        # Tire condition affects grip
        # Up to 3x on worn tires
        tire_multiplier = 1.0 + ((1.0 - state.tire_condition) * 2.0)

        # Calculate final probability
        mistake_prob = base_probability * push_risk * \
            skill_factor * fatigue_multiplier * tire_multiplier

        # Roll the dice
        if self.rng.random() < mistake_prob:
            state.frames_since_mistake = 0
            # Determine severity
            severity = "minor" if self.rng.random() > 0.3 else "major"
            if severity == "major":
                print(f"  WARNING: {state.driver_name} runs wide! (push={state.push_intensity:.2f}, fatigue={state.push_fatigue:.2f})")
            return True

        return False

    def _check_incident(self, state: DriverState,
                        race_state: RaceState) -> bool:
        """
        *** PHYSICS-BASED COLLISION DETECTION ***

        NO RANDOM PROBABILITY - Collisions emerge from actual position overlap!

        Returns True if driver suffers incident (DNF).

        Detection logic:
        1. Check if car occupies same physical space as another car
        2. If position difference < CAR_LENGTH and on same lap
        3. Check if it's a racing incident (both at fault) or solo spin
        4. Use driver skill to determine if they can avoid/recover
        """
        # Update active overtakes
        self._resolve_active_overtakes(race_state)

        # === POSITION-BASED COLLISION DETECTION ===
        # Collisions occur when two cars occupy the same physical space
        CAR_LENGTH = 4.0  # meters (20% smaller cars)
        SAFE_FOLLOWING_DISTANCE = 15.0  # minimum safe gap (unchanged)

        # Check all other cars
        for other_id, other_state in race_state.driver_states.items():
            if other_id == state.driver_id or not other_state.running:
                continue

            # Only check cars on same lap (or within track length wrap)
            if other_state.lap != state.lap:
                continue

            # Longitudinal separation (along track)
            longitudinal_gap = abs(
                state.position_m - other_state.position_m) % race_state.track_length_m
            if longitudinal_gap > race_state.track_length_m / 2:
                longitudinal_gap = race_state.track_length_m - longitudinal_gap

            # If cars are very close longitudinally
            if longitudinal_gap < SAFE_FOLLOWING_DISTANCE:
                # Assume lateral separation based on racing behaviour
                # Cars in ATTACK/DEFEND mode are trying to overtake (side-by-side)
                # Cars in MANAGE/CRUISE maintain racing line (not side-by-side)

                is_overtaking = (state.racing_mode == RacingMode.ATTACK or
                                 state.racing_mode == RacingMode.DEFEND or
                                 other_state.racing_mode == RacingMode.ATTACK or
                                 other_state.racing_mode == RacingMode.DEFEND)

                if is_overtaking and longitudinal_gap < CAR_LENGTH * 1.5:
                    # Side-by-side racing - small chance of contact
                    # Skill determines if they can race wheel-to-wheel safely
                    # Use canonical-derived helpers instead of legacy fields
                    my_vehicle_control = get_vehicle_control(state.driver)
                    my_reactions = get_safe_attribute(state.driver, 'reactions')
                    my_racecraft = (my_vehicle_control + my_reactions + get_safe_attribute(state.driver, 'racecraft')) / 300.0

                    other_vehicle_control = get_vehicle_control(other_state.driver)
                    other_reactions = get_safe_attribute(other_state.driver, 'reactions')
                    other_racecraft = (other_vehicle_control + other_reactions + get_safe_attribute(other_state.driver, 'racecraft')) / 300.0

                    combined_skill = (my_racecraft + other_racecraft) / 2.0

                    # Tire condition affects car control
                    control_factor = min(
                        state.tire_condition, other_state.tire_condition)

                    # Very small chance of contact even with good skills
                    # Reduce baseline contact probability to make DNFs rarer
                    contact_probability = 0.0000002 * \
                        (1.0 - combined_skill * control_factor)

                    if self.rng.random() < contact_probability:
                        state.dnf_reason = "contact_during_overtake"
                        other_state.running = False
                        other_state.dnf_reason = "contact_during_overtake"
                        print(f"  *** RACING INCIDENT! {state.driver_name} and {other_state.driver_name} "
                              f"made contact at position {state.position_m:.0f}m")
                        # Log collision with both drivers
                        race_state.collision_log.append({
                            "lap": state.lap,
                            "time": race_state.current_time,
                            "position_m": state.position_m,
                            "type": "contact_during_overtake",
                            "driver1_id": state.driver_id,
                            "driver1_name": state.driver_name,
                            "driver2_id": other_state.driver_id,
                            "driver2_name": other_state.driver_name,
                            "description": f"{state.driver_name} and {other_state.driver_name} collided during overtake"
                        })
                        # Emit DNF event for the other driver (state will be
                        # emitted by the caller's event path). This ensures the
                        # GUI is notified for both parties even if the main loop
                        # skips the other driver later.
                        try:
                            if hasattr(self, '_event_callback') and callable(self._event_callback) and not getattr(other_state, 'dnf_event_emitted', False):
                                self._event_callback({
                                    "type": "dnf",
                                    "driver_id": other_state.driver_id,
                                    "driver_name": other_state.driver_name,
                                    "lap": other_state.lap,
                                    "reason": other_state.dnf_reason
                                })
                                other_state.dnf_event_emitted = True
                        except Exception:
                            pass
                        return True

                elif not is_overtaking and longitudinal_gap < CAR_LENGTH:
                    # Not overtaking but too close = potential rear-end
                    # Only trigger if rear car is going significantly faster
                    # (actual rear-end scenario)
                    relative_velocity = state.velocity_mps - other_state.velocity_mps

                    # Determine who is behind
                    if state.position_m < other_state.position_m:
                        # Other car is ahead - state is behind
                        # Closing at >15 m/s = real rear-end risk (increased
                        # from 5)
                        if relative_velocity > 15.0:
                                # Instead of immediate DNF, make rear-end collisions
                                # probabilistic and much less likely to retire a car.
                                # Skillful drivers are less likely to cause a DNF.
                                my_vehicle_control = get_vehicle_control(state.driver)
                                other_vehicle_control = get_vehicle_control(other_state.driver)
                                combined_control = (my_vehicle_control + other_vehicle_control) / 200.0  # 0..1

                                # Severity scales with closing speed beyond threshold
                                severity = min(1.0, (relative_velocity - 15.0) / 15.0)

                                # Base DNF probability at threshold (12%), scales with severity
                                base_rear_end_dnf = 0.12
                                dnf_probability = base_rear_end_dnf * severity * (1.0 - combined_control)

                                if self.rng.random() < dnf_probability:
                                    print(
                                        f"  *** REAR-END! {state.driver_name} hit {other_state.driver_name}")
                                    state.dnf_reason = "rear_end_collision"
                                    # Log collision with both drivers
                                    race_state.collision_log.append({
                                        "lap": state.lap,
                                        "time": race_state.current_time,
                                        "position_m": state.position_m,
                                        "type": "rear_end_collision",
                                        "driver1_id": state.driver_id,
                                        "driver1_name": state.driver_name,
                                        "driver2_id": other_state.driver_id,
                                        "driver2_name": other_state.driver_name,
                                        "description": f"{state.driver_name} rear-ended {other_state.driver_name}"
                                    })
                                    return True
                                else:
                                    # Minor contact / fender-bender: reduce grip and log
                                    print(
                                        f"  !!! NEAR MISS/CONTACT (no DNF): {state.driver_name} & {other_state.driver_name} - closing {relative_velocity:.1f}m/s")
                                    # Apply small damage/penalty so incident is meaningful
                                    state.tire_condition = max(0.2, state.tire_condition - 0.12)
                                    other_state.tire_condition = max(0.2, other_state.tire_condition - 0.08)
                                    race_state.collision_log.append({
                                        "lap": state.lap,
                                        "time": race_state.current_time,
                                        "position_m": state.position_m,
                                        "type": "rear_end_contact_minor",
                                        "driver1_id": state.driver_id,
                                        "driver1_name": state.driver_name,
                                        "driver2_id": other_state.driver_id,
                                        "driver2_name": other_state.driver_name,
                                        "description": f"Minor rear contact between {state.driver_name} and {other_state.driver_name} (no DNF)"
                                    })
                    else:
                        # State is ahead - other car is behind
                        if relative_velocity < -5.0:  # Other car closing fast
                            # Other car will hit this car next frame
                            pass  # Let it be handled when other car is checked

        # === SOLO INCIDENTS (mechanical, tire failure) ===
        # Very rare - only if tires are completely dead or mechanical issues
        if state.tire_condition < 0.1:
            # Tires are destroyed - high chance of spin
            consistency = state.driver.consistency / 100.0
            if self.rng.random() > consistency:
                state.dnf_reason = "tire_failure_spin"
                print(f"  X {state.driver_name} spins off - tire condition critical!")
                return True

        # Mechanical DNF (extremely rare)
        if self.rng.random() < 0.00001:  # 0.001% per frame
            state.dnf_reason = "mechanical"
            print(f"  X {state.driver_name} retires - mechanical failure!")
            return True

        return False

    def _resolve_active_overtakes(self, race_state: RaceState):
        """
        Resolve all active overtaking attempts

        Updates positions and tracks incidents from wheel-to-wheel combat.
        """
        if not self.track_map:
            return

        # Update each active overtake
        completed_attempts = []

        for key, attempt in self.active_overtakes.items():
            attacker_id, defender_id = key
            attacker_state = race_state.driver_states.get(attacker_id)
            defender_state = race_state.driver_states.get(defender_id)

            if not attacker_state or not defender_state:
                completed_attempts.append(key)
                continue

            if not attacker_state.running or not defender_state.running:
                completed_attempts.append(key)
                continue

            # Get track section
            position_on_track = attacker_state.position_m % race_state.track_length_m
            _, _ = self.track_map.get_section_at_position(position_on_track)

            # Calculate lateral overlap (simulated from speed difference)
            speed_diff = attacker_state.velocity_mps - defender_state.velocity_mps
            gap_meters = attacker_state.gap_ahead * attacker_state.velocity_mps

            # Estimate lateral overlap based on gap closing rate
            if gap_meters < 5.0:  # Very close - side by side
                lateral_overlap = min(0.8, 0.2 + (5.0 - gap_meters) * 0.12)
            else:
                lateral_overlap = max(
                    0.0, attempt.lateral_overlap - 0.05)  # Decay if not close

            # Update attempt state
            attempt.gap_m = gap_meters
            attempt.speed_advantage_kmh = speed_diff * 3.6
            attempt.lateral_overlap = lateral_overlap

            # Update frames
            timestep = 1.0 / 30.0  # 30 FPS
            outcome = attempt.update(timestep)

            # Check if attempt should be resolved (use outcome from update or
            # resolve manually)
            if outcome or attempt.frames_active > 30 or lateral_overlap > 0.7 or attacker_state.gap_ahead > 2.0:
                # Use outcome from update() or resolve manually
                if not outcome:
                    result, _ = resolve_overtake_outcome(
                        attacker=attacker_state.driver,
                        defender=defender_state.driver,
                        overtake_attempt=attempt,
                        rng=self.rng
                    )
                else:
                    result = outcome

                if result == "success":
                    # Prevent immediate duplicate prints for the same pair
                    last_print = self._recent_overtakes.get(key)
                    # If we printed this overtake within the last 0.8s, skip
                    if last_print is None or (race_state.current_time - last_print) > 0.8:
                        print(f"  OK {attacker_state.driver_name} overtakes {defender_state.driver_name}! ({attempt.attempt_type.value})")
                        self._recent_overtakes[key] = race_state.current_time
                    # Nudge the attacker ahead of the defender so positions reflect
                    # the successful overtake on the next sorting update.
                    try:
                        # Place attacker ahead of defender by a safe margin (CAR_LENGTH + 1m)
                        SAFE_NUDGE = 5.0
                        attacker_state.position_m = defender_state.position_m + SAFE_NUDGE
                        # Give attacker a small velocity bump to reflect momentum
                        attacker_state.velocity_mps = max(attacker_state.velocity_mps, defender_state.velocity_mps + 0.5)
                        # Add a short cooldown for this pair to avoid immediate reversal
                        pair_key_done = frozenset((attacker_state.driver_id, defender_state.driver_id))
                        self._overtake_pair_cooldown[pair_key_done] = race_state.current_time + 1.0
                        # Log overtake event into collision_log (reuse for events)
                        race_state.collision_log.append({
                            "time": race_state.current_time,
                            "lap": attacker_state.lap,
                            "position_m": attacker_state.position_m,
                            "type": "overtake",
                            "attacker_id": attacker_state.driver_id,
                            "attacker_name": attacker_state.driver_name,
                            "defender_id": defender_state.driver_id,
                            "defender_name": defender_state.driver_name,
                            "attempt_type": attempt.attempt_type.value,
                            "description": f"{attacker_state.driver_name} overtook {defender_state.driver_name} ({attempt.attempt_type.value})"
                        })
                    except Exception:
                        pass
                elif result == "incident":
                    # Collision occurred
                    # For simplicity, both cars out (can refine later with
                    # fault assignment)
                    attacker_state.running = False
                    attacker_state.dnf_reason = "collision"
                    defender_state.running = False
                    defender_state.dnf_reason = "collision"
                    print(f"  COLLISION! {attacker_state.driver_name} and {defender_state.driver_name} crash!")
                    # Emit DNF events for both parties if an external event
                    # callback is available and we haven't previously emitted
                    # for these drivers.
                    try:
                        if hasattr(self, '_event_callback') and callable(self._event_callback):
                            if not getattr(attacker_state, 'dnf_event_emitted', False):
                                self._event_callback({
                                    'type': 'dnf',
                                    'driver_id': attacker_state.driver_id,
                                    'driver_name': attacker_state.driver_name,
                                    'lap': attacker_state.lap,
                                    'reason': attacker_state.dnf_reason
                                })
                                attacker_state.dnf_event_emitted = True
                            if not getattr(defender_state, 'dnf_event_emitted', False):
                                self._event_callback({
                                    'type': 'dnf',
                                    'driver_id': defender_state.driver_id,
                                    'driver_name': defender_state.driver_name,
                                    'lap': defender_state.lap,
                                    'reason': defender_state.dnf_reason
                                })
                                defender_state.dnf_event_emitted = True
                    except Exception:
                        pass
                else:
                    # Failed attempt - defender holds position
                    pass

                completed_attempts.append(key)

        # Remove completed attempts
        for key in completed_attempts:
            del self.active_overtakes[key]

    def _get_car_ahead(self, state: DriverState,
                       race_state: RaceState) -> Optional[DriverState]:
        """Find the car directly ahead"""
        ahead_car = None
        min_gap = float('inf')

        for other_state in race_state.driver_states.values():
            if other_state.driver_id == state.driver_id or not other_state.running:
                continue
            if other_state.position == state.position - 1:
                gap = state.position_m - other_state.position_m if state.lap == other_state.lap else 999
                if gap < min_gap:
                    min_gap = gap
                    ahead_car = other_state

        return ahead_car

    def _get_car_behind(self, state: DriverState,
                        race_state: RaceState) -> Optional[DriverState]:
        """Find the car directly behind"""
        behind_car = None
        min_gap = float('inf')

        for other_state in race_state.driver_states.values():
            if other_state.driver_id == state.driver_id or not other_state.running:
                continue
            if other_state.position == state.position + 1:
                gap = other_state.position_m - \
                    state.position_m if state.lap == other_state.lap else 999
                if gap < min_gap:
                    min_gap = gap
                    behind_car = other_state

        return behind_car

    def _race_finished(self, race_state: RaceState) -> bool:
        """Check if race is complete with checkered flag logic
        
        Two-phase finishing:
        1. When leader completes all laps, deploy checkered flag
        2. Other drivers finish when they cross the line (don't need full laps)
        3. Race ends when all drivers have finished or DNF'd
        """
        # Get all drivers who are still running (not DNF)
        active_drivers = [
            s for s in race_state.driver_states.values() if s.running]

        # If no one is running, race is over
        if not active_drivers:
            return True

        # If checkered flag not yet deployed, check if leader finished
        if not race_state.checkered_flag_deployed:
            leader_laps = max(driver.lap for driver in active_drivers)
            if leader_laps >= race_state.total_laps:
                # Leader finished - deploy checkered flag but don't end race yet
                # Let other drivers finish when they cross the line
                return False
        
        # If checkered flag deployed, race continues until all drivers finish
        return False

    def _create_position_event(
            self, race_state: RaceState, frame: int) -> Dict[str, Any]:
        """Create position update event for GUI"""
        positions = []

        for driver_id, state in race_state.driver_states.items():
            # Wrap position to track length for GUI rendering
            display_position = state.position_m % race_state.track_length_m

            positions.append({
                "driver_id": driver_id,
                "driver_name": state.driver_name,
                "position": state.position,
                "lap": state.lap,
                "position_m": display_position,
                "velocity_mps": state.velocity_mps,
                "racing_mode": state.racing_mode.value,
                "push_intensity": state.push_intensity,
                "push_fatigue": state.push_fatigue,
                "tire_condition": state.tire_condition,
                "fuel_load": state.fuel_load,
                "gap_ahead": state.gap_ahead,
                "gap_behind": state.gap_behind,
                "running": state.running
            })

        return {
            "type": "position_update",
            "frame": frame,
            "time": race_state.current_time,
            "positions": positions
        }

    def _compile_results(self, race_state: RaceState) -> List[Dict[str, Any]]:
        """Compile final race results with accurate timing and proper lapped classification"""
        results = []

        finished_drivers, lapped_drivers, dnf_drivers = self._classify_result_states(race_state)
        
        # Sort finished drivers by position on track
        finished_drivers.sort(key=lambda s: s.position_m)
        
        # Sort lapped drivers by laps completed (descending), then by position (ascending)
        lapped_drivers.sort(key=lambda s: (-s.lap, s.position_m))
        
        # Add finished drivers first (positions 1, 2, 3...)
        for position, state in enumerate(finished_drivers, 1):
            results.append(self._build_result_entry(race_state, state, position, "FINISHED", False))
        
        # Add lapped drivers after finishers, marked as lapped with their lap deficit
        for position, state in enumerate(lapped_drivers, len(finished_drivers) + 1):
            lap_deficit = race_state.total_laps - state.lap
            results.append(
                self._build_result_entry(
                    race_state,
                    state,
                    position,
                    "LAPPED",
                    True,
                    lap_deficit=lap_deficit,
                )
            )
        
        # Add DNF drivers at the end
        for state in dnf_drivers:
            results.append(self._build_result_entry(race_state, state, len(results) + 1, "DNF", False))

        return results

    def _classify_result_states(self, race_state: RaceState):
        """Split driver states into finished, lapped and DNF buckets."""
        finished_drivers = []
        lapped_drivers = []
        dnf_drivers = []

        for state in race_state.driver_states.values():
            if state.dnf_reason is not None:
                dnf_drivers.append(state)
            elif state.lap >= race_state.total_laps:
                finished_drivers.append(state)
            else:
                lapped_drivers.append(state)

        return finished_drivers, lapped_drivers, dnf_drivers

    def _build_result_entry(
        self,
        race_state: RaceState,
        state: DriverState,
        position: int,
        status: str,
        lapped: bool,
        lap_deficit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Build a standardized result row with optional lap-deficit metadata."""
        average_lap_time = None
        if race_state.lap_times[state.driver_id]:
            average_lap_time = float(np.mean(race_state.lap_times[state.driver_id]))

        entry = {
            "driver_id": state.driver_id,
            "driver_name": state.driver_name,
            "team_id": state.team.id,
            "position": position,
            "laps_completed": state.lap,
            "time_seconds": state.total_time,
            "dnf_reason": state.dnf_reason,
            "best_lap_time": state.best_lap_time if state.best_lap_time < 999 else None,
            "average_lap_time": average_lap_time,
            "status": status,
            "lapped": lapped,
        }
        if lap_deficit is not None:
            entry["lap_deficit"] = lap_deficit
        return entry


__all__ = ['RealtimeRaceEngine', 'DriverState', 'RaceState', 'RacingMode']
