"""Every change to a team's money is a recorded, sourced transaction."""

from __future__ import annotations

import pytest

from momentum.services.finance_service import (
    OWNER_FUNDING,
    SIGNING_BONUS,
    FinanceService,
    InsufficientFunds,
)
from momentum.services.team_service import TeamService


@pytest.mark.unit
def test_founding_a_team_posts_its_capital(test_db):
    created = TeamService(test_db).create_team(
        "Ledger Racing", discipline="SINGLE_SEATER", tier="TIER_1", team_principal="A. Owner"
    )
    team_id = int(created["id"])
    finance = FinanceService(test_db)
    team = test_db.get_team(team_id)
    statement = finance.statement(team_id)

    assert team.budget == TeamService.TIER_BUDGETS["TIER_1"]
    assert [row["category"] for row in statement] == [OWNER_FUNDING]
    assert statement[0]["source"].startswith("A. Owner")
    assert finance.ledger_balance(team_id) == team.budget
    assert finance.reconcile() == []


@pytest.mark.unit
def test_spending_is_signed_and_cannot_overdraw(test_db):
    created = TeamService(test_db).create_team("Thrifty GP", tier="TIER_5")
    team_id = int(created["id"])
    finance = FinanceService(test_db)
    opening = test_db.get_team(team_id).budget

    balance = finance.post(team_id, -250_000, SIGNING_BONUS, "Signing bonus", source="Thrifty GP")
    assert balance == pytest.approx(opening - 250_000)
    assert finance.ledger_balance(team_id) == pytest.approx(balance)

    with pytest.raises(InsufficientFunds):
        finance.post(team_id, -(balance + 1), SIGNING_BONUS, "Too much")
    assert test_db.get_team(team_id).budget == pytest.approx(balance)
    assert finance.reconcile() == []


@pytest.mark.unit
def test_reconcile_reports_a_balance_the_ledger_cannot_explain(test_db):
    created = TeamService(test_db).create_team("Mystery Money", tier="TIER_3")
    team_id = int(created["id"])
    with test_db.get_connection() as conn:
        conn.execute("UPDATE teams SET budget = budget + 1000000 WHERE id = ?", (team_id,))
        conn.commit()
    mismatches = FinanceService(test_db).reconcile()
    assert [m["team_id"] for m in mismatches] == [team_id]
    assert mismatches[0]["balance"] - mismatches[0]["ledger"] == pytest.approx(1_000_000)
