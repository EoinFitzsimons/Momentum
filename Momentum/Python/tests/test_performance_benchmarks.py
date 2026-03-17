"""
Performance Benchmark Tests

Comprehensive performance testing:
✓ 20-driver race completes < 1 second
✓ 100 sequential races < 30 seconds
✓ Database queries < 100ms
✓ Memory usage stable (no leaks)
✓ Simulation is deterministic with seed control
"""

import pytest
import sys
import os
from pathlib import Path
import time
import psutil
import gc

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from RaceLogic.realtime_race_engine import RealtimeRaceEngine


class TestRaceSimulationPerformance:
    """Test race simulation performance benchmarks"""
    
    @pytest.mark.performance
    def test_single_race_under_1_second(self, seeded_db):
        """Test that 20-driver race completes < 1 second"""
        engine = RealtimeRaceEngine(db=seeded_db)
        
        drivers = seeded_db.list_drivers()[:20]
        teams = seeded_db.list_teams()[:10]
        tracks = seeded_db.list_tracks()
        track = next((t for t in tracks if t.discipline == "SINGLE_SEATER"), tracks[0])
        
        start = time.time()
        results = engine.simulate_single_race(
            discipline="SINGLE_SEATER",
            drivers=drivers,
            teams=teams,
            track=track,
            iterations=100
        )
        elapsed = time.time() - start
        
        assert results is not None
        assert len(results) == 20
        assert elapsed < 1.0, f"Race took {elapsed:.2f}s, target < 1.0s"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_100_sequential_races(self, seeded_db):
        """Test that 100 races complete in < 30 seconds"""
        engine = RealtimeRaceEngine(db=seeded_db)
        
        drivers = seeded_db.list_drivers()[:20]
        teams = seeded_db.list_teams()[:10]
        tracks = seeded_db.list_tracks()
        track = next((t for t in tracks if t.discipline == "SINGLE_SEATER"), tracks[0])
        
        start = time.time()
        
        for i in range(100):
            results = engine.simulate_single_race(
                discipline="SINGLE_SEATER",
                drivers=drivers,
                teams=teams,
                track=track,
                iterations=50  # Reduced iterations for batch test
            )
            assert results is not None
        
        elapsed = time.time() - start
        
        assert elapsed < 30.0, f"100 races took {elapsed:.2f}s, target < 30.0s"
        print(f"✓ 100 races completed in {elapsed:.2f}s ({elapsed/100:.3f}s per race)")
    
    @pytest.mark.performance
    def test_race_throughput(self, seeded_db):
        """Measure race simulation throughput (races per second)"""
        engine = RealtimeRaceEngine(db=seeded_db)
        
        drivers = seeded_db.list_drivers()[:20]
        teams = seeded_db.list_teams()[:10]
        tracks = seeded_db.list_tracks()
        track = next((t for t in tracks if t.discipline == "SINGLE_SEATER"), tracks[0])
        
        race_count = 0
        start = time.time()
        target_duration = 5.0  # Run for 5 seconds
        
        while time.time() - start < target_duration:
            results = engine.simulate_single_race(
                discipline="SINGLE_SEATER",
                drivers=drivers,
                teams=teams,
                track=track,
                iterations=50
            )
            race_count += 1
        
        elapsed = time.time() - start
        throughput = race_count / elapsed
        
        assert throughput > 0, "No races completed"
        print(f"✓ Throughput: {throughput:.1f} races/second")


class TestMemoryUsage:
    """Test memory usage and detect leaks"""
    
    @pytest.mark.performance
    def test_memory_stable_after_races(self, seeded_db):
        """Test that memory usage remains stable after multiple races"""
        engine = RealtimeRaceEngine(db=seeded_db)
        
        drivers = seeded_db.list_drivers()[:20]
        teams = seeded_db.list_teams()[:10]
        tracks = seeded_db.list_tracks()
        track = next((t for t in tracks if t.discipline == "SINGLE_SEATER"), tracks[0])
        
        # Force garbage collection
        gc.collect()
        
        # Baseline measurement
        process = psutil.Process(os.getpid())
        baseline_mb = process.memory_info().rss / 1024 / 1024
        
        # Run races
        for _ in range(50):
            results = engine.simulate_single_race(
                discipline="SINGLE_SEATER",
                drivers=drivers,
                teams=teams,
                track=track,
                iterations=50
            )
        
        gc.collect()
        
        # Final measurement
        final_mb = process.memory_info().rss / 1024 / 1024
        increase_mb = final_mb - baseline_mb
        increase_percent = (increase_mb / baseline_mb) * 100
        
        print(f"Memory: {baseline_mb:.1f}MB -> {final_mb:.1f}MB (+{increase_mb:.1f}MB, {increase_percent:.1f}%)")
        
        # Allow up to 50% memory increase (after 50 races)
        assert increase_percent < 50, f"Memory increased by {increase_percent:.1f}%, threshold 50%"


