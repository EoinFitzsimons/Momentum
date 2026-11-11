"""Integration tests for championship lifecycle and standings flow."""

from momentum.database.models import RaceResult
from momentum.services.race_simulation_api import persist_race_results
import pytest


@pytest.mark.integration
def test_create_championship_season_assigns_discipline_surface(seeded_championship):
    db = seeded_championship["db"]
    seed = seeded_championship["seed"]

    for track_id in seed["track_ids"]:
        track = db.get_track(track_id)
        assert track is not None
        assert track.surface == "mixed"


@pytest.mark.integration
def test_validate_race_event_rejects_date_conflict(seeded_championship):
    service = seeded_championship["service"]
    championship_id = seeded_championship["championship_id"]
    seed = seeded_championship["seed"]

    calendar = service.get_championship_calendar(championship_id, season=1)
    existing_date = calendar[0]["race_date"]

    valid, message = service.validate_race_event(
        championship_id=championship_id,
        track_id=seed["track_ids"][0],
        race_date=existing_date,
        season=1,
    )

    assert valid is False
    assert "Date conflict" in (message or "")


@pytest.mark.integration
def test_race_lifecycle_transition_rules(seeded_championship):
    service = seeded_championship["service"]
    race_id = seeded_championship["race_ids"][0]

    success, error = service.update_race_lifecycle_status(race_id, "in-progress")
    assert success is True
    assert error is None

    success, error = service.update_race_lifecycle_status(race_id, "scheduled")
    assert success is False
    assert "Invalid transition" in (error or "")


@pytest.mark.integration
def test_recalculate_standings_orders_by_points_then_tiebreakers(seeded_championship):
    db = seeded_championship["db"]
    service = seeded_championship["service"]
    championship_id = seeded_championship["championship_id"]
    race_id = seeded_championship["race_ids"][0]

    driver_ids = seeded_championship["seed"]["driver_ids"][:3]
    team_ids = seeded_championship["seed"]["team_ids"]

    results = [
        RaceResult(
            id=0,
            race_id=race_id,
            driver_id=driver_id,
            team_id=team_ids[(position - 1) % len(team_ids)],
            position=position,
            points=service.calculate_points(
                position=position, discipline="SPRINT_RALLYCROSS"
            ),
            fastest_lap=(position == 1),
        )
        for position, driver_id in enumerate(driver_ids, start=1)
    ]
    persist_race_results(db, results)

    db.update_race_status(race_id, "completed")

    standings = service.recalculate_standings(championship_id=championship_id, season=1)

    assert len(standings) == 3
    assert standings[0].driver_id == driver_ids[0]
    assert (
        standings[0].total_points
        > standings[1].total_points
        > standings[2].total_points
    )
