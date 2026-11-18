"""Leaving a Quick Championship race settles the round and returns to the window."""

from __future__ import annotations

import pytest

from momentum.database.models import RaceResult
from momentum.services.race_settlement import settle_championship_race, settle_race
from momentum.services.race_simulation_api import persist_race_results


@pytest.mark.unit
def test_settle_race_core_rules():
    log: list[str] = []
    done = lambda: log.append("completed")  # noqa: E731
    back = lambda: log.append("scheduled")  # noqa: E731
    assert settle_race("in-progress", True, done, back) == "completed"
    assert settle_race("in-progress", False, done, back) == "reopened"
    assert settle_race("scheduled", False, done, back) == "unchanged"
    assert settle_race("scheduled", True, done, back) == "completed"
    assert settle_race("completed", True, done, back) == "unchanged"
    assert settle_race(None, True, done, back) == "unchanged"
    assert log == ["completed", "scheduled", "completed"]


def _save_results(db, service, race_id, seeded):
    driver_ids = seeded["seed"]["driver_ids"][:3]
    team_ids = seeded["seed"]["team_ids"]
    results = [
        RaceResult(
            id=0,
            race_id=race_id,
            driver_id=driver_id,
            team_id=team_ids[(position - 1) % len(team_ids)],
            position=position,
            points=service.calculate_points(position=position, discipline="SPRINT_RALLYCROSS"),
            fastest_lap=(position == 1),
        )
        for position, driver_id in enumerate(driver_ids, start=1)
    ]
    persist_race_results(db, results)


@pytest.mark.integration
def test_abandoned_round_returns_to_scheduled_and_finished_round_completes(seeded_championship):
    db = seeded_championship["db"]
    service = seeded_championship["service"]
    race_id = seeded_championship["race_ids"][0]

    assert service.update_race_lifecycle_status(race_id, "in-progress") == (True, None)
    assert settle_championship_race(db, service, race_id) == "reopened"
    assert db.get_race(race_id).status == "scheduled"

    assert service.update_race_lifecycle_status(race_id, "in-progress") == (True, None)
    _save_results(db, service, race_id, seeded_championship)
    assert settle_championship_race(db, service, race_id) == "completed"
    assert db.get_race(race_id).status == "completed"
    assert settle_championship_race(db, service, race_id) == "unchanged"

    standings = service.recalculate_standings(seeded_championship["championship_id"], 1)
    assert standings and standings[0].total_points > 0


@pytest.mark.integration
def test_return_to_menu_after_a_championship_race_reopens_the_championship_window(
    seeded_championship, monkeypatch
):
    import momentum.database.database_manager as dm
    from momentum.gui import launcher as launcher_module

    db = seeded_championship["db"]
    service = seeded_championship["service"]
    championship_id = seeded_championship["championship_id"]
    race_id = seeded_championship["race_ids"][0]
    monkeypatch.setattr(dm, "DatabaseManager", lambda *a, **k: db)

    assert service.update_race_lifecycle_status(race_id, "in-progress") == (True, None)
    _save_results(db, service, race_id, seeded_championship)

    calls: list[str] = []

    class _Menu:
        def show_championship_page(self):
            calls.append("championship_page")
            return True

        def show(self):
            calls.append("main_menu")

    launcher = launcher_module.MomentumLauncher.__new__(launcher_module.MomentumLauncher)
    launcher.main_menu = _Menu()
    launcher.race_window = None
    launcher.race_config = {
        "mode": "championship",
        "championship_id": championship_id,
        "race_id": race_id,
    }
    launcher.return_to_menu()
    assert calls == ["championship_page"]
    assert db.get_race(race_id).status == "completed"
    assert launcher.race_config == {}
