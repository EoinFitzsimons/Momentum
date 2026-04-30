"""Edge-case tests for discipline math: extreme attributes and weather.

These tests verify numeric stability (no NaN/inf), non-negative lap times,
and reasonable bounds under extreme inputs.
"""
from typing import Any, Dict
import math
import pytest

from services.race_engine_factory import create_discipline_engine
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline
from database.models import Driver, Team, Track


@pytest.mark.unit
@pytest.mark.parametrize("discipline", [
    RacingDiscipline.SINGLE_SEATER,
    RacingDiscipline.PRODUCTION_TOURING,
    RacingDiscipline.URBAN_STREET,
    RacingDiscipline.SPRINT_RALLYCROSS,
    RacingDiscipline.ENDURANCE,
])
def test_discipline_extreme_attributes_and_weather(discipline):
    # Build extreme driver attributes
    driver = Driver(id=1, name="Edge", nationality="GBR", birth_date="1990-01-01")
    # Extreme high values
    for attr in [
        'speed','racecraft','consistency','fitness','reactions','pressure','setup_knowledge',
        'fuel_management','tyre_management','feedback','adaptability'
    ]:
        setattr(driver, attr, 1000.0)

    # extreme low driver
    driver2 = Driver(id=2, name="Edge2", nationality="GBR", birth_date="1990-01-01")
    for attr in ['speed','racecraft','consistency']:
        setattr(driver2, attr, -500.0)

    track = Track(id=1, name="EdgeTrack", country="UK", primary_discipline="SINGLE_SEATER", length_km=0.5)
    team1 = Team(id=1, name="T", nationality="GBR", discipline="SINGLE_SEATER", tier="TIER_1", budget=1e7)
    team2 = Team(id=2, name="T2", nationality="GBR", discipline="SINGLE_SEATER", tier="TIER_2", budget=5e6)

    context = RaceContext(
        discipline=discipline,
        track=track,
        drivers=[driver, driver2],
        teams={1: team1, 2: team2},
        total_laps=3,
    )
    context.track_conditions = {
        'precipitation': 100.0,  # absurdly high
        'wind_speed': 200.0,
        'temperature': -50.0,
    }
    # engine expects weather_conditions on context as well
    context.weather_conditions = {
        'precipitation': 100.0,
        'wind_speed': 200.0,
        'temperature': -50.0,
    }

    # Create adapter for discipline
    adapter = create_discipline_engine(context, seed=42)
    assert adapter is not None

    # Call calculate_lap_time for each driver and assert numeric sanity
    t1 = adapter.calculate_lap_time(driver, team1, context, 1, 1)
    t2 = adapter.calculate_lap_time(driver2, team2, context, 1, 2)

    for t in (t1, t2):
        assert t is not None
        assert isinstance(t, float)
        assert not math.isnan(t)
        assert not math.isinf(t)
        assert t >= 0.0, f"Lap time negative: {t}"
