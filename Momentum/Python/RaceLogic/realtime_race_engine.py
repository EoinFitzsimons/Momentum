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
- Tyre degradation and fuel effects over time
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

import random
import numpy as np
import time
from typing import List, Dict, Callable, Optional, Any, Tuple, cast
from dataclasses import dataclass, field
from enum import Enum

from database.models import Driver, Team, Track
from RaceLogic.track_physics import TrackMap, TrackSection, RacingLine
from RaceLogic.overtaking_system import (
    OvertakeAttempt,
    OvertakeAttemptType,
    evaluate_overtaking_opportunity,
    calculate_defensive_action,
    resolve_overtake_outcome,
    DEFAULT_LOGISTIC_SLOPES,
)
from services.driver_attributes import (
    get_safe_attribute,
    get_driver_aggression,
    get_driver_professionalism,
    get_vehicle_control,
    get_cornering_skill,
)
from config import STAFF_ROLES_CONFIG


class RacingMode(Enum):
    """Driver's current racing mode"""

    ATTACK = "attack"  # Pushing hard to overtake
    DEFEND = "defend"  # Protecting position
    MANAGE = "manage"  # Conserving tyres/fuel, managing gap
    CRUISE = "cruise"  # No immediate pressure


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
    # Absolute position from start line (metres)
    position_m: float = 0.0
    prev_position_m: float = 0.0  # Previous position (for lap detection)
    velocity_mps: float = 0.0  # Current velocity (metres per second)
    lap: int = 0  # Current lap number

    # Race situation awareness
    gap_ahead: float = 999.0  # Gap to car ahead (seconds)
    gap_behind: float = 999.0  # Gap to car behind (seconds)
    position: int = 1  # Current race position
    cars_nearby: List[int] = field(default_factory=list)  # Driver IDs of nearby cars

    # Strategic state
    racing_mode: RacingMode = RacingMode.MANAGE
    push_intensity: float = 0.5  # MUST be set by _update_racing_mode()
    racing_line: RacingLine = RacingLine.IDEAL  # Current racing line choice

    # Component degradation
    tyre_condition: float = 1.0  # 1.0=new tyres, 0.0=completely worn
    fuel_load: float = 1.0  # 1.0=full tank, 0.0=empty
    tyre_compound: str = "medium"  # soft, medium, hard, rain
    in_pit_lane: bool = False
    pit_time_remaining_s: float = 0.0
    pit_total_time_s: float = 0.0
    requested_tyre_compound: str = "medium"
    pit_stops_completed: int = 0
    last_pit_eval_lap: int = -1
    pit_window_notified: bool = False

    # Performance modifiers
    in_slipstream: bool = False  # Currently benefiting from draft
    making_overtake: bool = False  # Currently attempting overtake

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
    total_time: float = 0.0  # Total race time elapsed
    last_lap_time: float = 0.0  # Previous lap time
    best_lap_time: float = 999.0  # Personal best lap

    # Push fatigue and mistakes
    # Accumulated fatigue from pushing hard (0.0-1.0)
    push_fatigue: float = 0.0
    frames_since_mistake: int = 999  # Frames since last mistake (cooldown)
    # Stall detection: consecutive frames with no position change
    stall_frames: int = 0

    # (No compatibility aliases remain; attributes use 'tyre_' spelling)


@dataclass
class RaceState:
    """Overall race state tracking"""

    current_time: float = 0.0  # Race elapsed time (seconds)
    timestep: float = 1.0 / 30.0  # Simulation timestep (0.033s for 30 FPS)

    driver_states: Dict[int, DriverState] = field(default_factory=dict)
    lap_start_positions: Dict[int, float] = field(default_factory=dict)

    total_laps: int = 50
    track_length_m: float = 6000.0

    # For lap detection
    lap_times: Dict[int, List[float]] = field(default_factory=dict)

    # Collision tracking
    collision_log: List[Dict[str, Any]] = field(default_factory=list)

    # Chequered flag logic: when leader finishes, allow other drivers to finish at line
    checkered_flag_deployed: bool = False  # Set when leader completes all laps
    leader_lap_count: int = 0  # Highest lap count when chequered flag deployed


