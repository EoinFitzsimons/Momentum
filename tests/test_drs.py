"""DRS: zones from the circuit, permission from the tier, effect in the engine."""

import pytest

from momentum.data.circuit_schema import load_circuits
from momentum.database.models import Driver, Team, Track
from momentum.engine.race_format import race_format_for
from momentum.engine.realtime_race_engine import DriverState, RealtimeRaceEngine
from momentum.engine.track_physics import TrackMap, TrackSection

TRACK = Track(
    id=1, name="Enduro", country="FR", primary_discipline="ENDURANCE",
    length_km=6.0, turns=12, drs_zones=2, longest_straight_m=1000.0,
)
LAP_M = 6000.0
# a shorter main straight, so the zone before turn 1 runs back over the start line
WRAP_TRACK = Track(
    id=2, name="Wrap", country="FR", primary_discipline="ENDURANCE",
    length_km=6.0, turns=12, drs_zones=2, longest_straight_m=600.0,
)


def _engine(drs_allowed: bool) -> RealtimeRaceEngine:
    engine = RealtimeRaceEngine(seed=1)
    engine._race_format = race_format_for("ENDURANCE")
    engine.track_map = TrackMap(track=TRACK, drs_allowed=drs_allowed)
    return engine


def _state(position_m: float, gap_ahead: float, lap: int = 3, tier: str = "TIER_1") -> DriverState:
    driver = Driver(
        id=1, name="D", nationality="FRA", birth_date="1990-01-01", preferred_discipline="ENDURANCE",
    )
    team = Team(id=1, name="A", nationality="FRA", discipline="ENDURANCE", tier=tier, budget=1)
    return DriverState(
        driver_id=1, driver_name="D", driver=driver, team=team,
        position_m=position_m, gap_ahead=gap_ahead, lap=lap,
    )


def _zone_points(track_map: TrackMap):
    for start, end in track_map.drs_zones:
        for k in range(41):
            yield start + k * (end - start) / 40


@pytest.mark.unit
def test_the_main_straight_is_corner_free_and_carries_the_first_zone():
    track_map = TrackMap(track=TRACK)
    assert min(c.position_m for c in track_map.corners) == pytest.approx(1000.0)
    assert track_map.drs_zones[0] == (50.0, 850.0)  # the 800 m before braking for turn 1
    assert track_map.in_drs_zone(500.0) and track_map.in_drs_zone(3 * LAP_M + 500.0)
    assert not track_map.in_drs_zone(900.0)

    wrap_map = TrackMap(track=WRAP_TRACK)
    assert min(c.position_m for c in wrap_map.corners) == pytest.approx(600.0)
    assert wrap_map.in_drs_zone(LAP_M - 10.0)  # the zone runs over the start line ...
    assert wrap_map.in_drs_zone(10.0)
    assert wrap_map.in_drs_zone(440.0)
    assert not wrap_map.in_drs_zone(500.0)  # ... up to the braking point for turn 1


@pytest.mark.unit
def test_every_drs_circuit_in_the_source_has_zones_and_they_are_straights():
    for circuit in load_circuits():
        record = circuit.to_record()
        if not record.get("drs_zones"):
            continue
        track = Track(
            id=1, name=record["name"], country="X", primary_discipline=record["primary_discipline"],
            length_km=record["length_km"], turns=record["turns"], drs_zones=record["drs_zones"],
            longest_straight_m=record["longest_straight_m"],
        )
        track_map = TrackMap(track=track)
        assert track_map.drs_zones, record["name"]
        assert all(
            track_map.get_section_at_position(p)[0] == TrackSection.STRAIGHT for p in _zone_points(track_map)
        ), record["name"]


@pytest.mark.unit
def test_drs_opens_only_in_a_zone_within_detection_after_the_opening_laps():
    engine = _engine(drs_allowed=True)
    inside = 500.0  # on the main straight
    assert engine._drs_available(_state(inside, gap_ahead=0.8))
    assert engine._drs_available(_state(3 * LAP_M + inside, gap_ahead=0.8))  # position_m is cumulative
    assert not engine._drs_available(_state(inside, gap_ahead=1.4))
    assert not engine._drs_available(_state(inside, gap_ahead=0.8, lap=1))
    assert not engine._drs_available(_state(1000.0, gap_ahead=0.8))  # turn 1
    assert not engine._drs_available(_state(880.0, gap_ahead=0.8))  # braking for turn 1
    pitting = _state(inside, gap_ahead=0.8)
    pitting.in_pit_lane = True
    assert not engine._drs_available(pitting)


@pytest.mark.unit
def test_gt_car_in_a_mixed_endurance_field_keeps_its_wing_shut():
    engine = _engine(drs_allowed=True)  # a top-tier prototype in the field keeps the zones
    assert engine._drs_available(_state(500.0, gap_ahead=0.5, tier="TIER_1"))
    assert not engine._drs_available(_state(500.0, gap_ahead=0.5, tier="TIER_2"))


@pytest.mark.unit
def test_a_field_that_may_not_use_drs_never_opens_the_wing():
    engine = _engine(drs_allowed=False)
    assert engine.track_map.drs_zones == []
    assert not engine._drs_available(_state(500.0, gap_ahead=0.5))


@pytest.mark.unit
def test_drs_adds_to_straight_line_speed():
    engine = _engine(drs_allowed=True)
    assert 0 < engine.DRS_BONUS <= engine.SLIPSTREAM_BONUS
