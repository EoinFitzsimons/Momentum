"""
Race Simulation API - Real-time agent-based racing interface

Public API for real-time racing simulation where drivers are autonomous AI agents
making live decisions at 30 FPS based on race conditions and their attributes.

Authors: Eoin Fitzsimons
Date: December 2025
"""

from typing import List, Callable, Optional, Dict, Any
import contextlib
import io
from database.models import Driver, Track, RaceResult, Team
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline, BaseDisciplineEngine
import importlib
import inspect
import logging


LOGGER = logging.getLogger(__name__)


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
        LOGGER.debug("Could not import discipline module '%s'", module_path, exc_info=True)
        return None

    # Find first concrete subclass of BaseDisciplineEngine
    for _, cls in inspect.getmembers(mod, inspect.isclass):
        try:
            if issubclass(cls, BaseDisciplineEngine) and cls is not BaseDisciplineEngine:
                return cls(seed=seed if seed is not None else 0)
        except Exception:
            LOGGER.debug("Skipping candidate discipline engine class %s", getattr(cls, '__name__', repr(cls)), exc_info=True)
            continue

    return None


def _setup_context_teams(context: RaceContext) -> None:
    """Populate context.teams if not already set"""
    if not getattr(context, 'teams', None):
        ctx_teams = {}
        for d in getattr(context, 'drivers', []) or []:
            ctx_teams[d.current_team_id] = Team(
                id=d.current_team_id,
                name=f"Fallback Entry {d.current_team_id}",
                nationality="USA",
                discipline="formula",
                tier="tier2",
                budget=100.0,
                founded_year=2020,
                team_principal="Unknown"
            )
        context.teams = ctx_teams


def _extract_context_fields(context: RaceContext, seed: Optional[int]) -> tuple:
    """Extract fields from RaceContext for simulation"""
    engine = RealtimeRaceEngine(seed=seed, db=getattr(context, 'db', None))
    drivers = context.drivers
    track = context.track
    laps = context.total_laps
    event_callback = context.event_callback
    teams_dict = getattr(context, 'teams', {}) or {}
    track_points = None
    player_driver_id = None
    player_overrides = None
    
    # Pull from track_conditions if present
    if isinstance(getattr(context, 'track_conditions', None), dict):
        track_points = context.track_conditions.get('track_points')
        player_driver_id = context.track_conditions.get('player_driver_id')
        player_overrides = context.track_conditions.get('player_overrides')
    
    return engine, drivers, track, laps, event_callback, teams_dict, track_points, player_driver_id, player_overrides


def _populate_team_data_from_db(teams_dict: Dict[int, Team], drivers: Optional[List[Driver]], 
                                 db: Optional[Any], verbose: bool = False) -> Dict[int, Team]:
    """Fetch team data from database if available"""
    if not db or not drivers:
        return teams_dict
    
    try:
        team_ids = {d.current_team_id for d in drivers if d.current_team_id}
        from typing import cast
        db_any = cast(Any, db)
        get_team_fn = getattr(db_any, "get_team", None)
        for team_id in team_ids:
            if callable(get_team_fn) and team_id not in teams_dict:
                team = get_team_fn(team_id)
                if team:
                    teams_dict[team_id] = team
    except Exception as e:
        if verbose:
            print(f"Warning: Could not fetch team data: {e}")
    
    return teams_dict


def _create_fallback_teams(teams_dict: Dict[int, Team], drivers: Optional[List[Driver]], verbose: bool = False) -> Dict[int, Team]:
    """Create fallback teams for drivers missing resolvable team data."""
    if not drivers:
        return teams_dict

    created = 0
    for driver in drivers:
        if driver.current_team_id not in teams_dict:
            teams_dict[driver.current_team_id] = Team(
                id=driver.current_team_id,
                name=f"Fallback Entry {driver.current_team_id}",
                nationality="USA",
                discipline="formula",
                tier="tier2",
                budget=100.0,
                founded_year=2020,
                team_principal="Unknown"
            )
            created += 1

    if verbose and created > 0:
        print(f"Warning: created {created} fallback team entries for unresolved team IDs")

    return teams_dict


def _calculate_race_laps(track: Optional[Track], laps: Optional[int]) -> int:
    """Calculate appropriate lap count based on track length"""
    if laps is not None:
        return laps
    if track is not None:
        return max(20, min(int(300 / track.length_km), 80))
    return 20


