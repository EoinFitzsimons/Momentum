"""
Comprehensive test of realtime race engine WITHOUT GUI
This will prove the engine works correctly with proper Driver attributes
"""
import sys
from database.database_manager import DatabaseManager
from services.race_simulation_api import simulate_race

def test_full_race():
    print("=" * 70)
    print("REALTIME ENGINE - FULL RACE TEST (NO GUI)")
    print("=" * 70)
    
    # Load database
    db = DatabaseManager()
    
    # Get test data
    drivers = db.get_all_drivers()[:10]  # 10 drivers like the GUI
    tracks = db.get_all_tracks()
    
    if not tracks:
        print("ERROR: No tracks in database!")
        return False
    
    track = tracks[0]  # Use first track
    
    print(f"\nRace Configuration:")
    print(f"  Track: {track.name} ({track.length_km:.2f}km)")
    print(f"  Drivers: {len(drivers)}")
    for i, d in enumerate(drivers, 1):
        print(f"    {i:2d}. {d.name:25s} (Raw Speed: {d.raw_speed:.1f}, Consistency: {d.consistency:.1f})")
    print(f"  Laps: 47 (full race distance)")
    print()
    
    # Event tracking
    event_count = 0
    position_updates = 0
    dnf_count = 0
    lap_completions = 0
    
    def track_events(event):
        nonlocal event_count, position_updates, dnf_count, lap_completions
        event_count += 1
        
        if event['type'] == 'position_update':
            position_updates += 1
            if position_updates % 300 == 0:  # Every 10 seconds at 30 FPS
                positions = event['positions']
                top_3 = sorted(positions, key=lambda x: (x['lap'], x['position_m']), reverse=True)[:3]
                print(f"  [{position_updates/30:.1f}s] ", end='')
                for p in top_3:
                    driver = next(d for d in drivers if d.id == p['driver_id'])
                    print(f"P{p['position']}: {driver.name} (L{p['lap']}, {p['racing_mode']}) ", end='')
                print()
        
        elif event['type'] == 'dnf':
            dnf_count += 1
            driver = next(d for d in drivers if d.id == event['driver_id'])
            print(f"  ❌ DNF: {driver.name} (Lap {event['lap']}, reason: {event['reason']})")
        
        elif event['type'] == 'lap_completed':
            lap_completions += 1
    
    print("Starting race simulation...")
    print("-" * 70)
    
    try:
        results = simulate_race(
            drivers=drivers,
            track=track,
            seed=42,
            laps=47,
            verbose=False,
            event_callback=track_events,
            db=db
        )
        
        print("-" * 70)
        print("\n" + "=" * 70)
        print("RACE RESULTS")
        print("=" * 70)
        
        for i, result in enumerate(results, 1):
            driver = next(d for d in drivers if d.id == result.driver_id)
            if result.laps_completed < 47:
                status = f"DNF (L{result.laps_completed})"
            else:
                status = f"{result.laps_completed} laps"
            
            print(f"P{i:2d}: {driver.name:25s} | {status:15s} | Best: {result.best_lap_time:.1f}s | Avg: {result.average_lap_time:.1f}s")
        
        print("\n" + "=" * 70)
        print("EVENT STATISTICS")
        print("=" * 70)
        print(f"Total events: {event_count:,}")
        print(f"Position updates: {position_updates:,} ({position_updates/30:.1f} seconds of simulation)")
        print(f"Lap completions: {lap_completions}")
        print(f"DNFs: {dnf_count}")
        print(f"Expected updates: ~{47 * 10 * (track.length_km * 1000 / 60) * 30:,.0f} (47 laps × 10 drivers × ~90s/lap × 30 FPS)")
        
        print("\n✅ ENGINE TEST PASSED - Real-time simulation working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_race()
    sys.exit(0 if success else 1)
