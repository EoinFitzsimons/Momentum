"""
Quick Validation Tests - Verify Test Infrastructure

Simple tests to validate that the test infrastructure works correctly
before running the full comprehensive test suite.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.database_manager import DatabaseManager


class TestBasicSetup:
    """Test that basic infrastructure works"""
    
    @pytest.mark.unit
    def test_database_manager_initializes(self):
        """Test that DatabaseManager initializes"""
        db = DatabaseManager()
        assert db is not None
        assert hasattr(db, 'get_all_drivers')
    
    @pytest.mark.unit
    def test_database_has_drivers(self):
        """Test that database has drivers"""
        db = DatabaseManager()
        drivers = db.get_all_drivers()
        assert len(drivers) > 0
        print(f"✓ Database has {len(drivers)} drivers")
    
    @pytest.mark.unit
    def test_database_has_teams(self):
        """Test that database has teams"""
        db = DatabaseManager()
        teams = db.get_teams_by_discipline("SINGLE_SEATER")
        assert len(teams) > 0
        print(f"✓ Database has {len(teams)} SS teams")
    
    @pytest.mark.unit
    def test_database_has_tracks(self):
        """Test that database has tracks"""
        db = DatabaseManager()
        tracks = db.get_all_tracks()
        assert len(tracks) > 0
        print(f"✓ Database has {len(tracks)} tracks")
    
    @pytest.mark.unit
    def test_get_driver(self):
        """Test that we can get a driver"""
        db = DatabaseManager()
        drivers = db.get_all_drivers()
        driver = db.get_driver(drivers[0].id)
        assert driver is not None
        assert driver.id == drivers[0].id
        print(f"✓ Retrieved driver: {driver.name}")
