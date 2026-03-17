"""
Test: Verify race ends when leader finishes

This test checks that:
1. Race finishes when the leader completes all laps
2. Lapped cars are marked correctly in results
3. Checkered flag behavior is correct
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from RaceLogic.realtime_race_engine import RealtimeRaceEngine, RaceState, DriverState
from database.database_manager import DatabaseManager
from database.models import Driver, Team, Track
from config import DATABASE_PATH


def _mk_driver(driver_id: int, name: str) -> Driver:
    return Driver(
        id=driver_id,
        name=name,
        nationality="Test",
        birth_date="1995-01-01",
    )


def test_race_finish_logic():
    """Test that race ends when leader finishes"""
    print("\n=== Testing Race Finish Logic ===\n")
    
    # Create a mock race engine
    engine = RealtimeRaceEngine()
    
    # Create mock race state
    race_state = RaceState(
        track_length_m=5000,
        total_laps=3,  # 3-lap race
        current_time=0,
        driver_states={},
        lap_times={},
        collision_log=[]
    )
    
    # Create 3 drivers with different lap progress
    drivers_data = [
        (1, "Leader", 3),      # Leader: 3 laps complete (finished)
        (2, "Mid-field", 2.8), # Mid-field: 2.8 laps (not finished)
        (3, "Backmarker", 2.5) # Backmarker: 2.5 laps (not finished)
    ]
    
    for driver_id, name, laps in drivers_data:
        state = DriverState(
            driver_id=driver_id,
            driver_name=name,
            driver=_mk_driver(driver_id, name),
            team=Team(id=1, name="Test Team", nationality="Test", discipline="SINGLE_SEATER", tier="TOP_TIER", budget=100000000, operations_rating=50.0),
            position_m=laps * 5000,  # Calculate meters from laps
            lap=laps,
            running=True,  # All cars still running
            dnf_reason=None
        )
        race_state.driver_states[driver_id] = state
    
    # Test the race finish logic
    print("1. Testing race state:")
    for driver_id, state in race_state.driver_states.items():
        print(f"   Driver {driver_id:2}: {state.driver_name:15} - Laps: {state.lap:.1f}")
    
    is_finished = engine._race_finished(race_state)
    print(f"\n2. Race finished? {is_finished}")
    print(f"   Expected: True (leader has 3 laps)")
    
    if is_finished:
        print("   ✅ PASS - Race correctly identified as finished")
    else:
        print("   ❌ FAIL - Race should be finished!")
    
    # Test when leader hasn't finished yet
    print("\n3. Testing with leader at 2.9 laps:")
    race_state.driver_states[1].lap = 2.9  # Leader not quite done
    is_finished = engine._race_finished(race_state)
    print(f"   Race finished? {is_finished}")
    print(f"   Expected: False (leader hasn't completed 3 laps)")
    
    if not is_finished:
        print("   ✅ PASS - Race correctly identified as not finished")
    else:
        print("   ❌ FAIL - Race should not be finished!")
    
    # Test with all drivers finished (shouldn't matter now)
    print("\n4. Testing with all drivers finished:")
    race_state.driver_states[1].lap = 3.0
    race_state.driver_states[2].lap = 3.0
    race_state.driver_states[3].lap = 3.0
    is_finished = engine._race_finished(race_state)
    print(f"   Race finished? {is_finished}")
    print(f"   Expected: True (leader at 3 laps)")
    
    if is_finished:
        print("   ✅ PASS - Race correctly finished")
    else:
        print("   ❌ FAIL - Race should be finished!")
    
    # Test with DNF drivers
    print("\n5. Testing with some DNF drivers (should only count running):")
    race_state.driver_states[3].running = False  # Driver 3 DNFs
    race_state.driver_states[3].dnf_reason = "Engine Failure"
    race_state.driver_states[1].lap = 2.5  # Reset leader
    race_state.driver_states[2].lap = 2.0
    
    is_finished = engine._race_finished(race_state)
    print(f"   Race finished? {is_finished}")
    print(f"   Expected: False (leader at 2.5 laps, needs 3)")
    
    if not is_finished:
        print("   ✅ PASS - Race correctly not finished")
    else:
        print("   ❌ FAIL - Race should not be finished!")
    
    print("\n=== Race Finish Logic Test Complete ===\n")


def test_results_compilation():
    """Test that results are compiled correctly with early finish"""
    print("=== Testing Results Compilation ===\n")
    
    engine = RealtimeRaceEngine()
    
    # Create race state where leader finished but others didn't
    race_state = RaceState(
        track_length_m=5000,
        total_laps=3,
        current_time=3600,  # 1 hour elapsed
        driver_states={},
        lap_times={
            1: [90.0, 91.0, 92.0],  # Leader's lap times
            2: [95.0, 96.0],         # Mid-field (incomplete)
            3: [100.0, 101.0]        # Backmarker (incomplete)
        },
        collision_log=[]
    )
    
    # Create drivers
    drivers_data = [
        (1, "Leader", 3),        # Finished
        (2, "Mid-field", 2.3),   # Not finished
        (3, "Backmarker", 2.1)   # Not finished
    ]
    
    for driver_id, name, laps in drivers_data:
        state = DriverState(
            driver_id=driver_id,
            driver_name=name,
            driver=_mk_driver(driver_id, name),
            team=Team(id=driver_id, name=f"Team {driver_id}", nationality="Test", discipline="SINGLE_SEATER", tier="TOP_TIER", budget=100000000, operations_rating=50.0),
            position_m=laps * 5000,
            lap=laps,
            running=True,
            dnf_reason=None,
            best_lap_time=90.0 if driver_id == 1 else 95.0
        )
        race_state.driver_states[driver_id] = state
    
    # Compile results
    results = engine._compile_results(race_state)
    
    print("Results compiled:")
    for result in results:
        status = result['status']
        laps = result['laps_completed']
        print(f"  {result['position']}: {result['driver_name']:15} - {laps:.1f} laps - {status}")
    
    print("\nVerifying statuses:")
    leader_result = next(r for r in results if r['driver_id'] == 1)
    others = [r for r in results if r['driver_id'] != 1]
    
    print(f"  Leader status: {leader_result['status']} (expected: FINISHED)")
    if leader_result['status'] == 'FINISHED':
        print("  ✅ PASS - Leader marked as FINISHED")
    else:
        print("  ❌ FAIL - Leader should be FINISHED")
    
    for other in others:
        print(f"  {other['driver_name']} status: {other['status']} (expected: DNF)")
        if other['status'] == 'DNF':
            print(f"  ✅ PASS - {other['driver_name']} marked as DNF (didn't complete all laps)")
        else:
            print(f"  ❌ FAIL - {other['driver_name']} should be DNF")
    
    print("\n=== Results Compilation Test Complete ===\n")


if __name__ == "__main__":
    test_race_finish_logic()
    test_results_compilation()
    print("\n" + "="*60)
    print("ALL RACE FINISH TESTS COMPLETED")
    print("="*60)
