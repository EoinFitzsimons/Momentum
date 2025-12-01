from typing import List, Dict, Callable, Optional
import random
import time
import threading
from persistence_iface import PersistenceIface
from database.models import Driver as DBDriver, Track as DBTrack
from database.models import RaceResult as DBRaceResult


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
    # If seed is None use system randomness for non-deterministic runs;
    # otherwise use the provided seed for reproducible behaviour.
    rnd = random.Random(seed) if seed is not None else random.Random()

    # Heuristic laps if not provided: make race longer on longer tracks
    if laps is None:
        laps = max(20, int(25 - track.length_km)) if track.length_km < 5 else 30

    # Per-driver state
    state: Dict[int, Dict] = {}
    for d in drivers:
        # aggression influences tyre wear and risky overtaking (derived)
        aggression = max(0.0, min(1.0, (d.overtaking + d.defensive_driving) / 200.0))
        state[d.id] = {
            'driver': d,
            'total_time': 0.0,
            'tyre_wear': 0.0,  # 0..1 where 1 means tyres are shot
            'stint_laps': 0,
            'pitstops': 0,
            'running': True,
            'aggression': aggression,
        }

    pit_time = 22.0  # seconds lost for a pitstop (simple fixed)
    base_lap_factor = track.length_km * 60.0  # base scaling (seconds)

    # simulate each lap
    for lap in range(1, laps + 1):
        # allow cooperative cancellation from caller (GUI Stop)
        if stop_event is not None and stop_event.is_set():
            if verbose:
                print(f"Simulation stopped at lap {lap}")
            break
        if verbose:
            print(f"--- Lap {lap}/{laps} ---")
        if event_callback:
            event_callback({"type": "lap_start", "lap": lap})

        # per-driver lap computation
        for d in drivers:
            s = state[d.id]
            if not s['running']:
                continue

            # Performance factor: weighted combination of core attributes
            # Normalize attributes (0..1)
            def norm(x):
                return max(0.0, min(1.0, x / 100.0))

            perf_score = (
                0.45 * norm(d.raw_speed)
                + 0.20 * norm(d.cornering_skill)
                + 0.10 * norm(d.braking_technique)
                + 0.10 * norm(d.acceleration_control)
                + 0.05 * norm(d.race_pace)
            )

            # base lap reduced by performance (better drivers reduce lap time)
            lap_base = base_lap_factor * (1.0 - 0.25 * perf_score)

            # tyre degradation increases lap time
            tyre_penalty = 1.0 + (s['tyre_wear'] * 0.40)

            # fuel effect: early laps slightly slower due to heavier fuel (small effect)
            fuel_penalty = 1.0 + (0.02 * (laps - lap) / max(1, laps))

            # random variance influenced by consistency (more consistent -> less noise)
            consistency_factor = 1.0 - norm(d.consistency)
            var = rnd.uniform(-0.8, 1.6) * (1.0 + consistency_factor * 0.6 + s['aggression'] * 0.3)

            lap_time = lap_base * tyre_penalty * fuel_penalty + var

            # incident chance
            incident_roll = rnd.random()
            if incident_roll < (0.002 + s['aggression'] * 0.003):
                # incident: either time loss or DNF
                if rnd.random() < 0.25:
                    # DNF
                    s['running'] = False
                    if verbose:
                        print(f"{d.name} (id={d.id}) had a crash and retired on lap {lap}.")
                    if event_callback:
                        event_callback({
                            "type": "incident",
                            "subtype": "dnf",
                            "lap": lap,
                            "driver_id": d.id,
                        })
                    continue
                else:
                    # time loss
                    delay = rnd.uniform(5.0, 35.0)
                    lap_time += delay
                    if verbose:
                        print(f"{d.name} (id={d.id}) had an incident (+{delay:.1f}s) on lap {lap}.")
                    if event_callback:
                        event_callback({
                            "type": "incident",
                            "subtype": "delay",
                            "lap": lap,
                            "driver_id": d.id,
                            "delay": delay,
                        })

            # apply lap time
            s['total_time'] += lap_time
            s['stint_laps'] += 1
            # increase tyre wear (wear rate depends on aggression and tyre management)
            wear_rate = 0.01 + s['aggression'] * 0.03 + (1.0 - d.tire_management / 100.0) * 0.02 + (track.length_km / 200.0)
            s['tyre_wear'] += wear_rate

            # pitstop decision: consider tyre_wear and driver's pit entry/exit skill
            # Add a small probabilistic component so pitting isn't fully deterministic
            pit_threshold = 0.60 + (0.1 * (1.0 - d.pit_entry_exit / 100.0))
            prob_pit_early = 0.02 + s['tyre_wear'] * 0.12  # small chance scaled with wear
            if s['tyre_wear'] > pit_threshold or (s['stint_laps'] >= 20 and rnd.random() < 0.05) or (rnd.random() < prob_pit_early):
                # pit
                s['total_time'] += pit_time
                s['pitstops'] += 1
                s['stint_laps'] = 0
                s['tyre_wear'] = 0.06 * rnd.random()  # fresh tyres
                if verbose:
                    print(f"{d.name} (id={d.id}) pitted on lap {lap} (+{pit_time}s)")
                if event_callback:
                    event_callback({
                        "type": "pit",
                        "lap": lap,
                        "driver_id": d.id,
                        "pit_time": pit_time,
                    })

        # simple overtaking: reorder drivers by total_time so far
        # this is a proxy for track position; fast drivers will naturally move up
        # We don't model spatial gaps precisely, but the lap-by-lap variation creates dynamic changes
        # Emit current standings after each lap so UI can show live leaderboard
        if event_callback:
            # build standings sorted by total_time (DNF drivers have large time)
            current = []
            for d in drivers:
                s = state[d.id]
                t = float(s['total_time']) if s['running'] else getattr(s, 'total_time', float(1e9))
                current.append({
                    "driver_id": d.id,
                    "name": d.name,
                    "time_seconds": float(s['total_time']) if s['running'] else float(1e9),
                    "running": bool(s['running']),
                })
            # sort by time and assign positions
            current.sort(key=lambda x: x['time_seconds'])
            for idx, row in enumerate(current, start=1):
                row['position'] = idx
            event_callback({"type": "standings", "lap": lap, "standings": current})
        # optional pacing for demo/real-time mode
        if lap_delay and lap < laps:
            time.sleep(lap_delay)
    # Build results: drivers still running plus those who retired (DNF get very large time)
    results: List[DBRaceResult] = []
    for d in drivers:
        s = state[d.id]
        if not s['running']:
            # DNF: treat as very large time (so they are placed at the back)
            rr = DBRaceResult(id=0, race_id=0, driver_id=d.id, team_id=0, position=0, points=0, fastest_lap=False, dnf_reason='crash', grid_position=0)
            setattr(rr, 'time_seconds', float(1e9))
            results.append(rr)
        else:
            # create a minimal RaceResult: id/race_id will be set by persistence if needed
            rr = DBRaceResult(id=0, race_id=0, driver_id=d.id, team_id=0, position=0, points=0, fastest_lap=False, dnf_reason=None, grid_position=0)
            # attach time_seconds for storage/inspection (not part of dataclass schema but used by runner)
            setattr(rr, 'time_seconds', float(s['total_time']))
            results.append(rr)

    if event_callback:
        # emit a finished summary event
        event_callback({"type": "race_finished", "results": [{"driver_id": r.driver_id, "time_seconds": getattr(r, 'time_seconds', None), "position": r.position} for r in results]})

    # sort and assign finishing positions
    results.sort(key=lambda r: r.time_seconds)
    pos = 1
    for r in results:
        r.position = pos
        pos += 1

    return results
