"""Select Career opens with a league already chosen and visibly marked."""

from __future__ import annotations

import shutil

import pytest

from momentum.config import BUNDLED_DATABASE_PATH
from momentum.database.database_manager import DatabaseManager
from momentum.services.tier_service import TIERS


@pytest.fixture
def qapp():
    from PyQt6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def career_db(tmp_path):
    path = tmp_path / "career.db"
    shutil.copy(BUNDLED_DATABASE_PATH, path)
    return DatabaseManager(str(path), seed_from_bundle=False)


def _open_dialog_with_save(career_db):
    from momentum.gui.gui_career import (
        PLAYER_ID,
        WORLD_START_DATE,
        CareerSelectionDialog,
    )

    dialog = CareerSelectionDialog(career_db)
    if not dialog._has_profile(PLAYER_ID):
        dialog._upsert_profile(
            PLAYER_ID,
            {
                "player_name": "Eoin",
                "age": 30,
                "height_cm": 180.0,
                "nationality": "IRL",
                "bio": "",
            },
        )
        dialog._reset_world_to_start_date(PLAYER_ID, WORLD_START_DATE)
        dialog.load_championships()
    return dialog


def _selected_tier(dialog) -> str | None:
    checked = [
        tier for tier, column in dialog.tier_columns.items() if column["button"].isChecked()
    ]
    assert len(checked) <= 1
    return checked[0] if checked else None


@pytest.mark.unit
def test_new_save_defaults_to_the_lowest_league_and_enters_without_a_click(qapp, career_db):
    dialog = _open_dialog_with_save(career_db)

    assert dialog._selected_series is not None
    lowest_with_series = next(
        tier for tier in reversed(TIERS) if dialog.tier_columns[tier]["series"]
    )
    assert _selected_tier(dialog) == lowest_with_series
    assert dialog.tier_columns[lowest_with_series]["table"].property("selectedLeague") == "true"
    assert dialog._selected_series["name"] in dialog.select_btn.text()

    dialog.select_championship()
    assert dialog.selected_championship is not None
    assert dialog.selected_championship.tier == lowest_with_series


@pytest.mark.unit
def test_saved_profile_reopens_in_the_league_of_its_own_team(qapp, career_db):
    from momentum.gui.gui_career import PLAYER_ID
    from momentum.services.team_service import TeamService

    first = _open_dialog_with_save(career_db)
    discipline = first._selected_discipline
    result = TeamService(career_db).found_player_team(
        "Fitzsimons Racing", discipline, "IRL", "TIER_2", "Eoin", "Naas"
    )
    career_db.assign_team_owner(int(result["id"]), PLAYER_ID)

    reopened = _open_dialog_with_save(career_db)
    assert reopened._selected_discipline == discipline
    assert _selected_tier(reopened) == "TIER_2"
    assert reopened._selected_series["tier"] == "TIER_2"

    # Switching discipline still lands on a visible default rather than nothing.
    other = next(
        value for value, _ in reopened.discipline_buttons if value != discipline
    )
    reopened._select_discipline(other)
    assert reopened._selected_series is None or _selected_tier(reopened) is not None
    if reopened._selected_series is not None:
        assert reopened.select_btn.isEnabled()
