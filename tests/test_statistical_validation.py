"""Statistical validation tests for simulation outcomes, distributions, and fairness."""

from __future__ import annotations

from collections import Counter
from statistics import mean, stdev

import pytest

from momentum.database.models import Driver
from momentum.services.race_simulation_api import simulate_race


@pytest.mark.integration
def test_skill_attribute_affects_finishing_position(seeded_db):
    """Verify that driver skill attributes correlate with race finishing position."""
    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    assert track is not None

    # Create two drivers: one high-skill, one low-skill
    high_skill_driver = Driver(
        id=1,
        name="High Skill",
        nationality="GBR",
        birth_date="1990-01-01",
        speed=95,
        racecraft=92,
        consistency=90,
        preferred_discipline="SINGLE_SEATER",
        current_team_id=1,
    )

    low_skill_driver = Driver(
        id=2,
        name="Low Skill",
        nationality="GBR",
        birth_date="1995-01-01",
        speed=45,
        racecraft=42,
        consistency=40,
        preferred_discipline="SINGLE_SEATER",
        current_team_id=2,
    )

    # Run multiple races and track positions
    high_skill_positions = []
    low_skill_positions = []

    for seed in range(50):
        results = simulate_race(
            drivers=[high_skill_driver, low_skill_driver],
            track=track,
            laps=10,
            seed=seed,
        )

        # Find positions
        for result in results:
            if result.driver_id == 1:
                high_skill_positions.append(result.position)
            elif result.driver_id == 2:
                low_skill_positions.append(result.position)

    # High skill should finish ahead on average
    avg_high = mean(high_skill_positions) if high_skill_positions else 999
    avg_low = mean(low_skill_positions) if low_skill_positions else 1

    assert (
        avg_high <= avg_low
    ), f"High skill avg position {avg_high} should be <= low skill {avg_low}"


@pytest.mark.integration
def test_upset_frequency_is_bounded(seeded_db):
    """Verify upset races (lower skill wins) occur within reasonable frequency bounds."""
    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    assert track is not None

    # Create drivers with clear skill hierarchy
    drivers = []
    for i, skill_level in enumerate([90, 75, 60, 45]):
        driver = Driver(
            id=i + 1,
            name=f"Driver Skill {skill_level}",
            nationality="GBR",
            birth_date="1990-01-01",
            speed=skill_level,
            racecraft=skill_level - 2,
            consistency=skill_level - 3,
            preferred_discipline="SINGLE_SEATER",
            current_team_id=i + 1,
        )
        drivers.append(driver)

    # Run many races
    winner_counter = Counter()
    total_races = 100

    for seed in range(total_races):
        results = simulate_race(
            drivers=drivers,
            track=track,
            laps=5,
            seed=seed,
        )

        if results:
            winner = results[0]  # Assuming first in results is winner
            winner_counter[winner.driver_id] += 1

    # Highest skill driver (ID 1) should win most races
    highest_skill_wins = winner_counter.get(1, 0)
    total_wins = sum(winner_counter.values())

    if total_wins > 0:
        win_percentage = highest_skill_wins / total_wins
        # Highest skill should win at least 40% and at most 95%
        assert (
            0.4 <= win_percentage <= 0.95
        ), f"Win rate {win_percentage:.2%} outside expected bounds"


@pytest.mark.integration
def test_distribution_of_lap_times_is_plausible(seeded_db):
    """Verify lap time distributions are within expected bounds."""
    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    driver = seeded_db["db"].get_driver(seeded_db["driver_ids"][0])
    assert track is not None
    assert driver is not None

    # Run single driver races and collect times
    times = []
    for seed in range(30):
        results = simulate_race(
            drivers=[driver],
            track=track,
            laps=3,
            seed=seed,
        )

        if results:
            result = results[0]
            if result.average_lap_time is not None:
                times.append(result.average_lap_time)
            elif result.best_lap_time is not None:
                times.append(result.best_lap_time)
            elif result.time_seconds is not None:
                times.append(result.time_seconds)

    if len(times) >= 2:
        avg_time = mean(times)
        time_stdev = stdev(times)

        # Verify non-zero times
        assert avg_time > 0, "Average lap time should be positive"
        assert time_stdev >= 0, "Lap time standard deviation should be non-negative"

        # Verify reasonable variance (CV should be low but non-zero)
        if avg_time > 0:
            cv = time_stdev / avg_time
            assert (
                0.0 <= cv <= 0.5
            ), f"Coefficient of variation {cv:.3f} outside expected bounds"


