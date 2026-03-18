"""API-level team management tests for UC-11 through UC-14."""

from fastapi.testclient import TestClient

import simulation
from services.team_service import TeamService


def _client_with_test_service(test_db):
    simulation.team_service = TeamService(test_db)
    return TestClient(simulation.app), simulation.team_service


def test_get_teams_me_requires_auth_header(test_db):
    client, _ = _client_with_test_service(test_db)

    response = client.get("/teams/me")

    assert response.status_code == 401


def test_get_teams_me_returns_owned_team(test_db):
    client, service = _client_with_test_service(test_db)
    created = service.create_team(
        name="API Owned Team",
        discipline="SINGLE_SEATER",
        tier="TIER_2",
        player_id="api-owner",
    )

    response = client.get("/teams/me", headers={"X-Player-Id": "api-owner"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == created["id"]
    assert payload["editable"] is True
    assert payload["is_player_owned"] is True


def test_patch_team_blocks_non_owner(test_db):
    client, service = _client_with_test_service(test_db)
    created = service.create_team(
        name="API Guarded Team",
        discipline="SINGLE_SEATER",
        player_id="owner-a",
    )

    response = client.patch(
        f"/teams/{created['id']}",
        headers={"X-Player-Id": "owner-b"},
        json={"team_principal": "Unauthorized"},
    )

    assert response.status_code == 403


def test_patch_team_returns_conflict_for_stale_version(test_db):
    client, service = _client_with_test_service(test_db)
    created = service.create_team(name="API Lock Team", discipline="SINGLE_SEATER")

    ok = client.patch(
        f"/teams/{created['id']}",
        json={"team_principal": "First", "expected_version": 1},
    )
    assert ok.status_code == 200

    conflict = client.patch(
        f"/teams/{created['id']}",
        json={"team_principal": "Second", "expected_version": 1},
    )

    assert conflict.status_code == 409
