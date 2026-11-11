"""Car upgrades: where a team's budget turns into pace.

Budget is earned from race results and sponsors and spent on upgrade
areas. Upgrade levels (together with operations rating and staff) are
what the race engines read for team performance; tier and raw budget are
never read for pace.
"""

from __future__ import annotations

import random
from typing import Any, Dict, Iterable, List, Optional

from momentum.services.tier_service import TIERS, normalise_tier, tier_scale
from momentum.services.finance_service import RACE_INCOME, CAR_UPGRADE, post_with

UPGRADE_AREAS: tuple[str, ...] = (
    "power",
    "aero",
    "handling",
    "reliability",
    "operations",
)

UPGRADE_AREA_LABELS: Dict[str, str] = {
    "power": "Power Unit",
    "aero": "Aerodynamics",
    "handling": "Chassis & Handling",
    "reliability": "Reliability",
    "operations": "Race Operations",
}

MAX_UPGRADE_LEVEL = 10
COST_GROWTH_PER_LEVEL = 1.35

# Level-0 -> level-1 cost in EUR for a SINGLE_SEATER-sized budget.
BASE_UPGRADE_COST: Dict[str, float] = {
    "power": 2_500_000.0,
    "aero": 2_200_000.0,
    "handling": 2_000_000.0,
    "reliability": 1_800_000.0,
    "operations": 1_500_000.0,
}

# Weight of each area in the car performance rating.
PERFORMANCE_WEIGHTS: Dict[str, float] = {
    "power": 0.32,
    "aero": 0.28,
    "handling": 0.25,
    "operations": 0.15,
}

# Disciplines run on very different money; costs and payouts scale with it.
DISCIPLINE_MONEY_SCALE: Dict[str, float] = {
    "SINGLE_SEATER": 1.00,
    "ENDURANCE": 0.46,
    "PRODUCTION_TOURING": 0.38,
    "URBAN_STREET": 0.27,
    "SPRINT_RALLYCROSS": 0.23,
    "DRAG_ACCELERATION": 0.19,
}

# Prize money per finishing position (EUR, Tier 1, SINGLE_SEATER scale).
RACE_PRIZE_TABLE: tuple[float, ...] = (
    1_200_000.0,
    900_000.0,
    700_000.0,
    550_000.0,
    450_000.0,
    380_000.0,
    320_000.0,
    270_000.0,
    230_000.0,
    200_000.0,
)
RACE_PRIZE_FLOOR = 150_000.0

# Sponsor money paid for every race entered, by league.
SPONSOR_STIPEND_PER_RACE: Dict[str, float] = {
    tier: tier_scale(tier, 400_000.0, 100_000.0) for tier in TIERS
}
TIER_PRIZE_SCALE: Dict[str, float] = {
    tier: round(tier_scale(tier, 1.0, 0.2), 3) for tier in TIERS
}

RACE_INCOME_CATEGORY = RACE_INCOME
UPGRADE_CATEGORY = CAR_UPGRADE
AI_SPEND_FRACTION = 0.35
AI_RESERVE_FRACTION = 0.10


def discipline_money_scale(discipline: Any) -> float:
    return DISCIPLINE_MONEY_SCALE.get(str(discipline or "").upper(), 0.4)


def upgrade_cost(area: str, current_level: int, discipline: Any = None) -> float:
    """Cost of buying the next level of ``area`` from ``current_level``."""
    base = BASE_UPGRADE_COST.get(area, 2_000_000.0)
    level = max(0, min(MAX_UPGRADE_LEVEL, int(current_level)))
    scale = discipline_money_scale(discipline) if discipline is not None else 1.0
    return round(base * (COST_GROWTH_PER_LEVEL**level) * scale, 2)


def _level_curve(level: float) -> float:
    """0-1 with diminishing returns so the last levels matter less than the first."""
    x = max(0.0, min(1.0, float(level) / float(MAX_UPGRADE_LEVEL)))
    return 1.0 - (1.0 - x) ** 1.6


def performance_rating_from_levels(levels: Dict[str, int]) -> float:
    """Weighted 0-1 car performance rating from upgrade levels."""
    total = 0.0
    for area, weight in PERFORMANCE_WEIGHTS.items():
        total += weight * _level_curve(levels.get(area, 0))
    return max(0.0, min(1.0, total))


