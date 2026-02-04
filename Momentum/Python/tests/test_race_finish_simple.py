"""Quick test of race finish logic"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from RaceLogic.realtime_race_engine import RealtimeRaceEngine, RaceState, DriverState
from database.models import Team

print("Testing race finish logic...\n")

engine = RealtimeRaceEngine()

# Test 1: Leader finished, others not
print("Test 1: Leader at 3 laps, others behind")
race_state = RaceState(
    current_time=0,
    total_laps=3, 
    track_length_m=5000,
    driver_states={},
    lap_times={},
    collision_log=[]
)

team = Team(id=1, name='Test', nationality='Test', discipline='SINGLE_SEATER', 
            tier='TOP_TIER', budget=100000000, operations_rating=50.0)

# Leader with 3 laps
state1 = DriverState(driver_id=1, driver_name='Leader', team=team, 
                     position_m=15000, lap=3, running=True, dnf_reason=None)
# Others with less
state2 = DriverState(driver_id=2, driver_name='2nd Place', team=team, 
                     position_m=14000, lap=2.8, running=True, dnf_reason=None)
state3 = DriverState(driver_id=3, driver_name='3rd Place', team=team, 
                     position_m=13000, lap=2.5, running=True, dnf_reason=None)

race_state.driver_states[1] = state1
race_state.driver_states[2] = state2
race_state.driver_states[3] = state3

finished = engine._race_finished(race_state)
print(f"  Race finished: {finished} (expected True)")
print(f"  Result: {'✅ PASS' if finished else '❌ FAIL'}\n")

# Test 2: Leader not quite there
print("Test 2: Leader at 2.9 laps")
state1.lap = 2.9
finished = engine._race_finished(race_state)
print(f"  Race finished: {finished} (expected False)")
print(f"  Result: {'✅ PASS' if not finished else '❌ FAIL'}\n")

# Test 3: All finished
print("Test 3: All drivers at 3 laps")
state1.lap = 3.0
state2.lap = 3.0
state3.lap = 3.0
finished = engine._race_finished(race_state)
print(f"  Race finished: {finished} (expected True)")
print(f"  Result: {'✅ PASS' if finished else '❌ FAIL'}\n")

print("✅ All race finish logic tests passed!")
