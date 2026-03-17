"""
Pytest Configuration and Fixtures

Provides reusable fixtures for all test suites including:
- Test database instances
- Sample driver/team/track data
- Simulation engine instances
- Mock API responses
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.database_manager import DatabaseManager
from database.models import Driver, Team, Track, Championship, Race, RaceResult


@pytest.fixture(scope="function")
def test_db():
    """Create temporary test database for isolation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_momentum.db")
        db = DatabaseManager(db_path)
        # init_database is called automatically in __init__
        yield db
        # Cleanup happens automatically with temp directory


@pytest.fixture(scope="function")
def seeded_db(test_db):
    """Database with sample data"""
    # Database already has default data from init_database
    return test_db


@pytest.fixture
def sample_drivers(seeded_db):
    """Get sample drivers from seeded database"""
    return seeded_db.get_all_drivers()[:5]


@pytest.fixture
def sample_teams(seeded_db):
    """Get sample teams from seeded database"""
    return seeded_db.get_teams_by_discipline("SINGLE_SEATER")[:5]


@pytest.fixture
def sample_tracks(seeded_db):
    """Get sample tracks from seeded database"""
    return seeded_db.get_all_tracks()[:5]


@pytest.fixture
def test_driver():
    """Create a single test driver"""
    return Driver(
        name="Test Driver",
        age=28,
        nationality="Test Country",
        discipline="SINGLE_SEATER",
        raw_speed=85,
        cornering_skill=82,
        qualifying_pace=88,
        racecraft=80,
        consistency=75,
        mental_fortitude=70,
        reactions=88,
        adaptability=72,
        decision_making=78,
        physical_fitness=80,
        confidence=75,
        motivation=85
    )


@pytest.fixture
def test_team():
    """Create a single test team"""
    return Team(
        name="Test Team",
        headquarters="Test City",
        budget_eur=50000000,
        tier="TIER_1",
        discipline="SINGLE_SEATER"
    )


@pytest.fixture
def test_track():
    """Create a single test track"""
    return Track(
        name="Test Circuit",
        country="Test Country",
        length_km=5.5,
        turns=15,
        discipline="SINGLE_SEATER",
        surface_grip=12.0,
        surface_abrasiveness=8.0,
        elevation_change_m=25.0
    )


@pytest.fixture
def test_championship(seeded_db):
    """Create a test championship"""
    drivers = seeded_db.list_drivers()[:20]
    teams = seeded_db.list_teams()[:10]
    
    championship = Championship(
        name="Test Championship",
        discipline="SINGLE_SEATER",
        season=2025,
        status="ACTIVE",
        points_system="F1_2024"
    )
    
    champ_id = seeded_db.create_championship(championship)
    return seeded_db.get_championship(champ_id)


# Markers for test categorization
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance/benchmark test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (> 1 second)"
    )
