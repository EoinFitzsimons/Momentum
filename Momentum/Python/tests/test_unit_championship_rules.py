"""Unit tests for championship points rules."""

import pytest

from services.championship_service import ChampionshipService


@pytest.mark.unit
def test_calculate_points_single_seater_includes_fastest_lap_bonus(test_db):
    service = ChampionshipService(test_db)

    no_bonus = service.calculate_points(
        position=1, discipline="SINGLE_SEATER", fastest_lap=False
    )
    with_bonus = service.calculate_points(
        position=1, discipline="SINGLE_SEATER", fastest_lap=True
    )

    assert no_bonus == 25
    assert with_bonus == 26


@pytest.mark.unit
def test_calculate_points_fastest_lap_bonus_not_awarded_outside_top_ten(test_db):
    service = ChampionshipService(test_db)

    points = service.calculate_points(
        position=11, discipline="SINGLE_SEATER", fastest_lap=True
    )
    assert points == 0


@pytest.mark.unit
def test_calculate_points_out_of_range_position_returns_zero(test_db):
    service = ChampionshipService(test_db)

    assert service.calculate_points(position=0, discipline="ENDURANCE") == 0
    assert service.calculate_points(position=999, discipline="ENDURANCE") == 0


@pytest.mark.unit
def test_calculate_points_uses_discipline_specific_table(test_db):
    service = ChampionshipService(test_db)

    ss_p1 = service.calculate_points(position=1, discipline="SINGLE_SEATER")
    drag_p1 = service.calculate_points(position=1, discipline="DRAG_ACCELERATION")

    assert ss_p1 == 25
    assert drag_p1 == 20
