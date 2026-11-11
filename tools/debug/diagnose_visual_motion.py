"""Measure realtime race packets and rendered car motion for jitter diagnosis."""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

repo_root = Path(__file__).resolve().parents[2]

from PyQt6.QtCore import QEventLoop, QTimer, Qt  # noqa: E402
from PyQt6.QtGui import QColor  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

_APP = QApplication.instance() or QApplication([])

from momentum.gui.gui_race_visual import Car, CircuitGenerator, TrackWidget  # noqa: E402
from momentum.engine.realtime_race_engine import RealtimeRaceEngine  # noqa: E402
from momentum.database.models import Driver, Team, Track  # noqa: E402
from momentum.vehicles.appearance_integration import VehicleAppearanceManager  # noqa: E402


@dataclass
class PacketSample:
    wall_time: float
    simulation_time: float
    position_m: float


def _build_entries() -> tuple[list[Driver], dict[int, Team], Track]:
    team = Team(
        id=1,
        name="Motion Probe Team",
        nationality="GBR",
        discipline="SINGLE_SEATER",
        tier="TIER_1",
        budget=100.0,
    )
    drivers = [
        Driver(
            id=1,
            name="Motion Probe Driver",
            nationality="GBR",
            birth_date="2000-01-01",
            current_team_id=team.id,
            preferred_discipline="SINGLE_SEATER",
        )
    ]
    track = Track(
        id=1,
        name="Motion Probe Circuit",
        country="GBR",
        primary_discipline="SINGLE_SEATER",
        length_km=1.0,
        turns=4,
        avg_speed_kmh=150.0,
        surface_grip=1.0,
    )
    return drivers, {team.id: team}, track


def _measure_engine() -> list[PacketSample]:
    drivers, teams, track = _build_entries()
    samples: list[PacketSample] = []

    def capture(event: dict) -> None:
        if event.get("type") != "position_update":
            return
        position = event.get("positions", [])[0]
        samples.append(
            PacketSample(
                wall_time=time.perf_counter(),
                simulation_time=float(event.get("time", 0.0)),
                position_m=float(position.get("position_m", 0.0)),
            )
        )

    RealtimeRaceEngine(seed=7).simulate_race(
        drivers=drivers,
        teams=teams,
        track=track,
        total_laps=1,
        event_callback=capture,
        realtime_speed=5.0,
    )
    return samples


def _measure_widget(samples: list[PacketSample]) -> list[float]:
    app = QApplication.instance() or _APP
    points = CircuitGenerator.generate(track_length_km=1.0)
    widget = TrackWidget(
        track_points=points,
        track_length=1000.0,
        appearance_manager=VehicleAppearanceManager(),
    )
    widget.set_cars([Car(1, "Motion Probe Driver", 0.0, QColor("white"))])
    widget.show()
    widget.start_animation()

    rendered: list[float] = []
    for sample in samples:
        widget.update_car_realtime(
            driver_id=1,
            position_m=sample.position_m,
            lap=0,
            velocity_mps=70.0,
        )
        widget._animate_cars()
        rendered.append(float(widget.cars[0].display_s))
        app.processEvents()

    widget.stop_animation()
    widget.close()
    return rendered


def _measure_route_continuity() -> tuple[float, float]:
    app = QApplication.instance() or _APP
    points = CircuitGenerator.generate(track_length_km=1.0)
    widget = TrackWidget(
        track_points=points,
        track_length=1000.0,
        appearance_manager=VehicleAppearanceManager(),
    )
    route_gap = ((points[-1].x - points[0].x) ** 2 + (points[-1].y - points[0].y) ** 2) ** 0.5
    samples = []
    for index in range(1001):
        point = widget._point_at_s(index)
        if point is not None:
            samples.append((point.x, point.y))
    steps = [
        ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        for (x0, y0), (x1, y1) in zip(samples, samples[1:])
    ]
    widget.close()
    app.processEvents()
    return route_gap, max(steps) if steps else 0.0


