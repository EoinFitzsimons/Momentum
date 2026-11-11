"""Focused tests for live race timing, track grip, and wet-weather foundations."""

from __future__ import annotations

import pytest

from momentum.engine.base_race_engine import RacingDiscipline
from momentum.engine.realtime_race_engine import DriverState, RealtimeRaceEngine
from momentum.engine.track_physics import RacingLine, TrackMap, TrackSection
from momentum.database.models import Driver, Team, Track
from momentum.race_settings import normalize_race_settings


def _driver() -> Driver:
    return Driver(
        id=1,
        name="Test Driver",
        nationality="GBR",
        birth_date="2000-01-01",
        current_team_id=1,
        preferred_discipline="SINGLE_SEATER",
    )


def _team() -> Team:
    return Team(
        id=1,
        name="Test Team",
        nationality="GBR",
        discipline="SINGLE_SEATER",
        tier="TIER_1",
        budget=100.0,
    )


def _track() -> Track:
    return Track(
        id=1,
        name="Test Circuit",
        country="GBR",
        primary_discipline=RacingDiscipline.SINGLE_SEATER.value,
        length_km=5.0,
        turns=8,
        avg_speed_kmh=160.0,
        surface_grip=1.0,
    )


def test_race_settings_accept_uncapped_rendering_and_bound_speed():
    settings = normalize_race_settings(
        {"render_fps": 0, "simulation_speed": 100.0}
    )

    assert settings["render_fps"] == 0
    assert settings["simulation_speed"] == pytest.approx(20.0)


def test_track_lookup_wraps_across_start_line():
    track_map = TrackMap(_track())

    section, corner = track_map.get_section_at_position(
        track_map.track.length_km * 1000.0 - 1.0
    )

    assert corner is not None
    assert section in {
        TrackSection.SLOW_CORNER,
        TrackSection.MEDIUM_CORNER,
        TrackSection.FAST_CORNER,
    }


def test_wet_tyres_outperform_dry_tyres_on_a_wet_corner():
    engine = RealtimeRaceEngine(seed=7)
    engine.track_map = TrackMap(_track())
    engine.track_conditions = {"grip_level": 1.0, "track_wetness": 0.8}
    engine.weather_conditions = {"precipitation": 4.0}
    driver = _driver()
    state = DriverState(1, driver.name, driver, _team())
    state.racing_line = RacingLine.IDEAL
    section, corner = engine.track_map.get_section_at_position(0.0)

    state.tyre_compound = "medium"
    dry_grip = engine._live_grip_multiplier(state, section, corner)
    state.tyre_compound = "wet"
    wet_grip = engine._live_grip_multiplier(state, section, corner)

    assert wet_grip > dry_grip


def test_off_line_has_less_grip_than_the_ideal_line():
    engine = RealtimeRaceEngine(seed=7)
    engine.track_map = TrackMap(_track())
    engine.track_conditions = {"grip_level": 1.0, "track_wetness": 0.0}
    engine.weather_conditions = {"precipitation": 0.0}
    driver = _driver()
    state = DriverState(1, driver.name, driver, _team())
    section, corner = engine.track_map.get_section_at_position(0.0)

    state.racing_line = RacingLine.IDEAL
    ideal_grip = engine._live_grip_multiplier(state, section, corner)
    state.racing_line = RacingLine.OFF_LINE
    off_line_grip = engine._live_grip_multiplier(state, section, corner)

    assert off_line_grip < ideal_grip
