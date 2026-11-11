"""Unit tests for the urban street (drift-focused) discipline adapter."""

from __future__ import annotations

import pytest

from momentum.engine.base_race_engine import RaceContext, RacingDiscipline
from momentum.engine.disciplines.urban_street.urban_street_discipline import UrbanStreetEngine
from momentum.database.models import Driver, Team, Track


def _build_context() -> RaceContext:
    team = Team(
        id=1,
        name="Street Team",
        nationality="JPN",
        discipline="URBAN_STREET",
        tier="TIER_1",
        budget=120.0,
    )
    driver = Driver(
        id=1,
        name="Street Driver",
        nationality="JPN",
        birth_date="2000-01-01",
        current_team_id=team.id,
    )
    track = Track(
        id=1,
        name="Street Circuit",
        country="JP",
        primary_discipline="URBAN_STREET",
        length_km=3.1,
    )

    return RaceContext(
        discipline=RacingDiscipline.URBAN_STREET,
        track=track,
        drivers=[driver],
        teams={team.id: team},
        total_laps=3,
        track_conditions={
            "player_driver_id": 1,
            "player_team_driver_ids": ["1", 2, "bad"],
            "player_overrides": {"pace_multiplier": 1.1},
            "realtime_speed": "2.5",
            "track_points": [object()],
        },
    )


@pytest.mark.unit
def test_urban_street_adapter_delegates_to_realtime_engine(monkeypatch):
    captured = {}

    class _FakeRealtimeRaceEngine:
        def __init__(self, seed=None):
            self.seed = seed
            self.BASE_SPEED_MPS = 0.0

        def simulate_race(self, **kwargs):
            captured["kwargs"] = kwargs
            captured["BASE_SPEED_MPS"] = self.BASE_SPEED_MPS
            return [{"driver_id": 1, "position": 1}]

    monkeypatch.setattr(
        "momentum.engine.disciplines.urban_street.urban_street_discipline.RealtimeRaceEngine",
        _FakeRealtimeRaceEngine,
    )

    context = _build_context()
    engine = UrbanStreetEngine(seed=7)
    results = engine.simulate_race(context)

    assert results == [{"driver_id": 1, "position": 1}]
    assert captured["BASE_SPEED_MPS"] == pytest.approx(60.0)
    assert captured["kwargs"]["realtime_speed"] == pytest.approx(2.5)
    assert captured["kwargs"]["player_team_driver_ids"] == [1, 2]


@pytest.mark.unit
def test_urban_street_placeholder_for_drift_specific_behaviour():
    engine = UrbanStreetEngine(seed=7)
    # Placeholder for future drift scoring and line/angle weighting tests.
    assert engine.discipline == RacingDiscipline.URBAN_STREET
