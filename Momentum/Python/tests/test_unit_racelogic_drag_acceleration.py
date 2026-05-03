"""Unit tests for drag-acceleration discipline gameplay logic."""

from __future__ import annotations

import pytest

from RaceLogic.base_race_engine import RaceContext, RacingDiscipline
from RaceLogic.disciplines.drag_acceleration.drag_acceleration_discipline import (
    DragAccelerationEngine,
)
from database.models import Driver, Team, Track


def _build_context(
    drivers: list[Driver], teams: dict[int, Team], track_conditions=None
) -> RaceContext:
    track = Track(
        id=1,
        name="Drag Strip",
        country="US",
        primary_discipline="DRAG_ACCELERATION",
        length_km=0.402,
    )
    return RaceContext(
        discipline=RacingDiscipline.DRAG_ACCELERATION,
        track=track,
        drivers=drivers,
        teams=teams,
        total_laps=1,
        track_conditions=track_conditions or {},
    )


@pytest.mark.unit
def test_drag_select_representatives_picks_fastest_per_team_and_player_override():
    engine = DragAccelerationEngine(seed=11)

    team_1 = Team(
        id=1,
        name="Team 1",
        nationality="US",
        discipline="DRAG_ACCELERATION",
        tier="TIER_1",
        budget=80.0,
    )
    team_2 = Team(
        id=2,
        name="Team 2",
        nationality="US",
        discipline="DRAG_ACCELERATION",
        tier="TIER_1",
        budget=80.0,
    )

    d1 = Driver(
        id=1,
        name="Team1 Slow",
        nationality="US",
        birth_date="2000-01-01",
        current_team_id=1,
        speed=70,
    )
    d2 = Driver(
        id=2,
        name="Team1 Fast",
        nationality="US",
        birth_date="2000-01-01",
        current_team_id=1,
        speed=92,
    )
    d3 = Driver(
        id=3,
        name="Team2 Fast",
        nationality="US",
        birth_date="2000-01-01",
        current_team_id=2,
        speed=90,
    )
    d4 = Driver(
        id=4,
        name="Team2 Player",
        nationality="US",
        birth_date="2000-01-01",
        current_team_id=2,
        speed=60,
    )

    context = _build_context(
        drivers=[d1, d2, d3, d4],
        teams={1: team_1, 2: team_2},
        track_conditions={"player_driver_id": 4},
    )

    entrants = engine._select_team_representatives(context)
    chosen_ids = {entry["driver"].id for entry in entrants}

    # Team 1 should use fastest driver. Team 2 should use player override.
    assert 2 in chosen_ids
    assert 4 in chosen_ids
    assert 3 not in chosen_ids


@pytest.mark.unit
def test_drag_head_to_head_prefers_valid_time_over_dnf():
    engine = DragAccelerationEngine(seed=11)

    left = {
        "driver": Driver(
            id=1,
            name="Left",
            nationality="US",
            birth_date="2000-01-01",
            current_team_id=1,
        ),
        "team": Team(
            id=1,
            name="Left Team",
            nationality="US",
            discipline="DRAG_ACCELERATION",
            tier="TIER_1",
            budget=80.0,
        ),
    }
    right = {
        "driver": Driver(
            id=2,
            name="Right",
            nationality="US",
            birth_date="2000-01-01",
            current_team_id=2,
        ),
        "team": Team(
            id=2,
            name="Right Team",
            nationality="US",
            discipline="DRAG_ACCELERATION",
            tier="TIER_1",
            budget=80.0,
        ),
    }

    context = _build_context(
        drivers=[left["driver"], right["driver"]],
        teams={1: left["team"], 2: right["team"]},
    )

    # Left DNF, right finishes.
    left_result = {
        "driver_id": 1,
        "time_seconds": float("inf"),
        "dnf_reason": "red_light",
        "reaction_time_ms": 500.0,
    }
    right_result = {
        "driver_id": 2,
        "time_seconds": 4.2,
        "dnf_reason": None,
        "reaction_time_ms": 120.0,
    }

    def _fake_single_run(driver, team, _context):
        return left_result if driver.id == 1 else right_result

    engine._simulate_single_run = _fake_single_run  # type: ignore[method-assign]

    winner, loser = engine._run_head_to_head(left, right, context)

    assert winner["driver"].id == 2
    assert loser["driver"].id == 1


@pytest.mark.unit
def test_drag_simulate_single_run_applies_player_override_time_multiplier():
    engine = DragAccelerationEngine(seed=11)

    driver = Driver(
        id=1,
        name="Player",
        nationality="US",
        birth_date="2000-01-01",
        current_team_id=1,
    )
    team = Team(
        id=1,
        name="Team 1",
        nationality="US",
        discipline="DRAG_ACCELERATION",
        tier="TIER_1",
        budget=80.0,
    )

    context = _build_context(
        drivers=[driver],
        teams={1: team},
        track_conditions={
            "player_driver_id": 1,
            "player_team_driver_ids": ["1"],
            "player_overrides": {"pace": 1.0, "overtake": 1.0},
        },
    )

    engine._calculate_reaction_time = lambda *_args, **_kwargs: 100.0  # type: ignore[method-assign]
    engine._calculate_0_to_100_acceleration = lambda *_args, **_kwargs: 1000.0  # type: ignore[method-assign]
    engine._calculate_trap_speed = lambda *_args, **_kwargs: 300.0  # type: ignore[method-assign]
    engine._calculate_100_to_trap_acceleration = lambda *_args, **_kwargs: 2000.0  # type: ignore[method-assign]

    result = engine._simulate_single_run(driver, team, context)

    # Base = 3100ms. Player max push multiplier = 0.90 => 2790ms => 2.79s.
    assert result["time_seconds"] == pytest.approx(2.79, rel=1e-3)
    assert result["status"] == "FINISHED"
    assert result["dnf_reason"] is None
