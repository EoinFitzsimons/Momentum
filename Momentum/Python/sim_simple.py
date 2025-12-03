"""
Simple Race Simulator - Real-time agent-based racing

Wrapper for real-time racing engine that simulates at 30 FPS with drivers
actively making decisions based on their surroundings and attributes.

Key Features:
- 30 FPS simulation (2,700 updates per 90s lap)
- AI agents make live racing decisions (attack/defend/manage)
- Spatial awareness and overtaking logic
- Live position updates for smooth GUI visualization

Authors: Final Year Project - Computer Science
Date: December 2025
"""

from typing import List, Callable, Optional
from persistence_iface import PersistenceIface
from database.models import Driver as DBDriver, Track as DBTrack
from database.models import RaceResult as DBRaceResult, Team as DBTeam

# Import real-time racing engine
from realtime_race_engine import RealtimeRaceEngine


# ============================================================================
# MAIN SIMULATION FUNCTION
# ============================================================================
    """Calculate lap time considering performance, tyre wear, fuel, and randomness."""
    perf_score = _calculate_performance_score(driver)
    
    # base lap reduced by performance
    lap_base = base_lap_factor * (1.0 - 0.25 * perf_score)
    
    # penalties
    tyre_penalty = 1.0 + (driver_state['tyre_wear'] * 0.40)
    fuel_penalty = 1.0 + (0.02 * (total_laps - current_lap) / max(1, total_laps))
    
    # random variance
    consistency_factor = 1.0 - _norm(driver.consistency)
    var = rnd.uniform(-0.8, 1.6) * (1.0 + consistency_factor * 0.6 + driver_state['aggression'] * 0.3)
    
    return lap_base * tyre_penalty * fuel_penalty + var


def _handle_dnf(
    driver: DBDriver,
    driver_state: Dict,
    lap: int,
    verbose: bool,
    event_callback: Optional[Callable[[dict], None]]
) -> None:
    """Handle driver DNF (crash)."""
    driver_state['running'] = False
    if verbose:
        print(f"{driver.name} (id={driver.id}) had a crash and retired on lap {lap}.")
    if event_callback:
        event_callback({
            "type": "incident",
            "subtype": "dnf",
            "lap": lap,
            "driver_id": driver.id,
        })


def _handle_time_loss(
    driver: DBDriver,
    lap: int,
    delay: float,
    verbose: bool,
    event_callback: Optional[Callable[[dict], None]]
) -> None:
    """Handle incident causing time loss."""
    if verbose:
        print(f"{driver.name} (id={driver.id}) had an incident (+{delay:.1f}s) on lap {lap}.")
    if event_callback:
        event_callback({
            "type": "incident",
            "subtype": "delay",
            "lap": lap,
            "driver_id": driver.id,
            "delay": delay,
        })


def _handle_incident(
    driver: DBDriver,
    driver_state: Dict,
    lap: int,
    rnd: random.Random,
    verbose: bool,
    event_callback: Optional[Callable[[dict], None]]
) -> Optional[str | float]:
    """
    Handle incident chance for driver. 
    Returns 'dnf' if driver crashes, delay in seconds if time loss, or None if no incident.
    """
    incident_roll = rnd.random()
    if incident_roll >= (0.002 + driver_state['aggression'] * 0.003):
        return None
    
    if rnd.random() < 0.25:
        _handle_dnf(driver, driver_state, lap, verbose, event_callback)
        return "dnf"
    
    delay = rnd.uniform(5.0, 35.0)
    _handle_time_loss(driver, lap, delay, verbose, event_callback)
    return delay


def _should_pit(driver: DBDriver, driver_state: Dict, rnd: random.Random) -> bool:
    """Determine if driver should pit based on tyre wear and pit skill."""
    pit_threshold = 0.60 + (0.1 * (1.0 - driver.pit_entry_exit / 100.0))
    prob_pit_early = 0.02 + driver_state['tyre_wear'] * 0.12
    
    return (
        driver_state['tyre_wear'] > pit_threshold
        or (driver_state['stint_laps'] >= 20 and rnd.random() < 0.05)
        or (rnd.random() < prob_pit_early)
    )


def _handle_pit_stop(
    driver: DBDriver,
    driver_state: Dict,
    lap: int,
    pit_time: float,
    rnd: random.Random,
    verbose: bool,
    event_callback: Optional[Callable[[dict], None]]
) -> None:
    """Execute pit stop if conditions are met."""
    if _should_pit(driver, driver_state, rnd):
        driver_state['total_time'] += pit_time
        driver_state['pitstops'] += 1
        driver_state['stint_laps'] = 0
        driver_state['tyre_wear'] = 0.06 * rnd.random()
        
        if verbose:
            print(f"{driver.name} (id={driver.id}) pitted on lap {lap} (+{pit_time}s)")
        if event_callback:
            event_callback({
                "type": "pit",
                "lap": lap,
                "driver_id": driver.id,
                "pit_time": pit_time,
            })


