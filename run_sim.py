import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'Momentum', 'Python'))

from database.database_manager import DatabaseManager
from RaceLogic.realtime_race_engine import RealtimeRaceEngine

def run_simulation():
    db_path = os.path.join('Momentum', 'Python', 'database', 'momentum.db')
    db = DatabaseManager(db_path)
    
    tracks = db.get_tracks()
    track = tracks[0]
    for t in tracks:
        if 'single' in str(t.discipline).lower():
            track = t
            break
            
    drivers = db.get_drivers()[:20]
    all_teams = db.get_teams()
    teams_dict = {team.id: team for team in all_teams}

    event_counts = {'overtake_attempt': 0, 'overtake': 0}
    
    def event_callback(event):
        if event.get('type') == 'overtake_attempt':
            event_counts['overtake_attempt'] += 1
        elif event.get('type') == 'overtake':
            event_counts['overtake'] += 1

    engine = RealtimeRaceEngine(db=db)
    
    try:
        engine.simulate_race(
            drivers=drivers, 
            teams=teams_dict, 
            track=track, 
            total_laps=3, 
            event_callback=event_callback,
            realtime_speed=1000.0
        )
        print(f"Simulation Finished.")
        print(f"Overtake Attempts: {event_counts['overtake_attempt']}")
        print(f"Overtakes: {event_counts['overtake']}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_simulation()
