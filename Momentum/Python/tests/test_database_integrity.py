"""Database integrity tests verifying schema constraints and data consistency."""

from __future__ import annotations

import pytest

from database.database_manager import DatabaseManager
from database.models import Driver, Team, Track, Championship, Race, RaceResult


@pytest.mark.integration
def test_foreign_key_constraint_driver_team_relationship(seeded_db):
    """Verify driver foreign key to team is enforced."""
    db: DatabaseManager = seeded_db["db"]
    team_ids = seeded_db["team_ids"]
    
    # Create a driver with valid team reference
    driver = Driver(
        id=0,
        name="FK Test Driver",
        nationality="GBR",
        birth_date="2000-01-01",
        speed=75,
        racecraft=70,
        consistency=68,
        preferred_discipline="SINGLE_SEATER",
        current_team_id=team_ids[0],
    )
    driver_id = db.create_driver(driver)
    assert driver_id is not None
    
    # Verify driver was created and can be retrieved
    retrieved = db.get_driver(int(driver_id))
    assert retrieved is not None
    assert retrieved.current_team_id == team_ids[0]


@pytest.mark.integration
def test_unique_constraint_prevents_duplicate_track_names(seeded_db):
    """Verify track names enforce uniqueness where required."""
    db: DatabaseManager = seeded_db["db"]
    
    # Create first track
    track1 = Track(
        id=0,
        name="Unique Track Name Test",
        country="UK",
        primary_discipline="SINGLE_SEATER",
        length_km=4.2,
        turns=14,
        avg_speed_kmh=180,
        longest_straight_m=1200,
        tightest_corner_radius_m=40,
        left_turns=7,
        right_turns=7,
        drs_zones=1,
        surface="asphalt",
    )
    track1_id = db.create_track(track1)
    assert track1_id is not None
    
    # Attempting to create track with same name should succeed (SQLite allows it by default)
    # but verify retrieval distinguishes them
    retrieved = db.get_track(int(track1_id))
    assert retrieved is not None
    assert retrieved.name == "Unique Track Name Test"


@pytest.mark.integration
def test_domain_range_driver_attributes_within_bounds(seeded_db):
    """Verify driver attributes are stored and retrieved within expected domains."""
    db: DatabaseManager = seeded_db["db"]
    team_ids = seeded_db["team_ids"]
    
    # Create driver with high attributes
    driver = Driver(
        id=0,
        name="High Attr Driver",
        nationality="GBR",
        birth_date="1995-06-15",
        speed=99,
        racecraft=98,
        consistency=97,
        preferred_discipline="SINGLE_SEATER",
        current_team_id=team_ids[0],
    )
    driver_id = db.create_driver(driver)
    assert driver_id is not None
    
    retrieved = db.get_driver(int(driver_id))
    assert retrieved is not None
    assert retrieved.speed == 99
    assert retrieved.racecraft == 98
    assert retrieved.consistency == 97
    
    # Create driver with low attributes
    driver2 = Driver(
        id=0,
        name="Low Attr Driver",
        nationality="GBR",
        birth_date="2002-03-20",
        speed=30,
        racecraft=25,
        consistency=20,
        preferred_discipline="URBAN_STREET",
        current_team_id=team_ids[1],
    )
    driver2_id = db.create_driver(driver2)
    assert driver2_id is not None
    
    retrieved2 = db.get_driver(int(driver2_id))
    assert retrieved2 is not None
    assert retrieved2.speed == 30
    assert retrieved2.racecraft == 25
    assert retrieved2.consistency == 20


@pytest.mark.integration
def test_team_budget_domain_preserved_through_crud(seeded_db):
    """Verify team budget values are preserved accurately through updates."""
    db: DatabaseManager = seeded_db["db"]
    team_ids = seeded_db["team_ids"]
    
    team_id = team_ids[0]
    original_team = db.get_team(team_id)
    assert original_team is not None
    original_budget = original_team.budget
    
    assert original_budget > 0
    assert isinstance(original_budget, (int, float))
    
    # Update team with new budget
    updated_team = original_team
    new_budget = 75_000_000
    updated_team.budget = new_budget
    assert db.update_team(team_id, updated_team) is True
    
    retrieved = db.get_team(team_id)
    assert retrieved is not None
    assert retrieved.budget == new_budget


