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

Authors: Eoin Fitzsimons
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
    in_pit_lane: bool = False
    pit_time_remaining_s: float = 0.0
    pit_stops_completed: int = 0
    last_pit_eval_lap: int = -1
    pit_window_notified: bool = False

    # Performance modifiers
    in_slipstream: bool = False     # Currently benefiting from draft
    making_overtake: bool = False   # Currently attempting overtake

    # Incident tracking
    running: bool = True
    dnf_reason: Optional[str] = None
    # Has a DNF event already been emitted for this driver (prevents dupes)
    dnf_event_emitted: bool = False

    # Rallycross joker-lap tracking
    joker_lap_target: int = 0
    joker_lap_taken: bool = False
    joker_lap_taken_on: int = 0
    joker_time_penalty_s: float = 0.0

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

        # Pit strategy and service model
        self.PIT_LANE_SPEED_MPS = 22.0
        self.PIT_SERVICE_BASE_SECONDS = 4.0
        self.PIT_LANE_TRANSIT_SECONDS = 11.0
        self.PIT_TIRE_RESET = 0.94
        self.PIT_FUEL_GAIN = 0.40
        self.PIT_TIRE_THRESHOLD = 0.42
        self.PIT_MIN_LAPS_REMAINING = 3

        # Rallycross mandatory joker-lap model
        self.RALLYCROSS_JOKER_BASE_PENALTY_S = 2.8
        self._rallycross_joker_enabled = False

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
        race_state, track_length_m = self._prepare_simulation_runtime(
            drivers,
            teams,
            track,
            total_laps,
            event_callback,
            track_points,
            player_driver_id,
            player_team_driver_ids,
            player_overrides,
        )

        timestep = 1.0 / 30.0
        frame = 0
        if event_callback:
            event_callback(self._create_position_event(race_state, frame))

        frame = self._run_simulation_loop(
            race_state=race_state,
            track_length_m=track_length_m,
            timestep=timestep,
            frame=frame,
            event_callback=event_callback,
            stop_event=stop_event,
            realtime_speed=realtime_speed,
        )
        _ = frame
        return self._finalize_simulation_results(race_state, total_laps, event_callback)

    def _prepare_simulation_runtime(
        self,
        drivers: List[Driver],
        teams: Dict[int, Team],
        track: Track,
        total_laps: int,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
        track_points: Optional[List[Any]],
        player_driver_id: Optional[int],
        player_team_driver_ids: Optional[List[int]],
        player_overrides: Optional[Dict[str, float]],
    ) -> Tuple[RaceState, float]:
        """Prepare track map, controls and race state for simulation loop."""
        print(f"-> Generating track map for {track.name}...")
        self.track_map = TrackMap(track=track)
        self._event_callback = event_callback
        print(f"  OK Track map ready: {len(self.track_map.corners)} corners, {len(self.track_map.drs_zones)} DRS zones")

        self.track_points = track_points
        if track_points:
            print(f"  OK Using visual track with {len(track_points)} points for position mapping")

        self.player_driver_id = player_driver_id
        self.player_team_driver_ids = {int(x) for x in (player_team_driver_ids or []) if x is not None}
        self.player_overrides = player_overrides or {}
        if player_driver_id:
            print(f"  OK Player driver ID {player_driver_id} with overrides: {self.player_overrides}")
        if self.player_team_driver_ids:
            print(f"  OK Player team-controlled drivers: {sorted(self.player_team_driver_ids)}")

        self._configure_rallycross_joker_mode(track)

        track_length_m = track.length_km * 1000.0
        race_state = self._initialize_race(drivers, teams, track_length_m, total_laps)
        return race_state, track_length_m

    def _configure_rallycross_joker_mode(self, track: Track) -> None:
        """Enable mandatory joker-lap logic for sprint/rallycross races."""
        discipline = str(getattr(track, 'primary_discipline', '') or '').upper()
        explicit = bool(getattr(track, 'joker_enabled', False))
        self._rallycross_joker_enabled = explicit or discipline == 'SPRINT_RALLYCROSS'
        if self._rallycross_joker_enabled:
            print(f"  OK Rallycross joker-lap mode enabled (+{self.RALLYCROSS_JOKER_BASE_PENALTY_S:.2f}s route penalty)")

    def _initial_joker_lap_target(self, driver_id: int, total_laps: int) -> int:
        """Pick a default joker lap target for a driver."""
        if total_laps <= 1:
            return 1
        if self.player_driver_id is not None and int(driver_id) == int(self.player_driver_id):
            # Player can arm "come_in" whenever they want; if never armed,
            # joker is forced on final lap to satisfy mandatory usage.
            return max(1, int(total_laps))
        # Keep AI varied, but avoid final-lap clustering for most runs.
        upper = max(1, total_laps - 1)
        return int(self.rng.integers(1, upper + 1))

    def _player_requests_come_in_for_driver(self, state: DriverState) -> bool:
        """Return True when the player has armed a generic come-in request."""
        if self.player_driver_id is None or int(state.driver_id) != int(self.player_driver_id):
            return False
        if not isinstance(getattr(self, 'player_overrides', None), dict):
            return False
        return bool(self.player_overrides.get('come_in', False))

    def _consume_player_come_in_request(self, state: DriverState) -> None:
        """Reset one-shot come-in request after it has been acted upon."""
        if not self._player_requests_come_in_for_driver(state):
            return
        self.player_overrides['come_in'] = False

    def _run_simulation_loop(
        self,
        race_state: RaceState,
        track_length_m: float,
        timestep: float,
        frame: int,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
        stop_event: Any,
        realtime_speed: float,
    ) -> int:
        """Run per-frame simulation until race ends or stop is requested."""
        while not self._race_finished(race_state):
            if stop_event and stop_event.is_set():
                print("\n[RACE ENGINE] Stop requested - terminating simulation")
                break

            frame_start = time.time()
            self._update_running_drivers(race_state, track_length_m, timestep, event_callback)
            self._update_race_situation(race_state)
            self._log_frame_snapshot_if_needed(frame, race_state)

            frame += 1
            race_state.current_time += timestep
            self._emit_position_update_if_needed(frame, race_state, event_callback)
            self._throttle_frame_if_needed(frame_start, timestep, realtime_speed)

        return frame

    def _update_running_drivers(
        self,
        race_state: RaceState,
        track_length_m: float,
        timestep: float,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Advance each running driver by one simulation timestep."""
        for driver_id, state in race_state.driver_states.items():
            if not state.running:
                continue
            self._update_single_driver_step(driver_id, state, race_state, track_length_m, timestep, event_callback)

    def _update_single_driver_step(
        self,
        driver_id: int,
        state: DriverState,
        race_state: RaceState,
        track_length_m: float,
        timestep: float,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Run AI, physics, degradation, and incident checks for one driver."""
        if self._update_driver_pit_cycle(state, race_state, track_length_m, timestep, event_callback):
            return

        self._update_racing_mode(state, race_state)
        speed_mps = self._calculate_speed(state, track_length_m)
        if not np.isfinite(speed_mps):
            print(f"  [WARN] Non-finite speed for {state.driver_name} -> replacing with MIN_SPEED_MPS")
            speed_mps = float(self.MIN_SPEED_MPS)
        if self._check_driver_mistake(state):
            speed_mps *= 0.3

        self._advance_driver_position(state, race_state, speed_mps, timestep, track_length_m, event_callback)
        self._apply_driver_degradation(state)
        self._update_driver_stall_state(state, event_callback)
        self._update_driver_push_fatigue(state)

        if self._check_incident(state, race_state):
            state.running = False
            self._emit_driver_dnf_event_if_needed(driver_id, state)

    def _pit_strategy_enabled_for_track(self) -> bool:
        """Return whether this discipline should run pit strategy logic."""
        track_obj = getattr(self.track_map, 'track', None) if self.track_map is not None else None
        discipline = str(getattr(track_obj, 'primary_discipline', '') or '').upper()
        return discipline not in {'DRAG_ACCELERATION', 'SPRINT_RALLYCROSS'}

    def _update_driver_pit_cycle(
        self,
        state: DriverState,
        race_state: RaceState,
        track_length_m: float,
        timestep: float,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> bool:
        """Handle pit entry/service/exit; return True when frame was consumed by pit logic."""
        if not self._pit_strategy_enabled_for_track():
            return False

        if not state.in_pit_lane:
            if self._should_start_pit_stop(state, race_state, event_callback):
                self._enter_pit_lane(state, event_callback)
                return True
            return False

        state.prev_position_m = state.position_m
        state.position_m += self.PIT_LANE_SPEED_MPS * timestep
        state.velocity_mps = self.PIT_LANE_SPEED_MPS
        prev_lap = int(state.prev_position_m // track_length_m)
        curr_lap = int(state.position_m // track_length_m)
        if curr_lap > prev_lap:
            self._complete_lap(state, race_state, event_callback)

        state.total_time += timestep
        state.push_intensity = min(state.push_intensity, 0.45)
        state.pit_time_remaining_s = max(0.0, state.pit_time_remaining_s - timestep)
        if state.pit_time_remaining_s <= 0.0:
            self._exit_pit_lane(state, event_callback)
        return True

    def _should_start_pit_stop(
        self,
        state: DriverState,
        race_state: RaceState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> bool:
        """Decide pit stops once per lap using tire/fuel and mandatory-stop heuristics."""
        if state.last_pit_eval_lap == state.lap:
            return False
        state.last_pit_eval_lap = state.lap

        # Player one-shot override: come in at next lap opportunity.
        if self._player_requests_come_in_for_driver(state):
            return True

        laps_remaining = race_state.total_laps - state.lap
        if state.lap <= 0 or laps_remaining < self.PIT_MIN_LAPS_REMAINING:
            return False

        # Hard triggers
        if state.tire_condition <= self.PIT_TIRE_THRESHOLD:
            return True
        if state.fuel_load <= 0.14:
            return True

        # One mandatory stop for longer races if none taken yet
        if race_state.total_laps >= 20 and state.pit_stops_completed == 0:
            mandatory_window_lap = int(race_state.total_laps * 0.55)
            self._emit_pit_window_open_if_needed(state, mandatory_window_lap, event_callback)
            if state.lap >= mandatory_window_lap and state.tire_condition < 0.72:
                return True

        # Simple undercut behavior in traffic
        in_traffic_window = 0.8 < state.gap_ahead < 2.5
        if in_traffic_window and state.tire_condition < 0.65 and self.rng.random() < 0.20:
            return True

        return False

    def _emit_pit_window_open_if_needed(
        self,
        state: DriverState,
        mandatory_window_lap: int,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Emit one-shot pit-window notice for player-controlled driver."""
        if state.pit_window_notified:
            return
        if state.lap < mandatory_window_lap:
            return
        if self.player_driver_id is None or int(state.driver_id) != int(self.player_driver_id):
            return
        if not event_callback:
            return

        state.pit_window_notified = True
        event_callback({
            'type': 'pit_window_open',
            'driver_id': state.driver_id,
            'driver_name': state.driver_name,
            'lap': state.lap,
            'window_lap': mandatory_window_lap,
        })

    def _enter_pit_lane(
        self,
        state: DriverState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Start pit phase and emit telemetry event."""
        service_variance = float(self.rng.uniform(-0.7, 0.7))
        total_pit_time = self.PIT_LANE_TRANSIT_SECONDS + self.PIT_SERVICE_BASE_SECONDS + service_variance
        self._consume_player_come_in_request(state)
        state.in_pit_lane = True
        state.pit_time_remaining_s = max(6.0, total_pit_time)
        state.racing_mode = RacingMode.MANAGE
        if event_callback:
            event_callback({
                "type": "pit_entry",
                "driver_id": state.driver_id,
                "driver_name": state.driver_name,
                "lap": state.lap,
                "pit_time_remaining_s": state.pit_time_remaining_s,
            })

    def _exit_pit_lane(
        self,
        state: DriverState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Apply service effects and emit pit exit telemetry."""
        state.in_pit_lane = False
        state.pit_time_remaining_s = 0.0
        state.pit_stops_completed += 1
        state.tire_condition = max(state.tire_condition, self.PIT_TIRE_RESET)
        state.fuel_load = min(1.0, state.fuel_load + self.PIT_FUEL_GAIN)
        state.tire_compound = 'hard' if state.tire_condition < 0.5 else 'medium'
        if event_callback:
            event_callback({
                "type": "pit_exit",
                "driver_id": state.driver_id,
                "driver_name": state.driver_name,
                "lap": state.lap,
                "pit_stops_completed": state.pit_stops_completed,
            })

    def _advance_driver_position(
        self,
        state: DriverState,
        race_state: RaceState,
        speed_mps: float,
        timestep: float,
        track_length_m: float,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """Advance positional and lap state by one frame."""
        state.prev_position_m = state.position_m
        state.position_m += speed_mps * timestep
        state.velocity_mps = speed_mps
        prev_lap = int(state.prev_position_m // track_length_m)
        curr_lap = int(state.position_m // track_length_m)
        if curr_lap > prev_lap:
            self._complete_lap(state, race_state, event_callback)
        state.total_time += timestep

    def _apply_driver_degradation(self, state: DriverState) -> None:
        """Apply tire wear and fuel burn from surface and tire compound."""
        surface_multipliers = {
            'asphalt': 1.0,
            'tarmac': 1.0,
            'concrete': 1.05,
            'gravel': 1.6,
            'mixed': 1.3,
            'dirt': 1.8,
        }
        compound_multipliers = {
            'soft': 1.3,
            'medium': 1.0,
            'hard': 0.8,
            'rain': 1.2,
        }
        surf = None
        track_obj = getattr(self.track_map, 'track', None) if self.track_map is not None else None
        if track_obj is not None:
            surf = getattr(track_obj, 'surface', None) or getattr(track_obj, 'surface_type', None)
        surface_mul = surface_multipliers.get((surf or '').lower(), 1.0)
        comp_key = (getattr(state, 'tire_compound', 'medium') or 'medium').lower()
        comp_mul = compound_multipliers.get(comp_key, 1.0)
        degradation = self.TIRE_DEGRADATION_RATE * state.push_intensity * surface_mul * comp_mul
        state.tire_condition = max(0.0, state.tire_condition - degradation)
        state.fuel_load -= self.FUEL_BURN_RATE

    def _update_driver_stall_state(
        self,
        state: DriverState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Track stalls and mark DNF if a car remains static for too long."""
        try:
            moved = abs(state.position_m - state.prev_position_m) > 0.01
        except Exception:
            moved = True
        state.stall_frames = 0 if moved else state.stall_frames + 1
        if state.stall_frames <= 900:
            return

        state.running = False
        state.dnf_reason = 'stalled'
        print(f"  [STALL] {state.driver_name} marked DNF (stalled) after {state.stall_frames} frames")
        if event_callback:
            event_callback({
                "type": "dnf",
                "driver_id": state.driver_id,
                "driver_name": state.driver_name,
                "lap": state.lap,
                "reason": state.dnf_reason,
            })

    def _update_driver_push_fatigue(self, state: DriverState) -> None:
        """Update fatigue accumulation/recovery based on current push level."""
        if state.push_intensity > 0.8:
            state.push_fatigue += 0.00035 * (state.push_intensity - 0.8)
        else:
            state.push_fatigue = max(0.0, state.push_fatigue - 0.00008)
        state.push_fatigue = min(1.0, state.push_fatigue)
        state.frames_since_mistake += 1

    def _emit_driver_dnf_event_if_needed(self, driver_id: int, state: DriverState) -> None:
        """Emit DNF event once for a driver when available."""
        if not (hasattr(self, '_event_callback') and callable(self._event_callback)):
            return
        if getattr(state, 'dnf_event_emitted', False):
            return
        try:
            self._event_callback({
                "type": "dnf",
                "driver_id": driver_id,
                "driver_name": state.driver_name,
                "lap": state.lap,
                "reason": state.dnf_reason,
            })
            state.dnf_event_emitted = True
        except Exception:
            pass

    def _log_frame_snapshot_if_needed(self, frame: int, race_state: RaceState) -> None:
        """Periodic verbose snapshot for debugging frame-by-frame state."""
        if frame % 30 != 0:
            return
        print(f"\n[FRAME {frame}] Race time: {race_state.current_time:.1f}s")
        active_count = sum(1 for s in race_state.driver_states.values() if s.running)
        print(f"  Active cars: {active_count}/{len(race_state.driver_states)}")
        for driver_id, state in sorted(race_state.driver_states.items()):
            status = "RUNNING" if state.running else f"DNF({state.dnf_reason})"
            print(
                f"  Car {driver_id} ({state.driver_name}): "
                f"P{state.position} | L{state.lap} | "
                f"pos={state.position_m:.1f}m | v={state.velocity_mps:.1f}m/s | {status}"
            )

    def _emit_position_update_if_needed(
        self,
        frame: int,
        race_state: RaceState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Emit per-frame position event with periodic verbose send logging."""
        if not event_callback:
            return
        position_event = self._create_position_event(race_state, frame)
        if frame % 90 == 0:
            print(f"  -> Emitting {len(position_event['positions'])} car positions to GUI")
        event_callback(position_event)

    def _throttle_frame_if_needed(self, frame_start: float, timestep: float, realtime_speed: float) -> None:
        """Sleep to honor realtime_speed for low-speed visualized runs."""
        if realtime_speed >= 100:
            return
        frame_duration = time.time() - frame_start
        target_duration = timestep / realtime_speed
        sleep_time = target_duration - frame_duration
        if sleep_time > 0:
            time.sleep(sleep_time)

    def _finalize_simulation_results(
        self,
        race_state: RaceState,
        total_laps: int,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> List[Dict[str, Any]]:
        """Compile and emit final race results payload."""
        results = self._compile_results(race_state)
        if event_callback:
            event_callback({
                "type": "race_finished",
                "total_laps": total_laps,
                "race_time": race_state.current_time,
                "results": results,
                "collision_log": race_state.collision_log,
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

            if self._rallycross_joker_enabled:
                state.joker_lap_target = self._initial_joker_lap_target(driver.id, total_laps)

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
        if self._apply_player_racing_overrides_if_controlled(state, driver):
            return

        base_push, consistency = self._compute_ai_base_push(driver)
        state.push_intensity = base_push

        if self._apply_attack_mode_if_needed(state, race_state, driver, base_push):
            self._apply_post_mode_push_adjustments(state, consistency)
            return
        if self._apply_defend_mode_if_needed(state, race_state, driver, base_push):
            self._apply_post_mode_push_adjustments(state, consistency)
            return

        self._apply_manage_or_cruise_mode(state, base_push, consistency)
        self._apply_post_mode_push_adjustments(state, consistency)

    def _is_player_controlled_driver(self, state: DriverState) -> bool:
        return bool(
            (hasattr(self, 'player_driver_id') and self.player_driver_id == state.driver_id)
            or (
                hasattr(self, 'player_team_driver_ids')
                and state.driver_id in getattr(self, 'player_team_driver_ids', set())
            )
        )

    def _apply_player_racing_overrides_if_controlled(self, state: DriverState, driver: Driver) -> bool:
        """Apply player UI overrides for controlled drivers; return True if handled."""
        if not self._is_player_controlled_driver(state):
            return False
        if not (hasattr(self, 'player_overrides') and self.player_overrides):
            return True

        self._apply_player_push_override(state, driver)
        self._apply_player_overtake_mode_override(state)
        self._log_player_control_snapshot(driver, state)
        return True

    def _apply_player_push_override(self, state: DriverState, driver: Driver) -> None:
        if 'push' not in self.player_overrides:
            return
        old_push = state.push_intensity
        state.push_intensity = self.player_overrides['push']
        if not hasattr(self, '_player_push_logged'):
            self._player_push_logged = True
            print(f"[PLAYER PUSH APPLIED] {driver.name}: {old_push:.2f} -> {state.push_intensity:.2f} (from sliders)")

    def _apply_player_overtake_mode_override(self, state: DriverState) -> None:
        if 'overtake' not in self.player_overrides:
            return
        overtake_multiplier = self.player_overrides['overtake']
        threshold = self.ATTACK_THRESHOLD_GAP * (1.5 - overtake_multiplier * 0.5)
        if state.gap_ahead < threshold and overtake_multiplier > 0.3:
            state.racing_mode = RacingMode.ATTACK
        elif state.gap_behind < self.DEFEND_THRESHOLD_GAP:
            state.racing_mode = RacingMode.DEFEND
        else:
            state.racing_mode = RacingMode.MANAGE

    def _log_player_control_snapshot(self, driver: Driver, state: DriverState) -> None:
        if not hasattr(self, '_player_log_counter'):
            self._player_log_counter = 0
        self._player_log_counter += 1
        if self._player_log_counter % 150 == 0:
            print(
                f"[PLAYER CONTROL] {driver.name}: push={state.push_intensity:.2f}, "
                f"mode={state.racing_mode.value}, gap_ahead={state.gap_ahead:.1f}s"
            )

    def _compute_ai_base_push(self, driver: Driver) -> Tuple[float, float]:
        """Return base AI push and consistency.

        Consistency is returned for later variance/post-processing.
        """
        raw_speed = get_safe_attribute(driver, 'speed') / 100.0
        aggression = get_driver_aggression(driver) / 100.0
        consistency = get_safe_attribute(driver, 'consistency') / 100.0
        professionalism = get_driver_professionalism(driver)
        risk_tolerance = (100.0 - professionalism) / 100.0

        base_push = 0.4 + (raw_speed * 0.2) + (aggression * 0.2) + (risk_tolerance * 0.2)
        variability = (1.0 - consistency) * self.rng.uniform(-0.05, 0.05)
        base_push = max(0.35, min(1.0, base_push + variability))
        return base_push, consistency

    def _apply_attack_mode_if_needed(self, state: DriverState, race_state: RaceState, driver: Driver, base_push: float) -> bool:
        if not (state.gap_ahead < self.ATTACK_THRESHOLD_GAP and state.position > 1):
            return False

        car_ahead = self._get_car_ahead(state, race_state)
        if car_ahead and self.track_map:
            self._apply_track_aware_attack(state, race_state, driver, car_ahead, base_push)
        else:
            state.racing_mode = RacingMode.ATTACK
            state.push_intensity = min(1.0, base_push + 0.15)
        return True

    def _apply_track_aware_attack(self, state: DriverState, race_state: RaceState, driver: Driver, car_ahead: DriverState, base_push: float) -> None:
        if self.track_map is None:
            state.racing_mode = RacingMode.ATTACK
            state.push_intensity = min(1.0, base_push + 0.15)
            return

        section_type, corner = self.track_map.get_section_at_position(state.position_m % race_state.track_length_m)
        gap_m = state.gap_ahead * state.velocity_mps

        should_attempt, success_prob, attempt_type = evaluate_overtaking_opportunity(
            attacker=driver,
            defender=car_ahead.driver,
            attacker_speed_kmh=state.velocity_mps * 3.6,
            defender_speed_kmh=car_ahead.velocity_mps * 3.6,
            gap_m=gap_m,
            section=section_type,
            corner=corner,
        )

        if not should_attempt:
            state.racing_mode = RacingMode.MANAGE
            return

        state.racing_mode = RacingMode.ATTACK
        state.push_intensity = min(1.0, base_push + 0.35)
        self._log_overtake_attempt(driver.name, car_ahead.driver.name, gap_m, success_prob)
        self._start_overtake_if_not_on_cooldown(state, car_ahead, race_state, attempt_type, gap_m, corner)

    def _log_overtake_attempt(self, attacker_name: str, defender_name: str, gap_m: float, success_prob: float) -> None:
        if not hasattr(self, '_overtake_log_counter'):
            self._overtake_log_counter = 0
        self._overtake_log_counter += 1
        if self._overtake_log_counter % 30 == 1:
            print(
                f"  OVERTAKING: {attacker_name} attempting to overtake {defender_name}! "
                f"Gap: {gap_m:.1f}m, Success chance: {success_prob * 100:.0f}%"
            )

    def _start_overtake_if_not_on_cooldown(
        self,
        state: DriverState,
        car_ahead: DriverState,
        race_state: RaceState,
        attempt_type: OvertakeAttemptType | str,
        gap_m: float,
        corner: Optional[Any],
    ) -> None:
        key = (state.driver_id, car_ahead.driver_id)
        pair_key = frozenset((state.driver_id, car_ahead.driver_id))
        cooldown_expiry = self._overtake_pair_cooldown.get(pair_key, 0.0)
        if race_state.current_time < cooldown_expiry or key in self.active_overtakes:
            return

        if isinstance(attempt_type, OvertakeAttemptType):
            normalized_attempt_type = attempt_type
        else:
            try:
                normalized_attempt_type = OvertakeAttemptType(attempt_type)
            except Exception:
                normalized_attempt_type = OvertakeAttemptType.SLIPSTREAM_STRAIGHT

        self.active_overtakes[key] = OvertakeAttempt(
            attacker_id=state.driver_id,
            defender_id=car_ahead.driver_id,
            attempt_type=normalized_attempt_type,
            position_m=state.position_m,
            gap_m=gap_m,
            speed_advantage_kmh=(state.velocity_mps - car_ahead.velocity_mps) * 3.6,
            corner=corner,
        )

    def _apply_defend_mode_if_needed(self, state: DriverState, race_state: RaceState, driver: Driver, base_push: float) -> bool:
        if not (state.gap_behind < self.DEFEND_THRESHOLD_GAP and state.position < len(race_state.driver_states)):
            return False

        car_behind = self._get_car_behind(state, race_state)
        state.racing_mode = RacingMode.DEFEND
        state.push_intensity = min(1.0, base_push + 0.10)
        if car_behind and self.track_map:
            section_type, corner = self.track_map.get_section_at_position(state.position_m % race_state.track_length_m)
            gap_m = state.gap_behind * state.velocity_mps
            _, racing_line = calculate_defensive_action(
                defender=driver,
                attacker=car_behind.driver,
                gap_m=gap_m,
                section=section_type,
                corner=corner,
            )
            state.racing_line = racing_line
        return True

    def _apply_manage_or_cruise_mode(self, state: DriverState, base_push: float, consistency: float) -> None:
        if state.gap_ahead > 3.0 and state.gap_behind > 3.0:
            state.racing_mode = RacingMode.MANAGE
            conservation_factor = 1.0 - (consistency * 0.3)
            state.push_intensity = base_push * conservation_factor
            state.racing_line = RacingLine.IDEAL
            return

        state.racing_mode = RacingMode.CRUISE
        state.push_intensity = base_push
        state.racing_line = RacingLine.IDEAL

    def _apply_post_mode_push_adjustments(self, state: DriverState, consistency: float) -> None:
        """Apply tire/fatigue randomization and clamp final push intensity."""
        if state.tire_condition < 0.7:
            tire_factor = 0.5 + (state.tire_condition * 0.5)
            state.push_intensity *= tire_factor
        variance = (1.0 - consistency) * 0.15
        state.push_intensity += self.rng.normal(0, variance)
        state.push_intensity = np.clip(state.push_intensity, 0.3, 1.0)

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
        active_drivers = self._sorted_active_drivers(race_state)
        for i, (driver_id, state) in enumerate(active_drivers):
            state.position = i + 1
            self._update_gap_ahead_and_slipstream(state, i, active_drivers, race_state)
            self._update_gap_behind(state, i, active_drivers)
            state.cars_nearby = self._collect_nearby_cars(driver_id, state, race_state)

    def _sorted_active_drivers(self, race_state: RaceState):
        """Return running drivers sorted by lap and position on lap."""
        active_drivers = [
            (driver_id, state)
            for driver_id, state in race_state.driver_states.items()
            if state.running
        ]
        active_drivers.sort(key=lambda x: (-x[1].lap, -x[1].position_m))
        return active_drivers

    def _update_gap_ahead_and_slipstream(self, state: DriverState, index: int, active_drivers, race_state: RaceState) -> None:
        """Compute gap ahead and slipstream eligibility."""
        if index == 0:
            state.gap_ahead = 999.0
            state.in_slipstream = False
            return

        ahead_state = active_drivers[index - 1][1]
        distance_gap = self._distance_to_ahead(state, ahead_state, race_state.track_length_m)
        state.gap_ahead = self._time_gap_to_ahead(state, ahead_state, distance_gap)
        state.in_slipstream = bool(ahead_state.lap == state.lap and distance_gap < self.SLIPSTREAM_DISTANCE)

    def _distance_to_ahead(self, state: DriverState, ahead_state: DriverState, track_length_m: float) -> float:
        """Return physical distance to car ahead."""
        if ahead_state.lap == state.lap:
            return ahead_state.position_m - state.position_m
        if ahead_state.lap > state.lap:
            return (track_length_m - state.position_m) + ahead_state.position_m
        return track_length_m

    def _time_gap_to_ahead(self, state: DriverState, ahead_state: DriverState, distance_gap: float) -> float:
        """Convert ahead-distance to UI gap convention (seconds or lap marker)."""
        if ahead_state.lap == state.lap:
            if state.velocity_mps > 0.1:
                return distance_gap / state.velocity_mps
            return distance_gap / self.BASE_SPEED_MPS if distance_gap > 0 else 0.0
        if ahead_state.lap > state.lap:
            lap_diff = ahead_state.lap - state.lap
            return 999.0 + lap_diff
        return 999.0

    def _update_gap_behind(self, state: DriverState, index: int, active_drivers) -> None:
        """Compute gap behind using same-lap distance or lap markers."""
        if index >= len(active_drivers) - 1:
            state.gap_behind = 999.0
            return

        behind_state = active_drivers[index + 1][1]
        if behind_state.lap == state.lap:
            distance_gap = state.position_m - behind_state.position_m
            state.gap_behind = distance_gap / self.BASE_SPEED_MPS
            return
        if state.lap > behind_state.lap:
            lap_diff = state.lap - behind_state.lap
            state.gap_behind = 999.0 + lap_diff
            return
        state.gap_behind = 999.0

    def _collect_nearby_cars(self, driver_id: int, state: DriverState, race_state: RaceState) -> List[int]:
        """Return nearby running cars on same lap within configured distance."""
        nearby: List[int] = []
        for other_id, other_state in race_state.driver_states.items():
            if other_id == driver_id or not other_state.running or other_state.lap != state.lap:
                continue
            if abs(other_state.position_m - state.position_m) < self.NEARBY_DISTANCE_M:
                nearby.append(other_id)
        return nearby

    def _complete_lap(
        self,
        state: DriverState,
        race_state: RaceState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """Handle lap completion and discipline-specific lap side effects."""
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

        self._maybe_apply_rallycross_joker(state, race_state, event_callback)

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

    def _maybe_apply_rallycross_joker(
        self,
        state: DriverState,
        race_state: RaceState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Apply mandatory single joker-lap penalty in rallycross mode."""
        if not self._rallycross_joker_enabled or state.joker_lap_taken:
            return

        self._refresh_player_joker_target_if_needed(state, race_state)
        target_lap = max(1, int(state.joker_lap_target or 1))

        should_serve_now = state.lap == target_lap
        forced = False
        if not should_serve_now and state.lap >= race_state.total_laps:
            # Mandatory fallback: cannot finish race without exactly one joker lap.
            should_serve_now = True
            forced = True

        if not should_serve_now:
            return

        penalty_s = self._joker_penalty_seconds(state)
        state.total_time += penalty_s
        state.joker_lap_taken = True
        state.joker_lap_taken_on = int(state.lap)
        state.joker_time_penalty_s = penalty_s
        self._consume_player_come_in_request(state)

        if event_callback:
            event_callback({
                'type': 'joker_lap_served',
                'driver_id': state.driver_id,
                'driver_name': state.driver_name,
                'served_lap': state.joker_lap_taken_on,
                'target_lap': target_lap,
                'forced': forced,
                'penalty_s': penalty_s,
            })

    def _refresh_player_joker_target_if_needed(self, state: DriverState, race_state: RaceState) -> None:
        """Allow player to trigger joker timing using generic come-in toggle."""
        _ = race_state
        if self.player_driver_id is None:
            return
        if int(state.driver_id) != int(self.player_driver_id):
            return
        if state.joker_lap_taken:
            return
        if self._player_requests_come_in_for_driver(state):
            state.joker_lap_target = max(1, int(state.lap))

    def _joker_penalty_seconds(self, state: DriverState) -> float:
        """Compute one-time joker route penalty in seconds."""
        consistency = get_safe_attribute(state.driver, 'consistency') / 100.0
        skill_adjust = 1.0 - (consistency - 0.5) * 0.20
        jitter = float(self.rng.uniform(-0.20, 0.20))
        penalty = self.RALLYCROSS_JOKER_BASE_PENALTY_S * skill_adjust + jitter
        return max(1.8, penalty)

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
        car_length = 4.0
        safe_following_distance = 15.0

        for other_id, other_state in race_state.driver_states.items():
            if not self._is_collision_candidate(state, other_id, other_state):
                continue
            longitudinal_gap = self._longitudinal_gap(state, other_state, race_state.track_length_m)
            if longitudinal_gap >= safe_following_distance:
                continue
            if self._handle_pair_incident(state, other_state, race_state, longitudinal_gap, car_length):
                return True

        return self._check_solo_incident(state)

    def _is_collision_candidate(self, state: DriverState, other_id: int, other_state: DriverState) -> bool:
        """Return whether another state can collide with the current state this frame."""
        if other_id == state.driver_id or not other_state.running:
            return False
        if other_state.lap != state.lap:
            return False
        return True

    def _longitudinal_gap(self, state: DriverState, other_state: DriverState, track_length_m: float) -> float:
        """Compute shortest longitudinal distance between two cars on looped track."""
        longitudinal_gap = abs(state.position_m - other_state.position_m) % track_length_m
        if longitudinal_gap > track_length_m / 2:
            longitudinal_gap = track_length_m - longitudinal_gap
        return longitudinal_gap

    def _is_overtaking_pair(self, state: DriverState, other_state: DriverState) -> bool:
        return bool(
            state.racing_mode in (RacingMode.ATTACK, RacingMode.DEFEND)
            or other_state.racing_mode in (RacingMode.ATTACK, RacingMode.DEFEND)
        )

    def _handle_pair_incident(
        self,
        state: DriverState,
        other_state: DriverState,
        race_state: RaceState,
        longitudinal_gap: float,
        car_length: float,
    ) -> bool:
        """Handle side-by-side overtake contact and rear-end scenarios."""
        is_overtaking = self._is_overtaking_pair(state, other_state)
        if is_overtaking and longitudinal_gap < car_length * 1.5:
            return self._maybe_trigger_overtake_contact(state, other_state, race_state)
        if not is_overtaking and longitudinal_gap < car_length:
            return self._maybe_trigger_rear_end_incident(state, other_state, race_state)
        return False

    def _racecraft_score(self, state: DriverState) -> float:
        """Return normalized racecraft/control/reaction composite in [0,1]."""
        vehicle_control = get_vehicle_control(state.driver)
        reactions = get_safe_attribute(state.driver, 'reactions')
        racecraft = get_safe_attribute(state.driver, 'racecraft')
        return (vehicle_control + reactions + racecraft) / 300.0

    def _maybe_trigger_overtake_contact(self, state: DriverState, other_state: DriverState, race_state: RaceState) -> bool:
        my_racecraft = self._racecraft_score(state)
        other_racecraft = self._racecraft_score(other_state)
        combined_skill = (my_racecraft + other_racecraft) / 2.0
        control_factor = min(state.tire_condition, other_state.tire_condition)
        contact_probability = 0.0000002 * (1.0 - combined_skill * control_factor)
        if self.rng.random() >= contact_probability:
            return False

        state.dnf_reason = "contact_during_overtake"
        other_state.running = False
        other_state.dnf_reason = "contact_during_overtake"
        print(
            f"  *** RACING INCIDENT! {state.driver_name} and {other_state.driver_name} "
            f"made contact at position {state.position_m:.0f}m"
        )
        race_state.collision_log.append({
            "lap": state.lap,
            "time": race_state.current_time,
            "position_m": state.position_m,
            "type": "contact_during_overtake",
            "driver1_id": state.driver_id,
            "driver1_name": state.driver_name,
            "driver2_id": other_state.driver_id,
            "driver2_name": other_state.driver_name,
            "description": f"{state.driver_name} and {other_state.driver_name} collided during overtake",
        })
        self._emit_other_driver_dnf_event(other_state)
        return True

    def _emit_other_driver_dnf_event(self, other_state: DriverState) -> None:
        """Emit DNF event for secondary collision party when needed."""
        try:
            if not (hasattr(self, '_event_callback') and callable(self._event_callback)):
                return
            if getattr(other_state, 'dnf_event_emitted', False):
                return
            self._event_callback({
                "type": "dnf",
                "driver_id": other_state.driver_id,
                "driver_name": other_state.driver_name,
                "lap": other_state.lap,
                "reason": other_state.dnf_reason,
            })
            other_state.dnf_event_emitted = True
        except Exception:
            pass

    def _maybe_trigger_rear_end_incident(self, state: DriverState, other_state: DriverState, race_state: RaceState) -> bool:
        relative_velocity = state.velocity_mps - other_state.velocity_mps
        if state.position_m >= other_state.position_m:
            if relative_velocity < -5.0:
                return False
            return False
        if relative_velocity <= 15.0:
            return False

        combined_control = (get_vehicle_control(state.driver) + get_vehicle_control(other_state.driver)) / 200.0
        severity = min(1.0, (relative_velocity - 15.0) / 15.0)
        dnf_probability = 0.12 * severity * (1.0 - combined_control)
        if self.rng.random() < dnf_probability:
            print(f"  *** REAR-END! {state.driver_name} hit {other_state.driver_name}")
            state.dnf_reason = "rear_end_collision"
            race_state.collision_log.append({
                "lap": state.lap,
                "time": race_state.current_time,
                "position_m": state.position_m,
                "type": "rear_end_collision",
                "driver1_id": state.driver_id,
                "driver1_name": state.driver_name,
                "driver2_id": other_state.driver_id,
                "driver2_name": other_state.driver_name,
                "description": f"{state.driver_name} rear-ended {other_state.driver_name}",
            })
            return True

        print(
            f"  !!! NEAR MISS/CONTACT (no DNF): {state.driver_name} & {other_state.driver_name} "
            f"- closing {relative_velocity:.1f}m/s"
        )
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
            "description": f"Minor rear contact between {state.driver_name} and {other_state.driver_name} (no DNF)",
        })
        return False

    def _check_solo_incident(self, state: DriverState) -> bool:
        """Handle non-contact DNFs (tire failure spin and mechanical failure)."""
        if state.tire_condition < 0.1:
            consistency = state.driver.consistency / 100.0
            if self.rng.random() > consistency:
                state.dnf_reason = "tire_failure_spin"
                print(f"  X {state.driver_name} spins off - tire condition critical!")
                return True
        if self.rng.random() < 0.00001:
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

        completed_attempts = []
        for key, attempt in self.active_overtakes.items():
            if self._resolve_single_overtake_attempt(key, attempt, race_state):
                completed_attempts.append(key)

        for key in completed_attempts:
            del self.active_overtakes[key]

    def _resolve_single_overtake_attempt(self, key, attempt: OvertakeAttempt, race_state: RaceState) -> bool:
        """Resolve one active overtake attempt; return True when completed."""
        attacker_id, defender_id = key
        attacker_state = race_state.driver_states.get(attacker_id)
        defender_state = race_state.driver_states.get(defender_id)
        if attacker_state is None or defender_state is None:
            return True
        if not attacker_state.running or not defender_state.running:
            return True

        position_on_track = attacker_state.position_m % race_state.track_length_m
        if self.track_map is not None:
            self.track_map.get_section_at_position(position_on_track)

        speed_diff = attacker_state.velocity_mps - defender_state.velocity_mps
        gap_meters = attacker_state.gap_ahead * attacker_state.velocity_mps
        lateral_overlap = self._compute_overtake_lateral_overlap(attempt, gap_meters)

        attempt.gap_m = gap_meters
        attempt.speed_advantage_kmh = speed_diff * 3.6
        attempt.lateral_overlap = lateral_overlap

        outcome = attempt.update(1.0 / 30.0)
        if not self._should_resolve_overtake_attempt(outcome, attempt, lateral_overlap, attacker_state):
            return False

        result = self._resolve_overtake_result(outcome, attempt, attacker_state, defender_state)
        self._apply_overtake_result(result, key, attempt, race_state, attacker_state, defender_state)
        return True

    def _compute_overtake_lateral_overlap(self, attempt: OvertakeAttempt, gap_meters: float) -> float:
        if gap_meters < 5.0:
            return min(0.8, 0.2 + (5.0 - gap_meters) * 0.12)
        return max(0.0, attempt.lateral_overlap - 0.05)

    def _should_resolve_overtake_attempt(self, outcome: Optional[str], attempt: OvertakeAttempt, lateral_overlap: float, attacker_state: DriverState) -> bool:
        if outcome:
            return True
        if attempt.frames_active > 30:
            return True
        if lateral_overlap > 0.7:
            return True
        if attacker_state.gap_ahead > 2.0:
            return True
        return False

    def _resolve_overtake_result(
        self,
        outcome: Optional[str],
        attempt: OvertakeAttempt,
        attacker_state: DriverState,
        defender_state: DriverState,
    ) -> str:
        if outcome:
            return outcome
        result, _ = resolve_overtake_outcome(
            attacker=attacker_state.driver,
            defender=defender_state.driver,
            overtake_attempt=attempt,
            rng=self.rng,
        )
        return result

    def _apply_overtake_result(
        self,
        result: str,
        key,
        attempt: OvertakeAttempt,
        race_state: RaceState,
        attacker_state: DriverState,
        defender_state: DriverState,
    ) -> None:
        if result == "success":
            self._handle_overtake_success(key, attempt, race_state, attacker_state, defender_state)
            return
        if result == "incident":
            self._handle_overtake_incident(attacker_state, defender_state)

    def _handle_overtake_success(
        self,
        key,
        attempt: OvertakeAttempt,
        race_state: RaceState,
        attacker_state: DriverState,
        defender_state: DriverState,
    ) -> None:
        last_print = self._recent_overtakes.get(key)
        if last_print is None or (race_state.current_time - last_print) > 0.8:
            print(f"  OK {attacker_state.driver_name} overtakes {defender_state.driver_name}! ({attempt.attempt_type.value})")
            self._recent_overtakes[key] = race_state.current_time
        try:
            safe_nudge = 5.0
            attacker_state.position_m = defender_state.position_m + safe_nudge
            attacker_state.velocity_mps = max(attacker_state.velocity_mps, defender_state.velocity_mps + 0.5)
            pair_key_done = frozenset((attacker_state.driver_id, defender_state.driver_id))
            self._overtake_pair_cooldown[pair_key_done] = race_state.current_time + 1.0
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
                "description": f"{attacker_state.driver_name} overtook {defender_state.driver_name} ({attempt.attempt_type.value})",
            })
        except Exception:
            pass

    def _handle_overtake_incident(self, attacker_state: DriverState, defender_state: DriverState) -> None:
        attacker_state.running = False
        attacker_state.dnf_reason = "collision"
        defender_state.running = False
        defender_state.dnf_reason = "collision"
        print(f"  COLLISION! {attacker_state.driver_name} and {defender_state.driver_name} crash!")
        self._emit_dnf_event_if_needed(attacker_state)
        self._emit_dnf_event_if_needed(defender_state)

    def _emit_dnf_event_if_needed(self, state: DriverState) -> None:
        try:
            if not (hasattr(self, '_event_callback') and callable(self._event_callback)):
                return
            if getattr(state, 'dnf_event_emitted', False):
                return
            self._event_callback({
                'type': 'dnf',
                'driver_id': state.driver_id,
                'driver_name': state.driver_name,
                'lap': state.lap,
                'reason': state.dnf_reason,
            })
            state.dnf_event_emitted = True
        except Exception:
            pass

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
                "in_pit_lane": state.in_pit_lane,
                "pit_time_remaining_s": state.pit_time_remaining_s,
                "pit_stops_completed": state.pit_stops_completed,
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
            "pit_stops": state.pit_stops_completed,
            "status": status,
            "lapped": lapped,
        }
        if lap_deficit is not None:
            entry["lap_deficit"] = lap_deficit
        return entry


__all__ = ['RealtimeRaceEngine', 'DriverState', 'RaceState', 'RacingMode']
