"""
Race Simulation API - Real-time agent-based racing interface

Public API for real-time racing simulation where drivers are autonomous AI agents
making live decisions at 30 FPS based on race conditions and their attributes.

Authors: Final Year Project - Computer Science
Date: December 2025
"""

from typing import List, Callable, Optional, Dict, Any
from database.models import Driver, Track, RaceResult, Team
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline, BaseDisciplineEngine
import importlib
import inspect


def _load_discipline_engine(context: RaceContext, seed: Optional[int] = None) -> Optional[BaseDisciplineEngine]:
    """Dynamically load a discipline adapter matching the context.discipline.

    Strategy:
    - Derive module path from discipline enum value (lowercase). Example:
      RacingDiscipline.SINGLE_SEATER -> module `RaceLogic.disciplines.single_seater.single_seater_discipline`
    - Import module and find the first class that subclasses BaseDisciplineEngine.
    - Instantiate with seed and return instance.
    - Return None on failure to allow fallback to RealtimeRaceEngine.
    """
    if not context or not getattr(context, 'discipline', None):
        return None

    disc_name = context.discipline.value.lower()
    module_path = f"RaceLogic.disciplines.{disc_name}.{disc_name}_discipline"
    try:
        mod = importlib.import_module(module_path)
    except Exception:
        return None

    # Find first concrete subclass of BaseDisciplineEngine
    for _, cls in inspect.getmembers(mod, inspect.isclass):
        try:
            if issubclass(cls, BaseDisciplineEngine) and cls is not BaseDisciplineEngine:
                return cls(seed=seed if seed is not None else 0)
        except Exception:
            continue

    return None


