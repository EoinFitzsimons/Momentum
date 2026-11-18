"""A race halted before the flag yields an honest classification, not a result."""

from __future__ import annotations

import threading

import pytest

from momentum.database.models import Driver, Team, Track
from momentum.engine.realtime_race_engine import RealtimeRaceEngine


@pytest.fixture
def qapp():
    from PyQt6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def _run_stopped_race(stop_after_updates: int = 90) -> dict:
    events: list[dict] = []
    stop_event = threading.Event()
    seen = {"updates": 0}

    def capture(event: dict) -> None:
        events.append(event)
        if event.get("type") == "position_update":
            seen["updates"] += 1
            if seen["updates"] >= stop_after_updates:
                stop_event.set()

    track = Track(
        id=1,
        name="StopTrack",
        country="UK",
        primary_discipline="SINGLE_SEATER",
        length_km=4.0,
    )
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
    RealtimeRaceEngine(seed=3).simulate_race(
        drivers,
        teams,
        track,
        total_laps=5,
        event_callback=capture,
        stop_event=stop_event,
        realtime_speed=50.0,
    )
    finished = [e for e in events if e.get("type") == "race_finished"]
    assert len(finished) == 1
    return finished[0]


@pytest.mark.unit
def test_stopped_race_is_classified_by_distance_without_invented_times():
    payload = _run_stopped_race()
    assert payload["race_stopped"] is True
    results = payload["results"]
    assert len(results) == 4
    running = [r for r in results if not r.get("dnf_reason")]
    assert running, "a two-second stop should leave cars running"
    for entry in running:
        assert entry["status"] == "NOT_CLASSIFIED"
        assert entry["time_seconds"] is None
        assert entry["race_stopped"] is True
    distances = [float(r["distance_m"]) for r in running]
    assert distances == sorted(distances, reverse=True)
    assert len(set(distances)) == len(distances), "cars are ranked by real distance"
    assert [r["position"] for r in results] == list(range(1, len(results) + 1))


@pytest.mark.unit
def test_stopped_race_summary_rows_show_no_time_or_gap(qapp):
    from momentum.gui.gui_race_visual import RaceWindow

    window = RaceWindow.__new__(RaceWindow)
    window.player_driver_id = 2
    stopped_row = {
        "driver_id": 2,
        "driver_name": "Player",
        "time_seconds": None,
        "status": "NOT_CLASSIFIED",
        "race_stopped": True,
    }
    pos, name, time_text, gap_text, _, _, status = window._format_detail_row(
        stopped_row, 0, 0.0, 1
    )
    assert (pos, name) == (1, "Player")
    assert time_text == "-" and gap_text == "-"
    assert status == "Not classified / race stopped"

    dnf_row = {"driver_name": "Out", "time_seconds": None, "dnf_reason": "Crash"}
    _, _, time_text, _, _, _, status = window._format_detail_row(dnf_row, 3, 0.0, 4)
    assert (time_text, status) == ("DNF", "DNF")

    assert window._build_final_time_display(0, stopped_row, 0.0) == "-"
    assert window._position_trend_legend_label({"driver_id": 2, "name": "Player"}) == (
        "Player (you)"
    )
    assert window._position_trend_legend_label({"driver_id": 7, "name": "Rival"}) == (
        "Rival"
    )


@pytest.mark.unit
def test_finished_race_keeps_real_times(qapp):
    from momentum.gui.gui_race_visual import RaceWindow

    window = RaceWindow.__new__(RaceWindow)
    window.player_driver_id = None
    row = {"driver_name": "Winner", "time_seconds": 100.5, "status": "FINISHED"}
    _, _, time_text, gap_text, _, _, status = window._format_detail_row(
        row, 0, 100.5, 1
    )
    assert (time_text, gap_text, status) == ("100.500s", "-", "FINISHED")
    assert window._build_final_time_display(1, {"time_seconds": 102.0}, 100.5) == (
        "+1.50s"
    )
