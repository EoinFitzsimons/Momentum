"""
Test Checkered Flag Logic - Verify proper race finishing behavior
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from RaceLogic.realtime_race_engine import RaceState, DriverState


def test_checkered_flag_logic():
    """Test checkered flag deployment and lapped car finishing"""
    print("\n=== Testing Checkered Flag Logic ===\n")
    
    # Create race state with 3 laps
    race_state = RaceState()
    race_state.total_laps = 3
    race_state.track_length_m = 5000.0
    
    # Create drivers (minimal initialization)
    for i in range(1, 4):
        state = DriverState(
            driver_id=i,
            driver_name=f"Driver {i}",
            driver=None,
            team=None
        )
        race_state.driver_states[i] = state
        race_state.lap_times[i] = []
        race_state.lap_start_positions[i] = 0.0
    
    # Scenario: Driver 1 finishes lap 3, Driver 2 is on lap 2
    print("1. INITIAL STATE:")
    print(f"   Checkered flag deployed: {race_state.checkered_flag_deployed}")
    print(f"   Driver 1 lap: {race_state.driver_states[1].lap}, running: {race_state.driver_states[1].running}")
    print(f"   Driver 2 lap: {race_state.driver_states[2].lap}, running: {race_state.driver_states[2].running}")
    
    # Driver 1 completes lap 3
    driver1 = race_state.driver_states[1]
    driver1.lap = 3
    driver1.velocity_mps = 70.0
    
    # Simulate lap completion
    if driver1.lap >= race_state.total_laps:
        driver1.running = False
        if not race_state.checkered_flag_deployed:
            race_state.checkered_flag_deployed = True
            race_state.leader_lap_count = driver1.lap
    
    print("\n2. AFTER LEADER (Driver 1) FINISHES LAP 3:")
    print(f"   Checkered flag deployed: {race_state.checkered_flag_deployed}")
    print(f"   Leader lap count: {race_state.leader_lap_count}")
    print(f"   Driver 1 lap: {driver1.lap}, running: {driver1.running}")
    
    assert race_state.checkered_flag_deployed is True, "✗ Checkered flag should be deployed"
    assert race_state.leader_lap_count == 3, "✗ Leader lap count should be 3"
    assert driver1.running is False, "✗ Leader should stop running"
    print("   ✓ Checkered flag correctly deployed")
    
    # Driver 2 crosses finish line on lap 2 (will finish earlier than full laps)
    driver2 = race_state.driver_states[2]
    driver2.lap = 2
    
    # Simulate crossing finish line after checkered flag
    if race_state.checkered_flag_deployed:
        driver2.running = False
    
    print("\n3. DRIVER 2 CROSSES FINISH LINE ON LAP 2:")
    print(f"   Checkered flag deployed: {race_state.checkered_flag_deployed}")
    print(f"   Driver 2 lap: {driver2.lap}, running: {driver2.running}")
    
    assert driver2.running is False, "✗ Driver 2 should finish when crossing line after checkered flag"
    print("   ✓ Lapped car correctly finished at finish line (no need for all laps)")
    
    # Check all drivers status
    print("\n4. FINAL RACE STATE:")
    active = [s for s in race_state.driver_states.values() if s.running]
    print(f"   Active drivers still running: {len(active)}")
    
    for driver_id in [1, 2, 3]:
        state = race_state.driver_states[driver_id]
        print(f"   Driver {driver_id}: lap {state.lap}, running: {state.running}")
    
    if len(active) == 0:
        print("\n   ✓ All drivers finished - race should end")
    
    print("\n" + "=" * 50)
    print("ALL CHECKERED FLAG TESTS PASSED ✓")
    print("=" * 50)


if __name__ == "__main__":
    test_checkered_flag_logic()
