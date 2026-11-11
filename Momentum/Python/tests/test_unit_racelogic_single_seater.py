"""Unit tests for RaceLogic single-seater adapter behaviour."""

from __future__ import annotations

import pytest

from RaceLogic.base_race_engine import RaceContext, RacingDiscipline
from RaceLogic.disciplines.single_seater.single_seater_discipline import (
    SingleSeaterEngine,
)
from database.models import Driver, Team, Track


def _build_minimal_context() -> RaceContext:
    """Create minimal race context used by single-seater unit tests."""
    team = Team(
        id=1,
        name="Test Team",
        nationality="GBR",
        discipline="SINGLE_SEATER",
        tier="TIER_1",
        budget=120.0,
    )
    driver = Driver(
        id=1,
        name="Test Driver",
        nationality="GBR",
        birth_date="2000-01-01",
        current_team_id=team.id,
    )
    track = Track(
        id=1,
        name="Test Circuit",
        country="UK",
        primary_discipline="SINGLE_SEATER",
        length_km=4.2,
    )

    return RaceContext(
        discipline=RacingDiscipline.SINGLE_SEATER,
        track=track,
        drivers=[driver],
        teams={team.id: team},
        total_laps=3,
        track_conditions={
            "tuning_preset": "aggressive",
            "player_driver_id": 1,
            "player_team_driver_ids": ["1", 2, "bad"],
            "player_overrides": {"pace_multiplier": 1.1},
            "realtime_speed": "2.5",
            "track_points": [object(), object()],
        },
    )


@pytest.mark.unit
def test_single_seater_get_attribute_weights_has_core_keys():
    """Single-seater weight map should include core performance keys."""
    engine = SingleSeaterEngine(seed=7)
    weights = engine.get_attribute_weights()

    assert "raw_speed" in weights
    assert "consistency" in weights
    assert "cornering_skill" in weights
    assert weights["raw_speed"] > 0


@pytest.mark.unit
def test_single_seater_simulation_delegates_to_realtime_engine(monkeypatch):
    """Adapter should tune and forward context data to realtime engine."""
    captured: dict = {}

    class FakeRealtimeRaceEngine:
        def __init__(self, seed=None):
            self.seed = seed
            self.SLIPSTREAM_BONUS = 0.0

        def simulate_race(self, **kwargs):
            captured["kwargs"] = kwargs
            captured["slipstream_bonus"] = self.SLIPSTREAM_BONUS
            return [{"driver_id": 1, "position": 1}]

    monkeypatch.setattr(
        "RaceLogic.disciplines.single_seater.single_seater_discipline.RealtimeRaceEngine",
        FakeRealtimeRaceEngine,
    )

    context = _build_minimal_context()
    engine = SingleSeaterEngine(seed=5)
    results = engine.simulate_race(context)

    assert results == [{"driver_id": 1, "position": 1}]
    assert captured["kwargs"]["drivers"] == context.drivers
    assert captured["kwargs"]["teams"] == context.teams
    assert captured["kwargs"]["track"] == context.track
    assert captured["kwargs"]["total_laps"] == context.total_laps
    assert captured["kwargs"]["player_driver_id"] == 1
    assert captured["kwargs"]["player_team_driver_ids"] == [1, 2]
    assert captured["kwargs"]["player_overrides"] == {"pace_multiplier": 1.1}
    assert captured["kwargs"]["realtime_speed"] == pytest.approx(2.5)

    # Aggressive preset should increase slipstream effect to 0.12.
    assert captured["slipstream_bonus"] == pytest.approx(0.12)
