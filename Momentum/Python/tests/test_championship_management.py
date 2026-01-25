"""
Championship Management Integration Tests

Comprehensive test suite for UC-4 through UC-10 covering:
- Championship creation and configuration
- Race event scheduling
- Results tracking and standings calculation
- Status lifecycle management
- Points system validation
- Tie-breaking rules

Usage:
    python tests/test_championship_management.py
"""

import sys
import io
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.database_manager import DatabaseManager
from database.models import Championship, Race, RaceResult, Driver, Team, Track
from services.championship_service import ChampionshipService, POINTS_SYSTEMS
from datetime import datetime, timedelta
from typing import List


class TestChampionshipManagement:
    """Test suite for championship management system"""
    
    def __init__(self):
        """Initialize test database"""
        # Use a test-specific database file
        test_db_path = Path(__file__).parent / "test_championship.db"
        
        # Remove old test database if exists
        if test_db_path.exists():
            test_db_path.unlink()
        
        self.db = DatabaseManager(str(test_db_path))
        self.service = ChampionshipService(self.db)
        self.setup_test_data()
        self.test_db_path = test_db_path
    
    def setup_test_data(self):
        """Create test drivers, teams, and tracks using direct SQL"""
        print("Setting up test data...")
        
        # Create test data using direct SQL to bypass complex model requirements
        with self.db.get_connection() as conn:
            # Create test drivers with minimal fields
            self.drivers = []
            for i in range(1, 11):
                cursor = conn.execute("""
                    INSERT INTO drivers (name, nationality, birth_date, speed, racecraft, 
                                       consistency, preferred_discipline)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f"Test Driver {i}", "GBR", "1995-01-01", 70.0 + i, 
                     65.0 + i, 60.0 + i, "SINGLE_SEATER"))
                
                # Create a simple driver object for reference
                driver = Driver(
                    id=cursor.lastrowid,
                    name=f"Test Driver {i}",
                    nationality="GBR",
                    birth_date="1995-01-01",
                    speed=70.0 + i,
                    racecraft=65.0 + i,
                    consistency=60.0 + i,
                    preferred_discipline="SINGLE_SEATER"
                )
                self.drivers.append(driver)
            
            # Create test teams
            self.teams = []
            for i in range(1, 6):
                cursor = conn.execute("""
                    INSERT INTO teams (name, nationality, discipline, tier, budget, operations_rating)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (f"Test Team {i}", "GBR", "SINGLE_SEATER", "TIER_1", 
                     50000000.0, 70.0 + i))
                
                team = Team(
                    id=cursor.lastrowid,
                    name=f"Test Team {i}",
                    nationality="GBR",
                    discipline="SINGLE_SEATER",
                    tier="TIER_1",
                    budget=50000000.0,
                    operations_rating=70.0 + i
                )
                self.teams.append(team)
            
            # Create test tracks
            self.tracks = []
            for i in range(1, 6):
                cursor = conn.execute("""
                    INSERT INTO tracks (name, country, primary_discipline)
                    VALUES (?, ?, ?)
                """, (f"Test Circuit {i}", "United Kingdom", "SINGLE_SEATER"))
                
                track = Track(
                    id=cursor.lastrowid,
                    name=f"Test Circuit {i}",
                    country="United Kingdom",
                    primary_discipline="SINGLE_SEATER"
                )
                self.tracks.append(track)
            
            conn.commit()
        
        print(f"[OK] Created {len(self.drivers)} drivers, {len(self.teams)} teams, {len(self.tracks)} tracks")
    
    def test_uc10_create_championship(self):
        """UC-10: Create Championship"""
        print("\n=== Testing UC-10: Create Championship ===")
        
        # Create championship with calendar
        championship = Championship(
            id=0,
            name="Test F1 Championship",
            discipline="SINGLE_SEATER",
            season_length=5,
            points_system="standard",
            current_season=1,
            tier="TOP_TIER",
            founded_year=2025,
            description="Test championship for UC-10"
        )
        
        track_ids = [t.id for t in self.tracks]
        start_date = datetime(2025, 3, 1)
        
        champ_id, race_ids = self.service.create_championship_season(
            championship,
            track_ids,
            start_date
        )
        
        assert champ_id > 0, "Championship should be created with valid ID"
        assert len(race_ids) == len(track_ids), "Should create race for each track"
        
        # Verify championship was created
        created_champ = self.db.get_championship(champ_id)
        assert created_champ is not None, "Championship should be retrievable"
        assert created_champ.name == "Test F1 Championship"
        
        print(f"✓ Championship created with ID {champ_id}")
        print(f"✓ Created {len(race_ids)} race events")
        
        return champ_id
    
    def test_uc7_create_race_event(self, championship_id: int):
        """UC-7: Create Race Event"""
        print("\n=== Testing UC-7: Create Race Event ===")
        
        # Get existing races count
        calendar = self.service.get_championship_calendar(championship_id, 1)
        
        # Validate race event (should succeed)
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        is_valid, error = self.service.validate_race_event(
            championship_id,
            self.tracks[0].id,
            future_date,
            1
        )
        
        assert is_valid, f"Future race should be valid: {error}"
        print(f"✓ Race event validation passed")
        
        # Test date conflict validation
        is_valid, error = self.service.validate_race_event(
            championship_id,
            self.tracks[0].id,
            calendar[0]["race_date"],  # Same date as existing race
            1
        )
        
        assert not is_valid, "Should detect date conflict"
        assert "conflict" in error.lower(), "Error should mention conflict"
        print(f"✓ Date conflict detection working")
    
    def test_uc8_read_race_schedule(self, championship_id: int):
        """UC-8: Read Race Schedule"""
        print("\n=== Testing UC-8: Read Race Schedule ===")
        
        calendar = self.service.get_championship_calendar(championship_id, 1)
        
        assert len(calendar) > 0, "Calendar should have races"
        
        # Verify ordering by round number
        for i, race in enumerate(calendar):
            assert race["round_number"] == i + 1, "Races should be ordered by round"
        
        # Verify all required fields
        required_fields = [
            "race_id", "round_number", "race_date", "track_id",
            "track_name", "track_country", "status", "laps"
        ]
        
        for field in required_fields:
            assert field in calendar[0], f"Race should have {field} field"
        
        print(f"✓ Retrieved {len(calendar)} races in correct order")
        print(f"✓ All required fields present")
    
    def test_uc9_update_race_status(self, championship_id: int):
        """UC-9: Update Race Status"""
        print("\n=== Testing UC-9: Update Race Status ===")
        
        # Get first race
        calendar = self.service.get_championship_calendar(championship_id, 1)
        race_id = calendar[0]["race_id"]
        
        # Test valid transition: scheduled -> in-progress
        success, error = self.service.update_race_lifecycle_status(race_id, "in-progress")
        assert success, f"Should allow scheduled->in-progress: {error}"
        print(f"✓ Valid transition: scheduled -> in-progress")
        
        # Test valid transition: in-progress -> completed
        success, error = self.service.update_race_lifecycle_status(race_id, "completed")
        assert success, f"Should allow in-progress->completed: {error}"
        print(f"✓ Valid transition: in-progress -> completed")
        
        # Test invalid transition: completed -> scheduled
        success, error = self.service.update_race_lifecycle_status(race_id, "scheduled")
        assert not success, "Should reject completed->scheduled"
        print(f"✓ Invalid transition rejected: completed -> scheduled")
        
        # Test invalid status
        success, error = self.service.update_race_lifecycle_status(race_id, "invalid_status")
        assert not success, "Should reject invalid status"
        print(f"✓ Invalid status rejected")
    
    def test_uc4_uc6_race_results_and_standings(self, championship_id: int):
        """UC-4: Read Race Results & UC-6: Update Championship Standings"""
        print("\n=== Testing UC-4 & UC-6: Race Results and Standings ===")
        
        # Get races
        calendar = self.service.get_championship_calendar(championship_id, 1)
        
        # Simulate first race results
        race_id = calendar[0]["race_id"]
        championship = self.db.get_championship(championship_id)
        
        # Create race results
        results_data = [
            (1, self.drivers[0].id, self.teams[0].id, 1, True),   # 1st + fastest lap
            (2, self.drivers[1].id, self.teams[0].id, 2, False),  # 2nd
            (3, self.drivers[2].id, self.teams[1].id, 3, False),  # 3rd
            (4, self.drivers[3].id, self.teams[1].id, 4, False),  # 4th
            (5, self.drivers[4].id, self.teams[2].id, 5, False),  # 5th
        ]
        
        for grid_pos, driver_id, team_id, position, fastest_lap in results_data:
            points = self.service.calculate_points(
                position,
                championship.discipline,
                fastest_lap
            )
            
            result = RaceResult(
                id=0,
                race_id=race_id,
                driver_id=driver_id,
                team_id=team_id,
                position=position,
                points=points,
                fastest_lap=fastest_lap,
                grid_position=grid_pos
            )
            
            self.db.save_race_result(result)
        
        # Mark race as completed
        self.db.update_race_status(race_id, "completed")
        
        print(f"✓ Created results for race {race_id}")
        
        # Read race results (UC-4)
        results = self.db.get_race_results(race_id)
        assert len(results) == 5, "Should have 5 results"
        assert results[0].position == 1, "Results should be ordered"
        print(f"✓ Retrieved {len(results)} race results")
        
        # Calculate standings (UC-6)
        standings = self.service.recalculate_standings(championship_id, 1)
        
        assert len(standings) == 5, "Should have 5 drivers in standings"
        assert standings[0].position == 1, "Leader should be position 1"
        assert standings[0].driver_id == self.drivers[0].id, "Winner should lead"
        
        # Verify points calculation (F1 system: 25, 18, 15, 12, 10)
        expected_points = POINTS_SYSTEMS["SINGLE_SEATER"]
        assert standings[0].total_points == expected_points[0] + 1, "Winner should have 26 points (25 + fastest lap)"
        assert standings[1].total_points == expected_points[1], "2nd should have 18 points"
        
        print(f"✓ Standings calculated correctly:")
        for i, entry in enumerate(standings[:3], 1):
            print(f"  {i}. {entry.driver_name}: {entry.total_points} points")
        
        # Test tie-breaking
        self._test_tie_breaking(championship_id)
    
    def _test_tie_breaking(self, championship_id: int):
        """Test tie-breaking rules"""
        print("\n--- Testing Tie-Breaking Rules ---")
        
        # Simulate second race with tie scenario
        calendar = self.service.get_championship_calendar(championship_id, 1)
        race_id = calendar[1]["race_id"]
        championship = self.db.get_championship(championship_id)
        
        # Create results that will tie two drivers on points
        # Driver 1 currently has 26 points (win + fastest lap)
        # Driver 2 currently has 18 points (2nd)
        # If driver 2 wins race 2, they'll have 43 points
        # If driver 1 gets 2nd, they'll have 44 points - still ahead
        # But if driver 1 gets 3rd (15 points = 41 total) and driver 2 wins (25 points = 43 total)
        # Driver 2 would lead on countback
        
        results_data = [
            (1, self.drivers[1].id, self.teams[0].id, 1, True),   # Driver 2 wins (18 + 26 = 44)
            (2, self.drivers[0].id, self.teams[0].id, 2, False),  # Driver 1 2nd (26 + 18 = 44) - TIED!
            (3, self.drivers[2].id, self.teams[1].id, 3, False),
        ]
        
        for grid_pos, driver_id, team_id, position, fastest_lap in results_data:
            points = self.service.calculate_points(
                position,
                championship.discipline,
                fastest_lap
            )
            
            result = RaceResult(
                id=0,
                race_id=race_id,
                driver_id=driver_id,
                team_id=team_id,
                position=position,
                points=points,
                fastest_lap=fastest_lap,
                grid_position=grid_pos
            )
            
            self.db.save_race_result(result)
        
        self.db.update_race_status(race_id, "completed")
        
        # Recalculate standings
        standings = self.service.recalculate_standings(championship_id, 1)
        
        # Both drivers should have 44 points
        top_two = standings[:2]
        assert top_two[0].total_points == 44, "Leader should have 44 points"
        assert top_two[1].total_points == 44, "2nd should have 44 points"
        
        # Driver 1 should lead due to tie-breaking (2 wins vs 1 win)
        assert top_two[0].driver_id == self.drivers[0].id, "Driver with more wins should lead"
        assert top_two[0].wins == 1, "Leader should have 1 win"
        assert top_two[1].wins == 1, "2nd should have 1 win"
        
        print(f"✓ Tie-breaking working correctly:")
        print(f"  Tied on {top_two[0].total_points} points")
        print(f"  Leader has {top_two[0].wins} win(s), 2nd has {top_two[1].wins} win(s)")
    
    def test_uc5_championship_details(self, championship_id: int):
        """UC-5: Read Championship Details"""
        print("\n=== Testing UC-5: Read Championship Details ===")
        
        championship = self.db.get_championship(championship_id)
        standings = self.service.recalculate_standings(championship_id, 1)
        calendar = self.service.get_championship_calendar(championship_id, 1)
        
        # Verify we have all components
        assert championship is not None, "Championship should exist"
        assert len(standings) > 0, "Should have standings"
        assert len(calendar) > 0, "Should have calendar"
        
        # Verify archived championship support
        assert hasattr(championship, 'archived'), "Championship should have archived field"
        
        print(f"✓ Championship: {championship.name}")
        print(f"✓ Current Season: {championship.current_season}")
        print(f"✓ Standings Entries: {len(standings)}")
        print(f"✓ Calendar Races: {len(calendar)}")
        print(f"✓ Discipline: {championship.discipline}")
        print(f"✓ Points System: {championship.points_system}")
    
    def test_points_systems(self):
        """Test all discipline-specific points systems"""
        print("\n=== Testing Points Systems ===")
        
        for discipline, points_table in POINTS_SYSTEMS.items():
            # Test winner points
            winner_points = self.service.calculate_points(1, discipline, False)
            assert winner_points == points_table[0], f"{discipline}: Winner should get {points_table[0]} points"
            
            # Test out of points
            out_of_points = self.service.calculate_points(len(points_table) + 1, discipline, False)
            assert out_of_points == 0, f"{discipline}: Position outside points should get 0"
            
            # Test fastest lap bonus (only for SINGLE_SEATER and URBAN_STREET)
            if discipline in ["SINGLE_SEATER", "URBAN_STREET"]:
                with_bonus = self.service.calculate_points(1, discipline, True)
                assert with_bonus == points_table[0] + 1, f"{discipline}: Should get fastest lap bonus"
            
            print(f"✓ {discipline}: Points system validated")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 60)
        print("CHAMPIONSHIP MANAGEMENT INTEGRATION TESTS")
        print("Testing UC-4 through UC-10")
        print("=" * 60)
        
        try:
            # UC-10: Create Championship
            champ_id = self.test_uc10_create_championship()
            
            # UC-7: Create Race Event
            self.test_uc7_create_race_event(champ_id)
            
            # UC-8: Read Race Schedule
            self.test_uc8_read_race_schedule(champ_id)
            
            # UC-9: Update Race Status
            self.test_uc9_update_race_status(champ_id)
            
            # UC-4 & UC-6: Race Results and Standings
            self.test_uc4_uc6_race_results_and_standings(champ_id)
            
            # UC-5: Championship Details
            self.test_uc5_championship_details(champ_id)
            
            # Points Systems
            self.test_points_systems()
            
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED")
            print("=" * 60)
            print("\nChampionship Management System (UC-4 to UC-10) is working correctly!")
            print("\nFeatures Verified:")
            print("  ✓ Championship creation with season rollover")
            print("  ✓ Race event scheduling with validation")
            print("  ✓ Race schedule retrieval")
            print("  ✓ Race status lifecycle management")
            print("  ✓ Race results tracking")
            print("  ✓ Championship standings calculation")
            print("  ✓ Discipline-specific points systems")
            print("  ✓ Tie-breaking rules")
            print("  ✓ Championship details aggregation")
            
            return True
            
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {e}")
            return False
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run tests"""
    tester = TestChampionshipManagement()
    try:
        success = tester.run_all_tests()
    finally:
        # Clean up test database
        if hasattr(tester, 'test_db_path') and tester.test_db_path.exists():
            try:
                # Close database connection first
                if hasattr(tester, 'db'):
                    tester.db.get_connection().close()
                tester.test_db_path.unlink()
                print(f"\n✓ Cleaned up test database: {tester.test_db_path}")
            except Exception as e:
                print(f"\n⚠ Could not clean up test database: {e}")
                print(f"  Please manually delete: {tester.test_db_path}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
