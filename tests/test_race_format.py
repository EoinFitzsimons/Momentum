"""Each discipline organises its race day differently."""

from __future__ import annotations

import pytest

from momentum.engine.race_format import (
    DISCIPLINE_FORMATS,
    HEATS_AND_FINAL,
    KNOCKOUT_BRACKET,
    RaceFormat,
    race_format_for,
)
from momentum.services.race_engine_factory import discipline_engine_class


@pytest.mark.unit
@pytest.mark.parametrize("discipline", sorted(DISCIPLINE_FORMATS))
def test_every_engine_declares_the_format_the_game_uses(discipline):
    engine_cls = discipline_engine_class(discipline)
    assert engine_cls is not None
    assert isinstance(engine_cls.race_format, RaceFormat)
    assert race_format_for(discipline) is engine_cls.race_format


@pytest.mark.unit
def test_grid_sizes_follow_the_format_the_league_and_the_track():
    single = race_format_for("SINGLE_SEATER")
    assert single.grid_size(5000.0, "TIER_1") == 30
    assert single.grid_size(5000.0, "TIER_5") == 40
    assert single.grid_size(2200.0, "TIER_5") == 20, "short tracks take fewer cars"
    assert single.grid_size(5000.0, "TIER_5", available=12) == 12

    rallycross = race_format_for("SPRINT_RALLYCROSS")
    assert rallycross.race_day == HEATS_AND_FINAL
    assert not rallycross.team_based
    assert rallycross.grid_size(1200.0) == 10

    drag = race_format_for("DRAG_ACCELERATION")
    assert drag.race_day == KNOCKOUT_BRACKET
    assert drag.grid_size(402.0) == 16

    endurance = race_format_for("ENDURANCE")
    assert endurance.cars_per_team == 1
    assert endurance.drivers_per_car == 3
    assert endurance.driver_slots == 4


@pytest.mark.unit
def test_unknown_discipline_falls_back_to_a_grand_prix():
    assert race_format_for("something-new") is DISCIPLINE_FORMATS["SINGLE_SEATER"]


@pytest.mark.unit
def test_drs_is_a_rule_of_the_discipline_and_the_tier():
    assert race_format_for("SINGLE_SEATER").allows_drs("TIER_5")
    endurance = race_format_for("ENDURANCE")
    assert endurance.allows_drs("TIER_1")
    assert not endurance.allows_drs("TIER_2")
    for discipline in ("URBAN_STREET", "PRODUCTION_TOURING", "SPRINT_RALLYCROSS", "DRAG_ACCELERATION"):
        assert not race_format_for(discipline).allows_drs("TIER_1")


@pytest.mark.unit
def test_lower_tier_endurance_field_races_without_drs_zones():
    from momentum.database.models import Team, Track
    from momentum.engine.realtime_race_engine import RealtimeRaceEngine
    from momentum.engine.track_physics import TrackMap

    track = Track(id=1, name="Enduro", country="FR", primary_discipline="ENDURANCE", length_km=6.0, drs_zones=3)

    def field_of(tier):
        return {1: Team(id=1, name="A", nationality="FRA", discipline="ENDURANCE", tier=tier, budget=1)}

    endurance = race_format_for("ENDURANCE")
    assert RealtimeRaceEngine._drs_allowed(endurance, field_of("TIER_1"))
    assert not RealtimeRaceEngine._drs_allowed(endurance, field_of("TIER_3"))
    assert RealtimeRaceEngine._drs_allowed(endurance, {})  # no team information keeps the circuit's zones
    assert len(TrackMap(track=track, drs_allowed=True).drs_zones) == 3
    assert TrackMap(track=track, drs_allowed=False).drs_zones == []
