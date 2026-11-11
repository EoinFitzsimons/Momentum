"""Property-based tests using Hypothesis for core performance functions."""

import pytest
from hypothesis import given, strategies as st  # pyright: ignore[reportMissingImports]
from momentum.engine.base_race_engine import RaceContext, RacingDiscipline
from momentum.database.models import Driver, Team, Track
from momentum.services.race_engine_factory import create_discipline_engine


@pytest.mark.unit
@given(
    speed=st.floats(min_value=0.0, max_value=100.0),
    racecraft=st.floats(min_value=0.0, max_value=100.0),
    consistency=st.floats(min_value=0.0, max_value=100.0),
)
def test_base_performance_property(speed, racecraft, consistency):
    # Construct a minimal discipline adapter (single seater) and driver
    driver = Driver(id=1, name="P", nationality="GBR", birth_date="1990-01-01")
    driver.speed = speed
    driver.racecraft = racecraft
    driver.consistency = consistency

    team = Team(
        id=1,
        name="T",
        nationality="GBR",
        discipline="SINGLE_SEATER",
        tier="TIER_1",
        budget=1e7,
    )
    track = Track(
        id=1, name="T", country="UK", primary_discipline="SINGLE_SEATER", length_km=5.0
    )

    context = RaceContext(
        discipline=RacingDiscipline.SINGLE_SEATER,
        track=track,
        drivers=[driver],
        teams={team.id: team},
        total_laps=1,
    )

    adapter = create_discipline_engine(context, seed=1)
    assert adapter is not None
    # Use the adapter's calculate_base_performance via protected method
    val = adapter.calculate_base_performance(driver, team, context)
    assert isinstance(val, float)
    assert 0.0 <= val <= 1.0
