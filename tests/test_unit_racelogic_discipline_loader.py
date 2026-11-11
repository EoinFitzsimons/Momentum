"""Unit tests for discipline loader and context-dispatch simulation path."""

from __future__ import annotations

import pytest

from momentum.engine.base_race_engine import RaceContext, RacingDiscipline
from momentum.database.models import Driver, Team, Track
from momentum.services import race_simulation_api


def _build_context(discipline: RacingDiscipline) -> RaceContext:
    team = Team(
        id=1,
        name="Loader Team",
        nationality="GBR",
        discipline=discipline.value,
        tier="TIER_1",
        budget=120.0,
    )
    driver = Driver(
        id=1,
        name="Loader Driver",
        nationality="GBR",
        birth_date="2000-01-01",
        current_team_id=team.id,
    )
    track = Track(
        id=1,
        name="Loader Circuit",
        country="UK",
        primary_discipline=discipline.value,
        length_km=4.0,
    )
    return RaceContext(
        discipline=discipline,
        track=track,
        drivers=[driver],
        teams={team.id: team},
        total_laps=3,
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "discipline,expected_class",
    [
        (RacingDiscipline.SINGLE_SEATER, "SingleSeaterEngine"),
        (RacingDiscipline.PRODUCTION_TOURING, "ProductionTouringEngine"),
        (RacingDiscipline.URBAN_STREET, "UrbanStreetEngine"),
        (RacingDiscipline.DRAG_ACCELERATION, "DragAccelerationEngine"),
        (RacingDiscipline.SPRINT_RALLYCROSS, "SprintRallycrossEngine"),
        (RacingDiscipline.ENDURANCE, "EnduranceEngine"),
    ],
)
def test_load_discipline_engine_resolves_all_disciplines(discipline, expected_class):
    context = _build_context(discipline)

    adapter = race_simulation_api._load_discipline_engine(context, seed=11)

    assert adapter is not None
    assert adapter.__class__.__name__ == expected_class
    assert adapter.discipline == discipline


@pytest.mark.unit
def test_simulate_race_uses_context_adapter_result(monkeypatch):
    context = _build_context(RacingDiscipline.SINGLE_SEATER)

    class _FakeAdapter:
        discipline = RacingDiscipline.SINGLE_SEATER

        def simulate_race(self, incoming_context):
            assert incoming_context is context
            return [{"driver_id": 1, "position": 1, "source": "adapter"}]

    monkeypatch.setattr(
        race_simulation_api,
        "_load_discipline_engine",
        lambda _context, seed=None: _FakeAdapter(),
    )

    results = race_simulation_api.simulate_race(context=context)

    assert results == [{"driver_id": 1, "position": 1, "source": "adapter"}]