def _print_race_summary(verbose: bool, track: Optional[Track], drivers: Optional[List[Driver]], laps: Optional[int]) -> None:
    """Print race simulation summary info"""
    if not verbose or track is None or drivers is None or laps is None:
        return
    
    print(f"\n{'='*70}")
    print("REAL-TIME RACE SIMULATION - 30 FPS")
    print(f"{'='*70}")
    print(f"Track: {track.name} ({track.length_km:.2f}km)")
    print(f"Drivers: {len(drivers)} | Laps: {laps}")
    print(f"Expected updates: ~{2700 * laps * len(drivers):,}")
    print(f"{'='*70}\n")


def _extract_time_from_result(result: dict) -> Optional[float]:
    """Extract total time from result dict, trying multiple common field names"""
    # Try direct time fields
    for k in ("time_seconds", "total_time", "total_time_seconds", "race_time", "total_seconds"):
        if k in result and result[k] is not None:
            try:
                return float(result[k])
            except Exception:
                continue
    
    # Fallback: calculate from lap times
    avg = result.get("average_lap_time") or result.get("best_lap_time")
    laps = result.get("laps_completed") or 0
    try:
        if avg and laps:
            return float(avg) * float(laps)
    except Exception:
        LOGGER.debug("Could not derive total time from lap values avg=%r laps=%r", avg, laps, exc_info=True)
    
    return None


def _convert_result_to_race_result(result: dict, race_id: int) -> RaceResult:
    """Convert a simulation result dict to a RaceResult object"""
    total_time = _extract_time_from_result(result)
    
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
    
    # Set status from result or infer from DNF reason
    try:
        rr.status = result.get('status') or ('DNF' if result.get('dnf_reason') else 'FINISHED')
    except Exception:
        LOGGER.debug("Could not derive race result status; defaulting to FINISHED", exc_info=True)
        rr.status = 'FINISHED'
    
    return rr


def _convert_results_to_race_results(results_list: List[dict], race_id: int) -> List[RaceResult]:
    """Convert simulation results list to RaceResult objects"""
    return [_convert_result_to_race_result(result, race_id) for result in results_list]


def _print_final_results_summary(verbose: bool, results_list: List[dict]) -> None:
    """Print final results summary to console"""
    if not verbose:
        return
    
    print(f"\n{'='*70}")
    print("FINAL RESULTS")
    print(f"{'='*70}")
    for i, result in enumerate(results_list[:10], 1):
        status = f"DNF ({result['dnf_reason']})" if result["dnf_reason"] else f"{result['laps_completed']} laps"
        best = f"{result['best_lap_time']:.2f}s" if result.get('best_lap_time') else "N/A"
        print(f"{i:2d}. {result['driver_name']:20s} - {status:15s} | Best: {best}")
    print(f"{'='*70}\n")


def _persist_race_results(db: Optional[Any], race_id: int, results_list: List[dict]) -> None:
    """Persist race results to database if available"""
    if not db or not race_id or not getattr(db, 'save_race_results', None):
        return
    
    try:
        save_fn = getattr(db, 'save_race_results')
        save_fn(race_id, results_list)
    except Exception:
        LOGGER.warning("Failed to persist race results for race_id=%s", race_id, exc_info=True)


def _create_realtime_engine(seed: Optional[int], verbose: bool, db: Optional[Any]) -> RealtimeRaceEngine:
    """Create and configure the realtime engine instance."""
    engine = RealtimeRaceEngine(seed=seed)
    engine.debug_logging = bool(verbose)
    if db is not None:
        engine.db = db
    return engine


def _try_run_context_adapter(context: RaceContext, seed: Optional[int], verbose: bool):
    """Return adapter simulation result when a discipline adapter exists, else None."""
    try:
        _setup_context_teams(context)
    except Exception:
        LOGGER.warning("Failed to prepare context teams; continuing with fallback flow", exc_info=True)

    adapter = _load_discipline_engine(context, seed=seed)
    if adapter is None:
        return None
    if verbose:
        print(f"Using discipline adapter: {adapter.__class__.__name__} for {context.discipline}")
    return adapter.simulate_race(context)