class RealtimeRaceEngine:
    """
    Real-time agent-based racing simulation engine

    Simulates racing at 30 FPS with drivers making active decisions based on
    their surroundings, attributes, and race situation.
    """

    def __init__(self, seed: Optional[int] = None, db: Optional[Any] = None):
        """Initialise engine with random generator"""
        self.rng = np.random.default_rng(seed)
        # Also seed the global random module for backward compatibility
        # (some code paths use random.choice instead of self.rng.choice)
        random.seed(seed)
        # Kept for backward compatibility with older tests that pass `db=`.
        self.db = db
        self.debug_logging: bool = False
        self._team_staff_effects: Dict[int, Dict[str, float]] = {}
        self.STAFF_EFFECT_CAP = 0.35
        self.STAFF_EFFECT_SATURATION_STRENGTH = 1.35
        self.DRIVER_EFFECT_CURVE_SCALE = 2.6
        self.discipline_calibration: Dict[str, Dict[str, float]] = (
            self._build_default_discipline_calibration()
        )
        self._active_discipline_calibration: Dict[str, float] = {}
        self._active_logistic_slopes: Dict[str, float] = dict(DEFAULT_LOGISTIC_SLOPES)
        self.START_GRID_SPACING_M = 20.0

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
        self.MAX_SPEED_MPS = 90.0  # ~324 km/h maximum speed
        self.MIN_SPEED_MPS = 30.0  # ~108 km/h minimum speed in corners

        # Performance factors
        # === SLIPSTREAM/DRAFTING EFFECT ===
        # When car is within 2 car lengths (50m) behind another, gets speed boost
        # from reduced air resistance. Real F1 data shows 5-10% boost.
        self.SLIPSTREAM_BONUS = 0.07  # 7% speed boost when drafting
        self.SLIPSTREAM_DISTANCE = 50.0  # Metres - effective draft range

        # === DIRTY AIR EFFECT - MUCH STRONGER ===
        # When following closely in corners, turbulent air reduces downforce
        # Real F1: 10-30% downforce loss, translates to ~5% speed loss in
        # corners
        # 15% speed loss in corners when following (was 5%)
        self.DIRTY_AIR_PENALTY = 0.15
        # Metres - dirty air affects up to this distance (was 100m)
        self.DIRTY_AIR_DISTANCE = 150.0
        self.TYRE_DEGRADATION_RATE = 0.00001  # Per timestep degradation
        self.FUEL_BURN_RATE = 0.00002  # Per timestep fuel consumption

        # AI decision parameters - MUCH MORE AGGRESSIVE
        self.ATTACK_THRESHOLD_GAP = 3.0  # Attack if within 3 seconds (was 1.0)
        # Defend if car within 2s behind (was 0.5s)
        self.DEFEND_THRESHOLD_GAP = 2.0
        # Consider cars within 150m as "nearby" (was 100m)
        self.NEARBY_DISTANCE_M = 150.0

        # Incident probabilities (per timestep) - Now track-aware
        self.BASE_INCIDENT_RATE = 0.0000002  # Base rate for normal driving
        self.OVERTAKE_INCIDENT_MULTIPLIER = 3.0  # Multiplier during overtakes

        # High closing-speed straight-line run-by tuning.
        self.OVERSPEED_AUTO_PASS_KMH = 18.0
        self.OVERSPEED_AUTO_PASS_MAX_GAP_M = 34.0
        self.OVERSPEED_HIGH_CONFIDENCE_PROB = 0.995

        # Pit strategy and service model
        self.PIT_LANE_SPEED_MPS = 22.0
        self.PIT_SERVICE_BASE_SECONDS = 4.0
        self.PIT_LANE_TRANSIT_SECONDS = 11.0
        self.PIT_TYRE_RESET = 0.94
        self.PIT_FUEL_GAIN = 0.40
        self.PIT_TYRE_THRESHOLD = 0.42
        self.PIT_MIN_LAPS_REMAINING = 3
        self.TYRE_BASE_WEAR_RATE = 0.000018
        self.TYRE_WEAR_PROFILES = {
            "soft": {
                "wear_multiplier": 1.55,
                "pace_base": 1.02,
                "pace_falloff_max": 0.24,
                "pace_falloff_curve": 1.25,
            },
            "medium": {
                "wear_multiplier": 1.00,
                "pace_base": 1.00,
                "pace_falloff_max": 0.18,
                "pace_falloff_curve": 1.40,
            },
            "hard": {
                "wear_multiplier": 0.72,
                "pace_base": 0.985,
                "pace_falloff_max": 0.13,
                "pace_falloff_curve": 1.55,
            },
            "rain": {
                "wear_multiplier": 1.18,
                "pace_base": 0.95,
                "pace_falloff_max": 0.16,
                "pace_falloff_curve": 1.30,
            },
            "wet": {
                "wear_multiplier": 1.18,
                "pace_base": 0.95,
                "pace_falloff_max": 0.16,
                "pace_falloff_curve": 1.30,
            },
        }
        self.TYRE_AI_PIT_WEAR_THRESHOLD = 0.58
        self.TYRE_AI_PIT_PACE_LOSS_THRESHOLD = 1.45
        self.TYRE_AI_STINT_MARGIN_LAPS = 2.0

        # Rallycross mandatory joker-lap model
        self.RALLYCROSS_JOKER_BASE_PENALTY_S = 2.8
        self._rallycross_joker_enabled = False

    def _build_default_discipline_calibration(self) -> Dict[str, Dict[str, float]]:
        """Return default per-discipline calibration profile.

        Profile key guide:
        - *_slope: logistic steepness for overtake/incident probability curves.
          Higher slope means a sharper jump between unlikely and likely.
                - tyre_eta / mech_eta: Weibull scale ("life") parameters.
                    Higher values delay typical failures.
                - tyre_beta / mech_beta: Weibull shape parameters.
                    Values > 1 model wear-out behaviour where risk increases over laps.
        """
        default = {
            "straight_slope": 3.8,
            "braking_slope": 3.4,
            "outside_slope": 3.2,
            "switch_slope": 3.0,
            "risk_slope": 3.4,
            "tyre_eta": 28.0,
            "tyre_beta": 2.6,
            "mech_eta": 95.0,
            "mech_beta": 2.1,
        }
        return {
            "DEFAULT": dict(default),
            "SINGLE_SEATER": dict(default),
            "PRODUCTION_TOURING": dict(default),
            "URBAN_STREET": dict(default),
            "DRAG_ACCELERATION": dict(default),
            "SPRINT_RALLYCROSS": dict(default),
            "ENDURANCE": dict(default),
        }

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
        player_team_driver_ids: Optional[
            List[int]
        ] = None,  # Player-controlled team car IDs
        # Player's pace and overtake settings
        player_overrides: Optional[Dict[str, float]] = None,
        weather_conditions: Optional[Dict[str, float]] = None,
        track_conditions: Optional[Dict[str, Any]] = None,
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
            weather_conditions,
            track_conditions,
        )

        # Headless runs are used by the statistical and performance tests, so
        # use a coarser simulation step there to keep the test suite tractable.
        timestep = 1.0 / 30.0 if event_callback else 1.0
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
        weather_conditions: Optional[Dict[str, float]],
        track_conditions: Optional[Dict[str, Any]],
    ) -> Tuple[RaceState, float]:
        """Prepare track map, controls and race state for simulation loop."""
        if self.debug_logging:
            print(f"-> Generating track map for {track.name}...")
        self.track_map = TrackMap(track=track)
        self._event_callback = event_callback
        if self.debug_logging:
            print(
                f"  OK Track map ready: {len(self.track_map.corners)} corners, {len(self.track_map.drs_zones)} DRS zones"
            )

        self.track_points = track_points
        if track_points and self.debug_logging:
            print(
                f"  OK Using visual track with {len(track_points)} points for position mapping"
            )

        self.player_driver_id = player_driver_id
        self.player_team_driver_ids = {
            int(x) for x in (player_team_driver_ids or []) if x is not None
        }
        self.player_overrides = player_overrides or {}
        self.weather_conditions = dict(weather_conditions or {})
        self.track_conditions = dict(track_conditions or {})
        self._current_race_state = None
        if player_driver_id and self.debug_logging:
            print(
                f"  OK Player driver ID {player_driver_id} with overrides: {self.player_overrides}"
            )
        if self.player_team_driver_ids and self.debug_logging:
            print(
                f"  OK Player team-controlled drivers: {sorted(self.player_team_driver_ids)}"
            )

        self._apply_discipline_calibration(track)
        self._configure_rallycross_joker_mode(track)

        track_length_m = track.length_km * 1000.0
        race_state = self._initialize_race(drivers, teams, track_length_m, total_laps)
        self._current_race_state = race_state
        self._hydrate_staff_effects_for_teams(teams)
        return race_state, track_length_m

    def _get_track_discipline(self, track: Track) -> str:
        return str(getattr(track, "primary_discipline", "") or "").upper()

    def _apply_discipline_calibration(self, track: Track) -> None:
        """Activate discipline-specific calibration for overtakes and reliability."""
        discipline = self._get_track_discipline(track)
        profile = self.discipline_calibration.get(
            discipline
        ) or self.discipline_calibration.get("DEFAULT", {})
        self._active_discipline_calibration = dict(profile)
        self._active_logistic_slopes = {
            "straight": self._active_discipline_calibration.get("straight_slope", 3.8),
            "braking": self._active_discipline_calibration.get("braking_slope", 3.4),
            "outside": self._active_discipline_calibration.get("outside_slope", 3.2),
            "switch": self._active_discipline_calibration.get("switch_slope", 3.0),
            "risk": self._active_discipline_calibration.get("risk_slope", 3.4),
        }

    def _hydrate_staff_effects_for_teams(
        self, teams: Dict[int, Team]
    ) -> None:  # NOSONAR
        """Compute normalised per-team staff effects from DB roster and role config."""
        self._team_staff_effects = {
            int(team_id): {} for team_id in teams.keys() if team_id is not None
        }
        if not self.db or not hasattr(self.db, "get_staff_by_team"):
            return

        for team_id, team in teams.items():
            if team_id is None:
                continue
            self._team_staff_effects[int(team_id)] = self._calculate_team_staff_effects(
                int(team_id), team
            )

    def _calculate_team_staff_effects(
        self, team_id: int, team: Team
    ) -> Dict[str, float]:
        db = self.db
        if db is None or not hasattr(db, "get_staff_by_team"):
            return {}
        try:
            staff = db.get_staff_by_team(team_id)
        except Exception:
            staff = []
        raw_effects: Dict[str, float] = {}
        discipline = str(getattr(team, "discipline", "") or "").upper()
        for member in staff:
            self._accumulate_staff_member_effects(raw_effects, member, discipline)
        return {
            key: self._saturate_staff_effect(value)
            for key, value in raw_effects.items()
        }

    def _accumulate_staff_member_effects(
        self, raw_effects: Dict[str, float], member: Any, discipline: str
    ) -> None:
        role_key = str(getattr(member, "role", "") or "").upper()
        cfg = STAFF_ROLES_CONFIG.get(role_key)
        if not cfg:
            return
        rating = float(getattr(member, "rating", 50.0) or 50.0)
        rating_factor = self._rating_impact_factor(rating)
        discipline_mod = float(cfg.get("discipline_modifiers", {}).get(discipline, 1.0))
        for effect_name, effect_value in cfg.get("base_effects", {}).items():
            raw_effects[effect_name] = raw_effects.get(effect_name, 0.0) + (
                float(effect_value) * rating_factor * discipline_mod
            )

    def _rating_impact_factor(self, rating: float) -> float:
        """Map staff rating to nonlinear impact where early improvements matter more."""
        normalized = max(0.0, min(1.0, float(rating) / 100.0))
        scale = 3.0
        raw = 1.0 - np.exp(-scale * normalized)
        max_raw = 1.0 - np.exp(-scale)
        return raw / max_raw if max_raw > 0.0 else normalized

    def _saturate_staff_effect(self, raw_effect: float) -> float:
        """Apply diminishing returns so stacking elite staff tails off near perfection."""
        x = max(0.0, float(raw_effect))
        cap = float(self.STAFF_EFFECT_CAP)
        strength = float(self.STAFF_EFFECT_SATURATION_STRENGTH)
        if cap <= 0.0:
            return 0.0
        saturated = cap * (1.0 - np.exp(-strength * (x / cap)))
        return max(0.0, min(cap, saturated))

    def _driver_attr_factor(self, value: float) -> float:
        """Map 0-100 driver attributes onto a diminishing-returns curve in [0,1]."""
        normalized = max(0.0, min(1.0, float(value) / 100.0))
        scale = float(self.DRIVER_EFFECT_CURVE_SCALE)
        raw = 1.0 - np.exp(-scale * normalized)
        max_raw = 1.0 - np.exp(-scale)
        return raw / max_raw if max_raw > 0.0 else normalized

    def _get_team_staff_effect(self, team: Team, effect_name: str) -> float:
        """Return precomputed staff effect for a team and effect key."""
        team_id = int(getattr(team, "id", 0) or 0)
        effects = self._team_staff_effects.get(team_id, {})
        return float(effects.get(effect_name, 0.0) or 0.0)

    def _configure_rallycross_joker_mode(self, track: Track) -> None:
        """Enable mandatory joker-lap logic for sprint/rallycross races."""
        discipline = str(getattr(track, "primary_discipline", "") or "").upper()
        explicit = bool(getattr(track, "joker_enabled", False))
        self._rallycross_joker_enabled = explicit or discipline == "SPRINT_RALLYCROSS"
        if self._rallycross_joker_enabled:
            print(
                f"  OK Rallycross joker-lap mode enabled (+{self.RALLYCROSS_JOKER_BASE_PENALTY_S:.2f}s route penalty)"
            )

    def _initial_joker_lap_target(self, driver_id: int, total_laps: int) -> int:
        """Pick a default joker lap target for a driver."""
        if total_laps <= 1:
            return 1
        if self.player_driver_id is not None and int(driver_id) == int(
            self.player_driver_id
        ):
            # Player can arm "come_in" whenever they want; if never armed,
            # joker is forced on final lap to satisfy mandatory usage.
            return max(1, int(total_laps))
        # Keep AI varied, but avoid final-lap clustering for most runs.
        upper = max(1, total_laps - 1)
        return int(self.rng.integers(1, upper + 1))

    def _player_requests_come_in_for_driver(self, state: DriverState) -> bool:
        """Return True when the player has armed a generic come-in request."""
        if self.player_driver_id is None or int(state.driver_id) != int(
            self.player_driver_id
        ):
            return False
        if not isinstance(getattr(self, "player_overrides", None), dict):
            return False
        return bool(self.player_overrides.get("come_in", False))

    def _consume_player_come_in_request(self, state: DriverState) -> None:
        """Reset one-shot come-in request after it has been acted upon."""
        if not self._player_requests_come_in_for_driver(state):
            return
        self.player_overrides["come_in"] = False

    def _requested_tyre_compound_for_driver(self, state: DriverState) -> str:
        """Resolve requested pit-stop tyre compound for a driver."""
        if self.player_driver_id is None or int(state.driver_id) != int(
            self.player_driver_id
        ):
            return self._select_ai_tyre_compound(state)
        if not isinstance(getattr(self, "player_overrides", None), dict):
            return "medium"
        raw = (
            str(self.player_overrides.get("pit_tyre_compound", "medium") or "medium")
            .strip()
            .lower()
        )
        return self._normalise_tyre_compound(raw)

    def _normalise_tyre_compound(self, compound: Any) -> str:
        """Return a supported tyre compound key."""
        raw = str(compound or "medium").strip().lower()
        if raw == "rain":
            raw = "wet"
        if raw not in self.TYRE_WEAR_PROFILES:
            return "medium"
        return raw

    def _tyre_profile(self, compound: Any) -> Dict[str, float]:
        """Return wear and pace profile for a compound."""
        key = self._normalise_tyre_compound(compound)
        return self.TYRE_WEAR_PROFILES.get(key, self.TYRE_WEAR_PROFILES["medium"])

    def _select_ai_tyre_compound(self, state: DriverState) -> str:
        """Choose a tyre compound for an AI pit stop."""
        race_state = getattr(self, "_current_race_state", None)
        total_laps = int(getattr(race_state, "total_laps", 12) or 12)
        laps_remaining = max(1, total_laps - int(state.lap))
        current_compound = self._normalise_tyre_compound(
            getattr(state, "tyre_compound", "medium")
        )
        current_wear = float(getattr(state, "tyre_condition", 1.0))

        wetness = self._safe_condition_float("track_wetness", 0.0)
        if wetness >= 0.45:
            return "wet"
        if total_laps <= 10:
            return "soft" if laps_remaining <= 4 else "medium"
        if laps_remaining <= 6:
            return "soft"
        return self._select_long_race_tyre(
            state, total_laps, laps_remaining, current_compound, current_wear
        )

    def _select_long_race_tyre(
        self,
        state: DriverState,
        total_laps: int,
        laps_remaining: int,
        current_compound: str,
        current_wear: float,
    ) -> str:
        if laps_remaining <= 11:
            return "medium"
        if current_wear < 0.35 and total_laps >= 18:
            return "hard"
        if current_compound == "soft" and current_wear < 0.55:
            return "medium"
        consistency = self._driver_attr_factor(
            get_safe_attribute(state.driver, "consistency")
        )
        professionalism = self._driver_attr_factor(
            get_driver_professionalism(state.driver)
        )
        if total_laps >= 18 and (consistency + professionalism) / 2.0 > 0.62:
            return "hard"
        if current_wear < 0.50 and laps_remaining > 8:
            return "medium"
        return "soft" if laps_remaining <= 8 else "medium"

    def _tyre_wear_per_step(self, state: DriverState) -> float:
        """Calculate tyre wear applied during one timestep."""
        profile = self._tyre_profile(state.tyre_compound)
        track_obj = (
            getattr(self.track_map, "track", None)
            if self.track_map is not None
            else None
        )
        surf = getattr(track_obj, "surface", None) or getattr(
            track_obj, "surface_type", None
        )
        surface_multipliers = {
            "asphalt": 1.0,
            "tarmac": 1.0,
            "concrete": 1.05,
            "gravel": 1.65,
            "mixed": 1.28,
            "dirt": 1.82,
        }
        surface_mul = surface_multipliers.get((surf or "").lower(), 1.0)
        driver_wear_factor = 1.0 - (
            (
                self._driver_attr_factor(
                    get_safe_attribute(state.driver, "consistency")
                )
                * 0.08
            )
            + (self._driver_attr_factor(get_vehicle_control(state.driver)) * 0.05)
        )
        driver_wear_factor = float(np.clip(driver_wear_factor, 0.82, 1.08))
        push_mul = 0.70 + (float(state.push_intensity) * 0.75)
        fatigue_mul = 1.0 + (float(state.push_fatigue) * 0.20)
        return (
            self.TYRE_BASE_WEAR_RATE
            * profile["wear_multiplier"]
            * surface_mul
            * driver_wear_factor
            * push_mul
            * fatigue_mul
        )

    def _tyre_pace_multiplier(self, state: DriverState) -> float:
        """Return a speed multiplier that decays smoothly as tyres wear."""
        profile = self._tyre_profile(state.tyre_compound)
        wear = 1.0 - float(np.clip(state.tyre_condition, 0.0, 1.0))
        pace_base = profile["pace_base"]
        falloff = profile["pace_falloff_max"] * (wear ** profile["pace_falloff_curve"])
        if wear > 0.70:
            falloff += (wear - 0.70) * 0.20
        if wear > 0.90:
            falloff += (wear - 0.90) * 0.35
        return float(np.clip(pace_base - falloff, 0.72, 1.03))

    def _projected_tyre_loss_seconds(
        self, state: DriverState, laps_ahead: float
    ) -> float:
        """Estimate lap-time loss from tyre wear over a short horizon."""
        if laps_ahead <= 0:
            return 0.0
        wear_rate = self._tyre_wear_per_step(state)
        # Derive steps-per-lap from current pace and simulation timestep.
        race_state = getattr(self, "_current_race_state", None)
        track_length_m = float(getattr(race_state, "track_length_m", 0.0) or 0.0)
        timestep = float(getattr(race_state, "timestep", 1.0 / 30.0) or (1.0 / 30.0))
        speed_mps = max(1.0, float(getattr(state, "velocity_mps", 0.0) or 0.0))
        if track_length_m > 0.0:
            est_lap_seconds = track_length_m / speed_mps
        else:
            est_lap_seconds = 92.0
        est_lap_seconds = float(np.clip(est_lap_seconds, 45.0, 220.0))
        steps_per_lap = max(1.0, est_lap_seconds / max(1e-6, timestep))
        projected_wear = wear_rate * steps_per_lap * laps_ahead
        projected_condition = max(0.0, float(state.tyre_condition) - projected_wear)
        current_mult = self._tyre_pace_multiplier(state)
        future_state = DriverState(
            driver_id=state.driver_id,
            driver_name=state.driver_name,
            driver=state.driver,
            team=state.team,
            tyre_condition=projected_condition,
            tyre_compound=state.tyre_compound,
        )
        future_mult = self._tyre_pace_multiplier(future_state)
        baseline_lap_seconds = 92.0
        return max(
            0.0, baseline_lap_seconds * (current_mult - future_mult) * laps_ahead
        )

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
        max_race_time_s = max(180.0, float(race_state.total_laps) * 240.0)
        while not self._race_finished(race_state):
            if self._should_stop_simulation(stop_event):
                break

            if self._apply_time_limit_if_needed(race_state, max_race_time_s):
                break

            frame = self._process_simulation_frame(
                frame=frame,
                race_state=race_state,
                track_length_m=track_length_m,
                timestep=timestep,
                event_callback=event_callback,
                realtime_speed=realtime_speed,
            )

        return frame

    def _should_stop_simulation(self, stop_event: Any) -> bool:
        """Return True if an external stop event requested termination."""
        if not (stop_event and stop_event.is_set()):
            return False
        print("\n[RACE ENGINE] Stop requested - terminating simulation")
        return True

    def _apply_time_limit_if_needed(
        self, race_state: RaceState, max_race_time_s: float
    ) -> bool:
        """Force-stop running cars when a race exceeds its safety time limit."""
        if race_state.current_time < max_race_time_s:
            return False
        for state in race_state.driver_states.values():
            if state.running:
                state.running = False
                state.dnf_reason = state.dnf_reason or "time_limit"
        if self.debug_logging:
            print(
                f"[RACE ENGINE] Time limit reached ({max_race_time_s:.1f}s), forcing race end"
            )
        return True

    def _process_simulation_frame(
        self,
        frame: int,
        race_state: RaceState,
        track_length_m: float,
        timestep: float,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
        realtime_speed: float,
    ) -> int:
        """Execute one simulation frame and return the incremented frame index."""
        frame_start = time.time()
        self._update_track_wetness(timestep, event_callback, race_state.current_time)
        self._update_running_drivers(
            race_state, track_length_m, timestep, event_callback
        )
        self._update_race_situation(race_state)
        self._log_frame_snapshot_if_needed(frame, race_state)

        next_frame = frame + 1
        race_state.current_time += timestep
        self._emit_position_update_if_needed(next_frame, race_state, event_callback)
        self._throttle_frame_if_needed(frame_start, timestep, realtime_speed)
        return next_frame

    def _update_track_wetness(
        self,
        timestep: float,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
        current_time: float,
    ) -> None:
        """Move track wetness toward precipitation-driven conditions over time."""
        precipitation = self._safe_condition_float("precipitation", 0.0)
        current = self._safe_condition_float("track_wetness", 0.0)
        target = float(np.clip(precipitation / 8.0, 0.0, 1.0))
        rate = 0.035 if target > current else 0.012
        updated = float(np.clip(current + (target - current) * rate * timestep * 30.0, 0.0, 1.0))
        previous_band = int(current * 4.0)
        updated_band = int(updated * 4.0)
        self.track_conditions["track_wetness"] = updated
        if updated_band != previous_band and callable(event_callback):
            event_callback(
                {
                    "type": "track_condition_update",
                    "time": float(current_time),
                    "track_wetness": updated,
                    "precipitation": precipitation,
                }
            )

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
            self._update_single_driver_step(
                driver_id, state, race_state, track_length_m, timestep, event_callback
            )

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
        if self._update_driver_pit_cycle(
            state, race_state, track_length_m, timestep, event_callback
        ):
            return

        self._update_racing_mode(state, race_state)
        speed_mps = self._calculate_speed(state, track_length_m)
        if not np.isfinite(speed_mps):
            print(
                f"  [WARN] Non-finite speed for {state.driver_name} -> replacing with MIN_SPEED_MPS"
            )
            speed_mps = float(self.MIN_SPEED_MPS)
        if self._check_driver_mistake(state):
            speed_mps *= 0.3

        self._advance_driver_position(
            state, race_state, speed_mps, timestep, track_length_m, event_callback
        )
        self._apply_driver_degradation(state)
        self._update_driver_stall_state(state, event_callback)
        self._update_driver_push_fatigue(state)

        if self._check_incident(state, race_state):
            state.running = False
            self._emit_driver_dnf_event_if_needed(driver_id, state)

    def _pit_strategy_enabled_for_track(self) -> bool:
        """Return whether this discipline should run pit strategy logic."""
        track_obj = (
            getattr(self.track_map, "track", None)
            if self.track_map is not None
            else None
        )
        discipline = str(getattr(track_obj, "primary_discipline", "") or "").upper()
        return discipline not in {"DRAG_ACCELERATION", "SPRINT_RALLYCROSS"}

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
        """Decide pit stops once per lap using tyre/fuel and mandatory-stop heuristics."""
        if self._pit_eval_already_processed_this_lap(state):
            return False

        # Player one-shot override: come in at next lap opportunity.
        if self._player_requests_come_in_for_driver(state):
            return True

        laps_remaining = race_state.total_laps - state.lap
        if self._pit_eval_not_in_window(state, laps_remaining):
            return False

        if self._pit_hard_trigger_active(state):
            return True
        if self._should_pit_for_weather(state, laps_remaining):
            return True
        if self._should_pit_for_ai_tyre_strategy(state, laps_remaining):
            return True
        if self._should_take_mandatory_stop(state, race_state, event_callback):
            return True
        if self._should_attempt_traffic_undercut(state):
            return True

        return False

    def _pit_eval_already_processed_this_lap(self, state: DriverState) -> bool:
        """Guard against repeated pit decisions within the same lap."""
        if state.last_pit_eval_lap == state.lap:
            return True
        state.last_pit_eval_lap = state.lap
        return False

    def _pit_eval_not_in_window(self, state: DriverState, laps_remaining: int) -> bool:
        """Return True when pit decisioning should be skipped this lap."""
        return state.lap <= 0 or laps_remaining < self.PIT_MIN_LAPS_REMAINING

    def _pit_hard_trigger_active(self, state: DriverState) -> bool:
        """Immediate pit triggers that ignore strategic nuance."""
        return (
            state.tyre_condition <= self.PIT_TYRE_THRESHOLD or state.fuel_load <= 0.14
        )

    def _is_player_controlled_for_pit_strategy(self, state: DriverState) -> bool:
        """Return True for the player-controlled driver in pit strategy logic."""
        return self.player_driver_id is not None and int(state.driver_id) == int(
            self.player_driver_id
        )

    def _should_pit_for_ai_tyre_strategy(
        self, state: DriverState, laps_remaining: int
    ) -> bool:
        """AI-only tyre strategy triggers based on wear and projected pace loss."""
        if self._is_player_controlled_for_pit_strategy(state):
            return False

        projected_loss = self._projected_tyre_loss_seconds(
            state, self.TYRE_AI_STINT_MARGIN_LAPS
        )
        if state.tyre_condition <= self.TYRE_AI_PIT_WEAR_THRESHOLD:
            return True
        return (
            projected_loss >= self.TYRE_AI_PIT_PACE_LOSS_THRESHOLD
            and laps_remaining > self.PIT_MIN_LAPS_REMAINING
        )

    def _should_pit_for_weather(
        self, state: DriverState, laps_remaining: int
    ) -> bool:
        """Pit when current tyres are unsuitable for a materially wet track."""
        if self._is_player_controlled_for_pit_strategy(state):
            return False
        if laps_remaining <= self.PIT_MIN_LAPS_REMAINING:
            return False
        wetness = self._safe_condition_float("track_wetness", 0.0)
        is_wet = state.tyre_compound.lower() in {"wet", "rain"}
        if wetness >= 0.45 and not is_wet:
            return True
        return wetness <= 0.12 and is_wet

    def _should_take_mandatory_stop(
        self,
        state: DriverState,
        race_state: RaceState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> bool:
        """Evaluate mandatory-stop policy for longer races."""
        if race_state.total_laps < 20 or state.pit_stops_completed != 0:
            return False

        mandatory_window_lap = int(race_state.total_laps * 0.55)
        self._emit_pit_window_open_if_needed(
            state, mandatory_window_lap, event_callback
        )
        return state.lap >= mandatory_window_lap and state.tyre_condition < 0.72

    def _should_attempt_traffic_undercut(self, state: DriverState) -> bool:
        """Return True for occasional undercut calls when trapped in traffic."""
        in_traffic_window = 0.8 < state.gap_ahead < 2.5
        return (
            in_traffic_window
            and state.tyre_condition < 0.65
            and self.rng.random() < 0.20
        )

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
        if self.player_driver_id is None or int(state.driver_id) != int(
            self.player_driver_id
        ):
            return
        if not event_callback:
            return

        state.pit_window_notified = True
        event_callback(
            {
                "type": "pit_window_open",
                "driver_id": state.driver_id,
                "driver_name": state.driver_name,
                "lap": state.lap,
                "window_lap": mandatory_window_lap,
            }
        )

    def _enter_pit_lane(
        self,
        state: DriverState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Start pit phase and emit telemetry event."""
        service_variance = float(self.rng.uniform(-0.7, 0.7))
        pitstop_effect = self._get_team_staff_effect(state.team, "pitstop")
        operations_effect = self._get_team_staff_effect(state.team, "operations")
        strategy_effect = self._get_team_staff_effect(state.team, "strategy")
        pit_reduction = min(
            1.8,
            6.0
            * (pitstop_effect * 0.6 + operations_effect * 0.3 + strategy_effect * 0.1),
        )
        total_pit_time = (
            self.PIT_LANE_TRANSIT_SECONDS
            + self.PIT_SERVICE_BASE_SECONDS
            + service_variance
            - pit_reduction
        )
        self._consume_player_come_in_request(state)
        state.requested_tyre_compound = self._requested_tyre_compound_for_driver(state)
        state.in_pit_lane = True
        state.pit_time_remaining_s = max(6.0, total_pit_time)
        state.pit_total_time_s = state.pit_time_remaining_s
        state.racing_mode = RacingMode.MANAGE
        if event_callback:
            event_callback(
                {
                    "type": "pit_entry",
                    "driver_id": state.driver_id,
                    "driver_name": state.driver_name,
                    "lap": state.lap,
                    "pit_time_remaining_s": state.pit_time_remaining_s,
                    "pit_total_time_s": state.pit_total_time_s,
                    "tyre_compound": state.requested_tyre_compound,
                }
            )

    def _exit_pit_lane(
        self,
        state: DriverState,
        event_callback: Optional[Callable[[Dict[str, Any]], None]],
    ) -> None:
        """Apply service effects and emit pit exit telemetry."""
        state.in_pit_lane = False
        state.pit_time_remaining_s = 0.0
        state.pit_total_time_s = 0.0
        state.pit_stops_completed += 1
        state.tyre_condition = 1.0
        state.fuel_load = min(1.0, state.fuel_load + self.PIT_FUEL_GAIN)
        state.tyre_compound = state.requested_tyre_compound or "medium"
        if event_callback:
            event_callback(
                {
                    "type": "pit_exit",
                    "driver_id": state.driver_id,
                    "driver_name": state.driver_name,
                    "lap": state.lap,
                    "pit_stops_completed": state.pit_stops_completed,
                    "tyre_compound": state.tyre_compound,
                }
            )

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
        """Apply tyre wear and fuel burn from surface and tyre compound."""
        degradation = self._tyre_wear_per_step(state)
        state.tyre_condition = max(0.0, state.tyre_condition - degradation)
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
        state.dnf_reason = "stalled"
        print(
            f"  [STALL] {state.driver_name} marked DNF (stalled) after {state.stall_frames} frames"
        )
        if event_callback:
            event_callback(
                {
                    "type": "dnf",
                    "driver_id": state.driver_id,
                    "driver_name": state.driver_name,
                    "lap": state.lap,
                    "reason": state.dnf_reason,
                }
            )

    def _update_driver_push_fatigue(self, state: DriverState) -> None:
        """Update fatigue accumulation/recovery based on current push level."""
        fatigue_gain_rate = 0.00035
        fatigue_recovery_rate = 0.00008
        fatigue_cap = 1.0

        if self._is_player_full_attack(state):
            # Max player attack should still carry risk, but not collapse pace in short runs.
            fatigue_gain_rate = 0.00016
            fatigue_recovery_rate = 0.00010
            fatigue_cap = 0.55

        if state.push_intensity > 0.8:
            state.push_fatigue += fatigue_gain_rate * (state.push_intensity - 0.8)
        else:
            state.push_fatigue = max(0.0, state.push_fatigue - fatigue_recovery_rate)
        state.push_fatigue = min(fatigue_cap, state.push_fatigue)
        state.frames_since_mistake += 1

    def _emit_driver_dnf_event_if_needed(
        self, driver_id: int, state: DriverState
    ) -> None:
        """Emit DNF event once for a driver when available."""
        if not (hasattr(self, "_event_callback") and callable(self._event_callback)):
            return
        if getattr(state, "dnf_event_emitted", False):
            return
        try:
            self._event_callback(
                {
                    "type": "dnf",
                    "driver_id": driver_id,
                    "driver_name": state.driver_name,
                    "lap": state.lap,
                    "reason": state.dnf_reason,
                }
            )
            state.dnf_event_emitted = True
        except Exception:
            pass

    def _log_frame_snapshot_if_needed(self, frame: int, race_state: RaceState) -> None:
        """Periodic verbose snapshot for debugging frame-by-frame state."""
        if not self.debug_logging:
            return
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
        if self.debug_logging and frame % 90 == 0:
            print(
                f"  -> Emitting {len(position_event['positions'])} car positions to GUI"
            )
        event_callback(position_event)

    def _throttle_frame_if_needed(
        self, frame_start: float, timestep: float, realtime_speed: float
    ) -> None:
        """Sleep to honour realtime_speed for low-speed visualised runs."""
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
            event_callback(
                {
                    "type": "race_finished",
                    "total_laps": total_laps,
                    "race_time": race_state.current_time,
                    "results": results,
                    "collision_log": race_state.collision_log,
                }
            )
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
            random.seed(seed)

        # Kept for signature compatibility.
        _ = discipline
        _ = verbose
        _ = iterations
        _ = kwargs

        # Older tests may pass teams as a list/tuple; normalise to {team_id: team}.
        if not hasattr(teams, "get"):
            teams = cast(Dict[int, Team], {
                int(getattr(team, "id", idx + 1)): team
                for idx, team in enumerate(list(teams))
            })

        # Ensure each driver is assigned to a valid team for race init.
        team_ids = list(teams.keys())
        if team_ids:
            for idx, driver in enumerate(drivers):
                if getattr(driver, "current_team_id", None) not in teams:
                    setattr(driver, "current_team_id", team_ids[idx % len(team_ids)])

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
        total_laps: int,
    ) -> RaceState:
        """Initialise race with starting grid"""
        race_state = RaceState(total_laps=total_laps, track_length_m=track_length_m)

        # Seed the initial grid so identical seeds stay reproducible while
        # different seeds can produce different first-lap ordering. We use a
        # light qualifying-style ranking so stronger drivers usually start
        # nearer the front, but small seeded variation can still reshuffle the
        # grid across runs.
        driver_grid_scores = []
        for driver_index, driver in enumerate(drivers):
            skill_score = (
                float(get_safe_attribute(driver, "speed")) * 0.45
                + float(get_safe_attribute(driver, "racecraft")) * 0.35
                + float(get_safe_attribute(driver, "consistency")) * 0.20
            )
            qualifying_noise = float(self.rng.normal(0.0, 18.0))
            driver_grid_scores.append((-(skill_score + qualifying_noise), driver_index))
        grid_order = [driver_index for _, driver_index in sorted(driver_grid_scores)]
        grid_slots = {
            driver_index: grid_position
            for grid_position, driver_index in enumerate(grid_order)
        }

        # Create driver states in grid order
        for i, driver in enumerate(drivers):
            current_team_id = getattr(driver, "current_team_id", None)
            team = teams.get(current_team_id) if isinstance(current_team_id, int) else None
            if not team:
                continue

            # Stagger starting positions using the seeded grid order.
            # NOTE: SAFE_FOLLOWING_DISTANCE used in collision detection is
            # approximately 15.0m, so keep the spacing comfortably above that.
            starting_position = (len(drivers) - grid_slots.get(i, i) - 1) * float(
                self.START_GRID_SPACING_M
            )

            # Calculate initial push intensity based on driver personality
            raw_speed = get_safe_attribute(driver, "speed") / 100.0
            aggression = get_driver_aggression(driver) / 100.0
            # Risk is derived from professionalism: less professional -> more risk
            professionalism = get_driver_professionalism(driver)
            risk = (100.0 - professionalism) / 100.0
            # Range: 0.3 to 1.0
            initial_push = 0.3 + (raw_speed * 0.2) + (aggression * 0.3) + (risk * 0.2)

            state = DriverState(
                driver_id=driver.id,
                driver_name=driver.name,
                driver=driver,
                team=team,
                position_m=starting_position,
                position=grid_slots.get(i, i) + 1,
                lap=0,
                push_fatigue=0.0,
                frames_since_mistake=999,
                push_intensity=initial_push,
            )

            if self._rallycross_joker_enabled:
                state.joker_lap_target = self._initial_joker_lap_target(
                    driver.id, total_laps
                )

            if self.debug_logging:
                print(
                    f"  [INIT] {driver.name}: speed={get_safe_attribute(driver, 'speed'):.1f} -> initial_push={initial_push:.2f}"
                )

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
            (
                hasattr(self, "player_driver_id")
                and self.player_driver_id == state.driver_id
            )
            or (
                hasattr(self, "player_team_driver_ids")
                and state.driver_id in getattr(self, "player_team_driver_ids", set())
            )
        )

    def _is_player_full_attack(self, state: DriverState) -> bool:
        """Return True when a controlled driver is explicitly on max attack inputs."""
        if not self._is_player_controlled_driver(state):
            return False
        if not (
            hasattr(self, "player_overrides")
            and isinstance(self.player_overrides, dict)
        ):
            return False
        push = float(self.player_overrides.get("push", state.push_intensity))
        overtake = float(self.player_overrides.get("overtake", 0.0))
        return push >= 0.95 and overtake >= 0.95

    def _apply_player_racing_overrides_if_controlled(
        self, state: DriverState, driver: Driver
    ) -> bool:
        """Apply player UI overrides for controlled drivers; return True if handled."""
        if not self._is_player_controlled_driver(state):
            return False
        if not (hasattr(self, "player_overrides") and self.player_overrides):
            return True

        self._apply_player_push_override(state, driver)
        self._apply_player_overtake_mode_override(state)
        self._log_player_control_snapshot(driver, state)
        return True

    def _apply_player_push_override(self, state: DriverState, driver: Driver) -> None:
        if "push" not in self.player_overrides:
            return
        old_push = state.push_intensity
        state.push_intensity = self.player_overrides["push"]
        if not hasattr(self, "_player_push_logged"):
            self._player_push_logged = True
            print(
                f"[PLAYER PUSH APPLIED] {driver.name}: {old_push:.2f} -> {state.push_intensity:.2f} (from sliders)"
            )

    def _apply_player_overtake_mode_override(self, state: DriverState) -> None:
        if "overtake" not in self.player_overrides:
            return
        overtake_multiplier = self.player_overrides["overtake"]
        push_multiplier = float(self.player_overrides.get("push", state.push_intensity))
        threshold = self.ATTACK_THRESHOLD_GAP * (1.5 - overtake_multiplier * 0.5)

        # Keep full attack sticky for controlled drivers fighting through the pack.
        if (
            state.position > 1
            and overtake_multiplier >= 0.95
            and push_multiplier >= 0.95
        ):
            state.racing_mode = RacingMode.ATTACK
            return

        # Keep chasing if gap sentinel indicates separation/lap mismatch.
        if (
            state.position > 1
            and state.gap_ahead >= 900.0
            and overtake_multiplier >= 0.6
        ):
            state.racing_mode = RacingMode.ATTACK
            return

        if state.gap_ahead < threshold and overtake_multiplier > 0.3:
            state.racing_mode = RacingMode.ATTACK
        elif state.gap_behind < self.DEFEND_THRESHOLD_GAP:
            state.racing_mode = RacingMode.DEFEND
        else:
            state.racing_mode = RacingMode.MANAGE

    def _log_player_control_snapshot(self, driver: Driver, state: DriverState) -> None:
        if not hasattr(self, "_player_log_counter"):
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
        raw_speed = self._driver_attr_factor(get_safe_attribute(driver, "speed"))
        aggression = self._driver_attr_factor(get_driver_aggression(driver))
        consistency = self._driver_attr_factor(
            get_safe_attribute(driver, "consistency")
        )
        professionalism = get_driver_professionalism(driver)
        professionalism_factor = self._driver_attr_factor(professionalism)
        risk_tolerance = 1.0 - professionalism_factor

        base_push = (
            0.4 + (raw_speed * 0.2) + (aggression * 0.2) + (risk_tolerance * 0.2)
        )
        variability = (1.0 - consistency) * self.rng.uniform(-0.05, 0.05)
        base_push = max(0.35, min(1.0, base_push + variability))
        return base_push, consistency

    def _apply_attack_mode_if_needed(
        self,
        state: DriverState,
        race_state: RaceState,
        driver: Driver,
        base_push: float,
    ) -> bool:
        if not (state.gap_ahead < self.ATTACK_THRESHOLD_GAP and state.position > 1):
            return False

        car_ahead = self._get_car_ahead(state, race_state)
        if car_ahead and self.track_map:
            self._apply_track_aware_attack(
                state, race_state, driver, car_ahead, base_push
            )
        else:
            state.racing_mode = RacingMode.ATTACK
            state.push_intensity = min(1.0, base_push + 0.06)
        return True

    def _apply_track_aware_attack(
        self,
        state: DriverState,
        race_state: RaceState,
        driver: Driver,
        car_ahead: DriverState,
        base_push: float,
    ) -> None:
        if self.track_map is None:
            state.racing_mode = RacingMode.ATTACK
            state.push_intensity = min(1.0, base_push + 0.06)
            return

        section_type, corner = self.track_map.get_section_at_position(
            state.position_m % race_state.track_length_m
        )
        gap_m = state.gap_ahead * state.velocity_mps
        player_overrides = (
            getattr(self, "player_overrides", {})
            if isinstance(getattr(self, "player_overrides", None), dict)
            else {}
        )
        attack_context = {
            "is_player_controlled": self._is_player_controlled_driver(state),
            "push_intensity": float(state.push_intensity),
            "overtake_intensity": float(player_overrides.get("overtake", 0.5) or 0.5),
            "racing_mode": state.racing_mode.value,
        }

        should_attempt, success_prob, attempt_type = evaluate_overtaking_opportunity(
            attacker=driver,
            defender=car_ahead.driver,
            attacker_speed_kmh=state.velocity_mps * 3.6,
            defender_speed_kmh=car_ahead.velocity_mps * 3.6,
            gap_m=gap_m,
            section=section_type,
            corner=corner,
            logistic_slopes=self._active_logistic_slopes,
            attack_context=attack_context,
        )

        speed_advantage_kmh = (state.velocity_mps - car_ahead.velocity_mps) * 3.6
        should_attempt, success_prob, attempt_type = (
            self._apply_overspeed_straight_override(
                should_attempt=should_attempt,
                success_prob=float(success_prob),
                attempt_type=attempt_type,
                section_type=section_type,
                gap_m=float(gap_m),
                speed_advantage_kmh=float(speed_advantage_kmh),
            )
        )

        should_attempt, success_prob, attempt_type = (
            self._apply_player_committed_pass_override(
                state=state,
                should_attempt=should_attempt,
                success_prob=float(success_prob),
                attempt_type=attempt_type,
                section_type=section_type,
                gap_m=float(gap_m),
                speed_advantage_kmh=float(speed_advantage_kmh),
            )
        )

        if not should_attempt:
            state.racing_mode = RacingMode.MANAGE
            return

        state.racing_mode = RacingMode.ATTACK
        state.racing_line = (
            RacingLine.ATTACKING
            if attempt_type
            in {
                OvertakeAttemptType.LATE_BRAKING,
                OvertakeAttemptType.AROUND_OUTSIDE,
                OvertakeAttemptType.SWITCHBACK,
            }
            else RacingLine.IDEAL
        )
        state.push_intensity = min(1.0, base_push + 0.35)
        self._log_overtake_attempt(
            driver.name, car_ahead.driver.name, gap_m, success_prob
        )
        self._start_overtake_if_not_on_cooldown(
            state,
            car_ahead,
            race_state,
            attempt_type,
            gap_m,
            corner,
            section_type,
            float(success_prob),
        )

    def _apply_overspeed_straight_override(
        self,
        should_attempt: bool,
        success_prob: float,
        attempt_type: OvertakeAttemptType,
        section_type: Any,
        gap_m: float,
        speed_advantage_kmh: float,
    ) -> Tuple[bool, float, OvertakeAttemptType]:
        """Force a clean straight-line pass when closing speed is overwhelming."""
        if section_type != TrackSection.STRAIGHT:
            return should_attempt, success_prob, attempt_type
        if speed_advantage_kmh < self.OVERSPEED_AUTO_PASS_KMH:
            return should_attempt, success_prob, attempt_type
        if gap_m > self.OVERSPEED_AUTO_PASS_MAX_GAP_M:
            return should_attempt, success_prob, attempt_type
        return (
            True,
            max(success_prob, self.OVERSPEED_HIGH_CONFIDENCE_PROB),
            OvertakeAttemptType.SLIPSTREAM_STRAIGHT,
        )

    def _apply_player_committed_pass_override(
        self,
        state: DriverState,
        should_attempt: bool,
        success_prob: float,
        attempt_type: OvertakeAttemptType,
        section_type: Any,
        gap_m: float,
        speed_advantage_kmh: float,
    ) -> Tuple[bool, float, OvertakeAttemptType]:
        """Force committed player pass attempts at tiny gaps under max controls."""
        if not self._is_player_controlled_driver(state):
            return should_attempt, success_prob, attempt_type

        overrides = (
            getattr(self, "player_overrides", {})
            if isinstance(getattr(self, "player_overrides", None), dict)
            else {}
        )
        push = float(
            overrides.get("push", state.push_intensity) or state.push_intensity
        )
        overtake = float(overrides.get("overtake", 0.5) or 0.5)
        if push < 0.95 or overtake < 0.90:
            return should_attempt, success_prob, attempt_type
        if gap_m > 10.0 or speed_advantage_kmh < 0.5:
            return should_attempt, success_prob, attempt_type

        if section_type == TrackSection.STRAIGHT:
            return (
                True,
                max(success_prob, 0.97),
                OvertakeAttemptType.SLIPSTREAM_STRAIGHT,
            )
        if section_type == TrackSection.BRAKING_ZONE:
            return True, max(success_prob, 0.88), OvertakeAttemptType.LATE_BRAKING
        return True, max(success_prob, 0.80), attempt_type

    def _log_overtake_attempt(
        self, attacker_name: str, defender_name: str, gap_m: float, success_prob: float
    ) -> None:
        if not hasattr(self, "_overtake_log_counter"):
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
        section_type: Any,
        success_prob: float,
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
            attacker_line=state.racing_line,
            defender_line=(
                car_ahead.racing_line
                if car_ahead.racing_mode == RacingMode.DEFEND
                else RacingLine.IDEAL
            ),
            success_probability=float(np.clip(success_prob, 0.05, 0.95)),
        )

        # Emit quality context so calibration can reward realistic opportunities,
        # not just raw attempt volume.
        if hasattr(self, "_event_callback") and callable(self._event_callback):
            try:
                self._event_callback(
                    {
                        "type": "overtake_attempt",
                        "attacker_id": state.driver_id,
                        "attacker_name": state.driver_name,
                        "defender_id": car_ahead.driver_id,
                        "defender_name": car_ahead.driver_name,
                        "lap": state.lap,
                        "time": race_state.current_time,
                        "section": str(getattr(section_type, "value", section_type)),
                        "attempt_type": normalized_attempt_type.value,
                        "gap_m": float(gap_m),
                        "speed_advantage_kmh": float(
                            (state.velocity_mps - car_ahead.velocity_mps) * 3.6
                        ),
                        "push_intensity": float(state.push_intensity),
                        "success_probability": float(success_prob),
                    }
                )
            except Exception:
                pass

    def _apply_defend_mode_if_needed(
        self,
        state: DriverState,
        race_state: RaceState,
        driver: Driver,
        base_push: float,
    ) -> bool:
        if not (
            state.gap_behind < self.DEFEND_THRESHOLD_GAP
            and state.position < len(race_state.driver_states)
        ):
            return False

        car_behind = self._get_car_behind(state, race_state)
        state.racing_mode = RacingMode.DEFEND
        state.push_intensity = min(1.0, base_push + 0.10)
        if car_behind and self.track_map:
            section_type, corner = self.track_map.get_section_at_position(
                state.position_m % race_state.track_length_m
            )
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

    def _apply_manage_or_cruise_mode(
        self, state: DriverState, base_push: float, consistency: float
    ) -> None:
        if state.gap_ahead > 3.0 and state.gap_behind > 3.0:
            state.racing_mode = RacingMode.MANAGE
            # High-consistency drivers should be slightly more efficient, not
            # dramatically slower. Keep manage mode near base pace while still
            # giving reliable drivers a small advantage.
            conservation_factor = 0.94 + (consistency * 0.08)
            state.push_intensity = base_push * conservation_factor
            state.racing_line = RacingLine.IDEAL
            return

        state.racing_mode = RacingMode.CRUISE
        state.push_intensity = base_push
        state.racing_line = RacingLine.IDEAL

    def _apply_post_mode_push_adjustments(
        self, state: DriverState, consistency: float
    ) -> None:
        """Apply tyre/fatigue randomization and clamp final push intensity."""
        if state.tyre_condition < 0.7:
            tyre_factor = 0.5 + (state.tyre_condition * 0.5)
            state.push_intensity *= tyre_factor
        variance = (1.0 - consistency) * 0.15
        state.push_intensity += self.rng.normal(0, variance)
        state.push_intensity = np.clip(state.push_intensity, 0.3, 1.0)

    def _calculate_speed(self, state: DriverState, track_length_m: float) -> float:
        """
        Calculate current speed with DRAMATIC variation based on push_intensity

        Returns speed in metres per second.
        """
        driver = state.driver
        team = state.team

        # Base speed from driver canonical skill and team capability
        raw_speed = self._driver_attr_factor(get_safe_attribute(driver, "speed"))
        cornering_skill = self._driver_attr_factor(get_cornering_skill(driver))
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
        driver_modifier = 0.94 + (raw_speed * 0.11)

        # Team performance adds small bonus (0-5%)
        team_modifier = 0.975 + (team_performance * 0.05)

        section, corner = self._get_live_track_section(state, track_length_m)
        vehicle_profile = self._get_vehicle_profile()
        in_corner = section in {
            TrackSection.SLOW_CORNER,
            TrackSection.MEDIUM_CORNER,
            TrackSection.FAST_CORNER,
            TrackSection.BRAKING_ZONE,
        }

        if in_corner:
            corner_modifier = (
                0.84
                + (cornering_skill * 0.16)
            ) * vehicle_profile["cornering_multiplier"]
        else:
            corner_modifier = vehicle_profile["straight_multiplier"]

        # Calculate final speed
        speed = (
            reference_speed
            * push_multiplier
            * driver_modifier
            * team_modifier
            * corner_modifier
        )

        self._log_speed_debug(state, push_multiplier, speed)

        # Tyre wear now falls off progressively by compound and wear state.
        speed *= self._tyre_pace_multiplier(state)
        speed *= self._live_grip_multiplier(state, section, corner)

        if corner is not None:
            corner_speed_mps = (
                corner.apex_speed_kmh
                / 3.6
                * vehicle_profile["cornering_multiplier"]
            )
            speed = min(speed, max(self.MIN_SPEED_MPS, corner_speed_mps))

        # Fuel weight - lighter car is faster
        fuel_bonus = 1.0 + (1.0 - state.fuel_load) * 0.03
        speed *= fuel_bonus

        # Push fatigue - accumulated stress from pushing hard
        # Increases mistake probability and slightly reduces performance
        if state.push_fatigue > 0.3:
            fatigue_drag = 0.25
            if self._is_player_full_attack(state):
                fatigue_drag = 0.12
            fatigue_penalty = 1.0 - (state.push_fatigue * fatigue_drag)
            speed *= fatigue_penalty

        # === SLIPSTREAM BOOST (straights) ===
        if state.in_slipstream:
            speed *= 1.0 + self.SLIPSTREAM_BONUS

        speed = self._apply_dirty_air_penalty(speed, state, track_length_m)

        speed = self._apply_collision_avoidance(speed, state)

        # Consistency variance
        consistency = self._driver_attr_factor(
            get_safe_attribute(driver, "consistency")
        )
        speed_variance = (1.0 - consistency) * 0.05
        speed *= 1.0 + self.rng.normal(0, speed_variance)

        # Clamp to realistic bounds
        return np.clip(speed, self.MIN_SPEED_MPS, self.MAX_SPEED_MPS)

    def _is_in_corner_proxy(self, state: DriverState, track_length_m: float) -> bool:
        """Compatibility wrapper for callers that only need corner occupancy."""
        section, _ = self._get_live_track_section(state, track_length_m)
        return section in {
            TrackSection.SLOW_CORNER,
            TrackSection.MEDIUM_CORNER,
            TrackSection.FAST_CORNER,
            TrackSection.BRAKING_ZONE,
        }

    def _get_live_track_section(
        self, state: DriverState, track_length_m: float
    ) -> Tuple[TrackSection, Optional[Any]]:
        if self.track_map is None:
            return TrackSection.STRAIGHT, None
        return self.track_map.get_section_at_position(
            state.position_m % max(1.0, track_length_m)
        )

    def _get_vehicle_profile(self) -> Dict[str, float]:
        """Return discipline-specific handling characteristics for live physics."""
        discipline = "SINGLE_SEATER"
        if self.track_map is not None:
            discipline = str(
                getattr(self.track_map.track, "primary_discipline", discipline)
                or discipline
            ).upper()
        profiles = {
            "SINGLE_SEATER": {
                "straight_multiplier": 1.04,
                "cornering_multiplier": 1.08,
                "surface_sensitivity": 0.65,
            },
            "PRODUCTION_TOURING": {
                "straight_multiplier": 0.96,
                "cornering_multiplier": 0.94,
                "surface_sensitivity": 0.85,
            },
            "URBAN_STREET": {
                "straight_multiplier": 0.98,
                "cornering_multiplier": 0.97,
                "surface_sensitivity": 0.95,
            },
            "SPRINT_RALLYCROSS": {
                "straight_multiplier": 0.90,
                "cornering_multiplier": 0.91,
                "surface_sensitivity": 1.15,
            },
            "ENDURANCE": {
                "straight_multiplier": 0.93,
                "cornering_multiplier": 0.96,
                "surface_sensitivity": 0.80,
            },
        }
        return profiles.get(discipline, profiles["SINGLE_SEATER"])

    def _live_grip_multiplier(
        self,
        state: DriverState,
        section: TrackSection,
        corner: Optional[Any],
    ) -> float:
        """Combine surface, weather, line, tyre, and driver adaptation grip."""
        if section == TrackSection.STRAIGHT:
            return 1.0

        profile = self._get_vehicle_profile()
        base_grip = float(getattr(corner, "grip_level", 1.0) or 1.0)
        track_grip = self.track_conditions.get("grip_level", 1.0)
        try:
            base_grip *= float(track_grip)
        except (TypeError, ValueError):
            pass

        precipitation = self._safe_condition_float("precipitation", 0.0)
        wetness = self._safe_condition_float("track_wetness", precipitation / 8.0)
        wetness = float(np.clip(wetness, 0.0, 1.0))
        wet_skill = self._driver_attr_factor(
            get_safe_attribute(state.driver, "wet_weather_skill")
        )
        tyre_is_wet = state.tyre_compound.lower() in {"wet", "rain"}
        wet_tyre_factor = 1.0
        if wetness > 0.15:
            wet_tyre_factor = 1.04 if tyre_is_wet else 0.72
        weather_factor = 1.0 - (wetness * (0.18 - (wet_skill * 0.08)))
        line_factor = {
            RacingLine.IDEAL: 1.0,
            RacingLine.DEFENSIVE: 0.97,
            RacingLine.ATTACKING: 0.96,
            RacingLine.OFF_LINE: 0.87,
        }.get(state.racing_line, 1.0)
        if wetness > 0.45 and state.racing_line == RacingLine.OFF_LINE:
            line_factor *= 0.92

        adaptation = self._driver_attr_factor(
            get_safe_attribute(state.driver, "surface_adaptation")
        )
        surface_factor = 1.0 - (
            max(0.0, 1.0 - base_grip) * profile["surface_sensitivity"] * (1.0 - adaptation * 0.35)
        )
        return float(
            np.clip(surface_factor * weather_factor * wet_tyre_factor * line_factor, 0.55, 1.08)
        )

    def _safe_condition_float(self, key: str, default: float) -> float:
        try:
            return float(self.track_conditions.get(key, self.weather_conditions.get(key, default)))
        except (TypeError, ValueError):
            return float(default)

    def _log_speed_debug(
        self, state: DriverState, push_multiplier: float, speed: float
    ) -> None:
        """Emit throttled speed diagnostics for early frames and periodic checkpoints."""
        if not self.debug_logging:
            return
        if not hasattr(self, "_speed_debug_counter"):
            self._speed_debug_counter = 0
        self._speed_debug_counter += 1
        if self._speed_debug_counter < 50 or self._speed_debug_counter % 300 == 0:
            print(
                f"  [SPEED] {state.driver_name}: push={state.push_intensity:.2f} -> mult={push_multiplier:.2f} -> speed={speed:.1f}m/s"
            )

    def _apply_dirty_air_penalty(
        self, speed: float, state: DriverState, track_length_m: float
    ) -> float:
        """Apply corner dirty-air speed penalty when following too closely."""
        if not (hasattr(self, "track_map") and self.track_map):
            return speed

        position_on_track = state.position_m % track_length_m
        section_type, _ = self.track_map.get_section_at_position(position_on_track)
        is_corner = section_type in [
            TrackSection.SLOW_CORNER,
            TrackSection.MEDIUM_CORNER,
            TrackSection.FAST_CORNER,
            TrackSection.BRAKING_ZONE,
        ]

        if (
            is_corner
            and state.velocity_mps > 1.0
            and state.gap_ahead < self.DIRTY_AIR_DISTANCE / state.velocity_mps
        ):
            return speed * (1.0 - self.DIRTY_AIR_PENALTY)
        return speed

    def _apply_collision_avoidance(self, speed: float, state: DriverState) -> float:
        """Reduce speed using smooth desired-gap dynamics instead of hard thresholds."""
        if state.velocity_mps <= 0.1:
            return speed

        if state.gap_ahead >= 3.0:
            return speed

        car_length = 4.0
        standstill_gap = car_length * self._collision_standstill_gap_multiplier(state)
        headway_time = self._collision_headway_time(state)
        desired_gap = standstill_gap + (state.velocity_mps * headway_time)
        actual_gap = max(
            0.0, state.gap_ahead * max(state.velocity_mps, self.BASE_SPEED_MPS * 0.35)
        )

        if actual_gap >= desired_gap:
            return speed

        ratio = actual_gap / max(desired_gap, 1e-6)
        soft_brake = np.clip(ratio**1.35, self._collision_brake_floor(state), 1.0)
        speed *= float(soft_brake)

        if actual_gap < standstill_gap:
            speed *= self._collision_critical_gap_penalty(state)
        return speed

    def _collision_headway_time(self, state: DriverState) -> float:
        """Return adaptive time headway for collision-avoidance target gap."""
        base_headway = 0.45 + ((1.0 - float(state.push_intensity)) * 0.90)
        if state.racing_mode == RacingMode.ATTACK:
            base_headway *= 0.78

        if not self._is_player_controlled_driver(state):
            return max(0.18, base_headway)

        overtake = float(
            getattr(self, "player_overrides", {}).get("overtake", 0.5) or 0.5
        )
        push = float(
            getattr(self, "player_overrides", {}).get("push", state.push_intensity)
            or state.push_intensity
        )
        if push >= 0.95 and overtake >= 0.90 and state.racing_mode == RacingMode.ATTACK:
            return max(0.10, base_headway * 0.48)
        return max(0.16, base_headway)

    def _collision_standstill_gap_multiplier(self, state: DriverState) -> float:
        """Return standstill-gap multiplier; smaller for committed player attacks."""
        if not self._is_player_controlled_driver(state):
            return 1.4
        overtake = float(
            getattr(self, "player_overrides", {}).get("overtake", 0.5) or 0.5
        )
        push = float(
            getattr(self, "player_overrides", {}).get("push", state.push_intensity)
            or state.push_intensity
        )
        if push >= 0.95 and overtake >= 0.90 and state.racing_mode == RacingMode.ATTACK:
            return 1.0
        return 1.3

    def _collision_brake_floor(self, state: DriverState) -> float:
        """Minimum braking multiplier; higher floor keeps overspeed alive when attacking."""
        floor = 0.40
        if state.racing_mode == RacingMode.ATTACK:
            floor = 0.55
        if self._is_player_controlled_driver(state):
            overtake = float(
                getattr(self, "player_overrides", {}).get("overtake", 0.5) or 0.5
            )
            push = float(
                getattr(self, "player_overrides", {}).get("push", state.push_intensity)
                or state.push_intensity
            )
            if (
                push >= 0.95
                and overtake >= 0.90
                and state.racing_mode == RacingMode.ATTACK
            ):
                floor = 0.70
        return floor

    def _collision_critical_gap_penalty(self, state: DriverState) -> float:
        """Secondary penalty in near-contact ranges; softened for committed attacks."""
        penalty = 0.72
        if state.racing_mode == RacingMode.ATTACK:
            penalty = 0.84
        if self._is_player_controlled_driver(state):
            overtake = float(
                getattr(self, "player_overrides", {}).get("overtake", 0.5) or 0.5
            )
            push = float(
                getattr(self, "player_overrides", {}).get("push", state.push_intensity)
                or state.push_intensity
            )
            if (
                push >= 0.95
                and overtake >= 0.90
                and state.racing_mode == RacingMode.ATTACK
            ):
                penalty = 0.90
        return penalty

    def _weibull_incremental_failure_prob(
        self, t_laps: float, delta_laps: float, eta: float, beta: float
    ) -> float:
        """Return failure probability over one lap window using Weibull reliability.

        Weibull CDF is F(t) = 1 - exp(-(t/eta)^beta). We convert that into a
        discrete step probability by computing F(t + delta) - F(t), which is
        the chance a failure occurs during this frame/window.

        Parameters:
        - t_laps: elapsed usage in lap-equivalent units.
        - delta_laps: current step size in lap units.
        - eta: scale (characteristic life); larger => later failures.
        - beta: shape; >1 means wear-out risk grows with usage.
        """
        t0 = max(0.0, float(t_laps))
        dt = max(1e-8, float(delta_laps))
        scale = max(1e-6, float(eta))
        shape = max(0.2, float(beta))

        f_t0 = 1.0 - np.exp(-((t0 / scale) ** shape))
        f_t1 = 1.0 - np.exp(-(((t0 + dt) / scale) ** shape))
        return float(np.clip(f_t1 - f_t0, 0.0, 1.0))

    def _get_team_multiplier(self, team: Team) -> float:
        """Get team performance multiplier"""
        tier_values = {"tier1": 0.95, "tier2": 0.75, "tier3": 0.55}
        base = tier_values.get(team.tier.lower(), 0.75)

        # Budget factor
        budget_factor = min(team.budget / 200.0, 1.0) * 0.2

        # Staff-role effects from HQ roster.
        operations_effect = self._get_team_staff_effect(team, "operations")
        car_perf_effect = self._get_team_staff_effect(team, "car_performance")
        power_effect = self._get_team_staff_effect(team, "power")
        handling_effect = self._get_team_staff_effect(team, "handling")
        aero_effect = self._get_team_staff_effect(team, "aero")
        strategy_effect = self._get_team_staff_effect(team, "strategy")

        staff_bonus_raw = (
            (operations_effect * 0.30)
            + (car_perf_effect * 0.45)
            + (power_effect * 0.18)
            + (handling_effect * 0.16)
            + (aero_effect * 0.16)
            + (strategy_effect * 0.10)
        )
        staff_bonus = min(0.12, max(0.0, staff_bonus_raw))

        return min(base + budget_factor + staff_bonus, 1.05)

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

    def _update_gap_ahead_and_slipstream(
        self, state: DriverState, index: int, active_drivers, race_state: RaceState
    ) -> None:
        """Compute gap ahead and slipstream eligibility."""
        if index == 0:
            state.gap_ahead = 999.0
            state.in_slipstream = False
            return

        ahead_state = active_drivers[index - 1][1]
        distance_gap = self._distance_to_ahead(
            state, ahead_state, race_state.track_length_m
        )
        state.gap_ahead = self._time_gap_to_ahead(state, ahead_state, distance_gap)
        state.in_slipstream = bool(
            ahead_state.lap == state.lap and distance_gap < self.SLIPSTREAM_DISTANCE
        )

    def _distance_to_ahead(
        self, state: DriverState, ahead_state: DriverState, track_length_m: float
    ) -> float:
        """Return physical distance to car ahead."""
        if ahead_state.lap == state.lap:
            return ahead_state.position_m - state.position_m
        if ahead_state.lap > state.lap:
            return (track_length_m - state.position_m) + ahead_state.position_m
        return track_length_m

    def _time_gap_to_ahead(
        self, state: DriverState, ahead_state: DriverState, distance_gap: float
    ) -> float:
        """Convert ahead-distance to UI gap convention (seconds or lap marker)."""
        if ahead_state.lap == state.lap:
            if state.velocity_mps > 0.1:
                return distance_gap / state.velocity_mps
            return distance_gap / self.BASE_SPEED_MPS if distance_gap > 0 else 0.0
        if ahead_state.lap > state.lap:
            lap_diff = ahead_state.lap - state.lap
            return 999.0 + lap_diff
        return 999.0

    def _update_gap_behind(
        self, state: DriverState, index: int, active_drivers
    ) -> None:
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

    def _collect_nearby_cars(
        self, driver_id: int, state: DriverState, race_state: RaceState
    ) -> List[int]:
        """Return nearby running cars on same lap within configured distance."""
        nearby: List[int] = []
        for other_id, other_state in race_state.driver_states.items():
            if (
                other_id == driver_id
                or not other_state.running
                or other_state.lap != state.lap
            ):
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
            lap_start_pos = race_state.lap_start_positions.get(state.driver_id, 0.0)
            lap_distance = state.position_m - lap_start_pos
            lap_time = (
                lap_distance / state.velocity_mps if state.velocity_mps > 0 else 90.0
            )

            state.last_lap_time = lap_time
            if lap_time < state.best_lap_time:
                state.best_lap_time = lap_time

            race_state.lap_times[state.driver_id].append(lap_time)

        self._maybe_apply_rallycross_joker(state, race_state, event_callback)

        race_state.lap_start_positions[state.driver_id] = state.position_m

        # Check if this driver completed all required laps
        if state.lap >= race_state.total_laps:
            state.running = False
            # If this is the first driver to finish, deploy chequered flag
            if not race_state.checkered_flag_deployed:
                race_state.checkered_flag_deployed = True
                race_state.leader_lap_count = state.lap
        # If chequered flag is deployed, finish any driver crossing the line
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
            event_callback(
                {
                    "type": "joker_lap_served",
                    "driver_id": state.driver_id,
                    "driver_name": state.driver_name,
                    "served_lap": state.joker_lap_taken_on,
                    "target_lap": target_lap,
                    "forced": forced,
                    "penalty_s": penalty_s,
                }
            )

    def _refresh_player_joker_target_if_needed(
        self, state: DriverState, race_state: RaceState
    ) -> None:
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
        consistency = self._driver_attr_factor(
            get_safe_attribute(state.driver, "consistency")
        )
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
        - Worn tyres

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
            push_risk = 1.0 + (
                (state.push_intensity - 0.8) * 20.0
            )  # Exponential increase
        else:
            push_risk = state.push_intensity / 0.7  # Linear below aggressive threshold

        # Driver skill reduces mistakes
        consistency = self._driver_attr_factor(
            get_safe_attribute(state.driver, "consistency")
        )
        vehicle_control = self._driver_attr_factor(get_vehicle_control(state.driver))
        # Range: 0.0 to 2.0
        skill_factor = 2.0 - (consistency + vehicle_control)

        # Fatigue increases mistakes
        # Up to 4x when exhausted
        fatigue_multiplier = 1.0 + (state.push_fatigue * 3.0)
        if self._is_player_full_attack(state):
            fatigue_multiplier = 1.0 + (state.push_fatigue * 1.8)

        # Tyre condition affects grip
        # Up to 3x on worn tyres
        tyre_multiplier = 1.0 + ((1.0 - state.tyre_condition) * 2.0)

        # Calculate final probability
        mistake_prob = (
            base_probability
            * push_risk
            * skill_factor
            * fatigue_multiplier
            * tyre_multiplier
        )
        if self._is_player_full_attack(state):
            mistake_prob *= 0.72

        # Roll the dice
        if self.rng.random() < mistake_prob:
            state.frames_since_mistake = 0
            # Determine severity
            severity = "minor" if self.rng.random() > 0.3 else "major"
            if severity == "major":
                print(
                    f"  WARNING: {state.driver_name} runs wide! (push={state.push_intensity:.2f}, fatigue={state.push_fatigue:.2f})"
                )
            return True

        return False

    def _check_incident(self, state: DriverState, race_state: RaceState) -> bool:
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
            longitudinal_gap = self._longitudinal_gap(
                state, other_state, race_state.track_length_m
            )
            if longitudinal_gap >= safe_following_distance:
                continue
            if self._handle_pair_incident(
                state, other_state, race_state, longitudinal_gap, car_length
            ):
                return True

        return self._check_solo_incident(state, race_state)

    def _is_collision_candidate(
        self, state: DriverState, other_id: int, other_state: DriverState
    ) -> bool:
        """Return whether another state can collide with the current state this frame."""
        if other_id == state.driver_id or not other_state.running:
            return False
        if other_state.lap != state.lap:
            return False
        return True

    def _longitudinal_gap(
        self, state: DriverState, other_state: DriverState, track_length_m: float
    ) -> float:
        """Compute shortest longitudinal distance between two cars on looped track."""
        longitudinal_gap = (
            abs(state.position_m - other_state.position_m) % track_length_m
        )
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
        """Return normalised racecraft/control/reaction composite in [0,1]."""
        vehicle_control = self._driver_attr_factor(get_vehicle_control(state.driver))
        reactions = self._driver_attr_factor(
            get_safe_attribute(state.driver, "reactions")
        )
        racecraft = self._driver_attr_factor(
            get_safe_attribute(state.driver, "racecraft")
        )
        return (vehicle_control + reactions + racecraft) / 3.0

    def _maybe_trigger_overtake_contact(
        self, state: DriverState, other_state: DriverState, race_state: RaceState
    ) -> bool:
        my_racecraft = self._racecraft_score(state)
        other_racecraft = self._racecraft_score(other_state)
        combined_skill = (my_racecraft + other_racecraft) / 2.0
        control_factor = min(state.tyre_condition, other_state.tyre_condition)
        safety_bonus = (
            self._get_team_staff_effect(state.team, "reliability")
            + self._get_team_staff_effect(state.team, "consistency")
            + self._get_team_staff_effect(state.team, "racecraft")
            + self._get_team_staff_effect(other_state.team, "reliability")
            + self._get_team_staff_effect(other_state.team, "consistency")
            + self._get_team_staff_effect(other_state.team, "racecraft")
        ) / 6.0
        safety_multiplier = max(0.72, 1.0 - (safety_bonus * 0.45))
        contact_probability = (
            0.0000002 * (1.0 - combined_skill * control_factor) * safety_multiplier
        )
        if self.rng.random() >= contact_probability:
            return False

        state.dnf_reason = "contact_during_overtake"
        other_state.running = False
        other_state.dnf_reason = "contact_during_overtake"
        print(
            f"  *** RACING INCIDENT! {state.driver_name} and {other_state.driver_name} "
            f"made contact at position {state.position_m:.0f}m"
        )
        race_state.collision_log.append(
            {
                "lap": state.lap,
                "time": race_state.current_time,
                "position_m": state.position_m,
                "type": "contact_during_overtake",
                "driver1_id": state.driver_id,
                "driver1_name": state.driver_name,
                "driver2_id": other_state.driver_id,
                "driver2_name": other_state.driver_name,
                "description": f"{state.driver_name} and {other_state.driver_name} collided during overtake",
            }
        )
        self._emit_other_driver_dnf_event(other_state)
        return True

    def _emit_other_driver_dnf_event(self, other_state: DriverState) -> None:
        """Emit DNF event for secondary collision party when needed."""
        try:
            if not (
                hasattr(self, "_event_callback") and callable(self._event_callback)
            ):
                return
            if getattr(other_state, "dnf_event_emitted", False):
                return
            self._event_callback(
                {
                    "type": "dnf",
                    "driver_id": other_state.driver_id,
                    "driver_name": other_state.driver_name,
                    "lap": other_state.lap,
                    "reason": other_state.dnf_reason,
                }
            )
            other_state.dnf_event_emitted = True
        except Exception:
            pass

    def _maybe_trigger_rear_end_incident(
        self, state: DriverState, other_state: DriverState, race_state: RaceState
    ) -> bool:
        relative_velocity = state.velocity_mps - other_state.velocity_mps
        if state.position_m >= other_state.position_m:
            if relative_velocity < -5.0:
                return False
            return False
        if relative_velocity <= 15.0:
            return False

        combined_control = (
            get_vehicle_control(state.driver) + get_vehicle_control(other_state.driver)
        ) / 200.0
        severity = min(1.0, (relative_velocity - 15.0) / 15.0)
        safety_bonus = (
            self._get_team_staff_effect(state.team, "reliability")
            + self._get_team_staff_effect(state.team, "consistency")
            + self._get_team_staff_effect(other_state.team, "reliability")
            + self._get_team_staff_effect(other_state.team, "consistency")
        ) / 4.0
        safety_multiplier = max(0.70, 1.0 - (safety_bonus * 0.50))
        dnf_probability = 0.12 * severity * (1.0 - combined_control) * safety_multiplier
        if self.rng.random() < dnf_probability:
            print(f"  *** REAR-END! {state.driver_name} hit {other_state.driver_name}")
            state.dnf_reason = "rear_end_collision"
            race_state.collision_log.append(
                {
                    "lap": state.lap,
                    "time": race_state.current_time,
                    "position_m": state.position_m,
                    "type": "rear_end_collision",
                    "driver1_id": state.driver_id,
                    "driver1_name": state.driver_name,
                    "driver2_id": other_state.driver_id,
                    "driver2_name": other_state.driver_name,
                    "description": f"{state.driver_name} rear-ended {other_state.driver_name}",
                }
            )
            return True

        print(
            f"  !!! NEAR MISS/CONTACT (no DNF): {state.driver_name} & {other_state.driver_name} "
            f"- closing {relative_velocity:.1f}m/s"
        )
        state.tyre_condition = max(0.2, state.tyre_condition - 0.12)
        other_state.tyre_condition = max(0.2, other_state.tyre_condition - 0.08)
        race_state.collision_log.append(
            {
                "lap": state.lap,
                "time": race_state.current_time,
                "position_m": state.position_m,
                "type": "rear_end_contact_minor",
                "driver1_id": state.driver_id,
                "driver1_name": state.driver_name,
                "driver2_id": other_state.driver_id,
                "driver2_name": other_state.driver_name,
                "description": f"Minor rear contact between {state.driver_name} and {other_state.driver_name} (no DNF)",
            }
        )
        return False

    def _check_solo_incident(self, state: DriverState, race_state: RaceState) -> bool:
        """Handle non-contact DNFs (tyre failure spin and mechanical failure)."""
        tyre_management_effect = self._get_team_staff_effect(
            state.team, "tyre_management"
        )
        setup_effect = self._get_team_staff_effect(state.team, "setup")
        reliability_effect = self._get_team_staff_effect(state.team, "reliability")

        track_length = max(
            1.0, float(getattr(race_state, "track_length_m", 1.0) or 1.0)
        )
        lap_fraction = (float(state.position_m) % track_length) / track_length
        race_progress_laps = max(0.0, float(state.lap) + lap_fraction)
        delta_laps = max(1e-6, float(state.velocity_mps) / track_length / 30.0)

        tyre_eta = float(self._active_discipline_calibration.get("tyre_eta", 28.0))
        tyre_beta = float(self._active_discipline_calibration.get("tyre_beta", 2.6))
        mech_eta = float(self._active_discipline_calibration.get("mech_eta", 95.0))
        mech_beta = float(self._active_discipline_calibration.get("mech_beta", 2.1))

        if state.tyre_condition < 0.1:
            consistency = self._driver_attr_factor(state.driver.consistency)
            tyre_spin_risk_reduction = min(
                0.45, (tyre_management_effect * 0.6) + (setup_effect * 0.4)
            )
            spin_threshold = consistency + tyre_spin_risk_reduction
            tyre_hazard = self._weibull_incremental_failure_prob(
                t_laps=race_progress_laps,
                delta_laps=delta_laps,
                eta=tyre_eta,
                beta=tyre_beta,
            )
            tyre_hazard *= 1.0 + ((1.0 - state.tyre_condition) * 2.8)
            tyre_hazard *= max(0.35, 1.0 - tyre_spin_risk_reduction)
            tyre_hazard *= max(0.40, 1.0 - (consistency * 0.55))
            if self.rng.random() < np.clip(
                tyre_hazard, 0.0, 0.95
            ) and self.rng.random() > min(0.98, spin_threshold):
                state.dnf_reason = "tyre_failure_spin"
                print(f"  X {state.driver_name} spins off - tyre condition critical!")
                return True

        push_stress = (
            0.85
            + (float(state.push_intensity) * 0.35)
            + (float(state.push_fatigue) * 0.25)
        )
        reliability_guard = max(0.40, 1.0 - (reliability_effect * 0.9))
        mech_failure_prob = self._weibull_incremental_failure_prob(
            t_laps=race_progress_laps,
            delta_laps=delta_laps,
            eta=mech_eta,
            beta=mech_beta,
        )
        mech_failure_prob *= push_stress * reliability_guard
        mech_failure_prob = float(np.clip(mech_failure_prob, 0.0, 0.03))
        if self.rng.random() < mech_failure_prob:
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

    def _resolve_single_overtake_attempt(
        self, key, attempt: OvertakeAttempt, race_state: RaceState
    ) -> bool:
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
        attempt.speed_advantage_kmh = speed_diff * 3.6 + self._line_battle_delta(attempt)
        attempt.lateral_overlap = lateral_overlap

        if self._should_force_player_close_gap_pass(attacker_state, attempt):
            self._apply_overtake_result(
                "success", key, attempt, race_state, attacker_state, defender_state
            )
            return True

        # Massive closing speed on a straight should convert into a near-immediate
        # run-by rather than getting trapped in prolonged side-by-side resolution.
        if (
            attempt.attempt_type == OvertakeAttemptType.SLIPSTREAM_STRAIGHT
            and attempt.speed_advantage_kmh >= self.OVERSPEED_AUTO_PASS_KMH
            and gap_meters <= self.OVERSPEED_AUTO_PASS_MAX_GAP_M
        ):
            self._apply_overtake_result(
                "success", key, attempt, race_state, attacker_state, defender_state
            )
            return True

        outcome = attempt.update(1.0 / 30.0)
        if not self._should_resolve_overtake_attempt(
            outcome, attempt, lateral_overlap, attacker_state
        ):
            return False

        result = self._resolve_overtake_result(
            outcome, attempt, attacker_state, defender_state
        )
        self._apply_overtake_result(
            result, key, attempt, race_state, attacker_state, defender_state
        )
        return True

    def _line_battle_delta(self, attempt: OvertakeAttempt) -> float:
        """Translate line choice into a small, readable battle advantage."""
        attacker_bonus = {
            RacingLine.IDEAL: 0.0,
            RacingLine.ATTACKING: 1.8,
            RacingLine.DEFENSIVE: -0.8,
            RacingLine.OFF_LINE: -2.4,
        }.get(attempt.attacker_line, 0.0)
        defender_bonus = {
            RacingLine.IDEAL: 0.0,
            RacingLine.DEFENSIVE: -2.2,
            RacingLine.ATTACKING: 0.6,
            RacingLine.OFF_LINE: 1.0,
        }.get(attempt.defender_line, 0.0)
        return attacker_bonus + defender_bonus

    def _compute_overtake_lateral_overlap(
        self, attempt: OvertakeAttempt, gap_meters: float
    ) -> float:
        if gap_meters < 5.0:
            # Keep overlap growth progressive at close range instead of clamping too
            # early, which can force unresolved battles to terminate as failures.
            return min(
                1.1, max(attempt.lateral_overlap, 0.2 + (5.0 - gap_meters) * 0.12)
            )
        retreat = 0.01
        if attempt.speed_advantage_kmh > 12.0:
            retreat = 0.0
        return max(0.0, attempt.lateral_overlap - retreat)

    def _should_force_player_close_gap_pass(
        self, attacker_state: DriverState, attempt: OvertakeAttempt
    ) -> bool:
        """Return True when a player max-attack run should instantly convert to a pass."""
        if not self._is_player_controlled_driver(attacker_state):
            return False
        overrides = (
            getattr(self, "player_overrides", {})
            if isinstance(getattr(self, "player_overrides", None), dict)
            else {}
        )
        push = float(
            overrides.get("push", attacker_state.push_intensity)
            or attacker_state.push_intensity
        )
        overtake = float(overrides.get("overtake", 0.5) or 0.5)
        if push < 0.95 or overtake < 0.90:
            return False
        if attacker_state.racing_mode != RacingMode.ATTACK:
            return False
        if attempt.gap_m > 3.5:
            return False
        return attempt.speed_advantage_kmh >= 2.0

    def _should_resolve_overtake_attempt(
        self,
        outcome: Optional[str],
        attempt: OvertakeAttempt,
        lateral_overlap: float,
        attacker_state: DriverState,
    ) -> bool:
        if outcome:
            return True
        if attempt.frames_active > 45:
            return True
        if lateral_overlap > 0.95:
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
            logistic_slopes=self._active_logistic_slopes,
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
            self._handle_overtake_success(
                key, attempt, race_state, attacker_state, defender_state
            )
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
            print(
                f"  OK {attacker_state.driver_name} overtakes {defender_state.driver_name}! ({attempt.attempt_type.value})"
            )
            self._recent_overtakes[key] = race_state.current_time
        try:
            safe_nudge = 5.0
            attacker_state.position_m = defender_state.position_m + safe_nudge
            attacker_state.velocity_mps = max(
                attacker_state.velocity_mps, defender_state.velocity_mps + 0.5
            )
            pair_key_done = frozenset(
                (attacker_state.driver_id, defender_state.driver_id)
            )
            self._overtake_pair_cooldown[pair_key_done] = race_state.current_time + 1.0
            race_state.collision_log.append(
                {
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
                }
            )

            # Mirror overtake into callback stream so calibration/UI consumers
            # do not need to parse collision logs to observe overtakes.
            if hasattr(self, "_event_callback") and callable(self._event_callback):
                self._event_callback(
                    {
                        "type": "overtake",
                        "attacker_id": attacker_state.driver_id,
                        "attacker_name": attacker_state.driver_name,
                        "defender_id": defender_state.driver_id,
                        "defender_name": defender_state.driver_name,
                        "lap": attacker_state.lap,
                        "time": race_state.current_time,
                        "attempt_type": attempt.attempt_type.value,
                    }
                )
        except Exception:
            pass

    def _handle_overtake_incident(
        self, attacker_state: DriverState, defender_state: DriverState
    ) -> None:
        attacker_state.running = False
        attacker_state.dnf_reason = "collision"
        defender_state.running = False
        defender_state.dnf_reason = "collision"
        print(
            f"  COLLISION! {attacker_state.driver_name} and {defender_state.driver_name} crash!"
        )
        self._emit_dnf_event_if_needed(attacker_state)
        self._emit_dnf_event_if_needed(defender_state)

    def _emit_dnf_event_if_needed(self, state: DriverState) -> None:
        try:
            if not (
                hasattr(self, "_event_callback") and callable(self._event_callback)
            ):
                return
            if getattr(state, "dnf_event_emitted", False):
                return
            self._event_callback(
                {
                    "type": "dnf",
                    "driver_id": state.driver_id,
                    "driver_name": state.driver_name,
                    "lap": state.lap,
                    "reason": state.dnf_reason,
                }
            )
            state.dnf_event_emitted = True
        except Exception:
            pass

    def _get_car_ahead(
        self, state: DriverState, race_state: RaceState
    ) -> Optional[DriverState]:
        """Find the car directly ahead"""
        ahead_car = None
        min_gap = float("inf")

        for other_state in race_state.driver_states.values():
            if other_state.driver_id == state.driver_id or not other_state.running:
                continue
            if other_state.position == state.position - 1:
                gap = (
                    state.position_m - other_state.position_m
                    if state.lap == other_state.lap
                    else 999
                )
                if gap < min_gap:
                    min_gap = gap
                    ahead_car = other_state

        return ahead_car

    def _get_car_behind(
        self, state: DriverState, race_state: RaceState
    ) -> Optional[DriverState]:
        """Find the car directly behind"""
        behind_car = None
        min_gap = float("inf")

        for other_state in race_state.driver_states.values():
            if other_state.driver_id == state.driver_id or not other_state.running:
                continue
            if other_state.position == state.position + 1:
                gap = (
                    other_state.position_m - state.position_m
                    if state.lap == other_state.lap
                    else 999
                )
                if gap < min_gap:
                    min_gap = gap
                    behind_car = other_state

        return behind_car

    def _race_finished(self, race_state: RaceState) -> bool:
        """Check if race is complete with chequered flag logic

        Two-phase finishing:
        1. When leader completes all laps, deploy chequered flag
        2. Other drivers finish when they cross the line (don't need full laps)
        3. Race ends when all drivers have finished or DNF'd
        """
        # Get all drivers who are still running (not DNF)
        active_drivers = [s for s in race_state.driver_states.values() if s.running]

        # If no one is running, race is over
        if not active_drivers:
            return True

        # If chequered flag not yet deployed, check if leader finished
        if not race_state.checkered_flag_deployed:
            leader_laps = max(driver.lap for driver in active_drivers)
            if leader_laps >= race_state.total_laps:
                # Leader finished - deploy chequered flag but don't end race yet
                # Let other drivers finish when they cross the line
                return False

        # If chequered flag deployed, race continues until all drivers finish
        return False

    def _create_position_event(
        self, race_state: RaceState, frame: int
    ) -> Dict[str, Any]:
        """Create position update event for GUI"""
        positions = []

        for driver_id, state in race_state.driver_states.items():
            # Wrap position to track length for GUI rendering
            display_position = state.position_m % race_state.track_length_m

            positions.append(
                {
                    "driver_id": driver_id,
                    "driver_name": state.driver_name,
                    "position": state.position,
                    "lap": state.lap,
                    "position_m": display_position,
                    "total_time": state.total_time,
                    "velocity_mps": state.velocity_mps,
                    "racing_mode": state.racing_mode.value,
                    "push_intensity": state.push_intensity,
                    "push_fatigue": state.push_fatigue,
                    "tyre_condition": state.tyre_condition,
                    "tyre_compound": state.tyre_compound,
                    "fuel_load": state.fuel_load,
                    "in_pit_lane": state.in_pit_lane,
                    "pit_time_remaining_s": state.pit_time_remaining_s,
                    "pit_total_time_s": state.pit_total_time_s,
                    "pit_stops_completed": state.pit_stops_completed,
                    "gap_ahead": state.gap_ahead,
                    "gap_behind": state.gap_behind,
                    "running": state.running,
                }
            )

        return {
            "type": "position_update",
            "frame": frame,
            "time": race_state.current_time,
            "positions": positions,
        }

    def _compile_results(self, race_state: RaceState) -> List[Dict[str, Any]]:
        """Compile final race results with accurate timing and proper lapped classification"""
        results = []

        finished_drivers, lapped_drivers, dnf_drivers = self._classify_result_states(
            race_state
        )

        # Sort finishers by actual elapsed race time (lowest wins).
        finished_drivers.sort(key=lambda s: float(s.total_time))

        # Sort lapped drivers by laps completed (descending), then elapsed time.
        lapped_drivers.sort(key=lambda s: (-s.lap, float(s.total_time)))
        # Keep DNF ordering deterministic for UI and persistence.
        dnf_drivers.sort(key=lambda s: (-s.lap, float(s.total_time)))

        # Add finished drivers first (positions 1, 2, 3...)
        for position, state in enumerate(finished_drivers, 1):
            results.append(
                self._build_result_entry(race_state, state, position, "FINISHED", False)
            )

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
            results.append(
                self._build_result_entry(
                    race_state, state, len(results) + 1, "DNF", False
                )
            )

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


__all__ = ["RealtimeRaceEngine", "DriverState", "RaceState", "RacingMode"]
