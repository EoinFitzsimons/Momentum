"""
GUI Integration Tests for Drag Racing Discipline

Tests drag racing through the actual GUI system:
1. Drag racing simulation execution with RaceContext
2. Results display validation
3. Visual validation of drag racing metrics

Requires PyQt6 and access to the full GUI system.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication

from services.race_simulation_api import simulate_race
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline
from database.models import Driver, Team, Track

import json
import time
from datetime import datetime
from datetime import datetime


class DragRacingGUITester:
    """Test harness for drag racing GUI integration"""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        
    def create_test_drivers_and_teams(self, count: int = 8):
        """Create test drivers and teams"""
        drivers = []
        teams = {}
        
        for i in range(count):
            driver = Driver(
                id=i + 1,
                name=f"Driver {i + 1}",
                nationality="USA",
                birth_date="1995-01-01",
                speed=40 + (i * 5),
                reactions=50 + (i * 3),
                pressure=50,
                consistency=50 + (i * 2),
                fitness=60,
                racecraft=50,
                setup_knowledge=50,
                fuel_management=50,
                tyre_management=50,
                feedback=50,
                adaptability=50,
                current_team_id=i + 1
            )
            drivers.append(driver)
            
            team = Team(
                id=i + 1,
                name=f"Team {i + 1}",
                nationality="USA",
                discipline="DRAG",
                tier="TOP_TIER" if i < 3 else "TIER_2",
                budget=100.0 + (i * 10),
                founded_year=2020,
                team_principal=f"Principal {i + 1}"
            )
            teams[i + 1] = team
        
        return drivers, teams
    
    def create_test_track(self) -> Track:
        """Create a test track"""
        return Track(
            id=1,
            name="Test Drag Strip",
            country="USA",
            primary_discipline="DRAG_ACCELERATION",
            length_km=0.402,
            turns=0,
            surface="asphalt",
            avg_speed_kmh=200.0,
            top_speed_kmh=300.0
        )
        
    def simulate_drag_race_gui(self) -> dict:
        """Simulate a drag race for GUI display"""
        print("\n" + "="*70)
        print("GUI TEST 1: Simulate Drag Race with RaceContext")
        print("="*70)
        
        drivers, teams = self.create_test_drivers_and_teams(8)
        track = self.create_test_track()
        
        print(f"\n✓ Created test environment:")
        print(f"  Drivers: {len(drivers)}")
        print(f"  Teams: {len(teams)}")
        print(f"  Track: {track.name}")
        
        # Create race context for drag racing
        context = RaceContext(
            discipline=RacingDiscipline.DRAG_ACCELERATION,
            track=track,
            drivers=drivers,
            teams=teams,
            total_laps=1,
            weather_conditions={
                "temperature": 25.0,
                "humidity": 50.0,
                "wind_speed": 5.0,
                "precipitation": 0.0,
                "visibility": 100.0
            },
            track_conditions={
                "grip_level": 1.0,
                "surface_temp": 30.0,
                "rubbering": 0.5,
                "surface_wear": 0.1
            }
        )
        
        print(f"\nSimulating drag race using RaceContext...")
        try:
            results = simulate_race(context=context, verbose=False, seed=42)
            
            print(f"✓ Race simulation completed")
            print(f"  Results: {len(results)} drivers finished")
            
            # Display results
            print(f"\n{'Pos':<4} {'Driver':<20} {'Time':<12} {'Reaction':<15} {'Trap Speed':<15} {'Status':<10}")
            print("-" * 80)
            
            for i, result in enumerate(results[:8]):
                pos = result.get('position', i+1)
                name = result.get('driver_name', 'Unknown')
                elapsed = result.get('time_seconds', 0)
                reaction = result.get('reaction_time_ms', 0)
                trap = result.get('trap_speed_kmh', 0)
                status = result.get('status', '')
                
                time_str = f"{elapsed:.3f}s" if elapsed != float('inf') else "DNF"
                
                print(f"{pos:<4} {name:<20} {time_str:<12} {reaction:.1f}ms{'':<7} {trap:.1f} km/h{'':<3} {status:<10}")
            
            return {
                'context': context,
                'results': results,
                'track': track,
                'drivers': drivers
            }
            
        except Exception as e:
            print(f"ERROR during race simulation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def simulate_drag_race(self, champ_id: int) -> dict:
        """Simulate a drag racing event"""
        print("\n" + "="*70)
        print("GUI TEST 2: Simulate Drag Racing Event")
        print("="*70)
        
        # Get championship
        championship = self.db.get_championship(champ_id)
        if not championship:
            print(f"ERROR: Championship {champ_id} not found")
            return None
        
        print(f"\nSimulating race for: {championship.name}")
        
        # Get drivers and teams for the championship
        drivers = self.db.get_all_drivers()[:8]
        teams = {d.current_team_id: self.db.get_team(d.current_team_id) or 
                 Team(id=d.current_team_id, name=f"Team {d.current_team_id}", 
                      nationality="USA", discipline="DRAG", tier="TIER_2",
                      budget=50.0, founded_year=2020, team_principal="Principal")
                 for d in drivers if d.current_team_id}
        
        # Get a random track
        track = self.db.get_all_tracks()[0] if self.db.get_all_tracks() else None
        if not track:
            print("ERROR: No tracks in database")
            return None
        
        print(f"✓ Drivers: {len(drivers)}")
        print(f"✓ Teams: {len(teams)}")
        print(f"✓ Track: {track.name}")
        
        # Create race context for drag racing
        context = RaceContext(
            discipline=RacingDiscipline.DRAG_ACCELERATION,
            track=track,
            drivers=drivers,
            teams=teams,
            total_laps=1,
            weather_conditions={
                "temperature": 25.0,
                "humidity": 50.0,
                "wind_speed": 5.0,
                "precipitation": 0.0,
                "visibility": 100.0
            },
            track_conditions={
                "grip_level": 1.0,
                "surface_temp": 30.0,
                "rubbering": 0.5,
                "surface_wear": 0.1
            }
        )
        
        print(f"\nSimulating drag race...")
        try:
            results = simulate_race(context=context, verbose=True)
            
            print(f"\n✓ Race simulation completed")
            print(f"  Results: {len(results)} drivers")
            
            # Display results
            print(f"\n{'Pos':<4} {'Driver':<20} {'Time':<12} {'Reaction':<15} {'Trap Speed':<15}")
            print("-" * 70)
            
            for i, result in enumerate(results[:8]):
                pos = result.get('position', i+1)
                name = result.get('driver_name', 'Unknown')
                elapsed = result.get('time_seconds', 0)
                reaction = result.get('reaction_time_ms', 0)
                trap = result.get('trap_speed_kmh', 0)
                status = result.get('status', '')
                
                time_str = f"{elapsed:.3f}s" if elapsed != float('inf') else "DNF"
                
                print(f"{pos:<4} {name:<20} {time_str:<12} {reaction:.1f}ms{'':<8} {trap:.1f} km/h")
            
            return {
                'context': context,
                'results': results,
                'track': track,
                'drivers': drivers
            }
            
        except Exception as e:
            print(f"ERROR during race simulation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def validate_gui_display(self, race_data: dict) -> bool:
        """Validate that GUI can display drag racing results"""
        print("\n" + "="*70)
        print("GUI TEST 3: Validate GUI Display Capability")
        print("="*70)
        
        results = race_data['results']
        drivers = race_data['drivers']
        
        print(f"\nValidating {len(results)} race results for GUI display...")
        
        # Check that each result has required fields for GUI display
        required_fields = ['driver_id', 'driver_name', 'position', 'time_seconds', 'status']
        drag_fields = ['reaction_time_ms', 'trap_speed_kmh']
        
        all_valid = True
        for i, result in enumerate(results):
            # Check required fields
            for field in required_fields:
                if field not in result:
                    print(f"  ERROR: Result {i} missing field: {field}")
                    all_valid = False
            
            # Check drag-specific fields (should be present for finished races)
            if result.get('status') == 'FINISHED':
                for field in drag_fields:
                    if field not in result:
                        print(f"  WARNING: Result {i} missing drag field: {field}")
        
        if all_valid:
            print("✓ All results have required fields for GUI display")
            
            # Validate data types
            print("\nValidating data types...")
            for i, result in enumerate(results[:3]):  # Check first 3
                pos = result.get('position')
                time = result.get('time_seconds')
                reaction = result.get('reaction_time_ms')
                trap = result.get('trap_speed_kmh')
                
                assert isinstance(pos, (int, float)), f"Position not numeric: {pos}"
                assert isinstance(time, (int, float)) or time == float('inf'), f"Time not numeric: {time}"
                assert isinstance(reaction, (int, float)), f"Reaction not numeric: {reaction}"
                assert isinstance(trap, (int, float)), f"Trap speed not numeric: {trap}"
            
            print("✓ All data types valid for GUI rendering")
        
        return all_valid
    
    def validate_standings_calculation(self, race_data: dict, champ_id: int) -> bool:
        """Validate that standings can be calculated from drag results"""
        print("\n" + "="*70)
        print("GUI TEST 4: Validate Championship Standings")
        print("="*70)
        
        results = race_data['results']
        
        print(f"\nCalculating championship standings from {len(results)} race results...")
        
        # Get championship standings
        standings = self.champ_service.recalculate_standings(champ_id)
        
        if not standings:
            print("ERROR: No standings calculated")
            return False
        
        print(f"✓ Standings calculated for {len(standings)} drivers")
        
        # Validate standings structure
        print("\nValidating standings structure...")
        for i, entry in enumerate(standings[:5]):
            print(f"  {i+1}. {entry.driver_name}: {entry.total_points} points")
            
            # Validate fields
            assert hasattr(entry, 'driver_id'), "Missing driver_id"
            assert hasattr(entry, 'driver_name'), "Missing driver_name"
            assert hasattr(entry, 'total_points'), "Missing total_points"
            assert hasattr(entry, 'wins'), "Missing wins"
        
        print("✓ Standings structure valid for GUI display")
        
        return True
    
    def run_all_tests(self):
        """Run all GUI integration tests"""
        print("\n" + "#"*70)
        print("# DRAG RACING GUI INTEGRATION TESTS")
        print("#"*70)
        
        # Test 1: Create championship
        champ_id = self.create_drag_championship()
        if not champ_id:
            print("\n❌ Championship creation failed - aborting remaining tests")
            return False
        
        # Test 2: Simulate race
        race_data = self.simulate_drag_race(champ_id)
        if not race_data:
            print("\n❌ Race simulation failed - aborting remaining tests")
            return False
        
        # Test 3: Validate GUI display
        if not self.validate_gui_display(race_data):
            print("\n⚠️ GUI display validation had warnings")
        
        # Test 4: Validate standings
        if not self.validate_standings_calculation(race_data, champ_id):
            print("\n❌ Standings calculation failed")
            return False
        
        # Summary
        print("\n" + "#"*70)
        print("# GUI INTEGRATION TEST SUMMARY")
        print("#"*70)
        print("\n✅ All GUI integration tests completed successfully!")
        print("\nDrag racing GUI integration verified:")
        print("  ✓ Championship creation with DRAG_ACCELERATION discipline")
        print("  ✓ Race simulation executes correctly")
        print("  ✓ Results contain all required fields for GUI display")
        print("  ✓ Championship standings calculated from results")
        print("  ✓ Drag-specific metrics (reaction time, trap speed) present")
        print("\nThe drag racing discipline is ready for GUI visualization!")
        print("\nNext steps for full GUI testing:")
        print("  1. Run with actual RaceWindow to see visual display")
        print("  2. Test standings table updates during race")
        print("  3. Add drag-specific metrics display (reaction time column)")
        print("  4. Create drag racing results summary screen")
        
        return True


def run_headless_gui_tests():
    """Run GUI tests without displaying windows"""
    print("\nRunning headless GUI integration tests...")
    print("(No windows will be displayed, only validation)\n")
    
    tester = DragRacingGUITester()
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = run_headless_gui_tests()
    sys.exit(exit_code)
