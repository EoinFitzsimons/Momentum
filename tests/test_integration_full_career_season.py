"""Integration test for the repeatable full career season runner."""

from __future__ import annotations

import pytest


def _seed_single_seater_roster(db):
    import importlib

    career_seed = importlib.import_module("momentum.seed.world")

    disciplines = ["SINGLE_SEATER"]
    career_seed.seed_teams(db, 2, disciplines)
    career_seed.seed_drivers(db, 12, disciplines)
    career_seed.assign_driver_contracts(db, disciplines)


@pytest.mark.integration
def test_full_career_season_runner_completes_seeded_season(seeded_db):
    """Run a small but real season pipeline against a seeded temp database."""
    season_runner = pytest.importorskip("tools.run_full_career_season")

    _seed_single_seater_roster(seeded_db["db"])

    outcome = season_runner.run_season(
        discipline="SINGLE_SEATER",
        race_count=2,
        grid_size=3,
        laps_per_race=1,
        season_year=2026,
        db=seeded_db["db"],
    )

    assert outcome["scheduled_races"] == 2
    assert outcome["completed_races"] == 2
    assert outcome["grid_size"] == 3
    assert outcome["discipline"] == "SINGLE_SEATER"
    assert len(outcome["standings"]) == 3
    assert outcome["standings"][0].position == 1
    assert outcome["standings"][0].total_points >= outcome["standings"][1].total_points
