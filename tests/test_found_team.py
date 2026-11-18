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


@pytest.mark.unit
def test_founding_in_a_full_league_needs_no_prior_service_imports(tmp_path):
    """Regression: the GUI reaches ``TeamService`` before any hiring or
    progression service has been imported, so the personnel operations must
    be real ``DatabaseManager`` methods rather than runtime patches."""
    import subprocess
    import sys
    import textwrap

    script = textwrap.dedent(
        f"""
        import json
        from momentum.database.database_manager import DatabaseManager
        from momentum.services.team_service import TeamService
        from momentum.services.tier_service import LEAGUE_SIZE

        db = DatabaseManager({str(tmp_path / 'fresh.db')!r})
        db.init_database()
        assert "release_driver" in DatabaseManager.__dict__ or any(
            "release_driver" in base.__dict__ for base in DatabaseManager.__mro__
        )
        service = TeamService(db)
        for index in range(LEAGUE_SIZE):
            service.create_team(f"Incumbent {{index:02d}}", "SINGLE_SEATER", "GBR", "TIER_1")
        result = service.found_player_team(
            "Fresh Import Racing", "SINGLE_SEATER", "IRL", "TIER_1", "Eoin", "Naas"
        )
        replaced = result["replaced_team"]["id"]
        released = [d.id for d in db.get_drivers_by_team(replaced)]
        free_agents = {{d.id for d in db.get_available_drivers("SINGLE_SEATER")[0]}}
        rows = db.get_budget_transactions(int(result["id"]))
        print(json.dumps({{
            "released_still_on_team": released,
            "replaced_left_league": replaced not in {{
                t.id for t in db.get_teams_by_discipline("SINGLE_SEATER")
            }},
            "ledger": [(r["category"], r["source"]) for r in rows],
            "free_agents": len(free_agents),
        }}))
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=120
    )
    assert completed.returncode == 0, completed.stderr
    import json

    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    assert payload["released_still_on_team"] == []
    assert payload["replaced_left_league"] is True
    assert payload["ledger"][0][0] == OWNER_FUNDING
    assert "Eoin" in payload["ledger"][0][1]
