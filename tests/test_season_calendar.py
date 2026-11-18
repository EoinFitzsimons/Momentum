"""A season is a designed calendar, not the track table in id order."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest

from momentum.data.circuit_schema import load_circuits
from momentum.engine.race_format import race_format_for
from momentum.engine.season_calendar import (
    REGION_TOUR,
    plan_calendar,
    plan_season,
    region_of,
    season_dates,
    season_year,
)


def _track(track_id: int, name: str, country: str) -> SimpleNamespace:
    return SimpleNamespace(id=track_id, name=name, country=country)


TRACKS = [
    _track(1, "Zeelandring", "Netherlands"),
    _track(2, "Andes Raceway", "Chile"),
    _track(3, "Lusail Raceway", "Qatar"),
    _track(4, "Kanto Raceway", "Japan"),
    _track(5, "Bavaria Ring", "Germany"),
    _track(6, "Great Lakes Raceway", "United States"),
    _track(7, "Table Bay Raceway", "South Africa"),
    _track(8, "Yas Raceway", "United Arab Emirates"),
]


def test_season_travels_region_by_region():
    order = [region_of(t.country) for t in plan_season(TRACKS, len(TRACKS))]
    assert order == sorted(order, key=REGION_TOUR.index)
    assert order[0] == "Middle East" and order[-1] == "Americas"


def test_short_season_draws_from_every_region_and_keeps_tour_order():
    names = [t.name for t in plan_season(TRACKS, 5)]
    assert names == [
        "Lusail Raceway", "Kanto Raceway", "Bavaria Ring", "Table Bay Raceway", "Andes Raceway",
    ]


def test_a_season_longer_than_the_circuit_list_repeats_the_tour():
    season = plan_season(TRACKS[:3], 7)
    assert len(season) == 7
    assert [t.id for t in season[:3]] == [t.id for t in season[3:6]]


def test_season_dates_run_march_to_november_on_sundays_with_a_summer_break():
    dates = season_dates(20, datetime(2026, 1, 1))
    assert len(dates) == 20
    assert all(d.weekday() == 6 for d in dates)
    assert dates[0] == datetime(2026, 3, 1)
    assert dates[-1] == datetime(2026, 11, 29)
    assert dates == sorted(dates) and len(set(dates)) == 20
    assert not any(d.month == 8 and d.day <= 21 for d in dates)


def test_eight_rounds_are_spread_across_the_season_not_fortnightly():
    dates = season_dates(8, datetime(2026, 1, 1))
    gaps = {(b - a).days for a, b in zip(dates, dates[1:])}
    assert min(gaps) >= 28


def test_a_season_started_after_the_opener_is_next_years():
    assert season_year(datetime(2026, 1, 1)) == 2026
    assert season_year(datetime(2026, 11, 18)) == 2027
    assert season_dates(3, datetime(2026, 11, 18))[0].year == 2027


def test_rounds_come_from_the_discipline_format():
    calendar = plan_calendar(TRACKS, "ENDURANCE", datetime(2026, 1, 1))
    assert len(calendar) == race_format_for("ENDURANCE").season_rounds == 8
    assert [r.round_number for r in calendar] == list(range(1, 9))
    assert calendar[0].date < calendar[-1].date


@pytest.mark.parametrize("discipline", ["SINGLE_SEATER", "PRODUCTION_TOURING", "URBAN_STREET",
                                        "DRAG_ACCELERATION", "SPRINT_RALLYCROSS", "ENDURANCE"])
def test_every_shipped_discipline_fills_its_season_from_its_own_circuits(discipline):
    circuits = [c for c in load_circuits() if c.discipline_key == discipline]
    rounds = race_format_for(discipline).season_rounds
    season = plan_season(circuits, rounds)
    assert len(season) == rounds
    assert len({c.name for c in season}) == rounds
