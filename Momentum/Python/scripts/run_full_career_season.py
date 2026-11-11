"""Run a repeatable full-season career-mode simulation.

This script creates a championship, schedules a season, simulates each race,
persists the results, and prints the final standings. It is intended for
report evidence and manual regression checks.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import os
import sys
from typing import Any, Dict, List


_THIS_DIR = os.path.dirname(__file__)
_PKG_ROOT = os.path.normpath(os.path.join(_THIS_DIR, ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from database.database_manager import DatabaseManager
from database.models import Championship
from services.championship_service import ChampionshipService
from services.race_simulation_api import persist_race_results, simulate_race


def _select_grid(db: DatabaseManager, discipline: str, grid_size: int):
    drivers = [
        driver
        for driver in db.get_all_drivers()
        if getattr(driver, "preferred_discipline", None) == discipline
        and getattr(driver, "current_team_id", None)
    ]
    if len(drivers) < grid_size:
        drivers = [
            driver
            for driver in db.get_all_drivers()
            if getattr(driver, "current_team_id", None)
        ]
    if len(drivers) < grid_size:
        raise ValueError(
            f"Not enough drivers with team assignments: have {len(drivers)}, need {grid_size}"
        )
    return drivers[:grid_size]


def _select_tracks(db: DatabaseManager, discipline: str, race_count: int) -> List[int]:
    tracks = db.get_tracks_by_discipline(discipline) or db.get_all_tracks()
    if len(tracks) < race_count:
        raise ValueError(
            f"Not enough tracks for a season: have {len(tracks)}, need {race_count}"
        )
    return [track.id for track in tracks[:race_count]]


def _ensure_result_team_ids(db: DatabaseManager, results: List[Any]) -> None:
    for result in results:
        if getattr(result, "team_id", None):
            continue
        driver = db.get_driver(getattr(result, "driver_id", 0))
        result.team_id = getattr(driver, "current_team_id", 0) or 0


def run_season(
    discipline: str = "SINGLE_SEATER",
    race_count: int = 10,
    grid_size: int = 20,
    laps_per_race: int = 1,
    season_year: int = 2026,
    db: DatabaseManager | None = None,
) -> Dict[str, Any]:
    db = db or DatabaseManager()
    service = ChampionshipService(db)

    tracks = _select_tracks(db, discipline, race_count)
    grid = _select_grid(db, discipline, grid_size)

    championship = Championship(
        id=0,
        name=f"Auto Career Season {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        discipline=discipline,
        season_length=len(tracks),
        points_system=discipline,
        current_season=1,
    )

    championship_id, race_ids = service.create_championship_season(
        championship=championship,
        tracks=tracks,
        start_date=datetime(season_year, 1, 1),
    )

    completed_races = 0
    for race_id in race_ids:
        ok, error = service.update_race_lifecycle_status(race_id, "in-progress")
        if not ok:
            print(f"[WARN] could not mark race {race_id} in-progress: {error}")
            continue

        race = db.get_race(race_id)
        track = db.get_track(race.track_id) if race else None
        if not track:
            print(f"[WARN] race {race_id} missing track; skipping")
            continue

        results = simulate_race(
            drivers=grid,
            track=track,
            laps=laps_per_race,
            race_id=race_id,
            verbose=False,
            db=None,
        )

        _ensure_result_team_ids(db, results)

        for result in results:
            result.points = service.calculate_points(
                position=int(getattr(result, "position", 0) or 0),
                discipline=discipline,
                fastest_lap=bool(getattr(result, "fastest_lap", False)),
            )

        persist_race_results(db, results)

        ok, error = service.update_race_lifecycle_status(race_id, "completed")
        if not ok:
            print(f"[WARN] could not mark race {race_id} completed: {error}")
        else:
            completed_races += 1

    standings = service.recalculate_standings(championship_id, 1)

    return {
        "championship_id": championship_id,
        "scheduled_races": len(race_ids),
        "completed_races": completed_races,
        "grid_size": len(grid),
        "discipline": discipline,
        "standings": standings,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a full career-mode season simulation."
    )
    parser.add_argument(
        "--discipline",
        default="SINGLE_SEATER",
        help="Discipline to run (default: SINGLE_SEATER)",
    )
    parser.add_argument(
        "--races",
        type=int,
        default=10,
        help="Number of races in the season (default: 10)",
    )
    parser.add_argument(
        "--grid-size",
        type=int,
        default=20,
        help="Number of cars on the grid (default: 20)",
    )
    parser.add_argument(
        "--laps", type=int, default=1, help="Laps per race (default: 1)"
    )
    parser.add_argument(
        "--season-year",
        type=int,
        default=2026,
        help="Start year for the season (default: 2026)",
    )
    args = parser.parse_args(argv)

    outcome = run_season(
        discipline=args.discipline,
        race_count=args.races,
        grid_size=args.grid_size,
        laps_per_race=args.laps,
        season_year=args.season_year,
    )

    print("--- FULL CAREER SEASON COMPLETE ---")
    print(f"championship_id {outcome['championship_id']}")
    print(f"scheduled_races {outcome['scheduled_races']}")
    print(f"completed_races {outcome['completed_races']}")
    print(f"grid_size {outcome['grid_size']}")
    print(f"discipline {outcome['discipline']}")
    print("top5:")
    for entry in outcome["standings"][:5]:
        print(
            f"P{entry.position} driver_id={entry.driver_id} points={entry.total_points} wins={entry.wins} podiums={entry.podiums}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
