"""Use-case coverage tests mapping tests to UC-1..UC-29.

This file focuses on the supporting CRUD, hiring, progression, and
appearance flows that are not fully exercised by the existing integration
suite.
"""

from __future__ import annotations


import pytest
from faker import Faker

import database.database_extensions  # noqa: F401  # patches DatabaseManager
from database.database_manager import DatabaseManager
from database.models import Driver, Race, RaceResult, Track
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from scripts.seed_career_mode import generate_driver, generate_staff_member
from services.hiring_service import HiringService
from services.team_service import TeamService
from vehicles.appearance_integration import VehicleAppearanceManager
from vehicles.vehicle_appearance import create_team_livery


_FAKER = Faker()
_FAKER.seed_instance(42)


@pytest.mark.integration
def test_uc12_create_team_and_uc13_read_team_details(seeded_db):
    """UC-12 + UC-13: team creation and team profile retrieval."""
    db: DatabaseManager = seeded_db["db"]
    service = TeamService(db)

    created = service.create_team(
        name="Coverage Racing",
        discipline="SINGLE_SEATER",
        nationality="GBR",
        tier="TIER_2",
        team_principal="A. Principal",
        headquarters="Silverstone",
    )

    assert created["name"] == "Coverage Racing"
    assert created["driver_slots"] == 2

    team = db.get_team(created["id"])
    assert team is not None
    assert team.name == "Coverage Racing"

    profile = service.get_team_details(created["id"])
    assert profile is not None
    assert profile["name"] == "Coverage Racing"
    assert profile["staff_count"] == 0
    assert profile["driver_slots"] == 2


@pytest.mark.integration
def test_uc17_uc18_staff_hiring_flow(seeded_db):
    """UC-17 + UC-18: staff listing and staff contract signing."""
    db: DatabaseManager = seeded_db["db"]
    team_id = seeded_db["team_ids"][0]
    db_path = str(db.db_path)

    staff_name = generate_staff_member(_FAKER, "MECHANIC")
    assert staff_name is not None

    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO staff_members (name, role, rating)
            VALUES (?, ?, ?)
            """,
            (staff_name["name"], staff_name["role"], staff_name["rating"]),
        )
        assert cursor.lastrowid is not None
        staff_id = int(cursor.lastrowid)
        conn.commit()

    hiring = HiringService(db_path)

    staff_list, total = hiring.get_available_staff(role="MECHANIC", min_rating=0.0)
    assert total >= 1
    assert any(item["name"] == staff_name["name"] for item in staff_list)
    assert staff_list[0]["estimated_salary"] > 0

    success, message, details = hiring.sign_staff_contract(
        team_id=team_id,
        staff_id=staff_id,
        contract_length=2,
        salary=125_000.0,
        start_season=2026,
    )
    assert success is True
    assert "Successfully signed" in message
    assert details["team_id"] == team_id
    assert details["staff_id"] == staff_id

    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT current_team_id, annual_salary, contract_length FROM staff_members WHERE id = ?",
            (staff_id,),
        ).fetchone()

    assert row is not None
    assert int(row[0]) == team_id
    assert float(row[1]) == pytest.approx(125_000.0)
    assert int(row[2]) == 2


@pytest.mark.integration
def test_uc21_uc22_generation_helpers_produce_valid_entities(seeded_db):
    """UC-21 + UC-22: driver/staff generation helpers produce usable payloads."""
    db: DatabaseManager = seeded_db["db"]

    driver_payload = generate_driver(_FAKER, "IRL", "SINGLE_SEATER", "en_GB")
    assert driver_payload is not None
    new_driver_id = db.create_driver(
        Driver(
            id=0,
            name=driver_payload["name"],
            nationality=driver_payload["nationality"],
            birth_date=driver_payload["birth_date"],
            speed=driver_payload["speed"],
            racecraft=driver_payload["racecraft"],
            consistency=driver_payload["consistency"],
            preferred_discipline=driver_payload["preferred_discipline"],
        )
    )
    assert new_driver_id is not None
    created_driver = db.get_driver(int(new_driver_id))
    assert created_driver is not None
    assert created_driver.name == driver_payload["name"]
    assert created_driver.preferred_discipline == "SINGLE_SEATER"

    staff_payload = generate_staff_member(_FAKER, "STRATEGIST")
    assert staff_payload is not None
    with db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO staff_members (name, role, rating)
            VALUES (?, ?, ?)
            """,
            (staff_payload["name"], staff_payload["role"], staff_payload["rating"]),
        )
        conn.commit()

    hiring = HiringService(str(db.db_path))
    staff_list, total = hiring.get_available_staff(role="STRATEGIST")
    assert total >= 1
    assert any(item["name"] == staff_payload["name"] for item in staff_list)