def simulate_race(
    drivers: Optional[List[Driver]] = None,
    track: Optional[Track] = None,
    seed: Optional[int] = None,
    laps: Optional[int] = None,
    race_id: int = 0,
    verbose: bool = False,
    event_callback: Optional[Callable[[dict], None]] = None,
    stop_event=None,
    db: Optional[Any] = None,
    track_points: Optional[List] = None,
    player_driver_id: Optional[int] = None,
    player_overrides: Optional[Dict[str, float]] = None,
    context: Optional[RaceContext] = None,
) -> List[RaceResult]:
    """
    Run real-time agent-based race simulation at 30 FPS
    
    Drivers are AI agents making live racing decisions (attack/defend/manage)
    based on gaps, position, and their attributes.
    """
    # If a full RaceContext is provided prefer discipline-specific engines
    if context is not None:
        # Best-effort: ensure a minimal teams mapping exists on the context so
        # discipline adapters or fallback engines that require a team object
        # per-driver don't skip drivers when callers omit `context.teams`.
        try:
            if not getattr(context, 'teams', None):
                ctx_teams = {}
                for d in getattr(context, 'drivers', []) or []:
                    ctx_teams[d.current_team_id] = Team(
                        id=d.current_team_id,
                        name=f"Team {d.current_team_id}",
                        nationality="USA",
                        discipline="formula",
                        tier="tier2",
                        budget=100.0,
                        founded_year=2020,
                        team_principal="Unknown"
                    )
                context.teams = ctx_teams
        except Exception:
            # Best-effort population; if anything goes wrong, continue and let
            # the downstream engine handle missing teams gracefully.
            pass

        # Try to dynamically load a discipline adapter
        adapter = _load_discipline_engine(context, seed=seed)
        if adapter is not None:
            if verbose:
                print(f"Using discipline adapter: {adapter.__class__.__name__} for {context.discipline}")
            return adapter.simulate_race(context)

        # Otherwise, fall back to RealtimeRaceEngine using the context fields
        engine = RealtimeRaceEngine(seed=seed)
        drivers = context.drivers
        track = context.track
        laps = context.total_laps
        event_callback = context.event_callback
        # Provide teams if available on context
        teams_dict = getattr(context, 'teams', {}) or {}
        # Pull track_points and player overrides from context.track_conditions if present
        if isinstance(getattr(context, 'track_conditions', None), dict):
            track_points = context.track_conditions.get('track_points', track_points)
            player_driver_id = context.track_conditions.get('player_driver_id', player_driver_id)
            player_overrides = context.track_conditions.get('player_overrides', player_overrides)
        if laps is None:
            laps = max(20, min(int(300 / track.length_km), 80))

    else:
        engine = RealtimeRaceEngine(seed=seed)
    
    if context is None:
        if laps is None and track is not None:
            laps = max(20, min(int(300 / track.length_km), 80))
        elif laps is None:
            laps = 20  # Default if no track provided
    
    # Fetch team data if not provided via context
    if 'teams_dict' not in locals():
        teams_dict = {}
    if db and drivers is not None:
        try:
            team_ids = {d.current_team_id for d in drivers if d.current_team_id}
            # Some PersistenceIface implementations may provide get_team but the
            # interface type does not declare it; access it dynamically and cast
            # to Any to satisfy static type-checkers.
            from typing import Any, cast
            db_any = cast(Any, db)
            get_team_fn = getattr(db_any, "get_team", None)
            for team_id in team_ids:
                if callable(get_team_fn):
                    team = get_team_fn(team_id)
                    if team:
                        teams_dict[team_id] = team
        except Exception as e:
            if verbose:
                print(f"Warning: Could not fetch team data: {e}")
    
    # Create placeholder teams if needed
    if not teams_dict and drivers is not None:
        for driver in drivers:
            if driver.current_team_id not in teams_dict:
                teams_dict[driver.current_team_id] = Team(
                    id=driver.current_team_id,
                    name=f"Team {driver.current_team_id}",
                    nationality="USA",
                    discipline="formula",
                    tier="tier2",
                    budget=100.0,
                    founded_year=2020,
                    team_principal="Unknown"
                )
    
    if verbose and track is not None and drivers is not None and laps is not None:
        print(f"\n{'='*70}")
        print("REAL-TIME RACE SIMULATION - 30 FPS")
        print(f"{'='*70}")
        print(f"Track: {track.name} ({track.length_km:.2f}km)")
        print(f"Drivers: {len(drivers)} | Laps: {laps}")
        print(f"Expected updates: ~{2700 * laps * len(drivers):,}")
        print(f"{'='*70}\n")
    
    # Run simulation with visual track
    # Ensure required parameters are not None
    if drivers is None:
        raise ValueError("drivers parameter is required")
    if track is None:
        raise ValueError("track parameter is required")
    if laps is None:
        laps = 20  # Default fallback
    
    try:
        results_list = engine.simulate_race(
            drivers=drivers,
            teams=teams_dict,
            track=track,
            total_laps=laps,
            event_callback=event_callback,
            stop_event=stop_event,  # Pass stop event for cancellation
            realtime_speed=5.0,  # 5x real-time speed for watchable racing
            track_points=track_points,  # Visual track for unified position mapping
            player_driver_id=player_driver_id,  # Player-controlled driver
            player_overrides=player_overrides  # Player's pace and overtake settings
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
        # Attempt to extract a sensible total time from common keys
        def _extract_time(res):
            for k in ("time_seconds", "total_time", "total_time_seconds", "race_time", "total_seconds"):
                if k in res and res[k] is not None:
                    try:
                        return float(res[k])
                    except Exception:
                        continue
            # Fallback: if average lap time and laps are present, estimate total
            avg = res.get("average_lap_time") or res.get("best_lap_time")
            laps = res.get("laps_completed") or 0
            try:
                if avg and laps:
                    return float(avg) * float(laps)
            except Exception:
                pass
            return None

        total_time = _extract_time(result)

        rr = RaceResult(
            id=0,
            race_id=race_id,
            driver_id=result.get("driver_id"),
            team_id=result.get("team_id"),
            position=result.get("position"),
            points=result.get("points", 0),
            fastest_lap=bool(result.get("fastest_lap", False)),
            dnf_reason=result.get("dnf_reason"),
            grid_position=result.get("position"),
            time_seconds=total_time,
            best_lap_time=result.get("best_lap_time"),
            average_lap_time=result.get("average_lap_time")
        )
        setattr(rr, 'laps_completed', result.get("laps_completed", 0))
        # Persist explicit status if engine provided one (DNF/FINISHED)
        try:
            rr.status = result.get('status') or ('DNF' if result.get('dnf_reason') else 'FINISHED')
        except Exception:
            rr.status = 'FINISHED'
        db_results.append(rr)
    
    if verbose:
        print(f"\n{'='*70}")
        print("FINAL RESULTS")
        print(f"{'='*70}")
        for i, result in enumerate(results_list[:10], 1):
            status = f"DNF ({result['dnf_reason']})" if result["dnf_reason"] else f"{result['laps_completed']} laps"
            best = f"{result['best_lap_time']:.2f}s" if result.get('best_lap_time') else "N/A"
            print(f"{i:2d}. {result['driver_name']:20s} - {status:15s} | Best: {best}")
        print(f"{'='*70}\n")
    
    # Persist results if a persistence layer and race_id provided
    try:
        if db and race_id and getattr(db, 'save_race_results', None):
            save_fn = getattr(db, 'save_race_results')
            if callable(save_fn):
                try:
                    save_fn(race_id, db_results)
                except Exception:
                    # Do not hide simulation results on persistence failure
                    if verbose:
                        print(f"Warning: failed to persist race results for race_id={race_id}")
    except Exception:
        # Silently ignore persistence-related errors here
        pass

    return db_results
