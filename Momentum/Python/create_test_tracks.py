"""
Quick Track Generator for Testing

Creates a minimal set of tracks for race simulation testing.
"""

import sys
sys.path.insert(0, '.')

from database.database_manager import DatabaseManager
from database.models import Track

def create_test_tracks():
    """Create a minimal set of test tracks"""
    db = DatabaseManager()
    
    tracks = [
        Track(
            id=1,
            name="Silverstone Circuit",
            country="United Kingdom",
            length_km=5.891,
            discipline="SINGLE_SEATER",
            surface_type="tarmac",
            difficulty=0.7,
            weather_impact=0.6,
            overtaking_difficulty=0.4,
            lap_record_time="01:27.097",
            description="High-speed, flowing corners, technical"
        ),
        Track(
            id=2,
            name="Monaco Street Circuit",
            country="Monaco",
            length_km=3.337,
            discipline="SINGLE_SEATER",
            surface_type="tarmac",
            difficulty=0.95,
            weather_impact=0.3,
            overtaking_difficulty=0.95,
            lap_record_time="01:10.166",
            description="Tight, technical, low-speed, high-precision"
        ),
        Track(
            id=3,
            name="Circuit de la Sarthe",
            country="France",
            length_km=13.626,
            discipline="ENDURANCE",
            surface_type="tarmac",
            difficulty=0.75,
            weather_impact=0.8,
            overtaking_difficulty=0.3,
            lap_record_time="03:17.297",
            description="High-speed, long straights, mixed corners"
        ),
        Track(
            id=4,
            name="Rally Finland Stage",
            country="Finland",
            length_km=25.0,
            discipline="RALLY_STAGE",
            surface_type="gravel",
            difficulty=0.85,
            weather_impact=0.6,
            overtaking_difficulty=0.1,
            lap_record_time="12:45.123",
            description="Fast gravel, jumps, crests, narrow"
        ),
        Track(
            id=5,
            name="Laguna Seca",
            country="USA",
            length_km=3.602,
            discipline="PRODUCTION_TOURING",
            surface_type="tarmac",
            difficulty=0.8,
            weather_impact=0.2,
            overtaking_difficulty=0.5,
            lap_record_time="01:20.674",
            description="Technical, elevation changes, corkscrew"
        ),
    ]
    
    print("Creating test tracks...")
    for track in tracks:
        try:
            track_id = db.add_track(track)
            print(f"✅ Created: {track.name} (ID: {track_id}) - {track.discipline}")
        except Exception as e:
            print(f"⚠️  Error creating {track.name}: {e}")
    
    print(f"\n✅ Created {len(tracks)} test tracks")
    
    # Verify
    all_tracks = db.get_all_tracks()
    print(f"📊 Total tracks in database: {len(all_tracks)}")

if __name__ == "__main__":
    create_test_tracks()
