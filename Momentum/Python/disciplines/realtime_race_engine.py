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
- Live position updates for GUI visualization

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
from disciplines.track_physics import TrackMap, TrackSection, RacingLine
from disciplines.overtaking_system import (
    OvertakeAttempt, OvertakeAttemptType, DefensiveAction,
    evaluate_overtaking_opportunity, calculate_defensive_action,
    resolve_overtake_outcome
)
from services.driver_attributes import get_safe_attribute


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
    position_m: float = 0.0         # Absolute position from start line (meters)
    prev_position_m: float = 0.0    # Previous position (for lap detection)
    velocity_mps: float = 0.0       # Current velocity (meters per second)
    lap: int = 0                    # Current lap number
    
    # Race situation awareness
    gap_ahead: float = 999.0        # Gap to car ahead (seconds)
    gap_behind: float = 999.0       # Gap to car behind (seconds)
    position: int = 1               # Current race position
    cars_nearby: List[int] = field(default_factory=list)  # Driver IDs of nearby cars
    
    # Strategic state
    racing_mode: RacingMode = RacingMode.MANAGE
    push_intensity: float = 0.7     # How hard pushing (0.5=conserve, 1.0=maximum attack)
    racing_line: RacingLine = RacingLine.IDEAL  # Current racing line choice
    
    # Component degradation
    tire_condition: float = 1.0     # 1.0=new tires, 0.0=completely worn
    fuel_load: float = 1.0          # 1.0=full tank, 0.0=empty
    
    # Performance modifiers
    in_slipstream: bool = False     # Currently benefiting from draft
    making_overtake: bool = False   # Currently attempting overtake
    
    # Incident tracking
    running: bool = True
    dnf_reason: Optional[str] = None
    
    # Timing
    total_time: float = 0.0         # Total race time elapsed
    last_lap_time: float = 0.0      # Previous lap time
    best_lap_time: float = 999.0    # Personal best lap


@dataclass
class RaceState:
    """Overall race state tracking"""
    current_time: float = 0.0       # Race elapsed time (seconds)
    timestep: float = 1.0/30.0      # Simulation timestep (0.033s for 30 FPS)
    
    driver_states: Dict[int, DriverState] = field(default_factory=dict)
    lap_start_positions: Dict[int, float] = field(default_factory=dict)
    
    total_laps: int = 50
    track_length_m: float = 6000.0
    
    # For lap detection
    lap_times: Dict[int, List[float]] = field(default_factory=dict)


