"""Team money, with every change recorded.

A team's budget is never set directly. Each change is posted as a signed
transaction (income positive, spending negative) with a category, a short
description and the source the money came from, and the balance moves in the
same database transaction. The ledger therefore always sums to the balance,
and ``reconcile()`` says so for every team.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from database.database_manager import DatabaseManager

# Categories. Income
OWNER_FUNDING = "owner_funding"
RACE_INCOME = "race_income"
SPONSOR_INCOME = "sponsor_income"
CAR_UPGRADE_REFUND = "car_upgrade_refund"
MARKETING_REVENUE = "marketing_revenue"
# Spending
CAR_UPGRADE = "car_upgrade"
FACILITY_UPGRADE = "facility_upgrade"
SIGNING_BONUS = "signing_bonus"
CONTRACT_BUYOUT = "contract_buyout"
MARKETING = "marketing"
DRIVER_DEVELOPMENT = "driver_development"
STAFF_DEVELOPMENT = "staff_development"
# Anything legacy code still posts without a better name
ADJUSTMENT = "adjustment"

RECONCILE_TOLERANCE = 0.005


class InsufficientFunds(ValueError):
    """Raised when a posting would take a team's balance below zero."""


def ensure_ledger_schema(conn: sqlite3.Connection) -> None:
    """Add the ``source`` column to older databases."""
    columns = {row[1] for row in conn.execute("PRAGMA table_info(team_budget_transactions)")}
    if columns and "source" not in columns:
        conn.execute("ALTER TABLE team_budget_transactions ADD COLUMN source TEXT DEFAULT ''")


def post_with(
    conn: sqlite3.Connection,
    team_id: int,
    amount: float,
    category: str,
    description: str = "",
    source: str = "",
) -> float:
    """Record one transaction and move the balance inside the caller's transaction."""
    ensure_ledger_schema(conn)
    amount = round(float(amount), 2)
    conn.execute(
        "UPDATE teams SET budget = budget + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (amount, int(team_id)),
    )
    conn.execute(
        """
        INSERT INTO team_budget_transactions (team_id, category, amount, description, source)
        VALUES (?, ?, ?, ?, ?)
        """,
        (int(team_id), str(category), amount, str(description or ""), str(source or "")),
    )
    row = conn.execute("SELECT budget FROM teams WHERE id = ?", (int(team_id),)).fetchone()
    return float(row[0]) if row else 0.0


class FinanceService:
    """Posts money to and from teams and checks the books balance."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def post(
        self,
        team_id: int,
        amount: float,
        category: str,
        description: str = "",
        source: str = "",
        allow_overdraft: bool = False,
    ) -> float:
        """Post a signed amount and return the new balance.

        Spending that the team cannot afford raises ``InsufficientFunds``
        unless ``allow_overdraft`` is set.
        """
        with self.db.get_connection() as conn:
            if amount < 0 and not allow_overdraft:
                row = conn.execute(
                    "SELECT budget FROM teams WHERE id = ?", (int(team_id),)
                ).fetchone()
                balance = float(row[0]) if row else 0.0
                if balance + amount < -RECONCILE_TOLERANCE:
                    raise InsufficientFunds(
                        f"Team {team_id} has EUR {balance:,.0f}, cannot spend EUR {-amount:,.0f}"
                    )
            new_balance = post_with(conn, team_id, amount, category, description, source)
            conn.commit()
        return new_balance

    def ledger_balance(self, team_id: int) -> float:
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM team_budget_transactions WHERE team_id = ?",
                (int(team_id),),
            ).fetchone()
        return float(row[0] or 0.0)

    def statement(self, team_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Most recent transactions first."""
        sql = (
            "SELECT id, category, amount, description, source, created_at "
            "FROM team_budget_transactions WHERE team_id = ? ORDER BY id DESC"
        )
        params: tuple = (int(team_id),)
        if limit is not None:
            sql += " LIMIT ?"
            params = (int(team_id), int(limit))
        with self.db.get_connection() as conn:
            ensure_ledger_schema(conn)
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def reconcile(self) -> List[Dict[str, float]]:
        """Teams whose balance differs from the sum of their transactions."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT t.id AS team_id, t.name AS name, t.budget AS balance,
                       COALESCE((SELECT SUM(x.amount) FROM team_budget_transactions x
                                 WHERE x.team_id = t.id), 0) AS ledger
                FROM teams t
                """
            ).fetchall()
        return [
            {
                "team_id": int(row["team_id"]),
                "name": row["name"],
                "balance": float(row["balance"] or 0.0),
                "ledger": float(row["ledger"] or 0.0),
            }
            for row in rows
            if abs(float(row["balance"] or 0.0) - float(row["ledger"] or 0.0)) > RECONCILE_TOLERANCE
        ]


__all__ = [
    "ADJUSTMENT",
    "CAR_UPGRADE",
    "CAR_UPGRADE_REFUND",
    "CONTRACT_BUYOUT",
    "DRIVER_DEVELOPMENT",
    "FACILITY_UPGRADE",
    "FinanceService",
    "InsufficientFunds",
    "MARKETING",
    "MARKETING_REVENUE",
    "OWNER_FUNDING",
    "RACE_INCOME",
    "SIGNING_BONUS",
    "SPONSOR_INCOME",
    "STAFF_DEVELOPMENT",
    "ensure_ledger_schema",
    "post_with",
]
