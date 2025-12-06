"""
Gap Tracking Diagnostic Test

Runs a race simulation and monitors gap calculations to identify issues
with the 999+ encoding appearing incorrectly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager
from RaceLogic.realtime_race_engine import RealtimeRaceEngine
from database.models import Driver, Team, Track
from typing import Dict, List, Any
import time


def track_gaps_callback(event: Dict[str, Any], gap_log: List[Dict]):
    """Callback to track gap calculations"""
    if event.get('type') == 'position_update':
        positions = event.get('positions', [])
        race_time = event.get('time', 0)
        
        # Sort by position
        positions.sort(key=lambda p: p['position'])
        
        # Check for anomalies
        for i, pos in enumerate(positions):
            gap_ahead = pos.get('gap_ahead', 0)
            lap = pos.get('lap', 0)
            
            # Log if gap is encoded (999+)
            if gap_ahead >= 999.0:
                lap_diff = int(gap_ahead - 999.0)
                if lap_diff == 0:
                    # This is suspicious - 999.0 exactly means something went wrong
                    gap_log.append({
                        'time': race_time,
                        'driver': pos['driver_name'],
                        'position': pos['position'],
                        'lap': lap,
                        'gap_ahead': gap_ahead,
                        'issue': 'SUSPICIOUS_999',
                        'running': pos.get('running', True)
                    })
                elif lap_diff > 0:
                    # Valid lap difference encoding
                    gap_log.append({
                        'time': race_time,
                        'driver': pos['driver_name'],
                        'position': pos['position'],
                        'lap': lap,
                        'gap_ahead': gap_ahead,
                        'issue': f'LAP_DIFF_{lap_diff}',
                        'running': pos.get('running', True)
                    })
            
            # Log position 1 (leader) always
            if i == 0:
                gap_log.append({
                    'time': race_time,
                    'driver': pos['driver_name'],
                    'position': 1,
                    'lap': lap,
                    'gap_ahead': gap_ahead,
                    'issue': 'LEADER',
                    'running': pos.get('running', True)
                })


def run_gap_tracking_test():
    """Run race with detailed gap tracking"""
    print("=" * 70)
    print("GAP TRACKING DIAGNOSTIC TEST")
    print("=" * 70)
    
    # Initialize database
    db = DatabaseManager()
    
    # Get test drivers
    drivers = db.get_all_drivers()[:10]
    print(f"\nLoaded {len(drivers)} drivers for test")
    for d in drivers:
        print(f"  - {d.name} (ID: {d.id})")
    
    # Get teams - get from drivers' team IDs
    team_ids = set(d.current_team_id for d in drivers if d.current_team_id)
    teams = {}
    for team_id in team_ids:
        team = db.get_team(team_id)
        if team:
            teams[team_id] = team
    print(f"\nLoaded {len(teams)} teams")
    
    # Get track
    tracks = db.get_all_tracks()
    track = tracks[0] if tracks else None
    if not track:
        print("ERROR: No tracks found!")
        return
    
    print(f"\nUsing track: {track.name} ({track.length_km}km)")
    
    # Create gap log
    gap_log = []
    
    # Create callback wrapper
    def event_callback(event):
        track_gaps_callback(event, gap_log)
    
    # Initialize engine
    engine = RealtimeRaceEngine()
    
    # Run simulation
    print("\n" + "=" * 70)
    print("STARTING RACE SIMULATION")
    print("=" * 70)
    
    try:
        results = engine.simulate_race(
            drivers=drivers,
            teams=teams,
            track=track,  # Pass Track object, not length
            total_laps=3,  # Short race for testing
            event_callback=event_callback,
            realtime_speed=100,  # Fast simulation
            player_overrides=None
        )
        
        print("\n" + "=" * 70)
        print("RACE COMPLETE")
        print("=" * 70)
        
        # Print results
        print(f"\nFinal Results:")
        for i, result in enumerate(results[:5], 1):
            dnf = result.get('dnf_reason')
            status = f"DNF ({dnf})" if dnf else "FINISHED"
            print(f"  P{i}: {result['driver_name']} - {status} - {result['laps_completed']} laps")
        
    except Exception as e:
        print(f"\nERROR during simulation: {e}")
        import traceback
        traceback.print_exc()
    
    # Analyze gap log
    print("\n" + "=" * 70)
    print("GAP ANALYSIS")
    print("=" * 70)
    
    # Filter suspicious 999.0 gaps
    suspicious = [g for g in gap_log if g['issue'] == 'SUSPICIOUS_999']
    lap_diffs = [g for g in gap_log if g['issue'].startswith('LAP_DIFF_')]
    leaders = [g for g in gap_log if g['issue'] == 'LEADER']
    
    print(f"\nTotal gap measurements: {len(gap_log)}")
    print(f"Leader measurements: {len(leaders)}")
    print(f"Lap difference encodings: {len(lap_diffs)}")
    print(f"SUSPICIOUS 999.0 gaps: {len(suspicious)}")
    
    if suspicious:
        print("\n!!! SUSPICIOUS 999.0 GAPS FOUND !!!")
        print("These gaps should not be exactly 999.0 - indicates calculation error")
        print("-" * 70)
        for g in suspicious[:20]:  # Show first 20
            print(f"  Time {g['time']:.1f}s: {g['driver']} (P{g['position']}, L{g['lap']}) - gap={g['gap_ahead']:.1f}s, running={g['running']}")
    else:
        print("\n✓ No suspicious 999.0 gaps found")
    
    if lap_diffs:
        print(f"\nValid lap difference encodings found: {len(lap_diffs)}")
        print("Sample lap differences:")
        for g in lap_diffs[:10]:
            lap_behind = int(g['gap_ahead'] - 999.0)
            print(f"  Time {g['time']:.1f}s: {g['driver']} (P{g['position']}, L{g['lap']}) - {lap_behind} lap(s) behind")
    
    # Check leader progression
    print("\nLeader lap progression:")
    for g in leaders[::30]:  # Sample every 30 frames (1 second)
        print(f"  Time {g['time']:.1f}s: {g['driver']} on lap {g['lap']}")
    
    # Look for gaps when leader changes lap
    print("\nGap behavior when leader completes laps:")
    for i, g in enumerate(leaders):
        if i > 0 and g['lap'] > leaders[i-1]['lap']:
            print(f"  Leader completed lap {leaders[i-1]['lap']} → {g['lap']} at time {g['time']:.1f}s")
            # Show gaps of other cars around this time
            nearby_gaps = [gg for gg in gap_log if abs(gg['time'] - g['time']) < 0.5 and gg['position'] > 1]
            if nearby_gaps:
                print(f"    Other cars at this time:")
                for gg in nearby_gaps[:5]:
                    print(f"      P{gg['position']}: {gg['driver']} - gap={gg['gap_ahead']:.1f}s, lap={gg['lap']}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_gap_tracking_test()