def _emit_standings(
    drivers: List[DBDriver],
    state: Dict[int, Dict],
    lap: int,
    event_callback: Optional[Callable[[dict], None]]
) -> None:
    """Emit current standings after lap completion."""
    if not event_callback:
        return
    
    current = []
    for d in drivers:
        s = state[d.id]
        time_sec = float(s['total_time']) if s['running'] else float(1e9)
        current.append({
            "driver_id": d.id,
            "name": d.name,
            "time_seconds": time_sec,
            "running": bool(s['running']),
        })
    
    current.sort(key=lambda x: x['time_seconds'])
    for idx, row in enumerate(current, start=1):
        row['position'] = idx
    
    event_callback({"type": "standings", "lap": lap, "standings": current})


def _build_results(
    drivers: List[DBDriver],
    state: Dict[int, Dict],
    event_callback: Optional[Callable[[dict], None]]
) -> List[DBRaceResult]:
    """Build final race results from driver states."""
    results: List[DBRaceResult] = []
    
    for d in drivers:
        s = state[d.id]
        if not s['running']:
            # DNF
            rr = DBRaceResult(
                id=0, race_id=0, driver_id=d.id, team_id=0,
                position=0, points=0, fastest_lap=False,
                dnf_reason='crash', grid_position=0
            )
            setattr(rr, 'time_seconds', float(1e9))
        else:
            # Finisher
            rr = DBRaceResult(
                id=0, race_id=0, driver_id=d.id, team_id=0,
                position=0, points=0, fastest_lap=False,
                dnf_reason=None, grid_position=0
            )
            setattr(rr, 'time_seconds', float(s['total_time']))
        results.append(rr)
    
    if event_callback:
        event_callback({
            "type": "race_finished",
            "results": [{
                "driver_id": r.driver_id,
                "time_seconds": getattr(r, 'time_seconds', None),
                "position": r.position
            } for r in results]
        })
    
    # Sort and assign positions
    results.sort(key=lambda r: r.time_seconds)
    for pos, r in enumerate(results, start=1):
        r.position = pos
    
    return results


def _initialize_driver_states(drivers: List[DBDriver]) -> Dict[int, Dict]:
    """Initialize state dictionary for all drivers."""
    state: Dict[int, Dict] = {}
    for d in drivers:
        aggression = max(0.0, min(1.0, (d.overtaking + d.defensive_driving) / 200.0))
        state[d.id] = {
            'driver': d,
            'total_time': 0.0,
            'tyre_wear': 0.0,
            'stint_laps': 0,
            'pitstops': 0,
            'running': True,
            'aggression': aggression,
        }
    return state


def _calculate_laps(track: DBTrack, laps: Optional[int]) -> int:
    """Calculate number of laps for race based on track length."""
    if laps is not None:
        return laps
    return max(20, int(25 - track.length_km)) if track.length_km < 5 else 30


def _process_driver_lap(
    driver: DBDriver,
    driver_state: Dict,
    lap: int,
    laps: int,
    base_lap_factor: float,
    track: DBTrack,
    pit_time: float,
    rnd: random.Random,
    verbose: bool,
    event_callback: Optional[Callable[[dict], None]]
) -> None:
    """Process one lap for a single driver."""
    if not driver_state['running']:
        return
    
    lap_time = _calculate_lap_time(driver, driver_state, base_lap_factor, lap, laps, rnd)
    
    # Handle incidents
    incident_result = _handle_incident(driver, driver_state, lap, rnd, verbose, event_callback)
    if incident_result == "dnf":
        return
    elif incident_result is not None:
        lap_time += incident_result
    
    # Apply lap time and tyre wear
    driver_state['total_time'] += lap_time
    driver_state['stint_laps'] += 1
    wear_rate = 0.01 + driver_state['aggression'] * 0.03 + (1.0 - driver.tire_management / 100.0) * 0.02 + (track.length_km / 200.0)
    driver_state['tyre_wear'] += wear_rate
    
    # Handle pit stop
    _handle_pit_stop(driver, driver_state, lap, pit_time, rnd, verbose, event_callback)


def _check_stop_event(stop_event: Optional[threading.Event], lap: int, verbose: bool) -> bool:
    """Check if simulation should stop. Returns True if should stop."""
    if stop_event is not None and stop_event.is_set():
        if verbose:
            print(f"Simulation stopped at lap {lap}")
        return True
    return False


