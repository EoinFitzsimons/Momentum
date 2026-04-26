"""Unit tests for career season rollover and promotion/relegation."""

from __future__ import annotations

from datetime import datetime

import pytest

from database.models import Driver, Team
from services.career_season_service import CareerSeasonService


PLAYER_ID = "local_player"


@pytest.mark.unit
def test_advance_season_rolls_over_and_applies_tier_movement(seeded_db):
    db = seeded_db["db"]
    service = CareerSeasonService(db)

    teams = {
        "t1_a": db.create_team(Team(id=0, name="T1 A", nationality="GBR", discipline="ENDURANCE", tier="TIER_1", budget=50_000_000)),
        "t1_b": db.create_team(Team(id=0, name="T1 B", nationality="GBR", discipline="ENDURANCE", tier="TIER_1", budget=50_000_000)),
        "t1_c": db.create_team(Team(id=0, name="T1 C", nationality="GBR", discipline="ENDURANCE", tier="TIER_1", budget=50_000_000)),
        "t2_a": db.create_team(Team(id=0, name="T2 A", nationality="GBR", discipline="ENDURANCE", tier="TIER_2", budget=35_000_000)),
        "t2_b": db.create_team(Team(id=0, name="T2 B", nationality="GBR", discipline="ENDURANCE", tier="TIER_2", budget=35_000_000)),
        "t2_c": db.create_team(Team(id=0, name="T2 C", nationality="GBR", discipline="ENDURANCE", tier="TIER_2", budget=35_000_000)),
        "t3_a": db.create_team(Team(id=0, name="T3 A", nationality="GBR", discipline="ENDURANCE", tier="TIER_3", budget=20_000_000)),
        "t3_b": db.create_team(Team(id=0, name="T3 B", nationality="GBR", discipline="ENDURANCE", tier="TIER_3", budget=20_000_000)),
        "t3_c": db.create_team(Team(id=0, name="T3 C", nationality="GBR", discipline="ENDURANCE", tier="TIER_3", budget=20_000_000)),
    }

    with db.get_connection() as conn:
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

        championships = {}
        for tier in ["TIER_1", "TIER_2", "TIER_3"]:
            cursor = conn.execute(
                """
                    INSERT INTO career_championships (player_id, name, discipline, tier, season_length, current_season, is_active)
                    VALUES (?, ?, 'ENDURANCE', ?, 2, 1, 1)
                """,
                (PLAYER_ID, f"{tier} Series", tier),
            )
            championships[tier] = int(cursor.lastrowid)

        race_ids = {}
        race_date = datetime(2026, 1, 1).strftime("%Y-%m-%d")
        for tier, champ_id in championships.items():
            cursor = conn.execute(
                """
                INSERT INTO career_races (player_id, career_championship_id, track_id, season, round_number, race_date, weather_conditions, laps, status)
                VALUES (?, ?, ?, 1, 1, ?, 'clear', 3, 'completed')
                """,
                (PLAYER_ID, champ_id, int(seeded_db["track_ids"][0]), race_date),
            )
            race_ids[tier] = int(cursor.lastrowid)

        # Tier 1: C and B should be relegated; Tier 2: A and B should be promoted.
        t1_points = [(teams["t1_a"], 30), (teams["t1_b"], 20), (teams["t1_c"], 10)]
        t2_points = [(teams["t2_a"], 40), (teams["t2_b"], 25), (teams["t2_c"], 5)]
        t3_points = [(teams["t3_a"], 35), (teams["t3_b"], 15), (teams["t3_c"], 4)]

        driver_seed = 1
        for tier, point_rows in [("TIER_1", t1_points), ("TIER_2", t2_points), ("TIER_3", t3_points)]:
            for team_id, points in point_rows:
                conn.execute(
                    """
                    INSERT INTO career_race_results
                        (player_id, career_race_id, driver_id, team_id, position, points, fastest_lap, dnf_reason, grid_position)
                    VALUES (?, ?, ?, ?, ?, ?, 0, NULL, ?)
                    """,
                    (PLAYER_ID, race_ids[tier], driver_seed, int(team_id), driver_seed, int(points), driver_seed),
                )
                driver_seed += 1

        conn.commit()

    result = service.advance_season(player_id=PLAYER_ID, completed_season=1, discipline="ENDURANCE")

    assert result["rolled_over"] is True
    assert len(result["promoted"]) == 3
    assert len(result["relegated"]) == 3

    # Boundaries respected: no tier outside known bands.
    for team_id in [
        teams["t1_a"], teams["t1_b"], teams["t1_c"],
        teams["t2_a"], teams["t2_b"], teams["t2_c"],
        teams["t3_a"], teams["t3_b"], teams["t3_c"],
    ]:
        tier = db.get_team(team_id).tier
        assert tier in {"TIER_1", "TIER_2", "TIER_3", "TOP_TIER"}

    with db.get_connection() as conn:
        # All active championships should have moved to season 2 and received a season 2 calendar.
        rows = conn.execute(
            "SELECT current_season FROM career_championships WHERE player_id = ?",
            (PLAYER_ID,),
        ).fetchall()
        assert rows
        assert all(int(r["current_season"]) == 2 for r in rows)

        next_races = conn.execute(
            "SELECT COUNT(1) FROM career_races WHERE player_id = ? AND season = 2",
            (PLAYER_ID,),
        ).fetchone()
        assert int(next_races[0] or 0) > 0


