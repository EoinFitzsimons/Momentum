"""Unit tests for league (tier) handling and the car upgrade economy."""

from __future__ import annotations

import random

import pytest

from database.models import Driver, Team
from RaceLogic.disciplines.single_seater.single_seater_discipline import (
    SingleSeaterEngine,
)
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from services.tier_service import (
    TIERS,
    TierService,
    normalise_tier,
    normalise_tier_columns,
    split_by_shares,
    tier_label,
)
from services.upgrade_service import (
    MAX_UPGRADE_LEVEL,
    UPGRADE_AREAS,
    UpgradeService,
    performance_rating_from_levels,
    upgrade_cost,
)


def _team(team_id: int, tier: str, budget: float, ops: float = 50.0, **extra) -> Team:
    team = Team(
        id=team_id,
        name=f"Team {team_id}",
        nationality="IE",
        discipline="SINGLE_SEATER",
        tier=tier,
        budget=budget,
        operations_rating=ops,
    )
    for key, value in extra.items():
        setattr(team, key, value)
    return team


def _create_team(db, name: str, ops: float, budget: float = 50_000_000.0) -> int:
    return db.create_team(
        Team(
            id=0,
            name=name,
            nationality="IE",
            discipline="SINGLE_SEATER",
            tier="TIER_3",
            budget=budget,
            operations_rating=ops,
        )
    )


def _create_driver(db, name: str, team_id: int, skill: float) -> int:
    return db.create_driver(
        Driver(
            id=0,
            name=name,
            nationality="IE",
            birth_date="1995-01-01",
            current_team_id=team_id,
            preferred_discipline="SINGLE_SEATER",
            speed=skill,
            racecraft=skill,
            consistency=skill,
        )
    )


# ---------------------------------------------------------------------------
# Naming
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("tier1", "TIER_1"),
        ("TOP_TIER", "TIER_1"),
        ("Tier-2", "TIER_2"),
        ("TIER_3", "TIER_3"),
        ("3", "TIER_3"),
        ("", "TIER_5"),
        (None, "TIER_5"),
    ],
)
def test_normalise_tier_maps_every_legacy_spelling(raw, expected):
    assert normalise_tier(raw) == expected


@pytest.mark.unit
def test_tier_label_is_player_facing():
    assert tier_label("tier1") == "Tier 1"