def _resolve_simulation_inputs_from_context(
    context: Optional[RaceContext],
    engine: RealtimeRaceEngine,
    drivers: Optional[List[Driver]],
    track: Optional[Track],
    laps: Optional[int],
    event_callback: Optional[Callable[[dict], None]],
    teams_dict: Dict[int, Team],
    track_points: Optional[List],
    player_driver_id: Optional[int],
    player_overrides: Optional[Dict[str, float]],
    seed: Optional[int],
) -> tuple:
    """Return normalized simulation inputs after optional RaceContext extraction."""
    if context is None:
        return engine, drivers, track, laps, event_callback, teams_dict, track_points, player_driver_id, player_overrides
    return _extract_context_fields(context, seed)


def _validate_required_simulation_inputs(drivers: Optional[List[Driver]], track: Optional[Track]) -> None:
    """Validate required non-optional inputs for simulation runtime."""
    if drivers is None:
        raise ValueError("drivers parameter is required")
    if track is None:
        raise ValueError("track parameter is required")


def _resolve_realtime_speed(verbose: bool, event_callback: Optional[Callable[[dict], None]]) -> float:
    """Use fast defaults for headless runs and slower speed for visualised runs."""
    return 5.0 if (verbose or event_callback is not None) else 250.0


def _build_engine_run_kwargs(
    drivers: List[Driver],
    teams_dict: Dict[int, Team],
    track: Track,
    laps: int,
    event_callback: Optional[Callable[[dict], None]],
    stop_event: Any,
    realtime_speed: float,
    track_points: Optional[List],
    player_driver_id: Optional[int],
    player_overrides: Optional[Dict[str, float]],
) -> Dict[str, Any]:
    """Build runtime kwargs for RealtimeRaceEngine.simulate_race."""
    return {
        'drivers': drivers,
        'teams': teams_dict,
        'track': track,
        'total_laps': laps,
        'event_callback': event_callback,
        'stop_event': stop_event,
        'realtime_speed': float(realtime_speed),
        'track_points': track_points,
        'player_driver_id': player_driver_id,
        'player_overrides': player_overrides,
    }


def _execute_engine_simulation(
    engine: RealtimeRaceEngine,
    run_kwargs: Dict[str, Any],
    verbose: bool,
    event_callback: Optional[Callable[[dict], None]],
) -> List[dict]:
    """Execute engine simulation with optional stdout suppression for headless runs."""
    suppress_output = (not verbose and event_callback is None)
    if suppress_output:
        with contextlib.redirect_stdout(io.StringIO()):
            return engine.simulate_race(**run_kwargs)
    return engine.simulate_race(**run_kwargs)


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
    engine = _create_realtime_engine(seed, verbose, db)
    teams_dict: Dict[int, Team] = {}

    if context is not None:
        adapter_results = _try_run_context_adapter(context, seed, verbose)
        if adapter_results is not None:
            return adapter_results

    engine, drivers, track, laps, event_callback, teams_dict, track_points, player_driver_id, player_overrides = _resolve_simulation_inputs_from_context(
        context,
        engine,
        drivers,
        track,
        laps,
        event_callback,
        teams_dict,
        track_points,
        player_driver_id,
        player_overrides,
        seed,
    )
    
    # Fetch team data from database if provided
    teams_dict = _populate_team_data_from_db(teams_dict, drivers, db, verbose)
    
    # Create fallback teams if needed
    teams_dict = _create_fallback_teams(teams_dict, drivers, verbose)
    
    # Validate required parameters before using helper flows
    _validate_required_simulation_inputs(drivers, track)

    # Explicitly narrow optionals after validation for static type checkers.
    assert drivers is not None
    assert track is not None

    # Calculate lap count
    laps = _calculate_race_laps(track, laps)
    realtime_speed = _resolve_realtime_speed(verbose, event_callback)
    
    # Print summary
    _print_race_summary(verbose, track, drivers, laps)
    
    try:
        run_kwargs = _build_engine_run_kwargs(
            drivers=drivers,
            teams_dict=teams_dict,
            track=track,
            laps=laps,
            event_callback=event_callback,
            stop_event=stop_event,
            realtime_speed=realtime_speed,
            track_points=track_points,
            player_driver_id=player_driver_id,
            player_overrides=player_overrides,
        )
        results_list = _execute_engine_simulation(engine, run_kwargs, verbose, event_callback)
    except Exception as e:
        if verbose:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
        raise
    
    # Convert to RaceResult objects
    db_results = _convert_results_to_race_results(results_list, race_id)
    
    # Print final results summary
    _print_final_results_summary(verbose, results_list)
    
    # Persist results to database
    _persist_race_results(db, race_id, db_results)

    return db_results