@pytest.mark.integration
def test_uc23_delete_championship_cascades_races_and_results(seeded_championship):
    """UC-23: deleting a championship removes its dependent races/results."""
    db: DatabaseManager = seeded_championship["db"]
    championship_id = seeded_championship["championship_id"]
    race_id = seeded_championship["race_ids"][0]
    seed = seeded_championship["seed"]

    result = RaceResult(
        id=0,
        race_id=race_id,
        driver_id=seed["driver_ids"][0],
        team_id=seed["team_ids"][0],
        position=1,
        fastest_lap=True,
        points=25,
    )
    db.create_race_result(result)
    assert len(db.get_race_results(race_id)) == 1

    assert db.delete_championship(championship_id) is True
    assert db.get_championship(championship_id) is None
    assert db.get_race_results(race_id) == []


@pytest.mark.integration
def test_uc24_uc25_create_and_update_track(seeded_db):
    """UC-24 + UC-25: create a custom track and update its characteristics."""
    db: DatabaseManager = seeded_db["db"]

    track_id = db.create_track(
        Track(
            id=0,
            name="Coverage Park",
            country="GBR",
            primary_discipline="SINGLE_SEATER",
            length_km=4.2,
            turns=14,
            avg_speed_kmh=182.0,
            longest_straight_m=790.0,
            tightest_corner_radius_m=32.0,
            left_turns=7,
            right_turns=7,
            drs_zones=2,
            surface="asphalt",
        )
    )
    assert track_id is not None

    created = db.get_track(int(track_id))
    assert created is not None
    assert created.name == "Coverage Park"
    assert created.surface == "asphalt"

    assert db.update_track_surface(int(track_id), "gravel") is True
    updated = db.get_track(int(track_id))
    assert updated is not None
    assert updated.surface == "gravel"


@pytest.mark.integration
def test_uc26_delete_track_removes_dependent_races_and_results(seeded_championship):
    """UC-26: deleting a track removes dependent races and results."""
    db: DatabaseManager = seeded_championship["db"]
    championship_id = seeded_championship["championship_id"]
    track_id = db.create_track(
        Track(
            id=0,
            name="Delete Me Circuit",
            country="GBR",
            primary_discipline="SINGLE_SEATER",
            length_km=3.9,
            surface="asphalt",
        )
    )
    assert track_id is not None

    race_id = db.create_race(
        Race(
            id=0,
            championship_id=championship_id,
            track_id=int(track_id),
            season=1,
            round_number=99,
            race_date="2026-06-01",
            weather_conditions="clear",
            laps=3,
            status="scheduled",
        )
    )
    assert race_id is not None

    db.create_race_result(
        RaceResult(
            id=0,
            race_id=int(race_id),
            driver_id=seeded_championship["seed"]["driver_ids"][0],
            team_id=seeded_championship["seed"]["team_ids"][0],
            position=1,
            fastest_lap=False,
            points=15,
        )
    )

    assert db._delete_track(int(track_id)) is True
    assert db.get_track(int(track_id)) is None
    assert db.get_race(int(race_id)) is None
    assert db.get_race_results(int(race_id)) == []


@pytest.mark.integration
def test_uc27_staff_performance_effects_feed_realtime_engine(seeded_db):
    """UC-27: staff roster is converted into positive realtime performance effects."""
    db: DatabaseManager = seeded_db["db"]
    team = db.get_team(seeded_db["team_ids"][0])
    assert team is not None

    staff_rows = [
        ("Team Boss", "TEAM_PRINCIPAL", 90.0),
        ("Strategist One", "STRATEGIST", 84.0),
        ("Mechanic One", "MECHANIC", 82.0),
        ("Engineer One", "TECHNICAL_DIRECTOR", 88.0),
    ]
    with db.get_connection() as conn:
        for name, role, rating in staff_rows:
            conn.execute(
                """
                INSERT INTO staff_members (name, role, rating, current_team_id)
                VALUES (?, ?, ?, ?)
                """,
                (name, role, rating, team.id),
            )
        conn.commit()

    engine = RealtimeRaceEngine(seed=7, db=db)
    engine._hydrate_staff_effects_for_teams({team.id: team})

    assert engine._get_team_staff_effect(team, "operations") > 0.0
    assert engine._get_team_staff_effect(team, "strategy") > 0.0
    assert engine._get_team_staff_effect(team, "pitstop") > 0.0
    assert engine._get_team_staff_effect(team, "reliability") > 0.0


@pytest.mark.integration
def test_uc28_uc29_vehicle_appearance_and_branding_helpers(seeded_db):
    """UC-28 + UC-29: driver and team visual identity helpers return stable assets."""
    db: DatabaseManager = seeded_db["db"]
    driver = db.get_driver(seeded_db["driver_ids"][0])
    team = db.get_team(seeded_db["team_ids"][0])
    assert driver is not None
    assert team is not None

    appearance_manager = VehicleAppearanceManager()
    config = appearance_manager.create_vehicle_for_driver(driver, team)

    assert config.driver_number == driver.id
    assert appearance_manager.get_vehicle_type(driver.id).name
    assert appearance_manager.get_livery(driver.id) is not None

    team_livery = create_team_livery(team.id, team.name, driver.id)
    assert team_livery.team_name == team.name
    assert team_livery.driver_number == driver.id