@pytest.mark.unit
def test_normalise_tier_columns_rewrites_legacy_rows(test_db):
    with test_db.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO teams (name, nationality, discipline, tier, budget)
            VALUES ('Legacy A', 'IE', 'SINGLE_SEATER', 'tier1', 1.0),
                   ('Legacy B', 'IE', 'SINGLE_SEATER', 'TOP_TIER', 1.0),
                   ('Legacy C', 'IE', 'SINGLE_SEATER', 'TIER_3', 1.0)
            """
        )
        conn.commit()
        changed = normalise_tier_columns(conn)
        conn.commit()
        rows = conn.execute("SELECT DISTINCT tier FROM teams").fetchall()

    assert changed == 2
    assert {row[0] for row in rows} == {"TIER_1", "TIER_3"}


# ---------------------------------------------------------------------------
# League placement by strength
# ---------------------------------------------------------------------------
@pytest.mark.unit
def test_split_by_shares_fills_top_league_first():
    assert split_by_shares(0) == {tier: 0 for tier in TIERS}
    assert split_by_shares(2) == {"TIER_1": 1, "TIER_2": 1, "TIER_3": 0, "TIER_4": 0, "TIER_5": 0}
    sizes = split_by_shares(100)
    assert sum(sizes.values()) == 100
    assert all(size == 20 for size in sizes.values())
    assert sum(split_by_shares(23).values()) == 23


@pytest.mark.unit
def test_assign_tiers_by_strength_puts_strongest_team_in_tier_1(test_db):
    strengths = [40.0, 95.0, 55.0, 70.0, 60.0, 85.0, 45.0, 65.0, 50.0, 75.0]
    ids = [
        _create_team(test_db, f"Strength {int(ops)}", ops)
        for ops in strengths
    ]
    for team_id, ops in zip(ids, strengths):
        _create_driver(test_db, f"Driver {team_id}", team_id, ops)

    placement = TierService(test_db).assign_tiers_by_strength("SINGLE_SEATER")

    strongest = ids[strengths.index(95.0)]
    weakest = ids[strengths.index(40.0)]
    assert strongest in placement["TIER_1"]
    assert weakest in placement["TIER_5"]
    assert test_db.get_team(strongest).tier == "TIER_1"
    assert test_db.get_team(weakest).tier == "TIER_5"
    assert sum(len(v) for v in placement.values()) == len(ids)

    # Every TIER_1 team is stronger than every TIER_3 team.
    service = TierService(test_db)
    top = min(service.team_strength(test_db.get_team(t)) for t in placement["TIER_1"])
    bottom = max(
        service.team_strength(test_db.get_team(t)) for t in placement["TIER_3"]
    )
    assert top > bottom


# ---------------------------------------------------------------------------
# Upgrades
# ---------------------------------------------------------------------------
@pytest.mark.unit
def test_upgrade_cost_rises_per_level_and_scales_by_discipline():
    assert upgrade_cost("power", 1) > upgrade_cost("power", 0)
    assert upgrade_cost("power", 0, "DRAG_ACCELERATION") < upgrade_cost(
        "power", 0, "SINGLE_SEATER"
    )


@pytest.mark.unit
def test_performance_rating_grows_with_levels_and_is_bounded():
    empty = performance_rating_from_levels({})
    full = performance_rating_from_levels({a: MAX_UPGRADE_LEVEL for a in UPGRADE_AREAS})
    half = performance_rating_from_levels({a: 5 for a in UPGRADE_AREAS})
    assert empty == 0.0
    assert 0.0 < half < full <= 1.0


@pytest.mark.unit
def test_purchase_upgrade_deducts_budget_and_records_transaction(test_db):
    team_id = _create_team(test_db, "Buyer", 60.0, budget=10_000_000.0)
    service = UpgradeService(test_db)

    result = service.purchase_upgrade(team_id, "power")

    assert result["ok"] is True
    assert result["level"] == 1
    team = test_db.get_team(team_id)
    assert team.budget == pytest.approx(10_000_000.0 - result["cost"])
    assert service.get_upgrade_levels(team_id)["power"] == 1
    assert team.car_rating > 0.0

    transactions = test_db.get_budget_transactions(team_id)
    assert any(t["category"] == "car_upgrade" for t in transactions)


@pytest.mark.unit
def test_purchase_upgrade_refuses_when_budget_is_short(test_db):
    team_id = _create_team(test_db, "Skint", 60.0, budget=1_000.0)
    result = UpgradeService(test_db).purchase_upgrade(team_id, "aero")

    assert result["ok"] is False
    assert result["reason"] == "insufficient_budget"
    assert test_db.get_team(team_id).budget == pytest.approx(1_000.0)


@pytest.mark.unit
def test_ai_spending_buys_upgrades_but_keeps_a_reserve(test_db):
    rich = _create_team(test_db, "Rich AI", 70.0, budget=40_000_000.0)
    player = _create_team(test_db, "Player", 70.0, budget=40_000_000.0)
    service = UpgradeService(test_db)

    purchases = service.run_ai_upgrade_spending(
        "SINGLE_SEATER", exclude_team_ids=[player], rng=random.Random(7)
    )

    assert rich in purchases and purchases[rich]
    assert player not in purchases
    assert service.get_upgrade_levels(player) == {a: 0 for a in UPGRADE_AREAS}
    remaining = test_db.get_team(rich).budget
    assert remaining >= 40_000_000.0 * 0.10
    assert remaining <= 40_000_000.0 * (1 - 0.35) + max(
        upgrade_cost(a, 0, "SINGLE_SEATER") for a in UPGRADE_AREAS
    )


@pytest.mark.unit
def test_race_income_pays_every_team_once(test_db):
    winner = _create_team(test_db, "Winner", 60.0, budget=0.0)
    runner_up = _create_team(test_db, "Runner Up", 60.0, budget=0.0)
    d1 = _create_driver(test_db, "D1", winner, 70.0)
    d2 = _create_driver(test_db, "D2", runner_up, 60.0)

    with test_db.get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS career_championships (
                id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL,
                name TEXT NOT NULL, discipline TEXT NOT NULL, tier TEXT NOT NULL,
                season_length INTEGER NOT NULL, current_season INTEGER NOT NULL DEFAULT 1,
                is_active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS career_races (
                id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL,
                career_championship_id INTEGER NOT NULL, track_id INTEGER NOT NULL,
                season INTEGER NOT NULL, round_number INTEGER NOT NULL,
                race_date TEXT NOT NULL, weather_conditions TEXT, laps INTEGER,
                status TEXT NOT NULL DEFAULT 'scheduled'
            );
            CREATE TABLE IF NOT EXISTS career_race_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL,
                career_race_id INTEGER NOT NULL, driver_id INTEGER NOT NULL,
                team_id INTEGER, position INTEGER, points INTEGER DEFAULT 0,
                fastest_lap INTEGER DEFAULT 0, dnf_reason TEXT, grid_position INTEGER,
                UNIQUE(career_race_id, driver_id)
            );
            """
        )
        champ = conn.execute(
            "INSERT INTO career_championships (player_id, name, discipline, tier, season_length) "
            "VALUES ('p1', 'Series', 'SINGLE_SEATER', 'TIER_1', 1)"
        ).lastrowid
        race = conn.execute(
            "INSERT INTO career_races (player_id, career_championship_id, track_id, season, round_number, race_date, status) "
            "VALUES ('p1', ?, 1, 1, 1, '2026-01-01', 'completed')",
            (champ,),
        ).lastrowid
        conn.executemany(
            "INSERT INTO career_race_results (player_id, career_race_id, driver_id, team_id, position) VALUES ('p1', ?, ?, ?, ?)",
            [(race, d1, winner, 1), (race, d2, runner_up, 2)],
        )
        conn.commit()

    service = UpgradeService(test_db)
    assert service.award_pending_income("p1", season=1) == 2
    assert service.award_pending_income("p1", season=1) == 0  # idempotent

    winner_budget = test_db.get_team(winner).budget
    runner_budget = test_db.get_team(runner_up).budget
    assert winner_budget > runner_budget > 0.0
    assert winner_budget == pytest.approx(service.race_payout(1, "TIER_1", "SINGLE_SEATER"))