def reliability_rating_from_levels(levels: Dict[str, int]) -> float:
    return _level_curve(levels.get("reliability", 0))


def race_income_marker(career_race_id: int) -> str:
    return f"race_income_ref:{int(career_race_id)}"


def tier_label_text(tier: Any) -> str:
    return f"Tier {TIERS.index(normalise_tier(tier)) + 1}"


class UpgradeService:
    """Buys upgrades for teams (player or AI) and pays out race income."""

    TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS ai_offseason_spending (
        team_id INTEGER NOT NULL,
        season INTEGER NOT NULL,
        completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (team_id, season)
    );
    CREATE TABLE IF NOT EXISTS team_car_upgrades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        area TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 0,
        invested_amount REAL NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(team_id, area),
        FOREIGN KEY (team_id) REFERENCES teams(id)
    );
    CREATE INDEX IF NOT EXISTS idx_team_car_upgrades_team_id ON team_car_upgrades(team_id);
    """

    def __init__(self, db: Any):
        self.db = db
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.db.get_connection() as conn:
            conn.executescript(self.TABLE_SQL)
            conn.commit()

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------
    def get_upgrade_levels(self, team_id: int) -> Dict[str, int]:
        levels = {area: 0 for area in UPGRADE_AREAS}
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT area, level FROM team_car_upgrades WHERE team_id = ?",
                (int(team_id),),
            ).fetchall()
        for row in rows:
            area = str(row[0])
            if area in levels:
                levels[area] = int(row[1] or 0)
        return levels

    def get_upgrade_levels_for_teams(
        self, team_ids: Iterable[int]
    ) -> Dict[int, Dict[str, int]]:
        ids = [int(t) for t in team_ids]
        result = {tid: {area: 0 for area in UPGRADE_AREAS} for tid in ids}
        if not ids:
            return result
        placeholders = ",".join("?" for _ in ids)
        with self.db.get_connection() as conn:
            rows = conn.execute(
                f"SELECT team_id, area, level FROM team_car_upgrades WHERE team_id IN ({placeholders})",
                ids,
            ).fetchall()
        for row in rows:
            tid, area = int(row[0]), str(row[1])
            if tid in result and area in result[tid]:
                result[tid][area] = int(row[2] or 0)
        return result

    def get_upgrade_summary(self, team: Any) -> List[Dict[str, Any]]:
        """Per-area rows for a UI: label, level, next cost (None at max)."""
        team_id = int(getattr(team, "id", 0) or 0)
        discipline = getattr(team, "discipline", None)
        levels = self.get_upgrade_levels(team_id)
        rows = []
        for area in UPGRADE_AREAS:
            level = levels[area]
            rows.append(
                {
                    "area": area,
                    "label": UPGRADE_AREA_LABELS[area],
                    "level": level,
                    "max_level": MAX_UPGRADE_LEVEL,
                    "next_cost": (
                        None
                        if level >= MAX_UPGRADE_LEVEL
                        else upgrade_cost(area, level, discipline)
                    ),
                }
            )
        return rows

    def car_performance_rating(self, team_id: int) -> float:
        return performance_rating_from_levels(self.get_upgrade_levels(team_id))

    def reliability_rating(self, team_id: int) -> float:
        return reliability_rating_from_levels(self.get_upgrade_levels(team_id))

    # ------------------------------------------------------------------
    # Spending
    # ------------------------------------------------------------------
    def purchase_upgrade(
        self, team_id: int, area: str, actor: str = "player"
    ) -> Dict[str, Any]:
        """Buy one level of ``area`` for a team, deducting the cost from its budget."""
        if area not in UPGRADE_AREAS:
            raise ValueError(f"Unknown upgrade area: {area}")

        team = self.db.get_team(int(team_id))
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        level = self.get_upgrade_levels(int(team_id))[area]
        if level >= MAX_UPGRADE_LEVEL:
            return {
                "ok": False,
                "reason": "max_level",
                "message": f"{UPGRADE_AREA_LABELS[area]} is already at maximum level.",
                "level": level,
            }

        cost = upgrade_cost(area, level, team.discipline)
        budget = float(getattr(team, "budget", 0.0) or 0.0)
        if budget < cost:
            return {
                "ok": False,
                "reason": "insufficient_budget",
                "message": (
                    f"Not enough budget for {UPGRADE_AREA_LABELS[area]} level {level + 1}. "
                    f"Need EUR {cost:,.0f}, have EUR {budget:,.0f}."
                ),
                "level": level,
                "cost": cost,
            }

        with self.db.get_connection() as conn:
            post_with(
                conn,
                int(team_id),
                -cost,
                CAR_UPGRADE,
                f"{UPGRADE_AREA_LABELS[area]} upgrade to level {level + 1} ({actor})",
                source=str(getattr(team, "name", "") or ""),
            )
            conn.execute(
                """
                INSERT INTO team_car_upgrades (team_id, area, level, invested_amount, updated_at)
                VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(team_id, area) DO UPDATE SET
                    level = team_car_upgrades.level + 1,
                    invested_amount = team_car_upgrades.invested_amount + excluded.invested_amount,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (int(team_id), area, cost),
            )
            remaining = conn.execute(
                "SELECT budget FROM teams WHERE id = ?", (int(team_id),)
            ).fetchone()
            conn.commit()

        return {
            "ok": True,
            "area": area,
            "level": level + 1,
            "cost": cost,
            "remaining_budget": float(remaining[0]) if remaining else budget - cost,
            "message": f"{UPGRADE_AREA_LABELS[area]} upgraded to level {level + 1}.",
        }

    def choose_ai_upgrade_area(
        self,
        levels: Dict[str, int],
        rng: random.Random,
        max_cost: Optional[float] = None,
        discipline: Any = None,
    ) -> Optional[str]:
        """Pick the area an AI team develops next: weakest first, weighted by pace value.

        Only areas below max level and (when ``max_cost`` is given) affordable
        are considered, so one expensive area never stops cheaper purchases.
        """
        candidates = [
            a
            for a in UPGRADE_AREAS
            if levels.get(a, 0) < MAX_UPGRADE_LEVEL
            and (
                max_cost is None
                or upgrade_cost(a, levels.get(a, 0), discipline) <= max_cost
            )
        ]
        if not candidates:
            return None
        weights = []
        for area in candidates:
            gap = MAX_UPGRADE_LEVEL - levels.get(area, 0)
            value = PERFORMANCE_WEIGHTS.get(area, 0.18)
            weights.append(gap * (0.5 + value))
        return rng.choices(candidates, weights=weights, k=1)[0]

    def run_ai_upgrade_spending(
        self,
        discipline: str,
        exclude_team_ids: Iterable[int] = (),
        spend_fraction: float = AI_SPEND_FRACTION,
        rng: Optional[random.Random] = None,
        season: Optional[int] = None,
    ) -> Dict[int, List[Dict[str, Any]]]:
        """Let every AI team in a discipline spend part of its budget on upgrades.

        When ``season`` is given, each team is marked once its off-season
        spending is done, so a repeated call for the same season (for example
        a retried rollover) only resumes the teams that have not spent yet.
        """
        rng = rng or random.Random()
        excluded = {int(t) for t in exclude_team_ids}
        if season is not None:
            excluded |= self._teams_done_spending(int(season))
        purchases: Dict[int, List[Dict[str, Any]]] = {}

        for team in self.db.get_teams_by_discipline(discipline):
            team_id = int(team.id)
            if team_id in excluded:
                continue
            budget = float(getattr(team, "budget", 0.0) or 0.0)
            reserve = budget * AI_RESERVE_FRACTION
            allowance = budget * spend_fraction
            levels = self.get_upgrade_levels(team_id)
            bought: List[Dict[str, Any]] = []
            if season is not None:
                # Marked before buying: an interrupted team under-spends this
                # off-season rather than getting a fresh allowance on retry.
                self._mark_spending_done(team_id, int(season))

            while allowance > 0:
                spendable = min(allowance, budget - reserve)
                area = self.choose_ai_upgrade_area(
                    levels, rng, max_cost=spendable, discipline=team.discipline
                )
                if area is None:
                    break
                cost = upgrade_cost(area, levels[area], team.discipline)
                result = self.purchase_upgrade(team_id, area, actor="ai")
                if not result.get("ok"):
                    break
                levels[area] += 1
                allowance -= cost
                budget -= cost
                bought.append(result)

            if bought:
                purchases[team_id] = bought
        return purchases

    def _teams_done_spending(self, season: int) -> set[int]:
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT team_id FROM ai_offseason_spending WHERE season = ?",
                (season,),
            ).fetchall()
        return {int(row[0]) for row in rows}

    def _mark_spending_done(self, team_id: int, season: int) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO ai_offseason_spending (team_id, season) VALUES (?, ?)",
                (int(team_id), int(season)),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Income
    # ------------------------------------------------------------------
    def race_payout(self, position: int, tier: Any, discipline: Any) -> float:
        """Prize money plus sponsor stipend for one entry in one race."""
        tier_key = normalise_tier(tier)
        scale = discipline_money_scale(discipline)
        if position is None or int(position) <= 0:
            prize = RACE_PRIZE_FLOOR
        elif int(position) <= len(RACE_PRIZE_TABLE):
            prize = RACE_PRIZE_TABLE[int(position) - 1]
        else:
            prize = RACE_PRIZE_FLOOR
        prize *= TIER_PRIZE_SCALE[tier_key]
        stipend = SPONSOR_STIPEND_PER_RACE[tier_key]
        return round((prize + stipend) * scale, 2)

    def award_race_income(self, career_race_id: int) -> int:
        """Pay every team classified in a completed career race. Idempotent per team/race."""
        marker = race_income_marker(career_race_id)
        with self.db.get_connection() as conn:
            race = conn.execute(
                """
                SELECT cr.id, cr.status, cc.tier, cc.discipline
                FROM career_races cr
                JOIN career_championships cc ON cc.id = cr.career_championship_id
                WHERE cr.id = ?
                """,
                (int(career_race_id),),
            ).fetchone()
            if race is None or str(race[1]) != "completed":
                return 0
            tier, discipline = race[2], race[3]

            results = conn.execute(
                """
                SELECT team_id, MIN(position) AS best_position
                FROM career_race_results
                WHERE career_race_id = ? AND team_id IS NOT NULL
                GROUP BY team_id
                """,
                (int(career_race_id),),
            ).fetchall()
            already_paid = {
                int(row[0])
                for row in conn.execute(
                    """
                    SELECT team_id FROM team_budget_transactions
                    WHERE category = ? AND description LIKE ?
                    """,
                    (RACE_INCOME_CATEGORY, f"%({marker})%"),
                ).fetchall()
            }

            paid = 0
            for row in results:
                team_id = int(row[0])
                if team_id in already_paid:
                    continue
                payout = self.race_payout(row[1], tier, discipline)
                post_with(
                    conn,
                    team_id,
                    payout,
                    RACE_INCOME,
                    f"Prize money and sponsor income, best finish P{int(row[1] or 0)} ({marker})",
                    source=f"{str(discipline).replace('_', ' ').title()} {tier_label_text(tier)} promoter and sponsors",
                )
                paid += 1
            conn.commit()
        return paid

    def award_pending_income(
        self, player_id: str, season: Optional[int] = None
    ) -> int:
        """Pay out every completed career race for a player's world not yet paid."""
        with self.db.get_connection() as conn:
            query = """
                SELECT cr.id
                FROM career_races cr
                JOIN career_championships cc ON cc.id = cr.career_championship_id
                WHERE cc.player_id = ? AND cr.status = 'completed'
            """
            params: list[Any] = [player_id]
            if season is not None:
                query += " AND cr.season = ?"
                params.append(int(season))
            race_ids = [int(r[0]) for r in conn.execute(query, params).fetchall()]
        return sum(self.award_race_income(rid) for rid in race_ids)


__all__ = [
    "UPGRADE_AREAS",
    "UPGRADE_AREA_LABELS",
    "MAX_UPGRADE_LEVEL",
    "UpgradeService",
    "performance_rating_from_levels",
    "reliability_rating_from_levels",
    "upgrade_cost",
]