def simulate_race(
    drivers: List[DBDriver],
    track: DBTrack,
    seed: Optional[int] = None,
    laps: int | None = None,
    verbose: bool = False,
    event_callback: Optional[Callable[[dict], None]] = None,
    stop_event=None,  # Not used in real-time engine
    lap_delay: float = 0.0,  # Not used - real-time engine controls pacing
    db: Optional[PersistenceIface] = None,
) -> List[DBRaceResult]:
    """
    Real-time agent-based race simulator at 30 FPS
    
    NEW ARCHITECTURE: Drivers are AI agents making live decisions based on:
    - Position relative to other cars
    - Gaps ahead/behind
    - Their attributes (aggression, overtaking, tire_management, etc.)
    - Current race situation (attack/defend/manage/cruise modes)
    
    Simulation runs at 30 FPS (0.033s timesteps):
    - 90s lap = 2,700 position updates per lap
    - 20 cars × 50 laps = 2,700,000 total updates
    
    Features:
    - Spatial awareness: drivers know where other cars are
    - Active decision-making: push harder to attack, conserve to manage tires
    - Real-time overtaking with skill-based outcomes
    - Slipstream/drafting effects
    - Tire degradation and fuel consumption
    - Live position updates for smooth GUI visualization
    
    Args:
        drivers: List of drivers participating in race
        track: Track with length and characteristics
        seed: Random seed for reproducibility
        laps: Number of laps (default 50)
        verbose: Print race updates to console
        event_callback: Callback for position updates (called at 30 FPS)
        db: Database interface to fetch team data

    Returns:
        List of RaceResult objects sorted by finishing order
    """
    # Initialize real-time racing engine
    engine = RealtimeRaceEngine(seed=seed)
    
    # Calculate laps if not specified
    if laps is None:
        laps = max(20, min(int(300 / track.length_km), 80))  # 20-80 laps depending on track length
    
    # Fetch team data for all drivers
    teams_dict = {}
    if db:
        try:
            team_ids = set(d.current_team_id for d in drivers if d.current_team_id)
            for team_id in team_ids:
                team = None
                if hasattr(db, 'get_team'):
                    team = db.get_team(team_id)
                
                if team:
                    teams_dict[team_id] = team
        except Exception as e:
            if verbose:
                print(f"Warning: Could not fetch team data: {e}")
    
    # Create dummy teams if none found
    if not teams_dict:
        for driver in drivers:
            if driver.current_team_id not in teams_dict:
                teams_dict[driver.current_team_id] = DBTeam(
                    id=driver.current_team_id,
                    name=f"Team {driver.current_team_id}",
                    nationality="USA",
                    founded_year=2020,
                    discipline="formula",
                    tier="tier2",
                    budget=100.0,
                    headquarters="Unknown",
                    team_principal="Unknown"
                )
    
    # Run real-time simulation
    if verbose:
        print(f"\nStarting real-time race: {len(drivers)} drivers, {laps} laps, {track.length_km:.2f}km track")
        print(f"Simulation rate: 30 FPS (2,700 updates per 90s lap)")
        print(f"Total expected updates: ~{2700 * laps * len(drivers):,}\n")
    
    try:
        results_list = engine.simulate_race(
            drivers=drivers,
            teams=teams_dict,
            track=track,
            total_laps=laps,
            event_callback=event_callback,
            realtime_speed=100.0  # Run as fast as possible (no throttling)
        )
    except Exception as e:
        if verbose:
            print(f"Error in simulation: {e}")
            import traceback
            traceback.print_exc()
        raise
    
    # Convert results to DBRaceResult objects (for backward compatibility)
    db_results = []
    for result in results_list:
        rr = DBRaceResult(
            id=0,
            race_id=0,
            driver_id=result["driver_id"],
            team_id=result["team_id"],
            position=result["position"],
            points=0,  # TODO: Add points calculation
            fastest_lap=False,
            dnf_reason=result["dnf_reason"],
            grid_position=result["position"]
        )
        # Store additional data
        setattr(rr, 'laps_completed', result["laps_completed"])
        setattr(rr, 'best_lap_time', result.get("best_lap_time"))
        setattr(rr, 'average_lap_time', result.get("average_lap_time"))
        db_results.append(rr)
    
    if verbose:
        print("\n=== Final Results ===")
        for i, result in enumerate(results_list[:10], 1):
            status = "DNF" if result["dnf_reason"] else f"{result['laps_completed']} laps"
            best_lap = f"{result['best_lap_time']:.2f}s" if result.get('best_lap_time') else "N/A"
            print(f"{i}. {result['driver_name']} - {status} (Best: {best_lap})")
    
    return db_results