@pytest.mark.unit
def test_race_income_marker_for_race_1_does_not_shadow_race_10(test_db):
    """Paying race 1 must not mark race 10 (same id prefix) as already paid."""
    team = _create_team(test_db, "Prefix Team", 60.0, budget=0.0)
    driver = _create_driver(test_db, "D1", team, 70.0)

    with test_db.get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS career_championships (
                id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL,
                name TEXT NOT NULL, discipline TEXT NOT NULL, tier TEXT NOT NULL,
                season_length INTEGER NOT NULL, current_season INTEGER NOT NULL DEFAULT 1,
                is_active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS career_races (
                id INTEGER PRIMARY KEY, player_id TEXT NOT NULL,
                career_championship_id INTEGER NOT NULL, track_id INTEGER NOT NULL,
                season INTEGER NOT NULL, round_number INTEGER NOT NULL,
                race_date TEXT NOT NULL, weather_conditions TEXT, laps INTEGER,
                status TEXT NOT NULL DEFAULT 'scheduled'
            );
            CREATE TABLE IF NOT EXISTS career_race_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL,
                career_race_id INTEGER NOT NULL, driver_id INTEGER NOT NULL,
                team_id INTEGER, position INTEGER, points INTEGER DEFAULT 0,
                fastest_lap INTEGER DEFAULT 0, dnf_reason TEXT, grid_position INTEGER,
                UNIQUE(career_race_id, driver_id)
            );
            """
        )
        champ = conn.execute(
            "INSERT INTO career_championships (player_id, name, discipline, tier, season_length) "
            "VALUES ('p1', 'Series', 'SINGLE_SEATER', 'TIER_1', 10)"
        ).lastrowid
        for race_id, round_number in ((1, 1), (10, 10)):
            conn.execute(
                "INSERT INTO career_races (id, player_id, career_championship_id, track_id, season, round_number, race_date, status) "
                "VALUES (?, 'p1', ?, 1, 1, ?, '2026-01-01', 'completed')",
                (race_id, champ, round_number),
            )
            conn.execute(
                "INSERT INTO career_race_results (player_id, career_race_id, driver_id, team_id, position) "
                "VALUES ('p1', ?, ?, ?, 1)",
                (race_id, driver, team),
            )
        conn.commit()

    service = UpgradeService(test_db)
    assert service.award_race_income(1) == 1
    assert service.award_race_income(10) == 1
    assert service.award_race_income(10) == 0
    expected = 2 * service.race_payout(1, "TIER_1", "SINGLE_SEATER")
    assert test_db.get_team(team).budget == pytest.approx(expected)


@pytest.mark.unit
def test_ai_spending_for_a_season_runs_once_per_team(test_db):
    """A retried off-season must not let a team spend twice for the same season."""
    _create_team(test_db, "Spender", 60.0, budget=80_000_000.0)
    service = UpgradeService(test_db)

    first = service.run_ai_upgrade_spending(
        "SINGLE_SEATER", rng=random.Random(5), season=1
    )
    assert first
    budget_after_first = {t.id: t.budget for t in test_db.get_teams_by_discipline("SINGLE_SEATER")}

    second = service.run_ai_upgrade_spending(
        "SINGLE_SEATER", rng=random.Random(5), season=1
    )
    assert second == {}
    assert {t.id: t.budget for t in test_db.get_teams_by_discipline("SINGLE_SEATER")} == budget_after_first

    # The next off-season spends again.
    assert service.run_ai_upgrade_spending("SINGLE_SEATER", rng=random.Random(5), season=2)


# ---------------------------------------------------------------------------
# Pace must not depend on tier or budget
# ---------------------------------------------------------------------------
@pytest.mark.unit
def test_realtime_team_multiplier_ignores_tier_and_budget():
    engine = RealtimeRaceEngine(seed=1)
    poor_tier_3 = _team(1, "TIER_3", 1_000_000.0, ops=70.0)
    rich_tier_1 = _team(2, "TIER_1", 150_000_000.0, ops=70.0)
    developed = _team(3, "TIER_3", 1_000_000.0, ops=70.0, car_rating=0.8)

    assert engine._get_team_multiplier(poor_tier_3) == pytest.approx(
        engine._get_team_multiplier(rich_tier_1)
    )
    assert engine._get_team_multiplier(developed) > engine._get_team_multiplier(
        poor_tier_3
    )


@pytest.mark.unit
def test_base_engine_team_performance_ignores_tier_and_budget():
    engine = SingleSeaterEngine(seed=1)
    poor_tier_3 = _team(1, "TIER_3", 1_000_000.0, ops=60.0)
    rich_tier_1 = _team(2, "TIER_1", 150_000_000.0, ops=60.0)
    developed = _team(3, "TIER_3", 1_000_000.0, ops=60.0, car_rating=1.0)

    assert engine._calculate_team_performance(poor_tier_3) == pytest.approx(
        engine._calculate_team_performance(rich_tier_1)
    )
    assert engine._calculate_team_performance(developed) > engine._calculate_team_performance(
        poor_tier_3
    )


@pytest.mark.unit
def test_ai_spending_still_buys_cheaper_areas_when_an_expensive_one_is_unaffordable(
    test_db,
):
    team_id = _create_team(test_db, "Tight AI", 60.0, budget=6_000_000.0)
    service = UpgradeService(test_db)
    # 35% of 6M is 2.1M: power (2.5M) is unaffordable, operations (1.5M) is not.
    purchases = service.run_ai_upgrade_spending("SINGLE_SEATER", rng=random.Random(3))

    assert purchases[team_id]
    assert all(p["area"] != "power" for p in purchases[team_id])