def _measure_timer_fairness(render_interval: int) -> tuple[int, int, int]:
    """Count render, packet, and flush timer service over a fixed window."""
    app = QApplication.instance() or _APP
    loop = QEventLoop()
    render_count = 0
    packet_count = 0
    flush_count = 0

    render_timer = QTimer()
    render_timer.setTimerType(Qt.TimerType.PreciseTimer)
    render_timer.setInterval(render_interval)
    packet_timer = QTimer()
    packet_timer.setTimerType(Qt.TimerType.PreciseTimer)
    packet_timer.setInterval(7)
    flush_timer = QTimer()
    flush_timer.setTimerType(Qt.TimerType.PreciseTimer)
    flush_timer.setInterval(8)

    render_timer.timeout.connect(lambda: _increment("render"))
    packet_timer.timeout.connect(lambda: _increment("packet"))
    flush_timer.timeout.connect(lambda: _increment("flush"))
    counters = {"render": 0, "packet": 0, "flush": 0}

    def _increment(key: str) -> None:
        counters[key] += 1

    render_timer.timeout.disconnect()
    packet_timer.timeout.disconnect()
    flush_timer.timeout.disconnect()
    render_timer.timeout.connect(lambda: _increment("render"))
    packet_timer.timeout.connect(lambda: _increment("packet"))
    flush_timer.timeout.connect(lambda: _increment("flush"))
    QTimer.singleShot(500, loop.quit)
    render_timer.start()
    packet_timer.start()
    flush_timer.start()
    loop.exec()
    render_timer.stop()
    packet_timer.stop()
    flush_timer.stop()
    app.processEvents()
    return counters["render"], counters["packet"], counters["flush"]


def _deltas(values: list[float], track_length: float | None = None) -> list[float]:
    result = []
    for previous, current in zip(values, values[1:]):
        delta = current - previous
        if track_length and delta < -(track_length / 2.0):
            delta += track_length
        elif track_length and delta > track_length / 2.0:
            delta -= track_length
        result.append(delta)
    return result


def main() -> int:
    samples = _measure_engine()
    rendered = _measure_widget(samples)
    if len(samples) < 3:
        print(f"INSUFFICIENT PACKETS: {len(samples)}")
        return 1

    wall_intervals = [
        current.wall_time - previous.wall_time
        for previous, current in zip(samples, samples[1:])
    ]
    sim_intervals = [
        current.simulation_time - previous.simulation_time
        for previous, current in zip(samples, samples[1:])
    ]
    packet_deltas = _deltas([sample.position_m for sample in samples], 1000.0)
    render_deltas = _deltas(rendered, 1000.0)

    print(f"PACKETS={len(samples)}")
    print(f"WALL_INTERVAL_MS min={min(wall_intervals) * 1000:.3f} max={max(wall_intervals) * 1000:.3f} avg={sum(wall_intervals) / len(wall_intervals) * 1000:.3f}")
    print(f"SIM_INTERVAL_MS min={min(sim_intervals) * 1000:.3f} max={max(sim_intervals) * 1000:.3f} avg={sum(sim_intervals) / len(sim_intervals) * 1000:.3f}")
    print(f"PACKET_DELTA_M min={min(packet_deltas):.3f} max={max(packet_deltas):.3f} avg={sum(packet_deltas) / len(packet_deltas):.3f}")
    print(f"RENDER_DELTA_M min={min(render_deltas):.3f} max={max(render_deltas):.3f} avg={sum(render_deltas) / len(render_deltas):.3f}")
    print(f"RENDER_BACKWARD_JUMPS={sum(1 for delta in render_deltas if delta < -0.5)}")
    print(f"RENDER_LARGE_JUMPS={sum(1 for delta in render_deltas if abs(delta) > 15.0)}")
    route_gap, max_route_step = _measure_route_continuity()
    print(f"ROUTE_CLOSURE_GAP_M={route_gap:.3f}")
    print(f"ROUTE_MAX_1M_SAMPLE_STEP_M={max_route_step:.3f}")
    for interval in (0, 1, 4):
        render_count, packet_count, flush_count = _measure_timer_fairness(interval)
        print(
            f"TIMER_INTERVAL_MS={interval} render={render_count} "
            f"packets={packet_count} flush={flush_count}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