@pytest.mark.unit
def test_advance_season_blocked_when_races_incomplete(seeded_db):
    db = seeded_db["db"]
    service = CareerSeasonService(db)

    with db.get_connection() as conn:
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
            """
        )

        cursor = conn.execute(
            """
            INSERT INTO career_championships (player_id, name, discipline, tier, season_length, current_season, is_active)
            VALUES (?, 'Tier 2 Series', 'ENDURANCE', 'TIER_2', 2, 1, 1)
            """,
            (PLAYER_ID,),
        )
        champ_id = int(cursor.lastrowid)

        conn.execute(
            """
            INSERT INTO career_races (player_id, career_championship_id, track_id, season, round_number, race_date, weather_conditions, laps, status)
            VALUES (?, ?, ?, 1, 1, '2026-01-01', 'clear', 3, 'scheduled')
            """,
            (PLAYER_ID, champ_id, int(seeded_db["track_ids"][0])),
        )
        conn.commit()

    result = service.advance_season(player_id=PLAYER_ID, completed_season=1, discipline="ENDURANCE")
    assert result["rolled_over"] is False


@pytest.mark.unit
def test_headless_simulates_non_player_championships(seeded_db):
    db = seeded_db["db"]
    service = CareerSeasonService(db)

    # Player-owned series team (ENDURANCE TIER_2)
    player_team_id = db.create_team(
        Team(id=0, name="Player Endurance", nationality="GBR", discipline="ENDURANCE", tier="TIER_2", budget=40_000_000)
    )
    db.assign_team_owner(int(player_team_id), PLAYER_ID)

    # Non-player series teams (ENDURANCE TIER_1)
    ai_team_a = db.create_team(
        Team(id=0, name="AI Endurance A", nationality="GBR", discipline="ENDURANCE", tier="TIER_1", budget=55_000_000)
    )
    ai_team_b = db.create_team(
        Team(id=0, name="AI Endurance B", nationality="GBR", discipline="ENDURANCE", tier="TIER_1", budget=53_000_000)
    )

    # Provide drivers so headless simulation can build a grid.
    ai_driver_1 = db.create_driver(
        Driver(
            id=0,
            name="AI Driver 1",
            nationality="GBR",
            birth_date="1996-01-01",
            speed=78,
            racecraft=76,
            consistency=74,
            preferred_discipline="ENDURANCE",
            current_team_id=int(ai_team_a),
        )
    )
    ai_driver_2 = db.create_driver(
        Driver(
            id=0,
            name="AI Driver 2",
            nationality="GBR",
            birth_date="1997-01-01",
            speed=75,
            racecraft=75,
            consistency=73,
            preferred_discipline="ENDURANCE",
            current_team_id=int(ai_team_a),
        )
    )
    ai_driver_3 = db.create_driver(
        Driver(
            id=0,
            name="AI Driver 3",
            nationality="GBR",
            birth_date="1998-01-01",
            speed=77,
            racecraft=74,
            consistency=72,
            preferred_discipline="ENDURANCE",
            current_team_id=int(ai_team_b),
        )
    )
    ai_driver_4 = db.create_driver(
        Driver(
            id=0,
            name="AI Driver 4",
            nationality="GBR",
            birth_date="1999-01-01",
            speed=74,
            racecraft=73,
            consistency=71,
            preferred_discipline="ENDURANCE",
            current_team_id=int(ai_team_b),
        )
    )

    # Compact driver insert fallback may omit current_team_id, so enforce it.
    with db.get_connection() as conn:
        conn.execute("UPDATE drivers SET current_team_id = ? WHERE id = ?", (int(ai_team_a), int(ai_driver_1)))
        conn.execute("UPDATE drivers SET current_team_id = ? WHERE id = ?", (int(ai_team_a), int(ai_driver_2)))
        conn.execute("UPDATE drivers SET current_team_id = ? WHERE id = ?", (int(ai_team_b), int(ai_driver_3)))
        conn.execute("UPDATE drivers SET current_team_id = ? WHERE id = ?", (int(ai_team_b), int(ai_driver_4)))
        conn.commit()

    with db.get_connection() as conn:
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

        player_cursor = conn.execute(
            """
            INSERT INTO career_championships (player_id, name, discipline, tier, season_length, current_season, is_active)
            VALUES (?, 'Player Series', 'ENDURANCE', 'TIER_2', 1, 1, 1)
            """,
            (PLAYER_ID,),
        )
        player_championship_id = int(player_cursor.lastrowid)

        ai_cursor = conn.execute(
            """
            INSERT INTO career_championships (player_id, name, discipline, tier, season_length, current_season, is_active)
            VALUES (?, 'AI Series', 'ENDURANCE', 'TIER_1', 1, 1, 1)
            """,
            (PLAYER_ID,),
        )
        ai_championship_id = int(ai_cursor.lastrowid)

        # Player series race already complete. Non-player race should be resolved headlessly.
        conn.execute(
            """
            INSERT INTO career_races (player_id, career_championship_id, track_id, season, round_number, race_date, weather_conditions, laps, status)
            VALUES (?, ?, ?, 1, 1, '2026-01-01', 'clear', 3, 'completed')
            """,
            (PLAYER_ID, player_championship_id, int(seeded_db["track_ids"][0])),
        )
        ai_race_cursor = conn.execute(
            """
            INSERT INTO career_races (player_id, career_championship_id, track_id, season, round_number, race_date, weather_conditions, laps, status)
            VALUES (?, ?, ?, 1, 1, '2026-01-01', 'clear', 3, 'scheduled')
            """,
            (PLAYER_ID, ai_championship_id, int(seeded_db["track_ids"][0])),
        )
        ai_race_id = int(ai_race_cursor.lastrowid)
        conn.commit()

    result = service.advance_season(player_id=PLAYER_ID, completed_season=1, discipline="ENDURANCE")

    assert result["headless_resolved_races"] == 1
    assert result["headless_persisted_results"] >= 2
    assert result["rolled_over"] is True

    with db.get_connection() as conn:
        ai_race_row = conn.execute("SELECT status FROM career_races WHERE id = ?", (ai_race_id,)).fetchone()
        assert ai_race_row is not None
        assert str(ai_race_row["status"]) == "completed"

        ai_results = conn.execute(
            "SELECT COUNT(1) FROM career_race_results WHERE career_race_id = ?",
            (ai_race_id,),
        ).fetchone()
        assert int(ai_results[0] or 0) >= 2
