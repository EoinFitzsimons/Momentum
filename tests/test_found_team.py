"""Founding a player team in a chosen league."""

from __future__ import annotations

import pytest

from momentum.database.database_manager import DatabaseManager
from momentum.database.models import Driver
from momentum.services.finance_service import OWNER_FUNDING, FinanceService
from momentum.services.team_service import TeamService
from momentum.services.tier_service import LEAGUE_SIZE


@pytest.fixture
def db(tmp_path):
    manager = DatabaseManager(str(tmp_path / "found.db"))
    manager.init_database()
    return manager


@pytest.mark.unit
def test_chosen_league_sets_the_founding_capital(db):
    service = TeamService(db)
    result = service.found_player_team(
        "Fitzsimons Racing", "SINGLE_SEATER", "IRL", "TIER_2", "Eoin Fitzsimons", "Naas"
    )
    team = db.get_team(int(result["id"]))
    assert team.tier == "TIER_2"
    assert team.budget == pytest.approx(service.TIER_BUDGETS["TIER_2"])
    rows = db.get_budget_transactions(int(result["id"]))
    assert [row["category"] for row in rows] == [OWNER_FUNDING]
    assert "Eoin Fitzsimons" in rows[0]["source"]
    assert FinanceService(db).reconcile() == []
    assert result["replaced_team"] is None


@pytest.mark.unit
def test_full_league_makes_room_by_dissolving_its_weakest_team(db):
    service = TeamService(db)
    for index in range(LEAGUE_SIZE):
        service.create_team(f"Incumbent {index:02d}", "SINGLE_SEATER", "GBR", "TIER_1")
    before = {t.id for t in db.get_teams_by_discipline("SINGLE_SEATER")}
    assert len(before) == LEAGUE_SIZE

    for index in range(3):
        db.create_driver(
            Driver(
                id=0,
                name=f"Free Agent {index + 1}",
                nationality="IRL",
                birth_date="1999-01-01",
                speed=60 + index,
                racecraft=60 + index,
                consistency=60 + index,
                preferred_discipline="SINGLE_SEATER",
                current_team_id=None,
            )
        )
    result = service.found_player_team("Newcomers", "SINGLE_SEATER", "GBR", "TIER_1")
    after = db.get_teams_by_discipline("SINGLE_SEATER")
    assert len(after) == LEAGUE_SIZE
    assert int(result["id"]) in {t.id for t in after}
    assert result["replaced_team"]["id"] in before
    assert result["replaced_team"]["id"] not in {t.id for t in after}
    assert FinanceService(db).reconcile() == []
    assert len(result["signed_drivers"]) >= 1
    assert len(db.get_drivers_by_team(int(result["id"]))) >= 1
