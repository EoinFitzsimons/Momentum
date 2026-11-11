"""The shipped world can be rebuilt from source, the same way every time."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from scripts.build_seed_database import PLAY_STATE_TABLES, build
from services.tier_service import TIERS

TEAMS_PER_DISCIPLINE = 10
DRIVERS = None  # every seat plus free agents


def _rows(path: Path, table: str) -> list[tuple]:
    conn = sqlite3.connect(path)
    try:
        cols = [
            row[1]
            for row in conn.execute(f"PRAGMA table_info({table})")
            if row[1] not in ("created_at", "updated_at")
        ]
        return conn.execute(f"SELECT {', '.join(cols)} FROM {table} ORDER BY id").fetchall()
    finally:
        conn.close()


@pytest.fixture(scope="module")
def seed_db(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("seed") / "world.db"
    build(output, seed=11, teams_per_discipline=TEAMS_PER_DISCIPLINE, drivers=DRIVERS)
    return output


@pytest.mark.integration
def test_fresh_build_completes_and_fills_every_league(seed_db):
    conn = sqlite3.connect(seed_db)
    disciplines = [r[0] for r in conn.execute("SELECT DISTINCT discipline FROM teams")]
    assert len(disciplines) == 6
    for discipline in disciplines:
        by_tier = dict(
            conn.execute(
                "SELECT tier, COUNT(1) FROM teams WHERE discipline = ? GROUP BY tier",
                (discipline,),
            ).fetchall()
        )
        assert set(by_tier) == set(TIERS)
        assert sum(by_tier.values()) == TEAMS_PER_DISCIPLINE


@pytest.mark.integration
def test_every_team_has_drivers_staff_and_a_league_budget(seed_db):
    conn = sqlite3.connect(seed_db)
    without_drivers = conn.execute(
        "SELECT COUNT(1) FROM teams t WHERE NOT EXISTS "
        "(SELECT 1 FROM drivers d WHERE d.current_team_id = t.id)"
    ).fetchone()[0]
    without_staff = conn.execute(
        "SELECT COUNT(1) FROM teams t WHERE NOT EXISTS "
        "(SELECT 1 FROM staff_members s WHERE s.current_team_id = t.id)"
    ).fetchone()[0]
    assert without_drivers == 0
    assert without_staff == 0
    short_handed = conn.execute(
        "SELECT COUNT(1) FROM teams t WHERE t.discipline = 'ENDURANCE' AND "
        "(SELECT COUNT(1) FROM drivers d WHERE d.current_team_id = t.id) < 4"
    ).fetchone()[0]
    assert short_handed == 0, "endurance teams need four drivers each"
    assert conn.execute(
        "SELECT COUNT(1) FROM staff_members WHERE name LIKE 'Generated Staff%'"
    ).fetchone()[0] == 0

    budgets = dict(
        conn.execute(
            "SELECT tier, AVG(budget) FROM teams WHERE discipline = 'SINGLE_SEATER' GROUP BY tier"
        ).fetchall()
    )
    ordered = [budgets[tier] for tier in TIERS]
    assert ordered == sorted(ordered, reverse=True)


@pytest.mark.integration
def test_names_are_latin_and_nationalities_lean_towards_heartlands(seed_db):
    conn = sqlite3.connect(seed_db)
    names = [r[0] for r in conn.execute("SELECT name FROM drivers")]
    assert all(name.isascii() for name in names)
    assert all("," not in name for name in names)

    rally = dict(
        conn.execute(
            "SELECT nationality, COUNT(1) FROM drivers "
            "WHERE preferred_discipline = 'SPRINT_RALLYCROSS' GROUP BY nationality"
        ).fetchall()
    )
    nordic = sum(rally.get(code, 0) for code in ("SWE", "NOR", "FIN"))
    assert nordic >= 0.25 * sum(rally.values())
    assert len(rally) > 3, "smaller nations should still appear"


@pytest.mark.integration
def test_tracks_match_source_json_and_no_play_state(seed_db):
    data = json.loads(
        (Path(__file__).resolve().parents[1] / "data" / "circuits_database.json").read_text(
            encoding="utf-8"
        )
    )
    records = data if isinstance(data, list) else data.get("circuits", data)
    conn = sqlite3.connect(seed_db)
    assert conn.execute("SELECT COUNT(1) FROM tracks").fetchone()[0] == len(records)
    # Every circuit must carry a drawable layout, not just its metadata.
    empty_layouts = conn.execute(
        "SELECT COUNT(1) FROM tracks WHERE instructions_json IS NULL "
        "OR json_array_length(instructions_json) < 2"
    ).fetchone()[0]
    assert empty_layouts == 0
    present = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table in PLAY_STATE_TABLES:
        if table in present:
            assert conn.execute(f"SELECT COUNT(1) FROM {table}").fetchone()[0] == 0, table


@pytest.mark.integration
def test_same_seed_builds_the_same_world(tmp_path, seed_db):
    again = tmp_path / "again.db"
    build(again, seed=11, teams_per_discipline=TEAMS_PER_DISCIPLINE, drivers=DRIVERS)
    for table in ("drivers", "teams", "staff_members", "tracks"):
        assert _rows(again, table) == _rows(seed_db, table), table
