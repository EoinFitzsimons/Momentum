"""Finishing a career race from the GUI closes it, pays out and returns to HQ."""

from __future__ import annotations

import shutil
from types import SimpleNamespace

import pytest

from momentum.config import BUNDLED_DATABASE_PATH
from momentum.database.database_manager import DatabaseManager
from momentum.services.career_result_service import (
    complete_career_race,
    persist_career_race_result,
    settle_career_race,
)

PLAYER = "player_1"


@pytest.fixture
def qapp():
    from PyQt6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def career_db(tmp_path, qapp):
    """A seed-world copy with a career save, a player team and a calendar."""
    from momentum.gui.gui_career import PLAYER_ID, WORLD_START_DATE, CareerSelectionDialog
    from momentum.services.team_service import TeamService

    path = tmp_path / "career.db"
    shutil.copy(BUNDLED_DATABASE_PATH, path)
    db = DatabaseManager(str(path), seed_from_bundle=False)
    dialog = CareerSelectionDialog(db)
    dialog._upsert_profile(
        PLAYER_ID,
        {"player_name": "Eoin", "age": 30, "height_cm": 180.0, "nationality": "IRL", "bio": ""},
    )
    dialog._reset_world_to_start_date(PLAYER_ID, WORLD_START_DATE)
    dialog.load_championships()
    series = dialog._selected_series
    result = TeamService(db).found_player_team(
        "Fitzsimons Racing", series["discipline"], "IRL", series["tier"], "Eoin", "Naas"
    )
    db.assign_team_owner(int(result["id"]), PLAYER_ID)
    dialog.select_championship()
    return db, dialog.selected_championship, int(result["id"]), PLAYER_ID


def _first_race(db, championship_id: int) -> dict:
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM career_races WHERE career_championship_id = ? "
            "ORDER BY season, round_number LIMIT 1",
            (championship_id,),
        ).fetchone()
    return dict(row)


def _status(db, race_id: int) -> str:
    with db.get_connection() as conn:
        return str(conn.execute(
            "SELECT status FROM career_races WHERE id = ?", (race_id,)
        ).fetchone()[0])


@pytest.mark.unit
def test_completion_needs_results_and_is_idempotent(career_db):
    db, championship, team_id, player_id = career_db
    race = _first_race(db, int(championship.id))
    race_id = int(race["id"])
    with db.get_connection() as conn:
        conn.execute("UPDATE career_races SET status = 'in-progress' WHERE id = ?", (race_id,))
        conn.commit()

    assert complete_career_race(db, race_id) is False
    assert _status(db, race_id) == "in-progress"
    # Leaving the race window mid-race reopens the round instead of skipping it.
    assert settle_career_race(db, race_id) == "reopened"
    assert _status(db, race_id) == "scheduled"

    driver = db.get_drivers_by_team(team_id)[0]
    persist_career_race_result(db, player_id, race_id, int(driver.id), team_id, 1, 25, True, None, 3)
    assert complete_career_race(db, race_id) is True
    assert _status(db, race_id) == "completed"
    assert complete_career_race(db, race_id) is False
    assert settle_career_race(db, race_id) == "unchanged"


@pytest.mark.unit
def test_completed_race_pays_the_team_through_the_ledger(career_db):
    from momentum.services.finance_service import FinanceService
    from momentum.services.upgrade_service import UpgradeService

    db, championship, team_id, player_id = career_db
    race = _first_race(db, int(championship.id))
    race_id = int(race["id"])
    before = float(db.get_team(team_id).budget)
    ledger_before = len(db.get_budget_transactions(team_id))
    driver = db.get_drivers_by_team(team_id)[0]
    persist_career_race_result(db, player_id, race_id, int(driver.id), team_id, 1, 25, False, None, 1)

    service = UpgradeService(db)
    assert service.award_pending_income(player_id=player_id, season=int(race["season"])) == 0
    assert complete_career_race(db, race_id) is True
    paid = service.award_pending_income(player_id=player_id, season=int(race["season"]))
    assert paid >= 1
    assert float(db.get_team(team_id).budget) > before
    rows = db.get_budget_transactions(team_id)
    assert len(rows) > ledger_before
    assert all(row["source"] for row in rows[ledger_before:])
    assert FinanceService(db).reconcile() == []
    assert service.award_pending_income(player_id=player_id, season=int(race["season"])) == 0


