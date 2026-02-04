#!/usr/bin/env python3
"""Test lapped driver classification logic"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from RaceLogic.realtime_race_engine import RaceState, DriverState, RealtimeRaceEngine


class MockTeam:
    """Mock team object for testing"""
    def __init__(self, team_id):
        self.id = team_id


def test_lapped_driver_classification():
    """Test that _compile_results properly classifies lapped drivers"""
    print("\n=== Testing Lapped Driver Classification ===\n")
    
    # Create race engine
    engine = RealtimeRaceEngine()
    
    # Create race state
    race_state = RaceState()
    race_state.total_laps = 3
    race_state.track_length_m = 5000.0
    race_state.checkered_flag_deployed = True
    race_state.leader_lap_count = 3
    
    # Create test drivers
    drivers_config = [
        (1, "Leader", 3, None),      # Finished 3 laps
        (2, "Second", 3, None),      # Finished 3 laps
        (3, "Lapped", 2, None),      # Only completed 2 laps (lapped)
        (4, "Lapped2", 1, None),     # Only completed 1 lap (lapped)
        (5, "DNF", 1, "mechanical"), # DNF on lap 1
    ]
    
    for driver_id, name, laps, dnf_reason in drivers_config:
        state = DriverState(
            driver_id=driver_id,
            driver_name=name,
            driver=None,
            team=None
        )
        state.lap = laps
        state.position_m = laps * race_state.track_length_m
        state.total_time = laps * 100.0  # Dummy time
        state.dnf_reason = dnf_reason
        state.team = MockTeam(team_id=driver_id * 10)  # Create mock team
        if dnf_reason is None:
            state.running = False  # Finished or still running
        
        race_state.driver_states[driver_id] = state
        race_state.lap_times[driver_id] = [90.0] * laps
    
    # Compile results
    results = engine._compile_results(race_state)
    
    print("Race Results:")
    print("=" * 70)
    for result in results:
        status = result['status']
        lapped = result.get('lapped', False)
        lap_deficit = result.get('lap_deficit', None)
        
        if status == 'FINISHED':
            print(f"P{result['position']}: {result['driver_name']} - {status} ({result['laps_completed']} laps)")
        elif status == 'LAPPED':
            print(f"+{lap_deficit}L: {result['driver_name']} - {status} ({result['laps_completed']} laps)")
        else:  # DNF
            print(f"---: {result['driver_name']} - {status} ({result['laps_completed']} laps, {result['dnf_reason']})")
    
    print("\n" + "=" * 70)
    print("✓ Classification Test Complete")
    print("\nExpected Classification:")
    print("  P1: Leader (3 laps) - FINISHED")
    print("  P2: Second (3 laps) - FINISHED")
    print("  +1L: Lapped (2 laps) - LAPPED")
    print("  +2L: Lapped2 (1 lap) - LAPPED")
    print("  ---: DNF (1 lap) - DNF")
    
    # Validate
    assert results[0]['position'] == 1 and results[0]['driver_name'] == 'Leader', "Leader should be P1"
    assert results[1]['position'] == 2 and results[1]['driver_name'] == 'Second', "Second should be P2"
    assert results[2]['status'] == 'LAPPED' and results[2]['lap_deficit'] == 1, "Lapped driver should have +1L"
    assert results[3]['status'] == 'LAPPED' and results[3]['lap_deficit'] == 2, "Lapped2 should have +2L"
    assert results[4]['status'] == 'DNF', "DNF driver should be DNF"
    
    print("\n✓ All assertions passed - Lapped classification working correctly!")


if __name__ == "__main__":
    test_lapped_driver_classification()