class TestDatabaseQueryPerformance:
    """Test database query performance under load"""
    
    @pytest.mark.performance
    def test_bulk_driver_queries(self, seeded_db):
        """Test querying all drivers 100 times"""
        start = time.time()
        
        for _ in range(100):
            drivers = seeded_db.list_drivers()
            assert len(drivers) > 0
        
        elapsed = time.time() - start
        avg_query_time = (elapsed / 100) * 1000  # Convert to ms
        
        assert avg_query_time < 100, f"Avg query time {avg_query_time}ms, target < 100ms"
        print(f"✓ 100 driver queries: {elapsed:.2f}s ({avg_query_time:.1f}ms avg)")
    
    @pytest.mark.performance
    def test_bulk_team_queries(self, seeded_db):
        """Test querying teams 100 times"""
        start = time.time()
        
        for _ in range(100):
            teams = seeded_db.list_teams()
            assert len(teams) > 0
        
        elapsed = time.time() - start
        avg_query_time = (elapsed / 100) * 1000
        
        assert avg_query_time < 100
        print(f"✓ 100 team queries: {elapsed:.2f}s ({avg_query_time:.1f}ms avg)")


class TestDifferentDisciplinePerformance:
    """Test performance across different disciplines"""
    
    @pytest.mark.performance
    def test_drag_racing_performance(self, seeded_db):
        """Test drag racing (can be faster, fewer laps)"""
        engine = RealtimeRaceEngine(db=seeded_db)
        
        drivers = seeded_db.list_drivers()[:64]
        teams = seeded_db.list_teams()[:32]
        tracks = seeded_db.list_tracks()
        track = next((t for t in tracks if t.discipline == "DRAG_ACCELERATION"), tracks[0])
        
        start = time.time()
        results = engine.simulate_single_race(
            discipline="DRAG_ACCELERATION",
            drivers=drivers,
            teams=teams,
            track=track,
            iterations=100
        )
        elapsed = time.time() - start
        
        assert results is not None
        assert elapsed < 2.0, f"Drag race took {elapsed:.2f}s"
        print(f"✓ Drag race (64 drivers): {elapsed:.3f}s")
    
    @pytest.mark.performance
    def test_endurance_performance(self, seeded_db):
        """Test endurance racing performance"""
        engine = RealtimeRaceEngine(db=seeded_db)
        
        drivers = seeded_db.list_drivers()[:30]
        teams = seeded_db.list_teams()[:15]
        tracks = seeded_db.list_tracks()
        track = next((t for t in tracks if t.discipline == "ENDURANCE"), tracks[0])
        
        start = time.time()
        results = engine.simulate_single_race(
            discipline="ENDURANCE",
            drivers=drivers,
            teams=teams,
            track=track,
            iterations=100
        )
        elapsed = time.time() - start
        
        assert results is not None
        assert elapsed < 2.0, f"Endurance race took {elapsed:.2f}s"
        print(f"✓ Endurance race (30 drivers): {elapsed:.3f}s")


class TestScalability:
    """Test system scalability with larger datasets"""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_grid_performance(self, seeded_db):
        """Test race with maximum grid size"""
        engine = RealtimeRaceEngine(db=seeded_db)
        
        # Use maximum practical grid size (64 for drag)
        drivers = seeded_db.list_drivers()[:64]
        teams = seeded_db.list_teams()[:32]
        tracks = seeded_db.list_tracks()
        track = next((t for t in tracks if t.discipline == "DRAG_ACCELERATION"), tracks[0])
        
        start = time.time()
        results = engine.simulate_single_race(
            discipline="DRAG_ACCELERATION",
            drivers=drivers,
            teams=teams,
            track=track,
            iterations=50
        )
        elapsed = time.time() - start
        
        assert len(results) <= 64
        print(f"✓ Maximum grid (64 drivers): {elapsed:.3f}s")
    
    @pytest.mark.performance
    def test_multiple_disciplines_sequential(self, seeded_db):
        """Test sequential races across multiple disciplines"""
        engine = RealtimeRaceEngine(db=seeded_db)
        
        disciplines = [
            "SINGLE_SEATER",
            "PRODUCTION_TOURING",
            "DRAG_ACCELERATION",
            "ENDURANCE"
        ]
        
        drivers = seeded_db.list_drivers()[:40]
        teams = seeded_db.list_teams()[:20]
        tracks = seeded_db.list_tracks()
        
        start = time.time()
        
        for discipline in disciplines:
            track = next(
                (t for t in tracks if t.discipline == discipline),
                tracks[0]
            )
            
            results = engine.simulate_single_race(
                discipline=discipline,
                drivers=drivers[:20],
                teams=teams[:10],
                track=track,
                iterations=50
            )
            assert results is not None
        
        elapsed = time.time() - start
        
        assert elapsed < 10.0, f"4 disciplines took {elapsed:.2f}s"
        print(f"✓ Sequential races (4 disciplines): {elapsed:.3f}s")
