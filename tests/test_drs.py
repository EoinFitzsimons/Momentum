"""DRS: zones from the circuit, permission from the tier, effect in the engine."""

import pytest

from momentum.database.models import Driver, Team, Track
from momentum.engine.realtime_race_engine import DriverState, RealtimeRaceEngine
from momentum.engine.track_physics import TrackMap

TRACK = Track(
    id=1, name="Enduro", country="FR", primary_discipline="ENDURANCE",
    length_km=6.0, drs_zones=2, longest_straight_m=1000.0,
)


def _engine(drs_allowed: bool) -> RealtimeRaceEngine:
    engine = RealtimeRaceEngine(seed=1)
    engine.track_map = TrackMap(track=TRACK, drs_allowed=drs_allowed)
    return engine


def _state(position_m: float, gap_ahead: float, lap: int = 3) -> DriverState:
    driver = Driver(
        id=1, name="D", nationality="FRA", birth_date="1990-01-01", preferred_discipline="ENDURANCE",
    )
    team = Team(id=1, name="A", nationality="FRA", discipline="ENDURANCE", tier="TIER_1", budget=1)
    return DriverState(
        driver_id=1, driver_name="D", driver=driver, team=team,
        position_m=position_m, gap_ahead=gap_ahead, lap=lap,
    )


@pytest.mark.unit
def test_drs_opens_only_in_a_zone_within_detection_after_the_opening_laps():
    engine = _engine(drs_allowed=True)
    start, end = engine.track_map.drs_zones[0]
    inside = (start + end) / 2
    assert engine._drs_available(_state(inside, gap_ahead=0.8))
    assert not engine._drs_available(_state(inside, gap_ahead=1.4))
    assert not engine._drs_available(_state(inside, gap_ahead=0.8, lap=1))
    assert not engine._drs_available(_state(end + 50.0, gap_ahead=0.8))
    pitting = _state(inside, gap_ahead=0.8)
    pitting.in_pit_lane = True
    assert not engine._drs_available(pitting)


@pytest.mark.unit
def test_a_field_that_may_not_use_drs_never_opens_the_wing():
    engine = _engine(drs_allowed=False)
    assert engine.track_map.drs_zones == []
    assert not engine._drs_available(_state(3000.0, gap_ahead=0.5))


@pytest.mark.unit
def test_drs_adds_to_straight_line_speed():
    engine = _engine(drs_allowed=True)
    assert engine.DRS_BONUS > 0
    assert 0 < engine.DRS_BONUS <= engine.SLIPSTREAM_BONUS