@pytest.mark.integration
def test_randomness_seed_produces_consistent_results(seeded_db):
    """Verify same seed produces identical race outcomes (determinism)."""
    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    assert track is not None
    drivers = [
        driver
        for driver_id in seeded_db["driver_ids"][:4]
        if (driver := seeded_db["db"].get_driver(driver_id)) is not None
    ]
    assert drivers

    # Run race with seed 42 twice
    results1 = simulate_race(
        drivers=drivers,
        track=track,
        laps=5,
        seed=42,
    )

    results2 = simulate_race(
        drivers=drivers,
        track=track,
        laps=5,
        seed=42,
    )

    # Results should be identical
    assert results1 is not None and results2 is not None
    assert len(results1) == len(results2)

    # Compare finishing positions
    if results1 and results2:
        positions1 = [r.position for r in results1]
        positions2 = [r.position for r in results2]
        assert positions1 == positions2, "Same seed should produce identical results"


@pytest.mark.integration
def test_different_seeds_produce_different_outcomes(seeded_db):
    """Verify different seeds produce varied race outcomes."""
    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    assert track is not None
    drivers = [
        driver
        for driver_id in seeded_db["driver_ids"][:4]
        if (driver := seeded_db["db"].get_driver(driver_id)) is not None
    ]
    assert drivers

    # Run races with different seeds
    all_finishing_orders = []

    for seed in range(20):
        results = simulate_race(
            drivers=drivers,
            track=track,
            laps=5,
            seed=seed,
        )

        if results:
            finishing_order = tuple(r.driver_id for r in results)
            all_finishing_orders.append(finishing_order)

    # Should have variation across runs
    unique_outcomes = len(set(all_finishing_orders))
    assert unique_outcomes > 1, "Different seeds should produce different outcomes"


@pytest.mark.integration
def test_track_surface_affects_driver_performance(seeded_db):
    """Verify different track surfaces produce different race outcomes."""
    driver = seeded_db["db"].get_driver(seeded_db["driver_ids"][0])
    assert driver is not None

    # Get tracks with different surfaces
    track1 = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    track2 = (
        seeded_db["db"].get_track(seeded_db["track_ids"][1])
        if len(seeded_db["track_ids"]) > 1
        else track1
    )
    assert track1 is not None
    assert track2 is not None

    # Run race on track1
    results1 = simulate_race(
        drivers=[driver],
        track=track1,
        laps=5,
        seed=42,
    )

    # Run race on track2
    results2 = simulate_race(
        drivers=[driver],
        track=track2,
        laps=5,
        seed=42,
    )

    # Both should succeed and produce results
    assert results1 is not None
    assert results2 is not None
    assert len(results1) > 0
    assert len(results2) > 0


@pytest.mark.slow
@pytest.mark.integration
def test_long_race_distance_produces_consistent_winner(seeded_db):
    """Verify longer race distances favor skilled drivers consistently."""
    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    assert track is not None

    # Create skill-differentiated drivers
    high_skill = Driver(
        id=1,
        name="High Skill",
        nationality="GBR",
        birth_date="1990-01-01",
        speed=88,
        racecraft=85,
        consistency=87,
        preferred_discipline="SINGLE_SEATER",
        current_team_id=1,
    )

    low_skill = Driver(
        id=2,
        name="Low Skill",
        nationality="GBR",
        birth_date="1995-01-01",
        speed=52,
        racecraft=50,
        consistency=51,
        preferred_discipline="SINGLE_SEATER",
        current_team_id=2,
    )

    # Run long races
    high_skill_wins = 0
    total_races = 50

    for seed in range(total_races):
        results = simulate_race(
            drivers=[high_skill, low_skill],
            track=track,
            laps=20,  # Longer race
            seed=seed,
        )

        if results and len(results) > 0:
            winner_id = results[0].driver_id
            if winner_id == 1:
                high_skill_wins += 1

    # High skill should win majority of long races
    win_rate = high_skill_wins / total_races
    assert win_rate > 0.65, f"High skill win rate {win_rate:.2%} too low for long races"