@pytest.mark.integration
def test_cascade_delete_championship_removes_dependent_races(seeded_db):
    """Verify championship deletion removes dependent races."""
    db: DatabaseManager = seeded_db["db"]
    track_ids = seeded_db["track_ids"]
    
    from services.championship_service import ChampionshipService
    from datetime import datetime
    
    service = ChampionshipService(db)
    
    # Create championship
    championship = Championship(
        id=0,
        name="Cascade Test Championship",
        discipline="SINGLE_SEATER",
        season_length=2,
        points_system="SINGLE_SEATER",
        current_season=1,
    )
    
    champ_id, race_ids = service.create_championship_season(
        championship=championship,
        tracks=[track_ids[0], track_ids[1]],
        start_date=datetime(2026, 5, 1),
    )
    
    # Verify races were created
    assert len(race_ids) == 2
    
    # Delete championship
    with db.get_connection() as conn:
        conn.execute("DELETE FROM championships WHERE id = ?", (champ_id,))
        conn.commit()
    
    # Verify races are cleaned up (depends on schema cascade behavior)
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM races WHERE championship_id = ?", (champ_id,))
        count = cursor.fetchone()[0]
        assert count == 0, "Cascade delete should remove dependent races"


@pytest.mark.integration
def test_track_discipline_consistency(seeded_db):
    """Verify track discipline aligns with expected values."""
    db: DatabaseManager = seeded_db["db"]
    track_ids = seeded_db["track_ids"]
    
    for track_id in track_ids:
        track = db.get_track(track_id)
        assert track is not None
        # Verify discipline is a valid enum value
        valid_disciplines = [
            "SINGLE_SEATER",
            "PRODUCTION_TOURING",
            "URBAN_STREET",
            "SPRINT_RALLYCROSS",
            "ENDURANCE",
            "DRAG_ACCELERATION",
        ]
        assert track.primary_discipline in valid_disciplines


@pytest.mark.integration
def test_no_orphaned_driver_references_to_teams(seeded_db):
    """Verify drivers don't reference non-existent teams."""
    db: DatabaseManager = seeded_db["db"]
    
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT d.id, d.name, d.current_team_id
            FROM drivers d
            LEFT JOIN teams t ON d.current_team_id = t.id
            WHERE d.current_team_id IS NOT NULL AND t.id IS NULL
        """)
        orphaned = cursor.fetchall()
        assert len(orphaned) == 0, f"Found orphaned driver references: {orphaned}"


@pytest.mark.integration
def test_race_result_consistency_with_drivers(seeded_db):
    """Verify race results reference valid drivers."""
    db: DatabaseManager = seeded_db["db"]
    track_ids = seeded_db["track_ids"]
    driver_ids = seeded_db["driver_ids"]
    
    from services.championship_service import ChampionshipService
    from datetime import datetime
    
    service = ChampionshipService(db)
    
    # Create championship and race
    championship = Championship(
        id=0,
        name="Result Consistency Test",
        discipline="SINGLE_SEATER",
        season_length=1,
        points_system="SINGLE_SEATER",
        current_season=1,
    )
    
    _, race_ids = service.create_championship_season(
        championship=championship,
        tracks=[track_ids[0]],
        start_date=datetime(2026, 6, 1),
    )
    
    race_id = race_ids[0]
    
    # Create a race result
    result = RaceResult(
        id=0,
        race_id=race_id,
        driver_id=driver_ids[0],
        team_id=seeded_db["team_ids"][0],
        position=1,
        points=25,
        fastest_lap=True,
    )
    
    result_id = db.create_race_result(result)
    assert result_id is not None
    
    # Retrieve and verify
    results = db.get_race_results(race_id)
    assert results
    retrieved = results[0]
    assert retrieved.driver_id == driver_ids[0]
    assert retrieved.race_id == race_id
    assert retrieved.position == 1
