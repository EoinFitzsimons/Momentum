"""
R-SIM-001: Deterministic simulation reproducibility tests.

Tests that identical RaceContext + seed produce identical simulation results
(serialized events and standings).
"""

import json
import hashlib
import pytest
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Driver, Track, RaceResult
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline
from services.race_simulation_api import simulate_race


FIXTURE_DIR = Path(__file__).parent.parent.parent / "SRS" / "fixtures"


def _load_fixture(fixture_name: str) -> dict:
    """Load a fixture from SRS/fixtures/"""
    fixture_path = FIXTURE_DIR / fixture_name
    if not fixture_path.exists():
        pytest.skip(f"Fixture {fixture_name} not found at {fixture_path}")
    with open(fixture_path) as f:
        return json.load(f)


def _build_race_context_from_fixture(fixture: dict) -> RaceContext:
    """
    Construct a RaceContext from fixture JSON.
    
    Fixture JSON schema:
    {
      "race_id": "...",
      "total_laps": 5,
      "track": {"id": 1, "name": "...", "lap_time": 78.0, "length_m": 5000},
      "drivers": [{"id": 1, "name": "...", "attributes": {...}}],
      "seed": 42
    }
    """
    track_dict = fixture.get("track", {})
    track = Track(
        id=track_dict.get("id", 1),
        name=track_dict.get("name", "Test Track"),
        lap_time=track_dict.get("lap_time", 78.0),
        length_km=track_dict.get("length_m", 5000) / 1000.0
    )

    drivers = []
    for d_dict in fixture.get("drivers", []):
        d = Driver(
            id=d_dict.get("id", 1),
            name=d_dict.get("name", "Test Driver"),
            preferred_discipline="formula"
        )
        # Set attributes if present
        for attr_name, attr_val in d_dict.get("attributes", {}).items():
            setattr(d, attr_name, attr_val)
        drivers.append(d)

    context = RaceContext(
        race_id=fixture.get("race_id", "test-001"),
        total_laps=fixture.get("total_laps", 5),
        track=track,
        drivers=drivers,
        event_callback=None
    )
    return context


def _serialize_results(results: List[RaceResult]) -> str:
    """Serialize RaceResult objects to stable JSON for comparison."""
    out = []
    for r in results:
        out.append({
            "driver_id": r.driver_id,
            "position": r.position,
            "points": r.points,
            "fastest_lap": r.fastest_lap,
            "dnf_reason": r.dnf_reason,
            "status": getattr(r, "status", "FINISHED")
        })
    return json.dumps(out, sort_keys=True)


def _hash_string(s: str) -> str:
    """Compute SHA256 hash of a string."""
    return hashlib.sha256(s.encode()).hexdigest()


def test_reproducibility_with_seed(tmp_path):
    """
    Acceptance: Running the same fixture with the same seed produces
    identical serialized outputs (hash equivalence).
    """
    fixture = _load_fixture("example_racecontext.json")
    context = _build_race_context_from_fixture(fixture)
    seed = fixture.get("seed", 42)

    # Run twice with identical seed
    results1 = simulate_race(
        drivers=context.drivers,
        track=context.track,
        seed=seed,
        laps=context.total_laps,
        verbose=False
    )

    results2 = simulate_race(
        drivers=context.drivers,
        track=context.track,
        seed=seed,
        laps=context.total_laps,
        verbose=False
    )

    # Serialize and hash
    serialized1 = _serialize_results(results1)
    serialized2 = _serialize_results(results2)
    
    hash1 = _hash_string(serialized1)
    hash2 = _hash_string(serialized2)

    assert hash1 == hash2, (
        f"Results differ for identical seed {seed}:\n"
        f"Run 1: {serialized1}\n"
        f"Run 2: {serialized2}"
    )


def test_determinism_across_multiple_runs(tmp_path):
    """
    Acceptance: 5 consecutive runs with the same seed produce identical
    serialized outputs.
    """
    fixture = _load_fixture("example_racecontext.json")
    context = _build_race_context_from_fixture(fixture)
    seed = fixture.get("seed", 42)

    results_list = []
    hashes = []

    for run in range(5):
        results = simulate_race(
            drivers=context.drivers,
            track=context.track,
            seed=seed,
            laps=context.total_laps,
            verbose=False
        )
        serialized = _serialize_results(results)
        results_list.append(results)
        hashes.append(_hash_string(serialized))

    # All hashes must match
    unique_hashes = set(hashes)
    assert len(unique_hashes) == 1, (
        f"Determinism broken: {len(unique_hashes)} unique hashes across 5 runs. "
        f"Hashes: {unique_hashes}"
    )


def test_different_seeds_produce_different_results(tmp_path):
    """
    Acceptance: Running with different seeds should (with high probability)
    produce different results.
    """
    fixture = _load_fixture("example_racecontext.json")
    context = _build_race_context_from_fixture(fixture)

    results_seed_42 = simulate_race(
        drivers=context.drivers,
        track=context.track,
        seed=42,
        laps=context.total_laps,
        verbose=False
    )

    results_seed_99 = simulate_race(
        drivers=context.drivers,
        track=context.track,
        seed=99,
        laps=context.total_laps,
        verbose=False
    )

    serialized_42 = _serialize_results(results_seed_42)
    serialized_99 = _serialize_results(results_seed_99)

    # They should differ (with high probability)
    assert serialized_42 != serialized_99, (
        "Different seeds unexpectedly produced identical results. "
        "This suggests determinism is working but the simulation is too "
        "constrained."
    )
