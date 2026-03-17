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
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_momentum.db")
        db = DatabaseManager(db_path)
        # init_database is called automatically in __init__
        yield db
        # Cleanup happens automatically with temp directory


@pytest.fixture(scope="function")
def seeded_db(test_db):
    """Database with sample data"""
    # Populate minimal baseline data expected by integration tests.
    if len(test_db.get_all_drivers()) == 0:
        with test_db.get_connection() as conn:
            for i in range(1, 11):
                conn.execute(
                    """
                    INSERT INTO drivers (name, nationality, birth_date, speed, racecraft, consistency, preferred_discipline)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (f"Seed Driver {i}", "GBR", "1995-01-01", 60 + i, 55 + i, 50 + i, "SINGLE_SEATER"),
                )

            for i in range(1, 6):
                conn.execute(
                    """
                    INSERT INTO teams (name, nationality, discipline, tier, budget, operations_rating)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (f"Seed Team {i}", "GBR", "SINGLE_SEATER", "TIER_1", 50_000_000.0, 70.0 + i),
                )

            for i in range(1, 4):
                conn.execute(
                    """
                    INSERT INTO tracks (name, country, primary_discipline, surface, length_km, turns, avg_speed_kmh)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (f"Seed Circuit {i}", "UK", "SINGLE_SEATER", "asphalt", 4.0 + i * 0.2, 10 + i, 170.0),
                )
            conn.commit()

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
        id=1,
        name="Test Driver",
        nationality="Test Country",
        birth_date="1996-01-01",
        speed=85,
        racecraft=80,
        consistency=75,
        pressure=70,
        reactions=88,
        adaptability=72,
        fitness=80,
        preferred_discipline="SINGLE_SEATER",
    )


@pytest.fixture
def test_team():
    """Create a single test team"""
    return Team(
        id=1,
        nationality="Test Country",
        discipline="SINGLE_SEATER",
        tier="TIER_1",
        budget=50000000,
        name="Test Team",
        headquarters="Test City",
    )


@pytest.fixture
def test_track():
    """Create a single test track"""
    return Track(
        id=1,
        name="Test Circuit",
        country="Test Country",
        primary_discipline="SINGLE_SEATER",
        length_km=5.5,
        turns=15,
        surface_grip=1.0,
        surface_abrasiveness=8.0,
    )


@pytest.fixture
def test_championship(seeded_db):
    """Create a test championship"""
    drivers = seeded_db.list_drivers()[:20]
    teams = seeded_db.list_teams()[:10]
    
    championship = Championship(
        id=0,
        name="Test Championship",
        discipline="SINGLE_SEATER",
        season_length=10,
        points_system="standard",
        current_season=1,
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
