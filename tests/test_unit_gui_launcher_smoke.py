"""Unit smoke tests for launcher GUI orchestration flows."""

from __future__ import annotations

import os

import pytest


class _SignalStub:
    def __init__(self):
        self.connected = []

    def connect(self, callback):
        self.connected.append(callback)

    def emit(self, *args, **kwargs):
        for callback in self.connected:
            callback(*args, **kwargs)


class _RaceWindowStub:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.return_to_menu = _SignalStub()
        self.next_race = _SignalStub()
        self.player_driver = None
        self.player_team = None
        self.tuning_preset = None
        self.display_mode = None
        self.closed = False

    def set_player_driver(self, driver):
        self.player_driver = driver

    def set_player_team(self, team):
        self.player_team = team

    def set_tuning_preset(self, preset):
        self.tuning_preset = preset

    def set_display_mode(self, mode):
        self.display_mode = mode

    def show(self):
        return None

    def close(self):
        self.closed = True


class _MainMenuStub:
    def __init__(self):
        self.shown = False

    def show(self):
        self.shown = True


class _MainMenuWithSignalStub:
    def __init__(self):
        self.shown = False
        self.start_race_signal = _SignalStub()

    def show(self):
        self.shown = True


@pytest.mark.unit
def test_launcher_start_race_wires_race_window(monkeypatch):
    """Launcher start flow should pass config and connect signals."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    launcher_module = pytest.importorskip("momentum.gui.launcher")

    launcher = launcher_module.MomentumLauncher.__new__(
        launcher_module.MomentumLauncher
    )
    launcher.race_window_class = _RaceWindowStub
    launcher.main_menu_class = object
    launcher.championship_window_class = object
    launcher.main_menu = None
    launcher.race_window = None
    launcher.championship_window = None
    launcher.race_config = {}
    launcher.championship_config = {}

    driver = type("DriverStub", (), {"name": "Player One"})()
    team = type("TeamStub", (), {"id": 44})()
    config = {
        "driver": driver,
        "team": team,
        "track_id": 7,
        "discipline": "SINGLE_SEATER",
        "championship_id": 10,
        "race_id": 20,
        "tuning_preset": "balanced",
        "display_mode": "windowed",
        "mode": "championship",
    }

    launcher.start_race(config)

    assert launcher.race_window is not None
    assert launcher.race_window.kwargs["track_id"] == 7
    assert launcher.race_window.kwargs["discipline"] == "SINGLE_SEATER"
    assert launcher.race_window.kwargs["championship_id"] == 10
    assert launcher.race_window.kwargs["race_id"] == 20
    assert launcher.race_window.player_driver is driver
    assert launcher.race_window.player_team is team
    assert launcher.race_window.tuning_preset == "balanced"
    assert launcher.race_window.display_mode == "windowed"
    assert getattr(launcher.race_window, "_game_mode") == "championship"
    assert len(launcher.race_window.return_to_menu.connected) == 1
    assert len(launcher.race_window.next_race.connected) == 1


@pytest.mark.unit
def test_launcher_return_to_menu_closes_race_and_shows_menu():
    """Returning to menu should close race window and show menu window."""
    launcher_module = pytest.importorskip("momentum.gui.launcher")

    launcher = launcher_module.MomentumLauncher.__new__(
        launcher_module.MomentumLauncher
    )
    launcher.race_window = _RaceWindowStub()
    launcher.main_menu = _MainMenuStub()

    launcher.return_to_menu()

    assert launcher.race_window is None
    assert launcher.main_menu.shown is True


@pytest.mark.unit
def test_launcher_menu_signal_can_automate_start_race_flow():
    """Menu signal emission should drive launcher into race window flow."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    launcher_module = pytest.importorskip("momentum.gui.launcher")

    launcher = launcher_module.MomentumLauncher.__new__(
        launcher_module.MomentumLauncher
    )
    launcher.race_window_class = _RaceWindowStub
    launcher.main_menu_class = _MainMenuWithSignalStub
    launcher.championship_window_class = object
    launcher.main_menu = None
    launcher.race_window = None
    launcher.championship_window = None
    launcher.race_config = {}
    launcher.championship_config = {}

    launcher.show_main_menu()
    assert launcher.main_menu is not None
    assert launcher.main_menu.shown is True

    driver = type("DriverStub", (), {"name": "Player Auto"})()
    team = type("TeamStub", (), {"id": 9})()
    config = {
        "driver": driver,
        "team": team,
        "track_id": 5,
        "discipline": "SINGLE_SEATER",
        "race_id": 12,
        "display_mode": "windowed",
        "mode": "single_race",
    }

    # Automates the same route as a user pressing "Start Race" in the menu.
    launcher.main_menu.start_race_signal.emit(config)

    assert launcher.race_window is not None
    assert launcher.race_window.kwargs["track_id"] == 5
    assert launcher.race_window.kwargs["discipline"] == "SINGLE_SEATER"
    assert launcher.race_window.kwargs["race_id"] == 12
    assert launcher.race_window.player_driver is driver
    assert launcher.race_window.player_team is team
