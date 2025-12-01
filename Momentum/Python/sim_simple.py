from typing import List, Dict, Callable, Optional
import random
import time
import threading
from persistence_iface import PersistenceIface
from database.models import Driver as DBDriver, Track as DBTrack
from database.models import RaceResult as DBRaceResult


def _norm(x: float) -> float:
    """Normalize attribute value to 0-1 range."""
    return max(0.0, min(1.0, x / 100.0))


def _calculate_performance_score(driver: DBDriver) -> float:
    """Calculate weighted performance score from driver attributes."""
    return (
        0.45 * _norm(driver.raw_speed)
        + 0.20 * _norm(driver.cornering_skill)
        + 0.10 * _norm(driver.braking_technique)
        + 0.10 * _norm(driver.acceleration_control)
        + 0.05 * _norm(driver.race_pace)
    )


def _calculate_lap_time(
    driver: DBDriver,
    driver_state: Dict,
    base_lap_factor: float,
    current_lap: int,
    total_laps: int,
    rnd: random.Random
) -> float:
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
    stop_event: Optional[threading.Event] = None,
    lap_delay: float = 0.0,
) -> List[DBRaceResult]:
    """
    Lap-by-lap race simulator.

    Features:
    - Per-lap times influenced by `raw_speed`, tyre wear, fuel effect and randomness
    - Simple pit-stop logic (tyre-driven) and pit time penalty
    - Incidents with small DNF chance
    - Reproducible via `seed`

    Returns list of `RaceResult` sorted by finishing order.
    """
    rnd = random.Random(seed) if seed is not None else random.Random()
    laps = _calculate_laps(track, laps)
    state = _initialize_driver_states(drivers)

    pit_time = 22.0
    base_lap_factor = track.length_km * 60.0

    # simulate each lap
    for lap in range(1, laps + 1):
        if _check_stop_event(stop_event, lap, verbose):
            break
        
        if verbose:
            print(f"--- Lap {lap}/{laps} ---")
        if event_callback:
            event_callback({"type": "lap_start", "lap": lap})

        # Process each driver's lap
        for d in drivers:
            _process_driver_lap(d, state[d.id], lap, laps, base_lap_factor, track, pit_time, rnd, verbose, event_callback)

        _emit_standings(drivers, state, lap, event_callback)
        
        if lap_delay and lap < laps:
            time.sleep(lap_delay)
    
    return _build_results(drivers, state, event_callback)
