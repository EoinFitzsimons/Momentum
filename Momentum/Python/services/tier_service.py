"""Canonical team tiers.

A tier is a league. Teams are placed in a tier from their past results
(promotion and relegation between seasons) and, for a fresh world, from
their overall strength so the strongest teams start in the top league.
Tier never feeds into race pace directly.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

TIER_1 = "TIER_1"
TIER_2 = "TIER_2"
TIER_3 = "TIER_3"
TIERS: tuple[str, ...] = (TIER_1, TIER_2, TIER_3)
DEFAULT_TIER = TIER_2

TIER_LABELS: Dict[str, str] = {
    TIER_1: "Tier 1",
    TIER_2: "Tier 2",
    TIER_3: "Tier 3",
}

# Share of a discipline's teams placed in each league for a fresh world.
TIER_SHARES: Dict[str, float] = {TIER_1: 0.15, TIER_2: 0.30, TIER_3: 0.55}

_TIER_ALIASES: Dict[str, str] = {
    "TIER_1": TIER_1,
    "TIER1": TIER_1,
    "TOP_TIER": TIER_1,
    "TOPTIER": TIER_1,
    "1": TIER_1,
    "TIER_2": TIER_2,
    "TIER2": TIER_2,
    "2": TIER_2,
    "TIER_3": TIER_3,
    "TIER3": TIER_3,
    "3": TIER_3,
}

# Tables holding a tier column that must only contain canonical values.
_TIERED_TABLES: tuple[str, ...] = ("teams", "championships", "career_championships")


def normalise_tier(value: Any, default: str = DEFAULT_TIER) -> str:
    """Map any historical tier spelling (``tier1``, ``TOP_TIER`` ...) to a canonical value."""
    raw = str(value or "").strip().upper().replace("-", "_").replace(" ", "_")
    return _TIER_ALIASES.get(raw, default)


def tier_label(value: Any) -> str:
    """Player-facing label for a tier value."""
    return TIER_LABELS[normalise_tier(value)]


def tier_rank(value: Any) -> int:
    """1 for the top league, 3 for the bottom one."""
    return TIERS.index(normalise_tier(value)) + 1


def normalise_tier_columns(conn: Any) -> int:
    """Rewrite non-canonical tier values in place. Returns the number of rows changed."""
    changed = 0
    for table in _TIERED_TABLES:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
        ).fetchone()
        if not exists:
            continue
        rows = conn.execute(
            f"SELECT DISTINCT tier FROM {table} WHERE tier IS NOT NULL"
        ).fetchall()
        for row in rows:
            raw = row[0]
            canonical = normalise_tier(raw)
            if raw == canonical:
                continue
            cursor = conn.execute(
                f"UPDATE {table} SET tier = ? WHERE tier = ?", (canonical, raw)
            )
            changed += int(cursor.rowcount or 0)
    return changed


def split_by_shares(count: int) -> Dict[str, int]:
    """How many of ``count`` ranked teams go in each tier (top tier first)."""
    if count <= 0:
        return {tier: 0 for tier in TIERS}
    if count < len(TIERS):
        # Too few teams for three leagues: fill from the top down.
        return {tier: (1 if idx < count else 0) for idx, tier in enumerate(TIERS)}
    sizes = {tier: max(1, int(round(count * TIER_SHARES[tier]))) for tier in TIERS}
    sizes[TIER_3] = max(1, count - sizes[TIER_1] - sizes[TIER_2])
    overflow = sum(sizes.values()) - count
    while overflow > 0:
        for tier in (TIER_2, TIER_1):
            if overflow > 0 and sizes[tier] > 1:
                sizes[tier] -= 1
                overflow -= 1
    return sizes


class TierService:
    """Places teams into leagues by strength and keeps tier values canonical."""

    def __init__(self, db: Any):
        self.db = db

    # ------------------------------------------------------------------
    # Strength
    # ------------------------------------------------------------------
    def team_strength(self, team: Any) -> float:
        """Overall strength on a 0-100 scale: car, operations and driver line-up."""
        from services.upgrade_service import UpgradeService

        team_id = int(getattr(team, "id", 0) or 0)
        operations = float(getattr(team, "operations_rating", 50.0) or 50.0)
        car = UpgradeService(self.db).car_performance_rating(team_id) * 100.0

        try:
            drivers = self.db.get_drivers_by_team(team_id)
        except Exception:
            drivers = []
        driver_ratings = sorted(
            (
                float(getattr(d, "speed", 50.0) or 50.0) * 0.45
                + float(getattr(d, "racecraft", 50.0) or 50.0) * 0.30
                + float(getattr(d, "consistency", 50.0) or 50.0) * 0.25
                for d in drivers
            ),
            reverse=True,
        )[:2]
        driver_score = (
            sum(driver_ratings) / len(driver_ratings) if driver_ratings else 50.0
        )

        return operations * 0.45 + car * 0.25 + driver_score * 0.30

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------
    def assign_tiers_by_strength(self, discipline: str) -> Dict[str, List[int]]:
        """Rank a discipline's teams by strength and place them into leagues."""
        teams = list(self.db.get_teams_by_discipline(discipline))
        ranked = sorted(
            teams,
            key=lambda t: (-self.team_strength(t), int(getattr(t, "id", 0) or 0)),
        )
        sizes = split_by_shares(len(ranked))

        placement: Dict[str, List[int]] = {tier: [] for tier in TIERS}
        cursor = 0
        for tier in TIERS:
            for team in ranked[cursor : cursor + sizes[tier]]:
                placement[tier].append(int(team.id))
            cursor += sizes[tier]

        with self.db.get_connection() as conn:
            for tier, team_ids in placement.items():
                if not team_ids:
                    continue
                placeholders = ",".join("?" for _ in team_ids)
                conn.execute(
                    f"UPDATE teams SET tier = ? WHERE id IN ({placeholders})",
                    (tier, *team_ids),
                )
            conn.commit()
        return placement

    def assign_all_disciplines(
        self, disciplines: Optional[Iterable[str]] = None
    ) -> Dict[str, Dict[str, List[int]]]:
        """Assign tiers by strength for every discipline (or the given ones)."""
        if disciplines is None:
            with self.db.get_connection() as conn:
                rows = conn.execute(
                    "SELECT DISTINCT UPPER(discipline) FROM teams ORDER BY 1"
                ).fetchall()
            disciplines = [str(r[0]) for r in rows if r and r[0]]
        return {
            str(d).upper(): self.assign_tiers_by_strength(str(d)) for d in disciplines
        }


__all__ = [
    "TIER_1",
    "TIER_2",
    "TIER_3",
    "TIERS",
    "DEFAULT_TIER",
    "TIER_LABELS",
    "TIER_SHARES",
    "TierService",
    "normalise_tier",
    "normalise_tier_columns",
    "split_by_shares",
    "tier_label",
    "tier_rank",
]