class RealtimeRaceEngine:
    """
    Real-time agent-based racing simulation engine
    
    Simulates racing at 30 FPS with drivers making active decisions based on
    their surroundings, attributes, and race situation.
    """
    
    def __init__(self, seed: int = None):
        """Initialize engine with random generator"""
        self.rng = np.random.default_rng(seed)
        
        # Track-aware racing physics
        self.track_map: Optional[TrackMap] = None
        self.active_overtakes: Dict[Tuple[int, int], OvertakeAttempt] = {}  # (attacker_id, defender_id) -> attempt
        
        # Physics constants
        self.BASE_SPEED_MPS = 70.0  # ~250 km/h base racing speed
        self.MAX_SPEED_MPS = 90.0   # ~324 km/h maximum speed
        self.MIN_SPEED_MPS = 30.0   # ~108 km/h minimum speed in corners
        
        # Performance factors
        self.SLIPSTREAM_BONUS = 0.05     # 5% speed boost in draft
        self.TIRE_DEGRADATION_RATE = 0.00001  # Per timestep degradation
        self.FUEL_BURN_RATE = 0.00002    # Per timestep fuel consumption
        
        # AI decision parameters
        self.ATTACK_THRESHOLD_GAP = 1.0  # Attack if within 1 second
        self.DEFEND_THRESHOLD_GAP = 0.5  # Defend if car within 0.5s behind
        self.NEARBY_DISTANCE_M = 100.0   # Consider cars within 100m as "nearby"
        
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
        realtime_speed: float = 1.0,  # 1.0=real-time, 2.0=2x speed, 0.5=half speed
        track_points: Optional[List[Any]] = None  # Visual track points for unified position mapping
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
        # Initialize track map for racing physics
        print(f"→ Generating track map for {track.name}...")
        self.track_map = TrackMap(track=track)
        print(f"  ✓ Track map ready: {len(self.track_map.corners)} corners, {len(self.track_map.drs_zones)} DRS zones")
        
        # Store visual track points for unified position mapping
        self.track_points = track_points
        if track_points:
            print(f"  ✓ Using visual track with {len(track_points)} points for position mapping")
        
        # Initialize race state
        track_length_m = track.length_km * 1000.0
        race_state = self._initialize_race(drivers, teams, track_length_m, total_laps)
        
        # Calculate target lap time (used for pacing)
        target_lap_time = track_length_m / self.BASE_SPEED_MPS
        
        # Simulation loop at 30 FPS
        timestep = 1.0 / 30.0
        frame = 0
        
        # Emit initial positions
        if event_callback:
            event_callback(self._create_position_event(race_state, frame))
        
        while not self._race_finished(race_state):
            frame_start = time.time()
            
            # Update each driver
            for driver_id, state in race_state.driver_states.items():
                if not state.running:
                    continue
                
                # AI Decision Making: determine racing mode and push intensity
                self._update_racing_mode(state, race_state)
                
                # Calculate performance for this timestep
                speed_mps = self._calculate_speed(state, race_state, track_length_m)
                
                # Update position
                distance_this_step = speed_mps * timestep
                state.prev_position_m = state.position_m
                state.position_m += distance_this_step
                state.velocity_mps = speed_mps
                # Lap completion: detect crossing start/finish line
                prev_lap = int(state.prev_position_m // track_length_m)
                curr_lap = int(state.position_m // track_length_m)
                if curr_lap > prev_lap:
                    self._complete_lap(state, race_state, track_length_m)
                
                # Update degradation
                state.tire_condition -= self.TIRE_DEGRADATION_RATE * state.push_intensity
                state.fuel_load -= self.FUEL_BURN_RATE
                
                # Check for incidents
                if self._check_incident(state, race_state):
                    state.running = False
                    if event_callback:
                        event_callback({
                            "type": "dnf",
                            "driver_id": driver_id,
                            "driver_name": state.driver_name,
                            "lap": state.lap,
                            "reason": state.dnf_reason
                        })
            
            # Update race situation (gaps, positions, nearby cars)
            self._update_race_situation(race_state)
            
            # Emit position update every frame (30 FPS)
            frame += 1
            race_state.current_time += timestep
            
            if event_callback:
                event_callback(self._create_position_event(race_state, frame))
            
            # Throttle to realtime_speed if needed
            if realtime_speed < 100:  # Don't throttle if running very fast
                frame_duration = time.time() - frame_start
                target_duration = timestep / realtime_speed
                sleep_time = target_duration - frame_duration
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        # Emit race finished
        if event_callback:
            event_callback({
                "type": "race_finished",
                "total_laps": total_laps,
                "race_time": race_state.current_time
            })
        
        return self._compile_results(race_state)
    
    def _initialize_race(
        self,
        drivers: List[Driver],
        teams: Dict[int, Team],
        track_length_m: float,
        total_laps: int
    ) -> RaceState:
        """Initialize race with starting grid"""
        race_state = RaceState(
            total_laps=total_laps,
            track_length_m=track_length_m
        )
        
        # Create driver states in grid order
        for i, driver in enumerate(drivers):
            team = teams.get(driver.current_team_id)
            if not team:
                continue
            
            # Stagger starting positions (2m between cars)
            starting_position = -i * 2.0
            
            state = DriverState(
                driver_id=driver.id,
                driver_name=driver.name,
                driver=driver,
                team=team,
                position_m=starting_position,
                position=i + 1,
                lap=0
            )
            
            race_state.driver_states[driver.id] = state
            race_state.lap_times[driver.id] = []
        
        return race_state
    
    def _update_racing_mode(self, state: DriverState, race_state: RaceState):
        """
        AI Decision Making: Update driver's racing mode and push intensity
        
        Uses advanced track-aware overtaking evaluation.
        """
        driver = state.driver
        
        # Base push intensity from driver attributes
        overtaking_tendency = driver.overtaking / 100.0
        consistency = driver.consistency / 100.0
        risk_tolerance = (100.0 - driver.professionalism) / 100.0
        adrenaline_control = driver.adrenaline_management / 100.0
        
        # Track-aware overtaking evaluation
        if state.gap_ahead < self.ATTACK_THRESHOLD_GAP and state.position > 1:
            # Find car ahead
            car_ahead = self._get_car_ahead(state, race_state)
            if car_ahead and self.track_map:
                # Get track section and corner data
                section_type, corner = self.track_map.get_section_at_position(
                    state.position_m % race_state.track_length_m
                )
                is_overtaking_zone = self.track_map.is_overtaking_zone(
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
                    # Start overtaking attempt
                    state.racing_mode = RacingMode.ATTACK
                    state.push_intensity = 0.9 + risk_tolerance * 0.1
                    
                    # Create or update active overtake
                    key = (state.driver_id, car_ahead.driver_id)
                    if key not in self.active_overtakes:
                        self.active_overtakes[key] = OvertakeAttempt(
                            attacker_id=state.driver_id,
                            defender_id=car_ahead.driver_id,
                            attempt_type=attempt_type,
                            position_m=state.position_m,
                            gap_m=gap_m,
                            speed_advantage_kmh=(state.velocity_mps - car_ahead.velocity_mps) * 3.6,
                            corner=corner
                        )
                else:
                    state.racing_mode = RacingMode.MANAGE
                    state.push_intensity = 0.7 + overtaking_tendency * 0.2
            else:
                # Fallback to simple logic
                state.racing_mode = RacingMode.ATTACK
                state.push_intensity = 0.85
        
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
                defensive_action, racing_line = calculate_defensive_action(
                    defender=driver,
                    attacker=car_behind.driver,
                    gap_m=gap_m,
                    section=section_type,
                    corner=corner
                )
                
                state.racing_mode = RacingMode.DEFEND
                state.push_intensity = 0.8 + (driver.defensive_driving / 100.0) * 0.15
                # Store racing line for speed calculation
                state.racing_line = racing_line
            else:
                state.racing_mode = RacingMode.DEFEND
                state.push_intensity = 0.8
        
        elif state.gap_ahead > 3.0 and state.gap_behind > 3.0:
            # Comfortable gap - manage
            state.racing_mode = RacingMode.MANAGE
            state.push_intensity = 0.6 + (driver.tire_management / 100.0) * 0.2
            state.racing_line = RacingLine.IDEAL
        
        else:
            state.racing_mode = RacingMode.CRUISE
            state.push_intensity = 0.65 + overtaking_tendency * 0.1
            state.racing_line = RacingLine.IDEAL
        
        # Tire condition affects push
        if state.tire_condition < 0.5:
            state.push_intensity *= (0.7 + state.tire_condition * 0.6)
        
        # Consistency variance
        variance = (1.0 - consistency) * 0.1
        state.push_intensity += self.rng.normal(0, variance)
        state.push_intensity = np.clip(state.push_intensity, 0.4, 1.0)
    
    def _calculate_speed(
        self,
        state: DriverState,
        race_state: RaceState,
        track_length_m: float
    ) -> float:
        """
        Calculate current speed using track-aware physics
        
        Returns speed in meters per second.
        """
        driver = state.driver
        team = state.team
        
        # Base speed from driver and team
        raw_speed = driver.raw_speed / 100.0
        team_performance = self._get_team_multiplier(team)
        base_speed = self.BASE_SPEED_MPS * (0.7 + raw_speed * 0.3) * (0.85 + team_performance * 0.15)
        
        # Track-aware corner physics
        if self.track_map:
            position_on_track = state.position_m % track_length_m
            section_type, corner = self.track_map.get_section_at_position(position_on_track)
            
            if corner:
                # Use advanced corner performance calculation
                from disciplines.track_physics import calculate_corner_performance
                
                perf = calculate_corner_performance(
                    driver=driver,
                    corner=corner,
                    racing_line=state.racing_line,
                    tire_condition=state.tire_condition,
                    cars_nearby=len(state.cars_nearby)
                )
                
                # Use calculated exit speed (convert km/h to m/s)
                corner_speed_mps = perf["exit_speed_kmh"] / 3.6
                
                # Apply push intensity to corner exit
                corner_speed_mps *= (0.85 + state.push_intensity * 0.15)
                
                # Blend corner speed with base speed based on section type
                if section_type == TrackSection.BRAKING_ZONE:
                    speed = corner_speed_mps * 0.6 + base_speed * 0.4
                elif section_type in [TrackSection.SLOW_CORNER, TrackSection.MEDIUM_CORNER]:
                    speed = corner_speed_mps * 0.8 + base_speed * 0.2
                elif section_type == TrackSection.FAST_CORNER:
                    speed = corner_speed_mps * 0.5 + base_speed * 0.5
                else:
                    speed = base_speed
            else:
                # Straight section - use base speed
                speed = base_speed
        else:
            # Fallback to simple calculation
            speed = base_speed
            position_in_lap = (state.position_m % track_length_m) / track_length_m
            corner_factor = 0.85 + 0.15 * np.sin(position_in_lap * 2 * np.pi * 8)
            cornering_skill = driver.cornering_skill / 100.0
            corner_speed_retention = 0.7 + cornering_skill * 0.3
            speed *= (corner_factor * corner_speed_retention + (1.0 - corner_factor))
        
        # Modify by push intensity
        speed *= (0.8 + state.push_intensity * 0.2)
        
        # Tire degradation
        tire_penalty = 1.0 - (1.0 - state.tire_condition) * 0.3
        speed *= tire_penalty
        
        # Fuel weight
        fuel_bonus = 1.0 + (1.0 - state.fuel_load) * 0.02
        speed *= fuel_bonus
        
        # Slipstream
        if state.in_slipstream:
            speed *= (1.0 + self.SLIPSTREAM_BONUS)
        
        # Consistency variance
        consistency = driver.consistency / 100.0
        speed_variance = (1.0 - consistency) * 0.05
        speed *= (1.0 + self.rng.normal(0, speed_variance))
        
        # Clamp to realistic bounds
        return np.clip(speed, self.MIN_SPEED_MPS, self.MAX_SPEED_MPS)
    
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
        active_drivers = [(did, state) for did, state in race_state.driver_states.items() if state.running]
        active_drivers.sort(key=lambda x: (-x[1].lap, -x[1].position_m))
        
        # Update positions and gaps
        for i, (driver_id, state) in enumerate(active_drivers):
            state.position = i + 1
            
            # Gap ahead
            if i > 0:
                ahead_state = active_drivers[i - 1][1]
                if ahead_state.lap == state.lap:
                    distance_gap = ahead_state.position_m - state.position_m
                    # Convert to time gap (approximate)
                    state.gap_ahead = distance_gap / self.BASE_SPEED_MPS
                    
                    # Check slipstream (within 50m and similar lap)
                    if distance_gap < 50.0:
                        state.in_slipstream = True
                    else:
                        state.in_slipstream = False
                else:
                    state.gap_ahead = 999.0
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
    
    def _complete_lap(self, state: DriverState, race_state: RaceState, track_length_m: float):
        """Handle lap completion"""
        state.lap += 1
        
        # Calculate lap time
        if state.lap > 0:
            lap_start_pos = race_state.lap_start_positions.get(state.driver_id, 0.0)
            lap_distance = state.position_m - lap_start_pos
            lap_time = lap_distance / state.velocity_mps if state.velocity_mps > 0 else 90.0
            
            state.last_lap_time = lap_time
            if lap_time < state.best_lap_time:
                state.best_lap_time = lap_time
            
            race_state.lap_times[state.driver_id].append(lap_time)
        
        race_state.lap_start_positions[state.driver_id] = state.position_m
    
    def _check_incident(self, state: DriverState, race_state: RaceState) -> bool:
        """
        Advanced incident checking with overtaking combat resolution
        
        Returns True if driver suffers incident (DNF).
        """
        # Update active overtakes
        self._resolve_active_overtakes(race_state)
        
        # Base incident rate for normal driving
        consistency = state.driver.consistency / 100.0
        incident_rate = self.BASE_INCIDENT_RATE * (1.5 - consistency * 0.5)
        
        # Tire condition dramatically increases risk
        if state.tire_condition < 0.3:
            incident_rate *= 2.0
        
        # Check for solo incident (spin, off-track, mechanical)
        if self.rng.random() < incident_rate:
            incident_types = ["spin", "mechanical", "off_track"]
            state.dnf_reason = self.rng.choice(incident_types)
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
            section_type, corner = self.track_map.get_section_at_position(position_on_track)
            
            # Calculate lateral overlap (simulated from speed difference)
            speed_diff = attacker_state.velocity_mps - defender_state.velocity_mps
            gap_meters = attacker_state.gap_ahead * attacker_state.velocity_mps
            
            # Estimate lateral overlap based on gap closing rate
            if gap_meters < 5.0:  # Very close - side by side
                lateral_overlap = min(0.8, 0.2 + (5.0 - gap_meters) * 0.12)
            else:
                lateral_overlap = max(0.0, attempt.lateral_overlap - 0.05)  # Decay if not close
            
            # Update attempt state
            attempt.gap_m = gap_meters
            attempt.speed_advantage_kmh = speed_diff * 3.6
            attempt.lateral_overlap = lateral_overlap
            
            # Update frames
            timestep = 1.0 / 30.0  # 30 FPS
            outcome = attempt.update(timestep)
            
            # Check if attempt should be resolved (use outcome from update or resolve manually)
            if outcome or attempt.frames_active > 30 or lateral_overlap > 0.7 or attacker_state.gap_ahead > 2.0:
                # Use outcome from update() or resolve manually
                if not outcome:
                    result, incident_type = resolve_overtake_outcome(
                        attacker=attacker_state.driver,
                        defender=defender_state.driver,
                        overtake_attempt=attempt,
                        rng=self.rng
                    )
                else:
                    result = outcome
                    incident_type = None
                
                if result == "success":
                    print(f"  \u2713 {attacker_state.driver_name} overtakes {defender_state.driver_name}! ({attempt.attempt_type.value})")
                    # Swap positions will happen naturally in next update
                elif result == "incident":
                    # Collision occurred
                    # For simplicity, both cars out (can refine later with fault assignment)
                    attacker_state.running = False
                    attacker_state.dnf_reason = "collision"
                    defender_state.running = False
                    defender_state.dnf_reason = "collision"
                    print(f"  \u2718 COLLISION! {attacker_state.driver_name} and {defender_state.driver_name} crash!")
                else:
                    # Failed attempt - defender holds position
                    pass
                
                completed_attempts.append(key)
        
        # Remove completed attempts
        for key in completed_attempts:
            del self.active_overtakes[key]
    
    def _get_car_ahead(self, state: DriverState, race_state: RaceState) -> Optional[DriverState]:
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
    
    def _get_car_behind(self, state: DriverState, race_state: RaceState) -> Optional[DriverState]:
        """Find the car directly behind"""
        behind_car = None
        min_gap = float('inf')
        
        for other_state in race_state.driver_states.values():
            if other_state.driver_id == state.driver_id or not other_state.running:
                continue
            if other_state.position == state.position + 1:
                gap = other_state.position_m - state.position_m if state.lap == other_state.lap else 999
                if gap < min_gap:
                    min_gap = gap
                    behind_car = other_state
        
        return behind_car
    
    def _race_finished(self, race_state: RaceState) -> bool:
        """Check if race is complete"""
        # Race ends when leader completes all laps or all drivers DNF
        active_drivers = [s for s in race_state.driver_states.values() if s.running]
        
        if not active_drivers:
            return True
        
        leader = max(active_drivers, key=lambda s: (s.lap, s.position_m))
        return leader.lap >= race_state.total_laps
    
    def _create_position_event(self, race_state: RaceState, frame: int) -> Dict[str, Any]:
        """Create position update event for GUI"""
        positions = []
        
        for driver_id, state in race_state.driver_states.items():
            positions.append({
                "driver_id": driver_id,
                "driver_name": state.driver_name,
                "position": state.position,
                "lap": state.lap,
                "position_m": state.position_m,
                "velocity_mps": state.velocity_mps,
                "racing_mode": state.racing_mode.value,
                "push_intensity": state.push_intensity,
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
        """Compile final race results"""
        results = []
        
        # Sort by laps completed and final position
        all_states = list(race_state.driver_states.values())
        all_states.sort(key=lambda s: (-s.lap, -s.position_m))
        
        for position, state in enumerate(all_states, 1):
            results.append({
                "driver_id": state.driver_id,
                "driver_name": state.driver_name,
                "team_id": state.team.id,
                "position": position,
                "laps_completed": state.lap,
                "dnf_reason": state.dnf_reason,
                "best_lap_time": state.best_lap_time if state.best_lap_time < 999 else None,
                "average_lap_time": np.mean(race_state.lap_times[state.driver_id]) if race_state.lap_times[state.driver_id] else None
            })
        
        return results


__all__ = ['RealtimeRaceEngine', 'DriverState', 'RaceState', 'RacingMode']
