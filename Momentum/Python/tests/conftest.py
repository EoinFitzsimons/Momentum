"""Shared fixtures for Momentum backend test suite.

This suite is intentionally deterministic and report-friendly:
- Isolated temporary SQLite database per test
- Explicitly seeded reference data
- API client fixture patched to test DB
"""

from __future__ import annotations

import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
import os

import pytest
from fastapi.testclient import TestClient

# Ensure imports resolve from Momentum/Python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure offscreen Qt rendering for headless CI/test environments before any PyQt6 imports
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from database.database_manager import DatabaseManager
from database.models import Championship, Driver, Team, Track
from services.championship_service import ChampionshipService
from services.team_service import TeamService


@pytest.fixture(scope="function")
def test_db() -> Iterator[DatabaseManager]:
    """Create an isolated temporary SQLite database for each test."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        db_path = Path(temp_dir) / "momentum_test.db"
        db = DatabaseManager(str(db_path))
        yield db


@pytest.fixture(scope="function")
def seeded_db(test_db: DatabaseManager):
    """Seed deterministic teams, tracks, and drivers for stable tests."""
    team_ids = []
    for idx in range(3):
        team_id = test_db.create_team(
            Team(
                id=0,
                name=f"Team {idx + 1}",
                nationality="UK",
                discipline="SINGLE_SEATER",
                tier="TIER_1",
                budget=50_000_000 + idx * 1_000_000,
                headquarters="Silverstone",
                team_principal=f"Principal {idx + 1}",
            )
        )
        team_ids.append(team_id)

    track_specs = [
        ("Alpha Circuit", "SINGLE_SEATER", "asphalt"),
        ("Beta Raceway", "SPRINT_RALLYCROSS", "asphalt"),
        ("Gamma Park", "SINGLE_SEATER", "asphalt"),
    ]
    track_ids = []
    for name, discipline, surface in track_specs:
        track_id = test_db.create_track(
            Track(
                id=0,
                name=name,
                country="UK",
                primary_discipline=discipline,
                length_km=4.5,
                turns=12,
                avg_speed_kmh=175.0,
                longest_straight_m=800.0,
                tightest_corner_radius_m=35.0,
                left_turns=6,
                right_turns=6,
                drs_zones=1,
                surface=surface,
            )
        )
        track_ids.append(track_id)

    driver_ids = []
    for idx in range(6):
        driver_id = test_db.create_driver(
            Driver(
                id=0,
                name=f"Driver {idx + 1}",
                nationality="GBR",
                birth_date="1998-01-01",
                speed=70 + idx,
                racecraft=68 + idx,
                consistency=65 + idx,
                preferred_discipline="SINGLE_SEATER",
                current_team_id=team_ids[idx % len(team_ids)],
            )
        )
        driver_ids.append(driver_id)

    return {
        "db": test_db,
        "team_ids": team_ids,
        "track_ids": track_ids,
        "driver_ids": driver_ids,
    }


@pytest.fixture(scope="function")
def seeded_championship(seeded_db):
    """Create a championship season with scheduled races using seeded tracks."""
    db: DatabaseManager = seeded_db["db"]
    service = ChampionshipService(db)

    championship = Championship(
        id=0,
        name="Test Championship",
        discipline="SPRINT_RALLYCROSS",
        season_length=3,
        points_system="SPRINT_RALLYCROSS",
        current_season=1,
    )

    champ_id, race_ids = service.create_championship_season(
        championship=championship,
        tracks=seeded_db["track_ids"],
        start_date=__import__("datetime").datetime(2026, 1, 1),
    )

    return {
        "db": db,
        "service": service,
        "championship_id": champ_id,
        "race_ids": race_ids,
        "seed": seeded_db,
    }


@pytest.fixture(scope="function")
def api_client(seeded_db, monkeypatch):
    """Return FastAPI TestClient with simulation services patched to test DB."""
    import simulation

    db: DatabaseManager = seeded_db["db"]
    monkeypatch.setattr(simulation, "db_manager", db)
    monkeypatch.setattr(simulation, "championship_service", ChampionshipService(db))
    monkeypatch.setattr(simulation, "team_service", TeamService(db))

    return TestClient(simulation.app)
