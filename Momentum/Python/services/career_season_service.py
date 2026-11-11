"""Career season rollover and tier movement logic for career mode."""

from __future__ import annotations

from datetime import datetime, timedelta
import random
from typing import Any

from database.database_manager import DatabaseManager
from services.championship_service import ChampionshipService
from services.career_result_service import persist_career_race_result
from services.tier_service import TIERS, normalise_tier
from RaceLogic.race_format import race_format_for
from services.upgrade_service import UpgradeService

TIER_ORDER = list(TIERS)
MAX_MOVES_PER_TIER = 2


class CareerSeasonService:
    """Applies season rollover and team promotion/relegation for career worlds."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def advance_season(
        self, player_id: str, completed_season: int, discipline: str
    ) -> dict[str, Any]:
        """Advance a completed season and apply tier movement for one discipline."""
        self._ensure_career_tables()

        headless = self._resolve_non_player_races_headless(
            player_id=player_id, season=completed_season
        )

        with self.db.get_connection() as conn:
            blocked = self._has_incomplete_races(conn, player_id, completed_season)
        if blocked:
            # Nothing else may run until the season is actually finished;
            # otherwise retries would pay income and spend AI budgets again.
            return {
                "rolled_over": False,
                "promoted": [],
                "relegated": [],
                "headless_resolved_races": headless["resolved_races"],
                "headless_persisted_results": headless["persisted_results"],
                "income_payouts": 0,
                "ai_upgrades": 0,
            }

        payouts = self._award_season_income(
            player_id=player_id, season=completed_season
        )
        ai_upgrades = self._run_ai_spending(
            player_id=player_id, discipline=discipline, season=completed_season
        )

        movements = self._apply_promotion_relegation(
            player_id=player_id,
            discipline=discipline,
            season=completed_season,
        )
        rolled = self._rollover_world(
            player_id=player_id, completed_season=completed_season
        )

        return {
            "rolled_over": rolled,
            "promoted": movements["promoted"],
            "relegated": movements["relegated"],
            "headless_resolved_races": headless["resolved_races"],
            "headless_persisted_results": headless["persisted_results"],
            "income_payouts": payouts,
            "ai_upgrades": ai_upgrades,
        }

    def _award_season_income(self, player_id: str, season: int) -> int:
        """Pay out the season's race income (idempotent per race and team)."""
        upgrades = UpgradeService(self.db)
        return int(upgrades.award_pending_income(player_id=player_id, season=season))

    def _run_ai_spending(self, player_id: str, discipline: str, season: int) -> int:
        """Let AI teams buy upgrades once per off-season; retries resume unfinished teams."""
        upgrades = UpgradeService(self.db)
        owned_team_id = self.db.get_player_team_id(player_id)
        excluded = [int(owned_team_id)] if owned_team_id else []
        purchases = upgrades.run_ai_upgrade_spending(
            discipline=str(discipline or "").upper(),
            exclude_team_ids=excluded,
            season=int(season),
        )
        return sum(len(items) for items in purchases.values())

    def _resolve_non_player_races_headless(
        self, player_id: str, season: int
    ) -> dict[str, int]:
        owned_team_id = self.db.get_player_team_id(player_id)
        owned_team = self.db.get_team(owned_team_id) if owned_team_id else None
        owned_discipline = str(getattr(owned_team, "discipline", "") or "").upper()
        owned_tier = (
            normalise_tier(getattr(owned_team, "tier", None)) if owned_team else None
        )

        resolved_races = 0
        persisted_results = 0

        with self.db.get_connection() as conn:
            race_rows = conn.execute(
                """
                SELECT cr.id AS race_id,
                       cc.id AS championship_id,
                       cc.discipline AS discipline,
                       cc.tier AS tier
                FROM career_races cr
                JOIN career_championships cc ON cc.id = cr.career_championship_id
                WHERE cc.player_id = ?
                  AND cr.season = ?
                  AND cr.status IN ('scheduled', 'in-progress')
                  AND cc.is_active = 1
                ORDER BY cr.id
                """,
                (player_id, season),
            ).fetchall()

        for row in race_rows:
            race_id = int(row["race_id"])
            discipline_key = str(row["discipline"] or "").upper()
            tier_key = normalise_tier(row["tier"])

            # Only auto-resolve championships outside the player's owned series.
            if (
                owned_team
                and discipline_key == owned_discipline
                and tier_key == owned_tier
            ):
                continue

            entrants = self._build_headless_grid(
                discipline=discipline_key, tier=tier_key
            )
            if not entrants:
                continue

            with self.db.get_connection() as conn:
                conn.execute(
                    "DELETE FROM career_race_results WHERE career_race_id = ?",
                    (race_id,),
                )
                conn.commit()

            fastest_lap_index = random.randint(0, len(entrants) - 1)
            points_service = ChampionshipService(self.db)
            for idx, entry in enumerate(entrants, start=1):
                fastest_lap = (idx - 1) == fastest_lap_index
                points = points_service.calculate_points(
                    position=idx,
                    discipline=discipline_key,
                    fastest_lap=fastest_lap,
                )
                persist_career_race_result(
                    db=self.db,
                    player_id=player_id,
                    career_race_id=race_id,
                    driver_id=int(entry["driver_id"]),
                    team_id=int(entry["team_id"]),
                    position=idx,
                    points=int(points),
                    fastest_lap=fastest_lap,
                    dnf_reason=None,
                    grid_position=idx,
                )
                persisted_results += 1

            with self.db.get_connection() as conn:
                conn.execute(
                    "UPDATE career_races SET status = 'completed' WHERE id = ?",
                    (race_id,),
                )
                conn.commit()
            resolved_races += 1

        return {
            "resolved_races": resolved_races,
            "persisted_results": persisted_results,
        }

    def _build_headless_grid(
        self, discipline: str, tier: str
    ) -> list[dict[str, int | float]]:
        teams = [
            team
            for team in self.db.get_teams_by_discipline(discipline)
            if normalise_tier(getattr(team, "tier", None)) == tier
        ]
        if not teams:
            return []

        fmt = race_format_for(discipline)
        entries: list[dict[str, int | float]] = []
        for team in teams:
            drivers = self.db.get_drivers_by_team(int(team.id))
            if not drivers:
                continue

            top_drivers = sorted(
                drivers,
                key=lambda d: (
                    float(getattr(d, "speed", 50.0) or 50.0)
                    + float(getattr(d, "racecraft", 50.0) or 50.0)
                    + float(getattr(d, "consistency", 50.0) or 50.0)
                ),
                reverse=True,
            )[: fmt.cars_per_team * fmt.drivers_per_car]

            team_rating = (
                float(getattr(team, "operations_rating", 50.0) or 50.0) * 0.65
                + float(getattr(team, "car_rating", 0.0) or 0.0) * 35.0
            )

            for driver in top_drivers:
                driver_rating = (
                    float(getattr(driver, "speed", 50.0) or 50.0) * 0.42
                    + float(getattr(driver, "racecraft", 50.0) or 50.0) * 0.33
                    + float(getattr(driver, "consistency", 50.0) or 50.0) * 0.25
                )
                total = (
                    (driver_rating * 0.62)
                    + (team_rating * 0.33)
                    + random.uniform(-4.0, 4.0)
                )
                entries.append(
                    {
                        "driver_id": int(driver.id),
                        "team_id": int(team.id),
                        "score": float(total),
                    }
                )

        entries.sort(key=lambda item: float(item["score"]), reverse=True)
        # Heats, brackets and regulation caps: only the format's field size
        # makes the final classification.
        return entries[: fmt.grid_size(tier=tier, available=len(entries))]

    def _apply_promotion_relegation(
        self, player_id: str, discipline: str, season: int
    ) -> dict[str, list[int]]:
        by_tier: dict[str, list[dict[str, Any]]] = {tier: [] for tier in TIERS}

        discipline_key = str(discipline or "").upper()

        with self.db.get_connection() as conn:
            team_rows = conn.execute(
                """
                SELECT id, tier
                FROM teams
                WHERE UPPER(discipline) = ?
                """,
                (discipline_key,),
            ).fetchall()

            for row in team_rows:
                tier = normalise_tier(row["tier"])
                by_tier.setdefault(tier, []).append(
                    {"team_id": int(row["id"]), "points": 0}
                )

            points_rows = conn.execute(
                """
                SELECT cc.tier AS tier,
                       rr.team_id AS team_id,
                       COALESCE(SUM(rr.points), 0) AS total_points
                FROM career_race_results rr
                JOIN career_races cr ON cr.id = rr.career_race_id
                JOIN career_championships cc ON cc.id = cr.career_championship_id
                WHERE cc.player_id = ?
                  AND UPPER(cc.discipline) = ?
                  AND cr.season = ?
                GROUP BY cc.tier, rr.team_id
                """,
                (player_id, discipline_key, season),
            ).fetchall()

            score_map: dict[tuple[str, int], int] = {}
            for row in points_rows:
                key = (normalise_tier(row["tier"]), int(row["team_id"]))
                score_map[key] = int(row["total_points"] or 0)

            for tier_key, teams in by_tier.items():
                for team in teams:
                    team["points"] = int(score_map.get((tier_key, team["team_id"]), 0))

            promoted: list[int] = []
            relegated: list[int] = []
            moved_teams: set[int] = set()

            for high_tier, low_tier in zip(TIERS[:-1], TIERS[1:]):
                upper = sorted(
                    [
                        item
                        for item in by_tier.get(high_tier, [])
                        if int(item["team_id"]) not in moved_teams
                    ],
                    key=lambda item: (item["points"], -item["team_id"]),
                )
                lower = sorted(
                    [
                        item
                        for item in by_tier.get(low_tier, [])
                        if int(item["team_id"]) not in moved_teams
                    ],
                    key=lambda item: (-item["points"], item["team_id"]),
                )

                move_count = min(MAX_MOVES_PER_TIER, len(upper), len(lower))
                if move_count <= 0:
                    continue

                promote_ids = [int(item["team_id"]) for item in lower[:move_count]]
                relegate_ids = [int(item["team_id"]) for item in upper[:move_count]]

                if promote_ids:
                    placeholders = ",".join(["?"] * len(promote_ids))
                    conn.execute(
                        f"UPDATE teams SET tier = ? WHERE id IN ({placeholders})",
                        (high_tier, *promote_ids),
                    )
                    promoted.extend(promote_ids)
                    moved_teams.update(promote_ids)

                if relegate_ids:
                    placeholders = ",".join(["?"] * len(relegate_ids))
                    conn.execute(
                        f"UPDATE teams SET tier = ? WHERE id IN ({placeholders})",
                        (low_tier, *relegate_ids),
                    )
                    relegated.extend(relegate_ids)
                    moved_teams.update(relegate_ids)

            conn.commit()

        return {"promoted": promoted, "relegated": relegated}

    def _rollover_world(self, player_id: str, completed_season: int) -> bool:
        with self.db.get_connection() as conn:
            if self._has_incomplete_races(conn, player_id, completed_season):
                return False

            championships = self._get_active_championships(conn, player_id)

            moved = False
            for champ in championships:
                champ_id = int(champ["id"])
                current = int(champ["current_season"] or 1)
                if current != completed_season:
                    continue

                next_season = current + 1
                self._ensure_next_season_calendar(
                    conn=conn,
                    player_id=player_id,
                    championship_id=champ_id,
                    discipline=str(champ["discipline"]),
                    season_length=int(champ["season_length"] or 10),
                    current_season=current,
                    next_season=next_season,
                )

                conn.execute(
                    "UPDATE career_championships SET current_season = ? WHERE id = ?",
                    (next_season, champ_id),
                )
                moved = True

            conn.commit()
            return moved

    def _has_incomplete_races(self, conn, player_id: str, season: int) -> bool:
        row = conn.execute(
            """
            SELECT COUNT(1)
            FROM career_races
            WHERE player_id = ?
              AND season = ?
              AND status != 'completed'
            """,
            (player_id, season),
        ).fetchone()
        return int(row[0] or 0) > 0

    def _get_active_championships(self, conn, player_id: str):
        return conn.execute(
            """
            SELECT id, discipline, season_length, current_season
            FROM career_championships
            WHERE player_id = ? AND is_active = 1
            """,
            (player_id,),
        ).fetchall()

    def _ensure_next_season_calendar(
        self,
        conn,
        player_id: str,
        championship_id: int,
        discipline: str,
        season_length: int,
        current_season: int,
        next_season: int,
    ) -> None:
        existing_next = conn.execute(
            """
            SELECT COUNT(1)
            FROM career_races
            WHERE player_id = ? AND career_championship_id = ? AND season = ?
            """,
            (player_id, championship_id, next_season),
        ).fetchone()
        if int(existing_next[0] or 0) > 0:
            return

        track_ids = self._resolve_track_ids_for_championship(
            conn, discipline, season_length
        )
        start_date = self._season_start_date(
            conn, player_id, championship_id, current_season, next_season
        )

        for round_number, track_id in enumerate(track_ids, start=1):
            conn.execute(
                """
                INSERT INTO career_races (
                    player_id, career_championship_id, track_id, season, round_number,
                    race_date, weather_conditions, laps, status
                )
                VALUES (?, ?, ?, ?, ?, ?, 'clear', ?, 'scheduled')
                """,
                (
                    player_id,
                    championship_id,
                    int(track_id),
                    next_season,
                    round_number,
                    start_date.strftime("%Y-%m-%d"),
                    ChampionshipService.default_laps_for_discipline(discipline),
                ),
            )
            start_date += timedelta(days=14)

    def _season_start_date(
        self,
        conn,
        player_id: str,
        championship_id: int,
        current_season: int,
        next_season: int,
    ) -> datetime:
        row = conn.execute(
            """
            SELECT MAX(race_date) AS max_date
            FROM career_races
            WHERE player_id = ? AND career_championship_id = ? AND season = ?
            """,
            (player_id, championship_id, current_season),
        ).fetchone()
        if row and row["max_date"]:
            return datetime.strptime(str(row["max_date"]), "%Y-%m-%d") + timedelta(
                days=14
            )
        return datetime(2026, 1, 1) + timedelta(days=((next_season - 1) * 365))

    def _resolve_track_ids_for_championship(
        self, conn, discipline: str, season_length: int
    ) -> list[int]:
        rows = conn.execute(
            "SELECT id FROM tracks WHERE UPPER(primary_discipline) = ? ORDER BY id",
            (str(discipline or "").upper(),),
        ).fetchall()
        if not rows:
            rows = conn.execute("SELECT id FROM tracks ORDER BY id").fetchall()
        if not rows:
            raise ValueError("No tracks available to build next season calendar.")

        base_ids = [int(row["id"]) for row in rows]
        if len(base_ids) >= season_length:
            return base_ids[:season_length]

        expanded: list[int] = []
        while len(expanded) < season_length:
            expanded.extend(base_ids)
        return expanded[:season_length]

    def _ensure_career_tables(self) -> None:
        with self.db.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS career_championships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    discipline TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    season_length INTEGER NOT NULL,
                    current_season INTEGER NOT NULL DEFAULT 1,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS career_races (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT NOT NULL,
                    career_championship_id INTEGER NOT NULL,
                    track_id INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    round_number INTEGER NOT NULL,
                    race_date TEXT NOT NULL,
                    weather_conditions TEXT NOT NULL DEFAULT 'clear',
                    laps INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'scheduled',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS career_race_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT NOT NULL,
                    career_race_id INTEGER NOT NULL,
                    driver_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    points INTEGER NOT NULL DEFAULT 0,
                    fastest_lap INTEGER NOT NULL DEFAULT 0,
                    dnf_reason TEXT,
                    grid_position INTEGER,
                    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(career_race_id, driver_id)
                );
                """
            )
            conn.commit()
