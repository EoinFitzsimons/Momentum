"""The bundled seed is copied only into the default per-user save."""

import sqlite3

import pytest

from momentum.database import database_manager as dm


def _drivers(path):
    with sqlite3.connect(path) as conn:
        return conn.execute("SELECT COUNT(1) FROM drivers").fetchone()[0]


@pytest.mark.unit
def test_default_save_is_seeded_from_the_bundle(tmp_path, monkeypatch):
    save = tmp_path / "saves" / "momentum.db"
    monkeypatch.setattr(dm, "DEFAULT_SAVE_PATH", save)
    dm.DatabaseManager(db_path=str(save))
    assert _drivers(save) == _drivers(dm.BUNDLED_DATABASE_PATH) > 0


@pytest.mark.unit
def test_other_paths_start_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(dm, "DEFAULT_SAVE_PATH", tmp_path / "saves" / "momentum.db")
    other = tmp_path / "explicit.db"
    dm.DatabaseManager(db_path=str(other))
    assert _drivers(other) == 0


@pytest.mark.unit
def test_seed_copy_can_be_switched_off_for_the_default_save(tmp_path, monkeypatch):
    save = tmp_path / "saves" / "momentum.db"
    monkeypatch.setattr(dm, "DEFAULT_SAVE_PATH", save)
    dm.DatabaseManager(db_path=str(save), seed_from_bundle=False)
    assert _drivers(save) == 0
