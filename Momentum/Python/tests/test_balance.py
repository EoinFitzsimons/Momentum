#!/usr/bin/env python3
"""
Quick Balance Test - Run multiple races to check DNF rate

Tests the incident probability adjustments to ensure realistic finish rates.
Target: 60-80% of drivers finish the race (DNF rate 20-40%)
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.database_manager import DatabaseManager
from config import DATABASE_PATH
from disciplines.realtime_race_engine import RealtimeRaceEngine


def run_balance_test(num_races=5):
    """Run multiple races and report DNF statistics"""
    
    print("=" * 60)
    print("BALANCE TEST - DNF Rate Validation")
    print("=" * 60)
    print(f"Running {num_races} races to test incident probability...")
    print()
    
    print("→ Initializing database connection...", end=" ", flush=True)
    db = DatabaseManager(DATABASE_PATH)
    print("✓")
    
    total_drivers = 0
    total_finishers = 0
    total_dnfs = 0
    
    race_results = []
    
    # Get track for testing
    print("→ Loading tracks from database...", end=" ", flush=True)
    tracks = db.get_all_tracks()
    print(f"✓ {len(tracks)} tracks found")
    
    if not tracks:
        print("❌ ERROR: No tracks in database!")
        print("   Fix: python scripts/import_circuits.py")
        return 0
    
    track = tracks[0]
    print(f"→ Using track: {track.name} ({track.length_km:.2f}km)")
    print()
    
    for race_num in range(1, num_races + 1):
        print(f"\n{'='*60}")
        print(f"Race {race_num}/{num_races}")
        print(f"{'='*60}")
        
        # Get drivers
        print(f"  → Loading drivers from database...", end=" ", flush=True)
        drivers = db.get_all_drivers()[:10]  # 10 drivers per race
        print(f"✓ {len(drivers)} drivers loaded")
        
        if not drivers:
            print("ERROR: No drivers in database!")
            return 0
        
        # Display driver lineup
        print(f"  → Driver lineup:")
        for i, d in enumerate(drivers, 1):
            print(f"     {i:2d}. {d.name:25s} (Speed: {d.raw_speed:5.1f}, Consistency: {d.consistency:5.1f})")
        
        # Run race using the API (handles team loading internally)
        from services.race_simulation_api import simulate_race
        
        print(f\"  → Starting race simulation...\")
        print(f"     Track: {track.name} ({track.length_km:.2f}km)")
        print(f"     Laps: 20")
        print(f"     Speed: 100x (fast test mode)")
        print(f"  → Simulating race (this may take 10-30 seconds)...", flush=True)
        
        start_time = time.time()
        
        # Event counter for progress feedback
        event_counter = {'count': 0, 'last_report': 0}
        
        def progress_callback(event):
            event_counter['count'] += 1
            # Report every 1000 events
            if event_counter['count'] - event_counter['last_report'] >= 1000:
                elapsed = time.time() - start_time
                print(f"     [{elapsed:5.1f}s] {event_counter['count']:,} events processed...", flush=True)
                event_counter['last_report'] = event_counter['count']
        
        try:
            # Use race_simulation_api but we need to modify it to accept realtime_speed parameter
            # For now, call engine directly with faster speed
            from disciplines.realtime_race_engine import RealtimeRaceEngine
            
            engine = RealtimeRaceEngine(seed=race_num * 42)
            
            # Get teams
            teams_dict = {}
            team_ids = set(d.current_team_id for d in drivers if d.current_team_id)
            for team_id in team_ids:
                team = db.get_team(team_id)
                if team:
                    teams_dict[team_id] = team
            
            # Create placeholder teams if needed
            from database.models import Team
            if not teams_dict:
                for driver in drivers:
                    if driver.current_team_id not in teams_dict:
                        teams_dict[driver.current_team_id] = Team(
                            id=driver.current_team_id,
                            name=f"Team {driver.current_team_id}",
                            nationality="USA",
                            founded_year=2020,
                            discipline="formula",
                            tier="tier2",
                            budget=100.0,
                            headquarters="Unknown",
                            team_principal="Unknown"
                        )
            
            results_list = engine.simulate_race(
                drivers=drivers,
                teams=teams_dict,
                track=track,
                total_laps=20,
                event_callback=progress_callback,
                realtime_speed=1000.0  # 1000x for ultra-fast testing
            )
            
            elapsed = time.time() - start_time
            print(f"  ✓ Race completed in {elapsed:.1f}s ({event_counter['count']:,} total events)")
            
            # Convert to RaceResult format
            from database.models import RaceResult
            results = []
            for result in results_list:
                rr = RaceResult(
                    id=0, race_id=0,
                    driver_id=result["driver_id"],
                    team_id=result["team_id"],
                    position=result["position"],
                    points=0,
                    fastest_lap=False,
                    dnf_reason=result["dnf_reason"],
                    grid_position=result["position"]
                )
                setattr(rr, 'laps_completed', result["laps_completed"])
                setattr(rr, 'best_lap_time', result.get("best_lap_time"))
                setattr(rr, 'average_lap_time', result.get("average_lap_time"))
                results.append(rr)
            
            # Count finishers (check if they have DNF reason)
            print(f"  → Analyzing results...", end=" ", flush=True)
            finishers = len([r for r in results if not r.dnf_reason])
            dnfs = len([r for r in results if r.dnf_reason])
            print(f"✓")
            
            total_drivers += len(drivers)
            total_finishers += finishers
            total_dnfs += dnfs
            
            finish_rate = (finishers / len(drivers)) * 100
            
            print(f"\n  RACE RESULT: {finishers}/{len(drivers)} finished ({finish_rate:.0f}%)")
            
            # Show DNF details
            if dnfs > 0:
                print(f"  DNF Details:")
                for r in results:
                    if r.dnf_reason:
                        driver = next(d for d in drivers if d.id == r.driver_id)
                        print(f"    ❌ {driver.name:25s} - {r.dnf_reason}")
            
            # Show top 3 finishers
            finisher_results = [r for r in results if not r.dnf_reason][:3]
            if finisher_results:
                print(f"  Top Finishers:")
                for i, r in enumerate(finisher_results, 1):
                    driver = next(d for d in drivers if d.id == r.driver_id)
                    best = f"{r.best_lap_time:.2f}s" if hasattr(r, 'best_lap_time') and r.best_lap_time else "N/A"
                    print(f"    🏆 P{i}. {driver.name:25s} - Best lap: {best}")
            
            race_results.append({
                "race": race_num,
                "finishers": finishers,
                "dnfs": dnfs,
                "finish_rate": finish_rate
            })
            
        except Exception as e:
            print(f"\n\nFATAL ERROR in race {race_num}:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("OVERALL RESULTS")
    print("=" * 60)
    
    overall_finish_rate = (total_finishers / total_drivers) * 100 if total_drivers > 0 else 0
    overall_dnf_rate = (total_dnfs / total_drivers) * 100 if total_drivers > 0 else 0
    
    print(f"Total Drivers:    {total_drivers}")
    print(f"Total Finishers:  {total_finishers} ({overall_finish_rate:.1f}%)")
    print(f"Total DNFs:       {total_dnfs} ({overall_dnf_rate:.1f}%)")
    print()
    
    # Evaluate
    print("=" * 60)
    print("EVALUATION")
    print("=" * 60)
    
    if overall_finish_rate >= 60 and overall_finish_rate <= 80:
        print("✅ EXCELLENT: Finish rate in target range (60-80%)")
        print("   Realistic balance - some attrition but not excessive")
    elif overall_finish_rate >= 50 and overall_finish_rate < 60:
        print("⚠️  ACCEPTABLE: Finish rate slightly low (50-60%)")
        print("   Consider reducing incident rate slightly")
    elif overall_finish_rate > 80:
        print("⚠️  TOO HIGH: Finish rate too high (>80%)")
        print("   Races may lack drama - consider increasing incident rate")
    else:
        print("❌ TOO LOW: Finish rate too low (<50%)")
        print("   Incident rate too high - reduce BASE_INCIDENT_RATE")
    
    print()
    print("Race-by-Race Breakdown:")
    for result in race_results:
        status = "✅" if 60 <= result["finish_rate"] <= 80 else "⚠️"
        print(f"  {status} Race {result['race']}: {result['finishers']}/10 finished ({result['finish_rate']:.0f}%)")
    
    print()
    print("=" * 60)
    print(f"Test completed in {sum([r['finishers'] + r['dnfs'] for r in race_results]) / num_races:.0f} drivers/race")
    print("=" * 60)
    
    return overall_finish_rate


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test DNF rate balance")
    parser.add_argument("--races", type=int, default=5, help="Number of races to run")
    args = parser.parse_args()
    
    finish_rate = run_balance_test(args.races)
    
    # Exit code for automation
    if 60 <= finish_rate <= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs tuning
