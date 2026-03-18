"""Team management tests for UC-11 through UC-14."""

import pytest

from services.team_service import TeamService


@pytest.fixture()
def service(test_db):
    return TeamService(test_db)


def _seed_roster_and_staff(test_db, team_id: int) -> None:
    with test_db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO drivers (name, nationality, birth_date, speed, racecraft, consistency, current_team_id, salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("Driver One", "GB", "1998-01-01", 82.0, 79.0, 80.0, team_id, 1_500_000),
        )
        conn.execute(
            """
            INSERT INTO staff_members (name, role, rating, current_team_id)
            VALUES (?, ?, ?, ?)
            """,
            ("Chief Engineer", "ENGINEER", 84.0, team_id),
        )
        conn.commit()


def test_create_team_provisions_tier_assets_and_owner(service, test_db):
    result = service.create_team(
        name="Atlas GP",
        discipline="SINGLE_SEATER",
        nationality="IE",
        tier="TIER_1",
        team_principal="Alex Byrne",
        headquarters="Dublin",
        player_id="player-one",
    )

    assert result["initial_budget"] == service.TIER_BUDGETS["TIER_1"]
    assert result["staff_limit"] == service.TIER_STAFF_LIMITS["TIER_1"]
    assert result["driver_slots"] == service.DRIVER_SLOTS_PER_DISCIPLINE["SINGLE_SEATER"]
    assert test_db.get_player_team_id("player-one") == result["id"]


def test_get_team_details_returns_roster_staff_financials_and_stats(service, test_db):
    created = service.create_team(name="Nordic Works", discipline="ENDURANCE", tier="TIER_2")
    _seed_roster_and_staff(test_db, created["id"])

    details = service.get_team_details(created["id"])

    assert details is not None
    assert details["id"] == created["id"]
    assert len(details["drivers"]) == 1
    assert details["staff_count"] == 1
    assert "budget" in details and "available_budget" in details and "annual_income" in details
    assert "total_wins" in details and "operations_rating" in details


def test_get_player_team_marks_editable_for_owner(service):
    created = service.create_team(name="Pulse Racing", discipline="SINGLE_SEATER", player_id="owner-a")

    me = service.get_player_team("owner-a")

    assert me is not None
    assert me["id"] == created["id"]
    assert me["is_player_owned"] is True
    assert me["editable"] is True


def test_budget_constraint_rejects_over_allocation(service, test_db):
    created = service.create_team(name="Budget Team", discipline="DRAG_ACCELERATION", tier="TIER_3")
    team = test_db.get_team(created["id"])

    with pytest.raises(ValueError, match="Insufficient budget"):
        service.allocate_budget(created["id"], "facility_upgrade", team.budget + 1.0)


def test_permission_validation_blocks_non_owner_update(service):
    created = service.create_team(name="Guarded Team", discipline="SINGLE_SEATER", player_id="owner-real")

    with pytest.raises(ValueError, match="permission"):
        service.update_team(created["id"], {"team_principal": "Not Allowed"}, actor_id="intruder")


def test_optimistic_locking_rejects_stale_update(service):
    created = service.create_team(name="Lock Team", discipline="SINGLE_SEATER")

    first = service.update_team(
        created["id"],
        {"team_principal": "First", "expected_version": 1},
    )
    assert first["new_version"] == 2

    with pytest.raises(ValueError, match="conflict"):
        service.update_team(
            created["id"],
            {"team_principal": "Second", "expected_version": 1},
        )


def test_facility_upgrade_tracking_deducts_budget_and_persists(service, test_db):
    created = service.create_team(name="Upgrade Team", discipline="ENDURANCE", tier="TIER_2")
    before = test_db.get_team(created["id"]).budget

    service.update_team(created["id"], {"facility_upgrades": ["wind_tunnel"]})

    after_team = test_db.get_team(created["id"])
    details = service.get_team_details(created["id"])

    assert after_team.budget < before
    assert any(item["facility_name"] == "wind_tunnel" for item in details["facility_upgrades"])
