"""Integration tests for FastAPI endpoint contracts."""

import pytest


@pytest.mark.integration
def test_health_endpoint_returns_healthy_and_stats(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["database"] == "connected"
    assert "stats" in payload


@pytest.mark.integration
def test_drivers_endpoint_returns_contract_envelope(api_client):
    response = api_client.get("/drivers", params={"limit": 2})

    assert response.status_code == 200
    payload = response.json()

    assert set(payload.keys()) == {"drivers", "count", "total"}
    assert payload["count"] == 2
    assert len(payload["drivers"]) == 2


@pytest.mark.integration
def test_drivers_endpoint_discipline_filter_can_return_empty_set(api_client):
    response = api_client.get("/drivers", params={"discipline": "NOT_REAL"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["drivers"] == []
    assert payload["count"] == 0


@pytest.mark.integration
def test_drivers_endpoint_enforces_limit_validation(api_client):
    response = api_client.get("/drivers", params={"limit": 2001})
    assert response.status_code == 422


@pytest.mark.integration
def test_teams_me_requires_player_header(api_client):
    response = api_client.get("/teams/me")

    assert response.status_code == 401
    assert "Missing X-Player-Id header" in response.json()["detail"]


@pytest.mark.integration
def test_teams_endpoint_returns_count_and_list(api_client):
    response = api_client.get("/teams", params={"discipline": "SINGLE_SEATER"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 3
    assert len(payload["teams"]) == 3
