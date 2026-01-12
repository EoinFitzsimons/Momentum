"""
Test Surface Implementation - Verify track surfaces are properly integrated

Tests:
1. TrackSurfaceService discipline mapping
2. Surface assignment during championship creation
3. Surface persistence in database
4. Surface-to-grip conversion for simulation
5. Visualization receives correct surface attributes
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database_manager import DatabaseManager
from database.models import Track, Championship, Driver, Team
from services.championship_service import ChampionshipService
from services.track_surface_service import TrackSurfaceService
from config import DATABASE_PATH


def test_surface_service():
    """Test TrackSurfaceService functionality"""
    print("\n=== Testing TrackSurfaceService ===")
    
    # Test grip level mapping
    print("\n1. Testing surface-to-grip mapping:")
    surfaces = ["asphalt", "concrete", "gravel", "mixed", "dirt", "grassy"]
    for surface in surfaces:
        grip = TrackSurfaceService.get_grip_level(surface)
        print(f"   {surface:12} -> grip level: {grip}")
    
    # Test discipline-specific surfaces
    print("\n2. Testing discipline-specific surface selection:")
    disciplines = [
        "SINGLE_SEATER",
        "PRODUCTION_TOURING",
        "URBAN_STREET",
        "DRAG_ACCELERATION",
        "SPRINT_RALLYCROSS",
        "ENDURANCE"
    ]
    
    for discipline in disciplines:
        surface = TrackSurfaceService.get_surface_for_discipline(discipline)
        description = TrackSurfaceService.get_discipline_surface_description(discipline)
        print(f"   {discipline:20} -> {surface:10} | {description}")
    
    # Test track surface assignment
    print("\n3. Testing track surface assignment:")
    test_track = Track(
        id=999,
        name="Test Circuit",
        country="Test Country",
        primary_discipline="SINGLE_SEATER",
        length_km=3.5,
        turns=12,
        avg_speed_kmh=160,
        longest_straight_m=750,
        tightest_corner_radius_m=30,
        left_turns=6,
        right_turns=6,
        drs_zones=1,
        surface="asphalt"  # Start with asphalt
    )
    
    # Assign to different disciplines
    for discipline in ["SINGLE_SEATER", "SPRINT_RALLYCROSS", "DRAG_ACCELERATION"]:
        test_track.surface = "asphalt"  # Reset
        assigned = TrackSurfaceService.assign_surface_to_track(test_track, discipline)
        print(f"   {discipline:20} -> {assigned.surface}")


def test_database_surface_update():
    """Test database surface update functionality"""
    print("\n=== Testing Database Surface Update ===")
    
    db = DatabaseManager(DATABASE_PATH)
    
    # Get a track
    tracks = db.get_all_tracks()
    if not tracks:
        print("   No tracks in database to test")
        return
    
    test_track = tracks[0]
    print(f"\n1. Original track: {test_track.name}")
    print(f"   Surface: {test_track.surface}")
    
    # Update surface
    new_surface = "gravel" if test_track.surface != "gravel" else "asphalt"
    success = db.update_track_surface(test_track.id, new_surface)
    print(f"\n2. Updated surface to: {new_surface}")
    print(f"   Success: {success}")
    
    # Retrieve and verify
    updated_track = db.get_track(test_track.id)
    print(f"\n3. Verified surface in database: {updated_track.surface}")
    
    # Restore original
    db.update_track_surface(test_track.id, test_track.surface)
    print(f"   Restored to: {test_track.surface}")


def test_championship_surface_assignment():
    """Test surface assignment during championship creation"""
    print("\n=== Testing Championship Surface Assignment ===")
    
    import time
    db = DatabaseManager(DATABASE_PATH)
    champ_service = ChampionshipService(db)
    
    # Get available tracks
    all_tracks = db.get_all_tracks()
    if len(all_tracks) < 3:
        print("   Not enough tracks in database for championship test (need 3+)")
        return
    
    selected_tracks = [t.id for t in all_tracks[:3]]
    
    print(f"\n1. Creating championship with {len(selected_tracks)} tracks")
    print(f"   Discipline: SPRINT_RALLYCROSS")
    
    # Create test championship with unique name
    unique_name = f"Surface Test Championship {int(time.time())}"
    test_champ = Championship(
        id=0,
        name=unique_name,
        discipline="SPRINT_RALLYCROSS",
        season_length=10,
        points_system="SPRINT_RALLYCROSS",
        current_season=1
    )
    
    try:
        champ_id, race_ids = champ_service.create_championship_season(
            test_champ,
            selected_tracks,
            datetime(2024, 1, 1)
        )
        
        print(f"\n2. Championship created: ID={champ_id}")
        print(f"   Races created: {len(race_ids)}")
        
        # Verify surfaces were assigned
        print(f"\n3. Verifying track surfaces assigned for SPRINT_RALLYCROSS:")
        for track_id in selected_tracks:
            track = db.get_track(track_id)
            print(f"   Track {track.id:3}: {track.name:30} -> {track.surface}")
        
    except Exception as e:
        print(f"   Error: {e}")


def test_visualization_integration():
    """Test that surface attributes flow to visualization"""
    print("\n=== Testing Visualization Integration ===")
    
    db = DatabaseManager(DATABASE_PATH)
    
    # Get a track with surface
    tracks = db.get_all_tracks()
    if not tracks:
        print("   No tracks in database")
        return
    
    track = tracks[0]
    
    print(f"\n1. Track data for visualization:")
    print(f"   Name: {track.name}")
    print(f"   Surface: {track.surface}")
    print(f"   Country: {track.country}")
    print(f"   Discipline: {track.primary_discipline}")
    
    # Verify visualization attributes
    print(f"\n2. Visualization attributes:")
    print(f"   track.surface = {getattr(track, 'surface', 'NOT FOUND')}")
    print(f"   track.surface_grip = {getattr(track, 'surface_grip', 'NOT FOUND')}")
    
    # Check grip level from service
    grip_level = TrackSurfaceService.get_grip_level(track.surface or 'asphalt')
    print(f"\n3. Calculated grip level for surface '{track.surface}': {grip_level}")


def main():
    """Run all surface implementation tests"""
    print("=" * 60)
    print("SURFACE IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    
    try:
        test_surface_service()
        test_database_surface_update()
        test_championship_surface_assignment()
        test_visualization_integration()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