@pytest.mark.unit
def test_race_window_marks_the_career_race_completed_after_saving(career_db):
    from momentum.gui.gui_race_visual import RaceWindow

    db, championship, team_id, player_id = career_db
    race = _first_race(db, int(championship.id))
    race_id = int(race["id"])
    with db.get_connection() as conn:
        conn.execute("UPDATE career_races SET status = 'in-progress' WHERE id = ?", (race_id,))
        conn.commit()
    driver = db.get_drivers_by_team(team_id)[0]
    persist_career_race_result(db, player_id, race_id, int(driver.id), team_id, 2, 18, False, None, 2)

    window = RaceWindow.__new__(RaceWindow)
    window.db = db
    window._race_id = race_id
    window._championship_id = None
    window._game_mode = "career"
    window._save_single_race_result = lambda result: True  # rows already persisted above
    window._save_race_results_if_needed([{"driver_id": int(driver.id)}])
    assert _status(db, race_id) == "completed"


@pytest.mark.unit
def test_return_to_menu_after_a_career_race_goes_to_career_hq(career_db, monkeypatch):
    from momentum.gui import launcher as launcher_module

    db, championship, team_id, player_id = career_db
    race = _first_race(db, int(championship.id))
    race_id = int(race["id"])
    monkeypatch.setattr(launcher_module, "DatabaseManager", lambda *a, **k: db, raising=False)
    import momentum.database.database_manager as dm

    monkeypatch.setattr(dm, "DatabaseManager", lambda *a, **k: db)

    calls = []

    class _Menu:
        career_window = SimpleNamespace(championship=championship)

        def show_career_page(self):
            calls.append("career_page")
            return True

        def show(self):
            calls.append("main_menu")

    launcher = launcher_module.MomentumLauncher.__new__(launcher_module.MomentumLauncher)
    launcher.main_menu = _Menu()
    launcher.race_window = None
    launcher.race_config = {
        "mode": "career",
        "career_championship_id": int(championship.id),
        "race_id": race_id,
        "career_race_id": race_id,
    }
    launcher.return_to_menu()
    assert calls == ["career_page"]

    launcher.race_config = {"mode": "single_race"}
    launcher.return_to_menu()
    assert calls == ["career_page", "main_menu"]


@pytest.mark.unit
def test_career_pre_race_dialog_locks_team_and_driver(career_db):
    from momentum.gui.gui_career import CareerWindow

    db, championship, team_id, player_id = career_db
    race = _first_race(db, int(championship.id))
    from PyQt6.QtWidgets import QMainWindow

    window = CareerWindow.__new__(CareerWindow)
    QMainWindow.__init__(window)
    window.db = db
    window.championship = championship
    window.owned_team = db.get_team(team_id)
    window.selected_driver = db.get_drivers_by_team(team_id)[1]

    dialog = window._pre_race_dialog(race)
    assert dialog.windowTitle().startswith("Pre-Race Setup")
    assert dialog.team_combo.isEnabled() is False
    assert dialog.selected_team.id == team_id
    assert dialog.driver_combo.isEnabled() is False
    assert dialog.selected_driver.id == window.selected_driver.id
    assert dialog.weather_combo.currentText().lower() == str(race["weather_conditions"]).lower()
    assert dialog.start_btn.isEnabled()
    config = dialog.get_race_config()
    assert config["team"].id == team_id
    assert config["driver"].id == window.selected_driver.id
    assert config["race_id"] == int(race["id"])


@pytest.mark.unit
def test_failed_career_settlement_falls_back_to_the_main_menu_once(career_db, monkeypatch):
    from momentum.gui import launcher as launcher_module
    import momentum.services.career_result_service as crs

    db, championship, team_id, player_id = career_db

    def boom(*_args, **_kwargs):
        raise RuntimeError("database is locked")

    monkeypatch.setattr(crs, "settle_career_race", boom)

    calls = []

    class _Menu:
        def show_career_page(self):
            calls.append("career_page")
            return True

        def show(self):
            calls.append("main_menu")

    launcher = launcher_module.MomentumLauncher.__new__(launcher_module.MomentumLauncher)
    launcher.main_menu = _Menu()
    launcher.race_window = None
    launcher.race_config = {"mode": "career", "career_championship_id": int(championship.id), "race_id": 1}
    launcher.return_to_menu()
    assert calls == ["main_menu"]
    assert launcher.race_config == {}
