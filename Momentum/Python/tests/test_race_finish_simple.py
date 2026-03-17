"""Quick pytest smoke test for race finish logic."""

import sys
from pathlib import Path

# Ensure project root is importable.
sys.path.insert(0, str(Path(__file__).parent.parent))

from RaceLogic.realtime_race_engine import DriverState, RaceState, RealtimeRaceEngine
from database.models import Driver, Team


def _make_driver(driver_id: int, name: str) -> Driver:
    return Driver(
        id=driver_id,
        name=name,
        nationality="Test",
        birth_date="1995-01-01",
    )


def test_race_finish_logic_smoke():
    engine = RealtimeRaceEngine()

    race_state = RaceState(
        current_time=0,
        total_laps=3,
        track_length_m=5000,
        driver_states={},
        lap_times={},
        collision_log=[],
    )

    team = Team(
        id=1,
        name="Test",
        nationality="Test",
        discipline="SINGLE_SEATER",
        tier="TOP_TIER",
        budget=100000000,
        operations_rating=50.0,
    )

    leader = DriverState(
        driver_id=1,
        driver_name="Leader",
        driver=_make_driver(1, "Leader"),
        team=team,
        position_m=15000,
        lap=3,
        running=True,
        dnf_reason=None,
    )
    second = DriverState(
        driver_id=2,
        driver_name="Second",
        driver=_make_driver(2, "Second"),
        team=team,
        position_m=14000,
        lap=2,
        running=True,
        dnf_reason=None,
    )
    third = DriverState(
        driver_id=3,
        driver_name="Third",
        driver=_make_driver(3, "Third"),
        team=team,
        position_m=13000,
        lap=2,
        running=True,
        dnf_reason=None,
    )

    race_state.driver_states[1] = leader
    race_state.driver_states[2] = second
    race_state.driver_states[3] = third

    # Current implementation does not end race immediately when leader reaches distance.
    assert not engine._race_finished(race_state)

    # Leader below required laps -> race should still continue.
    leader.lap = 2
    assert not engine._race_finished(race_state)

    # Even with everyone at race distance, race remains active until all stop running.
    leader.lap = 3
    second.lap = 3
    third.lap = 3
    assert not engine._race_finished(race_state)

    # Race ends when no active drivers remain.
    leader.running = False
    second.running = False
    third.running = False
    assert engine._race_finished(race_state)
