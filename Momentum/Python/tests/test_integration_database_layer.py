"""Integration tests for database manager CRUD and persistence."""

import pytest

from database.models import Driver


@pytest.mark.integration
def test_seeded_reference_data_counts(seeded_db):
    db = seeded_db["db"]

    assert len(db.list_drivers()) == 6
    assert len(db.list_teams()) == 3
    assert len(db.list_tracks()) == 3


@pytest.mark.integration
def test_update_track_surface_persists_to_database(seeded_db):
    db = seeded_db["db"]
    track_id = seeded_db["track_ids"][0]

    assert db.update_track_surface(track_id, "gravel") is True
    updated = db.get_track(track_id)

    assert updated is not None
    assert updated.surface == "gravel"


@pytest.mark.integration
def test_create_and_update_driver_round_trip(seeded_db):
    db = seeded_db["db"]

    new_driver_id = db.create_driver(
        Driver(
            id=0,
            name="Round Trip Driver",
            nationality="IRL",
            birth_date="2000-01-01",
            speed=72.0,
            racecraft=70.0,
            consistency=69.0,
            preferred_discipline="SINGLE_SEATER",
        )
    )

    created = db.get_driver(new_driver_id)
    assert created is not None
    assert created.name == "Round Trip Driver"

    created.name = "Updated Round Trip Driver"
    assert db.update_driver(created) is True

    updated = db.get_driver(new_driver_id)
    assert updated is not None
    assert updated.name == "Updated Round Trip Driver"


@pytest.mark.integration
def test_get_teams_by_discipline_supports_normalized_input(seeded_db):
    db = seeded_db["db"]

    teams_upper = db.get_teams_by_discipline("SINGLE_SEATER")
    teams_spaced = db.get_teams_by_discipline("single seater")

    assert len(teams_upper) == 3
    assert len(teams_spaced) == 3


@pytest.mark.integration
def test_database_stats_report_core_entities(seeded_db):
    db = seeded_db["db"]
    stats = db.get_database_stats()

    assert stats["drivers"] >= 6
    assert stats["teams"] >= 3
    assert stats["tracks"] >= 3
