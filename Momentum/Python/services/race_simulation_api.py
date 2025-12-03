"""
Race Simulation API - Real-time agent-based racing interface

Public API for real-time racing simulation where drivers are autonomous AI agents
making live decisions at 30 FPS based on race conditions and their attributes.

Authors: Final Year Project - Computer Science
Date: December 2025
"""

from typing import List, Callable, Optional
from services.persistence_iface import PersistenceIface
from database.models import Driver, Track, RaceResult, Team
from disciplines.realtime_race_engine import RealtimeRaceEngine


def simulate_race(
    drivers: List[Driver],
    track: Track,
    seed: Optional[int] = None,
    laps: Optional[int] = None,
    verbose: bool = False,
    event_callback: Optional[Callable[[dict], None]] = None,
    stop_event=None,
    lap_delay: float = 0.0,
    db: Optional[PersistenceIface] = None,
    track_points: Optional[List] = None,
) -> List[RaceResult]:
    """
    Run real-time agent-based race simulation at 30 FPS
    
    Drivers are AI agents making live racing decisions (attack/defend/manage)
    based on gaps, position, and their attributes.
    """
    engine = RealtimeRaceEngine(seed=seed)
    
    if laps is None:
        laps = max(20, min(int(300 / track.length_km), 80))
    
    # Fetch team data
    teams_dict = {}
    if db:
        try:
            team_ids = set(d.current_team_id for d in drivers if d.current_team_id)
            for team_id in team_ids:
                if hasattr(db, 'get_team'):
                    team = db.get_team(team_id)
                    if team:
                        teams_dict[team_id] = team
        except Exception as e:
            if verbose:
                print(f"Warning: Could not fetch team data: {e}")
    
    # Create placeholder teams if needed
    if not teams_dict:
        for driver in drivers:
            if driver.current_team_id not in teams_dict:
                teams_dict[driver.current_team_id] = Team(
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
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"REAL-TIME RACE SIMULATION - 30 FPS")
        print(f"{'='*70}")
        print(f"Track: {track.name} ({track.length_km:.2f}km)")
        print(f"Drivers: {len(drivers)} | Laps: {laps}")
        print(f"Expected updates: ~{2700 * laps * len(drivers):,}")
        print(f"{'='*70}\n")
    
    # Run simulation with visual track
    try:
        results_list = engine.simulate_race(
            drivers=drivers,
            teams=teams_dict,
            track=track,
            total_laps=laps,
            event_callback=event_callback,
            realtime_speed=5.0,  # 5x real-time speed for watchable racing
            track_points=track_points  # Visual track for unified position mapping
        )
    except Exception as e:
        if verbose:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
        raise
    
    # Convert to RaceResult objects
    db_results = []
    for result in results_list:
        rr = RaceResult(
            id=0, race_id=0,
            driver_id=result["driver_id"],
            team_id=result["team_id"],
            position=result["position"],
            points=0,
            fastest_lap=False,
            dnf_reason=result["dnf_reason"],
            grid_position=result["position"]
        )
        setattr(rr, 'laps_completed', result["laps_completed"])
        setattr(rr, 'best_lap_time', result.get("best_lap_time"))
        setattr(rr, 'average_lap_time', result.get("average_lap_time"))
        db_results.append(rr)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"FINAL RESULTS")
        print(f"{'='*70}")
        for i, result in enumerate(results_list[:10], 1):
            status = f"DNF ({result['dnf_reason']})" if result["dnf_reason"] else f"{result['laps_completed']} laps"
            best = f"{result['best_lap_time']:.2f}s" if result.get('best_lap_time') else "N/A"
            print(f"{i:2d}. {result['driver_name']:20s} - {status:15s} | Best: {best}")
        print(f"{'='*70}\n")
    
    return db_results
