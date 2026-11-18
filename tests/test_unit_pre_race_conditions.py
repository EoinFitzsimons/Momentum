"""Pre-Race Setup weather and starting tyres reach the engine's starting state."""

from __future__ import annotations

import threading

import pytest

from momentum.database.models import Driver, Team, Track
from momentum.engine.base_race_engine import RaceContext, RacingDiscipline, apply_forecast
from momentum.engine.realtime_race_engine import RealtimeRaceEngine
from momentum.services.race_simulation_api import _context_conditions


def _track() -> Track:
    return Track(
        id=1,
        name="Forecast Park",
        country="UK",
        primary_discipline="SINGLE_SEATER",
        length_km=4.0,
    )


def _field():
    teams = {
        i: Team(
            id=i,
            name=f"Team {i}",
            nationality="GBR",
            discipline="SINGLE_SEATER",
            tier="TIER_1",
            budget=100.0,
        )
        for i in (1, 2)
    }
    drivers = [
        Driver(
            id=i,
            name=f"D{i}",
            nationality="GBR",
            birth_date="1990-01-01",
            current_team_id=1 + (i % 2),
            preferred_discipline="SINGLE_SEATER",
        )
        for i in range(1, 5)
    ]
    return drivers, teams


@pytest.mark.unit
def test_apply_forecast_writes_engine_inputs():
    drivers, teams = _field()
    context = RaceContext(
        discipline=RacingDiscipline.SINGLE_SEATER,
        track=_track(),
        drivers=drivers,
        teams=teams,
        total_laps=3,
    )
    assert apply_forecast(context, "Rainy") == "rainy"
    assert context.weather_conditions["precipitation"] == 4.0
    assert context.track_conditions["track_wetness"] == 0.5
    assert apply_forecast(context, "nonsense") is None
    assert context.track_conditions["forecast"] == "rainy"

    conditions = _context_conditions(context)
    assert conditions["weather_conditions"]["precipitation"] == 4.0
    assert conditions["track_conditions"]["track_wetness"] == 0.5
    assert _context_conditions(None) == {}


def _run_one_frame(weather, track_conditions, player_driver_id, player_team_driver_ids):
    drivers, teams = _field()
    stop_event = threading.Event()

    def capture(event: dict) -> None:
        if event.get("type") == "position_update":
            stop_event.set()

    engine = RealtimeRaceEngine(seed=1)
    engine.simulate_race(
        drivers,
        teams,
        _track(),
        total_laps=3,
        event_callback=capture,
        stop_event=stop_event,
        realtime_speed=50.0,
        player_driver_id=player_driver_id,
        player_team_driver_ids=player_team_driver_ids,
        weather_conditions=weather,
        track_conditions=track_conditions,
    )
    return engine


@pytest.mark.unit
def test_chosen_compound_and_weather_arrive_in_the_starting_state():
    drivers, teams = _field()
    context = RaceContext(
        discipline=RacingDiscipline.SINGLE_SEATER,
        track=_track(),
        drivers=drivers,
        teams=teams,
        total_laps=3,
    )
    apply_forecast(context, "Rainy")
    context.track_conditions["starting_tyre_compound"] = "soft"

    engine = _run_one_frame(
        context.weather_conditions, context.track_conditions, 2, [2, 4]
    )
    assert engine.weather_conditions["precipitation"] == 4.0
    assert engine.track_conditions["track_wetness"] == 0.5
    states = engine._current_race_state.driver_states
    assert states[2].tyre_compound == "soft"
    assert states[4].tyre_compound == "soft"
    # AI teams read the wet track rather than starting on dry defaults.
    assert states[1].tyre_compound == "wet"
    assert states[3].tyre_compound == "wet"


@pytest.mark.unit
def test_dry_default_keeps_mediums_and_intermediate_maps_to_the_wet_profile():
    engine = _run_one_frame(
        {"precipitation": 0.0}, {"starting_tyre_compound": "Intermediate"}, 1, [1]
    )
    states = engine._current_race_state.driver_states
    assert states[1].tyre_compound == "wet"
    assert states[2].tyre_compound == "medium"


@pytest.mark.unit
def test_launcher_hands_dialog_choices_to_the_race_window():
    from momentum.gui import launcher as launcher_module

    class _Signal:
        def connect(self, _cb):
            pass

    class _Window:
        def __init__(self, **_kwargs):
            self.return_to_menu = _Signal()
            self.next_race = _Signal()
            self.conditions = None

        def set_player_driver(self, _d):
            pass

        def set_player_team(self, _t):
            pass

        def set_tuning_preset(self, _p):
            pass

        def set_display_mode(self, _m):
            pass

        def set_accessibility_profile(self, _a):
            pass

        def set_pre_race_conditions(self, weather, tyre_strategy):
            self.conditions = (weather, tyre_strategy)

        def show(self):
            pass

    launcher = launcher_module.MomentumLauncher.__new__(launcher_module.MomentumLauncher)
    launcher.race_window_class = _Window
    launcher.main_menu = None
    launcher.race_window = None
    launcher.race_config = {}
    launcher.accessibility_settings = {}
    launcher.start_race(
        {
            "mode": "championship",
            "track_id": 1,
            "driver": None,
            "team": None,
            "weather": "Storm",
            "tyre_strategy": "Wet",
        }
    )
    assert launcher.race_window.conditions == ("Storm", "Wet")


@pytest.mark.unit
def test_race_window_context_carries_forecast_and_compound():
    from PyQt6.QtWidgets import QApplication

    QApplication.instance() or QApplication([])
    from momentum.gui.gui_race_visual import RaceWindow
    from momentum.race_settings import normalize_race_settings

    drivers, teams = _field()
    window = RaceWindow.__new__(RaceWindow)
    window.track = _track()
    window.drivers = drivers
    window.player_driver_id = 2
    window.player_team_driver_ids = [2, 4]
    window.player_overrides = {}
    window.race_settings = normalize_race_settings({})
    window.stop_event = threading.Event()
    window.tuning_preset = "balanced"
    window._initial_discipline = "SINGLE_SEATER"
    window._race_total_laps = 3
    window.set_pre_race_conditions("Wet", "Hard")

    context = window._build_race_context(lambda _e: None, None, teams)
    assert context.track_conditions["forecast"] == "wet"
    assert context.track_conditions["track_wetness"] == 0.8
    assert context.weather_conditions["precipitation"] == 2.0
    assert context.track_conditions["starting_tyre_compound"] == "hard"
