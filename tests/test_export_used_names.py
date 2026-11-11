"""The name export must never write over the database it reads."""

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import export_used_names  # noqa: E402


@pytest.fixture
def world_db(tmp_path):
    path = tmp_path / "world.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE drivers (name TEXT, nationality TEXT)")
        conn.execute("CREATE TABLE staff_members (name TEXT)")
        conn.execute("CREATE TABLE teams (name TEXT, nationality TEXT)")
        conn.execute("CREATE TABLE races (id INTEGER)")
        conn.execute("INSERT INTO drivers VALUES ('Aino Virtanen', 'FIN')")
        conn.execute("INSERT INTO staff_members VALUES ('Marek Nowak')")
        conn.execute("INSERT INTO teams VALUES ('Ito Racing Group', 'JPN')")
        conn.execute("INSERT INTO races VALUES (1)")
    return path


def _tables(path):
    with sqlite3.connect(path) as conn:
        return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


@pytest.mark.unit
@pytest.mark.parametrize("fmt", ["sqlite", "csv"])
def test_export_refuses_to_overwrite_its_source(world_db, fmt):
    code = export_used_names.main(["--db", str(world_db), "--out", str(world_db), "--format", fmt])
    assert code == 2
    assert _tables(world_db) == {"drivers", "staff_members", "teams", "races"}


@pytest.mark.unit
@pytest.mark.skipif(sys.platform.startswith("win"), reason="symlinks need privileges on Windows")
def test_export_refuses_a_symlink_to_its_source(world_db, tmp_path):
    alias = tmp_path / "alias.db"
    alias.symlink_to(world_db)
    code = export_used_names.main(["--db", str(world_db), "--out", str(alias)])
    assert code == 2
    assert _tables(world_db) == {"drivers", "staff_members", "teams", "races"}


@pytest.mark.unit
def test_export_writes_every_name(world_db, tmp_path):
    out = tmp_path / "names.db"
    assert export_used_names.main(["--db", str(world_db), "--out", str(out)]) == 0
    with sqlite3.connect(out) as conn:
        rows = conn.execute("SELECT kind, name FROM used_names ORDER BY kind").fetchall()
    assert rows == [("driver", "Aino Virtanen"), ("staff", "Marek Nowak"), ("team", "Ito Racing Group")]
    assert _tables(world_db) == {"drivers", "staff_members", "teams", "races"}
