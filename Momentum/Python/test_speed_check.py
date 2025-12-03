"""
Test that simulation runs at correct speed (5x real-time)
"""
import time
from database.database_manager import DatabaseManager
from race_simulation_api import simulate_race

def main():
    print("=" * 70)
    print("SPEED TEST - Should run at 5x real-time")
    print("=" * 70)
    
    db = DatabaseManager()
    drivers = db.get_all_drivers()[:5]
    tracks = db.get_all_tracks()
    
    if not tracks:
        print("ERROR: No tracks!")
        return
    
    track = tracks[0]
    
    print(f"\nTrack: {track.name} ({track.length_km:.2f}km)")
    print(f"Drivers: {len(drivers)}")
    print(f"Test: 2 laps (should take ~15-20 seconds at 5x speed)\n")
    
    start_time = time.time()
    
    results = simulate_race(
        drivers=drivers,
        track=track,
        seed=42,
        laps=2,
        verbose=False,
        event_callback=None,
        db=db
    )
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Test complete!")
    print(f"Elapsed time: {elapsed:.1f}s")
    print(f"Expected: ~15-20s for 2 laps at 5x speed")
    
    if 10 < elapsed < 30:
        print("✅ Speed is reasonable!")
    else:
        print("⚠️ Speed might be off")

if __name__ == "__main__":
    main()
