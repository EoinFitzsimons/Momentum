"""Unit tests for procedural circuit layouts and trackside dressing."""

import math

import numpy as np
import pytest
from scipy.spatial import cKDTree

from momentum.engine.circuit_layout import LayoutSpec, generate_layout, simulate

SPECS = [
    LayoutSpec(length_m=5690, turns=19, left_turns=7, right_turns=12,
               longest_straight_m=1100, tightest_corner_radius_m=63, seed=805676338),
    LayoutSpec(length_m=3200, turns=11, left_turns=6, right_turns=5,
               discipline="PRODUCTION_TOURING", seed=17),
    LayoutSpec(length_m=2400, turns=14, left_turns=8, right_turns=6,
               discipline="URBAN_STREET", seed=99),
    # A long technical circuit: 41 corners in 9.3 km, as dense as the real
    # Nordschleife, which the old length-scaled corners could never fit.
    LayoutSpec(length_m=9290, turns=41, left_turns=20, right_turns=21,
               tightest_corner_radius_m=63.8, seed=5),
    # A kart-sized lap with hairpins every fifty metres.
    LayoutSpec(length_m=820, turns=16, left_turns=7, right_turns=9,
               tightest_corner_radius_m=9, discipline="URBAN_STREET", seed=3),
]


def _self_clearance(xy: np.ndarray, window: int = 60) -> float:
    pairs = cKDTree(xy).query_pairs(r=12.0, output_type="ndarray")
    n = len(xy)
    if len(pairs) == 0:
        return math.inf
    gap = np.abs(pairs[:, 0] - pairs[:, 1])
    distant = np.minimum(gap, n - gap) > window
    if not distant.any():
        return math.inf
    p = pairs[distant]
    return float(np.min(np.linalg.norm(xy[p[:, 0]] - xy[p[:, 1]], axis=1)))


@pytest.fixture(scope="module", params=SPECS, ids=lambda s: f"{s.discipline}-{int(s.length_m)}")
def layout(request):
    return request.param, generate_layout(request.param)


@pytest.mark.unit
def test_layout_closes_at_target_length(layout):
    spec, instructions = layout
    xy = simulate(instructions)[:, :2]
    assert math.dist(xy[-1], (0.0, 0.0)) < 10.0
    assert abs(len(xy) - spec.length_m) / spec.length_m < 0.02


@pytest.mark.unit
def test_layout_does_not_cross_itself(layout):
    _, instructions = layout
    xy = simulate(instructions)[:, :2]
    assert _self_clearance(xy) > 10.0


@pytest.mark.unit
def test_layout_turns_both_ways_and_completes_one_loop(layout):
    _, instructions = layout
    angles = [i["angle_deg"] for i in instructions if i["type"] == "C"]
    assert any(a > 0 for a in angles) and any(a < 0 for a in angles)
    heading = simulate(instructions)[-1, 2]
    assert abs(abs(math.degrees(heading)) - 360.0) < 2.0


@pytest.mark.unit
def test_layout_has_exactly_the_specified_corners(layout):
    """Every corner in the source data is a real change of direction."""
    spec, instructions = layout
    angles = [i["angle_deg"] for i in instructions if i["type"] == "C"]
    assert sum(a > 0 for a in angles) == spec.left_turns
    assert sum(a < 0 for a in angles) == spec.right_turns


@pytest.mark.unit
def test_corner_radius_follows_the_circuit_not_the_lap_length():
    """A 10 km lap can still have a 15 m hairpin; a kart track cannot have a 300 m sweeper."""
    long_lap = generate_layout(SPECS[3])
    kart = generate_layout(SPECS[4])
    assert min(i["radius_m"] for i in long_lap if i["type"] == "C") < 80.0
    assert max(i["radius_m"] for i in kart if i["type"] == "C") < 150.0


@pytest.mark.unit
def test_layout_is_deterministic_per_seed():
    spec = SPECS[1]
    assert generate_layout(spec) == generate_layout(spec)


@pytest.fixture(scope="module")
def qt_app():
    from PyQt6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.mark.unit
def test_clockwise_layout_is_not_extended_by_closure(qt_app, layout):
    from momentum.gui.gui_race_visual import CircuitGenerator

    spec, instructions = layout
    main = CircuitGenerator.generate_with_routes(instructions, options={})["main"]
    assert abs(len(main) - spec.length_m) / spec.length_m < 0.02


@pytest.mark.unit
def test_dressing_builds_pit_lane_and_grandstands(qt_app, layout):
    from momentum.gui.circuit_dressing import (
        CircuitDressing,
        build_pit_route,
        pit_box_positions,
    )
    from momentum.gui.gui_race_visual import CircuitGenerator

    _, instructions = layout
    main = CircuitGenerator.generate_with_routes(instructions, options={})["main"]
    pit = build_pit_route(main)
    assert pit is not None
    assert math.dist((pit[0].x, pit[0].y), (main[pit_index(main, pit[0])].x,
                                            main[pit_index(main, pit[0])].y)) < 1.0
    boxes = pit_box_positions(pit[-1].s)
    assert boxes == sorted(boxes) and boxes[0] > 0 and boxes[-1] < pit[-1].s
    dressing = CircuitDressing(main, pit)
    assert dressing.pit_paths.get("building") is not None
    assert dressing.stands


def pit_index(main, point):
    return min(range(len(main)), key=lambda i: (main[i].x - point.x) ** 2 + (main[i].y - point.y) ** 2)


@pytest.mark.unit
def test_pit_route_survives_short_main_straight(qt_app):
    from momentum.gui.circuit_dressing import build_pit_route
    from momentum.gui.gui_race_visual import TrackPoint

    pts = [
        TrackPoint(s=float(i), x=200 * math.cos(i / 200), y=200 * math.sin(i / 200),
                   theta=i / 200 + math.pi / 2, curvature=1 / 200)
        for i in range(int(2 * math.pi * 200))
    ]
    pit = build_pit_route(pts)
    assert pit is not None and len(pit) > 100

    tight = [
        TrackPoint(s=float(i), x=20 * math.cos(i / 20), y=20 * math.sin(i / 20),
                   theta=i / 20 + math.pi / 2, curvature=1 / 20)
        for i in range(int(2 * math.pi * 20) * 3)
    ]
    pit = build_pit_route(tight)
    assert pit is not None
    assert all(math.hypot(p.x, p.y) >= 9.9 for p in pit)
