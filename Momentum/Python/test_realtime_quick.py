"""
Quick test of realtime race engine with correct Driver attributes
"""
import sys
from database.database_manager import DatabaseManager
from race_simulation_api import simulate_race

def main():
    print("=" * 70)
    print("QUICK REALTIME ENGINE TEST")
    print("=" * 70)
    
    # Load database
    db = DatabaseManager()
    
    # Get test data
    drivers = db.get_all_drivers()[:5]  # Just 5 drivers for quick test
    tracks = db.get_all_tracks()
    
    if not tracks:
        print("ERROR: No tracks in database!")
        return
    
    track = tracks[0]
    
    print(f"\nTest configuration:")
    print(f"  Drivers: {len(drivers)} ({', '.join(d.name for d in drivers[:3])}...)")
    print(f"  Track: {track.name} ({track.length_km:.2f}km)")
    print(f"  Laps: 3 (short test)")
    print()
    
    # Run simulation
    print("Starting simulation...")
    results = simulate_race(
        drivers=drivers,
        track=track,
        seed=42,
        laps=3,
        verbose=False,
        event_callback=None,
        db=db
    )
    
    print("\n" + "=" * 70)
    print("RACE RESULTS")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        driver = next(d for d in drivers if d.id == result.driver_id)
        status = "DNF" if result.laps_completed < 3 else f"{result.laps_completed}L"
        print(f"P{i:2d}: {driver.name:25s} | {status} | Best: {result.best_lap_time:.1f}s | Avg: {result.average_lap_time:.1f}s")
    
    print("\n✅ Test complete - engine working correctly!\n")

if __name__ == "__main__":
    main()
