"""API tests for UC-15 to UC-19 hiring, contracts, and progression flows."""

from datetime import datetime

from fastapi.testclient import TestClient

import simulation
from services.hiring_service import HiringService
from services.progression_service import ProgressionService


def _client_with_test_services(test_db):
    simulation.hiring_service = HiringService(test_db.db_path)
    simulation.progression_service = ProgressionService(test_db.db_path)
    return TestClient(simulation.app)


def _seed_hiring_data(test_db):
    with test_db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO teams (name, nationality, discipline, tier, budget, operations_rating)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("Cap Team", "GBR", "SINGLE_SEATER", "TIER_1", 120_000_000.0, 80.0),
        )
        team_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        for idx in range(1, 6):
            conn.execute(
                """
                INSERT INTO drivers (
                    name, nationality, birth_date, speed, racecraft, consistency,
                    preferred_discipline, career_phase, current_team_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'active', NULL)
                """,
                (
                    f"Market Driver {idx}",
                    "GBR",
                    f"199{idx}-01-01",
                    50.0 + idx,
                    52.0 + idx,
                    48.0 + idx,
                    "SINGLE_SEATER",
                ),
            )

        for idx in range(1, 6):
            conn.execute(
                """
                INSERT INTO staff_members (name, role, rating, current_team_id)
                VALUES (?, ?, ?, NULL)
                """,
                (f"Staff {idx}", "RACE_ENGINEER", 55.0 + idx),
            )

        conn.commit()

    return team_id


def test_available_market_endpoints_support_filters_pagination_and_sorting(test_db):
    client = _client_with_test_services(test_db)
    _seed_hiring_data(test_db)

    drivers_resp = client.get(
        "/drivers/available",
        params={
            "discipline": "SINGLE_SEATER",
            "page": 1,
            "page_size": 2,
            "sort_by": "name",
            "sort_order": "asc",
        },
    )

    assert drivers_resp.status_code == 200
    drivers_payload = drivers_resp.json()
    assert drivers_payload["count"] == 2
    assert drivers_payload["total_pages"] >= 3
    returned_names = [d["name"] for d in drivers_payload["drivers"]]
    assert returned_names == sorted(returned_names)

    staff_resp = client.get(
        "/staff/available",
        params={"role": "RACE_ENGINEER", "page": 1, "page_size": 3, "sort_by": "rating"},
    )

    assert staff_resp.status_code == 200
    staff_payload = staff_resp.json()
    assert staff_payload["count"] == 3
    ratings = [s["rating"] for s in staff_payload["staff"]]
    assert ratings == sorted(ratings, reverse=True)


def test_contract_endpoints_create_contracts_with_season_tracking(test_db):
    client = _client_with_test_services(test_db)
    team_id = _seed_hiring_data(test_db)

    available_driver = client.get("/drivers/available", params={"page_size": 1}).json()["drivers"][0]
    driver_resp = client.post(
        "/contracts/driver",
        json={
            "team_id": team_id,
            "driver_id": available_driver["id"],
            "contract_length": 2,
            "salary": 3_000_000.0,
            "performance_bonus": 100_000.0,
            "start_season": 2026,
        },
    )

    assert driver_resp.status_code == 200
    driver_payload = driver_resp.json()
    assert driver_payload["contract_start_season"] == 2026
    assert driver_payload["contract_end_season"] == 2027

    available_staff = client.get("/staff/available", params={"page_size": 1}).json()["staff"][0]
    staff_resp = client.post(
        "/contracts/staff",
        json={
            "team_id": team_id,
            "staff_id": available_staff["id"],
            "contract_length": 3,
            "salary": 500_000.0,
            "start_season": 2026,
        },
    )

    assert staff_resp.status_code == 200
    staff_payload = staff_resp.json()
    assert staff_payload["contract_start_season"] == 2026
    assert staff_payload["contract_end_season"] == 2028


def test_salary_cap_validation_blocks_driver_and_staff_contracts(test_db):
    client = _client_with_test_services(test_db)
    team_id = _seed_hiring_data(test_db)

    # Oversized driver deal should exceed cap immediately.
    driver_id = client.get("/drivers/available", params={"page_size": 1}).json()["drivers"][0]["id"]
    too_big_driver = client.post(
        "/contracts/driver",
        json={
            "team_id": team_id,
            "driver_id": driver_id,
            "contract_length": 1,
            "salary": 200_000_000.0,
        },
    )
    assert too_big_driver.status_code == 400

    # Fill most of cap with one valid driver, then reject staff due to cap.
    ok_driver = client.post(
        "/contracts/driver",
        json={
            "team_id": team_id,
            "driver_id": driver_id,
            "contract_length": 1,
            "salary": 115_000_000.0,
            "start_season": 2026,
        },
    )
    assert ok_driver.status_code == 200

    staff_id = client.get("/staff/available", params={"page_size": 1}).json()["staff"][0]["id"]
    too_big_staff = client.post(
        "/contracts/staff",
        json={
            "team_id": team_id,
            "staff_id": staff_id,
            "contract_length": 1,
            "salary": 20_000_000.0,
            "start_season": 2026,
        },
    )
    assert too_big_staff.status_code == 400


def test_progression_retires_recycles_and_expires_contracts(test_db):
    client = _client_with_test_services(test_db)

    with test_db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO teams (name, nationality, discipline, tier, budget, operations_rating)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("Lifecycle Team", "FRA", "SINGLE_SEATER", "TIER_1", 100_000_000.0, 80.0),
        )
        team_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Driver guaranteed to retire (age 46+) and recycle.
        conn.execute(
            """
            INSERT INTO drivers (
                name, nationality, birth_date, speed, racecraft, consistency,
                preferred_discipline, career_phase, current_team_id, salary,
                contract_length, contract_start_season, contract_end_season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?)
            """,
            (
                "Retire Me",
                "ESP",
                "1979-01-01",
                65.0,
                65.0,
                65.0,
                "SINGLE_SEATER",
                team_id,
                2_000_000.0,
                1,
                2025,
                2025,
            ),
        )

        # Active contract that should expire entering season 2026.
        conn.execute(
            """
            INSERT INTO drivers (
                name, nationality, birth_date, speed, racecraft, consistency,
                preferred_discipline, career_phase, current_team_id, salary,
                contract_length, contract_start_season, contract_end_season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?)
            """,
            (
                "Expire Contract",
                "DEU",
                "1995-01-01",
                70.0,
                70.0,
                70.0,
                "SINGLE_SEATER",
                team_id,
                1_500_000.0,
                1,
                2025,
                2025,
            ),
        )

        conn.execute(
            """
            INSERT INTO staff_members (
                name, role, rating, current_team_id, annual_salary,
                contract_length, contract_start_season, contract_end_season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("Expire Staff", "RACE_ENGINEER", 80.0, team_id, 300_000.0, 1, 2025, 2025),
        )

        conn.commit()

    resp = client.post("/progression/season", json={"season": 2026})

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["drivers_retired"] >= 1
    assert payload["drivers_recycled"] >= 1
    assert payload["summary"]["contracts_expired_drivers"] >= 1
    assert payload["summary"]["contracts_expired_staff"] >= 1

    with test_db.get_connection() as conn:
        released_driver = conn.execute(
            "SELECT current_team_id FROM drivers WHERE name = ?",
            ("Expire Contract",),
        ).fetchone()
        released_staff = conn.execute(
            "SELECT current_team_id FROM staff_members WHERE name = ?",
            ("Expire Staff",),
        ).fetchone()

    assert released_driver and released_driver["current_team_id"] is None
    assert released_staff and released_staff["current_team_id"] is None
